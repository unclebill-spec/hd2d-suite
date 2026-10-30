// Title attract demo (WILL-SPEC sec 19, pattern: templates/game-shell/src/shell/attract.ts). After ATTRACT_IDLE_SEC idle on the title,
// loop randomly picked live realms and boss fights with real combat driven by a small AI (walk to the nearest foe, swing, cast).
// Sandboxed: every localStorage / sessionStorage write is dropped while it runs, the save state (G.S) and the combat "defeated" map
// are snapshotted and put back, and save() is a no-op (G.attract). Any key, click, tap or pad button ends it at once.
export const ATTRACT_IDLE_SEC = 40, ATTRACT_SCENE_SEC = 24;
// live realms with their own SPAWNS (heroes.js) + the boss fight (Elder Golem in Mossglen). Locked / unfinished realms are not listed.
export const ATTRACT_SCENES = [
  { area: 'hollows', label: 'Toadstool Hollows' }, { area: 'rotwood', label: 'the Rotwood' },
  { area: 'vanaheim', label: 'Vanaheim' }, { area: 'verdant', label: 'the Verdant' },
  { area: 'mossglen', label: 'Mossglen: the Elder Golem', boss: 'eldergolem' }];

export function makeAttract(G, host) {
  const A = { active: false, idle: 0, t: 0, scene: null, last: 0, order: [], i: 0, stats: { swings: 0, casts: 0, scenes: 0, dropped: 0 } };
  const SP = Storage.prototype, real = { setItem: SP.setItem, removeItem: SP.removeItem, clear: SP.clear };
  const lock = (on) => {
    if (on) { SP.setItem = function () { A.stats.dropped++; }; SP.removeItem = function () { A.stats.dropped++; }; SP.clear = function () { A.stats.dropped++; }; }
    else Object.assign(SP, real);
  };
  let snap = null, badge = null, busy = false, act = { walk: 0, swing: 0, cast: 0 }, padPrev = 0;
  const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const live = () => ATTRACT_SCENES.filter((s) => (host.spawns()[s.area] || []).length);

  async function play(sc) {
    busy = true; A.scene = sc; A.t = 0; A.stats.scenes++;
    G.combat.defeated = {}; G.S.hp = null;
    try { await host.loadArea(sc.area, 'start'); } catch (e) { console.warn('attract: skip', sc.area, e && e.message); }
    busy = false;
    if (!A.active) return;
    if (badge) badge.querySelector('b').textContent = sc.label;
  }
  function next() { if (A.i >= A.order.length) { A.order = shuffle(live().slice()); A.i = 0; } const sc = A.order[A.i++]; if (sc) play(sc); }

  async function begin() {
    if (A.active) return;
    A.active = true; A.idle = 0; A.stats = { swings: 0, casts: 0, scenes: 0, dropped: 0 };
    snap = { S: JSON.stringify(G.S), defeated: JSON.stringify(G.combat.defeated || {}), area: G.area };
    lock(true); G.attract = true; G.title = false;
    G.S.cls = G.preview || G.S.cls || 'wildcaller'; G.S.autoLevel = true;
    G.introNext = false; G.S.flags = G.S.flags || {}; G.S.flags.intro = G.S.flags.intro || 'skipped';   // demo copy only: no story intro
    host.hideTitle();
    badge = document.createElement('div'); badge.id = 'attractBadge';
    badge.innerHTML = '<span>DEMO</span> <b></b><em>press any key</em>';
    badge.style.cssText = 'position:fixed;left:50%;top:12px;transform:translateX(-50%);z-index:60;padding:6px 14px;border:2px solid #f0d9a0;background:rgba(26,29,58,.82);color:#f0d9a0;font:600 13px/1.3 monospace;letter-spacing:.06em;pointer-events:none;display:flex;gap:10px';
    document.body.appendChild(badge);
    A.order = []; A.i = 0; next();
  }
  async function end() {
    if (!A.active) return;
    A.active = false; A.idle = 0; A.scene = null;
    if (badge) { badge.remove(); badge = null; }
    host.showTitle();   // the title card is back on screen at once; the world swaps behind it
    const s = JSON.parse(snap.S); for (const k of Object.keys(G.S)) delete G.S[k]; Object.assign(G.S, s);
    G.combat.defeated = JSON.parse(snap.defeated);
    G.title = true; G.attract = false;
    const area = snap.area || 'plaza'; snap = null;
    while (busy) await new Promise((r) => setTimeout(r, 30));
    try { await host.loadArea(area, 'start'); } finally { lock(false); }
  }

  // the AI pilot: walk at the nearest foe (the party / pets follow the player), face it, swing, cast whatever spell is equipped
  function pilot(dt) {
    if (G.dlg && G.dropDialogue) G.dropDialogue();   // no story dialogs / area intros in the demo
    if (G.downed) G.downed = false;
    const ctx = G.ctx; if (!ctx || busy || !ctx.player) return;
    const p = ctx.player, max = G.combat.maxHp(); if (G.S.hp != null && G.S.hp < max * 0.5) G.S.hp = max;   // the demo hero never goes down
    let foes = G.combat.alive();
    if (A.scene && A.scene.boss) { const b = foes.filter((e) => e.a.role === A.scene.boss); if (b.length && foes.length > 3) foes = b.concat(foes.filter((e) => e.a.role !== A.scene.boss).slice(0, 2)); }
    let tgt = null, bd = 1e9; for (const e of foes) { const d = Math.hypot(e.a.x - p.x, e.a.z - p.z); if (d < bd) { bd = d; tgt = e; } }
    act.walk -= dt; act.swing -= dt; act.cast -= dt;
    if (!tgt) { if (A.t > 4) A.t = Math.max(A.t, ATTRACT_SCENE_SEC - 2); return; }
    const dx = tgt.a.x - p.x, dz = tgt.a.z - p.z, reach = 1.2 + (tgt.D.r || 0.4);
    if (bd > reach) { if (act.walk <= 0 || !ctx.walking()) { ctx.walkTo(tgt.a.x - dx / bd * reach * 0.7, tgt.a.z - dz / bd * reach * 0.7); act.walk = 0.6; } }
    else {
      if (ctx.walking()) ctx.stopWalk();
      p.facing = Math.abs(dx) > Math.abs(dz) ? (dx > 0 ? 'right' : 'left') : (dz > 0 ? 'down' : 'up');
      if (act.swing <= 0) { ctx.act('attack'); A.stats.swings++; act.swing = 0.55 + Math.random() * 0.25; }
    }
    if (act.cast <= 0 && bd < 7) { try { if (ctx.playerCast && ctx.playerCast() !== false) A.stats.casts++; } catch (e) { /* no spell here */ } act.cast = 2.2 + Math.random() * 1.2; if (Math.random() < 0.35 && ctx.cycleSpell) ctx.cycleSpell(1); }
  }

  let prevT = performance.now();
  function frame(now) {
    const dt = Math.min(0.1, (now - prevT) / 1000); prevT = now;
    if (!A.active) {
      // gamepad: any button counts as input on the title
      const pads = navigator.getGamepads ? [...navigator.getGamepads()].filter(Boolean) : [];
      const any = pads.some((g) => g.buttons.some((b) => b.pressed)); if (any) A.idle = 0;
      if (host.eligible()) { A.idle += dt; if (A.idle >= (G.attractIdle || ATTRACT_IDLE_SEC)) begin(); } else A.idle = 0;
    } else {
      const pads = navigator.getGamepads ? [...navigator.getGamepads()].filter(Boolean) : [];
      const n = pads.reduce((c, g) => c + g.buttons.filter((b) => b.pressed).length, 0);
      if (n > padPrev) { padPrev = n; end(); } else padPrev = n;
      if (A.active) { A.t += dt; pilot(dt); if (!busy && A.t >= (G.attractScene || ATTRACT_SCENE_SEC)) next(); }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  const poke = (e) => {
    A.idle = 0;
    if (!A.active || !e.isTrusted && !G.attractTestPoke) return;
    e.preventDefault(); e.stopImmediatePropagation(); end();
  };
  for (const ev of ['keydown', 'pointerdown', 'mousedown', 'touchstart', 'wheel']) addEventListener(ev, poke, { capture: true, passive: false });
  addEventListener('mousemove', () => { if (!A.active) A.idle = 0; }, { capture: true });
  A.begin = begin; A.end = end;
  A.state = () => ({ active: A.active, idle: +A.idle.toFixed(1), t: +A.t.toFixed(1), scene: A.scene && A.scene.area, busy, ...A.stats });
  return A;
}
