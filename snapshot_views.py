# -*- coding: utf-8 -*-
"""把每頁的瀏覽次數抓下來存成 views_snapshot.json（服務倒掉時歷史還在）。

用法：
    python snapshot_views.py               # 抓數字並寫檔（排程／週健檢用）
    python snapshot_views.py --dry         # 只印結果、不寫檔（驗收用）
    python snapshot_views.py --dry --only stock   # 只抓路徑含 stock 的頁（少量測試用）

計數服務（abacus）會偶發超時或 500，而 `add_site_nav.py` 是拿這份快照當
`data-views-fallback`：某頁這次抓不到（None）就會被注入成「沒有 fallback 屬性」→
服務出錯時 counter.js 會把整行瀏覽次數收起來（使用者就會回報「這頁少了瀏覽數統計」）。
所以這裡有兩層防護：
  1. 每次抓取重試多次（服務偶發超時，重試就過）。
  2. 重試都失敗時**沿用上次快照裡的好數字**，不要把已經有值的頁面洗成 None。
（abacus 對「從來沒人看過」的 key 會回 Key not found → 這仍然是 None，不沿用。）
另外：週健檢的「本週 +N」也是比這份快照的前後兩版，沿用舊值可以避免把抓取失敗
誤算成一整批負成長。
"""
import glob, json, os, re, sys, time, urllib.request, datetime

SITE = os.path.dirname(os.path.abspath(__file__))
NS = "littler5071-github-io"
API = "https://abacus.jasoncameron.dev/get/%s/%s"
TRIES = 4
FAIL = None  # 佔位說明：失敗時回傳字串 "FAIL"，None 代表服務明確回答「Key not found」


def key_of(rel_dir):
    path = "/" if rel_dir == "." else "/" + rel_dir.replace(os.sep, "/") + "/"
    k = re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") or "root"
    return "p" + k if len(k) < 3 else k   # 與 counter.js 相同規則（abacus 要求 >=3）


def get(key, tries=TRIES):
    """回傳數字、或 None（Key not found＝真的沒人看過）、或 "FAIL"（服務不通）。"""
    req = urllib.request.Request(API % (NS, key), headers={
        "User-Agent": "Mozilla/5.0", "Origin": "https://littler5071.github.io"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode("utf-8"))
                return d.get("value")          # Key not found → 這裡就是 None
        except Exception:
            if i < tries - 1:
                time.sleep(2 * (i + 1))
    return "FAIL"


def snapshot(site=SITE, dry=False, only=None, tries=TRIES):
    f = os.path.join(site, "views_snapshot.json")
    prev = {}
    if os.path.exists(f):
        prev = json.load(open(f, encoding="utf-8")).get("pages", {})

    out, carried, failed = {}, [], []
    for p in sorted(glob.glob(os.path.join(site, "**", "index.html"), recursive=True)):
        rel = os.path.relpath(os.path.dirname(p), site)
        if rel.startswith(".."):
            continue
        rel = rel.replace(os.sep, "/")
        if only and only not in rel:
            continue
        v = get(key_of(rel), tries=tries)
        if v == "FAIL":
            if prev.get(rel) is not None:      # 沿用上次的好數字，不要把 fallback 洗掉
                v = prev[rel]
                carried.append(rel)
            else:
                v = None
                failed.append(rel)
        out[rel] = v

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("頁數 %d｜沿用上次數字 %d｜完全抓不到 %d｜%s"
          % (len(out), len(carried), len(failed), "（--dry，未寫檔）" if dry else ""))
    for r in carried:
        print("  沿用:", r, "→", out[r])
    for r in failed:
        print("  抓不到:", r, "（上一次快照也沒有值）")

    if not dry:
        json.dump(dict(snapshot_at=now, service="abacus.jasoncameron.dev", pages=out),
                  open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已寫出", f, "| 時間", now)
        for k, v in out.items():
            d = (v or 0) - (prev.get(k) or 0)
            print(f"  {k or '(首頁)'} → {v}（較上次 +{d}）")
    return out


def main(argv):
    only = None
    for a in argv:
        if a.startswith("--only="):
            only = a.split("=", 1)[1]
        elif a == "--only":
            i = argv.index(a)
            only = argv[i + 1] if len(argv) > i + 1 else None
    snapshot(dry="--dry" in argv, only=only)


if __name__ == "__main__":
    main(sys.argv[1:])
