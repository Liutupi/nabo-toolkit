/* Shared F2 schema. Defaults still come directly from tk_hid.js and tk_core.js. */
(function (root) {
  'use strict';
  const LIMIT = Object.freeze({ groups: 6, cards: 3, name: 8, label: 8, title: 6, cardName: 24, line: 32, text: 64, qr: 160, bytes: 4000 });
  const bytes = (s) => new TextEncoder().encode(s);
  const fail = (code) => { throw new Error(code); };
  function object(o, keys) {
    if (!o || Array.isArray(o) || typeof o !== 'object') fail('object');
    if (Object.keys(o).some((k) => !keys.includes(k))) fail('keys');
  }
  function string(s, max, byteMax, empty = true, newline = false) {
    if (typeof s !== 'string' || (!empty && !s.length) || [...s].length > max || bytes(s).length > byteMax) fail('string');
    for (const c of s) { const u = c.codePointAt(0); if ((u < 32 && !(newline && u === 10)) || u === 127 || (u >= 0xd800 && u <= 0xdfff)) fail('string'); }
    return s;
  }
  function number(n, lo, hi) { if (!Number.isInteger(n) || n < lo || n > hi) fail('number'); return n; }
  function combo(o) {
    if (o == null) return null;
    object(o, ['mod', 'key']); const mod = number(o.mod, 0, 255), key = number(o.key, 0, 0x73);
    if (key > 0 && key < 4) fail('key');
    return { mod, key };
  }
  function slot(o) {
    object(o, ['label', 'mac', 'win', 'media', 'text']);
    const label = string(o.label, LIMIT.label, 32);
    if ('media' in o) {
      if ('text' in o || 'mac' in o || 'win' in o || ![0xcd,0xb5,0xb6,0xe9,0xea].includes(o.media)) fail('media');
      return { label, media: o.media };
    }
    if ('text' in o) {
      if ('mac' in o || 'win' in o) fail('text');
      const text = string(o.text, LIMIT.text, LIMIT.text, true, true);
      if ([...text].some((c) => c.codePointAt(0) > 126)) fail('text');
      return { label, text };
    }
    return { label, mac: combo(o.mac), win: combo(o.win) };
  }
  function validate(c) {
    object(c, ['v', 'groups', 'cards']); if (c.v !== 1) fail('version');
    if (!Array.isArray(c.groups) || !c.groups.length || c.groups.length > LIMIT.groups) fail('groups');
    if (!Array.isArray(c.cards) || !c.cards.length || c.cards.length > LIMIT.cards) fail('cards');
    const groups = c.groups.map((g) => { object(g, ['name','up','ok','down']); return {
      name: string(g.name, LIMIT.name, 32, false), up: slot(g.up), ok: slot(g.ok), down: slot(g.down) }; });
    const cards = c.cards.map((c) => { object(c, ['title','name','line','qr']); return {
      title: string(c.title, LIMIT.title, 24, false), name: string(c.name, LIMIT.cardName, 95),
      line: string(c.line, LIMIT.line, 191), qr: string(c.qr, LIMIT.qr, LIMIT.qr, false, true) }; });
    const result = { v: 1, groups, cards };
    if (bytes(JSON.stringify(result)).length > LIMIT.bytes) fail('size');
    return result;
  }
  // Inspect syntax before JSON.parse loses duplicate keys or numeric spelling.
  function parse(text) {
    if (typeof text !== 'string' || !text.length || bytes(text).length > LIMIT.bytes) fail('size');
    let i = 0;
    const space = () => { while (/[\x20\t\r\n]/.test(text[i] || '\0')) i++; };
    function quoted() {
      const start = i++; let escaped = false;
      while (i < text.length) {
        const ch = text[i++];
        if (!escaped && ch === '"') { const value = JSON.parse(text.slice(start, i)); if (value.includes('\0')) fail('json'); return value; }
        if (!escaped && ch === '\\') escaped = true; else escaped = false;
      }
      fail('json');
    }
    function value(depth) {
      if (depth > 8) fail('depth'); space(); const ch = text[i];
      if (ch === '"') { quoted(); return; }
      if (ch === '{' || ch === '[') {
        const obj = ch === '{', end = obj ? '}' : ']'; i++; space(); const seen = new Set();
        if (text[i] === end) { i++; return; }
        for (;;) {
          if (obj) { space(); if (text[i] !== '"') fail('json'); const key = quoted(); if (seen.has(key)) fail('keys'); seen.add(key); space(); if (text[i++] !== ':') fail('json'); }
          value(depth + 1); space(); const separator = text[i++]; if (separator === end) return; if (separator !== ',') fail('json');
        }
      }
      const tail = text.slice(i), token = /^(?:0|[1-9][0-9]*|true|false|null)/.exec(tail);
      if (!token) fail('json'); i += token[0].length;
    }
    value(0); space(); if (i !== text.length) fail('json');
    return validate(JSON.parse(text));
  }
  function defaults() {
    const H = root.TKHID, pick = (s, os) => { const p = H.resolve(s, os); return p ? { mod: p.mod, key: p.usage } : null; };
    const slot = (s) => s.media || s.text != null ? { ...s } : { label: s.label, mac: pick(s, 'mac'), win: pick(s, 'win') };
    return validate({ v: 1, groups: H.MACRO_GROUPS.map((g) => ({ name: g.name, up: slot(g.up), ok: slot(g.ok), down: slot(g.down) })), cards: root.TK.create(0).cards });
  }
  function withDefaultGroups(config) {
    const current = validate(config);
    return validate({ ...current, groups: defaults().groups });
  }
  // Explicit opt-in only: retain every existing group and card, and put the
  // bridge group immediately before Typeless so long-OK can advance to it.
  function withAssistantGroup(config) {
    const current = validate(config);
    if (current.groups.some((g) => g.name === 'AI助手')) fail('duplicate');
    if (current.groups.length >= LIMIT.groups) fail('groups');
    const slot = (label, key) => ({ label, mac: { mod: 0, key }, win: { mod: 0, key } });
    const group = { name: 'AI助手', up: slot('Codex', 0x68), down: slot('Claude', 0x69), ok: slot('Grok Bot', 0x6a) };
    const pos = current.groups.findIndex((g) => g.name === 'Typeless' || g.name === '语音输入');
    const groups = current.groups.slice(); groups.splice(pos < 0 ? groups.length : pos, 0, group);
    return validate({ ...current, groups });
  }
  function resolve(s, os) {
    if (s && ('mac' in s || 'win' in s)) return root.TKHID.resolve(root.TKHID.isApple(os) ? s.mac : s.win, os);
    return root.TKHID.resolve(s, os);
  }
  function crc32(data) { let c = 0xffffffff; for (const b of data) { c ^= b; for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1)); } return (c ^ 0xffffffff) >>> 0; }
  root.TKConfig = { LIMIT, bytes, parse, validate, defaults, withDefaultGroups, withAssistantGroup, resolve, crc32, encode: (c) => JSON.stringify(validate(c)) };
})(typeof window !== 'undefined' ? window : globalThis);
