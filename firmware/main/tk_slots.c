#include "tk_slots.h"
#include <string.h>
void tk_slots_init(tk_slots_t *s){memset(s,0,sizeof(*s));}
int tk_slots_find(const tk_slots_t *s,const uint8_t address[6],unsigned type)
{
    for(int i=0;i<3;i++)if(s->peers[i].used && s->peers[i].type==type && !memcmp(s->peers[i].address,address,6))return i;
    return -1;
}
bool tk_slots_valid(const tk_slots_t *s)
{
    if(s->count>3 || s->active>2)return false;
    unsigned used=0,mask=0;
    for(unsigned i=0;i<3;i++){
        const tk_peer_t *p=&s->peers[i];if(!p->used)continue;
        if(p->used!=1 || p->type>1 || p->os>3 || !p->name[0] || !memchr(p->name,0,sizeof(p->name)))return false;
        uint8_t any=0;for(int k=0;k<6;k++)any|=p->address[k];if(!any)return false;
        for(unsigned j=0;j<i;j++)if(s->peers[j].used && p->type==s->peers[j].type && !memcmp(p->address,s->peers[j].address,6))return false;
        used++;
    }
    if(used!=s->count)return false;
    for(unsigned i=0;i<s->count;i++){unsigned slot=s->order[i];if(slot>2 || !s->peers[slot].used || (mask&(1u<<slot)))return false;mask|=1u<<slot;}
    return true;
}
static void remove_order(tk_slots_t *s,unsigned slot)
{
    unsigned n=0;for(unsigned i=0;i<s->count;i++)if(s->order[i]!=slot)s->order[n++]=s->order[i];
    s->count=n;for(unsigned i=n;i<3;i++)s->order[i]=0;
}
int tk_slots_add(tk_slots_t *s,const tk_peer_t *peer,tk_peer_t *evicted)
{
    if(!tk_slots_valid(s) || !peer)return -1;
    tk_slots_t next=*s;
    int slot=tk_slots_find(s,peer->address,peer->type);
    if(evicted)memset(evicted,0,sizeof(*evicted));
    // A successful re-pair updates the same peer; ordinary selection never calls add.
    if(slot<0){for(int i=0;i<3;i++)if(!s->peers[i].used){slot=i;break;}}
    if(slot<0){slot=s->order[0];if(evicted)*evicted=s->peers[slot];}
    next.peers[slot]=*peer;next.peers[slot].used=1;remove_order(&next,slot);
    next.order[next.count++]=slot;next.active=slot;
    if(!tk_slots_valid(&next)){if(evicted)memset(evicted,0,sizeof(*evicted));return -1;}
    *s=next;return slot;
}
bool tk_slots_remove(tk_slots_t *s,unsigned slot)
{
    if(slot>2 || !tk_slots_valid(s))return false;
    memset(&s->peers[slot],0,sizeof(s->peers[slot]));remove_order(s,slot);return true;
}
static uint32_t crc32(const uint8_t *data,size_t size)
{
    uint32_t crc=0xffffffff;
    for(size_t i=0;i<size;i++){crc^=data[i];for(int bit=0;bit<8;bit++)crc=(crc>>1)^(0xedb88320u & (0u-(crc&1u)));}
    return ~crc;
}
bool tk_slots_encode(const tk_slots_t *s,uint8_t out[TK_SLOTS_STORAGE_SIZE])
{
    if(!tk_slots_valid(s))return false;
    memset(out,0,TK_SLOTS_STORAGE_SIZE);memcpy(out,"TKSL",4);out[4]=1;out[5]=s->active;out[6]=s->count;memcpy(out+7,s->order,s->count);
    for(unsigned i=0;i<3;i++){
        const tk_peer_t *p=&s->peers[i];uint8_t *d=out+10+i*105;
        if(!p->used)continue;
        d[0]=1;d[1]=p->type;d[2]=p->os;memcpy(d+3,p->address,6);memcpy(d+9,p->name,strlen(p->name));
    }
    uint32_t crc=crc32(out,325);for(int i=0;i<4;i++)out[325+i]=(uint8_t)(crc>>(8*i));return true;
}
bool tk_slots_decode(tk_slots_t *s,const uint8_t *data,size_t size)
{
    if(size!=TK_SLOTS_STORAGE_SIZE || memcmp(data,"TKSL",4) || data[4]!=1)return false;
    uint32_t crc=0;for(int i=0;i<4;i++)crc|=(uint32_t)data[325+i]<<(8*i);if(crc32(data,325)!=crc)return false;
    tk_slots_t next;tk_slots_init(&next);next.active=data[5];next.count=data[6];memcpy(next.order,data+7,3);
    for(unsigned i=0;i<3;i++){
        const uint8_t *d=data+10+i*105;tk_peer_t *p=&next.peers[i];p->used=d[0];p->type=d[1];p->os=d[2];memcpy(p->address,d+3,6);memcpy(p->name,d+9,96);
    }
    if(!tk_slots_valid(&next))return false;
    *s=next;return true;
}
