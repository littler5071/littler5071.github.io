# -*- coding: utf-8 -*-
"""產生 RPAHelper 系列的四篇分類文章：
    code/rpa-basic/    基本操作（含找圖點擊的重點段落）
    code/rpa-flow/     變數與流程
    code/rpa-system/   系統與檔案
    code/rpa-wait/     等待與訊息

四篇共用同一套版型（與 build_code_rpa_overview.py 同一組 CSS／.box／h2 dot），
截圖由 ep_rpa\\shots 複製進各頁目錄；分類清單與「對應示範腳本」以程式常數維護，
數字用檔案存在性算，不寫死。

用法：python build_code_rpa_series.py [網站根目錄]
"""
import io
import os
import re
import shutil
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
SHOTS = r"C:\Users\Summer\banner\ep_rpa\shots"
DEMOS = r"D:\_Richard\OpenCode\RPA工具\publish\Scripts\Demos"
DATE = "2026/10/01"

CSS = """
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
  .box.blue{border-color:#c3cddd;background:#f5f7fb}
  ul.plain,ol.plain{margin:8px 0;padding-left:22px}
  ul.plain li,ol.plain li{margin:7px 0}
  figure{margin:16px 0 20px}
  img.shot{width:100%;display:block;border:2px solid var(--line);border-radius:14px;background:#fff}
  figcaption{color:var(--soft);font-size:13.5px;margin-top:8px;text-align:center}
  code{background:rgba(54,78,112,.07);border:1px solid var(--line);border-radius:6px;padding:1px 6px;
       font-size:14px;font-family:Consolas,"Courier New",monospace}
  .embed{position:relative;margin:10px 0 8px;border:2px solid var(--line);border-radius:14px;overflow:hidden;background:#000}
  .embed iframe{display:block;width:100%;aspect-ratio:16/9;border:0}
  @supports not (aspect-ratio:16/9){.embed{padding-bottom:56.25%;height:0}
    .embed iframe{position:absolute;top:0;left:0;width:100%;height:100%}}
  table.scope{width:100%;border-collapse:collapse;margin:12px 0 4px;font-size:15px;line-height:1.75}
  table.scope th{text-align:left;padding:8px 10px;background:#f2f5f9;border-bottom:2px solid var(--line);font-weight:700}
  table.scope td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
  table.scope td.sc-step{width:44%;font-weight:600;color:#1a4f8a}
  .vidlink{color:var(--soft);font-size:14px;margin:0 0 6px}
  .note{margin-top:34px;padding:15px 18px;border:2px dashed var(--line);border-radius:14px;
        color:var(--soft);font-size:14px;background:rgba(255,253,246,.6)}
  footer{margin-top:30px;text-align:center;color:var(--soft);font-size:13.5px}
  a{color:var(--blue)}
"""

HEAD = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__｜程式設計｜小R 頻道</title>
<meta name="description" content="__DESC__">
<style>__CSS__
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="../">← 回程式設計</a>
  <a class="back" style="margin-left:14px" href="../../">← 回影片索引</a>

  <h1>__H1__</h1>
  <div class="sub">__SUB__</div>
  <div class="meta">__DATE__・__KIND__</div>

__BODY__
  <div class="note">
    這是「四類動作」系列的其中一篇。系列第一篇是功能總覽（三種自動化方式、31 個動作、內建示範腳本與限制）：
    <a href="../rpa-overview/">把重複的電腦操作，變成自己會跑的流程 →</a>
  </div>
  <div class="note">
    本文是工具實作與流程的記錄，不構成任何軟體或服務的推薦。
    頁面上的畫面都是實際操作時擷取，未經合成。
  </div>

  <footer>小R 頻道・程式設計</footer>
</div>
</body>
</html>
"""


def shrink(src, dst, maxw=1360, trim=12):
    if not os.path.exists(src):
        print("⚠ 找不到截圖：", src)
        return
    try:
        from PIL import Image
        im = Image.open(src)
        if trim:
            w, h = im.size
            im = im.crop((trim, trim, w - trim, h - trim))
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        im.convert("RGB").save(dst, "PNG", optimize=True)
    except Exception as e:
        print("（PIL 不可用，原樣複製：%s）" % e)
        shutil.copy2(src, dst)
    print("  截圖 %s → %s（%d bytes）" % (os.path.basename(src), os.path.basename(dst),
                                        os.path.getsize(dst)))


def demos_box(names):
    """「對應的示範腳本」區塊；清單以資料夾實際存在的檔案為準（缺檔會標出來，不寫死）。"""
    have = [n for n in names if os.path.exists(os.path.join(DEMOS, n + ".rpa.json"))]
    miss = [n for n in names if n not in have]
    txt = "、".join(n.replace("_", " ") for n in have) if have else "（無）"
    extra = ("　⚠ 找不到：" + "、".join(miss)) if miss else ""
    return ('\n  <div class="box blue"><b>對應的示範腳本（工具內建）：</b>' + txt + "。" + extra +
            " 每支都用註解步驟寫清楚在做什麼，可以開啟來對照本文。<b>但影片裡跑的是另一份</b>：示範副本放在 Scripts\Demo_影片\，內容跟這幾支相同，只是把播放速度調慢一點、每個步驟之間多停一下，方便看清楚程式在做什麼。你要自己試，直接用工具內建的那幾支就可以。</div>\n")


def check_demos(names):
    return [n for n in names if os.path.exists(os.path.join(DEMOS, n + ".rpa.json"))]


IDS_JSON = r"C:\Users\Summer\banner\ep_rpa\out\rpa_video_ids.json"


def video_ids():
    """影片 id 一律從 JSON 讀，不寫死（換版本只改那個檔）。"""
    try:
        import json as _json
        return _json.load(io.open(IDS_JSON, encoding="utf-8"))
    except Exception as e:
        print("⚠ 讀不到影片 id：", e)
        return {}


# ★ 影片實際示範的範圍（照 RPAHelper\Scripts\Demo_影片 裡腳本的真实流程整理）
#   影片只示範這些步驟，上面文章講的是完整的功能分類 —— 兩者不是同一件事，必須講清楚。
VIDEO_SCOPE = {
    "rpa_cat_basic": {
        "intro": "一支示範腳本，從頭到尾沒有人碰鍵盤滑鼠。",
        "steps": [
            ("啟動 notepad.exe", "腳本自己去啟動程式，你不用先手動開。"),
            ("等待「記事本」視窗出現", "等視窗真的跑出來才往下走，不是硬等固定秒數。"),
            ("程式自己輸入這段文字", "中文也沒問題，換成任何一段文字都行。"),
            ("Ctrl+A 全選、Ctrl+C 複製", "用鍵盤步驟把選到的內容放進剪貼簿。"),
            ("複製到的內容存成一個變數", "存成變數之後，後面的步驟隨時可以再拿出來用。"),
        ],
    },
    "rpa_cat_flow": {
        "intro": "一支示範腳本：存變數、處理字串、讓流程重複跑，條件成立就跳過該跑的。",
        "steps": [
            ("先存兩個變數：姓名、產品", "值的內容會直接帶進後面的訊息裡。"),
            ("把變數帶進訊息顯示", "訊息視窗裡看到的是程式真正代入後的結果，不是模板。"),
            ("把一段文字去空白再轉成大寫", "關鍵字寫在變數名後面，整理完再拿來用。"),
            ("迴圈從 1 跑到 4", "每一輪都把累積值往上加，訊息裡的數字每輪都不一樣。"),
            ("條件成立就跳過中間那一段", "搭配標籤與跳到標籤，就做出分支。"),
            ("把結果寫成一個檔案", "寫檔之後可以在別的流程再讀回來。"),
        ],
    },
    "rpa_cat_system": {
        "intro": "一支示範腳本：執行外部程式、寫檔讀檔、把畫面擷取下來。",
        "steps": [
            ("設定一個變數記住存檔位置", "先決定輸出要放哪裡。"),
            ("腳本自己去執行 cmd", "執行完把結束代碼記下來，0 代表成功。"),
            ("把內容寫成一個文字檔", "寫檔路徑用剛才那個變數。"),
            ("再把這個檔案讀回來", "讀進來的內容變成一個變數，訊息裡看得到讀到的字。"),
            ("把整個畫面擷取存檔", "留下「當時畫面長什麼樣」的證據。"),
            ("把產出的檔案用程式打開", "直接看到輸出結果，不用自己去資料夾找。"),
        ],
    },
    "rpa_cat_wait": {
        "intro": "一支示範腳本：出錯的時候怎麼處理，成功的時候怎麼回報。",
        "steps": [
            ("腳本要去讀一個不存在的檔案", "這是故意的，讓你看得到出錯時的樣子。"),
            ("讀不到就跳出訊息視窗", "內容是腳本裡先寫好的文字。"),
            ("按一下確定，腳本才繼續", "訊息視窗是阻塞的，沒按就不會往下走。"),
            ("跳過那一段，繼續執行外部程式", "執行完檢查結束代碼。"),
            ("結束代碼 0 就回報成功", "不為 0 就跳到另一個標籤、回報失敗。"),
        ],
    },
}

def embed(key, title):
    """影片段落：youtube-nocookie 內嵌 ＋ 備援連結 ＋ 這支示範腳本的步驟對照。"""
    vid = video_ids().get(key)
    if not vid:
        return ""
    sc = VIDEO_SCOPE.get(key, {})
    rows = "\n".join(
        '          <tr><td class="sc-step">%s</td><td>%s</td></tr>' % (a, b)
        for a, b in sc.get("steps", []))
    return ('\n  <h2><span class="dot"></span>影片：這支示範腳本實際跑一遍</h2>\n'
            '  <div class="box"><b>%s</b></div>\n'
            '  <table class="scope">\n'
            '    <thead><tr><th>影片裡看到的步驟</th><th>說明</th></tr></thead>\n'
            '    <tbody>\n%s\n    </tbody>\n  </table>\n'
            '  <div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s"\n'
            '      loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"\n'
            '      allowfullscreen></iframe></div>\n'
            '  <p class="vidlink">看不方便的話，也可以 <a href="https://youtu.be/%s">直接在 YouTube 看</a>。'
            '這支是 RPAHelper 的實際執行錄影：畫面上看得到工具視窗和動作清單，程式自己跑完，'
            '全程沒有人碰鍵盤滑鼠；程式跳出的訊息視窗也一起入鏡，訊息裡的內容是變數真正代入後的值，'
            '工具視窗以外的畫面都已經塗黑。</p>\n'
            % (sc.get("intro", ""), rows, vid, title, vid))


# ---------------------------------------------------------------- 各篇內容
BASIC = """
  <div class="box">
    <b>這支示範的是最基本的一條路線：</b>讓電腦自己去啟動程式、敲鍵盤、打字、複製，
    最後把複製到的內容存成變數。整支腳本從頭到尾沒有人碰鍵盤滑鼠。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「基本操作」分類">
    <figcaption>「步驟」選單的「基本操作」分類。示範腳本是 01（滑鼠鍵盤與文字）。</figcaption>
  </figure>

  <h2><span class="dot"></span>啟動程式、等待視窗出現</h2>
  <div class="box green">
    <b>影片裡的做法：</b>第一個動作是啟動 <code>notepad.exe</code>，第二個動作是
    <b>等待「記事本」視窗出現</b>。等視窗比硬等固定秒數可靠——程式還沒開好就繼續下一步，
    常常會把字打到不對的地方；等視窗是「真的看到它了才往下走」。
  </div>

  <h2><span class="dot"></span>文字輸入與鍵盤：中文也沒問題</h2>
  <div class="box green">
    <b>影片裡的做法：</b>程式自己把三段文字打進記事本，包含中文與數字。
    <b>文字輸入</b>支援中文與多行，換行會自動轉成 Enter；連續打字在錄製時會合併成一個步驟。
    <br>少數程式對「直接注入文字」不理會時，設定裡可以改成用剪貼簿貼上或逐鍵掃描碼；
    中文輸入法干擾的話，有一個「播放前自動切換輸入法為英文」的選項。
  </div>

  <h2><span class="dot"></span>組合鍵與變數：把結果留下來</h2>
  <div class="box green">
    <b>影片裡的做法：</b>用 Ctrl+A 全選、Ctrl+C 複製，把選到的內容放進剪貼簿，
    再把複製到的內容存成一個變數。之後任何一步驟要用，隨時可以拿出來。
    <br><b>組合鍵</b>（例如 Ctrl+Shift+End）就是「按下、放開」的序列，
    所以 Ctrl+A 這種動作會拆成三個鍵盤步驟記錄下來。
  </div>
"""

FLOW = """
  <div class="box">
    <b>這支示範的是「會存資料、會改字串、會重複做事」：</b>
    有了這些，腳本才不只是照順序重播，而是能看情況做事。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「變數與流程」分類">
    <figcaption>「步驟」選單的「變數與流程」分類。示範腳本是 03（變數與剪貼簿）、04（條件判斷與跳躍）、05（迴圈）。</figcaption>
  </figure>

  <h2><span class="dot"></span>變數：先存起來，之後帶進任何地方</h2>
  <div class="box green">
    <b>影片裡的做法：</b>一開始先存兩個變數——姓名跟產品。接著顯示訊息的時候把變數放進去，
    程式會<b>把值直接帶進去</b>，所以你在影片裡看到的訊息視窗是
    「你好 王小明，歡迎使用 RPAHelper！」，不是模板。
    <br>變數名不分大小寫，可以跨腳本共用；同一支腳本重複執行時，
    變數的初始值也可以在「腳本 → 變數」裡設定。
  </div>

  <h2><span class="dot"></span>字串處理：關鍵字寫在變數名後面</h2>
  <div class="box green">
    <b>影片裡的做法：</b>把一段帶空白的文字，去空白再轉成大寫。
    寫法是把關鍵字接在變數名後面（例如大括號加變數名再加去空白、轉大寫），
    不用另外寫程式。
    <br>可以用的處理包含去空白、轉大寫或小寫、取長度、數字格式化、日期格式化。
  </div>

  <h2><span class="dot"></span>迴圈：讓同一段流程重複跑</h2>
  <div class="box green">
    <b>影片裡的做法：</b>迴圈寫在「迴圈開始」與「迴圈結束」之間。開始那一步要設定
    <b>起始、結束、遞增</b>，以及<b>把當下的索引寫進哪個變數</b>。
    <br>示範腳本讓迴圈從 1 跑到 4，每一輪都把累積值往上加，所以訊息視窗裡的數字
    每一輪都不一樣：0+1、0+1+2、0+1+2+3、0+1+2+3+4。這是程式真的算出來的。
    <br><b>安全機制：</b>播放設定裡有「單次播放最多執行幾個動作」的上限，
    會自動攔住寫錯的無限迴圈。
  </div>

  <h2><span class="dot"></span>條件判斷：成立時就跳過該跑的</h2>
  <div class="box green">
    <b>影片裡的做法：</b>用一個判斷式決定後面該不該跑。條件成立的話就<b>跳過中間那一段</b>，
    直接接到標籤後面繼續——所以影片裡會出現「這條路走不到」的訊息被略過，
    接著是「程式跳過中間那段」。
    <br>搭配「標籤」與「跳到標籤」就能做出分支：條件不成立走 A 路，成立走 B 路。
  </div>

  <h2><span class="dot"></span>把結果寫成檔案</h2>
  <div class="box green">
    <b>影片裡的做法：</b>迴圈與判斷跑完之後，把累積結果寫成一個文字檔，
    並回報寫到哪裡。寫檔之後可以在別的流程再讀回來。
  </div>
"""

SYSTEM = """
  <div class="box">
    <b>這支示範的是「跟電腦上其他東西打交道」：</b>執行外部程式、把內容寫成檔案再讀回來，
    以及把畫面擷取下來。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「系統與檔案」分類">
    <figcaption>「步驟」選單的「系統與檔案」分類。示範腳本是 06（執行外部程式）、07（檔案讀寫）、11（螢幕擷取）。</figcaption>
  </figure>

  <h2><span class="dot"></span>執行外部程式：把它的輸出當下一步的輸入</h2>
  <div class="box green">
    <b>影片裡的做法：</b>腳本自己去執行 <code>cmd</code>，執行完會把<b>結束代碼</b>記下來。
    <b>結束代碼等於 0 代表成功，非 0 代表失敗</b>——這是判斷「那件事到底有沒有做成」
    最可靠的線索，比事後看畫面猜好得多。
    <br>也可以把外部程式的<b>輸出</b>存成變數，當成下一步的輸入。
  </div>

  <h2><span class="dot"></span>寫檔、讀檔：讓資料能在流程之間流動</h2>
  <div class="box green">
    <b>影片裡的做法：</b>先設定一個變數記住要存檔的位置，接著把內容<b>寫成一個文字檔</b>，
    然後<b>再把同一個檔案讀回來</b>——讀進來的內容就變成一個變數。
    <br>你在影片訊息視窗裡看到的「讀回來的內容」，就是剛才寫進檔案的那幾行字，
    不是寫死的文字。資料夾不存在的話，工具可以自動建立。
  </div>

  <h2><span class="dot"></span>螢幕擷取：把當下的畫面存成圖片</h2>
  <div class="box green">
    <b>影片裡的做法：</b>一個動作就把整個畫面擷取下來存成 png，
    訊息視窗會回報「畫面已擷取存檔」，也可以自己指定存檔路徑。
    <br>用途是留下「當時畫面長什麼樣」的證據：出錯時要回頭看當時畫面上的哪個按鈕被按了，
    存一張圖比事後描述清楚得多。
  </div>

  <h2><span class="dot"></span>把產出的檔案打開來看</h2>
  <div class="box green">
    <b>影片裡的做法：</b>最後用「啟動程式」把剛才產出的檔案用系統預設程式打開，
    直接看到輸出結果，不用自己去資料夾裡找。
  </div>
"""

WAIT = """
  <div class="box">
    <b>這支示範的是「出錯的時候怎麼處理，成功的時候怎麼回報」：</b>
    腳本做錯事，也要讓人知道發生什麼。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「等待與訊息」分類">
    <figcaption>「步驟」選單的「等待與訊息」分類。示範腳本是 10（錯誤處理與結束代碼）。</figcaption>
  </figure>

  <h2><span class="dot"></span>讀不到檔案：跳一個訊息視窗出來</h2>
  <div class="box green">
    <b>影片裡的做法：</b>腳本要去讀一個檔案，而這個檔案不存在。
    讀不到就<b>跳出訊息視窗</b>，內容是腳本裡先寫好的文字，不是程式亂寫的。
    <br>訊息視窗是<b>阻塞</b>的：畫面上跳出來之後，腳本就停在那裡等你按。
    你按「確定」，它才知道可以往下走——這也是為什麼影片裡的訊息視窗都會停留幾秒，
    讓觀眾看得清楚內容。
    <br>訊息還有三種型態：單純顯示、是／否確認（結果存成變數）、以及請人輸入文字。
  </div>

  <h2><span class="dot"></span>結束代碼：分辨成功還是失敗</h2>
  <div class="box green">
    <b>影片裡的做法：</b>跳過那一段之後，腳本繼續去執行外部程式，並檢查它的結束代碼。
    <br><b>結束代碼等於 0 就跳出「執行成功」的訊息；不等於 0 就跳到另一個標籤、
    顯示「結束代碼不是 0，代表失敗」。</b>
    <br>同一支影片裡訊息視窗被用了兩次：一次是出錯提示、一次是成功回報——
    這就是腳本自己決定要回報什麼。要讓排程看得出成敗，最後再用「停止播放」指定成功或失敗。
  </div>
"""

PAGES = [
    dict(slug="rpa-basic", shot="menu_basic.png",
         title="讓電腦自己開程式、打字，再把內容複製下來",
         h1="讓電腦自己開程式、打字，<br>再把內容複製下來",
         sub="一支示範腳本：啟動記事本、輸入文字、全選複製、存成變數",
         kind="系列 2／5：基本操作", video="rpa_cat_basic",
         desc="RPA 工具的基本操作類 8 個動作：滑鼠點擊與文字輸入、找圖點擊（不必知道座標、可跨程式找到別的應用程式的按鈕並點擊）、"
              "等待圖片出現、切換與等待視窗、啟動程式、加入巨集流程。含找圖會壞掉的四種情況與「何時該用找圖、何時用座標」。",
         demos=["01_滑鼠鍵盤與文字", "02_找圖與等待影像"],
         body=BASIC),
    dict(slug="rpa-flow", shot="menu_flow.png",
         title="會存資料、會改字串，還會讓同一段流程重複跑",
         h1="會存資料、會改字串，<br>還會讓同一段流程重複跑",
         sub="一支示範腳本：存變數、處理字串、迴圈累加，條件成立就跳過那一段",
         kind="系列 3／5：變數與流程", video="rpa_cat_flow",
         desc="RPA 工具的變數與流程類 11 個動作：變數與修飾詞（可跨腳本共用）、設定剪貼簿、正規式解析、"
              "條件判斷（含檔案存在／視窗存在／程序執行中）、標籤與跳躍、For 迴圈與 Break／Continue。",
         demos=["03_變數與剪貼簿", "04_條件判斷與跳躍", "05_迴圈"],
         body=FLOW),
    dict(slug="rpa-system", shot="menu_system.png",
         title="執行外部程式、讀寫檔案，還把畫面擷取下來",
         h1="執行外部程式、讀寫檔案，<br>還把畫面擷取下來",
         sub="一支示範腳本：執行 cmd 看結束代碼、把內容寫成檔案再讀回來、擷取畫面存檔",
         kind="系列 4／5：系統與檔案", video="rpa_cat_system",
         desc="RPA 工具的系統與檔案類 8 個動作：執行外部程式（等待、取得輸出、結束代碼）、讀取與寫入檔案、"
              "螢幕擷取、視窗操作、等待視窗關閉與等待程序、輸入法控制，以及把腳本當積木的巨集呼叫。",
         demos=["06_執行外部程式", "07_檔案讀寫", "11_螢幕擷取"],
         body=SYSTEM),
    dict(slug="rpa-wait", shot="menu_wait.png",
         title="等對地方，腳本才換得了電腦",
         h1="等對地方，<br>腳本才換得了電腦",
         sub="一支示範腳本：讀不到檔案就跳訊息說明，執行完看結束代碼決定回報成功還是失敗",
         kind="系列 5／5：等待與訊息", video="rpa_cat_wait",
         desc="RPA 工具的等待與訊息類 4 個動作：固定與隨機等待、顯示訊息（唯一真的需要人在旁邊的動作）、"
              "停止播放並指定成功或失敗；含步驟失敗時的兩種行為與排程該選哪一種。",
         demos=["10_錯誤處理與結束代碼"],
         body=WAIT),
]


def main():
    for p in PAGES:
        out = os.path.join(SITE, "code", p["slug"])
        os.makedirs(out, exist_ok=True)
        shrink(os.path.join(SHOTS, p["shot"]), os.path.join(out, "menu.png"))
        html = (HEAD.replace("__CSS__", CSS)
                    .replace("__TITLE__", p["title"])
                    .replace("__DESC__", p["desc"])
                    .replace("__H1__", p["h1"])
                    .replace("__SUB__", p["sub"])
                    .replace("__KIND__", p["kind"])
                    .replace("__DATE__", DATE)
                    .replace("__BODY__", p["body"] + embed(p["video"], p["title"]) + demos_box(p["demos"])))
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
        print("wrote %s (%d chars)" % (os.path.join(out, "index.html"), len(html)))
        bad = re.findall(r"__[A-Z]+__", html)
        print("  殘留佔位符:", bad or "none",
              "| email:", re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html) or "none",
              "| 本機路徑:", re.findall(r"[A-Za-z]:[\\/][^\s\"<>]*", html) or "none")


if __name__ == "__main__":
    main()
