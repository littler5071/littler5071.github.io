# -*- coding: utf-8 -*-
"""本機檢查某頁的回跳功能是否完整。用法：python _check_bj.py toeic/p2-sample [期望每題按鈕數]"""
import re, sys, os

SITE = "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
rel = sys.argv[1].strip("/")
p = os.path.join(SITE, rel, "index.html")
h = open(p, encoding="utf-8").read()
implicit = int(sys.argv[2]) if len(sys.argv) > 2 else 0

btns = re.findall(r'class="backjump[^"]*"[^>]*\s*data-target="([^"]+)"', h, re.S)
targets = [t for t in btns if t != "scoring"]
n_scoring_id = h.count('id="scoring"')
n_jumpend = h.count("jumpend")
n_goto = h.count("gotoscore")
n_css = h.count("button.backjump")
n_flash = h.count("blkflash")
n_smooth = h.count("'smooth'")
n_to = h.count("}, 2000)")
n_hit = h.count("'hit'")
q_missing = [t for t in btns if t not in h]

print(rel + ": " + str(len(h)) + " chars")
print("  .backjump 按鈕總數 = " + str(len(btns)) + "（每題 " + str(len(targets)) + " ＋ 頁底 1）")
print("  頁底 data-target=scoring = " + str(sum(1 for t in btns if t == "scoring")))
print('  id="scoring" = ' + str(n_scoring_id))
print("  data-target 目標缺失 = " + str(q_missing))
print("  .jumpend = " + str(n_jumpend) + "   gotoscore = " + str(n_goto))
print("  button.backjump CSS = " + str(n_css) + "   blkflash = " + str(n_flash))
print("  'smooth' = " + str(n_smooth) + "   2000ms setTimeout = " + str(n_to) + "   'hit' = " + str(n_hit))
print("  hnav = " + str(h.count("hnav")) + "   counter.js = " + str(h.count("counter.js"))
      + "   quiz.js = " + str(h.count("quiz.js")) + "   viewsline = " + str(h.count("viewsline")))
if implicit:
    print("  期望每題按鈕 " + str(implicit) + " -> " + ("OK" if len(targets) == implicit else "MISMATCH"))
