# -*- coding: utf-8 -*-
"""塔羅三牌 v2：洗牌動畫、牌簡介、更詳細解讀。"""
import json
import os

SITE = os.path.expanduser("~/opencode/圖片生成/小R頻道_網站/tarot")
os.makedirs(SITE, exist_ok=True)

# name, num, kw, upright, rev_kw, reversed, intro（一句個性）
from tarot_data import CARDS as cards  # noqa: E402  共用牌庫
from tarot_text import (  # noqa: E402
    MAJOR_SCENE, RANK_SCENE, SUIT_FLAVOR, TOPIC_POS, OPENERS,
    CLOSERS_POS, CLOSERS_REV,
)

SCENE = {}
for _c in cards:
    if _c["arc"] == "大阿爾克那":
        SCENE[_c["img"]] = MAJOR_SCENE.get(_c["n"], _c["intro"])
    else:
        _a = RANK_SCENE.get(_c["num"], "")
        _b = SUIT_FLAVOR.get(_c["arc"], "")
        SCENE[_c["img"]] = (_a + "；" + _b) if _b else _a


html = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>三牌塔羅｜小R頻道</title>
<meta name="description" content="免註冊的三牌塔羅：洗牌、抽牌、依牌義與位置給出解讀。娛樂用途，不做醫療、投資或法律建議。">
<link rel="canonical" href="https://littler5071.github.io/tarot/">
<meta property="og:title" content="三牌塔羅｜小R頻道">
<meta property="og:description" content="洗牌、抽牌，用三張牌把問題講清楚。">
<meta property="og:type" content="website">
<style>
  :root{--bg:#0b1020;--ink:#f2ead6;--sub:#a9b2c9;--gold:#c9a227;--gold2:#e8cd79;--line:rgba(201,162,39,.35)}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;color:var(--ink);
    background:radial-gradient(1200px 600px at 50% -10%,#1b2447 0%,transparent 60%),linear-gradient(180deg,#0b1020,#0a0e1a);
    font-family:"Noto Serif TC","Songti TC","PingFang TC",serif;-webkit-text-size-adjust:100%}
  .wrap{max-width:820px;margin:0 auto;padding:28px clamp(16px,5vw,40px) 80px}
  header{text-align:center;margin-bottom:16px}
  .brand{font-size:13px;letter-spacing:.35em;color:var(--gold);opacity:.85}
  h1{font-size:clamp(24px,5.2vw,34px);margin:8px 0 6px;letter-spacing:.06em}
  .lead{color:var(--sub);font-size:14px;line-height:1.7;margin:0}
  .panel{background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
    border:1px solid var(--line);border-radius:18px;padding:16px;margin:18px 0}
  label{display:block;font-size:13px;color:var(--gold2);margin-bottom:6px;letter-spacing:.08em}
  input[type=text]{width:100%;padding:12px 14px;border-radius:12px;border:1px solid var(--line);
    background:#0e1526;color:var(--ink);font-size:15px;font-family:inherit}
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
  .chip{padding:7px 13px;border-radius:999px;border:1px solid var(--line);background:transparent;
    color:var(--sub);font-size:13px;cursor:pointer;font-family:inherit}
  .chip.on{background:rgba(201,162,39,.16);color:var(--gold2);border-color:var(--gold)}
  .actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
  button{font-family:inherit;cursor:pointer;border:0}
  .btn{padding:12px 20px;border-radius:999px;font-size:15px;letter-spacing:.06em;
    background:linear-gradient(180deg,#d9b64a,#b78e1c);color:#1a1406;font-weight:700}
  .btn.ghost{background:transparent;border:1px solid var(--line);color:var(--gold2);font-weight:400}
  .btn:disabled{opacity:.45;cursor:not-allowed}
  .deck{display:flex;justify-content:center;gap:14px;margin:22px 0 4px;flex-wrap:nowrap}
  .slot{width:30%;max-width:150px;aspect-ratio:5/8;perspective:900px}
  .cardface{position:relative;width:100%;height:100%;transform-style:preserve-3d;
    transition:transform .6s cubic-bezier(.2,.7,.2,1);border-radius:12px}
  .slot.flipped .cardface{transform:rotateY(180deg)}
  .side{position:absolute;inset:0;border-radius:12px;backface-visibility:hidden;
    border:1px solid var(--line);display:flex;align-items:center;justify-content:center;overflow:hidden}
  .back{background:repeating-linear-gradient(45deg,#101a33 0 6px,#0d1526 6px 12px);
    box-shadow:inset 0 0 0 6px rgba(201,162,39,.12)}
  .back svg{width:64%;height:64%;opacity:.85}
  .front{transform:rotateY(180deg);background:#0d1526;color:#f2ead6;position:relative;
    flex-direction:column;padding:0;text-align:center;overflow:hidden}
  .front img{width:100%;height:100%;object-fit:contain;display:block}
  .front .cap{position:absolute;left:0;right:0;bottom:0;padding:16px 4px 5px;
    background:linear-gradient(180deg,rgba(6,9,18,0),rgba(6,9,18,.94));font-size:clamp(9.5px,2.3vw,13px);
    font-weight:700;line-height:1.3;letter-spacing:.02em}
  .front .cap .r{display:block;color:#e8a2a2;font-size:9.5px;font-weight:700}
  .front .nm{font-size:clamp(11px,2.6vw,15px);font-weight:700;line-height:1.25}
  .front .num{font-size:clamp(9px,2.2vw,12px);opacity:.7}
  .front .rev{font-size:10px;color:#8a2b2b;font-weight:700}
  .slot.shuffling{animation:sh .28s ease-in-out infinite}
  .slot.shuffling:nth-child(2){animation-delay:.09s}
  .slot.shuffling:nth-child(3){animation-delay:.18s}
  @keyframes sh{
    0%{transform:translate(0,0) rotate(0)}
    25%{transform:translate(-12px,-6px) rotate(-7deg)}
    50%{transform:translate(10px,4px) rotate(6deg)}
    75%{transform:translate(-5px,2px) rotate(-3deg)}
    100%{transform:translate(0,0) rotate(0)}
  }
  .pos{text-align:center;font-size:12px;color:var(--sub);margin-top:8px;letter-spacing:.12em;min-height:18px}
  .rline{border-left:2px solid var(--gold);padding:10px 0 10px 12px;margin:18px 0;
    display:grid;grid-template-columns:84px 1fr;gap:12px;align-items:start}
  .rline .thumb{width:84px;border-radius:8px;overflow:hidden;border:1px solid rgba(201,162,39,.45);
    background:#0d1526;line-height:0}
  .rline .thumb img{width:100%;display:block}
  .rline .thumb.rev img{transform:rotate(180deg)}
  .rline .body{min-width:0}
  @media(max-width:400px){.rline{grid-template-columns:72px 1fr;gap:10px} .rline .thumb{width:72px}}
  .rline h3{margin:0 0 6px;font-size:15px;color:var(--gold2);letter-spacing:.06em}
  .rline .meta{font-size:12px;color:#9aa3b8;margin-bottom:6px}
  .rline p{margin:0 0 6px;font-size:14.5px;line-height:1.9;color:#e6dfcd}
  .rline p b{color:var(--gold2);font-weight:600}
  .summary{margin-top:18px;padding:16px;border-radius:14px;background:rgba(201,162,39,.08);
    border:1px dashed var(--line);font-size:14.5px;line-height:1.95}
  .summary h3{margin:0 0 8px;font-size:14px;color:var(--gold2);letter-spacing:.1em}
  .summary .act{margin-top:10px;padding-top:10px;border-top:1px dotted rgba(255,255,255,.12)}
  .hist{margin-top:22px}
  .hist h2{font-size:15px;color:var(--gold2);letter-spacing:.1em;margin:0 0 8px}
  .hist li{font-size:13px;color:var(--sub);line-height:1.8;border-bottom:1px dotted rgba(255,255,255,.08);
    padding:7px 0;list-style:none}
  footer{margin-top:34px;padding-top:16px;border-top:1px solid rgba(255,255,255,.08);color:#778;font-size:12px;line-height:1.8}
  .disclaimer{color:#8f7a3f}
  .more{display:inline-block;margin:2px 0 8px;padding:8px 14px;border-radius:999px;
    border:1px solid rgba(201,162,39,.35);background:rgba(201,162,39,.08);
    color:#e8cd79;text-decoration:none;font-size:13px;letter-spacing:.03em}
  .more:hover{background:rgba(201,162,39,.18);border-color:rgba(201,162,39,.6)}
  .backbtn{position:fixed;left:12px;top:14px;z-index:15;display:inline-flex;align-items:center;gap:6px;
    padding:0;width:34px;height:34px;justify-content:center;border-radius:50%;font-size:12px;letter-spacing:.04em;
    color:rgba(232,205,121,.62);text-decoration:none;border:1px solid rgba(201,162,39,.16);
    background:rgba(11,16,32,.12);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
    transition:color .18s,border-color .18s,background .18s}
  .backbtn span{display:none}
  .backbtn:hover,.backbtn:focus-visible{color:#e8cd79;border-color:rgba(201,162,39,.45);background:rgba(11,16,32,.3)}
  .backbtn svg{width:13px;height:13px;flex:none}
  @media(min-width:640px){
    .backbtn{width:auto;height:auto;padding:6px 12px 6px 9px;border-radius:999px;gap:6px}
    .backbtn span{display:inline}
  }
</style>
</head>
<body>
<div class="wrap">
  <a class="backbtn" href="../" aria-label="回首頁" title="回首頁">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"
         stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
    <span>回上一頁</span>
  </a>
  <header>
    <div class="brand">小R頻道</div>
    <h1>三牌塔羅</h1>
    <p class="lead">先想一個問題，再抽三張牌：過去、現在、未來。<br>牌不預言，它只把你已經知道的事講清楚。</p>
  </header>

  <div class="panel">
    <label for="q">你的問題（可以不填）</label>
    <input id="q" type="text" maxlength="60" placeholder="例如：這段關係我該繼續嗎？">
    <div class="chips" id="topic">
      <button class="chip on" data-t="感情">感情</button>
      <button class="chip" data-t="工作">工作</button>
      <button class="chip" data-t="金錢">金錢</button>
      <button class="chip" data-t="選擇">選擇</button>
      <button class="chip" data-t="自己">自己</button>
    </div>
    <div class="actions">
      <button class="btn" id="shuffle">洗牌</button>
      <button class="btn ghost" id="draw" disabled>抽三張</button>
      <button class="btn ghost" id="reset">重新開始</button>
    </div>
  </div>

  <div class="deck" id="deck">
    <div class="slot" data-i="0"><div class="cardface"><div class="side back">__BACK__</div><div class="side front"><div class="nm">—</div></div></div></div>
    <div class="slot" data-i="1"><div class="cardface"><div class="side back">__BACK__</div><div class="side front"><div class="nm">—</div></div></div></div>
    <div class="slot" data-i="2"><div class="cardface"><div class="side back">__BACK__</div><div class="side front"><div class="nm">—</div></div></div></div>
  </div>
  <div class="pos" id="posline">洗牌後，依序點三張牌</div>

  <div id="reading"></div>

  <div class="hist">
    <h2>最近的抽牌</h2>
    <ul id="hist"><li>還沒有紀錄</li></ul>
  </div>

  <footer>
    <p class="disclaimer">娛樂用途。塔羅不提供醫療、投資、法律建議；重大決定請找專業人士。</p>
    <p><a class="more" href="cards/">看 78 張完整牌義與牌的故事 →</a></p>
    <p>牌義整理：小R頻道｜78 張（大阿爾克那 22＋四花色 56）<br>牌面：Rider–Waite–Smith 塔羅（1909，Pamela Colman Smith 繪，公版）</p>
  </footer>
</div>

<script>
const CARDS = __CARDS__;
const POS = ["過去","現在","未來"];
const TOPIC_HINT = {
  "感情":"在關係裡，牌義偏向「你怎麼感受、怎麼表達」，不是對方會不會回頭。",
  "工作":"在工作上，重點是「資源、節奏與界線」，不是誰比較努力。",
  "金錢":"金錢問題先看現實條件（收入、支出、風險），再看你的恐懼。",
  "選擇":"選擇題沒有標準答案，只有你願意承擔哪一種後果。",
  "自己":"回到自己身上：你真正想要的是什麼，以及你願意為它放棄什麼。"
};
const POS_MEAN = {
  "過去":"這是事情的起點：你帶著什麼狀態進來，或什麼原因造成現在的局面。",
  "現在":"這是你此刻真正的狀態，也是卡住或順利的關鍵。",
  "未來":"照現在這樣走下去，最可能往哪裡去；不是命定，是趨勢。"
};
const SCENE = __SCENE__;
const TP = __TP__;
const OP = __OP__;
const CP = __CP__;
const CR = __CR__;
function h32(str){
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) % 2147483647;
  return h;
}
function scenOf(c, topic, pos, q, rev){
  const h = h32(c.img + topic + pos + q);
  const op = OP[pos][h % OP[pos].length];
  const tp = TP[topic][pos][Math.floor(h / 4) % TP[topic][pos].length];
  const closer = rev ? CR[Math.floor(h / 9) % CR.length] : CP[Math.floor(h / 13) % CP.length];
  return op + tp + "。這張牌（" + c.n + "）看到的是：" + SCENE[c.img] + "。" + closer;
}
function detectTopic(q){
  const score=t=>{
    let s=0;
    (KW[t]||[]).forEach(w=>{ if(q.includes(w)) s+=w.length; });
    return s;
  };
  // 先判斷具體領域（工作／金錢／感情），都比不到才用「選擇／自己」
  const domain=["工作","金錢","感情"];
  let best=null, bs=0;
  domain.forEach(t=>{ const v=score(t); if(v>bs){bs=v;best=t;} });
  if(best) return best;
  ["選擇","自己"].forEach(t=>{ const v=score(t); if(v>bs){bs=v;best=t;} });
  return best;
}

let deck=[], picked=[], topic="感情", shuffled=false, busy=false, manualTopic=false;
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];

function shuffleDeck(){
  deck=CARDS.slice();
  for(let i=deck.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[deck[i],deck[j]]=[deck[j],deck[i]];}
  deck=deck.slice(0,12);
}

function resetView(){
  $$(".slot").forEach(s=>{s.classList.remove("flipped","shuffling");});
  $("#reading").innerHTML="";
}

$("#shuffle").onclick=()=>{
  if(busy) return;
  busy=true; picked=[]; resetView(); shuffled=false;
  $("#draw").disabled=true;
  $("#posline").textContent="洗牌中…";
  $$(".slot").forEach(s=>s.classList.add("shuffling"));
  setTimeout(()=>{
    shuffleDeck();
    $$(".slot").forEach(s=>s.classList.remove("shuffling"));
    shuffled=true; busy=false;
    $("#draw").disabled=false;
    $("#posline").textContent="牌洗好了，點三張牌（或按「抽三張」）";
  }, 1100);
};

$("#reset").onclick=()=>{
  picked=[]; shuffled=false; resetView();
  $("#draw").disabled=true; $("#q").value="";
  $("#posline").textContent="洗牌後，依序點三張牌";
};

$$("#topic .chip").forEach(c=>c.onclick=()=>{
  $$("#topic .chip").forEach(x=>x.classList.remove("on"));
  c.classList.add("on"); topic=c.dataset.t; manualTopic=true;
});
$("#q").addEventListener("input", e=>{
  if(manualTopic) return;
  const t=detectTopic(e.target.value);
  if(t){
    topic=t;
    $$("#topic .chip").forEach(x=>x.classList.toggle("on", x.dataset.t===t));
  }
});

function flip(slot, card, rev){
  const front=slot.querySelector(".front");
  front.innerHTML=`<img src="img/${card.img}.webp" alt="${card.n}${rev?"（逆位）":""}" loading="eager"
      style="${rev?"transform:rotate(180deg)":""}">
    <div class="cap">${card.n}${rev?'<span class="r">逆位</span>':''}</div>`;
  slot.classList.add("flipped");
}

$$(".slot").forEach(slot=>{
  slot.onclick=()=>{
    if(!shuffled||busy||picked.length>=3||slot.classList.contains("flipped")) return;
    const i=+slot.dataset.i, card=deck[i], rev=Math.random()<0.4;
    picked.push({...card,isRev:rev,pos:POS[picked.length]});
    flip(slot,card,rev);
    if(picked.length===3) setTimeout(renderReading,650);
  };
});

$("#draw").onclick=()=>{
  if(!shuffled||busy) return;
  picked=[];
  $$(".slot").forEach((slot,i)=>{
    const card=deck[i], rev=Math.random()<0.4;
    picked.push({...card,isRev:rev,pos:POS[i]});
    setTimeout(()=>flip(slot,card,rev), i*230);
  });
  setTimeout(renderReading, 1100);
};

function renderReading(){
  const q=$("#q").value.trim();
  const blocks=picked.map(c=>{
    const meaning=c.isRev?c.rev:c.up;
    const kw=c.isRev?c.kwr:c.kw;
    return `<div class="rline">
      <div class="thumb${c.isRev?' rev':''}"><img src="img/${c.img}.webp" alt="${c.n}${c.isRev?'（逆位）':''}" loading="lazy"></div>
      <div class="body">
        <h3>${c.pos}｜${c.n}${c.isRev?'（逆位）':''}</h3>
        <div class="meta">${c.arc}${c.arc==="大阿爾克那"?" ":"・"}${c.num}｜元素：${c.el}｜${c.isRev?"逆位":"正位"}</div>
        <p><b>牌的性格：</b>${c.intro}</p>
        <p><b>放在「${c.pos}」位：</b>${POS_MEAN[c.pos]}</p>
        <p><b>這張在說什麼：</b>${kw}——${meaning}</p>
        <p><b>套到你的問題：</b>${(q && c.pos==="現在") ? "回到你問的「"+q+"」——" : ""}${scenOf(c, topic, c.pos, q, c.isRev)}</p>
      </div>
    </div>`;
  }).join("");

  const p=picked[0], n=picked[1], f=picked[2];
  const trend = n.isRev
    ? `你現在的狀態是「${n.kwr}」。這代表卡點多半不在外面，而在你還沒處理的那一塊；先處理它，後面的牌才有意義。`
    : `你現在是「${n.kw}」的狀態。這代表方向其實是對的，只是成果還沒出現，需要的是時間與穩定。`;
  const ori=c=>c.isRev?"（逆位）":"";
  const head = `過去從「${p.n}${ori(p)}」開始，帶你走到現在的「${n.n}${ori(n)}」；如果照這個節奏走下去，未來會走向「${f.n}${ori(f)}」。`;
  const future = f.isRev
    ? `未來這張是逆位：不是壞事，是提醒你別急著定案。先把準備工作補齊，動起來會穩得多。`
    : `未來這張是正位：可以動了，而且越早越好；拖著反而會讓機會變薄。`;
  const act = f.isRev
    ? "今天可以做的一件事：把你還沒準備好的那一項寫下來（最多三條），只補第一條。"
    : "今天可以做的一件事：把你要做的決定寫成一句話，然後在 24 小時內執行最小的一步。";

  $("#reading").innerHTML = `<h2 style="font-size:15px;letter-spacing:.12em;color:var(--gold2);margin:20px 0 2px">三張牌的解讀</h2>`
    + blocks
    + `<div class="summary"><h3>綜合來看</h3>
        <div>${q?"你的問題是「"+q+"」。":""}${TOPIC_HINT[topic]}</div>
        <div style="margin-top:8px">${head}</div>
        <div style="margin-top:8px">${trend}</div>
        <div style="margin-top:8px">${future}</div>
        <div class="act">${act}</div>
      </div>`;
  $("#posline").textContent="解讀完成｜往下看完整說明";
  saveHistory(q);
  $("#reading").scrollIntoView({behavior:"smooth",block:"start"});
}

function saveHistory(q){
  try{
    const k="tarot_hist_v1";
    const arr=JSON.parse(localStorage.getItem(k)||"[]");
    arr.unshift({t:Date.now(),q:q||topic,c:picked.map(x=>x.n+(x.isRev?"（逆）":"")).join("、")});
    localStorage.setItem(k,JSON.stringify(arr.slice(0,8)));
    renderHistory();
  }catch(e){}
}
function renderHistory(){
  try{
    const arr=JSON.parse(localStorage.getItem("tarot_hist_v1")||"[]");
    if(!arr.length) return;
    $("#hist").innerHTML=arr.map(x=>{
      const d=new Date(x.t);
      const ds=`${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}`;
      return `<li>${ds}　${x.q}　<span style="color:#c9a227">${x.c}</span></li>`;
    }).join("");
  }catch(e){}
}
renderHistory();
</script>
</body>
</html>
"""

back_svg = ('<svg viewBox="0 0 100 140" fill="none" stroke="#c9a227" stroke-width="1.1">'
            '<rect x="8" y="8" width="84" height="124" rx="6" opacity=".55"/>'
            '<circle cx="50" cy="70" r="26" opacity=".7"/>'
            '<path d="M50 40 L58 62 L80 70 L58 78 L50 100 L42 78 L20 70 L42 62 Z" fill="#c9a227" fill-opacity=".18"/>'
            '<path d="M50 22 v10 M50 108 v10 M22 70 h10 M68 70 h10" opacity=".6"/>'
            '</svg>')

html = (html
        .replace("__CARDS__", json.dumps(cards, ensure_ascii=False))
        .replace("__SCENE__", json.dumps(SCENE, ensure_ascii=False))
        .replace("__TP__", json.dumps(TOPIC_POS, ensure_ascii=False))
        .replace("__OP__", json.dumps(OPENERS, ensure_ascii=False))
        .replace("__CP__", json.dumps(CLOSERS_POS, ensure_ascii=False))
        .replace("__CR__", json.dumps(CLOSERS_REV, ensure_ascii=False))
        .replace("__BACK__", back_svg))
with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("寫出", os.path.join(SITE, "index.html"), len(html), "字元；牌數", len(cards))
