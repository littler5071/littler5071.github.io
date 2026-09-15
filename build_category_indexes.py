# -*- coding: utf-8 -*-
"""自動產生分類頁的「全部集數」清單（可重複執行）。

- `stock/index.html`：掃描 stock/<YYYYMMDD>/index.html，抽出日期、加權指數與漲跌、市場廣度、
  五項全滿足名單，產生「日期｜重點｜連結」表格（最新在上），並把最新兩天做成卡片。
- `toeic/index.html`：掃描 toeic/*/index.html，列出題組（Part、標題、一句說明、連結）。

用法：python build_category_indexes.py [網站根目錄]
"""
import os, re, sys, glob, html

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"

HEAD = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<style>
  :root{{--paper:#f6f1e6;--ink:#4a4640;--soft:#78706a;--line:#d9d1c2;--red:#bf4a3a;--blue:#364e70;--leaf:#2f8f63;--card:#fffdf6}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);
    font-family:"Kaiti TC","標楷體",KaiTi,"Microsoft JhengHei",system-ui,sans-serif;
    line-height:1.75;background-image:radial-gradient(rgba(0,0,0,.035) 1px,transparent 1px);background-size:26px 26px}}
  .wrap{{max-width:900px;margin:0 auto;padding:34px 22px 80px}}
  header{{text-align:center;margin-bottom:6px}}
  h1{{font-size:clamp(30px,6vw,44px);margin:0 0 4px;letter-spacing:.05em}}
  .sub{{color:var(--blue);font-size:clamp(15px,2.6vw,19px)}}
  .rule{{height:6px;width:200px;margin:14px auto 30px;border:0;
        background:repeating-linear-gradient(90deg,var(--red) 0 12px,transparent 12px 20px);border-radius:3px;opacity:.75}}
  h2{{font-size:clamp(19px,3.2vw,25px);margin:38px 0 10px;display:flex;align-items:center;gap:10px}}
  h2 .dot{{width:14px;height:14px;border:3px solid var(--red);border-radius:50%;flex:none}}
  .card{{background:var(--card);border:2px solid var(--line);border-radius:16px;padding:18px 20px;
        margin:0 0 16px;box-shadow:2px 3px 0 rgba(74,70,64,.06)}}
  .tag{{display:inline-block;font-size:12.5px;padding:2px 10px;border-radius:999px;
       border:1.5px solid currentColor;margin-right:8px;vertical-align:2px;color:var(--leaf)}}
  .card h3{{margin:6px 0 4px;font-size:clamp(17px,2.9vw,21px)}}
  .card p{{margin:0 0 10px;color:var(--soft);font-size:15px}}
  a.btn{{display:inline-block;text-decoration:none;color:var(--blue);border-bottom:2px solid var(--blue);
        padding-bottom:1px;font-size:15.5px}}
  a.btn:hover{{color:var(--red);border-color:var(--red)}}
  table{{width:100%;border-collapse:collapse;margin:6px 0 4px;font-size:14.5px}}
  th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
  th{{background:rgba(255,253,246,.9);font-weight:400;color:var(--soft);white-space:nowrap}}
  td.d{{white-space:nowrap;color:var(--soft)}}
  td a{{color:var(--blue);text-decoration:none;border-bottom:1.5px solid rgba(54,78,112,.35)}}
  td a:hover{{color:var(--red);border-color:var(--red)}}
  .note{{margin-top:34px;padding:15px 18px;border:2px dashed var(--line);border-radius:14px;
        color:var(--soft);font-size:14px;background:rgba(255,253,246,.6)}}
  footer{{margin-top:30px;text-align:center;color:var(--soft);font-size:13.5px}}
  a{{color:var(--blue)}}
  .scroll{{overflow-x:auto}}
</style>
</head>
<body>
<div class="wrap">
"""

FOOT = """
  <footer>
    小R 頻道 · {cat} ｜ <a href="https://www.youtube.com/channel/UCl-5q4SoIybOvibMN1kRpsw">youtube.com/@小R-c4q</a>
  </footer>
</div>
</body>
</html>
"""


def txt(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()


def build_stock():
    """從每日頁面抽出摘要，產生股市觀察分類頁。"""
    rows, cards = [], []
    days = sorted([os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(SITE, "stock", "*", "index.html"))
                   if re.fullmatch(r"\d{8}", os.path.basename(os.path.dirname(p)))], reverse=True)
    for i, d in enumerate(days):
        h = open(os.path.join(SITE, "stock", d, "index.html"), encoding="utf-8").read()
        date_tw = f"{d[:4]}/{d[4:6]}/{d[6:]}"
        big = re.search(r'<div class="big[^"]*">([^<]+)</div>\s*<div>加權指數\s*([^<]*)</div>', h)
        idx = txt(big.group(1)) if big else "-"
        chg = txt(big.group(2)) if big else ""
        bd = re.search(r'<div class="big">([^<]+)</div><div>上市個股上漲／下跌家數</div>', h)
        breadth = txt(bd.group(1)) if bd else "-"
        five = re.search(r"<strong>五項全滿足</strong>([^<]*(?:<[^>]+>[^<]*)*?)<br>", h)
        five_txt = txt(five.group(1)).lstrip("：: ") if five else ""
        scope = re.search(r'<div class="sub">([^<]+)</div>', h)
        scope_txt = txt(scope.group(1)) if scope else ""
        cond = re.search(r"<strong>條件統計</strong>：(.*?)<br>", h)
        cond_txt = txt(cond.group(1))[:90] + "…" if cond else ""
        focus = five_txt.split("；")[0][:70] if five_txt else ""
        rows.append((date_tw, f"{idx}　{chg}", breadth, focus, d, scope_txt, cond_txt))
        if i < 2:
            cards.append(f"""  <div class="card">
    <span class="tag">{'最新' if i == 0 else '已上線'}</span>
    <h3>{date_tw} 收盤後觀察：{idx}　{chg}</h3>
    <p>上市個股上漲／下跌 {breadth}；{focus}。</p>
    <a class="btn" href="{d}/">逐檔 K 線圖與線型分析 →</a>
  </div>""")
    # 盤中觀察（目錄名為 <日期>-intraday）
    intr = sorted([os.path.basename(os.path.dirname(p)) for p in
                   glob.glob(os.path.join(SITE, "stock", "*-intraday", "index.html"))], reverse=True)
    icards = []
    for d in intr:
        h = open(os.path.join(SITE, "stock", d, "index.html"), encoding="utf-8").read()
        label = f"{d[:4]}/{d[4:6]}/{d[6:8]}"
        sub = re.search(r'<div class="sub">([^<]+)</div>', h)
        sub_txt = txt(sub.group(1)) if sub else ""
        snap = re.search(r"(\d{2}:\d{2}) 即時快照", sub_txt)
        big = re.search(r'<div class="big[^"]*">([^<]+)</div>\s*<div>加權指數\s*([^<]*)</div>', h)
        idx = txt(big.group(1)) if big else "-"
        chg = txt(big.group(2)) if big else ""
        bd = re.search(r'<div class="big">(\d+) / (\d+)</div><div>候選池', h)
        breadth = f"{bd.group(1)} / {bd.group(2)}" if bd else "-"
        snap_t = snap.group(1) if snap else ""
        icards.append('<div class="card"><span class="tag" style="color:#8a6d1f">盤中快照</span>'
                      '<h3>' + label + ' ' + snap_t + ' 盤中觀察：' + idx + '　' + chg + '</h3>'
                      '<p>候選池內上漲／下跌 ' + breadth + '；當日盤中成交金額前 50 檔（上市 35＋上櫃 15）。'
                      '<strong>盤中是快照、不是收盤定案。</strong></p>'
                      '<a class="btn" href="' + d + '/">盤中逐檔快照 →</a></div>')

    table = "\n".join(
        f'    <tr><td class="d">{r[0]}</td><td>{r[1]}</td><td>{r[3] or "—"}</td>'
        f'<td><a href="{r[4]}/">逐檔分析 →</a></td></tr>' for r in rows)
    body = HEAD.format(title="股市觀察｜小R 頻道",
                       desc="小R 頻道的股市觀察：每個交易日成交金額上市前 35 名與上櫃前 15 名的技術線型逐檔分析，只用公開資料。")
    body += """  <header>
    <h1>股市觀察</h1>
    <div class="sub">公開資料的觀察與記錄・不構成投資建議</div>
    <hr class="rule">
  </header>
""" + "\n".join(cards + icards) + f"""
  <h2><span class="dot"></span>全部觀察紀錄（{len(rows)} 個交易日）</h2>
  <div class="scroll">
  <table>
    <tr><th>資料日</th><th>加權指數</th><th>五項全滿足</th><th></th></tr>
{table}
  </table>
  </div>
  <div class="note">
    統計範圍為當日成交金額<strong>上市前 35 名 ＋ 上櫃前 15 名</strong>（4 位數代號個股，不含 ETF／權證）；
    資料來源為證交所與櫃買中心的每日收盤行情、三大法人（上櫃另有融資融券）公開資料，以及 Yahoo 股市日線。<br>
    <strong>內容為公開資料的整理與觀察，不構成任何投資建議</strong>；不報牌、不預測、不下買賣決策。
  </div>
""" + FOOT.format(cat="股市觀察")
    open(os.path.join(SITE, "stock", "index.html"), "w", encoding="utf-8").write(body)
    return len(rows)


def build_toeic():
    dirs = [os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(SITE, "toeic", "*", "index.html"))]
    order = {"p3-full": 0, "p2-sample": 1}
    dirs = sorted([d for d in dirs if d in order], key=lambda d: order[d])
    rows, cards = [], []
    for i, d in enumerate(dirs):
        h = open(os.path.join(SITE, "toeic", d, "index.html"), encoding="utf-8").read()
        t = txt(re.search(r"<title>(.*?)</title>", h, re.S).group(1)).split("｜")[0]
        sub = re.search(r'<div class="sub">([^<]+)</div>', h)
        sub_txt = txt(sub.group(1)) if sub else ""
        nq = len(re.findall(r'class="q" data-q=', h))
        rows.append((t, sub_txt, nq, d))
        if i < 2:
            cards.append(f"""  <div class="card">
    <span class="tag">{'最新' if i == 0 else '已上線'}</span>
    <h3>{t}</h3>
    <p>{sub_txt}（{nq} 題・可線上作答計分）</p>
    <a class="btn" href="{d}/">題目、詳解與音檔 →</a>
  </div>""")
    table = "\n".join(
        f'    <tr><td class="d">{r[0]}</td><td>{r[1]}</td><td>{r[2]} 題</td>'
        f'<td><a href="{r[3]}/">進入 →</a></td></tr>' for r in rows)
    body = HEAD.format(title="多益英文｜小R 頻道",
                       desc="小R 頻道的多益英文練習：題目自行撰寫、聲音為語音合成，未使用 ETS 的試題或音檔；附中文詳解與音檔。")
    body += """  <header>
    <h1>多益英文</h1>
    <div class="sub">題目自行撰寫・語音合成・節奏依實際考場</div>
    <hr class="rule">
  </header>
""" + "\n".join(cards) + f"""
  <h2><span class="dot"></span>全部題組（{len(rows)}）</h2>
  <div class="scroll">
  <table>
    <tr><th>題組</th><th>內容</th><th>題數</th><th></th></tr>
{table}
  </table>
  </div>
  <div class="note">
    題目與語音<strong>全部自行製作</strong>：題目自行撰寫、聲音由語音合成產生，<strong>不使用 ETS 的試題或音檔</strong>；
    「TOEIC／多益」是 ETS 的註冊商標，此處僅為描述性使用（指相同題型結構），不代表 ETS 授權、合作或認可。
  </div>
""" + FOOT.format(cat="多益英文")
    open(os.path.join(SITE, "toeic", "index.html"), "w", encoding="utf-8").write(body)
    return len(rows)


if __name__ == "__main__":
    print("股市觀察：", build_stock(), "個交易日")
    print("多益英文：", build_toeic(), "個題組")
