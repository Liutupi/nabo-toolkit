#include "tk_config_store.h"
#include "nvs.h"
#include <stdlib.h>
#include <string.h>
static uint32_t get32(const uint8_t *b){return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;}
static void set32(uint8_t *b,uint32_t n){for(int i=0;i<4;i++)b[i]=(uint8_t)(n>>(8*i));}
esp_err_t tk_config_store_save(const char *json,size_t size)
{
    if(!json || !size || size>TK_CFG_MAX)return ESP_ERR_INVALID_SIZE;
    nvs_stats_t stats;esp_err_t available=nvs_get_stats(NULL,&stats);
    if(available)return available;
    if(stats.available_entries<(size+16+31)/32+6)return ESP_ERR_NVS_NOT_ENOUGH_SPACE;
    uint8_t *record=calloc(1,size+16);if(!record)return ESP_ERR_NO_MEM;
    memcpy(record,"TKCF",4);record[4]=1;set32(record+8,(uint32_t)size);set32(record+12,tk_config_crc(json,size));memcpy(record+16,json,size);
    nvs_handle_t h;esp_err_t e=nvs_open("nabo_tk",NVS_READWRITE,&h);
    if(!e){e=nvs_set_blob(h,"cfg_v1",record,size+16);if(!e)e=nvs_commit(h);nvs_close(h);}free(record);return e;
}
esp_err_t tk_config_store_load(tk_custom_t *out,char json[TK_CFG_MAX+1],size_t *size)
{
    uint8_t *record=malloc(TK_CFG_RECORD_MAX);if(!record)return ESP_ERR_NO_MEM;
    nvs_handle_t h;size_t bytes=TK_CFG_RECORD_MAX;esp_err_t e=nvs_open("nabo_tk",NVS_READONLY,&h);
    if(!e){e=nvs_get_blob(h,"cfg_v1",record,&bytes);nvs_close(h);}
    if(!e){
        if(bytes<17 || memcmp(record,"TKCF",4) || record[4]!=1 || record[5] || record[6] || record[7] ||
           get32(record+8)!=bytes-16 || get32(record+12)!=tk_config_crc(record+16,bytes-16))e=ESP_ERR_INVALID_CRC;
        else if(tk_config_parse(out,(const char *)record+16,bytes-16))e=ESP_ERR_INVALID_CRC;
        else{memcpy(json,record+16,bytes-16);json[bytes-16]=0;*size=bytes-16;}
    }free(record);return e;
}
