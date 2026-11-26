/* ===== 舞台畫面：動畫時序控制 ===== */
(function () {
  'use strict';

  const $ = s => document.querySelector(s);
  const el = {
    body: document.body,
    eventName: $('#eventName'),
    poolInfo: $('#poolInfo'),
    clock: $('#clock'),
    eyebrow: $('#eyebrow'),
    slot: $('#slot'),
    name: $('#name'),
    dept: $('#dept'),
    winners: $('#winners'),
    prizeTag: $('#prizeTag'),
    hint: $('#hint'),
    flash: $('#flash'),
    unlock: $('#unlock')
  };

  const TIER = {
    1: { c: '#ffd166', c2: '#fff0c2', deep: '#b3760f' },   // 金星
    2: { c: '#ff4d5a', c2: '#ffc2c8', deep: '#8e1b26' },   // 聖誕紅
    3: { c: '#3ddc84', c2: '#c8ffe0', deep: '#12703f' },   // 聖誕綠
    4: { c: '#7fd8ff', c2: '#d8f6ff', deep: '#1a6d8c' }    // 冰藍
  };

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));

  let running = false;
  let soundOn = true;
  let musicUserOn = true;
  let musicDrawPaused = false;
  let applauseOn = true;
  let snapshot = null;
  let slotHideTimer = null;

  // 背景音樂：使用者開關（設定）＋ 抽獎暫停（由控制台恢復）
  function syncBGM() {
    if (!SFX.unlocked) return;
    if (musicUserOn && !musicDrawPaused) SFX.startBGM();
    else SFX.stopBGM();
  }

  // 回覆一律送回開啟本視窗的控制台（file:// 下 BroadcastChannel 可能不可用）
  function send(msg) {
    Bus.send(msg, window.opener || undefined);
  }

  /* ---------------- 基本狀態 ---------------- */
  function setPhase(p) {
    el.body.dataset.phase = p;
  }

  function setAccent(tier) {
    const t = TIER[tier] || TIER[4];
    const s = document.documentElement.style;
    s.setProperty('--accent', t.deep);
    s.setProperty('--accent-2', t.c2);
    s.setProperty('--accent-deep', t.deep);
    s.setProperty('--accent-bright', t.c);
    FX.setAccent(t.deep, tier === 1 ? 1.45 : tier === 2 ? 1.15 : tier === 3 ? 1 : 0.85);
  }

  function setName(text) {
    el.name.textContent = text;
    const n = Array.from(String(text)).length;
    el.name.classList.remove('len-4', 'len-5', 'len-6', 'len-long');
    if (n === 4) el.name.classList.add('len-4');
    else if (n === 5) el.name.classList.add('len-5');
    else if (n === 6) el.name.classList.add('len-6');
    else if (n > 6) el.name.classList.add('len-long');
  }

  function showDept(text) {
    el.dept.textContent = text || '';
    el.dept.classList.toggle('show', !!text);
  }

  function clearWinners() {
    el.winners.innerHTML = '';
    el.winners.classList.remove('show', 'many');
    el.slot.style.opacity = '';
    el.slot.style.transform = '';
  }

  function addCard(w, many) {
    const d = document.createElement('div');
    d.className = 'winner-card';
    const sub = [w.dept, (snapshot && snapshot.settings && snapshot.settings.showEmpNo) ? w.empNo : '']
      .filter(Boolean).join(' · ');
    d.innerHTML = `<div class="wc-name">${esc(w.name)}</div>` +
      (sub ? `<div class="wc-dept">${esc(sub)}</div>` : '');
    el.winners.appendChild(d);
    el.winners.classList.add('show');
    if (many) el.winners.classList.add('many');
  }

  function flash(strength) {
    el.flash.style.opacity = '';
    el.flash.classList.remove('go');
    void el.flash.offsetWidth;
    el.flash.classList.add('go');
    setTimeout(() => el.flash.classList.remove('go'), 800);
  }

  /* ---------------- 翻滾動畫 ---------------- */
  function spinReel(names, duration, tease) {
    return new Promise(resolve => {
      const t0 = performance.now();
      let last = 0;
      let decoy = null;
      let teased = false;
      const pool = names && names.length ? names : ['？'];

      setPhase('roll');

      function frame(now) {
        const t = Math.min(1, (now - t0) / duration);
        let iv;

        if (!tease) {
          iv = 30 + 320 * Math.pow(t, 3.4);
        } else if (t < 0.56) {
          iv = 28 + 26 * t;
        } else if (t < 0.755) {
          iv = 44 + ((t - 0.56) / 0.195) * 290;
        } else if (t < 0.865) {
          iv = 4000;
          if (!teased) {
            teased = true;
            decoy = pool[Math.floor(Math.random() * pool.length)];
            setName(decoy);
            setPhase('lock');
            el.eyebrow.textContent = '是… 嗎？';
            if (SFX.enabled) SFX.tease();
            if (SFX.enabled) SFX.heartbeat(1.1);
          }
        } else if (t < 0.945) {
          iv = 26;
          if (el.body.dataset.phase === 'lock') {
            setPhase('roll');
            el.eyebrow.textContent = '倒數揭曉';
            if (SFX.enabled) SFX.riser(0.6);
          }
        } else {
          iv = 70 + ((t - 0.945) / 0.055) * 300;
        }

        if (now - last >= iv && t < 1) {
          last = now;
          if (t < 0.865 || !teased) {
            setName(pool[Math.floor(Math.random() * pool.length)]);
          }
          if (SFX.enabled) SFX.tick(0.03 + 0.05 * (1 - t));
        }

        if (t < 1) requestAnimationFrame(frame);
        else resolve();
      }
      requestAnimationFrame(frame);
    });
  }

  /* ---------------- 單次抽獎流程 ---------------- */
  async function revealOne(w, index, total, payload) {
    const tier = payload.prize.tier || 4;
    // 低階獎項與大量名額自動加快，避免 20 位抽 2 分鐘
    const rapid = total >= 12 ? 0.55 : total >= 6 ? 0.78 : 1;
    const tierMul = tier === 1 ? 1.3 : tier === 2 ? 1.12 : tier === 3 ? 0.9 : 0.75;
    const spinMs = Math.max(1400, Math.round((payload.settings.spinMs || 4200) * tierMul * rapid));
    const chargeMs = Math.max(420, Math.round((tier === 1 ? 1500 : tier === 2 ? 1100 : tier === 3 ? 900 : 700) * rapid));
    const holdMs = total >= 8 ? 480 : (tier === 1 ? 900 : 700);

    /* 1. 蓄勢 */
    setPhase('charge');
    el.eyebrow.textContent = tier === 1 ? '最緊張的時刻' : '下一組幸運兒';
    el.hint.textContent = total > 1 ? `${payload.prize.name}　第 ${index + 1} / ${total} 位` : '準備揭曉';
    setName('？'.repeat(tier === 1 ? 3 : 1));
    showDept('');
    FX.vortex(true);
    FX.nameCloud(payload.poolNames, true);
    if (SFX.enabled) {
      SFX.whoosh(0.8);
      SFX.heartbeat(1);
      if (tier === 1) {
        SFX.startDrone();
        await sleep(Math.round(420 * rapid));
        SFX.heartbeat(1.2);
      }
      SFX.riser(spinMs / 1000);
    }
    await sleep(chargeMs);

    /* 2. 翻滾 */
    if (SFX.enabled) SFX.drumroll(spinMs / 1000 + 0.4);
    el.eyebrow.textContent = tier === 1 ? '即將抽出頭獎' : '抽獎中';
    await spinReel(payload.poolNames, spinMs, !!payload.settings.tease);
    if (SFX.enabled) SFX.stopDrone();

    /* 3. 定格 + 揭曉 */
    setName(w.name);
    setPhase('lock');
    el.eyebrow.textContent = '恭喜';
    if (SFX.enabled) {
      SFX.heartbeat(1.35);
      SFX.impact(tier === 1 ? 1.5 : tier === 2 ? 1.15 : 0.9);
    }
    await sleep(tier === 1 ? 620 : 480);

    setPhase('reveal');
    el.eyebrow.textContent = '恭喜得獎';
    el.hint.textContent = '請上台領獎';
    showDept([w.dept, (payload.settings.showEmpNo ? w.empNo : '')].filter(Boolean).join(' · '));
    FX.vortex(false);
    FX.nameScatter();
    el.body.classList.remove('shake');
    void el.body.offsetWidth;
    el.body.classList.add('shake');
    setTimeout(() => el.body.classList.remove('shake'), 640);
    if (SFX.enabled) SFX.fanfare(tier);
    if (SFX.enabled && applauseOn) setTimeout(() => SFX.playApplause(), 230);
    // 先讓名字彈出站穩，再炸彩帶（避免一瞬間把名字蓋住）
    setTimeout(() => {
      FX.burst(tier === 1 ? 1.7 : tier === 2 ? 1.35 : 1.1);
      flash();
    }, 200);
    if (tier === 1 && SFX.enabled) setTimeout(() => { SFX.shimmer(); }, 600);

    if (total > 1) addCard(w, total > 8);
    await sleep(holdMs);
  }

  async function runDraw(payload) {
    if (running) return;
    running = true;
    setAccent(payload.prize.tier);
    clearWinners();
    clearTimeout(slotHideTimer);
    el.slot.style.display = '';
    el.slot.style.opacity = '';
    el.prizeTag.textContent = `${payload.prize.name} · ${payload.count} 名`;
    document.body.style.setProperty('--glow', 1);
    if (SFX.enabled) SFX.unlock && SFX.unlock();
    // 一抽獎就關閉背景音樂，之後由控制台「播放音樂」恢復
    musicDrawPaused = true;
    syncBGM();

    try {
      const list = payload.winners || [];
      for (let i = 0; i < list.length; i++) {
        await revealOne(list[i], i, list.length, payload);
        if (i < list.length - 1) {
          setPhase('charge');
          el.slot.style.opacity = '0';
          el.slot.style.transform = 'translateY(-16px) scale(.94)';
          showDept('');
          await sleep(list.length >= 8 ? 200 : 420);
          el.slot.style.opacity = '';
          el.slot.style.transform = '';
        }
      }

      setPhase('result');
      el.eyebrow.textContent = list.length > 1 ? `${payload.prize.name} 得獎者` : '恭喜得獎';
      if (list.length > 1) {
        el.slot.style.opacity = '0';
        el.slot.style.transform = 'scale(.9)';
        el.winners.classList.add('show');
        el.hint.textContent = `本輪共 ${list.length} 位，請依序上台`;
        clearTimeout(slotHideTimer);
        slotHideTimer = setTimeout(() => { el.slot.style.display = 'none'; }, 700);
      } else {
        el.hint.textContent = '請上台領獎';
      }
      FX.sparkle();
      if (SFX.enabled) setTimeout(() => SFX.shimmer(), 700);
    } catch (err) {
      console.error('[stage]', err);
      Bus.send({ type: 'anim-error', roundId: payload.roundId, reason: String(err && err.message || err) }, window.opener || undefined);
    }

    running = false;
    send({ type: 'draw-done', roundId: payload.roundId });
  }

  /* ---------------- 待機 / 狀態 ---------------- */
  function renderIdle() {
    setPhase('idle');
    clearWinners();
    clearTimeout(slotHideTimer);
    el.slot.style.display = '';
    el.slot.style.opacity = '';
    el.slot.style.transform = '';
    setAccent(1);
    setName('聖誕快樂');
    showDept('');
    el.eyebrow.textContent = 'MERRY CHRISTMAS';
    el.hint.textContent = '等待控制台操作';
    el.prizeTag.textContent = snapshot
      ? `已抽出 ${snapshot.winnersCount} 位 · 候選 ${snapshot.stats.pool} 人`
      : '';
    FX.vortex(false);
    FX.nameCloud(null, false);
    el.body.classList.remove('shake');
  }

  function applySnapshot(snap) {
    if (!snap) return;
    snapshot = snap;
    el.eventName.textContent = snap.eventName || 'LUCKY DRAW';
    soundOn = !(snap.settings && snap.settings.sound === false);
    musicUserOn = !(snap.settings && snap.settings.music === false);
    applauseOn = !(snap.settings && snap.settings.applause === false);
    if (snap.settings) {
      if (snap.settings.bgm && snap.settings.bgm !== SFX.bgmTrack) SFX.setBGMTrack(snap.settings.bgm);
      if (snap.settings.drawStyle) SFX.setDrawStyle(snap.settings.drawStyle);
    }
    SFX.enabled = soundOn;
    syncBGM();
    if (snap.stats) {
      el.poolInfo.innerHTML = `候選 <b>${snap.stats.pool}</b> 人<br>已抽出 ${snap.winnersCount || 0} 位`;
      if (el.body.dataset.phase === 'idle') {
        el.prizeTag.textContent = `已抽出 ${snap.winnersCount || 0} 位 · 候選 ${snap.stats.pool} 人`;
      }
    }
  }

  /* ---------------- 連線 ---------------- */
  function hello() {
    send({ type: 'hello', unlocked: !!(window.SFX && SFX.unlocked) });
  }

  Bus.on(msg => {
    switch (msg.type) {
      case 'state':
        applySnapshot(msg.payload);
        break;
      case 'draw':
        applySnapshot(Object.assign({}, snapshot || {}, {
          settings: msg.payload.settings,
          eventName: snapshot ? snapshot.eventName : ''
        }));
        runDraw(msg.payload);
        break;
      case 'idle':
        if (!running) renderIdle();
        break;
      case 'blackout':
        if (running) return;
        if (msg.on) setPhase('blackout');
        else renderIdle();
        break;
      case 'ping':
        send({ type: 'pong' });
        break;
      case 'test':
        flash();
        if (SFX.enabled) SFX.shimmer();
        if (snapshot) {
          el.hint.textContent = '訊號正常　' + new Date().toLocaleTimeString('zh-TW', { hour12: false });
          setTimeout(() => { if (!running) el.hint.textContent = '等待控制台操作'; }, 3000);
        }
        break;
      case 'setting':
        soundOn = !!msg.sound;
        SFX.enabled = soundOn;
        syncBGM();
        break;
      case 'music':
        musicUserOn = !!msg.on;
        if (msg.on) musicDrawPaused = false;
        syncBGM();
        break;
    }
  });

  /* ---------------- 啟動 ---------------- */
  FX.init($('#fx'));

  el.unlock.addEventListener('click', () => {
    SFX.unlock();
    el.unlock.classList.add('hide');
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(() => {});
    }
    if (SFX.enabled) SFX.shimmer();
    syncBGM();
    send({ type: 'unlocked' });
    hello();
  });

  document.addEventListener('keydown', e => {
    if (e.key.toLowerCase() === 'f') {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {});
      else document.exitFullscreen().catch(() => {});
    }
    if (e.key.toLowerCase() === 'h') {
      el.unlock.classList.toggle('hide');
    }
  });

  function tickClock() {
    const d = new Date();
    el.clock.textContent = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  }
  tickClock();
  setInterval(tickClock, 15000);

  // 從 localStorage 取回上一次狀態（重開投影視窗時仍有基本資訊）
  try {
    const raw = localStorage.getItem('luckyDraw.v1');
    if (raw) {
      const st = JSON.parse(raw);
      const total = (st.roster || []).length;
      const won = new Set((st.winners || []).map(w => w.key)).size;
      applySnapshot({
        eventName: st.eventName || 'LUCKY DRAW',
        settings: st.settings || {},
        winnersCount: (st.winners || []).length,
        stats: { total, pool: Math.max(0, total - won), won }
      });
    }
  } catch (e) { /* ignore */ }

  renderIdle();
  hello();
  setInterval(hello, 4000);

  window.__stage = { runDraw, applySnapshot, renderIdle };
})();
