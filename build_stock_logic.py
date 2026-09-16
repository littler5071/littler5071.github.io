# -*- coding: utf-8 -*-
"""產生「飆股在線等的技術分析邏輯」整理頁：/stock/logic/

內容來源：公開節目《理財達人秀》「飆股在線等」第 1、4、9、11、16、17、20、29、42、60 集
（逐字稿由本地語音轉文字產生後整理），只做教學化重寫與公開資料對照；
不引用任何節目畫面、不暗示任何人背書、不構成投資建議。

用法：python build_stock_logic.py [網站根目錄]
"""
import html, os, re, shutil, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else r"D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
FIG_SRC = r"D:/_Richard/OpenCode/圖片生成/小R頻道_股市觀察/figs"
OUT = os.path.join(SITE, "stock", "logic")
FIG_DST = os.path.join(OUT, "figs")

SECTIONS = [
    ("trend", "一、先看趨勢：頭頭高、底底高", "fig1_趨勢.png",
     """技術分析的第一件事不是找買點，而是先判斷現在是多頭、空頭還是盤整。
節目用最簡單的兩句話定義：<strong>多頭＝頭頭高、底底高；空頭＝頭頭低、底底低</strong>（第9集 [10:20]、第29集 [13:30]）。
做法是把最近的高低點圈起來，看「高點有沒有比前一個高點高、低點有沒有比前一個低點高」；
兩個都在墊高才叫多頭，只有一邊成立就還不算（第42集 [07:50]）。""",
     ["道氏理論六大法則（第42集）：① 指數反映一切 ② 趨勢分多頭／空頭／盤整三種 ③ 三波段（初升、主升、末升）"
      "④ 不同市場要互相驗證（例如美股／韓國與台股、或同一家公司的不同市場）⑤ 趨勢要配合量能 "
      "⑥ 趨勢會持續到出現反轉訊號為止。",
      "三波段裡「主升段」通常不會最短、最容易賺；「末升段」變化最多、也是最容易追高被套的位置（第42集 [14:06]、[15:39]）。",
      "只做多頭六個字：<strong>頭頭高、底底高</strong>；看到頭頭低（高點不再創高）就先退出（第29集 [13:30]、[17:12]）。"]),

    ("position", "二、再看位置：多頭其實只有兩個買點", None,
     """很多人賠錢不是選錯股票，是<strong>買在錯的位置</strong>。節目反覆強調：多頭架構裡的買點只有兩種（第4集 [04:37]、第29集 [20:17]）：

<div class="two">
  <div class="box"><strong>① 回後買上漲</strong><br>漲一段後回檔，回檔不能跌破前低、也不能跌破月線；等回檔後
  出現「紅 K 站上 5 日均線、且收盤過昨天最高點」再進場。</div>
  <div class="box"><strong>② 盤整突破</strong><br>橫向整理一段後帶量突破整理區，量能要是昨天的 1.3 倍以上
  （攻擊量），突破後回測不破就是第二個位置。</div>
</div>

<b>進場的確認方式</b>：收盤前（節目說大約 13:20～13:25）看那根紅 K 是否成立再決定，新手不要盤中就衝進去（第4集 [25:51]）。""",
     ["進場當下就要決定「做長還是做短」——是用來決定出場依據的，不是等賠錢才想（第4集 [17:33]）。",
      "回檔深的股票較弱、回檔淺的（回檔不到漲幅 1/3）較強；跌破前低就是低低低，趨勢已改（第11集 [27:20]、第29集 [20:48]）。"]),

    ("ma", "三、均線：市場的平均成本線", "fig2_均線多頭排列.png",
     """均線就是「這幾天買進的人的平均成本」（第4集 [08:47]）。節目用的參數很標準：5、10、20（月線）、60（季線）、120、240 日（第4集 [10:21]）。
判斷多空的關鍵是<strong>月線（20 日）</strong>：月線之上只做多、月線之下只做空（第4集 [13:58]、第60集 [08:51]）。""",
     ["<strong>三線多排</strong>：5、10、20 由上而下排好、且都向上，是最基本的多頭條件；再加上季線叫「四線多排」（第4集 [18:03]、第29集 [20:17]）。",
      "<strong>月線下彎就趕快跑</strong>；跌破月線一定要處理，短線跌破 5 日／10 日線就先減碼（第4集 [07:13]、[29:28]）。",
      "<strong>站上哪條均線進場，就跌破哪條均線出場</strong>——用 5 日均線進場卻等跌破月線才賣，是最常見的紀律錯誤（第4集 [32:03]）。",
      "盤整時均線會失效（多空都容易被掃），但「盤整突破」反而是好位置（第4集 [28:55]）。"]),

    ("granville", "四、葛蘭碧八法：一條線的四個買點", "fig3_葛蘭碧八法.png",
     """葛蘭碧（Granville）在 1960 年代提出以均線為核心的八個法則＝四個買點＋四個賣點（第20集 [02:32]、[08:44]）。
節目那一集只細講買點，但四個買點的<strong>共同三條件</strong>很清楚：<strong>均線向上 ＋ 股價站回均線 ＋ 有量</strong>（第20集 [31:37]）。""",
     ["<strong>買點 1</strong>：股價由均線下站上均線，且均線已向上、帶量。此時未必是多頭架構，先試單，賺 2～3 天就跑（第20集 [15:26]）。",
      "<strong>買點 2</strong>：多頭中回測均線、均線撐住後放量再漲——就是「回後買上漲」，最容易看懂（第20集 [16:29]、[24:18]）。",
      "<strong>買點 3</strong>：跌破均線後又站回，而且均線仍向上的「慣性」會把股價拉回來；<strong>最好三天內站回</strong>，拖太久均線會下彎（第20集 [22:15]、[22:47]）。",
      "<strong>買點 4</strong>：跌破月線且負乖離達 15% 以上（跌太遠了），要等看到紅 K、過昨天高點才搶反彈，不能買正在下跌的（第20集 [24:50]、[26:57]）。",
      "<strong>最常被漏掉的條件</strong>：只看「站上均線」卻沒看「均線要向上」——均線向下的股票站上去也不能買（第20集 [14:24]）。"]),

    ("sr", "五、支撐與壓力：一線的兩面", None,
     """支撐與壓力是技術分析的兩大精華之一（另一個是趨勢）（第9集 [02:04]）。它們是<strong>同一條線的兩面</strong>：
站上就變支撐、跌破就變壓力（第9集 [08:16]、[33:00]）。""",
     ["<strong>畫線的四個地方</strong>：大量 K 線（大量紅 K 取低點、大量黑 K 取高點，都不該被跌破）、盤整區（盤整兩三週的區間最有效）、均線（5／10／20 均、月季線）、切線（第9集 [19:07]、[24:16]、[25:17]、[26:18]）。",
      "<strong>確認要等第二天</strong>：碰到支撐或壓力後，看隔天的 K 線表態才決定要不要動作（第9集 [06:45]）。",
      "<strong>強弱有別</strong>：20 日均線的支撐強度重於 5 日均線（第9集 [25:47]）；同一位置如果同時是盤整區＋月線＋上升切線，力量最強（第9集 [27:20]）。",
      "<strong>切線（趨勢線）</strong>：多頭連兩個低點畫上升切線、空頭連兩個高點畫下降切線；出新低就不斷重畫，最後一條叫「最後切線」，跌破大部分該離場（第16集 [05:11]、[14:38]）。",
      "切線角度越陡＝股票越強，角度變平就是轉弱（但還不能直接做空）（第16集 [13:33]、[14:06]）。"]),

    ("pattern", "六、型態：找機會也順便算目標價", "fig4_型態.png",
     """型態是「盤整後固定出現的圖形」，節目稱它是統計出來的大數法則：<strong>約九成會走出目標，但仍有一成失敗，所以停損一定要做</strong>（第11集 [03:35]、[04:38]）。
型態分兩類：<strong>反轉</strong>（底部轉多、頭部轉空）與<strong>續勢</strong>（整理後續走原方向）（第11集 [08:44]）。學型態有兩個目的：找機會、算目標價。""",
     ["<strong>N 字底</strong>是節目評價最高的底部型態：第一隻腳（空頭反彈，低檔大量長紅、站上 5 日均線）＋ 第二隻腳"
      "（回檔<strong>不破前低</strong>，且回跌幅度不超過前段漲幅的 1/2），突破前波高點（頸線）確認（第11集 [13:56]、[14:58]）。",
      "<strong>目標價＝等幅</strong>：第一隻腳漲多少，第二隻腳就抓多少。例：100 漲到 120（漲 20），回檔到約 110 起漲，目標 110＋20＝130（第11集 [20:07]）。",
      "節目說 N 字底勝率約九成，W 底約四成，關鍵差在「第二隻腳是高腳還是低腳」；W 底要成功需要均線多排配合（第11集 [11:18]、[12:20]）。",
      "停損：試單者守回檔低點；確認後買進者守「買進那根紅 K 的低點」，收盤跌破才算（第11集 [19:05]、[21:41]）。",
      "目標價到了、或「第二天不漲」就出場；走完之後就回到多頭的均線操作，不再算目標價（第11集 [24:45]、[25:16]）。"]),

    ("gap", "七、跳空缺口：看位置，不是看缺口", "fig5_缺口.png",
     """缺口＝今天最低價高於昨天最高價（向上跳空）。節目的重點是「<strong>缺口出現在哪裡</strong>比缺口本身重要」：
盤整中的缺口常被回補、意義不大；低檔帶量突破的缺口最有用；高檔爆量後出現的缺口要小心反轉（第10、13、51 集主題）。""",
     ["<strong>突破缺口</strong>：帶量突破頸線時出現，缺口不回補最強。",
      "<strong>逃逸缺口</strong>：上漲中途出現，代表主力加碼，可續抱。",
      "<strong>竭盡缺口</strong>：漲勢末端出現，常見爆量長黑後被回補。",
      "缺口要看「有沒有量」與「隔天 K 棒的方向」，單獨一個缺口不構成買賣理由。"]),

    ("volume", "八、量價關係：攻擊量與出貨量", "fig6_量價.png",
     """量是「相對的」，不是絕對數字（第17集 [00:00]）。節目用「均量」當基準：<strong>5 日均量是基本量</strong>，
放量約 1.2～1.3 倍、爆量約 2 倍以上（第17集 [12:27]、[13:30]）。看量一定要配四個東西：趨勢 → 位置 → 當天漲跌 → 隔天股價（第17集 [04:43]）。""",
     ["<strong>低檔爆大量</strong>：隔天不跌（收紅 K）就可能是換手成功、準備反彈（第17集 [15:32]）。",
      "<strong>高檔爆大量</strong>：如果隔天股價不漲，多半是出貨，要準備回檔（第17集 [16:35]、[26:55]）。",
      "「平地一聲雷」＝盤整突破同時爆量，是最漂亮的起漲組合（第17集 [17:36]）。",
      "價漲量縮是背離訊號、容易回檔；空頭時不用看量，有量沒量都會跌（第17集 [33:08]、[10:54]）。",
      "出貨判斷：高檔價漲量增、但量與價都不再創新高＝主力在跑，要賣（第17集 [26:55]）。"]),

    ("indicator", "九、指標：加分項，不是主角", "fig7_背離.png",
     """節目對指標的定位很清楚：<strong>指標是「加分用」，不能拿來判斷多空</strong>（第1集 [18:16]、[33:12]）。多空看趨勢與均線，指標只是幫你選位置。""",
     ["<strong>KD</strong>：以 9 天為比較基準，0～100 之間；低於 20 算超跌、高於 80 算過熱（第1集 [09:25]、[12:00]）。",
      "黃金交叉＝快線 K 向上穿過慢線 D、且兩線都向上；低檔（約 50）交叉常是起漲點，不一定回到 20；強勢股甚至 50～60 就交叉（第1集 [16:10]、[21:51]）。",
      "<strong>鈍化</strong>：高檔鈍化＝兩線卡在 80～100 兩三天不下來；低檔鈍化＝卡在 0～20 超過三天。鈍化時不要看指標，回到股價與紀律操作（第1集 [31:11]、[31:41]）。",
      "<strong>背離</strong>：價格創新高、指標沒跟著創新高＝高檔背離，是減碼訊號；低檔反過來看（第42、47 集主題）。",
      "<strong>MACD</strong>：做為進場的第六個確認條件（黃金交叉、綠轉紅、紅柱延長）（第29集 [22:21]）。",
      "<strong>盤整時指標失準</strong>：黃金交叉、死亡交叉都容易兩邊被打（第1集 [30:06]）。"]),

    ("exit", "十、出場與停利：訊號出現就執行", "fig8_出場訊號.png",
     """節目的說法是「<strong>會賣才是高手</strong>」：不要想賣最高點，訊號出現、把賺的入袋（第60集 [01:34]、[12:29]）。前提是買在起漲位置，才有 10～20% 的停利空間。""",
     ["<strong>停利訊號（一）</strong>：沿 5 日均線上漲、獲利超過 10%，跌破 5 日均線就賣；沒跌破就繼續抱（第60集 [02:37]）。",
      "<strong>停利訊號（二）</strong>：高檔連續兩天出大量，這兩天的低點被跌破就離開——代表主力已經跑掉，容易「一日反轉」（第60集 [05:44]、[06:15]）。",
      "<strong>停利訊號（三）</strong>：高檔爆量長黑 K。沒跌破昨天紅 K 先賣一半；如果長黑直接吃掉昨天的紅 K（長黑吞噬）＝全部出清，這是「一日反轉最嚴重的 K 線訊號」（第60集 [09:53]、[10:26]）。",
      "<strong>停損紀律</strong>：進場那根紅 K 的低點不可跌破；短線破 5 均、中線破 10 均、長線破月線（第4集 [26:52]、第17集 [19:40]）。",
      "賣掉之後如果又彈上來，不代表賣錯——上面壓著大量，量過不去就不該追（第60集 [07:17]）。"]),
]

CHECKLIST = [
    ("1. 大盤與類股", "先看美股（影響最大）→ 韓國（結構最接近）→ 台股；再看類股強弱與資金占比，"
                     "強勢類股裡挑領頭羊「大約兩檔就好」（第29集 [04:09]、[10:51]）。"),
    ("2. 趨勢", "頭頭高、底底高？高點與低點是否同步墊高（第29集 [13:30]）。"),
    ("3. 位置", "只有兩個買點：回後買上漲、盤整突破；回檔不可跌破前低與月線（第29集 [20:17]）。"),
    ("4. 均線", "5／10／20（加季線）多頭排列，且 K 棒在均線之上（第29集 [20:17]）。"),
    ("5. 價量", "價漲量增、價跌量縮；進場要有量（約昨天 1.3 倍以上）（第17集 [14:30]）。"),
    ("6. 進場 K 線", "紅 K 站上 5 日均線並突破昨天最高點，收盤前確認（第29集 [21:19]）。"),
    ("7. 指標加分", "MACD 黃金交叉、綠轉紅、紅柱延長（第29集 [22:21]）。"),
    ("8. 停損先設好", "進場紅 K 的低點；跌破就走，不要用「想買便宜」當理由接刀（第29集 [18:13]）。"),
]

PITFALLS = [
    ("在均線下做多", "月線之下的股票，紅 K 黃金交叉照樣會被跌破（第1集 [28:33]）。"),
    ("只看站上均線、忘了均線要向上", "均線向下＝沒有支撐，站上去也是假動作（第20集 [14:24]）。"),
    ("盤整時用指標", "黃金交叉、死亡交叉在盤整裡兩邊被打；盤整的價值在「突破」（第1集 [30:06]、第4集 [28:55]）。"),
    ("高檔爆量還追", "高檔爆量不是攻擊量而是出貨，隔天不漲就要跑（第17集 [05:46]、[16:35]）。"),
    ("沒有停損 / 沒有先決定做長做短", "進場不決定長短，就會變成不停損的藉口（第4集 [17:33]）。"),
    ("用錯線出場", "用 5 日均線進場、卻等跌破月線才賣（第4集 [32:03]）。"),
    ("把 N 字底看成 W 底", "兩者都有兩個角，但 N 字底第二腳是高腳，勝率差很多（第11集 [11:18]）。"),
]


def html_body():
    parts = []
    for sid, title, fig, intro, bullets in SECTIONS:
        blk = [f'<section id="{sid}">', f"  <h2><span class='dot'></span>{title}</h2>"]
        if fig:
            blk.append(f'  <figure><img src="figs/{fig}" alt="{html.escape(title)}">'
                       f'<figcaption>自製示意圖：{html.escape(title)}</figcaption></figure>')
        blk.append("  <p>" + intro.strip() + "</p>")
        if bullets:
            blk.append("  <ul class='how'>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>")
        blk.append("</section>")
        parts.append("\n".join(blk))
    check = "".join(f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>" for k, v in CHECKLIST)
    pit = "".join(f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>" for k, v in PITFALLS)
    eps = ("第 1 集 KD、第 4 集 均線、第 9 集 支撐壓力、第 11 集 N 字底、第 16 集 切線、第 17 集 量價、"
           "第 20 集 葛蘭碧八法、第 29 集 選股法則、第 42 集 道氏理論、第 60 集 停利訊號")
    return f"""
<div class="wrap">
  <a class="back" href="../">← 回股市觀察</a>

  <header>
    <h1>飆股在線等的技術分析邏輯：一套可以照著做的流程</h1>
    <div class="sub">從趨勢、位置、均線、支撐壓力、型態、量價，到進出場與停利訊號</div>
    <hr class="rule">
  </header>

  <div class="box">
    <strong>這篇是什麼</strong>：把公開節目《理財達人秀》「飆股在線等」的技術分析教學，整理成一套前後連貫的流程。
    內容根據節目的公開集數（{eps}）重寫，<strong>只做教學化整理、不使用節目畫面</strong>，
    也不代表節目或講者立場、<strong>不構成任何投資建議</strong>（詳見頁尾說明）。
  </div>

  <div class="summary">
    <div class="box"><div class="big">先趨勢</div><div>頭頭高、底底高才做多</div></div>
    <div class="box"><div class="big">再位置</div><div>只有兩個買點：回後買上漲、盤整突破</div></div>
    <div class="box"><div class="big">後訊號</div><div>均線、量價、型態、指標依序確認</div></div>
    <div class="box"><div class="big">先停損</div><div>進場就想好：破哪條線要走</div></div>
  </div>

  <div class="box">
    <strong>整體架構（節目的說法）</strong>：選股 → 進場 → 停損 → 停利，四個步驟環環相扣。
    「<strong>你把股票選好了，實際上你已經成功一半</strong>」——選對股票，即使進得不夠精準也還有機會賺；
    所以流程是<strong>從上到下</strong>：大盤 → 類股 → 個股，而不是看到紅 K 就買（第29集 [02:37]、[03:08]）。
  </div>

{''.join(parts)}

  <section id="checklist">
    <h2><span class="dot"></span>十一、進場前的檢核表（照順序問自己）</h2>
    <div class="scroll"><table>
      <tr><th>檢查項目</th><th>要問的問題</th></tr>
      {check}
    </table></div>
    <p class="dim">節目裡的成功率說法：前三個條件大約六成、加上價量約七成、六個條件都順到八成（第29集 [18:44]、[22:21]）。
    這是節目的經驗值，不是保證，也不是我們的統計。</p>
  </section>

  <section id="pitfalls">
    <h2><span class="dot"></span>十二、最常見的陷阱</h2>
    <div class="scroll"><table>
      <tr><th>陷阱</th><th>節目裡的說法</th></tr>
      {pit}
    </table></div>
  </section>

  <section id="howto">
    <h2><span class="dot"></span>十三、怎麼跟本站的每日觀察一起用</h2>
    <ul class="how">
      <li><a href="../">股市觀察首頁</a>：每個交易日收盤後的觀察報告，逐檔列出技術條件（站上月線、底底高、頭頭高、突破頸線…）。</li>
      <li><a href="../20260915/">2026/09/15 收盤後觀察</a>：含「好條件最多／不好條件最多」排行，可以對照這篇的檢核表看。</li>
      <li>每日觀察裡的條件是<strong>用公開資料可重算的版本</strong>，不含主觀判斷；這篇是方法論，兩者搭配使用。</li>
    </ul>
  </section>

  <div class="box">
    <strong>來源與聲明</strong>：本頁整理自公開節目《理財達人秀》「飆股在線等」的公開集數（第 1、4、9、11、16、17、20、29、42、60 集），
    以<strong>教學化重寫</strong>方式呈現，並標註出處集數與時間點供查證；<strong>未使用任何節目畫面、影片或他人的教材內容</strong>。
    為避免混淆，本頁一律以「朱老師」「K神」等公開稱謂指稱節目講者，<strong>不代表講者或電視台立場，也沒有任何合作或背書關係</strong>。
    所有勝率、報酬率數字都是節目中的說法，不是本頁實測結果。本頁為技術分析方法的整理，
    <strong>不構成投資建議、不報牌、不預測行情、不提供買賣決策</strong>；投資有風險，請自行判斷並自負盈虧。
  </div>
  <a class="back" href="../">← 回股市觀察</a>
</div>
"""

CSS = """  a.back{display:inline-block;margin:2px 0 12px;font-size:14.5px;text-decoration:none;color:var(--blue);border-bottom:1.5px solid currentColor}
  .summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:6px 0 18px}
  .summary .box{background:#fffdf6;border:2px solid var(--line);border-radius:14px;padding:12px 14px;font-size:13.5px;color:var(--soft)}
  .summary .big{font-size:23px;color:var(--ink);margin-bottom:2px}
  section{margin:0 0 6px}
  h2{font-size:clamp(19px,3.2vw,25px);margin:34px 0 10px;display:flex;align-items:center;gap:10px}
  h2 .dot{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}
  figure{margin:14px 0 6px}
  figure img{width:100%;border:2px solid var(--line);border-radius:14px;background:#fdfbf5}
  figcaption{font-size:13.5px;color:var(--soft);margin-top:6px}
  table{width:100%;border-collapse:collapse;font-size:14.5px;margin:10px 0}
  th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}
  .scroll{overflow-x:auto}
  ul.how{font-size:15.5px} ul.how li{margin:7px 0}
  .two{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:10px 0}
  .two .box{background:#fffdf6;border:2px solid var(--line);border-left:5px solid var(--blue);border-radius:14px;padding:12px 14px;font-size:14.5px}
  .dim{color:var(--soft);font-size:14px}
"""


def main():
    os.makedirs(FIG_DST, exist_ok=True)
    for f in os.listdir(FIG_SRC):
        if f.endswith(".png") and not f.startswith("_"):
            shutil.copy(os.path.join(FIG_SRC, f), os.path.join(FIG_DST, f))
    head = open(os.path.join(SITE, "stock", "index.html"), encoding="utf-8").read().split("<body")[0]
    head = re.sub(r"<title>[^<]*</title>",
                  "<title>飆股在線等的技術分析邏輯：趨勢、位置、均線、型態、量價到進出場｜小R 頻道</title>",
                  head, count=1)
    head = head.replace("</style>", CSS + "</style>", 1)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(head + "<body>\n" + html_body() + "\n</body>\n</html>\n")
    figs = len([f for f in os.listdir(FIG_DST) if f.endswith(".png")])
    print(f"已產生 {os.path.join(OUT, 'index.html')}｜圖 {figs} 張")


if __name__ == "__main__":
    main()
