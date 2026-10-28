#ifndef VP_MATCHER_H
#define VP_MATCHER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Experimental, speaker-enrolled acoustic-template matching. No pretrained ASR. */
enum {
    VP_FEATURE_DIM = 12,
    VP_MAX_WORDS = 7,
    VP_EXAMPLES_PER_WORD = 3,
    VP_MAX_TEMPLATE_FRAMES = 48,
    VP_MAX_QUERY_FRAMES = 96,
    VP_MIN_SPEECH_FRAMES = 8,
    VP_QUANT_DIVISOR = 16
};

typedef struct { int8_t value[VP_FEATURE_DIM]; } vp_frame_t;
typedef struct {
    vp_frame_t frame[VP_MAX_TEMPLATE_FRAMES];
    uint8_t count; /* Zero means unused. Speech-gated frames, not elapsed time. */
} vp_template_t;
typedef struct { vp_template_t word[VP_MAX_WORDS][VP_EXAMPLES_PER_WORD]; } vp_bank_t;
typedef struct { uint8_t max_distance, min_margin; } vp_options_t;

typedef enum {
    VP_ACCEPTED = 0,
    VP_NO_SPEECH,
    VP_TOO_SHORT,
    VP_TOO_LONG,
    VP_NO_TEMPLATE,
    VP_NO_DURATION_MATCH,
    VP_TOO_DISTANT,
    VP_AMBIGUOUS,
    VP_INVALID_INPUT
} vp_decision_t;

typedef struct {
    vp_decision_t decision;
    int word; /* -1 on every rejection. Scores are distances, not confidence. */
    unsigned speech_frames;
    uint16_t best_distance, runner_up_distance;
} vp_result_t;

/* Caller owns the bank and keeps it immutable during a query. One rolling DTW
 * row per example; the query audio/features are never buffered here. */
typedef struct {
    const vp_bank_t *bank;
    uint16_t cost[VP_MAX_WORDS * VP_EXAMPLES_PER_WORD][VP_MAX_TEMPLATE_FRAMES + 1];
    uint8_t path[VP_MAX_WORDS * VP_EXAMPLES_PER_WORD][VP_MAX_TEMPLATE_FRAMES + 1];
    vp_options_t options;
    uint8_t speech_frames;
    bool too_long, invalid;
} vp_matcher_t;

/* Input frontend is signed Q8; dividing by16 retains Q4, rounded and saturated.
 * This scale and thresholds require real recordings before any accuracy claim. */
void vp_quantize_features(const int16_t input[VP_FEATURE_DIM], vp_frame_t *out);
void vp_bank_init(vp_bank_t *bank);
bool vp_bank_enroll(vp_bank_t *bank, unsigned word, unsigned example,
                    const vp_frame_t *frames, size_t count);
void vp_matcher_begin(vp_matcher_t *matcher, const vp_bank_t *bank,
                      const vp_options_t *options); /* NULL options: {18,2}. */
bool vp_matcher_push(vp_matcher_t *matcher, const vp_frame_t *frame, bool voiced);
vp_result_t vp_matcher_finish(const vp_matcher_t *matcher);
size_t vp_bank_bytes(void);
size_t vp_matcher_bytes(void);
size_t vp_enrollment_buffer_bytes(void);

#endif
