# -*- coding: utf-8 -*-
"""把「中級」成績區塊加進 build_exam_page.py（原頁面只涵蓋初級）。

作法：
1. 在頁面產生器裡加一個 mid_section()：讀 研究_中級錯題.json 產生表格與錯題卡。
2. 換掉 h1／副標與 summary 區塊，讓同一頁同時涵蓋初級＋中級。
"""
import io, os

P = r"D:\_Richard\OpenCode\圖片生成\小R頻道_網站\build_exam_page.py"
s = io.open(P, encoding="utf-8").read()

# --- 1. 加入中級資料與產生函式（插在 def body_html 之前）---
helper = '''
MID_JSON = r"D:\\_Richard\\OpenCode\\圖片生成\\小R頻道_AI助理實測\\研究_中級錯題.json"

MID_SCORES = [
    ("科目1：人工智慧技術應用規劃", "51 / 51", "100%"),
    ("科目2：大數據處理分析與應用", "50 / 53", "94%"),
    ("科目3：機器學習技術與應用", "52 / 55", "95%"),
]


def mid_section():
    """中級成績區塊（錯題讀自研究_中級錯題.json）。"""
    import json
    rows = "".join(
        f"<tr><td>{html.escape(a)}</td><td>{b}</td><td><strong>{c}</strong></td></tr>"
        for a, b, c in MID_SCORES)
    wrong_html = ""
    try:
        w = json.load(io.open(MID_JSON, encoding="utf-8"))["wrong"]
        cards = []
        for x in w:
            cards.append(f"""
  <article class="q">
    <h3>{html.escape(x['sub'][:3])}　第 {x['no']} 題｜{html.escape(x['topic'])}</h3>
    <ul class="ans">
      <li class="mine"><span>我的選答</span>{html.escape(x['my'])}</li>
      <li class="off"><span>官方答案</span>{html.escape(x['official'])}</li>
    </ul>
    <p class="why"><strong>官方解析</strong>：{html.escape((x['explanation'] or '')[:260])}</p>
  </article>""")
        wrong_html = "".join(cards)
    except Exception as e:
        wrong_html = f"<p class=\\"dim\\">（錯題資料讀取失敗：{html.escape(str(e))}）</p>"
    return f"""
  <h2><span class="dot"></span>中級：115 年第一次（159 題，三科完整考卷）</h2>
  <div class="summary">
    <div class="box"><div class="big">153 / 159</div><div>總分 96.2%（科目1 滿分）</div></div>
    <div class="box"><div class="big">100%</div><div>科目1：人工智慧技術應用規劃（51/51）</div></div>
    <div class="box"><div class="big">6 題</div><div>總共只錯 6 題（科目2 錯 3、科目3 錯 3）</div></div>
    <div class="box"><div class="big">159 題</div><div>官方公告試題三科，作答前答案欄已移除</div></div>
  </div>
  <div class="scroll"><table>
    <tr><th>科目</th><th>得分</th><th>比率</th></tr>
    {rows}
  </table></div>
  <p class="dim">選答分布 A37／B43／C42／D37（分布平均，可確認不是亂猜）。</p>

  <div class="note warn">
    <strong>這一卷有 2 題的題庫「正解」與它自己的解析互相矛盾</strong>（科目2 第 46 題、科目3 第 52 題），
    因此 96.2% 應視為<strong>約 96～98% 的區間</strong>；公開引用前需對 iPAS 官方 PDF 逐題抽查。
  </div>

  <h2><span class="dot"></span>中級錯的 6 題</h2>
  {wrong_html}
"""


'''
anchor = "def body_html():"
assert anchor in s
s = s.replace(anchor, helper + anchor, 1)

# --- 2. 換掉標題與 summary ---
s = s.replace('<h1>AI 助理去考試：iPAS「AI 應用規劃師（初級）」</h1>',
              '<h1>AI 助理去考試：iPAS「AI 應用規劃師（初級＋中級）」</h1>')
s = s.replace('<div class="sub">用官方公告試題實測　·　實測日期 2026-09-14　·　及格 70 分／科</div>',
              '<div class="sub">用官方公告試題實測　·　初級 2026-09-14、中級 2026-09-16　·　及格 70 分／科</div>')
old_boxes = '''    <div class="box"><div class="big">2 題</div><div>總共只錯這兩題（都在 114 年第四梯次）</div></div>
    <div class="box"><div class="big">200 題</div><div>兩份官方考卷（各 100 題、兩科），作答前答案欄已移除</div></div>'''
new_boxes = '''    <div class="box"><div class="big">2 題</div><div>初級總共只錯這兩題（都在 114 年第四梯次）</div></div>
    <div class="box"><div class="big">159 題</div><div>中級 115 年第一次（三科完整考卷）→ 153/159</div></div>'''
assert old_boxes in s
s = s.replace(old_boxes, new_boxes, 1)

# --- 3. 把中級區塊插在「錯的那兩題」之前 ---
anchor2 = '  <h2><span class="dot"></span>錯的那兩題（這份報告最有價值的部分）</h2>'
assert anchor2 in s
s = s.replace(anchor2, '{mid_section()}\n' + anchor2, 1)

# --- 4. 結論區塊補一句中級 ---
s = s.replace('<li>針對 iPAS 初級這兩科的<strong>學科知識</strong>，AI 助理已能在官方公告試題上取得 96～100 分（及格 70 分）。</li>',
              '<li>針對 iPAS 初級這兩科的<strong>學科知識</strong>，AI 助理已能在官方公告試題上取得 96～100 分（及格 70 分）。</li>\n        <li>中級（三科、159 題）同樣在官方公告試題上取得 <strong>153/159＝96.2%</strong>。</li>')
# --- 5. 初級錯題標題改清楚 ---
s = s.replace('錯的那兩題（這份報告最有價值的部分）', '初級錯的那兩題（這份報告最有價值的部分）')

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("✅ build_exam_page.py 已更新（含中級區塊）")
print("檢查關鍵字:", all(k in s for k in ('mid_section', 'MID_SCORES', '153 / 159', '初級＋中級')))
