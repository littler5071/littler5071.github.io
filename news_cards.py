# -*- coding: utf-8 -*-
"""新聞頁的資料小卡：美股四大指數（含 30 日迷你走勢圖）。

資料來源：Yahoo Finance chart API（3 個月日線），快取 1 小時。
用法：from news_cards import indices_box
"""
import html
import json
import re
import os
import subprocess
import time

SITE = "/home/littler5071/opencode/圖片生成/小R頻道_網站"
CACHE_DIR = os.path.join(SITE, "news", ".cache")

INDICES = [("^DJI", "道瓊"), ("^GSPC", "S&P 500"), ("^IXIC", "那斯達克"), ("^SOX", "費半")]

# 新聞濃縮【數字】會出現的標的：關鍵字 → Yahoo 代號／顯示名稱
INSTRUMENTS = [
    (("台股", "加權指數", "加權"), "^TWII", "台股加權"),
    (("新台幣", "台幣", "匯率"), "TWD=X", "美元兌台幣"),
    (("日圓", "日元"), "JPY=X", "美元兌日圓"),
    (("人民幣", "人民幣匯率"), "CNY=X", "美元兌人民幣"),
    (("道瓊",), "^DJI", "道瓊"),
    (("那斯達克", "那指"), "^IXIC", "那斯達克"),
    (("S&P", "標普"), "^GSPC", "S&P 500"),
    (("費半", "費城半導體"), "^SOX", "費半"),
    (("日經",), "^N225", "日經 225"),
    (("恆生", "恒生"), "^HSI", "恆生指數"),
    (("上證", "上証"), "000001.SS", "上證指數"),
    (("韓國", "KOSPI"), "^KS11", "韓國 KOSPI"),
    (("布蘭特", "原油", "油價"), "BZ=F", "布蘭特原油"),
    (("黃金",), "GC=F", "黃金"),
    (("比特幣", "BTC"), "BTC-USD", "比特幣"),
    (("美債", "殖利率"), "^TNX", "美 10 年殖利率"),
    (("美元指數",), "DX-Y.NYB", "美元指數"),
]


def fetch_series(symbol, days=30):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, symbol.replace("^", "") + ".json")
    try:
        if os.path.exists(path) and (time.time() - os.path.getmtime(path)) < 3600:
            return json.load(open(path, encoding="utf-8"))["series"]
    except Exception:
        pass
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + symbol.replace("^", "%5E") + "?range=3mo&interval=1d")
    try:
        r = subprocess.run(["curl", "-s", "-m", "30", "-A", "Mozilla/5.0", url], capture_output=True)
        j = json.loads(r.stdout.decode("utf-8", "ignore"))
        res = (j.get("chart") or {}).get("result") or []
        q = res[0]["indicators"]["quote"][0]
        ts, cl = res[0].get("timestamp") or [], q.get("close") or []
        ser = [[d, c] for d, c in zip(ts, cl) if c][-max(days, 5):]
        json.dump({"series": ser}, open(path, "w", encoding="utf-8"))
        return ser
    except Exception:
        return []


def spark_svg(closes, up):
    if len(closes) < 3:
        return ""
    w, h, pad = 108, 30, 2
    lo, hi = min(closes), max(closes)
    rng = (hi - lo) or 1
    pts = []
    for i, c in enumerate(closes):
        x = pad + i * (w - 2 * pad) / (len(closes) - 1)
        y = h - pad - (c - lo) / rng * (h - 2 * pad)
        pts.append("%.1f,%.1f" % (x, y))
    color = "#c2452d" if up else "#1f7a4d"
    return ('<svg class="spark" viewBox="0 0 %d %d" preserveAspectRatio="none" aria-hidden="true">'
            '<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
            'stroke-linejoin="round" stroke-linecap="round"/></svg>' % (w, h, " ".join(pts), color))


def _asof(ser):
    """最後一根 K 的日期（台北時間 M/D），讓卡片標示資料截止日。"""
    try:
        ts = ser[-1][0]
        import datetime
        d = datetime.datetime.utcfromtimestamp(ts + 8 * 3600)
        return f"截至 {d.month}/{d.day}"
    except Exception:
        return ""


def _card(name, ser):
    closes = [c for _, c in ser]
    last, prev = closes[-1], closes[-2]
    chg = (last / prev - 1) * 100 if prev else 0
    up = chg >= 0
    cls = "up" if up else "dn"
    arrow = "▲" if up else "▼"
    fmt = format(last, ",.2f") if last >= 100 else format(last, ",.3f")
    return ('<div class="idxcard"><div class="nm">%s</div><div class="px">%s</div>'
            '<div class="chg %s">%s%.2f%%</div>%s'
            '<div class="asof">%s</div></div>'
            % (html.escape(name), fmt, cls, arrow, abs(chg), spark_svg(closes, up), _asof(ser)))


NUM_RE = r"([0-9][0-9,]*\.?[0-9]*)\s*(?:點|美元|元|%)?"
CHG_RE = r"([+\-\u2212]?[0-9]+\.?[0-9]*)\s*%"


def parse_pair(text, keys):
    """從報告文字抓「關鍵字後的價格」與「百分比」。

    要避開的雜訊：日期（10/21）、月份（12月期）、以及漲跌百分比本身。
    規則：百分比＝後面緊接 % 的數字；價格＝第一個「有逗號或帶小數且後面不是 %」的數字。
    """
    for kw in keys:
        i = text.find(kw)
        while i >= 0:
            seg = text[i + len(kw): i + len(kw) + 46]
            # 只看到這一句為止（遇到句號／分號／換行就切掉），避免抓到別檔的數字
            for stop in ("。", "；", "\n", "｜", "|"):
                if stop in seg:
                    seg = seg.split(stop)[0]
            val = None
            chg = None
            for m in re.finditer(r"([0-9][0-9,]*\.?[0-9]*)\s*(%?)", seg):
                raw = m.group(1)
                is_pct = m.group(2) == "%"
                after = seg[m.end(): m.end() + 1]
                pre = seg[max(0, m.start() - 1):m.start()]
                neg = pre in ("-", "\u2212", "\uff0d", "+") and pre != "+"
                if is_pct:
                    if chg is None:
                        try:
                            chg = float(raw.replace(",", ""))
                            if neg:
                                chg = -chg
                        except ValueError:
                            pass
                    continue
                if "/" in seg[max(0, m.start() - 1): m.start() + len(raw) + 1]:
                    continue
                if after in ("月", "期", "年", "日"):
                    continue
                if val is None:
                    try:
                        v = float(raw.replace(",", ""))
                    except ValueError:
                        continue
                    if v >= 100 or "." in raw:
                        val = v
            if chg is None:
                mj = re.search(r"(升|漲|貶|跌)值?\s*([0-9.]+)\s*(角|分)", seg)
                if mj and val:
                    unit = 0.1 if mj.group(3) == "角" else 0.01
                    v = float(mj.group(2)) * unit / val * 100
                    chg = v if mj.group(1) in "升漲" else -v
            if val is not None or chg is not None:
                src = "angle" if chg is not None and not re.search(r"%", seg) else "pct"
                return val, chg, src
            i = text.find(kw, i + 1)
    return None, None, None


def digits_box(text, asof=None):
    """新聞濃縮【數字】段落 → 依出現順序比對標的，做成有走勢圖的小卡。"""
    if not text:
        return ""
    # 【數字】段落優先：「標普500跌1.82%」這種寫法會讓解析器把 500 當成價位
    i = text.find("【數字】")
    if i > 0:
        text = text[i:] + "\n" + text[:i]
    found = []
    for keys, sym, name in INSTRUMENTS:
        if any(k in text for k in keys) and sym not in [s for s, _, _ in found]:
            found.append((sym, name, keys))
    if not found:
        return ""
    cards = []
    for sym, name, keys in found[:8]:
        ser = fetch_series(sym, 30)
        if len(ser) < 3:
            continue
        closes = [c for _, c in ser]
        val, chg, src = parse_pair(text, keys)
        if val is None:
            val = closes[-1]
        if chg is None:
            chg = (closes[-1] / closes[-2] - 1) * 100
        # 文字裡的數值若比 Yahoo 最後一根新（Yahoo 常落後一日），把它補進線尾，
        # 這樣「卡片數字」與「走勢線終點」就一致
        if val is not None and abs(val - closes[-1]) > max(1e-6, abs(closes[-1]) * 1e-6):
            closes = closes + [val]
        if sym.endswith("=X") and src == "angle":
            # 「台幣升 1.29 角」是台幣升值 → 美元兌台幣是下跌，方向要反過來
            chg = -chg
        up = chg >= 0
        cls = "up" if up else "dn"
        arrow = "▲" if up else "▼"
        fmt = format(val, ",.2f") if val >= 100 else format(val, ",.3f")
        cards.append('<div class="idxcard"><div class="nm">%s</div><div class="px">%s</div>'
                     '<div class="chg %s">%s%.2f%%</div>%s'
                     '<div class="asof">%s</div></div>'
                     % (html.escape(name), fmt, cls, arrow, abs(chg),
                        spark_svg(closes, up), ("截至 " + asof[4:6] + "/" + asof[6:8]) if asof else _asof(ser)))
    if not cards:
        return ""
    return ('<section class="blk idxsec"><h3><span class="dt"></span>'
            '今日數字（近 30 個交易日）</h3>'
            '<div class="idxgrid">%s</div>'
            '<p class="note">數字取自報告本文；走勢線為近 30 個交易日收盤（Yahoo，可能落後一日）</p>'
            '</section>' % "".join(cards))


def indices_box():
    """四大指數卡：名稱、收盤、漲跌%、近 30 日走勢圖。"""
    cards = []
    for sym, name in INDICES:
        ser = fetch_series(sym, 30)
        if len(ser) < 3:
            continue
        closes = [c for _, c in ser]
        last, prev = closes[-1], closes[-2]
        chg = (last / prev - 1) * 100 if prev else 0
        up = chg >= 0
        cls = "up" if up else "dn"
        arrow = "▲" if up else "▼"
        cards.append(
            '<div class="idxcard">'
            '<div class="nm">%s</div>'
            '<div class="px">%s</div>'
            '<div class="chg %s">%s%.2f%%</div>'
            '%s'
            '</div>' % (html.escape(name), format(last, ",.2f"), cls, arrow, abs(chg),
                        spark_svg(closes, up)))
    if not cards:
        return ""
    return ('<section class="blk idxsec"><h3><span class="dt"></span>'
            '美股四大指數（近 30 個交易日）</h3>'
            '<div class="idxgrid">%s</div></section>' % "".join(cards))
