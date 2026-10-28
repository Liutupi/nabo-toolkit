#include "tk_ble_diag.h"
#include <stdatomic.h>

static atomic_uint s_sequence,s_interval,s_latency,s_supervision;
static atomic_uint s_tx_completed,s_tx_errors,s_press_errors,s_release_errors;
static atomic_int s_enqueue_error,s_tx_error;

void tk_ble_diag_reset(void)
{
    atomic_store(&s_sequence,0);atomic_store(&s_interval,0);atomic_store(&s_latency,0);atomic_store(&s_supervision,0);
    atomic_store(&s_tx_completed,0);atomic_store(&s_tx_errors,0);atomic_store(&s_press_errors,0);atomic_store(&s_release_errors,0);
    atomic_store(&s_enqueue_error,0);atomic_store(&s_tx_error,0);
}
void tk_ble_diag_link(bool valid,uint16_t interval,uint16_t latency,uint16_t supervision)
{
    atomic_fetch_add(&s_sequence,1);
    atomic_store(&s_interval,valid?interval:0);atomic_store(&s_latency,valid?latency:0);atomic_store(&s_supervision,valid?supervision:0);
    atomic_fetch_add(&s_sequence,1);
}
void tk_ble_diag_enqueue(bool release,int status)
{
    if(!status)return;
    atomic_fetch_add(release?&s_release_errors:&s_press_errors,1);atomic_store(&s_enqueue_error,status);
}
void tk_ble_diag_tx(int status)
{
    if(status){atomic_fetch_add(&s_tx_errors,1);atomic_store(&s_tx_error,status);}
    else atomic_fetch_add(&s_tx_completed,1);
}
tk_ble_diag_t tk_ble_diag_snapshot(void)
{
    tk_ble_diag_t d={.tx_completed=atomic_load(&s_tx_completed),.tx_errors=atomic_load(&s_tx_errors),
        .press_errors=atomic_load(&s_press_errors),.release_errors=atomic_load(&s_release_errors),
        .enqueue_error=atomic_load(&s_enqueue_error),.tx_error=atomic_load(&s_tx_error)};
    // Never spin waiting for a lower-priority host task preempted mid-update.
    for(int i=0;i<2;i++){
        unsigned before=atomic_load(&s_sequence);if(before&1)continue;
        unsigned interval=atomic_load(&s_interval),latency=atomic_load(&s_latency),supervision=atomic_load(&s_supervision);
        if(before!=atomic_load(&s_sequence))continue;
        if(interval && supervision){d.params_valid=true;d.interval_us=interval*1250u;d.latency=latency;d.supervision_ms=supervision*10u;}
        break;
    }
    return d;
}
