# -*- coding: utf-8 -*-
"""產生「TOEIC 聽力與閱讀：題型分配、答題技巧、注意事項」頁：/toeic/guide/

用法：python build_toeic_guide.py [網站根目錄]
內容全部自行撰寫（不使用 ETS 官方試題原文）；題型數量與規則為公開資訊的整理。
"""
import html, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
TOEIC_INDEX = os.path.join(SITE, "toeic", "index.html")
OUT = os.path.join(SITE, "toeic", "guide")

PARTS = [
    ("Part 1", "照片描述", "6 題", "6 張照片", "聽力", "45 分鐘（與 Part 2–4 共用）",
     "照片 + 四個敘述句（紙本不印、只播一次）"),
    ("Part 2", "應答問題", "25 題", "25 題", "聽力", "同上", "一句問題或敘述 + 三個回應（A/B/C）"),
    ("Part 3", "簡短對話", "39 題", "13 組", "聽力", "同上", "兩人或三人對話，每組 3 題；部分題組附圖表"),
    ("Part 4", "簡短獨白", "30 題", "10 組", "聽力", "同上", "廣播、語音留言、公告、導覽等獨白，每組 3 題；部分附圖表"),
    ("Part 5", "句子填空", "30 題", "30 題", "閱讀", "75 分鐘（與 Part 6–7 共用）", "單句克漏字，考文法與字彙"),
    ("Part 6", "段落填空", "16 題", "4 篇", "閱讀", "同上", "每篇 4 題（其中 1 題常考整句插入）"),
    ("Part 7", "閱讀測驗", "54 題", "單篇＋多篇", "閱讀", "同上", "單篇 10 組、多篇（雙篇／三篇）題組，含即時通訊體、表格與圖表"),
]

TIPS = [
    ("Part 1 照片描述（6 題）",
     "先看照片再聽選項：先抓「誰、在做什麼、在哪、什麼狀態」四個要素。",
     ["常見陷阱：相似音（walk／work、copy／coffee）、把照片裡沒有的動作說成正在進行、"
      "用對的字講錯的關係（例如把桌上的杯子說成手上的）。",
      "看到「人在動作」的圖，選項出現 be 動詞＋被動（is being + p.p.）多半是干擾。",
      "看不到人、只有景物的照片，答案常描述位置與狀態（be lined up、be stacked）。"]),
    ("Part 2 應答問題（25 題）",
     "只聽一次、不留時間，靠「疑問詞 → 動詞 → 主詞」抓重點；答案常見間接回應。",
     ["WH 問句不會用 Yes/No 回答；Yes/No 問句反而常給「不直接說 Yes」的資訊（如 I'll check.）。",
      "注意「同音混淆」與「重複題目字詞」的假答案：聽到和題目一模一樣的字往往是陷阱。",
      "建議在播放前先掃描 A/B/C 選項位置（紙本只有題號），用鉛筆標記題號方便作答。"]),
    ("Part 3 簡短對話（39 題／13 組）",
     "每組對話前有時間看 3 題題目：先看「問什麼」再看選項，帶著問題聽。",
     ["三人對話要記住誰說了什麼（角色對應題）。",
      "圖表題先看圖表標題與單位，再回頭聽對話提到的數字或選項。",
      "題目順序大致等於對話順序；聽到答案就立刻畫卡，不要等聽完才回頭找。"]),
    ("Part 4 簡短獨白（30 題／10 組）",
     "先判斷獨白類型（廣播／語音留言／公告／導覽／廣告），類型決定答案會出現什麼資訊。",
     ["語音留言常考「回電號碼、目的、要求對方做什麼」；公告常考「時間、地點、變更原因」。",
      "獨白題的第二題常問「這段話最可能在什麼地方聽到」，靠場合線索判斷。",
      "圖表題出現時，先看座標軸與項目名稱，題目通常問某一項的變化或比較。"]),
    ("Part 5 句子填空（30 題）",
     "一題不超過 20 秒：先看空格前後決定考什麼（詞性／時態／連接詞／介系詞／字彙）。",
     ["看到空格前後是「形容詞 + 空格 + 名詞」→ 幾乎都是考詞性（要副詞還是形容詞）。",
      "整句只有一個動詞時，先確認主詞單複數與時態；有 although／because 這類連接詞，"
      "要注意前後子句的完整性。",
      "真的不會就猜，不要卡住：一題的時間可以留給 Part 7。"]),
    ("Part 6 段落填空（16 題／4 篇）",
     "先讀整段（30 秒）再作答，段落邏輯題占關鍵分。",
     ["每篇 4 題，通常 1 題考「整句插入」→ 看前後句的主詞與連接詞是否連貫。",
      "其餘考詞性、時態、字彙銜接；同一段落內答案常互相提示（例如時態要一致）。"]),
    ("Part 7 閱讀測驗（54 題）",
     "時間是最大敵人：閱讀 75 分鐘要寫 100 題，Part 7 大約留 50–55 分鐘。",
     ["先看題目再回文章找答案（定位法），不要逐字讀文章。",
      "多篇題組（雙篇／三篇）通常有 1–2 題需要交叉比對兩份文件（例如信件 + 訂單）。",
      "最後 5 分鐘一定要把畫卡補完，留白比答錯更虧。"]),
]

RULES = [
    "報名方式：台灣由官方代理辦理，可線上報名；考試場次與地點以官方公告為準。",
    "不用帶紙本准考證：全面改為線上查詢「應考資訊通知單」，測驗日前 2 個工作天上午 10:00 後查詢。",
    "必帶物品：有效身分證件正本（如身分證／護照）＋ 2B 鉛筆、橡皮擦；其他物品依考場規定放置。",
    "電子設備與穿戴裝置管制較過去嚴格：手機、智慧手錶等一律關機並放置指定處，違規可能不予計分。",
    "考試順序：先聽力（約 45 分鐘，100 題）再閱讀（75 分鐘，100 題），中間通常不另外休息。",
    "分數：聽力與閱讀各 5–495 分，合計 10–990 分；官方不公布「答對幾題換幾分」的精確對照，"
    "網路上流傳的換算表多為補習班依經驗回推。",
    "常見門檻參考：畢業門檻常見 550–750；外商／航空常見 700–850；金色證書（860 以上）常被當成求職亮點。",
]


def body_html():
    parts = "".join(
        f"<tr><td><strong>{p}</strong></td><td>{n}</td><td class='c'>{q}</td><td class='c'>{s}</td>"
        f"<td class='c'>{sec}</td><td>{time}</td><td>{what}</td></tr>"
        for p, n, q, s, sec, time, what in PARTS)
    tips = []
    for title, one, items in TIPS:
        li = "".join(f"<li>{html.escape(x)}</li>" for x in items)
        tips.append(f"""
  <article class="tip">
    <h3>{html.escape(title)}</h3>
    <p class="one">{html.escape(one)}</p>
    <ul>{li}</ul>
  </article>""")
    rules = "".join(f"<li>{html.escape(r)}</li>" for r in RULES)
    return f"""
<div class="wrap">
  <a class="back" href="../">← 回多益英文</a>
  <header>
    <h1>TOEIC 聽力與閱讀：題型分配、答題技巧、注意事項</h1>
    <div class="sub">Part 1–7 的題數、時間分配、答題技巧與考場規則</div>
    <hr class="rule">
  </header>

  <div class="summary">
    <div class="box"><div class="big">7 個 Part</div><div>Part 1–4 聽力、Part 5–7 閱讀</div></div>
    <div class="box"><div class="big">200 題</div><div>聽力 100 題（45 分鐘）＋ 閱讀 100 題（75 分鐘）</div></div>
    <div class="box"><div class="big">10 – 990</div><div>聽力、閱讀各 5–495 分</div></div>
    <div class="box"><div class="big">4 種口音</div><div>美式・加拿大・英式・澳式</div></div>
  </div>

  <div class="note">
    聽力與閱讀測驗（L&amp;R）共七個部分、200 題、約 2 小時，四種口音輪流出現；
    口說與寫作（S&amp;W）是<strong>另一場獨立的測驗</strong>（口說 11 題約 20 分鐘、寫作 8 題約 60 分鐘），不包含在 L&amp;R 裡。
  </div>

  <h2><span class="dot"></span>影片版（4 分 44 秒）</h2>
  <div class="embed">
    <iframe src="https://www.youtube-nocookie.com/embed/GMyjN9OyK4Y?rel=0" loading="lazy"
            title="多益聽力與閱讀：Part 1–7 題型分配、答題技巧與考場注意事項"
            allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen></iframe>
  </div>
  <p class="dim">影片內容就是這一頁：七個部分的題數、各部分技巧與陷阱、考場規則與分數制度。
    不想用嵌入播放的話，<a href="https://youtu.be/GMyjN9OyK4Y" target="_blank" rel="noopener">直接在 YouTube 看 →</a></p>

  <h2><span class="dot"></span>一、題型分配（這是考試的骨架）</h2>
  <div class="scroll"><table>
    <tr><th>部分</th><th>題型</th><th>題數</th><th>題組數</th><th>考科</th><th>時間</th><th>考什麼</th></tr>
    {parts}
  </table></div>
  <p class="dim">口音：聽力測驗包含美式、加拿大、英式、澳式四種口音（官方說明）；閱讀測驗 75 分鐘要完成 100 題，
  平均一題不到 45 秒，時間分配就是分數。</p>

  <h2><span class="dot"></span>二、各部分答題技巧與常見陷阱</h2>
  {''.join(tips)}

  <h2><span class="dot"></span>三、考場注意事項（台灣，2026）</h2>
  <ul class="how">{rules}</ul>

  <h2><span class="dot"></span>四、練習資源（全部自行撰寫，不使用官方試題）</h2>
  <ul class="how">
    <li><a href="../p2-sample/">Part 2 樣本</a>：4 題 × 四種口音，練「應答問題」的節奏。</li>
    <li><a href="../p3-full/">Part 3 完整題組</a>：13 組對話、39 題，含三人對話與圖表題，附中文詳解音檔。</li>
  </ul>

  <div class="note">
    <strong>原創聲明</strong>：本頁題型數量與考試規則為<strong>公開資訊的整理</strong>，答題技巧為自行撰寫；
    練習題目與語音全部自行製作，<strong>不使用 ETS 的試題或音檔</strong>。
    「TOEIC／多益」是 ETS 的註冊商標，此處僅為描述性使用（指相同題型結構），不代表 ETS 授權、合作或認可。
    考試規則與場次請以官方公告為準。
  </div>
  <a class="back" href="../">← 回多益英文</a>
</div>
"""

CSS = """  a.back{display:inline-block;margin:2px 0 12px;font-size:14.5px;text-decoration:none;color:var(--blue);border-bottom:1.5px solid currentColor}
  .summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:6px 0 18px}
  .box{background:#fffdf6;border:2px solid var(--line);border-radius:14px;padding:12px 14px;font-size:13.5px;color:var(--soft)}
  .box .big{font-size:23px;color:var(--ink);margin-bottom:2px}
  .note.warn{border:2px solid #c9a227;background:#fff9e6}
  h2{font-size:clamp(19px,3.2vw,25px);margin:34px 0 10px;display:flex;align-items:center;gap:10px}
  h2 .dot{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}
  table{width:100%;border-collapse:collapse;font-size:14px;margin:10px 0}
  th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}
  td.c{white-space:nowrap}
  .scroll{overflow-x:auto}
  article.tip{background:#fffdf6;border:2px solid var(--line);border-left:5px solid var(--blue);border-radius:14px;padding:14px 18px;margin:12px 0}
  article.tip h3{margin:0 0 6px;font-size:19px}
  .one{margin:0 0 8px;font-size:15.5px}
  article.tip ul{margin:0;padding-left:20px;font-size:15px;color:var(--soft)}
  article.tip ul li{margin:4px 0}
  ul.how{font-size:15.5px} ul.how li{margin:6px 0}
  .embed{position:relative;width:100%;max-width:820px;aspect-ratio:16/9;margin:10px 0 6px}
  .embed iframe{position:absolute;inset:0;width:100%;height:100%;border:0;border-radius:14px;background:#000}
  @supports not (aspect-ratio:16/9){.embed{height:0;padding-bottom:56.25%}}
  .dim{color:var(--soft);font-size:14px}
"""


def main():
    head = open(TOEIC_INDEX, encoding="utf-8").read().split("<body")[0]
    head = re.sub(r"<title>[^<]*</title>",
                  "<title>TOEIC 題型分配、答題技巧與注意事項（Part 1–7）｜小R 頻道</title>", head, count=1)
    head = head.replace("</style>", CSS + "</style>", 1)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(head + "<body>\n" + body_html() + "\n</body>\n</html>\n")
    print("已產生", os.path.join(OUT, "index.html"))


if __name__ == "__main__":
    main()
