#pragma once
#include "esp_err.h"
#include "matcher.h"

// Read legacy padded v1; new per-word A/B journals losslessly pack active frames.
enum { TK_VOICE_RECORD_BYTES=20+VP_EXAMPLES_PER_WORD*VP_MAX_TEMPLATE_FRAMES*VP_FEATURE_DIM+4 };
enum { TK_VOICE_RECORD_MAX=TK_VOICE_RECORD_BYTES+22, TK_VOICE_STORE_SCRATCH_BYTES=2*TK_VOICE_RECORD_MAX };
typedef struct {esp_err_t write_error,read_error;bool confirmed,unknown;} tk_voice_store_result_t;
esp_err_t tk_voice_store_load(unsigned word,vp_template_t out[VP_EXAMPLES_PER_WORD],
                              uint8_t *next,uint8_t scratch[TK_VOICE_STORE_SCRATCH_BYTES]);
bool tk_voice_store_bad_record(esp_err_t error);
esp_err_t tk_voice_store_scan(uint8_t counts[VP_MAX_WORDS],uint8_t *invalid_mask,
                              vp_template_t word[VP_EXAMPLES_PER_WORD],uint8_t scratch[TK_VOICE_STORE_SCRATCH_BYTES]);
// Existing RAM templates remain immutable. A fresh-handle read must confirm the
// expected record, regardless of the write API's result. No rollback is inferred
// from an SDK error, and no other NVS keys are written. Scratch holds both copies.
esp_err_t tk_voice_store_save(unsigned word,const vp_template_t current[VP_EXAMPLES_PER_WORD],
                              unsigned example,const vp_frame_t *frames,unsigned count,
                              uint8_t scratch[TK_VOICE_STORE_SCRATCH_BYTES],tk_voice_store_result_t *result);
// Explicit single-word preparation only; never called by init/load/save. Keeps
// samples, feature values and next slot unchanged, then retires verified legacy.
esp_err_t tk_voice_store_compact_legacy(unsigned word,uint8_t scratch[TK_VOICE_STORE_SCRATCH_BYTES]);
