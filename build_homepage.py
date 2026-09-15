# -*- coding: utf-8 -*-
"""首頁產生器：跨分類「最新動態」（最新 5 筆）＋ 三個分類入口。

資料來源
- 股市觀察：掃 `stock/<YYYYMMDD>/`（收盤後）與 `stock/<YYYYMMDD>-intraday/`（盤中快照），
  標題從頁面抽（加權指數／快照時間）。
- AI 助理實測：`build_ai_index.py` 的 VIDEOS（單一來源，不重複維護）。
- 其餘（多益等）：`latest_items.json`。

用法：python build_homepage.py [網站根目錄]
"""
import glob, html, json, os, re, sys, importlib.util

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
HEAD_FILE = os.path.join(SITE, "home_template_head.html")
CAT_CLASS = {"AI 助理實測": "c-ai", "股市觀察": "c-stock", "多益英文": "c-toeic"}


def _txt(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def stock_items():
    out = []
    for p in glob.glob(os.path.join(SITE, "stock", "*", "index.html")):
        d = os.path.basename(os.path.dirname(p))
        h = open(p, encoding="utf-8").read()
        if re.fullmatch(r"\d{8}", d):
            big = re.search(r'<div class="big[^"]*">([^<]+)</div>\s*<div>加權指數\s*([^<]*)</div>', h)
            tw = f"{d[:4]}/{d[4:6]}/{d[6:]}"
            out.append(dict(date=tw, sort=(d, 3), category="股市觀察",
                            title=f"{tw} 收盤後觀察：{_txt(big.group(1)) if big else '-'}　{_txt(big.group(2)) if big else ''}",
                            url=f"stock/{d}/",
                            note="成交金額前 50 檔（上市 35＋上櫃 15）逐檔 K 線圖與線型說明，含「好／不好條件最多」排行榜。"))
        elif d.endswith("-intraday"):
            day = d[:8]
            sub = re.search(r'<div class="sub">([^<]+)</div>', h)
            snap = re.search(r"(\d{2}:\d{2}) 即時快照", _txt(sub.group(1)) if sub else "")
            tw = f"{day[:4]}/{day[4:6]}/{day[6:]}"
            out.append(dict(date=tw, sort=(day, 1), category="股市觀察",
                            title=f"{tw} {snap.group(1) if snap else ''} 盤中快照",
                            url=f"stock/{d}/",
                            note="第一次盤中試作：候選池 411 檔即時報價＋盤中成交金額前 50 檔，含時程紀錄與「盤中 → 收盤」對照。"))
    return out


def ai_items():
    p = os.path.join(SITE, "build_ai_index.py")
    if not os.path.exists(p):
        return []
    spec = importlib.util.spec_from_file_location("bai", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = []
    for v in getattr(mod, "VIDEOS", []):
        d = v.get("date", "").replace("-", "/")
        out.append(dict(date=d, sort=(d.replace("/", ""), 2), category="AI 助理實測",
                        title=v["title"], url=v["url"], note=v.get("desc", "")))
    return out


def manifest_items():
    p = os.path.join(SITE, "latest_items.json")
    if not os.path.exists(p):
        return []
    out = []
    for v in json.load(open(p, encoding="utf-8")).get("items", []):
        d = v.get("date", "").replace("-", "/")
        out.append(dict(date=d, sort=(d.replace("/", ""), 2), category=v["category"],
                        title=v["title"], url=v["url"], note=v.get("note", "")))
    return out


FEED_HTML = """  <section id="feed">
    <h2><span class="dot"></span>最新動態<span class="more">跨分類最新 {n} 筆</span></h2>
    <ol class="feed">
{items}
    </ol>
  </section>

  <section id="cats">
    <h2><span class="dot"></span>分類入口<span class="more">想看某一類的全部內容就從這裡進</span></h2>
    <div class="entry-grid">
      <a class="entry-card" id="ai" href="ai/">
        <div class="ec-title">AI 助理實測</div>
        <div class="ec-note">把 AI 助理真正做過的事記錄下來：怎麼運作、怎麼踩坑、怎麼修好。</div>
        <div class="ec-go">全部影片 →</div>
      </a>
      <a class="entry-card" id="stock" href="stock/">
        <div class="ec-title">股市觀察</div>
        <div class="ec-note">每個交易日成交金額前 50 檔的技術線型逐檔分析；只用公開資料，不構成投資建議。</div>
        <div class="ec-go">全部觀察紀錄 →</div>
      </a>
      <a class="entry-card" id="toeic" href="toeic/">
        <div class="ec-title">多益英文</div>
        <div class="ec-note">題目全部自行撰寫、不使用官方試題；附中文詳解與音檔，適合通勤練一輪。</div>
        <div class="ec-go">全部題組 →</div>
      </a>
    </div>
  </section>
"""

BODY = """<body>
<div class="wrap">
  <header>
    <h1>小R 頻道</h1>
    <div class="sub">最新動態 · 分類入口</div>
    <hr class="rule">
  </header>

{feed}
  <div class="note">
    這裡是影片與文章的索引：上面是**跨分類的最新幾筆**，下面是三個分類入口。
    股市觀察為公開資料的整理與觀察，<strong>不構成投資建議</strong>；多益題目全部自行撰寫，不使用官方試題。
  </div>
  <div class="foot">
    頻道：<a href="https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw">youtube.com/@小R-c4q</a>
  </div>
</div>
</body>
</html>
"""

FEED_CSS = """  /* 首頁：最新動態與分類入口 */
  #feed h2 .more, #cats h2 .more{font-size:14px;color:var(--soft);margin-left:8px;font-weight:normal}
  ol.feed{list-style:none;margin:8px 0 0;padding:0}
  ol.feed li{background:#fffdf6;border:2px solid var(--line);border-left:5px solid var(--blue);
        border-radius:12px;padding:12px 16px;margin:0 0 10px;box-shadow:2px 3px 0 rgba(74,70,64,.05)}
  ol.feed li.c-ai{border-left-color:#364e70} ol.feed li.c-stock{border-left-color:#bf4a3a}
  ol.feed li.c-toeic{border-left-color:#2f8f63}
  .f-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 10px}
  .f-cat{font-size:12px;padding:1px 9px;border-radius:999px;border:1.5px solid currentColor}
  .f-cat.c-ai{color:#364e70} .f-cat.c-stock{color:#bf4a3a} .f-cat.c-toeic{color:#2f8f63}
  .f-date{font-size:13px;color:var(--soft)}
  .f-title{font-size:clamp(16px,2.6vw,19px)}
  .f-title a{color:var(--ink);text-decoration:none;border-bottom:2px solid rgba(54,78,112,.35)}
  .f-title a:hover{color:var(--red);border-color:var(--red)}
  .f-note{color:var(--soft);font-size:14px;margin-top:3px}
  .entry-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:10px}
  a.entry-card{display:block;text-decoration:none;background:#fffdf6;border:2px solid var(--line);
        border-radius:14px;padding:16px 18px;box-shadow:2px 3px 0 rgba(74,70,64,.06);color:var(--ink)}
  a.entry-card:hover{border-color:#c8bda8;box-shadow:3px 4px 0 rgba(74,70,64,.1)}
  .ec-title{font-size:20px;margin-bottom:4px}
  .ec-note{color:var(--soft);font-size:14px;min-height:44px}
  .ec-go{color:var(--blue);font-size:14.5px;margin-top:8px}
  .foot{text-align:center;color:var(--soft);font-size:14px;margin-top:34px}
"""


def build():
    items = stock_items() + ai_items() + manifest_items()
    items.sort(key=lambda x: x["sort"], reverse=True)
    top = items[:5]
    li = []
    for it in top:
        cls = CAT_CLASS.get(it["category"], "")
        li.append(f"""      <li class="{cls}">
        <div class="f-head"><span class="f-cat c-{cls[2:] if cls else 'x'}">{html.escape(it['category'])}</span>
          <span class="f-date">{html.escape(it['date'])}</span></div>
        <div class="f-title"><a href="{it['url']}">{html.escape(it['title'])}</a></div>
        <div class="f-note">{html.escape(it['note'])}</div>
      </li>""")
    head = open(HEAD_FILE, encoding="utf-8").read()
    if "</style>" in head:
        head = head.replace("</style>", FEED_CSS + "</style>", 1)
    body = BODY.replace("{feed}", FEED_HTML.format(n=len(top), items=chr(10).join(li)))
    body = body.replace("**跨分類的最新幾筆**", "<strong>跨分類的最新幾筆</strong>")
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(head + body)
    print("首頁已產生：", len(top), "筆最新動態（全部候選", len(items), "筆）+ 3 個分類入口")
    for it in top:
        print("   ", it["date"], it["category"], it["title"][:44])


if __name__ == "__main__":
    build()
