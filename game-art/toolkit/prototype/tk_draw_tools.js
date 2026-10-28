/* NABO 工具箱 · tool pages + frame entry point. */
(function (root) {
  'use strict';
  const H = root.TKHID, D = root.TKDraw, C = D.C, A = D.ACCENT;
  const { txt, fit, rr, topBar, bottomBar, nabo, legend, NUM } = D;

  const mmss = (ms) => {
    const s = Math.floor(Math.abs(ms) / 1000);
    return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
  };
  function toolFrame(g, st, now, imgs, page, rows, hint) {
    topBar(g, st, now, page);
    legend(g, rows, st.hit && st.hit.key, A[page]);
    D.naboBust(g, imgs, page, 194, 286, 110, now);
    bottomBar(g, hint, st.settings.remoteDim && (page === 'macro' || page === 'media'));
  }

  function drawPpt(g, st, now, imgs) {
    const p = st.ppt, el = root.TK.pptElapsed(st, now);
    const target = root.TK.TALK_MIN[st.settings.talk] * 60000, left = target - el;
    const col = left < 0 ? C.RED : (left <= 120000 && el > 0 ? A.ppt : C.WHITE);
    txt(g, '演讲计时', 12, 52, 12, C.DIM);
    txt(g, '已翻 ' + p.pages + ' 页', 228, 52, 12, C.PAPER, 'right');
    txt(g, (left < 0 ? '+' : '') + mmss(left < 0 ? -left : el), 120, 104, 48, col, 'center', NUM);
    rr(g, 16, 114, 208, 8, 4, C.PANEL);
    const fr = Math.min(1, el / target);
    if (fr > 0) rr(g, 16, 114, Math.max(8, 208 * fr), 8, 4, left < 0 ? C.RED : A.ppt);
    let line = '长按 OK 开始放映，或直接翻页';
    if (el > 0) line = left < 0 ? '超时 +' + mmss(-left) : (left <= 120000 ? '还剩 ' + mmss(left) + '，准备收尾' : '目标 ' + mmss(target) + ' · 还剩 ' + mmss(left));
    if (el > 0 && !p.running) line = '已结束 · 用时 ' + mmss(el);
    txt(g, fit(g, line, 224, 12), 120, 136, 12, left < 0 ? C.RED : C.PAPER, 'center');
    toolFrame(g, st, now, imgs, 'ppt', [
      { id: 'up', k: '↑', label: '上一页' },
      { id: 'ok', k: 'OK', label: p.black ? '恢复画面' : '黑屏' },
      { id: 'down', k: '↓', label: '下一页' },
    ], '长 OK 开始 · 长↓ 结束 · 长↑ 返回');
    if (p.black) { rr(g, 160, 154, 72, 18, 9, C.INK, A.ppt, 1); txt(g, '黑屏中', 196, 167, 12, A.ppt, 'center'); }
  }

  function drawMeet(g, st, now, imgs) {
    const app = H.MEET_APPS[st.meet.app], os = root.TK.os(st), desk = H.isDesktop(os);
    txt(g, '会议软件 ' + (st.meet.app + 1) + '/' + H.MEET_APPS.length, 12, 52, 12, C.DIM);
    rr(g, 12, 62, 216, 44, 10, C.PANEL, A.meet, 2);
    txt(g, '‹', 26, 90, 18, A.meet, 'center'); txt(g, '›', 214, 90, 18, A.meet, 'center');
    txt(g, app.name, 120, 91, 18, C.WHITE, 'center');
    txt(g, desk ? H.OS_NAME[os] + ' · 会议窗口要在最前面' : '会议快捷键只支持电脑', 120, 128, 12, desk ? C.PAPER : C.RED, 'center');
    const chord = (spec) => (spec ? D.chordLabel(spec, os) : '没有快捷键');
    toolFrame(g, st, now, imgs, 'meet', [
      { id: 'up', k: '↑', label: '摄像头', sub: chord(app.cam) },
      { id: 'ok', k: 'OK', label: '静音', sub: chord(app.mute) },
      { id: 'down', k: '↓', label: '举手', sub: chord(app.hand), dim: !app.hand },
    ], '长按 OK 换软件 · 长按↑ 返回');
  }

  function drawMediaChoice(g, st, now, imgs) {
    topBar(g, st, now, 'media');
    txt(g, '选择媒体玩法', 12, 53, 12, C.DIM);
    [['音乐', '音量 · 播放 · 切歌'], ['抖音', '方向键 ↑ / → / ↓']].forEach((r, i) => {
      const y = 66 + i * 78, selected = st.media.mode === i;
      rr(g, 10, y, 136, 64, 10, selected ? C.GOLD : C.PANEL, selected ? C.INK : null, 2);
      g.fillStyle = A.media; g.fillRect(13, y + 10, 4, 44);
      txt(g, r[0], 80, y + 28, 18, selected ? C.INK : C.PAPER, 'center');
      txt(g, fit(g, r[1], 116, 12), 80, y + 49, 12, selected ? C.INK : C.DIM, 'center');
    });
    D.naboBust(g, imgs, 'media', 194, 286, 110, now);
    txt(g, '选择后开始遥控', 12, 240, 12, C.DIM);
    bottomBar(g, '↑↓ 选择 · OK 进入 · 长↑ 返回');
  }
  function drawMedia(g, st, now, imgs) {
    if (st.media.choosing) return drawMediaChoice(g, st, now, imgs);
    if (st.media.mode === 1) {
      txt(g, '抖音 · 键盘方向键', 12, 53, 12, C.DIM);
      rr(g, 12, 62, 216, 44, 10, C.PANEL, A.media, 2);
      txt(g, '↑     →     ↓', 120, 91, 18, C.WHITE, 'center');
      txt(g, '右方向键可能快进，以App响应为准', 120, 128, 12, C.DIM, 'center');
      return toolFrame(g, st, now, imgs, 'media', [
        { id: 'up', k: '↑', label: '上个视频' },
        { id: 'down', k: '↓', label: '下个视频' },
        { id: 'ok', k: 'OK', label: '向右 / 快进' },
      ], '长↑ 返回媒体选择');
    }
    txt(g, '音乐遥控', 12, 52, 12, C.DIM);
    const cx = 120, cy = 88, hit = st.hit && st.hit.key;
    g.beginPath(); g.arc(cx, cy, 30, 0, 7); g.fillStyle = hit === 'ok' ? A.media : C.PANEL; g.fill();
    g.fillStyle = hit === 'ok' ? C.INK : C.WHITE;
    g.beginPath(); g.moveTo(cx - 12, cy - 13); g.lineTo(cx + 2, cy); g.lineTo(cx - 12, cy + 13); g.fill();
    g.fillRect(cx + 5, cy - 12, 4, 24); g.fillRect(cx + 12, cy - 12, 4, 24);
    [['−', 56, 'down'], ['+', 184, 'up']].forEach(([s, x, id]) => {
      g.beginPath(); g.arc(x, cy, 18, 0, 7); g.fillStyle = hit === id ? A.media : C.PANEL; g.fill();
      txt(g, s, x, cy + 8, 22, hit === id ? C.INK : C.WHITE, 'center', NUM);
    });
    txt(g, '音量', 120, 132, 12, C.DIM, 'center');
    toolFrame(g, st, now, imgs, 'media', [
      { id: 'up', k: '↑', label: '音量 +' },
      { id: 'ok', k: 'OK', label: '播放 / 暂停' },
      { id: 'down', k: '↓', label: '音量 −' },
    ], '长OK 下曲 · 长↓ 上曲 · 长↑ 选择');
  }

  function drawCam(g, st, now, imgs) {
    const c = st.cam, T = root.TK;
    if (c.endMs > 0) {
      const n = Math.ceil((c.endMs - now) / 1000);
      g.beginPath(); g.arc(120, 92, 46, 0, 7); g.fillStyle = A.cam; g.fill();
      txt(g, String(n), 120, 112, 48, C.INK, 'center', NUM);
      txt(g, '再按 OK 取消', 120, 156, 12, C.PAPER, 'center');
    } else if (c.burstLeft > 0) {
      txt(g, '连拍中', 120, 80, 18, A.cam, 'center');
      txt(g, (5 - c.burstLeft) + '/5', 120, 122, 28, C.WHITE, 'center', NUM);
    } else {
      txt(g, '延时', 12, 52, 12, C.DIM);
      T.CAM_DELAYS.forEach((d, i) => {
        const x = 12 + i * 74, sel = i === c.delay;
        rr(g, x, 60, 68, 50, 10, sel ? A.cam : C.PANEL, sel ? C.WHITE : null, 2);
        if (d) txt(g, d + 's', x + 34, 94, 22, sel ? C.INK : C.PAPER, 'center', NUM);
        else txt(g, '不延时', x + 34, 91, 16, sel ? C.INK : C.PAPER, 'center');
      });
      txt(g, '已拍 ' + c.shots + ' 张 · 先打开手机相机', 120, 136, 12, C.PAPER, 'center');
    }
    if (c.endMs > 0) return toolFrameNoLegend(g, st, now, imgs);
    toolFrame(g, st, now, imgs, 'cam', [
      { id: 'up', k: '↑', label: '换延时' },
      { id: 'ok', k: 'OK', label: '拍照' },
      { id: 'down', k: '↓', label: '连拍 5 张' },
    ], '快门 = 音量+ 键 · 长按↑ 返回');
  }
  function toolFrameNoLegend(g, st, now, imgs) {
    topBar(g, st, now, 'cam');
    D.naboBust(g, imgs, 'cam', 194, 286, 110, now);
    bottomBar(g, 'OK 取消 · 长按↑ 返回');
  }

  function drawMacro(g, st, now, imgs) {
    const G = root.TK.groups(st), n = G.length, gi = st.macro.group, grp = G[gi], os = root.TK.os(st);
    txt(g, '第 ' + (gi + 1) + ' / ' + n + ' 组', 12, 52, 12, C.DIM);
    for (let i = 0; i < n; i++) {
      g.beginPath(); g.arc(228 - (n - 1 - i) * 12, 48, 4, 0, 7);
      g.fillStyle = i === gi ? A.macro : C.PANEL; g.fill();
    }
    rr(g, 12, 62, 216, 44, 10, C.PANEL, A.macro, 2);
    txt(g, grp.name, 120, 91, 18, C.WHITE, 'center');
    txt(g, gi === 1 ? 'R = 右侧修饰键 · 配置页里可以改' : H.OS_NAME[os] + ' 键位 · 配置页里可以改', 120, 128, 12, C.PAPER, 'center');
    const sub = (b) => D.chordLabel(b, os) || '未设置';
    toolFrame(g, st, now, imgs, 'macro', [
      { id: 'up', k: '↑', label: grp.up.label, sub: sub(grp.up) },
      { id: 'ok', k: 'OK', label: grp.ok.label, sub: sub(grp.ok) },
      { id: 'down', k: '↓', label: grp.down.label, sub: sub(grp.down) },
    ], '长OK 下组 · 长↓ 上组 · 长↑ 返回');
  }

  /* QR via qrcode-generator (prototype only; firmware uses nayuki qrcodegen). */
  const qrCache = new Map();
  function qrMatrix(s) {
    if (qrCache.has(s)) return qrCache.get(s);
    let m = null;
    if (root.qrcode) {
      const q = root.qrcode(0, 'M'); q.addData(s); q.make();
      const n = q.getModuleCount();
      m = { n, dark: (r, c) => q.isDark(r, c) };
    }
    qrCache.set(s, m); return m;
  }
  function drawQr(g, s, cx, top, maxPx) {
    const m = qrMatrix(s);
    if (!m) { rr(g, cx - maxPx / 2, top, maxPx, maxPx, 6, '#ddd'); txt(g, 'QR', cx, top + maxPx / 2, 16, C.DIM, 'center'); return; }
    const sc = Math.max(1, Math.floor(maxPx / (m.n + 4))), size = sc * (m.n + 4);
    const x0 = Math.round(cx - size / 2);
    g.fillStyle = C.WHITE; g.fillRect(x0, top, size, size);
    g.fillStyle = '#000';
    for (let r = 0; r < m.n; r++) for (let c = 0; c < m.n; c++)
      if (m.dark(r, c)) g.fillRect(x0 + (c + 2) * sc, top + (r + 2) * sc, sc, sc);
  }
  function drawCard(g, st, now, imgs) {
    const card = st.cards[st.card.idx];
    if (st.card.zoom) {
      g.fillStyle = C.WHITE; g.fillRect(0, 0, 240, 320);
      drawQr(g, card.qr, 120, 40, 232);
      txt(g, fit(g, card.title + ' · ' + card.name, 220, 16), 120, 290, 16, C.INK, 'center');
      txt(g, 'OK 还原', 120, 310, 12, C.DIM, 'center');
      return;
    }
    topBar(g, st, now, 'card');
    rr(g, 10, 40, 220, 244, 12, C.PAPER);
    g.fillStyle = A.card; g.fillRect(13, 50, 4, 224);
    nabo(g, imgs, 20, 50, 64, A.card, now, null);
    g.font = '500 12px ' + D.FONT;
    rr(g, 96, 54, g.measureText(card.title).width + 16, 20, 10, A.card);
    txt(g, card.title, 104, 68, 12, C.INK);
    txt(g, fit(g, card.name, 126, 18), 96, 98, 18, C.INK);
    txt(g, fit(g, card.line, 126, 12), 96, 116, 12, C.DIM);
    drawQr(g, card.qr, 120, 126, 144);
    st.cards.forEach((_, i) => {
      g.beginPath(); g.arc(120 + (i - 1) * 14, 276, 4, 0, 7);
      g.fillStyle = i === st.card.idx ? A.card : '#D5CABD'; g.fill();
    });
    bottomBar(g, '↑↓ 换一张 · OK 放大 · 长按↑ 返回');
  }

  const PAGES = { ppt: drawPpt, meet: drawMeet, media: drawMedia, cam: drawCam, macro: drawMacro, card: drawCard };
  const offNotes = new WeakMap();
  function displayNote(g, off) {
    const canvas = g.canvas, doc = canvas && canvas.ownerDocument;
    if (!doc || !canvas.parentElement) return;
    let note = offNotes.get(canvas);
    if (!note && off) {
      note = doc.createElement('p'); note.className = 'hint'; note.setAttribute('role', 'status');
      note.textContent = '息屏遥控中：短键继续发送；长OK只亮屏，长↑返回。';
      const anchor = canvas.closest('.badge') || canvas.parentElement;
      anchor.insertAdjacentElement('afterend', note); offNotes.set(canvas, note);
    }
    if (note) note.hidden = !off;
  }
  function draw(g, st, now, imgs) {
    const off = Boolean(st.display && st.display.off);
    displayNote(g, off);
    if (off) { g.fillStyle = '#000000'; g.fillRect(0, 0, 240, 320); return; }
    g.fillStyle = C.BG; g.fillRect(0, 0, 240, 320);
    if (st.page === 'boot') { D.drawBoot(g, st, now, imgs); if (st.osPick) D.drawOsPick(g, st); return; }
    if (st.page === 'menu') D.drawMenu(g, st, now, imgs);
    else if (st.page === 'conn') D.drawConn(g, st, now);
    else if (st.page === 'set') D.drawSet(g, st, now);
    else PAGES[st.page](g, st, now, imgs);
    if (!(st.page === 'card' && st.card.zoom)) D.toast(g, st);
    if (st.osPick) D.drawOsPick(g, st);
  }

  root.TKDraw.draw = draw;
})(window);
