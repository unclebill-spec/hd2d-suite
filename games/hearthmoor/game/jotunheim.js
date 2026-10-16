// [JOTUNHEIM] Jotunheim (realm-jotunheim branch), built from the Hearthmoor Story script (staging story/jotunheim.md) with Cozy Builder's
// rulings (Hrimgard 7x, Ulfar combat_scale 2.4 with no second sheet, Flurry's neon twin as the main look). Chunk 1 = the first area: Stonehollow
// (`jotunheim`). Quests / TALK / shops / the Bifrost gate merge into the shared tables from here, like svartalfheim.js, so shared files only
// carry a few marked hook lines. Planned and not built yet: see JOT_PLANNED + JOTUNHEIM_PROGRESS.md (RESUME HERE).
import { TALK, ITEMS, QUESTS, MARKER_HOOKS } from './data.js';
import { REALM, MERIT } from './factions.js';
import { SHOPS, GOODS } from './shop.js';
import { WAYS } from './ravenhold.js';
import { lockRival, moodUp } from './alfheim.js';

export const JOT_PLANNED = {   // id -> display name (story 2.1); `barrow` (B1-B4) + `barrow2` (B5-B9) are the dungeon, two areas like clockdeep
  jotunheim: 'Stonehollow', jt_hall: 'Hall of Hearthstones', rimecaves: 'The Rime Caves', barrow: "The Titan's Barrow", barrow2: "The Titan's Barrow: the Throne",
};
export const AREAS_JOT = { jotunheim: 'areas/jotunheim/' };   // id -> 'areas/<id>/' (merged into game.js's area path map)
export const AREA_NAMES_JOT = { jotunheim: 'Stonehollow' };   // id -> display name (merged into game.js's AREA_NAME)
export const JOT_AREAS = Object.keys(JOT_PLANNED);

const flags = (S) => (S.flags = S.flags || {});
const F = (S) => S.flags || {};
const q = (S, k) => (S.quests || {})[k] || 0;
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };
Object.assign(REALM, { jotunheim: 'embassy', jt_hall: 'embassy', rimecaves: 'embassy', barrow: 'embassy', barrow2: 'embassy' });   // conquer / contract pay 'gate' with the alliance lock (later)
Object.assign(MERIT, { jt_gate: 60, jt_welcome: 40 });   // story 3.12 (the rest arrive with their quests)
WAYS.jotunheim = ['Stonehollow', 'jotunheim', 'from_waystone'];

export const JT_ARCH = { rect: [4.25, -12.3, 5.75, -11.45], pos: [5.0, -11.9], spawn: [5.0, -10.1, 'down'] };   // the ice arch on Bifrost's north wall
const HUB_GATE = { to: 'bifrost', spawn: 'from_jotunheim', rect: [-0.9, 10.1, 0.9, 11.1], label: 'the ice arch back to Bifrost Crossing' };
export const gateOpen = (S, qs) => !!(F(S).jt_gate_open || (F(S).alliance || {}).jotunheim || (qs && qs.has('jtq')));   // QA: ?jtq=... (Kolbrun's jt_gate quest comes next chunk)

// ------------------------------------------------------------------ items + Grimsa's stall (story 5.5; prices are first guesses)
Object.assign(ITEMS, {
  fur_mantle: { name: 'Fur cloak', px: 'tonic', about: "Grimsa's fur cloak, cut down for a small one. Frost resist +20%, and a cosmetic mantle over your tunic." },
  coldfire_lantern: { name: 'Cold-fire lamp', px: 'glowseed', about: 'A lamp that burns the giants\' blue cold fire. It lights, it never burns. Light radius +2.' },
});
Object.assign(GOODS, {
  tea: GOODS.tea || { name: 'Moonpetal tea', about: "A tin of moonpetal tea. Calms storms and clears a frost slow.", price: 14 },
  fur_mantle: { name: 'Fur cloak', about: 'Frost resist +20%. A mantle of goat-fur and bear-fur, sized for someone small.', price: 90 },
  coldfire_lantern: { name: 'Cold-fire lamp', about: 'Burns blue and never burns you. Light radius +2.', price: 55 },
});
SHOPS.jt_trader = { name: "Grimsa's Stall", keeper: 'Grimsa, giant trader', goods: ['tea', 'fur_mantle', 'coldfire_lantern', 'tonic'], gear: { n: 3, rar: [0, 1, 1] }, sellMul: 1 };

// ------------------------------------------------------------------ quests (story 3.2)
Object.assign(QUESTS, {
  jt_welcome: { title: 'The Stone Welcome', giver: 'Jarl Thyra Stonebrow', story: true, steps: {
    1: (S) => { const n = Math.min(F(S).jw_lifts || 0, need(S)); return n < need(S) ? `Lift the Welcome stones (E / A on the glow). ${n}/${need(S)}` : 'Let the town cheer.'; },
    2: "Sit at the Jarl's fire.",
    3: 'Stonehollow has welcomed you. The goats are still suspicious.',
  } },
});
const need = (S) => (S.hero === 'runeguard' ? 2 : 3);

// ------------------------------------------------------------------ talk (TALK is keyed by the actor id in the area spec)
const moodJot = (S) => ((F(S).realm_mood || {}).jotunheim || 0) >= 1;
Object.assign(TALK, {
  jt_trader(S) {
    const first = !(S.met || {}).jt_trader;
    return { pages: [first ? 'Grimsa. Stall. Cloaks for small ones, tea for cold ones. Everything here is cut to your size, which is, hm, more work than you know.'
                           : 'Cloak, tea or lamp? The lamp burns blue. It will not burn you. We tested on a goat.'],
             then: (G) => { met('jt_trader')(G); G.shopUI.show('jt_trader'); } };
  },
  goatherd(S) { return { pages: [F(S).jt_peace ? 'The war band turned back? Goats knew. Goats know everything.' : 'I know a goat-path. Goats know everything. Ask me when you have a reason to go sneaking.'] }; },
  goatwife(S) { return { pages: [q(S, 'jt_welcome') >= 3 ? 'She bit you? Good. That means she likes you.' : 'Mind the horns. Mind the whole goat, really. She has opinions.'] }; },
  ulfar(S) {
    const first = !(S.met || {}).ulfar;
    return { pages: [first ? 'Oh. Hello. You are very small. I am Ulfar. I look at the lake. It does not look back.'
                            : 'Snow tastes like nothing. I eat it anyway.', 'Kolbrun says stay off the lake. Unless you are a goat.'], then: met('ulfar') };
  },
  jt_a(S) { return { pages: ['Mind the stools. They are for sitting, not climbing.'] }; },
  jt_b(S) { return { pages: [['The aurora sings if you are quiet.', 'Dwarves think we steal. We cannot even fit in their doors.'][(S.day || 0) % 2]] }; },
  // the Jarl's choice (story 5.2). She sits in the Hall of Hearthstones (jt_hall, next chunk); the entry is here so the Hall only has to place her.
  jarl(S) {
    const f = F(S), mood = moodJot(S), locked = (f.rivals || {}).jotunheim === 'locked';
    if ((f.alliance || {}).jotunheim === 'befriend') return { pages: ['Then lift our stones. We trust arms that work.'] };
    if ((f.alliance || {}).jotunheim === 'conquer') return { pages: ['So. Midgard is a thief too. Take it, and go.'] };
    const opts = [];
    if (!locked) opts.push({ label: 'A friend. Let me prove you innocent.', pick: () => ({ pages: ['Then lift our stones. We trust arms that work.'],
      then: (G) => { ally(G.S).jotunheim = 'befriend'; lockRival(G.S, 'asgard'); moodUp(G.S, 'vanaheim'); G.setQuest(mood ? 'jt_heart' : 'jt_welcome', mood ? 1 : 1); G.toast('Jotunheim: befriended', 2.2); G.refreshMarkers && G.refreshMarkers(); } }) });
    opts.push({ label: "Midgard's. Hand over the Barrow Key.", pick: () => ({ pages: ['So. Midgard is a thief too. Take it, and go.'],
      then: (G) => { ally(G.S).jotunheim = 'conquer'; moodUp(G.S, 'asgard'); G.setQuest('jt_take', 1); G.toast('Jotunheim: conquered', 2.2); } }) });
    if (locked) opts.push({ label: 'The Guild sent me with an offer.', pick: () => ({ pages: ['An offer. Hm. Skuli will show you the goat-path.'], then: (G) => { flags(G.S).jt_contract = 1; G.setQuest('jt_hire', 1); } }) });
    return { pages: [mood ? 'You humbled the thunder-folk? Sit by the fire, small one.' : locked ? "Asgard's friend, in my hall. Say it quick."
                           : 'Midgard comes to Stonehollow. Dwarves call us thieves. Asgard calls us raiders. What are you?'], choice: { id: 'jt_jarl', options: opts } };
  },
});

// ------------------------------------------------------------------ the area's own look: cold fire on the braziers, rune pulses, the lake, a gloom light
const COLD = ['#7fd4ff', 4.2, 4.2];   // colour, intensity, range
const JT_FX = {
  jotunheim: [['cold_flame', [-2.4, -5.0], 1.0, 1], ['cold_flame', [2.4, -5.0], 1.0, 1], ['cold_flame', [-3.6, 1.6], 1.0, 1], ['cold_flame', [3.6, 1.6], 1.0, 1],
              ['cold_flame', [-3.2, 4.8], 1.0, 1], ['cold_flame', [3.2, 4.8], 1.0, 1], ['rune_pulse', [0, -5.4], 0.8, 1], ['rune_pulse', [-5.4, 0.2], 0.8, 1], ['rune_pulse', [5.2, -0.4], 0.8, 1],
              ['rune_pulse', [10.6, -1.4], 0.8, 1], ['ice_sparkles', [8.0, -3.2], 0.5, 0]],
};
const SPOTS = {   // look-spots / interactables (Svartalfheim pattern): hall door, cave path, frost prints, Welcome Ring stones
  lifts: [[-1.4, 2.6], [0.0, 3.3], [1.4, 2.6]],
  hall: [0, -9.4], caves: [10.0, -0.2], prints: [-3.4, -1.6],
};

export class Jotunheim {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.planned = JOT_PLANNED; this.fx = []; this.lights = []; this.spots = []; this.qaDone = null; this.gate = new JtGate(this); this.ring = null; this.lastLift = null; this.wrap(); }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  wrap() {   // E / A and tap try the realm's interactables first (same chained hook as Alfheim's / Svartalfheim's)
    const G = this.G, me = this; if (!G.harbor) return;
    const p0 = G.harbor.prompt.bind(G.harbor), i0 = G.harbor.interact.bind(G.harbor), t0 = G.harbor.onTap.bind(G.harbor);
    G.harbor.prompt = (...a) => me.prompt() || p0(...a);
    G.harbor.interact = (...a) => me.interact() || i0(...a);
    G.harbor.onTap = (hit, ...a) => me.onTap(hit) || t0(hit, ...a);
  }
  spot(o) { this.spots.push({ r: 1.6, show: () => true, ...o }); }
  nearSpot() {
    const c = this.ctx; if (!c || this.G.dlg) return null;
    let best = null, bd = 1e9;
    for (const s of this.spots) { if (!s.show()) continue; const d = Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]); if (d < s.r && d < bd) { bd = d; best = s; } }
    return best;
  }
  prompt() { const s = this.nearSpot(); return s ? s.label : ''; }
  interact() { const s = this.nearSpot(); if (!s) return false; s.act(); return true; }
  onTap(hit) {
    const c = this.ctx; if (!c || !hit) return false;
    for (const s of this.spots.filter((x) => x.show())) {
      if (Math.hypot(hit.x - s.pos[0], hit.z - s.pos[1]) > 0.9) continue;
      if (Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]) < s.r) s.act(); else c.walkTo(s.pos[0], s.pos[1] + 0.9);
      return true;
    }
    return false;
  }
  look(id, name, pages, then) { this.G.openDialogue({ id, name }, { pages, then }); }

  // QA preset (smoke / screenshots): ?jtq=open (gate only) | befriend (Jarl's choice made, Welcome quest at 1) | done
  qaPreset() {
    const v = this.qs().get('jtq'), S = this.G.S; if (!v || this.qaDone === v) return;
    this.qaDone = v;
    if (v === 'befriend' || v === 'done') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; if (!q(S, 'jt_welcome')) S.quests.jt_welcome = 1; }
    if (v === 'done') { S.quests.jt_welcome = 3; flags(S).jw_lifts = 3; flags(S).jt_trusted = 1; }
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (area === 'bifrost') { this.gate.atBifrost(ctx); return; }
    if (!AREAS_JOT[area]) return;
    this.qaPreset();
    if (area === 'jotunheim') this.stonehollow(ctx);
  }
  detach() {
    for (const f of this.fx) if (f) f.dur = f.t + 0.2;
    for (const l of this.lights) if (l) l.kill = true;
    this.fx = []; this.lights = []; this.spots = []; this.clearRing(); this.ctx = null; this.area = null;
  }
  stonehollow(ctx) {
    const G = this.G, S = G.S, gm = ctx.scene.game || (ctx.scene.game = {}), still = !!G.qaStill;
    this.gate.atHub(ctx);
    for (const [name, [x, z], dy, glow] of JT_FX.jotunheim) {   // gamefx decals / flames + a cold point light where the fx glows
      const y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    // Welcome Ring: three lift stones (story 3.2). E / A starts the ring, E / A again in the blue band lifts it.
    SPOTS.lifts.forEach((pos, i) => this.spot({ pos, r: 1.3, label: () => this.liftLabel(i), show: () => this.liftLive(i), act: () => this.tryLift(i) }));
    this.spot({ pos: [0, 4.0], r: 0.1, show: () => false, act: () => {}, label: '' });   // the ring's centre (story 2.3), for the QA / markers
    // look-spots (story 2.3 / 4.2): the Hall door, the cave path and the frost prints (entry points for the Giant Footprints clues)
    this.spot({ pos: SPOTS.hall, r: 1.8, label: 'the Hall of Hearthstones (E / A)', show: () => !AREAS_JOT.jt_hall, act: () => this.look('jt_hall_door', 'The Hall door', ["The great doors of the Hall of Hearthstones, barred by a beam as thick as a tree. The Jarl's fire glows under them.", '(The Hall opens in the next chapter of the build.)']) });
    this.spot({ pos: SPOTS.caves, r: 1.8, label: 'the path to the Rime Caves (E / A)', show: () => !AREAS_JOT.rimecaves, act: () => this.look('jt_caves_stair', 'The cave path', ['A stair of piled stone climbs toward a crack in the cliff. Cold blue light breathes out of it.', '(The Rime Caves open in a later chapter of the build.)']) });
    this.spot({ pos: SPOTS.prints, r: 1.8, label: 'giant frost prints (E / A)', act: () => this.prints() });
    if (!flags(S).jt_arrived && !still) { flags(S).jt_arrived = 1; G.toast('Snow drifts down; the cold fires gutter blue. A giant child stares, then waves.', 3.6); }
  }
  prints() {   // story 4: the footprints clue's entry point. The cellar clue (jh_trail) is in the Hall; here you learn the prints exist.
    const f = flags(this.G.S), decoy = !!f.sv_decoy;
    this.G.S.found = { ...(this.G.S.found || {}), jt_prints: 1 };
    this.look('jt_prints', 'Frost prints', decoy
      ? ["Giant prints, in frost. The boots match the mould you found in Anvildeep: the same cut, the same heel.", 'Someone wore these up the ice road and left the Hall by the cellar. Ask the Jarl to show you the cellar.']
      : ['Prints in the frost, bigger than a barrel lid, heading up to the Hall. They do not look like anyone in this town walks like that.', "(Jarl Thyra's cellar may know who wore them.)"]);
  }
  // ---- Welcome Ring stones (story 3.2): timing beat, 3 lifts (2 for the Runeguard)
  liftLive(i) { const S = this.G.S; return q(S, 'jt_welcome') === 1 && !((F(S).jw_done || {})[i]) && (F(S).jw_lifts || 0) < need(S); }
  liftLabel(i) { return this.ring && this.ring.i === i ? 'now! (E / A in the blue)' : 'lift the Welcome stone (E / A on the glow)'; }
  clearRing() { if (this.ring && this.ring.el) this.ring.el.remove(); this.ring = null; }
  tryLift(i) {
    const G = this.G;
    if (this.qs().get('lift') === 'auto') return this.lifted(i, true);
    if (!this.ring) {   // start: the ring fills over 1.6 s, the blue band is 0.55..0.8 of it
      const el = document.createElement('div'); el.id = 'jt-ring';
      el.style.cssText = 'position:fixed;left:50%;bottom:22%;width:180px;height:16px;margin-left:-90px;border:2px solid #cfeaff;border-radius:9px;background:#0a1830;z-index:50;pointer-events:none';
      el.innerHTML = '<div style="position:absolute;left:55%;width:25%;height:100%;background:#2ab4ff;opacity:.85"></div><div id="jt-ring-fill" style="position:absolute;left:0;height:100%;width:0;background:#e9f6ff;opacity:.9"></div>';
      document.body.appendChild(el); this.ring = { i, t: 0, el };
      return;
    }
    const t = this.ring.t / 1.6, hit = t >= 0.55 && t <= 0.8; this.clearRing();
    if (hit) this.lifted(i); else G.toast('The stone thuds. A giant laughs, kindly. Try again.', 2.2);
  }
  lifted(i, auto) {
    const G = this.G, S = G.S, f = flags(S); f.jw_done = { ...(f.jw_done || {}), [i]: 1 }; f.jw_lifts = (f.jw_lifts || 0) + 1; this.lastLift = i;
    const c = this.ctx, [x, z] = SPOTS.lifts[i];
    if (c && c.gamefx && c.gamefx.meta.effects.snow_puff) this.fx.push(c.gamefx.spawn('snow_puff', x, c.heightAt(x, z) + 0.2, z, { duration: 1.6 }));
    G.toast(`The stone lifts! ${Math.min(f.jw_lifts, need(S))}/${need(S)}`, 2);
    if (f.jw_lifts >= need(S)) this.cheer();
    G.drawLog && G.drawLog(); G.save && G.save();
  }
  cheer() {
    const G = this.G, hall = !!AREAS_JOT.jt_hall;
    this.look('jt_cheer', 'Stonehollow', ['(The last stone rolls upright with a boom. Giants lean out of their longhouses and cheer. A goat headbutts a fence in solidarity.)', hall ? "Jarl Thyra waits by her fire." : 'Welcome to Stonehollow, small one.'], (G2) => {
      if (hall) { G2.setQuest('jt_welcome', 2); return; }   // the Jarl's fire is in the Hall (next chunk): until it opens the welcome ends here
      this.finishWelcome(G2);
    });
  }
  finishWelcome(G) {
    const f = flags(G.S); G.setQuest('jt_welcome', 3); f.jt_trusted = 1; G.factions.add('embassy', MERIT.jt_welcome, 'jt_welcome'); gold(G, 20);
    f.realm_mood = { ...(f.realm_mood || {}), jotunheim: Math.max(3, (f.realm_mood || {}).jotunheim || 0) }; G.refreshMarkers && G.refreshMarkers();
  }
  update(dt) {
    if (!this.ctx) return;
    if (this.ring) {
      this.ring.t += dt; const el = this.ring.el, fill = el && el.querySelector('#jt-ring-fill');
      if (fill) fill.style.width = Math.min(100, (this.ring.t / 1.6) * 100) + '%';
      if (this.ring.t > 1.6) { this.clearRing(); this.G.toast('The stone thuds. A giant laughs, kindly. Try again.', 2.2); }
    }
  }
  // QA helpers for the smoke test
  qaTalk(id) { const e = TALK[id](this.G.S); if (e && e.then) e.then(this.G); return { pages: e ? e.pages.length : 0, choice: e && e.choice ? e.choice.options.map((o) => o.label) : null }; }
  qaPick(label, id = 'jarl') { const e = TALK[id](this.G.S), o = e.choice.options.find((x) => x.label === label), nx = o.pick(this.G); if (nx && nx.then) nx.then(this.G); return nx ? nx.pages.length : 0; }
  qaLift(i) { this.lifted(i, true); return this.qa(); }
  qa() {
    const c = this.ctx, S = this.G.S, f = F(S), gm = c ? (c.scene.game || {}) : {};
    return { realm: 'jotunheim', built: Object.keys(AREAS_JOT), planned: JOT_AREAS, area: this.area, exits: (gm.exits || []).map((e) => e.to), portals: (gm.portals || []).map((p) => p.to),
             spots: this.spots.filter((x) => x.show()).length, lifts: f.jw_lifts || 0, need: need(S), quest: q(S, 'jt_welcome'), gate: this.gate.qa(), alliance: (f.alliance || {}).jotunheim || null,
             actors: c ? c.actors.list.map((a) => a.id || a.role) : [], fx: this.fx.length, lights: this.lights.length, ring: !!this.ring, shop: !!SHOPS.jt_trader, found: S.found || {} };
  }
}

// ------------------------------------------------------------------ the gate (story 3.1 comes next chunk): runtime wiring on both ends, like svartalfheim_gate.js
class JtGate {
  constructor(jt) { this.jt = jt; this.G = jt.G; this.fetching = false; }
  get ctx() { return this.jt.ctx; }
  qs() { return this.jt.qs(); }
  put(sc) { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_jotunheim) gm.spawns.from_jotunheim = JT_ARCH.spawn.slice(); }
  atHub(ctx) {   // Stonehollow: the ice arch back to Bifrost (runtime portal) + the Bifrost scene prefetched with its return spawn
    const G = this.G, gm = ctx.scene.game || (ctx.scene.game = {});
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'bifrost')) gm.portals.push({ ...HUB_GATE, rect: HUB_GATE.rect.slice() });
    if (G.scenes && G.scenes.bifrost) { this.put(G.scenes.bifrost); return; }
    if (this.fetching || !G.scenes) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; this.put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  atBifrost(ctx) { this.put(ctx.scene); this.wire(ctx); }
  reopen() { if (this.ctx && this.jt.area === 'bifrost') this.wire(this.ctx); }
  wire(ctx) {   // the sealed ice arch becomes a portal once the gate is open
    const gm = ctx.scene.game; if (!gm || !gateOpen(this.G.S, this.qs())) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'jotunheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'jotunheim')) gm.portals.push({ fx: 'gate_jotunheim', to: 'jotunheim', spawn: 'from_bifrost', rect: JT_ARCH.rect.slice(), label: "Jotunheim's gate" });
    (gm.spawns = gm.spawns || {}).from_jotunheim = gm.spawns.from_jotunheim || JT_ARCH.spawn.slice();
  }
  qa() { const c = this.ctx, gm = c ? (c.scene.game || {}) : {}; return { portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch), spawns: Object.keys(gm.spawns || {}), open: gateOpen(this.G.S, this.qs()) }; }
}
