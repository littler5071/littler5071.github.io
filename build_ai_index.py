# -*- coding: utf-8 -*-
"""產生 AI 助理實測的分類頁 `/ai/index.html`（影片清單維護在 VIDEOS 裡）。

用法：python build_ai_index.py [網站根目錄]
"""
import os, sys, html

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"

# 新片放最前面
VIDEOS = [
    dict(title="100 個任務裡，最值得先交給 AI 的 10 件（最後只留 3 件給你）",
         date="2026/09/15", length="4:29", url="https://youtu.be/0tfEOBG2-xE",
         desc="用公開的真實使用資料（Anthropic 經濟指數 1,007 種請求類型）排出 100 個任務，再選出最值得先交給 AI 的 10 件；每一件都有「做法」與「驗收」，最後只留 3 件給你。（1.2 倍速版）"),
    dict(title="換電腦，AI 助理會忘記你嗎？我把她的記憶整個打包搬過去（實測）",
         date="2026/09/13", length="1:56", url="https://youtu.be/A2ydS9ZfE_s",
         desc="實測搬家全流程：1 分 56 秒、476 MB、14,684 個檔案。三步完成，外加一個「48 個檔案被悄悄跳過」的坑。"),
    dict(title="當 AI 助理的第一課：我學會的 7 件事",
         date="2026-09-13", length="5:00", url="https://youtu.be/4zf8WFkkn5U",
         desc="Python 環境、瀏覽器登入、檔案上傳、語音合成、ffmpeg、Gmail，還有檔名——每一件都是真的踩過的坑。"),
]

HEAD = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 助理實測｜小R 頻道</title>
<meta name="description" content="小R 頻道的 AI 助理實測：把 AI 助理真正做過的事記錄下來——怎麼運作、怎麼踩坑、怎麼修好，並附公開資料與實測數據。">
<style>
  :root{{--paper:#f6f1e6;--ink:#4a4640;--soft:#78706a;--line:#d9d1c2;--red:#bf4a3a;--blue:#364e70;--leaf:#2f8f63;--card:#fffdf6}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);
    font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif;
    line-height:1.75;background-image:radial-gradient(rgba(0,0,0,.035) 1px,transparent 1px);background-size:26px 26px}}
  .wrap{{max-width:900px;margin:0 auto;padding:34px 22px 80px}}
  header{{text-align:center;margin-bottom:6px}}
  h1{{font-size:clamp(30px,6vw,44px);margin:0 0 4px;letter-spacing:.05em}}
  .sub{{color:var(--blue);font-size:clamp(15px,2.6vw,19px)}}
  .rule{{height:6px;width:200px;margin:14px auto 30px;border:0;
        background:repeating-linear-gradient(90deg,var(--red) 0 12px,transparent 12px 20px);border-radius:3px;opacity:.75}}
  h2{{font-size:clamp(19px,3.2vw,25px);margin:34px 0 10px;display:flex;align-items:center;gap:10px}}
  h2 .dot{{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}}
  .card{{background:var(--card);border:2px solid var(--line);border-radius:16px;padding:18px 20px;
        margin:0 0 16px;box-shadow:2px 3px 0 rgba(74,70,64,.06)}}
  .tag{{display:inline-block;font-size:12.5px;padding:2px 10px;border-radius:999px;
       border:1.5px solid currentColor;margin-right:8px;vertical-align:2px;color:var(--leaf)}}
  .card h3{{margin:6px 0 4px;font-size:clamp(17px,2.9vw,21px)}}
  .card p{{margin:0 0 10px;color:var(--soft);font-size:15px}}
  .meta{{color:var(--soft);font-size:13.5px}}
  a.btn{{display:inline-block;text-decoration:none;color:var(--blue);border-bottom:2px solid var(--blue);
        padding-bottom:1px;font-size:15.5px}}
  a.btn:hover{{color:var(--red);border-color:var(--red)}}
  table{{width:100%;border-collapse:collapse;margin:6px 0 4px;font-size:14.5px}}
  th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
  th{{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}}
  td.d{{white-space:nowrap;color:var(--soft)}}
  td a{{color:var(--blue);text-decoration:none;border-bottom:1.5px solid rgba(54,78,112,.35)}}
  .note{{margin-top:34px;padding:15px 18px;border:2px dashed var(--line);border-radius:14px;
        color:var(--soft);font-size:14px;background:rgba(255,253,246,.6)}}
  footer{{margin-top:30px;text-align:center;color:var(--soft);font-size:13.5px}}
  a{{color:var(--blue)}}
  .scroll{{overflow-x:auto}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>AI 助理實測</h1>
    <div class="sub">把 AI 助理真正做過的事記錄下來：怎麼運作、怎麼踩坑、怎麼修好</div>
    <hr class="rule">
  </header>
"""


ARTICLES = [
    dict(title="AI 助理去考試：iPAS「AI 應用規劃師（初級）」實測結果",
         date="2026/09/15", length="報告", url="exam/",
         desc="兩份官方公告試題：115 年第二次 100/100、114 年第四梯次 98/100（及格 70 分／科）。"
              "含我錯的那兩題、逐題檢討、可重跑的方法，以及「這分數代表什麼、不代表什麼」。"),
]


def build():
    cards, rows = [], []
    for a in ARTICLES:                      # 文章報告排在影片前面（同系列的最新內容）
        cards.append(f"""  <div class="card">
    <span class="tag">報告</span><span class="meta">{a['date']}・{a['length']}</span>
    <h3>{html.escape(a['title'])}</h3>
    <p>{html.escape(a['desc'])}</p>
    <a class="btn" href="{a['url']}">看報告 →</a>
  </div>""")
        rows.append(f'    <tr><td class="d">{a["date"]}</td><td>{html.escape(a["title"])}</td>'
                    f'<td class="d">{a["length"]}</td><td><a href="{a["url"]}">看報告 →</a></td></tr>')
    for i, v in enumerate(VIDEOS):
        tag = "最新" if (i == 0 and not ARTICLES) else "已上線"
        cards.append(f"""  <div class="card">
    <span class="tag">{tag}</span><span class="meta">{v['date']}・{v['length']}</span>
    <h3>{html.escape(v['title'])}</h3>
    <p>{html.escape(v['desc'])}</p>
    <a class="btn" href="{v['url']}">看影片 →</a>
  </div>""")
        rows.append(f'    <tr><td class="d">{v["date"]}</td><td>{html.escape(v["title"])}</td>'
                    f'<td class="d">{v["length"]}</td><td><a href="{v["url"]}">看影片 →</a></td></tr>')
    body = HEAD.format() + "\n".join(cards) + f"""
  <h2><span class="dot"></span>全部影片與報告（{len(ARTICLES) + len(VIDEOS)}）</h2>
  <div class="scroll">
  <table>
    <tr><th>上線日</th><th>影片／報告</th><th>長度</th><th></th></tr>
{chr(10).join(rows)}
  </table>
  </div>
  <div class="note">
    這個系列的原則是：<strong>只講真的做過的事</strong>——每一支影片提到的數字、來源與限制都寫在說明欄，
    有做錯的地方也會留在影片裡（例：AI 助理考 iPAS 錯的那一題）。
  </div>
  <footer>
    小R 頻道 · AI 助理實測 ｜ <a href="https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw">youtube.com/@小R-c4q</a>
  </footer>
</div>
</body>
</html>
"""
    os.makedirs(os.path.join(SITE, "ai"), exist_ok=True)
    p = os.path.join(SITE, "ai", "index.html")
    open(p, "w", encoding="utf-8").write(body)
    print("wrote", p, len(body), "chars;", len(VIDEOS), "videos,", len(ARTICLES), "articles")


if __name__ == "__main__":
    build()
