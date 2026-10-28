/* NABO 工具箱 · HID tables (rules reference, mirrored by firmware tk_hid_map.c).
 * Report 1 = 8-byte boot keyboard, report 2 = 16-bit Consumer usage, same as
 * the radio edition's nabo_keys. All shortcut tables are data, not code. */
(function (root) {
  'use strict';

  const MOD = { ctrl: 0x01, shift: 0x02, alt: 0x04, gui: 0x08, rctrl: 0x10, rshift: 0x20, ralt: 0x40, rgui: 0x80 };
  const KEY = {
    ENTER: 0x28, ESC: 0x29, TAB: 0x2b, SPACE: 0x2c, LBRACKET: 0x2f, RBRACKET: 0x30,
    F5: 0x3e, PGUP: 0x4b, PGDN: 0x4e, RIGHT: 0x4f, DOWN: 0x51, UP: 0x52,
    F13: 0x68, F14: 0x69, F15: 0x6a, F16: 0x6b, F17: 0x6c, F18: 0x6d,
  };
  const MEDIA = { PLAY: 0xcd, NEXT: 0xb5, PREV: 0xb6, VOLUP: 0xe9, VOLDN: 0xea };
  const OS_LIST = ['mac', 'win', 'ios', 'android'];
  const OS_NAME = { mac: 'Mac', win: 'Windows', ios: 'iPhone·iPad', android: '安卓' };

  const L = (c) => 0x04 + c.charCodeAt(0) - 97; // a..z
  const isApple = (os) => os === 'mac' || os === 'ios';
  const isDesktop = (os) => os === 'mac' || os === 'win';

  /* Resolve a spec into a packet for one OS. A spec is one of
   *   {mods:[...], key}            'main' = Cmd on Apple, Ctrl elsewhere
   *   {mod, key}                   raw HID modifier byte (recorded on the config page)
   *   {media}                      consumer usage
   *   {text}                       ASCII string, typed key by key
   *   {mac:spec, win:spec}         per-family override (ios→mac, android→win)
   * Returns null when the spec has no binding for this OS. */
  function resolve(spec, os) {
    if (!spec) return null;
    if (spec.mac || spec.win) return resolve(isApple(os) ? spec.mac : spec.win, os);
    if (spec.media) return { kind: 'media', usage: spec.media };
    if (spec.text != null) return { kind: 'text', text: spec.text };
    if (typeof spec.mod === 'number') return { kind: 'key', mod: spec.mod, usage: spec.key || 0 };
    let mod = 0;
    for (const m of spec.mods || []) mod |= m === 'main' ? (isApple(os) ? MOD.gui : MOD.ctrl) : MOD[m];
    return { kind: 'key', mod, usage: spec.key || 0 };
  }

  const KEY_NAMES = {
    0x28: 'Enter', 0x29: 'Esc', 0x2b: 'Tab', 0x2c: 'Space', 0x2f: '[', 0x30: ']',
    0x2a: 'Backspace', 0x3c: 'F3', 0x46: 'PrtSc', 0x4b: 'PgUp', 0x4c: 'Del', 0x4e: 'PgDn', 0x4f: '→', 0x50: '←', 0x51: '↓', 0x52: '↑',
  };
  function keyName(u) {
    if (u >= 0x04 && u <= 0x1d) return String.fromCharCode(65 + u - 0x04);
    if (u >= 0x1e && u <= 0x26) return String(u - 0x1d);
    if (u === 0x27) return '0';
    if (u >= 0x3a && u <= 0x45) return 'F' + (u - 0x39);
    if (u >= 0x68 && u <= 0x73) return 'F' + (u - 0x68 + 13);
    return KEY_NAMES[u] || u.toString(16).padStart(2, '0');
  }
  const MEDIA_NAMES = { 0xcd: '播放/暂停', 0xb5: '下一曲', 0xb6: '上一曲', 0xe9: '音量+', 0xea: '音量−' };

  function chordLabel(p, os) {
    if (!p) return '';
    if (p.kind === 'media') return MEDIA_NAMES[p.usage] || 'MEDIA';
    if (p.kind === 'text') return '输入 "' + (p.text.length > 10 ? p.text.slice(0, 9) + '…' : p.text) + '"';
    const apple = isApple(os), parts = [];
    const alt = apple ? 'Option' : 'Alt', gui = apple ? 'Cmd' : 'Win';
    if (p.mod & MOD.ctrl) parts.push('Ctrl');
    if (p.mod & MOD.rctrl) parts.push('右Ctrl');
    if (p.mod & MOD.alt) parts.push(alt);
    if (p.mod & MOD.ralt) parts.push('右' + alt);
    if (p.mod & MOD.shift) parts.push('Shift');
    if (p.mod & MOD.rshift) parts.push('右Shift');
    if (p.mod & MOD.gui) parts.push(gui);
    if (p.mod & MOD.rgui) parts.push('右' + gui);
    if (p.usage) parts.push(keyName(p.usage));
    return parts.join('+');
  }

  /* US layout ASCII → [shift, usage]. */
  const SYMBOLS = {
    ' ': [0, 0x2c], '-': [0, 0x2d], '_': [1, 0x2d], '=': [0, 0x2e], '+': [1, 0x2e],
    '[': [0, 0x2f], '{': [1, 0x2f], ']': [0, 0x30], '}': [1, 0x30], '\\': [0, 0x31], '|': [1, 0x31],
    ';': [0, 0x33], ':': [1, 0x33], "'": [0, 0x34], '"': [1, 0x34], '`': [0, 0x35], '~': [1, 0x35],
    ',': [0, 0x36], '<': [1, 0x36], '.': [0, 0x37], '>': [1, 0x37], '/': [0, 0x38], '?': [1, 0x38],
    '!': [1, 0x1e], '@': [1, 0x1f], '#': [1, 0x20], '$': [1, 0x21], '%': [1, 0x22],
    '^': [1, 0x23], '&': [1, 0x24], '*': [1, 0x25], '(': [1, 0x26], ')': [1, 0x27], '\n': [0, 0x28],
  };
  function charKey(ch) {
    if (ch >= 'a' && ch <= 'z') return [0, L(ch)];
    if (ch >= 'A' && ch <= 'Z') return [1, L(ch.toLowerCase())];
    if (ch >= '1' && ch <= '9') return [0, 0x1e + ch.charCodeAt(0) - 49];
    if (ch === '0') return [0, 0x27];
    return SYMBOLS[ch] || null;
  }
  /* Expand a text packet into keyboard packets; unsupported chars are dropped. */
  function textPackets(text) {
    const out = [];
    for (const ch of text) {
      const k = charKey(ch);
      if (k) out.push({ kind: 'key', mod: k[0] ? MOD.shift : 0, usage: k[1] });
    }
    return out;
  }
  function reportBytes(p) {
    if (p.kind === 'media') return [p.usage & 255, p.usage >> 8];
    return [p.mod, 0, p.usage, 0, 0, 0, 0, 0];
  }

  /* ---- Tool tables ---------------------------------------------------- */
  const PPT = {
    prev: { mods: [], key: KEY.PGUP }, next: { mods: [], key: KEY.PGDN },
    black: { mods: [], key: L('b') }, end: { mods: [], key: KEY.ESC },
    start: { win: { mods: [], key: KEY.F5 }, mac: { mods: ['gui', 'shift'], key: KEY.ENTER } },
  };

  /* Meeting shortcuts. null = the app has no shortcut. All unverified (DESIGN 5.2). */
  const MEET_APPS = [
    { name: '腾讯会议',
      mute: { win: { mods: ['alt'], key: L('m') }, mac: { mods: ['gui', 'shift'], key: L('m') } },
      cam: { win: { mods: ['alt'], key: L('v') }, mac: { mods: ['gui', 'shift'], key: L('v') } },
      hand: null },
    { name: '飞书',
      mute: { win: { mods: ['ctrl', 'shift'], key: L('d') }, mac: { mods: ['gui', 'shift'], key: L('d') } },
      cam: { win: { mods: ['ctrl', 'shift'], key: L('v') }, mac: { mods: ['gui', 'shift'], key: L('v') } },
      hand: null },
    { name: 'Zoom',
      mute: { win: { mods: ['alt'], key: L('a') }, mac: { mods: ['gui', 'shift'], key: L('a') } },
      cam: { win: { mods: ['alt'], key: L('v') }, mac: { mods: ['gui', 'shift'], key: L('v') } },
      hand: { win: { mods: ['alt'], key: L('y') }, mac: { mods: ['alt'], key: L('y') } } },
    { name: 'Teams',
      mute: { mods: ['main', 'shift'], key: L('m') },
      cam: { mods: ['main', 'shift'], key: L('o') },
      hand: { mods: ['main', 'shift'], key: L('k') } },
  ];

  const MEDIA_KEYS = {
    up: { label: '音量 +', media: MEDIA.VOLUP }, down: { label: '音量 −', media: MEDIA.VOLDN },
    ok: { label: '播放 / 暂停', media: MEDIA.PLAY },
    long_ok: { label: '下一曲', media: MEDIA.NEXT }, long_down: { label: '上一曲', media: MEDIA.PREV },
  };
  const SHUTTER = { media: MEDIA.VOLUP };

  const B = (label, spec) => Object.assign({ label }, spec);
  /* Built-in groups, used until the config page writes its own. Typeless
   * defaults are the author's bindings (Mac: 右Option+M / 右Option+右Shift /
   * 右Option+Space); other people re-record them on the config page. */
  // Media > Douyin; use plain arrows on both computers and phones.
  const DOUYIN_KEYS = {
    up: B('上个视频', { mods: [], key: KEY.UP }),
    down: B('下个视频', { mods: [], key: KEY.DOWN }),
    ok: B('向右/快进', { mods: [], key: KEY.RIGHT }),
  };
  const MACRO_GROUPS = [
    { name: '截图',
      up: B('截屏', { mac: { mods: ['ctrl', 'gui', 'shift'], key: 0x21 }, win: { mods: ['gui', 'shift'], key: L('s') } }),
      ok: B('粘贴', { mods: ['main'], key: L('v') }),
      down: B('取消 Esc', { mods: [], key: KEY.ESC }) },
    { name: 'Typeless',
      up: B('翻译', { mods: ['ralt', 'rshift'], key: 0 }),
      ok: B('语音输入', { mac: { mods: ['ralt'], key: L('m') }, win: { mods: ['ralt'], key: 0 } }),
      down: B('随便问', { mods: ['ralt'], key: KEY.SPACE }) },
    { name: '剪映',
      up: B('分割', { mods: ['main'], key: L('b') }),
      ok: B('播放 / 暂停', { mods: [], key: KEY.SPACE }),
      down: B('撤销', { mods: ['main'], key: L('z') }) },
    // User-requested plain arrows for desktop and phone apps. The app decides
    // how an arrow behaves; Right is requested for the next chapter.
    { name: '微信读书',
      up: B('上一页', { mods: [], key: KEY.UP }),
      ok: B('下一章 →', { mods: [], key: KEY.RIGHT }),
      down: B('下一页', { mods: [], key: KEY.DOWN }) },
    { name: '编辑',
      up: B('撤销', { mods: ['main'], key: L('z') }),
      ok: B('复制', { mods: ['main'], key: L('c') }),
      down: B('全选', { mods: ['main'], key: L('a') }) },
  ];

  /* KeyboardEvent.code → HID usage, for recording on the config page. */
  const CODE_USAGE = (() => {
    const m = {};
    for (let i = 0; i < 26; i++) m['Key' + String.fromCharCode(65 + i)] = 0x04 + i;
    for (let i = 1; i <= 9; i++) m['Digit' + i] = 0x1d + i;
    m.Digit0 = 0x27;
    for (let i = 1; i <= 12; i++) m['F' + i] = 0x39 + i;
    for (let i = 13; i <= 24; i++) m['F' + i] = 0x68 + i - 13;
    Object.assign(m, {
      Enter: 0x28, Escape: 0x29, Backspace: 0x2a, Tab: 0x2b, Space: 0x2c, Minus: 0x2d, Equal: 0x2e,
      BracketLeft: 0x2f, BracketRight: 0x30, Backslash: 0x31, Semicolon: 0x33, Quote: 0x34,
      Backquote: 0x35, Comma: 0x36, Period: 0x37, Slash: 0x38, CapsLock: 0x39, PrintScreen: 0x46,
      ScrollLock: 0x47, Pause: 0x48, Insert: 0x49, Home: 0x4a, PageUp: 0x4b, Delete: 0x4c, End: 0x4d,
      PageDown: 0x4e, ArrowRight: 0x4f, ArrowLeft: 0x50, ArrowDown: 0x51, ArrowUp: 0x52,
    });
    return m;
  })();
  const CODE_MOD = {
    ControlLeft: MOD.ctrl, ShiftLeft: MOD.shift, AltLeft: MOD.alt, MetaLeft: MOD.gui,
    ControlRight: MOD.rctrl, ShiftRight: MOD.rshift, AltRight: MOD.ralt, MetaRight: MOD.rgui,
  };

  root.TKHID = {
    MOD, KEY, MEDIA, OS_LIST, OS_NAME, isApple, isDesktop, resolve, chordLabel, keyName,
    textPackets, reportBytes, PPT, MEET_APPS, MEDIA_KEYS, DOUYIN_KEYS, SHUTTER, MACRO_GROUPS, CODE_USAGE, CODE_MOD,
  };
})(typeof window !== 'undefined' ? window : globalThis);
