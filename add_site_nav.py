# -*- coding: utf-8 -*-
"""在網站每一頁注入：共用導覽列 ＋ 瀏覽次數（可重複執行：會先移除舊版再注入）。

導覽列＝「小R 頻道」（＝首頁，使用者在首頁時會highlight）＋ AI 助理實測 / 股市觀察 / 多益英文。
瀏覽次數＝counter.js（abacus.jasoncameron.dev，免註冊、無 cookie），每頁一個 key。
用法：python add_site_nav.py [網站根目錄]
"""
import hashlib, json, os, re, sys, glob


def asset_ver(name):
    """用檔案內容雜湊當版本碼：counter.js 一改，所有頁面的 src 都會變 → 不會被瀏覽器快取卡住。"""
    p = os.path.join(SITE, name)
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else "1"

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
MARK = "<!-- hermesnav -->"

NAV_CSS = """  /* hermesnav（共用導覽・密集版：手機單行可橫向滑） */
  .hnav{position:sticky;top:0;z-index:20;display:flex;flex-wrap:nowrap;align-items:center;gap:2px;
        background:rgba(246,241,230,.97);border-bottom:2px solid #d9d1c2;padding:5px 10px;
        overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;
        font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif}
  .hnav::-webkit-scrollbar{display:none}
  .hnav a{white-space:nowrap}
  .hnav a.brand{font-size:14px;color:#4a4640;text-decoration:none;margin-right:6px;letter-spacing:.02em;
        padding:2px 8px;border-radius:999px;border:1.5px solid transparent;flex:none}
  .hnav a.brand:hover{border-color:#c8bda8;color:#bf4a3a}
  .hnav a.brand.on{background:#fffdf6;border-color:#364e70;color:#364e70}
  .hnav a.lnk{font-size:13.5px;color:#364e70;text-decoration:none;padding:2px 8px;border-radius:999px;
        border:1.5px solid transparent;flex:none}
  .hnav a.lnk:hover{border-color:#c8bda8;color:#bf4a3a}
  .hnav a.lnk.on{background:#fffdf6;border-color:#364e70;color:#364e70}
  @media (max-width:430px){
    .hnav{padding:4px 8px}
    .hnav a.brand{font-size:13px;padding:2px 6px}
    .hnav a.lnk{font-size:12.5px;padding:2px 6px}
  }
  /* hermesviews（瀏覽次數） */
  .viewsline{max-width:1000px;margin:8px auto 0;padding:0 18px;text-align:right;
        font-size:13px;color:#78706a}
  .viewsline .vnum{color:#364e70}
  .viewsline .vnum.vnum-on{color:#bf4a3a}
  .viewsline .vnum.vnum-off{color:#78706a}
"""
NAV_HTML = """{mark}
<nav class="hnav">
  <a class="brand{on_home}" href="{base}/">小R 頻道</a>
  <a class="lnk{on_ai}" href="{base}/ai/">AI 助理實測</a>
  <a class="lnk{on_stock}" href="{base}/stock/">股市觀察</a>
  <a class="lnk{on_toeic}" href="{base}/toeic/">多益英文</a>
</nav>
"""
SNAP = {}
_snapfile = os.path.join(SITE, "views_snapshot.json")
if os.path.exists(_snapfile):
    try:
        SNAP = json.load(open(_snapfile, encoding="utf-8")).get("pages", {})
    except Exception:
        SNAP = {}


def snap_key(rel):
    """與 counter.js／snapshot_views.py 相同的 key 規則（abacus key 長度需 >= 3）。"""
    path = "/" if rel == "." else "/" + rel + "/"
    k = re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") or "root"
    return "p" + k if len(k) < 3 else k


def views_html(rel):
    n = SNAP.get(rel)
    fb = f' data-views-fallback="{n}"' if n else ""
    return f'<div class="viewsline">瀏覽次數 <span class="vnum"{fb} data-views>—</span></div>'



def strip_old(html):
    """移除先前注入的導覽列／瀏覽次數與它們的 CSS（讓本腳本可以重複執行）。"""
    html = re.sub(r"\n?<!-- hermesnav -->\s*<nav class=\"hnav\">.*?</nav>\s*", "\n", html, flags=re.S)
    html = re.sub(r"\n?<div class=\"viewsline\">.*?</div>\s*", "\n", html, flags=re.S)
    html = re.sub(r"\n?<script defer src=\"[^\"]*counter\.js[^\"]*\"></script>\s*", "\n", html)
    html = re.sub(r"\n  /\* hermes(nav|views).*?(?=</style>)", "\n", html, flags=re.S)
    return html


def inject(path):
    html = strip_old(open(path, encoding="utf-8").read())
    rel = os.path.relpath(os.path.dirname(path), SITE).replace("\\", "/")
    depth = 0 if rel == "." else rel.count("/") + 1
    base = "." if depth == 0 else "/".join([".."] * depth)
    cat = ("stock" if rel.startswith("stock") else "toeic" if rel.startswith("toeic")
           else "ai" if rel == "ai" else "home")
    nav = NAV_HTML.format(mark=MARK, base=base,
                          on_home=' on' if cat == "home" else "",
                          on_ai=' on' if cat == "ai" else "",
                          on_stock=' on' if cat == "stock" else "",
                          on_toeic=' on' if cat == "toeic" else "")
    if "</style>" in html:
        html = html.replace("</style>", NAV_CSS + "</style>", 1)
    m = re.search(r"<body[^>]*>", html)
    html = (html[:m.end()] + "\n" + nav + html[m.end():]) if m else (nav + html)
    # 瀏覽次數：放在內容容器開頭（置右的小字），沒有容器就放 body 結尾
    if '<div class="wrap">' in html:
        html = html.replace('<div class="wrap">', '<div class="wrap">\n' + views_html(rel), 1)
    elif '<div class="wrap" ' in html:
        html = re.sub(r'(<div class="wrap"[^>]*>)', r"\1\n" + views_html(rel), html, count=1)
    elif "</body>" in html:
        html = html.replace("</body>", views_html(rel) + "\n</body>", 1)
    script = f'<script defer src="{base}/counter.js?v={asset_ver("counter.js")}"></script>'
    html = html.replace("</head>", script + "\n</head>", 1)
    open(path, "w", encoding="utf-8").write(html)
    return f"ok({cat})"


pages = sorted(glob.glob(os.path.join(SITE, "**", "index.html"), recursive=True))
for p in pages:
    if "counter.js" in p:
        continue
    print(os.path.relpath(p, SITE).replace("\\", "/"), "→", inject(p))
print(f"共 {len(pages)} 頁")
