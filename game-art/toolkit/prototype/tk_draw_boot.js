/* NABO 工具箱 · 开机画面（DESIGN 5.0）。Placeholders: icons are coloured
 * discs, the wordmark is font text, NABO is the unchanged reference frame. */
(function (root) {
  'use strict';
  const D = root.TKDraw, C = D.C, A = D.ACCENT;
  const { txt, NUM } = D;

  const CX = 120, CY = 178, RING = 74;
  const ICONS = ['macro', 'ppt', 'meet', 'media', 'cam', 'card', 'conn', 'set'];
  const GLYPH = { macro: '键', ppt: 'P', meet: '会', media: '♪', cam: '拍', card: '名', conn: '连', set: '设' };
  const FLASH_AT = 2200, RISE_AT = 1400, RISE_MS = 300;

  const clamp = (v) => Math.max(0, Math.min(1, v));
  const easeOut = (p) => 1 - Math.pow(1 - p, 3);
  function backOut(p) { const s = 1.7; p -= 1; return p * p * ((s + 1) * p + s) + 1; }

  function drawBoot(g, st, now, imgs) {
    const t = now - st.boot.start;
    g.fillStyle = C.BG; g.fillRect(0, 0, 240, 320);

    /* 0–400 ms: dot + three signal rings, then a slow repeating pulse. */
    const dot = clamp(t / 150);
    g.beginPath(); g.arc(CX, CY, 5 * dot, 0, 7); g.fillStyle = A.conn; g.fill();
    for (let k = 0; k < 3; k++) {
      const local = t < 400 ? (t - k * 100) / 300 : ((t - 400 - k * 400) % 1200) / 1200;
      if (local <= 0 || local >= 1) continue;
      g.globalAlpha = (1 - local) * (t < 400 ? 0.9 : 0.35);
      g.beginPath(); g.arc(CX, CY, 8 + local * (RING + 20), 0, 7);
      g.lineWidth = 2; g.strokeStyle = A.conn; g.stroke();
    }
    g.globalAlpha = 1;

    /* 400–1000 ms: eight tool icons pop in around the ring; flash on the press. */
    const flash = t >= FLASH_AT && t < FLASH_AT + 150;
    ICONS.forEach((id, i) => {
      const p = clamp((t - 400 - i * 60) / 180);
      if (p <= 0) return;
      const ang = -Math.PI / 2 + i * Math.PI / 4, r = 15 * backOut(p);
      const x = CX + RING * Math.cos(ang), y = CY + RING * Math.sin(ang);
      g.beginPath(); g.arc(x, y, r + 2, 0, 7); g.fillStyle = flash ? C.WHITE : C.INK; g.fill();
      g.beginPath(); g.arc(x, y, r, 0, 7); g.fillStyle = flash ? C.WHITE : A[id]; g.fill();
      if (p === 1) txt(g, GLYPH[id], x, y + 5, 12, C.INK, 'center');
    });

    /* 700–1400 ms: wordmark drops in, subtitle fades in. */
    const drop = easeOut(clamp((t - 700) / 350));
    if (drop > 0) {
      const y = -10 + drop * 52;
      txt(g, 'NABO', 112, y, 28, C.WHITE, 'right', NUM);
      txt(g, '工具箱', 118, y - 2, 18, C.GOLD, 'left');
    }
    const sub = clamp((t - 1050) / 350);
    if (sub > 0) { g.globalAlpha = sub; txt(g, '陪你遥控万物', 120, 74, 16, C.PAPER, 'center'); g.globalAlpha = 1; }

    txt(g, '按任意键跳过', 120, 314, 12, C.DIM, 'center');
    /* 1.4 s: 150px waist-up welcome, fixed bottom-center anchor; NABO stays in front. */
    const rise = easeOut(clamp((t - RISE_AT) / RISE_MS));
    if (rise > 0) {
      const bottom = 470 - rise * 150;
      D.naboBust(g, imgs, 'welcome', CX, bottom, 150, t - RISE_AT);
    }
  }

  root.TKDraw.drawBoot = drawBoot;
})(window);
