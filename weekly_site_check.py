# -*- coding: utf-8 -*-
"""每週網站健檢：① 檢查全站連結 ② 抓每頁瀏覽次數並算本週增量 ③ 產生 Top 10 流量圖。
最後印出精簡報告 + 一行 MEDIA:（給 cron 的 agent 原樣附上）。

用法：python weekly_site_check.py
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

from PIL import Image, ImageDraw, ImageFont

SITE = r"D:\_Richard\OpenCode\圖片生成\小R頻道_網站"
PY = r"C:\Users\Summer\AppData\Local\hermes\venvs\video\Scripts\python.exe"
OUT = r"C:\Users\Summer\banner\ep_rpa\out\site_weekly"
SNAP = os.path.join(SITE, "views_snapshot.json")
HIST = os.path.join(OUT, "views_history.jsonl")

PAPER = (246, 241, 230)
DOTBG = (236, 230, 218)
INK = (74, 70, 64)
SOFT = (90, 84, 76)
LINE = (217, 209, 194)
BLUE = (54, 78, 112)
LEAF = (47, 143, 99)
RED = (191, 74, 58)
F_KAI = r"C:\Windows\Fonts\kaiu.ttf"
F_HEI = r"C:\Windows\Fonts\msjh.ttc"
F_HEIB = r"C:\Windows\Fonts\msjhbd.ttc"

os.makedirs(OUT, exist_ok=True)


def font(p, s):
    try:
        return ImageFont.truetype(p, s)
    except Exception:
        return ImageFont.load_default()


# ── ① 連結檢查
links_ok, links_total, links_bad = None, None, []
try:
    r = subprocess.run([PY, "-u", os.path.join(SITE, "check_links.py")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=SITE, timeout=900)
    outtxt = (r.stdout or "")
    m = re.search(r"檢查頁面數[:：]\s*(\d+)", outtxt)
    if m:
        links_total = int(m.group(1))
    if "非 200: （沒有）" in outtxt or "非 200：（沒有）" in outtxt:
        links_bad = []
        links_ok = True
    else:
        seg = outtxt.split("非 200:")[-1].split("清單:")[0]
        links_bad = re.findall(r"(https?://\S+)", seg)
        links_ok = not links_bad
except Exception as e:
    links_ok = None
    links_bad = ["檢查失敗: %s" % type(e).__name__]

# ── ② 瀏覽次數
views_now, deltas = {}, {}
try:
    subprocess.run([PY, "-u", os.path.join(SITE, "snapshot_views.py")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=SITE, timeout=600)
except Exception:
    pass

prev_pages, cur_pages, snap_at = {}, {}, ""
if os.path.exists(SNAP):
    try:
        d = json.load(open(SNAP, encoding="utf-8"))
        cur_pages = d.get("pages", {}) or {}
        snap_at = d.get("snapshot_at", "")
    except Exception:
        pass
# 上一週的歷史（自己累積，第一次跑沒有基準）
try:
    if os.path.exists(HIST):
        for line in open(HIST, encoding="utf-8"):
            line = line.strip()
            if line:
                prev_pages = json.loads(line).get("pages", {}) or {}
except Exception:
    pass

rows = []
for k, v in cur_pages.items():
    if v is None:
        continue
    pv = prev_pages.get(k)
    d = (v - pv) if isinstance(pv, int) else None
    rows.append(("(首頁)" if (k or "").strip() in ("", ".", "root") else k, int(v), d))
rows.sort(key=lambda x: -x[1])

# 寫入本週歷史（供下週算增量）
with open(HIST, "a", encoding="utf-8") as f:
    f.write(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M"),
                        "pages": {k: v for k, v in cur_pages.items() if v is not None}},
                       ensure_ascii=False) + "\n")

# ── ③ Top 10 圖
def draw_chart(rows, path):
    top = rows[:10]
    W = 1080
    PAD = 34
    ROW = 78
    H = 210 + len(top) * ROW + 70
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)
    for yy in range(0, H, 26):
        for xx in range(0, W, 26):
            dr.point((xx, yy), fill=DOTBG)
    f_t = font(F_KAI, 56)
    f_s = font(F_HEI, 30)
    f_n = font(F_HEIB, 36)
    f_l = font(F_HEI, 32)

    dr.text((PAD, PAD), "網站流量・本週 Top 10", font=f_t, fill=INK)
    dr.text((PAD, PAD + 76), "來源 abacus 計數器｜快照 %s" % (snap_at or "—"), font=f_s, fill=SOFT)
    dr.line([(PAD, PAD + 128), (W - PAD, PAD + 128)], fill=LINE, width=2)

    mx = max([r[1] for r in top] + [1])
    y = PAD + 156
    for name, v, d in top:
        dr.text((PAD, y), name[:22], font=f_l, fill=INK)
        barw = int((W - PAD * 2 - 220) * v / mx)
        dr.rounded_rectangle([PAD, y + 40, PAD + max(6, barw), y + 62], 10, fill=BLUE)
        num = "%d" % v
        if d:
            num += "  (+%d)" % d
        dr.text((W - PAD - dr.textlength(num, font=f_n), y + 8), num, font=f_n,
                fill=LEAF if d and d > 0 else SOFT)
        y += ROW
    dr.text((PAD, H - 52), "由 Hermes 產生｜每週自動執行", font=f_s, fill=SOFT)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", optimize=True)
    return path, img.size


chart = None
try:
    if rows:
        chart = draw_chart(rows, os.path.join(OUT, "site_top10_%s.png" % time.strftime("%Y%m%d")))
except Exception as e:
    sys.stderr.write("畫圖失敗: %s\n" % e)

# ── ④ 報告
print("網站週健檢 %s" % time.strftime("%Y/%m/%d"))
print()
if links_total is None:
    print("① 連結檢查：✗ 執行失敗")
elif links_ok:
    print("① 連結檢查：%d 頁全部正常 ✓" % links_total)
else:
    print("① 連結檢查：%d 頁中有 %d 個非 200 ✗" % (links_total, len(links_bad)))
    for u in links_bad[:10]:
        print("　✗ %s" % u)
print()
if rows:
    print("② 瀏覽次數（有數字的頁面共 %d 頁）：" % len(rows))
    for name, v, d in rows[:10]:
        print("　・%-26s %4d%s" % (name[:26], v, "（本週 +%d）" % d if d else ""))
    tot = sum(r[1] for r in rows)
    dtot = sum(r[2] for r in rows if r[2])
    print("　合計 %d 次%s" % (tot, "（本週 +%d）" % dtot if dtot else "（首次基準）"))
else:
    print("② 瀏覽次數：✗ 抓不到資料（計數服務可能掛了）")
print()
if chart:
    print("MEDIA:%s" % chart[0])
