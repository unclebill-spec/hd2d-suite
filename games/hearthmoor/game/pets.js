// Hearthmoor glowing pets (Stage 6 part 2): one active pet follows the hero, glows (a light pool at night and in the
// Rift's always-dim places), and hums a small aura buff. Pets never fight. Story and numbers: the Story bot's pets doc
// (Stray Den, Signe Larkspur, "Strays of the Rift"); art: art/pets/ from the Art bot (pets.png = the NEON variant Bill
// approved 2026-10-05; build.py install_pets puts the sheet, the aura / pool effects and the particles in every area).
// Swap-in points: PETS[id].role (sprite row on the pets sheet), .fx (aura / pool / particles names), .light, .hover.
export const PETS = {
  wispkit: {
    name: 'Wisp kit', species: 'wisp kit', role: 'pet_wisp', glow: '#5ab4f0',
    hover: { lift: 0.5, bob: 0.06, hz: 0.8 },
    light: { color: '#5ab4f0', intensity: 4.0, range: 3.2, lift: 0.75, pulse: [0.75, 1.15, 0.9], r: 2.2 },
    fx: { aura: 'pet_aura_wisp', pool: 'pet_pool_wisp', parts: 'pet_wisp_spark' },
    aura: { id: 'coldfire_focus', name: 'Cold-fire Focus', desc: 'Spell cooldowns 6% shorter. Bond 3: 8%.', mods: { spellCd: 0.06 }, bond3: { spellCd: 0.08 } },
    about: 'A palm-sized orb of neon-blue cold fire with two dot eyes and a flicker for a tail. Hums when happy.',
    names: ['Pip', 'Wick', 'Glimmer', 'Bluebell', 'Sputter', 'Nix', 'Flicker', 'Mote', 'Skerry', 'Sapphire'],
  },
  glowmoth: {
    name: 'Glow-moth', species: 'glow-moth', role: 'pet_moth', glow: '#a45cf0',
    hover: { lift: 0.75, bob: 0.08, hz: 0.6 },
    light: { color: '#a45cf0', intensity: 5.0, range: 3.8, lift: 0.95, pulse: [0.85, 1.05, 0.5], r: 1.8 },
    fx: { aura: 'pet_aura_moth', pool: 'pet_pool_moth', parts: 'pet_moth_dust' },
    aura: { id: 'lamplight_dust', name: 'Lamplight Dust', desc: 'Hidden doors, gnome doors and springs shimmer within 6 m. Healing +10%. Bond 3: 8 m, +12%.',
            mods: { secretSense: 6, healMul: 0.10 }, bond3: { secretSense: 8, healMul: 0.12 } },
    about: 'A fluffy moth the size of a sparrow. Cream fur, gold antennae, violet eyespots that glow in the dark.',
    names: ['Velvet', 'Plum', 'Hush', 'Duskwing', 'Mothwick', 'Lavender', 'Nimbus', 'Fuzz', 'Page', 'Thistle'],
  },
  lanternfox: {
    name: 'Lantern-fox', species: 'lantern-fox', role: 'pet_fox', glow: '#ff4a3a',
    hover: { lift: 0, bob: 0, hz: 0 },
    light: { color: '#ff4a3a', intensity: 3.5, range: 2.8, lift: 0.6, pulse: [0.85, 1.1, 5.0], flicker: true, r: 1.6 },
    fx: { aura: 'pet_aura_fox', pool: 'pet_pool_fox', parts: 'pet_fox_ember', auraLift: 0.6 },
    aura: { id: 'rift_sense', name: 'Rift-sense', desc: 'Rifts are sensed 10 s earlier, with a direction. +10% Rift Marks, stamina refills 8% faster. Bond 3: 15 s, +12%, 10%.',
            mods: { riftWarn: 10, riftMarkMul: 0.10, stRegen: 0.08 }, bond3: { riftWarn: 15, riftMarkMul: 0.12, stRegen: 0.10 } },
    about: 'A rust-red fox kit with white socks. Its tail ends in a round glowing tuft, and a tiny light-fish swims inside.',
    names: ['Ember', 'Rusk', 'Tinder', 'Cinnabar', 'Pepper', 'Saffron', 'Tally', 'Hob', 'Marigold', 'Rowan'],
  },
  // the 4th Den pet (pets doc 6.6): a gift from Mossbrook on the Vanaheim befriend path (6.4 sets S.pets.mosspup.atDen),
  // never in the adopt list. Light per the Art bot's README (lime neon); the doc's draft cold-blue light was superseded.
  mosspup: {
    name: 'Moss-pup', species: 'moss-pup', role: 'pet_mosspup', glow: '#5aec3c', gift: 'vanaheim',
    hover: { lift: 0, bob: 0, hz: 0 },
    light: { color: '#5aec3c', intensity: 3.5, range: 3.0, lift: 0.55, pulse: [0.8, 1.1, 0.7], r: 1.5 },
    fx: { aura: 'pet_aura_mosspup', pool: 'pet_pool_mosspup', parts: 'pet_mosspup_spore', auraLift: 0.35 },
    aura: { id: 'foragers_nose', name: "Forager's Nose", desc: 'Hidden springs shimmer within 5 m. Spring-fizz +15 s. Forage +1 (25%). Bond 3: 7 m, +20 s, 35%.',
            mods: { springSense: 5, springBuff: 15, forage: 0.25 }, bond3: { springSense: 7, springBuff: 20, forage: 0.35 } },
    about: 'A puppy of soft green moss with root legs and a red toadstool on its head. Smells water through stone.',
    names: ['Sprout', 'Clover', 'Bramble', 'Truffle', 'Fernly', 'Burdock', 'Tuft', 'Pebble', 'Chanterelle', 'Mossy'],
  },
};
export const PET_IDS = Object.keys(PETS);
export const DEN = { biscuit: 6, adopt: 40, fedBond2: 3, fedBond3: 7, glowBoost: 60 };
const DARK = (t) => t > 0.75 || t < 0.25;   // dusk into night to dawn (the Hollows brazier window)
const DIM = { hollows: true, rift: true, ravenhold: true, bifrost: true };   // the Rift's gloom: pet light at every hour
const SECRET_SAY = { mosspup: ['({name} digs at the ground, ears up. Water down there?)', '({name} sits and stares at a wall. It hears fizzing.)'], glowmoth: ['({name} beats its wings at a blank wall. A hidden door?)', '({name} dusts the ground. Something fizzes below.)', '({name} hovers at a mushroom stem. Tiny door, tiny knock?)'] };

// the active pet's aura mods (bond 3 uses the bigger numbers); folded into progress.mods() like gear
export function petAura(S) {
  const p = S && S.pet, P = p && PETS[p.id]; if (!P) return {};
  return (p.bond || 1) >= 3 ? P.aura.bond3 : P.aura.mods;
}
export function petMods(S, m) {
  for (const [k, v] of Object.entries(petAura(S))) {
    if (k === 'healMul') m.healMul += v;
    else m[k] = (m[k] || 0) + v;
  }
  return m;
}
// the name choice: 4 names from the pet's list, seeded by the save (class + slot start + species), so a reload offers the same four
export function petNames(S, id) {
  const L = PETS[id].names.slice(); let h = 2166136261;
  for (const c of `${S.cls || ''}|${S.made || ''}|${id}`) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); }
  const out = [];
  while (out.length < 4 && L.length) { h = Math.imul(h ^ (h >>> 15), 2246822507) >>> 0; out.push(L.splice(h % L.length, 1)[0]); }
  return out;
}
export const isNight = (t) => t > 0.75 || t < 0.25;
// Forager's Nose: a chance of one more moonpetal / red cap / garden harvest (returns the extra count, 0 or 1)
export function forageExtra(S, rnd = Math.random) { const f = petAura(S).forage || 0; return f && rnd() < f ? 1 : 0; }
export function ensurePets(S) { S.pets = S.pets || {}; if (S.pet === undefined) S.pet = null; return S; }

export class Pets {
  constructor(G) { this.G = G; this.ctx = null; this.a = null; this.t = 0; this.boostT = 0; this.sensed = {}; this.lit = false; this.lastSense = null; this.lastWarn = null; }
  get S() { return ensurePets(this.G.S); }
  def() { const p = this.S.pet; return p ? PETS[p.id] : null; }
  attach(ctx, area) { this.ctx = ctx; this.area = area; this.sensed = {}; this.a = null; if (this.def()) this.spawn(); }
  detach() { this.despawn(); this.ctx = null; }
  dark() { const c = this.ctx; return !!c && (!!DIM[this.area] || (this.area === 'temple' && !(this.G.S.flags || {}).temple_lit) || DARK(c.clock.t)); }   // the Old Temple is dim until the relight (6.3)
  spawn() {
    const ctx = this.ctx, P = this.def(); if (!ctx || !P || this.a) return null;
    if (!ctx.actors.sheetOf(P.role)) return null;   // an area built without the pet sheet (old build): no pet, no crash
    const p = ctx.player;
    const a = ctx.addNpc({ id: 'pet', role: P.role, name: this.S.pet.name, pos: [p.x - 0.8, p.z + 0.5], behavior: 'follow', speed: 2.4, facing: p.facing });
    a.noTalk = true; a.followGap = 1.0; a.y = ctx.heightAt(a.x, a.z); a.pet = this.S.pet.id;
    this.a = a; this.t = 0; this.fx = []; this.light = null; this.emitter = null; this.lit = false;
    return a;
  }
  despawn() {
    const ctx = this.ctx; this.lightOff();
    if (this.a && ctx) ctx.removeNpc(this.a);
    this.a = null;
  }
  lightOn() {
    const ctx = this.ctx, P = this.def(), a = this.a, still = !!this.G.qaStill; if (!ctx || !P || !a || this.lit) return;
    const L = P.light;
    this.light = ctx.addGlow ? ctx.addGlow(a.x, a.y, a.z, { color: L.color, intensity: L.intensity, range: L.range, lift: L.lift, fadeIn: still ? 0.01 : 0.4 }) : null;
    this.fx = [];
    if (ctx.effects && ctx.effects.meta.effects[P.fx.pool]) {
      this.fx.push(this.pool = ctx.effects.spawn(P.fx.pool, a.x, a.y + 0.02, a.z + 0.03, { duration: 1e9, fadeIn: still ? 0 : 0.4 }));
      this.fx.push(this.aura = ctx.effects.spawn(P.fx.aura, a.x, a.y + (P.fx.auraLift ?? P.hover.lift), a.z + 0.05, { duration: 1e9, fadeIn: still ? 0 : 0.4 }));
    }
    if (ctx.particles && ctx.particles.meta && ctx.particles.meta.presets[P.fx.parts] && ctx.particles.addEmitter) {
      const pos = [a.x, a.y + P.hover.lift + 0.2, a.z];
      ctx.particles.addEmitter({ preset: P.fx.parts, pos });
      this.emitter = ctx.particles.emitters.find((e) => e.pos === pos) || null;   // addEmitter keeps our pos array: move it each frame
    }
    this.lit = true;
  }
  lightOff() {
    const ctx = this.ctx;
    for (const f of this.fx || []) if (f && ctx && ctx.effects) ctx.effects.remove(f);
    if (this.light) this.light.kill = true;
    if (this.emitter && ctx && ctx.particles) { const E = ctx.particles.emitters, i = E ? E.indexOf(this.emitter) : -1; if (i >= 0) E.splice(i, 1); }
    this.fx = []; this.light = null; this.emitter = null; this.pool = null; this.aura = null; this.lit = false;
  }
  zones() { return this.lit && this.a ? [{ x: this.a.x, z: this.a.z, r: this.def().light.r, src: 'pet' }] : []; }
  // ---------------------------------------------------------------- adopting, swapping, feeding
  adopt(id, name) {
    const S = this.S, P = PETS[id]; if (!P) return false;
    S.pets[id] = S.pets[id] || { name: name || P.name, bond: 1, fed: 0, lastFed: null };
    if (name) S.pets[id].name = name;
    return this.swap(id);
  }
  swap(id) {
    const S = this.S, own = S.pets[id]; if (!own) return false;
    S.pet = { id, name: own.name, bond: own.bond || 1 };
    if (this.ctx) {
      const at = this.a ? [this.a.x, this.a.z] : null;
      this.despawn(); const a = this.spawn();
      if (a && at) { a.x = at[0]; a.z = at[1]; }
      if (a && this.ctx.effects) this.ctx.effects.spawn('sparkle_burst', a.x, a.y, a.z + 0.05);
    }
    return true;
  }
  feed() {
    const G = this.G, S = this.S, p = S.pet; if (!p) return { ok: false, why: 'no pet' };
    if (!(S.inv.denbiscuit > 0)) return { ok: false, why: 'no biscuit' };
    const own = S.pets[p.id], day = S.day || 0;
    G.take('denbiscuit', 1);
    this.boostT = DEN.glowBoost;
    let up = false;
    if (own.lastFed !== day) {   // one feed counts per in-game day: 3 fed days = bond 2, 7 = bond 3
      own.fed = (own.fed || 0) + 1; own.lastFed = day;
      const b = own.fed >= DEN.fedBond3 ? 3 : own.fed >= DEN.fedBond2 ? 2 : 1;
      if (b > (own.bond || 1)) { own.bond = b; p.bond = b; up = true; }
    }
    G.toast && G.toast(up ? `${p.name}'s bond grows: ${'♥'.repeat(p.bond)}${'♡'.repeat(3 - p.bond)}` : `${p.name} crunches the biscuit and glows twice as bright.`, 2.4);
    G.audio && G.audio.sfx('pickup');
    return { ok: true, up, bond: p.bond, fed: own.fed };
  }
  // ---------------------------------------------------------------- aura effects that need the world
  riftWarn() { return petAura(this.S).riftWarn || 0; }
  senseRift(pos) {   // the lantern-fox's tail flares before a rift opens: a toast with a direction
    const ctx = this.ctx, p = this.S.pet; if (!ctx || !p) return;
    const dx = pos[0] - ctx.player.x, dz = pos[1] - ctx.player.z;
    const dir = Math.abs(dx) > Math.abs(dz) ? (dx > 0 ? 'east ➜' : '⬅ west') : (dz > 0 ? 'south ⬇' : 'north ⬆');
    this.lastWarn = { pos: pos.slice(), dir, t: +(this.G.rifts ? this.G.rifts.timer : 0).toFixed(1) };
    if (this.a && ctx.addGlow) ctx.addGlow(this.a.x, this.a.y, this.a.z, { color: '#ff4a3a', intensity: 7, range: 3.4, life: 1.2, lift: 0.6 });
    this.G.toast && this.G.toast(`${p.name}'s tail flares red: a rift, that way (${dir}).`, 3);
  }
  secrets() {   // springs, gnome doors and hidden ledges this area has that are not found yet
    const ctx = this.ctx, gm = (ctx && ctx.scene.game) || {}, F = this.S.found || {}, out = [];
    if (gm.spring && !(gm.spring.secret ? F[gm.spring.secret] : F.spring)) out.push({ id: gm.spring.secret || 'spring', pos: gm.spring.pos, kind: 'spring' });
    for (const d of gm.doors || []) if (!F[d.id]) out.push({ id: d.id, pos: d.pos, kind: 'door' });
    for (const b of gm.bounces || []) if (b.secret && !F[b.id || 'bounce']) out.push({ id: b.id || 'bounce', pos: b.pos, kind: 'ledge' });
    return out;
  }
  update(dt) {
    const ctx = this.ctx, a = this.a, P = this.def(); if (!ctx) return;
    if (P && !a) { this.spawn(); return; }
    if (!a || !P) return;
    this.t += dt; if (this.boostT > 0) this.boostT -= dt;
    if (a.hurry && a.anim === 'follow' && !this.gait) { const p = ctx.player; this.gait = { anim: a.anim, hurry: true, d: +Math.hypot(a.x - p.x, a.z - p.z).toFixed(2) }; }   // first catch-up gait frame (QA)
    if (!a.act) a.lift = P.hover.lift ? P.hover.lift + Math.sin(this.t * 2 * Math.PI * P.hover.hz) * P.hover.bob : 0;
    const want = this.dark() || this.boostT > 0;
    if (want && !this.lit) this.lightOn(); else if (!want && this.lit) this.lightOff();
    if (this.lit) {
      const L = P.light, [lo, hi, hz] = L.pulse;
      let k = lo + (hi - lo) * (0.5 + 0.5 * Math.sin(this.t * 2 * Math.PI * hz));
      if (L.flicker) k = lo + (hi - lo) * (0.5 + 0.5 * Math.sin(this.t * 2 * Math.PI * hz) * Math.sin(this.t * 7.3));
      if (this.boostT > 0) k *= 1.6;
      if (this.light) { this.light.pos.set(a.x, a.y, a.z); this.light.base = L.intensity * k; }
      if (this.pool) { this.pool.x = a.x; this.pool.y = a.y + 0.02; this.pool.z = a.z + 0.03; }
      if (this.aura) { this.aura.x = a.x; this.aura.y = a.y + (P.fx.auraLift ?? P.hover.lift) + (a.lift - P.hover.lift); this.aura.z = a.z + 0.05; }
      if (this.emitter) { this.emitter.pos[0] = a.x; this.emitter.pos[1] = a.y + (a.lift || 0) + 0.2; this.emitter.pos[2] = a.z; }
    }
    // the glow-moth's Lamplight Dust: unfound secrets within range shimmer (a glitter + a soft chime, once per visit)
    const au = petAura(this.S), sr = au.secretSense || 0, wr = au.springSense || 0;   // the moss-pup's Forager's Nose: springs only
    if (sr || wr) for (const q of this.secrets()) {
      const r = q.kind === 'spring' ? Math.max(sr, wr) : sr;
      if (!r || this.sensed[q.id] || Math.hypot(ctx.player.x - q.pos[0], ctx.player.z - q.pos[1]) > r) continue;
      this.sensed[q.id] = true; this.lastSense = { ...q };
      if (ctx.effects) ctx.effects.spawn('glitter', q.pos[0], ctx.heightAt(q.pos[0], q.pos[1]) + 0.2, q.pos[1] + 0.05, { duration: 2.4 });
      const lines = SECRET_SAY[this.S.pet.id] || SECRET_SAY.glowmoth; this.G.toast && this.G.toast(lines[Object.keys(this.sensed).length % lines.length].replace('{name}', this.S.pet.name), 2.6);
      this.G.audio && this.G.audio.sfx('blip');
    }
  }
  state() {
    const a = this.a, P = this.def(), S = this.S;
    return { pet: S.pet, owned: Object.keys(S.pets), role: P && P.role, aura: petAura(S), dark: this.dark(), lit: this.lit, boost: this.boostT > 0,
             actor: a ? { x: +a.x.toFixed(2), z: +a.z.toFixed(2), lift: +(a.lift || 0).toFixed(3), anim: a.anim, hurry: !!a.hurry, sheet: a.S && a.S.name } : null,
             gait: this.gait || null,
             light: this.light ? { color: '#' + this.light.color.getHexString(), base: +this.light.base.toFixed(2), range: this.light.range, power: +this.light.power.toFixed(2) } : null,
             fx: (this.fx || []).map((f) => f && f.name), emitter: !!this.emitter, sensed: this.lastSense, warned: this.lastWarn };
  }
}
