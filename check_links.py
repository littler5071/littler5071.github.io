# -*- coding: utf-8 -*-
"""檢查 littler5071.github.io 的內部連結是否有 404（只檢查頁面 href，不抓圖片/資產）。"""
import re, subprocess, urllib.parse

BASE = "https://littler5071.github.io/"
START = ["", "stock/", "stock/logic/", "stock/20260916-intraday/", "stock/20260915/",
         "stock/20260915-intraday/", "stock/20260914/", "stock/20260911/",
         "toeic/", "toeic/guide/", "toeic/p2-sample/", "toeic/p3-full/",
         "ai/", "ai/exam/"]


def code_of(u):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-A", "Mozilla/5.0", u],
                       capture_output=True, text=True)
    return r.stdout.strip()


def html_of(u):
    r = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0", u], capture_output=True, text=True, errors="ignore")
    return r.stdout


seen, bad, queue = set(), [], [BASE + p for p in START]
while queue and len(seen) < 80:
    u = queue.pop(0)
    if u in seen:
        continue
    seen.add(u)
    c = code_of(u)
    if c != "200":
        bad.append((u, c))
        continue
    if not u.endswith("/") and not u.endswith(".html"):
        continue
    for ref in sorted(set(re.findall(r'href="([^"#]+)"', html_of(u)))):
        if ref.startswith(("http", "mailto:", "javascript:", "data:")):
            continue
        full = urllib.parse.urljoin(u, ref)
        if full.startswith(BASE) and full not in seen:
            queue.append(full)

print("檢查頁面數:", len(seen))
print("非 200:", bad if bad else "（沒有）")
print("清單:", *sorted(seen), sep="\n  ")
