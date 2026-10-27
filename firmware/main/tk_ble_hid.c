// HID GATT adapted from the NABO radio keyboard; report IDs stay in descriptors.
#include "tk_ble.h"
#include <stdatomic.h>
#include "host/ble_hs.h"
#include "host/ble_gatt.h"
#include "os/os_mbuf.h"
static atomic_bool s_suspended, s_protocol = ATOMIC_VAR_INIT(true);
static uint16_t s_keyboard, s_consumer, s_boot, s_battery;
/* HID keyboard (report 1) and Consumer controls (report 2). Report IDs are
 * carried by each GATT Report Reference, not prepended to notifications. */
static const uint8_t report_map[]={
    0x05,0x01,0x09,0x06,0xa1,0x01,0x85,0x01,
    0x05,0x07,0x19,0xe0,0x29,0xe7,0x15,0x00,0x25,0x01,0x75,0x01,0x95,0x08,0x81,0x02,
    0x75,0x08,0x95,0x01,0x81,0x01,
    0x19,0x00,0x29,0x73,0x15,0x00,0x25,0x73,0x75,0x08,0x95,0x06,0x81,0x00,
    0x05,0x08,0x19,0x01,0x29,0x05,0x75,0x01,0x95,0x05,0x91,0x02,
    0x75,0x03,0x95,0x01,0x91,0x01,0xc0,
    0x05,0x0c,0x09,0x01,0xa1,0x01,0x85,0x02,
    0x15,0x00,0x26,0xff,0x03,0x19,0x00,0x2a,0xff,0x03,0x75,0x10,0x95,0x01,0x81,0x00,0xc0
};
static const ble_uuid16_t hid_uuid=BLE_UUID16_INIT(0x1812);
static const ble_uuid16_t info_uuid=BLE_UUID16_INIT(0x2a4a), map_uuid=BLE_UUID16_INIT(0x2a4b);
static const ble_uuid16_t control_uuid=BLE_UUID16_INIT(0x2a4c), report_uuid=BLE_UUID16_INIT(0x2a4d);
static const ble_uuid16_t protocol_uuid=BLE_UUID16_INIT(0x2a4e), boot_in_uuid=BLE_UUID16_INIT(0x2a22);
static const ble_uuid16_t boot_out_uuid=BLE_UUID16_INIT(0x2a32), ref_uuid=BLE_UUID16_INIT(0x2908);
static const ble_uuid16_t dis_uuid=BLE_UUID16_INIT(0x180a), pnp_uuid=BLE_UUID16_INIT(0x2a50);
static const ble_uuid16_t bas_uuid=BLE_UUID16_INIT(0x180f), battery_uuid=BLE_UUID16_INIT(0x2a19);
enum { ACCESS_INFO, ACCESS_MAP, ACCESS_CONTROL, ACCESS_PROTOCOL, ACCESS_KEYBOARD, ACCESS_CONSUMER, ACCESS_LEDS,
       ACCESS_PNP, ACCESS_BATTERY };

static atomic_int s_battery_pct = ATOMIC_VAR_INIT(-1);
static int battery_level(void) { return atomic_load(&s_battery_pct); }
void tk_ble_hid_battery(int pct) { atomic_store(&s_battery_pct, pct); }

static int access_value(uint16_t conn, uint16_t attr, struct ble_gatt_access_ctxt *ctx, void *arg)
{
    (void)conn; (void)attr;
    unsigned kind=(uintptr_t)arg;
    uint8_t b[8]={0}; const void *data=b; size_t len=0;
    if (ctx->op==BLE_GATT_ACCESS_OP_READ_CHR) {
        switch(kind) {
        case ACCESS_INFO: b[0]=0x11;b[1]=0x01;b[3]=0x02;len=4;break;
        case ACCESS_MAP:data=report_map;len=sizeof(report_map);break;
        case ACCESS_PROTOCOL:b[0]=atomic_load(&s_protocol);len=1;break;
        case ACCESS_KEYBOARD:len=8;break;
        case ACCESS_CONSUMER:len=2;break;
        case ACCESS_LEDS:len=1;break;
        /* Experimental Bluetooth vendor ID, not an assigned USB vendor ID. */
        case ACCESS_PNP:b[0]=1;b[1]=0xff;b[2]=0xff;b[3]=1;b[6]=1;len=7;break;
        case ACCESS_BATTERY: {
            int pct=battery_level();
            if (pct<0) return BLE_ATT_ERR_UNLIKELY;
            b[0]=(uint8_t)pct;len=1;break;
        }
        default:return BLE_ATT_ERR_READ_NOT_PERMITTED;
        }
        return os_mbuf_append(ctx->om,data,len)==0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
    }
    if (ctx->op==BLE_GATT_ACCESS_OP_WRITE_CHR) {
        if (OS_MBUF_PKTLEN(ctx->om)!=1 || os_mbuf_copydata(ctx->om,0,1,b)!=0)
            return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
        if (kind==ACCESS_LEDS) return 0;
        if (b[0]>1) return BLE_ATT_ERR_UNLIKELY;
        if (kind==ACCESS_CONTROL) atomic_store(&s_suspended,b[0]==0);
        else if (kind==ACCESS_PROTOCOL) atomic_store(&s_protocol,b[0]!=0);
        else return BLE_ATT_ERR_WRITE_NOT_PERMITTED;
        return 0;
    }
    return BLE_ATT_ERR_UNLIKELY;
}
static int access_ref(uint16_t conn, uint16_t attr, struct ble_gatt_access_ctxt *ctx, void *arg)
{
    (void)conn;(void)attr;
    uint8_t ref[2]={(uintptr_t)arg&255,((uintptr_t)arg>>8)&255};
    return os_mbuf_append(ctx->om,ref,2)==0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
}
#define READ_ENC (BLE_GATT_CHR_F_READ|BLE_GATT_CHR_F_READ_ENC|BLE_GATT_CHR_F_READ_AUTHEN)
#define WRITE_ENC (BLE_GATT_CHR_F_WRITE_NO_RSP|BLE_GATT_CHR_F_WRITE_ENC|BLE_GATT_CHR_F_WRITE_AUTHEN)
#define REFERENCE(id,type) (struct ble_gatt_dsc_def[]){{.uuid=&ref_uuid.u,.att_flags=BLE_ATT_F_READ,.access_cb=access_ref,.arg=(void *)((type)*256+(id))},{0}}
static const struct ble_gatt_svc_def services[]={
    {.type=BLE_GATT_SVC_TYPE_PRIMARY,.uuid=&hid_uuid.u,
     .characteristics=(struct ble_gatt_chr_def[]){
        /* Gate discovery too: macOS can abandon HID creation if it reads the
         * map before the first passkey pairing has finished encrypting. */
        {.uuid=&info_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_INFO,.flags=READ_ENC},
        {.uuid=&map_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_MAP,.flags=READ_ENC},
        {.uuid=&control_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_CONTROL,.flags=WRITE_ENC},
        {.uuid=&protocol_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_PROTOCOL,.flags=READ_ENC|WRITE_ENC},
        {.uuid=&report_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_KEYBOARD,.flags=READ_ENC|BLE_GATT_CHR_F_NOTIFY,
         .val_handle=&s_keyboard,.descriptors=REFERENCE(1,1)},
        {.uuid=&report_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_CONSUMER,.flags=READ_ENC|BLE_GATT_CHR_F_NOTIFY,
         .val_handle=&s_consumer,.descriptors=REFERENCE(2,1)},
        {.uuid=&report_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_LEDS,.flags=READ_ENC|WRITE_ENC|BLE_GATT_CHR_F_WRITE,
         .descriptors=REFERENCE(1,2)},
        {.uuid=&boot_in_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_KEYBOARD,.flags=READ_ENC|BLE_GATT_CHR_F_NOTIFY,.val_handle=&s_boot},
        {.uuid=&boot_out_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_LEDS,.flags=READ_ENC|WRITE_ENC|BLE_GATT_CHR_F_WRITE},
        {0}}},
    {.type=BLE_GATT_SVC_TYPE_PRIMARY,.uuid=&dis_uuid.u,
     .characteristics=(struct ble_gatt_chr_def[]){
        {.uuid=&pnp_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_PNP,.flags=BLE_GATT_CHR_F_READ},
        {0}}},
    {.type=BLE_GATT_SVC_TYPE_PRIMARY,.uuid=&bas_uuid.u,
     .characteristics=(struct ble_gatt_chr_def[]){
        {.uuid=&battery_uuid.u,.access_cb=access_value,.arg=(void *)ACCESS_BATTERY,
         .flags=READ_ENC|BLE_GATT_CHR_F_NOTIFY,.val_handle=&s_battery},
        {0}}},
    {0}
};

int tk_ble_hid_register(void)
{
    int rc = ble_gatts_count_cfg(services);
    return rc ? rc : ble_gatts_add_svcs(services);
}
unsigned tk_ble_hid_subscription(uint16_t attr)
{
    return attr == s_keyboard ? 1 : attr == s_consumer ? 2 : attr == s_boot ? 4 : 0;
}
uint16_t tk_ble_hid_handle(int report, bool protocol)
{
    return report == 2 ? s_consumer : protocol ? s_keyboard : s_boot;
}
bool tk_ble_hid_protocol(void) { return atomic_load(&s_protocol); }
bool tk_ble_hid_suspended(void) { return atomic_load(&s_suspended); }
void tk_ble_hid_reset(void) { atomic_store(&s_protocol, true); atomic_store(&s_suspended, false); }
