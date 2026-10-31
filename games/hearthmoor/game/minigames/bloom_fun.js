// game/minigames/bloom_fun.js: FUN PASS for the Bloomtide minigames (juice only: popups, sparks, combo, count-in,
// metronome, cap pop, result flair). No rule, number, control or palette changes; every colour comes from PAL.
// Reduced motion (st.rm): no shake, no flying sparks, popups stay still.
import { HOOKS, PAL, W, cell, ANIM } from './bloomtide.js';

const LABEL = { perfect: ['Perfect!', PAL.cyan_hi], good: ['Good', PAL.lime], miss: ['Miss', PAL.vio_hi] };
const sfx = (st, k) => { try { st.G.audio && st.G.audio.sfx && st.G.audio.sfx(k); } catch (_) {} };
const pluck = (st, s, v) => { try { st.G.audio && st.G.audio.pluck && st.G.audio.pluck(s, v, 0); } catch (_) {} };

HOOKS.push({
  start(st) { st.fun = { combo: 0, best: 0, pops: [], sparks: [], basket: 0, shake: 0, beat: -1, lastNow: st.now() }; },
  judge(st, r) {
    const f = st.fun; if (!f) return;
    if (r.grade === 'stray') return;   // stray taps: no penalty, no noise
    const [x, y] = st.fx.target || [W / 2, 80];
    if (r.grade === 'miss') { f.combo = 0; sfx(st, 'blip'); }
    else {
      f.combo++; f.best = Math.max(f.best, f.combo);
      sfx(st, r.grade === 'perfect' ? 'pickup' : 'lampchime');
      if (st.kind === 'dance') pluck(st, r.grade === 'perfect' ? 12 : 7, 0.12);
      if (st.kind === 'harvest') { f.basket++; f.caughtAt = st.t; }
      if (r.grade === 'perfect' && !st.rm) f.shake = 3;
      const n = st.rm ? 0 : r.grade === 'perfect' ? 4 : 5;   // perfect: bt_glow_fx ring does most of the work
      for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2; f.sparks.push({ x, y, vx: Math.cos(a) * 0.9, vy: Math.sin(a) * 0.9 - 0.4, life: 18, c: i % 2 ? PAL.cyan : PAL.mag_hi }); }
    }
    const [txt, c] = LABEL[r.grade]; f.pops.push({ txt, c, x, y: y - 22, life: 34 });
  },
  draw(g, st) {
    const f = st.fun; if (!f) return;
    if (f.shake > 0) { st.cv.style.transform = `translate(${(f.shake % 2 ? 1 : -1) * f.shake}px,0)`; f.shake--; if (!f.shake) st.cv.style.transform = ''; }
    // count-in 3-2-1 + dance metronome (beats from the chart's tempo; sound only, no judging)
    const t = st.t;
    if (t < 0 || (st.times[0] - t > 0 && st.times[0] - t < 1800)) {
      const left = t < 0 ? 3 : Math.max(1, Math.ceil((st.times[0] - t) / 600));
      if (left <= 3) { g.font = '16px "Pixelify Sans",monospace'; g.textAlign = 'center'; g.fillStyle = PAL.frost_hi; g.fillText(t < 0 ? 'Ready' : String(left), W / 2, 30); }
    }
    if (st.kind === 'dance' && t >= 0 && !st.done) {
      const beatMs = 60000 / (st.g.bpm || 96), b = Math.floor(t / beatMs);
      if (b !== f.beat) { f.beat = b; pluck(st, b % 4 ? 0 : 5, 0.05); }
      const ph = (t % beatMs) / beatMs; if (ph < 0.15) { g.fillStyle = PAL.vio; g.fillRect(0, 0, W, 2); g.fillRect(0, 142, W, 2); }
    }
    // the violet wicker basket (Hearthmoor Art): catch squash on each pick, full once 3+ caps are in
    if (st.kind === 'harvest') { const c = f.caughtAt != null && st.t - f.caughtAt < ANIM.catch; cell(g, 'basket', 0, (f.basket >= 3 ? 2 : 0) + (c ? 1 : 0), 24, 116, 1); }
    for (const s of f.sparks) { g.fillStyle = s.c; g.fillRect(Math.round(s.x), Math.round(s.y), 1, 1); s.x += s.vx; s.y += s.vy; s.vy += 0.04; s.life--; }
    f.sparks = f.sparks.filter((s) => s.life > 0);
    g.textAlign = 'center'; g.font = '12px "Pixelify Sans",monospace';
    for (const p of f.pops) { g.globalAlpha = Math.min(1, p.life / 12); g.fillStyle = PAL.ink; g.fillText(p.txt, p.x + 1, p.y + 1); g.fillStyle = p.c; g.fillText(p.txt, p.x, p.y); g.globalAlpha = 1; p.life--; if (!st.rm) p.y -= 0.35; }
    f.pops = f.pops.filter((p) => p.life > 0);
    if (f.combo >= 2) { g.textAlign = 'right'; g.font = '11px "Pixelify Sans",monospace'; g.fillStyle = PAL.mag_hi; g.fillText(`Combo x${f.combo}`, W - 4, 12); }
    g.textAlign = 'left';
  },
  result(st, r) {
    const f = st.fun || {}; sfx(st, r.won ? 'quest' : 'blip');
    setTimeout(() => { const p = st.res && st.res.querySelector('p'); if (p && f.best >= 2) p.insertAdjacentHTML('afterend', `<p style="color:${PAL.mag_hi}">Best combo x${f.best}</p>`); }, 0);
  },
  stop(st) { if (st.cv) st.cv.style.transform = ''; },
});
