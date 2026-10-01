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
            " 每支都用註解步驟寫清楚在做什麼，可以開啟來對照本文。</div>\n")


def check_demos(names):
    return [n for n in names if os.path.exists(os.path.join(DEMOS, n + ".rpa.json"))]


# ---------------------------------------------------------------- 各篇內容
BASIC = """
  <div class="box">
    <b>這一類管的是「手」和「眼睛」：</b>動滑鼠、打鍵盤、在畫面上找東西、把視窗叫出來。
    錄製能產生的大部分動作都在這裡，也是整個工具最直覺的部分——
    <b>錄一次就能重播，但要它穩定，靠的是下面「等待」與「找圖」這幾個動作。</b>
    這一類共 8 個動作：滑鼠點擊／拖曳、文字輸入、找圖點擊、等待圖片出現、切換視窗、等待視窗、
    啟動程式或開網址、加入巨集流程。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「基本操作」分類，展開後是 8 個動作">
    <figcaption>「步驟」選單的「基本操作」分類。下面挑其中兩個最有價值的講：<b>找圖點擊</b>與<b>等待視窗</b>。</figcaption>
  </figure>

  <h2><span class="dot"></span>找圖點擊：不必知道座標，找到才按</h2>
  <div class="box green">
    <b>怎麼用：</b>按 <code>F12</code>（或從選單選「找圖點擊…」），畫面會變暗讓你<b>框選一個目標</b>——
    一個按鈕、一個圖示、一段文字都行。播放時它會在畫面裡搜尋這塊目標，<b>找到才點下去</b>，
    不是死記上一次錄下來的座標。
    <br><br>
    <b>它可以跨程式。</b>這是我最常用它、也最想推薦的一點：<b>別的應用程式裡的按鈕、
    甚至是 Windows 的「開始」按鈕，它都找得到、按得下去</b>——
    不需要知道座標，也不需要那個程式提供任何自動化介面。遇到「只能靠人看著畫面點」的老系統，
    這是最省事的一條路。
  </div>
  <div class="box">
    <b>幾個讓它更穩的設定：</b>
    <ul class="plain">
      <li><b>限定搜尋區域</b>：只在你框的範圍裡找，快很多，也避免畫面其他地方有長得像的東西時誤點。</li>
      <li><b>點擊位置</b>：預設點在樣板中心；需要偏一點就用自訂位移。也支援右鍵與雙擊。</li>
      <li><b>容差與重試</b>：設定裡有預設容差與重試次數／間隔；畫面有抗鋸齒或半透明時把它放寬一點。</li>
      <li><b>找不到時</b>：逾時可以「跳過」或「中止」。示範腳本裡故意用了畫面上不會出現的假圖，
          並設成「跳過」，讓你看到逾時後腳本怎麼繼續。</li>
    </ul>
  </div>
  <div class="box red">
    <b>它會壞掉的幾種情況（先知道省得踩）：</b>
    <ul class="plain">
      <li><b>解析度、系統縮放、佈景主題或字型改變</b>：目標長相就變了，要重新框選一次。</li>
      <li><b>目標程式改版、按鈕搬位置</b>：要找的東西還在，但可能被收進選單或換了圖示——重新框一次就好。</li>
      <li><b>目標被別的視窗蓋住</b>：螢幕上找不到它就找不到；所以腳本裡常要先「切換視窗」把它叫到前景。</li>
      <li><b>動畫中的按鈕</b>：淡入、位移中的元件，等它停下再找（前面加一個「固定等待」或改用「等待圖片出現」）。</li>
    </ul>
  </div>
  <div class="box">
    <b>「等待圖片出現」是它的搭擋：</b>找圖點擊是「找到了就點」，等待圖片出現是「等到它出現才繼續」，
    常用在「按下送出之後，等結果畫面跑出來」。逾時同樣可以選跳過或中止。
    <br><br>
    <b>什麼時候該用找圖、什麼時候直接用座標？</b>位置固定、每次都在同一個地方的，用座標最快；
    <b>位置會變的（視窗大小會變、清單順序會動、程式的版面會被使用者拉大拉小）就用找圖</b>——
    這也是同一支腳本能不能換到別人電腦上跑的关键。
  </div>

  <h2><span class="dot"></span>等待視窗：把「等 5 秒」換成「等到它出現」</h2>
  <div class="box">
    錄製出來的腳本常常長這樣：點一下、等個幾秒、再點下一個。問題是那幾秒是<b>當下那台電腦</b>需要的時間——
    換一台慢一點的機器就不夠，快一點的機器又白白浪費。
    <br><br>
    「等待視窗」是「等到符合條件的視窗出現才往下走」，比對方式有四種：<b>完全相同／包含關鍵字／
    正規式／行程名稱</b>。實務上最常用「行程名稱」（例如等 <code>excel.exe</code> 的視窗出現）或
    「包含關鍵字」（例如標題含 Excel）。<b>開得慢它會等、開得快它不會多等。</b>
    <br><br>
    小提醒：視窗標題會隨檔案變動（未儲存的檔案前面會有 <code>*</code>），所以「標題完全相同」很容易失敗，
    用「包含關鍵字」比較保險。
  </div>

  <h2><span class="dot"></span>文字輸入、鍵盤與視窗</h2>
  <div class="box">
    <b>文字輸入</b>支援中文與多行，換行會自動轉成 Enter；連續打字在錄製時會合併成一個步驟。
    少數程式對「直接注入文字」不理會，設定裡可以改成「剪貼簿貼上」或「逐鍵掃描碼」；
    中文輸入法干擾的話，有一個「播放前自動切換輸入法為英文」的選項。
    <br><br>
    <b>鍵盤按鍵</b>含方向鍵這類延伸鍵；組合鍵（例如 <code>Ctrl+Shift+End</code>）就是按下、放開的序列。
    <br><br>
    <b>切換視窗</b>把目標視窗叫到前景（常常是「找圖或點擊之前」要先做的一步）；
    <b>啟動程式 / 開網址</b>可以開執行檔、文件、資料夾或網址。
  </div>

  <h2><span class="dot"></span>加入巨集流程：把做過的事變成積木</h2>
  <div class="box">
    「加入巨集流程」是<b>把另一支腳本當成一個步驟</b>來執行：可以設定它自己的重複次數與速度，
    路徑存成相對於 Scripts 資料夾（整包複製到別台電腦也能用）。
    <br><br>
    <b>它和變數是連在一起的</b>：被呼叫的子腳本用的是<b>同一份變數</b>，
    所以主流程先設好的值，子腳本直接就能用；子腳本自己宣告的初始變數也會併進來，呼叫端要覆寫也可以。
    同一支子巨集就能給很多支主流程重複使用——換掉參數就是另一件事，不必複製整份腳本。
    （這是「變數與流程」那篇會講的細節。）
  </div>
"""

FLOW = """
  <div class="box">
    <b>這一類是「判斷」與「重複」：</b>錄製只能照順序重播，加上這一類的 11 個動作之後，
    腳本才有辦法「看情況做事」。共 11 個：註解、設定變數、設定剪貼簿、正規式解析、條件判斷、
    標籤、跳躍、迴圈開始／結束、跳出迴圈、下一輪。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「變數與流程」分類，展開後是 11 個動作">
    <figcaption>「步驟」選單的「變數與流程」分類。示範腳本是 03（變數與剪貼簿）、04（條件判斷與跳躍）、05（迴圈）。</figcaption>
  </figure>

  <h2><span class="dot"></span>變數：可以跨腳本共用</h2>
  <div class="box green">
    任何文字欄位都可以用 <code>${名稱}</code>。變數的來源除了常數，還有<b>剪貼簿、日期時間、游標位置、
    前景視窗、隨機數、環境變數、檔案內容</b>⋯⋯所以「讀進來的資料」可以直接餵給後面的步驟。
    <br><br>
    <b>它可以跨腳本共用。</b>用「加入巨集流程」呼叫另一個腳本時，子腳本用的是同一份變數：
    主流程先設好的值，子腳本直接就能用；子腳本自己宣告的初始變數也會併進來，呼叫端要覆寫也可以。
    所以同一支子巨集能給很多支主流程重複使用。
  </div>
  <div class="box">
    <b>修飾詞與預設值</b>（寫在變數名稱後面，用冒號串接，由左到右依序套用）：
    <ul class="plain">
      <li><code>${原文:trim}</code> 去頭尾空白；<code>:upper</code>／<code>:lower</code> 轉大小寫；<code>:length</code> 取長度。</li>
      <li><code>${價格:int}</code> 轉整數、<code>:float</code> 轉小數、<code>:0.00</code> 數字格式化（也有 <code>#,##0</code> 千分位、日期格式）。</li>
      <li><code>${代號|未設定}</code>：變數不存在時使用預設值，<b>而且不會中斷流程</b>；找不到的變數會展開成空字串並在播放紀錄留一行警告。</li>
    </ul>
    變數名稱不分大小寫，可含中英文、數字與底線。初始變數可以存在腳本裡（適合把腳本參數化），
    命令列再用 <code>--var 月份=9</code> 覆寫；播放期間「變數」分頁會即時顯示每一個變數的值。
  </div>
  <div class="box">
    <b>設定剪貼簿</b>把變數或文字放進剪貼簿（給那些不吃模擬輸入的程式用）；
    <b>正規式解析</b>用正規表示式從變數或文字裡取出資料，可以指定第 N 個群組。
    這兩步加上變數，就能把「網頁或報表上的一小段文字」變成後面流程可以判斷的資料。
  </div>

  <h2><span class="dot"></span>條件判斷：成立時可以做三件事</h2>
  <div class="box">
    條件成立時可以：<b>跳到某個標籤</b>、<b>略過下一步</b>、<b>中止整個播放</b>。
    搭配「標籤」與「跳躍」就能組成 if / else；<code>SkipNextWhenTrue</code> 是「成立時跳過下一步」，
    也就是 if 的相反寫法。
    <br><br>
    <b>比較方式不只等於／大於</b>，還有：包含、不包含、開頭是、結尾是、符合正規式、是空的、是數字，
    以及很實用的狀態檢查——<b>檔案存在、視窗存在、程序執行中</b>。
    所以「等那個程式跑完才繼續」「檔案生出來了才往下做」這種事，不需要寫程式。
    <br><br>
    一個容易踩的小地方：<b>兩邊都是數字時用數值比較</b>（所以 9 不會被當成比 10 大）；
    一邊是文字時用字串比較（不分大小寫）。
  </div>

  <h2><span class="dot"></span>迴圈：重複、巢狀、提早結束</h2>
  <div class="box">
    迴圈寫在「迴圈開始」與「迴圈結束」之間，可以巢狀。開始那一步要設定<b>起始、結束、遞增</b>，
    以及<b>把當下的索引寫進哪個變數</b>——那一步的欄位就是「輪數變數」，之後用
    <code>${i}</code> 就能拿到它。
    <br><br>
    <b>跳出迴圈（Break）</b>提早結束整個迴圈；<b>下一輪（Continue）</b>跳過這一輪剩下的步驟、直接進下一輪。
    實務上「遇到某一筆資料格式不對就跳過」就是這兩個動作用起來的。
    <br><br>
    安全機制：播放設定裡有「單次播放最多執行幾個動作」的上限，會自動攔住寫錯的無限迴圈；
    流程跑不完時，先把「重複次數」改成 1，並檢查迴圈範圍。
  </div>
"""

SYSTEM = """
  <div class="box">
    <b>這一類是「跟外面的世界打交道」：</b>執行別的程式並拿它的輸出、讀寫檔案、抓畫面、
    控制視窗、切輸入法。共 8 個：執行外部程式、讀取檔案、寫入檔案、螢幕擷取、視窗操作、
    等待視窗關閉、等待程序、輸入法。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「系統與檔案」分類，展開後是 8 個動作">
    <figcaption>「步驟」選單的「系統與檔案」分類。示範腳本是 06（執行外部程式）、07（檔案讀寫）、11（螢幕擷取）。</figcaption>
  </figure>

  <h2><span class="dot"></span>執行外部程式：拿它的輸出當下一步的輸入</h2>
  <div class="box green">
    三種執行方式：<b>不等待</b>（丟出去就繼續）、<b>等待完成</b>、<b>取得輸出</b>。
    路徑與參數都可以用變數；<b>輸出與結束代碼都能存進變數</b>，所以「跑完之後根據結果決定下一步」是可行的。
    <br><br>
    參數用變數代入，同一支腳本就能重複使用；輸出要修掉前後空白可以勾選。
    它也可以呼叫 PowerShell 或命令列工具——腳本本身沒有寫程式，但可以借用系統既有的能力。
  </div>
  <div class="box">
    <b>三個實務設定：</b>
    <ul class="plain">
      <li><b>結束代碼</b>：非 0 通常代表失敗；可以只靠它判斷成敗，不必解析輸出文字。</li>
      <li><b>輸出編碼</b>：拿到亂碼時把它改成正確的編碼（預設跟隨主機命令列）。</li>
      <li><b>隱藏視窗</b>：排程執行時不彈出黑窗，畫面比較乾淨。</li>
    </ul>
  </div>

  <h2><span class="dot"></span>檔案讀寫與螢幕擷取</h2>
  <div class="box">
    <b>讀取檔案</b>把整個檔案讀進變數（可選擇是否修掉前後空白）；
    <b>寫入檔案</b>有覆寫與附加模式，自動建立不存在的資料夾，編碼支援 UTF-8 與 Big5。
    加上變數與正規式，就能做出「讀一份清單 → 每筆查一次 → 把結果寫成一份報表」這種流程。
    <br><br>
    <b>螢幕擷取</b>可以全螢幕、自訂區域，或只擷取目標視窗，存成 PNG 或 JPG；
    檔名路徑可以用變數組合，<b>加上時間戳記就不會覆蓋前一次</b>——
    這對「定時截圖留存」或「失敗時留證據」很有用。
  </div>

  <h2><span class="dot"></span>視窗與程序：等到該關的關完</h2>
  <div class="box">
    <b>視窗操作</b>包含叫到前景、最大化、最小化、還原、關閉、搬移、置頂，
    以及<b>把視窗資訊讀進變數</b>（標題、行程、位置、大小）——讀出來之後可以用正規式再解析。
    <br><br>
    <b>等待視窗關閉</b>與<b>等待程序</b>是兩個很常被忽略、但能救命的動作：
    例如「等 Excel 完全關閉」再繼續，否則下一步會找到一個正在關閉的視窗。
    <br><br>
    <b>輸入法</b>可以讀取目前狀態、切換中／英模式、切到指定輸入法。
    打字前先切成英文，可以避免中文輸入法攔截按鍵；查詢系統有哪些輸入法可以用命令列
    <code>--ime-status</code>。要注意輸入法狀態是<b>每個視窗各自</b>的，少數程式不支援控制。
  </div>

  <h2><span class="dot"></span>把腳本當積木：呼叫其他巨集</h2>
  <div class="box">
    示範腳本 12 講的是子流程與<b>參數共用</b>：把「複製貼上一格資料」「下一行開頭」這種動作抽成子巨集，
    主流程只負責組織。子巨集有它自己的重複次數、速度與目標視窗，路徑存成相對於 Scripts 資料夾，
    整包複製到別台電腦也能用。
    <br><br>
    <b>循環引用會被擋下來</b>：巨集引用有深度上限，互相呼叫的錯誤會直接停止播放並回報，
    不會無限遞迴把電腦卡死。
  </div>
"""

WAIT = """
  <div class="box">
    <b>這一類只有 4 個動作，但它們決定腳本是「能跑」還是「跑得穩」：</b>
    固定等待、隨機等待、顯示訊息 / 確認 / 輸入、停止播放（指定成功或失敗）。
  </div>

  <figure>
    <img class="shot" src="menu.png" alt="「步驟」選單的「等待與訊息」分類，展開後是 4 個動作">
    <figcaption>「步驟」選單的「等待與訊息」分類。相關示範腳本是 10（錯誤處理與結束代碼）。</figcaption>
  </figure>

  <h2><span class="dot"></span>等待：先求穩，再求快</h2>
  <div class="box green">
    <b>固定等待</b>是等固定的毫秒數；<b>隨機等待</b>是在一個範圍內隨機（例如 300～900 毫秒），
    讓節奏不那麼機械。
    <br><br>
    <b>最重要的一句：能用「等待視窗／等待圖片／等待程序」就不要用固定等待。</b>
    固定等待是在賭那台電腦的速度，換一台機器就可能不夠或浪費；
    等條件的動作是「條件到了就走」，慢的機器會等、快的機器不會多等，
    同一支腳本才換得了機器。
    <br><br>
    實測上的經驗值：需要「讓畫面喘一下」時用 200～500 毫秒的隨機等待就夠，
    真正不確定的等待交給條件類的動作。
  </div>

  <h2><span class="dot"></span>顯示訊息：需要人看一眼的時候</h2>
  <div class="box">
    三種形式：<b>提示</b>（只是告知）、<b>是／否確認</b>（結果存變數）、<b>輸入文字</b>（結果存變數）。
    <br><br>
    這是<b>唯一真的需要有人在旁邊的動作</b>。所以它同時是「無人值守」的分界線：
    腳本裡有它，就要有人在；沒有的話，桌面開著讓它自己跑就好。
    <br><br>
    常見用法：執行到一半要人工判斷的地方停下來問一句；或是拿來當「這支腳本的用法說明」
    （執行前先顯示一句「請先把報表開好」）。
  </div>

  <h2><span class="dot"></span>停止播放與結束代碼：讓排程看得出成敗</h2>
  <div class="box">
    <b>停止播放</b>可以主動結束，並指定這次是<b>成功還是失敗</b>；
    這個結果會變成命令列的<b>結束代碼</b>（<code>0</code> 完成、<code>1</code> 失敗或被停止、
    <code>2</code> 參數錯誤、<code>3</code> 找不到腳本）。
    <br><br>
    為什麼重要：交給排程或別的程式呼叫時，<b>結束代碼是唯一的判斷依據</b>。
    腳本自己知道「這次的結果不對」時，用「停止播放（失敗）」收尾，呼叫端才看得出來。
  </div>

  <h2><span class="dot"></span>步驟失敗時的行為（示範腳本 10）</h2>
  <div class="box">
    每個步驟都可以各自指定<b>找不到／逾時時要怎麼做</b>，只有兩種選擇：
    <ul class="plain">
      <li><b>跳過並繼續</b>：記錄訊息後直接執行下一步。</li>
      <li><b>中止整個播放</b>：停止並回報失敗。</li>
    </ul>
    <b>排程執行時建議用「中止」</b>，這樣失敗會回傳非 0 的結束代碼，排程器才看得出異常；
    純示範或探索性的腳本才用「跳過」。
    <br><br>
    舊版的「暫停並詢問我」已經移除——播放中不會再跳出詢問視窗，所以不會有「沒人理它就卡在那裡」的狀況。
    舊腳本還留著這個設定值的話，載入時會自動視為「跳過」。
  </div>

  <h2><span class="dot"></span>除錯時看哪裡</h2>
  <div class="box">
    播放紀錄（<code>Logs\\playback.log</code>）與錯誤紀錄（<code>Logs\\error.log</code>）會記下每一步的結果與變數值；
    播放中「變數」分頁也會即時更新。播放到一半停住時，最有效的一步是<b>真的跑一遍、讀紀錄</b>，
    而不是猜。
  </div>
"""

PAGES = [
    dict(slug="rpa-basic", shot="menu_basic.png",
         title="讓電腦自己動滑鼠、打字，還會在畫面上找按鈕",
         h1="讓電腦自己動滑鼠、打字，<br>還會在畫面上找按鈕",
         sub="基本操作 8 個動作：找圖點擊可以跨程式找到別的程式的按鈕（連開始按鈕都行）",
         kind="系列 2／5：基本操作",
         desc="RPA 工具的基本操作類 8 個動作：滑鼠點擊與文字輸入、找圖點擊（不必知道座標、可跨程式找到別的應用程式的按鈕並點擊）、"
              "等待圖片出現、切換與等待視窗、啟動程式、加入巨集流程。含找圖會壞掉的四種情況與「何時該用找圖、何時用座標」。",
         demos=["01_滑鼠鍵盤與文字", "02_找圖與等待影像"],
         body=BASIC),
    dict(slug="rpa-flow", shot="menu_flow.png",
         title="從照順序重播，變成會判斷、會重複的流程",
         h1="從照順序重播，<br>變成會判斷、會重複的流程",
         sub="變數與流程 11 個動作：變數可以跨腳本共用，條件判斷還能檢查檔案與視窗狀態",
         kind="系列 3／5：變數與流程",
         desc="RPA 工具的變數與流程類 11 個動作：變數與修飾詞（可跨腳本共用）、設定剪貼簿、正規式解析、"
              "條件判斷（含檔案存在／視窗存在／程序執行中）、標籤與跳躍、For 迴圈與 Break／Continue。",
         demos=["03_變數與剪貼簿", "04_條件判斷與跳躍", "05_迴圈"],
         body=FLOW),
    dict(slug="rpa-system", shot="menu_system.png",
         title="讓腳本去執行別的程式、讀寫檔案、抓下畫面",
         h1="讓腳本去執行別的程式、<br>讀寫檔案、抓下畫面",
         sub="系統與檔案 8 個動作：外部程式的輸出與結束代碼可以直接拿來判斷",
         kind="系列 4／5：系統與檔案",
         desc="RPA 工具的系統與檔案類 8 個動作：執行外部程式（等待、取得輸出、結束代碼）、讀取與寫入檔案、"
              "螢幕擷取、視窗操作、等待視窗關閉與等待程序、輸入法控制，以及把腳本當積木的巨集呼叫。",
         demos=["06_執行外部程式", "07_檔案讀寫", "11_螢幕擷取"],
         body=SYSTEM),
    dict(slug="rpa-wait", shot="menu_wait.png",
         title="等對地方，腳本才換得了電腦",
         h1="等對地方，<br>腳本才換得了電腦",
         sub="等待與訊息 4 個動作：能用「等條件」就不要用「等時間」",
         kind="系列 5／5：等待與訊息",
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
                    .replace("__BODY__", p["body"] + demos_box(p["demos"])))
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
        print("wrote %s (%d chars)" % (os.path.join(out, "index.html"), len(html)))
        bad = re.findall(r"__[A-Z]+__", html)
        print("  殘留佔位符:", bad or "none",
              "| email:", re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html) or "none",
              "| 本機路徑:", re.findall(r"[A-Za-z]:[\\/][^\s\"<>]*", html) or "none")


if __name__ == "__main__":
    main()
