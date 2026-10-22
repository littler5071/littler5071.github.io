# -*- coding: utf-8 -*-
"""新聞頁的資料小卡：美股四大指數（含 30 日迷你走勢圖）。

資料來源：Yahoo Finance chart API（3 個月日線），快取 1 小時。
用法：from news_cards import indices_box
"""
import html
import json
import os
import subprocess
import time

SITE = "/home/littler5071/opencode/圖片生成/小R頻道_網站"
CACHE_DIR = os.path.join(SITE, "news", ".cache")

INDICES = [("^DJI", "道瓊"), ("^GSPC", "S&P 500"), ("^IXIC", "那斯達克"), ("^SOX", "費半")]


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
