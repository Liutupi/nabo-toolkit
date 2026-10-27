/* NABO 工具箱 · shared drawing, menu, 连接, 设置 (240×320, firmware layout).
 * Chinese only at 18/16/12 px; Archivo Black only for digits and Latin. */
(function (root) {
  'use strict';
  const H = root.TKHID;

  const C = {
    BG: '#14203a', PANEL: '#22324f', INK: '#182439', PAPER: '#EEE6DE', GOLD: '#FFAD84',
    WHITE: '#FFFFFF', DIM: '#7B7D7B', RED: '#E65152', GREEN: '#4CC38A',
  };
  const ACCENT = {
    ppt: '#F28C38', meet: '#4CC38A', media: '#9B7BEA', cam: '#4FA3F7',
    macro: '#FFCE4A', card: '#F08DB0', conn: '#4FC3C8', set: '#C5C6CD', menu: '#FFAD84',
  };
  const NAME = {
    ppt: 'PPT 翻页笔', meet: '会议键', media: '媒体遥控', cam: '拍照快门',
    macro: '快捷键', card: '名片', conn: '连接', set: '设置', menu: 'NABO 工具箱',
  };
  const SUB = {
    ppt: '翻页 · 计时', meet: '静音 · 摄像头', media: '音量 · 切歌', cam: '延时 · 连拍',
    macro: '截屏 · 复制 · 粘贴', card: '二维码', conn: '3 台设备', set: '提示音 · 休眠',
  };
  const FONT = '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif';
  const NUM = '"Archivo Black", Impact, sans-serif';

  function txt(g, s, x, y, size, color, align, font) {
    g.font = (font === NUM ? '' : '500 ') + size + 'px ' + (font || FONT);
    g.fillStyle = color; g.textAlign = align || 'left'; g.textBaseline = 'alphabetic';
    g.fillText(s, x, y);
  }
  function fit(g, s, maxW, size, font) {
    g.font = (font === NUM ? '' : '500 ') + size + 'px ' + (font || FONT);
    if (g.measureText(s).width <= maxW) return s;
    while (s.length > 1 && g.measureText(s + '…').width > maxW) s = s.slice(0, -1);
    return s + '…';
  }
  function rr(g, x, y, w, h, r, fill, stroke, lw) {
    g.beginPath(); g.roundRect(x, y, w, h, r);
    if (fill) { g.fillStyle = fill; g.fill(); }
    if (stroke) { g.lineWidth = lw || 2; g.strokeStyle = stroke; g.stroke(); }
  }

  function statusText(st, now) {
    if (st.pairing) return { s: '配对中 ' + Math.ceil((st.pairing.until - now) / 1000) + 's', c: C.GOLD };
    const slot = st.slots[st.active];
    if (st.connected && slot) return { s: slot.name, c: C.GREEN };
    return { s: '未连接', c: C.RED };
  }
  function topBar(g, st, now, page) {
    g.fillStyle = C.INK; g.fillRect(0, 0, 240, 32);
    g.fillStyle = ACCENT[page]; g.fillRect(0, 30, 240, 2);
    txt(g, NAME[page], 10, 22, 16, C.PAPER);
    const t = statusText(st, now), s = fit(g, t.s, 84, 12);
    g.font = '500 12px ' + FONT;
    const w = g.measureText(s).width;
    g.beginPath(); g.arc(240 - 14 - w - 8, 17, 3.5, 0, 7); g.fillStyle = t.c; g.fill();
    txt(g, s, 230, 21, 12, C.PAPER, 'right');
  }
  function bottomBar(g, hint) {
    g.fillStyle = C.INK; g.fillRect(0, 290, 240, 30);
    txt(g, fit(g, hint, 228, 12), 120, 310, 12, C.PAPER, 'center');
  }

  /* NABO placeholder: unchanged frames from nabo-idle.png in a round frame. */
  function nabo(g, imgs, x, y, size, accent, now, react) {
    const ph = now % 3600;
    const frame = ph > 3460 && ph < 3540 ? imgs.closed : (ph > 3400 && ph < 3600 ? imgs.half : imgs.open);
    const dy = react ? -Math.round(5 * Math.sin(Math.PI * Math.min(1, (react.until - now) / 500))) : 0;
    const cx = x + size / 2, cy = y + size / 2 + dy;
    g.beginPath(); g.arc(cx, cy, size / 2 + 3, 0, 7); g.fillStyle = accent; g.fill();
    g.save(); g.beginPath(); g.arc(cx, cy, size / 2, 0, 7); g.clip();
    g.fillStyle = '#000'; g.fillRect(x, y + dy, size, size);
    if (frame && frame.complete) g.drawImage(frame, x, y + dy, size, size);
    g.restore();
  }

  function toast(g, st) {
    const t = st.toast;
    if (!t) return;
    const err = t.kind === 'err';
    rr(g, 8, 256, 224, 26, 8, err ? C.RED : C.PANEL);
    if (!err) { g.fillStyle = ACCENT[st.page] || C.GOLD; g.fillRect(8, 262, 3, 14); }
    txt(g, fit(g, t.text, 206, 12), err ? 120 : 18, 274, 12, C.WHITE, err ? 'center' : 'left');
  }

  /* Three-row key legend; rows: {k, label, sub?, dim?}. */
  function legend(g, rows, hitKey, accent, x, y, w) {
    const h = rows.some((r) => r.sub) ? 34 : 30;
    x = x || 8; y = y || (h === 34 ? 140 : 150); w = w || 146;
    rows.forEach((r, i) => {
      const ry = y + i * (h + 4), hit = hitKey && r.id === hitKey;
      rr(g, x, ry, w, h, 8, hit ? accent : C.PANEL);
      rr(g, x + 4, ry + (h - 22) / 2, 30, 22, 6, hit ? C.INK : C.BG);
      txt(g, r.k, x + 19, ry + h / 2 + 5, r.k === 'OK' ? 12 : 14, hit ? accent : C.PAPER, 'center', r.k === 'OK' ? NUM : FONT);
      const col = hit ? C.INK : (r.dim ? C.DIM : C.PAPER);
      if (r.sub) {
        txt(g, fit(g, r.label, w - 46, 16), x + 42, ry + 16, 16, col);
        txt(g, fit(g, r.sub, w - 46, 12), x + 42, ry + 30, 12, hit ? C.INK : C.DIM);
      } else txt(g, fit(g, r.label, w - 46, 16), x + 42, ry + h / 2 + 6, 16, col);
    });
  }

  /* ---- 菜单 ---- */
  function drawMenu(g, st, now, imgs) {
    topBar(g, st, now, 'menu');
    g.fillStyle = C.PANEL; g.fillRect(0, 32, 240, 72);
    nabo(g, imgs, 10, 37, 62, C.GOLD, now, null);
    rr(g, 84, 44, 148, 50, 10, C.PAPER);
    g.beginPath(); g.moveTo(84, 62); g.lineTo(76, 68); g.lineTo(84, 72); g.fillStyle = C.PAPER; g.fill();
    txt(g, '今天遥控什么？', 94, 65, 16, C.INK);
    const slot = st.slots[st.active];
    const line = st.connected && slot ? '已连 ' + slot.name + ' · ' + H.OS_NAME[slot.os] : '还没连接设备';
    txt(g, fit(g, line, 130, 12), 94, 84, 12, st.connected ? C.DIM : C.RED);
    root.TK.MENU.forEach((id, i) => {
      const x = i % 2 ? 124 : 8, y = 110 + Math.floor(i / 2) * 44, sel = i === st.menu;
      rr(g, x, y, 108, 40, 9, sel ? C.GOLD : C.PAPER, sel ? C.INK : null, 2);
      g.fillStyle = ACCENT[id]; g.fillRect(x + 6, y + 8, 4, 24);
      txt(g, fit(g, NAME[id], 88, 16), x + 16, y + 19, 16, C.INK);
      txt(g, fit(g, SUB[id], 88, 12), x + 16, y + 34, 12, sel ? C.INK : C.DIM);
    });
    bottomBar(g, '↑↓ 选择 · OK 进入');
  }

  /* ---- 连接 ---- */
  function drawConn(g, st, now) {
    topBar(g, st, now, 'conn');
    txt(g, '最多 3 台，同一时间连一台', 12, 52, 12, C.DIM);
    for (let i = 0; i <= 3; i++) {
      const y = 62 + i * 50, sel = i === st.connSel, slot = st.slots[i];
      rr(g, 10, y, 220, 44, 10, sel ? C.GOLD : C.PANEL, sel ? C.INK : null, 2);
      const fg = sel ? C.INK : C.PAPER, dim = sel ? C.INK : C.DIM;
      if (i === 3) { txt(g, '+  配对新设备', 24, y + 28, 16, sel ? C.INK : ACCENT.conn); continue; }
      g.beginPath(); g.arc(30, y + 22, 11, 0, 7); g.fillStyle = sel ? C.INK : C.BG; g.fill();
      txt(g, String(i + 1), 30, y + 27, 12, sel ? C.GOLD : C.PAPER, 'center', NUM);
      if (!slot) { txt(g, '空位', 50, y + 28, 16, dim); continue; }
      txt(g, fit(g, slot.name, 100, 16), 50, y + 20, 16, fg);
      txt(g, H.OS_NAME[slot.os], 50, y + 36, 12, dim);
      const cur = i === st.active, s = cur ? (st.connected ? '已连接' : '未连接') : 'OK 连接';
      txt(g, s, 220, y + 28, 12, cur ? (st.connected ? (sel ? C.INK : C.GREEN) : C.RED) : dim, 'right');
    }
    bottomBar(g, '长按 OK 改类型 · 长按↓ 删除 · 长按↑ 返回');
    if (st.pairing) {
      popup(g, 156);
      txt(g, '配对中', 120, 108, 18, C.INK, 'center');
      txt(g, String(Math.ceil((st.pairing.until - now) / 1000)), 120, 162, 48, ACCENT.conn, 'center', NUM);
      txt(g, '在电脑或手机的蓝牙里选择', 120, 190, 12, C.INK, 'center');
      txt(g, '「NABO 工具箱」', 120, 208, 16, C.INK, 'center');
      txt(g, 'OK 停止配对', 120, 228, 12, C.DIM, 'center');
    }
    if (st.confirmDel >= 0) {
      popup(g, 100);
      txt(g, fit(g, '删除「' + st.slots[st.confirmDel].name + '」？', 172, 16), 120, 140, 16, C.INK, 'center');
      txt(g, '删除后要在那台设备上重新配对', 120, 162, 12, C.DIM, 'center');
      txt(g, 'OK 删除 · 其他键取消', 120, 186, 12, C.RED, 'center');
    }
  }
  function popup(g, h) {
    g.fillStyle = 'rgba(24,36,57,0.6)'; g.fillRect(0, 0, 240, 320);
    rr(g, 24, 160 - h / 2 - 4, 192, h, 14, C.PAPER, C.INK, 2);
  }
  function drawOsPick(g, st) {
    popup(g, 200);
    txt(g, '这是什么设备？', 120, 86, 16, C.INK, 'center');
    H.OS_LIST.forEach((o, i) => {
      const y = 98 + i * 36, sel = i === st.osPick.sel;
      rr(g, 40, y, 160, 30, 8, sel ? C.GOLD : '#E2D8CC', sel ? C.INK : null, 2);
      txt(g, H.OS_NAME[o], 120, y + 21, 16, C.INK, 'center');
    });
    txt(g, '↑↓ 选择 · OK 确定', 120, 254, 12, C.DIM, 'center');
  }

  /* ---- 设置 ---- */
  function drawSet(g, st, now) {
    topBar(g, st, now, 'set');
    const T = root.TK, s = st.settings, sl = T.SLEEP[s.sleep];
    const rows = [
      ['按键提示音', s.beep ? '开' : '关', '演讲翻页时始终不响'],
      ['演讲时长', T.TALK_MIN[s.talk] + ' 分钟', 'PPT 计时的目标时长'],
      ['自动休眠', sl ? sl + ' 分钟' : '连接时不休眠', '计时、倒数、配对时不休眠'],
      ['关于', 'v0.1 原型', '离线 · 蓝牙键盘 · 不联网'],
    ];
    rows.forEach((r, i) => {
      const y = 44 + i * 48, sel = i === st.setSel;
      rr(g, 10, y, 220, 42, 10, sel ? C.GOLD : C.PANEL, sel ? C.INK : null, 2);
      txt(g, r[0], 22, y + 27, 16, sel ? C.INK : C.PAPER);
      txt(g, r[1], 218, y + 27, 16, sel ? C.INK : ACCENT.set, 'right');
    });
    txt(g, rows[st.setSel][2], 120, 250, 12, C.DIM, 'center');
    bottomBar(g, '↑↓ 选择 · OK 修改 · 长按↑ 返回');
  }

  root.TKDraw = { C, ACCENT, NAME, FONT, NUM, txt, fit, rr, topBar, bottomBar, nabo, toast, legend,
                  drawMenu, drawConn, drawOsPick, drawSet };
})(window);
