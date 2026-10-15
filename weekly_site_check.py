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

# ── 把路徑換成看得懂的標題（2026-10-15 加：使用者要求報告顯示文章標題）
_title_cache = {}


def page_title(key):
    """由計數器 key 反推頁面路徑，讀本機 HTML 的 <title>，去掉「｜小R頻道」尾巴。"""
    if key in _title_cache:
        return _title_cache[key]
    k = (key or "").strip()
    rel = "index.html" if k in ("", ".", "root") else k.strip("/") + "/index.html"
    cand = [os.path.join(SITE, rel)]
    if k not in ("", ".", "root"):
        cand.append(os.path.join(SITE, k.strip("/") + ".html"))
    title = None
    for p in cand:
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                head = f.read(4000)
            if "<title>" in head and "</title>" in head:
                t = head.split("<title>", 1)[1].split("</title>", 1)[0].strip()
                for suf in ("｜小R頻道", "|小R頻道", "｜小R 頻道", "|小R 頻道"):
                    if t.endswith(suf):
                        t = t[: -len(suf)].strip()
                title = t
                break
        except Exception:
            continue
    _title_cache[key] = title or key
    return _title_cache[key]


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
        lbl = page_title(name)
        dr.text((PAD, y), lbl[:22], font=f_l, fill=INK)
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
        shown = page_title(name)
        suffix = "" if shown == name else "（%s）" % name
        print("　・%s %s%4d%s" % (shown[:34], suffix, v, "（本週 +%d）" % d if d else ""))
    tot = sum(r[1] for r in rows)
    dtot = sum(r[2] for r in rows if r[2])
    print("　合計 %d 次%s" % (tot, "（本週 +%d）" % dtot if dtot else "（首次基準）"))
else:
    print("② 瀏覽次數：✗ 抓不到資料（計數服務可能掛了）")
print()

# ── ③ 內容完整性（2026-10-12 加：防止排程改版把該有的卡片洗掉、或把區塊順序改跑掉）
def check_content():
    """檢查線上關鍵卡片與區塊順序。這些東西以前是手動補的 HTML，會被每日排程洗掉。"""
    import urllib.request
    UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141.0"}
    problems = []

    def fetch(url):
        req = urllib.request.Request(url + "?cb=%d" % int(time.time()), headers=UA)
        return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

    try:
        s = fetch("https://littler5071.github.io/stock/")
        if 'href="backtest/"' not in s:
            problems.append("股市觀察頁少了「訊號回測」卡片（href=\"backtest/\"）")
        if 'href="logic/"' not in s:
            problems.append("股市觀察頁少了「技術分析邏輯」卡片（href=\"logic/\"）")
        p_fang = s.find('<h2><span class="dot"></span>方法必讀')
        p_day = s.find('<h2><span class="dot"></span>每日觀察紀錄')
        if p_fang < 0:
            problems.append("股市觀察頁找不到「方法必讀」區塊標題")
        elif p_day > 0 and p_fang > p_day:
            problems.append("「方法必讀」被排到日報卡片後面（順序錯了：應在每日觀察紀錄之前）")
    except Exception as e:
        problems.append("抓股市觀察頁失敗: %s: %s" % (type(e).__name__, str(e)[:60]))

    try:
        h = fetch("https://littler5071.github.io/")
        if "stock/backtest/" not in h:
            problems.append("首頁少了「訊號回測」卡片（stock/backtest/）")
    except Exception as e:
        problems.append("抓首頁失敗: %s: %s" % (type(e).__name__, str(e)[:60]))

    return problems


content_bad = check_content()
if content_bad:
    print("③ 內容完整性：✗ 有 %d 項不對" % len(content_bad))
    for p in content_bad:
        print("　✗ %s" % p)
else:
    print("③ 內容完整性：關鍵卡片都在、區塊順序正確 ✓")
print()

if chart:
    print("MEDIA:%s" % chart[0])
