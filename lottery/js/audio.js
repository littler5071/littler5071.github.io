/* ===== 聖誕主題音效 + 背景音樂（WebAudio 即時合成，無音檔） =====
   BGM：112 BPM，C–Am–F–G 四小節循環，雪橇鈴＋貝斯＋和聲＋鐘聲旋律
   抽獎音效：銅管、定音鼓、鈸、小鼓、教堂鐘，組成短樂句
*/
(function (global) {
  'use strict';

  const SFX = {
    ctx: null,
    master: null,
    comp: null,
    enabled: true,
    unlocked: false,
    _noise: null,
    _drone: null,
    _bgm: null,
    _bgmMedia: null,
    _bgmFailed: false,
    _applauseMedia: null
  };

  function t0() { return SFX.ctx.currentTime; }
  function ok() { return !!(SFX.enabled && SFX.ctx && SFX.unlocked); }

  SFX.unlock = function () {
    if (SFX.ctx) {
      if (SFX.ctx.state === 'suspended') SFX.ctx.resume();
      SFX.unlocked = true;
      return true;
    }
    const AC = global.AudioContext || global.webkitAudioContext;
    if (!AC) return false;
    try {
      SFX.ctx = new AC();
      SFX.comp = SFX.ctx.createDynamicsCompressor();
      SFX.comp.threshold.value = -14;
      SFX.comp.knee.value = 22;
      SFX.comp.ratio.value = 8;
      SFX.comp.attack.value = 0.003;
      SFX.comp.release.value = 0.22;

      SFX.master = SFX.ctx.createGain();
      SFX.master.gain.value = 0.85;
      SFX.master.connect(SFX.comp);
      SFX.comp.connect(SFX.ctx.destination);

      const len = SFX.ctx.sampleRate * 2;
      const buf = SFX.ctx.createBuffer(1, len, SFX.ctx.sampleRate);
      const data = buf.getChannelData(0);
      for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
      SFX._noise = buf;

      SFX.unlocked = true;
      if (SFX.ctx.state === 'suspended') SFX.ctx.resume();
      return true;
    } catch (e) {
      return false;
    }
  };

  function noiseSrc() {
    const s = SFX.ctx.createBufferSource();
    s.buffer = SFX._noise;
    s.loop = true;
    return s;
  }

  function gainNode() {
    const g = SFX.ctx.createGain();
    g.connect(SFX.master);
    return g;
  }

  /* ================= 樂器 ================= */

  /* 教堂鐘（加法合成） */
  function bell(freq, dur, gain, delay) {
    if (!ok()) return;
    const t = t0() + (delay || 0);
    const partials = [1, 2.0, 2.76, 3.0, 4.07];
    const amps = [1, 0.5, 0.3, 0.2, 0.11];
    for (let i = 0; i < partials.length; i++) {
      const o = SFX.ctx.createOscillator();
      const g = gainNode();
      o.type = 'sine';
      o.frequency.value = freq * partials[i];
      const decay = Math.max(0.12, dur * (1 - i * 0.1));
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(Math.max(0.0002, gain * amps[i]), t + 0.004);
      g.gain.exponentialRampToValueAtTime(0.0001, t + decay);
      o.connect(g);
      o.start(t);
      o.stop(t + decay + 0.06);
    }
  }

  /* 銅管：兩支鋸齒波 + 低通 */
  function brass(freq, t, dur, gain) {
    if (!ok()) return;
    const o = SFX.ctx.createOscillator();
    const o2 = SFX.ctx.createOscillator();
    const lp = SFX.ctx.createBiquadFilter();
    const g = gainNode();
    o.type = 'sawtooth'; o.frequency.value = freq;
    o2.type = 'sawtooth'; o2.frequency.value = freq * 1.006;
    lp.type = 'lowpass';
    lp.frequency.setValueAtTime(3000, t);
    lp.frequency.exponentialRampToValueAtTime(1100, t + dur);
    lp.Q.value = 0.8;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(gain, t + 0.02);
    g.gain.setValueAtTime(gain * 0.9, t + Math.min(dur * 0.6, 0.8));
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(lp); o2.connect(lp); lp.connect(g);
    o.start(t); o2.start(t);
    o.stop(t + dur + 0.05); o2.stop(t + dur + 0.05);
  }

  /* 定音鼓 */
  function timpani(t, gain, freq) {
    if (!ok()) return;
    const f = freq || 86;
    const o = SFX.ctx.createOscillator();
    const g = gainNode();
    o.type = 'sine';
    o.frequency.setValueAtTime(f * 1.7, t);
    o.frequency.exponentialRampToValueAtTime(f * 0.92, t + 0.14);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(gain, t + 0.007);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.95);
    o.connect(g); o.start(t); o.stop(t + 1.0);

    const src = noiseSrc();
    const lp = SFX.ctx.createBiquadFilter();
    lp.type = 'lowpass'; lp.frequency.value = 340;
    const g2 = gainNode();
    g2.gain.setValueAtTime(gain * 0.55, t);
    g2.gain.exponentialRampToValueAtTime(0.0001, t + 0.26);
    src.connect(lp); lp.connect(g2);
    src.start(t); src.stop(t + 0.3);
  }

  /* 鈸 */
  function cymbal(t, gain) {
    if (!ok()) return;
    const src = noiseSrc();
    const hp = SFX.ctx.createBiquadFilter();
    hp.type = 'highpass'; hp.frequency.value = 6200;
    const g = gainNode();
    g.gain.setValueAtTime(gain, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 1.7);
    src.connect(hp); hp.connect(g);
    src.start(t); src.stop(t + 1.8);
  }

  /* 小鼓 */
  function snare(t, gain) {
    if (!ok()) return;
    const src = noiseSrc();
    const bp = SFX.ctx.createBiquadFilter();
    bp.type = 'bandpass'; bp.frequency.value = 1900; bp.Q.value = 0.7;
    const g = gainNode();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(gain, t + 0.002);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.09);
    src.connect(bp); bp.connect(g);
    src.start(t); src.stop(t + 0.12);
  }

  /* 雪橇鈴 */
  function sleighHit(t, gain) {
    if (!ok()) return;
    const base = 2100 * (0.88 + Math.random() * 0.26);
    const mults = [1, 1.58, 2.31];
    for (let i = 0; i < mults.length; i++) {
      const o = SFX.ctx.createOscillator();
      const g = gainNode();
      o.type = 'sine';
      o.frequency.value = base * mults[i];
      const d = 0.05 + i * 0.012;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(
        Math.max(0.0002, gain * (i === 0 ? 1 : 0.4 / (i + 0.6))), t + 0.002);
      g.gain.exponentialRampToValueAtTime(0.0001, t + d);
      o.connect(g); o.start(t); o.stop(t + d + 0.03);
    }
  }

  /* ================= 背景音樂 ================= */

  const BPM = 112;
  const BEAT = 60 / BPM;
  const STEP = BEAT / 2;               // 八分音符
  const BGM_NORMAL = 0.22;
  const BGM_DUCK = 0.06;

  // C 大調：C - Am - F - G
  const CHORDS = [
    [261.63, 329.63, 392.00],   // C4 E4 G4
    [220.00, 261.63, 329.63],   // A3 C4 E4
    [174.61, 220.00, 261.63],   // F3 A3 C4
    [196.00, 246.94, 293.66]    // G3 B3 D4
  ];
  const BASS = [130.81, 110.00, 87.31, 98.00];   // C3 A2 F2 G2
  const MELODY = [
    523.25, 659.25, 783.99, 659.25, 523.25, 659.25, 783.99, 880,
    880, 783.99, 659.25, 523.25, 440, 523.25, 659.25, 783.99,
    698.46, 880, 1046.5, 880, 698.46, 880, 1046.5, 1174.66,
    1174.66, 1046.5, 987.77, 783.99, 587.33, 783.99, 987.77, 1174.66
  ];

  function bgmStep(step, t) {
    const bar = Math.floor(step / 8);
    const pos = step % 8;
    const chord = CHORDS[bar];

    // 雪橇鈴（每八分）
    sleighHit(t, pos % 2 === 0 ? 0.05 : 0.03);

    // 貝斯（第 1、3 拍）
    if (pos === 0 || pos === 4) {
      const o = SFX.ctx.createOscillator();
      const g = SFX.ctx.createGain();
      g.connect(SFX._bgm ? SFX._bgm.gain : SFX.master);
      o.type = 'triangle';
      o.frequency.value = BASS[bar];
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.16, t + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.42);
      o.connect(g); o.start(t); o.stop(t + 0.46);
    }

    // 和聲墊（每小節第 1 拍）
    if (pos === 0) {
      chord.forEach(f => {
        const o = SFX.ctx.createOscillator();
        const lp = SFX.ctx.createBiquadFilter();
        const g = SFX.ctx.createGain();
        g.connect(SFX._bgm ? SFX._bgm.gain : SFX.master);
        o.type = 'triangle';
        o.frequency.value = f;
        lp.type = 'lowpass'; lp.frequency.value = 1200;
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(0.035, t + 0.06);
        g.gain.exponentialRampToValueAtTime(0.0001, t + BEAT * 3.4);
        o.connect(lp); lp.connect(g); o.start(t); o.stop(t + BEAT * 3.5);
      });
    }

    // 旋律鐘聲
    const f = MELODY[step % MELODY.length];
    if (f) {
      const o = SFX.ctx.createOscillator();
      const o2 = SFX.ctx.createOscillator();
      const g = SFX.ctx.createGain();
      g.connect(SFX._bgm ? SFX._bgm.gain : SFX.master);
      o.type = 'sine'; o.frequency.value = f;
      o2.type = 'sine'; o2.frequency.value = f * 2.01;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.055, t + 0.008);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.42);
      o.connect(g); o2.connect(g);
      o.start(t); o.stop(t + 0.46); o2.start(t); o2.stop(t + 0.46);
    }
  }

  function bgmSchedule() {
    if (!SFX._bgm || !SFX.ctx) return;
    const horizon = t0() + 0.5;
    let guard = 0;
    while (SFX._bgm.next < horizon && guard < 64) {
      bgmStep(SFX._bgm.step, SFX._bgm.next);
      SFX._bgm.step = (SFX._bgm.step + 1) % 32;
      SFX._bgm.next += STEP;
      guard++;
    }
  }

  /* ---------- 音檔播放（背景音樂／拍手聲） ---------- */
  function mediaNode(src, loop, level) {
    const el = new Audio();
    el.src = src;
    el.loop = !!loop;
    el.preload = 'auto';
    el.volume = 1;
    const srcNode = SFX.ctx.createMediaElementSource(el);
    const g = SFX.ctx.createGain();
    g.gain.value = level == null ? 1 : level;
    srcNode.connect(g);
    g.connect(SFX.master);
    return { el, gain: g };
  }

  function startSynthBGM() {
    if (!ok() || SFX._bgm) return;
    const g = SFX.ctx.createGain();
    g.gain.setValueAtTime(0.0001, t0());
    g.gain.exponentialRampToValueAtTime(BGM_NORMAL, t0() + 1.2);
    g.connect(SFX.master);
    SFX._bgm = { gain: g, step: 0, next: t0() + 0.18, timer: null, ducked: false };
    bgmSchedule();
    SFX._bgm.timer = setInterval(bgmSchedule, 120);
  }

  function stopSynthBGM() {
    if (!SFX._bgm) return;
    const b = SFX._bgm;
    SFX._bgm = null;
    clearInterval(b.timer);
    try {
      b.gain.gain.cancelScheduledValues(t0());
      b.gain.gain.setValueAtTime(Math.max(0.0001, b.gain.gain.value), t0());
      b.gain.gain.exponentialRampToValueAtTime(0.0001, t0() + 0.6);
      setTimeout(() => { try { b.gain.disconnect(); } catch (e) {} }, 1200);
    } catch (e) { /* ignore */ }
  }

  SFX.startBGM = function () {
    if (!ok()) return;
    if (SFX._bgmMedia) {
      const p = SFX._bgmMedia.el.play();
      if (p && p.catch) p.catch(() => {});
      return;
    }
    if (SFX._bgmFailed) { startSynthBGM(); return; }
    const track = BGM_TRACKS[SFX.bgmTrack] || BGM_TRACKS.jingle;
    try {
      const m = mediaNode(track.file, true, 0.5);
      m.el.addEventListener('error', () => {
        SFX._bgmFailed = true;
        SFX._bgmMedia = null;
        startSynthBGM();
      });
      SFX._bgmMedia = m;
      const p = m.el.play();
      if (p && p.catch) p.catch(() => {});
    } catch (e) {
      SFX._bgmFailed = true;
      startSynthBGM();
    }
  };

  SFX.stopBGM = function () {
    if (SFX._bgmMedia) {
      try { SFX._bgmMedia.el.pause(); } catch (e) { /* ignore */ }
    }
    stopSynthBGM();
  };

  SFX.setMusic = function (on) {
    if (on) SFX.startBGM();
    else SFX.stopBGM();
  };

  SFX.duck = function (on) {
    const t = t0();
    if (SFX._bgmMedia) {
      const g = SFX._bgmMedia.gain.gain;
      g.cancelScheduledValues(t);
      g.setValueAtTime(Math.max(0.0001, g.value), t);
      g.setTargetAtTime(on ? 0.13 : 0.5, t, 0.18);
    }
    if (!SFX._bgm) return;
    if (SFX._bgm.ducked === !!on) return;
    SFX._bgm.ducked = !!on;
    const g2 = SFX._bgm.gain.gain;
    g2.cancelScheduledValues(t);
    g2.setValueAtTime(Math.max(0.0001, g2.value), t);
    g2.exponentialRampToValueAtTime(on ? BGM_DUCK : BGM_NORMAL, t + 0.35);
  };

  /* 拍手／歡呼聲（CC0 音檔） */
  SFX.playApplause = function () {
    if (!ok()) return;
    try {
      if (!SFX._applauseMedia) {
        SFX._applauseMedia = mediaNode('audio/applause.wav', false, 0.85);
      }
      const el = SFX._applauseMedia.el;
      el.currentTime = 0;
      const p = el.play();
      if (p && p.catch) p.catch(() => {});
    } catch (e) { /* ignore */ }
  };

  /* ================= 抽獎音效 ================= */

  SFX.tick = function (gain) {
    if (!ok()) return;
    sleighHit(t0(), Math.min(0.09, (gain || 0.045) * 1.15));
  };

  SFX.whoosh = function (dur) {
    if (!ok()) return;
    const d = dur || 0.8;
    const t = t0();
    const src = noiseSrc();
    const lp = SFX.ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.setValueAtTime(260, t);
    lp.frequency.exponentialRampToValueAtTime(1500, t + d * 0.65);
    lp.frequency.exponentialRampToValueAtTime(420, t + d);
    const g = gainNode();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.18, t + d * 0.5);
    g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    src.connect(lp); lp.connect(g);
    src.start(t); src.stop(t + d + 0.1);
  };

  SFX.heartbeat = function (strength) {
    if (!ok()) return;
    const s = strength == null ? 1 : strength;
    const beat = (delay, gain) => {
      const t = t0() + delay;
      const o = SFX.ctx.createOscillator();
      const g = gainNode();
      o.type = 'sine';
      o.frequency.setValueAtTime(62, t);
      o.frequency.exponentialRampToValueAtTime(38, t + 0.16);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.32 * s * gain, t + 0.005);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.2);
      o.connect(g); o.start(t); o.stop(t + 0.24);
    };
    beat(0, 1);
    beat(0.22, 0.6);
  };

  /* ================= 曲目與風格 ================= */

  const BGM_TRACKS = {
    jingle: { file: 'audio/jingle-bells.mp3', name: 'Jingle Bells（輕快派對）' },
    wish: { file: 'audio/wewishyou.mp3', name: 'We Wish You（大樂團）' },
    tree: { file: 'audio/oh-christmas-tree.mp3', name: 'Oh Christmas Tree（熱鬧）' },
    carol: { file: 'audio/carol-of-the-bells.mp3', name: 'Carol of the Bells（戲劇張力）' },
    wish2: { file: 'audio/wewishyouamerryxmas.mp3', name: 'We Wish You（輕音樂）' }
  };

  SFX.bgmTrack = 'jingle';
  SFX.drawStyle = 'orchestra';
  SFX.BGM_TRACKS = BGM_TRACKS;

  SFX.setBGMTrack = function (key) {
    if (!BGM_TRACKS[key] || SFX.bgmTrack === key) return;
    SFX.bgmTrack = key;
    const wasPlaying = !!(SFX._bgmMedia && !SFX._bgmMedia.el.paused);
    if (SFX._bgmMedia) {
      try { SFX._bgmMedia.el.pause(); } catch (e) { /* ignore */ }
      try { SFX._bgmMedia.gain.disconnect(); } catch (e) { /* ignore */ }
      SFX._bgmMedia = null;
    }
    SFX._bgmFailed = false;
    if (wasPlaying) SFX.startBGM();
  };

  SFX.setDrawStyle = function (style) {
    if (style === 'orchestra' || style === 'bells' || style === 'party') {
      SFX.drawStyle = style;
    }
  };

  /* 蓄勢：弦樂上滑 + 豎琴 + 小鼓漸強 */
  SFX.riser = function (dur) {
    if (!ok()) return;
    const d = dur || 2.5;
    const t = t0();
    const style = SFX.drawStyle;

    // 弦樂上滑（鐘聲風格省略）
    if (style !== 'bells') {
      const o = SFX.ctx.createOscillator();
      const lp = SFX.ctx.createBiquadFilter();
      const g = gainNode();
      o.type = 'sawtooth';
      o.frequency.setValueAtTime(82, t);
      o.frequency.exponentialRampToValueAtTime(330, t + d);
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(500, t);
      lp.frequency.exponentialRampToValueAtTime(3200, t + d);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(style === 'party' ? 0.09 : 0.07, t + d * 0.9);
      g.gain.exponentialRampToValueAtTime(0.0001, t + d + 0.12);
      o.connect(lp); lp.connect(g); o.start(t); o.stop(t + d + 0.2);
    }

    // 豎琴滑音
    const notes = [523.25, 587.33, 659.25, 783.99, 880, 1046.5, 1174.66, 1318.5, 1567.98, 2093];
    notes.forEach((f, i) => bell(f, 0.5, style === 'bells' ? 0.06 : 0.045, (i * d) / notes.length));

    // 小鼓漸強（鐘聲風格改成無鼓）
    if (style !== 'bells') {
      const hits = Math.floor(d * (style === 'party' ? 14 : 10));
      for (let i = 0; i < hits; i++) {
        snare(t + (i * d) / hits, 0.012 + 0.03 * (i / hits));
      }
    }
  };

  /* 翻牌滾奏：依風格調整鼓與鈴的比例 */
  SFX.drumroll = function (dur) {
    if (!ok()) return { stop() {} };
    const d = dur || 4;
    const start = t0() + 0.02;
    const style = SFX.drawStyle;
    let time = 0.02;
    while (time < d) {
      const p = time / d;
      sleighHit(start + time, (style === 'bells' ? 0.045 : 0.03) + 0.075 * p);
      if (style === 'orchestra' && p > 0.45) snare(start + time, 0.015 + 0.045 * p);
      if (style === 'party' && p > 0.25) snare(start + time, 0.02 + 0.05 * p);
      time += 0.08 - 0.05 * p;
    }
    if (style !== 'bells') {
      for (let i = 0; i < 5; i++) {
        timpani(start + d * 0.5 + (d * 0.42) * (i / 5),
          0.05 + 0.035 * i, style === 'party' ? 74 : 68);
      }
    }
    return { stop() {} };
  };

  SFX.startDrone = function () {
    if (!ok() || SFX._drone) return;
    const t = t0();
    const osc = SFX.ctx.createOscillator();
    const osc2 = SFX.ctx.createOscillator();
    const g = gainNode();
    const lp = SFX.ctx.createBiquadFilter();
    osc.type = 'sine'; osc.frequency.value = 55;
    osc2.type = 'triangle'; osc2.frequency.value = 82.5;
    lp.type = 'lowpass'; lp.frequency.value = 380;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.08, t + 1.4);
    osc.connect(lp); osc2.connect(lp); lp.connect(g);
    osc.start(t); osc2.start(t);
    SFX._drone = { osc, osc2, g };
  };

  SFX.stopDrone = function () {
    if (!SFX._drone || !SFX.ctx) return;
    const d = SFX._drone;
    const t = t0();
    try {
      d.g.gain.cancelScheduledValues(t);
      d.g.gain.setValueAtTime(d.g.gain.value || 0.0001, t);
      d.g.gain.exponentialRampToValueAtTime(0.0001, t + 0.4);
      d.osc.stop(t + 0.45); d.osc2.stop(t + 0.45);
    } catch (e) { /* ignore */ }
    SFX._drone = null;
  };

  /* 衝擊：定音鼓 + 大鐘 + 鈸 */
  SFX.impact = function (power) {
    if (!ok()) return;
    const p = power || 1;
    const t = t0();
    timpani(t, 0.38 * p, 72);
    bell(98, 2.2, 0.26 * p, 0);
    cymbal(t, 0.1 * p);
  };

  /* 中獎音樂：三種風格（交響／鐘聲／派對） */
  function fanfareOrchestra(tier) {
    const t = t0();
    const seq = tier === 1 ? [392, 523.25, 659.25, 783.99]
      : tier === 2 ? [392, 523.25, 659.25]
        : tier === 3 ? [392, 523.25]
          : [523.25, 659.25];

    seq.forEach((f, i) => {
      brass(f, t + i * 0.11, 0.46, 0.085);
      bell(f * 2, 0.55, 0.045, i * 0.11);
    });

    const chordAt = t + seq.length * 0.11 + 0.03;
    [261.63, 329.63, 392.00, 523.25].forEach(f => brass(f, chordAt, 1.5, 0.05));
    bell(1046.5, 1.9, 0.12, chordAt);
    bell(1567.98, 1.5, 0.06, chordAt + 0.02);
    timpani(chordAt, 0.26, 78);
    cymbal(chordAt, 0.12);

    if (tier <= 2) {
      setTimeout(() => {
        if (!ok()) return;
        [523.25, 659.25, 783.99].forEach(f => brass(f, t0() + 0.1, 1.0, 0.035));
      }, 900);
    }
  }

  function fanfareBells(tier) {
    const t = t0();
    const run = tier >= 2
      ? [523.25, 587.33, 659.25, 783.99, 880, 1046.5]
      : [523.25, 659.25, 783.99, 1046.5];
    run.forEach((f, i) => bell(f, 0.8, 0.085, i * 0.07));
    const at = run.length * 0.07 + 0.05;
    bell(130.81, 2.4, 0.07, at);
    [523.25, 659.25, 783.99, 1046.5].forEach(f => bell(f, 2.6, 0.06, at));
    bell(1567.98, 2.0, 0.045, at + 0.02);
    bell(2093, 1.4, 0.03, at + 0.06);
    if (tier <= 2) cymbal(t + at, 0.07);
  }

  function fanfareParty(tier) {
    const t = t0();
    for (let i = 0; i < 7; i++) snare(t + i * 0.045, 0.04 + i * 0.01);

    [130.81, 174.61, 196.00, 261.63].forEach((f, i) => {
      const at = t + 0.1 + i * 0.14;
      const o = SFX.ctx.createOscillator();
      const g = gainNode();
      o.type = 'triangle';
      o.frequency.value = f;
      g.gain.setValueAtTime(0.0001, at);
      g.gain.exponentialRampToValueAtTime(0.13, at + 0.012);
      g.gain.exponentialRampToValueAtTime(0.0001, at + 0.18);
      o.connect(g); o.start(at); o.stop(at + 0.22);
      sleighHit(at, 0.05);
    });

    const stabs = tier >= 2 ? [523.25, 659.25, 783.99] : [523.25, 783.99];
    stabs.forEach((f, i) => brass(f, t + 0.12 + i * 0.14, 0.2, 0.07));

    const at = t + 0.66;
    [261.63, 329.63, 392.00, 523.25].forEach(f => brass(f, at, 1.3, 0.055));
    bell(1046.5, 1.6, 0.1, at);
    timpani(at, 0.22, 82);
    cymbal(at, 0.12);
  }

  SFX.fanfare = function (tier) {
    if (!ok()) return;
    if (SFX.drawStyle === 'bells') return fanfareBells(tier);
    if (SFX.drawStyle === 'party') return fanfareParty(tier);
    return fanfareOrchestra(tier);
  };

  SFX.shimmer = function () {
    if (!ok()) return;
    for (let i = 0; i < 7; i++) {
      bell(1600 + Math.random() * 2600, 0.5, 0.026, i * 0.055);
    }
  };

  /* 假動作：三音動機 dun–dun–DUN */
  SFX.tease = function () {
    if (!ok()) return;
    const t = t0();
    brass(196, t, 0.18, 0.09);
    brass(196, t + 0.18, 0.18, 0.09);
    brass(246.94, t + 0.36, 0.4, 0.11);
    timpani(t + 0.36, 0.12, 70);
    SFX.heartbeat(1.15);
  };

  global.SFX = SFX;
})(window);
