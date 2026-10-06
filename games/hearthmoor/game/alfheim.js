// [ALFHEIM] Alfheim (realm-alfheim branch): Lumenvale Glade + the Prism Vault, wired to Alfheim's sealed arch at
// Bifrost Crossing. Everything Alfheim lives here and is merged into the shared tables at import (enemy stats + spawns,
// talk, the story quest, quest tags, faction realm, glow pools), so the shared files only carry a few marked hook lines.
//   * the gate: Alfheim's arch at Bifrost opens (a violet swirl instead of the frozen seal) once you hold the Guild's
//     Keybearer rank (bifrost.js GATES: gate rank 3), or S.flags.alf_key, or ?alfheim (QA). Until then it stays sealed.
//   * Lumenvale: Warden Aelindra Starwell (alliance choice: befriend / conquer, S.flags.alliance.alfheim) gives the story
//     quest; Thalion the ranger, Nyssa the wisp-keeper and a child round out the town.
//   * foes: prism shards (fast melee), neon wisps (ranged prism bolts, float), crystal golems (heavy slam, dazzle),
//     Mirror Duelists (elites: a hit can make them blink behind you), the Prism Colossus (mini-boss, ~2.5x, guards the
//     vault door) and Lady Sylvaine (the boss, 5x: drains your magic with her nova, bolts you at range, calls two Mirror
//     Duelists at half health).
// Gloom and glow: violet is Alfheim's lead glow, cold-fire blue and red accents; point lights + palette pixels, no bloom.
import { ENEMIES, SPAWNS } from './heroes.js';
import { TALK, QUESTS, MARKER_HOOKS } from './data.js';
import { REALM } from './factions.js';
import { XP } from './progress.js';
import { GLOW_TABLES } from './glow.js';

const V = '#a45cf0', COLD = '#5ab4f0', RED = '#e0302a';
export const AREAS_ALF = { alfheim: 'areas/alfheim/', prismvault: 'areas/prismvault/' };
export const AREA_NAMES_ALF = { alfheim: 'Lumenvale Glade', prismvault: 'The Prism Vault' };
const BF_ARCH = { pos: [-5.0, -11.9], rect: [-5.75, -12.3, -4.25, -11.45], spawn: [-5.0, -10.1, 'down'] };   // Bifrost's Alfheim arch

// ------------------------------------------------------------------ enemies (heroes.js fields; scale = hero heights)
Object.assign(ENEMIES, {
  prismshard: { name: 'Prism shard', hp: 50, dmg: 10, speed: 2.2, reach: 1.2, windup: 0.34, cd: 1.1, aggro: 6.0, r: 0.26, push: 0.5, float: true },
  neonwisp: { name: 'Neon wisp', hp: 38, dmg: 8, speed: 1.7, reach: 6.0, keep: 3.4, windup: 0.5, cd: 2.3, aggro: 6.5, r: 0.24, push: 0.6, ranged: true, float: true, bolt: 'prism_bolt' },
  crystalgolem: { name: 'Crystal golem', hp: 150, dmg: 17, speed: 1.0, reach: 1.6, windup: 0.7, cd: 2.0, aggro: 5.5, r: 0.38, push: 0.2, heavy: true, slam: true, chill: 12,
                  chillMsg: 'Dazzled! The crystal golem\'s prism flash saps your stamina.' },
  mirrorduelist: { name: 'Mirror Duelist', hp: 110, dmg: 14, speed: 2.3, reach: 1.4, windup: 0.3, cd: 0.95, aggro: 7.0, r: 0.3, push: 0.45, elite: true },
  prismcolossus: { name: 'The Prism Colossus', scale: 2.5, hp: 520, dmg: 24, speed: 0.95, reach: 3.0, windup: 0.8, cd: 2.1, aggro: 7.5, r: 0.8, push: 0.15, heavy: true, slam: true,
                   boss: true, wave: { every: 3, r: 4.4, dmg: 17 }, respawn: 600, legendary: true, glow: V },
  sylvaine: { name: 'Lady Sylvaine, the Vampire Queen', scale: 5, hp: 1400, dmg: 28, speed: 1.1, reach: 4.6, windup: 0.85, cd: 2.2, aggro: 10, r: 1.6, push: 0.15, heavy: true,
              boss: true, wave: { every: 3, r: 6.2, dmg: 22 }, respawn: 900, legendary: true, glow: V, minRar: 3 },
});
Object.assign(XP, { prismshard: 32, neonwisp: 30, crystalgolem: 60, mirrorduelist: 70, prismcolossus: 280, sylvaine: 600 });
SPAWNS.alfheim = [
  { id: 'shard_a0', role: 'prismshard', pos: [-3.2, -1.4] },
  { id: 'shard_a1', role: 'prismshard', pos: [3.6, 0.2] },
  { id: 'wisp_a0', role: 'neonwisp', pos: [-4.2, 4.6] },
  { id: 'wisp_a1', role: 'neonwisp', pos: [6.8, 6.0] },
  { id: 'golem_a0', role: 'crystalgolem', pos: [6.4, -2.0] },
  { id: 'duelist_a0', role: 'mirrorduelist', pos: [1.8, 5.8] },
  { id: 'wisp_anight', role: 'neonwisp', pos: [-1.6, 6.8], night: true },
  { id: 'colossus', role: 'prismcolossus', pos: [7.8, 4.0] },
];
SPAWNS.prismvault = [
  { id: 'shard_v0', role: 'prismshard', pos: [-3.4, 2.4] },
  { id: 'shard_v1', role: 'prismshard', pos: [3.4, 2.0] },
  { id: 'wisp_v0', role: 'neonwisp', pos: [-5.0, 5.0] },
  { id: 'duelist_v0', role: 'mirrorduelist', pos: [-4.0, -1.8] },
  { id: 'duelist_v1', role: 'mirrorduelist', pos: [4.0, -2.0] },
  { id: 'sylvaine', role: 'sylvaine', pos: [0.0, -5.0] },
];
Object.assign(REALM, { alfheim: 'embassy', prismvault: 'embassy' });   // Alfheim's merit is the Realm Embassies'

// ------------------------------------------------------------------ glow: always-on gloom-and-glow pools
if (GLOW_TABLES) {
  Object.assign(GLOW_TABLES.ALWAYS, { alfheim: true, prismvault: true });
  Object.assign(GLOW_TABLES.LAMP_R, { orb_lantern: 2.4 });
  GLOW_TABLES.POOLS.alfheim = [[-11.0, 2.6, 'violet', V], [10.4, 2.4, 'violet', V], [0.0, -7.4, 'light', V], [0.0, -4.2, 'cold', COLD],
    [-8.6, 4.4, 'violet', V], [7.8, 4.6, 'violet', V], [0.0, 1.0, 'light', V], [5.2, 5.6, 'red', RED],
    [-6.4, 6.0, 'bloom', 'violet'], [3.0, -2.6, 'bloom', 'coldfire'], [-9.6, -1.6, 'bloom', 'violet']];
  GLOW_TABLES.POOLS.prismvault = [[0.0, 7.2, 'violet', V], [0.0, -6.4, 'light', V], [-6.0, -3.6, 'violet', V], [6.0, -3.6, 'violet', V],
    [-2.4, 5.6, 'cold', COLD], [2.4, 5.6, 'cold', COLD], [0.0, -8.8, 'red', RED], [-7.4, 0.4, 'violet', V], [7.4, 0.4, 'violet', V]];
}

// ------------------------------------------------------------------ the story quest + talk (placeholder script until
// the Hearthmoor Story bot's alfheim.md lands; lines kept here so they swap in one place)
QUESTS.alfheim = {
  title: 'The Thief of Light',
  giver: 'Warden Aelindra Starwell',
  story: true,
  steps: { 1: 'Something is drinking Lumenvale\'s light. Find the Prism Vault door, east of the glade past the Prism Colossus.',
           2: (S) => ((S.flags || {}).alf_sylvaine
             ? 'Lady Sylvaine is defeated. Tell Warden Aelindra in Lumenvale.'
             : 'Lady Sylvaine, the vampire queen, sits in the Prism Vault drinking the realm\'s magic. Defeat her.'),
           3: 'The light is back in Lumenvale\'s lanterns. Warden Aelindra has put your name in the elves\' songs.' },
};
const flags = (S) => (S.flags = S.flags || {});
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
Object.assign(TALK, {
  aelindra(S) {
    const A = ((S.flags || {}).alliance || {}).alfheim, q = (S.quests || {}).alfheim || 0, F = S.flags || {};
    if (!A) return {
      pages: ['A Midgard face, through a gate that has been frozen for a season. I am Aelindra Starwell, warden of Lumenvale.',
              'Our light is thinning. The orb lanterns dim, the lumen trees drop their leaf-lights, and something below the glade is drinking it all.',
              'Vanaheim blames us for runes we never burned. So before I ask anything of you: what are you to Alfheim?'],
      choice: { id: 'alliance_alfheim', options: [
        { label: 'A friend. I\'ll help bring your light back.', pick: (G) => { ally(G.S).alfheim = 'befriend'; G.toast('Alfheim: befriended', 2.2); G.factions.add('embassy', 20, 'alfheim');
            return { pages: ['Then Lumenvale is yours to walk. The Prism Vault lies east, past the crystals. Lady Sylvaine has woken there, and she is hungry.',
                             '(Alfheim is your friend now. Its gate will stay open to you.)'], then: (G2) => { if (!(G2.S.quests || {}).alfheim) G2.setQuest('alfheim', 1); } }; } },
        { label: 'Alfheim will bow to Hearthmoor.', pick: (G) => { ally(G.S).alfheim = 'conquer'; G.toast('Alfheim: conquered', 2.2);
            return { pages: ['...Bold, for someone standing in our glade. Very well. Clear the vault and we will talk about who bows.',
                             '(Alfheim stands against you now. The elves will remember.)'], then: (G2) => { if (!(G2.S.quests || {}).alfheim) G2.setQuest('alfheim', 1); } }; } },
        { label: 'I\'m only passing through.', cancel: true, pick: () => ({ pages: ['Then pass softly. The shards in the glade cut anyone.'] }) },
      ] },
    };
    if (q === 2 && F.alf_sylvaine) return {
      pages: ['The lanterns are bright again. I felt it the moment she fell: the light came home all at once.',
              A === 'befriend' ? 'Lumenvale will sing your name. Take this, and the elves\' thanks.' : 'You kept your word, Midgarder. Take your due. Alfheim pays its debts, even to conquerors.'],
      then: (G) => { G.S.gold = (G.S.gold || 0) + 60; G.toast('+60 gold', 1.8); G.factions.add('embassy', 60, 'sylvaine'); G.setQuest('alfheim', 3); },
    };
    if (!q) return { pages: ['The Prism Vault is east, past the crystals. Mind the Colossus at its door.'], then: (G) => G.setQuest('alfheim', 1) };
    if (q < 3) return { pages: [A === 'befriend' ? 'The vault door is east of the glade. Sylvaine drinks magic: when her violet ring blooms, get clear, or your spells will sputter.'
                                                 : 'The vault is east. Go, conqueror.'] };
    return { pages: [A === 'befriend' ? 'Friend of Lumenvale! The light-fish are fat and happy again.' : 'Conqueror. Lumenvale keeps its word to you.'] };
  },
  thalion(S) {
    const F = S.flags || {};
    return { pages: F.alf_sylvaine
      ? ['The glade is quieter now. Still shards about, but they don\'t sing that hungry note any more.']
      : ['Shards dart at anything that moves. The wisps keep their distance and throw light; close in on them fast.',
         'And the Duelists: hit one and it may step out of its own reflection behind you. Turn around.'] };
  },
  nyssa(S) {
    return { pages: ['Every orb lantern holds a little light-fish. They sulk when the realm goes dim, so I sing to them.',
                     (S.flags || {}).alf_sylvaine ? 'Listen! They\'re humming again.' : 'Lately they only blink. Something below is drinking them.'] };
  },
  elfkid() { return { pages: ['Are you from Midgard? Is it true your lanterns use FIRE? Real fire?', 'Thalion says I can\'t go past the crystals. I went past one. Don\'t tell.'] }; },
});
if (MARKER_HOOKS) MARKER_HOOKS.push((id, S) => {
  const q = (S.quests || {}).alfheim || 0, F = S.flags || {};
  if (id === 'aelindra' && !q) return 'quest_mark';
  if (id === 'aelindra' && q === 2 && F.alf_sylvaine) return 'quest_turnin';
  return undefined;
});

// ------------------------------------------------------------------ the module
export class Alfheim {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.t = 0; this.told = {}; }
  open() {
    const G = this.G, F = G.S.flags || {};
    return !!((G.qs && G.qs.has('alfheim')) || F.alf_key || (F.alliance || {}).alfheim || (G.factions && G.factions.rank('gate') >= 3));
  }
  attach(ctx, id) {
    this.ctx = ctx; this.area = id; this.t = 0;
    this.prefetchBifrost();
    if (id === 'bifrost') this.wireGate(ctx);
    if (id === 'prismvault') {
      const S = this.G.S; if (((S.quests || {}).alfheim || 0) === 1) this.G.setQuest('alfheim', 2);
      flags(S).alf_vault = 1;
    }
    if (id === 'alfheim') flags(this.G.S).alf_seen = 1;
  }
  detach() { this.ctx = null; this.area = null; }
  // the Crossing's spawn in front of Alfheim's arch (the built bifrost scene predates this branch): patch the cached scene
  prefetchBifrost() {
    const G = this.G, put = (sc) => { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_alfheim) gm.spawns.from_alfheim = BF_ARCH.spawn.slice(); };
    if (G.scenes && G.scenes.bifrost) { put(G.scenes.bifrost); return; }
    if (this.area !== 'alfheim' || this.fetching) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  // Bifrost: Alfheim's arch swaps its frozen seal for an open violet swirl and becomes a portal (idempotent: scenes are cached)
  wireGate(ctx) {
    const gm = ctx.scene.game; if (!gm || !this.open()) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'alfheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'alfheim')) gm.portals.push({ fx: 'gate_alfheim', to: 'alfheim', spawn: 'from_bifrost', rect: BF_ARCH.rect.slice(), label: 'Alfheim\'s gate' });
    (gm.spawns = gm.spawns || {}).from_alfheim = gm.spawns.from_alfheim || BF_ARCH.spawn.slice();
    const f = ctx.fx && ctx.fx.gate_alfheim, meta = ctx.gamefx && ctx.gamefx.meta && ctx.gamefx.meta.effects;
    const want = meta && meta.rift_vortex_violet ? 'rift_vortex_violet' : 'rift_vortex';   // violet once bifrost is rebuilt with portal_alfheim
    if (f && f.name !== want && ctx.gamefx) { ctx.gamefx.remove(f); ctx.fx.gate_alfheim = ctx.gamefx.spawn(want, f.x, f.y, f.z, { duration: Infinity }); }
  }
  update(dt) {
    const ctx = this.ctx, C = this.G.combat; if (!ctx || !C || (this.area !== 'alfheim' && this.area !== 'prismvault')) return;
    this.t += dt;
    for (const e of C.enemies || []) if (!e.alf) this.hook(e);
  }
  hook(e) {
    e.alf = true;
    const role = e.a.role;
    if (role === 'mirrorduelist') this.hookDuelist(e);
    if (role === 'sylvaine') this.hookSylvaine(e);
  }
  // a Mirror Duelist: a hit may make it step out of its reflection behind you (4 s cooldown)
  hookDuelist(e) {
    const self = this;
    e.mods = { ...(e.mods || {}), hurt(en, dmg) {
      const ctx = self.ctx, C = self.G.combat; if (!ctx || en.hp - dmg <= 0 || self.t < (en.blinkT || 0) || Math.random() > 0.35) return dmg;
      en.blinkT = self.t + 4;
      const p = ctx.player, a = en.a, FV = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }, fv = FV[p.facing] || [0, 1];
      if (ctx.effects) ctx.effects.spawn('prism_pop', a.x, a.y + 0.6, a.z + 0.05);
      C.shove(a, p.x - fv[0] * 1.3 - a.x, p.z - fv[1] * 1.3 - a.z, Math.hypot(p.x - fv[0] * 1.3 - a.x, p.z - fv[1] * 1.3 - a.z));
      if (ctx.effects) ctx.effects.spawn('prism_pop', a.x, a.y + 0.6, a.z + 0.05);
      if (!self.told.blink) { self.told.blink = 1; self.G.toast('The Mirror Duelist steps out of its reflection behind you!', 2); }
      return dmg * 0.5;   // half the blow lands on the reflection
    } };
  }
  // Lady Sylvaine: drain nova on every third swing (spells + charms sputter), prism bolts at range, two Duelists at half HP
  hookSylvaine(e) {
    const self = this, D = e.D;
    e.tick = (en, dt, frozen) => {
      const ctx = self.ctx, C = self.G.combat; if (!ctx || frozen || C.peace) return;
      const a = en.a, p = ctx.player, d = Math.hypot(p.x - a.x, p.z - a.z);
      // the drain nova lands with her wave strike
      if (en.state === 'attack' && en.waveNow && en.fired && en.novaAt !== en.swings) {
        en.novaAt = en.swings;
        if (ctx.effects) ctx.effects.spawn('drain_nova', a.x, a.y + 0.04, a.z);
        if (self.G.glow) self.G.glow.pool(a.x, a.z, V, 1.6);
        if (d <= D.wave.r + 0.8) {
          C.cd.spell = Math.max(C.cd.spell || 0, 4); C.cd.charm = Math.max(C.cd.charm || 0, 4);
          en.hp = Math.min(D.hp, en.hp + Math.round(D.hp * 0.02));
          if (!self.told.drain) { self.told.drain = 1; self.G.toast('Lady Sylvaine drinks your magic! Spells sputter for a few seconds.', 2.6); }
        }
      }
      // prism bolts when you keep your distance
      en.boltCd = (en.boltCd ?? 2) - dt;
      if ((en.state === 'chase' || en.state === 'idle') && en.boltCd <= 0 && d > D.reach + 1.2 && d < 13 && Math.abs(p.y - a.y) < 1.5) {
        en.boltCd = 3.2;
        const k = D.scale || 1, from = [a.x, a.y + 0.6 * k, a.z + 0.05], L = d || 1, reach = Math.min(14, L + 2.5);
        const tx = a.x + (p.x - a.x) / L * reach, tz = a.z + (p.z - a.z) / L * reach;
        const f = ctx.effects && ctx.effects.spawn('prism_bolt', from[0], from[1], from[2], { to: [tx, ctx.heightAt(tx, tz), tz] });
        if (f) C.projs.push({ f, owner: 'enemy', dmg: 14, r: 0.6, src: a });
      }
      // at half health: two Mirror Duelists step out of her mirrors
      if (!en.called && en.hp <= D.hp * 0.5) {
        en.called = true;
        for (const [i, ox] of [[0, -3.2], [1, 3.2]]) {
          const x = a.x + ox, z = a.z + 2.4;
          C.spawnEnemy({ id: `syl_mirror_${i}`, role: 'mirrorduelist', pos: [x, z], once: true, noLoot: true }, true);
        }
        self.G.toast('Lady Sylvaine calls her Mirror Duelists!', 2.4);
      }
    };
    e.onKill = () => {
      const S = self.G.S; flags(S).alf_sylvaine = (flags(S).alf_sylvaine || 0) + 1;
      if (((S.quests || {}).alfheim || 0) < 2) self.G.setQuest('alfheim', 2);
      self.G.refreshMarkers && self.G.refreshMarkers();
      setTimeout(() => self.G.toast('The light pours back up toward Lumenvale. Tell Warden Aelindra.', 3), 3400);
    };
  }
  qa() {
    const c = this.ctx, C = this.G.combat;
    const gm = c ? c.scene.game || {} : {};
    const syl = (C.enemies || []).find((e) => e.a.role === 'sylvaine');
    return { area: this.area, open: this.open(), portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch || g.realm),
             gateFx: c && c.fx && c.fx.gate_alfheim ? c.fx.gate_alfheim.name : null,
             quest: (this.G.S.quests || {}).alfheim || 0, alliance: ((this.G.S.flags || {}).alliance || {}).alfheim || null,
             sylvaine: syl ? { hp: syl.hp, max: syl.D.hp, scale: syl.D.scale, r: syl.D.r, state: syl.state, hooked: !!syl.tick, called: !!syl.called } : null };
  }
}
