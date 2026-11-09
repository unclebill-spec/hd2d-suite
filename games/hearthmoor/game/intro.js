// Hearthmoor, Stage 5 part 1: the Lantern Eve opening (day 0, dusk, the Plaza). Plays once, on a new game only:
//   lanterns  villagers light fish-orb lanterns (sky_lantern + a warm light_pool under each + sparkles) and let them go;
//             they float up as glowing points of light (two warm point lights ride along, inside the glow-light cap)
//   talk      Bram, Grandpa Alder, Tib and Marla say INTRO_LINES, one line per page, in the dialogue panel
//   tear      a violet-red tear (rift_tear) opens over the moss gate; a dark mist column stands in it;
//             three lanterns fall into Marla's geraniums and the rest stop dead in the air
//   fight     a cold-fire wraith slips out of it (def 'evewraith': not light-shy, gentle) and the first fight happens
//             under the lanterns; input is free, the skip chip stays up
//   after     the tear seals, the three fallen lanterns stay down, the rest drift on; the sigil drops (flags.ew_on)
// Skip any time: Esc, controller B, or a tap / click on the 'skip' chip. S.flags.intro = 'done' | 'skipped' is saved,
// and Continue never replays it (a save made mid-intro, 'playing', counts as skipped on load).
import { INTRO_LINES } from './data.js';
export const EVE_T = 0.76;   // named dusk: blue sky, lamps coming on
const RELEASE = [[-2.4, -1.4], [-0.9, 0.7], [1.3, 1.1], [2.7, -0.5], [-3.3, 1.5], [0.4, -2.3], [3.3, 2.4]];
const BRAM_AT = [-0.9, 1.9];
const WRAITH = { id: 'eve_wraith', role: 'wraith', def: 'evewraith', noLoot: true };
// the flower crate by Marla's stall: three lanterns land in her geraniums
const GERANIUMS = [[-3.2, -1.4], [-2.45, -1.85], [-2.85, -2.05]];
const FIG_HOLD = 2.5, FIG_FADE = 0.6;

export class Intro {
  constructor(G) { this.G = G; this.active = false; this.step = null; this.t = 0; this.lan = []; this.drift = []; this.lights = []; }
  blocking() { return this.active && (this.step === 'lanterns' || this.step === 'tear'); }   // cinematic beats: no walking
  state() {
    return { active: this.active, step: this.step, flag: (this.G.S.flags || {}).intro || null,
             lanterns: this.lan.length, rising: this.lan.filter((l) => l.up > 0.05).length, maxUp: Math.max(0, ...this.lan.map((l) => l.up)),
             tear: !!this.tear, wraith: !!(this.wraith && this.wraith.state !== 'dead' && this.wraith.state !== 'gone'), frozen: !!this.frozen };
  }
  // new game in the Plaza -> play; `force` lets the smoke test replay it to check the skip paths
  start(force = false) {
    const G = this.G, ctx = G.ctx, F = (G.S.flags = G.S.flags || {});
    if (!ctx || G.area !== 'plaza' || this.active || (F.intro && !force)) return false;
    this.active = true; this.step = 'lanterns'; this.t = 0; this.frozen = false; F.intro = 'playing';
    G.S.t = EVE_T; ctx.clock.set(EVE_T);
    $('introSkip').hidden = false;
    const fx = ctx.effects;
    this.lan = RELEASE.map(([x, z], i) => {
      const y = ctx.heightAt(x, z);
      const l = { x, z, y0: y + 0.8, up: 0, rel: 0.5 + i * 0.32, sway: i * 1.7, f: null, pool: null };
      l.f = fx && fx.spawn('sky_lantern', x, l.y0, z, { duration: 1e9, fadeIn: 0.6 });
      l.pool = fx && fx.spawn('light_pool', x, y, z + 0.03, { duration: 1e9, fadeIn: 0.6 });
      return l;
    });
    this.lights = [0, 2].map((i) => ctx.addGlow ? ctx.addGlow(RELEASE[i][0], this.lan[i].y0, RELEASE[i][1], { color: '#ffb84a', intensity: 6, range: 5.0, fadeIn: 0.8, lift: 0 }) : null);
    this.bram = ctx.npc('eve_bram') || ctx.addNpc({ id: 'eve_bram', role: 'innkeeper', name: 'Bram of the Kettle & Key', pos: BRAM_AT.slice(), facing: 'down', behavior: 'idle' });
    G.audio.sfx('quest');
    return true;
  }
  update(dt) {
    const G = this.G, ctx = G.ctx; if (!ctx) return;
    if (this.drift && this.drift.length) {
      for (const l of this.drift) if (l.f) { l.up += dt * 0.5; l.f.y = l.y0 + l.up; }
      if (this.drift.every((l) => !l.f || l.f.t >= l.f.dur)) this.drift = [];
    }
    if (!this.active) return;
    this.t += dt;
    this.tickFigure(dt);
    for (const l of this.lan) {   // rise (unless the tear has frozen them), sway, and carry their lights
      if (l.fall) { this.fallLantern(l, dt, ctx); continue; }   // three drop into the geraniums instead of freezing
      if (this.t < l.rel || this.frozen) continue;
      if (!l.sent) { l.sent = true; ctx.effects && ctx.effects.spawn('sparkle_burst', l.x, l.y0 - 0.3, l.z + 0.05); if (l.pool) l.pool.dur = l.pool.t + 6; }
      l.up += dt * (0.42 + (l.sway % 1) * 0.12);
      if (l.f) { l.f.y = l.y0 + l.up; l.f.x = l.x + Math.sin(this.t * 0.8 + l.sway) * 0.18; }
      if (l.up > 9 && l.f && l.f.dur > 1e8) l.f.dur = l.f.t + 0.3;   // gone into the sky: dither out
    }
    this.lights.forEach((g, k) => { const l = this.lan[k * 2]; if (g && l && l.f) { g.pos.set(l.f.x, l.f.y, l.z); g.scale = Math.max(0, 1 - l.up / 8); } });
    if (this.step === 'lanterns' && this.t > 3.2 && !G.dlg) { this.step = 'talk'; this.talk(); }
    else if (this.step === 'tear' && this.t - this.t0 > 2.2 && !this.wraith) this.spawnWraith();
    else if (this.step === 'fight') {
      const e = this.wraith;
      if (!e || e.state === 'dead' || e.state === 'gone') { this.step = 'after'; this.after(); }
    }
  }
  say(id, pages, then) {
    const G = this.G;
    const a = id === 'narr' ? { id: 'narr', name: '' } : (G.ctx.npc(id) || { id, name: id, role: id });
    G.openDialogue(a, { pages, then: () => { if (this.active && then) then(); } });
  }
  // one line per page; consecutive lines from one speaker share a panel, chained the way the old nested say() did
  chain(lines, done) {
    const groups = [];
    for (const [id, text] of lines) {
      const g = groups[groups.length - 1];
      if (g && g.id === id) g.pages.push(text);
      else groups.push({ id, pages: [text] });
    }
    const step = (i) => {
      if (!this.active) return;
      if (i >= groups.length) { if (done) done(); return; }
      this.say(groups[i].id, groups[i].pages, () => step(i + 1));
    };
    step(0);
  }
  talk() { this.chain(INTRO_LINES.talk, () => this.openTear()); }
  // spawn from whichever atlas actually has the row (plaza spells do not carry mist_drift)
  fxSpawn(ctx, name, x, y, z, opts) {
    for (const E of [ctx.effects, ctx.gamefx, ctx.hmfx]) {
      if (E && E.meta && E.meta.effects && E.meta.effects[name]) return E.spawn(name, x, y, z, opts);
    }
    return null;
  }
  // fx-only silhouette: no veyra billboard. A dark mist_drift column, two small blue glints at eye height.
  tallFigure(ctx, x, y, z) {
    this.figFx = []; this.figGlows = []; this.figAge = 0;
    const zx = z - 0.55, opts = { duration: 1e9, fadeIn: 0.25 };
    for (const dy of [0.3, 1.05, 1.8]) {
      const col = this.fxSpawn(ctx, 'mist_drift', x, y + dy, zx, opts);
      if (col) this.figFx.push(col);
    }
    const eyeY = y + 1.7;
    for (const dx of [-0.14, 0.14]) {
      // light_pool-sized (same 32px cell) and blue; the light_pool row itself is gold
      const glint = ctx.effects && ctx.effects.spawn('coldfire_pool', x + dx, eyeY, zx + 0.06, opts);
      if (glint) this.figFx.push(glint);
      if (ctx.addGlow) this.figGlows.push(ctx.addGlow(x + dx, eyeY, zx, { color: '#7eb6ff', intensity: 1.5, range: 1.15, fadeIn: 0.2, lift: 0 }));
    }
  }
  tickFigure(dt) {
    if (this.figAge == null) return;
    this.figAge += dt;
    if (this.figAge <= FIG_HOLD) return;
    const u = Math.min(1, (this.figAge - FIG_HOLD) / FIG_FADE);
    for (const f of this.figFx) if (f) f.fade = u;
    for (const g of this.figGlows) if (g) g.scale = 1 - u;
    if (u >= 1) this.clearFigure();
  }
  clearFigure() {
    for (const f of this.figFx || []) if (f && f.dur > f.t) f.dur = f.t;
    for (const g of this.figGlows || []) if (g) g.kill = true;
    this.figFx = null; this.figGlows = null; this.figAge = null;
  }
  fallLantern(l, dt, ctx) {
    if (l.landed) {
      if (l.f) { l.f.x = l.land[0]; l.f.y = l.landY; l.f.z = l.land[1]; }
      l.x = l.land[0]; l.z = l.land[1];
      return;
    }
    l.fallT += dt;
    const u = Math.min(1, l.fallT / l.fallDur), e = u * u;
    const x = l.x0 + (l.land[0] - l.x0) * e, z = l.z0 + (l.land[1] - l.z0) * e;
    const y = l.yStart + (l.landY - l.yStart) * e;
    l.x = x; l.z = z;
    if (l.f) { l.f.x = x; l.f.y = y; l.f.z = z; }
    if (u < 1) return;
    l.landed = true;
    ctx.effects && ctx.effects.spawn('sparkle_burst', l.land[0], l.landY, l.land[1] + 0.05);
    this.G.audio.sfx('splash');
  }
  openTear() {
    const G = this.G, ctx = G.ctx;
    this.step = 'tear'; this.t0 = this.t; this.frozen = true;
    const g = ctx.fx && ctx.fx.portal_0, x = g ? g.x : -1.4, z = g ? g.z : -8.5, y = (g ? g.y : ctx.heightAt(x, z)) + 0.7;
    this.tearAt = [x, y, z];
    this.tear = ctx.effects && ctx.effects.spawn('rift_tear', x, y, z + 0.45, { duration: 1e9, fadeIn: 0.5, onTop: true });
    this.tearLight = ctx.addGlow ? ctx.addGlow(x, y + 0.6, z + 0.6, { color: '#c03cc8', intensity: 7, range: 6, fadeIn: 0.6, lift: 0 }) : null;
    ctx.effects && ctx.effects.spawn('glyph_burst', x, y - 0.6, z + 0.3);
    this.tallFigure(ctx, x, y, z);
    GERANIUMS.forEach((land, k) => {
      const l = this.lan[k]; if (!l) return;
      l.fall = true; l.fallT = 0; l.fallDur = 0.75 + k * 0.12; l.landed = false; l.land = land;
      l.x0 = l.f ? l.f.x : l.x; l.z0 = l.f ? l.f.z : l.z;
      l.yStart = l.f ? l.f.y : l.y0 + l.up;
      l.landY = ctx.heightAt(land[0], land[1]) + 0.42;
    });
    G.audio.sfx('portal');
    G.toast('A violet-red tear flickers open over the moss gate. The lanterns stop dead in the air.', 3.0);
  }
  spawnWraith() {
    const G = this.G, ctx = G.ctx, C = G.combat;
    const [x, , z] = this.tearAt;
    const sp = { ...WRAITH, pos: [x + 0.2, z + 1.6] };
    this.wraith = C.spawnEnemy(sp, true);
    this.wraith.home = [0.2, -0.6];   // it means the Plaza: leash from the square, not the gate
    if (!C.peace) { this.wraith.state = 'chase'; this.wraith.target = ctx.player; }
    this.chain(INTRO_LINES.wraith, () => {
      this.step = 'fight';
      G.toast(G.hintFight ? G.hintFight() : 'Fight! Attack: R (controller X, ⚔ on the pad). Guard C, roll X.', 3.4);
    });
  }
  // sigil + the Lanterns Down flag. Idempotent: skip during the aftermath must not hand out a second seal.
  eveGrant() {
    const G = this.G, S = G.S;
    S.flags = S.flags || {};
    S.flags.ew_on = 1;
    if (!S.inv.eve_sigil) G.give('eve_sigil', 1);
  }
  after() {
    const G = this.G, ctx = G.ctx;
    this.frozen = false;
    if (this.tear) { this.tear.dur = this.tear.t + 0.4; this.tear = null; }
    if (this.tearLight) { this.tearLight.kill = true; this.tearLight = null; }
    G.audio.sfx('quest');
    this.eveGrant();
    const lines = INTRO_LINES.after.slice();
    const cls = G.S.cls;
    if ((cls === 'seer' || cls === 'cinderknight') && INTRO_LINES[cls]) lines.splice(1, 0, INTRO_LINES[cls]);
    this.chain(lines, () => this.finish('done'));
  }
  finish(how) {
    const G = this.G, ctx = G.ctx;
    this.cleanup(how === 'skipped');
    G.S.flags.intro = how;
    G.toast(how === 'done' ? 'Grandpa Alder wants a word (!).' : 'Intro skipped. Lantern Eve tasks are in your quest log (J).', 3.2);
    G.refreshMarkers && G.refreshMarkers();
    if (ctx && G.factions) G.factions.attach(ctx, G.area);   // the Order's warden takes her post once the opening is over
    G.save();
  }
  skip() { if (this.active) { this.eveGrant(); this.finish('skipped'); } return true; }
  cleanup(hard) {
    const G = this.G, ctx = G.ctx;
    this.active = false; this.step = null; this.frozen = false;
    this.clearFigure();
    $('introSkip').hidden = true;
    if (G.dlg) G.dropDialogue();
    for (const l of this.lan) {
      const linger = l.fall ? (hard ? 0.3 : 8) : (hard ? 0.3 : 0.3 + 6 + Math.random() * 3);
      if (l.f) l.f.dur = l.f.t + linger;
      if (l.pool) l.pool.dur = l.pool.t + 0.3;
    }
    this.drift = hard ? [] : this.lan.filter((l) => !l.fall);   // the fallen three stay in the geraniums; the rest drift on
    this.lan = [];
    for (const g of this.lights) if (g) g.kill = true;
    this.lights = [];
    if (this.tear) { this.tear.dur = this.tear.t + 0.3; this.tear = null; }
    if (this.tearLight) { this.tearLight.kill = true; this.tearLight = null; }
    const e = this.wraith; this.wraith = null;
    if (e && e.state !== 'dead' && e.state !== 'gone' && G.combat.ctx) G.combat.kill(e, true);
    if (this.bram && ctx) { ctx.removeNpc(this.bram); this.bram = null; }
  }
  // a load / area change mid-intro drops it (the flag says 'skipped' so it never replays)
  abandon() { this.drift = []; this.clearFigure(); if (this.active) { this.active = false; this.step = null; this.lan = []; this.lights = []; this.tear = null; this.tearLight = null; this.wraith = null; this.bram = null; $('introSkip').hidden = true; this.G.S.flags.intro = 'skipped'; } }
}
const $ = (id) => document.getElementById(id);
