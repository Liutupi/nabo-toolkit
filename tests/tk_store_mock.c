// In-memory provider contracts only: no serial, ESP driver, radio or real NVS access.
#include "nvs.h"
#include "host/ble_store.h"
#include <stdbool.h>
#include <string.h>
typedef struct {uint8_t bytes[4016];size_t size;} blob_t;
static blob_t s_blobs[27],s_stage;
static unsigned s_capacity=630,s_external;
static int s_key=-1,s_read_key=-1,s_fail,s_step,s_commit_step,s_unpair_step,s_drops[16],s_drop_count;
static bool s_voice_read_error;
static ble_addr_t s_peers[4];static int s_peer_count;
static int key(const char *s){
    if(!strncmp(s,"vc",2) && s[2]>='0' && s[2]<='6' && (s[3]=='a' || s[3]=='b') && !s[4])return 13+(s[2]-'0')*2+s[3]-'a';
    if(!strncmp(s,"voice",5) && s[5]>='0' && s[5]<='6' && !s[6])return 6+s[5]-'0';
    return !strcmp(s,"slots_v1")?0:!strcmp(s,"settings_v1")?1:!strcmp(s,"f0_peer")?2:!strcmp(s,"f0_mac")?3:!strcmp(s,"cfg_v1")?4:!strcmp(s,"remote_v1")?5:-1;
}
void tk_mock_reset(void){memset(s_blobs,0,sizeof(s_blobs));s_fail=s_step=s_commit_step=s_unpair_step=s_drop_count=s_peer_count=0;s_key=s_read_key=-1;s_voice_read_error=false;s_capacity=630;s_external=0;}
void tk_mock_read_fail_key(const char *name){s_read_key=name?key(name):-1;}
void tk_mock_capacity(unsigned capacity,unsigned external){s_capacity=capacity;s_external=external;}
void tk_mock_fail(int stage){s_fail=stage;s_voice_read_error=false;}
void tk_mock_blob(const char *name,const uint8_t *bytes,unsigned size){int i=key(name);if(i>=0 && size<=4016){memcpy(s_blobs[i].bytes,bytes,size);s_blobs[i].size=size;}}
unsigned tk_mock_dump(const char *name,uint8_t *out){int i=key(name);if(i<0)return 0;memcpy(out,s_blobs[i].bytes,s_blobs[i].size);return s_blobs[i].size;}
void tk_mock_add_peer(unsigned id){if(s_peer_count<4){ble_addr_t *a=&s_peers[s_peer_count++];a->type=0;for(int k=0;k<5;k++)a->val[k]=k+1;a->val[5]=id;}}
int tk_mock_peer_count(void){return s_peer_count;}
int tk_mock_peer_id(int i){return i>=0 && i<s_peer_count?s_peers[i].val[5]:-1;}
int tk_mock_drop_count(void){return s_drop_count;}
int tk_mock_drop_id(int i){return s_drops[i];}
int tk_mock_commit_step(void){return s_commit_step;}
int tk_mock_unpair_step(void){return s_unpair_step;}
esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle){(void)mode;if(strcmp(name,"nabo_tk"))return ESP_FAIL;*handle=1;return ESP_OK;}
esp_err_t nvs_get_blob(nvs_handle_t handle,const char *name,void *out,size_t *size)
{
    (void)handle;int i=key(name);
    if(s_fail==3 || (i>=6 && s_voice_read_error) || (i>=0 && i==s_read_key))return ESP_FAIL;
    if(i<0 || !s_blobs[i].size)return ESP_ERR_NVS_NOT_FOUND;
    if(*size<s_blobs[i].size)return ESP_ERR_INVALID_SIZE;
    *size=s_blobs[i].size;if(out)memcpy(out,s_blobs[i].bytes,*size);return ESP_OK;
}
esp_err_t nvs_set_blob(nvs_handle_t handle,const char *name,const void *data,size_t size)
{
    (void)handle;if(s_fail==1)return ESP_FAIL;int i=key(name);if(i<0 || size>4016)return ESP_FAIL;
    // IDF NVS blob updates are immediate. Voice faults distinguish an old
    // retained value, a completed update with an SDK error, and unknown readback.
    // Existing nonvoice provider tests retain their historical commit fault model.
    if(i>=6){
        s_key=-1;
        if(s_fail==5)return ESP_OK;
        if(s_fail==7){s_blobs[i].size=0;return ESP_ERR_NVS_NOT_ENOUGH_SPACE;}
        s_blobs[i].size=size;memcpy(s_blobs[i].bytes,data,size);
        if(s_fail==6)s_voice_read_error=true;
        return s_fail==4?ESP_ERR_NVS_REMOVE_FAILED:ESP_OK;
    }
    s_key=i;s_stage.size=size;memcpy(s_stage.bytes,data,size);return ESP_OK;
}
esp_err_t nvs_get_u8(nvs_handle_t handle,const char *name,uint8_t *out){size_t size=1;return nvs_get_blob(handle,name,out,&size);}
esp_err_t nvs_commit(nvs_handle_t handle){(void)handle;if(s_fail==2)return ESP_FAIL;if(s_key>=0)s_blobs[s_key]=s_stage;s_key=-1;s_commit_step=++s_step;return ESP_OK;}
void nvs_close(nvs_handle_t handle){(void)handle;}
esp_err_t nvs_erase_key(nvs_handle_t handle,const char *name){(void)handle;int i=key(name);if(i<0 || !s_blobs[i].size)return ESP_ERR_NVS_NOT_FOUND;if(s_fail==8)return ESP_FAIL;s_blobs[i].size=0;return ESP_OK;}
esp_err_t nvs_get_stats(const char *partition,nvs_stats_t *stats)
{
    (void)partition;unsigned used=s_external;
    for(unsigned i=6;i<27;i++)if(s_blobs[i].size)used+=(unsigned)((s_blobs[i].size+31)/32+2);
    *stats=(nvs_stats_t){.used_entries=used,.total_entries=s_capacity+126,.available_entries=used>s_capacity?0:s_capacity-used};return ESP_OK;
}
int ble_store_util_bonded_peers(ble_addr_t *out,int *count,int capacity){if(capacity<s_peer_count)return -1;*count=s_peer_count;memcpy(out,s_peers,sizeof(ble_addr_t)*s_peer_count);return 0;}
int ble_gap_unpair(const ble_addr_t *peer)
{
    s_unpair_step=++s_step;if(s_drop_count<16)s_drops[s_drop_count++]=peer->val[5];
    for(int i=0;i<s_peer_count;i++)if(s_peers[i].type==peer->type && !memcmp(s_peers[i].val,peer->val,6)){s_peers[i]=s_peers[--s_peer_count];break;}
    return 0;
}
