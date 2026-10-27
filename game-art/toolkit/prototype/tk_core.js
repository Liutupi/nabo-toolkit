/* NABO 工具箱 · rules reference (DESIGN.md). Pure model: no canvas, no audio,
 * no wall clock — every call takes `now` in ms. Firmware tk_model.c must
 * replay traces recorded from this file step for step. */
(function (root) {
  'use strict';
  const H = root.TKHID;

  const MENU = ['macro', 'ppt', 'meet', 'media', 'cam', 'card', 'conn', 'set'];
  const TOOLS = new Set(['ppt', 'meet', 'media', 'cam', 'macro', 'card']);
  const TALK_MIN = [5, 10, 15, 20, 30, 45, 60];
  const SLEEP = [5, 15, 30, 0];              // minutes; 0 = 连接时不休眠
  const CAM_DELAYS = [0, 3, 10];
  const BURST = { count: 5, gapMs: 600 };
  const BOOT_MS = 5500, VOICE_AT_MS = 1400;    // Full welcome clip; any key skips.
  const PAIR_MS = 60000, TOAST_MS = 1200, ERR_MS = 1500, REACT_MS = 500;
  const MAX_SLOTS = 3, MAX_CARDS = 3;

  function create(now) {
    return {
      page: 'boot', menu: 0, lastInput: now || 0,
      boot: { start: now || 0, voiced: false },
      slots: [{ name: 'MacBook', os: 'mac' }, { name: 'iPhone', os: 'ios' }, null],
      bindOrder: [0, 1],  // Oldest pairing first; ordinary reconnects do not reorder.
      active: 0, connected: true, pairing: null, connSel: 0, confirmDel: -1, osPick: null,
      settings: { beep: true, voice: true, talk: 1, sleep: 3 }, setSel: 0,
      ppt: { running: false, startMs: 0, accMs: 0, pages: 1, black: false },
      meet: { app: 0 },
      cam: { delay: 0, endMs: 0, lastSec: 0, burstLeft: 0, nextShot: 0, shots: 0 },
      macro: { group: 0 },
      groups: null,          // null = built-in H.MACRO_GROUPS; set by the config page
      card: { idx: 0, zoom: false },
      cards: [
        { title: '名片', name: 'NABO', line: 'AI Passport 小助手', qr: 'https://ai-passport.folotoy.cn' },
        { title: 'Wi-Fi', name: 'NABO-Guest', line: '手机相机扫码直接连上', qr: 'WIFI:T:WPA;S:NABO-Guest;P:nabo2026;;' },
        { title: '主页', name: 'github.com/Liutupi', line: '我的开源项目', qr: 'https://github.com/Liutupi' },
      ],
      toast: null, react: null, hit: null,
    };
  }

  const os = (st) => (st.slots[st.active] || { os: 'win' }).os;
  const toast = (st, now, text, kind) =>
    (st.toast = { text, kind: kind || 'ok', until: now + (kind === 'err' ? ERR_MS : TOAST_MS) });
  const beep = (out, st, f, ms) => { if (st.settings.beep) out.push({ t: 'beep', f, ms: ms || 40 }); };

  /* Send one spec. Returns false (and shows why) when nothing could be sent. */
  function send(out, st, now, spec, label, key) {
    if (!st.connected) { toast(st, now, '未连接 · 去菜单选「连接」', 'err'); return false; }
    const p = root.TKConfig ? root.TKConfig.resolve(spec, os(st)) : H.resolve(spec, os(st));
    if (!p) { toast(st, now, '这个设备没有对应快捷键', 'err'); return false; }
    const chord = H.chordLabel(p, os(st));
    const packets = p.kind === 'text' ? H.textPackets(p.text) : [p];
    for (const q of packets) out.push({ t: 'hid', kind: q.kind, mod: q.mod, usage: q.usage,
                                        bytes: H.reportBytes(q), label: label + ' · ' + chord });
    toast(st, now, '→ ' + chord + '  ' + label);
    st.react = { until: now + REACT_MS, key };
    if (key) st.hit = { key, until: now + 250 };
    return true;
  }

  const groups = (st) => st.groups || H.MACRO_GROUPS;

  /* Config written by the config page (same JSON the firmware will keep in NVS). */
  function applyConfig(st, cfg) {
    let valid;
    try { valid = root.TKConfig.validate(cfg); } catch (_) { return false; }
    st.groups = valid.groups;
    st.cards = valid.cards;
    st.macro.group = Math.min(st.macro.group, groups(st).length - 1);
    st.card.idx = Math.min(st.card.idx, st.cards.length - 1);
    return true;
  }

  function pptElapsed(st, now) { return st.ppt.accMs + (st.ppt.running ? now - st.ppt.startMs : 0); }
  function pptStart(p, now) { Object.assign(p, { running: true, startMs: now, accMs: 0, pages: 1, black: false }); }

  function onPpt(st, k, now, out) {
    const p = st.ppt, T = H.PPT;
    if (k === 'up' || k === 'down') {
      if (!send(out, st, now, k === 'up' ? T.prev : T.next, k === 'up' ? '上一页' : '下一页', k)) return;
      if (!p.running && pptElapsed(st, now) === 0) pptStart(p, now);
      p.pages = Math.max(1, p.pages + (k === 'up' ? -1 : 1));
    } else if (k === 'ok') {
      if (send(out, st, now, T.black, p.black ? '恢复画面' : '黑屏', k)) p.black = !p.black;
    } else if (k === 'long_ok') {
      if (send(out, st, now, T.start, '开始放映', 'ok')) pptStart(p, now);
    } else if (k === 'long_down') {
      if (send(out, st, now, T.end, '结束放映', 'down') && p.running) {
        p.accMs = pptElapsed(st, now); p.running = false; p.black = false;
      }
    }
  }

  function onMeet(st, k, now, out) {
    if (k === 'long_ok') {
      st.meet.app = (st.meet.app + 1) % H.MEET_APPS.length;
      toast(st, now, '会议软件：' + H.MEET_APPS[st.meet.app].name); beep(out, st, 880); return;
    }
    const field = { ok: 'mute', up: 'cam', down: 'hand' }[k];
    if (!field) return;
    if (!H.isDesktop(os(st))) { toast(st, now, '会议快捷键只支持电脑', 'err'); return; }
    const app = H.MEET_APPS[st.meet.app], label = { mute: '静音切换', cam: '摄像头切换', hand: '举手' }[field];
    if (!app[field]) { toast(st, now, app.name + '没有' + label + '快捷键', 'err'); return; }
    send(out, st, now, app[field], label, k);
  }

  function onMedia(st, k, now, out) {
    const m = H.MEDIA_KEYS[k];
    if (m) send(out, st, now, m, m.label, k.replace('long_', ''));
  }

  function camShoot(st, now, out) {
    if (send(out, st, now, H.SHUTTER, '快门', 'ok')) { st.cam.shots++; out.push({ t: 'beep', f: 1568, ms: 120 }); }
  }
  function onCam(st, k, now, out) {
    const c = st.cam, counting = c.endMs > 0;
    if (k === 'ok' && counting) { c.endMs = 0; toast(st, now, '已取消'); beep(out, st, 440); return; }
    if (counting || c.burstLeft > 0) return;
    if (k === 'up') {
      c.delay = (c.delay + 1) % CAM_DELAYS.length;
      toast(st, now, CAM_DELAYS[c.delay] ? '延时 ' + CAM_DELAYS[c.delay] + ' 秒' : '不延时'); beep(out, st, 880);
    } else if (!st.connected && (k === 'ok' || k === 'down')) {
      toast(st, now, '未连接 · 去菜单选「连接」', 'err');
    } else if (k === 'ok') {
      const d = CAM_DELAYS[c.delay];
      if (!d) camShoot(st, now, out);
      else { c.endMs = now + d * 1000; c.lastSec = d; out.push({ t: 'beep', f: 988, ms: 60 }); }
    } else if (k === 'down') {
      c.burstLeft = BURST.count; c.nextShot = now;
    }
  }

  function onMacro(st, k, now, out) {
    const G = groups(st), n = G.length;
    if (k === 'long_ok' || k === 'long_down') {
      st.macro.group = (st.macro.group + (k === 'long_ok' ? 1 : n - 1)) % n;
      toast(st, now, '第 ' + (st.macro.group + 1) + ' 组 · ' + G[st.macro.group].name);
      beep(out, st, 880); return;
    }
    const b = G[st.macro.group][k];
    if (b) send(out, st, now, b, b.label, k);
  }

  function onCard(st, k, now, out) {
    const c = st.card, n = Math.min(st.cards.length, MAX_CARDS);
    if (k === 'ok') { c.zoom = !c.zoom; beep(out, st, 880); }
    else if (!c.zoom && (k === 'up' || k === 'down')) { c.idx = (c.idx + (k === 'up' ? n - 1 : 1)) % n; beep(out, st, 660); }
  }

  /* ---- 连接 ---- */
  function connRows(st) { return MAX_SLOTS + 1; }   // 3 slots + 配对新设备
  function startPairing(st, now) {
    if (st.slots.every(Boolean)) toast(st, now, '配对成功后替换 ' + st.slots[st.bindOrder[0]].name);
    st.connected = false; st.pairing = { until: now + PAIR_MS, passkey: null };
  }
  function onConn(st, k, now, out) {
    if (st.confirmDel >= 0) {
      if (k === 'ok') {
        const i = st.confirmDel; st.slots[i] = null;
        st.bindOrder = st.bindOrder.filter((index) => index !== i);
        if (st.active === i) st.connected = false;
        toast(st, now, '已删除配对');
      }
      st.confirmDel = -1; return;
    }
    if (st.pairing) { if (k === 'ok') { st.pairing = null; toast(st, now, '已停止配对'); } return; }
    const i = st.connSel, slot = st.slots[i];
    if (k === 'up' || k === 'down') { st.connSel = (i + (k === 'up' ? connRows(st) - 1 : 1)) % connRows(st); beep(out, st, 660); }
    else if (k === 'ok') {
      if (i === MAX_SLOTS || !slot) startPairing(st, now);
      else { st.active = i; st.connected = true; toast(st, now, '已连接 ' + slot.name); }
      beep(out, st, 880);
    } else if (k === 'long_ok' && slot) st.osPick = { slot: i, sel: H.OS_LIST.indexOf(slot.os) };
    else if (k === 'long_down' && slot) st.confirmDel = i;
  }
  function onOsPick(st, k, now, out) {
    const p = st.osPick, n = H.OS_LIST.length;
    if (k === 'up' || k === 'down') p.sel = (p.sel + (k === 'up' ? n - 1 : 1)) % n;
    else if (k === 'long_up') st.osPick = null;
    else if (k === 'ok') {
      st.slots[p.slot].os = H.OS_LIST[p.sel]; st.osPick = null;
      toast(st, now, '设备类型：' + H.OS_NAME[H.OS_LIST[p.sel]]);
    }
    beep(out, st, 660);
  }

  /* ---- 设置 ---- */
  const SET_ROWS = 5;   // 提示音 · 开机语音 · 演讲时长 · 自动休眠 · 关于
  function onSet(st, k, now, out) {
    const s = st.settings;
    if (k === 'up' || k === 'down') st.setSel = (st.setSel + (k === 'up' ? SET_ROWS - 1 : 1)) % SET_ROWS;
    else if (k === 'ok') {
      if (st.setSel === 0) s.beep = !s.beep;
      else if (st.setSel === 1) s.voice = !s.voice;
      else if (st.setSel === 2) s.talk = (s.talk + 1) % TALK_MIN.length;
      else if (st.setSel === 3) s.sleep = (s.sleep + 1) % SLEEP.length;
    }
    beep(out, st, 660);
  }

  const HANDLERS = { ppt: onPpt, meet: onMeet, media: onMedia, cam: onCam, macro: onMacro, card: onCard, conn: onConn, set: onSet };

  /* key ∈ up | down | ok | long_up | long_down | long_ok */
  function press(st, key, now) {
    const out = [];
    st.lastInput = now;
    if (st.osPick) { onOsPick(st, key, now, out); return out; }
    if (st.page === 'boot') { st.page = 'menu'; return out; }   // any key skips; nothing is sent
    if (st.page === 'menu') {
      if (key === 'up' || key === 'down') { st.menu = (st.menu + (key === 'up' ? MENU.length - 1 : 1)) % MENU.length; beep(out, st, 660); }
      else if (key === 'ok') { st.page = MENU[st.menu]; st.toast = null; beep(out, st, 880); }
      return out;
    }
    if (key === 'long_up') {
      if (st.pairing) { st.pairing = null; toast(st, now, '已停止配对'); }
      else if (st.page === 'card' && st.card.zoom) st.card.zoom = false;
      else { st.cam.endMs = 0; st.cam.burstLeft = 0; st.confirmDel = -1; st.page = 'menu'; st.toast = null; }
      beep(out, st, 523); return out;
    }
    HANDLERS[st.page](st, key, now, out);
    return out;
  }

  /* Timers: camera countdown and burst, pairing timeout, expiring overlays. */
  function tick(st, now) {
    const out = [], c = st.cam;
    if (st.page === 'boot') {
      const t = now - st.boot.start;
      if (!st.boot.voiced && t >= VOICE_AT_MS) {
        st.boot.voiced = true;
        if (st.settings.voice) out.push({ t: 'voice', id: 'boot-welcome', text: '那波，陪你遥控万物！' });
      }
      if (t >= BOOT_MS) st.page = 'menu';
    }
    if (c.endMs > 0) {
      const left = Math.ceil((c.endMs - now) / 1000);
      if (now >= c.endMs) { c.endMs = 0; camShoot(st, now, out); }
      else if (left < c.lastSec) { c.lastSec = left; out.push({ t: 'beep', f: 988, ms: 60 }); }
    }
    while (c.burstLeft > 0 && now >= c.nextShot) {
      camShoot(st, now, out); c.burstLeft--; c.nextShot += BURST.gapMs;
      if (!st.connected) c.burstLeft = 0;
    }
    if (st.pairing && now >= st.pairing.until) { st.pairing = null; toast(st, now, '配对超时', 'err'); }
    if (st.toast && now >= st.toast.until) st.toast = null;
    if (st.react && now >= st.react.until) st.react = null;
    if (st.hit && now >= st.hit.until) st.hit = null;
    return out;
  }

  /* Simulated radio events from the host side (prototype only). */
  function sim(st, ev, now, arg) {
    if (ev === 'paired' && st.pairing) {
      const empty = st.slots.indexOf(null);
      const i = empty >= 0 ? empty : st.bindOrder[0];
      st.slots[i] = { name: arg || '新设备 ' + (i + 1), os: 'win' };
      st.bindOrder = st.bindOrder.filter((index) => index !== i).concat(i);
      st.pairing = null; st.active = i; st.connected = true; st.connSel = i;
      st.osPick = { slot: i, sel: 1 };
    } else if (ev === 'passkey' && st.pairing) {
      const valid = (Number.isInteger(arg) && arg >= 0 && arg <= 999999) ||
        (typeof arg === 'string' && /^\d{6}$/.test(arg));
      if (valid) st.pairing.passkey = String(arg).padStart(6, '0');
    } else if (ev === 'disconnect') st.connected = false;
    else if (ev === 'reconnect' && !st.pairing && st.slots[st.active]) st.connected = true;
    else if (ev === 'wake') {
      st.page = 'boot'; st.boot = { start: now, voiced: false }; st.osPick = null;
      st.lastInput = now; st.connected = false; st.pairing = null;
    }
  }

  function sleepDue(st, now) {
    if (st.ppt.running || st.cam.endMs > 0 || st.pairing) return false;
    const m = SLEEP[st.settings.sleep];
    const limit = (m === 0 ? (st.connected ? Infinity : 5) : m) * 60000;
    return now - st.lastInput >= limit;
  }

  root.TK = {
    MENU, TOOLS, TALK_MIN, SLEEP, CAM_DELAYS, MAX_SLOTS, BOOT_MS, VOICE_AT_MS,
    create, press, tick, sim, sleepDue, pptElapsed, os, groups, applyConfig,
  };
})(typeof window !== 'undefined' ? window : globalThis);
