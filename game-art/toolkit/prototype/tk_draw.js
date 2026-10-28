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
    macro: '#FFCE4A', card: '#F08DB0', conn: '#4FC3C8', set: '#C5C6CD', menu: '#FFAD84', voice: '#FFAD84',
  };
  const NAME = {
    ppt: 'PPT 翻页笔', meet: '会议键', media: '媒体遥控', cam: '拍照快门',
    macro: '快捷键', card: '名片', conn: '连接', set: '设置', menu: 'NABO 工具箱', voice: '语音查找',
  };
  const SUB = {
    ppt: '翻页 · 计时', meet: '静音 · 摄像头', media: '音乐 · 抖音', cam: '延时 · 连拍',
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
  function chordLabel(spec, os) {
    const packet = root.TKConfig ? root.TKConfig.resolve(spec, os) : H.resolve(spec, os);
    if (!packet || packet.kind !== 'key' || !H.isApple(os)) return H.chordLabel(packet, os);
    const parts = [];
    for (const [mask, name] of [[1,'⌃'],[16,'R⌃'],[4,'⌥'],[64,'R⌥'],[2,'⇧'],[32,'R⇧'],[8,'⌘'],[128,'R⌘']]) {
      if (packet.mod & mask) parts.push(name);
    }
    if (packet.usage) parts.push(H.keyName(packet.usage));
    return parts.join('+');
  }

  function statusText(st, now) {
    if (st.pairing) return { s: '配对中 ' + Math.ceil((st.pairing.until - now) / 1000) + 's', c: C.GOLD };
    const slot = st.slots[st.active];
    if (st.connected && slot) return { s: slot.name, c: C.GREEN };
    return { s: '未连接', c: C.RED };
  }
  function topBar(g, st, now, page) {
    g.fillStyle = C.INK; g.fillRect(0, 0, 240, 32);
    g.fillStyle = ACCENT[page]; g.fillRect(0, 32, 240, 4);
    g.save(); g.beginPath(); g.rect(0, 32, 240, 4); g.clip();
    g.strokeStyle = C.INK; g.globalAlpha = .4; g.lineWidth = 3;
    for (let x = -4; x < 248; x += 6) { g.beginPath(); g.moveTo(x, 36); g.lineTo(x + 4, 32); g.stroke(); }
    g.restore();
    txt(g, fit(g, NAME[page], 116, 16), 10, 22, 16, C.PAPER);
    const t = statusText(st, now), s = fit(g, t.s, 84, 12);
    g.font = '500 12px ' + FONT;
    const w = g.measureText(s).width;
    g.beginPath(); g.arc(240 - 14 - w - 8, 17, 3.5, 0, 7); g.fillStyle = t.c; g.fill();
    txt(g, s, 230, 21, 12, C.PAPER, 'right');
  }
  function bottomBar(g, hint, remoteDim) {
    g.fillStyle = C.INK; g.fillRect(0, 290, 240, 30);
    if (remoteDim) txt(g, '30秒息屏 · 长OK亮屏', 120, 301, 12, C.PAPER, 'center');
    txt(g, fit(g, hint, 228, 12), 120, remoteDim ? 315 : 310, 12, C.PAPER, 'center');
  }

  /* NABO placeholder: unchanged frames from nabo-idle.png in a round frame. */
  function nabo(g, imgs, x, y, size, accent, now, react) {
    if (imgs.clips && sprite(g, imgs, 'base', 'avatar', x, y, size, now)) {
      g.beginPath(); g.arc(x + size/2, y + size/2, size/2, 0, 7);
      g.strokeStyle = accent; g.lineWidth = 3; g.stroke(); return;
    }
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

  function sprite(g, imgs, id, variant, x, y, height, elapsed) {
    const clip = imgs.clips && imgs.clips[id], asset = clip && clip[variant];
    if (!asset || !asset.image.complete || !asset.image.naturalWidth) return false;
    const t = clip.loop ? Math.max(0, elapsed) % clip.durationMs : Math.max(0, elapsed);
    let i = 0;
    while (i + 1 < clip.times.length && t >= clip.times[i + 1]) i++;
    const width = height * asset.w / asset.h;
    g.drawImage(asset.image, i * asset.w, 0, asset.w, asset.h, x, y, width, height);
    return true;
  }
  function naboBust(g, imgs, id, cx, bottom, height, elapsed) {
    const variant = height === 150 ? 'large' : 'bust';
    const asset = imgs.clips && imgs.clips[id] && imgs.clips[id][variant];
    const width = asset ? height * asset.w / asset.h : height * 84/110;
    if (sprite(g, imgs, id, variant, cx-width/2, bottom-height, height, elapsed)) return;
    const frame = imgs.open;
    if (frame && frame.complete) g.drawImage(frame, cx-height/2, bottom-height, height, height);
  }

  function toast(g, st) {
    const t = st.toast;
    if (!t) return;
    const err = t.kind === 'err';
    const tool = root.TK.TOOLS.has(st.page) && st.page !== 'card', w = tool ? 138 : 224;
    rr(g, 8, 256, w, 26, 8, err ? C.RED : C.PANEL);
    if (!err) { g.fillStyle = ACCENT[st.page] || C.GOLD; g.fillRect(8, 262, 3, 14); }
    txt(g, fit(g, t.text, w - 18, 12), err ? 8 + w/2 : 18, 274, 12, C.WHITE, err ? 'center' : 'left');
  }

  /* Three-row key legend; rows: {k, label, sub?, dim?}. */
  function legend(g, rows, hitKey, accent, x, y, w) {
    const h = 34;
    x = x || 8; y = y || 142; w = w || 138;
    const physicalOrder = ['up', 'down', 'ok'];
    rows.slice().sort((a, b) => physicalOrder.indexOf(a.id) - physicalOrder.indexOf(b.id)).forEach((r, i) => {
      const hit = hitKey && r.id === hitKey, ry = y + i * (h + 4) + (hit ? 2 : 0);
      if (!hit) rr(g, x, ry + 2, w, h, 8, C.INK);
      rr(g, x, ry, w, h, 8, hit ? accent : C.PANEL);
      rr(g, x + 4, ry + (h - 22) / 2, 30, 22, 6, hit ? C.INK : C.BG);
      txt(g, r.k, x + 19, ry + h / 2 + 5, r.k === 'OK' ? 12 : 16, hit ? accent : C.PAPER, 'center', r.k === 'OK' ? NUM : FONT);
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
    g.fillStyle = C.PANEL; g.fillRect(0, 36, 240, 68);
    nabo(g, imgs, 10, 38, 64, C.GOLD, now, null);
    rr(g, 84, 44, 148, 50, 10, C.PAPER);
    g.beginPath(); g.moveTo(84, 62); g.lineTo(76, 68); g.lineTo(84, 72); g.fillStyle = C.PAPER; g.fill();
    txt(g, '今天遥控什么？', 94, 65, 16, C.INK);
    const slot = st.slots[st.active];
    const line = st.connected && slot ? '已连 ' + slot.name + ' · ' + H.OS_NAME[slot.os] : '还没连接设备';
    txt(g, fit(g, line, 130, 12), 94, 84, 12, st.connected ? C.DIM : C.RED);
    root.TK.MENU.forEach((id, i) => {
      const x = i % 2 ? 124 : 8, y = 110 + Math.floor(i / 2) * 44, sel = i === st.menu;
      rr(g, x, y, 108, 40, 10, sel ? C.GOLD : C.PAPER, sel ? C.INK : null, 2);
      g.fillStyle = ACCENT[id]; g.fillRect(x + 3, y + 8, 4, 24);
      g.beginPath(); g.arc(x + 20, y + 20, 12, 0, 7); g.fill();
      txt(g, fit(g, id === 'ppt' ? 'PPT翻页' : NAME[id], 64, 16), x + 38, y + 19, 16, C.INK);
      txt(g, fit(g, SUB[id], 64, 12), x + 38, y + 34, 12, sel ? C.INK : C.DIM);
    });
    bottomBar(g, '↑↓ 选择 · OK 进入 · 长OK 语音');
  }

  function drawVoice(g, st, now, imgs) {
    topBar(g, st, now, 'voice');
    const v = st.voice, names = root.TK.VOICE_TARGETS;
    const states = ['准备', '请说口令', '请说目标名称', '已保存', '未识别', '操作失败', '尚未录入', '未找到分组', '准备采音', '歧义', '口令太长', '采音失败'];
    const status = Number.isInteger(v.status) && v.status >= 0 && v.status < states.length ? v.status : 5;
    g.fillStyle = C.PANEL; g.fillRect(0, 36, 240, 68);
    nabo(g, imgs, 10, 38, 64, C.GOLD, v.busy ? 0 : now, null);
    txt(g, '本人录入', 84, 64, 16, C.PAPER);
    txt(g, fit(g, '按需聆听 · 不持续唤醒', 148, 12), 84, 85, 12, C.DIM);
    names.forEach((name, i) => {
      const x = i % 2 ? 124 : 10, y = 110 + Math.floor(i / 2) * 26, sel = i === v.selected;
      rr(g, x, y, 106, 24, 6, sel ? C.GOLD : C.PANEL, sel ? C.INK : null, 2);
      txt(g, name, x + 10, y + 18, 16, sel ? C.INK : C.PAPER);
      txt(g, v.counts[i] + '/3', x + 96, y + 18, 12, sel ? C.INK : C.DIM, 'right');
    });
    const error = status === 4 || status === 5 || status === 7 || status >= 9;
    rr(g, 10, 222, 220, 60, 10, C.PANEL, error ? C.RED : null, 1);
    txt(g, states[status], 120, 245, 16, error ? C.RED : status === 3 ? C.GREEN : C.PAPER, 'center');
    let hint = v.selected === 6 ? '只进Typeless · 再按键' : '长OK 为每个口令录入3次';
    if (status === 1) hint = '已录入口令任选一个';
    else if (status === 2) hint = '自然说一次所选名称';
    else if (status === 3) hint = v.counts[v.selected] < 3 ? '长OK 继续录入' : 'OK 识别 · 长OK 重新录入';
    else if (status === 4 || status === 9) hint = '请短OK 后再说一次';
    else if (status === 5 || status === 11) hint = '请稍后重试';
    else if (status === 6) hint = '长OK 录入所选口令';
    else if (status === 7) hint = '配置页中恢复目标分组';
    else if (status === 8) hint = '请保持安静，稍后再说';
    else if (status === 10) hint = '请只说目标名称';
    txt(g, fit(g, hint, 204, 12), 120, 266, 12, C.DIM, 'center');
    g.fillStyle = C.INK; g.fillRect(0, 290, 240, 30);
    txt(g, fit(g, v.busy ? '采音中 · 请稍候' : '↑↓ 选择 · OK 识别 · 长OK 录入', 228, 12), 120, 301, 12, C.PAPER, 'center');
    txt(g, '长↑ 返回', 120, 315, 12, C.PAPER, 'center');
  }

  /* ---- 连接 ---- */
  function drawConn(g, st, now) {
    topBar(g, st, now, 'conn');
    txt(g, '最多 3 台，同一时间连一台', 12, 52, 12, C.DIM);
    for (let i = 0; i <= 3; i++) {
      const y = 62 + i * 50, sel = i === st.connSel, slot = st.slots[i];
      rr(g, 10, y, 220, 44, 10, sel ? C.GOLD : C.PANEL, sel ? C.INK : null, 2);
      g.fillStyle = ACCENT.conn; g.fillRect(13, y + 8, 4, 28);
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
    bottomBar(g, '长 OK 类型 · 长↓ 删除 · 长↑ 返回');
    if (st.pairing) {
      popup(g, 156);
      if (st.pairing.passkey !== null) {
        txt(g, '配对码', 120, 108, 18, C.INK, 'center');
        const code = st.pairing.passkey;
        g.font = '48px ' + NUM;
        const scale = Math.min(1, 172/g.measureText(code.slice(0,3) + ' ' + code.slice(3)).width);
        g.save(); g.translate(120, 0); g.scale(scale, 1);
        txt(g, code.slice(0,3) + ' ' + code.slice(3), 0, 166, 48, ACCENT.conn, 'center', NUM); g.restore();
        txt(g, '在电脑上输入这 6 位数字', 120, 194, 12, C.INK, 'center');
        txt(g, 'OK 取消 · 长按↑ 返回', 120, 224, 12, C.DIM, 'center');
      } else {
        txt(g, '配对中', 120, 108, 18, C.INK, 'center');
        txt(g, String(Math.ceil((st.pairing.until - now) / 1000)), 120, 162, 48, ACCENT.conn, 'center', NUM);
        txt(g, '在电脑或手机的蓝牙里选择', 120, 190, 12, C.INK, 'center');
        txt(g, '「NABO 工具箱」', 120, 208, 16, C.INK, 'center');
        txt(g, 'OK 停止配对', 120, 228, 12, C.DIM, 'center');
      }
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
      ['开机语音', s.voice ? '开' : '关', '“那波，陪你遥控万物！”'],
      ['演讲时长', T.TALK_MIN[s.talk] + ' 分钟', 'PPT 计时的目标时长'],
      ['自动休眠', sl ? sl + ' 分钟' : '连接时不休眠', '计时、倒数、配对时不休眠'],
      ['息屏遥控', s.remoteDim ? '开' : '关', s.remoteDim ? '短键照常发送 · 长OK只亮屏' : '遥控时保持亮屏'],
      ['关于', 'v0.1 原型', '离线 · 蓝牙键盘 · 不联网'],
    ];
    rows.forEach((r, i) => {
      const y = 42 + i * 36, sel = i === st.setSel;
      rr(g, 10, y, 220, 32, 8, sel ? C.GOLD : C.PANEL, sel ? C.INK : null, 2);
      txt(g, r[0], 22, y + 22, 16, sel ? C.INK : C.PAPER);
      txt(g, fit(g, r[1], 116, 16), 218, y + 22, 16, sel ? C.INK : ACCENT.set, 'right');
    });
    txt(g, fit(g, rows[st.setSel][2], 224, 12), 120, 275, 12, C.DIM, 'center');
    bottomBar(g, '↑↓ 选择 · OK 修改 · 长按↑ 返回');
  }

  root.TKDraw = { C, ACCENT, NAME, FONT, NUM, txt, fit, rr, chordLabel, topBar, bottomBar, nabo, naboBust, sprite, toast, legend,
                  drawMenu, drawVoice, drawConn, drawOsPick, drawSet };
})(window);
