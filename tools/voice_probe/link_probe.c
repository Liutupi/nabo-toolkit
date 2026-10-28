/* Link/sizeof probe only. Deliberately has no FreeRTOS task, microphone,
 * persistence, navigation or HID integration. Never a device-test firmware.
 */
#include "features.h"
#include "matcher.h"

_Static_assert(VP_FEATURE_DIM == VP_CEPSTRAL_DIM, "frontend/matcher dimensions");

static vp_features_t frontend;
static vp_bank_t bank;
static vp_matcher_t matcher;
static vp_frame_t enrollment[VP_MAX_TEMPLATE_FRAMES];
static int16_t samples[VP_PCM_SAMPLES];
static int16_t coefficients[VP_CEPSTRAL_DIM];
static vp_frame_t frame;
static uint32_t level;
static volatile int decision_sink;

/* Forcing this root keeps the complete acoustic path and all caller-owned
 * buffers in the sizing ELF. The production app never calls this symbol.
 */
void vp_link_probe_step(void)
{
    vp_bank_init(&bank);
    vp_features_frame(&frontend,samples,coefficients,&level);
    vp_quantize_features(coefficients,&frame);
    for (unsigned i=0;i<VP_MAX_TEMPLATE_FRAMES;i++) enrollment[i]=frame;
    vp_bank_enroll(&bank,0,0,enrollment,VP_MAX_TEMPLATE_FRAMES);
    vp_matcher_begin(&matcher,&bank,NULL);
    vp_matcher_push(&matcher,&frame,level>=128);
    decision_sink=(int)vp_matcher_finish(&matcher).decision;
    decision_sink+=(int)(vp_bank_bytes()+vp_matcher_bytes()+vp_enrollment_buffer_bytes());
}
