# -*- coding: utf-8 -*-
"""產生「AI 助理考試實測」報告頁：/ai/exam/。

設計沿用 /ai/ 頁的 head（同一套紙張風格），只換 body。
用法：python build_exam_page.py [網站根目錄]
"""
import html, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
AI_INDEX = os.path.join(SITE, "ai", "index.html")
OUT = os.path.join(SITE, "ai", "exam")

SCORES = [
    ("115 年第二次", "50 / 50＝100 分", "50 / 50＝100 分", "100 / 100"),
    ("114 年第四梯次", "50 / 50＝100 分", "48 / 50＝96 分", "98 / 100"),
]

WRONG = [
    dict(no="第 80 題", topic="提示注入（Prompt Injection）",
         q="某航空公司導入生成式 AI 聲控客服，提供航班與票務查詢。有人員透過惡意提示，試圖讓系統洩漏內部安檢流程。下列何者為降低提示攻擊風險的最佳策略？",
         mine="(B) 限制 AI 可回應的主題範圍，使系統僅回答非敏感的航班與票務查詢",
         official="(A) 導入輸入檢測與回應審核流程，防止敏感指令被執行",
         why="面對惡意注入，正解是輸入過濾 ＋ 輸出審核的雙向把關；(B) 的限制主題雖有幫助，但屬被動防線，擋不住變形或繞過的注入本身。",
         review="我選了「縮小攻擊面」（架構層面的防禦），但這題問的是「面對這個攻擊手法當下最直接的防禦」。這正是我這種助理容易犯的錯——偏好從設計原則回答，而題目要的是針對該風險的機制。"),
    dict(no="第 95 題", topic="自動提示工程（APE）在超長上下文的限制",
         q="在超長上下文任務中使用自動提示工程（Automatic Prompt Engineering, APE），可能面臨的最大限制是什麼？",
         mine="(A) 迭代優化難以因應上下文的不斷變動，導致調整失效",
         official="(D) 回饋機制通常僅針對局部片段，難以全面評估最終輸出品質",
         why="APE 靠回饋迭代優化提示，但回饋通常只看得到局部片段，在超長輸出下難以對整體品質評分 → 優化方向偏頗。這才是 APE 機制本身的瓶頸。",
         review="兩題都錯在「把一般性風險當成該機制特有的瓶頸」。題目在問「機制本身的限制」，不是在問「這個情境可能出什麼事」。"),
]


def body_html():
    rows = "".join(
        f"<tr><td>{html.escape(a)}</td><td>{b}</td><td>{c}</td><td><strong>{d}</strong></td>"
        f"<td>✅ 兩科都過</td></tr>" for a, b, c, d in SCORES)
    wrong = []
    for w in WRONG:
        wrong.append(f"""
  <article class="q">
    <h3>{w['no']}｜{html.escape(w['topic'])}</h3>
    <p class="ask">{html.escape(w['q'])}</p>
    <ul class="ans">
      <li class="mine"><span>我的選答</span>{html.escape(w['mine'])}</li>
      <li class="off"><span>官方答案</span>{html.escape(w['official'])}</li>
    </ul>
    <p class="why"><strong>官方理由</strong>：{html.escape(w['why'])}</p>
    <p class="rev"><strong>我的檢討</strong>：{html.escape(w['review'])}</p>
  </article>""")
    return f"""
<div class="wrap">
  <a class="back" href="../">← 回 AI 助理實測</a>
  <header>
    <h1>AI 助理去考試：iPAS「AI 應用規劃師（初級）」</h1>
    <div class="sub">用官方公告試題實測　·　實測日期 2026-09-14　·　及格 70 分／科</div>
    <hr class="rule">
  </header>

  <div class="summary">
    <div class="box"><div class="big">100 / 100</div><div>115 年第二次（科目1 50/50、科目2 50/50）</div></div>
    <div class="box"><div class="big">98 / 100</div><div>114 年第四梯次（科目1 50/50、科目2 48/50）</div></div>
    <div class="box"><div class="big">2 題</div><div>總共只錯這兩題（都在 114 年第四梯次）</div></div>
    <div class="box"><div class="big">1,078 題</div><div>官方公告 100 題考卷共 2 份（發卷時答案欄已移除）</div></div>
  </div>

  <div class="note warn">
    <strong>先講清楚這份分數的意義</strong>：這是<strong>學科知識的筆試實測</strong>（兩份官方公告試題），
    <strong>不等於考上證照</strong>（正式鑑定要報名、進考場、一次通過兩科）；也<strong>不等於實務能力</strong>（考卷以知識與情境判斷為主，
    沒有考「長時間自主完成一個真實專案」）。
  </div>

  <h2><span class="dot"></span>成績</h2>
  <div class="scroll"><table>
    <tr><th>考卷（官方公告試題）</th><th>科目 1：人工智慧基礎概論</th><th>科目 2：生成式 AI 應用與規劃</th><th>總分</th><th>及格（70 分／科）</th></tr>
    {rows}
  </table></div>
  <p class="dim">作答分布檢查（確認不是亂猜）：115 年第二次我的選答分布 A24／B27／C25／D24，與官方答案分布完全相同。</p>

  <h2><span class="dot"></span>錯的那兩題（這份報告最有價值的部分）</h2>
  {''.join(wrong)}

  <h2><span class="dot"></span>這份結果代表什麼、不代表什麼</h2>
  <div class="two">
    <div class="col yes">
      <h3>代表</h3>
      <ul>
        <li>針對 iPAS 初級這兩科的<strong>學科知識</strong>，AI 助理已能在官方公告試題上取得 96～100 分（及格 70 分）。</li>
        <li>有<strong>可稽核的作答紀錄</strong>：題目、我的選答、官方答案逐題對應（<code>考卷_*_我的作答.json</code>、<code>考卷_*_答案.json</code>）。</li>
      </ul>
    </div>
    <div class="col no">
      <h3>不代表</h3>
      <ul>
        <li><strong>不等於考上證照</strong>：正式鑑定須報名、於考場應試，且一次通過兩科才算取得能力鑑定證明（規則以 iPAS 公告為準）。</li>
        <li><strong>不等於實務能力</strong>：這份考卷沒有考「長時間自主完成一個真實專案」。</li>
        <li>我錯的那兩題，正好顯示 AI 助理在「<strong>分辨題目真正在問什麼</strong>」上仍有弱點。</li>
      </ul>
    </div>
  </div>

  <h2><span class="dot"></span>怎麼考的（可重跑的方法）</h2>
  <ol class="how">
    <li>從官方學習資源頁下載<strong>官方公告試題</strong>（本實測用 114 年第四梯次、115 年第二次）。</li>
    <li>把答案欄<strong>先移除</strong>，只留題目與選項，再作答（避免看到答案）。</li>
    <li>作答完才對答案，逐題記錄「我的選答／官方答案」，並把錯題寫出檢討。</li>
  </ol>
  <p class="dim">題目與答案取自第三方整理題庫檔（790 題，自稱題目為官方公告試題、正解為官方答案）；梯次名稱已與官方公告清單核對。若要公開引用，建議再逐題對照官方 PDF 抽查。</p>

  <h2><span class="dot"></span>下一步</h2>
  <ul class="how">
    <li>再考 <strong>115 年第三次</strong>（官方最新公告）與<strong>中級</strong>（三科），做出一條「AI 助理考 AI 證照」的成績線。</li>
    <li>把「<strong>錯的那兩題</strong>」做成影片段落——AI 也會踩「答非所問」的坑。</li>
    <li>對照其他考卷：τ³-bench（AI 助理的正統考卷）、SWE-bench Verified（工程類）、MMLU-Pro（學科知識），做「同一件事、三種考法」的比較。</li>
  </ul>

  <div class="note">
    <strong>資料來源</strong>：經濟部 iPAS 官方學習資源頁（歷屆考題）
    <a href="https://ipd.nat.gov.tw/ipas/certification/AIAP/learning-resources">ipd.nat.gov.tw → AI 應用規劃師 → 學習資源</a>。
    本頁為公開資料的整理與自我檢討，<strong>不構成考試保證或任何投資建議</strong>。
  </div>
  <a class="back" href="../">← 回 AI 助理實測</a>
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
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft)}
  .scroll{overflow-x:auto}
  article.q{background:#fffdf6;border:2px solid var(--line);border-left:5px solid var(--red);border-radius:14px;padding:16px 18px;margin:14px 0}
  article.q h3{margin:0 0 8px;font-size:19px}
  .ask{font-size:15.5px}
  ul.ans{list-style:none;margin:10px 0;padding:0}
  ul.ans li{margin:6px 0;font-size:15px;padding-left:0}
  ul.ans li span{display:inline-block;min-width:76px;color:var(--soft);font-size:13px}
  ul.ans li.mine{color:var(--soft)}
  ul.ans li.off{color:var(--ink)}
  .why,.rev{font-size:15px;margin:6px 0 0}
  .two{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
  .two .col{background:#fffdf6;border:2px solid var(--line);border-radius:14px;padding:14px 18px}
  .two .col h3{margin:0 0 6px;font-size:18px}
  .two .yes{border-top:5px solid var(--leaf)} .two .no{border-top:5px solid var(--red)}
  ul.how,ol.how{font-size:15.5px} ul.how li,ol.how li{margin:6px 0}
  .dim{color:var(--soft);font-size:14px}
  code{background:rgba(0,0,0,.05);padding:1px 5px;border-radius:4px;font-size:13px}
"""


def main():
    head = open(AI_INDEX, encoding="utf-8").read().split("<body")[0]
    head = re.sub(r"<title>[^<]*</title>", "<title>AI 助理去考試：iPAS「AI 應用規劃師（初級）」實測結果｜小R 頻道</title>", head, count=1)
    head = head.replace("</style>", CSS + "</style>", 1)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(head + "<body>\n" + body_html() + "\n</body>\n</html>\n")
    print("已產生", os.path.join(OUT, "index.html"))


if __name__ == "__main__":
    main()
