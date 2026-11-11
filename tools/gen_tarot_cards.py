# -*- coding: utf-8 -*-
"""產生塔羅牌義總覽／教學頁：/tarot/cards/"""
import html as H
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tarot_data import CARDS, MAJORS, SUITS  # noqa: E402

SITE = os.path.dirname(HERE)
OUT_DIR = os.path.join(SITE, "tarot", "cards")
os.makedirs(OUT_DIR, exist_ok=True)

# ── 22 張大牌的「故事／象徵」────────────────────────────────
MAJOR_STORY = {
    "愚者": "懸崖邊的青年，一隻腳已經踏出去，狗在後面叫。他不是不怕，是還沒學會怕——所以這種勇氣最乾淨，也最容易摔。",
    "魔術師": "桌上擺著杖、杯、劍、幣四樣工具，他一手指天一手點地，意思是：上頭的想法要真的落到地上，才算數。",
    "女祭司": "坐在兩根柱子中間，身後是石榴簾幕，手上的卷軸只露出一角。她知道得比說出來的多，因為有些事一說破就不準了。",
    "皇后": "麥田、森林、流水，她坐在豐收裡面。這張牌講的不是浪漫，是「照顧」與「讓它長大」需要時間。",
    "皇帝": "石頭王座、盔甲、腳邊的山羊頭。他代表規矩、界線，還有那句最難說出口的話：「這件事我負責。」",
    "教皇": "兩名信徒跪在階下，他把鑰匙交出去。象徵傳承：有些東西不必自己重新發明，問對人比想破頭快。",
    "戀人": "伊甸園裡的兩個人與天上的天使。重點其實不是愛情，是「選擇」——你選的那邊，得跟你的價值觀對得上。",
    "戰車": "兩隻人面獅身獸拉著車，一黑一白。牠們往不同方向走，卻同時被你駕住——這就是意志。",
    "力量": "女子輕輕按住獅子的嘴，沒有武器。她不是壓制，是安撫；溫柔比蠻力更難，也更持久。",
    "隱者": "提著燈站在雪地高處，燈裡只有一顆星。光只照得到下一步，所以只能走一步看一步。",
    "命運之輪": "輪子上三個生物隨輪轉動：往上、到頂、往下。局面會轉，你能決定的只有自己怎麼站。",
    "正義": "一手劍、一手天秤。劍切開事實，秤量責任；這張牌不談運氣，只談「有沒有做到」。",
    "倒吊人": "自願倒吊在樹上，表情卻是平靜的。換一個角度看世界，是主動的選擇，不是懲罰。",
    "死神": "白馬上的骸骨走過人群，遠方太陽正在升起。結束與開始是同一件事，只是我們通常只看到前面那半。",
    "節制": "天使把水從一杯倒到另一杯，水沒有灑出來。這張牌講比例、節奏，還有「剛剛好」。",
    "惡魔": "兩個被鏈住的人，鍊子鬆得可以自己拿下來。真正綁住你的通常不是別人，是你捨不得放的那個習慣。",
    "高塔": "閃電打中塔頂，王冠掉下來、人往下墜。倒掉的都是本來就不穩的東西——痛，但誠實。",
    "星星": "女子在池邊倒水，天上有八顆星。這是災後重建的第一口氣：不熱鬧，但方向是對的。",
    "月亮": "兩隻狗對著月亮叫，路在水裡若隱若現。看不清的時候不要硬走，這張牌在提醒你等霧散。",
    "太陽": "孩子騎著白馬，向日葵在牆後盛開。最直接的一張牌：事情就是好，不用想太多。",
    "審判": "號角響起，人們從棺木裡起身。象徵總結與回應召喚：過去的事會回來告訴你答案。",
    "世界": "舞者在花環裡，四角落四隻生物。一圈走完了，可以驗收，也可以往下一個循環走。",
}

SUIT_STORY = {
    "權杖": "火是行動與熱情：想做、想衝、想被看見。權杖牌組講的通常是「你要不要動」。",
    "聖杯": "水是情感與關係：感受、連結、失落。聖杯牌組講的通常是「你心裡怎麼了」。",
    "寶劍": "風是思考與溝通：判斷、衝突、真相。寶劍牌組講的通常是「你怎麼想、怎麼說」。",
    "錢幣": "土是現實與資源：錢、身體、時間。錢幣牌組講的通常是「現實條件夠不夠」。",
}

RANK_SCENE = {
    "一": "一顆剛掉下來的種子，還沒有形狀，但潛力最滿。",
    "二": "兩邊各站一個選擇，你正在秤哪一邊比較重。",
    "三": "第一個成果出現了，開始有人回應你。",
    "四": "把門關起來，先守住現有的東西。",
    "五": "走過一段泥地：損失與摩擦同時發生。",
    "六": "開始收到回報，也有人願意給你。",
    "七": "停下來盤點：種下去的到底長出多少。",
    "八": "低頭重複做同一件事，直到它變成能力。",
    "九": "一個人站在成果前面，離終點只差最後一步。",
    "十": "責任到頂了，該收成，或該交棒。",
    "侍者": "剛入門，什麼都想試，還在學規矩。",
    "騎士": "已經上路，速度很快，方向感還在抓。",
    "皇后": "把場面照顧好，靠的是經驗不是力氣。",
    "國王": "做最後決定，也承擔結果。",
}

MAJOR_TITLES = {
    0: "開始", 1: "創造", 2: "直覺", 3: "豐盛", 4: "秩序", 5: "傳承",
    6: "選擇", 7: "意志", 8: "勇氣", 9: "獨處", 10: "轉折", 11: "平衡",
    12: "換角度", 13: "結束", 14: "節制", 15: "執著", 16: "崩解",
    17: "希望", 18: "迷霧", 19: "清晰", 20: "總結", 21: "完成",
}


def esc(s):
    return H.escape(str(s), quote=True)


def card_block(c, idx):
    if c["arc"] == "大阿爾克那":
        story = MAJOR_STORY.get(c["n"], c["intro"])
        tag = f"大阿爾克那 {c['num']}"
        sub = MAJOR_TITLES.get(idx, "")
        title = f"{c['n']}"
        tagline = f"{tag}｜{sub}" if sub else tag
    else:
        rank = c["num"]
        suit = c["arc"]
        story = SUIT_STORY.get(suit, "") + RANK_SCENE.get(rank, "")
        title = c["n"]
        tagline = f"{suit}・{rank}｜元素：{c['el']}"
    return f"""
    <article class="card" data-key="{esc(c['n'] + ' ' + c['kw'] + ' ' + c['el'] + ' ' + c['arc'] + ' ' + c['num'])}" id="c-{esc(c['img'])}">
      <div class="thumb"><img src="../img/{esc(c['img'])}.webp" alt="{esc(c['n'])}" loading="lazy" width="360" height="600"></div>
      <div class="body">
        <h3>{esc(title)}<span class="tag">{esc(tagline)}</span></h3>
        <p class="kw">{esc(c['kw'])}</p>
        <p><b>象徵</b>{esc(story)}</p>
        <p class="up"><b>正位</b>{esc(c['up'])}</p>
        <p class="rev"><b>逆位</b>{esc(c['rev'])}</p>
      </div>
    </article>"""


majors = CARDS[:22]
minors = {s: [c for c in CARDS if c["arc"] == s] for s in SUITS}

sec_major = "\n".join(card_block(c, i) for i, c in enumerate(majors))
sec_suits = ""
for suit in SUITS:
    blocks = "\n".join(card_block(c, 0) for c in minors[suit])
    sec_suits += f"""
  <section class="group" id="g-{suit}">
    <h2>{suit}（14 張）<span class="sub">元素：{SUITS[suit]['el']}｜{SUITS[suit]['theme']}</span></h2>
    <p class="gintro">{esc(SUIT_STORY[suit])}</p>
    {blocks}
  </section>"""

PAGE = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>78 張塔羅牌義總覽與教學｜小R頻道</title>
<meta name="description" content="完整 78 張塔羅牌義：22 張大阿爾克那與權杖、聖杯、寶劍、錢幣四花色，含象徵故事、正位與逆位解說，以及三牌陣讀法教學。">
<link rel="canonical" href="https://littler5071.github.io/tarot/cards/">
<meta property="og:title" content="78 張塔羅牌義總覽與教學｜小R頻道">
<meta property="og:description" content="每張牌的故事、象徵、正位與逆位，一次看完。">
<meta property="og:type" content="article">
<style>
  :root{{--ink:#f2ead6;--sub:#a9b2c9;--gold:#c9a227;--gold2:#e8cd79;--line:rgba(201,162,39,.32)}}
  *{{box-sizing:border-box}}
  body{{margin:0;color:var(--ink);background:
      radial-gradient(1100px 520px at 50% -8%,#1b2447 0%,transparent 62%),linear-gradient(180deg,#0b1020,#0a0e1a);
    font-family:"Noto Serif TC","Songti TC","PingFang TC",serif;-webkit-text-size-adjust:100%}}
  .wrap{{max-width:860px;margin:0 auto;padding:26px clamp(15px,4.6vw,38px) 70px}}
  header.top{{text-align:center;margin:6px 0 18px}}
  .brand{{font-size:12.5px;letter-spacing:.34em;color:var(--gold);opacity:.85}}
  h1{{font-size:clamp(22px,5vw,32px);margin:8px 0 8px;letter-spacing:.05em}}
  .lead{{color:var(--sub);font-size:14px;line-height:1.8;margin:0}}
  .backbtn{{position:fixed;left:12px;top:14px;z-index:15;width:34px;height:34px;display:inline-flex;align-items:center;
    justify-content:center;border-radius:50%;color:rgba(232,205,121,.62);text-decoration:none;
    border:1px solid rgba(201,162,39,.16);background:rgba(11,16,32,.12);backdrop-filter:blur(6px);
    -webkit-backdrop-filter:blur(6px);transition:color .18s,border-color .18s,background .18s}}
  .backbtn:hover,.backbtn:focus-visible{{color:#e8cd79;border-color:rgba(201,162,39,.45);background:rgba(11,16,32,.3)}}
  .backbtn svg{{width:13px;height:13px}}
  nav.jump{{position:sticky;top:0;z-index:12;display:flex;gap:7px;overflow-x:auto;scrollbar-width:none;
    padding:10px 0;margin:6px 0 4px;background:linear-gradient(180deg,#0b1020 70%,rgba(11,16,32,.75))}}
  nav.jump::-webkit-scrollbar{{display:none}}
  nav.jump a{{flex:none;font-size:12.5px;color:var(--gold2);text-decoration:none;padding:6px 12px;
    border:1px solid var(--line);border-radius:999px;background:rgba(201,162,39,.07)}}
  nav.jump a:hover{{background:rgba(201,162,39,.16)}}
  .search{{margin:10px 0 4px}}
  .search input{{width:100%;padding:11px 14px;border-radius:12px;border:1px solid var(--line);
    background:#0e1526;color:var(--ink);font-size:14.5px;font-family:inherit}}
  .how{{margin:16px 0 6px;padding:16px 16px 6px;border:1px dashed var(--line);border-radius:16px;
    background:rgba(201,162,39,.05)}}
  .how h2{{font-size:15px;color:var(--gold2);letter-spacing:.1em;margin:0 0 10px}}
  .how h3{{font-size:13.5px;color:var(--gold2);margin:14px 0 6px;font-weight:600}}
  .how p,.how li{{font-size:14px;line-height:1.9;color:#e2dbca;margin:0 0 6px}}
  .how ul{{margin:0 0 8px;padding-left:18px}}
  .how b{{color:var(--gold2);font-weight:600}}
  .group{{margin-top:26px}}
  .group h2{{font-size:clamp(17px,4vw,21px);letter-spacing:.06em;margin:0 0 6px;
    border-left:3px solid var(--gold);padding-left:10px}}
  .group h2 .sub{{display:block;font-size:12px;color:var(--sub);letter-spacing:.04em;margin-top:5px;font-weight:400}}
  .gintro{{font-size:13.5px;color:var(--sub);line-height:1.85;margin:6px 0 10px}}
  .card{{display:grid;grid-template-columns:84px 1fr;gap:12px;padding:12px 0;align-items:start;border-bottom:1px dotted rgba(255,255,255,.08)}}
  .card .thumb{{width:84px;align-self:start;border-radius:8px;overflow:hidden;border:1px solid rgba(201,162,39,.4);background:#0d1526;line-height:0}}
  .card .thumb img{{width:100%;height:auto;display:block}}
  .card h3{{margin:0 0 4px;font-size:15.5px;display:flex;flex-wrap:wrap;align-items:baseline;gap:8px}}
  .card h3 .tag{{font-size:11.5px;color:var(--sub);font-weight:400;letter-spacing:.02em}}
  .card .kw{{margin:0 0 6px;font-size:12.5px;color:var(--gold2);letter-spacing:.02em}}
  .card p{{margin:0 0 5px;font-size:14px;line-height:1.82;color:#e6dfcd}}
  .card p b{{display:inline-block;min-width:36px;color:var(--gold2);font-weight:600}}
  .card p.rev{{color:#dbc9c2}}
  footer{{margin-top:34px;padding-top:16px;border-top:1px solid rgba(255,255,255,.08);
    color:#7c8399;font-size:12px;line-height:1.9}}
  footer a{{color:var(--gold2);text-decoration:none}}
  @media(max-width:400px){{.card{{grid-template-columns:72px 1fr;gap:10px}} .card .thumb{{width:72px}}}}
</style>
</head>
<body>
<div class="wrap">
  <a class="backbtn" href="../" aria-label="回塔羅抽牌" title="回塔羅抽牌">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
  </a>

  <header class="top">
    <div class="brand">小R頻道</div>
    <h1>78 張塔羅牌義總覽</h1>
    <p class="lead">每張牌長什麼樣、象徵什麼、正位與逆位怎麼讀。<br>先看前面的讀法，再往下翻牌；也可以直接搜尋。</p>
  </header>

  <nav class="jump">
    <a href="#how">怎麼讀</a>
    <a href="#g-大阿爾克那">大阿爾克那</a>
    <a href="#g-權杖">權杖</a>
    <a href="#g-聖杯">聖杯</a>
    <a href="#g-寶劍">寶劍</a>
    <a href="#g-錢幣">錢幣</a>
  </nav>

  <div class="search"><input id="q" type="search" placeholder="搜尋牌名或關鍵詞，例如：死神、寶劍、選擇、結束"></div>

  <section class="how" id="how">
    <h2>先懂這四件事，再看牌</h2>

    <h3>1. 一副牌＝22＋56</h3>
    <p><b>大阿爾克那</b> 22 張（0～XXI）講的是人生的大主題：開始、選擇、崩解、完成。<b>小阿爾克那</b> 56 張分成四花色，講日常的細節：今天、這段關係、這筆錢。</p>

    <h3>2. 四花色＝四種元素</h3>
    <ul>
      <li><b>權杖（火）</b>行動與熱情——想不想做、敢不敢衝</li>
      <li><b>聖杯（水）</b>情感與關係——你心裡怎麼了</li>
      <li><b>寶劍（風）</b>思考與溝通——你怎麼想、怎麼說</li>
      <li><b>錢幣（土）</b>現實與資源——錢、身體、時間夠不夠</li>
    </ul>

    <h3>3. 數字與宮廷牌＝進度</h3>
    <p>一＝種子、二＝選擇、三＝初成果、四＝守成、五＝摩擦、六＝回報、七＝盤點、八＝專注、九＝快完成、十＝到頂。<br>
    宮廷牌：<b>侍者</b>剛入門、<b>騎士</b>已上路、<b>皇后</b>會照顧、<b>國王</b>做決定。</p>

    <h3>4. 正位與逆位</h3>
    <p>正位＝這股能量正在發生。逆位不等於壞事，通常是「卡住、過度、還沒準備好，或往內走」。看到逆位先問一句：是太少，還是太多？</p>

    <h3>三張牌怎麼讀</h3>
    <p>本站抽牌用「過去／現在／未來」：<b>過去</b>是你帶著什麼進來、<b>現在</b>是真正的狀態與卡點、<b>未來</b>是照現在這樣走的趨勢（不是命定）。三張要串成一句話，不要分開解。</p>

    <h3>三個常見誤解</h3>
    <ul>
      <li><b>死神不是死亡</b>——是某件事該結束了。</li>
      <li><b>高塔不是災難</b>——是本來就不穩的東西倒掉，倒完才好重建。</li>
      <li><b>塔羅不預言</b>——它把你已經知道、但還沒承認的事講清楚。醫療、投資、法律請找專業人士。</li>
    </ul>
  </section>

  <section class="group" id="g-大阿爾克那">
    <h2>大阿爾克那（22 張）<span class="sub">人生的主線：從開始走到完成</span></h2>
    <p class="gintro">從 0 號愚者走到 XXI 世界，是一條完整的路：先上路、學會選擇、遇到崩解，最後收尾。</p>
    {sec_major}
  </section>
  {sec_suits}

  <footer>
    <p>牌義整理：小R頻道｜78 張（大阿爾克那 22＋四花色 56）<br>
    牌面：Rider–Waite–Smith 塔羅（1909，Pamela Colman Smith 繪，公版）</p>
    <p><a href="../">← 回三牌塔羅抽牌</a>　·　<a href="../../">回小R頻道首頁</a></p>
    <p>娛樂用途。塔羅不提供醫療、投資、法律建議；重大決定請找專業人士。</p>
  </footer>
</div>

<script>
const q = document.getElementById('q');
const cards = [...document.querySelectorAll('.card')];
const groups = [...document.querySelectorAll('.group')];
const how = document.getElementById('how');
q.addEventListener('input', () => {{
  const v = q.value.trim();
  if (!v) {{
    cards.forEach(c => c.style.display = '');
    groups.forEach(g => g.style.display = '');
    how.style.display = '';
    return;
  }}
  how.style.display = 'none';
  let any = false;
  cards.forEach(c => {{
    const hit = (c.dataset.key || '').includes(v) || c.textContent.includes(v);
    c.style.display = hit ? '' : 'none';
    if (hit) any = true;
  }});
  groups.forEach(g => {{
    const vis = [...g.querySelectorAll('.card')].some(c => c.style.display !== 'none');
    g.style.display = vis ? '' : 'none';
  }});
}});
</script>
</body>
</html>
"""

path = os.path.join(OUT_DIR, "index.html")
with open(path, "w", encoding="utf-8") as f:
    f.write(PAGE)
print("寫出", path, len(PAGE), "字元；卡數", len(CARDS))
