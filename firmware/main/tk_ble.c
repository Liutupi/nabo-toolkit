// F0: one active peer, secure HID queue, persistent last-peer reconnect.
// F1's three-slot UI/model is deliberately gated on actual F0 device results.
#include "tk_ble.h"
#include "tk_probe_model.h"
#include <stdatomic.h>
#include <string.h>
#include "esp_random.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "host/ble_hs.h"
#include "host/ble_store.h"
#include "host/util/util.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "nvs.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

void ble_store_config_init(void);
typedef struct { uint32_t generation; uint8_t report, length, data[8]; } request_t;
static QueueHandle_t s_queue;
static tk_ble_sink_t s_sink;
static atomic_uint s_conn = ATOMIC_VAR_INIT(BLE_HS_CONN_HANDLE_NONE), s_generation, s_subscribed, s_command;
static atomic_bool s_encrypted, s_authenticated;
static struct ble_npl_callout s_timer;
static ble_addr_t s_peer;
static bool s_peer_valid, s_restart, s_had_ready;
static uint8_t s_addr_type;
static tk_ble_state_t s_mode, s_last_state = (tk_ble_state_t)-1;
static uint32_t s_until, s_attempt;
static int gap(struct ble_gap_event *ev, void *arg);
static uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }
static void emit(tk_ble_event_kind_t kind, uint32_t value, uint32_t ms)
{
    if (s_sink) s_sink((tk_ble_event_t){kind, value, ms});
}
bool tk_ble_ready(void)
{
    return !atomic_load(&s_command) && atomic_load(&s_conn) != BLE_HS_CONN_HANDLE_NONE &&
        tk_hid_ready(atomic_load(&s_encrypted), atomic_load(&s_authenticated), atomic_load(&s_subscribed),
                     tk_ble_hid_protocol(), tk_ble_hid_suspended());
}
static void state(void)
{
    tk_ble_state_t next = tk_ble_ready() ? TK_BLE_SECURED :
        atomic_load(&s_conn) != BLE_HS_CONN_HANDLE_NONE ? TK_BLE_LINK : s_mode;
    if (next != s_last_state) {
        emit(TK_BLE_STATE, next, next == TK_BLE_SECURED ? now_ms() - s_attempt : 0);
        s_last_state = next;
    }
}
static void clear_link(void)
{
    atomic_fetch_add(&s_generation, 1);
    atomic_store(&s_conn, BLE_HS_CONN_HANDLE_NONE);
    atomic_store(&s_encrypted, false); atomic_store(&s_authenticated, false);
    atomic_store(&s_subscribed, 0);
    tk_ble_hid_reset();
    xQueueReset(s_queue);
    emit(TK_BLE_PASSKEY, UINT32_MAX, 0);
}
static void load_peer(void)
{
    nvs_handle_t h;
    if (nvs_open("nabo_tk", NVS_READONLY, &h) != ESP_OK) return;
    uint8_t p[7]; size_t length = sizeof(p);
    if (nvs_get_blob(h, "f0_peer", p, &length) == ESP_OK && length == 7 && p[0] <= 1) {
        s_peer.type = p[0]; memcpy(s_peer.val, p + 1, 6); s_peer_valid = true;
    }
    nvs_close(h);
}
static void save_peer(const ble_addr_t *peer)
{
    s_peer = *peer; s_peer.type &= 1; s_peer_valid = true;
    uint8_t p[7] = {s_peer.type}; memcpy(p + 1, peer->val, 6);
    nvs_handle_t h;
    esp_err_t err = nvs_open("nabo_tk", NVS_READWRITE, &h);
    if (err == ESP_OK) {
        err = nvs_set_blob(h, "f0_peer", p, sizeof(p));
        if (!err) err = nvs_commit(h);
        nvs_close(h);
    }
    if (err) emit(TK_BLE_ERROR, err, 0);
}
static int fields(void)
{
    static const ble_uuid16_t hid = BLE_UUID16_INIT(0x1812);
    struct ble_hs_adv_fields f = {0};
    f.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    f.appearance = 0x03c1; f.appearance_is_present = 1;
    f.uuids16 = (ble_uuid16_t *)&hid; f.num_uuids16 = 1; f.uuids16_is_complete = 1;
    int rc = ble_gap_adv_set_fields(&f);
    struct ble_hs_adv_fields scan = {0};
    const char *name = ble_svc_gap_device_name();
    scan.name = (uint8_t *)name; scan.name_len = strlen(name); scan.name_is_complete = 1;
    return rc ? rc : ble_gap_adv_rsp_set_fields(&scan);
}
static void advertise(void)
{
    if (atomic_load(&s_conn) != BLE_HS_CONN_HANDLE_NONE || ble_gap_adv_active()) return;
    int rc = fields();
    struct ble_gap_adv_params p = {.conn_mode = BLE_GAP_CONN_MODE_UND,
        .disc_mode = BLE_GAP_DISC_MODE_GEN, .itvl_min = 32, .itvl_max = 48};
    const ble_addr_t *direct = NULL;
    int32_t duration = BLE_HS_FOREVER;
    if (s_mode == TK_BLE_RECONNECT && s_peer_valid) {
        p.conn_mode = BLE_GAP_CONN_MODE_DIR; p.disc_mode = BLE_GAP_DISC_MODE_NON;
        direct = &s_peer; duration = 10000;
    } else if (s_mode != TK_BLE_PAIRING) {
        if (!s_peer_valid) { s_mode = TK_BLE_IDLE; state(); return; }
        rc = rc ? rc : ble_gap_wl_set(&s_peer, 1);
        p.filter_policy = BLE_HCI_ADV_FILT_CONN;
        p.disc_mode = BLE_GAP_DISC_MODE_NON;
    }
    if (!rc) rc = ble_gap_adv_start(s_addr_type, direct, duration, &p, gap, NULL);
    if (rc) emit(TK_BLE_ERROR, rc, 0);
    state();
}
static void begin(bool pairing)
{
    atomic_fetch_add(&s_generation, 1); xQueueReset(s_queue);
    atomic_store(&s_encrypted, false); atomic_store(&s_authenticated, false); atomic_store(&s_subscribed, 0);
    s_had_ready = false;
    s_mode = pairing ? TK_BLE_PAIRING : s_peer_valid ? TK_BLE_RECONNECT : TK_BLE_IDLE;
    s_attempt = now_ms(); s_until = s_attempt + (pairing ? 60000 : 10000);
    emit(TK_BLE_PASSKEY, UINT32_MAX, 0);
    ble_gap_adv_stop();
    unsigned conn = atomic_load(&s_conn);
    if (conn != BLE_HS_CONN_HANDLE_NONE) ble_gap_terminate(conn, BLE_ERR_REM_USER_CONN_TERM);
    s_restart = true; // next timer event; never stop/start advertising in the same context
}
static int gap(struct ble_gap_event *ev, void *arg)
{
    (void)arg;
    switch (ev->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (ev->connect.status) { s_restart = true; break; }
        clear_link(); atomic_store(&s_conn, ev->connect.conn_handle);
        ble_gap_security_initiate(ev->connect.conn_handle);
        break;
    case BLE_GAP_EVENT_DISCONNECT:
        clear_link();
        if (s_had_ready) {
            s_had_ready = false; s_mode = TK_BLE_RECONNECT;
            s_attempt = now_ms(); s_until = s_attempt + 10000;
        }
        s_restart = true;
        break;
    case BLE_GAP_EVENT_ENC_CHANGE: {
        struct ble_gap_conn_desc d;
        bool ok = !ev->enc_change.status && !ble_gap_conn_find(ev->enc_change.conn_handle, &d);
        atomic_store(&s_encrypted, ok && d.sec_state.encrypted);
        atomic_store(&s_authenticated, ok && d.sec_state.authenticated);
        emit(TK_BLE_PASSKEY, UINT32_MAX, 0);
        if (ok && d.sec_state.encrypted && d.sec_state.authenticated && d.sec_state.bonded) save_peer(&d.peer_id_addr);
        else ble_gap_terminate(ev->enc_change.conn_handle, BLE_ERR_AUTH_FAIL);
        break;
    }
    case BLE_GAP_EVENT_SUBSCRIBE: {
        unsigned bit = tk_ble_hid_subscription(ev->subscribe.attr_handle);
        if (ev->subscribe.cur_notify) atomic_fetch_or(&s_subscribed, bit);
        else atomic_fetch_and(&s_subscribed, ~bit);
        break;
    }
    case BLE_GAP_EVENT_PASSKEY_ACTION:
        if (ev->passkey.params.action == BLE_SM_IOACT_DISP) {
            struct ble_sm_io io = {.action = BLE_SM_IOACT_DISP, .passkey = esp_random() % 1000000};
            emit(TK_BLE_PASSKEY, io.passkey, 0);
            int rc = ble_sm_inject_io(ev->passkey.conn_handle, &io);
            if (rc) emit(TK_BLE_ERROR, rc, 0);
        }
        break;
    case BLE_GAP_EVENT_REPEAT_PAIRING: {
        struct ble_gap_conn_desc d;
        if (s_mode != TK_BLE_PAIRING) return BLE_GAP_REPEAT_PAIRING_IGNORE;
        if (!ble_gap_conn_find(ev->repeat_pairing.conn_handle, &d)) ble_store_util_delete_peer(&d.peer_id_addr);
        return BLE_GAP_REPEAT_PAIRING_RETRY;
    }
    case BLE_GAP_EVENT_ADV_COMPLETE:
        if (s_mode == TK_BLE_RECONNECT) s_mode = TK_BLE_IDLE;
        s_restart = true;
        break;
    default: break;
    }
    if (tk_ble_ready()) s_had_ready = true;
    state();
    return 0;
}
static void timer(struct ble_npl_event *ev)
{
    (void)ev;
    unsigned command = atomic_exchange(&s_command, 0);
    if (command) begin(command == 1);
    else if ((s_mode == TK_BLE_PAIRING || s_mode == TK_BLE_RECONNECT) &&
             (int32_t)(now_ms() - s_until) >= 0 && !tk_ble_ready()) {
        begin(false); s_mode = TK_BLE_IDLE;
    } else if (s_restart) { s_restart = false; advertise(); }
    state();
    ble_npl_callout_reset(&s_timer, ble_npl_time_ms_to_ticks32(100));
}
static void sync_host(void)
{
    int rc = ble_hs_util_ensure_addr(0);
    if (!rc) rc = ble_hs_id_infer_auto(0, &s_addr_type);
    if (rc) { emit(TK_BLE_ERROR, rc, 0); return; }
    begin(!s_peer_valid);
    ble_npl_callout_reset(&s_timer, 1);
}
static void reset_host(int reason) { clear_link(); emit(TK_BLE_ERROR, reason, 0); }
static void host_task(void *arg) { (void)arg; nimble_port_run(); nimble_port_freertos_deinit(); }
static int notify(const request_t *r, uint16_t handle, bool release)
{
    if (r->generation != atomic_load(&s_generation) || !tk_ble_ready()) return BLE_HS_ENOTCONN;
    uint8_t zero[8] = {0};
    struct os_mbuf *om = ble_hs_mbuf_from_flat(release ? zero : r->data, r->length);
    return om ? ble_gatts_notify_custom(atomic_load(&s_conn), handle, om) : BLE_HS_ENOMEM;
}
static void sender(void *arg)
{
    (void)arg;
    for (;;) {
        request_t r;
        if (xQueueReceive(s_queue, &r, portMAX_DELAY) != pdTRUE) continue;
        if (r.generation != atomic_load(&s_generation) || !tk_ble_ready()) { emit(TK_BLE_RESULT, 0, 0); continue; }
        if (r.report == 2 && !tk_ble_hid_protocol()) { emit(TK_BLE_RESULT, 0, 0); continue; }
        uint16_t handle = tk_ble_hid_handle(r.report, tk_ble_hid_protocol());
        int rc = notify(&r, handle, false);
        if (!rc) {
            vTaskDelay(pdMS_TO_TICKS(45));
            for (int i = 0; i < 3; ++i) {
                rc = notify(&r, handle, true);
                if (!rc || rc == BLE_HS_ENOTCONN) break;
                vTaskDelay(pdMS_TO_TICKS(20));
            }
            if (rc && r.generation == atomic_load(&s_generation))
                ble_gap_terminate(atomic_load(&s_conn), BLE_ERR_REM_USER_CONN_TERM);
        }
        emit(TK_BLE_RESULT, rc == 0, 0);
        vTaskDelay(pdMS_TO_TICKS(35));
    }
}
bool tk_ble_send(int report, int modifier, int usage)
{
    request_t r = {.generation = atomic_load(&s_generation), .report = report};
    unsigned length;
    if (!s_queue || !tk_ble_ready() || !tk_hid_packet(report, modifier, usage, r.data, &length)) return false;
    r.length = length;
    return xQueueSend(s_queue, &r, 0) == pdTRUE;
}
void tk_ble_pair(void) { atomic_store(&s_command, 1); }
void tk_ble_reconnect(void) { atomic_store(&s_command, 2); }
esp_err_t tk_ble_start(tk_ble_sink_t sink)
{
    s_sink = sink;
    s_queue = xQueueCreate(64, sizeof(request_t));
    if (!s_queue) return ESP_ERR_NO_MEM;
    load_peer();
    esp_err_t err = nimble_port_init();
    if (err) { vQueueDelete(s_queue); s_queue = NULL; return err; }
    ble_svc_gap_init(); ble_svc_gatt_init();
    int rc = ble_svc_gap_device_name_set("NABO 工具箱");
    if (!rc) rc = ble_svc_gap_device_appearance_set(0x03c1);
    if (!rc) rc = tk_ble_hid_register();
    if (rc) { ble_gatts_reset(); nimble_port_deinit(); vQueueDelete(s_queue); s_queue = NULL; return ESP_FAIL; }
    ble_hs_cfg.sync_cb = sync_host; ble_hs_cfg.reset_cb = reset_host;
    ble_hs_cfg.store_status_cb = ble_store_util_status_rr;
    ble_hs_cfg.sm_io_cap = BLE_SM_IO_CAP_DISP_ONLY;
    ble_hs_cfg.sm_bonding = 1; ble_hs_cfg.sm_mitm = 1; ble_hs_cfg.sm_sc = 1;
    ble_hs_cfg.sm_our_key_dist = BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID;
    ble_hs_cfg.sm_their_key_dist = BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID;
    ble_store_config_init();
    ble_npl_callout_init(&s_timer, nimble_port_get_dflt_eventq(), timer, NULL);
    if (xTaskCreate(sender, "tk_hid", 3072, NULL, 4, NULL) != pdPASS) {
        ble_gatts_reset(); nimble_port_deinit(); vQueueDelete(s_queue); s_queue = NULL; return ESP_ERR_NO_MEM;
    }
    nimble_port_freertos_init(host_task);
    return ESP_OK;
}
