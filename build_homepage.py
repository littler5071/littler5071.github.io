# -*- coding: utf-8 -*-
"""首頁產生器：三塊分類卡（每塊＝名稱、說明、「最新」兩則、全部連結）。

為什麼是這種形狀：使用者要「直覺、好讀」——一眼看到這個站有哪三類、每一類最新是什麼，
不要跨分類的流水帳，也不要一長串卡片。

資料來源
- 股市觀察：掃 `stock/<YYYYMMDD>/`（收盤後）與 `stock/<YYYYMMDD>-intraday/`（盤中快照）。
- AI 助理實測：`build_ai_index.py` 的 VIDEOS（單一來源）。
- 其餘（多益等）：`latest_items.json`。

用法：python build_homepage.py [網站根目錄]
"""
import glob, html, importlib.util, json, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
HEAD_FILE = os.path.join(SITE, "home_template_head.html")

CATS = [
    ("AI 助理實測", "ai", "c-ai",
     "把 AI 助理真正做過的事記錄下來。",
     "全部影片"),
    ("股市觀察", "stock", "c-stock",
     "每個交易日成交金額前 50 檔的技術線型逐檔分析（上市 35＋上櫃 15）。",
     "全部觀察紀錄"),
    ("多益英文", "toeic", "c-toeic",
     "題目全部自行撰寫；附中文詳解與音檔。",
     "全部題組"),
]


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
                            note="成交金額前 50 檔逐檔 K 線圖與線型說明，含「好／不好條件最多」排行榜。"))
        elif d.endswith("-intraday"):
            day = d[:8]
            sub = re.search(r'<div class="sub">([^<]+)</div>', h)
            snap = re.search(r"(\d{2}:\d{2}) 即時快照", _txt(sub.group(1)) if sub else "")
            tw = f"{day[:4]}/{day[4:6]}/{day[6:]}"
            out.append(dict(date=tw, sort=(day, 1), category="股市觀察",
                            title=f"{tw} {snap.group(1) if snap else ''} 盤中快照",
                            url=f"stock/{d}/",
                            note="候選池即時報價＋盤中成交金額前 50 檔，含時程紀錄與「盤中 → 收盤」對照。"))
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


CAT_HTML = """  <section id="cats">
    <div class="cat-grid">
{cards}
    </div>
  </section>

  <div class="note">
    上面三塊就是這個站的全部內容，每一塊只放<strong>最新的兩則</strong>，更早的都在各自的分類頁裡。
    股市觀察為公開資料的整理與觀察，<strong>不構成投資建議</strong>。
  </div>
  <div class="foot">
    頻道：<a href="https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw">youtube.com/@小R-c4q</a>
  </div>
"""

BODY = """<body>
<div class="wrap">
  <header>
    <h1>小R 頻道</h1>
    <div class="sub">影片索引 · 分類入口</div>
    <hr class="rule">
  </header>

{cats}
</div>
</body>
</html>
"""

FEED_CSS = """  /* 首頁：三塊分類卡（名稱、說明、最新兩則、全部連結） */
  .cat-grid{display:grid;grid-template-columns:1fr;gap:16px;margin-top:6px}
  @media (min-width:760px){.cat-grid{grid-template-columns:repeat(3,1fr);gap:14px}}
  .cat-card{display:block;background:#fffdf6;border:2px solid var(--line);border-radius:16px;
        padding:18px 20px 16px;box-shadow:2px 3px 0 rgba(74,70,64,.06);text-decoration:none;
        color:var(--ink);border-top:6px solid var(--line)}
  .cat-card.c-stock{border-top-color:#bf4a3a}
  .cat-card.c-ai{border-top-color:#364e70}
  .cat-card.c-toeic{border-top-color:#2f8f63}
  .cat-card:hover{box-shadow:3px 5px 0 rgba(74,70,64,.1)}
  .cc-title{font-size:clamp(21px,3.4vw,25px);margin-bottom:4px}
  .cc-note{color:var(--soft);font-size:14px;margin-bottom:12px}
  .cc-latest-label{font-size:12.5px;letter-spacing:.16em;color:var(--soft);margin-bottom:6px}
  ul.cc-list{list-style:none;margin:0 0 12px;padding:0}
  ul.cc-list li{margin:0 0 9px;line-height:1.55}
  ul.cc-list .d{display:inline-block;min-width:50px;color:var(--soft);font-size:13px;margin-right:8px}
  ul.cc-list a{color:var(--blue);text-decoration:none;font-size:15.5px;
        border-bottom:1.5px solid rgba(54,78,112,.3)}
  ul.cc-list a:hover{color:var(--red);border-color:var(--red)}
  .cc-go{display:inline-block;font-size:14.5px;color:var(--ink);border-bottom:2px solid var(--line);padding-bottom:1px}
  .cat-card:hover .cc-go{border-color:var(--red);color:var(--red)}
  .foot{text-align:center;color:var(--soft);font-size:14px;margin-top:30px}
"""


def short_title(it):
    """清單用的短標題：去掉開頭日期；股市每日只留指數與點數（手機一行內讀得完）。"""
    t = re.sub(r"^\d{4}/\d{2}/\d{2}\s*", "", it["title"])
    if it["category"] == "股市觀察" and t.startswith("收盤後觀察"):
        m = re.match(r"收盤後觀察：([\d.]+)\s*(\S*\s*點)", t)
        if m:
            try:
                idx = f"{float(m.group(1)):,.2f}"
            except ValueError:
                idx = m.group(1)
            return f"收盤後觀察：{idx}（{m.group(2)}）"
    return t


def build():
    items = stock_items() + ai_items() + manifest_items()
    cards = []
    summary = []
    for name, slug, cls, note, go in CATS:
        mine = sorted([i for i in items if i["category"] == name],
                      key=lambda x: x["sort"], reverse=True)
        rows = []
        for it in mine[:2]:
            d = it["date"][5:] if len(it["date"]) >= 10 else it["date"]
            title = short_title(it)   # 日期已顯示在左邊，標題不要再寫一次，且股市標題要縮短
            rows.append('        <li><span class="d">' + html.escape(d) + ' ·</span>'
                        '<a href="' + it["url"] + '">' + html.escape(title) + "</a></li>")
        cards.append('    <a class="cat-card ' + cls + '" href="' + slug + '/">\n'
                     '      <div class="cc-title">' + name + "</div>\n"
                     '      <div class="cc-note">' + note + "</div>\n"
                     '      <div class="cc-latest-label">最新</div>\n'
                     '      <ul class="cc-list">\n'
                     + (chr(10).join(rows) if rows else "        <li>（尚無內容）</li>") + "\n"
                     "      </ul>\n"
                     '      <span class="cc-go">' + go + "（" + str(len(mine)) + "）→</span>\n"
                     "    </a>")
        summary.append((name, len(mine), mine[0]["title"] if mine else "—"))

    head = open(HEAD_FILE, encoding="utf-8").read()
    if "</style>" in head:
        head = head.replace("</style>", FEED_CSS + "</style>", 1)
    body = BODY.replace("{cats}", CAT_HTML.format(cards=chr(10).join(cards)))
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(head + body)
    print("首頁已產生：3 塊分類卡")
    for name, n, latest in summary:
        print("   ", name, "共", n, "則｜最新:", latest[:40])


if __name__ == "__main__":
    build()
