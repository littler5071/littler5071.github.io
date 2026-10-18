# -*- coding: utf-8 -*-
"""
產生站內文章／展示頁 `/ai/floorplan-3d/index.html`。
主題：AI 助理自己畫平面圖 → 用「同一份 plan.json」生成 Three.js 互動 3D 室內設計展示。

- 版型沿用既有 AI 文章頁（同一套 :root 色票、.box／<h2><span class="dot">）。
- 導覽列與瀏覽次數由 site_tools/_inject_site_blocks.py 事後從兄弟頁補上（本產生器不寫導覽）。
- 產生器會一併把 plan.json／plan.svg／plan.png 複製到頁面目錄（3D 頁在執行時 fetch plan.json）。
- 隱私：不得出現本機路徑、帳號、email。

用法：python build_ai_floorplan3d.py [網站根目錄] [素材目錄]
"""
import json
import os
import shutil
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "D:/_Richard/OpenCode/圖片生成/小R頻道_網站"
ASSETS = sys.argv[2] if len(sys.argv) > 2 else "C:/Users/Summer/banner/floorplan3d"
SLUG = "floorplan-3d"

plan = json.load(open(os.path.join(ASSETS, "plan.json"), encoding="utf-8"))
N_ROOM = len(plan["rooms"])
AREA = plan["total_interior_m2"]
BAL = plan["balcony_m2"]
PING = round((AREA + BAL) / 3.3058, 1)
PING_IN = round(AREA / 3.3058, 1)
# 各房間面積表列
ROWS = "\n".join(
    '    <tr><td>%s</td><td class="pg">%s</td><td class="n">%.2f</td><td class="n">%.2f</td></tr>'
    % (r["name"], r["id"], r["area_m2"], r["area_ping"]) for r in plan["rooms"])

HTML = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>我請 AI 助理自己畫平面圖，再生成可走動的 3D 室內設計網頁｜AI 助理實測｜小R頻道</title>
<meta name="description" content="同一個 AI 助理先畫出專業平面圖（SVG＋PNG），再用同一份 plan.json 生成 Three.js 互動 3D 室內設計：軌道環繞、WASD 第一人稱走動、房間標籤、2D／3D 切換。全程免費工具、無付費模型、無外部服務，含做法、資料結構與原始碼說明。">
<link rel="stylesheet" href="../../css/ai-article.css">
<style>
  /* ── 3D 展示區 ───────────────────────────────── */
  .demo{background:var(--card);border:2px solid var(--line);border-radius:16px;
        overflow:hidden;margin:0 0 20px}
  .demo-top{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 12px;
        border-bottom:1px solid var(--line);background:rgba(54,78,112,.045)}
  .demo-top .ttl{font-size:14px;color:var(--soft);margin-right:auto;letter-spacing:.02em}
  button.ui{font:inherit;font-size:13.5px;padding:6px 13px;border-radius:999px;cursor:pointer;
        border:1.5px solid var(--line);background:#fff;color:var(--blue);transition:.15s}
  button.ui:hover{border-color:var(--blue);background:rgba(54,78,112,.06)}
  button.ui.on{background:var(--blue);color:#fff;border-color:var(--blue)}
  .stagewrap{display:flex;flex-direction:column;min-height:0}
  @media(min-width:900px){.stagewrap{flex-direction:row}}
  .stage{position:relative;flex:1 1 auto;background:#eef1f4;min-height:340px;
        height:56vh;min-height:340px;max-height:640px}
  .side{flex:0 0 auto;width:100%;border-top:1px solid var(--line);
        padding:10px 12px;background:#fbfcfd;max-height:230px;overflow:auto}
  @media(min-width:900px){.side{width:216px;border-top:0;border-left:1px solid var(--line);
        max-height:640px}}
  .side h4{font-size:12px;color:var(--soft);margin:0 0 7px;font-weight:600;letter-spacing:.06em}
  .side ul{list-style:none;margin:0 0 14px;padding:0}
  .side li a{display:block;font-size:13.5px;color:var(--ink);text-decoration:none;
        padding:5px 8px;border-radius:8px;cursor:pointer}
  .side li a:hover{background:rgba(54,78,112,.08)}
  .side li a.cur{background:var(--blue);color:#fff}
  .side .kv{font-size:12.5px;color:var(--soft);line-height:1.9}
  .side .kv b{color:var(--ink);font-weight:600}
  canvas{display:block;width:100%;height:100%}
  #labels{position:absolute;inset:0;pointer-events:none;overflow:hidden}
  .lab{position:absolute;transform:translate(-50%,-50%);background:rgba(255,255,255,.86);
        border:1px solid rgba(54,78,112,.25);border-radius:999px;padding:2px 9px;
        font-size:12px;color:#1d2734;white-space:nowrap;letter-spacing:.02em;
        box-shadow:0 1px 4px rgba(20,30,50,.08)}
  #plan2d{display:none;width:100%;height:100%;object-fit:contain;background:#fff}
  .hint{position:absolute;left:10px;bottom:10px;background:rgba(23,32,48,.78);color:#fff;
        font-size:12px;padding:5px 11px;border-radius:999px;letter-spacing:.02em}
  #loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
        background:#eef1f4;color:var(--soft);font-size:14px;z-index:5}
  .fallback{display:none;padding:16px;font-size:14px;color:var(--soft)}
  /* ── 表格 ─────────────────────────────────────── */
  .tw{overflow-x:auto;margin:0 0 16px}
  table.bd{width:100%;min-width:480px;border-collapse:collapse;font-size:14.5px;
    background:var(--card);border:2px solid var(--line);border-radius:14px;overflow:hidden}
  table.bd th,table.bd td{padding:8px 11px;border-bottom:1px solid var(--line);text-align:left}
  table.bd th{background:rgba(54,78,112,.07);color:var(--blue);font-size:13.5px;font-weight:600}
  table.bd tr:last-child td{border-bottom:0}
  table.bd td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
  table.bd td.pg{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--soft)}
  pre.code{background:#f6f8fa;border:1px solid var(--line);border-radius:12px;padding:12px 14px;
    overflow-x:auto;font-size:13px;line-height:1.7;color:#2a3442;
    font-family:ui-monospace,Consolas,monospace}
</style>
<link rel="stylesheet" href="../../nav.css?v=73b4d013">
<script defer src="../../nav.js?v=4b28034a"></script>
</head>
<body>
<div class="wrap">
  <a class="back" href="../">← 回 AI 助理實測</a>
  <a class="back" style="margin-left:14px" href="../../">← 回影片索引</a>
  <h1>我請 AI 助理自己畫平面圖<br>再生成可以走動的 3D 室內設計網頁</h1>
  <div class="sub">同一份 plan.json，同時長出 2D 平面圖與 3D 空間：軌道環繞、WASD 走動、房間標籤、2D／3D 切換</div>
  <div class="meta">2026/10/18・實作記錄＋互動展示（純前端、免費工具）</div>

  <div class="box">
    <strong>一句話摘要</strong>：先用 Python 以「資料驅動」畫出一張專業平面圖
    （向量 SVG ＋ 1900 px 點陣 PNG），資料存成一份 <b>plan.json</b>；
    再讓同一份 plan.json 餵給 Three.js，長出一個可以環繞、縮放、<b>走進去</b>的 3D 室內設計展示。
    <b>2D 與 3D 不是兩份工，是同一份資料的兩種呈現</b> —— 改一個房間尺寸，兩邊同時更新。
  </div>

  <div class="demo">
    <div class="demo-top">
      <span class="ttl">示範住宅・室內 __PING_IN__ 坪（含陽台 __PING__ 坪）</span>
      <button class="ui on" id="b3d">3D 空間</button>
      <button class="ui" id="b2d">2D 平面圖</button>
      <button class="ui" id="bwalk">走進室內（WASD）</button>
      <button class="ui" id="bceil">天花板</button>
      <button class="ui" id="breset">回到鳥瞰</button>
    </div>
    <div class="stagewrap">
      <div class="stage">
        <canvas id="c"></canvas>
        <div id="labels"></div>
        <div id="loading">正在載入 plan.json 與 3D 場景…</div>
        <div class="hint" id="hint">拖曳＝環繞／滾輪＝縮放／右鍵拖曳＝平移</div>
        <img id="plan2d" alt="住宅平面圖">
        <div class="fallback" id="fb">此瀏覽器無法載入 3D 或 plan.json。可直接開啟
          <a href="plan.svg">平面圖（SVG）</a> 或 <a href="plan.png">平面圖（PNG）</a>。</div>
      </div>
      <div class="side">
        <h4>房間（點選飛過去）</h4>
        <ul id="roomlist"></ul>
        <h4>資料</h4>
        <div class="kv">
          房間 <b>__NROOM__</b> 間<br>
          室內 <b>__AREA__</b> m²（<b>__PING_IN__</b> 坪）<br>
          陽台 <b>__BAL__</b> m²<br>
          樓高 <b>__WH__</b> cm｜外牆 <b>__EW__</b>／內牆 <b>__IW__</b> cm<br>
          家具 <b>__NFURN__</b> 件
        </div>
      </div>
    </div>
  </div>

  <h2><span class="dot"></span>為什麼要「同一份資料」</h2>
  <p>很多 AI 助理示範是這樣做的：畫一張平面圖給你看，再另外生一張 3D 圖 —— 兩張圖其實沒關係，
  房間數對不上、牆的位置也不一樣。這次刻意反過來：<b>先決定一份資料，再讓兩種呈現都從它長出來</b>。</p>
  <pre class="code">plan.json
 ├── rooms     房間：名稱、用途、矩形（公分）→ 2D 塗色 + 3D 地板
 ├── walls     牆：走向、厚度、起訖、門/窗開口（台度、上緣）
 ├── furniture 家具：矩形、高度 → 2D 符號 + 3D 量體
 └── project   圖框資料（專案名、比例、圖號）

make_plan.py ──► plan.svg（向量平面圖）
             ──► plan.png（1900 px 預覽）
build 3D 頁面 ──► fetch plan.json ──► Three.js 生成地板／牆／家具</pre>
  <p>所以牆上的<b>同一個門洞</b>，在 2D 是「牆斷開＋門扇弧線」，在 3D 是「牆分成兩段、上方留過樑」——
  兩邊讀的是<b>同一個 opening 物件</b>。</p>

  <h2><span class="dot"></span>第一階段：平面圖怎麼畫的</h2>
  <ul class="plain">
    <li><b>資料驅動</b>　房間、牆、門窗全部寫成 dict（清單在上），程式只負責畫，不寫死任何一個房間。
    單位用<b>公分</b>，跟真實圖說一致。</li>
    <li><b>專業線稿的做法</b>　牆體以實心黑（poché）表示、外牆 15 cm／內牆 12 cm 兩種厚度；
    門是<b>牆留缺口＋門扇直線＋四分之一圓弧</b>；窗是<b>三條平行線</b>（外牆面兩條＋中間玻璃線）；
    陽台女兒牆只畫輪廓不塗黑，跟結構牆分開。</li>
    <li><b>圖面元素</b>　房間名稱＋面積（m²／坪）、四邊尺寸標註（分段＋總長）、指北針、比例尺、
    天花樑虛線、圖框與標題欄。</li>
    <li><b>兩個後端、同一份繪圖命令</b>　同一段繪圖程式碼同時輸出 SVG（向量）與 PNG（Pillow 點陣），
    所以兩張圖的內容一定一致，不會「向量圖跟點陣圖不一樣」。</li>
  </ul>
  <div class="tw"><table class="bd">
    <tr><th>房間</th><th>代號</th><th class="n">m²</th><th class="n">坪</th></tr>
__ROWS__
    <tr><td><b>合計（室內）</b></td><td class="pg"></td><td class="n"><b>__AREA__</b></td><td class="n"><b>__PING_IN__</b></td></tr>
  </table></div>

  <h2><span class="dot"></span>第二階段：3D 網頁怎麼生成</h2>
  <ul class="plain">
    <li><b>牆有洞</b>　程式把每道牆扣掉門窗後切成實體段，再把每個開口拆成「檯度以下的矮牆」與
    「上緣以上的過樑」——所以窗戶底下有牆、門上面有樑，牆不會是整片實心的。</li>
    <li><b>家具只用基本量體</b>　床、衣櫃、沙發、餐桌、廚具台、冰箱、馬桶、洗手台、洗衣機
    全部用方塊與圓柱拼出來，不載入任何外部模型檔。</li>
    <li><b>光線</b>　環境光＋半球光＋方向光（帶陰影），確保每個房間都看得清楚，不會一片黑。</li>
    <li><b>三種視角</b>　①軌道環繞（拖曳旋轉、滾輪縮放、右鍵平移）②俯視鳥瞰 ③第一人稱走動
    （WASD／方向鍵，滑鼠拖曳轉頭，撞到牆會停下來）。</li>
    <li><b>免費、單檔</b>　一個 HTML 檔＋CDN 載入的 Three.js，沒有 npm、沒有打包、沒有後端。</li>
  </ul>

  <h2><span class="dot"></span>怎麼操作</h2>
  <ul class="plain">
    <li><b>環繞</b>：拖曳＝旋轉、滾輪＝縮放、右鍵拖曳＝平移。</li>
    <li><b>走進室內</b>：按「走進室內」，用 <b>W A S D</b>（或方向鍵）前後左右移動，
    按住滑鼠拖曳可轉頭，<b>Shift</b> 加速、<b>Esc</b> 離開。</li>
    <li><b>點房間</b>：右側清單點一下，鏡頭會飛到那個房間；房間列表會標示目前所在。</li>
    <li><b>天花板</b>：可切換顯示／隱藏，隱藏時是「娃娃屋」視角，看得見隔間與家具。</li>
  </ul>

  <h2><span class="dot"></span>花了多少、用了什麼</h2>
  <ul class="plain">
    <li><b>工具</b>：Python 3（標準庫＋Pillow 畫點陣圖）、純 HTML/CSS/JS、Three.js（CDN）。</li>
    <li><b>費用</b>：<b>零</b>。沒有付費模型、沒有付費 API、沒有外部服務、沒有 npm 套件。</li>
    <li><b>驗收方式</b>：用真實瀏覽器開線上頁面截圖，再逐張看畫面確認（不是只看程式有沒有跑完）。</li>
    <li><b>可以怎麼用在自己家</b>：把 plan.json 的房間矩形改成自己家的尺寸，重跑一次
    make_plan.py，平面圖與 3D 就一起更新 —— 這就是「同一份資料」的價值。</li>
  </ul>

  <div class="box">
    <strong>內容說明</strong>：本頁的住宅格局為<b>示範用</b>的自行設計，非任何真實個案；
    所有圖面與 3D 都由腳本生成。文中不含任何帳號、憑證、個人識別或本機資訊。
    互動 3D 需要瀏覽器支援 WebGL；不支援時可用下方連結直接看平面圖。
  </div>
  <footer>小R頻道 · AI 助理實測 ｜ <a href="../">回 AI 助理實測</a></footer>
</div>

<script type="importmap">
{"imports":{
  "three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const CM = 0.01;
const $ = (s) => document.querySelector(s);
const canvas = $('#c');

const FLOOR_COLOR = {bedroom:0xe6d8c0, bath:0xcfe1ea, living:0xe8ddc9, dining:0xe8ddc9,
  kitchen:0xd8e2d4, corridor:0xe1e3e7, balcony:0xccd2c8};
const FURN_COLOR = {bed:0x9b7d63, bed_single:0x9b7d63, wardrobe:0xc2ad93, sofa:0x7f8fa1,
  coffee:0xb08f66, tv:0x6d737c, dtable:0xac8a62, chair:0x9d8568, cabinet:0xc2ad93,
  counter:0xd6d3cc, fridge:0xc8ced5, toilet:0xffffff, basin:0xffffff, shower:0x9fd2e3,
  washer:0xe2e5e8, desk:0xb28f65, nightstand:0xb28f65};

let plan = null, scene, camera, controls, renderer, ceiling, furnGroup, wallGroup;
let roomMeshes = {}, labels = {}, planCenter = new THREE.Vector3(5.8,0,4);
let mode = 'orbit';
let loaded = false;
const keys = {};
let yaw = 0, pitch = 0, dragging = false, walkVel = new THREE.Vector3();
const d = new THREE.Vector2();
let solidsForCollision = [];

const R = (hex, rough=0.85) => new THREE.MeshStandardMaterial({color:hex, roughness:rough, metalness:0.03});
const MAT = {
  wall: new THREE.MeshStandardMaterial({color:0xf7f5f1, roughness:0.95}),
  wallExt: new THREE.MeshStandardMaterial({color:0xece8e2, roughness:0.95}),
  parapet: new THREE.MeshStandardMaterial({color:0xdedbd5, roughness:0.95}),
  ceil: new THREE.MeshStandardMaterial({color:0xffffff, roughness:1, transparent:true,
        opacity:0.5, side:THREE.DoubleSide}),
  glass: new THREE.MeshStandardMaterial({color:0x9fd0e8, roughness:0.15, metalness:0.1,
        transparent:true, opacity:0.42}),
};

function box(w,h,dp,x,y,z,mat){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,dp), mat);
  m.position.set(x,y,z); m.castShadow = true; m.receiveShadow = true;
  return m;
}

// ── 牆：把開口切成「檯度以下矮牆 + 上緣以上過樑」 ───────────────
function wallSegments(w, H){
  const out = [];
  const ops = (w.openings||[]).slice().sort((a,b)=>a.s-b.s);
  let cur = w.a0;
  for (const o of ops){
    if (o.s > cur) out.push([cur, o.s, 0, H]);
    if (o.sill > 0) out.push([o.s, o.e, 0, o.sill]);
    if (o.head < H) out.push([o.s, o.e, o.head, H]);
    cur = Math.max(cur, o.e);
  }
  if (cur < w.a1) out.push([cur, w.a1, 0, H]);
  return out;
}

function addWall(w){
  const H = (w.kind === 'parapet') ? plan.parapet_height : plan.wall_height;
  const mat = w.kind === 'parapet' ? MAT.parapet : (w.kind === 'ext' ? MAT.wallExt : MAT.wall);
  for (const [s,e,h0,h1] of wallSegments(w, H)){
    const len = (e-s)*CM, th = w.t*CM, hh = (h1-h0)*CM;
    let ww, dd, cx, cz;
    if (w.axis === 'h'){ ww = len; dd = th; cx = (s+e)/2*CM; cz = w.b*CM; }
    else { ww = th; dd = len; cx = w.b*CM; cz = (s+e)/2*CM; }
    wallGroup.add(box(ww, hh, dd, cx, (h0+h1)/2*CM, cz, mat));
    if (h0 === 0 && h1 === H && w.kind !== 'parapet')
      solidsForCollision.push({x0:cx-ww/2, x1:cx+ww/2, z0:cz-dd/2, z1:cz+dd/2});
  }
  // 玻璃：窗與落地窗
  for (const o of (w.openings||[])){
    if (o.type !== 'window' && o.type !== 'slider') continue;
    const len = (o.e-o.s)*CM, th = 0.03, hh = (o.head-o.sill)*CM;
    let ww, dd, cx, cz;
    if (w.axis === 'h'){ ww = len; dd = th; cx = (o.s+o.e)/2*CM; cz = w.b*CM; }
    else { ww = th; dd = len; cx = w.b*CM; cz = (o.s+o.e)/2*CM; }
    wallGroup.add(box(ww, hh, dd, cx, (o.sill+o.head)/2*CM, cz, MAT.glass));
  }
}

// ── 家具：基本量體拼出來 ──────────────────────────────────────
function addFurn(f){
  const [x0,y0,x1,y1] = f.rect;
  const w = (x1-x0)*CM, dp = (y1-y0)*CM, h = f.h*CM;
  const cx = (x0+x1)/2*CM, cz = (y0+y1)/2*CM;
  const c = FURN_COLOR[f.type] || 0xb9b2a6;
  const g = new THREE.Group();
  const t = f.type;
  if (t === 'bed' || t === 'bed_single'){
    g.add(box(w, h*0.55, dp, cx, h*0.275, cz, R(c)));
    g.add(box(w*0.96, h*0.30, dp*0.94, cx, h*0.70, cz, R(0xf3f0ea)));
    const pw = t === 'bed' ? w*0.42 : w*0.62;
    g.add(box(pw, 0.10, dp*0.16, cx - (t==='bed'? w*0.23 : 0), h*0.88, cz - dp*0.36, R(0xffffff, 0.9)));
    if (t === 'bed')
      g.add(box(pw, 0.10, dp*0.16, cx + w*0.23, h*0.88, cz - dp*0.36, R(0xffffff, 0.9)));
  } else if (t === 'sofa'){
    g.add(box(w, h*0.45, dp, cx, h*0.225, cz, R(c)));
    g.add(box(w*0.22, h*0.95, dp, cx - w*0.39, h*0.475, cz, R(c)));
    g.add(box(w, h*0.95, dp*0.18, cx, h*0.475, cz - dp*0.41, R(c)));
  } else if (t === 'toilet'){
    g.add(box(w, h*0.75, dp*0.42, cx, h*0.375, cz - dp*0.29, R(0xffffff, 0.5)));
    const cyl = new THREE.Mesh(new THREE.CylinderGeometry(dp*0.30, dp*0.26, h*0.62, 18), R(0xffffff,0.5));
    cyl.position.set(cx, h*0.31, cz + dp*0.12); cyl.castShadow = true; g.add(cyl);
  } else if (t === 'basin'){
    g.add(box(w*0.55, h*0.78, dp*0.55, cx, h*0.39, cz, R(0xf0f0ee)));
    g.add(box(w, h*0.16, dp, cx, h*0.92, cz, R(0xffffff, 0.5)));
  } else if (t === 'shower'){
    g.add(box(w, 0.04, dp, cx, 0.02, cz, R(0xdfe6ea)));
    g.add(box(0.03, h, dp, cx - w/2, h/2, cz, MAT.glass));
    g.add(box(w, h, 0.03, cx, h/2, cz - dp/2, MAT.glass));
  } else if (t === 'dtable'){
    g.add(box(w, 0.05, dp, cx, h - 0.025, cz, R(c)));
    for (const sx of [-1,1]) for (const sz of [-1,1])
      g.add(box(0.06, h - 0.05, 0.06, cx + sx*(w/2-0.08), (h-0.05)/2, cz + sz*(dp/2-0.08), R(c)));
  } else if (t === 'desk'){
    g.add(box(w, 0.04, dp, cx, h - 0.02, cz, R(c)));
    for (const sx of [-1,1])
      g.add(box(0.05, h - 0.04, 0.05, cx + sx*(w/2-0.06), (h-0.04)/2, cz, R(c)));
  } else if (t === 'chair'){
    g.add(box(w, 0.05, dp, cx, h - 0.03, cz, R(c)));
    g.add(box(w, h*0.55, 0.05, cx, h*0.72, cz - dp/2, R(c)));
    for (const sx of [-1,1]) for (const sz of [-1,1])
      g.add(box(0.035, h-0.05, 0.035, cx + sx*(w/2-0.05), (h-0.05)/2, cz + sz*(dp/2-0.05), R(c)));
  } else if (t === 'tv'){
    g.add(box(w, h, dp, cx, h/2, cz, R(c)));
    g.add(box(0.04, 0.62, 1.08, cx - w/2 - 0.03, 0.95, cz, R(0x1a1d22, 0.4)));
  } else if (t === 'counter'){
    g.add(box(w, h*0.92, dp, cx, h*0.46, cz, R(c)));
    g.add(box(w, 0.04, dp, cx, h*0.96, cz, R(0x4b515a, 0.5)));
    if (w > 1.0) g.add(box(0.5, 0.01, 0.36, cx - 0.3, h*0.99, cz, R(0xb9c3cc, 0.3)));
    if (w < 1.0) for (let i=0;i<2;i++)
      g.add(new THREE.Mesh(new THREE.CylinderGeometry(0.09,0.09,0.02,14),
        R(0x2c3138,0.6)).translateX(cx).translateY(h*0.99).translateZ(cz - 0.28 + i*0.55));
  } else if (t === 'washer'){
    g.add(box(w, h, dp, cx, h/2, cz, R(c)));
    const c1 = new THREE.Mesh(new THREE.CylinderGeometry(0.22,0.22,0.05,18), R(0x8f979f,0.4));
    c1.rotation.x = Math.PI/2; c1.position.set(cx, h*0.55, cz + dp/2 + 0.01); g.add(c1);
  } else {
    g.add(box(w, h, dp, cx, h/2, cz, R(c)));
  }
  g.traverse(o => { if (o.isMesh){ o.castShadow = true; o.receiveShadow = true; } });
  return g;
}

function buildPlan(){
  const rooms = plan.rooms;
  let minx=1e9, maxx=-1e9, minz=1e9, maxz=-1e9;
  for (const r of rooms){
    minx = Math.min(minx, r.rect[0]); maxx = Math.max(maxx, r.rect[2]);
    minz = Math.min(minz, r.rect[1]); maxz = Math.max(maxz, r.rect[3]);
  }
  planCenter.set((minx+maxx)/2*CM, 0, (minz+maxz)/2*CM);

  // 地板
  for (const r of rooms){
    const w = (r.rect[2]-r.rect[0])*CM, dp = (r.rect[3]-r.rect[1])*CM;
    const cx = (r.rect[0]+r.rect[2])/2*CM, cz = (r.rect[1]+r.rect[3])/2*CM;
    const m = box(w, 0.06, dp, cx, -0.03, cz, R(FLOOR_COLOR[r.kind] || 0xe6e2d8, 0.95));
    m.userData.room = r.id;
    scene.add(m); roomMeshes[r.id] = m;
  }
  // 天花板
  const cw = (maxx-minx)*CM + 0.3, cd = (maxz-minz)*CM + 0.3;
  ceiling = box(cw, 0.06, cd, planCenter.x, plan.wall_height*CM + 0.03, planCenter.z, MAT.ceil);
  ceiling.castShadow = false; ceiling.visible = false;
  scene.add(ceiling);

  wallGroup = new THREE.Group(); scene.add(wallGroup);
  for (const w of plan.walls) addWall(w);

  furnGroup = new THREE.Group(); scene.add(furnGroup);
  for (const f of plan.furniture) furnGroup.add(addFurn(f));
}

// ── 房間標籤（把 3D 座標投影到畫面，用 HTML 顯示）─────────────
function buildLabels(){
  const box = $('#labels');
  for (const r of plan.rooms){
    const el = document.createElement('div');
    el.className = 'lab'; el.textContent = r.name;
    box.appendChild(el);
    labels[r.id] = {el:el, p:new THREE.Vector3((r.rect[0]+r.rect[2])/2*CM,
                                               1.25, (r.rect[1]+r.rect[3])/2*CM)};
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.textContent = r.name + '　' + r.area_m2 + ' m²';
    a.dataset.room = r.id;
    a.addEventListener('click', () => flyTo(r.id));
    li.appendChild(a); $('#roomlist').appendChild(li);
  }
}
function updateLabels(){
  const el = $('#labels');
  const show = (mode === 'orbit');
  el.style.display = show ? 'block' : 'none';
  if (!show) return;
  const w = el.clientWidth || 1, h = el.clientHeight || 1;
  for (const id in labels){
    const L = labels[id];
    const v = L.p.clone().project(camera);
    if (v.z > 1 || v.x < -1 || v.x > 1 || v.y < -1 || v.y > 1){ L.el.style.display='none'; continue; }
    L.el.style.display = 'block';
    L.el.style.left = ((v.x*0.5+0.5)*w) + 'px';
    L.el.style.top = ((-v.y*0.5+0.5)*h) + 'px';
  }
}

// ── 鏡頭飛行 ────────────────────────────────────────────────
let fly = null;
function flyTo(roomId){
  const r = plan.rooms.find(x => x.id === roomId);
  if (!r) return;
  const cx = (r.rect[0]+r.rect[2])/2*CM, cz = (r.rect[1]+r.rect[3])/2*CM;
  const zh = Math.max(3.2, Math.min(8.5, (r.rect[2]-r.rect[0])*CM*2.6));
  const to = new THREE.Vector3(cx, zh*0.85, cz + zh*1.15);
  const look = new THREE.Vector3(cx, Math.min(1.2, plan.wall_height*CM*0.42), cz);
  fly = {t:0, p0:camera.position.clone(), p1:to, c0:controls.target.clone(), c1:look};
  document.querySelectorAll('#roomlist a').forEach(a =>
    a.classList.toggle('cur', a.dataset.room === roomId));
}
function resetView(){
  camera.position.set(planCenter.x, 9.6, planCenter.z + 8.4);
  controls.target.set(planCenter.x, 0.9, planCenter.z);
  document.querySelectorAll('#roomlist a').forEach(a => a.classList.remove('cur'));
}

// ── 第一人稱 ────────────────────────────────────────────────
function enterWalk(){
  const r = plan.rooms.find(x => x.id === 'living');
  camera.position.set((r.rect[0]+r.rect[2])/2*CM, 1.62, (r.rect[1]+r.rect[3])/2*CM);
  const dir = new THREE.Vector3(planCenter.x - camera.position.x, 0, planCenter.z - camera.position.z);
  yaw = Math.atan2(-dir.x, -dir.z); pitch = -0.05;
  mode = 'walk'; controls.enabled = false; camera.fov = 72; camera.updateProjectionMatrix();
  $('#hint').textContent = 'W A S D／方向鍵移動・拖曳滑鼠轉頭・Shift 加速・Esc 離開';
  $('#bwalk').classList.add('on');
  document.querySelectorAll('#roomlist a').forEach(a => a.classList.remove('cur'));
}
function exitWalk(){
  mode = 'orbit'; controls.enabled = true; camera.fov = 55; camera.updateProjectionMatrix();
  $('#hint').textContent = '拖曳＝環繞／滾輪＝縮放／右鍵拖曳＝平移';
  $('#bwalk').classList.remove('on'); resetView();
}
function blocked(x, z){
  const pad = 0.16;
  for (const s of solidsForCollision)
    if (x > s.x0-pad && x < s.x1+pad && z > s.z0-pad && z < s.z1+pad) return true;
  return false;
}
function walkMove(dt){
  const sp = (keys['shift'] ? 3.4 : 1.9) * dt;
  let fx = 0, fz = 0;
  if (keys['w'] || keys['arrowup']) fz -= 1;
  if (keys['s'] || keys['arrowdown']) fz += 1;
  if (keys['a'] || keys['arrowleft']) fx -= 1;
  if (keys['d'] || keys['arrowright']) fx += 1;
  if (!fx && !fz) return;
  const len = Math.hypot(fx, fz); fx /= len; fz /= len;
  const sin = Math.sin(yaw), cos = Math.cos(yaw);
  const dx = (fx*cos + fz*sin) * sp;
  const dz = (-fx*sin + fz*cos) * sp;
  const nx = camera.position.x + dx, nz = camera.position.z + dz;
  if (!blocked(nx, camera.position.z)) camera.position.x = nx;
  if (!blocked(camera.position.x, nz)) camera.position.z = nz;
  camera.position.x = Math.max(-1.6, Math.min(planCenter.x*2+1.6, camera.position.x));
  camera.position.z = Math.max(-1.6, Math.min(planCenter.z*2+1.6, camera.position.z));
}
function applyLook(){
  const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ'));
  camera.quaternion.copy(q);
}

// ── 初始化 ──────────────────────────────────────────────────
function initThree(){
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xeef1f4);
  scene.fog = new THREE.Fog(0xeef1f4, 26, 60);
  camera = new THREE.PerspectiveCamera(55, 1, 0.1, 300);
  renderer = new THREE.WebGLRenderer({canvas:canvas, antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true; controls.dampingFactor = 0.08;
  controls.maxPolarAngle = Math.PI*0.495; controls.minDistance = 1.2; controls.maxDistance = 40;

  scene.add(new THREE.AmbientLight(0xffffff, 0.55));
  scene.add(new THREE.HemisphereLight(0xffffff, 0xc9cfd6, 0.75));
  const sun = new THREE.DirectionalLight(0xfff5e6, 1.55);
  sun.position.set(14, 19, 11); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  const sc = sun.shadow.camera;
  sc.left = -16; sc.right = 16; sc.top = 16; sc.bottom = -16; sc.near = 1; sc.far = 60;
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0xdfe9ff, 0.45);
  fill.position.set(-12, 12, -9); scene.add(fill);

  resize();
  addEventListener('resize', resize);
}
function resize(){
  const st = document.querySelector('.stage');
  const w = st.clientWidth, h = st.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h; camera.updateProjectionMatrix();
}

function animate(t){
  requestAnimationFrame(animate);
  if (!renderer) return;
  if (plan){
    if (mode === 'walk'){
      walkMove(1/60); applyLook();
    } else {
      if (fly){
        fly.t = Math.min(1, fly.t + 0.028);
        const e = 1 - Math.pow(1 - fly.t, 3);
        camera.position.lerpVectors(fly.p0, fly.p1, e);
        controls.target.lerpVectors(fly.c0, fly.c1, e);
        if (fly.t >= 1) fly = null;
      }
      controls.update();
    }
    updateLabels();
  }
  renderer.render(scene, camera);
  if (plan && !loaded){ loaded = true; const ld = $('#loading'); if (ld) ld.style.display = 'none'; }
}

// ── 互動 ────────────────────────────────────────────────────
$('#b3d').addEventListener('click', () => {
  $('#c').style.display='block'; $('#plan2d').style.display='none';
  $('#labels').style.display='block'; $('#hint').style.display='block';
  $('#b3d').classList.add('on'); $('#b2d').classList.remove('on');
  if (mode === 'walk') exitWalk();
  resize();
});
$('#b2d').addEventListener('click', () => {
  $('#plan2d').style.display='block'; $('#c').style.display='none';
  $('#labels').style.display='none'; $('#hint').style.display='none';
  $('#b2d').classList.add('on'); $('#b3d').classList.remove('on');
  if (mode === 'walk') exitWalk();
});
$('#bwalk').addEventListener('click', () => { if (mode === 'walk') exitWalk(); else enterWalk(); });
$('#bceil').addEventListener('click', () => {
  if (!ceiling) return; ceiling.visible = !ceiling.visible;
  $('#bceil').classList.toggle('on', ceiling.visible);
});
$('#breset').addEventListener('click', () => { if (mode==='walk') exitWalk(); else resetView(); });

canvas.addEventListener('mousedown', e => { if (mode === 'walk'){ dragging = true; d.set(e.clientX, e.clientY); } });
addEventListener('mouseup', () => dragging = false);
addEventListener('mousemove', e => {
  if (!dragging || mode !== 'walk') return;
  yaw -= (e.clientX - d.x) * 0.0045;
  pitch -= (e.clientY - d.y) * 0.0032;
  pitch = Math.max(-1.15, Math.min(1.15, pitch));
  d.set(e.clientX, e.clientY);
});
canvas.style.touchAction = 'none';
addEventListener('keydown', e => {
  const k = e.key.toLowerCase();
  keys[k] = true; if (k === 'shift') keys['shift'] = true;
  if (k === ' ' || (k === 'arrowup' && mode==='walk')) e.preventDefault();
  if (k === 'escape' && mode === 'walk') exitWalk();
});
addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

initThree();
animate();
fetch('plan.json').then(r => r.json()).then(p => {
  plan = p;
  if (p && p.rooms) $('#plan2d').src = 'plan.svg';
  buildPlan(); buildLabels(); resetView();
}).catch(() => {
  $('#fb').style.display = 'block'; $('#loading').style.display = 'none';
  $('#plan2d').style.display = 'none';
});
</script>
</body>
</html>
"""

HTML = (HTML
        .replace("__NROOM__", str(N_ROOM))
        .replace("__AREA__", str(AREA))
        .replace("__BAL__", str(BAL))
        .replace("__PING__", str(PING))
        .replace("__PING_IN__", str(PING_IN))
        .replace("__WH__", str(plan["wall_height"]))
        .replace("__EW__", str(plan["exterior_wall"]))
        .replace("__IW__", str(plan["interior_wall"]))
        .replace("__NFURN__", str(len(plan["furniture"])))
        .replace("__ROWS__", ROWS))


def build():
    out = os.path.join(SITE, "ai", SLUG)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8", newline="\n").write(HTML)
    for fn in ("plan.json", "plan.svg", "plan.png"):
        shutil.copy2(os.path.join(ASSETS, fn), os.path.join(out, fn))
    print("wrote", os.path.join(out, "index.html"), len(HTML), "chars")
    print("copied plan.json / plan.svg / plan.png")


if __name__ == "__main__":
    build()
