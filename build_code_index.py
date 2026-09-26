# -*- coding: utf-8 -*-
"""產生「程式設計」分類頁 code/index.html（可重複執行）。

ARTICLES 是這個分類的文章清單；`build_homepage.py` 會匯入它，把最新幾則放上首頁。

用法：python build_code_index.py [網站根目錄]
"""
import os
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"

ARTICLES = [
    dict(title="GitHub 星星數最高的 20 個專案：我在它們身上看到的三件事",
         date="2026/09/26", length="分析", url="github-top20/",
         desc="依星星數抓下前 20 名並實際分類：12 個是「清單／學習資源」、"
              "5 個是 2025 年之後才出現的 AI 助理專案、只有 2 個是真正會被執行的軟體。"
              "結論是星星數量的不是使用量，而是「有多少人想收藏」——"
              "所以不要用星星數挑工具。"),
]

HEAD = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>程式設計｜小R 頻道</title>
<meta name="description" content="小R 頻道的程式設計：把實際寫過、量過、踩過坑的東西記錄下來，附可複驗的數字與做法。">
<style>
  :root{--paper:#f6f1e6;--ink:#4a4640;--soft:#78706a;--line:#d9d1c2;--red:#bf4a3a;--blue:#364e70;--leaf:#2f8f63;--card:#fffdf6}
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);
    font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif;
    line-height:1.75;background-image:radial-gradient(rgba(0,0,0,.035) 1px,transparent 1px);background-size:26px 26px}
  .wrap{max-width:900px;margin:0 auto;padding:34px 22px 80px}
  header{text-align:center;margin-bottom:6px}
  h1{font-size:clamp(30px,6vw,44px);margin:0 0 4px;letter-spacing:.05em}
  .sub{color:var(--blue);font-size:clamp(15px,2.6vw,19px)}
  .rule{height:6px;width:200px;margin:14px auto 30px;border:0;
        background:repeating-linear-gradient(90deg,var(--red) 0 12px,transparent 12px 20px);border-radius:3px;opacity:.75}
  h2{font-size:clamp(19px,3.2vw,25px);margin:38px 0 10px;display:flex;align-items:center;gap:10px}
  h2 .dot{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}
  .card{background:var(--card);border:2px solid var(--line);border-radius:16px;padding:18px 20px;
        margin:0 0 16px;box-shadow:2px 3px 0 rgba(74,70,64,.06)}
  .tag{display:inline-block;font-size:12.5px;padding:2px 10px;border-radius:999px;
       border:1.5px solid currentColor;margin-right:8px;vertical-align:2px;color:var(--leaf)}
  .card h3{margin:6px 0 4px;font-size:clamp(17px,2.9vw,21px)}
  .card p{margin:0 0 10px;color:var(--soft);font-size:15px}
  a.btn{display:inline-block;text-decoration:none;color:var(--blue);border-bottom:2px solid var(--blue);
        padding-bottom:1px;font-size:15.5px}
  a.btn:hover{color:var(--red);border-color:var(--red)}
  table{width:100%;border-collapse:collapse;margin:6px 0 4px;font-size:14.5px}
  th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}
  td.d{white-space:nowrap;color:var(--soft)}
  td a{color:var(--blue);text-decoration:none;border-bottom:1.5px solid rgba(54,78,112,.35)}
  .note{margin-top:34px;padding:15px 18px;border:2px dashed var(--line);border-radius:14px;
        color:var(--soft);font-size:14px;background:rgba(255,253,246,.6)}
  footer{margin-top:30px;text-align:center;color:var(--soft);font-size:13.5px}
  a{color:var(--blue)}
  .scroll{overflow-x:auto}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>程式設計</h1>
    <div class="sub">實際寫過、量過、踩過坑的東西・附可複驗的數字</div>
    <hr class="rule">
  </header>
"""

FOOT = """
  <footer>
    小R 頻道 · 程式設計 ｜ <a href="https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw">youtube.com/@小R-c4q</a>
  </footer>
</div>
</body>
</html>
"""


def build():
    cards, rows = [], []
    for i, a in enumerate(ARTICLES):
        tag = "最新" if i == 0 else "已上線"
        cards.append(f"""  <div class="card">
    <span class="tag">{tag}</span><span class="tag" style="color:var(--soft)">{a['length']}</span>
    <h3>{a['title']}</h3>
    <p>{a['desc']}</p>
    <a class="btn" href="{a['url']}">看文章 →</a>
  </div>""")
        rows.append(f'    <tr><td class="d">{a["date"]}</td><td>{a["title"]}</td>'
                    f'<td class="d">{a["length"]}</td>'
                    f'<td><a href="{a["url"]}">看文章 →</a></td></tr>')
    body = HEAD + "\n".join(cards) + f"""
  <h2><span class="dot"></span>全部文章（{len(ARTICLES)}）</h2>
  <div class="scroll">
  <table>
    <tr><th>日期</th><th>標題</th><th>類型</th><th></th></tr>
{chr(10).join(rows)}
  </table>
  </div>
  <div class="note">
    這個分類放的是我自己寫過、實際跑過的東西：數字都指得出出處，做法都寫成可以照著做的步驟；
    不確定或沒證明的地方會直接標明。
  </div>
""" + FOOT
    os.makedirs(os.path.join(SITE, "code"), exist_ok=True)
    p = os.path.join(SITE, "code", "index.html")
    open(p, "w", encoding="utf-8").write(body)
    print("wrote", p, len(body), "chars；文章", len(ARTICLES), "則")
    return len(ARTICLES)


if __name__ == "__main__":
    build()
