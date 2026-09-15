# -*- coding: utf-8 -*-
"""在網站每一頁注入共用導覽列（可重複執行：會先移除舊版再注入）。

導覽列＝「小R 頻道」（＝首頁，使用者在首頁時會highlight）＋ AI 助理實測 / 股市觀察 / 多益英文。
用法：python add_site_nav.py [網站根目錄]
"""
import os, re, sys, glob

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
"""
NAV_HTML = """{mark}
<nav class="hnav">
  <a class="brand{on_home}" href="{base}/">小R 頻道</a>
  <a class="lnk{on_ai}" href="{base}/ai/">AI 助理實測</a>
  <a class="lnk{on_stock}" href="{base}/stock/">股市觀察</a>
  <a class="lnk{on_toeic}" href="{base}/toeic/">多益英文</a>
</nav>
"""


def strip_old(html):
    """移除先前注入的導覽列與它的 CSS（讓本腳本可以重複執行、改了版型也能更新）。"""
    html = re.sub(r"\n?<!-- hermesnav -->\s*<nav class=\"hnav\">.*?</nav>\s*", "\n", html, flags=re.S)
    html = re.sub(r"\n  /\* hermesnav（共用導覽） \*/.*?(?=</style>)", "\n", html, flags=re.S)
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
    open(path, "w", encoding="utf-8").write(html)
    return f"ok({cat})"


pages = sorted(glob.glob(os.path.join(SITE, "**", "index.html"), recursive=True))
for p in pages:
    print(os.path.relpath(p, SITE).replace("\\", "/"), "→", inject(p))
print(f"共 {len(pages)} 頁")
