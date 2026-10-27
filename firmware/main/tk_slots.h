#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct { uint8_t used,type,os,address[6]; char name[96]; } tk_peer_t;
typedef struct { tk_peer_t peers[3]; uint8_t order[3],count,active; } tk_slots_t;
#define TK_SLOTS_STORAGE_SIZE 329
void tk_slots_init(tk_slots_t *s);
int tk_slots_find(const tk_slots_t *s,const uint8_t address[6],unsigned type);
int tk_slots_add(tk_slots_t *s,const tk_peer_t *peer,tk_peer_t *evicted);
bool tk_slots_remove(tk_slots_t *s,unsigned slot);
bool tk_slots_valid(const tk_slots_t *s);
bool tk_slots_encode(const tk_slots_t *s,uint8_t out[TK_SLOTS_STORAGE_SIZE]);
bool tk_slots_decode(tk_slots_t *s,const uint8_t *data,size_t size);
