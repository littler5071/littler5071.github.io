/* 小R 頻道｜多益題本頁共用互動：點選作答 → 對答案計分（P2／P3 共用）
   需要的 HTML 結構：
     <div class="q" data-q="32" data-a="0"> … <ul class="opts"><li data-i="0">…</li></ul>
       <div class="sol"><button class="toggle">看詳解</button><div class="solbody" hidden>…</div></div>
     </div>
     （可選）外層 <section class="set" data-set="1"> 作為分組
     <span id="done"></span> <button id="scoreBtn"></button> <button id="resetBtn"></button>
     <div id="result"></div> <span id="hint"></span>
   可用 <body data-quiz-key="xxx"> 指定 localStorage key。 */
(function () {
  var qs = Array.prototype.slice.call(document.querySelectorAll('.q[data-q][data-a]'));
  if (!qs.length) return;
  var KEY = document.body.getAttribute('data-quiz-key') || ('quiz_' + location.pathname);
  var total = qs.length;
  var sel = {};
  try { sel = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { sel = {}; }
  var scored = false;
  var lastMove = 0;      /* 最近一次捲動時間：滑動/自動捲動時的手指抬起不要當成選答案（防誤觸改答案） */
  ['touchmove', 'scroll'].forEach(function (ev) {
    window.addEventListener(ev, function () { lastMove = Date.now(); }, { passive: true });
  });
  var doneEl = document.getElementById('done');
  var resultEl = document.getElementById('result');
  var hintEl = document.getElementById('hint');

  function save() { try { localStorage.setItem(KEY, JSON.stringify(sel)); } catch (e) {} }
  function groupOf(q) { var s = q.closest ? q.closest('.set') : null; return s ? s.getAttribute('data-set') : null; }
  function doneCount() { return qs.filter(function (q) { return sel[q.getAttribute('data-q')] !== undefined; }).length; }

  function paint() {
    qs.forEach(function (q) {
      var picked = sel[q.getAttribute('data-q')];
      Array.prototype.forEach.call(q.querySelectorAll('.opts li'), function (li) {
        li.classList.toggle('sel', String(picked) === li.getAttribute('data-i'));
      });
    });
    if (doneEl) doneEl.textContent = doneCount();
  }

  function clearMarks() {
    qs.forEach(function (q) {
      q.classList.remove('right', 'wrong');
      var mark = q.querySelector('.mark'); if (mark) mark.textContent = '';
      Array.prototype.forEach.call(q.querySelectorAll('.opts li'), function (li) {
        li.classList.remove('ok', 'bad', 'locked');
      });
      var body = q.querySelector('.solbody');
      if (body) body.hidden = true;
      var info = q.querySelector('.pickinfo');
      if (info && info.parentNode) info.parentNode.removeChild(info);
      var t = q.querySelector('.toggle');
      if (t) t.textContent = '看詳解';
    });
    if (resultEl) resultEl.classList.remove('show');
  }

  document.addEventListener('click', function (ev) {
    var li = ev.target.closest && ev.target.closest('.opts li');
    if (li && !scored && !li.classList.contains('locked')) {
      if (Date.now() - lastMove < 180) return;   /* 剛捲動完的手指抬起不選答案 */
      var q = li.closest('.q');
      sel[q.getAttribute('data-q')] = Number(li.getAttribute('data-i'));
      save(); paint();
      return;
    }
    var t = ev.target.closest && ev.target.closest('.toggle');
    if (t) {
      var q2 = t.closest('.q');
      var body2 = q2.querySelector('.solbody');
      body2.hidden = !body2.hidden;
      t.textContent = body2.hidden ? '看詳解' : '收起詳解';
    }
  });

  var scoreBtn = document.getElementById('scoreBtn');
  if (scoreBtn) scoreBtn.addEventListener('click', function () {
    var right = 0, blank = 0, groups = {}, hasGroups = false;
    qs.forEach(function (q) {
      var a = Number(q.getAttribute('data-a'));
      var picked = sel[q.getAttribute('data-q')];
      var g = groupOf(q);
      if (g !== null) hasGroups = true;
      var key = (g === null ? '_all' : g);
      groups[key] = groups[key] || { ok: 0, wrong: 0, blank: 0, n: 0 };
      groups[key].n += 1;
      var lis = q.querySelectorAll('.opts li');
      Array.prototype.forEach.call(lis, function (li) { li.classList.add('locked'); });
      var mark = q.querySelector('.mark');
      if (picked === undefined) {
        blank++; groups[key].blank++;
        if (mark) mark.textContent = '—';
        if (lis[a]) lis[a].classList.add('ok');
        return;
      }
      if (picked === a) {
        right++; groups[key].ok++;
        q.classList.add('right');
        if (mark) mark.textContent = '✅';
        if (lis[a]) lis[a].classList.add('ok');
      } else {
        groups[key].wrong++;
        q.classList.add('wrong');
        if (mark) mark.textContent = '❌';
        if (lis[a]) lis[a].classList.add('ok');
        if (lis[picked]) lis[picked].classList.add('bad');
        /* 明確寫出「你選誰／正解誰」，避免爭議時無法核對 */
        var txtOf = function (li) {
          return li ? li.textContent.replace(/^\s*[A-D]\s*/, '').trim() : '(不明)';
        };
        var info = q.querySelector('.pickinfo');
        if (!info) {
          info = document.createElement('div');
          info.className = 'pickinfo';
          var optsUl = q.querySelector('.opts');
          if (optsUl && optsUl.parentNode) optsUl.parentNode.insertBefore(info, optsUl.nextSibling);
          else q.appendChild(info);
        }
        info.setAttribute('style', 'margin:6px 0 0;font-size:14px;color:#8a3b2e;' +
          'background:#fdf0ec;border-left:4px solid #bf4a3a;border-radius:0 8px 8px 0;padding:6px 10px');
        info.innerHTML = '你選 <b>' + 'ABCD'[picked] + '</b>（' + txtOf(lis[picked]) + '）' +
          '　→　正解 <b>' + 'ABCD'[a] + '</b>（' + txtOf(lis[a]) + '）';
        var body = q.querySelector('.solbody');
        if (body) { body.hidden = false;
          var t = q.querySelector('.toggle'); if (t) t.textContent = '收起詳解'; }
      }
    });
    scored = true;
    var keys = Object.keys(groups).sort(function (a, b) {
      if (a === '_all') return -1; if (b === '_all') return 1; return a - b;
    });
    var rows = hasGroups ? keys.map(function (k) {
      var v = groups[k], parts = [];
      if (v.wrong) parts.push('錯 ' + v.wrong + ' 題');
      if (v.blank) parts.push('未作答 ' + v.blank + ' 題');
      if (!parts.length) parts.push('全對');
      return '<li>第 ' + k + ' 組：' + v.ok + ' / ' + v.n + '（' + parts.join('・') + '）</li>';
    }).join('') : '';
    var weak = keys.filter(function (k) { return groups[k].wrong > 0; });
    if (resultEl) {
      resultEl.innerHTML =
        '<div class="big">' + right + ' / ' + total + '</div>' +
        '<div>答對 ' + right + ' 題' + (blank ? '，未作答 ' + blank + ' 題' : '') +
        '，答對率 ' + Math.round(right / total * 100) + '%。' +
        (!hasGroups && !weak.length ? '' : (weak.length ? '' : '　全部答對，漂亮！')) + '</div>' +
        (rows ? '<ul>' + rows + '</ul>' : '') +
        (weak.length && hasGroups ? '<p class="dim" style="margin-top:8px">優先複習：' +
          weak.map(function (k) { return '第 ' + k + ' 組'; }).join('、') + '</p>' : '');
      resultEl.classList.add('show');
      window.scrollTo({ top: resultEl.offsetTop - 80, behavior: 'smooth' });
    }
    if (hintEl) hintEl.textContent = '（要重做請按「清除作答」）';
  });

  var resetBtn = document.getElementById('resetBtn');
  if (resetBtn) resetBtn.addEventListener('click', function () {
    sel = {}; scored = false;
    save(); clearMarks(); paint();
    if (hintEl) hintEl.textContent = '（作答已清除）';
  });

  clearMarks();
  paint();
})();
