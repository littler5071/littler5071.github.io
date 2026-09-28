# -*- coding: utf-8 -*-
"""產生 code/rpa-demo/index.html：「RPAHelper 播放示範：20 開啟 Excel 並輸入資料」

內容全部由程式產生：
  - 步驟表：直接讀腳本 JSON（43 個動作，標示型別與啟用狀態）
  - 內嵌示範動畫（mp4 放在同目錄，由 make_rpa_demo.py 產出後複製過來）
用法：python build_code_rpa_demo.py [網站根目錄]
"""
import io
import json
import os
import shutil
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
SRC = r"D:\_Richard\OpenCode\RPA工具\publish\Scripts\Demos\20_開啟Excel並輸入資料.rpa.json"
VIDEO_SRC = r"C:\Users\Summer\banner\ep_rpa\out\rpa_demo_20.mp4"          # 逐步動畫
REAL_SRC = r"C:\Users\Summer\banner\ep_rpa\out\rpa_demo_real.mp4"        # 實際操作錄影＋旁白
SRC21 = r"D:\_Richard\OpenCode\RPA工具\publish\Scripts\Demos\21_開啟Notepad並模擬從excel複製多筆資料貼上.rpa.json"
VIDEO21_SRC = r"C:\Users\Summer\banner\ep_rpa\out\rpa_demo_21.mp4"       # 範例 21 實際錄影＋旁白

TYPE = {0: "滑鼠移動", 1: "滑鼠按鍵", 2: "滑鼠滾輪", 3: "鍵盤按鍵", 4: "文字輸入", 5: "找圖點擊",
        6: "切換視窗", 7: "巨集引用", 8: "固定等待", 32: "隨機等待", 10: "等待視窗",
        30: "等待視窗關閉", 11: "等待圖片", 31: "等待程序", 9: "啟動程式", 23: "執行外部程式",
        27: "停止播放", 13: "設定變數", 14: "設定剪貼簿", 15: "正規式解析", 24: "讀取檔案",
        25: "寫入檔案", 16: "條件判斷", 17: "跳躍", 18: "標籤", 19: "迴圈起點", 20: "迴圈終點",
        21: "跳出迴圈", 22: "下一輪", 12: "註解", 26: "顯示訊息", 28: "輸入法", 29: "視窗操作",
        33: "螢幕擷取"}
WM = {0: "完全相同", 1: "包含關鍵字", 2: "正規式", 3: "行程名稱"}
KEYS = {13: "Enter", 9: "Tab", 27: "Esc", 91: "Win", 32: "Space"}


def h(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def detail(a):
    t = a.get("Type")
    if t == 3:
        return "按鍵 %s" % KEYS.get(a.get("VkCode"), "VK %s" % a.get("VkCode"))
    if t == 4:
        return "輸入「%s」" % h(a.get("Text") or "")
    if t == 23:
        return "啟動 %s（不等待）" % h(a.get("RunFileName") or "")
    if t == 7:
        return "執行巨集：%s" % h(a.get("MacroName") or "")
    if t == 1:
        return "%s (%s, %s)" % ("雙擊" if a.get("IsDoubleClick") else "點擊",
                                a.get("X"), a.get("Y"))
    if t == 8:
        return "等待 %s ms" % a.get("WaitMs")
    if t == 10:
        return "等到「%s」（%s）逾時 %s ms" % (h(a.get("WindowTitle")),
                                              WM.get(a.get("WindowMatchMode")), a.get("TimeoutMs"))
    if t == 13:
        vs = a.get("ValueSource")
        src = {15: "亂數", 19: "目前播放的輪數", 1: "剪貼簿", 0: "文字"}.get(vs, "來源 %s" % vs)
        return "變數「%s」← %s" % (h(a.get("VariableName")), src)
    if t == 19:
        return "For %s..%s（每輪把索引寫入「%s」）" % (a.get("LoopFrom"), a.get("LoopTo"),
                                                    h(a.get("LoopVariable")))
    if t == 20:
        return "迴圈結束"
    if t == 28:
        return "切換輸入法"
    if t == 27:
        return "結束播放（標示為%s）" % ("成功" if a.get("StopIsSuccess") else "失敗")
    if t == 12:
        return h((a.get("Note") or "").lstrip("/ "))
    return ""


def main():
    d = json.load(io.open(SRC, encoding="utf-8"))
    A = d["Actions"]
    n_tot = len(A)
    n_en = sum(1 for a in A if a.get("Enabled", True))
    n_com = sum(1 for a in A if a.get("Type") == 12)
    n_eff = sum(1 for a in A if a.get("Enabled", True) and a.get("Type") != 12)

    rows = []
    for i, a in enumerate(A, 1):
        en = a.get("Enabled", True)
        cls = ' class="off"' if not en else ""
        rows.append('    <tr%s><td class="num">%d</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                    % (cls, i, TYPE.get(a.get("Type"), "?"), detail(a),
                       "啟用" if en else "停用"))
    rows = "\n".join(rows)

    out = os.path.join(SITE, "code", "rpa-demo")
    os.makedirs(out, exist_ok=True)
    if os.path.exists(VIDEO_SRC):
        shutil.copy2(VIDEO_SRC, os.path.join(out, "demo.mp4"))
        print("動畫複製：", os.path.getsize(VIDEO_SRC), "bytes")
    else:
        print("⚠ 找不到動畫：", VIDEO_SRC)
    if os.path.exists(REAL_SRC):
        shutil.copy2(REAL_SRC, os.path.join(out, "real-run.mp4"))
        print("實際錄影複製：", os.path.getsize(REAL_SRC), "bytes")
    else:
        print("⚠ 找不到實際錄影：", REAL_SRC)
    if os.path.exists(VIDEO21_SRC):
        shutil.copy2(VIDEO21_SRC, os.path.join(out, "ex21.mp4"))
        print("範例21錄影複製：", os.path.getsize(VIDEO21_SRC), "bytes")
    else:
        print("⚠ 找不到範例21錄影：", VIDEO21_SRC)

    # 範例 21 的步驟表（同樣由腳本檔產生）
    d21 = json.load(io.open(SRC21, encoding="utf-8"))
    A21 = d21["Actions"]
    n21 = len(A21)
    n21en = sum(1 for a in A21 if a.get("Enabled", True))
    n21eff = sum(1 for a in A21 if a.get("Enabled", True) and a.get("Type") != 12)
    rows21 = []
    for i, a in enumerate(A21, 1):
        en = a.get("Enabled", True)
        cls = ' class="off"' if not en else ""
        rows21.append('    <tr%s><td class="num">%d</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                      % (cls, i, TYPE.get(a.get("Type"), "?"), detail(a),
                         "啟用" if en else "停用"))
    rows21 = "\n".join(rows21)

    HTML = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>不用寫程式，讓電腦自己開 Excel、填資料、再貼進記事本｜程式設計｜小R 頻道</title>
<meta name="description" content="兩支腳本的實際操作錄影：一支讓電腦自己開啟 Excel、輸入四筆資料；另一支把 Excel 的資料一筆一筆複製貼進記事本。同一套做法換掉目標程式，就能貼進別的應用程式或網頁表單。附兩支腳本的完整步驟表。">
<style>
  :root{--paper:#f6f1e6;--ink:#4a4640;--soft:#78706a;--line:#d9d1c2;--red:#bf4a3a;
        --blue:#364e70;--leaf:#2f8f63;--card:#fffdf6}
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);line-height:1.8;
    font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif;
    background-image:radial-gradient(rgba(0,0,0,.035) 1px,transparent 1px);background-size:26px 26px}
  .wrap{max-width:900px;margin:0 auto;padding:38px 20px 80px}
  a.back{display:inline-block;margin-bottom:8px;font-size:14.5px;text-decoration:none;
         border-bottom:1.5px solid currentColor;color:var(--blue)}
  h1{font-size:clamp(24px,4.4vw,34px);margin:8px 0 6px;text-align:center;line-height:1.4}
  .sub{text-align:center;color:var(--blue);margin-bottom:6px}
  .meta{text-align:center;color:var(--soft);font-size:13.5px;margin-bottom:20px}
  h2{font-size:clamp(19px,3.3vw,25px);margin:36px 0 12px;display:flex;align-items:center;gap:10px;line-height:1.4}
  h2 .dot{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}
  .box{background:var(--card);border:2px solid var(--line);border-radius:16px;padding:18px 20px;
       margin:0 0 18px;box-shadow:2px 3px 0 rgba(74,70,64,.06)}
  .box.red{border-color:#e6c3bc;background:#fdf6f4}
  .box.green{border-color:#bfdccd;background:#f4fbf7}
  video{width:100%;border:2px solid var(--line);border-radius:14px;background:#000;display:block}
  ul.plain,ol.plain{margin:8px 0;padding-left:22px}
  ul.plain li,ol.plain li{margin:6px 0}
  .scroll{overflow-x:auto;margin:12px 0}
  table{width:100%;border-collapse:collapse;font-size:14.5px;min-width:560px}
  th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}
  td.num{white-space:nowrap;color:var(--soft);width:56px}
  tr.off td{color:#a9a29a}
  .note{margin-top:34px;padding:15px 18px;border:2px dashed var(--line);border-radius:14px;
        color:var(--soft);font-size:14px;background:rgba(255,253,246,.6)}
  footer{margin-top:30px;text-align:center;color:var(--soft);font-size:13.5px}
  a{color:var(--blue)}
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="../">← 回程式設計</a>
  <a class="back" style="margin-left:14px" href="../../">← 回影片索引</a>

  <h1>不用寫程式，<br>讓電腦自己開 Excel、填資料、再貼進記事本</h1>
  <div class="sub">兩支腳本的實際操作錄影：錄一次，之後它自己做完</div>
  <div class="meta">__DATE__・實際操作錄影＋完整步驟解析</div>

  <div class="box">
    <b>兩個範例的關係：</b>範例 20 把資料打進 Excel，示範的是「開啟程式、等到視窗出現、用迴圈產生每一筆」；
    範例 21 接著把 Excel 裡的資料<b>一筆一筆複製貼到另一個程式</b>（這裡是記事本），
    做法對任何能貼上的地方都通用——其他應用程式、網頁表單都一樣。
    兩支腳本都沒有寫任何程式碼，是「錄製一次」加幾步流程控制組起來的。
  </div>

  <h2><span class="dot"></span>實際操作錄影</h2>
  <video controls preload="metadata">
    <source src="real-run.mp4" type="video/mp4">
    你的瀏覽器不支援影片播放，<a href="real-run.mp4">點此下載</a>。
  </video>
  <div class="note" style="margin-top:14px">
    這段是<b>真的跑一遍的螢幕錄影</b>：先看工具裡載入的這支腳本與它的步驟，按播放之後畫面切到 Excel，
    表頭與三列資料被一列一列打進去。錄影從整台桌面擷取，所以有幾處處理：
    <br>・<b>開頭那幾秒切掉了</b>——腳本會按 Win 鍵搜尋應用程式，那個畫面會列出最近用過的檔案（含本機檔名），不適合公開。
    <br>・<b>畫面頂端裁掉一條</b>——Office 的標題列會顯示登入的帳號名稱。
    <br>・螢幕是 1920×1080 但系統縮放 150%，所以錄下來的實際像素是 1920×1080（不是某些程式回報的 1280×720）。
  </div>

  <h2><span class="dot"></span>逐步動畫（含每一句說明）</h2>
  <video controls preload="metadata">
    <source src="demo.mp4" type="video/mp4">
    你的瀏覽器不支援影片播放，<a href="demo.mp4">點此下載</a>。
  </video>
  <div class="note" style="margin-top:14px">
    這段是<b>依腳本內容產生的動畫</b>：左邊是那 __TOT__ 個步驟（跟著播放游標走、目前步驟高亮、停用的標灰），
    右邊是螢幕模擬。畫面與旁白都是<b>直接從腳本檔讀出來</b>的，所以它與腳本一致，適合看每一個步驟的細節。
  </div>

  <h2><span class="dot"></span>範例 21：把 Excel 的資料貼進記事本</h2>
  <video controls preload="metadata">
    <source src="ex21.mp4" type="video/mp4">
    你的瀏覽器不支援影片播放，<a href="ex21.mp4">點此下載</a>。
  </video>
  <div class="note" style="margin-top:14px">
    <b>這段是實際操作錄影。</b>先看程式裡載入的範例 21，然後切到 Excel（四筆資料、游標停在 A1），
    按播放之後畫面就在 Excel 與記事本之間來回：複製一格 → 切過去貼上 → 切回來換下一格。
    <br>中間的執行過程以 <b>2 倍速</b>播放，否則光是來回切換就要近四十秒。
    <br>錄影前要先讓記事本「空白開場」——Windows 11 的記事本會還原上次的內容，不清掉的話上一次的字會留在裡面。
  </div>

  <div class="box green">
    <b>它怎麼做到的：兩個子巨集。</b><br>
    範例 21 本身只有 <b>__N21__ 個動作</b>（__N21EN__ 個啟用、實際會執行 __N21EFF__ 個），
    真正做事的內容放在兩個可以重複呼叫的子腳本裡：
    <br><br>
    <b>1.「複製貼上一格資料」</b>：Ctrl+C 複製目前這一格 → Alt+Tab 切到記事本 → 貼上 →
    Alt+Tab 切回 Excel → 右移一格。
    <br>
    <b>2.「下一行開頭」</b>：往下移一列，再回到那一列的第一欄。
    <br><br>
    主腳本只用兩層迴圈把它們串起來：外層跑 4 次（每一列），內層跑 2 次（每一欄），
    總共 8 個儲存格被搬過去。
  </div>

  <div class="box">
    <b>為什麼這個模式好用：</b>「資料在哪個程式」和「要貼到哪裡」是<b>兩件可以分開換掉的事</b>。
    把「複製貼上一格資料」裡切換目標的那幾個步驟改掉，同一套迴圈就能把資料送進別的應用程式或網頁表單；
    要動的地方只有子巨集，主腳本不用改。
  </div>

  <h2><span class="dot"></span>三個值得看的設計（範例 20）</h2>

  <div class="box green">
    <b>1. 用「等待視窗」取代固定延遲。</b><br>
    腳本不是「等 5 秒再看」，而是「等到行程名稱是 excel.exe 的視窗出現，最多等 10 秒」。
    這代表 <b>Excel 開得慢它會等、開得快它不會多等</b>；同一支腳本換到比較慢的電腦上也不會壞。
    後面那兩個 Esc 是跳過 Excel 的範本開始畫面。
  </div>

  <div class="box">
    <b>2. 迴圈變數：不用自己寫計數邏輯。</b><br>
    迴圈設定的是一個範圍（這裡是 1 到 3）加上<b>要把當下的索引寫進哪個變數</b>（這裡是「月份」）。
    所以 <code>${月份} 月</code> 會依序展開成 <b>1 月、2 月、3 月</b>，
    金額那欄則用「設定變數 ← 亂數」每輪取一個新值。變數分頁在播放時會即時顯示每一輪的值。
  </div>

  <div class="box red">
    <b>3. 刻意留白的地方（這也是設計）。</b><br>
    腳本<b>沒有</b>去處理「另存新檔」對話框，註解裡寫明是為了避免排程時卡在對話框；
    <b>也刻意不關閉 Excel</b>，留著讓人確認結果。示範腳本把「不做什麼」也寫清楚，比硬做到底安全。
  </div>

  <h2><span class="dot"></span>我犯的錯：我把一個正常的腳本「修」壞了</h2>
  <div class="box red">
    第一次解析這支腳本時，我看到它用到 <code>${月份}</code>，卻只找到一個「設定變數」（金額），
    就下結論說「月份沒有被設定，三列會是空白」——<b>這個結論是錯的。</b>
    <br><br>
    錯在哪：我漏看了<b>迴圈步驟自己就有一個欄位</b>指定「索引要寫進哪個變數」，那欄的值就是「月份」。
    我當時是拿一個自己猜的欄位名去比對，猜錯了欄位名、就以為那欄不存在。
    <br><br>
    更糟的是我接著「修」它：加了一步「設定變數 ← 目前播放的輪數」。
    那個來源指的是<b>外層重複播放的輪數</b>（這支腳本只播一輪，所以永遠是 1），
    不是 For 迴圈的索引——它在迴圈裡每跑一輪就把「月份」覆寫成 1，<b>把原本正常的行為弄壞了。</b>
    <br><br>
    抓到它的方式很簡單也很老派：<b>真的跑一遍</b>，然後讀執行紀錄。
    記錄裡三輪都是「月份 = 1」，我就知道是我的問題，不是腳本的問題。
    已從備份還原，確認檔案雜湊與修改前完全相同。
    <br><br>
    這件事也直接影響到示範怎麼拍。第一次嘗試螢幕錄影時，錄到的畫面大半是 Excel 的開始畫面與登入提示，
    而且 Excel 的最近檔案清單一起入了鏡——<b>那裡面是本機的檔案名稱</b>。後來把錄影環境整理乾淨
    （先開好一個空白活頁簿、清掉會露出檔名的畫面、裁掉顯示帳號名稱的標題列）才錄成上面那段。
    在這之前，能不能看出「工具真的能跑」，靠的是執行紀錄的數字：三輪的變數值、亂數金額、
    以及輸入完成後的儲存格內容。
    </div>

  <h2><span class="dot"></span>範例 20 的全部 __TOT__ 個步驟</h2>
  <div class="scroll">
  <table>
    <tr><th>#</th><th>動作</th><th>內容</th><th>狀態</th></tr>
__ROWS__
  </table>
  </div>

  <h2><span class="dot"></span>範例 21 的全部 __N21__ 個動作</h2>
  <div class="scroll">
  <table>
    <tr><th>#</th><th>動作</th><th>內容</th><th>狀態</th></tr>
__ROWS21__
  </table>
  </div>
  <div class="note">
    兩張表都由程式直接讀腳本檔產生，不是手打的。灰色列是停用的步驟；「執行巨集」那幾列就是呼叫子腳本的地方，
    所以在表裡看到迴圈包著兩個「執行巨集」，就是範例 21 的兩層迴圈。
  </div>

  <div class="note">
    本文為工具實作與流程的記錄，不構成任何軟體或服務的推薦。示範腳本是這個工具內建的範例之一；
    錄影與動畫都只在實際操作過的那台機器上產生。
  </div>

  <footer>小R 頻道・程式設計</footer>
</div>
</body>
</html>
"""
    html = (HTML.replace("__N21__", str(n21)).replace("__N21EN__", str(n21en))
                .replace("__N21EFF__", str(n21eff)).replace("__ROWS21__", rows21)
                .replace("__TOT__", str(n_tot)).replace("__EN__", str(n_en))
                .replace("__COM__", str(n_com)).replace("__EFF__", str(n_eff))
                .replace("__ROWS__", rows)
                .replace("__DATE__", "2026/09/28"))
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
    print("wrote", os.path.join(out, "index.html"), len(html), "chars")
    print("  步驟 %d｜啟用 %d｜註解 %d｜實際執行 %d" % (n_tot, n_en, n_com, n_eff))
    import re
    print("  email:", re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html) or "none")
    print("  本機路徑:", re.findall(r"[A-Za-z]:[\\/][^\s\"<>]*", html) or "none")


if __name__ == "__main__":
    main()
