// Hearthmoor 6.7: the Forge Quarter (story/forge_alchemy.md sections 2-3). Ravenhold's east district gate opens once The
// Cold Altar is done. Tova Anvilsong tempers gear +1..+10 (cap by rarity, 7% per + on the item's own mods, never breaks:
// a failed try keeps gold + gems, eats iron / steel and adds heat). Orri Flintcog rerolls one stat with rune-stones
// (random 1 stone, chosen 2; keep new or old; per-item limit by rarity). Gloom and glow: red forge mouths, neon-blue
// quench tanks (forge pack gamefx + point lights). Also: Sparks in the Street (the riot, 5), sockets via Orri (4), smelt /
// scrap-for-iron (1.1, 2.5), The First Temper (6), cold-blue sparks on +7 / +10 weapons (2.3). Nettle + the Still: later.
import { RARITY, scrap as lootScrap } from './loot.js';
export const SOCKET = { cap: [0, 1, 2, 3, 3], punch: [{ gold: 50, iron: 2 }, { gold: 120, steel: 1 }, { gold: 250, steel: 2, gems: ['rift_shard'] }] };
export const SCRAP_IRON = [1, 2, 3, 4, 6];
export const SMELT = { iron: 4, gem: 'frost_core', steel: 2 };
export const RIOT = [
  { id: 'rioter1', flag: 'rt_gunnar', right: 0, name: 'Gunnar Saltbeck, fishmonger', role: 'fisher', pos: [-1.6, 1.6], shout: "Dwarf tongs at our altar! Who else in Ravenhold owns dwarf tongs? Eh?", calm: "...Frost on forge tools. Never warmed. Huh. No smith leaves cold tongs. I'm going home." },
  { id: 'rioter2', flag: 'rt_mags', right: 1, name: 'Old Mags, temple candle-seller', role: 'lamplighter', pos: [1.4, 1.2], shout: 'Someone walked into my temple and straight back out to these forges!', calm: 'The prints walked away from the forges? Into the court? Then who was it? ...I need a candle.' },
  { id: 'rioter3', flag: 'rt_pell', right: 2, name: 'Pell, dock porter', role: 'corsair', pos: [0.2, -0.6], shout: "And who snuffs a holy flame? A smith, with a smith's snuffer, that's who!", calm: "No maker's mark? Everything up here's marked. Twice. Right. Sorry, Tova. Sorry, everyone." },
];
const CLUE_OPTS = ['Show the frosted tongs.', 'Describe the frost footprints.', 'Show the snuffer with no mark.'];
export const calmed = (S) => RIOT.filter((r) => (S.flags || {})[r.flag]).length;
// the rioters are spec actors (areas/src/forge.json); game.js skipActor hides each one unless it is still shouting
export const rioterOn = (S, id) => { const r = RIOT.find((x) => x.id === id); return !!r && forgeOpen(S) && !riotDone(S) && !(S.flags || {})[r.flag]; };
export const riotDone = (S) => ((S.quests || {}).forge_riot || 0) === 3;
const BELLOWS = [-5.6, -8.4];
export const UP = {
  per: 0.07, cap: [2, 4, 6, 8, 10], heatBonus: 0.15, sure: 3,
  cost: [null,
    { gold: 15, iron: 2, steel: 0, gems: [], chance: 1 }, { gold: 25, iron: 3, steel: 0, gems: [], chance: 1 },
    { gold: 40, iron: 4, steel: 0, gems: [], chance: 1 }, { gold: 60, iron: 5, steel: 1, gems: [], chance: 1 },
    { gold: 85, iron: 6, steel: 1, gems: [], chance: 1 }, { gold: 120, iron: 6, steel: 2, gems: [], chance: 0.9 },
    { gold: 160, iron: 8, steel: 2, gems: ['frost_core'], chance: 0.8 }, { gold: 210, iron: 8, steel: 3, gems: ['frost_core'], chance: 0.7 },
    { gold: 270, iron: 10, steel: 4, gems: ['golem_core'], chance: 0.6 }, { gold: 350, iron: 12, steel: 5, gems: ['golem_core', 'rift_shard'], chance: 0.5 }],
};
export const REROLL = {
  max: [1, 2, 3, 4, 5], cost: { random: 1, chosen: 2 },
  pool: {
    weapon: { meleeMul: 0.04, spellMul: 0.04, summonMul: 0.05, crit: 0.01, critDmg: 0.05, drain: 0.01 },
    armor: { hpAdd: 8, guardMul: -0.015, stAdd: 4, regen: 0.3, healMul: 0.04 },
    trinket: { crit: 0.01, stAdd: 4, summonMul: 0.05, spellCd: 0.015, stRegen: 0.04, healMul: 0.04 },
  },
};
export const upK = (it) => 1 + UP.per * ((it && it.up) || 0);
const TOVA_OK = [null, "There. Warm iron remembers being loved. It'll hold an edge for you now.", 'Plus two. A good honest piece. Common steel, uncommon care.',
  "Plus three. Hear that ring? That's the iron saying thank you.", "Cold-steel in the fold now. Feel the weight shift? It's listening to your hand.",
  "Plus five. Halfway to a legend. Don't tell it. It'll get proud.", "Plus six. Steady hands, both of us. I'll have a cup of tea after that one.",
  'Into the quench! ...There. Cold fire took. Blue at the edges, warm at the heart.', "Plus eight. My grandmother made one plus-eight in her whole life. Now I've made two. Hm. Three.",
  "Plus nine. The golem core sang the whole time. I'm going to dream about that sound.", "Plus ten. Hearthforged. I'm not crying. It's the steam. Take it before I change my mind."];
const TOVA_FAIL = ["Hiss. The quench wasn't ready. My fault. The iron's fine, and it's warmer for trying.",
  "Not this time. Your gold's back in your purse. The iron and steel went into the lesson.", "Close! It wants to be better. Give it another go. It'll take next time, I promise."];
export const forgeOpen = (S) => ((S.quests || {}).altar || 0) === 3;
const GATE_EXIT = { rect: [10.3, -12.4, 12.7, -10.2], to: 'forge', spawn: 'from_harbor', label: 'the Forge Quarter lane' };
// why the next + can't happen (null = it can)
export function temperLock(S, it) {
  if (!it) return 'nothing equipped there';
  const up = it.up || 0, cap = UP.cap[it.rar];
  if (up >= cap) return `at cap (${RARITY[it.rar].name} +${cap})`;
  const c = UP.cost[up + 1], inv = S.inv || {}, gems = S.gems || {};
  if ((S.gold || 0) < c.gold) return `need ${c.gold - (S.gold || 0)} more gold`;
  if ((inv.ironbit || 0) < c.iron) return `need ${c.iron - (inv.ironbit || 0)} more iron bits`;
  if ((inv.coldsteel || 0) < c.steel) return `need ${c.steel - (inv.coldsteel || 0)} more cold-steel`;
  for (const g of c.gems) if (!(gems[g] > 0)) return `need a ${g.replace('_', ' ')}`;
  return null;
}
// one temper try; rnd injectable for tests. Returns { ok, up, line, quench }
export function temper(S, it, rnd = Math.random) {
  const why = temperLock(S, it); if (why) return { ok: false, blocked: why };
  const to = (it.up || 0) + 1, c = UP.cost[to], heat = it.heat || 0;
  const chance = heat >= UP.sure ? 1 : Math.min(1, c.chance + heat * UP.heatBonus);
  S.inv.ironbit -= c.iron; if (c.steel) S.inv.coldsteel -= c.steel;
  for (const k of ['ironbit', 'coldsteel']) if (!S.inv[k]) delete S.inv[k];
  if (rnd() < chance) {
    S.gold -= c.gold; for (const g of c.gems) S.gems[g] -= 1;
    it.up = to; it.heat = 0;
    return { ok: true, up: to, line: TOVA_OK[to], quench: to >= 7 };
  }
  it.heat = heat + 1;   // gold + gems refunded (never taken), iron + steel spent
  return { ok: false, up: to - 1, line: it.heat >= UP.sure - 1 ? "She's hot as she'll get. Next try takes, I'd stake my anvil on it." : TOVA_FAIL[Math.floor(rnd() * 3)], quench: to >= 7 };
}
const itemK = (it) => RARITY[it.rar].mul * (1 + ((it.lv || 1) - 1) * 0.06);
// a reroll: replace `stat` (or a random one) with a fresh stat from the slot pool. Returns { old, neu } mods for the keep choice.
export function rerollLock(S, it, chosen) {
  if (!it) return 'nothing equipped there';
  if ((it.rr || 0) >= REROLL.max[it.rar]) return "That piece has heard all the runes it can take. Any more and it'd start talking back.";
  if (((S.inv || {}).runestone || 0) < REROLL.cost[chosen ? 'chosen' : 'random']) return "No stone, no rune. Nettle sells them. She'll tell you she found them. She didn't.";
  return null;
}
export function reroll(S, it, stat = null, rnd = Math.random) {
  const chosen = !!stat, why = rerollLock(S, it, chosen); if (why) return { blocked: why };
  const keys = Object.keys(it.mods), out = stat && keys.includes(stat) ? stat : keys[Math.floor(rnd() * keys.length)];
  const pool = REROLL.pool[it.slot], free = Object.keys(pool).filter((k) => !keys.includes(k));
  const nk = free[Math.floor(rnd() * free.length)], raw = pool[nk] * itemK(it) * (0.8 + 0.4 * rnd());
  const v = ['hpAdd', 'stAdd'].includes(nk) ? Math.max(1, Math.round(raw)) : +raw.toFixed(3);
  S.inv.runestone -= REROLL.cost[chosen ? 'chosen' : 'random']; if (!S.inv.runestone) delete S.inv.runestone;
  it.rr = (it.rr || 0) + 1;
  const neu = { ...it.mods }; delete neu[out]; neu[nk] = v;
  return { old: { ...it.mods }, neu, out, nk };
}
export function punchLock(S, it) {
  if (!it) return 'nothing equipped there';
  if (it.rar === 0) return "Commons don't take sockets.";
  const n = (it.gems || []).length; if (n >= SOCKET.cap[it.rar]) return "Any more holes and it's a colander. Rarer steel takes more sockets. That's just the rule of iron.";
  if ((S.flags || {}).orri_socket) return null;   // the riot's thank-you: the first punch is free
  const c = SOCKET.punch[n], inv = S.inv || {};
  if ((S.gold || 0) < c.gold) return `need ${c.gold - (S.gold || 0)} more gold`;
  if ((inv.ironbit || 0) < (c.iron || 0)) return 'need more iron bits';
  if ((inv.coldsteel || 0) < (c.steel || 0)) return 'need more cold-steel';
  for (const g of c.gems || []) if (!((S.gems || {})[g] > 0)) return `need a ${g.replace('_', ' ')}`;
  return null;
}
export function punch(S, it) {
  const why = punchLock(S, it); if (why) return { blocked: why };
  const n = (it.gems || []).length, c = SOCKET.punch[n], F = S.flags || (S.flags = {});
  if (F.orri_socket) delete F.orri_socket;
  else { S.gold -= c.gold; if (c.iron) S.inv.ironbit -= c.iron; if (c.steel) S.inv.coldsteel -= c.steel; for (const g of c.gems || []) S.gems[g] -= 1; }
  for (const k of ['ironbit', 'coldsteel']) if (S.inv[k] <= 0) delete S.inv[k];
  it.gems = [...(it.gems || []), null];
  return { ok: true, n: n + 1 };
}
// scrap a bag piece at the forge: the usual scrap gold plus iron bits by rarity
export function forgeScrap(S, i) {
  const it = (S.bag || [])[i]; if (!it) return null;
  const iron = SCRAP_IRON[it.rar], gold = lootScrap(S, i);
  S.inv.ironbit = (S.inv.ironbit || 0) + iron; return { gold, iron, name: it.name };
}
export function smelt(S) {
  if ((S.inv.ironbit || 0) < SMELT.iron || !((S.gems || {})[SMELT.gem] > 0)) return false;
  S.inv.ironbit -= SMELT.iron; if (!S.inv.ironbit) delete S.inv.ironbit; S.gems[SMELT.gem] -= 1;
  S.inv.coldsteel = (S.inv.coldsteel || 0) + SMELT.steel; return true;
}
const SLOT_NAME = { weapon: 'weapon', armor: 'armour', trinket: 'trinket' };
export class Forge {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.fx = []; this.lights = []; }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    const gm = ctx.scene.game || (ctx.scene.game = {}), S = this.G.S;
    if (area === 'ravenhold' && forgeOpen(S)) {
      gm.sealed = (gm.sealed || []).filter((g) => g.id !== 'forge');
      gm.exits = (gm.exits || []).filter((e) => e.to !== 'forge').concat([{ ...GATE_EXIT }]);
    }
    if (area !== 'forge') return;
    const still = !!this.G.qaStill;
    this.swingT = -1; this.moteT = 0;
    if (forgeOpen(S) && !riotDone(S)) {   // 5: Sparks in the Street: the crowd is still at the gate
      if (!S.quests.forge_riot) setTimeout(() => this.G.setQuest && this.G.setQuest('forge_riot', 1), 0);
    }
    for (const f of gm.forgefx || []) {
      const [x, , z] = f.pos, y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[f.name]) this.fx.push(ctx.gamefx.spawn(f.name, x, y, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (ctx.addGlow && /fire|pool/.test(f.name)) {
        const red = /red|fire/.test(f.name);
        this.lights.push(ctx.addGlow(x, y, z, { color: red ? '#ff5a4a' : '#2ab4ff', intensity: red ? 7 : 5, range: red ? 5 : 3.6, lift: 0.6, fadeIn: still ? 0.01 : 0.8 }));
      }
    }
  }
  detach() { for (const f of this.fx) if (f) f.dur = f.t + 0.2; for (const l of this.lights) if (l) l.kill = true; this.fx = []; this.lights = []; this.ctx = null; }
  zones() { const gm = this.ctx && this.area === 'forge' ? this.ctx.scene.game : null; return gm ? (gm.forgefx || []).filter((f) => /pool/.test(f.name)).map((f) => ({ x: f.pos[0], z: f.pos[2], r: 2.0, src: 'forge' })) : []; }
  burst(name, x, z) { const ctx = this.ctx; if (ctx && ctx.gamefx && ctx.gamefx.meta.effects[name]) ctx.gamefx.spawn(name, x, ctx.heightAt(x, z), z + 0.1); }
  // ---- the riot (5.3): each rioter wants the right temple clue; a wrong one just reopens the choice
  rioter(id) {
    const G = this.G, S = G.S, r = RIOT.find((x) => x.id === id), F = (S.flags = S.flags || {});
    if (!r || F[r.flag]) return { pages: ['(They grumble, but they are heading home.)'] };
    const opts = CLUE_OPTS.map((label, k) => ({ label, pick: () => (k === r.right ? this.calm(r) : { pages: ["That's not what I asked, is it? Don't you change the subject on me."], then: () => G.openDialogue(this.ctx.npc(id) || { id, name: r.name }, this.rioter(id)) }) }));
    if (S.cls === 'seer' && !F.rt_seer) opts.push({ label: '(Read the frame aloud.)', pick: () => { F.rt_seer = 1; return this.calm(r, "Your runes say it's a setup. You say it with a straight face. ...Fine. Fine!"); } });
    const first = S.cls === 'cinderknight' && id === 'rioter1' && !F.rt_ck ? (F.rt_ck = 1, ['And YOU. Fire-blood. Bet you know all about forges, eh?']) : [];
    return { pages: [...first, r.shout], choice: { id: `riot_${id}`, options: opts } };
  }
  calm(r, line) {
    const G = this.G, S = G.S; S.flags[r.flag] = 1;
    const a = this.ctx && this.ctx.npc(r.id); if (a) { a.behavior = 'wander'; a.home = [r.pos[0], 4.2]; a.radius = 0.6; setTimeout(() => { if (this.ctx && this.ctx.npc(r.id)) this.ctx.removeNpc(a); }, 2500); }
    const done = calmed(S) >= 3;
    if (done) { G.setQuest('forge_riot', 2); G.drawLog && G.drawLog(); }
    G.save && G.save();
    return { pages: [line || r.calm, ...(done ? ["(Sergeant Holt pushes through.) About time someone used words. Clear off, all of you. Gate's open."] : [])] };
  }
  // ---- Tova: services menu + The First Temper (6)
  tova() {
    const G = this.G, S = G.S, q = S.quests || {};
    if (!riotDone(S)) return { pages: [(q.forge_riot || 0) >= 2 ? "I've had that hammer up so long my arm's asleep. Thank you. Go see Orri. He's taking it hard." : "Not now, love. Not with a crowd at my door and a hammer in my hand. Talk them down if you can."] };
    if (!q.temper) return { pages: ['Tova Anvilsong. Six generations of us on this cliff. The Hilde in the Plaza? No relation. Thank goodness.',
      "You've got gear. Gear wants to be better. Scrap one thing you've outgrown, and we'll feed the bits to the fire."], then: (G2) => G2.setQuest('temper', 1) };
    return { pages: ['The forge is hot. What are we making better today?'],
      choice: { id: 'tova', options: [
        { label: 'Temper (upgrade gear)', pick: () => this.temperMenu() },
        { label: `Smelt: ${SMELT.iron} iron bits + 1 frost core → ${SMELT.steel} cold-steel`, pick: () => this.doSmelt() },
        { label: 'Scrap gear for gold + iron bits', pick: () => this.scrapMenu() },
        { label: 'Buy iron bits / cold-steel', pick: () => { setTimeout(() => G.shopUI.show('forge'), 0); return null; } },
        { label: 'Not yet', cancel: true, pick: () => null }] } };
  }
  freeTemper() { const S = this.G.S, F = S.flags || {}; return (S.quests || {}).temper === 1 && F.tp_scrap && F.tp_bellows && !F.tp_up; }
  temperMenu() {
    const S = this.G.S, gear = S.gear || {}, free = this.freeTemper();
    const opt = (slot) => {
      const it = gear[slot], to = ((it && it.up) || 0) + 1, c = UP.cost[Math.min(10, to)];
      const why = free && it && !it.up ? null : temperLock(S, it);
      const cost = free && it && !it.up ? 'free (your first)' : `${c.gold} g · ${c.iron} iron${c.steel ? ` · ${c.steel} steel` : ''}${c.gems.length ? ` · ${c.gems.join(', ').replace(/_/g, ' ')}` : ''}`;
      return { label: it ? (why ? `${SLOT_NAME[slot]}: +${it.up || 0} ${it.name} (${why})` : `${SLOT_NAME[slot]}: +${to - 1} → +${to} · ${cost}`) : `${SLOT_NAME[slot]}: (empty)`, pick: () => this.doTemper(slot) };
    };
    return { pages: [free ? 'Lay it on the anvil. This first one is on the house.' : 'Which piece?'], choice: { id: 'tova_temper', options: [opt('weapon'), opt('armor'), opt('trinket'), { label: 'Not yet', cancel: true, pick: () => null }] } };
  }
  scrapMenu() {
    const S = this.G.S, bag = S.bag || [];
    if (!bag.length) return { pages: ['Your bag is empty of gear. Bring me something you\'ve outgrown.'] };
    const opts = bag.slice(0, 5).map((it, i) => ({ label: `${it.name} (${RARITY[it.rar].name}): +${RARITY[it.rar].scrap} g, +${SCRAP_IRON[it.rar]} iron`, pick: () => this.doScrap(i) }));
    return { pages: ['Scrap here for gold and iron bits.'], choice: { id: 'tova_scrap', options: [...opts, { label: 'Not yet', cancel: true, pick: () => null }] } };
  }
  doScrap(i) {
    const G = this.G, S = G.S, r = forgeScrap(S, i); if (!r) return null;
    const F = (S.flags = S.flags || {}); if (S.quests.temper === 1) F.tp_scrap = 1;
    G.audio && G.audio.sfx('pickup'); G.drawLog && G.drawLog(); G.save && G.save();
    return { pages: [`(${r.name} goes into the scrap bin.) +${r.gold} gold, +${r.iron} iron bits.${S.quests.temper === 1 && !F.tp_bellows ? ' Now work the bellows by the forge till she roars.' : ''}`] };
  }
  doSmelt() {
    const G = this.G, ok = smelt(G.S); if (ok) { G.save && G.save(); G.audio && G.audio.sfx('craft'); }
    return { pages: [ok ? '(Hiss. The iron goes in grey and comes out blue at the edges.) Two cold-steel ingots.' : `I need ${SMELT.iron} iron bits and a frost core for a smelt.`] };
  }
  // bellows by the left forge (First Temper): three pumps
  near(ctx = this.ctx) { if (!ctx || this.area !== 'forge') return false; const p = ctx.player; return Math.hypot(p.x - BELLOWS[0], p.z - BELLOWS[1]) < 1.4; }
  nearThing(ctx) { return this.near(ctx); }
  interact() {
    if (!this.near()) return false;
    const G = this.G, S = G.S, F = (S.flags = S.flags || {});
    if (S.quests.temper !== 1 || !F.tp_scrap || F.tp_bellows) { G.toast && G.toast('The forge bellows. Tova keeps the fire fed.', 2.0); return true; }
    F.tp_pumps = (F.tp_pumps || 0) + 1; this.burst('forge_sparks', -4.2, -8.6);
    if (F.tp_pumps >= 3) { F.tp_bellows = 1; G.toast && G.toast('(The fire roars. Tova whistles, impressed.)', 2.4); } else G.toast && G.toast('(Whoomph. The forge mouth flares red.)', 1.6);
    G.drawLog && G.drawLog(); G.save && G.save(); return true;
  }
  // cold-blue sparks: a +7..+9 weapon throws a few on each swing, a +10 trails more and sheds a slow mote at rest
  update(dt) {
    const ctx = this.ctx, w = ((this.G.S && this.G.S.gear) || {}).weapon; if (!ctx || !w || (w.up || 0) < 7 || !ctx.burst) return;
    const p = ctx.player, sw = p.act && p.act.name === 'attack';
    if (sw && !this.swung) { const n = w.up >= 10 ? 5 : 2; for (let k = 0; k < n; k++) ctx.burst('wet_glint_cool', p.x + (k - n / 2) * 0.15, (p.y || 0) + 0.7, p.z + 0.1); this.sparks = (this.sparks || 0) + n; }
    this.swung = sw;
    if (w.up >= 10 && (this.moteT -= dt) <= 0) { this.moteT = 1.4; ctx.burst('wet_glint_cool', p.x, (p.y || 0) + 1.0, p.z); this.sparks = (this.sparks || 0) + 1; }
  }
  doTemper(slot, rnd) {
    const G = this.G, S = G.S, it = (S.gear || {})[slot];
    if (this.freeTemper() && it && !it.up) {
      it.up = 1; it.heat = 0; S.flags.tp_up = 1; G.setQuest('temper', 2);
      const a0 = (this.ctx.scene.game.anvils || [])[0]; if (a0) this.burst('forge_sparks', a0.pos[0], a0.pos[1]);
      G.save && G.save(); return { pages: ["There. Your first temper. Now go show Orri. He gets grumpy if he's not the second to know."] };
    }
    const r = temper(S, it, rnd);
    if (r.blocked) return { pages: [/gold/.test(r.blocked) ? "Short on gold. The forge eats coal and coal costs coin. I'll keep the fire warm for you." : /iron|steel/.test(r.blocked) ? "Short on iron. Scrap something you've outgrown, and I'll sort the bits." : /cap/.test(r.blocked) ? "That's as far as this piece goes. A Common can't carry a Legendary's fire. Bring me something rarer." : `Not today: ${r.blocked}.`] };
    const a = (this.ctx.scene.game.anvils || [])[0];
    if (a) { this.burst('forge_sparks', a.pos[0], a.pos[1]); if (r.quench) { this.burst('forge_sparks', -1.8, -8.0); for (let k = 0; k < 4; k++) this.ctx.burst && this.ctx.burst('wet_glint_cool', -1.8 + (k - 1.5) * 0.3, this.ctx.heightAt(-1.8, -8.0) + 0.8, -7.6); } }
    G.audio && G.audio.sfx(r.ok ? 'quest' : 'blip'); G.save && G.save();
    return { pages: [r.line] };
  }
  orri() {
    const G = this.G, S = G.S, q = S.quests || {}, gear = S.gear || {};
    if (q.forge_riot === 2) return { pages: ['Those tongs had my mark on the grip. Two crossed cogs. My grandfather\'s mark.',
      'They went missing the night my quench tank froze solid. In midsummer. Ice an inch thick on cold fire.',
      "Cold fire doesn't freeze. I've told the watch twice. They wrote it down and looked at me funny.",
      ...(S.cls === 'seer' ? ['(The frost he describes hums in your runes, the same echo you felt on the tongs.)'] : []),
      'Someone with very cold hands wanted Ravenhold to hate dwarves. You stopped them. I owe you a socket.'],
      then: (G2) => { G2.setQuest('forge_riot', 3); G2.factions && G2.factions.add('hearth', 60, 'riot'); const F = (G2.S.flags = G2.S.flags || {}); F.forge_open = 1; F.orri_socket = 1; G2.save(); } };
    if (!riotDone(S)) return { pages: ['(Orri sweeps glass from his smashed shutters and does not look up.)'] };
    if (q.temper === 2) return { pages: ["Plus one. Clean work. Here's a rune-stone for luck. Every smith needs one they never use."],
      then: (G2) => { G2.give('ironbit', 6); G2.give('runestone', 1); G2.setQuest('temper', 3); } };
    const opt = (slot, chosen) => {
      const it = gear[slot], why = rerollLock(S, it, chosen);
      return { label: it ? `${chosen ? 'Pick a stat' : 'Random stat'} · ${SLOT_NAME[slot]}: ${it.name} (${why ? 'no' : `${REROLL.max[it.rar] - (it.rr || 0)} left`}, ${REROLL.cost[chosen ? 'chosen' : 'random']} stone${chosen ? 's' : ''})` : `${SLOT_NAME[slot]}: (empty)`,
        pick: () => (chosen && it && !why ? this.statMenu(slot) : this.doReroll(slot)) };
    };
    const pk = (slot) => { const it = gear[slot], why = punchLock(S, it), n = ((it && it.gems) || []).length, c = SOCKET.punch[Math.min(2, n)];
      return { label: it ? `Socket · ${SLOT_NAME[slot]}: ${it.name} (${why ? why.split('.')[0] : (S.flags || {}).orri_socket ? 'free' : `${c.gold} g${c.iron ? ` · ${c.iron} iron` : ''}${c.steel ? ` · ${c.steel} steel` : ''}${c.gems ? ' · rift shard' : ''}`})` : `${SLOT_NAME[slot]}: (empty)`, pick: () => this.doPunch(slot) }; };
    return { pages: ["Rune bench. Pick a stat you don't love and let the stone decide. Or pay double and decide yourself."],
      choice: { id: 'orri', options: [
        { label: 'Reroll a stat (1 rune-stone, random)', pick: () => ({ pages: ['Which piece?'], choice: { id: 'orri_rr', options: [opt('weapon', false), opt('armor', false), opt('trinket', false), { label: 'Not now', cancel: true, pick: () => null }] } }) },
        { label: 'Reroll a stat you pick (2 rune-stones)', pick: () => ({ pages: ['Which piece?'], choice: { id: 'orri_rr2', options: [opt('weapon', true), opt('armor', true), opt('trinket', true), { label: 'Not now', cancel: true, pick: () => null }] } }) },
        { label: 'Punch a socket', pick: () => ({ pages: ['Which piece gets a hole?'], choice: { id: 'orri_sock', options: [pk('weapon'), pk('armor'), pk('trinket'), { label: 'Not now', cancel: true, pick: () => null }] } }) },
        { label: 'Buy rune-stones', pick: () => { setTimeout(() => G.shopUI.show('runebench'), 0); return null; } },
        { label: 'Not now', cancel: true, pick: () => null }] } };
  }
  statMenu(slot) {
    const it = this.G.S.gear[slot];
    return { pages: ['Which stat goes? The others stay locked.'], choice: { id: 'orri_stat', options: [...Object.keys(it.mods).map((k) => ({ label: `${k} ${+(+it.mods[k]).toFixed(3)}`, pick: () => this.doReroll(slot, k) })), { label: 'Not now', cancel: true, pick: () => null }] } };
  }
  doPunch(slot) {
    const G = this.G, it = (G.S.gear || {})[slot], r = punch(G.S, it);
    if (r.blocked) return { pages: [r.blocked] };
    G.audio && G.audio.sfx('craft'); G.save && G.save();
    return { pages: ['(Clink. Clink. A neat round socket, rimmed with copper.) There. Room for something shiny.'] };
  }
  doReroll(slot, stat, rnd) {
    const G = this.G, it = (G.S.gear || {})[slot], r = reroll(G.S, it, stat, rnd);
    if (r.blocked) return { pages: [r.blocked] };
    const fmt = (m) => Object.entries(m).map(([k, v]) => `${k} ${v}`).join(', ');
    G.save && G.save();
    return { pages: ['(Orri presses the rune-stone to the steel. It glows violet, then goes dark.)', `Old: ${fmt(r.old)}. New: ${fmt(r.neu)}.`],
      choice: { id: 'orri_keep', options: [
        { label: 'Keep new', pick: () => { it.mods = r.neu; G.save && G.save(); return { pages: ["Ha! The stone likes you. Don't let it go to your head. Or do. It's your head."] }; } },
        { label: 'Keep old', cancel: true, pick: () => ({ pages: ['Hm. Keep the old one, I would. Stones have moods.'] }) }] } };
  }
}
