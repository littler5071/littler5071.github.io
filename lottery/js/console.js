/* ===== 抽獎控制台 ===== */
(function () {
  'use strict';

  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));
  const Store = window.LuckyStore;
  const S = () => Store.state;

  /* ---------------- 小工具 ---------------- */
  let toastTimer = null;
  function toast(msg, kind) {
    const el = $('#toast');
    el.textContent = msg;
    el.className = 'show ' + (kind || '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.className = kind || ''; }, 2600);
  }

  function pad2(n) { return String(n).padStart(2, '0'); }
  function timeStr(ts) {
    const d = new Date(ts);
    return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
  }
  function dateStamp() {
    const d = new Date();
    return `${d.getFullYear()}${pad2(d.getMonth() + 1)}${pad2(d.getDate())}_${pad2(d.getHours())}${pad2(d.getMinutes())}`;
  }
  function download(filename, content, type) {
    const blob = new Blob([content], { type: type || 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }
  function decodeFile(buffer) {
    let txt = new TextDecoder('utf-8').decode(buffer);
    if (txt.indexOf('\uFFFD') >= 0) {
      try { txt = new TextDecoder('big5').decode(buffer); } catch (e) { /* keep utf-8 */ }
    }
    return txt.replace(/^\uFEFF/, '');
  }

  /* ---------------- Modal ---------------- */
  const mask = $('#modalMask');
  let modalResolve = null;

  function closeModal(value) {
    mask.classList.remove('show');
    const r = modalResolve;
    modalResolve = null;
    if (r) r(value);
  }
  function modalShell(title, desc, bodyHtml) {
    if (mask.classList.contains('show')) closeModal(null);
    $('#modalBox').innerHTML =
      `<h3>${esc(title)}</h3>` +
      (desc ? `<p class="hint">${desc}</p>` : '') +
      `<div class="modal-form">${bodyHtml || ''}</div>` +
      `<div class="modal-actions" id="modalActions"></div>`;
    mask.classList.add('show');
  }
  mask.addEventListener('mousedown', e => { if (e.target === mask) closeModal(null); });

  function confirmModal(opts) {
    return new Promise(resolve => {
      modalResolve = resolve;
      modalShell(opts.title, opts.desc || '');
      const bar = $('#modalActions');
      const cancel = document.createElement('button');
      cancel.className = 'btn ghost';
      cancel.textContent = '取消';
      cancel.onclick = () => closeModal(false);
      const ok = document.createElement('button');
      ok.className = 'btn ' + (opts.danger ? 'danger' : 'primary');
      ok.textContent = opts.okText || '確定';
      ok.onclick = () => closeModal(true);
      bar.appendChild(cancel);
      bar.appendChild(ok);
      setTimeout(() => ok.focus(), 40);
    });
  }

  function chooseModal(opts) {
    return new Promise(resolve => {
      modalResolve = resolve;
      modalShell(opts.title, opts.desc || '');
      const bar = $('#modalActions');
      (opts.choices || []).forEach(c => {
        const b = document.createElement('button');
        b.className = 'btn ' + (c.cls || 'ghost');
        b.textContent = c.label;
        b.onclick = () => closeModal(c.value);
        bar.appendChild(b);
      });
      const cancel = document.createElement('button');
      cancel.className = 'btn ghost';
      cancel.textContent = '取消';
      cancel.onclick = () => closeModal(null);
      bar.appendChild(cancel);
      setTimeout(() => {
        const btns = bar.querySelectorAll('.btn');
        if (btns.length > 1) btns[btns.length - 2].focus();
      }, 40);
    });
  }

  function promptModal(opts) {
    return new Promise(resolve => {
      modalResolve = resolve;
      const fields = (opts.fields || []).map((f, i) => {
        const id = 'mf' + i;
        let input;
        if (f.type === 'textarea') {
          input = `<textarea id="${id}" rows="${f.rows || 8}" placeholder="${esc(f.placeholder || '')}">${esc(f.value || '')}</textarea>`;
        } else if (f.type === 'select') {
          input = `<select id="${id}">${(f.options || []).map(o =>
            `<option value="${esc(o.value)}"${String(o.value) === String(f.value) ? ' selected' : ''}>${esc(o.label)}</option>`).join('')}</select>`;
        } else {
          input = `<input id="${id}" type="${f.type || 'text'}" value="${esc(f.value == null ? '' : f.value)}" placeholder="${esc(f.placeholder || '')}"${f.min != null ? ` min="${f.min}"` : ''}${f.max != null ? ` max="${f.max}"` : ''}>`;
        }
        return `<div class="field"><span>${esc(f.label)}</span>${input}</div>`;
      }).join('');

      modalShell(opts.title, opts.desc || '', fields);
      const bar = $('#modalActions');
      const cancel = document.createElement('button');
      cancel.className = 'btn ghost';
      cancel.textContent = '取消';
      cancel.onclick = () => closeModal(null);
      const ok = document.createElement('button');
      ok.className = 'btn primary';
      ok.textContent = opts.okText || '確定';
      const collect = () => {
        const out = {};
        (opts.fields || []).forEach((f, i) => {
          const el = $('#mf' + i);
          out[f.key] = f.type === 'number' ? Number(el.value) : el.value;
        });
        return out;
      };
      ok.onclick = () => closeModal(collect());
      bar.appendChild(cancel);
      bar.appendChild(ok);
      setTimeout(() => {
        const first = $('#mf0');
        if (first) { first.focus(); first.select && first.select(); }
      }, 60);
    });
  }

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && mask.classList.contains('show')) closeModal(null);
  });

  /* ---------------- 視窗／連線 ---------------- */
  let stageWin = null;
  let stageReady = false;
  let stageUnlocked = false;
  let audioHintShown = false;
  let lastPong = 0;
  let blackout = false;
  let stagePingTimer = null;

  function openStage() {
    if (stageWin && !stageWin.closed) {
      stageWin.focus();
      toast('投影視窗已開啟');
      return;
    }
    stageWin = window.open('stage.html', 'lucky-draw-stage',
      'width=1280,height=760,menubar=no,toolbar=no,location=no,status=no');
    if (!stageWin) {
      toast('瀏覽器封鎖了彈出視窗，請允許後再試', 'bad');
      return;
    }
    setTimeout(() => {
      sendState();
      Bus.send({ type: 'ping' }, stageWin);
    }, 600);
  }

  function sendState() {
    Bus.send({ type: 'state', payload: Store.stageSnapshot() }, stageWin);
  }

  function updateStagePill() {
    const on = stageReady && (Date.now() - lastPong < 9000);
    const pill = $('#stagePill');
    pill.classList.toggle('on', on);
    $('#stagePillText').textContent = on ? '投影畫面已連線' : '投影畫面未連線';
    if (!on) {
      stageReady = false;
      stageUnlocked = false;
      audioHintShown = false;
    }
    $('#btnOpenStage').textContent = (stageWin && !stageWin.closed) ? '投影視窗已開' : '開啟投影畫面';
    renderTip();
  }

  // 捕捉投影視窗來源（不需依賴 window.open 的參考）
  window.addEventListener('message', e => {
    const d = e.data;
    if (!d || d.__luckyDraw !== 1 || !d.payload) return;
    if (!e.source || e.source === window) return;
    if (['hello', 'pong', 'draw-done', 'unlocked'].indexOf(d.payload.type) < 0) return;

    const isNew = stageWin !== e.source;
    stageWin = e.source;
    stageReady = true;
    lastPong = Date.now();
    if (d.payload.unlocked) stageUnlocked = true;
    if (d.payload.type === 'unlocked') stageUnlocked = true;
    updateStagePill();
    if (isNew || d.payload.type === 'hello') {
      sendState();
      Bus.send({ type: 'ping' }, stageWin);
    }
  });

  Bus.on(msg => {
    switch (msg.type) {
      case 'hello':
        stageReady = true;
        lastPong = Date.now();
        if (msg.unlocked) stageUnlocked = true;
        sendState();
        updateStagePill();
        if (!stageUnlocked && !audioHintShown) {
          audioHintShown = true;
          setTimeout(() => toast('提醒：請在投影視窗點一下「點擊啟動舞台」，啟用音效', 'warn'), 1500);
        }
        break;
      case 'unlocked':
        stageUnlocked = true;
        toast('投影音效已啟用');
        break;
      case 'pong':
        stageReady = true;
        lastPong = Date.now();
        updateStagePill();
        break;
      case 'need-state':
        sendState();
        break;
      case 'draw-done':
        finishDraw(msg.roundId);
        break;
      case 'anim-error':
        console.warn('[stage]', msg.reason);
        finishDraw(msg.roundId);
        break;
    }
  });

  function startHeartbeat() {
    clearInterval(stagePingTimer);
    stagePingTimer = setInterval(() => {
      if (stageWin && !stageWin.closed) Bus.send({ type: 'ping' }, stageWin);
      if (stageReady && Date.now() - lastPong > 9000) {
        stageReady = false;
        updateStagePill();
      }
    }, 3000);
  }

  /* ---------------- 抽獎 ---------------- */
  let busy = false;
  let busyTimer = null;
  let currentPrizeId = null;
  let musicPaused = false;

  function updateMusicBtn() {
    const btn = $('#btnMusic');
    if (!btn) return;
    const settingOn = !!S().settings.music;
    const playing = settingOn && !musicPaused;
    btn.textContent = musicPaused ? '♪ 音樂：已暫停' : (settingOn ? '♪ 音樂：開' : '♪ 音樂：關');
    btn.classList.toggle('music-off', !playing);
  }

  function pickDefaultPrize() {
    const prizes = S().prizes;
    const unfinished = prizes.find(p => Store.prizeProgress(p.id) < p.count);
    currentPrizeId = (unfinished || prizes[0] || {}).id || null;
  }

  function setBusy(on, ms) {
    busy = on;
    const btn = $('#btnDraw');
    btn.dataset.busy = on ? '1' : '0';
    btn.disabled = on;
    if (on) {
      $('#btnDrawText').textContent = '抽獎進行中…';
      clearTimeout(busyTimer);
      busyTimer = setTimeout(() => { if (busy) finishDraw(null, true); }, ms || 45000);
    } else {
      updateDrawBtnLabel();
    }
  }

  function finishDraw(roundId, silent) {
    if (!busy) return;
    setBusy(false);
    clearTimeout(busyTimer);
    if (silent) toast('投影畫面無回應，已解除鎖定', 'warn');

    // 這一輪抽完：自動把背景音樂接回來（並維持循環播放）
    if (S().settings.music) {
      musicPaused = false;
      updateMusicBtn();
      Bus.send({ type: 'music', on: true }, stageWin);
    }
  }

  async function startDraw(override) {
    if (busy) return;

    const prize = Store.prizeOf(currentPrizeId);
    if (!prize) { toast('請先選擇獎項', 'warn'); return; }
    if (!S().roster.length) {
      toast('尚未匯入員工名單', 'bad');
      switchTab('roster');
      return;
    }

    const count = Math.max(1, Number(override || $('#drawCount').value) || 1);
    const progress = Store.prizeProgress(prize.id);
    const remainQuota = prize.count - progress;

    if (count > remainQuota && remainQuota >= 0 && !override) {
      const okGo = await confirmModal({
        title: `「${prize.name}」名額只剩 ${remainQuota} 位`,
        desc: `設定名額 ${prize.count} 名，已抽出 ${progress} 名。這次要抽 <b>${count}</b> 名，會超出設定。<br>要繼續嗎？`,
        okText: '繼續抽獎'
      });
      if (!okGo) return;
    }

    if (!stageReady) {
      const go = await confirmModal({
        title: '投影畫面尚未連線',
        desc: '現在抽出將<b>直接記錄結果</b>，但投影畫面不會播放動畫。<br>建議先開啟投影畫面；若臨時故障，可在此繼續。',
        okText: '仍然抽出',
        danger: true
      });
      if (!go) { openStage(); return; }
    }

    const res = Store.draw(prize.id, count);
    if (!res.ok) { toast(res.reason, 'bad'); return; }

    // 依名額估算動畫總長，避免大量抽出時鎖定過早解除
    const perWinner = (S().settings.spinMs || 4200) * 1.35 + 2400;
    setBusy(true, Math.max(20000, Math.round(res.count * perWinner) + 12000));

    const payload = {
      roundId: res.roundId,
      prize: res.prize,
      winners: res.winners,
      count: res.count,
      poolNames: res.poolNames,
      poolSize: res.poolSize,
      settings: Object.assign({}, S().settings)
    };

    if (stageReady) {
      Bus.send({ type: 'draw', payload }, stageWin);
      if (S().settings.music) {
        musicPaused = true;
        updateMusicBtn();
      }
    } else {
      setTimeout(() => finishDraw(res.roundId), 400);
    }

    if (res.truncated) toast(`可抽人數不足，僅抽出 ${res.count} 名`, 'warn');
    else toast(`已抽出 ${res.count} 名：${res.prize.name}`);

    afterDrawUi();
  }

  function updateDrawBtnLabel() {
    if (busy) return;
    const n = Math.max(1, Number($('#drawCount').value) || 1);
    $('#btnDrawText').textContent = n > 1 ? `開始抽獎 · ${n} 名` : '開始抽獎';
  }

  function afterDrawUi() {
    // 抽完一輪回到「1 名」，避免誤按一次抽出整個獎項
    $('#drawCount').value = 1;
    updateDrawBtnLabel();
  }

  async function extraOne() {
    if (busy) return;
    const prize = Store.prizeOf(currentPrizeId);
    if (!prize) { toast('請先選擇獎項', 'warn'); return; }
    await startDraw(1);
  }

  async function adhocPrize() {
    if (busy) return;
    const vals = await promptModal({
      title: '臨時加碼',
      desc: '新增一個臨時獎項，抽出後同樣計入中獎紀錄。',
      okText: '建立並選擇',
      fields: [
        { key: 'name', label: '獎項名稱', value: '加碼獎', placeholder: '例如：董事長加碼' },
        { key: 'count', label: '名額', type: 'number', value: 1, min: 1, max: 300 },
        { key: 'tier', label: '視覺等級', type: 'select', value: '1', options: [
          { value: '1', label: '金（最高規格）' },
          { value: '2', label: '紅' },
          { value: '3', label: '紫' },
          { value: '4', label: '青' }
        ] }
      ]
    });
    if (!vals) return;
    const p = Store.addPrize({ name: vals.name, count: vals.count, tier: Number(vals.tier) });
    currentPrizeId = p.id;
    renderAll();
    $('#drawCount').value = Math.max(1, p.count);
    updateDrawBtnLabel();
    toast(`已建立「${p.name}」，按 Enter 開抽`);
  }

  async function undoLast() {
    if (busy) { toast('抽獎進行中，請稍候', 'warn'); return; }
    if (!S().winners.length) { toast('沒有可撤銷的紀錄', 'warn'); return; }
    const last = S().winners[S().winners.length - 1];
    const roundWinners = S().winners.filter(w => w.roundId === last.roundId);
    const ok = await confirmModal({
      title: '撤銷上一輪？',
      desc: `「${last.prizeName}」這一輪共 ${roundWinners.length} 位（${roundWinners.slice(0, 3).map(w => esc(w.name)).join('、')}${roundWinners.length > 3 ? '…' : ''}）將被移除並回到候選池。`,
      okText: '撤銷',
      danger: true
    });
    if (!ok) return;
    const res = Store.undoLast();
    if (res.ok) {
      sendState();
      Bus.send({ type: 'idle' }, stageWin);
      toast('已撤銷上一輪');
    }
  }

  async function resetPrize() {
    if (busy) return;
    const prize = Store.prizeOf(currentPrizeId);
    if (!prize) return;
    const n = Store.prizeProgress(prize.id);
    if (!n) { toast('本獎項尚無中獎紀錄', 'warn'); return; }
    const ok = await confirmModal({
      title: `重設「${prize.name}」？`,
      desc: `將移除本獎項的 ${n} 筆中獎紀錄，這些人會回到候選池。`,
      okText: '重設',
      danger: true
    });
    if (!ok) return;
    Store.resetPrize(prize.id);
    sendState();
    Bus.send({ type: 'idle' }, stageWin);
    toast('已重設本獎項');
  }

  /* ---------------- 名單 ---------------- */
  async function applyRoster(list) {
    if (!list.length) { toast('沒有解析到任何姓名', 'bad'); return; }
    if (!S().roster.length) {
      const n = Store.setRoster(list);
      toast(`已匯入 ${n} 人`);
    } else {
      const mode = await chooseModal({
        title: `解析到 ${list.length} 筆名單`,
        desc: `目前已有 ${S().roster.length} 人。要附加在名單後面，或整批取代？`,
        choices: [
          { label: '附加', value: 'append' },
          { label: '取代', value: 'replace', cls: 'primary' }
        ]
      });
      if (!mode) return;
      const n = mode === 'replace' ? Store.setRoster(list) : Store.appendRoster(list);
      toast(mode === 'replace' ? `名單已取代，共 ${n} 人` : `已附加，共 ${n} 人`);
    }
    sendState();
    renderAll();
  }

  async function importRosterText(text) {
    await applyRoster(Store.parseRoster(text));
  }

  async function pasteRoster() {
    const vals = await promptModal({
      title: '貼上員工名單',
      desc: '從 Excel 直接複製三欄（姓名、部門、員工編號）貼上即可，Tab 或逗號分隔都支援。',
      okText: '下一步',
      fields: [{
        key: 'text', label: '名單內容', type: 'textarea', rows: 12,
        placeholder: '王小明\t業務部\tA001\n陳大文\t研發部\tA002'
      }]
    });
    if (!vals || !vals.text.trim()) return;
    await applyRoster(Store.parseRoster(vals.text));
  }

  async function loadSample() {
    if (S().roster.length) {
      const ok = await confirmModal({
        title: '載入範例名單？',
        desc: `目前已有 ${S().roster.length} 人名單，將被<b>取代</b>。`,
        okText: '取代為範例',
        danger: true
      });
      if (!ok) return;
    }
    const depts = ['業務部', '研發部', '行銷部', '人資部', '財務部', '客服部', '製造部', '資訊部'];
    const sur = '陳林黃張李王吳劉蔡楊許鄭謝郭洪邱曾廖賴徐周葉蘇潘何蕭羅高'.split('');
    const given = ['志明', '美玲', '建宏', '雅婷', '俊傑', '淑芬', '家豪', '怡君', '冠宇', '佩珊',
      '文彬', '欣怡', '柏翰', '思妤', '承恩', '靜宜', '宗翰', '子晴', '威廷', '郁婷'];
    const list = [];
    for (let i = 0; i < 180; i++) {
      list.push({
        name: sur[i % sur.length] + given[(i * 7) % given.length],
        dept: depts[i % depts.length],
        empNo: 'E' + String(1001 + i)
      });
    }
    Store.setRoster(list);
    toast('已載入 180 人範例名單');
    sendState();
    renderAll();
  }

  /* ---------------- 分頁 ---------------- */
  let activeTab = 'record';
  function switchTab(name) {
    activeTab = name;
    $$('#tabs button').forEach(b => b.classList.toggle('active', b.dataset.tab === name));
    ['record', 'roster', 'prizes', 'settings'].forEach(t => {
      $('#tab-' + t).hidden = t !== name;
    });
    const side = document.querySelector('.side');
    if (side) side.classList.toggle('side-auto', name === 'settings');
  }

  /* ---------------- 渲染 ---------------- */
  function isEditing(container) {
    const a = document.activeElement;
    if (!a || !container.contains(a)) return false;
    if (a.tagName === 'TEXTAREA' || a.tagName === 'SELECT') return true;
    if (a.tagName === 'INPUT') {
      return ['checkbox', 'radio', 'button', 'range', 'file', 'color'].indexOf(a.type) < 0;
    }
    return false;
  }

  let rosterSig = '';
  let rosterSort = { key: null, dir: 1 };

  function sortRoster(list) {
    if (!rosterSort.key) return list;
    const key = rosterSort.key;
    const dir = rosterSort.dir;
    const val = p => String(p[key] || '').trim();
    return list.slice().sort((a, b) => {
      const va = val(a);
      const vb = val(b);
      if (!va && vb) return 1;          // 空值固定排最後
      if (va && !vb) return -1;
      let r;
      if (key === 'empNo') {
        r = va.localeCompare(vb, undefined, { numeric: true, sensitivity: 'base' });
      } else {
        r = va.localeCompare(vb, 'zh-Hant');
      }
      if (r === 0) r = (a.name || '').localeCompare(b.name || '', 'zh-Hant');
      return r * dir;
    });
  }

  function updateSortIndicators() {
    $$('#rosterTable th.sortable').forEach(th => {
      const ind = th.querySelector('.sort-ind');
      const on = th.dataset.sort === rosterSort.key;
      if (ind) ind.textContent = on ? (rosterSort.dir > 0 ? ' ▲' : ' ▼') : '';
      th.setAttribute('aria-sort', on ? (rosterSort.dir > 0 ? 'ascending' : 'descending') : 'none');
    });
  }

  function renderAll() {
    if (!Store.prizeOf(currentPrizeId)) pickDefaultPrize();
    renderHeader();
    renderChips();
    renderPanel();
    renderWinners();
    renderRoster();
    renderPrizeEditor();
    renderSettings();
    renderTip();
    updateMusicBtn();
  }

  function renderHeader() {
    const inp = $('#eventName');
    if (document.activeElement !== inp) inp.value = S().eventName;
    document.title = S().eventName + '｜抽獎控制台';
  }

  function tierColor(t) { return Store.TIER_COLORS[t] || '#7c5cff'; }

  function renderChips() {
    const box = $('#prizeChips');
    box.innerHTML = S().prizes.map(p => {
      const done = Store.prizeProgress(p.id);
      const active = p.id === currentPrizeId;
      return `<div class="chip${active ? ' active' : ''}${done >= p.count ? ' done' : ''}"
        data-prize="${p.id}" style="--tier:${tierColor(p.tier)}">
        <span class="dot"></span>${esc(p.name)}<small>${done}/${p.count}</small></div>`;
    }).join('') || '<span class="hint">尚未建立獎項</span>';

    $$('#prizeChips .chip').forEach(chip => {
      chip.onclick = () => {
        if (busy) return;
        const changed = chip.dataset.prize !== currentPrizeId;
        currentPrizeId = chip.dataset.prize;
        if (changed) fillPrizeCount();
        renderChips();
        renderPanel();
        sendState();
      };
    });
  }

  // 切換獎項時，把「抽出人數」帶入該獎項的剩餘可抽人數
  function fillPrizeCount() {
    const p = Store.prizeOf(currentPrizeId);
    if (!p) return;
    const remain = p.count - Store.prizeProgress(p.id);
    const pool = Store.stats().pool;
    const n = Math.max(1, Math.min(remain > 0 ? remain : 1, pool > 0 ? pool : 1, 300));
    $('#drawCount').value = n;
    updateDrawBtnLabel();
    if (remain > pool && pool > 0) {
      toast(`「${p.name}」剩 ${remain} 名，候選人只有 ${pool} 位，已帶入 ${n}`, 'warn');
    }
  }

  function renderPanel() {
    const p = Store.prizeOf(currentPrizeId);
    const st = Store.stats();
    $('#curPrizeName').textContent = p ? p.name : '—';
    $('#curPrizeProgress').textContent = p
      ? `${Store.prizeProgress(p.id)} / ${p.count}`
      : '0 / 0';
    $('#stPool').textContent = st.pool;
    $('#stWon').textContent = st.won;
    $('#stTotal').textContent = st.total;
    const input = $('#drawCount');
    const max = Math.max(1, st.pool);
    input.max = max;
    if (Number(input.value) > max) input.value = max;
    if (!busy) input.closest('.stepper').classList.toggle('disabled', !st.pool);
    updateDrawBtnLabel();
  }

  function renderTip() {
    const tip = $('#drawTip');
    const st = Store.stats();
    let html = '', warn = false;
    if (!st.total) {
      html = '尚未匯入名單 → 到右側「員工名單」貼上或匯入 CSV，或先載入<b>範例名單</b>試玩。';
      warn = true;
    } else if (!stageReady) {
      html = '投影畫面未連線 → 點右上「<b>開啟投影畫面</b>」，拖到投影螢幕後在該視窗按 <b>F</b> 全螢幕。';
      warn = true;
    } else if (!st.pool) {
      html = '所有候選人都已中獎。可撤銷紀錄、增加名單，或開啟「允許重複中獎」。';
      warn = true;
    } else {
      html = `準備就緒：按 <b>Enter</b> 開始抽獎，目前可抽 <b>${st.pool}</b> 人。`;
    }
    tip.innerHTML = html;
    tip.classList.toggle('warn', warn);
  }

  function renderWinners() {
    const list = $('#winnerList');
    const winners = S().winners;
    $('#recordSummary').textContent = winners.length
      ? `共 ${winners.length} 人中獎`
      : '尚無紀錄';

    if (!winners.length) {
      list.innerHTML = '<div class="empty"><b>◈</b>還沒有中獎紀錄<br>抽出的名單會即時出現在這裡</div>';
      return;
    }

    const groups = [];
    winners.forEach(w => {
      let g = groups.find(x => x.roundId === w.roundId);
      if (!g) { g = { roundId: w.roundId, prizeName: w.prizeName, ts: w.ts, items: [] }; groups.push(g); }
      g.items.push(w);
    });

    list.innerHTML = groups.slice().reverse().map(g => `
      <div class="round">
        <div class="round-head">
          <span class="badge">${esc(g.prizeName)}</span>
          <b>${g.items.length} 位</b>
          <small>${timeStr(g.ts)}</small>
          <button class="undo" data-round="${g.roundId}">撤銷</button>
        </div>
        ${g.items.map((w, i) => `
          <div class="winner-row">
            <span class="idx">${String(i + 1).padStart(2, '0')}</span>
            <span class="nm">${esc(w.name)}</span>
            <span class="dp">${esc(w.dept || '—')}</span>
            <span class="en">${w.empNo ? esc(w.empNo) : ''}</span>
          </div>`).join('')}
      </div>`).join('');

    $$('#winnerList .undo').forEach(btn => {
      btn.onclick = async () => {
        if (busy) { toast('抽獎進行中，請稍候', 'warn'); return; }
        const ok = await confirmModal({
          title: '撤銷這一輪？',
          desc: '這批中獎者將回到候選池，紀錄會從清單移除。',
          okText: '撤銷',
          danger: true
        });
        if (!ok) return;
        Store.undoRound(btn.dataset.round);
        sendState();
        toast('已撤銷該輪');
      };
    });
  }

  function renderRoster() {
    const tbody = $('#rosterTable tbody');
    if (isEditing(tbody)) return;
    const roster = S().roster;
    const sig = roster.length + '|' + S().winners.length + '|' + S().excluded.join(',') +
      '|' + (rosterSort.key || '') + rosterSort.dir;
    if (sig === rosterSig) return;
    rosterSig = sig;
    updateSortIndicators();
    if (!roster.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="hint" style="padding:26px;text-align:center">尚無名單。匯入 CSV 或貼上 Excel 內容。</td></tr>';
      return;
    }
    const wonMap = new Map();
    S().winners.forEach(w => { if (!wonMap.has(w.key)) wonMap.set(w.key, w.prizeName); });
    const excluded = new Set(S().excluded);

    const rows = sortRoster(roster).map((p, i) => {
      const won = wonMap.get(p.key);
      return `<tr class="${excluded.has(p.key) ? 'excluded' : ''}">
        <td class="row-no">${i + 1}</td>
        <td><b>${esc(p.name)}</b>${won ? `<span class="won-tag">${esc(won)}</span>` : ''}</td>
        <td class="dim">${esc(p.dept || '—')}</td>
        <td class="dim">${esc(p.empNo || '—')}</td>
        <td><input type="checkbox" data-key="${esc(p.key)}" data-ex="${excluded.has(p.key) ? '1' : '0'}"${excluded.has(p.key) ? ' checked' : ''}></td>
      </tr>`;
    }).join('');
    tbody.innerHTML = rows;

    tbody.querySelectorAll('input[data-key]').forEach(cb => {
      cb.onchange = () => {
        Store.toggleExclude(cb.dataset.key);
        sendState();
        renderPanel();
        renderTip();
      };
    });
  }

  const TIER_OPTIONS = [
    { v: 1, t: '金（頭獎規格）' },
    { v: 2, t: '紅' },
    { v: 3, t: '紫' },
    { v: 4, t: '青' }
  ];

  function renderPrizeEditor() {
    const box = $('#prizeEditor');
    if (isEditing(box)) return;
    box.innerHTML = S().prizes.map((p, i) => `
      <div class="prize-item" data-id="${p.id}" style="--tier:${tierColor(p.tier)}">
        <span class="tier-dot"></span>
        <input class="name" value="${esc(p.name)}" maxlength="20" data-field="name">
        <input class="count" type="number" min="0" max="300" value="${p.count}" data-field="count">
        <button class="del" title="刪除">✕</button>
        <div class="meta">
          <select data-field="tier">${TIER_OPTIONS.map(o =>
            `<option value="${o.v}"${p.tier === o.v ? ' selected' : ''}>${o.t}</option>`).join('')}</select>
          <small>已抽 ${Store.prizeProgress(p.id)} 人</small>
          <span style="margin-left:auto;display:flex;gap:4px">
            <button class="btn ghost" data-move="-1" style="padding:2px 8px;font-size:11px">↑</button>
            <button class="btn ghost" data-move="1" style="padding:2px 8px;font-size:11px">↓</button>
          </span>
        </div>
      </div>`).join('') || '<p class="hint">尚未建立獎項。</p>';

    box.querySelectorAll('.prize-item').forEach(item => {
      const id = item.dataset.id;
      item.querySelectorAll('[data-field]').forEach(input => {
        input.addEventListener('change', () => {
          const f = input.dataset.field;
          const val = f === 'count' ? Number(input.value) : f === 'tier' ? Number(input.value) : input.value;
          Store.updatePrize(id, { [f]: val });
          sendState();
          renderChips();
          renderPanel();
          renderWinners();
        });
      });
      item.querySelector('.del').onclick = async () => {
        const p = Store.prizeOf(id);
        const n = Store.prizeProgress(id);
        const ok = await confirmModal({
          title: `刪除「${p.name}」？`,
          desc: n ? `此獎項已有 ${n} 筆中獎紀錄，刪除獎項後<b>紀錄仍會保留</b>在清單中。` : '此操作無法復原。',
          okText: '刪除',
          danger: true
        });
        if (!ok) return;
        Store.removePrize(id);
        if (currentPrizeId === id) pickDefaultPrize();
        renderAll();
        sendState();
        toast('已刪除獎項');
      };
      item.querySelectorAll('[data-move]').forEach(btn => {
        btn.onclick = () => {
          Store.movePrize(id, Number(btn.dataset.move));
          renderAll();
          sendState();
        };
      });
    });
  }

  function renderSettings() {
    const s = S().settings;
    const nameInput = $('#setEventName');
    if (nameInput && document.activeElement !== nameInput) nameInput.value = S().eventName;
    $('#setSpin').value = s.spinMs;
    $('#setSpinVal').textContent = (s.spinMs / 1000).toFixed(1) + 's';
    $('#setTease').checked = !!s.tease;
    $('#setSound').checked = !!s.sound;
    $('#setApplause').checked = s.applause !== false;
    $('#setMusic').checked = s.music !== false;
    const ds = $('#setDrawStyle');
    if (ds) ds.value = s.drawStyle || 'orchestra';
    const bt = $('#setBgmTrack');
    if (bt) bt.value = s.bgm || 'jingle';
    $('#setEmpNo').checked = !!s.showEmpNo;
    $('#setRepeat').checked = !!s.allowRepeat;
  }

  /* ---------------- 事件綁定 ---------------- */
  let nameTimer = null;
  function commitEventName(value) {
    clearTimeout(nameTimer);
    nameTimer = null;
    if (value !== S().eventName) Store.setEventName(value);
  }
  $('#eventName').addEventListener('input', e => {
    const v = e.target.value;
    document.title = v + '｜抽獎控制台';
    clearTimeout(nameTimer);
    nameTimer = setTimeout(() => commitEventName(v), 450);
  });
  $('#eventName').addEventListener('blur', e => commitEventName(e.target.value));
  $('#eventName').addEventListener('change', e => commitEventName(e.target.value));

  $('#btnOpenStage').onclick = openStage;

  $('#btnBlackout').onclick = () => {
    if (!stageReady) { toast('投影畫面未連線', 'warn'); return; }
    blackout = !blackout;
    Bus.send({ type: 'blackout', on: blackout }, stageWin);
    $('#btnBlackout').textContent = blackout ? '恢復畫面' : '黑屏';
  };

  $('#btnMusic').onclick = () => {
    if (!stageReady) { toast('投影畫面未連線', 'warn'); return; }
    if (musicPaused) {
      musicPaused = false;
      if (!S().settings.music) Store.updateSettings({ music: true });
      Bus.send({ type: 'music', on: true }, stageWin);
      toast('背景音樂已開啟');
    } else if (S().settings.music) {
      Store.updateSettings({ music: false });
      Bus.send({ type: 'music', on: false }, stageWin);
      toast('背景音樂已關閉');
    } else {
      Store.updateSettings({ music: true });
      Bus.send({ type: 'music', on: true }, stageWin);
      toast('背景音樂已開啟');
    }
    updateMusicBtn();
  };

  $('#btnDraw').onclick = () => startDraw();
  $('#btnExtra1').onclick = extraOne;
  $('#btnAdhoc').onclick = adhocPrize;
  $('#btnUndo').onclick = undoLast;
  $('#btnResetPrize').onclick = resetPrize;
  $('#btnIdle').onclick = () => {
    Bus.send({ type: 'idle' }, stageWin);
    toast('投影畫面回到待機');
  };

  $$('.stepper button').forEach(b => {
    b.onclick = () => {
      const input = $('#drawCount');
      const v = Math.max(1, Math.min(Number(input.max) || 300, (Number(input.value) || 1) + Number(b.dataset.step)));
      input.value = v;
      updateDrawBtnLabel();
    };
  });
  $('#drawCount').addEventListener('input', updateDrawBtnLabel);
  $('#drawCount').addEventListener('change', updateDrawBtnLabel);

  $$('#tabs button').forEach(b => { b.onclick = () => switchTab(b.dataset.tab); });

  $('#fileRoster').addEventListener('change', e => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    if (/\.(xlsx|xls)$/i.test(f.name)) {
      toast('請在 Excel 另存 CSV，或直接複製儲存格貼上', 'warn');
      e.target.value = '';
      return;
    }
    const reader = new FileReader();
    reader.onload = () => importRosterText(decodeFile(reader.result));
    reader.readAsArrayBuffer(f);
    e.target.value = '';
  });

  $$('#rosterTable th.sortable').forEach(th => {
    th.onclick = () => {
      const k = th.dataset.sort;
      if (rosterSort.key === k) rosterSort.dir = -rosterSort.dir;
      else { rosterSort.key = k; rosterSort.dir = 1; }
      rosterSig = '';
      renderRoster();
      const label = { name: '姓名', dept: '部門', empNo: '員工編號' }[k] || k;
      toast(`依「${label}」${rosterSort.dir > 0 ? '遞增' : '遞減'}排序`);
    };
  });

  $('#btnPasteRoster').onclick = pasteRoster;
  $('#btnSample').onclick = loadSample;
  $('#btnClearRoster').onclick = async () => {
    const ok = await confirmModal({ title: '清空名單？', desc: '名單與排除設定會清除，中獎紀錄保留。', okText: '清空', danger: true });
    if (!ok) return;
    Store.setRoster([]);
    toast('已清空名單');
    sendState();
    renderAll();
  };

  $('#btnAddPrize').onclick = async () => {
    const vals = await promptModal({
      title: '新增獎項',
      okText: '新增',
      fields: [
        { key: 'name', label: '獎項名稱', value: '四獎', placeholder: '例如：特別獎' },
        { key: 'count', label: '名額', type: 'number', value: 5, min: 1, max: 300 },
        { key: 'tier', label: '視覺等級', type: 'select', value: '3', options: TIER_OPTIONS.map(o => ({ value: String(o.v), label: o.t })) }
      ]
    });
    if (!vals) return;
    const p = Store.addPrize({ name: vals.name, count: vals.count, tier: Number(vals.tier) });
    currentPrizeId = p.id;
    renderAll();
    sendState();
    toast(`已新增「${p.name}」`);
  };

  $('#btnExportCsv').onclick = () => {
    if (!S().winners.length) { toast('尚無中獎紀錄', 'warn'); return; }
    download(`抽獎結果_${dateStamp()}.csv`, Store.exportCsv(), 'text/csv;charset=utf-8');
    toast('已匯出 CSV');
  };

  $('#setSpin').addEventListener('input', e => {
    const v = Number(e.target.value);
    $('#setSpinVal').textContent = (v / 1000).toFixed(1) + 's';
    Store.updateSettings({ spinMs: v });
  });
  $('#setTease').onchange = e => Store.updateSettings({ tease: e.target.checked });
  $('#setSound').onchange = e => {
    Store.updateSettings({ sound: e.target.checked });
    Bus.send({ type: 'setting', sound: e.target.checked }, stageWin);
  };
  $('#setMusic').onchange = e => {
    musicPaused = false;
    Store.updateSettings({ music: e.target.checked });
    Bus.send({ type: 'music', on: e.target.checked }, stageWin);
    updateMusicBtn();
  };
  $('#setApplause').onchange = e => {
    Store.updateSettings({ applause: e.target.checked });
    sendState();
  };
  $('#setDrawStyle').onchange = e => {
    Store.updateSettings({ drawStyle: e.target.value });
    sendState();
    toast('抽獎音樂風格已切換');
  };
  $('#setBgmTrack').onchange = e => {
    Store.updateSettings({ bgm: e.target.value });
    sendState();
    toast('背景音樂已切換');
  };
  $('#setEventName').addEventListener('input', e => {
    const v = e.target.value;
    clearTimeout(nameTimer);
    nameTimer = setTimeout(() => commitEventName(v), 400);
  });
  $('#setEventName').addEventListener('blur', e => commitEventName(e.target.value));
  $('#setEmpNo').onchange = e => Store.updateSettings({ showEmpNo: e.target.checked });
  $('#setRepeat').onchange = e => {
    Store.updateSettings({ allowRepeat: e.target.checked });
    renderPanel();
    renderTip();
    toast(e.target.checked ? '已允許重複中獎' : '已恢復每人限中一次');
    sendState();
  };

  $('#btnBackup').onclick = () => {
    download(`抽獎備份_${dateStamp()}.json`, JSON.stringify(S(), null, 2), 'application/json');
    toast('已匯出備份');
  };
  $('#fileBackup').addEventListener('change', e => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const raw = JSON.parse(reader.result);
        const ok = await confirmModal({
          title: '匯入備份？',
          desc: `名單 ${(raw.roster || []).length} 人、中獎 ${(raw.winners || []).length} 筆。目前資料會被<b>覆蓋</b>。`,
          okText: '覆蓋並匯入',
          danger: true
        });
        if (!ok) return;
        Store.replaceState(raw);
        pickDefaultPrize();
        renderAll();
        sendState();
        toast('備份已匯入');
      } catch (err) {
        toast('備份檔格式錯誤', 'bad');
      }
    };
    reader.readAsText(f);
    e.target.value = '';
  });

  $('#btnResetAll').onclick = async () => {
    const ok = await confirmModal({
      title: '全部重置？',
      desc: '名單、獎項、中獎紀錄將全部清除並恢復預設獎項。<b>此操作無法復原</b>，建議先匯出備份。',
      okText: '全部重置',
      danger: true
    });
    if (!ok) return;
    Store.resetAll();
    pickDefaultPrize();
    renderAll();
    sendState();
    toast('已全部重置');
  };

  $('#btnTest').onclick = () => {
    if (!stageReady) { toast('投影畫面未連線', 'warn'); openStage(); return; }
    Bus.send({ type: 'test' }, stageWin);
    toast('已送出測試訊號');
  };

  /* ---------------- 快捷鍵 ---------------- */
  document.addEventListener('keydown', e => {
    const tag = (e.target.tagName || '').toUpperCase();
    const typing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || tag === 'BUTTON';

    if (mask.classList.contains('show')) return;
    if ((e.key === 'Enter' || e.key === ' ') && !typing) {
      e.preventDefault();
      startDraw();
      return;
    }
    if (typing) return;

    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
      e.preventDefault();
      undoLast();
    } else if (e.key.toLowerCase() === 's') {
      openStage();
    } else if (e.key.toLowerCase() === 'b') {
      $('#btnBlackout').click();
    } else if (e.key.toLowerCase() === 'm') {
      $('#btnMusic').click();
    }
  });

  /* ---------------- 初始化 ---------------- */
  Store.subscribe(() => {
    renderAll();
    sendState();
  });

  pickDefaultPrize();
  renderAll();
  updateStagePill();
  startHeartbeat();

  if (!stageWin) setTimeout(() => {
    if (!stageReady) toast('提示：先按右上「開啟投影畫面」再開始抽獎', 'warn');
  }, 1200);

  window.__console = { Store, startDraw, sendState };
})();
