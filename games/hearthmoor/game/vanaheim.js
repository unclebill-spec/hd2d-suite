// game/vanaheim.js (Hearthmoor Story, staging 2026-10-26). Mossbrook city arc; dungeons stay in verdant_heart.md.
import { allyCount } from './muspelheim.js';   // as niflheim.js does (PREP.md: not in data.js)
import { MERIT, NEED, REALM, VANAHEIM_AREAS, Factions } from './factions.js';
import { TALK, QUESTS, ITEMS, MARKER_HOOKS } from './data.js';
import { ENEMIES } from './heroes.js';
import { XP } from './progress.js';
import { SHOPS } from './shop.js';

const F_ = (S) => (S.flags || (S.flags = {}));
const A = (S) => ((S.flags || {}).alliance || {}).vanaheim;
const mood = (S) => ((S.flags || {}).realm_mood || {}).vanaheim || 0;

export const VH_MERIT = { vh_swing: 20, vh_hex: 60, vh_thorn: 120, vh_bloom: 40 };

export const VH_ITEMS = {
  hexknot:    { name: 'Hex-knot', px: 'hexknot', about: 'A twist of black thorn around a frost-blue bead. It whispers "elf-work" if you hold it too long.' },
  fizzstone:  { name: 'Fizzstone', px: 'fizzstone', about: 'A pebble from a hidden spring. It never stops bubbling, even in your pocket.' },
  glowfry:    { name: 'Glow-fish fry', px: 'glowfry', about: 'A very small volunteer. It glows cyan when it is happy, which is always.' },
  tithe_seal: { name: 'Tithe-seal', px: 'tithe_seal', about: 'Ravenhold wax, stamped with a spring. Clerk Pike apologised while handing it over.' },
  frost_bloom:{ name: 'Frost bloom', px: 'frost_bloom', about: 'A thorn-flower frozen blue at the heart. The same cold as the spike.' },
  nettle_circlet: { name: 'Nettlecrown\'s Bean-Circlet', px: 'alder_charm', accessory: true, unique: true, regen: 2, thorns: 5,
                    about: 'A woven bean-vine crown with one blue bloom. +2 HP/s regen while resting; the first enemy that hits you each fight takes 5 thorn damage.' },
  bloom_token:{ name: 'Bloomtide token', px: 'bloom_token', about: 'A pressed glow-cap on a ribbon. Gnomes trade them like secrets.' },
  mossheart_staff: { name: 'Mossheart Staff', px: 'mossheart_staff', legendary: true,
                     about: 'Grown, not carved, around a Greenheart tine. It hums, and somewhere a spore giant wakes up.' },
};

export const VH_QUESTS = {
  vh_hex: {
    title: 'Whispers in the Toadstools', giver: 'Elder Burrowmoss', story: true,
    steps: {
      1: (S) => `Find and burn the Thornhex knots hidden in Mossbrook. ${Math.min(3, (S.flags || {}).vh_knots || 0)}/3`,
      2: 'Tell Burrowmoss what the knots whispered.',
      3: 'The whispers came from Thornhex knots, beaded with frost. Someone is feeding the hedge-witches.',
    },
  },
  vh_thorn: {
    title: 'The Thornhex Garden', giver: 'Elder Burrowmoss', story: true,
    steps: {
      1: (S) => `Cut the frost-thorn roots in the Thorngarden and reach the coven circle. ${Math.min(3, (S.flags || {}).vh_roots || 0)}/3`,
      2: (S) => ((S.flags || {}).vh_thorn_pact ? 'Nettlecrown holds Mossbrook for you now. Leave the garden.' : 'Face Mother Nettlecrown.'),
      3: (S) => {
        const f = S.flags || {};
        if (f.vh_thorn_pact) return 'Mossbrook is held, by thorns. Nettlecrown will remember the favour.';
        return f.vh_nettle === 'spared' ? 'Nettlecrown is planting beans again.' : 'The Thorngarden is quiet. One blue bloom stayed frozen.';
      },
    },
  },
  vh_tobble: {
    title: 'Small Brave Things', giver: 'Tobble Capwhistle', story: true,
    steps: {
      1: (S) => { const i = S.inv || {}; return `Bring Tobble a fizzstone (${i.fizzstone ? 1 : 0}/1) and a glow-fish fry (${i.glowfry ? 1 : 0}/1).`; },
      2: 'Watch Tobble fix the bubble-lamp.',
      3: 'The bubble-lamp shines again. Tobble is coming along for the big brave things.',
    },
  },
  vh_tithe: {
    title: 'The Spring Tithe', giver: 'Clerk Ansel Pike', story: true,
    steps: {
      1: (S) => `Set tithe-seals on Mossbrook's three upper springs. ${Math.min(3, (S.flags || {}).vh_seals || 0)}/3`,
      2: 'Report to Clerk Pike at the vine gate.',
      3: 'Mossbrook pays its tithe of spring water. The gnomes have stopped whistling.',
    },
  },
  vh_bloom: {
    title: 'Bloomtide', giver: 'Liss of the Fizzing Steps', bounty: true,
    steps: {
      1: (S) => { const b = (S.flags || {}).vh_bloom_games || {}; return `Bloomtide night: harvest ${b.harvest ? 1 : 0}/1, dance ${b.dance ? 1 : 0}/1, riddles ${b.riddle ? 1 : 0}/1.`; },
      3: 'Bloomtide is over. The springs will sing again in seven nights.',
    },
  },
  vh_staff: {
    title: 'The Mossheart Staff', giver: 'Tobble Capwhistle', ripple: true,
    steps: {
      1: (S) => { const i = S.inv || {}; return `Bring a Greenheart tine (${i.greenheart_tine ? 1 : 0}/1) and 3 fizzstones (${Math.min(3, i.fizzstone || 0)}/3) to Tobble's bench.`; },
      2: 'Let Tobble and Burrowmoss grow the staff.',
      3: 'The Mossheart Staff is yours. Something large and spore-shaped is very pleased.',
    },
  },
};

// Prepended pages for TALK.warden before the alliance choice (5.2)
export const swingPages = (S) => {
  const m = mood(S);
  if (m >= 1) return ['Ulfar\'s folk vouch for you. Giants don\'t vouch lightly. Sit, sit.'];
  if (m < 0) return ['Goldspire\'s friend. The Aesir burned our orchards once. We don\'t forget, we just compost.'];
  return [];
};

// Replaces the befriend option when the cap is full (5.2): the Spring Wages contract (Q2). Other options in TALK.warden are unchanged.
export const capOption = {
  label: 'Then hire me. Just for the spring.',
  pick: (G) => { const f = F_(G.S); f.vh_contract = 1; G.setQuest('vh_spring', 1);
    return { pages: ['Four friends already? Then you\'ve no room for a fifth. But a spring doesn\'t care who cleans it.',
                     'Spring Wages, then. Clear the water, and Mossbrook pays you fair. No oaths.'] }; },
};
export const wardenOptions = (S, options) => (allyCount(S) >= 4 ? [capOption, ...options.slice(1)] : options);

export const VH_TALK = {
  tobble(S) {
    const q = S.quests || {}, i = S.inv || {};
    if (A(S) !== 'befriend') return { pages: ['(Tobble hides behind a toadstool and does not come out.)'] };
    if ((q.rotwood || 0) === 3 && !q.vh_tobble) return {
      pages: ['This is Mother\'s bubble-lamp. It went dark the night the spring went violet. I can fix it. Probably. Possibly.',
              'I need a fizzstone from a hidden spring and a baby glow-fish. A volunteer glow-fish. We\'ll ask nicely.'],
      then: (G) => G.setQuest('vh_tobble', 1) };
    if (q.vh_tobble === 1 && i.fizzstone && i.glowfry) return {
      pages: ['(Tobble works with his tongue between his teeth. The fry swims into the lamp\'s globe. Cyan light fills the workshop.)',
              'Mother would say, "Be brave in small ways." Well. That was small.'],
      choice: { id: 'vh_tobble_join', options: [
        { label: 'Come on, then. The big ones are waiting.', pick: (G) => {
            const f = F_(G.S); f.companions = { ...(f.companions || {}), tobble: 1 };
            G.S.inv.fizzstone -= 1; G.S.inv.glowfry -= 1; G.setQuest('vh_tobble', 3); G.toast('Tobble Capwhistle joins you', 2.2);
            return { pages: ['Really? Really really? I\'ll get my goggles. And my other goggles.'] }; } },
        { label: 'Not yet. Stay with the lamp a while.', cancel: true, pick: (G) => {
            G.setQuest('vh_tobble', 2);
            return { pages: ['Oh. Yes. Someone should watch it. Come back for me? You promise? Gnome-promise?'] }; } },
      ] } };
    if (q.vh_tobble === 2) return {
      pages: ['You came back! The lamp\'s fine. I told it I\'d be brave. Let\'s go.'],
      then: (G) => { const f = F_(G.S); f.companions = { ...(f.companions || {}), tobble: 1 }; G.setQuest('vh_tobble', 3); } };
    return { pages: ['That mushroom is judging us. Don\'t look at it.'] };
  },

  nettlecrown(S) {
    const f = S.flags || {}, q = S.quests || {};
    if (q.vh_thorn !== 1 || (f.vh_roots || 0) < 3) return { pages: ['(The thorns rustle. Somewhere ahead, someone is humming a planting song, very badly.)'] };
    const intro = ['You\'ve come to weed me. Everyone comes to weed me.',
      'The cold lady gave me thorns that never wilt. Do you know what it is to plant and plant and watch it all go to rot?',
      'Hers doesn\'t rot. Hers lasts.'];
    if (A(S) === 'conquer') return { pages: intro, choice: { id: 'nettle_bargain', options: [
      { label: 'Hold Mossbrook for me, then.', pick: (G) => {
          const g = F_(G.S); g.vh_thorn_pact = 1; G.setQuest('vh_thorn', 2);
          return { pages: ['Ha. A Midgarder who likes thorns. I\'ll hold it. Tight.'] }; } },
      { label: 'No. You\'re done.', pick: (G) => { G.setQuest('vh_thorn', 2); G.startBoss('nettlecrown');
          return { pages: ['Then come and weed me.'] }; } },
    ] } };
    return { pages: intro, then: (G) => { G.setQuest('vh_thorn', 2); G.startBoss('nettlecrown'); } };
  },

  nettlecrown_after(S) {   // shown when ENEMIES.nettlecrown yields at 5% (after the 10% heartroot grab)
    return { pages: ['(She kneels. The thorns go soft around her.)', 'I only wanted something that lasted.'],
      choice: { id: 'nettle_end', options: [
        { label: 'Plant something that rots. It\'s allowed.', pick: (G) => {
            const f = F_(G.S); f.vh_nettle = 'spared'; endBossAdds(G); G.S.inv.frost_bloom = 1; G.S.inv.nettle_circlet = 1; giveCirclet(G); G.setQuest('vh_thorn', 3);
            if (A(G.S) === 'befriend') G.factions.add('embassy', VH_MERIT.vh_thorn, 'vh_thorn');
            { const r = G.factions.rank('embassy'); if (r < NEED.length - 1)   // +1 Embassy rank: top merit up to the next NEED step
                G.factions.add('embassy', Math.max(0, NEED[r + 1] - ((G.S.merit || {}).embassy || 0)), 'nettle_spare'); }
            return { pages: ['...Beans, then. Beans rot beautifully.', '(She weaves a bean-vine circlet, one blue bloom in it, and sets it on your head.)',
                             'Wear it. Things grow back. Even you.'] }; } },
        { label: 'Your garden\'s done.', pick: (G) => {
            const f = F_(G.S); f.vh_nettle = 'ended'; endBossAdds(G); G.S.inv.frost_bloom = 1; G.setQuest('vh_thorn', 3);
            if (A(G.S) === 'befriend') G.factions.add('embassy', VH_MERIT.vh_thorn, 'vh_thorn');
            return { pages: ['(The thorns crumble to petals as she fades. One blue bloom stays frozen in your hand.)'] }; } },
      ] } };
  },

  ansel(S) {
    const q = S.quests || {}, f = S.flags || {};
    if (A(S) !== 'conquer') return { pages: ['(A clerk\'s stool by the vines, empty. Someone left a very neat inkpot.)'] };
    if (!q.vh_tithe) return { pages: ['Clerk Pike, Ravenhold tithe office. Midgard claims the upper springs. I have the form. I\'m sorry about the form.'],
      then: (G) => { G.S.inv.tithe_seal = 3; G.setQuest('vh_tithe', 1); } };
    if (q.vh_tithe === 1 && (f.vh_seals || 0) >= 3) return { pages: ['All three. Stamped, sealed, filed. Nobody here will speak to me again, I expect.'],
      then: (G) => { G.setQuest('vh_tithe', 3); G.S.gold = (G.S.gold || 0) + 200; if (!(G.S.quests || {}).rotwood) G.setQuest('rotwood', 1); } };
    return { pages: ['Three springs, three seals. Mind the gnomes. They bite ankles. Politely, but they bite.'] };
  },

  nymph_vh(S) {
    if (A(S) === 'conquer') return { pages: ['(The water goes still and dark when you come near.)'] };
    return { pages: ['Dance with the springs and they\'ll sing for you. Step on the fish and they won\'t.',
                     'The violet made us sick. You made us well. Dance!'] };
  },
};

export const vhMarker = (S, id) => {
  const q = S.quests || {}, f = S.flags || {}, av = A(S), i = S.inv || {};
  if (id === 'warden' && av === 'befriend' && q.vh_spring === 3 && !q.vh_hex) return 'quest_mark';
  if (id === 'warden' && q.vh_hex === 1 && (f.vh_knots || 0) >= 3) return 'quest_turnin';
  if (id === 'warden' && q.rotwood === 3 && !q.vh_thorn) return 'quest_mark';
  if (id === 'tobble' && av === 'befriend' && q.rotwood === 3 && !q.vh_tobble) return 'quest_mark';
  if (id === 'tobble' && q.vh_tobble === 1 && i.fizzstone && i.glowfry) return 'quest_turnin';
  if (id === 'ansel' && av === 'conquer' && !q.vh_tithe) return 'quest_mark';
  if (id === 'ansel' && q.vh_tithe === 1 && (f.vh_seals || 0) >= 3) return 'quest_turnin';
  return null;
};

export const VH_ENEMIES = {
  nettlecrown: { name: 'Mother Nettlecrown', scale: 5.5, hp: 1500, dmg: 22, speed: 0.9, reach: 5.0, windup: 0.8, cd: 2.0, aggro: 10, r: 1.5,
                 push: 0.1, heavy: true, boss: true, minion: 'thornnymph', phases: [0.65, 0.35, 0.1], weak: 'crown', grabAt: 0.1,
                 yieldAt: 0.05, glow: '#7fd8ff', legendary: true, noRespawn: true },
  thornhex:    { name: 'Thornhex', scale: 1.0, hp: 120, dmg: 12, speed: 1.0, reach: 3.5, windup: 0.7, cd: 2.4, aggro: 8, r: 0.5,
                 elite: true, caster: true, snare: 2.0, healPulse: 20, conquerCount: 1, glow: '#a45cf0' },
  thornnymph:  { name: 'Thorn-nymph', scale: 1.0, hp: 70, dmg: 9, speed: 1.3, reach: 1.4, windup: 0.5, cd: 1.6, aggro: 8, r: 0.45, glow: '#ff3fb4' },
};


// =================================================================== Stage B wiring (Hearthmoor Cozy Builder, 2026-10-28)
// Game Director's numbers (BALANCE.md 2026-10-28): Nettlecrown 1500 HP / 22 dmg / phases 65 % + 35 % / heartroot grab 10 % /
// yields 5 % / 2 thorn-nymphs in P1 and P3 / conquer path +1 Thornhex (heals her 20) / no enrage / 600 XP.
export const NETTLE = { adds: { 1: 2, 3: 2 }, healEvery: 6, grabDmg: 14, circle: [4.0, -2.2] };
// Hearthmoor Art icons (art/vanaheim/icons, 16 px): drawn as images in the bag (game.js iconHTML)
for (const k of ['hexknot', 'fizzstone', 'tithe_seal', 'frost_bloom', 'mossheart_staff', 'nettle_circlet']) if (ITEMS[k]) ITEMS[k].img = `art/vanaheim/icons/${k}.png`;
const PLACEHOLDER_ROLE = { nettlecrown: 'hedgewitch', thornnymph: 'sporeling', thornhex: 'hedgewitch' };   // PLACEHOLDER until art/vanaheim/READY.txt
export const VH_PLANNED = { vh_village: 'Mossbrook', vh_garden: 'The Thorngarden' };
export const AREAS_VH = Object.fromEntries(Object.keys(VH_PLANNED).map((a) => [a, `areas/${a}/`]));
export const AREA_NAMES_VH = { ...VH_PLANNED };
export const VILLAGE_PATH = { rect: [12.6, -1.4, 14.0, 1.4], to: 'vh_village', spawn: 'from_vanaheim', label: 'the lane to Mossbrook village' };

Object.assign(ITEMS, VH_ITEMS);
Object.assign(QUESTS, VH_QUESTS);
Object.assign(ENEMIES, VH_ENEMIES);
Object.assign(MERIT, VH_MERIT);
Object.assign(XP, { blightregent: 560, hjortur: 640, nettlecrown: 600, thornhex: 70, thornnymph: 32 });   // GD: Regent ~560, Hjortur ~640 (combat fell back to 25)
SHOPS.nettle = { name: 'Nettlecrown\'s Seed & Tonic Stall', keeper: 'Mother Nettlecrown, gardening again', goods: ['tonic', 'glowseed'], gear: { n: 0, rar: [] }, sellMul: 1 };   // the spare path: her garden reopens
Object.assign(REALM, { vh_village: 'embassy', vh_garden: 'embassy' });
Object.assign(VANAHEIM_AREAS, { vh_village: 1, vh_garden: 1 });
Object.assign(TALK, VH_TALK, { capseller: () => ({ pages: ['Caps! Two for one on fizz days. Every day is a fizz day.'] }) });
MARKER_HOOKS.push((id, S) => { const m = vhMarker(S, id); return m === null ? undefined : m; });

// Spring Wages (Q2): a contract player's Vanaheim merit goes to the Gatekeepers, like conquer
const realm0 = Factions.prototype.realm;
Factions.prototype.realm = function () { const r = realm0.call(this); return r === 'embassy' && (this.G.S.flags || {}).vh_contract && VANAHEIM_AREAS[this.G.area] ? 'gate' : r; };

// TALK.warden: swing pages + the 4-ally cap (wardenOptions) on the alliance choice; Spring Wages + Stage B quest steps after it
const warden0 = TALK.warden;
TALK.warden = (S) => {
  const f = S.flags || {}, q = S.quests || {}, i = S.inv || {};
  if (!A(S) && f.vh_contract) {
    if (q.rotwood === 2 && f.rw_spike) return { pages: ['(Burrowmoss weighs the frost-iron spike.) Cold runes. Not elf-work. Your wages, as agreed.', '(Spring Wages paid. The Gatekeepers note the evidence.)'],
      then: (G) => { G.setQuest('rotwood', 3); G.S.gold = (G.S.gold || 0) + 150; G.S.evidence = { ...(G.S.evidence || {}), vanaheim: 'blight_spike' }; G.factions.add('gate', MERIT.rotwood, 'vh_contract'); } };
    if (q.vh_spring === 2) return { pages: ['Clearing! But violet still runs down from the root-cave. The roots will part for a hired hand too.'],
      then: (G) => { G.setQuest('vh_spring', 3); G.factions.add('gate', MERIT.vh_spring, 'vh_contract'); G.setQuest('rotwood', 1); } };
    if (!q.vh_spring) return { pages: ['Spring Wages. Three red caps in the spring, then we talk.'], then: (G) => G.setQuest('vh_spring', 1) };
    return { pages: ['Wages when the water runs clear, hired hand.'] };
  }
  if (A(S) === 'befriend') {
    if (q.vh_spring === 3 && !q.vh_hex && q.rotwood !== 2) return { pages: ['Something whispers in the toadstools at night. "Elf-work, elf-work." Find what\'s whispering and burn it. Three of them, by the sound.'],
      then: (G) => { G.setQuest('vh_hex', 1); G.S.inv.hexknot = G.S.inv.hexknot || 0; } };
    if (q.vh_hex === 1 && (f.vh_knots || 0) >= 3) return { pages: ['Thornhex knots. Beaded with frost. Someone is feeding the hedge-witches, and it isn\'t elves.'],
      then: (G) => { G.setQuest('vh_hex', 3); G.factions.add('embassy', VH_MERIT.vh_hex, 'vh_hex'); } };
  }
  if (A(S) && q.rotwood === 3 && !q.vh_thorn) return { pages: ['The Thorngarden past the village. Frost-thorns, blue at the heart. Cut the roots and Nettlecrown will have to talk to you.'],
    then: (G) => G.setQuest('vh_thorn', 1) };
  const e = warden0(S);
  if (e && e.choice && e.choice.id === 'alliance_vanaheim') return { ...e, pages: [...swingPages(S), ...e.pages], choice: { ...e.choice, options: wardenOptions(S, e.choice.options) } };
  return e;
};

const GREF = {};
function giveCirclet(G) {   // the spare reward (Hearthmoor Story): a unique trinket; regen maps onto progress.mods().regen (HP/s while not chased)
  const S = G.S; S.bag = S.bag || [];
  if ([...S.bag, ...Object.values(S.gear || {})].some((x) => x && x.unique === 'nettle_circlet')) return;
  S.bag.push({ uid: `nettle${Date.now().toString(36)}`, slot: 'trinket', name: 'Nettlecrown\'s Bean-Circlet', rar: 4, lv: Math.max(1, S.lv || 1), unique: 'nettle_circlet',
    mods: { regen: 2 }, gems: [], about: VH_ITEMS.nettle_circlet.about });
}
function endBossAdds(G) { const v = GREF.vana; if (v) v.clearAdds(); }
export const wearsCirclet = (S) => !!(((S.gear || {}).trinket || {}).unique === 'nettle_circlet');

export class Vanaheim {
  constructor(G) { this.G = G; GREF.vana = this; this.ctx = null; this.area = null; this.spots = []; this.boss = null; this.adds = []; this.qaDone = null; this.thornUsed = false;
    G.startBoss = (id) => this.startBoss(id); this.wrap(); }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  get S() { return this.G.S; }
  wrap() {
    const G = this.G, me = this; if (!G.harbor) return;
    const p0 = G.harbor.prompt.bind(G.harbor), i0 = G.harbor.interact.bind(G.harbor), t0 = G.harbor.onTap.bind(G.harbor);
    G.harbor.prompt = (...a) => me.prompt() || p0(...a);
    G.harbor.interact = (...a) => me.interact() || i0(...a);
    G.harbor.onTap = (hit, ...a) => me.onTap(hit) || t0(hit, ...a);
    const C = G.combat; if (C && !C.vhThorns) {   // the circlet's thorns: the first foe to hit you each fight takes 5
      C.vhThorns = 1; const h0 = C.hurtPlayer.bind(C);
      C.hurtPlayer = (dmg, src, push) => {
        const hit = h0(dmg, src, push);
        if (hit && src && !me.thornUsed && wearsCirclet(G.S)) {
          const foe = C.enemies.find((x) => x.a === src || (src.a && x.a === src.a));
          if (foe) { me.thornUsed = true; C.damageEnemy(foe, VH_ITEMS.nettle_circlet.thorns, null, 0, '#7fd8ff'); }
        }
        return hit;
      };
    }
  }
  spot(o) { this.spots.push({ r: 1.6, show: () => true, ...o }); }
  nearSpot() {
    const c = this.ctx; if (!c || this.G.dlg) return null;
    let best = null, bd = 1e9;
    for (const s of this.spots) { if (!s.show()) continue; const d = Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]); if (d < s.r && d < bd) { bd = d; best = s; } }
    return best;
  }
  prompt() { const s = this.nearSpot(); return s ? (typeof s.label === 'function' ? s.label() : s.label) : ''; }
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
  look(name, pages, then) { this.G.openDialogue({ id: 'vh_look', name }, { pages, then }); }
  // ?vhq= QA preset: village | hex | thorn | fight | conquer | spare (yield dialogue open) | contract | cap | tobble
  qaPreset() {
    const v = this.qs().get('vhq'), S = this.S; if (!v || this.qaDone === v) return;
    this.qaDone = v; const f = F_(S), al = (f.alliance = f.alliance || {}); S.quests = S.quests || {};
    const base = () => { al.vanaheim = al.vanaheim || 'befriend'; S.quests.vh_spring = 3; };
    if (v === 'village' || v === 'hex') { base(); if (v === 'hex') S.quests.vh_hex = 1; }
    if (v === 'tobble') { base(); S.quests.rotwood = 3; S.inv.fizzstone = 1; S.inv.glowfry = 1; }
    if (['thorn', 'fight', 'spare', 'conquer'].includes(v)) { base(); if (v === 'conquer') al.vanaheim = 'conquer'; S.quests.rotwood = 3; S.quests.vh_thorn = 1; f.vh_roots = 3; }
    if (v === 'contract') { f.vh_contract = 1; S.quests.vh_spring = 1; }
    if (v === 'cap') { for (const r of ['alfheim', 'svartalfheim', 'jotunheim', 'muspelheim']) al[r] = 'befriend'; delete al.vanaheim; }
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    const gm = ctx.scene.game || (ctx.scene.game = {});
    if (area === 'vanaheim') { this.qaPreset(); if (A(this.S) || F_(this.S).vh_contract || this.qs().has('vhq')) gm.exits = (gm.exits || []).filter((e) => e.to !== 'vh_village').concat([{ ...VILLAGE_PATH }]); }
    if (!AREAS_VH[area]) return;
    this.qaPreset();
    if (area === 'vh_village') this.village(ctx);
    if (area === 'vh_garden') this.garden(ctx);
    const v = this.qs().get('vhq');
    if (area === 'vh_garden' && (v === 'fight' || v === 'spare') && !this.boss && !F_(this.S).vh_nettle) setTimeout(() => { this.startBoss('nettlecrown'); if (v === 'spare') this.qaYield(); }, 400);
  }
  detach() { this.spots = []; this.adds = []; this.boss = null; this.ctx = null; this.area = null; }
  village(ctx) {
    const S = this.S, f = F_(S);
    const KNOTS = [[-6.0, -3.0], [2.4, 2.6], [8.2, -3.6]], SPRING = [-1.2, 1.4], FRY = [6.6, 3.2], SEALS = [[-7.0, 2.8], [0.0, -3.4], [7.4, 1.2]];
    KNOTS.forEach((pos, k) => this.spot({ pos, label: 'Burn the Thornhex knot', show: () => (S.quests || {}).vh_hex === 1 && !((f.vh_knot || {})[k]),
      act: () => { f.vh_knot = { ...(f.vh_knot || {}), [k]: 1 }; f.vh_knots = Object.keys(f.vh_knot).length; this.G.give('hexknot', 1); ctx.effects && ctx.effects.spawn('earth_burst', pos[0], 0, pos[1]);
        this.G.toast(`The knot hisses "elf-work" and burns blue. ${Math.min(3, f.vh_knots)}/3`, 2.2); this.G.refreshMarkers && this.G.refreshMarkers(); } }));
    this.spot({ pos: SPRING, label: 'Scoop a fizzstone from the hidden spring', show: () => (S.quests || {}).vh_tobble === 1 && !(S.inv || {}).fizzstone, act: () => this.G.give('fizzstone', 1) });
    this.spot({ pos: FRY, label: 'Ask a glow-fish fry to volunteer', show: () => (S.quests || {}).vh_tobble === 1 && !(S.inv || {}).glowfry, act: () => this.look('The Fizzing Steps', ['(A tiny fish glows cyan and swims into your jar. It seems thrilled.)'], (G) => G.give('glowfry', 1)) });
    SEALS.forEach((pos, k) => this.spot({ pos, label: 'Set a tithe-seal on the spring', show: () => (S.quests || {}).vh_tithe === 1 && !((f.vh_seal || {})[k]) && (S.inv || {}).tithe_seal,
      act: () => { f.vh_seal = { ...(f.vh_seal || {}), [k]: 1 }; f.vh_seals = Object.keys(f.vh_seal).length; this.G.take('tithe_seal', 1); this.G.toast(`The spring goes quiet under the wax. ${f.vh_seals}/3`, 2.2); } }));
  }
  garden(ctx) {
    const S = this.S, f = F_(S), ROOTS = [[-6.4, -2.6], [-1.0, 2.4], [3.0, -4.2]];
    ROOTS.forEach((pos, k) => this.spot({ pos, label: 'Cut the frost-thorn root', show: () => (S.quests || {}).vh_thorn === 1 && !((f.vh_root || {})[k]),
      act: () => { f.vh_root = { ...(f.vh_root || {}), [k]: 1 }; f.vh_roots = Object.keys(f.vh_root).length; ctx.effects && ctx.effects.spawn('frost_puff', pos[0], 0.3, pos[1]);
        this.G.toast(`The root snaps, cold to the core. ${Math.min(3, f.vh_roots)}/3`, 2.2); } }));
    this.spot({ pos: [6.0, -3.6], r: 2.0, label: 'Nettlecrown\'s seed & tonic stall', show: () => f.vh_nettle === 'spared', act: () => this.G.shopUI && this.G.shopUI.show('nettle') });
    if (f.vh_nettle && ctx.npc && ctx.npc('nettlecrown') && f.vh_nettle !== 'spared') { const a = ctx.npc('nettlecrown'); a.quad && (a.quad.visible = false); a.noTalk = true; }
  }
  // ---------------------------------------------------------------- the boss (Regent spawn pattern, verdant.js)
  role(id) { const A_ = this.ctx && this.ctx.actors; return A_ && A_.meta && A_.meta.roles[id] ? id : PLACEHOLDER_ROLE[id]; }
  startBoss(id) {
    const G = this.G, C = G.combat; if (!C || !this.ctx || id !== 'nettlecrown' || (this.boss && this.boss.state !== 'dead')) return null;
    const npc = this.ctx.npc && this.ctx.npc('nettlecrown'); if (npc && npc.quad) npc.quad.visible = false; if (npc) npc.noTalk = true;
    const P = NETTLE.circle;
    const e = C.spawnEnemy({ id: 'nettlecrown', def: 'nettlecrown', role: this.role('nettlecrown'), pos: P.slice(), once: true, noRespawn: true }, true);
    e.state = 'chase'; e.phaseN = 1; this.boss = e; this.thornUsed = false;
    e.mods = { ...(e.mods || {}), hurt: (en, dmg) => this.nettleHurt(en, dmg) };
    e.onKill = () => { this.boss = null; };
    this.spawnAdds(NETTLE.adds[1], 'P1');
    if (A(this.S) === 'conquer') this.spawnHex();
    G.toast && G.toast('MOTHER NETTLECROWN\n\nThe thorns stand up like hackles.', 3.0);
    return e;
  }
  spawnAdds(n, tag) {
    const P = NETTLE.circle;
    for (let k = 0; k < n; k++) {
      const e = this.G.combat.spawnEnemy({ id: `thornnymph_${tag}_${k}`, def: 'thornnymph', role: this.role('thornnymph'), pos: [P[0] - 2 + 4 * k, P[1] + 2.2], once: true, noRespawn: true }, true);
      e.state = 'chase'; this.adds.push(e);
    }
  }
  spawnHex() {
    const P = NETTLE.circle, e = this.G.combat.spawnEnemy({ id: 'thornhex_0', def: 'thornhex', role: this.role('thornhex'), pos: [P[0] + 3, P[1] - 0.6], once: true, noRespawn: true }, true);
    e.state = 'chase'; e.healT = 0; this.adds.push(e); this.hex = e;
  }
  clearAdds() { const C = this.G.combat; for (const e of this.adds) if (C && e.state !== 'dead' && e.state !== 'gone') C.kill(e, true); this.adds = []; }
  nettleHurt(e, dmg) {
    const D = e.D, floor = Math.ceil(D.hp * D.yieldAt);
    if (e.yieldedVh) return 0;
    const after = e.hp - dmg, f = after / D.hp;
    if (e.phaseN === 1 && f < D.phases[0]) { e.phaseN = 2; this.G.toast && this.G.toast('Nettlecrown tears up her own hedges. The thorns close in.', 2.2); }
    if (e.phaseN === 2 && f < D.phases[1]) { e.phaseN = 3; this.spawnAdds(NETTLE.adds[3], 'P3'); this.G.toast && this.G.toast('"Children! Mother needs you!"', 2.2); }
    if (!e.grabbed && f < D.grabAt) { e.grabbed = 1; this.grab(e); }
    if (after <= floor) { this.yieldNow(e); return Math.max(0, e.hp - floor); }
    return dmg;
  }
  grab(e) {   // heartroot grab at 10 %: one rooting squeeze, stamina drained
    const G = this.G, C = G.combat, p = this.ctx.player;
    if (this.ctx.effects) this.ctx.effects.spawn('earth_burst', p.x, p.y, p.z + 0.05);
    C.hurtPlayer(NETTLE.grabDmg, e.a, 0); C.st = 0;
    G.toast && G.toast('HEARTROOT GRAB! Roots burst up and squeeze. Roll free!', 2.4);
  }
  yieldNow(e) {
    const G = this.G; e.yieldedVh = true; e.state = 'idle'; e.a.act = null; e.cd = 1e9;
    this.clearAdds();
    G.toast && G.toast('Mother Nettlecrown yields.', 2.2);
    setTimeout(() => {
      G.combat.kill(e, true); this.boss = null;
      const npc = this.ctx && this.ctx.npc && this.ctx.npc('nettlecrown'); if (npc && npc.quad) { npc.quad.visible = true; npc.x = e.a.x; npc.z = e.a.z; }
      G.gainXP && G.gainXP(XP.nettlecrown, e.a);   // 600 XP (GD); the quiet kill skips combat's own XP + loot
      G.openDialogue({ id: 'nettlecrown', name: 'Mother Nettlecrown' }, VH_TALK.nettlecrown_after(G.S));
    }, 900);
  }
  qaTalk(id) { const e = TALK[id](this.S); return { pages: e.pages, options: e.choice ? e.choice.options.map((o) => o.label) : [] }; }
  qaYield() { const e = this.boss; if (!e) return; e.hp = Math.ceil(e.D.hp * 0.12); e.phaseN = 3; this.G.combat.damageEnemy(e, e.D.hp, null, 0); }
  update(dt) {
    const C = this.G.combat; if (!this.ctx || !C) return;
    if (this.thornUsed && !C.alive().some((x) => x.state === 'chase')) this.thornUsed = false;   // fight over: the circlet's thorns re-arm
    const h = this.hex, b = this.boss;
    if (h && b && h.state !== 'dead' && h.state !== 'gone' && !b.yieldedVh) {
      h.healT = (h.healT || 0) + dt;
      if (h.healT > NETTLE.healEvery) { h.healT = 0; b.hp = Math.min(b.D.hp, b.hp + VH_ENEMIES.thornhex.healPulse); C.number && C.number(VH_ENEMIES.thornhex.healPulse, b.a.x, b.a.y + 2.4, b.a.z, '#5aec3c'); }
    }
  }
}
