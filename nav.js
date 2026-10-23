/* 共用導覽列（hermesnav）— 模組化版
   ────────────────────────────────────────────────────────────
   以前選單是「產生時寫死進 62 個頁面」，所以改任何一個字都要重生全部頁面，
   而且「現在在哪一區」要在產生時逐頁判斷 —— 那個判斷寫錯就變成亮錯位置
   （/ai/ 子頁曾亮成「小R頻道」）。

   現在選單只在這一個檔案裡：
     · 要改項目／順序／名稱 → 改下面的 ITEMS，全站立刻跟著變，不用碰任何頁面
     · 亮框改成「看目前網址自動判斷」，不再有逐頁寫死的判斷 → 整類 bug 消失
     · 樣式在 nav.css

   頁面上的兩個標籤（由 add_site_nav.py 維護）：
     <link rel="stylesheet" href="{base}/nav.css?v=...">
     <script defer src="{base}/nav.js?v=..."></script>

   沒有 JS 時的退路：每一頁內容裡本來就有「← 回 XX」的連結，所以還是能走。
*/
(function () {
  'use strict';

  /* ── 要改選單就改這裡 ─────────────────────────────────────────
     brand: true 的那一項＝首頁；path 是「相對於網站根目錄」的路徑。 */
  var ITEMS = [
    { label: '小R頻道',   path: '',        brand: true },
    { label: 'AI 助理實測', path: 'ai/'     },
    /* children＝下拉群組：手機點一下展開，桌面滑過就開。
       外站用 href（絕對網址），站內用 path（相對網站根目錄）。 */
    { label: '股市', children: [
        { label: '每日觀察報告',   path: 'stock/' },
        { label: 'Rich趨勢觀察家', href: 'https://gogohome.mooo.com/', external: true, note: '即時查詢' }
      ] },
    { label: '新聞晨報',   path: 'news/'   },
    { label: '多益英文',   path: 'toeic/'  },
    { label: '程式設計',   path: 'code/'   },
    { label: '教育輔助',   path: 'study/'  }
  ];

  var CLASS = 'hnav';          // 由 nav.css 決定長相

  /* ── 從自己的 script src 推出「到網站根目錄的相對前綴」 ────────
     同一份 nav.js 要能給 /ai/x/（../../）、/stock/20260930/（../../）
     和首頁（./）用，所以不能用寫死的路徑。 */
  function prefixOf() {
    var s = document.currentScript;
    if (!s) {
      var all = document.querySelectorAll('script[src]');
      for (var i = 0; i < all.length; i++) {
        if (/nav\.js(\?|$)/.test(all[i].getAttribute('src') || '')) { s = all[i]; break; }
      }
    }
    if (!s) return './';
    var src = s.getAttribute('src') || '';
    return src.replace(/nav\.js(\?.*)?$/, '') || './';
  }

  /* ── 目前這一頁「相對於網站根目錄」的路徑 ──────────────────────
     先把自己的前綴解析成絕對網址，再從目前路徑把它切掉。
     http 與 file:// 都能正確運作。 */
  function subPath(prefix, here) {
    var root;
    try { root = new URL(prefix, location.href).pathname; }
    catch (e) { root = '/'; }
    var p = here.replace(/index\.html$/, '');
    if (root && p.indexOf(root) === 0) p = p.slice(root.length);
    return p.replace(/^\/+/, '');
  }

  function build() {
    var prefix = prefixOf();
    var sub = subPath(prefix, location.pathname);
    var nav = document.createElement('nav');
    nav.className = CLASS;

    /* 下拉面板要放在 body 上（position:fixed），因為 nav 本身 overflow-x:auto
       會把 absolute 面板整個裁掉——這是實際踩過的坑。 */
    function makePanel(btn, kids) {
      var panel = document.createElement('div');
      panel.className = 'hdrop';
      kids.forEach(function (k) {
        var lk = document.createElement('a');
        lk.setAttribute('href', k.href || (prefix + k.path));
        if (k.external) { lk.setAttribute('target', '_blank'); lk.setAttribute('rel', 'noopener'); lk.className = 'ext'; }
        var t = document.createElement('span');
        t.textContent = k.label;
        lk.appendChild(t);
        if (k.note) {
          var nt = document.createElement('em');
          nt.textContent = k.note;
          lk.appendChild(nt);
        }
        panel.appendChild(lk);
      });
      document.body.appendChild(panel);

      function place() {
        var r = btn.getBoundingClientRect();
        panel.style.left = Math.max(8, Math.min(r.left, window.innerWidth - panel.offsetWidth - 8)) + 'px';
        panel.style.top = (r.bottom + 6) + 'px';
      }
      function open() {
        panel.classList.add('open');
        btn.classList.add('open');
        place();
      }
      function close() {
        panel.classList.remove('open');
        btn.classList.remove('open');
      }
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        panel.classList.contains('open') ? close() : open();
      });
      btn.addEventListener('mouseenter', function () { if (window.innerWidth > 760) open(); });
      btn.addEventListener('mouseleave', function () { if (window.innerWidth > 760) close(); });
      document.addEventListener('click', function (e) {
        if (!panel.contains(e.target) && e.target !== btn) close();
      });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
      window.addEventListener('resize', function () { if (panel.classList.contains('open')) place(); });
      window.addEventListener('scroll', close, { passive: true });
      return { panel: panel, close: close };
    }

    ITEMS.forEach(function (it) {
      if (it.children) {
        var g = document.createElement('a');
        g.className = 'lnk hgrp';
        g.setAttribute('href', '#');
        g.setAttribute('role', 'button');
        g.setAttribute('aria-haspopup', 'true');
        g.setAttribute('aria-expanded', 'false');
        g.textContent = it.label;
        var anyHit = it.children.some(function (k) {
          return k.path && sub.indexOf(k.path) === 0;
        });
        if (anyHit) g.className += ' on';
        nav.appendChild(g);
        var api = makePanel(g, it.children);
        g.addEventListener('click', function () {
          g.setAttribute('aria-expanded', api.panel.classList.contains('open') ? 'true' : 'false');
        });
        var cc = document.createElement('span');
        cc.className = 'caret';
        cc.textContent = '▾';
        g.appendChild(cc);
        return;
      }
      var a = document.createElement('a');
      a.className = it.brand ? 'brand' : 'lnk';
      a.setAttribute('href', it.href || (prefix + it.path));
      if (it.external) {
        a.className += ' ext';
        a.setAttribute('target', '_blank');
        a.setAttribute('rel', 'noopener');
      }
      a.textContent = it.label;
      // 亮框：首頁只有「完全在根目錄」才亮；其他分類用「開頭符合」。
      // （舊版就是在這裡把 ai 寫成「完全等於」，/ai/ 子頁才會亮錯。）
      var hit = it.external ? false : (it.brand ? (sub === '') : (it.path && sub.indexOf(it.path) === 0));
      if (hit) a.className += ' on';
      nav.appendChild(a);
    });

    var body = document.body;
    if (!body) return;
    var old = document.querySelector('nav.' + CLASS);
    if (old) old.remove();          // 保險：萬一頁面還留著舊的靜態選單
    body.insertBefore(nav, body.firstChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
