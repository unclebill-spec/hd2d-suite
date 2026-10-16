// [JOTUNHEIM] Jotunheim (realm-jotunheim branch), built from the Hearthmoor Story script (staging story/jotunheim.md) with Cozy Builder's
// rulings (Hrimgard 7x, Ulfar combat_scale 2.4 with no second sheet, Flurry's neon twin as the main look). Chunk 1 = the first area: Stonehollow
// (`jotunheim`). Quests / TALK / shops / the Bifrost gate merge into the shared tables from here, like svartalfheim.js, so shared files only
// carry a few marked hook lines. Planned and not built yet: see JOT_PLANNED + JOTUNHEIM_PROGRESS.md (RESUME HERE).
import { TALK, ITEMS, QUESTS, MARKER_HOOKS } from './data.js';
import { REALM, MERIT } from './factions.js';
import { ENEMIES, SPAWNS } from './heroes.js';
import { XP } from './progress.js';
import { SHOPS, GOODS } from './shop.js';
import { WAYS } from './ravenhold.js';
import { lockRival, moodUp } from './alfheim.js';

export const JOT_PLANNED = {   // id -> display name (story 2.1); `barrow` (B1-B4) + `barrow2` (B5-B9) are the dungeon, two areas like clockdeep
  jotunheim: 'Stonehollow', jt_hall: 'Hall of Hearthstones', rimecaves: 'The Rime Caves', barrow: "The Titan's Barrow", barrow2: "The Titan's Barrow: the Throne",
};
export const AREAS_JOT = { jotunheim: 'areas/jotunheim/', jt_hall: 'areas/jt_hall/', rimecaves: 'areas/rimecaves/' };   // id -> 'areas/<id>/' (merged into game.js's area path map)
export const AREA_NAMES_JOT = { jotunheim: 'Stonehollow', jt_hall: 'Hall of Hearthstones', rimecaves: 'The Rime Caves' };   // id -> display name (merged into game.js's AREA_NAME)
export const JOT_AREAS = Object.keys(JOT_PLANNED);

const flags = (S) => (S.flags = S.flags || {});
const F = (S) => S.flags || {};
const q = (S, k) => (S.quests || {})[k] || 0;
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };
Object.assign(REALM, { jotunheim: 'embassy', jt_hall: 'embassy', rimecaves: 'embassy', barrow: 'embassy', barrow2: 'embassy' });   // conquer / contract pay 'gate' with the alliance lock (later)
Object.assign(MERIT, { jt_gate: 60, jt_welcome: 40, jt_heart: 60, jt_rival: 20 });   // story 3.12 (the rest arrive with their quests)
WAYS.jotunheim = ['Stonehollow', 'jotunheim', 'from_waystone'];

export const JT_ARCH = { rect: [4.25, -12.3, 5.75, -11.45], pos: [5.0, -11.9], spawn: [5.0, -10.1, 'down'] };   // the ice arch on Bifrost's north wall
const HUB_GATE = { to: 'bifrost', spawn: 'from_jotunheim', rect: [-0.9, 10.1, 0.9, 11.1], label: 'the ice arch back to Bifrost Crossing' };
export const gateOpen = (S, qs) => !!(F(S).jt_gate_open || (F(S).alliance || {}).jotunheim || (qs && qs.has('jtq')));   // QA: ?jtq=... (Kolbrun's jt_gate quest comes next chunk)


// ------------------------------------------------------------------ foes (story 8.4) + the Rime Caves' pools (story 2.5; rares frostmother / avalanche come with the BASES hook)
Object.assign(ENEMIES, {
  frost_troll: { name: 'Frost troll', hp: 130, dmg: 15, speed: 1.0, reach: 1.8, windup: 0.7, cd: 2.0, aggro: 6.5, r: 0.5, push: 0.25, heavy: true },
  ice_golem: { name: 'Ice golem', hp: 160, dmg: 16, speed: 0.9, reach: 1.7, windup: 0.8, cd: 2.2, aggro: 6, r: 0.5, push: 0.2, heavy: true, weakBelly: 1.4 },
  avalanche_golem: { name: 'Avalanche golem', hp: 190, dmg: 20, speed: 0.9, reach: 2.0, windup: 1.0, cd: 2.4, aggro: 6, r: 0.6, push: 0.15, heavy: true },
  rime_berserker: { name: 'Rime Berserker', hp: 90, dmg: 13, speed: 2.0, reach: 1.5, windup: 0.4, cd: 1.4, aggro: 7.5, r: 0.4, push: 0.5, elite: true },
});
Object.assign(XP, { frost_troll: 50, ice_golem: 60, avalanche_golem: 85, rime_berserker: 80 });
SPAWNS.rimecaves = [   // giants are tall: foes stand north of the camera's first view (off screen) and >= 3.5 m apart (phone portrait shows them at the top; overlapping giants fail sprites_sharp)
  { id: 'rc_troll0', role: 'frost_troll', pos: [-10.5, -11.3] }, { id: 'rc_golem1', role: 'ice_golem', pos: [-7.0, -11.3] },
  { id: 'rc_zerk0', role: 'rime_berserker', pos: [-3.5, -11.3], night: true }, { id: 'rc_avl0', role: 'avalanche_golem', pos: [0.0, -9.6] },
  { id: 'rc_zerk1', role: 'rime_berserker', pos: [3.5, -11.3], night: true }, { id: 'rc_golem0', role: 'ice_golem', pos: [7.0, -11.3] },
  { id: 'rc_troll1', role: 'frost_troll', pos: [10.5, -11.3] },
];

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
  jt_heart: { title: 'The Hollow Heart', giver: 'Jarl Thyra Stonebrow', story: true, steps: {
    1: (S) => { const f = F(S), n = ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => f[k]).length;
      return f.sv_decoy ? 'Show the Jarl the boot mould from Anvildeep.' : `Study the Heart in the ice cellar. ${n}/3`; },
    2: 'Tell the Jarl what you found.',
    3: 'The Heart is a fake. Stonehollow was framed.',
  } },
  jt_hire: { title: 'Rime Wages', giver: 'Gatewright Halvard', story: true, steps: { 1: 'Hear the Jarl\'s terms, and meet Skuli at the goat pens.', 2: 'Lay Hrimgard back to sleep. (The Barrow comes in a later chapter.)', 3: 'Paid in full.' } },
  jt_take: { title: 'The Toll of Stones', giver: 'Envoy Kolbrun Hailstride', story: true, steps: { 1: 'Topple the watch-cairns. (The cairns come with the Rime Caves.)', 2: 'Open the Barrow.', 3: 'The Barrow Key is yours. Stonehollow will not forget.' } },
});
const need = (S) => (S.hero === 'runeguard' ? 2 : 3);

// ------------------------------------------------------------------ shared quest steps (module level so TALK can use them)
export const cellarOK = (S) => !!((F(S).alliance || {}).jotunheim || F(S).jt_contract || (typeof location !== 'undefined' && new URLSearchParams(location.search).has('jtq')));
const clueN = (S) => ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => F(S)[k]).length;
function finishWelcome(G) {
  const f = flags(G.S); G.setQuest('jt_welcome', 3); f.jt_trusted = 1; G.factions.add('embassy', MERIT.jt_welcome, 'jt_welcome'); gold(G, 20);
  f.realm_mood = { ...(f.realm_mood || {}), jotunheim: Math.max(3, (f.realm_mood || {}).jotunheim || 0) }; G.refreshMarkers && G.refreshMarkers();
}
function closeHeart(G) {   // The Hollow Heart done (story 3.3 / 4.3): the Heart is a fake, the war band turns back
  const S = G.S, f = flags(S), mood = moodJot(S);
  G.setQuest('jt_heart', 3); G.factions.add('embassy', MERIT.jt_heart + (mood ? MERIT.jt_rival : 0), 'jt_heart'); gold(G, 40);
  f.jt_cleared = 1; f.jt_peace = 1; S.evidence = { ...(S.evidence || {}), jotunheim: 'false_heart' }; G.refreshMarkers && G.refreshMarkers();
}

// ------------------------------------------------------------------ talk (TALK is keyed by the actor id in the area spec)
const moodJot = (S) => ((F(S).realm_mood || {}).jotunheim || 0) >= 1;
Object.assign(TALK, {
  jt_trader(S) {
    const first = !(S.met || {}).jt_trader;
    return { pages: [first ? 'Grimsa. Stall. Cloaks for small ones, tea for cold ones. Everything here is cut to your size, which is, hm, more work than you know.'
                           : 'Cloak, tea or lamp? The lamp burns blue. It will not burn you. We tested on a goat.'],
             then: (G) => { met('jt_trader')(G); G.shopUI.show('jt_trader'); } };
  },
  goatherd(S) {
    const f = F(S);
    if (f.jt_contract && f.jw_terms && !f.jw_skuli) return { pages: ['The Guild man! Skuli. I know a goat-path. Goats know everything. I will take you to the Barrow when it is time.', '(He whispers.) The Heart in the cellar rings hollow, you know. Look, if you like. Not my business.'], then: (G) => { flags(G.S).jw_skuli = 1; G.setQuest('jt_hire', 2); G.refreshMarkers && G.refreshMarkers(); } };
    if (f.jt_contract && !f.jw_terms) return { pages: ['The Jarl wants to hear your terms first. She is in the Hall. Goats wait. Goats are good at it.'] };
    return { pages: [f.jt_peace ? 'The war band turned back? Goats knew. Goats know everything.' : 'I know a goat-path. Goats know everything. Ask me when you have a reason to go sneaking.'] };
  },
  goatwife(S) { return { pages: [q(S, 'jt_welcome') >= 3 ? 'She bit you? Good. That means she likes you.' : 'Mind the horns. Mind the whole goat, really. She has opinions.'] }; },
  ulfar(S) {
    const first = !(S.met || {}).ulfar;
    return { pages: [first ? 'Oh. Hello. You are very small. I am Ulfar. I look at the lake. It does not look back.'
                            : 'Snow tastes like nothing. I eat it anyway.', 'Kolbrun says stay off the lake. Unless you are a goat.'], then: met('ulfar') };
  },
  jt_a(S) { return { pages: ['Mind the stools. They are for sitting, not climbing.'] }; },
  jt_b(S) { return { pages: [['The aurora sings if you are quiet.', 'Dwarves think we steal. We cannot even fit in their doors.'][(S.day || 0) % 2]] }; },
  // the Jarl (story 5.2, 3.2 stage 2, 3.3, 3.6, 4.3): the choice, the fire, the Hollow Heart, the contract terms
  jarl(S) {
    const f = F(S), mood = moodJot(S), locked = (f.rivals || {}).jotunheim === 'locked', al = (f.alliance || {}).jotunheim;
    if (f.jt_contract && !f.jw_terms) return { pages: ['An offer from the Guild? Hm. Terms, then: the Titan sleeps in the Barrow and his sleep is thinning.', 'Lay him back down, and the Guild may have its coin. Skuli at the goat pens will guide you. He is young. He is also right, mostly.'], then: (G) => { flags(G.S).jw_terms = 1; G.setQuest('jt_hire', 1); } };
    if (al === 'befriend') {
      if (q(S, 'jt_welcome') === 2) return { pages: ["(You sit at the Jarl's fire. The hall hums. Someone passes you a bone, politely.)", 'Arms that work, and a fire shared. Welcome, small one.', 'One more thing. The dwarves say we stole their Heart. There is a Heart in my cellar, and I am not proud of it. Go and look at it. Tell me what you see.'],
        then: (G) => { finishWelcome(G); G.setQuest('jt_heart', 1); } };
      if (q(S, 'jt_heart') === 1 && f.sv_decoy) return { pages: ['You carry a boot mould from Anvildeep? Show me.', '(The mould fits the frost-iron prints in the cellar, small straps and all.)', 'The dwarves sent a friend? Then the world is not all spears.', 'I will send a horn-message to their Thane. The war band turns back.'], then: (G) => closeHeart(G) };
      if (q(S, 'jt_heart') === 2) return { pages: ['A shell. Blue-black rime, and big boots that went in and never came out. Someone small and cruel wanted two realms at each other\'s throats.', 'You have done Stonehollow a great kindness. I will send a horn-message to Anvildeep: the war band turns back.'], then: (G) => closeHeart(G) };
      if (q(S, 'jt_heart') === 1) { const n = ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => f[k]).length; return { pages: [`The cellar trapdoor is by the north-east table. Tap the Heart, look at the rime, follow the prints. ${n}/3.`] }; }
      if (q(S, 'jt_welcome') === 3 && !q(S, 'jt_heart')) return { pages: ['The town trusts you. So I will ask the hard thing: look at the Heart in my cellar.'], then: (G) => G.setQuest('jt_heart', 1) };
      if (q(S, 'jt_welcome') === 1) return { pages: ['Then lift our stones. We trust arms that work.'] };
      return { pages: ['The fire is for everyone. Sit.'] };
    }
    if (al === 'conquer') return { pages: ['So. Midgard is a thief too. Take it, and go.'] };
    const opts = [];
    if (!locked) opts.push({ label: 'A friend. Let me prove you innocent.', pick: () => ({ pages: ['Then lift our stones. We trust arms that work.'],
      then: (G) => { ally(G.S).jotunheim = 'befriend'; lockRival(G.S, 'asgard'); moodUp(G.S, 'vanaheim'); G.setQuest(mood ? 'jt_heart' : 'jt_welcome', 1); G.toast('Jotunheim: befriended', 2.2); G.refreshMarkers && G.refreshMarkers(); } }) });
    opts.push({ label: "Midgard's. Hand over the Barrow Key.", pick: () => ({ pages: ['So. Midgard is a thief too. Take it, and go.'],
      then: (G) => { ally(G.S).jotunheim = 'conquer'; moodUp(G.S, 'asgard'); G.setQuest('jt_take', 1); G.toast('Jotunheim: conquered', 2.2); } }) });
    if (locked) opts.push({ label: 'The Guild sent me with an offer.', pick: () => ({ pages: ['An offer. Hm. Hear my terms.'], then: (G) => { flags(G.S).jt_contract = 1; G.setQuest('jt_hire', 1); } }) });
    return { pages: [mood ? 'You humbled the thunder-folk? Sit by the fire, small one.' : locked ? "Asgard's friend, in my hall. Say it quick."
                           : 'Midgard comes to Stonehollow. Dwarves call us thieves. Asgard calls us raiders. What are you?'], choice: { id: 'jt_jarl', options: opts } };
  },
  envoy_jt(S) {
    const al = (F(S).alliance || {}).jotunheim;
    return { pages: [al === 'conquer' ? 'So you took the Barrow Key by asking. Or by not asking. I keep the ledger either way.' : al === 'befriend' ? 'Stay off the lake. Unless you are a goat. The Jarl likes you; do not make her regret it.' : 'Stay off the lake. Unless you are a goat.'] };
  },
  rimewife(S) {
    const f = F(S), al = (f.alliance || {}).jotunheim;
    if (al === 'conquer') return { pages: ["You know it's hollow. Everyone can hear it.", 'Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.'] };
    if (al === 'befriend' && q(S, 'jt_heart') === 1 && !f.jh_solvi) return { pages: ['The cellar Heart? Rime tells the truth if you give it good light. Take my rune-light.', '(Solvi lends you her rune-light. It hums, and shows rime for what it is.)'], then: (G) => { flags(G.S).jh_solvi = 1; } };
    return { pages: ['Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.'] };
  },
  solvi(S) {   // the rune-keeper in her own hall (story 5.3); the Stonefrost school comes after the Barrow (barrow = 3)
    const f = F(S), al = (f.alliance || {}).jotunheim;
    if (al === 'conquer') return { pages: ["You know it's hollow. Everyone can hear it.", 'The Barrow Key? It opens the door. It does not make the dead agree.'] };
    if (al === 'befriend') return { pages: ['Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.', 'The Barrow door has three rune locks. I can open them when the Jarl trusts you with the Titan. Soon.'] };
    return { pages: ['Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.'] };
  },
  rc_skuli(S) { return { pages: [F(S).jt_contract ? 'The goat-path goes round the side of the door. Goats do not need rune locks.' : 'Goats know the way round the side.'] }; },
  jt_guard1(S) { return { pages: [cellarOK(S) ? 'The Jarl says you may go down. Mind the plinth.' : "The cellar is the Jarl's."] }; },
  jt_guard2(S) { return { pages: [cellarOK(S) ? 'Down the trapdoor. Do not lick the Heart.' : 'Nobody goes down without the Jarl\'s word.'] }; },
  jt_diner1(S) { return { pages: ['The aurora sings if you are quiet.'] }; },
  jt_diner2(S) { return { pages: ['Mind the stools. They are for sitting, not climbing.'] }; },
});

MARKER_HOOKS.push((id, S) => {
  const f = F(S), al = f.alliance && f.alliance.jotunheim;
  if (id === 'jarl') {
    if (!al || (al === 'befriend' && (q(S, 'jt_welcome') === 2 || q(S, 'jt_heart') === 2 || (q(S, 'jt_heart') === 1 && f.sv_decoy) || (q(S, 'jt_welcome') === 3 && !q(S, 'jt_heart'))))) return 'quest_mark';
    if (f.jt_contract && !f.jw_terms) return 'quest_mark';
  }
  if (id === 'rimewife' && al === 'befriend' && q(S, 'jt_heart') === 1 && !f.jh_solvi) return 'quest_mark';
});

// ------------------------------------------------------------------ the area's own look: cold fire on the braziers, rune pulses, the lake, a gloom light
const COLD = ['#7fd4ff', 4.2, 4.2];   // colour, intensity, range
const JT_FX = {
  jotunheim: [['cold_flame', [-2.4, -5.0], 1.0, 1], ['cold_flame', [2.4, -5.0], 1.0, 1],
              ['rune_pulse', [0, -5.4], 0.8, 1], ['rune_pulse', [-5.4, 0.2], 0.8, 0], ['rune_pulse', [5.2, -0.4], 0.8, 0],
              ['rune_pulse', [10.6, -1.4], 0.8, 1], ['ice_sparkles', [8.0, -3.2], 0.5, 0]],
};
JT_FX.jt_hall = [['cold_flame', [-1.5, -2.0], 1.0, 1], ['cold_flame', [1.5, -2.0], 1.0, 1], ['cold_flame', [0, -3.6], 1.0, 1], ['cold_flame', [0, -0.4], 1.0, 1],
  ['rune_pulse', [-7.0, -10.4], 0.8, 1], ['rune_pulse', [7.0, -10.4], 0.8, 1], ['cold_flame', [12.4, -3.0], 1.0, 1], ['cold_flame', [16.0, -3.0], 1.0, 1], ['ice_sparkles', [14.2, -5.4], 0.5, 0]];
JT_FX.rimecaves = [['cold_flame', [-3.6, -8.4], 1.0, 1], ['cold_flame', [3.6, -8.4], 1.0, 1], ['pool_teal', [-6.0, 5.2], 0, 0], ['pool_aurora', [6.0, 5.2], 0, 0],
  ['pool_teal', [-7.4, -0.4], 0, 0], ['ice_sparkles', [0, 0.2], 0.5, 0], ['rune_pulse', [-9.8, -7.0], 0.8, 0]];
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
    if (G.hollows) { const c0 = G.hollows.onCast.bind(G.hollows); G.hollows.onCast = (...a) => { const r = c0(...a); me.onCast(); return r; }; }
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
    if (v === 'heart' || v === 'decoy') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; S.quests.jt_welcome = 3; flags(S).jt_trusted = 1; S.quests.jt_heart = 1; }
    if (v === 'decoy') { flags(S).sv_decoy = 1; flags(S).sv_cleared = 1; S.evidence = { ...(S.evidence || {}), svartalfheim: 'boot_mould' }; }
    if (v === 'fire') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; S.quests.jt_welcome = 2; flags(S).jw_lifts = 3; }
    if (v === 'conquer') { ally(S).jotunheim = 'conquer'; flags(S).jt_gate_open = 1; S.quests.jt_take = 1; }
    if (v === 'contract') { flags(S).rivals = { ...(flags(S).rivals || {}), jotunheim: 'locked' }; flags(S).jt_contract = 1; flags(S).jt_gate_open = 1; S.quests.jt_hire = 1; }
    if (v === 'done') { S.quests.jt_welcome = 3; flags(S).jw_lifts = 3; flags(S).jt_trusted = 1; }
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (area === 'bifrost') { this.gate.atBifrost(ctx); return; }
    if (!AREAS_JOT[area]) return;
    this.qaPreset();
    if (area === 'jotunheim') this.stonehollow(ctx);
    if (area === 'jt_hall') this.hall(ctx);
    if (area === 'rimecaves') this.caves(ctx);
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
  // ---- the Hall of Hearthstones (story 2.4, 4): the Jarl, the ice cellar trapdoor and the false Heart's three clues. The cellar is the walled pocket
  // east of the hall (spawn `cellar`); the trapdoor and the cellar stair move the player between the two (no loading, one scene).
  hall(ctx) {
    const G = this.G, still = !!G.qaStill; this.inCellar = false;
    for (const [name, [x, z], dy, glow] of JT_FX.jt_hall) {
      const y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    this.spot({ id: 'trapdoor', pos: [5.0, -7.4], r: 1.7, label: 'the ice cellar trapdoor (E / A)', show: () => !this.inCellar, act: () => this.trapdoor() });
    this.spot({ id: 'plinth', pos: [14.2, -8.6], r: 2.0, label: 'the false Heart (E / A)', act: () => this.plinth() });
    this.spot({ id: 'rime', pos: [16.2, -9.0], r: 1.5, label: 'the rime on the plinth (E / A)', act: () => this.rime() });
    this.spot({ id: 'stair', pos: [14.2, -1.8], r: 1.6, label: 'the cellar stair (E / A)', act: () => this.cellarStair() });
  }
  // ---- the Rime Caves (story 2.5): Solvi's rune-hall, the Barrow mouth with its three rune locks, the frozen waterfall's hidden spring
  caves(ctx) {
    const G = this.G, still = !!G.qaStill;
    for (const [name, [x, z], dy, glow] of JT_FX.rimecaves) {
      const y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    this.spot({ id: 'door', pos: [0, -7.6], r: 2.2, label: 'the Barrow door (E / A)', show: () => !AREAS_JOT.barrow, act: () => this.barrowDoor() });
    this.spot({ id: 'spring', pos: [9.0, -7.4], r: 2.0, label: 'the frozen waterfall (E / A)', act: () => this.springLook() });
  }
  barrowDoor() {
    const f = F(this.G.S), al = (f.alliance || {}).jotunheim;
    const how = al === 'conquer' ? 'The Barrow Key would open them all at once.' : f.jt_contract ? "Skuli's goat-path runs round the side of the door." : al === 'befriend' ? 'Solvi can open them, when the Jarl says.' : 'Without the Jarl\'s word or a key, they stay locked.';
    this.look('jt_barrow_door', 'The Barrow door', ['A stone door six metres tall, sunk in the cliff. Three rune locks glow dull blue across it, one above the other.', how, '(The Barrow itself opens in a later chapter of the build.)']);
  }
  springLook() {
    const S = this.G.S;
    if (!(S.found || {}).rc_spring) this.look('rc_waterfall', 'The frozen waterfall', ['A waterfall frozen mid-fall, thick as a tree. Something blue glints behind it.', '(Any fire spell cast close by would melt it.)']);
    else this.look('rc_spring', 'The hidden spring', ['The thaw has uncovered a hidden spring behind the waterfall. The water is cold and very clear.']);
  }
  onCast() {   // a spell cast within 2.6 m of the waterfall melts it (the Hollows brazier / flue rule)
    const c = this.ctx, S = this.G.S; if (!c || this.area !== 'rimecaves' || (S.found || {}).rc_spring) return;
    if (Math.hypot(c.player.x - 9.0, c.player.z - -7.4) > 2.6) return;
    S.found = { ...(S.found || {}), rc_spring: 1 }; this.G.toast('The ice sweats and cracks: a hidden spring.', 2.6);
    if (c.gamefx && c.gamefx.meta.effects.snow_puff) this.fx.push(c.gamefx.spawn('snow_puff', 9.0, c.heightAt(9.0, -7.4) + 0.6, -7.4, { duration: 1.6 }));
    this.G.save && this.G.save();
  }
  moveTo(x, z) { const c = this.ctx; if (!c) return; c.player.x = x; c.player.z = z; c.player.y = c.heightAt(x, z); }
  trapdoor() {
    const S = this.G.S;
    if (!cellarOK(S)) { this.look('jt_trapdoor', 'The cellar trapdoor', ['A trapdoor of black oak, barred. A guard shifts to stand on it.', '"Nobody goes down without the Jarl\'s word."']); return; }
    this.look('jt_trapdoor', 'The cellar trapdoor', ['(You heave the trapdoor up. Cold breathes out, and a blue light below.)'], () => { this.inCellar = true; this.moveTo(14.2, -3.4); });
  }
  clue(k, name) {
    const G = this.G, S = G.S, f = flags(S); if (f[k]) return; f[k] = 1;
    G.toast(`Clue: ${name} (${clueN(S)}/3)`, 2.2);
    if (q(S, 'jt_heart') === 1 && !f.sv_decoy && clueN(S) >= 3) { G.setQuest('jt_heart', 2); G.refreshMarkers && G.refreshMarkers(); }
    G.save && G.save();
  }
  plinth() {
    const G = this.G, S = G.S, con = ((F(S).alliance || {}).jotunheim) === 'conquer';
    S.evidence = { ...(S.evidence || {}), jotunheim: 'false_heart' };   // the evidence counts on every path, if you look (story 4.4)
    const pages = ['(The false Heart sits on its plinth, a shell of frost-iron shaped like a heart. You tap it. It rings hollow, like a bucket.)', 'The real Anvil-Heart beats like a drum. This one is a shell.'];
    if (con) pages.push('(You could say it is the real one. You could use it as your excuse. Everyone in the hall knows what it sounds like.)');
    this.look('jh_heart', 'The false Heart', pages, () => this.clue('jh_heart', 'it rings hollow'));
  }
  rime() {
    const f = F(this.G.S);
    if (!f.jh_solvi) { this.look('jh_rime', 'The rime', ['The rime on the plinth looks grey in this gloom. Solvi\'s rune-light would show its true colour.']); return; }
    this.look('jh_rime', 'The rime', ["(Solvi's rune-light washes the plinth. The rime is blue-black, like the Cold Altar tongs and the boot mould.)", 'Giant frost is white. This is not giant frost.'], () => this.clue('jh_rime', 'the rime is blue-black'));
  }
  cellarStair() {
    this.look('jh_trail', 'The cellar stair', ['(Frost prints, huge ones, climb the stair. They go in. None come out.)', 'Someone small took off big boots right here, and went on in their socks.'], () => { this.clue('jh_trail', 'the prints go in, none come out'); this.inCellar = false; this.moveTo(4.6, -5.8); });
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
  finishWelcome(G) { finishWelcome(G); }
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
  qaSpot(id) { const sp = this.spots.find((x) => x.id === id); if (!sp) return false; sp.act(); return true; }
  qaLift(i) { this.lifted(i, true); return this.qa(); }
  qa() {
    const c = this.ctx, S = this.G.S, f = F(S), gm = c ? (c.scene.game || {}) : {};
    return { realm: 'jotunheim', built: Object.keys(AREAS_JOT), planned: JOT_AREAS, area: this.area, exits: (gm.exits || []).map((e) => e.to), portals: (gm.portals || []).map((p) => p.to),
             spots: this.spots.filter((x) => x.show()).length, lifts: f.jw_lifts || 0, need: need(S), quest: q(S, 'jt_welcome'), gate: this.gate.qa(), alliance: (f.alliance || {}).jotunheim || null,
             actors: c ? c.actors.list.map((a) => a.id || a.role) : [], fx: this.fx.length, lights: this.lights.length, ring: !!this.ring, inCellar: !!this.inCellar, heart: q(S, 'jt_heart'), clues: ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => f[k]), peace: !!f.jt_peace, evidence: (S.evidence || {}).jotunheim || null, hire: q(S, 'jt_hire'), terms: !!f.jw_terms, skuli: !!f.jw_skuli, pos: c ? [c.player.x, c.player.z] : null, spring: !!(S.found || {}).rc_spring, foes: c ? c.actors.list.filter((a) => ['frost_troll', 'ice_golem', 'avalanche_golem', 'rime_berserker'].includes(a.role)).map((a) => a.role) : [], shop: !!SHOPS.jt_trader, found: S.found || {} };
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
