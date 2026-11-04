// Bifrost Crossing ambient barks (Hearthmoor Story, 2026-10-26). One pool, one bubble.
// A line shows over a nearby NPC or plaza spot: one at a time, ~3 s, then a quiet 8–14 s.
// Not during dialogue, menus, combat, or pause. Colours are the existing parchment bubble.

export const NEAR = 3.5;
export const SHOW = 3;
export const GAP_MIN = 8;
export const GAP_MAX = 14;

export const BARKS = {
  bifrost: {
    any: [
      "Nine gates, nine colours. My eyes have never been so busy.",
      "Gatewright Halvard says 'coming soon' like it's a blessing.",
      "Vanaheim's gate is the only one open. Smells like moss and rain.",
      "Mind the frozen gate. Niflheim's seal bites back when you lean on it.",
      "Gatekeepers' Guild polishes the arches daily. Tidy lot.",
      "I came for the view, stayed because I lost my way. Again.",
      "Muspelheim's seal is warm. People toast bread on it. Don't.",
      "Asgard's gate hums like a hall fire. Rather smug, I find.",
      "Helheim's gate breathes on the glass. Polite, but chilly.",
      "Earn your merit, get your key. The Guild has a pamphlet."
    ],
    temple_lit: [
      "Old Temple's relit! The Midgard gate is open and singing.",
      "No more Corsair skiffs to get home. My stomach thanks the Temple.",
      "Rainbow light on the plaza stones again. Hearthmoor's next door now."
    ]
  }
};

// State pool when the Old Temple is lit, otherwise `any`. While lit, one pick in three stays on `any`.
export function pickLine(flags, rng, avoid) {
  const lit = !!(flags && flags.temple_lit);
  const useState = lit && rng() >= 1 / 3;
  const pool = useState ? BARKS.bifrost.temple_lit : BARKS.bifrost.any;
  let i = Math.floor(rng() * pool.length) % pool.length;
  if (pool.length > 1 && pool[i] === avoid) i = (i + 1) % pool.length;
  return pool[i];
}

export function rollGap(rng) {
  return GAP_MIN + rng() * (GAP_MAX - GAP_MIN);
}

export function freshSim(rng = Math.random) {
  return { wait: rollGap(rng), left: 0, line: null, spot: null, last: null, pin: false };
}

// sim.wait is the quiet gap. sim.left is the one visible bark.
// world: { blocked, spots: [{id, d}], flags, rng, near, show }. A pinned bark ignores range (QA force).
export function tick(sim, dt, world) {
  const rng = world.rng || Math.random;
  const near = world.near ?? NEAR;
  const show = world.show ?? SHOW;
  if (world.blocked) {
    if (sim.left > 0) { sim.left = 0; sim.line = null; sim.spot = null; sim.pin = false; }
    return sim;
  }
  if (sim.left > 0) {
    const spots = world.spots || [];
    const here = sim.pin || spots.some((s) => s.id === sim.spot && s.d <= near);
    sim.left -= dt;
    if (!here || sim.left <= 0) { sim.left = 0; sim.line = null; sim.spot = null; sim.pin = false; }
    return sim;
  }
  sim.wait -= dt;
  if (sim.wait > 0) return sim;
  const spots = (world.spots || []).filter((s) => s.d <= near);
  if (!spots.length) { sim.wait = 0; return sim; }
  const spot = spots[Math.floor(rng() * spots.length) % spots.length];
  sim.line = pickLine(world.flags, rng, sim.last);
  sim.last = sim.line;
  sim.spot = spot.id;
  sim.left = show;
  sim.pin = false;
  sim.wait = Math.max(0.05, rollGap(rng) - show);
  return sim;
}

const AMBIENT = [
  { id: 'arch', x: 2.2, z: -8.2, label: 'A traveller' },
  { id: 'skiff', x: 2.4, z: 10.5, label: 'A traveller' },
  { id: 'west', x: -7.2, z: -3.8, label: 'A traveller' },
  { id: 'east', x: 8.2, z: -2.4, label: 'A traveller' },
];
const TITLES = /^(gatewright|warden|keeper|elder|captain|lady|mother)$/i;

function shortName(a) {
  const raw = String(a.name || '').split(',')[0].trim();
  const bits = raw.split(/\s+/).filter(Boolean);
  if (bits.length >= 2 && TITLES.test(bits[0])) return bits[1];
  if (bits.length) return bits[0];
  return a.role || 'Someone';
}

export class Barks {
  constructor(G) {
    this.G = G;
    this.rng = Math.random;
    this.sim = freshSim(this.rng);
    this.here = false;
    this.el = null;
  }
  blocked() {
    const G = this.G;
    let wheel = false;
    try { wheel = !!(G.wheel && G.wheel.state && G.wheel.state().open); } catch (e) { wheel = false; }
    const foes = G.combat && G.combat.enemies;
    const fight = !!(foes && foes.some((e) => e.state === 'chase' || e.state === 'attack'));
    const intro = !!(G.intro && G.intro.blocking && G.intro.blocking());
    return !!(G.dlg || G.log || G.opts || G.pause || G.heroUI || G.shop || G.picking || G.title || G.asking || G.busy || G.downed || wheel || fight || intro);
  }
  spots(ctx) {
    const p = ctx.player, out = [];
    for (const a of ctx.npcs || []) {
      if (!a || a.ai || a.noTalk || a.kind === 'enemy' || a.behavior === 'follow') continue;
      if (!(a.talkable || a.say)) continue;
      if (a.quad && a.quad.visible === false) continue;
      out.push({ id: a.id, x: a.x, z: a.z, y: a.y || 0, lift: (a.lift || 0) + 2.15, label: shortName(a), d: Math.hypot(a.x - p.x, a.z - p.z) });
    }
    for (const s of AMBIENT) {
      const y = ctx.heightAt ? (ctx.heightAt(s.x, s.z) || 0) : 0;
      out.push({ id: s.id, x: s.x, z: s.z, y, lift: 1.85, label: s.label, d: Math.hypot(s.x - p.x, s.z - p.z) });
    }
    return out;
  }
  ensure() {
    if (this.el || typeof document === 'undefined') return this.el;
    const layer = document.getElementById('fxlayer');
    if (!layer) return null;
    const el = document.createElement('div');
    el.id = 'bark'; el.className = 'bark'; el.hidden = true; el.setAttribute('aria-hidden', 'true');
    layer.appendChild(el);
    this.el = el;
    return el;
  }
  hide() { if (this.el) this.el.hidden = true; }
  paint(ctx, spots) {
    const sim = this.sim;
    const shot = !!(this.G.qs && this.G.qs.has('shot') && !sim.pin);
    if (!sim.line || shot) { this.hide(); return; }
    const spot = spots.find((s) => s.id === sim.spot);
    const el = this.ensure();
    if (!spot || !el || !ctx.project) { this.hide(); return; }
    const s = ctx.project(spot.x, spot.y + spot.lift, spot.z);
    if (!s || s.z > 1) { el.hidden = true; return; }
    if (el.dataset.line !== sim.line || el.dataset.who !== spot.label) {
      el.dataset.line = sim.line; el.dataset.who = spot.label;
      el.replaceChildren();
      const b = document.createElement('b'); b.textContent = spot.label;
      const span = document.createElement('span'); span.textContent = sim.line;
      el.append(b, span);
    }
    el.hidden = false;
    el.style.transform = `translate(${Math.round(s.x)}px, ${Math.round(s.y)}px) translate(-50%, -100%)`;
  }
  update(dt) {
    const G = this.G, ctx = G.ctx;
    if (!ctx || G.area !== 'bifrost') {
      this.here = false;
      if (this.sim.line) { this.sim.left = 0; this.sim.line = null; this.sim.spot = null; this.sim.pin = false; }
      this.hide();
      return;
    }
    if (!this.here) { this.here = true; this.sim = freshSim(this.rng); }
    const spots = this.spots(ctx);
    tick(this.sim, dt, { blocked: this.blocked(), spots, flags: (G.S && G.S.flags) || {}, rng: this.rng, near: NEAR, show: SHOW });
    this.paint(ctx, spots);
  }
  // QA / screenshots: show one line now, over the nearest speaker, ignoring range and the quiet gap.
  force(line) {
    const ctx = this.G.ctx;
    if (!ctx || this.G.area !== 'bifrost') return null;
    const spots = this.spots(ctx);
    if (!spots.length) return null;
    spots.sort((a, b) => a.d - b.d);
    const spot = spots[0];
    const text = line || pickLine((this.G.S && this.G.S.flags) || {}, this.rng, this.sim.last);
    this.here = true;
    this.sim.line = text; this.sim.last = text; this.sim.spot = spot.id; this.sim.left = SHOW; this.sim.pin = true;
    this.sim.wait = Math.max(0.05, rollGap(this.rng) - SHOW);
    this.paint(ctx, spots);
    const el = this.el;
    return { line: text, id: spot.id, x: spot.x, z: spot.z, shown: !!(el && !el.hidden) };
  }
}
