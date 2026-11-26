/* ===== 資料層：名單、獎項、抽獎邏輯、持久化 ===== */
(function (global) {
  'use strict';

  const KEY = 'luckyDraw.v1';
  const DEFAULT_EVENT_NAME = '聖誕晚會抽獎';
  const TIER_COLORS = { 1: '#b3760f', 2: '#c8102e', 3: '#128a4a', 4: '#1a6d8c' };

  const uid = p => (p || 'id') + Math.random().toString(36).slice(2, 9);

  function defaults() {
    return {
      version: 1,
      eventName: DEFAULT_EVENT_NAME,
      roster: [],
      winners: [],
      excluded: [],
      lastRoundId: null,
      settings: {
        spinMs: 4200,
        tease: true,
        sound: true,
        music: true,
        bgm: 'jingle',
        drawStyle: 'orchestra',
        applause: true,
        showEmpNo: false,
        allowRepeat: false,
        idleText: '聖誕快樂',
        kickerText: 'MERRY CHRISTMAS'
      }
    };
  }

  function defaultPrizes() {
    return [
      { id: uid('p'), name: '參加獎', count: 20, tier: 4 },
      { id: uid('p'), name: '三獎', count: 5, tier: 3 },
      { id: uid('p'), name: '二獎', count: 3, tier: 2 },
      { id: uid('p'), name: '頭獎', count: 1, tier: 1 }
    ];
  }

  function seedState() {
    const s = defaults();
    s.prizes = defaultPrizes();
    return s;
  }

  function clampState(raw) {
    const base = seedState();
    const s = Object.assign(base, raw || {});
    s.roster = Array.isArray(s.roster) ? s.roster : [];
    s.winners = Array.isArray(s.winners) ? s.winners : [];
    s.excluded = Array.isArray(s.excluded) ? s.excluded : [];
    s.prizes = Array.isArray(s.prizes) && s.prizes.length ? s.prizes : defaultPrizes();
    s.settings = Object.assign({}, base.settings, s.settings || {});
    // 舊版預設活動名稱自動遷移（避免重新整理後還看到舊標題）
    const LEGACY_NAMES = ['員工大會 · 年度抽獎', '員工大會 年度抽獎', '員工大會抽獎'];
    if (!s.eventName || LEGACY_NAMES.indexOf(s.eventName) >= 0) s.eventName = DEFAULT_EVENT_NAME;
    s.prizes.forEach(p => {
      p.id = p.id || uid('p');
      p.count = Math.max(0, Number(p.count) || 0);
      p.tier = Number(p.tier) >= 1 && Number(p.tier) <= 4 ? Number(p.tier) : 4;
      p.name = p.name || '獎項';
    });
    return s;
  }

  function load() {
    try {
      const txt = localStorage.getItem(KEY);
      if (!txt) return seedState();
      return clampState(JSON.parse(txt));
    } catch (e) {
      return seedState();
    }
  }

  let state = load();
  const subs = [];

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* 空間不足時仍可繼續運作 */ }
  }
  function commit() { save(); subs.forEach(fn => { try { fn(state); } catch (e) { console.error(e); } }); }

  /* ---------- 名單解析 ---------- */
  const HEADER_MAP = {
    name: ['姓名', '名字', '員工姓名', '人員', 'name', 'employee', 'member'],
    dept: ['部門', '單位', '部門/單位', '組別', 'team', 'dept', 'department', 'org'],
    empNo: ['員工編號', '編號', '工號', '員工代號', '員編', 'id', 'empno', 'emp_no', 'employeeid', 'employee_id']
  };

  function detectDelimiter(lines) {
    const score = { '\t': 0, ',': 0, ';': 0, '|': 0 };
    lines.slice(0, 12).forEach(l => {
      Object.keys(score).forEach(d => { score[d] += (l.split(d).length - 1); });
    });
    let best = '\t', bestN = -1;
    Object.keys(score).forEach(d => { if (score[d] > bestN) { bestN = score[d]; best = d; } });
    if (bestN <= 0) {
      // 空白分隔（先嘗試兩個以上空白）
      return /\s{2,}/.test(lines[0]) ? 'WS' : 'NONE';
    }
    return best;
  }

  function splitLine(line, delim) {
    if (delim === 'WS') return line.trim().split(/\s{2,}/);
    if (delim === 'NONE') return [line.trim()];
    const out = [];
    let cur = '', quoted = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"') {
        if (quoted && line[i + 1] === '"') { cur += '"'; i++; }
        else quoted = !quoted;
      } else if (c === delim && !quoted) { out.push(cur); cur = ''; }
      else cur += c;
    }
    out.push(cur);
    return out.map(c => c.trim());
  }

  function matchHeader(cell) {
    const v = String(cell || '').replace(/[\s_\-（）()]/g, '').toLowerCase();
    for (const key of Object.keys(HEADER_MAP)) {
      if (HEADER_MAP[key].some(h => v === h.replace(/[\s_\-（）()]/g, '').toLowerCase())) return key;
    }
    return null;
  }

  function parseRoster(text) {
    const rawLines = String(text || '').replace(/\r/g, '').split('\n');
    const lines = rawLines.filter(l => l.trim() !== '');
    if (!lines.length) return [];

    const delim = detectDelimiter(lines);
    let rows = lines.map(l => splitLine(l, delim)).filter(r => r.some(c => c !== ''));

    let map = { name: 0, dept: 1, empNo: 2 };
    const head = rows[0].map(matchHeader);
    if (head.includes('name') || head.includes('dept')) {
      map = { name: head.indexOf('name'), dept: head.indexOf('dept'), empNo: head.indexOf('empNo') };
      rows = rows.slice(1);
    }

    const out = [];
    rows.forEach(r => {
      const pick = i => (i >= 0 && i < r.length ? String(r[i] || '').trim() : '');
      const name = pick(map.name);
      if (!name) return;
      if (/^(姓名|name|合計|總計|total)$/i.test(name)) return;
      out.push({ name, dept: pick(map.dept), empNo: pick(map.empNo) });
    });
    return out;
  }

  function normalizeRoster(list) {
    const seen = new Set();
    return (list || []).map(item => {
      const name = String(item.name || '').trim();
      const dept = String(item.dept || '').trim();
      const empNo = String(item.empNo || '').trim();
      let key = empNo ? 'e:' + empNo : 'n:' + name + '|' + dept;
      let n = 2;
      while (seen.has(key)) { key = (empNo ? 'e:' + empNo : 'n:' + name + '|' + dept) + '#' + n; n++; }
      seen.add(key);
      return { key, name, dept, empNo };
    }).filter(p => p.name);
  }

  /* ---------- 抽獎核心 ---------- */
  function shuffle(arr) {
    const a = arr.slice();
    const rnd = new Uint32Array(Math.max(a.length, 1));
    (global.crypto || global.msCrypto).getRandomValues(rnd);
    for (let i = a.length - 1; i > 0; i--) {
      const j = rnd[i] % (i + 1);
      const t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function wonKeySet() {
    return new Set(state.winners.map(w => w.key));
  }

  function pool() {
    const won = wonKeySet();
    const excluded = new Set(state.excluded);
    return state.roster.filter(p =>
      !excluded.has(p.key) && (state.settings.allowRepeat || !won.has(p.key))
    );
  }

  function prizeOf(id) {
    return state.prizes.find(p => p.id === id) || null;
  }

  function prizeProgress(prizeId) {
    return state.winners.filter(w => w.prizeId === prizeId).length;
  }

  function stats() {
    return {
      total: state.roster.length,
      pool: pool().length,
      won: new Set(state.winners.map(w => w.key)).size,
      excluded: state.excluded.length,
      totalWinners: state.winners.length
    };
  }

  function draw(prizeId, count) {
    const prize = prizeOf(prizeId);
    if (!prize) return { ok: false, reason: '找不到獎項' };
    const candidates = pool();
    if (!candidates.length) return { ok: false, reason: '沒有可抽的候選人了' };

    const want = Math.max(1, Math.floor(Number(count) || 1));
    const n = Math.min(want, candidates.length);
    const picked = shuffle(candidates).slice(0, n);
    const roundId = uid('r');
    const ts = Date.now();

    const winners = picked.map(p => ({
      roundId,
      prizeId,
      prizeName: prize.name,
      key: p.key,
      name: p.name,
      dept: p.dept,
      empNo: p.empNo,
      ts,
      poolSize: candidates.length
    }));

    state.winners.push(...winners);
    state.lastRoundId = roundId;
    commit();

    return {
      ok: true,
      roundId,
      prize: Object.assign({}, prize),
      winners: winners.map(w => Object.assign({}, w)),
      count: n,
      requested: want,
      truncated: n < want,
      poolSize: candidates.length,
      poolNames: candidates.map(p => p.name)
    };
  }

  function undoLast() {
    if (!state.winners.length) return { ok: false, reason: '沒有可撤銷的紀錄' };
    const roundId = state.winners[state.winners.length - 1].roundId;
    const removed = state.winners.filter(w => w.roundId === roundId);
    state.winners = state.winners.filter(w => w.roundId !== roundId);
    if (state.lastRoundId === roundId) {
      const last = state.winners[state.winners.length - 1];
      state.lastRoundId = last ? last.roundId : null;
    }
    commit();
    return { ok: true, removed };
  }

  function undoRound(roundId) {
    const removed = state.winners.filter(w => w.roundId === roundId);
    if (!removed.length) return { ok: false };
    state.winners = state.winners.filter(w => w.roundId !== roundId);
    if (state.lastRoundId === roundId) {
      const last = state.winners[state.winners.length - 1];
      state.lastRoundId = last ? last.roundId : null;
    }
    commit();
    return { ok: true, removed };
  }

  /* ---------- 操作 ---------- */
  const Store = {
    get state() { return state; },
    get settings() { return state.settings; },
    TIER_COLORS,

    subscribe(fn) { subs.push(fn); return () => subs.splice(subs.indexOf(fn), 1); },

    pool, stats, prizeOf, prizeProgress, parseRoster, normalizeRoster,

    setEventName(name) { state.eventName = String(name || '').slice(0, 60); commit(); },

    setRoster(list) {
      state.roster = normalizeRoster(list);
      const keys = new Set(state.roster.map(p => p.key));
      state.excluded = state.excluded.filter(k => keys.has(k));
      commit();
      return state.roster.length;
    },

    appendRoster(list) {
      const merged = normalizeRoster(state.roster.concat(list || []));
      state.roster = merged;
      commit();
      return merged.length;
    },

    toggleExclude(key) {
      const i = state.excluded.indexOf(key);
      if (i >= 0) state.excluded.splice(i, 1); else state.excluded.push(key);
      commit();
    },

    addPrize(data) {
      const p = {
        id: uid('p'),
        name: (data && data.name) || '新獎項',
        count: Math.max(1, Number(data && data.count) || 1),
        tier: (data && data.tier) || 4
      };
      state.prizes.push(p);
      commit();
      return p;
    },

    updatePrize(id, patch) {
      const p = prizeOf(id);
      if (!p) return null;
      Object.assign(p, patch);
      p.count = Math.max(0, Number(p.count) || 0);
      p.tier = Math.min(4, Math.max(1, Number(p.tier) || 4));
      commit();
      return p;
    },

    removePrize(id) {
      state.prizes = state.prizes.filter(p => p.id !== id);
      commit();
    },

    movePrize(id, dir) {
      const i = state.prizes.findIndex(p => p.id === id);
      const j = i + dir;
      if (i < 0 || j < 0 || j >= state.prizes.length) return;
      const t = state.prizes[i]; state.prizes[i] = state.prizes[j]; state.prizes[j] = t;
      commit();
    },

    updateSettings(patch) { Object.assign(state.settings, patch); commit(); },

    draw, undoLast, undoRound,

    resetPrize(prizeId) {
      const before = state.winners.length;
      state.winners = state.winners.filter(w => w.prizeId !== prizeId);
      commit();
      return before - state.winners.length;
    },

    resetAll() {
      state = seedState();
      commit();
      return state;
    },

    replaceState(raw) {
      state = clampState(raw);
      commit();
      return state;
    },

    stageSnapshot() {
      const st = stats();
      return {
        eventName: state.eventName,
        prizes: state.prizes.map(p => ({ id: p.id, name: p.name, count: p.count, tier: p.tier })),
        winnersCount: state.winners.length,
        settings: Object.assign({}, state.settings),
        stats: st,
        poolNames: pool().map(p => p.name),
        lastWinners: state.winners.slice(-30).map(w => ({ name: w.name, dept: w.dept, empNo: w.empNo, prizeName: w.prizeName }))
      };
    },

    exportCsv() {
      const esc = v => {
        const s = String(v == null ? '' : v);
        return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
      };
      const rows = [['獎項', '姓名', '部門', '員工編號', '抽獎時間']];
      const fmt = ts => {
        const d = new Date(ts);
        const p2 = n => String(n).padStart(2, '0');
        return `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())} ${p2(d.getHours())}:${p2(d.getMinutes())}:${p2(d.getSeconds())}`;
      };
      state.winners.forEach(w => rows.push([w.prizeName, w.name, w.dept, w.empNo, fmt(w.ts)]));
      const csv = rows.map(r => r.map(esc).join(',')).join('\r\n');
      return '\ufeff' + csv;
    }
  };

  global.LuckyStore = Store;
})(window);
