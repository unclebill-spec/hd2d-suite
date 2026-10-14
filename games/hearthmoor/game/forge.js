// Hearthmoor 6.7: the Forge Quarter (story/forge_alchemy.md sections 2-3). Ravenhold's east district gate opens once The
// Cold Altar is done. Tova Anvilsong tempers gear +1..+10 (cap by rarity, 7% per + on the item's own mods, never breaks:
// a failed try keeps gold + gems, eats iron / steel and adds heat). Orri Flintcog rerolls one stat with rune-stones
// (random 1 stone, chosen 2; keep new or old; per-item limit by rarity). Gloom and glow: red forge mouths, neon-blue
// quench tanks (forge pack gamefx + point lights). Not built yet: the riot beat, sockets (Orri / Nettle), The First Temper.
import { RARITY } from './loot.js';
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
  // dialogue entries for Tova and Orri (data.js TALK.smith / TALK.runesmith)
  tova() {
    const G = this.G, S = G.S, gear = S.gear || {};
    const opt = (slot) => {
      const it = gear[slot], why = temperLock(S, it), to = ((it && it.up) || 0) + 1, c = UP.cost[Math.min(10, to)];
      const label = it ? (why ? `${SLOT_NAME[slot]}: +${it.up || 0} ${it.name} (${why})` : `${SLOT_NAME[slot]}: +${to - 1} → +${to} · ${c.gold} g · ${c.iron} iron${c.steel ? ` · ${c.steel} steel` : ''}${c.gems.length ? ` · ${c.gems.join(', ').replace(/_/g, ' ')}` : ''}`) : `${SLOT_NAME[slot]}: (empty)`;
      return { label, pick: () => this.doTemper(slot) };
    };
    return { pages: ['The forge is hot. What are we making better today?'],
      choice: { id: 'tova', options: [opt('weapon'), opt('armor'), opt('trinket'), { label: 'Buy iron bits / cold-steel', pick: () => { setTimeout(() => G.shopUI.show('forge'), 0); return null; } }, { label: 'Not yet', cancel: true, pick: () => null }] } };
  }
  doTemper(slot, rnd) {
    const G = this.G, it = (G.S.gear || {})[slot], r = temper(G.S, it, rnd);
    if (r.blocked) return { pages: [/gold/.test(r.blocked) ? "Short on gold. The forge eats coal and coal costs coin. I'll keep the fire warm for you." : /iron|steel/.test(r.blocked) ? "Short on iron. Scrap something you've outgrown, and I'll sort the bits." : /cap/.test(r.blocked) ? "That's as far as this piece goes. A Common can't carry a Legendary's fire. Bring me something rarer." : `Not today: ${r.blocked}.`] };
    const a = (this.ctx.scene.game.anvils || [])[0];
    if (a) { this.burst('forge_sparks', a.pos[0], a.pos[1]); if (r.quench) this.burst('quench_steam', -1.8, -8.0); }
    G.audio && G.audio.sfx(r.ok ? 'quest' : 'blip'); G.save && G.save();
    return { pages: [r.line] };
  }
  orri() {
    const G = this.G, S = G.S, gear = S.gear || {};
    const opt = (slot) => {
      const it = gear[slot], why = rerollLock(S, it, false);
      return { label: it ? `${SLOT_NAME[slot]}: ${it.name} (${why ? 'no' : `${REROLL.max[it.rar] - (it.rr || 0)} left`})` : `${SLOT_NAME[slot]}: (empty)`, pick: () => this.doReroll(slot) };
    };
    return { pages: ["Rune bench. Pick a stat you don't love and let the stone decide. Or pay double and decide yourself."],
      choice: { id: 'orri', options: [opt('weapon'), opt('armor'), opt('trinket'), { label: 'Buy rune-stones', pick: () => { setTimeout(() => G.shopUI.show('runebench'), 0); return null; } }, { label: 'Not now', cancel: true, pick: () => null }] } };
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
