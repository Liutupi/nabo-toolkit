#ifndef VP_FEATURES_H
#define VP_FEATURES_H

#include <stdint.h>

/* Experimental acoustic frontend, not a pretrained speech recognizer.
 * 16 kHz mono PCM, 320 samples (20 ms) per non-overlapping frame.
 * FFT512 -> 20 log2 mel bands -> DCT coefficients 1..12 (Q8).
 * No heap allocation or floating-point arithmetic at runtime.
 */
#define VP_SAMPLE_RATE 16000
#define VP_PCM_SAMPLES 320
#define VP_FFT_SIZE 512
#define VP_CEPSTRAL_DIM 12
#define VP_MEL_BANDS 20

typedef struct {
    int32_t real[VP_FFT_SIZE];
    int32_t imag[VP_FFT_SIZE];
} vp_features_t;

/* pcm/out/context must be non-null and must not alias one another.
 * mean_abs is optional; it measures DC-removed PCM level, not speech probability.
 * The caller decides when to listen; this function has no microphone/UI/HID API.
 */
void vp_features_frame(vp_features_t *context,
                       const int16_t pcm[VP_PCM_SAMPLES],
                       int16_t out[VP_CEPSTRAL_DIM], uint32_t *mean_abs);

#endif
