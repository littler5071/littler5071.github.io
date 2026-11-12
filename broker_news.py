# -*- coding: utf-8 -*-
"""外資評等／目標價新聞：抓 Google News RSS，輸出新聞頁要用的區塊。

用法（獨立測試）：
    python broker_news.py
"""
from __future__ import annotations

import html
import re
import subprocess
import urllib.parse
from datetime import datetime, timedelta, timezone

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
QUERIES = [
    "外資 目標價 台股",
    "外資 降評 台股",
    "外資 調升 目標價",
    "外資 目標價 調降",
    "投顧 升評 目標價",
    "外資 報告 目標價",
]
# 排除美股與 FactSet 自動稿
BAD = re.compile(
    r"-US|FactSet|Factset|美股|那斯達克|道瓊|標普|輝達|NVIDIA|NVDA|Coinbase|"
    r"CoreWeave|JBS|Venture Global|QLYS|Pershing|盤前|EPS預估", re.I)
BROKERS = ["大摩", "摩根", "高盛", "瑞銀", "花旗", "美銀", "野村", "里昂", "麥格理",
           "小摩", "巴克萊", "匯豐", "德意志", "大和", "日系", "美系", "亞系", "歐系"]


def _fetch(q: str) -> str:
    u = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(q)
         + "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
    cp = subprocess.run(["curl", "-s", "-m", "25", "-A", UA, u],
                        capture_output=True, text=True, timeout=40)
    return cp.stdout or ""


def _parse(xml: str) -> list[dict]:
    out = []
    for m in re.finditer(r"<item>(.*?)</item>", xml, re.S):
        blk = m.group(1)
        t = (re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", blk, re.S)
             or re.search(r"<title>(.*?)</title>", blk, re.S))
        lk = re.search(r"<link>(.*?)</link>", blk, re.S)
        pd = re.search(r"<pubDate>(.*?)</pubDate>", blk, re.S)
        src = re.search(r"<source[^>]*>(.*?)</source>", blk, re.S)
        if not (t and lk):
            continue
        try:
            when = (datetime.strptime(pd.group(1).strip(), "%a, %d %b %Y %H:%M:%S %Z")
                    .replace(tzinfo=timezone.utc)) if pd else None
        except Exception:
            when = None
        out.append({
            "title": re.sub(r"<[^>]+>", "", t.group(1)).strip(),
            "url": lk.group(1).strip(),
            "when": when,
            "source": re.sub(r"<[^>]+>", "", src.group(1)).strip() if src else "",
        })
    return out


def items(hours: int = 48, limit: int = 12) -> list[dict]:
    rows, seen = [], set()
    for q in QUERIES:
        for it in _parse(_fetch(q)):
            key = re.sub(r"\W", "", it["title"])[:24]
            if key in seen or BAD.search(it["title"]):
                continue
            seen.add(key)
            rows.append(it)
    now = datetime.now(timezone.utc)
    rows = [r for r in rows if r["when"] and (now - r["when"]) <= timedelta(hours=hours)]
    rows.sort(key=lambda r: r["when"], reverse=True)
    return rows[:limit]


def _clean_title(t: str) -> str:
    # Google News 標題常以「 - 媒體名」結尾，去掉重複
    return re.sub(r"\s*-\s*[^-]{2,20}$", "", t).strip()


def section_html(limit: int = 10, hours: int = 48) -> str:
    rows = items(hours=hours, limit=limit)
    if not rows:
        return ""
    lis = []
    tz_tw = timezone(timedelta(hours=8))
    for r in rows:
        tw = r["when"].astimezone(tz_tw).strftime("%m/%d %H:%M")
        title = html.escape(_clean_title(r["title"]))
        src = html.escape(r["source"]) if r["source"] else ""
        url = html.escape(r["url"], quote=True)
        meta = f'{tw}・{src}' if src else tw
        lis.append(
            f'<li><a href="{url}" target="_blank" rel="noopener">{title}</a>'
            f'<span class="src">{meta}</span></li>'
        )
    return (
        '<section class="blk">'
        '<h3><span class="dt"></span>外資評等與目標價（含原文連結）</h3>'
        '<ul class="brk">' + "".join(lis) + "</ul>"
        '<p class="brknote">資料來源：新聞媒體轉述外資報告；原始報告為券商客戶專屬，'
        '數字與評等請點連結確認。僅供資訊整理，不構成投資建議。</p>'
        "</section>"
    )


if __name__ == "__main__":
    rows = items(hours=72, limit=12)
    print(f"{len(rows)} 則")
    for r in rows:
        tw = r["when"].astimezone(timezone(timedelta(hours=8))).strftime("%m/%d %H:%M")
        print(f"{tw} | {r['source'][:10]:<10} | {_clean_title(r['title'])[:58]}")
        print("   ", r["url"][:100])
