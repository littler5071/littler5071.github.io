# -*- coding: utf-8 -*-
"""在網站每一頁注入共用導覽列（可重複執行；以 <!-- hermesnav --> 標記判斷是否已注入）。

用法：python add_site_nav.py [網站根目錄]
分類頁與各集頁面都會出現固定的「首頁／AI 助理實測／股市觀察／多益英文」導覽，
並自動標示目前所在分類；連結用相對路徑，資料夾再深也不會壞。
"""
import os, re, sys, glob

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
MARK = "<!-- hermesnav -->"

NAV_CSS = """
  /* hermesnav（共用導覽） */
  .hnav{{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;align-items:center;gap:6px 4px;
        background:rgba(246,241,230,.97);border-bottom:2px solid #d9d1c2;padding:7px 14px;
        font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif;
        backdrop-filter:blur(4px)}}
  .hnav .brand{{font-size:15px;color:#4a4640;text-decoration:none;margin-right:10px;letter-spacing:.04em}}
  .hnav a.lnk{{font-size:14.5px;color:#364e70;text-decoration:none;padding:3px 11px;border-radius:999px;
        border:1.5px solid transparent}}
  .hnav a.lnk:hover{{border-color:#c8bda8;color:#bf4a3a}}
  .hnav a.lnk.on{{background:#fffdf6;border-color:#364e70;color:#364e70}}
"""
NAV_HTML = """{mark}
<nav class="hnav">
  <a class="brand" href="{base}/">小R 頻道</a>
  <a class="lnk{on_home}" href="{base}/">首頁</a>
  <a class="lnk{on_ai}" href="{base}/#ai">AI 助理實測</a>
  <a class="lnk{on_stock}" href="{base}/stock/">股市觀察</a>
  <a class="lnk{on_toeic}" href="{base}/toeic/">多益英文</a>
</nav>
"""


def inject(path):
    html = open(path, encoding="utf-8").read()
    if MARK in html:
        return "skip"
    rel = os.path.relpath(os.path.dirname(path), SITE).replace("\\", "/")
    depth = 0 if rel == "." else rel.count("/") + 1
    base = "." if depth == 0 else "/".join([".."] * depth)
    cat = "home"
    if rel.startswith("stock"):
        cat = "stock"
    elif rel.startswith("toeic"):
        cat = "toeic"
    nav = NAV_HTML.format(mark=MARK, base=base,
                          on_home=' on' if cat == "home" else "",
                          on_ai="", on_stock=' on' if cat == "stock" else "",
                          on_toeic=' on' if cat == "toeic" else "")
    if "</style>" in html:
        html = html.replace("</style>", NAV_CSS.format() + "</style>", 1)
    m = re.search(r"<body[^>]*>", html)
    if m:
        html = html[:m.end()] + "\n" + nav + html[m.end():]
    else:
        html = nav + html
    open(path, "w", encoding="utf-8").write(html)
    return f"ok({cat})"


pages = sorted(glob.glob(os.path.join(SITE, "**", "index.html"), recursive=True))
for p in pages:
    print(os.path.relpath(p, SITE).replace("\\", "/"), "→", inject(p))
print(f"共 {len(pages)} 頁")
