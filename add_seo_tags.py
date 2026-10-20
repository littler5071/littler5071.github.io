# -*- coding: utf-8 -*-
"""幫頻道網站加上品牌 SEO 基礎建設（可重複執行，冪等）。

做四件事：
  1. 每一頁插入 canonical／Open Graph／Twitter 卡／JSON-LD（標記註解，重跑會先移除再插）
  2. 每一頁的 <title> 若沒有「小R頻道」就補上「｜小R頻道」（品牌字排名最基本的一步）
  3. 產生 sitemap.xml（列出所有頁面）
  4. 產生 robots.txt（指向 sitemap）

跳過：StatiCrypt 加密頁（ai/hdd-ai、private/demo）——它們的 head 被加密工具動過，不要碰。

用法：
  python add_seo_tags.py            # 實際寫入
  python add_seo_tags.py --dry      # 只看會改幾頁
"""
from __future__ import annotations

import html
import os
import re
import sys
import time

SITE_DIR = "/home/littler5071/opencode/圖片生成/小R頻道_網站"
BASE = "https://littler5071.github.io"
BRAND = "小R頻道"
YT = "https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw"
SKIP = {os.path.join("ai", "hdd-ai", "index.html"),
        os.path.join("private", "demo", "index.html")}

START = "<!-- hermes-seo -->"
END = "<!-- /hermes-seo -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\s*", re.S)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', re.S | re.I)


def pages(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
        if "index.html" in filenames:
            yield os.path.join(dirpath, "index.html")


def canon_for(root: str, path: str) -> str:
    rel = os.path.relpath(path, root).replace("\\", "/")
    rel = rel[:-len("index.html")]          # 去掉 index.html → 目錄網址
    if not rel.strip("/"):
        return BASE + "/"
    return BASE + "/" + rel.strip("/") + "/"


def seo_block(title: str, desc: str, url: str) -> str:
    t = html.escape(title, quote=True)
    d = html.escape(desc, quote=True)
    ld = (
        '{"@context":"https://schema.org","@type":"WebSite",'
        '"name":"%s","alternateName":["小R","小R頻道","小R 頻道","小R老師","xiaor"],'
        '"url":"%s/",'
        '"inLanguage":"zh-Hant",'
        '"publisher":{"@type":"Organization","name":"%s","alternateName":["小R頻道"],'
        '"url":"%s/","sameAs":["%s"]},'
        '"potentialAction":{"@type":"SearchAction",'
        '"target":"%s/search/?q={search_term_string}","query-input":"required name=search_term_string"}}'
        % (BRAND, BASE, BRAND, BASE, YT, BASE)
    )
    return "\n".join([
        START,
        '<link rel="canonical" href="%s">' % url,
        (('<meta name="google-site-verification" '
          'content="d0-UsEPQx4WsiLOHng08n2o5Qclmq8Fw9tbMgaxIkck">') if url == BASE + "/" else ""),
        '<meta name="keywords" content="小R頻道, 小R 頻道, 小R, 小R老師, xiaor, AI 助理實測, 股市觀察, 多益英文, 台股觀察">',
        '<meta property="og:site_name" content="%s">' % BRAND,
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="%s">' % t,
        '<meta property="og:description" content="%s">' % d,
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:locale" content="zh_TW">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % t,
        '<meta name="twitter:description" content="%s">' % d,
        '<script type="application/ld+json">%s</script>' % ld,
        END,
    ])


def main() -> None:
    dry = "--dry" in sys.argv
    root = SITE_DIR
    n_pages = n_titles = n_seo = 0
    urls = []
    for path in sorted(pages(root)):
        rel = os.path.relpath(path, root)
        if rel.replace("/", os.sep) in SKIP:
            print("  跳過（加密頁）：%s" % rel)
            continue
        src = open(path, encoding="utf-8", errors="replace").read()
        if "<head>" not in src or "</head>" not in src:
            continue
        n_pages += 1
        url = canon_for(root, path)
        urls.append(url)
        m = TITLE_RE.search(src)
        title = (m.group(1).strip() if m else BRAND)
        d = DESC_RE.search(src)
        desc = (d.group(1).strip() if d else "小R頻道的影片索引與實測報告。")
        new = src
        # 1) 標題補品牌
        if m and BRAND not in title:
            new_title = title + "｜" + BRAND
            new = new[:m.start()] + "<title>%s</title>" % new_title + new[m.end():]
            title = new_title
            n_titles += 1
        # 2) SEO 區塊（先移除舊的，再插到 </head> 前）
        new = BLOCK_RE.sub("", new)
        new = new.replace("</head>", seo_block(title, desc, url) + "\n</head>", 1)
        n_seo += 1
        if not dry and new != src:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

    # 3) sitemap.xml
    today = time.strftime("%Y-%m-%d")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, today))
    sm.append("</urlset>")
    sitemap = "\n".join(sm) + "\n"
    # 4) robots.txt
    robots = ("User-agent: *\nAllow: /\n\n"
              "Sitemap: %s/sitemap.xml\n" % BASE)

    if not dry:
        open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)
        open(os.path.join(root, "robots.txt"), "w", encoding="utf-8").write(robots)

    print("  頁面：%d（補品牌標題 %d 頁、加 SEO 區塊 %d 頁）" % (n_pages, n_titles, n_seo))
    print("  sitemap.xml：%d 個網址%s" % (len(urls), "（未寫入）" if dry else ""))
    print("  robots.txt：%s" % ("未寫入" if dry else "已寫入"))


if __name__ == "__main__":
    main()
