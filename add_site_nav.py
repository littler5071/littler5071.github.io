# -*- coding: utf-8 -*-
"""維護網站每頁的「共用區塊」標籤（可重複執行、且必須冪等）。

★ 2026-10-07 起導覽列改成模組化：
    選單的「項目」在 nav.js、「長相」在 nav.css（都在網站根目錄）。
    本腳本**不再把選單寫進頁面**，只確認每頁都有：
      <link rel="stylesheet" href="{base}/nav.css?v=…">
      <script defer src="{base}/nav.js?v=…"></script>
    好處：改選單只改 nav.js 一個檔，不必重生 63 頁；
    　　「現在在哪一區」改由網址自動判斷，不再有逐頁寫死判斷造成的亮錯位置
    　　（舊版 /ai/ 子頁就是因此亮成「小R 頻道」）。

仍由本腳本注入（這些是「每頁不同」的資料，不是共用邏輯）：
    · counter.js 的 script 標籤（版本碼＝檔案內容雜湊）
    · <div class="viewsline">瀏覽次數 …</div>（含上次統計的 fallback 數字）
    · 上面那塊 viewsline 的 CSS

★ 三個實測踩到的坑：
  1. StatiCrypt 加密頁一律跳過。它們的 <style> 裡本來就有一份舊 nav CSS，
     非貪婪正則會從那一份一路吃到 hermesviews，把中間頁面自己的 CSS 一起吃掉（-110 行）。
  2. **必須冪等**：清舊樣式的正則要把「尾端換行」也吃掉（TAIL + \n?），
     替換字串用空字串。否則每跑一次就多留一個空行，跑三次檔案就多三行。
  3. 量測移除行數當安全閥：正常一頁只移除「一份 nav CSS ＋ viewsline CSS」≈ 27 行，
     超過上限就整頁不動，避免正則吃錯時靜默毀掉頁面。

用法：python add_site_nav.py [網站根目錄]
"""
import glob
import hashlib
import json
import os
import re
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
SKIP = {"ai/hdd-ai/index.html", "private/demo/index.html"}
MAX_REMOVED_LINES = 60


def asset_ver(name):
    """用檔案內容雜湊當版本碼：檔案一改，所有頁面的 src 都會變 → 不會被瀏覽器快取卡住。"""
    p = os.path.join(SITE, name)
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else "1"


VIEWS_CSS = """  /* hermesviews（瀏覽次數） */
  .viewsline{max-width:1000px;margin:30px auto 0;padding:16px 18px 30px;text-align:center;
        border-top:2px dashed #d9d1c2;font-size:13px;color:#78706a}
  .viewsline .vnum{color:#364e70}
  .viewsline .vnum.vnum-on{color:#bf4a3a}
  .viewsline .vnum.vnum-off{color:#78706a}
"""
# 清掉先前注入的樣式（含舊版寫死的 nav CSS）。只刪到注入區塊自己的最後一行，
# 不能寫成「刪到 </style> 之前」——產生器會在注入樣式之後追加自己的 CSS，那樣會把頁面樣式全刪掉。
# 尾端的 \n? 一定要吃：否則每次執行都會多留一個空行（不冪等）。
_TAIL = re.escape(VIEWS_CSS.rstrip().splitlines()[-1].strip())
OLD_CSS_RE = re.compile(r"[ \t]*/\* hermes(?:nav|views)[^\n]*\n?.*?" + _TAIL + r"\n?", re.S)

SNAP = {}
_snapfile = os.path.join(SITE, "views_snapshot.json")
if os.path.exists(_snapfile):
    try:
        SNAP = json.load(open(_snapfile, encoding="utf-8")).get("pages", {})
    except Exception:
        SNAP = {}


def views_html(rel):
    n = SNAP.get(rel)
    fb = f' data-views-fallback="{n}"' if n else ""
    return f'<div class="viewsline">瀏覽次數 <span class="vnum"{fb} data-views>—</span></div>'


def strip_old(html):
    """移除先前注入的選單（含舊版靜態 nav）、viewsline、counter.js／nav.js／nav.css 與它們的樣式。"""
    html = re.sub(r"[ \t]*(?:<!-- hermesnav -->\s*)?<nav class=\"hnav\">.*?</nav>\n?", "", html, flags=re.S)
    html = re.sub(r"[ \t]*<div class=\"viewsline\">.*?</div>\n?", "", html, flags=re.S)
    html = re.sub(r"[ \t]*<script[^>]*(?:counter|nav)\.js[^>]*></script>\n?", "", html)
    html = re.sub(r"[ \t]*<link[^>]*nav\.css[^>]*>\n?", "", html)
    stripped = OLD_CSS_RE.sub("", html)
    n = (sum(1 for l in html.splitlines() if l.strip())
         - sum(1 for l in stripped.splitlines() if l.strip()))
    return (stripped if n <= MAX_REMOVED_LINES else html), n


def inject(path):
    rel_file = os.path.relpath(path, SITE).replace("\\", "/")
    if rel_file in SKIP:
        return "skip（StatiCrypt 加密頁，不動）"

    html = open(path, encoding="utf-8").read()
    html, n_css = strip_old(html)

    rel = os.path.relpath(os.path.dirname(path), SITE).replace("\\", "/")
    depth = 0 if rel == "." else rel.count("/") + 1
    base = "." if depth == 0 else "/".join([".."] * depth)

    head_tags = (
        f'<link rel="stylesheet" href="{base}/nav.css?v={asset_ver("nav.css")}">\n'
        f'<script defer src="{base}/nav.js?v={asset_ver("nav.js")}"></script>\n'
        f'<script defer src="{base}/counter.js?v={asset_ver("counter.js")}"></script>\n'
    )
    if "</head>" in html:
        html = html.replace("</head>", head_tags + "</head>", 1)
    else:
        html = head_tags + html

    if "</style>" in html:
        html = html.replace("</style>", VIEWS_CSS + "</style>", 1)

    if "</body>" in html:
        html = html.replace("</body>", views_html(rel) + chr(10) + "</body>", 1)
    else:
        html += chr(10) + views_html(rel)

    open(path, "w", encoding="utf-8", newline="\n").write(html)
    return "ok（移除舊樣式 %d 行）" % n_css


def main():
    pages = sorted(p for p in glob.glob(os.path.join(SITE, "**", "index.html"), recursive=True)
                   if ".git" not in p)
    for p in pages:
        print(os.path.relpath(p, SITE).replace("\\", "/"), "→", inject(p))
    print(f"共 {len(pages)} 頁")
    return 0


if __name__ == "__main__":
    sys.exit(main())
