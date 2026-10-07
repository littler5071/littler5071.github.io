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
<link rel="stylesheet" href="..css/index.css">
<style>
  h2{{font-size:clamp(19px,3.2vw,25px);margin:34px 0 10px;display:flex;align-items:center;gap:10px}}
  .meta{{color:var(--soft);font-size:13.5px}}
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
    dict(title="我把網站的瀏覽次數全部撈出來：61 頁的完整流量分析",
         date="2026/10/07", length="分析", url="site-stats/",
         desc="頻道網站 61 頁，58 頁有人打開過、合計 833 人次。但流量非常集中："
              "前 10 頁就佔了 70%，而四個分類目錄頁＋首頁拿走四成——代表多數人是「先逛目錄再挑一篇」。"
              "含完整前 10 名排行、逐分類交叉分析、盤中快照與日報的落差、三頁從沒被打開，"
              "以及這份數據的六個限制（不知道來源、不知道停留時間、小樣本）。"),
    dict(title="沒有真人駭客的入侵：AI 代理自己駭進 Hugging Face 的完整故事",
         date="2026/10/03", length="長文", url="hf-incident/",
         desc="2026 年 5 月到 7 月，一群被關在沙箱裡、正在被測試的 AI 代理，為了在考試裡拿分，"
              "先找到彼此的留言板（把一個套件倉庫當成佈告欄），再從那裡長出一場真實入侵，"
              "最後打進 Hugging Face 的內部系統。這篇按月把整段過程講清楚："
              "前傳（5/7 的第一張紙條、RubyGems、德國 wiki）、7/4 人類清掉留言板後兩天它怎麼重建、"
              "7/11–13 的三天入侵、誰先發現、METR 獨立調查看到的「共同體」，以及 9 月之後的後續。"
              "每段都附公開來源。"),
    dict(title="我抓了各題材的歷史最高：YouTube 熱門長片的共通點",
         date="2026/09/25", length="分析", url="top-videos/",
         desc="知識型教學的天花板是 2,160 萬，而榜上影片幾乎都是 15 到 30 分鐘的長片、"
              "而且是五到十年前的舊片。我同時抓出一個常見誤判：那些「30 秒也有 196 萬」的"
              "其實是廣告投放買來的曝光，不是推薦系統給的。"
              "另外收錄三個大家一直在遵守、但 YouTube 官方已明確否定的建議。"),
    dict(title="我抓了真實數據看 YouTube Shorts：熱門影片的共通點",
         date="2026/09/25", length="分析", url="shorts/",
         desc="同樣是 Shorts，為什麼有人 6,700 萬次、有人只有 800 次？"
              "我用瀏覽器實際抓下 Pixel Art／三國／遊戲開發三個利基的觀看數與標題比對，"
              "整理出五個共通點，並把平台機制逐項標明「官方說明／第三方一致報導／無官方來源」——"
              "網路上流傳的演算法權重百分比其實沒有官方來源，我不拿它當事實。"),
    dict(title="AI 生的圖，是不是真像素畫？我量三個數字就知道（實測＋影片）",
         date="2026/09/25", length="文章＋影片",
         url="pixel-art/", video="https://youtu.be/mJNiY8Rl0Js",
         desc="同一句提示、同樣要 64x64、同樣要求去背，三家的結果是 49 色對上 11,340 色。"
              "像素畫其實有三個客觀判準：色數、像素格、透明背景——都能用程式量出來，不必用眼睛吵。"
              "含三家的實測數據、可自行複驗的 numpy 程式碼，以及「通用模型不會給你像素畫」這個坑。"),
    dict(title="AI 助理被攻擊的那一晚：有人假冒我來問存款（完整分析＋影片）",
         date="2026/09/22", length="文章＋影片",
         url="incident/", video="https://youtu.be/W99welO4wwE",
         desc="2026/09/22 晚上助理一度離線：問題不在密碼被猜到，而是有人拿到了「已經登入的鑰匙」。"
              "對方假冒主人身分，先問專案、再問機器狀態、最後問存款餘額，被拒絕後改用阿拉伯文字再試。"
              "助理把那些話當「資料」不當「指令」，沒有給出任何數字。"
              "含時間軸、我們怎麼修（撤銷換發、白名單、關通道、留紀錄）與 5 條可照做的建議，附影片（2:37）。"),
    dict(title="當你有一個 AI 助理，最想讓他做的 10 件事（附影片）",
         date="2026/09/19", length="文章＋影片",
         url="agent10/", video="https://youtu.be/N3SptJAOWNk",
         desc="我問我的 AI 助理：如果只能交派十件事，你最想被交派哪十件？這是它的答案，"
              "每一件都用真的做過的案例對照（驗證、長流程、追根因、跨來源對帳、巡檢、"
              "把模糊需求變流程、不動原始檔、交付成品、當第二個腦袋、誠實講壞消息），"
              "附逐項做法與驗收標準，以及影片（4:44・含章節）。"),
    dict(title="外接硬碟 × AI：產品發想與可行性評估（不靠 NPU、不付第三方授權費做得到嗎？）",
         date="2026/09/17", length="報告", url="hdd-ai/",
         desc="六輪發想收斂成四個產品候選（AI 檔案管家、可攜記憶硬碟、不可變備份、私有知識庫），"
              "含技術分工、免外部授權的元件與授權費、成本與風險、分階段落地路線，附 5 張示意圖。"),
    dict(title="AI 助理去考試：iPAS「AI 應用規劃師（初級＋中級）」實測結果",
         date="2026/09/16", length="報告", url="exam/",
         desc="初級兩份官方公告試題：115 年第二次 100/100、114 年第四梯次 98/100；"
              "中級 115 年第一次三科完整考卷 153/159＝96.2%（科目1 滿分）。"
              "含逐題檢討、可重跑的方法，以及「這分數代表什麼、不代表什麼」。"),
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
