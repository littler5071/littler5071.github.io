/* ===== 粒子特效引擎（Canvas） ===== */
(function (global) {
  'use strict';

  const FX = {
    canvas: null,
    ctx: null,
    W: 0, H: 0, dpr: 1,
    accent: '#f5c461',
    embers: [],
    vortexParts: [],
    names: [],
    confetti: [],
    rings: [],
    vortexActive: false,
    intensity: 1,
    _last: 0,
    _raf: null
  };

  function rand(a, b) { return a + Math.random() * (b - a); }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  FX.init = function (canvas) {
    FX.canvas = canvas;
    FX.ctx = canvas.getContext('2d');
    resize();
    global.addEventListener('resize', resize);
    seedEmbers();
    FX._last = performance.now();
    if (!FX._raf) FX._raf = requestAnimationFrame(loop);
  };

  function resize() {
    if (!FX.canvas) return;
    FX.dpr = Math.min(2, global.devicePixelRatio || 1);
    FX.W = FX.canvas.clientWidth || global.innerWidth;
    FX.H = FX.canvas.clientHeight || global.innerHeight;
    FX.canvas.width = Math.floor(FX.W * FX.dpr);
    FX.canvas.height = Math.floor(FX.H * FX.dpr);
    FX.ctx.setTransform(FX.dpr, 0, 0, FX.dpr, 0, 0);
    seedEmbers();
  }

  FX.setAccent = function (color, intensity) {
    FX.accent = color || '#f5c461';
    FX.intensity = intensity || 1;
  };

  /* ---------- 飄雪 ---------- */
  function seedEmbers() {
    const n = Math.round(Math.min(130, Math.max(45, FX.W / 14)));
    FX.embers = [];
    for (let i = 0; i < n; i++) {
      const big = Math.random() < .14;      // 少數大片的「景深雪」
      FX.embers.push({
        x: rand(0, FX.W || 1920),
        y: rand(0, FX.H || 1080),
        r: big ? rand(3.8, 7) : rand(1.2, 3.2),
        vy: big ? rand(12, 28) : rand(26, 70),
        vx: rand(-8, 8),
        sway: rand(8, 28),
        a: big ? rand(.1, .22) : rand(.38, .92),
        tw: rand(0, Math.PI * 2),
        gold: Math.random() < .18
      });
    }
  }

  /* ---------- 漩渦粒子 ---------- */
  function spawnVortex(count) {
    const min = Math.min(FX.W, FX.H);
    const max = Math.max(FX.W, FX.H);
    for (let i = 0; i < count; i++) {
      FX.vortexParts.push({
        ang: rand(0, Math.PI * 2),
        rad: rand(min * .34, max * .58),
        spin: rand(.0028, .0075) * (Math.random() < .5 ? 1 : -1),
        fall: rand(.9, 2.4),
        px: 0, py: 0,
        alpha: rand(.15, .7),
        w: rand(.7, 2)
      });
    }
  }

  FX.vortex = function (on) {
    FX.vortexActive = !!on;
    if (on) spawnVortex(160);
    else FX.vortexParts.length = 0;
  };

  /* ---------- 背景名字雲（候選人姓名） ---------- */
  FX.nameCloud = function (names, on) {
    FX.names.length = 0;
    if (!on) return;
    const list = (names || []).filter(Boolean);
    if (!list.length) return;
    const count = Math.min(20, Math.max(10, Math.round(FX.W / 95)));
    const cx = FX.W / 2;
    const cy = FX.H * .46;
    for (let i = 0; i < count; i++) {
      const a = rand(0, Math.PI * 2);
      const r = rand(Math.min(FX.W, FX.H) * .2, Math.max(FX.W, FX.H) * .46);
      const size = rand(FX.W * .04, FX.W * .072);
      FX.names.push({
        text: pick(list),
        x: cx + Math.cos(a) * r,
        y: cy + Math.sin(a) * r * .58,
        vx: rand(-14, 14),
        vy: rand(-20, -4),
        size,
        font: `900 ${Math.round(size)}px "Microsoft JhengHei","Noto Sans TC","PingFang TC",sans-serif`,
        alpha: rand(.10, .2),
        rot: rand(-.14, .14),
        vr: rand(-.12, .12),
        dying: false
      });
    }
  };

  FX.nameScatter = function () {
    const cx = FX.W / 2;
    const cy = FX.H * .46;
    for (const n of FX.names) {
      const a = Math.atan2(n.y - cy, n.x - cx) + rand(-.4, .4);
      const sp = rand(420, 1150);
      n.vx = Math.cos(a) * sp;
      n.vy = Math.sin(a) * sp;
      n.vr = rand(-1.8, 1.8);
      n.dying = true;
    }
  };

  /* ---------- 爆發 ---------- */
  FX.burst = function (power) {
    const p = power || 1;
    const cx = FX.W / 2;
    const cy = FX.H * .46;
    const colors = ['#c8102e', '#128a4a', '#e0a63c', '#7a1a2a', '#2f8fb5', '#fff3dc'];

    const n = Math.round(150 * p * FX.intensity);
    for (let i = 0; i < n; i++) {
      const a = rand(0, Math.PI * 2);
      const sp = rand(90, 760) * p;
      FX.confetti.push({
        x: cx + rand(-160, 160),
        y: cy + rand(-110, 110),
        vx: Math.cos(a) * sp,
        vy: Math.sin(a) * sp - rand(60, 320),
        g: rand(520, 900),
        w: rand(5, 12),
        h: rand(8, 22),
        rot: rand(0, Math.PI * 2),
        vr: rand(-9, 9),
        color: pick(colors),
        life: rand(1.6, 3.4),
        age: 0,
        shape: Math.random() < .28 ? 'circle' : 'rect'
      });
    }
    // 左右彩帶加農炮
    const cannon = (x, dir) => {
      const m = Math.round(55 * p * FX.intensity);
      for (let i = 0; i < m; i++) {
        FX.confetti.push({
          x: x + rand(-40, 40),
          y: FX.H * .92 + rand(-30, 20),
          vx: dir * rand(200, 780) + rand(-90, 90),
          vy: rand(-1400, -760),
          g: rand(720, 1020),
          w: rand(6, 13),
          h: rand(10, 26),
          rot: rand(0, Math.PI * 2),
          vr: rand(-11, 11),
          color: pick(colors),
          life: rand(2.2, 4.2),
          age: 0,
          shape: Math.random() < .22 ? 'circle' : 'rect'
        });
      }
    };
    cannon(0, 1);
    cannon(FX.W, -1);

    for (let i = 0; i < 4; i++) {
      FX.rings.push({ r: 20, max: FX.W * (.32 + i * .13), age: 0, life: .85 + i * .2, w: 3.4 - i * .65 });
    }
  };

  FX.sparkle = function () {
    for (let i = 0; i < 40; i++) {
      const a = rand(0, Math.PI * 2);
      FX.confetti.push({
        x: FX.W / 2, y: FX.H * .46,
        vx: Math.cos(a) * rand(40, 260),
        vy: Math.sin(a) * rand(40, 260),
        g: rand(200, 400), w: 2.5, h: 2.5, rot: 0, vr: 0,
        color: '#e0a63c', life: rand(.7, 1.6), age: 0, shape: 'circle'
      });
    }
  };

  FX.clear = function () {
    FX.confetti.length = 0;
    FX.rings.length = 0;
    FX.vortexParts.length = 0;
    FX.names.length = 0;
    FX.vortexActive = false;
  };

  /* ---------- 主迴圈 ---------- */
  function loop(now) {
    const dt = Math.min(0.05, (now - FX._last) / 1000 || 0.016);
    FX._last = now;
    const c = FX.ctx;
    if (!c) return;

    c.clearRect(0, 0, FX.W, FX.H);
    c.globalCompositeOperation = 'lighter';

    /* 飄雪 */
    for (const e of FX.embers) {
      e.y += e.vy * dt;
      e.x += e.vx * dt + Math.sin(now / 1400 + e.tw) * e.sway * dt;
      e.tw += dt * 1.6;
      if (e.y > FX.H + 16) { e.y = -16; e.x = rand(0, FX.W); }
      if (e.x < -20) e.x = FX.W + 10;
      if (e.x > FX.W + 20) e.x = -10;
      const a = e.a * (0.72 + 0.28 * Math.sin(e.tw * 2));
      if (e.gold) {
        // 深紅星芒
        const s = e.r * 2.4;
        c.fillStyle = hexA('#b3122a', a * .9);
        c.fillRect(e.x - s, e.y - 0.7, s * 2, 1.4);
        c.fillRect(e.x - 0.7, e.y - s, 1.4, s * 2);
        c.beginPath();
        c.arc(e.x, e.y, Math.max(1, e.r * .55), 0, Math.PI * 2);
        c.fill();
      } else {
        c.beginPath();
        c.fillStyle = hexA('#e8b45a', a * .7);
        c.arc(e.x, e.y, e.r, 0, Math.PI * 2);
        c.fill();
      }
    }

    /* 背景名字雲 */
    if (FX.names.length) {
      for (let i = FX.names.length - 1; i >= 0; i--) {
        const n = FX.names[i];
        if (n.dying) {
          n.alpha -= dt * .5;
          if (n.alpha <= 0) { FX.names.splice(i, 1); continue; }
        }
        n.x += n.vx * dt;
        n.y += n.vy * dt;
        n.rot += n.vr * dt;
        if (!n.dying) {
          if (n.x < -280) n.x = FX.W + 220;
          if (n.x > FX.W + 280) n.x = -220;
          if (n.y < -180) n.y = FX.H + 140;
          if (n.y > FX.H + 200) n.y = -160;
        }
        c.save();
        c.translate(n.x, n.y);
        c.rotate(n.rot);
        c.font = n.font;
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillStyle = hexA('#a3122b', n.alpha * .85);
        c.fillText(n.text, 0, 0);
        c.restore();
      }
    }

    /* 漩渦 */
    if (FX.vortexActive) {
      const cx = FX.W / 2, cy = FX.H * .46;
      for (const v of FX.vortexParts) {
        v.ang += v.spin * 60 * dt * (1 + (1 - v.rad / (Math.max(FX.W, FX.H) * .8)) * 2.2);
        v.rad -= v.fall * 60 * dt * (0.4 + v.rad / (FX.W * .5));
        if (v.rad < 26) {
          v.rad = rand(Math.min(FX.W, FX.H) * .34, Math.max(FX.W, FX.H) * .58);
          v.ang = rand(0, Math.PI * 2);
        }
        const x = cx + Math.cos(v.ang) * v.rad;
        const y = cy + Math.sin(v.ang) * v.rad * .62;
        const px = cx + Math.cos(v.ang - v.spin * 15) * (v.rad + 34);
        const py = cy + Math.sin(v.ang - v.spin * 15) * (v.rad + 34) * .62;
        c.beginPath();
        c.strokeStyle = hexA('#cf9236', v.alpha * .45);
        c.lineWidth = v.w * 1.25;
        c.moveTo(px, py);
        c.lineTo(x, y);
        c.stroke();
      }
    }

    /* 彩帶 */
    for (let i = FX.confetti.length - 1; i >= 0; i--) {
      const p = FX.confetti[i];
      p.age += dt;
      if (p.age > p.life) { FX.confetti.splice(i, 1); continue; }
      p.vy += p.g * dt;
      p.vx *= (1 - 0.9 * dt);
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.rot += p.vr * dt;
      const fade = Math.max(0, 1 - p.age / p.life);
      c.save();
      c.translate(p.x, p.y);
      c.rotate(p.rot);
      c.globalAlpha = Math.min(1, fade * 1.6);
      c.fillStyle = p.color;
      if (p.shape === 'circle') {
        c.beginPath(); c.arc(0, 0, p.w * .55, 0, Math.PI * 2); c.fill();
      } else {
        c.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * (0.5 + 0.5 * Math.abs(Math.cos(p.rot))));
      }
      c.restore();
    }

    /* 光環 */
    c.globalCompositeOperation = 'lighter';
    for (let i = FX.rings.length - 1; i >= 0; i--) {
      const r = FX.rings[i];
      r.age += dt;
      const t = r.age / r.life;
      if (t >= 1) { FX.rings.splice(i, 1); continue; }
      r.r = 20 + (r.max - 20) * easeOut(t);
      c.beginPath();
      c.strokeStyle = hexA(FX.accent, (1 - t) * .55);
      c.lineWidth = r.w * (1 - t) + .3;
      c.arc(FX.W / 2, FX.H * .46, r.r, 0, Math.PI * 2);
      c.stroke();
    }

    c.globalCompositeOperation = 'source-over';
    FX._raf = requestAnimationFrame(loop);
  }

  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

  function hexA(hex, a) {
    const h = hex.replace('#', '');
    const full = h.length === 3 ? h.split('').map(x => x + x).join('') : h;
    const n = parseInt(full, 16);
    const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    return `rgba(${r},${g},${b},${a})`;
  }

  global.FX = FX;
})(window);
