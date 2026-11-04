// game/vanaheim_c.js — Vanaheim Stage C village life (Hearthmoor Story 2026-10-30).
// Loaded once from game.js after vanaheim.js. Already live, so not redefined here:
// Growth school (gr_i / gr_iii, Vine Grasp, Moss Golem — Moss Ward gr_ii stays out),
// Bloomtide harvest + dance, items bloom_token / foresight_charm / mossheart_staff.
import { TALK, MARKER_HOOKS } from './data.js';
import { MERIT } from './factions.js';

// Filled by vanaheim.js once that module finishes (this file loads first, as its dependency).
export const LINK = { ctx: () => null };

const F_ = (S) => (S.flags || (S.flags = {}));
const A = (S) => ((S.flags || {}).alliance || {}).vanaheim;
const q = (S, id) => (S.quests || {})[id] || 0;
const mood = (S) => (((S.flags || {}).realm_mood || {}).vanaheim) || 0;
const emb = (S) => (S.ranks || {}).embassy || 0;

// Same night window as alfheim NIGHT. There is no G.night.
export const VH_NIGHT = (t) => typeof t === 'number' && (t > 0.8 || t < 0.25);
// Live bloom night: every 7th in-game day, and night. ?bloomnight forces it for QA.
export function realmBloomNight(S) {
  try { if (new URLSearchParams(location.search).has('bloomnight')) return true; } catch (e) { /* no location */ }
  const ctx = LINK.ctx();
  return (S.day || 0) % 7 === 0 && VH_NIGHT(ctx && ctx.clock && ctx.clock.t);
}
// The charm is a neck unique. combat.hurtPlayer reads it. One copy, used by Counted Stars and by giveForesight.
export function payForesight(G) {
  const S = G.S; S.bag = S.bag || [];
  const have = [...S.bag, ...Object.values(S.gear || {})].some((x) => x && x.unique === 'foresight_charm');
  if (have) return;
  S.bag.push({ uid: `fore${Date.now().toString(36)}`, slot: 'neck', name: 'Foresight Charm', rar: 2, rv: 2, lv: Math.max(1, S.lv || 1), unique: 'foresight_charm',
    mods: {}, gems: [], img: 'art/vanaheim/icons/foresight_charm.png', about: 'A star-shaped bead that blinks a moment before danger does. After a dodge, +5% crit chance for 60 s.' });
}

// Live growthLesson (gr_i, then gr_iii; no gr_ii) — warden '!' only, so the mark matches what he actually teaches.
function growthMark(S) {
  const f = F_(S);
  if (A(S) !== 'befriend' || q(S, 'vh_hex') !== 3) return false;
  if (!f.gr_i) return true;
  if (!f.gr_iii && (S.lv || 1) >= 10 && emb(S) >= 2) return true;
  return false;
}

// ---------------------------------------------------------------- Bloomtide riddles (harvest + dance stay in the live Liss talk)
export const BLOOM_RIDDLES = [
  { ask: 'I have a cap but no head, a stem but no flower. What am I?', right: 'A mushroom', wrong: ['A gnome', 'A bad hat'] },
  { ask: 'The more of me you take, the more you leave behind. What am I?', right: 'Footsteps', wrong: ['Beans', 'Second helpings'] },
  { ask: 'What runs but never walks, sings but never talks?', right: 'A spring', wrong: ['Tobble', 'Tobble, but louder'] },
];
export function bloomRiddle(G, i = 0) {
  const r = BLOOM_RIDDLES[i]; if (!r) return null;
  const opts = [r.right, ...r.wrong].sort(), done = (G2) => { const f = F_(G2.S); f.vh_bloom_games = { ...(f.vh_bloom_games || {}), riddle: 1 }; G2.factions.onRiddle(); };
  return { pages: [r.ask], choice: { id: `vh_riddle_${i}`, options: opts.map((o) => ({ label: o,
    pick: (G2) => (o === r.right ? (i < BLOOM_RIDDLES.length - 1 ? bloomRiddle(G2, i + 1) : (done(G2), { pages: ['Three for three! The judges stand on each other to applaud.'] }))
      : { pages: ['The gnomes gasp. Pibb faints, then gets up to see what happens next.'] }) })), cancel: true } };
}

function offerRiddle(pages) {
  return { pages, choice: { id: 'vh_bloom_riddle', options: [
    { label: 'Beat the riddle-gnomes', pick: (G) => bloomRiddle(G, 0) },
    { label: 'Later.', cancel: true, pick: () => null },
  ] } };
}

// ---------------------------------------------------------------- Mossheart Staff bench (item + quest text are already live)
const BENCH_IDLE = ['(A gnome workbench. Every drawer is labelled "NOT THIS ONE".)'];
function tobbleBench(S) {
  const i = S.inv || {}, s = q(S, 'vh_staff');
  if (A(S) !== 'befriend' || q(S, 'vh_tobble') !== 3) return { pages: BENCH_IDLE };
  if (!s && q(S, 'verdant') === 3) return { pages: ['That tine hums like a kettle with a secret. Bring it here with three fizzstones and I will make you something legendary. Probably.'],
    then: (G) => G.setQuest('vh_staff', 1) };
  if (s === 1 && i.greenheart_tine && (i.fizzstone || 0) >= 3) return { pages: ['(Tobble clamps the tine. Burrowmoss sings at it. The fizzstones melt into blue sap and climb the wood.)',
    'Tobble: "It is growing! It is growing at ME!"', '(A staff of living moss settles in your hands. Somewhere a large spore-shaped thing hums happily.)'],
    then: (G) => { G.take('greenheart_tine', 1); G.take('fizzstone', 3); G.give('mossheart_staff', 1); G.setQuest('vh_staff', 2); G.setQuest('vh_staff', 3); G.toast('Legendary: the Mossheart Staff', 3); G.save && G.save(); } };
  if (s === 1) return { pages: ['One Greenheart tine, three fizzstones. I would fetch them myself but I am busy. Inventing. Napping. Same thing.'] };
  return null;
}

// ---------------------------------------------------------------- side bits
export const STARS = [[-6.0, 3.6], [1.8, 4.2], [8.2, -3.4]];
// One toadstool. Mood < 0 withholds the count (the spots hide too). Repeats do not add.
export function readStar(S, i) {
  const f = F_(S);
  if (mood(S) < 0 || f.vh_stars_done) return f.vh_stars || 0;
  const seen = { ...(f.vh_stars_seen || {}) };
  if (!seen[i]) { seen[i] = 1; f.vh_stars_seen = seen; f.vh_stars = Object.keys(seen).length; }
  return f.vh_stars || 0;
}
function stargnome(S) {
  const f = F_(S), n = (f.vh_stars || 0);
  if (mood(S) < 0) return { pages: ['(The gnome astronomer turns his telescope away from you, very slowly, and very on purpose.)'] };
  if (n >= 3 && !f.vh_stars_done) return { pages: ['Two thousand and eleven! Two thousand and TWELVE! I can sleep. Take this. It sees a little ahead.'],
    then: (G) => { F_(G.S).vh_stars_done = 1; payForesight(G); G.factions.add('embassy', MERIT.errand, 'vh_stars'); G.toast && G.toast('Foresight Charm', 2.2); G.save && G.save(); } };
  if (f.vh_stars_done) return { pages: ['Two thousand and twelve stars. Thirteen if you count Pibb, who climbed up there to help.'] };
  return { pages: ['I have lost count of the stars. Climb my three toadstools at night and read them to me. Loudly.'] };
}
function capseller(S) {
  const f = F_(S), caps = (S.inv || {}).glowcap || 0;
  if (f.vh_morel === 2) return { pages: ['My best customer! Caps are two for one. For you, three for two. Do not tell the others.'] };
  if (f.vh_morel === 1 && caps >= 5) return { pages: ['Five glow-caps! Bright as a gnome who just had a good idea.'],
    then: (G) => { G.take('glowcap', 5); F_(G.S).vh_morel = 2; G.S.gold = (G.S.gold || 0) + 40; G.toast && G.toast('+40 gold', 1.8); G.drawBag && G.drawBag(); G.factions.add('embassy', MERIT.errand, 'vh_morel'); } };
  if (f.vh_morel === 1) return { pages: [`Five glow-caps, please. You have ${caps}. Counting is hard. I know.`] };
  return { pages: ['Caps! Two for one on fizz days. Every day is a fizz day.', 'Unless you could fetch me five glow-caps? The Rotwood edge is full of them.'],
    then: (G) => { F_(G.S).vh_morel = 1; } };
}
function riddlestump(S) {
  if (F_(S).vh_stump) return { pages: ['(The stump is asleep. It snores in riddles.)'] };
  return { pages: ['STUMP: "I stand all day, I never walk, I have a ring for every year. What am I?"'], choice: { id: 'vh_stump', options: [
    { label: 'A tree stump', pick: (G) => { F_(G.S).vh_stump = 1; G.factions.onRiddle(); return { pages: ['STUMP: "Rude. Correct. Pass."'] }; } },
    { label: 'A very old gnome', pick: () => ({ pages: ['STUMP: "Tempting. No."'] }) },
    { label: 'Leave', cancel: true, pick: () => ({ pages: ['STUMP: "Coward. Come back."'] }) }] } };
}

// ---------------------------------------------------------------- Prince Hollis (night only, on the village spring)
export const HOLLIS = { pos: [-1.2, 1.4], r: 1.1, night: true, flag: 'vh_hollis' };
function hollis(S) {
  if (F_(S).vh_hollis) return { pages: ['Hollis: "Still not cursed. Still a prince. Still fabulous."'] };
  return { pages: ['(A frog in a tiny silver crown climbs onto the spring rim at midnight.)', 'Hollis: "Are you here to break my curse?"'],
    choice: { id: 'vh_hollis', options: [
      { label: 'Yes! How?', pick: (G) => { F_(G.S).vh_hollis = 1; G.factions.onSecret(); return { pages: ['Hollis: "Ha! There is no curse. I just like the crown. Do not tell my mother."', '(He gives you a tiny bow, and a tiny wink.)'] }; } },
      { label: 'Is that crown real silver?', pick: (G) => { F_(G.S).vh_hollis = 1; G.factions.onSecret(); return { pages: ['Hollis: "Finally, someone with taste."'] }; } },
      { label: 'Leave', cancel: true, pick: () => ({ pages: ['Hollis: "Fine. I have other admirers. Mostly moths."'] }) }] } };
}

// ---------------------------------------------------------------- scenes, conquer, markers
export const ARRIVAL = ['(Bubbles rise from every pool. Somewhere a kettle whistles, then a gnome whistles back at it.)',
  'Pibb: "A big one! Wicker, a big one came through the vines!"', 'Wicker: "Don\'t stare. ...Are you staring? I\'m staring."'];
export const VEYRA_BLOOM = (S) => [`${F_(S).met_veyra ? 'Veyra' : 'A cold voice'}: "You pull my thorns, and they grow back in someone else's garden. Grief is a very good soil, hearth-walker."`,
  '(The blue bloom freezes solid and drops. It does not break.)'];
export const HUSHED = (S) => A(S) === 'conquer' && q(S, 'vh_tithe') === 3;
export const HUSHED_BARKS = ['...we don\'t riddle strangers anymore.', '(A gnome starts to whistle, sees you, and stops.)', 'The springs taste of ink now.'];
export function hushedBark(S) { return HUSHED_BARKS[(S.day || 0) % HUSHED_BARKS.length]; }

export const vhMarkerC = (S, id) => {
  const f = F_(S);
  if (id === 'warden' && growthMark(S)) return 'quest_mark';
  if (id === 'nymph_vh' && A(S) === 'befriend' && q(S, 'vh_bloom') === 1) { const b = f.vh_bloom_games || {}; return b.harvest && b.dance && b.riddle ? 'quest_turnin' : null; }
  if (id === 'nymph_vh' && A(S) === 'befriend' && realmBloomNight(S) && q(S, 'vh_bloom') !== 1) return 'quest_mark';
  if (id === 'tobble_bench' && q(S, 'vh_staff') === 1 && (S.inv || {}).greenheart_tine && ((S.inv || {}).fizzstone || 0) >= 3) return 'quest_turnin';
  if (id === 'capseller' && f.vh_morel === 1 && ((S.inv || {}).glowcap || 0) >= 5) return 'quest_turnin';
  if (id === 'stargnome' && mood(S) >= 0 && (f.vh_stars || 0) >= 3 && !f.vh_stars_done) return 'quest_turnin';
  return null;
};

export function vhMarkerHook(id, S) {
  const m = vhMarkerC(S, id);
  return m == null ? undefined : m;
}

let hooked = false;
// Called once while this module loads, then again at the bottom of vanaheim.js after that file's TALK assigns.
export function installStageC() {
  const prevNymph = TALK.nymph_vh;
  TALK.nymph_vh = (S) => {
    const f = F_(S), b = f.vh_bloom_games || {}, s = q(S, 'vh_bloom');
    if (A(S) === 'befriend' && s === 3 && (S.day || 0) !== f.vh_bloom_day && realmBloomNight(S)) return { pages: ['It is Bloomtide! Every seventh night the springs sing. Will you play?'],
      then: (G) => { F_(G.S).vh_bloom_games = {}; G.setQuest('vh_bloom', 1); } };
    if (A(S) === 'befriend' && s === 1 && b.harvest && b.dance && b.riddle) return { pages: ['You did all three! The springs are giggling. That is a technical term.'],
      then: (G) => { G.factions.add('embassy', MERIT.vh_bloom || 40, 'vh_bloom'); G.give('bloom_token', 1); F_(G.S).vh_bloom_day = G.S.day || 0; G.setQuest('vh_bloom', 3); G.save && G.save(); } };
    if (A(S) === 'befriend' && s === 1 && b.harvest && b.dance && !b.riddle && realmBloomNight(S)) return offerRiddle(['You harvested, you danced. The riddle-gnomes are waiting.']);
    const e = typeof prevNymph === 'function' ? prevNymph(S) : null;
    if (e && e.choice && e.choice.id === 'vh_bloom_games' && !b.riddle) {
      const options = e.choice.options.slice();
      const laterAt = options.findIndex((o) => o.label === 'Later.');
      const later = laterAt >= 0 ? options.splice(laterAt, 1)[0] : null;
      options.push({ label: 'Beat the riddle-gnomes', pick: (G) => bloomRiddle(G, 0) });
      if (later) options.push(later);
      return { ...e, choice: { ...e.choice, options } };
    }
    return e;
  };
  TALK.tobble_bench = tobbleBench;
  TALK.stargnome = stargnome;
  TALK.capseller = capseller;
  TALK.riddlestump = riddlestump;
  TALK.hollis = hollis;
  // Hooks are (id, S). A null from vhMarkerC must not swallow later realms' marks.
  if (!hooked) { hooked = true; MARKER_HOOKS.push(vhMarkerHook); }
}

// Called from Vanaheim.attach after the Stage B spots. No G.talkTo: vh.talk opens TALK, vh.look opens pages.
export function wireStageC(vh, G, area) {
  const f = G.S.flags || (G.S.flags = {});
  const night = () => {
    const clk = (vh.ctx && vh.ctx.clock) || (G.ctx && G.ctx.clock);
    return VH_NIGHT(clk && clk.t);
  };
  if (area === 'vh_village') {
    // Scene checks load with ?qa and never dismiss dialogue, so the arrival line would sit on every shot.
    if (!f.vh_arrived) { f.vh_arrived = 1; if (!(vh.qs && vh.qs().has('qa'))) vh.look('Mossbrook', ARRIVAL); }
    vh.spot({ pos: [3.6, -1.0], r: 1.0, label: 'Riddle Stump', show: () => true, act: () => vh.talk('riddlestump', 'Riddle Stump') });
    vh.spot({ pos: [4.6, 2.2], r: 1.0, label: "Tobble's bench", show: () => true, act: () => { if (!vh.talk('tobble_bench', "Tobble's bench")) vh.look("Tobble's bench", BENCH_IDLE); } });
    vh.spot({ pos: [0.2, 3.0], r: 1.1, label: 'Gnome astronomer', show: () => true, act: () => vh.talk('stargnome', 'the gnome astronomer') });
    STARS.forEach((p, i) => vh.spot({ pos: p, r: 0.9, label: 'Read the stars', show: () => night() && mood(G.S) >= 0 && !((f.vh_stars_seen || {})[i]) && !f.vh_stars_done,
      act: () => { const before = f.vh_stars || 0, n = readStar(G.S, i); if (n > before && G.toast) G.toast(`Stars read: ${n}/3`, 2); } }));
    // Same centre as the fizzing spring. Unshifted so at night, inside his radius, he wins the tie; the coin toss stays reachable farther out.
    vh.spots.unshift({ pos: HOLLIS.pos, r: HOLLIS.r, label: 'A frog in a crown?', show: () => night() && !f.vh_hollis, act: () => vh.talk('hollis', 'Hollis') });
    if (HUSHED(G.S) && G.toast) G.toast(hushedBark(G.S), 3);
  }
  if (area === 'vh_garden') {
    vh.spot({ pos: [2.4, -1.0], r: 1.0, label: 'A frozen blue bloom', show: () => (G.S.quests || {}).vh_thorn === 3 && !f.vh_veyra_bloom,
      act: () => { f.vh_veyra_bloom = 1; vh.look('The frozen bloom', VEYRA_BLOOM(G.S)); } });
    vh.spot({ pos: [-6.2, 2.8], r: 0.9, label: 'A spring under the roots', show: () => !f.vh_hidden_garden,
      act: () => { f.vh_hidden_garden = 1; G.factions.onSecret(); if (G.toast) G.toast('Hidden spring! Gnome Council merit', 2.4); } });
  }
}

installStageC();
