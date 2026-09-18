# -*- coding: utf-8 -*-
"""首頁產生器：每個分類放「最新 2 則」卡片（2026/09/16 使用者定案：原本只放 1 則）＋ 分類入口連結。

形狀：三個分類區塊（AI 助理實測 → 股市觀察 → 多益英文，順序與導覽列一致），
每區＝分類標題（可點）＋一句說明＋最新 2 則卡片（標籤＝最新／近期）＋「全部 N 則 →」。
股市若同一天另有盤中快照，在卡片下方給一行小連結（不要再佔一張卡）。

資料來源
- 股市觀察：掃 `stock/<YYYYMMDD>/`（收盤後）與 `stock/<YYYYMMDD>-intraday/`（盤中快照）。
- AI 助理實測：`build_ai_index.py` 的 VIDEOS。
- 其餘（多益等）：`latest_items.json`。

用法：python build_homepage.py [網站根目錄]
"""
import glob, html, importlib.util, json, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
HEAD_FILE = os.path.join(SITE, "home_template_head.html")

# 大盤快篩快照（market_screen.py 產出）放在股市觀察工作目錄：首頁只用它產生「一行大盤狀態」
MARKET_DIR = os.environ.get("XIAOR_MARKET_DIR", r"D:/_Richard/OpenCode/圖片生成/小R頻道_股市觀察")


def _minus(t):
    """負號用 U+2212（跟頁面其他數字一致）；只有正負號那個字會被換掉。"""
    return t.replace("-", "\u2212")


def market_line(day):
    """首頁股市區塊的一行大盤狀態（讀 out_market_screen_<day>.json）。

    例：09/17 主狀態：站上月線、月線向上｜距多方頸線 −2.71%（量比 20 1.00）
    找不到快照或快照裡沒有主狀態 → 回空字串（首頁照常產出，不寫猜的數字）。
    """
    files = sorted(glob.glob(os.path.join(MARKET_DIR, "out_market_screen_*.json")))
    if not files:
        return ""
    p = os.path.join(MARKET_DIR, f"out_market_screen_{day}.json")
    if not os.path.exists(p):                      # 沒有當天的就用不晚於當天的最新一份
        cand = [f for f in files if re.search(r"_(\d{8})\.json$", f).group(1) <= day]
        if not cand:
            return ""
        p = cand[-1]
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return ""
    st = d.get("status") or {}
    dc = d.get("date_compact") or ""
    if not st.get("label") or len(dc) != 8:
        return ""
    txt = f"{dc[4:6]}/{dc[6:]} 主狀態：{st['label']}"
    up = (d.get("neckline") or {}).get("up") or {}
    if up.get("dist_pct") is not None:
        dist = _minus(format(up["dist_pct"], "+.2f"))
        txt += f"｜距多方頸線 {dist}%"
    vol = d.get("volume") or {}
    if vol.get("ratio20") is not None:
        txt += f"｜量比 20 {vol['ratio20']:.2f}"
    return txt


CATS = [
    ("AI 助理實測", "ai", "把 AI 助理真正做過的事記錄下來。", "全部影片"),
    ("股市觀察", "stock", "只用公開資料，把「熱門」拿去驗證；內容為觀察與記錄，不構成投資建議。", "全部觀察紀錄"),
    ("多益英文", "toeic", "題目全部自行撰寫、不使用官方試題；附中文詳解與音檔。", "全部題組"),
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
            bd = re.search(r'<div class="big">([^<]+)</div><div>上市個股上漲／下跌家數</div>', h)
            tw = f"{d[:4]}/{d[4:6]}/{d[6:]}"
            out.append(dict(date=tw, sort=(d, 3), category="股市觀察",
                            title=f"{tw} 收盤後觀察：{_txt(big.group(1)) if big else '-'}　{_txt(big.group(2)) if big else ''}",
                            url=f"stock/{d}/", btn="逐檔 K 線圖與線型分析（50 檔）→",
                            note=f"成交金額前 50 檔（上市 35＋上櫃 15）逐檔技術線型"
                                 + (f"；上市個股上漲／下跌 {_txt(bd.group(1))}。" if bd else "。")
                                 + "另有「好／不好條件最多」兩個排行榜。"))
        elif d.endswith("-intraday"):
            day = d[:8]
            sub = re.search(r'<div class="sub">([^<]+)</div>', h)
            snap = re.search(r"(\d{2}:\d{2}) 即時快照", _txt(sub.group(1)) if sub else "")
            bd = re.search(r'<div class="big">(\d+) / (\d+)</div><div>候選池', h)
            tw = f"{day[:4]}/{day[4:6]}/{day[6:]}"
            out.append(dict(date=tw, sort=(day, 1), category="股市觀察",
                            title=f"{tw} {snap.group(1) if snap else ''} 盤中快照",
                            url=f"stock/{d}/", btn="盤中逐檔快照 →",
                            note="當日盤中成交金額前 50 檔即時快照"
                                 + (f"，候選池內上漲／下跌 {bd.group(1)} / {bd.group(2)}" if bd else "")
                                 + "；含時程紀錄與「盤中 → 收盤」對照。盤中是快照、不是收盤定案。"))
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
                        title=v["title"], url=v["url"], btn="看影片 →", note=v.get("desc", "")))
    for a in getattr(mod, "ARTICLES", []):      # 報告類文章也算 AI 助理實測的內容
        d = a.get("date", "").replace("-", "/")
        out.append(dict(date=d, sort=(d.replace("/", ""), 3), category="AI 助理實測",   # 同日：報告排在影片前面（更新）
                        title=a["title"], url="ai/" + a["url"], btn="看報告 →", note=a.get("desc", "")))
    return out


def manifest_items():
    p = os.path.join(SITE, "latest_items.json")
    if not os.path.exists(p):
        return []
    out = []
    for v in json.load(open(p, encoding="utf-8")).get("items", []):
        d = v.get("date", "").replace("-", "/")
        out.append(dict(date=d, sort=(d.replace("/", ""), 2), category=v["category"],
                        title=v["title"], url=v["url"], btn=v.get("btn", "看內容 →"),
                        note=v.get("note", "")))
    return out


SECTION = """  <section id="{slug}">
    <h2><a class="h2link" href="{slug}/"><span class="dot"></span>{name}</a>
      <span class="more"><a href="{slug}/">{go}（{n}）→</a></span>
    </h2>
    <p class="hint">{note}</p>
{mkt}{card}{extra}
  </section>
"""

CARD = """    <div class="card">
      <span class="tag new">{tag}</span>
      <h3>{title}</h3>
      <p>{note}</p>
      <a class="btn" href="{url}">{btn}</a>{btn2}
    </div>"""

BODY = """<body>
<div class="wrap">
  <header>
    <h1>小R 頻道</h1>
    <div class="sub">影片索引 · 分類入口</div>
    <hr class="rule">
  </header>

{sections}
  <div class="foot">
    頻道：<a href="https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw">youtube.com/@小R-c4q</a>
  </div>
</div>
</body>
</html>
"""

EXTRA_CSS = """  /* 首頁：每個分類放最新 2 則 */
  section .hint{color:var(--soft);font-size:14.5px;margin:2px 0 10px}
  .same-day{font-size:13.5px;color:var(--soft);margin:6px 0 0}
  .same-day a{color:var(--blue)}
  /* 首頁：股市區塊的一行大盤狀態（由 market_screen.py 的快篩快照產生） */
  .mktline{font-size:14.5px;color:var(--blue);margin:2px 0 12px;line-height:1.6}
  .mktline .dim{color:var(--soft);font-size:13px}
  .foot{text-align:center;color:var(--soft);font-size:14px;margin-top:34px}
"""


def build():
    items = stock_items() + ai_items() + manifest_items()
    sections = []
    log = []
    for name, slug, note, go in CATS:
        mine = sorted([i for i in items if i["category"] == name], key=lambda x: x["sort"], reverse=True)
        if not mine:
            sections.append(SECTION.format(slug=slug, name=name, go=go, n=0, note=note,
                                           mkt="", card="", extra=""))
            continue
        pool = [i for i in mine if "-intraday" not in i["url"]] if name == "股市觀察" else mine
        top = (pool or mine)[:2]                         # 每個分類保留最新 2 則（股市：盤中快照不佔卡）
        cards = []
        for k, it in enumerate(top):
            cards.append(CARD.format(tag=("最新" if k == 0 else "近期"),
                                     title=html.escape(it["title"]), note=html.escape(it["note"]),
                                     url=it["url"], btn=it["btn"], btn2=""))
        card = chr(10).join(cards)
        extra = ""
        # 大盤狀態一行（股市區塊才有）：由 market_screen.py 的快篩快照產生，抓不到就不顯示
        mkt = ""
        if name == "股市觀察":
            line = market_line(top[0]["sort"][0])
            if line:
                mkt = (f'    <p class="mktline">大盤（加權指數）{html.escape(line)}'
                       '<span class="dim">　公開資料技術面統計，不構成投資建議</span></p>' + chr(10))
        # 盤中快照：不佔卡片，只在同一天的收盤紀錄下面給一行連結（同一天排在一起）
        if name == "股市觀察":
            want = {t["sort"][0] for t in top}
            intr = [i for i in mine if "-intraday" in i["url"] and i["sort"][0] in want]
            if intr:
                s0 = sorted(intr, key=lambda x: x["sort"], reverse=True)[0]
                extra = ('    <p class="same-day">同一天另有：'
                         f'<a href="{s0["url"]}">{html.escape(_txt(s0["title"])[5:])}</a></p>')
        sections.append(SECTION.format(slug=slug, name=name, go=go, n=len(mine), note=note,
                                       mkt=mkt, card=card, extra=extra))
        log.append((name, len(mine), " / ".join(t["title"] for t in top)))
    head = open(HEAD_FILE, encoding="utf-8").read()
    if "</style>" in head:
        head = head.replace("</style>", EXTRA_CSS + "</style>", 1)
    body = BODY.replace("{sections}", chr(10).join(sections))
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(head + body)
    print("首頁已產生：每個分類保留最新 2 則")
    for name, n, t in log:
        print("   ", name, "共", n, "則｜最新 2 則:", t[:70])


if __name__ == "__main__":
    build()
