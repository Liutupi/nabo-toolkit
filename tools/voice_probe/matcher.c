#include "matcher.h"
#include <string.h>

#define VP_INF UINT16_MAX
#define VP_TOTAL_EXAMPLES (VP_MAX_WORDS * VP_EXAMPLES_PER_WORD)

_Static_assert(VP_MAX_QUERY_FRAMES + VP_MAX_TEMPLATE_FRAMES < UINT8_MAX,
               "DTW path length must fit one byte");
_Static_assert(255u * (VP_MAX_QUERY_FRAMES + VP_MAX_TEMPLATE_FRAMES) < VP_INF,
               "DTW worst-case accumulated distance must fit uint16_t");
_Static_assert(sizeof(vp_bank_t) + sizeof(vp_matcher_t) +
               sizeof(vp_frame_t) * VP_MAX_TEMPLATE_FRAMES < 16u * 1024u,
               "Matcher, bank and enrollment buffer exceed the 16KiB budget");

void vp_quantize_features(const int16_t input[VP_FEATURE_DIM], vp_frame_t *out)
{
    if(!input || !out)return;
    for(unsigned i=0;i<VP_FEATURE_DIM;i++){
        int n=input[i];n=(n+(n>=0?8:-8))/VP_QUANT_DIVISOR;
        if(n>127)n=127;
        if(n<-127)n=-127;
        out->value[i]=(int8_t)n;
    }
}

void vp_bank_init(vp_bank_t *bank){if(bank)memset(bank,0,sizeof(*bank));}

bool vp_bank_enroll(vp_bank_t *bank,unsigned word,unsigned example,
                    const vp_frame_t *frames,size_t count)
{
    if(!bank || !frames || word>=VP_MAX_WORDS || example>=VP_EXAMPLES_PER_WORD ||
       count<VP_MIN_SPEECH_FRAMES || count>VP_MAX_TEMPLATE_FRAMES)return false;
    vp_template_t *t=&bank->word[word][example];
    memmove(t->frame,frames,count*sizeof(*frames));t->count=(uint8_t)count;
    return true;
}

static bool usable(const vp_template_t *t)
{
    return t->count>=VP_MIN_SPEECH_FRAMES && t->count<=VP_MAX_TEMPLATE_FRAMES;
}

void vp_matcher_begin(vp_matcher_t *m,const vp_bank_t *bank,const vp_options_t *options)
{
    if(!m)return;
    memset(m,0,sizeof(*m));m->bank=bank;m->options=options?*options:(vp_options_t){18,2};
    for(unsigned i=0;i<VP_TOTAL_EXAMPLES;i++){
        for(unsigned j=0;j<=VP_MAX_TEMPLATE_FRAMES;j++)m->cost[i][j]=VP_INF;
        m->cost[i][0]=0;
    }
}

static uint16_t distance(const vp_frame_t *a,const vp_frame_t *b)
{
    unsigned sum=0;
    for(unsigned i=0;i<VP_FEATURE_DIM;i++){
        int delta=(int)a->value[i]-(int)b->value[i];sum+=(unsigned)(delta<0?-delta:delta);
    }
    return (uint16_t)((sum+VP_FEATURE_DIM/2)/VP_FEATURE_DIM);
}

static void advance(vp_matcher_t *m,unsigned index,const vp_template_t *t,const vp_frame_t *frame)
{
    uint16_t *row=m->cost[index];uint8_t *path=m->path[index];
    uint16_t diagonal=row[0];uint8_t diagonal_path=path[0];row[0]=VP_INF;path[0]=0;
    for(unsigned j=1;j<=t->count;j++){
        uint16_t upper=row[j],best=diagonal;uint8_t upper_path=path[j],steps=diagonal_path;
        /* Prefer a diagonal on equal accumulated cost; it avoids needless warp. */
        if(upper<best){best=upper;steps=upper_path;}
        if(row[j-1]<best){best=row[j-1];steps=path[j-1];}
        row[j]=best==VP_INF?VP_INF:(uint16_t)(best+distance(frame,&t->frame[j-1]));
        path[j]=best==VP_INF?0:(uint8_t)(steps+1);
        diagonal=upper;diagonal_path=upper_path;
    }
}

bool vp_matcher_push(vp_matcher_t *m,const vp_frame_t *frame,bool voiced)
{
    if(!m)return false;
    if(!voiced)return true; /* VAD owns this decision; zero coefficients are not silence. */
    if(!frame){m->invalid=true;return false;}
    if(m->too_long || m->invalid)return false;
    if(m->speech_frames==VP_MAX_QUERY_FRAMES){m->too_long=true;return false;}
    m->speech_frames++;
    if(m->bank)for(unsigned w=0;w<VP_MAX_WORDS;w++)for(unsigned e=0;e<VP_EXAMPLES_PER_WORD;e++){
        const vp_template_t *t=&m->bank->word[w][e];
        if(usable(t))advance(m,w*VP_EXAMPLES_PER_WORD+e,t,frame);
    }
    return true;
}

vp_result_t vp_matcher_finish(const vp_matcher_t *m)
{
    vp_result_t r={VP_INVALID_INPUT,-1,0,VP_INF,VP_INF};
    if(!m)return r;
    r.speech_frames=m->speech_frames;
    if(m->invalid)return r;
    if(m->too_long){r.decision=VP_TOO_LONG;return r;}
    if(!m->speech_frames){r.decision=VP_NO_SPEECH;return r;}
    if(m->speech_frames<VP_MIN_SPEECH_FRAMES){r.decision=VP_TOO_SHORT;return r;}
    unsigned templates=0,durations=0;int winner=-1;
    if(m->bank)for(unsigned w=0;w<VP_MAX_WORDS;w++){
        uint16_t score=VP_INF;
        for(unsigned e=0;e<VP_EXAMPLES_PER_WORD;e++){
            const vp_template_t *t=&m->bank->word[w][e];if(!usable(t))continue;
            templates++;
            if(m->speech_frames*2u<t->count || m->speech_frames>t->count*2u)continue;
            durations++;
            unsigned i=w*VP_EXAMPLES_PER_WORD+e,steps=m->path[i][t->count];
            if(steps && m->cost[i][t->count]!=VP_INF){
                uint16_t normalized=(uint16_t)((m->cost[i][t->count]+steps/2)/steps);
                if(normalized<score)score=normalized;
            }
        }
        /* Examples of the same word are not separate competitors. */
        if(score<r.best_distance){r.runner_up_distance=r.best_distance;r.best_distance=score;winner=(int)w;}
        else if(score<r.runner_up_distance)r.runner_up_distance=score;
    }
    if(!templates){r.decision=VP_NO_TEMPLATE;return r;}
    if(!durations || winner<0){r.decision=VP_NO_DURATION_MATCH;return r;}
    if(r.best_distance>m->options.max_distance){r.decision=VP_TOO_DISTANT;return r;}
    if(r.runner_up_distance!=VP_INF &&
       (r.runner_up_distance<=r.best_distance || r.runner_up_distance-r.best_distance<m->options.min_margin)){
        r.decision=VP_AMBIGUOUS;return r;
    }
    r.decision=VP_ACCEPTED;r.word=winner;return r;
}

size_t vp_bank_bytes(void){return sizeof(vp_bank_t);}
size_t vp_matcher_bytes(void){return sizeof(vp_matcher_t);}
size_t vp_enrollment_buffer_bytes(void){return VP_MAX_TEMPLATE_FRAMES*sizeof(vp_frame_t);}
