// Hearthmoor 6.8: the Glowfrog Still (story/forge_alchemy.md 7). Bryony Glasswort brews at Old Gurgle, a cauldron of neon
// cold-fire brew on the Forge Quarter's lower yard (art/alchemy: cauldron + table + shelf + herb rack kit, bubbling brew /
// fire / pool gamefx). 2-3 ingredients, order free (RECIPES key = sorted ids). A miss uses nothing and earns a hint.
// Potions are bag items brew_<id>: tap one in the bag to drink. Timed brews: one at a time (S.brew = {id, left}), folded
// into progress.mods() by brewMods. Ingredients: garden herbs (each bloom harvest gives one), moonpetals, red toadstools
// (Bryony: 3 a day), Bloop's lily pad (1 glow-dew a day), spring water (fill a vial at a hidden spring).
// The Cold Cauldron intro (7.6): find Bloop at Tova's quench, clear+light the vent under Old Gurgle, gather caps+petals,
// then brew Glowcap. Until then the Still is cold. Bloop (role pet_bloop, art/cold_cauldron/) sits in the quench tank while you look for him, then on his lily pad.
export const BREWS = {
  glowcap: { name: 'Glowcap Draught', col: '#ff4a3a', heal: 120, yield: 2, about: 'Heals 120 HP. Twice a tonic, half the taste.' },
  coldfire: { name: 'Cold-fire Tonic', col: '#5ab4f0', t: 90, mods: { spellMul: 0.15, spellCd: 0.10 }, about: '90 s: spells +15%, spell cooldowns 10% shorter. Glows neon blue.' },
  hush: { name: 'Violet Hush', col: '#a45cf0', t: 120, mods: { guardMul: -0.10, hpAdd: 20 }, about: '120 s: +20 HP, guarded hits do 10% less.' },
  ember: { name: 'Ember Cap Brew', col: '#e0302a', t: 60, mods: { meleeMul: 0.15, critDmg: 0.20 }, about: '60 s: melee +15%, crits hit 20% harder.' },
  frogleap: { name: 'Frogleap Fizz', col: '#5af0c8', t: 90, yield: 2, mods: { stAdd: 25, stRegen: 0.30, rollSpeed: 0.10 }, about: '90 s: +25 stamina, stamina refills 30% faster, dodge 10% farther. Ribbit.' },
  moonmilk: { name: 'Moonmilk', col: '#fff8e6', t: 180, heal: 30, yield: 2, mods: { regen: 2, healMul: 0.25 }, about: 'Heals 30. 180 s: 2 HP/s resting, healing +25%. Tastes like a nap.' },
  wisp: { name: 'Wisplight Elixir', col: '#7c8cff', t: 120, mods: { summonMul: 0.20, summonLife: 4 }, about: '120 s: summons +20% and last 4 s longer. Tiny wisps orbit the bottle.' },
  luckytoad: { name: 'Lucky Toad', col: '#f2c24a', t: 120, mods: { crit: 0.06 }, about: '120 s: +6% crit. The bottle has a frog face. It winks.' },
  riftbrew: { name: 'Riftbrew', col: '#c03cc8', t: 120, mods: { spellMul: 0.20, crit: 0.03, riftMarkMul: 0.10 }, about: '120 s: spells +20%, +3% crit, +10% Rift Marks. Fizzes violet and red.' },
  breadbroth: { name: 'Warm Bread Broth', col: '#f2a63a', heal: 60, t: 60, secret: true, mods: { stRegen: 0.20 }, about: 'Heals 60. 60 s: stamina refills 20% faster. Marla would be appalled. Then ask for the recipe.' },
};
export const RECIPES = {
  'dewdrop+redcap': 'glowcap', 'moonpetal+moonpetal+tea': 'moonmilk', 'coldpetal+dewdrop': 'coldfire',
  'glowbell+moonpetal': 'hush', 'glowcap+redcap': 'ember', 'dewdrop+springwater': 'frogleap',
  'coldpetal+glowbell+moonpetal': 'wisp', 'glowcap+moon_opal+redcap': 'luckytoad',
  'coldpetal+rift_shard+springwater': 'riftbrew', 'dewdrop+loaf+moonpetal': 'breadbroth',
};
export const recipeKey = (ids) => ids.slice().sort().join('+');
export const INGREDIENTS = ['redcap', 'dewdrop', 'moonpetal', 'tea', 'coldpetal', 'glowbell', 'glowcap', 'springwater', 'loaf', 'moon_opal', 'rift_shard'];
const GEM_ING = { moon_opal: 1, rift_shard: 1 };
const FOUND = {
  glowcap: "Red and dew! That's the first thing my gran taught me. Smells like a forest floor after rain.",
  moonmilk: "Moonmilk. Drink it by a fire, then don't make plans. It's not a potion. It's a nap in a bottle.",
  coldfire: "Look at it glow! Cold fire in a bottle. Don't drink it too fast, your teeth will hum.",
  hush: 'Violet Hush. Very calming. Monsters hit you and you just sort of... shrug. Gently.',
  ember: "Two reds! That's a spicy one. Hit things with your eyebrows raised. You'll understand.",
  frogleap: "Bloop! Bloop, they made your drink! (Bloop does a little hop. That's a frog's standing ovation.)",
  wisp: "Three lights in one bottle. Your summons will feel it. They'll glow a little smug.",
  luckytoad: "A Lucky Toad! I've only seen one before, at a fair. It winked at me. I married into that family.",
  riftbrew: "A rift shard in a cauldron? Bold. The Guild would approve. My eyebrows would not, but here we are.",
  breadbroth: "...Did you put bread in my cauldron? It worked?! Don't tell Marla. Actually do. I want her face.",
};
const HINTS = {
  glowcap: 'Close-ish. Old Gurgle wants something red, I think. Red and wet.', ember: "It's sulking. Try two reds. It loves a strong opinion.",
  coldfire: "Fizzle. Something cold, and something Bloop makes. That's all I'll say.", hush: 'A violet bell wants a pale flower beside it. Bells get lonely.',
  frogleap: "Bloop's dew and something from a hidden spring. Fizzy plus fizzy.", wisp: 'Three lights: a pale petal, a violet bell and a cold one.',
  luckytoad: 'Two reds and a moon opal. Gamblers swear by it.', riftbrew: 'Spring water, a cold petal and something from a rift. Bold.',
  moonmilk: "Two moonpetals and a tin of Wren's tea. That's a nap.",
};
const NIGHT = (t) => t > 0.8 || t < 0.25;
const OLD_GURGLE = [-6.0, -3.4], PAD = [-9.2, -2.4], QUENCH = [-1.8, -8.0], BLOOP_TANK = [-1.8, -7.3], REACH = 1.6, VENT_REACH = 2.6;
const flags = (S) => (S.flags = S.flags || {});
const cauldronDone = (S) => ((S.quests || {}).cauldron || 0) === 3;
export const stillLit = (S) => !!flags(S).cc_vent || cauldronDone(S) || !!(S.recipes || {}).glowcap;
export function brewMods(S, m) {
  const b = S && S.brew, B = b && b.left > 0 && BREWS[b.id]; if (!B || !B.mods) return m;
  for (const [k, v] of Object.entries(B.mods)) { if (k === 'guardMul') m.guardMul = Math.max(0.4, m.guardMul + v); else m[k] = (m[k] || 0) + v; }
  return m;
}
const have = (S, x) => (GEM_ING[x] ? (S.gems || {})[x] || 0 : (S.inv || {})[x] || 0);
// one stir: the ingredients are used only on a match
export function brew(G, ids) {
  const S = G.S, id = RECIPES[recipeKey(ids)];
  const need = {}; for (const x of ids) need[x] = (need[x] || 0) + 1;
  if (Object.entries(need).some(([x, n]) => have(S, x) < n)) return { short: true };
  if (!id) return { fizzle: true };
  for (const x of ids) { if (GEM_ING[x]) S.gems[x] -= 1; else G.take(x, 1); }
  const B = BREWS[id], n = B.yield || 1, isNew = !(S.recipes = S.recipes || {})[id];
  G.give(`brew_${id}`, n); S.recipes[id] = 1;
  if (isNew && B.secret && !(S.found || {}).brew_breadbroth) {
    S.found = S.found || {}; S.found.brew_breadbroth = 1; G.factions && G.factions.onSecret();
    G.toast && G.toast('A secret recipe! The Gnome Council will want to hear about this one.', 2.8);
  }
  // Cold Cauldron stage 2 → 3: first Glowcap Draught proves Old Gurgle still works
  if (id === 'glowcap' && (S.quests || {}).cauldron === 2) {
    G.setQuest('cauldron', 3); S.gold = (S.gold || 0) + 30;
    G.toast && G.toast("There it is! Glowing like a lighthouse. You're a natural. +30 gold.", 2.8);
  }
  return { id, n, isNew };
}
export function drink(G, id) {
  const S = G.S, B = BREWS[id], C = G.combat, key = `brew_${id}`;
  if (!B || !(S.inv[key] > 0) || G.downed) return false;
  G.take(key, 1);
  if (B.heal && C && C.ctx) C.heal(B.heal, true);
  if (B.t) { const was = S.brew && S.brew.left > 0 && BREWS[S.brew.id]; if (was && S.brew.id !== id) G.toast && G.toast(`The ${was.name} fades as the ${B.name} takes hold.`, 2.4); S.brew = { id, left: B.t }; }
  const ctx = C && C.ctx;
  if (ctx) { if (ctx.effects) ctx.effects.spawn('sparkle_burst', ctx.player.x, ctx.player.y, ctx.player.z + 0.05); if (ctx.addGlow) { const l = ctx.addGlow(ctx.player.x, ctx.player.y, ctx.player.z, { color: B.col, intensity: 6, range: 3, lift: 0.8 }); setTimeout(() => { if (l) l.kill = true; }, 1000); } }
  G.audio && G.audio.sfx('pickup'); return true;
}
export class Alchemy {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.fx = []; this.lights = []; this.pot = []; this.moteT = 0; }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area; this.pot = [];
    if (area !== 'forge') return;
    const S = this.G.S, R = S.recipes || {}, q = (S.quests = S.quests || {});
    // migration: saves that already got free recipes skip the intro
    if (R.glowcap && R.moonmilk && !q.cauldron) { q.cauldron = 3; const F = flags(S); F.cc_vent = 1; F.cc_bloop = 1; F.cc_coal = 1; }
    this.relight(); this.syncBloop();
    // cast beside Old Gurgle lights the cleared vent (same reach as Hollows braziers)
    if (this.G.hollows && !this._castHook) {
      this._castHook = 1;
      const me = this, c0 = this.G.hollows.onCast.bind(this.G.hollows);
      this.G.hollows.onCast = (...a) => { const r = c0(...a); const p = me.ctx && me.ctx.player; if (p) me.spellAt(p.x, p.z); return r; };
    }
  }
  // Bloop (Cold Cauldron): in Tova's quench tank while you look for him (stage 1, not found yet), on his lily pad once found (and for saves
  // that already finished the quest); gone before Bryony asks. A runtime actor on the pet_bloop role (a build without the sheet just skips him).
  syncBloop() {
    const ctx = this.ctx; if (!ctx || this.area !== 'forge' || !ctx.addNpc) return;
    const S = this.G.S, q = (S.quests || {}).cauldron || 0, F = flags(S);
    const at = q === 1 && !F.cc_bloop ? BLOOP_TANK : (F.cc_bloop || q >= 2) ? PAD : null;
    const cur = ctx.npc('bloop');
    if (cur && at && Math.abs(cur.x - at[0]) < 0.05 && Math.abs(cur.z - at[1]) < 0.05) return;
    if (cur) ctx.removeNpc(cur);
    if (!at || !(ctx.actors && ctx.actors.meta.roles.pet_bloop)) return;
    const a = ctx.addNpc({ id: 'bloop', role: 'pet_bloop', name: 'Bloop', pos: at.slice(), facing: 'down', behavior: 'idle', talkable: true }); a.facing = 'down';
  }
  relight() {
    for (const f of this.fx) if (f) f.dur = f.t + 0.2; for (const l of this.lights) if (l) l.kill = true; this.fx = []; this.lights = [];
    const ctx = this.ctx; if (!ctx || this.area !== 'forge') return;
    if (!stillLit(this.G.S)) return;   // Cold Cauldron: vent blocked, no blue glow yet
    const [x, z] = OLD_GURGLE, y = ctx.heightAt(x, z), gf = ctx.gamefx, has = (n) => gf && gf.meta.effects[n];
    for (const [n, dz, yy] of [['cauldron_pool_blue', 0.05, 0], ['cauldron_fire', 0.3, 0], ['cauldron_brew_blue', 0.02, 0]]) if (has(n)) this.fx.push(gf.spawn(n, x, y + yy, z + dz, { duration: Infinity }));
    if (ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: '#2ab4ff', intensity: 6, range: 4.5, lift: 1.0, fadeIn: 0.5 }));
  }
  detach() { for (const f of this.fx) if (f) f.dur = f.t + 0.2; for (const l of this.lights) if (l) l.kill = true; this.fx = []; this.lights = []; this.ctx = null; }
  zones() { return this.ctx && this.area === 'forge' && stillLit(this.G.S) ? [{ x: OLD_GURGLE[0], z: OLD_GURGLE[1], r: 2.2, src: 'still' }] : []; }
  // timed brew countdown + a few motes in its colour drifting up from the hero
  update(dt) {
    const S = this.G.S, b = S && S.brew; if (!b || !(b.left > 0)) return;
    b.left -= dt; if (b.left <= 0) { const B = BREWS[b.id]; S.brew = null; this.G.toast && this.G.toast(`The ${B ? B.name : 'brew'} wears off.`, 1.8); return; }
    const ctx = this.G.combat && this.G.combat.ctx;
    if (ctx && ctx.burst && (this.moteT -= dt) <= 0) { this.moteT = 1.2; ctx.burst('wet_glint_cool', ctx.player.x, (ctx.player.y || 0) + 0.9, ctx.player.z); }
  }
  near(pt, ctx = this.ctx, reach = REACH) { if (!ctx) return false; const p = ctx.player; return Math.hypot(p.x - pt[0], p.z - pt[1]) < reach; }
  springNear(ctx = this.ctx) { const sp = ctx && ctx.scene.game && ctx.scene.game.spring; return sp && sp.pos && this.near(sp.pos, ctx); }
  seekingBloop(S = this.G.S) { return (S.quests || {}).cauldron === 1 && !flags(S).cc_bloop; }
  nearThing(ctx) {
    const S = this.G.S;
    if (this.area === 'forge' && (this.near(OLD_GURGLE, ctx) || this.near(PAD, ctx) || (this.seekingBloop(S) && this.near(QUENCH, ctx)))) return true;
    return !!this.springNear(ctx) && ((S.inv || {}).vial > 0);
  }
  // Cold Cauldron: cast beside Old Gurgle after clearing coal lights the vent (Hollows brazier reach 2.6 m)
  spellAt(x, z) {
    const S = this.G.S, F = flags(S);
    if (this.area !== 'forge' || (S.quests || {}).cauldron !== 1 || !F.cc_bloop || !F.cc_coal || F.cc_vent) return;
    if (Math.hypot(x - OLD_GURGLE[0], z - OLD_GURGLE[1]) > VENT_REACH) return;
    F.cc_vent = 1; this.relight();
    this.G.toast && this.G.toast("(A red flare, then Old Gurgle's blue glow returns. The Still breathes again.)", 2.8);
    this.G.audio && this.G.audio.sfx('spell'); this.G.drawLog && this.G.drawLog(); this.G.refreshMarkers && this.G.refreshMarkers(); this.G.save && this.G.save();
  }
  interact() {
    const G = this.G, S = G.S, F = flags(S), q = S.quests || {};
    if (this.springNear() && (S.inv.vial || 0) > 0) { G.take('vial', 1); G.give('springwater', 1); return true; }
    if (this.area !== 'forge') return false;
    // find Bloop in Tova's quench tank
    if (this.seekingBloop(S) && this.near(QUENCH)) {
      F.cc_bloop = 1;
      G.openDialogue({ id: 'smith', name: 'Tova Anvilsong' }, {
        pages: ['(A blue frog surfaces in the cold fire, blinks at you, and climbs your sleeve.)',
          "So that's what kept humming in my tank. Take it, take it. It was judging my work."],
        then: (G2) => { this.syncBloop(); G2.toast && G2.toast('Bloop hops onto your shoulder, spots pulsing violet.', 2.4); G2.drawLog && G2.drawLog(); G2.refreshMarkers && G2.refreshMarkers(); G2.save && G2.save(); },
      });
      return true;
    }
    if (this.near(PAD)) {
      if (!stillLit(S) || !F.cc_bloop) { G.toast && G.toast("Bloop's lily pad. Empty without the frog.", 2.0); return true; }
      if (S.dew === (S.day || 0)) { G.toast && G.toast("Bloop's lily pad. Tomorrow's dew is still forming.", 2.0); return true; }
      S.dew = S.day || 0; G.give('dewdrop', 1); G.save && G.save(); return true;
    }
    if (this.near(OLD_GURGLE)) {
      // clear coal from the vent (Cold Cauldron)
      if (q.cauldron === 1 && F.cc_bloop && !F.cc_coal) {
        F.cc_coal = 1; G.toast && G.toast('(You shovel the coal cart off the vent. Ash and a faint blue breath.)', 2.6);
        G.drawLog && G.drawLog(); G.save && G.save(); return true;
      }
      if (!stillLit(S)) { G.toast && G.toast('Old Gurgle is cold and grey. The vent under it is choked.', 2.2); return true; }
      const a = this.ctx.npc('alchemist'); G.openDialogue(a || { id: 'alchemist', name: 'Old Gurgle' }, this.brewMenu()); return true;
    }
    return false;
  }
  // ---- Bloop (TALK.bloop)
  bloop() {
    const S = this.G.S, F = flags(S);
    if (!F.cc_bloop && (S.quests || {}).cauldron === 1) return { pages: ['(A blue frog surfaces in the cold fire, blinks at you, and climbs your sleeve.)'] };
    return { pages: ["(Bloop blinks. Bloop's spots pulse violet. Bloop says nothing, wisely.)"] };
  }
  // ---- Bryony (TALK.alchemist)
  bryony() {
    const G = this.G, S = G.S, R = (S.recipes = S.recipes || {}), q = S.quests || {}, F = flags(S);
    if (q.forge_riot !== 3) return { pages: ['(Bryony is crouched behind Old Gurgle with a ladle raised, waiting for the shouting to stop.)'] };
    // offer The Cold Cauldron
    if (!q.cauldron) return {
      pages: ["Oh! A customer! Or a hero. Or both? I'm Bryony. This is the Glowfrog Still. It's normally much glowier.",
        "The riot tipped a coal cart over my vent. Old Gurgle's gone cold, and Bloop ran off. He hates shouting.",
        'Find my frog, light my fire, and bring me one red toadstool and two moonpetals. I\'ll teach you to brew. Deal?'],
      then: (G2) => { G2.setQuest('cauldron', 1); this.syncBloop(); },
    };
    // stage 1: turn-in when ready, else reminder
    if (q.cauldron === 1) {
      const ready = F.cc_bloop && F.cc_vent && (S.inv.redcap || 0) >= 1 && (S.inv.moonpetal || 0) >= 2;
      if (ready) return {
        pages: ["Bloop! And you lit the vent! And you brought... perfect. Watch. Red cap, dew, stir. Your turn.",
          "Here's dew, vials, and a tin of tea. Moonmilk is yours: two petals and the tea. Glowcap wants a red cap and dew."],
        then: (G2) => {
          G2.take('redcap', 1); G2.take('moonpetal', 2);
          G2.give('dewdrop', 1); G2.give('vial', 3); G2.give('tea', 1);
          R.moonmilk = 1; G2.setQuest('cauldron', 2);
          G2.toast && G2.toast('Moonmilk added to your recipe book.', 2.4);
        },
      };
      return { pages: ['Bloop likes warm and blue. So does everyone, really. Try the forges.'] };
    }
    // stage 2+: brew menu (Glowcap still to discover if stage 2)
    return { pages: [NIGHT(this.ctx ? this.ctx.clock.t : 0.5) ? "The frogs are up! Night's when the Still really shines. Literally. Mind your eyes."
      : q.cauldron === 2 ? 'Old Gurgle is warm again. Brew a Glowcap Draught: red toadstool and glow-dew. Prove it.'
        : 'Everything glows if you stir it long enough. Except soup. Soup resists.'],
      choice: { id: 'bryony', options: [
        { label: 'Brew something.', pick: () => this.brewMenu() },
        { label: 'Brew a known recipe again.', pick: () => this.recipesMenu() },
        { label: 'Buy ingredients.', pick: () => { setTimeout(() => G.shopUI.show('still'), 0); return null; } },
        { label: 'Not now.', cancel: true, pick: () => null }] } };
  }
  brewMenu() {
    const S = this.G.S, pot = this.pot;
    if (!stillLit(S)) return { pages: ['Old Gurgle is cold. Clear the vent and light it before brewing.'] };
    const left = INGREDIENTS.filter((x) => have(S, x) - pot.filter((p) => p === x).length > 0);
    const name = (x) => (this.G.ITEMS && this.G.ITEMS[x] ? this.G.ITEMS[x].name : x.replace('_', ' '));
    const opts = [];
    if (pot.length < 3) for (const x of left.slice(0, 5)) opts.push({ label: `Add ${name(x)} (${have(S, x) - pot.filter((p) => p === x).length})`, pick: () => { pot.push(x); return this.brewMenu(); } });
    if (pot.length >= 2) opts.push({ label: 'Stir!', pick: () => this.stir() });
    if (pot.length) opts.push({ label: 'Take the last one out', pick: () => { pot.pop(); return this.brewMenu(); } });
    opts.push({ label: 'Leave it', cancel: true, pick: () => { pot.length = 0; return null; } });
    return { pages: [pot.length ? `Old Gurgle holds: ${pot.map(name).join(' + ')}.` : 'Old Gurgle bubbles, empty and blue. Add 2 or 3 things.'], choice: { id: 'still_brew', options: opts } };
  }
  stir(ids = this.pot.slice()) {
    const G = this.G, S = G.S, r = brew(G, ids); this.pot.length = 0;
    const [x, z] = OLD_GURGLE, gf = this.ctx && this.ctx.gamefx;
    if (r.short) return { pages: ["You're short on something for that one."] };
    if (r.fizzle) {
      const miss = Object.keys(HINTS).filter((k) => !(S.recipes || {})[k] && !(S.hints || {})[k]);
      const h = miss[0]; if (h) (S.hints = S.hints || {})[h] = 1;
      G.save && G.save(); return { pages: ['(Old Gurgle fizzles grey. Nothing is used.)', h ? HINTS[h] : 'Hm. Not that. Try another mix.'] };
    }
    if (gf && gf.meta.effects.brew_puff_blue) gf.spawn('brew_puff_blue', x, this.ctx.heightAt(x, z) + 0.9, z + 0.1);
    G.audio && G.audio.sfx('quest'); G.save && G.save();
    const B = BREWS[r.id];
    if (r.isNew) G.toast && G.toast(`NEW RECIPE: ${B.name}`, 2.6);
    return { pages: [r.isNew ? FOUND[r.id] : r.n > 1 ? `${B.name} ×${r.n}. Old Gurgle was feeling generous.` : `${B.name}. Bottled.`] };
  }
  recipesMenu() {
    const S = this.G.S, known = Object.keys(S.recipes || {});
    const keyOf = (id) => Object.keys(RECIPES).find((k) => RECIPES[k] === id).split('+');
    const opts = known.slice(0, 6).map((id) => ({ label: `${BREWS[id].name}: ${BREWS[id].about}`, pick: () => this.stir(keyOf(id)) }));
    return { pages: ['Your recipe book.'], choice: { id: 'still_book', options: [...opts, { label: 'Not now.', cancel: true, pick: () => null }] } };
  }
  qa() { return { brew: this.G.S.brew, recipes: Object.keys(this.G.S.recipes || {}), fx: this.fx.length, lit: stillLit(this.G.S), q: (this.G.S.quests || {}).cauldron || 0 }; }
}
