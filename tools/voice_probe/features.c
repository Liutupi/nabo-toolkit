#include "features.h"
#include "feature_tables.inc"
#include <limits.h>
#include <stddef.h>

_Static_assert(sizeof(vp_features_t) == 4096, "frontend workspace budget");

/* Q8 log2. Exact integer exponent, eight fractional bits from repeated squaring.
 * y remains in [2^31,2^32), so unsigned y*y cannot overflow uint64_t.
 */
static int32_t log2_q8(uint64_t value)
{
    if (!value) return 0;
    unsigned exponent=0;
    for (uint64_t v=value; v>1; v>>=1) exponent++;
    uint64_t y=exponent>31 ? value>>(exponent-31) : value<<(31-exponent);
    unsigned fraction=0;
    for (unsigned bit=0; bit<8; bit++) {
        y=(y*y)>>31;
        if (y>=UINT64_C(0x100000000)) {
            y>>=1;
            fraction|=1u<<(7-bit);
        }
    }
    return (int32_t)(exponent*256+fraction);
}

static void fft(vp_features_t *s)
{
    for (unsigned i=1,j=0; i<VP_FFT_SIZE; i++) {
        unsigned bit=VP_FFT_SIZE>>1;
        for (; j&bit; bit>>=1) j^=bit;
        j^=bit;
        if (i<j) {
            int32_t t=s->real[i]; s->real[i]=s->real[j]; s->real[j]=t;
        }
    }
    for (unsigned size=2; size<=VP_FFT_SIZE; size*=2) {
        unsigned half=size/2, stride=VP_FFT_SIZE/size;
        for (unsigned start=0; start<VP_FFT_SIZE; start+=size) {
            for (unsigned j=0; j<half; j++) {
                unsigned a=start+j,b=a+half,k=j*stride;
                int32_t tr=(int32_t)(((int64_t)vp_cos[k]*s->real[b] -
                                     (int64_t)vp_sin[k]*s->imag[b])/32768);
                int32_t ti=(int32_t)(((int64_t)vp_sin[k]*s->real[b] +
                                     (int64_t)vp_cos[k]*s->imag[b])/32768);
                int32_t ar=s->real[a],ai=s->imag[a];
                s->real[a]=(ar+tr)/2; s->imag[a]=(ai+ti)/2;
                s->real[b]=(ar-tr)/2; s->imag[b]=(ai-ti)/2;
            }
        }
    }
}

static uint64_t power(const vp_features_t *s, unsigned bin)
{
    int64_t r=s->real[bin],i=s->imag[bin];
    return (uint64_t)(r*r+i*i);
}

void vp_features_frame(vp_features_t *s, const int16_t pcm[VP_PCM_SAMPLES],
                       int16_t out[VP_CEPSTRAL_DIM], uint32_t *mean_abs)
{
    int32_t dc=0;
    for (unsigned n=0; n<VP_PCM_SAMPLES; n++) dc+=pcm[n];
    dc/=VP_PCM_SAMPLES;
    uint32_t absolute=0,peak=0;
    for (unsigned n=0; n<VP_FFT_SIZE; n++) {
        int32_t sample=n<VP_PCM_SAMPLES ? (int32_t)pcm[n]-dc : 0;
        uint32_t magnitude=(uint32_t)(sample<0 ? -sample : sample);
        if (magnitude>peak) peak=magnitude;
        absolute+=magnitude;
        s->real[n]=sample; s->imag[n]=0;
    }
    if (mean_abs) *mean_abs=absolute/VP_PCM_SAMPLES;
    if (peak<16) {
        for (unsigned d=0; d<VP_CEPSTRAL_DIM; d++) out[d]=0;
        return;
    }
    // Frame-normalize gain before fixed-point FFT to preserve quiet spectra.
    for (unsigned n=0; n<VP_PCM_SAMPLES; n++) {
        s->real[n]=(int32_t)(((int64_t)s->real[n]*16384/peak)*vp_hann[n]/32768);
    }
    fft(s);
    int32_t bands[VP_MEL_BANDS];
    for (unsigned band=0; band<VP_MEL_BANDS; band++) {
        unsigned left=vp_mel_edges[band],middle=vp_mel_edges[band+1];
        unsigned right=vp_mel_edges[band+2];
        uint64_t sum=0;
        for (unsigned k=left+1; k<middle; k++)
            sum+=power(s,k)*(k-left)/(middle-left);
        sum+=power(s,middle);
        for (unsigned k=middle+1; k<right; k++)
            sum+=power(s,k)*(right-k)/(right-middle);
        bands[band]=log2_q8(sum+1);
    }
    for (unsigned d=0; d<VP_CEPSTRAL_DIM; d++) {
        int64_t sum=0;
        for (unsigned band=0; band<VP_MEL_BANDS; band++)
            sum+=(int64_t)bands[band]*vp_dct[d*VP_MEL_BANDS+band];
        sum/=16384*VP_MEL_BANDS;
        if (sum>INT16_MAX) sum=INT16_MAX;
        if (sum<INT16_MIN) sum=INT16_MIN;
        out[d]=(int16_t)sum;
    }
}
