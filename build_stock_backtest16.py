# -*- coding: utf-8 -*-
"""產生「16 條評分條件回測」頁：/stock/backtest16/

資料來源：小R頻道_股市觀察/backtest16/results.csv（h20）與 results_h5.csv、results_h10.csv
用法：python build_stock_backtest16.py [網站根目錄]
"""
import csv
import html
import os
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "/home/littler5071/opencode/圖片生成/小R頻道_網站"
OUT = os.path.join(SITE, "stock", "backtest16")
SRC = "/home/littler5071/opencode/圖片生成/小R頻道_股市觀察/backtest16"

TITLE = "16 條評分條件回測：多頭有效的，空頭期間全部反向｜小R頻道"
DESC = ("把每日評分與條件追蹤用的 16 條條件（8 條好條件、8 條壞條件）放進 458 個交易日、"
        "829,492 筆日 K 做多空分段回測：多頭期間趨勢條件有效，空頭期間同一組條件全部反向。")


def load(name):
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fnum(v, digits=2):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def pct(v, digits=2, dash="—"):
    x = fnum(v)
    if x is None:
        return dash
    return f"{x * 100:+.{digits}f}%"


def tnum(v):
    x = fnum(v)
    if x is None:
        return "—"
    return f"{x:+.2f}"


def cls_gap(v):
    x = fnum(v)
    if x is None:
        return ""
    return "up" if x > 0 else ("dn" if x < 0 else "")


def classify(r):
    b, s = fnum(r.get("bull_gap")), fnum(r.get("bear_gap"))
    if b is None or s is None:
        return "資料不足"
    if b > 0 and s > 0:
        return "兩期都正"
    if b < 0 and s < 0:
        return "兩期都負"
    return "單邊有效"


def rows_main(h20):
    out = []
    for r in h20:
        out.append(
            "<tr>"
            f"<td>{html.escape(r['condition'])}</td>"
            f"<td class='dim'>{html.escape(r['kind'])}</td>"
            f"<td class='m-hide'>{pct(r['bull_sig_fwd'])}</td><td class='m-hide'>{pct(r['bull_ctl_fwd'])}</td>"
            f"<td class='{cls_gap(r['bull_gap'])}'><b>{pct(r['bull_gap'])}</b></td><td class='m-hide'>{tnum(r['bull_t'])}</td>"
            f"<td class='m-hide'>{pct(r['bear_sig_fwd'])}</td><td class='m-hide'>{pct(r['bear_ctl_fwd'])}</td>"
            f"<td class='{cls_gap(r['bear_gap'])}'><b>{pct(r['bear_gap'])}</b></td><td class='m-hide'>{tnum(r['bear_t'])}</td>"
            f"<td class='m-hide'>{int(float(r['n_sig_dedup'])):,}</td>"
            f"<td>{classify(r)}</td>"
            "</tr>")
    return "\n".join(out)


def rows_indep(rows):
    out = []
    for r in rows:
        out.append(
            "<tr>"
            f"<td>{html.escape(r['condition'])}</td>"
            f"<td class='dim'>{html.escape(r['kind'])}</td>"
            f"<td class='{cls_gap(r['bull_gap'])}'>{pct(r['bull_gap'])}</td><td>{tnum(r['bull_t'])}</td>"
            f"<td class='{cls_gap(r['bear_gap'])}'>{pct(r['bear_gap'])}</td><td>{tnum(r['bear_t'])}</td>"
            f"<td>{int(float(r['n_sig_dedup'])):,}</td>"
            "</tr>")
    return "\n".join(out)


def rows_robust(h5, h10, h20):
    idx5 = {r["condition"]: r for r in h5}
    idx10 = {r["condition"]: r for r in h10}
    out = []
    for r in h20:
        c = r["condition"]
        cells = [f"<td>{html.escape(c)}</td>"]
        for idx in (idx5, idx10, {c: r}):
            rr = idx.get(c, {})
            hide = " m-hide" if (idx is idx5 or idx is idx10) else ""
            cells.append(f"<td class='{cls_gap(rr.get('bull_gap'))}{hide}'>{pct(rr.get('bull_gap'))}</td>")
            cells.append(f"<td class='{cls_gap(rr.get('bear_gap'))}{hide}'>{pct(rr.get('bear_gap'))}</td>")
        out.append("<tr>" + "".join(cells) + "</tr>")
    return "\n".join(out)


def main():
    h20, h10, h5 = load("results.csv"), load("results_h10.csv"), load("results_h5.csv")
    indep = load("results_independent.csv")
    if not h20:
        sys.exit("找不到 results.csv")
    os.makedirs(OUT, exist_ok=True)

    cls_count = {}
    for r in h20:
        k = classify(r)
        cls_count[k] = cls_count.get(k, 0) + 1
    both_pos = [r["condition"] for r in h20 if classify(r) == "兩期都正"]
    both_neg = [r["condition"] for r in h20 if classify(r) == "兩期都負"]
    bear_pos = sorted([r for r in h20 if (fnum(r["bear_gap"]) or 0) > 0.0015],
                      key=lambda r: -fnum(r["bear_gap"]))[:5]
    bull_top = sorted([r for r in h20 if r["kind"] == "GOOD"],
                      key=lambda r: -fnum(r["bull_gap"] or 0))[:3]

    boxes = [
        ("回測樣本", "829,492 筆", "1,992 檔・458 個交易日（2024/12/02–2026/10/21）"),
        ("多頭期間", "535,939 筆", "等權指數在 60 日均線之上"),
        ("空頭期間", "293,553 筆", "等權指數在 60 日均線之下"),
        ("多頭最強條件", f"+{fnum(bull_top[0]['bull_gap'])*100:.2f}%" if bull_top else "—",
         f"{bull_top[0]['condition']}（t={fnum(bull_top[0]['bull_t']):.1f}）" if bull_top else ""),
        ("空頭期間反向", f"{fnum(min(h20, key=lambda r: fnum(r['bear_gap']) or 0)['bear_gap'])*100:+.2f}%",
         "同一組好條件在空頭期間的後 20 日差距"),
        ("對照組（空頭）", "+2.2% ~ +3.2%", "什麼訊號都沒有的股票，空頭期間 20 日平均"),
    ]
    box_html = "\n".join(
        f'<div class="box"><div class="big">{html.escape(v)}</div>{html.escape(t)}<br><span class="dim">{html.escape(d)}</span></div>'
        for t, v, d in boxes)

    bear_rows = "\n".join(
        f"<tr><td>{html.escape(r['condition'])}</td>"
        f"<td class='up'><b>{pct(r['bear_gap'])}</b></td><td>{tnum(r['bear_t'])}</td>"
        f"<td>{int(float(r['n_sig_dedup'])):,}</td></tr>" for r in bear_pos)

    page = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<meta name="description" content="{html.escape(DESC)}">
<link rel="stylesheet" href="../../css/index.css">
<style>
  main{{max-width:980px;margin:0 auto;padding:22px 22px 46px}}
  h1{{margin:6px 0 10px}}
  p,li{{max-width:70ch}}
  h2{{font-size:clamp(19px,3.2vw,25px);margin:34px 0 8px;display:flex;align-items:center;gap:10px}}
  h2 .dot{{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}}
  a.back{{display:inline-block;margin:2px 0 12px;font-size:14.5px;text-decoration:none;color:var(--blue);border-bottom:1.5px solid currentColor}}
  .summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:6px 0 18px}}
  .summary .box{{background:#fffdf6;border:2px solid var(--line);border-radius:14px;padding:12px 14px;font-size:13.5px;color:var(--soft)}}
  .summary .big{{font-size:22px;color:var(--ink);margin-bottom:2px}}
  table{{width:100%;border-collapse:collapse;font-size:14px;margin:10px 0}}
  th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
  th{{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap;cursor:pointer}}
  .scroll{{overflow-x:auto}}
  .up{{color:var(--red)}} .dn{{color:var(--green)}}
  .dim{{color:var(--soft);font-size:13.5px}}
  @media (max-width:720px){{
    main{{padding:14px 16px 34px}}
    .m-hide{{display:none!important}}
    h1{{font-size:22px;line-height:1.35}}
    h2{{font-size:19px;margin:26px 0 6px}}
    table{{font-size:13.5px}}
    th,td{{padding:6px 8px}}
    .summary{{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}}
    .summary .big{{font-size:19px}}
    ul.how,ol.key{{font-size:15px}}
    .scroll{{-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:12px;padding:2px}}
    table{{margin:4px 0}}
    th,td{{padding:7px 9px}}
    h2{{margin:26px 0 6px}}
    ul.how li,ol.key li{{margin:6px 0}}
  }}
  ul.how{{font-size:15.5px}} ul.how li{{margin:7px 0}}
  ol.key{{font-size:15.5px}} ol.key li{{margin:8px 0}}
</style>
</head>
<body>
<main>
<a class="back" href="../">← 回股市觀察</a>
<h1>16 條評分條件回測：多頭有效的，空頭期間全部反向</h1>
<p class="dim">每日收盤評分與 19:00 條件追蹤用的 8 條「好條件」與 8 條「壞條件」，過去從來沒有被驗證過。
這頁把它們放進 458 個交易日、829,492 筆日 K，用同一套方法（去重、多空分段、對照組、Welch t、超額報酬）算一次。</p>

<div class="summary">
{box_html}
</div>

<h2><span class="dot"></span>怎麼讀這張表</h2>
<ul class="how">
<li>「有」＝訊號出現那組的後 20 日平均報酬；「對照」＝同一期間<b>沒出現</b>的股票。</li>
<li>要看的不是「有」本身，是<b>差距＝有 − 對照</b>，再加 t 值與樣本數；差距不顯著就是雜訊。</li>
<li>多頭（等權指數 &gt; 60 日均線）與空頭分開算，因為實測同一個條件在兩期<b>方向相反</b>。</li>
<li>顏色照台股慣例：<span class="up">紅＝上漲</span>、<span class="dn">綠＝下跌</span>。</li>
</ul>

<h2><span class="dot"></span>① 16 條條件（後 20 日報酬，點欄位標題可排序）</h2>
<div class="scroll">
<table id="t1">
<thead><tr>
<th>條件</th><th>類別</th><th class="m-hide">多頭 有</th><th class="m-hide">多頭 對照</th><th>多頭 差距</th><th class="m-hide">多頭 t</th>
<th class="m-hide">空頭 有</th><th class="m-hide">空頭 對照</th><th>空頭 差距</th><th class="m-hide">空頭 t</th><th class="m-hide">去重樣本</th><th>判定</th>
</tr></thead>
<tbody>
{rows_main(h20)}
</tbody></table>
</div>

<h2><span class="dot"></span>② 期限穩健性：後 5／10／20 日</h2>
<p class="dim">同一個條件在三個期限方向要一致才算穩。方向反覆的（量增下跌、跌破前低）不要用。</p>
<div class="scroll">
<table>
<thead><tr><th>條件</th><th class="m-hide">5日 多頭</th><th class="m-hide">5日 空頭</th><th class="m-hide">10日 多頭</th><th class="m-hide">10日 空頭</th><th>20日 多頭</th><th>20日 空頭</th></tr></thead>
<tbody>
{rows_robust(h5, h10, h20)}
</tbody></table>
</div>

<h2><span class="dot"></span>③ 空頭期間真正有效的條件</h2>
<p class="dim">空頭期間趨勢條件反向，真正有正差距的是「超跌反轉」這一組。</p>
<div class="scroll">
<table>
<thead><tr><th>條件</th><th>空頭 差距</th><th>空頭 t</th><th>去重樣本</th></tr></thead>
<tbody>
{bear_rows}
</tbody></table>
</div>

<h2><span class="dot"></span>④ 獨立樣本版（每 20 個交易日只取一筆）</h2>
<p class="dim">上面的表是「去重」後的結果，但訊號常常連續出現、樣本彼此重疊，t 值會偏高。
這一版把<b>同一檔股票在 20 個交易日內只留第一筆</b>，樣本完全互不重疊，是比較保守、也比較誠實的版本。</p>
<div class="scroll">
<table>
<thead><tr><th>條件</th><th>類別</th><th>多頭 差距</th><th>多頭 t</th><th>空頭 差距</th><th>空頭 t</th><th>樣本數</th></tr></thead>
<tbody>
{rows_indep(indep)}
</tbody></table>
</div>
<p class="dim">獨立樣本下有三個結論要修正：① 「外資買超」仍然兩期都正，但 t 從 7～9 掉到約 2，屬於<b>弱證據</b>；
② 「收盤跌破前一日低點」多空兩期都接近 0（t=0.35／−0.64）→ 這條已經沒用；
③ 「外資賣超」反而變成兩期都負（−0.49／−0.24），可以放進空頭的壞條件。</p>

<h2><span class="dot"></span>結論</h2>
<ol class="key">
<li><b>多頭期間，這套評分是對的</b>：突破頸線 +2.09%（t=12.2）、月線向上 +1.74%、頭頭高 +1.09%、站上月線 +1.07%。</li>
<li><b>空頭期間，同一組條件全部反向</b>（−0.88% ~ −2.08%，t −3.7 ~ −14.7）→ 空頭時「好條件最多」其實偏弱。</li>
<li><b>「相對大盤強」該拿掉</b>：三個期限都 ≈0（+0.03%，t 0.67），沒有分辨力。</li>
<li><b>「量增下跌（出貨）」不是壞條件</b>：後 20 日兩期都是正的（+0.24%／+0.31%）。</li>
<li><b>唯一兩期都正的是「外資買超」</b>：多頭 +0.39%、空頭 +0.55%（去重版 t=7.3／9.4；<b>獨立樣本版只剩 t≈2</b>）→
方向對、但不要說得太滿。「外資賣超」在獨立樣本下反而兩期都負（−0.49／−0.24）。</li>
<li><b>要改看超額報酬</b>：空頭期間連對照組都漲 +2.2%~+3.2%，只看原始報酬會把大盤的漲跌算成選股能力。</li>
</ol>

<h2><span class="dot"></span>方法與限制</h2>
<ul class="how">
<li>資料：證交所 <code>MI_INDEX(type=ALL)</code> 與櫃買中心逐日收盤行情，2024-09-01 起抓、清洗後 829,492 筆 / 1,992 檔 / 458 交易日。</li>
<li>濾除：ETF／ETN（00 開頭）、收盤 ≤ 0、單筆後 20 日報酬超過 ±100% 的資料瑕疵。</li>
<li>報酬在 <code>groupby(股票)</code> 內計算；訊號連續多天出現只留每段第一天（去重）。</li>
<li>市場分段：等權指數對 60 日均線、±1% 緩衝，避免天天翻。對照組在各期間內各自計算。</li>
<li>「突破頸線」以「最近 3 個已確認波高的最大值」近似原版的頸線群聚平均。</li>
<li>外資籌碼取自證交所 T86 與櫃買三大法人日報（逐日下載 458 天，其中 4 天檔案截斷未取得，已跳過）。</li>
<li>t 值在高度重疊的訊號上會偏高，當方向性參考；過去不等於未來，也未計交易成本。</li>
</ul>
<p class="dim">延伸閱讀：<a href="../backtest/">30 個朱家泓式訊號的回測（正向 vs 反向對照）</a> ｜
<a href="../tracker/">條件追蹤：好條件 Top10 vs 對照組</a></p>
<p class="dim">本頁只用公開資料做統計整理，不構成任何投資建議。</p>
</main>
<script>
document.querySelectorAll('#t1 th').forEach(function(th, i){{
  th.addEventListener('click', function(){{
    var tb = th.closest('table').tBodies[0];
    var rows = Array.prototype.slice.call(tb.rows);
    var num = function(c){{ var t = c.innerText.replace(/[^0-9+\\-.%]/g,'').replace('%',''); return parseFloat(t); }};
    var asc = th.dataset.asc === '1';
    rows.sort(function(a, b){{
      var x = num(a.cells[i]), y = num(b.cells[i]);
      if (isNaN(x) && isNaN(y)) return 0;
      if (isNaN(x)) return 1;
      if (isNaN(y)) return -1;
      return asc ? x - y : y - x;
    }});
    th.dataset.asc = asc ? '0' : '1';
    rows.forEach(function(r){{ tb.appendChild(r); }});
  }});
}});
</script>
</body>
</html>
"""
    p = os.path.join(OUT, "index.html")
    open(p, "w", encoding="utf-8").write(page)
    print("寫出", p, len(page), "chars｜兩期都正", both_pos, "｜兩期都負", both_neg)


if __name__ == "__main__":
    main()
