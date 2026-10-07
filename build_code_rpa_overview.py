# -*- coding: utf-8 -*-
"""產生 code/rpa-overview/index.html：RPAHelper 功能總覽（系列第一篇／系列導覽）

內容全部由程式產生：
  - 畫面截圖由 ep_rpa\\shots 複製進頁面目錄（頁面用相對路徑引用，圖不能留在 repo 外）
  - 分類數量與「四類動作」的清單以程式常數維護，數字與工具的實際選單一致
  - 「內建示範腳本」清單以資料夾實際存在的檔案為準（工具產生器會產生 00～12 ＋ 20 共 14 支；
    21 與兩支子巨集不在內建清單裡，它們是示範頁那兩支腳本自己帶的）

用法：python build_code_rpa_overview.py [網站根目錄]
"""
import io
import os
import re
import shutil
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
SHOTS = r"C:\Users\Summer\banner\ep_rpa\shots"
SRC_TOOL = os.path.join(SHOTS, "tool_main.png")      # 主視窗（腳本清單＋步驟清單）
SRC_MENU = os.path.join(SHOTS, "tool_menu.png")      # 「步驟」選單展開（四類＋基本操作）
DEMOS = r"D:\_Richard\OpenCode\RPA工具\publish\Scripts\Demos"

# 工具內建產生器會產生的示範腳本（見 RPAHelper/Demos/DemoScripts.cs）
BUILTIN = [
    "00_功能總覽", "01_滑鼠鍵盤與文字", "02_找圖與等待影像", "03_變數與剪貼簿",
    "04_條件判斷與跳躍", "05_迴圈", "06_執行外部程式", "07_檔案讀寫",
    "08_視窗操作與等待", "09_輸入法控制", "10_錯誤處理與結束代碼",
    "11_螢幕擷取", "12_呼叫其他巨集", "20_開啟Excel並輸入資料",
]
# 不需要操作視窗、可用命令列直接跑（也當工具自己的回歸測試）
UNATTENDED = ["03", "04", "05", "06", "07", "09", "10", "11", "12"]

DATE = "2026/10/01"


def shrink(src, dst, maxw=1360, trim=0):
    """複製截圖到頁面目錄；有 PIL 就順手去邊與縮圖（截圖是實際操作擷取，不加工內容）。"""
    if not os.path.exists(src):
        print("⚠ 找不到截圖：", src)
        return None
    try:
        from PIL import Image
        im = Image.open(src)
        if trim:
            w, h = im.size
            im = im.crop((trim, trim, w - trim, h - trim))
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        im.convert("RGB").save(dst, "PNG", optimize=True)
    except Exception as e:                      # 沒有 PIL 就原樣複製，不要讓產頁失敗
        print("（PIL 不可用，原樣複製：%s）" % e)
        shutil.copy2(src, dst)
    print("截圖：%s → %s（%d bytes）" % (os.path.basename(src), os.path.basename(dst),
                                        os.path.getsize(dst)))
    return dst


def main():
    out = os.path.join(SITE, "code", "rpa-overview")
    os.makedirs(out, exist_ok=True)
    shrink(SRC_TOOL, os.path.join(out, "tool.png"))
    shrink(SRC_MENU, os.path.join(out, "actions.png"), trim=12)

    missing = [n for n in BUILTIN if not os.path.exists(os.path.join(DEMOS, n + ".rpa.json"))]
    n_builtin = len(BUILTIN) - len(missing)
    n_unatt = len(UNATTENDED)
    if missing:
        print("⚠ 內建示範清單有檔案不存在（不列入計數）：", missing)

    HTML = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>把重複的電腦操作，變成自己會跑的流程｜程式設計｜小R 頻道</title>
<meta name="description" content="一套 Windows 自動化工具的功能總覽：錄製、找圖點擊、變數與流程控制到定時排程。四類共 31 個可以自己加的動作、__NB__ 支內建示範腳本（其中 __NU__ 支不需要操作視窗、可用命令列跑），以及什麼情況適合、什麼情況不適合。">
<link rel="stylesheet" href="../../css/code.css">
<style>
  h1{font-size:clamp(24px,4.4vw,34px);margin:8px 0 6px;text-align:center;line-height:1.4}
  .box.blue{border-color:#c3cddd;background:#f5f7fb}
  ul.plain li,ol.plain li{margin:7px 0}
  figure{margin:16px 0 20px}
  img.shot{width:100%;display:block;border:2px solid var(--line);border-radius:14px;background:#fff}
  figcaption{color:var(--soft);font-size:13.5px;margin-top:8px;text-align:center}
  .scroll{overflow-x:auto;margin:12px 0}
  table{width:100%;border-collapse:collapse;font-size:14.5px;min-width:560px}
  th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}
  code{background:rgba(54,78,112,.07);border:1px solid var(--line);border-radius:6px;padding:1px 6px;
       font-size:14px;font-family:Consolas,"Courier New",monospace}
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="../">← 回程式設計</a>
  <a class="back" style="margin-left:14px" href="../../">← 回影片索引</a>

  <h1>把重複的電腦操作，<br>變成自己會跑的流程</h1>
  <div class="sub">錄一次、補上判斷與迴圈，再讓它自己排程——不用寫程式</div>
  <div class="meta">__DATE__・功能總覽（系列導覽）</div>

  <div class="box">
    <b>這篇是系列的第一篇。</b>主角是一套 Windows 上的自動化工具（RPAHelper）。
    它和「錄一次就只能重播一次」的巨集工具最大的差別，是錄下來的動作<b>可以再編輯成流程</b>：
    插入變數、條件判斷、迴圈、呼叫外部程式，最後交給內建排程自己跑。
    這篇講它的能力範圍、限制，以及內建的示範腳本；四類動作的細節會另外寫成四篇
    （基本操作、變數與流程、系統與檔案、等待與訊息）。
  </div>

  <h2><span class="dot"></span>三種自動化方式，而且可以混用</h2>
  <div class="box">
    <b>1. 錄製</b>：按 <code>F9</code> 開始錄、照平常的方式操作、再按一次停止；播放是 <code>F10</code>，
    暫停／單步是 <code>F8</code>，停止是 <code>F11</code>。手動做一次就好的流程用這個最快。
    <br><br>
    <b>2. 找圖點擊</b>：按 <code>F12</code> 框選畫面上的一塊目標，播放時會先在畫面裡搜尋它、找到才點下去。
    這是它最實用的一招：<b>可以跨程式</b>——別的應用程式裡的按鈕，甚至是 Windows 的「開始」按鈕，
    它都找得到、按得下去，不需要知道座標，也不需要那個程式提供任何自動化介面。
    <br><br>
    <b>3. 程式化流程</b>：需要判斷、迴圈、變數或整合外部程式時，從「步驟」選單自己加動作。
    <br><br>
    三者可以混用——這才是它好玩的地方：<b>先錄一段日常操作，中間插入條件與迴圈，最後用排程執行。</b>
    錄製時按下的熱鍵不會被錄進腳本，也不會傳到目標程式。
  </div>

  <figure>
    <img class="shot" src="tool.png" alt="工具的流程頁：左邊是 Scripts 資料夾的腳本清單，右邊是步驟清單與播放控制">
    <figcaption>主視窗分成三頁：流程（平常都在這頁）、腳本設定、變數。
    左邊是 Scripts 資料夾的腳本清單（上圖載入的是內建示範腳本），右邊是步驟清單與播放控制。</figcaption>
  </figure>

  <h2><span class="dot"></span>可以自己加的動作有 31 個，分成四類</h2>
  <div class="box">
    錄製只會產生「滑鼠移動、點擊、滾輪、鍵盤、文字」這幾種；真正讓它能處理複雜工作的是「步驟」選單裡
    另外 31 個可以自己加的動作，分成四類：
    <ul class="plain">
      <li><b>基本操作（8）</b>：滑鼠點擊／拖曳、文字輸入（支援中文與多行）、找圖點擊、等待圖片出現、
          切換視窗、等待視窗、啟動程式或開網址、加入巨集流程（把另一支腳本當成一個步驟）。</li>
      <li><b>變數與流程（11）</b>：註解、設定變數、設定剪貼簿、正規式解析、條件判斷、
          標籤、跳躍、迴圈開始／結束、跳出迴圈、下一輪。</li>
      <li><b>系統與檔案（8）</b>：執行外部程式（不等待／等待完成／取得輸出）、讀取檔案、寫入檔案、
          螢幕擷取、視窗操作、等待視窗關閉、等待程序、輸入法。</li>
      <li><b>等待與訊息（4）</b>：固定等待、隨機等待、顯示訊息／確認／輸入、
          停止播放並指定成功或失敗（會反映在命令列的結束代碼）。</li>
    </ul>
  </div>

  <figure>
    <img class="shot" src="actions.png" alt="「步驟」選單展開，顯示四類分類與「基本操作」底下的動作">
    <figcaption>「步驟」選單就是這四類；圖中展開的是「基本操作」底下的 8 個動作。
    工具列的「＋ 新增步驟」是常用的那幾個，其餘都在這個選單裡。</figcaption>
  </figure>

  <h2><span class="dot"></span>變數：可以跨腳本共用</h2>
  <div class="box">
    任何文字欄位都可以用 <code>${名稱}</code>。變數的來源除了常數，還有剪貼簿、日期時間、
    游標位置、前景視窗、隨機數、環境變數、檔案內容⋯⋯所以「讀進來的資料」可以直接餵給後面的步驟。
    <br><br>
    <b>重點是它可以跨腳本共用。</b>用「加入巨集流程」呼叫另一個腳本時（例如把「複製貼上一格資料」
    這種動作抽成子巨集），子腳本用的是<b>同一份變數</b>：主流程先設好的值，被呼叫的子腳本直接就能用；
    子腳本自己宣告的初始變數也會併進來，呼叫端要覆寫也可以。
    所以同一支子巨集能給很多支主流程重複使用——換掉參數就是另一件事，不必複製整份腳本。
    <br><br>
    它也有修飾詞與預設值：<code>${原文:trim:upper}</code> 由左到右依序套用；
    <code>${代號|未設定}</code> 在變數不存在時給預設值（<b>不會中斷流程</b>）；
    <code>${價格:int}</code>、<code>${價格:0.00}</code> 是轉換與格式化。
    命令列也能覆寫初始值（<code>--var 月份=9</code>）；播放期間「變數」分頁會即時顯示每個變數的值，除錯時很有用。
  </div>

  <h2><span class="dot"></span>什麼情況適合，什麼情況不適合</h2>
  <div class="box green">
    <b>適合：</b>有固定順序、又要一再重複的操作；在多個程式之間搬資料（複製、切換、貼上）；
    每天或每週固定時間要做的事；以及「只有自己知道怎麼做」的那些瑣事——
    把判斷寫進條件裡，就變成別人也能跑的流程。
  </div>
  <div class="box red">
    <b>要先知道的限制：</b>
    <ul class="plain">
      <li><b>它要的不是「一個人」，而是「一個開著、已登入的桌面」。</b>
          要找圖或點擊就得有畫面，所以跑的時候桌面不能鎖定、程式視窗要在；
          但<b>放著讓它自己跑完就好，不需要有人在旁邊看</b>——每天固定時間做的那種事就是這樣跑的。
          真正需要人的，只有腳本裡放了「顯示訊息／確認／輸入」這種要人判斷的步驟。</li>
      <li><b>找圖對畫面變化敏感</b>：解析度、系統縮放、佈景主題或字型改變，都可能要重新框選一次。</li>
      <li><b>目標程式改版就要重錄那幾步</b>（按鈕搬了位置，腳本不知道）。</li>
      <li><b>步驟失敗只有兩種選擇：跳過並繼續、或中止整個播放。</b>
          舊版的「暫停並詢問我」已移除——播放中不會再跳出詢問視窗。要交給排程跑的時候，
          建議用「中止」，這樣失敗會回傳非 0 的結束代碼，排程器才看得出異常。</li>
      <li><b>防毒軟體可能誤判。</b>它會安裝全域鍵盤滑鼠鉤子、用模擬輸入送鍵，行為特徵和側錄程式重疊，
          加上執行檔沒有數位簽章——實際發生過被 AVG 判成 <code>IDP.Generic</code> 移入隔離區，
          隔離後連重新建置都會被鎖住。要用的話，記得把工具資料夾加進防毒軟體的例外。</li>
    </ul>
  </div>

  <h2><span class="dot"></span>內建的 __NB__ 支示範腳本，照著看最快</h2>
  <div class="box">
    選單「工具 → 產生功能示範腳本」會在 Scripts 資料夾產生 __NB__ 支範例，每支都用註解步驟寫清楚在做什麼：
    <br><br>
    <b>00 功能總覽</b>：純註解，把全部功能列一遍（第一次打開就從這支看）。
    <br>
    <b>01～12</b>：一種功能一支——滑鼠鍵盤與文字、找圖與等待影像、變數與剪貼簿、條件判斷與跳躍、
    迴圈、執行外部程式、檔案讀寫、視窗操作與等待、輸入法控制、錯誤處理與結束代碼、螢幕擷取、呼叫其他巨集。
    <br>
    <b>20</b>：實戰範例，開啟 Excel 並輸入資料。
    <br><br>
    其中 <b>__NU__ 支不需要操作視窗</b>（03、04、05、06、07、09、10、11、12），可以直接用命令列執行，
    也順便當作這個工具自己的回歸測試。
    <br><br>
    <b>建議順序</b>：先看 03、04、05 這三支（命令列就能跑，不必盯著畫面），再看 20 這支實戰範例。
  </div>

  <h2><span class="dot"></span>讓它自己跑：定時排程與命令列</h2>
  <div class="box">
    <b>定時執行排程</b>（選單「工具 → 定時執行排程」，或系統匣右鍵）可以建立一次、每天、每週
    （可勾多個星期）與「每隔 N 分鐘」四種週期，<b>同一支腳本可以同時有多筆排程</b>。
    <ul class="plain">
      <li>清單會顯示每一筆的執行週期、下次執行、上次執行與結果、狀態。</li>
      <li>需要<b>程式開著</b>才會執行（縮到系統匣也可以）。</li>
      <li>到點時如果正在播放或錄製，那一次會標成「跳過」。</li>
      <li>錯過超過 10 分鐘的時段<b>不會補跑</b>（避免中午開機就突然跑清晨的排程）。</li>
      <li>排程由程式自己管理，<b>不建立也不需要 Windows 工作排程器的工作</b>。</li>
    </ul>
  </div>
  <div class="box">
    <b>命令列模式</b>：不帶參數是圖形介面，帶參數就是命令列模式（不顯示視窗、不安裝鉤子）。
    <div class="scroll">
    <table>
      <tr><th>指令</th><th>用途</th></tr>
      <tr><td><code>--play 腳本.rpa.json</code></td><td>執行腳本</td></tr>
      <tr><td><code>--play X.rpa.json --loop 3 --quiet --log</code></td><td>重複 3 輪、安靜模式、寫入紀錄</td></tr>
      <tr><td><code>--play X.rpa.json --var 月份=9</code></td><td>用參數覆寫腳本裡的初始變數</td></tr>
      <tr><td><code>--list</code> / <code>--ime-status</code> / <code>--help</code></td><td>列出腳本／輸入法狀態／完整說明</td></tr>
    </table>
    </div>
    <b>結束代碼</b>：<code>0</code> 執行完成、<code>1</code> 失敗或被停止、<code>2</code> 參數錯誤、
    <code>3</code> 找不到腳本。腳本裡用「停止播放」步驟指定成功或失敗，就能直接控制結束代碼——
    要接上其他工具或自己寫的排程器時，這是唯一的判斷依據。
  </div>

  <div class="note">
    這個系列接下來會把四類動作各寫一篇（基本操作、變數與流程、系統與檔案、等待與訊息）。
    想看實際跑起來的樣子，可以先看已經發佈的實戰那篇：
    <a href="../rpa-demo/">不用寫程式，讓電腦自己批次輸入多筆資料 →</a>
  </div>

  <div class="note">
    本文是這套工具的功能整理與實作記錄，不構成任何軟體或服務的推薦。
    頁面上的畫面都是實際操作時擷取，未經合成。
  </div>

  <footer>小R 頻道・程式設計</footer>
</div>
</body>
</html>
"""
    html = (HTML.replace("__NB__", str(n_builtin))
                .replace("__NU__", str(n_unatt))
                .replace("__DATE__", DATE))
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
    print("wrote", os.path.join(out, "index.html"), len(html), "chars")
    print("  內建示範 %d 支（其中可無人值守 %d 支）" % (n_builtin, n_unatt))
    print("  email:", re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html) or "none")
    print("  本機路徑:", re.findall(r"[A-Za-z]:[\\/][^\s\"<>]*", html) or "none")
    left = re.findall(r"__[A-Z0-9]+__", html)
    print("  殘留佔位符:", left or "none")


if __name__ == "__main__":
    main()
