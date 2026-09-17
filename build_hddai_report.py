# -*- coding: utf-8 -*-
"""產生「外接硬碟 × AI：產品發想與可行性評估」報告頁：/ai/hdd-ai/。

設計沿用 /ai/ 頁的 head（同一套紙張風格），只換 body。
示意圖全部用 inline SVG 直接畫在頁面裡（紙張底、墨藍線條＋朱紅重點、手繪抖動感）。
用法：python build_hddai_report.py [網站根目錄]
"""
import html, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
AI_INDEX = os.path.join(SITE, "ai", "index.html")
OUT = os.path.join(SITE, "ai", "hdd-ai")

VIDEO = "https://youtu.be/sRfQqf2v8IE"

INK, BLUE, RED, SOFT, LINE, PAPER = "#4a4640", "#364e70", "#bf4a3a", "#78706a", "#d9d1c2", "#fffdf6"


def esc(s):
    return html.escape(s, quote=False)


def tx(x, y, s, size=14, fill=INK, anchor="start", bold=False):
    b = ' font-weight="700"' if bold else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"'
            f' text-anchor="{anchor}"{b}>{esc(s)}</text>')


def wob(i, freq=0.028, scale=2.4):
    """手繪抖動感的濾鏡（只套在線條／框上，不套文字，字才不會糊）。"""
    return (f'<defs><filter id="wob{i}" x="-8%" y="-8%" width="116%" height="116%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" '
            f'seed="{i * 7 + 3}" result="t"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="t" scale="{scale}" '
            f'xChannelSelector="R" yChannelSelector="G"/></filter>'
            f'<marker id="ar{i}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5.5" '
            f'markerHeight="5.5" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker></defs>')


def fig(svg, caption, i):
    return f"""
  <figure class="fig">
    <div class="figscroll">{svg}</div>
    <figcaption><b>圖 {i}</b>｜{caption}
      <span class="figtag">示意圖，非實際產品外觀、非規格保證</span><span class="figswipe">（圖較寬，可左右滑動）</span></figcaption>
  </figure>"""


# ── 圖 1：產品概念圖（誰負責什麼） ─────────────────────────────
def fig_concept():
    s = ['<svg viewBox="0 0 560 340" role="img" aria-label="外接硬碟與 AI 軟體層的分工示意圖">']
    s.append(wob(1))
    s.append(f'<rect x="1" y="1" width="558" height="338" rx="10" fill="{PAPER}" stroke="{LINE}" stroke-width="2"/>')
    # 紙膠帶裝飾（放在左上角空白處，不壓文字）
    s.append(f'<g opacity=".7" transform="rotate(-3 70 16)"><rect x="30" y="6" width="86" height="20" '
             f'fill="#e8dcc0" stroke="#cbbfa4" stroke-width="1.4" filter="url(#wob1)"/></g>')
    s.append(tx(130, 22, "小R 頻道 · 產品發想", 12, SOFT))
    s.append(tx(28, 52, "誰負責什麼：硬碟不推論，推論交給主機", 17, BLUE, bold=True))
    # 左框：外接硬碟
    s.append(f'<g filter="url(#wob1)"><rect x="24" y="68" width="238" height="234" rx="12" fill="{PAPER}" '
             f'stroke="{BLUE}" stroke-width="2.4"/></g>')
    s.append(tx(42, 96, "外接硬碟負責", 16, BLUE, bold=True))
    for k, t in enumerate(["儲存本體：檔案留在此",
                           "索引檔：向量＋全文",
                           "插上就沿用（跨裝置）",
                           "可攜加密容器",
                           "不可變快照（不可改）",
                           "I/O 與校驗：硬碟專長"]):
        s.append(tx(42, 126 + k * 25, "・" + t, 12.5, INK))
    s.append(tx(42, 286, "不做推論 → 不需內建 NPU", 13, RED, bold=True))
    # 右框：AI 軟體層
    s.append(f'<g filter="url(#wob1)"><rect x="298" y="68" width="238" height="234" rx="12" fill="{PAPER}" '
             f'stroke="{BLUE}" stroke-width="2.4"/></g>')
    s.append(tx(316, 96, "AI 軟體層負責（主機上）", 16, BLUE, bold=True))
    for k, t in enumerate(["推論：借主機 NPU／GPU",
                           "檢索編排：一句話→查詢",
                           "規則式：檔名、時間、大小",
                           "抽取：PDF／OCR／語音",
                           "問答：本機小模型",
                           "索引：存在硬碟上"]):
        s.append(tx(316, 126 + k * 25, "・" + t, 12.5, INK))
    s.append(tx(316, 286, "跑在免費算力 → 不付授權費", 13, RED, bold=True))
    # 中間來回箭頭
    s.append(f'<g filter="url(#wob1)" fill="none" stroke="{BLUE}" stroke-width="2.2">'
             f'<path d="M270,152 L292,152" marker-end="url(#ar1)"/>'
             f'<path d="M290,208 L268,208" marker-end="url(#ar1)"/></g>')
    s.append(tx(280, 144, "指令", 12, SOFT, anchor="middle"))
    s.append(tx(280, 228, "結果", 12, SOFT, anchor="middle"))
    s.append("</svg>")
    return "".join(s)


# ── 圖 2：系統架構／資料流（為何免 NPU、免授權費） ──────────────
def fig_arch():
    s = ['<svg viewBox="0 0 560 484" role="img" aria-label="四層架構與資料流示意圖">']
    s.append(wob(2))
    s.append(f'<rect x="1" y="1" width="558" height="482" rx="10" fill="{PAPER}" stroke="{LINE}" stroke-width="2"/>')
    s.append(tx(26, 34, "四層分工：授權費 0 元，算力向主機借", 17, BLUE, bold=True))
    layers = [
        ("使用者層", ["問一句話（下行）；內容不出門（上行）"], BLUE),
        ("主機算力層（免費）", ["NPU／GPU／CPU：主機已有，對應用程式免費", "AI PC 約占 PC 出貨 54.7%，NPU 多數閒置"], RED),
        ("開源元件層（MIT／BSD／Apache-2.0）",
         ["pdfium（PDF）・Tesseract（OCR）・whisper.cpp（語音）", "llama.cpp＋Qwen2.5（問答）・sqlite-vec（檢索）"], BLUE),
        ("外接硬碟自研層", ["索引檔（向量＋全文）・不可變快照", "可攜加密容器・搜尋編排"], BLUE),
    ]
    y = 52
    for name, det, col in layers:
        s.append(f'<g filter="url(#wob2)"><rect x="26" y="{y}" width="508" height="84" rx="10" fill="{PAPER}" '
                 f'stroke="{col}" stroke-width="2.2"/></g>')
        s.append(tx(44, y + 26, name, 14.5, col, bold=True))
        for j, ln in enumerate(det):
            s.append(tx(44, y + 50 + j * 19, ln, 11.5, SOFT))
        y += 106
    for gy in (136, 242, 348):
        s.append(f'<g filter="url(#wob2)" fill="none" stroke="{RED}" stroke-width="2">'
                 f'<path d="M274,{gy + 12} L280,{gy + 3} L286,{gy + 12}"/></g>')
    s.append(tx(26, 472, "授權費 0 元，義務仍在：保留開源聲明、避開 AGPL／GPL 與非商用權重", 12, RED))
    s.append("</svg>")
    return "".join(s)


# ── 圖 3：使用情境流程 ─────────────────────────────
def fig_flow():
    steps = [
        ("插上硬碟，首次建索引", "背景執行、只讀不改；索引檔寫回硬碟"),
        ("用一句話問它", "「三個月前跟王先生談的那份合約」——不必記檔名"),
        ("硬碟端比對索引", "向量＋關鍵字的混合檢索，先挑出候選"),
        ("主機端抽出內容並摘要", "PDF 內文、圖片 OCR、影音轉錄，都在本機完成"),
        ("得到結果，可以接著問", "檔案路徑＋摘要＋引用來源；不上傳雲端"),
    ]
    s = ['<svg viewBox="0 0 560 330" role="img" aria-label="插上硬碟後的使用流程示意圖">']
    s.append(wob(3))
    s.append(f'<rect x="1" y="1" width="558" height="328" rx="10" fill="{PAPER}" stroke="{LINE}" stroke-width="2"/>')
    s.append(tx(26, 36, "插上硬碟之後，發生什麼事", 17, BLUE, bold=True))
    for k, (main, det) in enumerate(steps):
        y = 76 + k * 50
        s.append(f'<g filter="url(#wob3)"><circle cx="44" cy="{y - 5}" r="13" fill="{PAPER}" '
                 f'stroke="{RED if k == 4 else BLUE}" stroke-width="2.2"/></g>')
        s.append(tx(44, y, str(k + 1), 14, RED if k == 4 else BLUE, anchor="middle", bold=True))
        s.append(tx(70, y, main, 14.5, INK, bold=True))
        s.append(tx(70, y + 19, det, 12, SOFT))
        if k < len(steps) - 1:
            s.append(f'<path d="M44,{y + 10} L44,{y + 24}" stroke="{LINE}" stroke-width="2"/>')
    s.append("</svg>")
    return "".join(s)


# ── 圖 4：成本對照（對數刻度長條） ─────────────────────────────
def fig_cost():
    s = ['<svg viewBox="0 0 560 330" role="img" aria-label="自建模組與第三方授權金的成本對照圖">']
    s.append(wob(4))
    s.append(f'<rect x="1" y="1" width="558" height="328" rx="10" fill="{PAPER}" stroke="{LINE}" stroke-width="2"/>')
    s.append(tx(26, 36, "授權費 0 元，要付的不是這一筆", 17, BLUE, bold=True))
    base, step = 110, 102.5     # 對數刻度：1 格＝10 倍
    # 刻度軸
    s.append(f'<path d="M{base},252 L530,252" stroke="{LINE}" stroke-width="2"/>')
    for k, lab in enumerate(["100", "1 千", "1 萬", "10 萬", "100 萬"]):
        x = base + k * step
        s.append(f'<path d="M{x},246 L{x},258" stroke="{LINE}" stroke-width="2"/>')
        s.append(tx(x, 274, lab, 11.5, SOFT, anchor="middle"))
    s.append(tx(base, 294, "金額（美元，對數刻度）", 11.5, SOFT))
    # 長條 A：自建模組
    s.append(f'<g filter="url(#wob4)"><rect x="{base}" y="86" width="61" height="40" rx="5" '
             f'fill="{BLUE}" opacity=".85"/></g>')
    s.append(tx(base + 71, 113, "約 200～400 美元／年", 13, INK))
    s.append(tx(base, 78, "自建模組：簽章＋公證（每年固定）", 13.5, BLUE, bold=True))
    # 長條 B：第三方授權金
    s.append(f'<g filter="url(#wob4)"><rect x="{base}" y="160" width="307" height="40" rx="5" '
             f'fill="{RED}" opacity=".85"/><rect x="417" y="160" width="72" height="40" rx="5" '
             f'fill="{RED}" opacity=".4"/></g>')
    s.append(tx(base, 152, "第三方授權金：每台 1～5 美元 × 10 萬台／年", 13.5, RED, bold=True))
    s.append(tx(497, 185, "10 萬", 11.5, RED, anchor="middle"))
    s.append(tx(453, 218, "約 10 萬 ～ 50 萬美元／年", 12.5, INK, anchor="middle"))
    s.append(tx(26, 316, "結論：真正的固定成本在簽章與公證，不在每台的授權金", 12.5, RED))
    s.append("</svg>")
    return "".join(s)


# ── 圖 5：分階段落地路線 ─────────────────────────────
def fig_phase():
    cols = [
        ("Phase 1", "0～3 個月", RED,
         ["不可變備份", "＋異常寫入偵測", "純自研：無授權問題", "風險最低的起點", "找 3 家企業試用"]),
        ("Phase 2", "3～6 個月", BLUE,
         ["AI 檔案管家", "語意搜尋、OCR", "影音字幕摘要", "索引檔存硬碟", "驗收：每週使用"]),
        ("Phase 3", "6～12 個月", BLUE,
         ["可攜記憶容器", "格式自訂＝話語權", "私有知識庫試點", "需 IT 支援", "人臉辨識最後談"]),
    ]
    s = ['<svg viewBox="0 0 560 340" role="img" aria-label="三階段落地路線示意圖">']
    s.append(wob(5))
    s.append(f'<rect x="1" y="1" width="558" height="338" rx="10" fill="{PAPER}" stroke="{LINE}" stroke-width="2"/>')
    s.append(tx(26, 36, "建議順序（初步評估，非承諾）", 17, BLUE, bold=True))
    for k, (name, dur, col, items) in enumerate(cols):
        x = 26 + k * 170
        s.append(f'<g filter="url(#wob5)"><rect x="{x}" y="56" width="158" height="228" rx="10" fill="{PAPER}" '
                 f'stroke="{LINE}" stroke-width="2"/><rect x="{x}" y="56" width="158" height="40" rx="10" '
                 f'fill="{col}" opacity=".12"/></g>')
        s.append(tx(x + 12, 74, name, 14.5, col, bold=True))
        s.append(tx(x + 12, 90, dur, 11.5, SOFT))
        for j, it in enumerate(items):
            s.append(tx(x + 12, 118 + j * 30, "・" + it, 12, INK))
    s.append(tx(26, 312, "停損：3 個月內每週語意搜尋 <1 次，或品牌客戶不願付 ≥2 美元／台 → 停", 12, RED))
    s.append("</svg>")
    return "".join(s)


PRODUCTS = [
    dict(code="A", name="AI 檔案管家（AI File Steward）",
         who="所有人：個人、SOHO、小型團隊（客群最廣）",
         prob="找檔案只能靠記憶檔名；「三個月前那份合約」不知道放哪；重複檔與無意義檔名一堆。",
         sell="講一句話就找到、自動分類與命名、圖片文字抽取、影音字幕與摘要；索引檔存在硬碟，換電腦直接沿用。",
         why="元件全部是 MIT／BSD／Apache-2.0（授權費 0 元）；硬碟端不做推論，算力向主機 NPU／GPU 借；"
             "規則式（檔名、時間、大小）承擔多數工作，只有語意分類才動模型。MVP 初步評估約 3 個月。"),
    dict(code="B", name="AI 記憶硬碟（可攜記憶容器）",
         who="個人、創作者、AI 助理重度使用者（差異化最大）",
         prob="換一台電腦就要重新教 AI；對話、向量庫、工作檔散落在各台機器與雲端。",
         sell="換機一鍵還原、不用重教；加密容器可攜；容器格式自己定，等於掌握話語權。",
         why="容器格式自研（沒有外部授權與格式相依）；向量庫可用 sqlite-vec／FAISS／LanceDB；"
             "Windows Recall 快照可用官方匯出與解密範例做備份與索引（只能離線處理，不能即時讀取）。"),
    dict(code="C", name="不可變備份 ＋ 異常偵測",
         who="中小企業、工作室、有勒索病毒風險的團隊（最痛的一刀）",
         prob="備份連同本機一起被加密；還原不回來；沒人發現資料是什麼時候被動過。",
         sell="寫入後不可竄改、異常寫入即告警、還原得回來。",
         why="純自研、完全不碰模型授權；技術與法遵風險最低，適合當第一個 MVP（初步評估約 3 個月）。"),
    dict(code="D", name="私有知識庫硬碟（本地 RAG）",
         who="中小企業：法務、醫療、會計、研發（單價最高）",
         prob="公司文件不敢上雲；內部問答沒人維護、新人重複問同樣的問題。",
         sell="資料不出門、一鍵建索引與問答、離線可用。",
         why="llama.cpp ＋ Apache-2.0 開源權重可完全離線推論，抽取用 pdfium／Tesseract；"
             "但需要 IT 支援與 6 個月期程，所以排在最後（初步評估）。"),
]

LICENSE_ROWS = [
    ("語意搜尋／向量檢索", "sqlite-vec／FAISS／LanceDB", "MIT／Apache-2.0", "0 元"),
    ("內文抽取（PDF）", "pdfium", "BSD-3", "0 元"),
    ("OCR（圖片文字）", "Tesseract／PaddleOCR", "Apache-2.0", "0 元"),
    ("語音轉錄", "whisper.cpp（權重亦 MIT）", "MIT", "0 元"),
    ("本地問答", "llama.cpp ＋ Qwen2.5", "MIT／Apache-2.0", "0 元"),
    ("備份／異常偵測／記憶容器", "自研", "自有", "0 元"),
]

COST_ROWS = [
    ("Windows 程式碼簽章（OV）", "約 65～250 美元／年", "沒有簽章，使用者會被系統警告擋下"),
    ("Windows 程式碼簽章（EV）", "約 226 美元／年起", "EV 憑證要硬體 token，流程較長"),
    ("macOS 公證（Apple Developer）", "99 美元／年", "不上公證，macOS 會被 Gatekeeper 擋下"),
    ("合計（每年固定）", "約 200～400 美元／年", "這是固定成本，不是每台抽 1～5 美元的授權金"),
]


def body_html():
    # 一頁摘要
    boxes = [("4 個", "產品候選（全部不含自家 NPU、不付第三方授權費）"),
             ("0 元", "第三方授權費（元件全為 MIT／BSD／Apache-2.0）"),
             ("約 3 個月", "第一個可跑 MVP 的初步評估（不可變備份）"),
             ("3 個", "自研元件＝真正的差異化來源"),
             ("0 顆", "自家 NPU：算力向主機端已有的 NPU／GPU 借")]
    summary = "".join(f'<div class="box"><div class="big">{a}</div><div>{b}</div></div>' for a, b in boxes)

    # 產品候選
    prods = []
    for p in PRODUCTS:
        prods.append(f"""
  <article class="prod">
    <h3><span class="code">{p['code']}</span>{esc(p['name'])}</h3>
    <dl>
      <dt>目標客群</dt><dd>{esc(p['who'])}</dd>
      <dt>要解決的問題</dt><dd>{esc(p['prob'])}</dd>
      <dt>賣點</dt><dd>{esc(p['sell'])}</dd>
      <dt>為何做得出來</dt><dd>{esc(p['why'])}</dd>
    </dl>
  </article>""")

    lic = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td><td><strong>{esc(d)}</strong></td></tr>"
                  for a, b, c, d in LICENSE_ROWS)
    cost = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in COST_ROWS)

    return f"""
<div class="wrap">
  <a class="back" href="../">← 回 AI 助理實測</a>
  <header>
    <h1>外接硬碟 × AI：產品發想與可行性評估</h1>
    <div class="sub">不靠 NPU、不付第三方授權費 —— 做得到嗎？</div>
    <div class="meta-line">報告日期 2026/09/17　·　六輪發想 → 四個產品 → 免授權可行性 → 建議順序</div>
    <hr class="rule">
  </header>

  <div class="note warn">
    <strong>先講清楚這份報告是什麼</strong>：這是<strong>產品發想與可行性推估</strong>，
    不是產品規格保證、不是任何硬碟廠商或軟體公司的<strong>背書</strong>，也不構成投資建議。
    文中數字為<strong>公開資料整理與推估</strong>，時程（3／6 個月）為<strong>初步評估</strong>，不是承諾。
    影片連結：<a href="{VIDEO}">{VIDEO}</a>（<strong>目前為私人影片、尚未公開</strong>，審核後會轉公開）。
  </div>

  <h2><span class="dot"></span>一頁摘要（結論先行）</h2>
  <div class="summary">{summary}</div>
  <ul class="how">
    <li><strong>可行，但可行性來自「分工」，不是硬體升級</strong>：硬碟端只做 I/O、索引與可攜性；推論交給主機已有的 NPU／GPU／CPU。</li>
    <li>四個產品候選<strong>都不需要自家 NPU、也不需要付第三方授權費</strong>就能做出來（初步評估 MVP 3～6 個月）。</li>
    <li>授權費為 <strong>0 元</strong>，但義務仍在：要保留開源聲明、避開 AGPL／GPL 傳染與非商用權重。</li>
    <li>真正要付的錢是<strong>程式碼簽章與公證</strong>（約 200～400 美元／年），不是每台 1～5 美元的授權金。</li>
    <li>差異化在三件<strong>自研元件</strong>：搜尋編排、不可變快照、可攜記憶格式。</li>
    <li>建議順序：<strong>C 不可變備份 → A 語意搜尋 → B 可攜記憶容器 → D 私有知識庫</strong>；並先寫下停損條件。</li>
  </ul>

  <div class="note">
    <strong>四個前提（2026，公開資料整理與推估）</strong>：
    ① AI PC 已占全球 PC 出貨約 <strong>54.7%</strong>（2025 年約 31%），主機端 NPU 對應用程式是免費算力，且多數應用並未用到。
    ② 硬碟價格自 2025/9 起上漲約 <strong>46～50%</strong>，只靠每 TB 單價競爭已難拉開差距。
    ③ 硬碟綁備份軟體一起賣（Seagate／WD 隨附 Acronis）已是<strong>十幾年</strong>的成熟模式。
    ④ 這一版<strong>先不做 NPU</strong>：把算力留給主機，硬碟專心做它最擅長的事。
  </div>

  <h2><span class="dot"></span>產品候選清單（4 個）</h2>
{fig(fig_concept(), "外接硬碟與 AI 軟體層的分工：硬碟負責儲存、索引與可攜性；推論與問答在主機上跑。", 1)}
{"".join(prods)}

  <h2><span class="dot"></span>技術可行性：為何「不靠 NPU」仍可實現</h2>
{fig(fig_arch(), "四層架構與資料流：外接硬碟自研層 → 開源元件層 → 主機免費算力層 → 使用者層；向上的箭頭代表資料由硬碟往上處理（內容不出門，只傳查詢與結果）。", 2)}
  <ol class="how">
    <li><strong>硬碟端不做推論，只做 I/O 與索引</strong>：向量＋全文索引檔存在硬碟上，插上就能沿用，跨裝置不必重新建。</li>
    <li><strong>借用主機端已存在的算力</strong>：AI PC 的 NPU 對應用程式是免費算力；多數應用根本沒用到，等於閒置資源。</li>
    <li><strong>規則式優先、模型為輔</strong>：檔名、副檔名、時間、大小、重複檔先用規則式處理（成本近乎 0）；只有語意分類、摘要、問答才動用模型，把算力需求壓下來。</li>
    <li><strong>元件全部選寬鬆授權</strong>：MIT／BSD-3／Apache-2.0（見下表）＝授權費 0 元，只要保留聲明與授權文件。</li>
    <li><strong>三個關鍵元件自研</strong>：搜尋編排、不可變快照、可攜記憶格式 —— 沒有外部授權、也沒有外部格式相依。</li>
    <li><strong>影音解碼不做</strong>：H.264／HEVC 有專利池，交給作業系統解碼器，把專利風險留在平台端。</li>
  </ol>
  <p class="dim">為什麼這一版不內建 NPU（初步評估）：Microsoft Copilot+ 的系統級認證門檻是 40 TOPS，外接盒拿不到那種認證；
  13 TOPS 級邊緣 NPU 雖可塞進外接盒，但功耗升到 10～20W 就得加風扇，產品會從口袋型變成桌面型；
  且 USB4 磁吸 AI SSD 已有廠商在展場展示。結論是<strong>先不做，不是永遠不做</strong>。</p>

  <h2><span class="dot"></span>免外部授權：建議元件與授權費</h2>
  <div class="scroll"><table>
    <tr><th>功能</th><th>建議元件</th><th>授權</th><th>授權費</th></tr>
    {lic}
  </table></div>
  <p class="dim">上表為元件<strong>建議</strong>與授權種類整理；實際可用性、版本與條款以各專案官方 repo 與授權文件為準，
  商用前需逐項由法務確認（尤其是模型權重與資料集的授權）。</p>

  <h2><span class="dot"></span>使用情境：插上硬碟之後發生什麼事</h2>
{fig(fig_flow(), "使用流程：插上硬碟 → 背景建索引（只讀不改）→ 一句話查詢 → 硬碟端比對索引 → 主機端抽取與摘要 → 得到檔案路徑與摘要。", 3)}
  <p class="dim">設計上刻意把<strong>「內容」留在本機</strong>：只有查詢與答案在記憶體中流動，檔案與索引都不需要上傳；
  索引本身含敏感資訊，因此在硬碟上以加密容器存放。</p>

  <h2><span class="dot"></span>成本：還是要付的錢（不是授權費）</h2>
  <div class="scroll"><table>
    <tr><th>項目</th><th>金額（公開資料整理，實際以各平台公告為準）</th><th>說明</th></tr>
    {cost}
  </table></div>
{fig(fig_cost(), "成本對照：自建模組的每年固定成本（簽章＋公證）與第三方授權金（每台 1～5 美元 × 10 萬台／年）的差距；長條採對數刻度。", 4)}
  <p class="dim">這也是「軟體邊際成本接近 0」這句話的來源：多賣一台硬碟，不會多付一筆授權金，只多一份安裝與支援成本。</p>

  <h2><span class="dot"></span>風險與限制（誠實揭露）</h2>
  <div class="two">
    <div class="col no">
      <h3>三條不能碰的線</h3>
      <ul>
        <li><strong>AGPL／GPL 元件會傳染授權</strong>：PDF 一律用 pdfium（BSD-3），不要 MuPDF（AGPL）。</li>
        <li><strong>非商用的模型權重</strong>：部分學術模型（例：InsightFace 系列）標明非商用，商用即違約。</li>
        <li><strong>自訂條款的模型</strong>：部分開源權重免費但附條件，需法務看過；選 Apache-2.0 的會乾淨得多。</li>
        <li><strong>影音編解碼自己做</strong>：H.264／HEVC 專利池風險高，交給作業系統解碼器。</li>
      </ul>
    </div>
    <div class="col no">
      <h3>其他風險與限制</h3>
      <ul>
        <li><strong>市場面</strong>：硬碟漲價 46～50% 的環境下，若只比每 TB 單價，軟體加值會被拿來殺價。</li>
        <li><strong>商業面</strong>：隨附軟體（ODM／品牌）決策慢，願不願意付授權金是最大未知數。</li>
        <li><strong>技術面</strong>：索引品質與誤判、加密與金鑰管理、Recall 快照只能離線匯出處理（非即時讀取）。</li>
        <li><strong>法遵面</strong>：模型權重、資料集、字型與商標都需逐項確認，「免授權費」不等於「無義務」。</li>
        <li><strong>隱私面</strong>：索引會暴露檔名與內容脈絡，必須加密；企業版還需要權限與稽核設計。</li>
      </ul>
    </div>
  </div>
  <div class="note warn">
    <strong>停損條件（先寫下來）</strong>：3 個月內，使用者每週使用語意搜尋 <strong>不到 1 次</strong>，
    或品牌客戶<strong>不願意付 ≥2 美元／台</strong>，就停止把資源投在這個方向。
  </div>

  <h2><span class="dot"></span>落地路線建議（分階段）</h2>
{fig(fig_phase(), "三階段路線：Phase 1 不可變備份（低風險起點）→ Phase 2 AI 檔案管家（體驗最有感）→ Phase 3 可攜記憶容器與私有知識庫。", 5)}
  <ol class="how">
    <li><strong>Phase 1（0～3 個月）</strong>：先做不可變備份與異常寫入偵測 —— 純自研、無模型授權問題，中小企業最痛的一刀。</li>
    <li><strong>Phase 2（3～6 個月）</strong>：做 A「AI 檔案管家」的語意搜尋、OCR 與影音摘要 —— 元件全免授權、體驗最有感、客群最廣。</li>
    <li><strong>Phase 3（6～12 個月）</strong>：做 B 可攜 AI 記憶容器，容器格式自己定；同時試點 D 私有知識庫硬碟（需 IT 支援）。</li>
    <li><strong>下一步</strong>：先做出能跑的原型，再拿實測數據去談 ODM 隨附與授權金 —— 有能動的東西，談判才有底氣。</li>
  </ol>

  <div class="note">
    <strong>誠實揭露</strong><br>
    1. 本頁是<strong>產品發想與可行性推估</strong>，不是產品規格保證，也不是任何硬碟／軟體公司的背書或任何形式的投資建議。<br>
    2. 文中數字（AI PC 出貨占比、硬碟漲幅、程式碼簽章與公證費用、開源授權種類、市場規模）為<strong>公開資料整理與推估</strong>，
    可能與最新官方公告不同，引用前請以官方來源與各專案 repo 為準。<br>
    3. 時程（3／6／12 個月）與「做得到」屬<strong>初步評估</strong>，未經原型驗證；牽涉授權的判斷需法務複核。<br>
    4. 頁內所有圖為<strong>示意圖</strong>，非實際產品外觀、非規格保證。<br>
    5. 影片連結 <a href="{VIDEO}">{VIDEO}</a> 目前為<strong>私人影片（未公開）</strong>。
  </div>

  <a class="back" href="../">← 回 AI 助理實測</a>
</div>
"""


CSS = """  a.back{display:inline-block;margin:2px 0 12px;font-size:14.5px;text-decoration:none;color:var(--blue);border-bottom:1.5px solid currentColor}
  .meta-line{color:var(--soft);font-size:14px;margin-top:4px}
  .summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:6px 0 18px}
  .box{background:#fffdf6;border:2px solid var(--line);border-radius:14px;padding:12px 14px;font-size:13.5px;color:var(--soft)}
  .box .big{font-size:23px;color:var(--ink);margin-bottom:2px}
  .note.warn{border:2px solid #c9a227;background:#fff9e6}
  h2{font-size:clamp(19px,3.2vw,25px);margin:34px 0 10px;display:flex;align-items:center;gap:10px}
  h2 .dot{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}
  table{width:100%;border-collapse:collapse;font-size:14px;margin:10px 0}
  th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft)}
  .scroll{overflow-x:auto}
  article.prod{background:#fffdf6;border:2px solid var(--line);border-left:5px solid var(--red);border-radius:14px;padding:16px 18px;margin:14px 0}
  article.prod h3{margin:0 0 8px;font-size:19px;display:flex;align-items:center;gap:10px}
  article.prod .code{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;flex:none;
        border:2px solid var(--blue);border-radius:50%;color:var(--blue);font-size:15px}
  article.prod dl{display:grid;grid-template-columns:auto 1fr;gap:6px 12px;margin:8px 0 0;font-size:14.5px}
  article.prod dt{color:var(--soft);white-space:nowrap}
  article.prod dd{margin:0}
  .two{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
  .two .col{background:#fffdf6;border:2px solid var(--line);border-radius:14px;padding:14px 18px}
  .two .col h3{margin:0 0 6px;font-size:18px}
  .two .no{border-top:5px solid var(--red)}
  ul.how,ol.how{font-size:15.5px} ul.how li,ol.how li{margin:6px 0}
  .dim{color:var(--soft);font-size:14px}
  figure.fig{margin:16px 0 20px;background:#fffdf6;border:2px solid var(--line);border-radius:16px;
        padding:10px 12px 4px;box-shadow:2px 3px 0 rgba(74,70,64,.06)}
  figure.fig svg{display:block;width:100%;min-width:520px;height:auto}
  figure.fig .figscroll{overflow-x:auto}
  figure.fig figcaption{margin:8px 2px 6px;font-size:13.5px;color:var(--soft);
        border-top:1.5px dashed var(--line);padding-top:7px}
  figure.fig figcaption b{color:var(--ink);font-weight:400}
  .figtag{display:inline-block;margin-left:4px;font-size:12px;color:#9a8f7d}
  .figswipe{display:none;font-size:12px;color:#9a8f7d}
  svg text{font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif}
  @media (max-width:430px){.wrap{padding:22px 14px 60px} article.prod dl{grid-template-columns:1fr;gap:2px 0} article.prod dt{margin-top:6px}}
  @media (max-width:620px){.figswipe{display:inline}}
"""


def main():
    head = open(AI_INDEX, encoding="utf-8").read().split("<body")[0]
    head = re.sub(r"<title>[^<]*</title>",
                  "<title>外接硬碟 × AI：產品發想與可行性評估｜小R 頻道</title>", head, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="外接硬碟 × AI 的產品發想與可行性評估：'
                  '不靠 NPU、不付第三方授權費的四個產品候選、技術分工、成本與風險、分階段落地路線，附 5 張示意圖。">',
                  head, count=1)
    head = head.replace("</style>", CSS + "</style>", 1)
    os.makedirs(OUT, exist_ok=True)
    body = body_html()
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(head + "<body>\n" + body + "\n</body>\n</html>\n")
    print("已產生", os.path.join(OUT, "index.html"))
    print("內容區塊（h2）:", body.count("<h2>"), "｜示意圖:", body.count("figure class=\"fig\""),
          "｜產品卡:", body.count("article class=\"prod\""), "｜字元數:", len(body))
    print("區塊數（h2＋圖）＝", body.count("<h2>") + body.count("figure class=\"fig\""))


if __name__ == "__main__":
    main()
