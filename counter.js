/* 全站瀏覽次數（免註冊、無 cookie）
   服務：abacus.jasoncameron.dev（JSON + CORS）
   規則：同一分頁每次工作階段只 +1 次，之後只讀取，避免重新整理把數字灌大。
*/
(function () {
  var el = document.querySelector('[data-views]');
  if (!el || location.protocol === 'file:') return;

  var NS = 'littler5071-github-io';
  var path = location.pathname.replace(/index\.html$/, '');
  var key = path.replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'root';
  if (key.length < 3) key = 'p' + key;   // abacus 要求 key 長度 3~64，太短要補
  var flag = 'hv_' + key;
  var counted = false;
  try { counted = sessionStorage.getItem(flag) === '1'; } catch (e) {}

  var url = 'https://abacus.jasoncameron.dev/' + (counted ? 'get' : 'hit') + '/' + NS + '/' + key;
  fetch(url, { cache: 'no-store' })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d && typeof d.value === 'number') {
        el.textContent = d.value.toLocaleString('en-US');
        el.classList.add('vnum-on');
        if (!counted) { try { sessionStorage.setItem(flag, '1'); } catch (e) {} }
      } else {
        hide();
      }
    })
    .catch(hide);

  function hide() {
    /* 服務不通／被限流：整行收起來，不留下「—」，也不影響閱讀 */
    var box = el.closest ? el.closest('.viewsline') : null;
    if (box) box.style.display = 'none';
  }
})();
