#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "matcher.h"

typedef struct {
    uint32_t start_ms,noise_sum,cal_frames,threshold,frames,silent,max_frames,min_frames;
    bool calibrated,started,done;
    int decision;
} tk_voice_capture_t;
void tk_voice_capture_init(tk_voice_capture_t *c,uint32_t now,bool enrolling);
// Returns true only for a speech-gated frame to feed into enrollment/matching.
// 300ms calibration, 300ms trailing silence, <=3s wall time; enrollment <=48
// speech frames, recognition <=96 so the matcher can test a slower utterance.
bool tk_voice_capture_feed(tk_voice_capture_t *c,uint32_t level,uint32_t now);
