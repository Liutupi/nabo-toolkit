/* One ADC button at a time. A long press fires once at 500ms, including a
 * release arriving before the next animation tick. No DOM or wall clock. */
(function(root) {
  'use strict';
  const LONG_MS=500, KEYS=new Set(['up','down','ok']);
  const create=()=>({active:null,at:0,fired:false});
  function down(st,key,now) {
    if (st.active || !KEYS.has(key)) return;
    st.active=key; st.at=now; st.fired=false;
  }
  function tick(st,now) {
    if (!st.active || st.fired || now-st.at<LONG_MS) return [];
    st.fired=true; return ['long_'+st.active];
  }
  function up(st,key,now) {
    if (key!==st.active) return [];
    const out=tick(st,now);
    if (!st.fired) out.push(key);
    cancel(st); return out;
  }
  function cancel(st) { st.active=null; st.fired=false; }
  root.TKButtons={LONG_MS,create,down,tick,up,cancel};
})(typeof window!=='undefined'?window:globalThis);
