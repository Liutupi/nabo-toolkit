/* F2 USB protocol client. No port opens until the user clicks Connect. */
(function (root) {
  'use strict';
  const C = root.TKConfig;
  function unbase64(s) {
    if (!s.length || s.length > 64 || s.length % 4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(s)) throw new Error('base64');
    const raw = atob(s); if (btoa(raw) !== s) throw new Error('base64'); return Uint8Array.from(raw, (c) => c.charCodeAt(0));
  }
  const base64 = (data) => btoa(String.fromCharCode(...data));
  class Client {
    constructor(send, timeoutMs = 10000) { this.send = send; this.timeoutMs = timeoutMs; this.pending = null; this.busy = false; this.closed = false; }
    receive(line) {
      if (!line.startsWith('tk.cfg.') || !this.pending) return;
      const p = this.pending;
      try {
        if (line.length > 95) throw new Error('line');
        if (line.startsWith('tk.cfg.err ')) throw new Error(line.slice(11));
        const result = p.accept(line);
        if (result !== undefined) { this.pending = null; clearTimeout(p.timer); p.resolve(result); }
        else { clearTimeout(p.timer); p.timer = setTimeout(() => this.disconnect(new Error('timeout')), this.timeoutMs); }
      } catch (e) { this.pending = null; clearTimeout(p.timer); p.reject(e); }
    }
    disconnect(error = new Error('connection')) {
      this.closed = true;
      if (this.pending) { const p = this.pending; this.pending = null; clearTimeout(p.timer); p.reject(error); }
    }
    async request(line, accept) {
      if (this.closed || this.pending) throw new Error(this.closed ? 'connection' : 'busy');
      return new Promise((resolve, reject) => {
        const p = { accept, resolve, reject, timer: setTimeout(() => this.disconnect(new Error('timeout')), this.timeoutMs) };
        this.pending = p;
        Promise.resolve().then(() => this.send(line)).catch((e) => { if (this.pending === p) { this.pending = null; clearTimeout(p.timer); reject(e); } });
      });
    }
    expect(command, pattern) { return this.request(command, (line) => { if (!pattern.test(line)) throw new Error('protocol'); return line; }); }
    async operation(fn) { if (this.busy) throw new Error('busy'); this.busy = true; try { return await fn(); } finally { this.busy = false; } }
    async readBody() {
      let expected = null, received = 0; const chunks = [];
      return this.request('>tk.cfg.read', (line) => {
        let match;
        if ((match = /^tk\.cfg\.begin ([0-9]+)$/.exec(line)) && expected === null) {
          expected = Number(match[1]); if (expected < 1 || expected > C.LIMIT.bytes) throw new Error('size');
        } else if (line.startsWith('tk.cfg.data ') && expected !== null) {
          const bytes = unbase64(line.slice(12)); received += bytes.length; if (received > expected) throw new Error('size'); chunks.push(bytes);
        } else if ((match = /^tk\.cfg\.end ([0-9a-fA-F]{8})$/.exec(line)) && expected !== null) {
          if (received !== expected) throw new Error('size');
          const bytes = new Uint8Array(received); let offset = 0; for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
          if (C.crc32(bytes) !== Number.parseInt(match[1], 16)) throw new Error('crc');
          return C.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
        } else throw new Error('protocol');
        return undefined;
      });
    }
    read() { return this.operation(async () => { await this.expect('>tk.cfg.abort', /^tk\.cfg\.aborted$/); return this.readBody(); }); }
    write(config) {
      const valid = C.validate(config), bytes = C.bytes(C.encode(valid));
      return this.operation(async () => {
        await this.expect('>tk.cfg.abort', /^tk\.cfg\.aborted$/);
        await this.expect('>tk.cfg.begin ' + bytes.length, new RegExp('^tk\\.cfg\\.ready ' + bytes.length + '$'));
        for (let i = 0; i < bytes.length; i += 48) {
          const chunk = bytes.slice(i, i + 48), received = i + chunk.length;
          await this.expect('>tk.cfg.data ' + base64(chunk), new RegExp('^tk\\.cfg\\.more ' + received + '$'));
        }
        const crc = C.crc32(bytes).toString(16).padStart(8, '0');
        await this.expect('>tk.cfg.end ' + crc, new RegExp('^tk\\.cfg\\.ok ' + bytes.length + ' ' + crc + '$', 'i'));
        const readback = await this.readBody(); if (C.encode(readback) !== C.encode(valid)) throw new Error('readback'); return readback;
      });
    }
  }
  async function connect(serial, onDisconnect) {
    if (!serial) throw new Error('unsupported');
    const port = await serial.requestPort(); await port.open({ baudRate: 115200 });
    let reader, writer, client;
    try { reader = port.readable.getReader(); writer = port.writable.getWriter(); }
    catch (e) { if (reader) reader.releaseLock(); await port.close(); throw e; }
    client = new Client((line) => writer.write(C.bytes(line + '\n')));
    let closing = false;
    const pump = (async () => {
      const decoder = new TextDecoder(); let fragment = '', discard = false;
      try {
        for (;;) {
          const { value, done } = await reader.read(); if (done) break;
          for (const ch of decoder.decode(value, { stream: true })) {
            if (ch === '\r') continue;
            if (ch === '\n') { if (!discard) client.receive(fragment); fragment = ''; discard = false; }
            else if (fragment.length < 256) fragment += ch; else { if (fragment.startsWith('tk.cfg.')) client.disconnect(new Error('line')); discard = true; }
          }
        }
      } catch (_) { /* Connection outcome is reported without raw serial data. */ }
      finally { client.disconnect(); if (!closing && onDisconnect) onDisconnect(); }
    })();
    return { client, async close() {
      if (closing) return; closing = true; client.disconnect();
      await Promise.allSettled([reader.cancel(), writer.abort()]); await pump; reader.releaseLock(); writer.releaseLock(); await port.close();
    } };
  }
  root.TKConfigSerial = { Client, connect };
})(typeof window !== 'undefined' ? window : globalThis);
