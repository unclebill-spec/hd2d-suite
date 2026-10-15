// [SVARTALFHEIM] Svartalfheim (realm-svartalfheim branch), built from the Hearthmoor Story script (staging story/svartalfheim.md)
// with Cozy Builder's decisions (section 14). Chunk 1 = the first area only: Anvildeep, Copper Row (`svartalfheim`).
// The realm's game module (quests, TALK, shops, gate at Bifrost, alliance lock, Dagna / Tick) comes in later chunks and merges into the
// shared tables from here, like alfheim.js, so shared files only carry a few marked hook lines.
import { ENEMIES, SPAWNS } from './heroes.js';
import { TALK, ITEMS } from './data.js';
import { REALM, MERIT } from './factions.js';
import { XP } from './progress.js';
import { SHOPS } from './shop.js';
import { WAYS } from './ravenhold.js';
import { SvStory } from './svartalfheim_story.js';
import { DeepRooms, ROOM_SPAWNS } from './svartalfheim_deep.js';
import { GorrakFight, PILLAR, ANVILS, VALVES } from './svartalfheim_bosses.js';

export const AREAS_SV = { svartalfheim: 'areas/svartalfheim/', forge_hall: 'areas/forge_hall/', glowmines: 'areas/glowmines/', clockdeep: 'areas/clockdeep/', clockdeep2: 'areas/clockdeep2/' };
export const AREA_NAMES_SV = { svartalfheim: 'Anvildeep: Copper Row', forge_hall: 'The Great Forge', glowmines: 'The Amethyst Mines', clockdeep: 'The Clockwork Deep', clockdeep2: 'The Clockwork Deep: the Binding Forge' };

const flags = (S) => (S.flags = S.flags || {});
const A = (S) => ((S.flags || {}).alliance || {}).alfheim;   // Alfheim's path (Brokk's arrival lines read it)
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };
Object.assign(REALM, { svartalfheim: 'embassy', forge_hall: 'embassy', glowmines: 'embassy', clockdeep: 'embassy', clockdeep2: 'embassy' });   // conquer / contract pay 'gate' with the alliance lock (later)
Object.assign(MERIT, { vouch: 40, copper: 60, forgeclaim: 60, contract: 60, deep_c: 120, sv_trial: 40, sv_name: 60, orri: 20, sv_kindle: 80, deep: 120, forgefire: 40 });   // story 3.12
WAYS.svartalfheim = ['Anvildeep, Copper Row', 'svartalfheim', 'from_waystone'];

// ------------------------------------------------------------------ foes (story 8.4) + XP; glowmines strays
Object.assign(ENEMIES, {
  forgeconstruct: { name: 'Forge construct', hp: 110, dmg: 14, speed: 1.1, reach: 1.6, windup: 0.6, cd: 1.8, aggro: 6.5, r: 0.36, push: 0.3, heavy: true, weakBelly: 1.5 },
  sparkgolem: { name: 'Spark golem', hp: 130, dmg: 15, speed: 1.0, reach: 5.0, keep: 3.0, windup: 0.7, cd: 2.2, aggro: 7, r: 0.4, push: 0.3, ranged: true, bolt: 'bolt', chain: 2 },
  sootling: { name: 'Sootling', hp: 34, dmg: 8, speed: 2.0, reach: 1.0, windup: 0.4, cd: 1.6, aggro: 6, r: 0.22, push: 0.7, float: true, popSmoke: 1.5 },
  shadowsmith: { name: 'Shadowsmith', hp: 100, dmg: 14, speed: 2.0, reach: 1.4, windup: 0.45, cd: 1.4, aggro: 7, r: 0.3, push: 0.5, elite: true, shadowStep: 8, hotHammer: 6 },
  hushblade: { name: 'Hushed blade', hp: 70, dmg: 11, speed: 2.2, reach: 1.3, windup: 0.4, cd: 1.4, aggro: 8, r: 0.28, push: 0.5, stealth: 4 },
  gorrak: { name: 'Gorrak Ironmaw, the Bound Forge-Tyrant', scale: 6, hp: 1800, dmg: 26, speed: 1.1, reach: 3.2, windup: 0.85, cd: 2.1, aggro: 12, r: 1.5, push: 0.1,
            heavy: true, slam: true, boss: true, minion: 'forgeconstruct', phases: [0.65, 0.3], chained: { r: 6 }, whip: { len: 9, dmg: 20 }, spray: { n: 5, dmg: 10 },
            plates: { every: 12, open: 4, mul: 2 }, quench: { stagger: 6 }, molten: { life: 8, dps: 10 }, rain: { every: 10, dmg: 22 }, anvils: 4, bindMul: 1.5,
            glow: '#e0602a', legendary: true, noRespawn: true },
  cavegolem: { ...ENEMIES.golem, name: 'Cave golem', glow: '#7a4ab0' },   // the stone golem's sprite (spawn { role: 'golem', def: 'cavegolem' }) with amethyst crusts
});
Object.assign(XP, { forgeconstruct: 50, sparkgolem: 60, sootling: 22, shadowsmith: 74, hushblade: 40, cavegolem: 56, gorrak: 900 });
Object.assign(SPAWNS, ROOM_SPAWNS);   // the Deep's foe pools (story 7)
SPAWNS.glowmines = [   // story 2.5: sootling, forgeconstruct (strays), cavegolem in the crystal galleries (north half) and around the lake
  { id: 'gm_soot1', role: 'sootling', pos: [6.8, -9.4] }, { id: 'gm_soot2', role: 'sootling', pos: [-1.2, -10.6] },
  { id: 'gm_fc0', role: 'forgeconstruct', pos: [-8.0, -3.2] }, { id: 'gm_fc1', role: 'forgeconstruct', pos: [7.8, -1.6] },
  { id: 'gm_golem0', role: 'golem', def: 'cavegolem', pos: [3.0, -7.6] },
  { id: 'gm_soot_n0', role: 'sootling', pos: [2.6, 4.2], night: true }, { id: 'gm_soot_n1', role: 'sootling', pos: [-3.6, 1.0], night: true },
];

// ------------------------------------------------------------------ items (story 11; icons reuse existing goods icons) + the tinker shop (story 5.8)
Object.assign(ITEMS, {
  forge_seal: { name: 'Forge-Seal', px: 'thawkey', about: 'Copper and rune-light. It opens the Deep\'s lift, and nothing else.' },
  forge_core: { name: 'Forge-core', px: 'glowseed', about: 'A lump of ember-ore that beats faintly, like it\'s thinking about being a heart.' },
  lesser_heart: { name: 'Lesser Heart', px: 'glowseed', about: 'Dagna\'s stopgap heart in a copper cage. Ugly. Works.' },
  deep_brass: { name: 'Deep brass', px: 'tonic', about: 'Old dwarven brass from the Deep\'s clockwork. Darker than normal brass, and warmer.' },
  amethyst: { name: 'Amethyst', px: 'glowseed', about: 'Violet crystal from the mines. It catches rune-light and keeps a little.' },
  clock_spring: { name: 'Clock spring', px: 'tonic', about: 'The Foreman\'s mainspring. Still tightly wound. Mind your fingers.' },
});
SHOPS.tinker = { name: 'Brasswhistle\'s Tinkery', keeper: 'Tansy Brasswhistle, gnome tinker', goods: ['tonic', 'runestone', 'ironbit'], gems: ['golem_core'], gear: { n: 3, rar: [1, 1, 2] }, sellMul: 1 };

// ------------------------------------------------------------------ talk (TALK is keyed by the actor id in the area spec)
Object.assign(TALK, {
  tansy(S) {
    const first = !(S.met || {}).tansy;
    return { pages: [first ? 'Tansy Brasswhistle, tinker! Mind the owl. He\'s not finished. Well, he\'s finished. He just doesn\'t know it.' : 'Gnomes and dwarves built half this city together. Dwarves did the heavy bits. We did the clever bits.'],
             then: (G) => { met('tansy')(G); G.shopUI.show('tinker'); } };
  },
  brokk(S) {   // story 5.6, arrival lines by Alfheim's path
    const a = A(S);
    return { pages: [a === 'befriend' ? 'Well. The elf-friend. I told you Anvildeep keeps a ledger. You\'re in it. Page one.'
                     : a === 'conquer' ? 'Ha! The one who humbled Lumenvale! Come in, come in. I\'ve told everyone. Twice.'
                     : 'A Midgarder. Hm. Haven\'t picked a side yet? Down here, everyone picks a side.'] };
  },
});

// ------------------------------------------------------------------ the Deep's lift (story 2.4): sealed until you hold the Forge-Seal
const LIFT = { rect: [3.2, -11.6, 5.0, -10.4], to: 'clockdeep', spawn: 'from_forge', label: 'the Deep\'s cog-cage lift behind the Great Forge' };
const hasSeal = (S) => !!(S.inv || {}).forge_seal;

// Ground light pools and glow lights placed from an area spec's `game.svfx` ([{ name, pos: [x, y, z], light? }]): svart_fx decals (pool_red /
// pool_blue / pool_violet / water_glow) with a matching point light at night, like forge.js does for the Forge Quarter. Data only; a later chunk
// adds the realm's quests / TALK / shops / gate on this class.
const SV_AREAS = Object.keys(AREAS_SV);
const SV_LIGHT = { pool_red: ['#ff5a4a', 7, 5.0], pool_blue: ['#2ab4ff', 5, 3.6], pool_violet: ['#a45cf0', 5, 4.0], water_glow: ['#3ac8b0', 4, 3.2] };
export class Svartalfheim {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.fx = []; this.lights = []; this.spots = []; this.qaDone = false; this.fight = new GorrakFight(this); this.deep = new DeepRooms(this); this.story = new SvStory(this); this.started = false; this.wrap(); }
  // E / A and tap try the realm's interactables first (same hook as Alfheim's, chained)
  wrap() {
    const G = this.G, me = this;
    if (!G.harbor) return;
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
    for (const s of this.spots.filter((q) => q.show())) {
      if (Math.hypot(hit.x - s.pos[0], hit.z - s.pos[1]) > 0.9) continue;
      if (Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]) < s.r) s.act(); else c.walkTo(s.pos[0], s.pos[1] + 0.9);
      return true;
    }
    return false;
  }
  look(id, name, pages) { this.G.openDialogue({ id, name }, { pages }); }
  qa() {   // read-only snapshot for the smoke test
    const c = this.ctx, gm = c ? (c.scene.game || {}) : {}, S0 = this.G.S;
    return { area: this.area, seal: hasSeal(this.G.S), exits: (gm.exits || []).map((e) => e.to),
             foes: c ? c.actors.list.filter((a) => ['sootling', 'forgeconstruct', 'golem', 'sparkgolem', 'shadowsmith'].includes(a.role)).map((a) => a.role) : [],
             deep: { vents: this.deep.v.reduce((n, v) => n + (v.n || 0), 0), hits: this.deep.hits, gusts: this.deep.gust.n, pushed: this.deep.gust.pushed || 0 },
             spots: this.spots.filter((x) => x.show()).length,
             quests: S0.quests || {}, alliance: ((S0.flags || {}).alliance || {}).svartalfheim || null, alfheim_alliance: ((S0.flags || {}).alliance || {}).alfheim || null, rivals: (S0.flags || {}).rivals || null, inv: S0.inv || {},
             gorrak: this.fight.e ? { hp: Math.round(this.fight.e.hp), max: this.fight.e.D.hp, scale: this.fight.e.D.scale, phase: this.fight.e.ph, state: this.fight.e.state, role: this.fight.e.a.role } : null };
  }
  // QA helpers for the smoke test: run an NPC's TALK entry (its `then`), or pick a Thane option by label
  qaTalk(id) { const e = TALK[id](this.G.S); if (e && e.then) e.then(this.G); return { pages: e ? e.pages.length : 0, choice: e && e.choice ? e.choice.options.map((o) => o.label) : null }; }
  qaPick(label, id = 'thane') { const e = TALK[id](this.G.S), o = e.choice.options.find((x) => x.label === label), nx = o.pick(this.G); if (nx && nx.then) nx.then(this.G); return nx ? nx.pages.length : 0; }
  qaPreset() {   // ?svq=seal gives the Forge-Seal (QA / smoke; the quests that hand it out come later)
    const q = (this.G.qs || new URLSearchParams(location.search)).get('svq'), S = this.G.S; if (!q || this.qaDone === q) return;
    this.qaDone = q;
    if (q === 'seal' || q === 'gorrak') { S.inv = S.inv || {}; S.inv.forge_seal = 1; }
    if (q === 'gorrak') { S.inv.lesser_heart = 1; this.skipIntro = true; }
    this.story.qaPreset(q);
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (!SV_AREAS.includes(area)) return;
    this.qaPreset();
    const S = this.G.S, gm = ctx.scene.game || (ctx.scene.game = {});
    if (area === 'forge_hall') {   // the lift stays shut until the Forge-Seal is in the bag
      gm.exits = (gm.exits || []).filter((e) => e.to !== 'clockdeep');
      if (hasSeal(S)) gm.exits.push({ ...LIFT });
      this.spot({ pos: [4.1, -10.0], r: 2.0, label: 'the Deep\'s lift is sealed (E / A to look)', show: () => !hasSeal(S),
        act: () => this.look('deep_lift', 'The Deep\'s lift', ['A lift cage. A seal of copper and rune-light holds it shut.']) });
    }
    this.started = false; this.fight.reset(); this.deep.reset(); this.story.attach(area);
    if (area === 'clockdeep2') {   // Gorrak's arena (C8): the quench valves (phase 2) and the rune-anvils (phase 3)
      VALVES.forEach((v, i) => this.spot({ pos: v, r: 1.7, label: 'open the quench valve (E / A)', show: () => !!this.fight.e && this.fight.e.ph === 2 && this.fight.e.state !== 'dead', act: () => this.fight.valve(i) }));
      ANVILS.forEach((v, i) => this.spot({ pos: v, r: 1.7, label: 'strike the rune-anvil (E / A)', show: () => !!this.fight.e && this.fight.e.ph === 3 && !this.fight.struck[i] && this.fight.e.state !== 'dead', act: () => this.fight.anvil(i) }));
    }
    const still = !!this.G.qaStill;
    for (const f of gm.svfx || []) {
      const [x, , z] = f.pos, y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[f.name]) this.fx.push(ctx.gamefx.spawn(f.name, x, y, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      const L = SV_LIGHT[f.name];
      if (ctx.addGlow && L && f.light !== false) this.lights.push(ctx.addGlow(x, y, z, { color: L[0], intensity: L[1], range: L[2], lift: 0.6, fadeIn: still ? 0.01 : 0.8 }));
    }
  }
  detach() { for (const f of this.fx) if (f) f.dur = f.t + 0.2; for (const l of this.lights) if (l) l.kill = true; this.fx = []; this.lights = []; this.spots = []; this.ctx = null; this.area = null; }
  anvilsOn() {}
  // the arena trigger: step into the Binding Forge and Gorrak wakes (intro dialogue, then the fight)
  gorrakIntro() {
    const G = this.G, S = G.S, conquer = ((flags(S).alliance || {}).svartalfheim) === 'conquer'; this.started = true;
    const pages = conquer ? ['Gorrak: "Not a dwarf. A Midgarder. With no heart in your hands, only a sword."', 'Gorrak: "You did not come to bind me. You came for my fire. Ha! Then TAKE it. If you can."']
      : ['(Chains groan. A shape the size of a house heaves against the anvil-pillar. Fire leaks through the seams of its plates.)', 'Gorrak: "SMALL ONES. Nine hundred years I burn for your pots and spoons. Now the cold comes, and the chains go slack."',
         'Gorrak: "You bring a little heart. A LITTLE heart. To hold ME. Ha! Come. Let us see if it fits."'];
    if (this.skipIntro || G.qaStill) { this.fight.spawn(); return; }
    G.openDialogue({ id: 'gorrak', name: 'Gorrak Ironmaw' }, { pages, then: () => this.ctx && this.fight.spawn() });
  }
  onGorrak() {
    const G = this.G, S = G.S, f = flags(S), conquer = ((f.alliance || {}).svartalfheim) === 'conquer';
    f.cd_boss = 1; this.fight.reset(); if (this.ctx && this.ctx.framePull) this.ctx.framePull(1);
    G.toast(conquer ? 'Gorrak falls. Something glows under rime in the flue.' : 'Gorrak sags against the chains. Set the Lesser Heart.', 3.2);
    // story 6.7: conquer = he gutters out; else rebound with the Lesser Heart (the Dagna / bargain variant waits on the companions)
    const pages = conquer ? ['(Gorrak falls to one knee. His plates split. The fire inside him has nothing left to hold it.)', 'Gorrak: "No little heart. No chains. Only a sword. ...So this is how a fire ends. Quietly."', '(The armour goes dark and cold. Above it, something glows under a shell of rime in the flue.)']
      : ['(Gorrak sags against the chains. The Lesser Heart fits his chest-plate with a clank.)', 'Gorrak: "A hired hand. Not even a dwarf. They could not be bothered to come themselves."', '(The runes flare cold blue.)'];
    G.openDialogue({ id: 'gorrak', name: 'Gorrak Ironmaw' }, { pages, then: (G2) => { const ff = flags(G2.S); if (conquer) ff.cd_taken = 1; else { ff.cd_bound = 1; if ((G2.S.inv || {}).lesser_heart) G2.take('lesser_heart', 1); if (((G2.S.quests || {}).sv_hire || 0) === 1) G2.setQuest('sv_hire', 2); } } });
  }
  update(dt) {
    const c = this.ctx;
    if (c && dt) { this.deep.update(dt, this.area); this.story.update(dt, this.area); }
    if (c && this.area === 'clockdeep2' && !this.started && !flags(this.G.S).cd_boss && !this.G.dlg) {
      const p = c.player; if (Math.hypot(p.x - PILLAR[0], p.z - PILLAR[1]) < 9) this.gorrakIntro();
    }
    if (!c || this.area !== 'forge_hall') return;
    const gm = c.scene.game, S = this.G.S;
    if (hasSeal(S) && !gm.exits.some((e) => e.to === 'clockdeep')) { gm.exits.push({ ...LIFT }); this.G.toast && this.G.toast('The Forge-Seal glows. The lift cage unlocks.', 2.4); }   // the seal arrived while you stand here
  }
}
