#include "tk_ble_slots.h"
#include "tk_ble.h"
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "host/util/util.h"
#include "host/ble_store.h"
#include "nvs.h"

static tk_slots_t s_slots;
static SemaphoreHandle_t s_lock;
static bool s_loaded;
static esp_err_t s_load_error;
static esp_err_t save(const tk_slots_t *next)
{
    uint8_t bytes[TK_SLOTS_STORAGE_SIZE];if(!tk_slots_encode(next,bytes))return ESP_ERR_INVALID_ARG;
    if(s_loaded && !memcmp(next,&s_slots,sizeof(*next)))return ESP_OK;
    nvs_handle_t h;esp_err_t error=nvs_open("nabo_tk",NVS_READWRITE,&h);
    if(!error){error=nvs_set_blob(h,"slots_v1",bytes,sizeof(bytes));if(!error)error=nvs_commit(h);nvs_close(h);}
    if(!error){xSemaphoreTake(s_lock,portMAX_DELAY);s_slots=*next;xSemaphoreGive(s_lock);}
    return error;
}
void tk_ble_slots_init(void)
{
    s_lock=xSemaphoreCreateMutex();tk_slots_init(&s_slots);if(!s_lock)return;
    nvs_handle_t h;uint8_t bytes[TK_SLOTS_STORAGE_SIZE];size_t size=sizeof(bytes);
    esp_err_t error=nvs_open("nabo_tk",NVS_READONLY,&h);
    if(error==ESP_OK){
        error=nvs_get_blob(h,"slots_v1",bytes,&size);nvs_close(h);
        if(error==ESP_OK){s_loaded=tk_slots_decode(&s_slots,bytes,size);if(!s_loaded)s_load_error=ESP_ERR_INVALID_CRC;}
        else if(error!=ESP_ERR_NVS_NOT_FOUND)s_load_error=error;
    }
    else if(error!=ESP_ERR_NVS_NOT_FOUND)s_load_error=error;
}
bool tk_ble_slots_snapshot(tk_slots_t *out)
{
    if(!s_lock || !out)return false;
    xSemaphoreTake(s_lock,portMAX_DELAY);*out=s_slots;xSemaphoreGive(s_lock);return true;
}
bool tk_ble_slots_available(void){return s_lock && s_loaded;}
bool tk_ble_slots_known(const ble_addr_t *peer)
{
    tk_slots_t s;return tk_ble_slots_snapshot(&s) && tk_slots_find(&s,peer->val,peer->type&1)>=0;
}
static ble_addr_t address(const tk_peer_t *peer){ble_addr_t a={.type=peer->type};memcpy(a.val,peer->address,6);return a;}
static bool present(const ble_addr_t *a,ble_addr_t *peers,int count)
{
    for(int i=0;i<count;i++)if((peers[i].type&1)==(a->type&1) && !memcmp(peers[i].val,a->val,6))return true;
    return false;
}
esp_err_t tk_ble_slots_sync(void)
{
    if(!s_lock)return ESP_ERR_NO_MEM;
    if(s_load_error)return s_load_error; // Keep a bad record intact; never erase NVS to hide it.
    ble_addr_t peers[4];int count=0;
    if(ble_store_util_bonded_peers(peers,&count,4))return ESP_FAIL;
    tk_slots_t next;if(!tk_ble_slots_snapshot(&next))return ESP_FAIL;
    if(!s_loaded){
        // Migrate existing NimBLE keys without clearing NVS. Friendly names were not stored by F0.
        for(int i=0;i<count;i++){
            tk_peer_t peer={.used=1,.type=peers[i].type&1,.os=1};memcpy(peer.address,peers[i].val,6);
            snprintf(peer.name,sizeof(peer.name),"已绑定设备 %d",i+1);tk_slots_add(&next,&peer,NULL);
        }
        // Preserve F0's selected identity and Mac/Windows preference where possible.
        nvs_handle_t h;if(nvs_open("nabo_tk",NVS_READONLY,&h)==ESP_OK){
            uint8_t previous[7],mac=0;size_t size=7;
            if(nvs_get_blob(h,"f0_peer",previous,&size)==ESP_OK && size==7){int slot=tk_slots_find(&next,previous+1,previous[0]&1);if(slot>=0){next.active=slot;if(nvs_get_u8(h,"f0_mac",&mac)==ESP_OK)next.peers[slot].os=mac?0:1;}}
            nvs_close(h);
        }
        esp_err_t error=save(&next);if(!error)s_loaded=true;return error;
    }else{
        // A committed three-slot record wins after a power loss during staging.
        for(int i=0;i<count;i++)if(tk_slots_find(&next,peers[i].val,peers[i].type&1)<0)ble_gap_unpair(&peers[i]);
        for(unsigned i=0;i<3;i++)if(next.peers[i].used){ble_addr_t a=address(&next.peers[i]);if(!present(&a,peers,count))tk_slots_remove(&next,i);}
        return save(&next);
    }
}
bool tk_ble_slots_selected(ble_addr_t *peer)
{
    tk_slots_t s;if(!tk_ble_slots_snapshot(&s) || !s.peers[s.active].used)return false;
    *peer=address(&s.peers[s.active]);return true;
}
int tk_ble_slots_bound(const ble_addr_t *a)
{
    tk_slots_t next;if(!tk_ble_slots_snapshot(&next))return -1;
    int found=tk_slots_find(&next,a->val,a->type&1);
    if(found>=0){next.active=found;return save(&next)==ESP_OK?found:-1;}
    tk_peer_t peer={.used=1,.type=a->type&1,.os=1},evicted;
    memcpy(peer.address,a->val,6);snprintf(peer.name,sizeof(peer.name),"新设备 %d",next.count<3?next.count+1:next.order[0]+1);
    int slot=tk_slots_add(&next,&peer,&evicted);
    if(slot<0 || save(&next)!=ESP_OK){ble_gap_unpair(a);return -1;}
    // Persist the new slot before dropping its FIFO predecessor. Four is staging capacity only.
    if(evicted.used){ble_addr_t old=address(&evicted);ble_gap_unpair(&old);}
    s_loaded=true;return slot;
}
esp_err_t tk_ble_slots_select(unsigned slot)
{
    tk_slots_t next;if(!tk_ble_slots_snapshot(&next) || slot>2 || !next.peers[slot].used)return ESP_ERR_INVALID_ARG;
    next.active=slot;return save(&next);
}
esp_err_t tk_ble_slots_type(unsigned slot,unsigned os)
{
    tk_slots_t next;if(!tk_ble_slots_snapshot(&next) || slot>2 || os>3 || !next.peers[slot].used)return ESP_ERR_INVALID_ARG;
    next.peers[slot].os=os;return save(&next);
}
esp_err_t tk_ble_slots_delete(unsigned slot)
{
    tk_slots_t next;if(!tk_ble_slots_snapshot(&next) || slot>2)return ESP_ERR_INVALID_ARG;
    tk_peer_t old=next.peers[slot];tk_slots_remove(&next,slot);esp_err_t error=save(&next);
    if(!error && old.used){ble_addr_t a=address(&old);ble_gap_unpair(&a);}return error;
}
