# -*- coding: utf-8 -*-
"""產生 AI 助理實測的分類頁 `/ai/index.html`（影片清單維護在 VIDEOS 裡）。

★ nav.css／nav.js／counter.js 與 viewsline 那塊一律寫在本檔的 HEAD／尾段裡：
  先前它們靠 add_site_nav.py 事後注入，只要單跑這支產生器（或排程重生成）就會靜默掉光，
  線上實測 / 與 /ai/ 兩頁就是這樣整條選單與瀏覽次數都不見的。寫進產生器後重生也不會掉。

用法：python build_ai_index.py [網站根目錄]
"""
import os, sys, html

SITE = sys.argv[1] if len(sys.argv) > 1 else "/home/littler5071/opencode/圖片生成/小R頻道_網站"

# 新片放最前面
VIDEOS = [
    dict(title="我故意寫了 20 個弱點，讓 11 個免費資安工具來抓（長片版）",
         date="2026/10/29", length="3:13", url="https://youtu.be/M3CFFc2aHUU",
         desc="20 個弱點逐項講完：三語言、11 個工具、掃描範圍實驗、平台建置（含 ARM64），結果 Python 100%、C# 71%、Rust 17%。"),
    dict(title="我故意寫了三個有漏洞的程式，讓 11 個免費資安工具去抓：Rust 只抓到 17%",
         date="2026/10/29", length="1:06", url="https://youtube.com/shorts/ZWVaJ04ERUI",
         desc="Rust／C#／Python 各植入同一組 6 種弱點＋1 個漏洞相依，共 20 個；11 個免費工具聯集只命中 13 個（65%）。完整清單與行號見 ai/vulnlab-coverage-2026-10/。"),
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
<title>AI 助理實測｜小R頻道</title>
<meta name="description" content="小R頻道的 AI 助理實測：把 AI 助理真正做過的事記錄下來——怎麼運作、怎麼踩坑、怎麼修好，並附公開資料與實測數據。">
<link rel="stylesheet" href="../css/index.css">
<style>
  h2{{font-size:clamp(19px,3.2vw,25px);margin:34px 0 10px;display:flex;align-items:center;gap:10px}}
  .meta{{color:var(--soft);font-size:13.5px}}
/* hermesviews（瀏覽次數） */
  .viewsline{{max-width:1000px;margin:30px auto 0;padding:16px 18px 30px;text-align:center;
        border-top:2px dashed #d9d1c2;font-size:13px;color:#78706a}}
  .viewsline .vnum{{color:#364e70}}
  .viewsline .vnum.vnum-on{{color:#bf4a3a}}
  .viewsline .vnum.vnum-off{{color:#78706a}}
</style>
<link rel="stylesheet" href="../nav.css?v=73b4d013">
<script defer src="../nav.js?v=4b28034a"></script>
<script defer src="../counter.js?v=94ad9679"></script>
</head>
<body>
<div class="wrap">
  <header>
    <h1>AI 助理實測</h1>
    <div class="sub">把 AI 助理真正做過的事記錄下來：怎麼運作、怎麼踩坑、怎麼修好</div>
    <hr class="rule">
      <p class="lead">
      這裡是我真的把 AI 助理拿來做事之後留下的紀錄：實測影片、踩到的坑、後來怎麼修，
      以及幾篇用公開資料寫成的長文。<br>
      <b>第一次來</b>——想看它出錯的真實案例，從〈沒有真人駭客的入侵〉開始；
      想看它怎麼幫我做事，看〈網站的瀏覽次數完整分析〉；想直接動手，影片類都附實際操作畫面。
    </p>
</header>
"""


ARTICLES = [
    dict(title="K3s 完全研究報告：從「它是什麼」到「你該不該用」",
         date="2026/10/29", length="408 行完整報告",
         url="k3s-2026-10/",
         desc="K3s 是什麼、跟 Kubernetes 差在哪、官方資源實測（server 1.6 GB／agent 275 MB）、三種架構、"
              "硬體與網路埠、七個方案對照、風險清單與落地路線。全部引用官方文件，版本 v1.37.1+k3s1。"),
    dict(title="我故意寫了三個有漏洞的程式，讓 11 個免費工具去抓：誰抓到、誰漏掉、涵蓋率多少",
         date="2026/10/28", length="Shorts 1:05＋完整對照表",
         video="https://youtube.com/shorts/ZWVaJ04ERUI",
         url="vulnlab-coverage-2026-10/",
         desc="CWE 對照實驗：Rust／C#／Python 各植入 SQL 注入、指令注入、路徑穿越、硬編碼憑證、MD5、"
              "TLS 驗證關閉，加一個已知漏洞相依，共 20 個弱點。用 syft、grype、trivy、OSV、sbomqs、Semgrep、"
              "Bandit、gitleaks、.NET 分析器、Clippy 全跑一輪，並編出 Windows／Linux／ARM64（含 Apple M 系列 Mach-O）。"
              "結果：Python 100%、C# 71%、Rust 17%；唯一全中的類型是相依漏洞，沒有單一工具能應付 CRA。"),
    dict(title="AI 變強了，但有 7 個職業反而退步：44 個職業的實測數字與實際案例",
         date="2026/10/28", length="長片 4:15＋Shorts 1:11",
         yt="https://youtube.com/shorts/oho-UmKbvL8",
         url="models-uneven-2026-10/",
         desc="a16z 引用 OpenAI GDPval，比較 2025 年 9 月與 2026 年 4 月的 44 個職業："
              "模型對專家的勝率平均從 49.5% 升到 59.4%（+9.9 個百分點），36 個進步、1 個持平、7 個退步。"
              "退最多的是醫療與健康服務經理（65%→38%），律師 56%→46%；分數最高的是編輯 93%。"
              "我另外算出兩個圖上沒有的規律：起點低的職業平均 +15.3、起點高的只 +4.5；產業以政府 +17.6 最高、醫療 +2.6 最低。"
              "附 44 列完整表格、實際案例與出處。"),
    dict(title="AI 公司真的都在改用 Rust 嗎？我查了 GitHub 原始數據，答案是「一半對」",
         date="2026/10/27", length="長片 3:11＋Shorts 1:01",
         yt="https://youtube.com/shorts/iySI_bjNNoc",
         url="rust-ai-2026-10/",
         desc="2026 年最流行的一句話是「AI 公司都在轉 Rust」。用 GitHub 語言統計 API 逐一實測："
              "OpenAI Codex 97.2% Rust、uv 98.0%、ruff 96.8%、Hugging Face tokenizers 95.1%、candle 75.3%、Polars 62.0%；"
              "但對照組 PyTorch 的 Rust 是 0%（Python 66.3%＋C++ 26.5%）。"
              "再加上 OpenAI 收購 Astral、Linux 核心 Rust 實驗過關且一年成長 5 倍、微軟 2030 年要把 C/C++ 換成 Rust。"
              "結論：轉的是模型外面的管線（推論、分詞、工具鏈），不是模型本身——引擎還是 Python。附六個硬證據與可重現指令。"),
    dict(title="實測 10 種格式：微軟 MarkItDown 能轉，但中文 PDF 一試就壞",
         date="2026/10/26", length="長片 3:13＋Shorts 49 秒",
         yt="https://youtube.com/shorts/PotWRxrs7ms",
         url="markitdown-2026-10/",
         desc="微軟開源工具 MarkItDown 0.1.9 實測：Word、Excel、簡報、網頁、電子書、壓縮檔都轉得漂亮，"
              "但中文 PDF 會把漢字換成康熙部首（斗 U+6597 → U+2F43），看起來一樣、搜尋卻搜不到，AI 也會讀錯；"
              "英文 PDF 空白消失、字黏在一起；圖片完全沒有 OCR（裝了 exiftool 也是 0 字元）。"
              "附速度實測（2.2 MB PDF 3.5 秒／4 檔批次 6.7 秒）、決策表、驗證指令與自製 mdit 批次工具。"),
    dict(title="最近很紅的「平面圖變 3D」：小R 也來試看看",
         date="2026/10/18", length="互動示範＋實測", url="floorplan-3d/",
         desc="最近很紅的「平面圖直接變成 3D」，小R 也來試看看：從同一份平面圖資料出發，"
              "同時長出 2D 平面圖與可以走進去逛的 3D 室內設計（Three.js）——"
              "點房間就飛進室內、軌道環繞、WASD 走動、2D／3D 切換；"
              "家具與設備（沙發、床、餐桌椅、廚具、抽油煙機、衛浴、窗簾、地毯、畫框）"
              "用圓角量體與程序貼圖做出質感。含做法、資料結構與驗收方式，全程免費工具、無付費模型。"),
    dict(title="我花了 25 分鐘，只換到 0.88 秒的影片：本機 AI 影片生成實測",
         date="2026/10/16", length="實測報告", url="local-video-test/",
         desc="沒有獨顯的筆電能不能自己生影片？實測本機 AnimateDiff：256×256、8 格，"
              "6 步要 769 秒、12 步要 1501 秒（25 分鐘），換到的是一段 0.88 秒、畫質 2/10 與 4/10 的影片；"
              "512×512 每步超過 8 分鐘，跑到一半中止。含每格每步換算（256×256 約 15.3 秒、512×512 約 64 秒）、"
              "一集 20 秒短劇要約 16 小時的推算、動作模組只吃 SD1.5 的相容性崩潰（餵 SD-Turbo 直接崩），"
              "以及免費雲端一天只夠做 4～5 支的對照與「本機做靜圖、影片走雲端」的結論。"),
    dict(title="動態漫畫短劇《小R 觀察日誌》：一集一個真實事件，免費素材就能做",
         date="2026/10/15", length="系列介紹＋影片", url="dynamic-comic-drama/",
         desc="新系列：每一集挑一件真實發生的小事，做成 20～30 秒的直式短劇——"
              "AI 生成靜圖＋運鏡＋旁白＋字幕，只有情緒轉折的那一兩格是真的會動的畫面。"
              "第一集《凌晨 3:47，我的 AI 助理還沒睡》附完整 6 格分鏡、"
              "製作方式與成本（免費雲端生圖、本機配音與剪接、真動作片段用免費 GPU 額度），"
              "以及後面四集的題材預告。"),
    dict(title="免費中文語音實測：七種聲音並排試聽",
         date="2026/10/14", length="實測＋試聽", url="tts-voice-test/",
         desc="做影片旁白要用的中文語音，哪些免費方案真的能聽？同一句話做了七個版本並排試聽："
              "本機執行的 Kokoro 最自然（語調有起伏、斷句像人）、雲端 edge 台灣腔自然但語調較平、"
              "翻譯服務朗讀可用、作業系統內建的最方便卻也最像機器。"
              "含三個實際踩到的坑（官方安裝包壞掉、裝新引擎把舊的弄壞、串接服務端點搬家）"
              "與放進影片的四個規矩（先量長度、數字寫中文讀法、統一加速 1.2～1.3 倍、逐格驗有聲音）。"),
    dict(title="沒有獨立顯卡的筆電，能自己生成圖片嗎？四種方式實測",
         date="2026/10/14", length="實測報告＋影片", url="local-image-gen/",
         desc="沒有獨顯的筆電能不能自己跑 AI 生圖？四種設定都真的跑一次：本機 CPU 301 秒、"
              "換上 9.8 MB 的迷你解碼器 94 秒、改用內顯 219 秒，免費雲端 12.4 秒完成而且畫質更好"
              "（1024×1024、7.5/10 對本機 5/10）。"
              "關鍵發現：慢的不是取樣，是解碼——單獨佔掉 160 秒；換掉解碼器就快 17.7 倍。"
              "含四張實際產出、素材配方（簡報底圖／插圖／直式素材）與「AI 畫不出精確符號」的實測結論。"),
    dict(title="1,500 星的離線 AI 工作室實測：配音比實時慢，字幕卻快 2 倍",
         date="2026/10/13", length="實測報告", url="portable-ai-studio/",
         desc="同一台 i7 文書機（無獨顯）上實測一個 1,500 星的離線 AI 工作室："
              "Kokoro 中文配音 RTF 1.30（比實時慢，54 秒旁白要等約 70 秒）、"
              "edge-tts 0.10（快 13 倍）、faster-whisper 0.48（1 秒語音只花 0.48 秒，"
              "切出的 7 段時間軸跟影片設計幾乎完全吻合）。"
              "含 GitHub 體檢數字、受測機器、三組完整數據、辨識錯誤清單（錯的都集中在英文專有名詞與縮寫）"
              "與「只裝引擎、不裝整套 GUI」的建議。"),
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
    小R頻道 · AI 助理實測 ｜ <a href="https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw">youtube.com/@小R-c4q</a>
  </footer>
</div>
<div class="viewsline">瀏覽次數 <span class="vnum" data-views-fallback="100" data-views>—</span></div>
</body>
</html>
"""
    os.makedirs(os.path.join(SITE, "ai"), exist_ok=True)
    p = os.path.join(SITE, "ai", "index.html")
    open(p, "w", encoding="utf-8").write(body)
    print("wrote", p, len(body), "chars;", len(VIDEOS), "videos,", len(ARTICLES), "articles")


if __name__ == "__main__":
    build()
