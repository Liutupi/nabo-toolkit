#include "tk_persist.h"
#include "nvs.h"
#include <string.h>
// Small, versioned settings blob. Device slots and NimBLE keys have independent stores.
static uint32_t crc32(const uint8_t *b,unsigned size)
{
    uint32_t c=0xffffffff;for(unsigned i=0;i<size;i++){c^=b[i];for(int k=0;k<8;k++)c=(c>>1)^(0xedb88320u&(0u-(c&1)));}return ~c;
}
esp_err_t tk_persist_load(tk_state_t *s)
{
    nvs_handle_t h;esp_err_t error=nvs_open("nabo_tk",NVS_READONLY,&h);
    if(error==ESP_ERR_NVS_NOT_FOUND)return ESP_OK;
    if(error)return error;
    uint8_t data[12];size_t size=sizeof(data);error=nvs_get_blob(h,"settings_v1",data,&size);nvs_close(h);
    if(error==ESP_ERR_NVS_NOT_FOUND)return ESP_OK;
    if(error)return error;
    if(size!=12)return ESP_ERR_INVALID_SIZE;
    uint32_t crc=0;for(int i=0;i<4;i++)crc|=(uint32_t)data[8+i]<<(i*8);
    if(memcmp(data,"TKS",3) || data[3]!=1 || data[4]>1 || data[5]>1 || data[6]>6 || data[7]>3 || crc!=crc32(data,8))return ESP_ERR_INVALID_CRC;
    s->beep=data[4];s->voice=data[5];s->talk=data[6];s->sleep=data[7];return ESP_OK;
}
esp_err_t tk_persist_save(const tk_state_t *s)
{
    if(s->talk<0 || s->talk>6 || s->sleep<0 || s->sleep>3)return ESP_ERR_INVALID_ARG;
    uint8_t data[12]={'T','K','S',1,s->beep,s->voice,s->talk,s->sleep};uint32_t crc=crc32(data,8);
    for(int i=0;i<4;i++)data[8+i]=(uint8_t)(crc>>(i*8));
    nvs_handle_t h;esp_err_t error=nvs_open("nabo_tk",NVS_READWRITE,&h);
    if(!error){error=nvs_set_blob(h,"settings_v1",data,sizeof(data));if(!error)error=nvs_commit(h);nvs_close(h);}return error;
}
