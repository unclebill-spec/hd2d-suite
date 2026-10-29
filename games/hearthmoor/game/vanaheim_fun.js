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
