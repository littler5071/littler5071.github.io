/* ===== 跨視窗訊息匯流排（postMessage + BroadcastChannel 雙軌） ===== */
(function (global) {
  'use strict';

  const CHANNEL = 'lucky-draw-v1';
  const DEDUPE_MS = 3000;
  const seen = new Map();
  const listeners = [];
  let ch = null;

  try {
    if ('BroadcastChannel' in global) ch = new BroadcastChannel(CHANNEL);
  } catch (e) { ch = null; }

  function isFresh(id) {
    if (!id) return true;
    const now = Date.now();
    if (seen.size > 200) {
      for (const [k, t] of seen) if (now - t > DEDUPE_MS) seen.delete(k);
    }
    if (seen.has(id)) return false;
    seen.set(id, now);
    return true;
  }

  function dispatch(msg) {
    if (!msg || typeof msg !== 'object' || !msg.type) return;
    if (!isFresh(msg.id)) return;
    listeners.slice().forEach(fn => {
      try { fn(msg); } catch (err) { console.error('[bus]', err); }
    });
  }

  function unwrap(data) {
    return data && data.__luckyDraw === 1 ? data.payload : null;
  }

  global.addEventListener('message', e => {
    const m = unwrap(e.data);
    if (m) dispatch(m);
  });
  if (ch) ch.onmessage = e => { const m = unwrap(e.data); if (m) dispatch(m); };

  const Bus = {
    on(fn) {
      listeners.push(fn);
      return () => {
        const i = listeners.indexOf(fn);
        if (i >= 0) listeners.splice(i, 1);
      };
    },
    send(msg, win) {
      const payload = Object.assign({
        id: Math.random().toString(36).slice(2, 10) + Date.now().toString(36)
      }, msg);
      const wrapped = { __luckyDraw: 1, payload };
      if (win && !win.closed) {
        try { win.postMessage(wrapped, '*'); } catch (e) { /* ignore */ }
      }
      if (ch) {
        try { ch.postMessage(wrapped); } catch (e) { /* ignore */ }
      }
      return payload;
    },
    local(msg) {
      dispatch(Object.assign({ id: 'local-' + Math.random() }, msg));
    }
  };

  global.Bus = Bus;
})(window);
