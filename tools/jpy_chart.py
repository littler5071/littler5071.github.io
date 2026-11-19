#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日幣兌台幣匯率趨勢圖（近 60 個交易日）

用法：python3 jpy_chart.py [YYYYMMDD]
輸出：news/digest/img/jpy_<date>.png，並印出相對路徑
資料：Yahoo Finance TWDJPY=X（1 TWD = X JPY），再倒數成 1 JPY = X TWD
"""
import io
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parents[1]
OUT_DIR = SITE / "news" / "digest" / "img"

W, H, S = 1200, 560, 3          # 邏輯尺寸與放大倍率
BG = (250, 249, 247)
GRID = (237, 233, 226)
AXIS = (150, 145, 138)
INK = (34, 32, 30)
SOFT = (120, 115, 108)
ACCENT = (194, 69, 45)          # 赤陶紅 #C2452D
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def fetch(days=90):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/TWDJPY=X?range={days}d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.loads(urllib.request.urlopen(req, timeout=25).read())
    r = d["chart"]["result"][0]
    ts = r["timestamp"]
    close = r["indicators"]["quote"][0]["close"]
    out = [(t, c) for t, c in zip(ts, close) if c]
    return out[-60:]


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT_B if bold else FONT, size * S)
    except Exception:
        return ImageFont.load_default()


def money(v):
    return f"{v:.4f}"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y%m%d")
    data = fetch()
    if len(data) < 10:
        print("資料不足", file=sys.stderr)
        return 1

    # 1 TWD = X JPY  →  1 JPY = 1/X TWD
    pts = [(datetime.fromtimestamp(t), 1.0 / c) for t, c in data]
    ys = [p[1] for p in pts]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.18 or 0.002
    lo, hi = lo - pad, hi + pad

    img = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(img, "RGBA")

    # 極淡點陣網格
    for y in range(0, H * S, 18 * S):
        for x in range(0, W * S, 18 * S):
            d.point((x, y), fill=(228, 223, 214))

    L, R, T, B = 90 * S, (W - 175) * S, 240 * S, (H - 78) * S

    def px(i):
        return L + (R - L) * i / (len(pts) - 1)

    def py(v):
        return B - (B - T) * (v - lo) / (hi - lo)

    # 水平參考線 + 右側刻度
    for k in range(4):
        v = lo + (hi - lo) * k / 3
        y = py(v)
        d.line([(L, y), (R, y)], fill=GRID, width=2 * S)
        d.text((R + 16 * S, y), money(v), font=font(26), fill=(96, 91, 84), anchor="lm")

    # 折線 + 淡面積
    poly = [(px(i), py(v)) for i, (_, v) in enumerate(pts)]
    d.polygon(poly + [(R, B), (L, B)], fill=(194, 69, 45, 20))
    d.line(poly, fill=ACCENT, width=3 * S, joint="curve")

    # 最後一點
    lx, ly = poly[-1]
    d.ellipse([lx - 7 * S, ly - 7 * S, lx + 7 * S, ly + 7 * S], fill=ACCENT)
    d.ellipse([lx - 3 * S, ly - 3 * S, lx + 3 * S, ly + 3 * S], fill=(255, 255, 255))

    # X 軸日期（起／中／末）
    for i in (0, len(pts) // 2, len(pts) - 1):
        t = pts[i][0].strftime("%m/%d")
        x = px(i)
        anchor = "lm" if i == 0 else ("rm" if i == len(pts) - 1 else "mm")
        d.text((x, B + 18 * S), t, font=font(26), fill=(104, 99, 92), anchor=anchor)

    # 左上角：最新值與期間變化（不寫圖表標題）
    last = ys[-1]
    chg = (ys[-1] / ys[0] - 1) * 100
    sign = "▲" if chg >= 0 else "▼"
    color = ACCENT if chg >= 0 else (34, 122, 90)
    d.text((L, 26 * S), "1 JPY =", font=font(24), fill=SOFT)
    d.text((L + 118 * S, 6 * S), f"{last:.4f}", font=font(56, True), fill=INK)
    d.text((L + 420 * S, 26 * S), "TWD", font=font(24), fill=SOFT)
    d.text((L, 196 * S), f"{sign}{abs(chg):.2f}%  近 60 個交易日", font=font(26, True), fill=color, anchor="lm")

    img = img.resize((W, H), Image.LANCZOS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"jpy_{stamp}.png"
    img.save(out, optimize=True)
    print(json.dumps({
        "png": f"img/jpy_{stamp}.png",
        "jpy_twd": round(last, 4),
        "twd_jpy": round(1 / last, 3),
        "chg_60d_pct": round(chg, 2),
        "as_of": pts[-1][0].strftime("%Y-%m-%d"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
