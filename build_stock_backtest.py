# -*- coding: utf-8 -*-
"""產生「訊號回測：正向 vs 反向」頁：/stock/backtest/

內容＝本機用 2 年歷史（993,806 筆日 K、2,059 檔）對 30 個訊號做的分段回測結果。
只做公開資料的統計整理；不報牌、不預測、不構成投資建議。
影片 id 讀同目錄的 video_sig.txt（沒有就不內嵌）。
用法：python build_stock_backtest.py [網站根目錄]
"""
import html, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else r"D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
OUT = os.path.join(SITE, "stock", "backtest")
VID_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_sig.txt")
INTERACTIVE = "https://littler5071.infinityfree.io/bt.html"

TITLE = "訊號回測：正向 vs 反向對照"
SUB = "把 30 個技術訊號放進 2 年歷史，分成多頭與空頭，各自比「有出現」和「沒出現」"


def embed():
    if not os.path.exists(VID_TXT):
        return ""
    vid = open(VID_TXT, encoding="utf-8").read().strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid or ""):
        return ""
    # 私人／草稿影片無法內嵌（會顯示錯誤 153）→ 先用 oembed 確認可嵌
    try:
        import urllib.request
        u = "https://www.youtube.com/oembed?url=https%%3A//youtu.be/%s&format=json" % vid
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            if r.status != 200:
                print("  oembed 非 200 → 不內嵌")
                return ""
    except Exception as e:
        print("  oembed 失敗（%s）→ 不內嵌（私人或草稿影片無法嵌入）" % type(e).__name__)
        return ""
    return f"""
  <section id="video">
    <h2><span class="dot"></span>影片版（4 分鐘）</h2>
    <div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/{vid}"
      title="{TITLE}" loading="lazy" allowfullscreen
      allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"></iframe></div>
    <p class="vidlink"><a href="https://youtu.be/{vid}">看不方便的話，直接在 YouTube 看 →</a></p>
  </section>
"""


def rows(rs):
    return "".join(
        "<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % r
        for r in rs)


def body():
    return f"""
<div class="wrap">
  <a class="back" href="../">← 回股市觀察</a>

  <header>
    <h1>{TITLE}</h1>
    <div class="sub">{SUB}</div>
    <hr class="rule">
  </header>

  <div class="box">
    <strong>一句話</strong>：把「感覺有效」換成「量出來有效」。30 個訊號裡，
    只有 <strong>4 個在多頭與空頭期間都是正的</strong>，<strong>6 個兩期都負（建議淘汰）</strong>，
    其餘 20 個只在單邊期間有效 —— 其中「底部進貨量」是<strong>反指標</strong>。
  </div>

  <div class="summary">
    <div class="box"><div class="big">2 年</div><div>2024-09 ~ 2026-09，494 個交易日</div></div>
    <div class="box"><div class="big">993,806 筆</div><div>日 K，涵蓋 2,059 檔</div></div>
    <div class="box"><div class="big">30 個訊號</div><div>每個都算有／對照／差距／t 值</div></div>
    <div class="box"><div class="big">4 個有效</div><div>多頭空頭兩期都正</div></div>
  </div>

  <section id="why">
    <h2><span class="dot"></span>① 為什麼要「反向驗證」</h2>
    <p>只算「訊號出現後漲多少」不能證明有用。如果一個訊號出現後 20 日平均 +1.4%，
    聽起來不錯；但同一段時間裡，<strong>沒出現這個訊號的股票平均也漲了 +1.2%</strong>，
    差距只有 +0.2% —— 那就只是市場本身在漲，不是訊號的功勞。</p>
    <p>所以每個訊號都要算 <strong>「有出現」減「沒出現（對照組）」的差距</strong>，再看 t 值。
    差距不顯著，等於雜訊。</p>
  </section>

  <section id="method">
    <h2><span class="dot"></span>② 方法：四個關鍵字</h2>
    <div class="two">
      <div class="box"><strong>兩年</strong><br>2024-09 到 2026-09，共 494 個交易日、2,059 檔、993,806 筆日 K。</div>
      <div class="box"><strong>去重</strong><br>同一檔股票連續出現的訊號只算第一天。不去重會嚴重高估顯著性
      （例：底部進貨量 672,887 筆 → 55,703 筆）。</div>
      <div class="box"><strong>分段</strong><br>多頭期間（342 天）與空頭期間（152 天）分開計算。
      市場狀態＝等權指數與其 60 日均線，含 1% 緩衝避免天天翻。</div>
      <div class="box"><strong>對照</strong><br>每個訊號都和「同期間沒出現」那一組比，報酬為後 20 個交易日收盤對收盤。</div>
    </div>
  </section>

  <section id="f1">
    <h2><span class="dot"></span>③ 發現一：對照組本身就是正的</h2>
    <p>沒出現任何訊號的股票，20 日平均報酬也是 <strong>+0.6%</strong>（多頭期間），因為這兩年整體偏多。
    所以判讀任何訊號的「+N%」時，都要先扣掉對照組。<strong>訊號的 +1% 如果對照組也是 +1%，就等於沒用。</strong></p>
  </section>

  <section id="f2">
    <h2><span class="dot"></span>④ 發現二：只有 4 個訊號兩期都正</h2>
    <div class="scroll"><table>
      <tr><th>訊號</th><th>多頭期間</th><th>空頭期間</th></tr>
      <tr><td><strong>朱-爆量二根</strong></td><td>+0.33%</td><td>+1.26%（t=4.7）</td></tr>
      <tr><td><strong>朱-早晨之星</strong></td><td>+0.47%</td><td>+0.89%（t=6.5）</td></tr>
      <tr><td><strong>跳空缺口 FD3</strong></td><td>+0.17%</td><td>+0.47%（t=8.0）</td></tr>
      <tr><td><strong>朱-MACD 柱翻揚</strong></td><td>+0.26%</td><td>+0.38%</td></tr>
    </table></div>
    <p class="dim">「兩期都正」才是不管市場怎麼走都站得住的訊號。其餘 6 個兩期都負（建議淘汰），20 個只有單邊有效。</p>
  </section>

  <section id="f3">
    <h2><span class="dot"></span>⑤ 發現三：同一個訊號會換方向</h2>
    <p>這是整份回測最重要的發現。<strong>把它們混在一起算平均，兩邊會互相抵消，得到「沒用」的錯誤結論。</strong></p>
    <div class="two">
      <div class="box"><strong>多頭期間有效（追強型）</strong><br>
        朱-長紅破 40 日高 +2.43%（t=13.0）<br>
        朱-缺口破 60 日高 +2.43%（t=11.0）<br>
        MACD 頂背離 +2.20%（t=14.1）<br>
        RSI 超買 +1.18%<br>
        均線多頭排列 +0.80%</div>
      <div class="box"><strong>空頭期間有效（抄底型）</strong><br>
        朱-爆量二根 +1.26%（t=4.7）<br>
        KD 低檔交叉 +0.99%（t=8.0）<br>
        朱-早晨之星 +0.89%（t=6.5）<br>
        RSI 超賣 +0.75%（t=6.6）<br>
        跳空缺口 FD3 +0.47%（t=8.0）</div>
    </div>
    <p>所以本站的排行頁已經改成<strong>依市場狀態分流計分</strong>：多頭只看追強型、空頭只看抄底型
    （2026-09-11 狀態：空頭，因此只用 6 個抄底型訊號）。</p>
  </section>

  <section id="f4">
    <h2><span class="dot"></span>⑥ 發現四：突破的窗口越長越強</h2>
    <div class="scroll"><table>
      <tr><th>突破窗口</th><th>差距（多頭期間）</th><th>t 值</th><th>勝率</th></tr>
      <tr><td>破 10 日高</td><td>+2.08%</td><td>10.96</td><td>45.6%</td></tr>
      <tr><td>破 20 日高</td><td>+2.70%</td><td>11.63</td><td>46.6%</td></tr>
      <tr><td>破 40 日高</td><td>+3.37%</td><td>11.90</td><td>48.1%</td></tr>
      <tr><td><strong>破 60 日高</strong></td><td><strong>+3.95%</strong></td><td>12.21</td><td>49.4%</td></tr>
    </table></div>
    <p>突破更長時間的壓力，才是真正的轉折。另外實測發現<strong>加量能條件反而變差</strong>
    （缺口＋破 40 日＋量 &gt; 1.2 倍 → +2.86%，不加是 +3.37%），所以量能條件已移除。</p>
  </section>

  <section id="f5">
    <h2><span class="dot"></span>⑦ 發現五：「底部進貨量」是反指標</h2>
    <p>舊版定義：多頭期間 <strong>-0.84%</strong>（t = -9.9）、空頭期間 <strong>-2.60%</strong>（t = -24.4）。
    <strong>有這個訊號的股票，後續表現比沒有的還差</strong>，而且統計上非常顯著。</p>
    <p>如果只算正向，會看到 <strong>+1.76%</strong>，然後誤以為它有效 —— 這是這一整份回測最好的例子：
    <strong>方向算錯，結論就完全相反。</strong></p>
  </section>

  <section id="limits">
    <h2><span class="dot"></span>⑧ 三個必須誠實說的限制</h2>
    <ul class="how">
      <li><strong>t 值仍然偏高</strong>：去重只解決「連續出現」，有些訊號（如紅K站上均線）本來就間歇性大量出現，
      樣本仍高度重疊。請當方向性參考，不要當精確的顯著性檢定。</li>
      <li><strong>這是過去的統計，不是未來的保證</strong>：市場結構改變，有效的方法也會改變。</li>
      <li><strong>沒有計算交易成本</strong>：報酬用收盤價計算，實際進出還會扣手續費與證交稅。</li>
    </ul>
  </section>

{embed()}
  <section id="howto">
    <h2><span class="dot"></span>⑨ 想看完整數字</h2>
    <ul class="how">
      <li><a href="{INTERACTIVE}">互動版表格</a>：全部 30 個訊號的「有／對照／差距／t 值」，
      可以點欄位排序，也標了哪幾個建議淘汰。顏色為台股慣例（紅＝上漲、綠＝下跌）。</li>
      <li><a href="../">股市觀察首頁</a>：每個交易日收盤後的逐檔技術條件觀察。</li>
      <li>本站排行頁已套用本頁結論：依市場狀態（多頭／空頭）只用對應的訊號計分。</li>
    </ul>
  </section>

  <div class="box">
    <strong>來源與聲明</strong>：本頁數字來自<strong>公開資料的統計回測</strong>
    （臺灣證券交易所公開資料；訊號的技術定義取自公開報導與公開著作的描述）。
    所有結果都是<strong>歷史統計</strong>，不代表未來表現。
    本頁<strong>不構成投資建議、不報牌、不預測行情、不提供買賣決策</strong>；
    投資有風險，請自行判斷並自負盈虧。
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
  table{width:100%;border-collapse:collapse;font-size:14.5px;margin:10px 0}
  th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
  th{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}
  .scroll{overflow-x:auto}
  ul.how{font-size:15.5px} ul.how li{margin:7px 0}
  .two{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:10px 0}
  .two .box{background:#fffdf6;border:2px solid var(--line);border-left:5px solid var(--blue);border-radius:14px;padding:12px 14px;font-size:14.5px}
  .dim{color:var(--soft);font-size:14px}
  .embed{position:relative;aspect-ratio:16/9;margin:12px 0 6px;background:#000;border:2px solid var(--line);border-radius:14px;overflow:hidden}
  .embed iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
  @supports not (aspect-ratio:16/9){.embed{height:0;padding-bottom:56.25%}}
  .vidlink{font-size:14.5px;margin-top:4px}
"""


def main():
    head = open(os.path.join(SITE, "stock", "index.html"), encoding="utf-8").read().split("<body")[0]
    head = re.sub(r"<title>[^<]*</title>",
                  "<title>%s：多頭、空頭分開算，只有 4 個訊號兩期都有效｜小R 頻道</title>" % TITLE,
                  head, count=1)
    head = head.replace("</style>", CSS + "</style>", 1)
    # ★ 連結深度：head 是從 stock/index.html（一層深）取得的，本頁是兩層深 → 站台連結要加一層
    #（只針對站台層資產；href="../" 與 ../20260915/ 這種同層連結要保持原樣）
    head = head.replace('href="../css/', 'href="../../css/')
    head = head.replace('href="../nav.css', 'href="../../nav.css')
    head = head.replace('src="../nav.js', 'src="../../nav.js')
    head = head.replace('src="../counter.js', 'src="../../counter.js')
    os.makedirs(OUT, exist_ok=True)
    html_out = head + "<body>\n" + body() + "\n</body>\n</html>\n"
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html_out)
    print("已產生", os.path.join(OUT, "index.html"), len(html_out), "bytes")
    print("影片內嵌:", "有" if "youtube-nocookie" in html_out else "無（還沒上傳）")


if __name__ == "__main__":
    main()
