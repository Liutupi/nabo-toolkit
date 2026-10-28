#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"

enum { TK_VR_WORDS=7, TK_VR_EXAMPLES=3 };
typedef enum {
    TK_VR_IDLE, TK_VR_STARTING, TK_VR_CALIBRATING,
    TK_VR_LISTENING, TK_VR_COMPLETE, TK_VR_CANCELLED, TK_VR_ERROR
} tk_voice_runtime_status_t;
enum { TK_VOICE_ERROR_NONE, TK_VOICE_ERROR_MEMORY, TK_VOICE_ERROR_CAPTURE, TK_VOICE_ERROR_STORE };
typedef struct {
    uint32_t generation,token;
    int status,word,example,decision;
    bool active,enrolling;
    _Alignas(4) uint8_t counts[TK_VR_WORDS];
    uint8_t invalid_mask; // Bad CRC/format/size words need explicit re-enrollment.
    uint16_t distance,runner_up_distance,frames;
    esp_err_t error;
    int error_stage;
    uint32_t heap,largest,peak,frame_max_us,threshold;
    esp_err_t storage_write_error,storage_read_error;
    bool storage_unknown;
    uint32_t stack_low_watermark; // Worker stack bytes, IDF FreeRTOS units.
    bool heap_integrity; // Bounded lifecycle checks; never every audio frame.
} tk_voice_snapshot_t;

// Init creates only the bounded worker/control storage; acoustic bank is per job.
esp_err_t tk_voice_init(void);
// Each accepted enrollment rotates its word's persistent sample slot 0..2.
esp_err_t tk_voice_request_enroll(unsigned word,uint32_t token);
esp_err_t tk_voice_request_recognize(uint32_t token);
void tk_voice_cancel(void);
bool tk_voice_active(void);
tk_voice_snapshot_t tk_voice_snapshot(void);
// Asynchronous cancellation: false until the last codec read has returned.
bool tk_voice_prepare_sleep(void);
// Explicit USB maintenance only; never called automatically during startup.
esp_err_t tk_voice_compact_legacy(void);
