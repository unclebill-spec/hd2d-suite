// game/vanaheim_fun.js (fun pass, 2026-10-29). Juice for Vanaheim Stage B: sound stingers from the existing
// audio.sfx kinds, existing effects only (skipped quietly if the area's atlas lacks one), a tiny CSS screen
// shake on the canvas that is OFF under the reduced-motion toggle / OS setting, and rare funny lines.
// No rules, numbers, controls or saves change.
export function sfx(G, kind) { try { G.audio && G.audio.sfx(kind); } catch (_) {} }
export function fx(ctx, names, x, y, z) {
  const E = ctx && ctx.effects; if (!E || !E.meta) return null;
  for (const n of [].concat(names)) if (E.meta.effects[n]) return E.spawn(n, x, y, z);
  return null;
}
// shake / flash obey the Settings toggles (G.shakeOK / G.flashOK, which fold in reduced motion)
function fxOK(G, k) { return G[k] ? G[k]() : !(G.reducedMotion && G.reducedMotion()); }
let shakeT = 0;
export function shake(G, amp = 3, ms = 220) {
  if (!fxOK(G, 'shakeOK')) return;
  const v = document.getElementById('view'); if (!v || typeof requestAnimationFrame !== 'function') return;
  const id = ++shakeT, t0 = performance.now();
  const step = (now) => {
    if (id !== shakeT) return;
    const k = 1 - (now - t0) / ms;
    if (k <= 0) { v.style.translate = ''; return; }
    v.style.translate = `${((Math.random() * 2 - 1) * amp * k).toFixed(1)}px ${((Math.random() * 2 - 1) * amp * k).toFixed(1)}px`;
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
export function flash(G, a, t = 0.18) { if (a && fxOK(G, 'flashOK')) a.flashT = Math.max(a.flashT || 0, t); }
export function rare(p = 0.08) { return Math.random() < p; }

// ---------------------------------------------------------------- GD fun-pass picks (Oct 29, 2026)
// #2 Nettlecrown phase 3: thorns visibly close in on the arena. Will hasn't decided: OFF by default.
// FLIP HERE (true = on). QA override without editing: ?thorns=1 (or ?vhq=thorns). Visual only: existing spell
// effects on a ring that creeps inward; no arena shrink, no collision, hitbox or damage change.
export const THORNS_CLOSE_IN = true;
export function thornsOn(qs) { return THORNS_CLOSE_IN || (qs && (qs.get('thorns') === '1' || qs.get('vhq') === 'thorns')); }
export const THORN_RING = { from: 7.5, to: 5.0, secs: 6, every: 0.45, n: 10, fx: ['leaf_gust', 'earth_burst'] };
export function thornRing(st, ctx, c, dt) {   // st: per-fight state { t, next }; c: arena centre [x, z]
  const E = ctx && ctx.effects; if (!E || !E.meta) return;
  st.t += dt; if ((st.next -= dt) > 0) return; st.next = THORN_RING.every;
  const R = THORN_RING, k = Math.min(1, st.t / R.secs), r = R.from + (R.to - R.from) * k, spin = st.t * 0.4;
  for (let i = 0; i < R.n; i++) {
    const a = spin + (i / R.n) * Math.PI * 2, x = c[0] + Math.cos(a) * r, z = c[1] + Math.sin(a) * r * 0.8;
    fx(ctx, R.fx[i % 2 ? 1 : 0], x, 0.05, z);
  }
}
// #3 Mossbrook coin-in-the-spring: toss 1 Copper bit (else 1 gold) into the fizzing spring. 1 in 8: a rare line
// (can repeat). The first rare line (or the 8th toss, whichever first) also gives the Spring-Wish Penny, once per save.
export const COIN = { cost: 1, rareP: 0.125, pity: 8 };
const COIN_LINES = ['(Plink. The spring fizzes politely.)', '(Plink. A bubble pops: you feel slightly luckier. You are not.)', '(Plink. The coin sinks, glinting green.)'];
const COIN_RARE = ['(The spring burps your coin back up, then thinks better of it and swallows it again. "Thank you," it fizzes.)',
  '(A tiny voice from the bubbles: "Wish received. Processing. Please hold.")'];
export function tossCoin(G, ctx, pos) {
  const S = G.S, f = (S.flags = S.flags || {}), inv = S.inv || (S.inv = {});
  if ((inv.coin || 0) >= COIN.cost) G.take('coin', COIN.cost);
  else if ((S.gold || 0) >= COIN.cost) S.gold -= COIN.cost;
  else { G.toast && G.toast('(Your pockets are empty. The spring fizzes, unbothered.)', 1.8); return 'broke'; }
  f.vh_wish_tosses = (f.vh_wish_tosses || 0) + 1;
  const qa = typeof location !== 'undefined' && new URLSearchParams(location.search).get('vhq') === 'coin' && f.vh_wish_tosses === 1;
  const hit = qa || Math.random() < COIN.rareP;
  sfx(G, hit ? 'quest' : 'blip'); fx(ctx, hit ? ['sparkle_burst', 'glitter'] : ['spring_bubbles', 'glitter'], pos[0], 0.3, pos[1]);
  if (hit) { f.vh_wish_rare = (f.vh_wish_rare || 0) + 1; G.toast && G.toast(COIN_RARE[(f.vh_wish_rare - 1) % COIN_RARE.length], 3.0); }
  else G.toast && G.toast(COIN_LINES[Math.floor(Math.random() * COIN_LINES.length)], 1.8);
  if (!f.vh_wish_penny && (hit || f.vh_wish_tosses >= COIN.pity)) {
    f.vh_wish_penny = 1; G.give('wish_penny', 1);
    setTimeout(() => G.toast && G.toast('Something warm bobs up: the Spring-Wish Penny. (A keepsake.)', 2.6), 1200);
  }
  G.drawBag && G.drawBag(); G.save && G.save();
  return hit ? 'rare' : 'plink';
}
// #4 Bonus seed at Nettlecrown's seed stall: 10 % per common-seed purchase, at most 1 bonus per in-game day
// (S.flags.vh_bonus_day = the S.day it was given; saved in the slot; old saves without it are simply eligible).
export const BONUS_SEED = { p: 0.10, perDay: 1, common: ['glowseed'] };
export function bonusSeed(G, id) {
  const S = G.S, f = (S.flags = S.flags || {}), day = S.day || 0;
  if (!BONUS_SEED.common.includes(id) || f.vh_bonus_day === day) return false;
  const force = typeof location !== 'undefined' && new URLSearchParams(location.search).get('vhq') === 'seed';
  if (!force && Math.random() >= BONUS_SEED.p) return false;
  f.vh_bonus_day = day; S.inv[id] = (S.inv[id] || 0) + 1;
  sfx(G, 'pickup'); G.toast && G.toast('(Nettlecrown slips an extra seed in the bag. "Shh. It\'s a bonus.")', 2.4);
  G.save && G.save();
  return true;
}
