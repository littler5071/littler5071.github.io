/* ===== FESTIVE FX · 彩色紙屑＋雪花（裝飾用，不影響抽獎邏輯） ===== */
(function () {
  "use strict";

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isStage = document.body.classList.contains("stage");
  if (!isStage) return; // 控制台不加任何特效

  var cv = document.createElement("canvas");
  cv.id = "festiveFx";
  document.body.appendChild(cv);
  var ctx = cv.getContext("2d");

  var W = 0, H = 0, DPR = Math.min(window.devicePixelRatio || 1, 2);
  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    cv.width = Math.floor(W * DPR); cv.height = Math.floor(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  resize();
  window.addEventListener("resize", resize);

  var COLORS = ["#c8102e", "#16a34a", "#d69e18", "#fff1c9", "#ff5d73"];

  function rnd(a, b) { return a + Math.random() * (b - a); }
  function pick(a) { return a[(Math.random() * a.length) | 0]; }

  var flakes = [];
  var count = reduce ? 0 : 80;
  for (var i = 0; i < count; i++) {
    flakes.push({
      x: rnd(0, W), y: rnd(0, H),
      r: rnd(1.6, 4.2),
      vy: rnd(0.15, 0.55),
      vx: rnd(-0.18, 0.18),
      a: rnd(0.25, 0.65),
      c: Math.random() < 0.72 ? "#ffffff" : (Math.random() < 0.6 ? "#ffd166" : pick(["#c8102e", "#16a34a", "#b3760f"]))
    });
  }

  var confetti = [];
  function burst(n, x, y, power) {
    if (reduce) return;
    for (var i = 0; i < n; i++) {
      var ang = rnd(-Math.PI * 0.85, -Math.PI * 0.15);
      var sp = rnd(3, 9) * (power || 1);
      confetti.push({
        x: x, y: y,
        vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp,
        w: rnd(4, 10), h: rnd(6, 14),
        rot: rnd(0, Math.PI * 2), vr: rnd(-0.22, 0.22),
        c: pick(COLORS),
        life: rnd(90, 170), age: 0
      });
    }
  }

  var last = 0;
  function loop(t) {
    if (t - last < 28) { requestAnimationFrame(loop); return; } // ~35fps
    last = t;
    ctx.clearRect(0, 0, W, H);

    // 雪花 / 彩點
    for (var i = 0; i < flakes.length; i++) {
      var f = flakes[i];
      f.y += f.vy; f.x += f.vx + Math.sin((f.y + i * 40) / 90) * 0.25;
      if (f.y > H + 8) { f.y = -8; f.x = rnd(0, W); }
      if (f.x < -8) f.x = W + 8; if (f.x > W + 8) f.x = -8;
      ctx.globalAlpha = f.a;
      ctx.fillStyle = f.c;
      ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2); ctx.fill();
    }

    // 紙屑
    for (var j = confetti.length - 1; j >= 0; j--) {
      var p = confetti[j];
      p.age++;
      p.vy += 0.16; p.vx *= 0.99;
      p.x += p.vx; p.y += p.vy; p.rot += p.vr;
      if (p.age > p.life || p.y > H + 40) { confetti.splice(j, 1); continue; }
      ctx.globalAlpha = Math.max(0, 1 - p.age / p.life);
      ctx.save();
      ctx.translate(p.x, p.y); ctx.rotate(p.rot);
      ctx.fillStyle = p.c;
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
      ctx.restore();
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);


  /* ---------- 松枝與聖誕樹剪影（純 SVG，舞台專用） ---------- */
  function svgEl(name, attrs) {
    var el = document.createElementNS("http://www.w3.org/2000/svg", name);
    for (var k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }

  function branch(len, thickness, flip) {
    // 主枝：一條弧線，沿線長出針葉
    var g = svgEl("g", { transform: flip ? "scale(-1,1)" : "" });
    var stem = svgEl("path", {
      d: "M0,0 C" + (len * 0.35) + "," + (-len * 0.16) + " " + (len * 0.72) + "," + (-len * 0.30) + " " + len + "," + (-len * 0.46),
      stroke: "#14532d", "stroke-width": thickness, fill: "none", "stroke-linecap": "round", opacity: ".55"
    });
    g.appendChild(stem);
    var n = 26;
    for (var i = 3; i < n; i++) {
      var t = i / n;
      var x = len * t;
      var y = -len * 0.46 * t * t - len * 0.10 * t;
      var nl = (1 - t) * len * 0.16 + len * 0.03;
      var up = svgEl("path", {
        d: "M" + x + "," + y + " l" + (nl * 0.75) + "," + (-nl) + " M" + x + "," + y + " l" + (nl * 0.85) + "," + (nl * 0.55),
        stroke: "#14532d", "stroke-width": Math.max(1.4, thickness * 0.28), "stroke-linecap": "round", fill: "none", opacity: ".5"
      });
      g.appendChild(up);
    }
    return g;
  }

  function buildDeco() {
    var svg = svgEl("svg", {
      class: "xmas-deco", viewBox: "0 0 1280 720", preserveAspectRatio: "xMidYMid slice"
    });
    // 左下松枝
    var g1 = svgEl("g", { transform: "translate(-40,760) rotate(-14)" });
    g1.appendChild(branch(560, 16, false));
    g1.appendChild(branch(430, 12, false).cloneNode(true));
    svg.appendChild(g1);
    // 右下松枝（鏡像）
    var g2 = svgEl("g", { transform: "translate(1320,770) rotate(194)" });
    g2.appendChild(branch(560, 16, false));
    svg.appendChild(g2);

    // 聖誕樹剪影（左下，淡淡的）
    var tree = svgEl("g", { class: "tree", transform: "translate(120, 620) scale(1)" });
    tree.appendChild(svgEl("path", { d: "M0,0 L120,-300 L240,0 Z" }));
    tree.appendChild(svgEl("path", { d: "M18,-60 L120,-330 L222,-60 Z" }));
    tree.appendChild(svgEl("path", { d: "M40,-150 L120,-400 L200,-150 Z" }));
    tree.appendChild(svgEl("rect", { x: "108", y: "0", width: "24", height: "54", fill: "#5b3a1e", opacity: ".5" }));
    svg.appendChild(tree);
    var star = svgEl("path", {
      class: "tree-star",
      d: "M120,-430 l10,26 28,2 -22,18 7,28 -23,-15 -23,15 7,-28 -22,-18 28,-2 z"
    });
    svg.appendChild(star);

    document.body.appendChild(svg);
  }
  buildDeco();

  // 中獎時噴彩帶：監看 #winners / #name 的變化
  function watch(el, cb) {
    if (!el) return;
    new MutationObserver(cb).observe(el, { childList: true, subtree: true, characterData: true, attributes: true });
  }

  var winners = document.getElementById("winners");
  if (winners) {
    watch(winners, function () {
      if (winners.classList.contains("show") || winners.children.length) {
        burst(70, W * 0.5, H * 0.42, 1.15);
        burst(40, W * 0.22, H * 0.5, 0.9);
        burst(40, W * 0.78, H * 0.5, 0.9);
      }
    });
  }

  // 舞台中獎名字出現時，再多一波
  if (isStage) {
    var nameEl = document.getElementById("name");
    var lastName = nameEl ? nameEl.textContent : "";
    if (nameEl) {
      watch(nameEl, function () {
        var now = nameEl.textContent;
        if (now && now !== lastName && now !== "LUCKY DRAW") {
          lastName = now;
          burst(90, W * 0.5, H * 0.38, 1.25);
        }
      });
    }
    // 待機時偶爾飄一點彩點
    if (!reduce) setInterval(function () {
      if (document.body.dataset.phase === "idle") burst(10, rnd(W * 0.1, W * 0.9), H + 10, 0.55);
    }, 4200);
  }

  // 點畫面也可以放一次（方便測試）
  window.addEventListener("keydown", function (e) {
    if (e.key === "t" || e.key === "T") burst(60, W / 2, H * 0.45, 1);
  });
})();
