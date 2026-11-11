# -*- coding: utf-8 -*-
"""塔羅三牌 v2：洗牌動畫、牌簡介、更詳細解讀。"""
import json
import os

SITE = os.path.expanduser("~/opencode/圖片生成/小R頻道_網站/tarot")
os.makedirs(SITE, exist_ok=True)

# name, num, kw, upright, rev_kw, reversed, intro（一句個性）
from tarot_data import CARDS as cards  # noqa: E402  共用牌庫

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
const SCEN = {
  "感情":{
    "過去":[
      "通常是某件沒講開的小事，或某一方先退了一步。",
      "你們其實有機會講清楚，但選了先放著。",
      "這段關係的底色是「不想麻煩對方」，所以很多話沒說。"
    ],
    "現在":[
      "你已經感覺到對方的態度，只是還在等一個明確的說法。",
      "你一邊想確認，一邊又怕問了會把氣氛弄壞。",
      "兩個人都在等對方先開口，所以誰都沒動。"
    ],
    "未來":[
      "可能出現一次講清楚的對話，或一次安靜的拉開。",
      "下一次見面或下一通電話，會決定這段關係的位置。",
      "你會先累，然後換你沉默——那時才是真正的分水嶺。"
    ]
  },
  "工作":{
    "過去":[
      "這個局面多半從一次交接、一個臨時任務，或一句「先撐一下」開始。",
      "你當初接下的東西比談好的多，而且沒有人正式補回來。",
      "那時候的判斷是對的，只是資源沒跟上。"
    ],
    "現在":[
      "事情推得動，但你要的是一個「確定可以」的訊號，而不是更多工作。",
      "你手上的事已經超出一個人能扛的量，卻還在用加班補。",
      "決定權不在你手上，你能做的只有把選項整理清楚。"
    ],
    "未來":[
      "下一次考核或下一次分工，會把答案直接攤在你面前。",
      "兩三個月內會有一個位置空出來，你要不要接是關鍵。",
      "你會先被肯定、再被加量——這是同一件事的兩面。"
    ]
  },
  "金錢":{
    "過去":[
      "現在的數字是幾個月前某個決定累積出來的，不是這個月突然變的。",
      "那筆錢在那時候看起來是小錢，累積起來才是現在的壓力。",
      "問題不在收入，在某個固定支出一直沒被檢視。"
    ],
    "現在":[
      "你已經在算，但還有一筆沒算進去（保費、稅、或某個固定支出）。",
      "現金流過得去，但沒有留緊急預備金，所以不敢停。",
      "你在等一筆錢進來，而那筆錢的時間點不是你能控制的。"
    ],
    "未來":[
      "兩三個月內會有一筆比較大的支出或收入，把缺口或餘裕顯示出來。",
      "年底前會有一次必須做決定的時刻，金額大概是你月收入的一半以上。",
      "數字會慢慢回穩，但前提是你真的開始記帳。"
    ]
  },
  "選擇":{
    "過去":[
      "你其實早就排出順序了，只是還沒承認哪個選項比較重。",
      "你上次猶豫的點跟這次一模一樣，代表那不是資訊不足。",
      "那時候你選了安全的那邊，所以現在才會想另一邊。"
    ],
    "現在":[
      "兩個選項各有代價，你卡住的不是資訊，是「選了就要承擔」。",
      "你已經在心裡選好了，只是在等一個允許。",
      "你怕的不是選錯，是選了之後不能反悔。"
    ],
    "未來":[
      "時間會替你選——通常是選掉你比較想要的那個。",
      "一個月內會出現一個小機會，讓你不用一次跳到底也能往那邊靠。",
      "你會先試水溫，再正式決定；這是比較穩的路。"
    ]
  },
  "自己":{
    "過去":[
      "這個狀態是從某一次「算了，先這樣」開始累積的。",
      "你把別人的優先順序排在自己前面，已經排了很久。",
      "那時候身體就提醒過了，只是你沒停。"
    ],
    "現在":[
      "你對別人很清楚，對自己反而說不出要什麼。",
      "你不是沒力氣，是力氣都用在撐住場面。",
      "你一直往前，卻沒問過這條路是不是你要的。"
    ],
    "未來":[
      "身體或情緒會先替你喊停，時間點大概在一兩週內。",
      "你會在某個小事上突然受不了——那不是小事，是累積。",
      "只要留一小段自己的時間，狀態就會明顯回來。"
    ]
  }
};
const OPEN = {
  "過去":["回頭看，", "把時間拉回起點，", "那時候的狀況是，"],
  "現在":["此刻最像的畫面是：", "你現在的處境比較像這樣：", "現在的感覺接近："],
  "未來":["再走下去，", "接下來兩三週，", "如果照現在這樣，"]
};
function pick(list, seed){ return list[seed % list.length]; }
function scenOf(card, topic, pos, q){
  const key = (card.img || card.n) + q + pos;
  let h = 0; for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) % 100000;
  const body = pick(SCEN[topic][pos], h);
  const head = pick(OPEN[pos], Math.floor(h / 7));
  return head + body;
}

const KW={
  "工作":["工作","職","公司","老闆","同事","面試","升遷","專案","客戶","創業","轉職","離職"],
  "金錢":["錢","投資","股","買","賣","房","貸","薪","收入","支出","存款"],
  "感情":["感情","他","她","喜歡","愛","交往","分手","復合","關係","婚","曖昧","對象"],
  "選擇":["要不要","該不該","選","決定","哪個","繼續"],
  "自己":["自己","人生","方向","焦慮","累","迷惘","目標","習慣"]
};
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
        <p><b>套到你的問題：</b>${(q && c.pos==="現在") ? "回到你問的「"+q+"」——" : ""}${c.n}在「${c.pos}」位強調的是「${kw}」，${scenOf(c, topic, c.pos, q)}${c.isRev
          ? " 逆位代表這股力量卡住或過頭了，所以先處理「哪一件事讓你卡住」，再談下一步。"
          : " 正位代表這股力量已經在發生，所以問題不是「會不會」，而是「你要不要順著它做」。"}</p>
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

html = html.replace("__CARDS__", json.dumps(cards, ensure_ascii=False)).replace("__BACK__", back_svg)
with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("寫出", os.path.join(SITE, "index.html"), len(html), "字元；牌數", len(cards))
