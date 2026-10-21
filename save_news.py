# -*- coding: utf-8 -*-
"""把「美股晨報」與「每日新聞濃縮」放上網站固定網址。

來源：Hermes cron 的執行紀錄
  ~/.hermes/cron/output/4853741fcfcc/*.md  → 美股晨報
  ~/.hermes/cron/output/c18726bc495b/*.md  → 每日新聞濃縮
輸出：
  <site>/news/us/index.html            （固定網址，永遠是最新一份）
  <site>/news/us/<YYYYMMDD>.html       （單日頁）
  <site>/news/digest/index.html
  <site>/news/digest/<YYYYMMDD>.html
  <site>/news/index.html               （兩邊的入口）

用法：
  python save_news.py --all          # 兩邊都處理（預設，可重跑）
  python save_news.py us             # 只處理美股晨報
  python save_news.py digest --push  # 處理完順便 commit + push
  python save_news.py --all --limit 30
"""
import argparse
import glob
import html
import os
import re
import subprocess
import sys

SITE = "/home/littler5071/opencode/圖片生成/小R頻道_網站"
OUTPUT = os.path.expanduser("~/.hermes/cron/output")

KINDS = {
    "us": {
        "job": "4853741fcfcc",
        "title": "美股晨報",
        "sub": "上一個美股交易日的四大指數、強弱族群、三件後續消息與對台股的影響",
        "dir": "us",
    },
    "digest": {
        "job": "c18726bc495b",
        "title": "每日新聞濃縮",
        "sub": "台灣與國際新聞濃縮，含關鍵數字",
        "dir": "digest",
    },
}


def response_of(md_path):
    """從 cron 紀錄取出「## Response」之後的正文。"""
    txt = open(md_path, encoding="utf-8", errors="ignore").read()
    m = re.search(r"^## Response\s*$(.*)\Z", txt, re.S | re.M)
    body = (m.group(1) if m else "").strip()
    if not body or body in ("[SILENT]",):
        return None
    if body.startswith("[CRON_FAILURE]"):
        return None
    return body


def date_of(md_path):
    """檔名 2026-10-22_07-01-52.md → 20261022"""
    b = os.path.basename(md_path)
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})_", b)
    return f"{m.group(1)}{m.group(2)}{m.group(3)}" if m else None


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def to_html(md):
    out = []
    for line in md.splitlines():
        t = line.strip()
        if not t:
            continue
        if t.startswith("### "):
            out.append(f"<h3>{inline(t[4:])}</h3>")
        elif t.startswith("## "):
            out.append(f"<h3>{inline(t[3:])}</h3>")
        elif t.startswith("# "):
            out.append(f"<h2>{inline(t[2:])}</h2>")
        elif re.match(r"^[・•\-]\s*", t):
            out.append(f"<p class='li'>・{inline(re.sub(r'^[・•\-]\s*', '', t))}</p>")
        elif re.match(r"^\d+[.)]\s*", t):
            out.append(f"<p class='li'>{inline(t)}</p>")
        else:
            out.append(f"<p>{inline(t)}</p>")
    return "\n".join(out)


CSS = """
  .wrap{max-width:820px;margin:0 auto;padding:0 18px 40px}
  h1{font-size:clamp(22px,4vw,30px);line-height:1.35;margin:18px 0 6px}
  .meta{color:var(--soft);font-size:14px;margin-bottom:16px}
  .body p{font-size:16.5px;line-height:1.85;margin:8px 0}
  .body p.li{padding-left:6px}
  .body h3{font-size:18px;margin:22px 0 6px}
  .body b{color:var(--ink)}
  .body code{background:#f3efe4;padding:1px 5px;border-radius:5px;font-size:15px}
  .arch{margin-top:34px;border-top:2px dashed #d9d1c2;padding-top:14px}
  .arch h3{font-size:16px;color:var(--soft);font-weight:400;margin:0 0 8px}
  .arch a{display:inline-block;margin:0 10px 8px 0;font-size:14.5px;color:var(--blue);text-decoration:none;border-bottom:1.5px solid currentColor}
  a.back{display:inline-block;margin:14px 0 0;font-size:14.5px;text-decoration:none;color:var(--blue);border-bottom:1.5px solid currentColor}
"""


def nav_tags():
    """沿用全站現用的 nav.css／nav.js 版本化標籤（沒有就退回無版本）。"""
    try:
        head = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
        css = re.search(r'<link rel="stylesheet" href="[^"]*nav\.css[^"]*">', head)
        js = re.search(r'<script defer src="[^"]*nav\.js[^"]*"></script>', head)
        out = []
        if css:
            out.append(css.group(0).replace('href="', 'href="/').replace('href="//', 'href="/'))
        if js:
            out.append(js.group(0).replace('src="', 'src="/').replace('src="//', 'src="/'))
        if out:
            return "\n".join(out)
    except Exception:
        pass
    return '<link rel="stylesheet" href="/nav.css">\n<script defer src="/nav.js"></script>'


def page(title, heading, meta, body_html, archive, canonical):
    links = "".join(f'<a href="{d}.html">{d[:4]}/{d[4:6]}/{d[6:]}</a>' for d in archive)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}｜小R頻道</title>
<link rel="stylesheet" href="/css/index.css">
{nav_tags()}
<style>{CSS}</style>
<link rel="canonical" href="{canonical}">
</head>
<body>
<div class="wrap">
<h1>{html.escape(heading)}</h1>
<div class="meta">{html.escape(meta)}</div>
<div class="body">
{body_html}
</div>
<div class="arch">
<h3>歷期</h3>
{links}
</div>
<a class="back" href="/news/">← 回新聞首頁</a>
</div>
</body>
</html>
"""


def collect(kind, limit):
    cfg = KINDS[kind]
    files = sorted(glob.glob(os.path.join(OUTPUT, cfg["job"], "*.md")))
    seen, items = set(), []
    for f in reversed(files):
        d = date_of(f)
        if not d or d in seen:
            continue
        body = response_of(f)
        if not body:
            continue
        seen.add(d)
        items.append((d, body))
        if len(items) >= limit:
            break
    return items


def build(kind, limit):
    cfg = KINDS[kind]
    items = collect(kind, limit)
    if not items:
        print(f"[{kind}] 沒有可用的報告")
        return False
    outdir = os.path.join(SITE, "news", cfg["dir"])
    os.makedirs(outdir, exist_ok=True)
    dates = [d for d, _ in items]
    for d, body in items:
        ymd = f"{d[:4]}/{d[4:6]}/{d[6:]}"
        html_doc = page(f"{cfg['title']} {ymd}", f"{cfg['title']} {ymd}", cfg["sub"],
                        to_html(body), dates,
                        f"https://littler5071.github.io/news/{cfg['dir']}/{d}.html")
        open(os.path.join(outdir, f"{d}.html"), "w", encoding="utf-8").write(html_doc)
    latest_date, latest_body = items[0]
    ymd = f"{latest_date[:4]}/{latest_date[4:6]}/{latest_date[6:]}"
    html_doc = page(f"{cfg['title']}｜最新", f"{cfg['title']} {ymd}", cfg["sub"],
                    to_html(latest_body), dates,
                    f"https://littler5071.github.io/news/{cfg['dir']}/")
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(html_doc)
    print(f"[{kind}] 產出 {len(items)} 期，最新 {latest_date}")
    return True


def build_hub():
    cards = []
    for kind, cfg in KINDS.items():
        items = collect(kind, 1)
        latest = items[0][0] if items else None
        when = f"{latest[:4]}/{latest[4:6]}/{latest[6:]}" if latest else "尚無資料"
        cards.append(f"""<div class="card">
  <h2>{html.escape(cfg['title'])}</h2>
  <p class="dim">{html.escape(cfg['sub'])}</p>
  <p class="dim">最新：{when}</p>
  <a class="btn" href="/news/{cfg['dir']}/">看最新 →</a>
</div>""")
    doc = f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>新聞與晨報｜小R頻道</title>
<link rel="stylesheet" href="/css/index.css">
{nav_tags()}
<style>
 .wrap{{max-width:900px;margin:0 auto;padding:0 18px 40px}}
 .card{{background:#fffdf6;border:2px solid var(--line);border-radius:16px;padding:16px 18px;margin:14px 0}}
 .card h2{{font-size:20px;margin:0 0 4px}}
 .dim{{color:var(--soft);font-size:14px;margin:4px 0}}
 .btn{{display:inline-block;margin-top:8px;font-size:15px;color:var(--blue);text-decoration:none;border-bottom:1.5px solid currentColor}}
</style></head><body><div class="wrap">
<h1>新聞與晨報</h1>
<p class="dim">固定網址，每天更新；舊的留在底下「歷期」。</p>
{''.join(cards)}
</div></body></html>"""
    os.makedirs(os.path.join(SITE, "news"), exist_ok=True)
    open(os.path.join(SITE, "news", "index.html"), "w", encoding="utf-8").write(doc)
    print("[hub] news/index.html")


def push():
    cmds = [
        ["git", "add", "-A"],
        ["git", "-c", "user.name=littler5071", "-c", "user.email=little.r5071@gmail.com",
         "commit", "-q", "-m", "新聞：更新美股晨報／每日新聞濃縮頁"],
        ["git", "push", "-q", "origin", "main"],
    ]
    for c in cmds:
        r = subprocess.run(c, cwd=SITE, capture_output=True, text=True)
        if r.returncode != 0 and "無變更" not in (r.stdout + r.stderr):
            print("git:", c[0], r.returncode, (r.stderr or r.stdout)[:200])
    print("已推送")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", nargs="?", default="all", choices=["all", "us", "digest"])
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()
    kinds = list(KINDS) if args.kind == "all" else [args.kind]
    ok = False
    for k in kinds:
        ok = build(k, args.limit) or ok
    build_hub()
    if args.push:
        push()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
