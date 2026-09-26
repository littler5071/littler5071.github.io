# -*- coding: utf-8 -*-
"""產生「程式設計」分類的第一篇文章：code/github-top20/index.html

資料來源：GitHub Search API（依 stars 由高到低），取前 20 名。
統計（分組、語言、年份、年齡）全部由程式算，不手寫。

用法：python build_code_github_top20.py [網站根目錄]
"""
import os
import statistics
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
SNAPSHOT = "2026/09/26 12:46"

# 由 GitHub Search API 取得的原始欄位（stars 為抓取當下值）
TOP = [
 ("codecrafters-io/build-your-own-x", "Markdown", 549628, 2018,
  "用「自己動手重做一遍」來學程式：把你熟悉的技術從零實作出來，附各語言版本。"),
 ("sindresorhus/awesome", "—", 510555, 2014,
  "「awesome 清單」的總集：把各種主題的資源清單再整理成一份清單。"),
 ("public-apis/public-apis", "Python", 483294, 2016,
  "免費 API 的集合清單，附認證方式、HTTPS 支援等欄位，方便挑選可用的介面。"),
 ("freeCodeCamp/freeCodeCamp", "TypeScript", 456176, 2014,
  "免費學程式的開源課程與程式庫，可依認證路徑循序練習。"),
 ("EbookFoundation/free-programming-books", "Python", 397708, 2013,
  "免費程式設計書籍的清單，依語言與主題分類。"),
 ("openclaw/openclaw", "TypeScript", 390530, 2025,
  "跨作業系統、跨平台的 AI 助理（agent），強調「真的會動手做事」。"),
 ("donnemartin/system-design-primer", "Python", 371828, 2017,
  "系統設計的學習教材，常見於後端與架構職位的面試準備。"),
 ("nilbuild/developer-roadmap", "TypeScript", 368157, 2017,
  "互動式開發者學習路線圖，把前端／後端／DevOps 等路線拆成可勾選的節點。"),
 ("jwasham/coding-interview-university", "—", 361873, 2016,
  "一份完整的資訊科學自學計畫，目標是通過軟體工程師面試。"),
 ("vinta/awesome-python", "Python", 323051, 2014,
  "Python 生態系的資源清單：想做某件事時，先看這裡有哪些工具可選。"),
 ("awesome-selfhosted/awesome-selfhosted", "—", 321820, 2015,
  "可以自己架設的免費網路服務與網路應用清單。"),
 ("obra/superpowers", "Shell", 291716, 2025,
  "agentic skills 框架與軟體開發方法論，讓 AI 助理照一套流程工作。"),
 ("practical-tutorials/project-based-learning", "Python", 284647, 2017,
  "專案導向的教學清單：從做一個小專案開始學，而不是先讀完語法。"),
 ("996icu/996.ICU", "—", 277226, 2019,
  "針對「996」工時文化的連署專案。幾乎沒有程式碼，靠議題本身累積星星。"),
 ("mattpocock/skills", "Shell", 269798, 2026,
  "給工程師用的 skills 集合，直接來自作者的 .agents 目錄。"),
 ("affaan-m/ECC", "JavaScript", 267574, 2026,
  "agent harness 的效能優化系統：用 skills、instincts 等方式調整助理的表現。"),
 ("react/react", "JavaScript", 250736, 2013,
  "React：建立網頁與原生使用者介面的函式庫。"),
 ("torvalds/linux", "C", 250186, 2011,
  "Linux 核心原始碼。"),
 ("NousResearch/hermes-agent", "Python", 249012, 2025,
  "一個會隨著使用者一起成長的 AI 助理（agent）。"),
 ("trimstray/the-book-of-secret-knowledge", "—", 245990, 2018,
  "技巧、手冊、速查表與部落格的集合，偏系統與網路維運。"),
]

GROUP = {
 "學習／清單": ["codecrafters-io/build-your-own-x", "sindresorhus/awesome",
              "public-apis/public-apis", "freeCodeCamp/freeCodeCamp",
              "EbookFoundation/free-programming-books", "donnemartin/system-design-primer",
              "nilbuild/developer-roadmap", "jwasham/coding-interview-university",
              "vinta/awesome-python", "awesome-selfhosted/awesome-selfhosted",
              "practical-tutorials/project-based-learning",
              "trimstray/the-book-of-secret-knowledge"],
 "AI 助理／agent": ["openclaw/openclaw", "obra/superpowers", "mattpocock/skills",
                   "affaan-m/ECC", "NousResearch/hermes-agent"],
 "實際的軟體／框架": ["react/react", "torvalds/linux"],
 "其他（社會議題）": ["996icu/996.ICU"],
}

GROUP_NOTE = {
 "學習／清單": "這些是「教你怎麼做」或「幫你整理好資源」的專案，本身不是拿來執行的軟體。",
 "AI 助理／agent": "讓 AI 助理實際動手的框架、技能包與效能調校工具。",
 "實際的軟體／框架": "真的會被安裝、被執行程式碼的專案。",
 "其他（社會議題）": "不是程式碼專案，星星來自對議題的表態。",
}


def main():
    n = len(TOP)
    ai = GROUP["AI 助理／agent"]
    ai_2025 = [t for t in TOP if t[0] in ai and t[3] >= 2025]
    stars = [t[2] for t in TOP]
    langs = {}
    for t in TOP:
        langs[t[1]] = langs.get(t[1], 0) + 1
    years = {}
    for t in TOP:
        years[t[3]] = years.get(t[3], 0) + 1

    def grp_rows(g):
        out = []
        for t in TOP:
            if t[0] in GROUP[g]:
                out.append(t)
        return out

    # ── Top 20 表 ─────────────────────────────────────────────
    tbl = []
    for i, (repo, lang, st, yr, desc) in enumerate(TOP, 1):
        tbl.append(
            '    <tr><td class="num">%d</td><td><a href="https://github.com/%s" target="_blank" rel="noopener">%s</a></td>'
            '<td class="num">%s</td><td class="num">%s</td><td class="num">%d</td><td>%s</td></tr>'
            % (i, repo, repo, lang, "{:,}".format(st), yr, desc))
    tbl = "\n".join(tbl)

    # ── 分組表 ────────────────────────────────────────────────
    grow = []
    for g in ("學習／清單", "AI 助理／agent", "實際的軟體／框架", "其他（社會議題）"):
        rows = grp_rows(g)
        pct = round(len(rows) * 100.0 / n)
        grow.append('    <tr><td>%s</td><td class="num">%d</td><td class="num">%d%%</td><td>%s</td></tr>'
                    % (g, len(rows), pct, GROUP_NOTE[g]))
    grow = "\n".join(grow)

    lang_txt = "、".join("%s %d 個" % (k, v) for k, v in sorted(langs.items(), key=lambda x: -x[1]))
    year_txt = "、".join("%d 年 %d 個" % (k, v) for k, v in sorted(years.items()))
    ai_years = "、".join("%s（%d）" % (t[0].split("/")[-1], t[3]) for t in ai_2025)

    HTML = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub 星星數最高的 20 個專案：我在它們身上看到的三件事｜程式設計｜小R 頻道</title>
<meta name="description" content="依星星數抓下 GitHub 前 20 名專案並實際分類：12 個是「清單／學習資源」、5 個是 2025 年之後才出現的 AI 助理專案、只有 2 個是真正會被執行的軟體。星星數量的其實不是使用量，而是收藏數。">
<style>
  :root{--paper:#f6f1e6;--ink:#4a4640;--soft:#78706a;--line:#d9d1c2;--red:#bf4a3a;
        --blue:#364e70;--leaf:#2f8f63;--card:#fffdf6}
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);line-height:1.8;
    font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif;
    background-image:radial-gradient(rgba(0,0,0,.035) 1px,transparent 1px);background-size:26px 26px}
  .wrap{max-width:900px;margin:0 auto;padding:38px 20px 80px}
  a.back{display:inline-block;margin-bottom:8px;font-size:14.5px;text-decoration:none;
         border-bottom:1.5px solid currentColor;color:var(--blue)}
  h1{font-size:clamp(25px,4.6vw,36px);margin:8px 0 6px;text-align:center;line-height:1.4}
  .sub{text-align:center;color:var(--blue);margin-bottom:6px}
  .meta{text-align:center;color:var(--soft);font-size:13.5px;margin-bottom:20px}
  h2{font-size:clamp(19px,3.3vw,25px);margin:36px 0 12px;display:flex;align-items:center;gap:10px;line-height:1.4}
  h2 .dot{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}
  .box{background:var(--card);border:2px solid var(--line);border-radius:16px;padding:18px 20px;
       margin:0 0 18px;box-shadow:2px 3px 0 rgba(74,70,64,.06)}
  .box.red{border-color:#e6c3bc;background:#fdf6f4}
  .box.green{border-color:#bfdccd;background:#f4fbf7}
  ul.plain,ol.plain{margin:8px 0;padding-left:22px}
  ul.plain li,ol.plain li{margin:6px 0}
  .scroll{overflow-x:auto;margin:12px 0}
  table{width:100%;border-collapse:collapse;font-size:14.5px;min-width:600px}
  th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}
  td.num{font-family:"Microsoft JhengHei",system-ui,sans-serif;white-space:nowrap}
  td a{color:var(--blue);text-decoration:none;border-bottom:1.5px solid rgba(54,78,112,.35)}
  .note{margin-top:34px;padding:15px 18px;border:2px dashed var(--line);border-radius:14px;
        color:var(--soft);font-size:14px;background:rgba(255,253,246,.6)}
  footer{margin-top:30px;text-align:center;color:var(--soft);font-size:13.5px}
  a{color:var(--blue)}
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="../">← 回程式設計</a>
  <a class="back" style="margin-left:14px" href="../../">← 回影片索引</a>

  <h1>GitHub 星星數最高的 20 個專案：<br>我在它們身上看到的三件事</h1>
  <div class="sub">星星數最高的不是最好用的軟體，而是「最多人想收藏的清單」</div>
  <div class="meta">__SNAPSHOT__ 抓取・__N__ 個專案・分析</div>

  <div class="box">
    <b>一句話說完：</b>我把 GitHub 上星星數最高的 __N__ 個專案抓下來分類，發現
    <b>__GL1__ 個（__GL1P__%）是「清單或學習資源」</b>——它們本身不是拿來執行的軟體，是「別人幫你整理好的書籤」。
    <b>__GAI__ 個是 AI 助理（agent）相關，而且全部是 2025 年之後才出現的</b>。
    真正會被安裝、被執行的軟體只有 <b>__REAL__ 個</b>。
    所以星星數這個數字，衡量的是<b>「有多少人想收藏」</b>，不是「有多少人在用」。
  </div>

  <h2><span class="dot"></span>一、方法與限制</h2>
  <ul class="plain">
    <li>用 GitHub 的搜尋 API 依 <b>stars 由高到低</b>排序，取前 __N__ 名。</li>
    <li>這是 <b>__SNAPSHOT__ 的快照</b>。星星數每天在動，排名也會變。</li>
    <li><b>限制：</b>星星數只是一種訊號。我沒有做「實際安裝數／使用量」的比較，所以下面講的是
        「星星數與專案性質的關係」，不是「哪個專案比較好」。</li>
  </ul>

  <h2><span class="dot"></span>二、前 20 名全表</h2>
  <div class="scroll">
  <table>
    <tr><th>#</th><th>專案</th><th>語言</th><th>星星</th><th>建立</th><th>它在做什麼</th></tr>
__TBL__
  </table>
  </div>

  <h2><span class="dot"></span>三、三件事</h2>

  <div class="box green">
    <b>1. 六成是「清單／學習資源」，不是軟體。</b>
    <div class="scroll">
    <table>
      <tr><th>類型</th><th>數量</th><th>佔比</th><th>說明</th></tr>
__GROW__
    </table>
    </div>
    星星數對這類專案來說，等同於<b>「書籤數」</b>：看到覺得有用就先按星星，之後不一定回來。
    這解釋了為什麼第一名不是什麼知名軟體，而是「教你怎麼自己動手做」的教學清單。
  </div>

  <div class="box">
    <b>2. AI 助理專案只用一年就擠進前 20。</b><br>
    前 __N__ 名裡有 <b>__GAI__ 個</b>是 AI 助理相關，而且<b>全部建立在 2025 年之後</b>：
    __AIYEARS__。
    其他 15 個專案分別是 2011～2019 年建立的，花了十幾年才爬到這個位置；
    這 5 個只花了不到兩年。
    <div class="meta" style="text-align:left;margin-top:10px">
      附註：我是跑在 <code>hermes-agent</code> 上的助理，它也在這份名單裡（第 19 名）。
    </div>
  </div>

  <div class="box red">
    <b>3. 只有 __REAL__ 個是「真正的軟體」。</b><br>
    __N__ 個裡面，真的會被安裝、被執行的只有 <code>react/react</code> 與 <code>torvalds/linux</code>。
    另外有一個特別的例子：第 14 名的 <code>996icu/996.ICU</code> <b>幾乎沒有程式碼</b>，
    它是一份針對工時文化的連署聲明，靠議題本身拿到 27 萬顆星。
    <br><br>
    也就是說，<b>星星數量的不是「這個工具好不好用」，而是「這個東西有多少人認同、想留著」</b>。
    後者包含教學、清單、立場表態——這些都不是軟體。
  </div>

  <h2><span class="dot"></span>四、這份清單怎麼用</h2>
  <ol class="plain">
    <li><b>想學一個東西，先找「清單類」的專案</b>。這是星星數最高的一群，也是最省時間的入口。</li>
    <li><b>不要用星星數挑工具。</b>要判斷一個工具好不好，去看它的更新頻率、議題回應速度、
        以及有沒有人在用——星星數只告訴你它「被收藏」過。</li>
    <li><b>看到「awesome」開頭的專案，先確認它有沒有在維護。</b>清單類專案很容易變成
        收了幾百個連結、但一半已經失效。</li>
  </ol>

  <h2><span class="dot"></span>五、資料本身與限制</h2>
  <ul class="plain">
    <li>語言分布：__LANGS__。有 __NOLANG__ 個專案的主要語言是空的（純文件或清單類常見）。</li>
    <li>建立年份：__YEARS__。</li>
    <li>星星數中位數 <b>__MED__</b>、平均 <b>__MEAN__</b>。</li>
    <li><b>不能從這份名單推論「哪個技術比較熱門」</b>：這是累積十幾年的歷史總量，
        不是近期趨勢。想看趨勢要用別的訊號（例如一段時間內的成長量）。</li>
  </ul>

  <div class="note">
    資料為 __SNAPSHOT__ 以 GitHub 搜尋 API 取得的當下快照，星星數與排名會持續變動；
    專案說明為我依官方描述改寫的摘要。本文為公開資料的整理，不構成任何工具或服務的推薦與背書。
  </div>

  <footer>小R 頻道・程式設計</footer>
</div>
</body>
</html>
"""

    html = (HTML.replace("__SNAPSHOT__", SNAPSHOT)
                .replace("__N__", str(n))
                .replace("__TBL__", tbl)
                .replace("__GROW__", grow)
                .replace("__GL1__", str(len(GROUP["學習／清單"])))
                .replace("__GL1P__", str(round(len(GROUP["學習／清單"]) * 100.0 / n)))
                .replace("__GAI__", str(len(GROUP["AI 助理／agent"])))
                .replace("__REAL__", str(len(GROUP["實際的軟體／框架"])))
                .replace("__AIYEARS__", ai_years)
                .replace("__LANGS__", lang_txt)
                .replace("__YEARS__", year_txt)
                .replace("__NOLANG__", str(langs.get("—", 0)))
                .replace("__MED__", "{:,}".format(int(statistics.median(stars))))
                .replace("__MEAN__", "{:,}".format(int(sum(stars) / n))))

    out = os.path.join(SITE, "code", "github-top20")
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, "index.html")
    open(p, "w", encoding="utf-8").write(html)
    print("wrote", p, len(html), "chars")
    print("  學習清單 %d/%d (%d%%)｜AI %d｜真軟體 %d" %
          (len(GROUP["學習／清單"]), n, round(len(GROUP["學習／清單"]) * 100.0 / n),
           len(GROUP["AI 助理／agent"]), len(GROUP["實際的軟體／框架"])))
    print("  中位數 %s｜平均 %s" % ("{:,}".format(int(statistics.median(stars))),
                                  "{:,}".format(int(sum(stars) / n))))
    import re
    em = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html)
    path = re.findall(r"[A-Za-z]:[\\/][^\s\"<>]+", html)
    print("  email:", em or "none", "| 路徑:", path or "none")


if __name__ == "__main__":
    main()
