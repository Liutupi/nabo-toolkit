/* NABO 工具箱 · 配置页（原型）。
 * The JSON built here is what the firmware will store in NVS (namespace nabo_tk).
 * Prototype: saved to localStorage, picked up live by index.html.
 * Firmware stage: the same page writes it over Web Serial. */
(function () {
  'use strict';
  const H = window.TKHID;
  const STORE = 'nabo_tk_config_v1';
  const LIMIT = { groups: 6, name: 8, label: 6, text: 64, qr: 160, bytes: 4000 };
  const SLOTS = [['up', '↑'], ['ok', 'OK'], ['down', '↓']];
  const MODS = [['ctrl', 'Ctrl'], ['shift', 'Shift'], ['alt', 'Alt / Option'], ['gui', 'Win / Cmd'],
                ['rctrl', '右 Ctrl'], ['rshift', '右 Shift'], ['ralt', '右 Alt / Option'], ['rgui', '右 Win / Cmd']];
  const MEDIA = [[0xcd, '播放 / 暂停'], [0xb5, '下一曲'], [0xb6, '上一曲'], [0xe9, '音量 +'], [0xea, '音量 −']];
  const $ = (s, el) => (el || document).querySelector(s);
  const h = (tag, attrs, ...kids) => {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      if (attrs[k] == null) continue;
      if (k.startsWith('on')) e.addEventListener(k.slice(2), attrs[k]);
      else if (k === 'class') e.className = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    for (const c of kids) if (c != null) e.append(c);
    return e;
  };

  /* Built-in groups → raw per-family bindings. */
  function defaults() {
    const slot = (b) => {
      if (b.media || b.text != null) return Object.assign({}, b);
      const pick = (os) => { const p = H.resolve(b, os); return p && p.kind === 'key' ? { mod: p.mod, key: p.usage } : null; };
      return { label: b.label, mac: pick('mac'), win: pick('win') };
    };
    return {
      v: 1,
      groups: H.MACRO_GROUPS.map((g) => ({ name: g.name, up: slot(g.up), ok: slot(g.ok), down: slot(g.down) })),
      cards: window.TK.create(0).cards,
    };
  }
  function load() {
    try { const c = JSON.parse(localStorage.getItem(STORE)); if (c && c.v === 1) return c; } catch (e) { /* fall through */ }
    return defaults();
  }
  let cfg = load(), family = 'mac', recording = null;

  const kindOf = (s) => (s.media ? 'media' : s.text != null ? 'text' : 'combo');
  const chord = (b) => (b ? H.chordLabel({ kind: 'key', mod: b.mod, usage: b.key }, family) || '（未设置）' : '（未设置）');

  /* ---- 录键 ---- */
  function startRecord(slot, btn) {
    stopRecord();
    recording = { slot, btn, held: 0, peak: 0, done: false };
    btn.textContent = '请按组合键…（点别处取消）';
    btn.classList.add('rec');
  }
  function stopRecord() {
    if (!recording) return;
    recording.btn.classList.remove('rec');
    recording = null;
    render();
  }
  function commit(mod, key) {
    recording.slot[family] = { mod, key };
    status('已录入：' + chord(recording.slot[family]));
    stopRecord();
  }
  addEventListener('keydown', (e) => {
    if (!recording) return;
    e.preventDefault(); e.stopPropagation();
    const m = H.CODE_MOD[e.code];
    if (m) { recording.held |= m; recording.peak |= m; return; }
    const u = H.CODE_USAGE[e.code];
    if (u == null) { status('这个键工牌发不了：' + e.code, true); return; }
    commit(recording.held, u);
  }, true);
  addEventListener('keyup', (e) => {
    if (!recording) return;
    e.preventDefault();
    const m = H.CODE_MOD[e.code];
    if (!m) return;
    if (recording.peak) commit(recording.peak, 0);      // modifier-only chord, e.g. 右Option+右Shift
  }, true);
  addEventListener('mousedown', (e) => { if (recording && e.target !== recording.btn) stopRecord(); });

  /* ---- 渲染 ---- */
  function slotEditor(g, id, arrow) {
    const s = g[id], kind = kindOf(s);
    const label = h('input', { value: s.label || '', maxlength: LIMIT.label, class: 'label', placeholder: '名字',
      oninput: (e) => { s.label = e.target.value; } });
    const type = h('select', { onchange: (e) => {
      const k = e.target.value, lab = s.label;
      for (const key of Object.keys(s)) delete s[key];
      s.label = lab;
      if (k === 'media') s.media = 0xcd; else if (k === 'text') s.text = '';
      render();
    } }, ...[['combo', '组合键'], ['media', '多媒体键'], ['text', '输入文字']].map(([v, t]) =>
      h('option', Object.assign({ value: v }, v === kind ? { selected: '' } : {}), t)));
    let body;
    if (kind === 'media') {
      body = h('select', { onchange: (e) => { s.media = Number(e.target.value); } },
        ...MEDIA.map(([v, t]) => h('option', Object.assign({ value: v }, v === s.media ? { selected: '' } : {}), t)));
    } else if (kind === 'text') {
      body = h('input', { value: s.text, maxlength: LIMIT.text, class: 'text', placeholder: '只能英文、数字和符号',
        oninput: (e) => {
          const bad = [...e.target.value].filter((c) => !H.textPackets(c).length && c !== '\n');
          s.text = e.target.value;
          e.target.classList.toggle('bad', bad.length > 0);
          if (bad.length) status('工牌只能打英文和符号，这些字会被跳过：' + bad.join(''), true);
        } });
    } else {
      const btn = h('button', { class: 'rec-btn', onclick: () => startRecord(s, btn) }, chord(s[family]));
      body = h('span', { class: 'combo' }, btn,
        h('button', { class: 'small', title: '手动设置', onclick: () => manual(s) }, '手动'));
    }
    return h('div', { class: 'slot' }, h('span', { class: 'key' }, arrow), label, type, body);
  }

  function manual(s) {
    const cur = s[family] || { mod: 0, key: 0 };
    const dlg = $('#manual'), box = $('#manual-mods'), sel = $('#manual-key');
    box.replaceChildren(...MODS.map(([n, t]) => h('label', {},
      h('input', Object.assign({ type: 'checkbox', value: H.MOD[n] }, cur.mod & H.MOD[n] ? { checked: '' } : {})), t)));
    sel.replaceChildren(h('option', { value: 0 }, '（只按修饰键）'),
      ...Object.entries(H.CODE_USAGE).map(([code, u]) =>
        h('option', Object.assign({ value: u }, u === cur.key ? { selected: '' } : {}), code.replace(/^Key|^Digit/, ''))));
    dlg.onclose = () => {
      if (dlg.returnValue !== 'ok') return;
      let mod = 0;
      box.querySelectorAll('input:checked').forEach((c) => { mod |= Number(c.value); });
      s[family] = { mod, key: Number(sel.value) };
      render();
    };
    dlg.showModal();
  }

  function groupCard(g, i) {
    const n = cfg.groups.length;
    return h('div', { class: 'group' },
      h('div', { class: 'ghead' },
        h('span', { class: 'num' }, String(i + 1)),
        h('input', { value: g.name, maxlength: LIMIT.name, class: 'gname', oninput: (e) => { g.name = e.target.value; } }),
        h('button', { class: 'small', disabled: i === 0 ? '' : null, onclick: () => { move(i, -1); } }, '上移'),
        h('button', { class: 'small', onclick: () => { cfg.groups.splice(i, 1); render(); } }, '删除')),
      ...SLOTS.map(([id, arrow]) => slotEditor(g, id, arrow)));
  }
  function move(i, d) {
    const j = i + d; if (j < 0) return;
    [cfg.groups[i], cfg.groups[j]] = [cfg.groups[j], cfg.groups[i]]; render();
  }

  function cardEditor(c, i) {
    const f = (key, ph, max) => h('input', { value: c[key] || '', placeholder: ph, maxlength: max,
      oninput: (e) => { c[key] = e.target.value; } });
    const ssid = h('input', { placeholder: 'Wi-Fi 名称' }), pass = h('input', { placeholder: 'Wi-Fi 密码', type: 'password' });
    return h('div', { class: 'group' },
      h('div', { class: 'ghead' }, h('span', { class: 'num' }, String(i + 1)), f('title', '标题，如 微信', 6)),
      h('div', { class: 'grid2' }, f('name', '名字', 16), f('line', '一行说明', 20)),
      h('div', { class: 'qr' }, f('qr', '二维码内容：网址或文字', LIMIT.qr)),
      h('details', {}, h('summary', {}, '生成 Wi-Fi 二维码'),
        h('div', { class: 'row' }, ssid, pass,
          h('button', { class: 'small', onclick: () => {
            const esc = (v) => v.replace(/([\\;,:"])/g, '\\$1');
            c.qr = 'WIFI:T:WPA;S:' + esc(ssid.value) + ';P:' + esc(pass.value) + ';;';
            render();
          } }, '填入')),
        h('div', { class: 'hint' }, '密码会明文存进工牌，别人拿到工牌能看到。')));
  }

  function render() {
    document.querySelectorAll('[data-family]').forEach((b) => b.classList.toggle('on', b.dataset.family === family));
    $('#groups').replaceChildren(...cfg.groups.map(groupCard));
    $('#add').disabled = cfg.groups.length >= LIMIT.groups;
    $('#cards').replaceChildren(...cfg.cards.map(cardEditor));
    const bytes = new TextEncoder().encode(JSON.stringify(cfg)).length;
    $('#size').textContent = bytes + ' / ' + LIMIT.bytes + ' 字节';
    $('#size').classList.toggle('bad', bytes > LIMIT.bytes);
  }
  function status(t, bad) { const s = $('#status'); s.textContent = t; s.classList.toggle('bad', !!bad); }

  document.querySelectorAll('[data-family]').forEach((b) => b.addEventListener('click', () => { family = b.dataset.family; render(); }));
  $('#add').onclick = () => {
    cfg.groups.push({ name: '新分组', up: { label: '' }, ok: { label: '' }, down: { label: '' } }); render();
  };
  $('#reset').onclick = () => { cfg = defaults(); render(); status('已恢复默认（还没保存）'); };
  $('#save').onclick = () => {
    try {
      localStorage.setItem(STORE, JSON.stringify(cfg));
      status('已保存。打开着的工牌原型会马上换成新键位。');
    } catch (e) { status('保存失败：浏览器不让写本地存储', true); }
  };
  $('#export').onclick = () => {
    const a = h('a', { href: URL.createObjectURL(new Blob([JSON.stringify(cfg, null, 2)], { type: 'application/json' })),
      download: 'nabo-toolkit-config.json' });
    a.click(); URL.revokeObjectURL(a.href);
  };
  $('#import').onchange = async (e) => {
    try {
      const c = JSON.parse(await e.target.files[0].text());
      if (c.v !== 1 || !Array.isArray(c.groups)) throw new Error('格式不对');
      cfg = c; render(); status('已导入（还没保存）');
    } catch (err) { status('导入失败：' + err.message, true); }
    e.target.value = '';
  };
  render();
})();
