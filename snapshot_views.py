# -*- coding: utf-8 -*-
"""把每頁的瀏覽次數抓下來存成 views_snapshot.json（服務倒掉時歷史還在）。

用法：python snapshot_views.py
"""
import glob, json, os, re, urllib.request, datetime

SITE = os.path.dirname(os.path.abspath(__file__))
NS = "littler5071-github-io"
API = "https://abacus.jasoncameron.dev/get/%s/%s"


def key_of(rel_dir):
    path = "/" if rel_dir == "." else "/" + rel_dir.replace(os.sep, "/") + "/"
    k = re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") or "root"
    return "p" + k if len(k) < 3 else k   # 與 counter.js 相同規則（abacus 要求 >=3）


def get(key):
    req = urllib.request.Request(API % (NS, key), headers={
        "User-Agent": "Mozilla/5.0", "Origin": "https://littler5071.github.io"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8")).get("value")
    except Exception:
        return None


out = {}
for p in sorted(glob.glob(os.path.join(SITE, "**", "index.html"), recursive=True)):
    rel = os.path.relpath(os.path.dirname(p), SITE)
    if rel.startswith(".."):
        continue
    out[rel.replace(os.sep, "/")] = get(key_of(rel))

f = os.path.join(SITE, "views_snapshot.json")
prev = {}
if os.path.exists(f):
    prev = json.load(open(f, encoding="utf-8")).get("pages", {})
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(dict(snapshot_at=now, service="abacus.jasoncameron.dev", pages=out),
          open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已寫出", f, "| 時間", now)
for k, v in out.items():
    d = (v or 0) - (prev.get(k) or 0)
    print(f"  {k or '(首頁)'} → {v}（較上次 +{d}）")
