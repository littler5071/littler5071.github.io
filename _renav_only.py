# -*- coding: utf-8 -*-
"""只對指定頁面重跑 add_site_nav.py 的注入邏輯（導覽列＋瀏覽次數），不動其他頁面。

用法：python _renav_only.py <rel1> [rel2 ...]     例如 toeic/p2-sample toeic/p3-full
（把 add_site_nav.py 的 glob 過濾成只剩指定頁面，所以 StatiCrypt 加密頁不會被碰到。）
"""
import glob, os, runpy, sys

SITE = "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
targets = {t.strip("/").replace("\\", "/") for t in sys.argv[1:]}
if not targets:
    raise SystemExit("need at least one page rel path")

_real_glob = glob.glob


def _filtered(pattern, **kw):
    out = []
    for p in _real_glob(pattern, **kw):
        rel = os.path.relpath(os.path.dirname(p), SITE).replace("\\", "/")
        if rel in targets:
            out.append(p)
    return out


glob.glob = _filtered
here = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["add_site_nav.py", SITE]          # add_site_nav 用 argv[1] 當網站根目錄
runpy.run_path(os.path.join(here, "add_site_nav.py"), run_name="__main__")
