// Hearthmoor: items, quests and every line of dialogue (all original text).
// A talk() entry returns { pages: [...], then?: (G) => void } for the current save state S.
import { PETS, PET_IDS, DEN, petNames, isNight } from './pets.js';
import { clues, tmBraziers, TAMSIN_CLUE } from './temple.js';
import { MERIT } from './factions.js';
import { stormName, stormHere } from './storms.js';

export const ITEMS = {
  loaf:      { name: 'Hearthloaf', icon: 0, about: 'A round loaf, still warm. Smells like Tuesday mornings.' },
  moonpetal: { name: 'Moonpetal', icon: 1, about: 'A pale glade flower. It hums faintly when you are not looking.' },
  coin:      { name: 'Copper bits', icon: 2, about: 'Small, round, and well loved.' },
  acorn:     { name: "Tib's lucky acorn", icon: 3, about: 'Polished smooth by a very small thumb.' },
  tea:       { name: 'Moonpetal tea', icon: 4, about: 'A tin of Wren\'s tea. Calms storms, and also grandparents.' },
  tonic:     { name: 'Hearth tonic', px: 'tonic', about: 'Heals 60 HP. Drink: U, right-stick click, or tap it here.' },
  glowseed:  { name: 'Glow seed', px: 'glowseed', about: 'Hums in the dark. Plant it in a garden plot: it blooms in two days.' },
  // Stage 6.3 (the Old Temple): key items, never sold
  reliefbasket: { name: 'Order relief basket', px: 'reliefbasket', about: 'Hearthloaves, wool blankets and a tin of Wren\'s tea, packed by the Order of the Hearth for the Old Temple.' },
  hearthwrit: { name: 'Hearth writ', px: 'hearthwrit', about: 'A folded writ with the Order\'s wax seal. The Old Temple\'s gate opens for whoever carries it.' },
  alder_charm: { name: 'Warden Aldis\'s lantern charm', px: 'alder_charm', key: true, about: 'A thumb-sized brass lantern on a chain. Grandpa Alder\'s grandmother carried it on the Rift.',
                 aboutLit: 'A thumb-sized brass lantern. A small cold-fire flame burns inside and never gutters.' },
  denbiscuit: { name: 'Den biscuit', px: 'denbiscuit', about: "Signe's oat-and-moonpetal biscuit. Feed your pet once a day (hero screen, Gear tab): bond grows, and its glow doubles for 60 s." },
};
// the Stray Den's three yard lanterns (Hollows brazier rule: S.found.den_l1..3)
export const denLit = (S) => ['den_l1', 'den_l2', 'den_l3'].filter((k) => (S.found || {})[k]).length;

export const QUESTS = {
  bread: {
    title: 'Warm Bread',
    giver: 'Marla the baker',
    steps: { 1: 'Carry the hearthloaf to Bram at the Kettle & Key, down in Bakery Lane.', 3: 'Bram got his loaf while it was warm.' },
  },
  tea: {
    title: 'Moonpetal Tea',
    giver: 'Wren the herbalist',
    steps: { 1: 'Gather 3 moonpetals in Mossglen (through the moss gate on the plaza terrace).', 2: 'Bring the moonpetals back to Wren in Bakery Lane.', 3: 'Wren brewed a tin of moonpetal tea.' },
  },
  cat: {
    title: "Where's Pudding?",
    giver: 'Tib',
    steps: { 1: 'Find Pudding the cat. Tib last saw her chasing a firefly toward the old gate.', 2: 'Pudding is following you. Walk her home to Tib in the plaza.', 3: 'Pudding is home, and already asleep on the bread crate.' },
  },  // Stage 5 part 4: Ravenhold Harbor's first story quest (story: not one of the three Lantern Eve errands; pays Corsair merit)
  // Stage 6 part 1: the Market Terraces gate stays sealed, so Brannoc sends you the other way, by Sable's rift-skiff up to
  // Bifrost Crossing; the Gatekeepers' Guild's gatewright finishes it (a step may be a function of the save)
  harbor: {
    title: 'The Road to the Rift',
    giver: 'Harbormaster Brannoc',
    story: true,
    steps: { 1: 'Take the harbor tally to Quartermaster Sable of the Rift Corsairs, on the east quay.',
             2: (S) => ((S.flags || {}).rh_road
               ? 'Take Sable\'s rift-skiff from Ravenhold\'s east pier up to Bifrost Crossing, and report to the Gatekeepers\' Guild.'
               : 'Climb the harbor stair and look at the Market Terraces gate, then tell Harbormaster Brannoc what you saw.'),
             3: (S) => ((S.flags || {}).bf_done
               ? 'Gatewright Halvard Ness has your name in the Gatekeepers\' Guild ledger. Earn Rift Marks, and the realm gates will open.'
               : 'Brannoc says the way to the Rainbow Rift runs up through the Market Terraces, once the gates open.') },
  },
  // Stage 6 part 2: the Stray Den's side quest (Story bot's pets doc). Stage 3 is hard-wired as done (toast, XP, the
  // errand's 40 Hearth Tokens through onErrand), so the four objectives ride stages 1-2 with flags, like 'harbor'.
  // Stage 6.3: the Old Temple (story quests; sub-progress on flags, stage 3 = done). Story bot's old_temple.md.
  altar: {
    title: 'The Cold Altar',
    giver: 'Warden Hilde of the Hearth',
    story: true,
    steps: { 1: 'Carry the Order\'s relief basket to Mother Ilse at the Old Temple. Show the Hearth writ at the Temple gate in Ravenhold Harbor.',
             2: (S) => (clues(S) < 3 ? `Find out who snuffed the sacred brazier. Look around the altar with Brother Tamsin. Clues: ${clues(S)}/3` : 'Tell Mother Ilse what the clues say.'),
             3: 'The dwarven tools were planted. Someone wanted the Forge Quarter blamed and the Temple dark.' },
  },
  gate: {
    title: 'Keeper of the Gate',
    giver: 'Mother Ilse Brightwater',
    story: true,
    steps: { 1: (S) => { const F = S.flags || {}, inv = S.inv || {};
               if (!inv.alder_charm) return 'Ask Grandpa Alder in Hearthmoor about Warden Aldis. Brother Tamsin\'s ledger says she was a Rift-warden.';
               if (!F.tm_wick) return 'Ask Ida Wickmere, the cold-fire chandler on Ravenhold\'s piers, to light the lantern charm.';
               if (tmBraziers(S) < 3) return `Feed the charm's flame at the 3 dark braziers on the Temple stair (cast a spell at each). ${tmBraziers(S)}/3`;
               return 'The charm burns bright blue. Bring it to Mother Ilse.'; },
             2: (S) => { const F = S.flags || {};
               if (!F.tm_altar) return 'At dusk or after dark, set the lantern charm on the cold altar (E / A).';
               if (!F.tm_gate) return 'Hold the charm up to the dark Rift-gate in the inner court (E / A).';
               if (!F.tm_rift) return 'Seal the rift tearing open above the Rift-gate!';
               return 'Tell Mother Ilse the gate is lit.'; },
             3: 'The Rift-gate burns blue again. Midgard\'s arch at Bifrost Crossing stands open, and the skiff can rest.' },
  },
  strays: {
    title: 'Strays of the Rift',
    giver: 'Signe Larkspur',
    side: true,
    steps: { 1: (S) => { const F = S.flags || {}, n = denLit(S);
               if (n < 3) return `Light the 3 cold-fire lanterns in the Stray Den's yard (cast any spell at one). ${n}/3`;
               if (!F.den_riftOpen) return 'Tell Signe the lanterns are lit.';
               if (!F.den_rift) return 'Seal the little rift behind the Stray Den\'s woodpile.';
               return 'Tell Signe the rift is sealed.'; },
             2: (S) => ((S.flags || {}).den_seed
               ? 'Come back to the Stray Den after dusk and sit by the cold-fire hearth.'
               : 'Bring Signe a glow seed (Odo\'s Wares or Wickmere\'s Chandlery) or a moonpetal.'),
             3: (S) => `${(S.pet && S.pet.name) || 'Your pet'} has a home with you now. The other strays wait at the Den.` },
  },
  // 6.5: the Gatekeepers' Guild's repeatable rift-storm bounty (offered again at the next storm's onset once done)
  stormwatch: {
    title: 'Storm Watch',
    giver: 'Gatewright Halvard Ness',
    side: true, bounty: true,   // bounty: no Hearth payout, never an errand; full XP once, half on repeats (game.js setQuest)
    steps: { 1: (S) => { const n = Math.min(3, (S.storm || {}).sealed || 0);
               return n < 3 ? `Seal 3 rifts during the rift storm (${stormName(S)}). ${n}/3` : 'Report to Gatewright Halvard at Bifrost Crossing.'; },
             2: 'Report to Gatewright Halvard at Bifrost Crossing.',
             3: 'Storm Watch done. The Guild will post another when the next storm breaks.' },
  },
};
// the three Lantern Eve errands (story and side quests do not count toward "quests n/3" or the Rift's opening)
export const errandsDone = (S) => Object.entries(S.quests || {}).filter(([k, v]) => v === 3 && !(QUESTS[k] && (QUESTS[k].story || QUESTS[k].side || QUESTS[k].ripple || QUESTS[k].bounty))).length;   // ripple: 6.4 Vanaheim follow-ups; bounty: 6.5

export const SPELL_NAMES = { sparkle_burst: 'sparkle burst', hearth_flame: 'hearth flame', light_orb: 'light orb', leaf_gust: 'leaf gust', healing_petals: 'healing petals' };

const petals = (S) => S.inv.moonpetal || 0;
const flags = (S) => (S.flags = S.flags || {});
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});   // realm alliances: { vanaheim: 'befriend' | 'conquer' }
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`); };
const gem = (G, id) => { G.S.gems = G.S.gems || {}; G.S.gems[id] = (G.S.gems[id] || 0) + 1; };
const openBank = (G) => { G.S.met = { ...(G.S.met || {}), banker: 1 }; G.shopUI.show('bank'); };
// Bix's riddle lock (the start of "Gnome in the Vault"): a wrong answer earns a hint and a retry, the right one opens drawer nine
const riddleWrong = (G) => { flags(G.S).riddle = 'tried'; return { pages: ['A soft clunk. The lock sulks.', 'A hint, free of charge: think about where you have been, not what you carry.'], then: openBank }; };

export const TALK = {
  // Stage 5 part 3: the Order of the Hearth's warden, the first faction contact (opens the Factions tab)
  hilde(S) {
    const first = !S.met?.hilde;
    return {
      pages: first ? ['Warden Hilde, Order of the Hearth. We keep Midgard\'s lamps lit and its roads walkable.',
                      'Five banners matter out past the Rift: the Hearth, the Gatekeepers\' Guild, the Gnome Council, the Rift Corsairs and the realm embassies. Each remembers what you do for it.',
                      'Run errands, seal rifts, fell the big brutes. Merit adds up: Stranger, Friend, Trusted, Honored, Champion, Legend. Here, your first Hearth Tokens.']
                   : ['Lamps are lit, roads are walkable. Your standing is in the Factions tab (H). Wear a title if you have earned one.'],
      // only the first talk opens the Factions tab (later chats just talk; the tab is on H / the hero screen)
      then: first ? (G) => { const was = G.S.met?.hilde; G.S.met = { ...(G.S.met || {}), hilde: 1 }; if (!was) { G.factions.add('hearth', 20, 'warden'); G.openFactions(); } } : null,
    };
  },
  // ---------------------------------------------------------------- Ravenhold Harbor (Stage 5 part 4)
  harbormaster(S) {
    const q = S.quests.harbor || 0, F = S.flags || {};
    if (!q) return {
      pages: ['Harbormaster Brannoc. Welcome to Ravenhold, at the foot of the Rainbow Rift. Mind the edge, the water is colder than it looks.',
              'Since the Rift tore wider the city shut its district gates: Market Terraces, Forge Quarter, Old Temple, the Undercity. Only the Harbor stays open, because the boats will not wait.',
              'Make yourself useful? This tally is owed to Quartermaster Sable, the Rift Corsairs\' woman on the east quay. She pays the harbor dues, and she pays them late.'],
      then: (G) => { G.setQuest('harbor', 1); },
    };
    if (q === 1) return { pages: ['Sable is on the east quay, by the barrels. Red kerchief, sharper tongue.'] };
    if (q === 2 && !F.rh_gate) return { pages: ['Sable sent you up the stair? Then go and see the Market Terraces gate for yourself. It is right at the top.'] };
    if (q === 2 && !F.rh_road) return {
      pages: ['Barred and chained, aye. The Market Terraces climb from that gate right up toward the Rift, and the city will not open it until the Rift settles.',
              'So you go the other way. Sable\'s rift-skiff rides the Rift\'s under-currents up to Bifrost Crossing, the portal capital. Every realm\'s gate stands there.',
              'Report to the Gatekeepers\' Guild at the Crossing and tell them Brannoc sent you. Here, for the tally and the climb. The skiff is tied up at the east pier.'],
      then: (G) => { G.S.gold = (G.S.gold || 0) + 30; G.toast('+30 gold', 1.8); G.factions.add('corsair', 40, 'harbor');
                     G.S.flags = G.S.flags || {}; G.S.flags.rh_road = 1; G.toast('Sable\'s rift-skiff will take you to Bifrost Crossing.', 2.6); G.setQuest('harbor', 2); },
    };
    if (q === 2) return { pages: ['Sable\'s skiff is tied up at the east pier. Tell the Guild at the Crossing that Brannoc sent you.'] };
    return { pages: (F.bf_done ? ['Back from the Crossing in one piece? Good. The Guild keeps a better ledger than I do, and that is saying something.']
                               : ['The gates will open. Until then, the Harbor is yours to wander. Look up at night: you can see the Rift from the pier ends.']) };
  },
  quartermaster(S) {
    const q = S.quests.harbor || 0, first = !S.met?.sable, F = S.flags || {};
    const hooks = { id: 'sable', options: [
      { label: 'How do I earn Corsair merit?', pick: () => ({ pages: ['Bring me rare cargo. Seal rifts, hunt the big brutes past them, buy from the night trade. The Corsairs remember who is useful.',
                                                                    'Your standing is in the Factions tab (H). Rank up and the harbor treats you kinder.'] }) },
      ...(F.rh_dues ? [] : [{ label: 'Pay the harbor dues (25 gold).', pick: (G) => {
        if ((G.S.gold || 0) < 25) return { pages: ['Twenty-five gold, friend. Come back when your purse has caught up with your manners.'] };
        G.S.gold -= 25; G.S.flags = G.S.flags || {}; G.S.flags.rh_dues = 1; G.factions.add('corsair', 15, 'dues');
        return { pages: ['Paid in full. The Corsairs will remember that you paid without being asked.'] }; } }]),
      { label: 'Just passing through.', cancel: true, pick: () => ({ pages: ['Then pass carefully. The quay is slippery.'] }) },
    ] };
    const meet = (G) => { const was = G.S.met?.sable; G.S.met = { ...(G.S.met || {}), sable: 1 }; if (!was) G.factions.add('corsair', 20, 'sable'); };
    if (q === 1) return {
      pages: ['Brannoc\'s tally? He counts every rope twice. Fine. Sable, quartermaster of the Rift Corsairs. We run cargo through the Rift when the gates let us.',
              'The Market Terraces gate is shut, and every crate I need is stuck above it. Climb the stair and see for yourself, then tell Brannoc the Corsairs want it open.'],
      then: (G) => { meet(G); G.setQuest('harbor', 2); },
    };
    return {
      pages: first ? ['Sable, quartermaster of the Rift Corsairs. The harbor is ours, more or less. The Rift is where the money is.',
                      'Do right by the Corsairs and the Corsairs do right by you. Merit, friend. It adds up.']
                   : ['Back again. Business, or just admiring the boats?'],
      // a pick replaces `then`, so the first meeting's merit rides on every answer (Esc / B picks the cancel one)
      choice: { ...hooks, options: hooks.options.map((o) => ({ ...o, pick: (G) => { meet(G); return o.pick(G); } })) },
    };
  },
  // ---------------------------------------------------------------- Bifrost Crossing (Stage 6 part 1)
  // Gatewright Halvard Ness, the Gatekeepers' Guild's keeper of the gates: finishes 'The Road to the Rift', pays Rift Marks
  gatewright(S) {
    const q = S.quests.harbor || 0, F = S.flags || {}, first = !S.met?.halvard;
    const meet = (G) => { const was = G.S.met?.halvard; G.S.met = { ...(G.S.met || {}), halvard: 1 }; if (!was) G.factions.add('gate', 20, 'halvard'); };
    if (q === 2 && F.rh_road && !F.bf_done) return {
      pages: ['Brannoc sent you on Sable\'s skiff? Then you came the long way round, and the honest way. Gatewright Halvard Ness, Gatekeepers\' Guild. Welcome to Bifrost Crossing.',
              'Nine gates, one bridge, and a ledger for every key. Vanaheim\'s stands open. The other eight want an alliance, or Guild merit, or both: look at any of them and it will tell you what it wants.',
              'Brannoc\'s road is walked. A rift shard for your kit, gold for the skiff fare, and your first Rift Marks in the Guild\'s ledger.'],
      then: (G) => { meet(G); G.S.flags = G.S.flags || {}; G.S.flags.bf_done = 1; gold(G, 50); gem(G, 'rift_shard'); G.toast('+1 Rift shard (a socket gem)', 2.2);
                     G.factions.add('gate', 60, 'road'); G.setQuest('harbor', 3); },
    };
    const hooks = [
      { label: 'How do I earn Rift Marks?', pick: () => ({ pages: ['Seal rifts, any tier, anywhere. Escort travellers, mend portals. Every gate you help keep is a mark in the ledger.',
                                                                  'Rank up and the Guild cuts you keys: Gate Runner first, then Keybearer. Your standing is in the Factions tab (H).'] }) },
      { label: 'Why are the gates sealed?', pick: () => ({ pages: ['Since the Rift tore, every realm guards its own door. Allies walk through; strangers need a key, and the Guild cuts keys only for those with merit.',
                                                                  'And some were frozen shut from the far side. Veyra\'s work. Those want more than a key.'] }) },
      { label: 'Which way is home?', pick: () => ({ pages: ['Sable\'s skiff at the landing sails back down to Ravenhold. The waystone by the plaza links our stones to Midgard\'s roads.'] }) },
      { label: 'Just looking.', cancel: true, pick: () => ({ pages: ['Look all you like. Mind the bridge: it is mostly light.'] }) },
    ];
    return {
      pages: first ? ['Gatewright Halvard Ness, Gatekeepers\' Guild. I keep the gates, the keys and the ledger, in that order.',
                      'You are standing on Bifrost Crossing, between the Nine Realms. Every gate here is lit in its realm\'s colour.']
                   : ['The ledger is open. What do you need?'],
      choice: { id: 'halvard', options: hooks.map((o) => ({ ...o, pick: (G) => { meet(G); return o.pick(G); } })) },
    };
  },
  chandler(S) {
    const first = !S.met?.chandler;
    return {
      pages: first ? ['Ida Wickmere, chandler. Cold-fire for your lantern, rope for your boat, tonics for your knees.',
                      'Those blue lanterns on the piers are mine. Cold-fire does not care about rain, and it does not mind the Rift.']
                   : ['Mind the wax. What will it be?'],
      then: (G) => { G.S.met = { ...(G.S.met || {}), chandler: 1 }; G.shopUI.show('harbor'); },
    };
  },
  dockkid(S) {
    return { pages: (S.found || {}).rh_spring
      ? ['You found the fizzy spring! Don\'t tell the gulls.']
      : ['I\'m fishing for lantern-eels. They only bite at night.', 'There is a spring in the west corner, behind the crates. It fizzes! Brannoc says it is the Rift\'s doing.'] };
  },
  // ---------------------------------------------------------------- Hearthmoor Plaza
  nightmerchant(S) {
    const first = !S.met?.night;
    return {
      pages: first ? ['Shh, the lantern likes it quiet. I\'m Sefa. I walk the roads after dark and only stop where the lamps are kind.',
                      'Rift shards, golem cores, a moon opal or two. Set them in a socket and your kit hums. Rarer stock, fairer to rarer purses.']
                   : ['The lantern found you again. Browse, friend. I leave at first light.'],
      then: (G) => { G.S.met = { ...(G.S.met || {}), night: 1 }; G.shopUI.show('night'); },
    };
  },
  banker(S) {
    const first = !S.met?.banker, F = S.flags || {};
    if (!first && F.riddle !== 'solved') return {
      pages: [F.riddle === 'tried' ? 'Back for drawer nine? The lock is patient. So am I.'
                                  : 'Before the ledger: the Gnome Council fitted drawer nine with a riddle lock. Solve it, and what is inside is yours.',
              '"The more of me you take, the more of me you leave behind." What am I?'],
      choice: { id: 'riddle', options: [
        { label: 'Footsteps.', pick: (G) => { flags(G.S).riddle = 'solved'; gem(G, 'moon_opal'); gold(G, 25); G.factions && G.factions.onRiddle();
            return { pages: ['Click. Drawer nine swings open.', 'A moon opal and twenty-five gold, Council seal and all. They will want to meet a mind like yours someday.'], then: openBank }; } },
        { label: 'Bread crumbs.', pick: riddleWrong },
        { label: 'Copper coins.', pick: riddleWrong },
        { label: 'Not now. Just the vault, please.', cancel: true, pick: () => ({ pages: ['Of course. The lock keeps.'], then: openBank }) },
      ] },
    };
    if (F.riddle === 'solved') return { pages: ['Keys, ledger, lantern. Drawer nine has hummed contentedly since you opened it. Deposit or withdraw?'], then: openBank };
    return {
      pages: first ? ['Bix Coppertuft, clerk of the Nine Keys Bank. Small desk, deep vault.',
                      'Forty slots, shared by every hero who carries your name. Gear, gems, gold. Banked gold stays put when you faint.']
                   : ['Keys, ledger, lantern. Deposit or withdraw?'],
      then: (G) => { G.S.met = { ...(G.S.met || {}), banker: 1 }; G.shopUI.show('bank'); },
    };
  },
  merchant(S) {
    const first = !S.met?.merchant;
    return {
      pages: first ? ['Odo Fairweather, purveyor of useful things! Tonics for scrapes, glow seeds for later, honest kit for now.',
                      'And whatever you haul out of Mossglen, I\'ll buy. Rarer finds fetch a rarer price.']
                   : ['Back again! Let\'s see what you\'ve got.'],
      then: (G) => { G.S.met = { ...(G.S.met || {}), merchant: 1 }; G.shopUI.show('hearthmoor'); },
    };
  },
  baker(S) {
    const q = S.quests.bread;
    if (q === 0) return {
      pages: [
        'Oh, a new face! Welcome to Hearthmoor. I\'m Marla. If it\'s round and golden, I baked it.',
        'Would you do me a kindness? Bram at the Kettle & Key ordered a hearthloaf, and my feet have done enough stairs today.',
        'Take the lane south, out past the hedges, and you\'ll come down into Bakery Lane. The inn has the kettle on its sign.',
      ],
      then: (G) => { G.give('loaf', 1); G.setQuest('bread', 1); },
    };
    if (q === 1) return { pages: ['Off you go, before it cools! South down the lane, then look for the kettle sign.'] };
    return { pages: [
      'Bram says it was the best loaf of the week. He says that every week, but I like hearing it.',
      'If you ever want to watch the oven at dusk, the crust goes the colour of lamplight.',
    ] };
  },
  kid(S) {
    const q = S.quests.cat;
    if (q === 0) return {
      pages: [
        'Have you seen Pudding? She\'s orange, and round, and she thinks she\'s in charge.',
        'She was chasing a firefly up the terrace this morning... toward the old moss gate. Grandpa says it goes somewhere green.',
        'Could you look for her? Please? She comes when you say her name nicely.',
      ],
      then: (G) => G.setQuest('cat', 1),
    };
    if (q === 1) return { pages: ['The gate is on the terrace, past Marla\'s cottage. It swirls! I\'m not allowed through it on my own.'] };
    if (q === 2) return {
      pages: [
        'PUDDING! You found her! Where were you, you silly loaf of a cat?',
        'She smells like moss and flowers. ...Here. This is my lucky acorn. It\'s for heroes.',
      ],
      then: (G) => { G.catHome(); G.give('acorn', 1); G.setQuest('cat', 3); G.learn('leaf_gust'); },
    };
    return { pages: ['Pudding is asleep on the bread crate again. Marla pretends to mind.', 'Race you to the top of the stairs!'] };
  },
  elder(S) {
    if (S.quests.cat === 3 && S.quests.tea === 3 && S.quests.bread === 3) return { pages: [
      'Bread delivered, tea brewed, cat home. That\'s a proper day\'s work in Hearthmoor.',
      'Sit a while. The lamps will be on soon, and the fireflies always come to see them.',
    ] };
    return { pages: [
      'That old gate up on the terrace hums when the moss is happy. Today it\'s practically singing.',
      'Step into the swirl and you\'ll come out in Mossglen. Mind your manners with the owl.',
    ] };
  },
  cat(S) {
    if (S.cat === 'home') return { pages: ['Pudding blinks slowly at you. That means friend.'] };
    if (S.cat === 'follow') return { pages: ['Pudding bumps her head against your boot. Onward, apparently.'] };
    return {
      pages: [
        'A stripy cat is sitting by the shrine, watching the fireflies with enormous seriousness.',
        'Her collar tag says: "PUDDING. If found, return to Tib, Hearthmoor Plaza. She likes crusts."',
        '"Pudding?" you say, nicely. She considers this, then trots over to your feet.',
      ],
      then: (G) => { if (!G.S.quests.cat) G.setQuest('cat', 1); G.catFollow(); G.setQuest('cat', 2); },
    };
  },

  // ---------------------------------------------------------------- Bakery Lane
  innkeeper(S) {
    const q = S.quests.bread;
    if (q === 1) return {
      pages: [
        'Is that... a hearthloaf? Still warm? You are a marvel, friend.',
        'Here, a few copper bits for your trouble. And a trick my grandmother taught me: snap your fingers at a cold hearth.',
      ],
      then: (G) => { G.take('loaf', 1); G.give('coin', 3); G.setQuest('bread', 3); G.learn('hearth_flame'); },
    };
    const L = (S.flags || {}).lantern;
    // Bram's Lantern Eve wish: who you float your lantern for changes his gift and what he says after
    if (q === 3 && !L) return {
      pages: ['Room\'s warm, stew\'s warmer, and the bread was perfect.',
              'It\'s Lantern Eve tonight. Everyone floats a fish-orb lantern up toward the Rift with a wish for someone. Who is yours for?'],
      choice: { id: 'lantern', options: [
        { label: 'My family.', pick: (G) => { flags(G.S).lantern = 'family'; G.give('tonic', 2);
            return { pages: ['Family it is. Here, two Hearth tonics. Family worries most about scrapes, so humour them.'] }; } },
        { label: 'All of Hearthmoor.', pick: (G) => { flags(G.S).lantern = 'hearth'; gold(G, 30);
            return { pages: ['The whole village? Then the village fund thanks you: thirty gold. Pass it forward when you can.'] }; } },
        { label: 'Whoever is lost out there.', pick: (G) => { flags(G.S).lantern = 'lost'; G.give('glowseed', 2);
            return { pages: ['For the lost... Take these glow seeds. Plant them where a lost traveller might see the light.'] }; } },
        { label: 'I\'ll decide later.', cancel: true, pick: () => ({ pages: ['No rush. The lanterns go up at dusk.'] }) },
      ] },
    };
    if (q === 3) return { pages: [
      L === 'family' ? 'Your lantern\'s the one with the little green fish, isn\'t it? Your family will see it from anywhere.'
        : L === 'hearth' ? 'Half the lane says you floated a lantern for all of us. Stew\'s on the house, always.'
        : 'Saw your lantern drift east, toward the dark hills. Someone out there will follow it home.',
      'The laundry over the stairs? That\'s mine. Mind the socks.'] };
    return { pages: ['Welcome to the Kettle & Key. We\'re waiting on Marla\'s bread for supper, if you\'re heading up to the plaza.'] };
  },
  // Vanaheim (Stage 4): Elder Burrowmoss, spring-warden of Mossbrook. The realm's befriend-or-conquer choice: it only
  // sets the alliance flag for now (S.flags.alliance.vanaheim = 'befriend' | 'conquer'); later stages read it
  warden(S) {
    const A = ((S.flags || {}).alliance || {}).vanaheim;
    if (!A) return {
      pages: ['Hmph. A Midgard face, come through the Rift. I\'m Burrowmoss, warden of the Mossbrook springs.',
              'Someone poisoned our spring and burned elf-runes into the moss. Alfheim\'s mark, plain as day. The spores woke angry, and the moss golems with them.',
              'Mossbrook is choosing sides in all this. So, hearth-walker: what are you to Vanaheim?'],
      choice: { id: 'alliance_vanaheim', options: [
        { label: 'A friend. I\'ll help heal the springs.', pick: (G) => { ally(G.S).vanaheim = 'befriend'; G.toast('Vanaheim: befriended', 2.2);
            return { pages: ['Ha! Then you\'re welcome in Mossbrook. Calm the spores in the glade, and mind those runes: they don\'t smell like elf-work to me.',
                             '(Vanaheim is your friend now. Its gate will stay open to you.)'] }; } },
        { label: 'Vanaheim will bow to Hearthmoor.', pick: (G) => { ally(G.S).vanaheim = 'conquer'; G.toast('Vanaheim: conquered', 2.2);
            return { pages: ['...So it\'s like that. Then take what you can, Midgarder. Mossbrook won\'t forget it.',
                             '(Vanaheim stands against you now. Its people will remember.)'] }; } },
        { label: 'I\'m only passing through.', cancel: true, pick: () => ({ pages: ['Then pass carefully. The spores don\'t care whose side you\'re on.'] }) },
      ] },
    };
    return { pages: [A === 'befriend'
      ? 'Friend of Mossbrook! The spring still tastes of violet. Whoever did this wanted us blaming the elves.'
      : 'You again. Say what you came to say, Midgarder, and go.'] };
  },
  herbalist(S) {
    const q = S.quests.tea;
    if (q === 0) return {
      pages: [
        'Hold still, the petals do the work. ...There. Hello! I\'m Wren. You have kind hands, so you must like plants.',
        'I\'m brewing moonpetal tea for the winter shelf, but moonpetals only grow in Mossglen, through the moss gate.',
        'Could you bring me three? They glimmer, you can\'t miss them. Just walk over one to pick it.',
      ],
      then: (G) => G.setQuest('tea', petals(G.S) >= 3 ? 2 : 1),
    };
    if (q === 1) return { pages: [`${petals(S)} of 3 so far. The gate is up on the plaza terrace, by Marla\'s cottage.`] };
    if (q === 2) return {
      pages: [
        'Three moonpetals! Oh, they\'re humming. That means they\'re happy.',
        'Here: the first tin of the batch is yours. And let me show you how to hold a little light in your hand.',
      ],
      then: (G) => { G.take('moonpetal', 3); G.give('tea', 1); G.setQuest('tea', 3); G.learn('light_orb'); },
    };
    return { pages: ['The tea is steeping beautifully. The whole lane smells like a summer night.'] };
  },
  musician() { return { pages: ['Requests? I know three songs and all of them are about bread.', 'This one\'s called "Crust". It\'s about bread.'] }; },
  gardener() { return { pages: ['The geraniums like the dusk best. So do I.', 'If you see Wren, tell her the mint is trying to escape again.'] }; },
  dog() { return { pages: ['Biscuit wags so hard his whole back half wags too.'] }; },
  chicken() { return { pages: ['Bawk.', 'Mrs. Cluck regards you with one eye, then the other. You pass inspection.'] }; },

  // ---------------------------------------------------------------- Mossglen
  owl() { return { pages: ['Hoo. Hoo-hoo.', '(The owl looks at the shrine, then at you, then at the shrine. You feel welcome.)'] }; },
  keeper(S) {
    if (S.quests.tea === 1 && petals(S) < 3) return { pages: ['Moonpetals? They grow where the fireflies sleep. Look for the glimmer, down by the stones and up by the lanterns.'] };
    return { pages: [
      'The moss remembers every footstep. Walk kindly and it will hum for you.',
      'The gate will always take you home. Hearthmoor is only a swirl away.',
    ] };
  },
};

// ---------------------------------------------------------------- the Stray Den (Stage 6 part 2): Signe Larkspur
const DEN_NPC = { id: 'den', name: 'The Stray Den' };
const petName = (S) => (S.pet && S.pet.name) || 'your pet';
const PICK_SAY = {
  wispkit: 'The wisp kit flares so bright the whole Den goes blue. That\'s a yes, if you were wondering.',
  glowmoth: 'The glow-moth settles on your shoulder like it\'s always lived there. Moths don\'t do that for just anyone.',
  lanternfox: 'The fox kit flops onto your boots, tail-lantern thumping. The little fish does a loop. Smitten, both of them.',
};
function namePet(G, id, name) {
  return {
    pages: [`There. ${name} is yours, and you're ${name}'s, which is the bigger job.`,
            'Three Den biscuits, a little gold for the road, and a good word to the Order. They like a pet with a home.',
            'The other two can stay with me. Come back when you\'re ready for more company, or for a swap.'],
    then: (G) => {
      const S = G.S; S.pets = S.pets || {};
      S.pets[id] = { name, bond: 1, fed: 0, lastFed: null };
      if (G.pets) G.pets.adopt(id, name); else S.pet = { id, name, bond: 1 };
      gold(G, 25); G.give('denbiscuit', 3); flags(S).den = 1;
      G.setQuest('strays', 3);   // 'Side quest done', XP, and the errand's +40 Hearth Tokens (onErrand): no new merit key
      G.toast(`✦ ${name} the ${PETS[id].species} joined you. Aura: ${PETS[id].aura.name}. (One pet at a time. Swap at the Stray Den.)`, 4);
    },
  };
}
function pickPet(G, id) {
  const names = petNames(G.S, id);
  return {
    pages: [PICK_SAY[id], 'Now it\'ll need a name. Something short, so it comes when you call.'],
    choice: { id: 'pet_name', options: [...names.map((n) => ({ label: n, pick: (G) => namePet(G, id, n) })),
                                        { label: `Just "${PETS[id].name}".`, pick: (G) => namePet(G, id, PETS[id].name) }] },
  };
}
function denNight(G) {
  G.openDialogue(DEN_NPC, {
    pages: ['You sit by the hearth. The cold-fire burns low and blue. One by one, three small lights creep out.',
            'A wisp kit bobs up first, humming like a kettle. It bumps your knee and fizzes.',
            'A glow-moth lands on your sleeve, fanning violet eyespots. It smells of old books and summer.',
            'A fox kit pads out last. Its round tail-lantern glows red, and a tiny light-fish swims inside it.',
            'Signe: "They\'ve all picked you. Rude of them, really. You only get to pick one, though."'],
    choice: { id: 'pet_pick', options: [
      { label: 'The wisp kit. (A cold-fire light, quicker spells.)', pick: (G) => pickPet(G, 'wispkit') },
      { label: 'The glow-moth. (Finds hidden things, better healing.)', pick: (G) => pickPet(G, 'glowmoth') },
      { label: 'The lantern-fox. (Senses rifts, more Rift Marks.)', pick: (G) => pickPet(G, 'lanternfox') },
      { label: 'I need a minute.', cancel: true, pick: () => ({ pages: ['Take your time. They\'re not going anywhere. Well. They might.'] }) },
    ] },
  });
}
function denSwap(G) {
  const S = G.S, cur = S.pet && S.pet.id, others = PET_IDS.filter((k) => (S.pets || {})[k] && !S.pets[k].atDen && k !== cur);
  if (!others.length) return { pages: ['Swap? You\'ve only the one. Adopt another stray first, then we\'ll talk baskets.'] };
  return { pages: ['Who\'s coming with you?'], choice: { id: 'den_swap', options: [
    ...others.map((k) => ({ label: `${S.pets[k].name} the ${PETS[k].species}. (${PETS[k].aura.name})`, pick: (G) => {
      const old = petName(G.S); G.pets.swap(k);
      G.toast(`(${G.S.pet.name} shakes off the basket straw and falls in beside you.)`, 2.6);
      return { pages: [`Swapping? ${old} gets the warm basket. ${G.S.pet.name}, up you get. No sulking, either of you.`] }; } })),
    { label: 'Never mind.', cancel: true, pick: () => null },
  ] } };
}
function buyBiscuit(G) {
  if ((G.S.gold || 0) < DEN.biscuit) return { pages: ['Six gold, love. The strays are cheap. The biscuits aren\'t.'] };
  G.S.gold -= DEN.biscuit; G.give('denbiscuit', 1);
  return { pages: ['Oat and moonpetal. Don\'t eat them yourself. Everyone tries it once.'] };
}
function denAdopt(G) {
  const S = G.S, left = PET_IDS.filter((k) => !(S.pets || {})[k] && !PETS[k].gift);   // gift pets (the moss-pup) arrive on their own
  if (!left.length) return { pages: ['Every stray in the Den has a name now. The Rift will send more. It always does.'] };
  if (!G.factions.has('hearth', 1)) return { pages: ['I don\'t hand out strays to just anyone. Get the Hearth to call you Friend, then we\'ll talk.'] };
  return { pages: ['Which one?'], choice: { id: 'den_adopt', options: [
    ...left.map((k) => ({ label: `The ${PETS[k].species}. (${PETS[k].aura.name}, ${DEN.adopt} gold)`, pick: (G) => {
      if ((G.S.gold || 0) < DEN.adopt) return { pages: [`A forty-gold gift to the Den, and the ${PETS[k].species} goes home with you. It's a donation, not a sale. Come back with forty.`] };
      G.S.gold -= DEN.adopt;
      return { pages: [`A forty-gold gift to the Den, and the ${PETS[k].species} goes home with you. It's a donation, not a sale.`, PICK_SAY[k]],
               then: (G) => G.openDialogue(DEN_NPC, adoptName(G, k)) }; } })),
    { label: 'Not today.', cancel: true, pick: () => null },
  ] } };
}
function adoptName(G, id) {
  const done = (n) => ({ pages: [`${n} it is. Mind the biscuits, ${n}.`], then: (G) => { G.S.pets[id] = { name: n, bond: 1, fed: 0, lastFed: null }; G.pets.swap(id);
    G.toast(`✦ ${n} the ${PETS[id].species} joined you. Aura: ${PETS[id].aura.name}.`, 3); } });
  return { pages: ['Now it\'ll need a name. Something short, so it comes when you call.'],
           choice: { id: 'pet_name', options: [...petNames(G.S, id).map((n) => ({ label: n, pick: () => done(n) })), { label: `Just "${PETS[id].name}".`, pick: () => done(PETS[id].name) }] } };
}
// a gift pet (the moss-pup): name it, then it falls in beside you (the old pet goes to the warm basket)
function giftName(G, id) {
  const done = (n) => ({ pages: [`${n} it is. Mind the carrots, ${n}.`], then: (G) => { const own = G.S.pets[id]; own.name = n; own.bond = own.bond || 1; own.fed = own.fed || 0;
    G.pets.swap(id); G.toast(`✦ ${n} the ${PETS[id].species} joined you. Aura: ${PETS[id].aura.name}. (Swap at the Stray Den.)`, 3); } });
  return { pages: ['Now it\'ll need a name. Something short, so it comes when you call.'],
           choice: { id: 'pet_name', options: [...petNames(G.S, id).map((n) => ({ label: n, pick: () => done(n) })), { label: `Just "${PETS[id].name}".`, pick: () => done(PETS[id].name) }] } };
}
function denHubLine(S) {
  const F = S.flags || {}, A = F.alliance || {}, nm = petName(S);
  if (F.storm === 'bifrost') return 'Storm\'s up. The strays are under the floor again. Bring a light if you\'re staying.';
  if (F.fainted_recent) return `Heard ${nm} hauled you home again. Biscuit for ${nm}. Nothing for you, you know what you did.`;
  if (F.gateday) return 'Gate Day! Every stray in the Crossing turns up for the fish lanterns. Even the ones who don\'t eat fish.';
  if (S.pet && (S.pet.bond || 1) >= 3) return `${nm} looks at you like you hung the moon. Took me thirty years to get that look from a cat.`;
  if (A.vanaheim === 'befriend') return 'The moss-pups heard you\'re a friend of Mossbrook. They\'ve been wagging since breakfast.';
  if (A.vanaheim === 'conquer') return 'A stray came in from Mossbrook, singed and shaking. I don\'t ask whose side you\'re on. I just ask.';
  if (isNight(S.t || 0)) return 'Shh. The moths are reading. Well, sitting on books. Same thing.';
  if ((S.pets || {}).mosspup && !S.pets.mosspup.atDen) return 'Your moss-pup found a spring under my floor. I have a pond in my kitchen now. Thank you.';
  if (A.vanaheim === 'conquer' && !F.den_nopups) { F.den_nopups = 1; return 'Mossbrook\'s sent no pups this season. Can\'t think why.'; }
  if (Object.keys(A).length && !F.halvard_betrayal) return 'Funny thing. Not one stray will go near the Gatewright. Animals can be wrong. Not often.';
  return 'Strays fed, hearth lit, roof mostly on. What can the Den do for you?';
}
const DEN_TALK = {
  denkeeper(S) {
    const q = S.quests.strays || 0, F = S.flags || {};
    const meet = (G) => { G.S.met = { ...(G.S.met || {}), signe: 1 }; };
    if (!q && !F.bf_done) return { pages: ['The Den\'s shut to new faces till the Guild has your name. Go and see Halvard first, then come back.'] };
    if (!q) return {
      pages: ['Mind the basket! Signe Larkspur, keeper of the Stray Den. Everything in here fell out of the Rift and landed on me.',
              'Since Lantern Eve the tears keep spitting out strays. Wisps, moths, a fox kit with a lamp for a tail.',
              'Three new ones came through last night, and they\'re hiding under the floor. Will you help me coax them out?',
              'Strays creep toward a kind light. Light my three yard lanterns. Any spell will do.'],
      then: (G) => { meet(G); G.setQuest('strays', 1); },
    };
    if (q === 1 && denLit(S) < 3) return { pages: ['Any spell will do. Cold-fire catches on anything that means well.'] };
    if (q === 1 && !F.den_riftOpen) return {
      pages: ['Look at that, three noses! ...Oh. And a tear behind the woodpile. No wonder they won\'t come out.',
              'It\'s only a little one. Seal it for me? I\'ll hold the biscuits.'],
      then: (G) => { flags(G.S).den_riftOpen = 1; G.rifts.open(0, G.ctx.scene.game.den.rift, { tag: 'den' }); G.refreshMarkers(); G.drawLog && G.drawLog(); },
    };
    if (q === 1 && !F.den_rift) return {
      pages: ['Behind the woodpile. Cold-fire wraiths hate a lit yard, so stay near the lanterns if it gets busy.'],
      // the tear closed some other way (an area change, a faint): open it again so the quest can never stall
      then: (G) => { if (G.rifts && !G.rifts.cur) G.rifts.open(0, G.ctx.scene.game.den.rift, { tag: 'den' }); },
    };
    if (q === 1) return {
      pages: ['Sealed! You\'ve a steady hand. Now they need something that smells like somewhere.',
              'A glow seed hums like a garden at night. Odo and Ida Wickmere both sell them. A moonpetal works too.'],
      then: (G) => G.setQuest('strays', 2),
    };
    if (q === 2 && !F.den_seed) {
      if (!((S.inv.glowseed || 0) + (S.inv.moonpetal || 0))) return { pages: ['A glow seed or a moonpetal. Anything that hums. Strays trust a hum.'] };
      return {
        pages: ['That hum! Hear it? The whole floor just went quiet to listen.',
                'Now we wait for dusk. Strays are brave in the dark, same as wisps. Come back after sundown and sit by the hearth.'],
        choice: { id: 'den_dark', options: [
          { label: 'I\'ll come back after dark.', cancel: true,
            pick: (G) => { takeHum(G); flags(G.S).den_seed = 1; G.refreshMarkers(); return { pages: ['Rest at an inn if you like. Night comes quicker that way.'] }; } },
          { label: 'Can we make it dark now?',
            pick: (G) => { takeHum(G); flags(G.S).den_seed = 1; flags(G.S).den_dark = 1;
                           return { pages: ['Ha. I\'ll draw the shutters. The Den\'s dark enough inside. Sit, sit.'], then: denNight }; } },
        ] },
      };
    }
    if (q === 2) {
      if (F.den_dark || isNight(S.t || 0)) return { pages: [isNight(S.t || 0) ? 'There you are. Hearth\'s lit, and the floor\'s gone very quiet. Sit.' : 'Shutters are still drawn. Sit, sit.'], then: denNight };
      return { pages: ['Not yet. Strays are brave in the dark. Come back after sundown, or ask me to draw the shutters.'],
               choice: { id: 'den_dark', options: [
                 { label: 'I\'ll come back after dark.', cancel: true, pick: () => ({ pages: ['Rest at an inn if you like. Night comes quicker that way.'] }) },
                 { label: 'Can we make it dark now?', pick: (G) => { flags(G.S).den_dark = 1; return { pages: ['Ha. I\'ll draw the shutters. Sit, sit.'], then: denNight }; } },
               ] } };
    }
    if ((S.pets || {}).mosspup && S.pets.mosspup.atDen) return {   // the moss-pup arrives from Mossbrook (6.4 befriend path)
      pages: ['A gnome in a toadstool hat dropped this one off. Said it\'s from Mossbrook, with love and mud. Mostly mud.',
              'It\'s yours. Gifts aren\'t mine to keep, more\'s the pity. It\'s already dug up my carrots.'],
      then: (G) => { G.S.pets.mosspup.atDen = 0; G.openDialogue(DEN_NPC, giftName(G, 'mosspup')); },
    };
    return {
      pages: [denHubLine(S)],
      choice: { id: 'den', options: [
        { label: 'Swap my pet.', pick: (G) => denSwap(G) },
        { label: 'Buy Den biscuits (6 gold).', pick: (G) => buyBiscuit(G) },
        { label: 'Adopt another stray.', pick: (G) => denAdopt(G) },
        { label: 'Tell me about pet auras.', pick: () => ({ pages: [
          'Every pet hums a little aura. Small, but it adds up, like biscuits.',
          'Feed a biscuit once a day and the bond grows. At three hearts, the aura grows with it.',
          'At night your pet\'s glow is a light pool. Wraiths keep out of it, same as a lantern.'] }) },
        { label: 'Just visiting.', cancel: true, pick: () => ({ pages: ['Visit any time. Knock softer on the way out.'] }) },
      ] },
    };
  },
};
// the hum for the strays: a glow seed first, else a moonpetal
const takeHum = (G) => { if ((G.S.inv.glowseed || 0) > 0) G.take('glowseed', 1); else if ((G.S.inv.moonpetal || 0) > 0) G.take('moonpetal', 1); };
Object.assign(TALK, DEN_TALK);

// ---------------------------------------------------------------- the Old Temple (Stage 6.3): Ilse, Tamsin, Edda, refugees + hooks
const dark = (S) => isNight(S.t || 0);
const OT = {
  priestess(S) {
    const qa = S.quests.altar || 0, qg = S.quests.gate || 0, F = S.flags || {}, inv = S.inv || {};
    if (qa === 1 && inv.reliefbasket) return {
      pages: ['Bread, blankets and Wren\'s tea. The Order remembered us. Bless you, and bless your aching arms.',
              'Mother Ilse Brightwater. I keep this Temple, and its flame. Kept. Three nights ago the sacred brazier went out.',
              'It has burned since the Rift was young. Cold fire doesn\'t go out on its own. Someone put it out.',
              'The watch found dwarven forge tongs at the altar and blamed the Forge Quarter. I\'d like better proof than tongs.',
              'Brother Tamsin is up in the nave with his ledgers. Look around with him. Tell me what the Temple tells you.'],
      then: (G) => { G.take('reliefbasket', 1); G.S.met = { ...(G.S.met || {}), ilse: 1 }; flags(G.S).ways = { ...(flags(G.S).ways || {}), temple: 1 };
                     G.factions.add('hearth', MERIT.refuge, 'refuge'); G.setQuest('altar', 2); },
    };
    if (qa === 2 && clues(S) < 3) return { pages: ['Look at the altar with Tamsin\'s eyes. He sees ink. You see the rest.'] };
    if (qa === 2) return {
      pages: ['Cold tongs. Footprints walking the wrong way. A snuffer with no name on it.',
              'Nobody from the Forge Quarter did this. Someone wanted Ravenhold fighting itself, and the Temple dark while it did.',
              'I\'ll send word to the watch before anyone burns a forge. Thank you. Now for the harder thing.',
              'A brazier lit by the Rift can only be relit by cold fire carried in a warden\'s lantern. The wardens are long gone.',
              ...(inv.alder_charm ? ['...Is that a warden\'s charm on your belt? Grandpa Alder\'s? Well. The Temple provides.']
                                  : ['Tamsin: "But! The ledger lists a Hearthmoor warden, three lifetimes back. Warden Aldis. Ring any bells?"',
                                     'Go home and ask, then. Hearthmoor folk keep everything. Especially lanterns.'])],
      then: (G) => { G.setQuest('altar', 3); G.factions.add('hearth', MERIT.altar, 'altar'); gold(G, 30); G.setQuest('gate', 1); },
    };
    if (qg === 1 && !(inv.alder_charm && F.tm_wick && tmBraziers(S) >= 3)) return { pages: [!inv.alder_charm ? 'Grandpa Alder, in Hearthmoor. Ask him about Warden Aldis.'
      : !F.tm_wick ? 'Ida Wickmere on the piers has the best cold-fire wick in Midgard. Ask her to light the charm.' : 'Feed the flame at the stair braziers. All three. It\'s hungry.'] };
    if (qg === 1) {
      const go = (G) => { G.setQuest('gate', 2); };
      return {
        pages: ['That blue. Oh, that\'s the right blue. I\'d almost forgotten it.',
                'Cold fire burns truest in the dark. Set the charm on the altar at dusk or after. I\'ll ring the old bell.'],
        choice: { id: 'tm_rite', options: [
          ...(dark(S) ? [{ label: 'It\'s dark. I\'m ready.', pick: (G) => { go(G); return { pages: ['Then go. I\'ll be right behind you.'] }; } }] : []),
          { label: 'Rest on a refugee cot until dusk.', pick: (G) => { go(G); if (G.ctx) G.ctx.clock.set(0.76); G.S.t = G.ctx ? G.ctx.clock.t : 0.76;
              return { pages: ['The cot is lumpy, the blanket smells of goats, and you sleep like a stone. Dusk comes blue.'] }; } },
          { label: 'Not yet.', cancel: true, pick: () => ({ pages: ['The altar will wait. It\'s had practice.'] }) },
        ] },
      };
    }
    if (qg === 2 && !F.tm_rift) return { pages: [!F.tm_altar ? 'The altar, at dusk or after. I\'ll be right behind you.' : !F.tm_gate ? 'Now the gate. Hold the charm up to it.' : 'The sky! Seal it, before it widens!'] };
    if (qg === 2) return {
      pages: [...(F.met_veyra ? ['The Rift-Warden. I thought the wardens were a bedtime story. She looked so tired.'] : []),
              'The flame\'s lit, the gate\'s lit, and my refugees are cheering at a hole in the sky. What a week.',
              'The Rift-gate opens onto Bifrost Crossing, and Midgard\'s arch there opens back to us. Go where you\'re needed.',
              'Keep the charm. It\'s yours now. A warden\'s lantern shouldn\'t sit on a shelf.'],
      then: (G) => { const Fx = flags(G.S); Fx.temple_lit = 1; G.setQuest('gate', 3);
                     G.factions.add('hearth', MERIT.relight, 'relight'); gold(G, 60); gem(G, 'frost_core'); G.toast('+1 Frost core (a socket gem)', 2.2);
                     G.toast('The Rift-gate to Bifrost Crossing is open. Midgard\'s arch is lit.', 3.0);
                     if (G.temple && G.area === 'temple') G.temple.attach(G.ctx, 'temple'); },
    };
    if (qg === 3) {
      const A = F.alliance || {};
      const line = dark(S) ? 'Listen. You can hear the brazier hum at night. It sounds pleased with itself.'
        : A.vanaheim === 'befriend' ? 'A gnome from Mossbrook came to pray. Or to steal candles. Either way, he left a bun.'
        : A.vanaheim === 'conquer' ? 'Mossbrook folk came through the gate today. They didn\'t look at you kindly. I gave them soup anyway.'
        : (F.met_veyra && !F.ilse_veyra) ? 'I keep thinking of the Warden. Someone that tired shouldn\'t be holding the Rift alone.'
        : 'Flame\'s lit. Soup\'s on. Sit if you like. The Temple has room again.';
      return { pages: [line], then: (G) => { if (line.includes('Warden')) flags(G.S).ilse_veyra = 1; } };
    }
    return { pages: ['Soup\'s hot, flame\'s out. One of those is my fault. Not the flame.'] };
  },
  archivist(S) {
    const F = S.flags || {}, qa = S.quests.altar || 0, first = !S.met?.tamsin;
    if (first) return {
      pages: ['Oh! A visitor who isn\'t a refugee or a watchman. Tamsin, archivist. Mind the ledgers. They don\'t bite. They fall over.',
              'Mother Ilse wants proof. I have opinions, which isn\'t the same. Look around the altar. I\'ll write down what you find.',
              'And don\'t mind the statues. They turn their masks toward the Rift at night. Probably the wind. Probably.'],
      then: (G) => { G.S.met = { ...(G.S.met || {}), tamsin: 1 }; },
    };
    if (qa === 2 && F.tm_lastclue && TAMSIN_CLUE[F.tm_lastclue]) return { pages: [TAMSIN_CLUE[F.tm_lastclue]], then: (G) => { delete flags(G.S).tm_lastclue; } };
    if (qa === 2) return { pages: ['Look by the altar\'s foot, behind the statues, and along the floor. Floors are honest.'] };
    if (dark(S)) return { pages: ['The statues turned toward the gate again last night. I wrote it down. Twice. In capitals.'] };
    if (F.met_veyra && !F.tamsin_veyra) return { pages: ['She sealed it with two fingers. Two! The ledger says the old order needed a whole choir.'], then: (G) => { flags(G.S).tamsin_veyra = 1; } };
    if (F.temple_lit && !F.tamsin_lit) return { pages: ['The ledger says the old order didn\'t build the Rift-gate. They found it. Nobody wrote down who built it.'], then: (G) => { flags(G.S).tamsin_lit = 1; } };
    return { pages: ['Ask me anything. Except about the statues. Actually, do ask about the statues.'] };
  },
  novice(S) {
    const F = S.flags || {};
    if (F.temple_lit) return { pages: ['Look at the stair now! Blue all the way up. I don\'t even need my lamp.'] };
    if ((S.quests.altar || 0) >= 1) return { pages: ['A Hearth writ! Mind the stair, it\'s dark since the brazier went out. Mother Ilse is in the lower court.'] };
    return { pages: ['Temple\'s shut, friend. Refugees only, and Order folk with a writ.'] };
  },
  refugee1(S) { return { pages: [(S.flags || {}).temple_lit ? 'Blue light on the stair again. My boy says it\'s the prettiest thing he\'s seen. He\'s seen a lot of snow.'
                                                           : 'Our road is ice now. We walked out over the hill with the goats.'] }; },
  refugee2(S) { return { pages: [(S.flags || {}).temple_lit ? 'Two families went home through the gate today. Mother Ilse cried. She says it was the soup steam.'
                                                           : ((S.played || 0) % 2 < 1 ? 'The soup\'s thin, but Mother Ilse makes it hot. Hot counts for a lot.' : 'Is it true you\'ve been to the Crossing? Is it as bright as they say?')] }; },
};
// existing NPCs: new branches first, then their old talk
const BASE = { hilde: TALK.hilde, elder: TALK.elder, chandler: TALK.chandler, gatewright: TALK.gatewright, harbormaster: TALK.harbormaster, quartermaster: TALK.quartermaster };
OT.hilde = (S) => {
  const F = S.flags || {}, qa = S.quests.altar || 0, qg = S.quests.gate || 0;
  if (F.bf_done && !qa && S.met?.hilde) return {
    pages: [...(F.tm_hint ? ['Midgard\'s arch, is it? Then you want the Temple anyway. Its Rift-gate is the arch\'s far side.'] : []),
            'The Old Temple\'s full of folk from cut-off villages, and the Order owes them bread.',
            'Carry this basket up to Mother Ilse. The Temple gate is shut, but it opens for a Hearth writ. Here\'s yours.'],
    then: (G) => { G.give('reliefbasket', 1); G.give('hearthwrit', 1); G.setQuest('altar', 1); },
  };
  if (qa === 1) return { pages: ['Up the Harbor\'s west stair to the Temple gate. Show Edda the writ. Mind the basket, the tea\'s loose.'] };
  if (qg === 3) return { pages: ['Mother Ilse writes that you\'ve a steady hand. From her, that\'s a medal.'] };
  return BASE.hilde(S);
};
OT.elder = (S) => {
  const F = S.flags || {}, inv = S.inv || {};
  if (S.quests.gate === 1 && !inv.alder_charm) return {
    pages: ['A Rift-warden? Aldis? ...Ah. Tamsin\'s ledger found my grandmother, did it.',
            'She walked the bridge once, when it still sang. She left me this, and a lot of stories nobody believed.',
            'It\'s a lantern charm. It held cold fire once. Take it. I think it\'s been waiting for you.'],
    then: (G) => { G.give('alder_charm', 1); G.toast('Warden Aldis\'s lantern charm. Cold, and waiting for a flame.', 2.6); },
  };
  if (F.temple_lit) return { pages: ['The Temple\'s lit, and by a Hearthmoor hand. Aldis would have been insufferable about it. Proudly.'] };
  if (F.tm_wick) return { pages: ['Is it lit? Show me. ...There it is. The same blue she used to talk about.'] };
  return BASE.elder(S);
};
OT.chandler = (S) => {
  const F = S.flags || {}, inv = S.inv || {};
  if (S.quests.gate === 1 && inv.alder_charm && !F.tm_wick) return {
    pages: ['A warden\'s charm! I\'ve only ever seen one in a book. Hold it still.',
            'Cold-fire wick, my very best. It\'ll catch, but it\'s a seedling flame. Feed it at the Temple\'s old braziers.'],
    then: (G) => { G.S.met = { ...(G.S.met || {}), chandler: 1 }; flags(G.S).tm_wick = 1; G.toast('The charm glows a small, stubborn blue.', 2.4); G.refreshMarkers(); G.drawLog && G.drawLog(); G.shopUI.show('harbor'); },
  };
  if (F.tm_wick && !F.temple_lit && S.met?.chandler) { const e = BASE.chandler(S); return { ...e, pages: ['How\'s my wick? Burning blue, I hope. Blue means it likes you.'] }; }
  return BASE.chandler(S);
};
OT.gatewright = (S) => {
  const F = S.flags || {}, q = S.quests.harbor || 0;
  if (F.temple_lit && !S.met?.arch && !(q === 2 && F.rh_road && !F.bf_done)) return {
    pages: ['Midgard\'s arch is lit! The whole ledger shook when it caught. Mother Ilse\'s flame, from the Temple itself?',
            'Then the city has a front door again, and Sable\'s skiff a quieter season. Forty marks for a gate repaired.',
            'That charm of yours. A warden\'s lantern, if I\'m any judge. Keep it close. Keys go missing at the Crossing.'],
    then: (G) => { G.S.met = { ...(G.S.met || {}), arch: 1, halvard: 1 }; G.factions.add('gate', MERIT.arch, 'arch'); },
  };
  const e = BASE.gatewright(S);
  if (!e.choice) return e;
  const meet = (G) => { const was = G.S.met?.halvard; G.S.met = { ...(G.S.met || {}), halvard: 1 }; if (!was) G.factions.add('gate', 20, 'halvard'); };
  let opts = e.choice.options.slice();
  if (F.temple_lit) opts = opts.map((o) => (o.label === 'Which way is home?' ? { ...o, pick: (G) => { meet(G); return { pages: ['Midgard\'s arch, now that the Temple is lit. Or Sable\'s skiff, if you like getting wet.'] }; } } : o));
  const extra = [];
  if (!F.temple_lit) extra.push({ label: 'What about Midgard\'s arch?', pick: (G) => { meet(G); flags(G.S).tm_hint = 1; return { pages: [
    'Midgard\'s arch is the far side of the Old Temple\'s Rift-gate. The Temple\'s flame went out, and the gate went dark.',
    'The Order of the Hearth tends the Temple\'s refugees. Ask Warden Hilde in Hearthmoor. Doors open for Hearth folk.'] }; } });
  if (F.met_veyra) extra.push({ label: 'I met the Rift-Warden.', pick: (G) => { meet(G); return { pages: [
    'Veyra? Here? ...The Guild hasn\'t seen a warden in years. If she\'s holding the Rift, we should all be grateful.',
    'Did she say where she was going? No? No matter. The ledger will find her, if she wants finding.'] }; } });
  opts.splice(opts.length - 1, 0, ...extra);   // before 'Just looking.' (the cancel row stays last)
  return { ...e, choice: { ...e.choice, options: opts } };
};
OT.harbormaster = (S) => ((S.flags || {}).temple_lit && (S.quests.harbor || 0) === 3
  ? { pages: ['See that blue at the top of the hill? The Temple\'s lit. I\'ve watched that light forty years. I missed it.'] } : BASE.harbormaster(S));
OT.quartermaster = (S) => {
  const e = BASE.quartermaster(S);
  return (S.flags || {}).temple_lit && S.met?.sable && e.choice ? { ...e, pages: ['A gate that doesn\'t need my skiff. Bad for business, good for the city. I\'ll sulk quietly.'] } : e;
};
Object.assign(TALK, OT);

// ---------------------------------------------------------------- 6.5 rift storms: NPC storm lines, morning-after lines, toast scenes
// While S.flags.storm is set, an NPC's first page becomes its storm line ('here' when the storm covers this area, else
// 'afar'), unless they're mid-quest with you (a quest tag over their head: quest pages win). The day after a storm in
// which you sealed a rift (S.flags.stormAfter === S.day) they use AFTER_SAY, and the hosts below raise a toast once.
const STORM_SAY = {
  baker: 'Storm over the Rift again. I\'ve put an extra loaf in. Storms make heroes hungry.',
  kid: 'The sky\'s doing the purple crackle! Grandpa says count between flashes. I got to forty and lost track.',
  elder: 'My grandmother called these bridge-storms. She said the Rift was stretching its legs. Stay warm.',
  hilde: 'Rift storm. The Order\'s lamps stay lit till dawn, every one. If you\'re going out, go armed.',
  merchant: 'Storm night! Tonics are flying off the shelf. Well. Being bought. Nothing\'s flying. Hopefully.',
  banker: 'Storm insurance? No such thing. Bank your gold before you go. Fainting in a storm is expensive.',
  nightmerchant: 'Storm nights are good for trade. The lantern likes the crackle. So do rift shards.',
  cat: 'Pudding is under the bread crate, glaring at the sky.',
  herbalist: 'Moonpetal tea calms storms. Not the sky kind. The tummy kind. Take a sip before you go.',
  innkeeper: 'Storm\'s up! Fire\'s high, stew\'s hot, and the door stays open for anyone running from the sky.',
  musician: 'I\'m writing a storm song. It\'s about bread. Bread in a storm. It\'s very dramatic.',
  gardener: 'The geraniums don\'t like the crackle. Neither do I. We\'re staying in.',
  dog: 'Biscuit howls at the purple sky, then hides behind your legs.',
  chicken: 'Mrs. Cluck has gone indoors. Mrs. Cluck has opinions about storms.',
  keeper: { here: 'The moss is shivering. Rifts are opening in the glade. Walk kindly, and walk fast.', afar: 'The moss feels the storm from here. It hums lower. Listen.' },
  owl: '(Hoot\'s feathers stand on end. He stares at the sky like it owes him mice.)',
  gnome: { here: 'Big-folk! Rifts between the caps! Light the braziers, cold fire keeps the worst off!', afar: 'Storm on the bridge. Down here we bolt the gnome doors and eat cake.' },
  // Ondra keeps the 'cold side' foreshadow (lead decision 7)
  riftkeeper: 'The Rift isn\'t angry, hearth-walker. It\'s straining. Something pulls at it from the cold side.',
  warden: { here: 'Rifts over the springs! Keep them off the water. We just got it clean.', afar: 'Bridge-storm. The spores get twitchy. So do I.' },
  tobble: '*tweet tweet!* Two means run. But we\'re not running, are we? No. Fine. Brave tweet.',
  harbormaster: 'Rift storm up top. No boats under the bridge tonight, Corsair or otherwise. Not on my watch.',
  quartermaster: 'Storm nights pay double up there, if you\'ve the nerve. The Guild pays marks. I pay in coin.',
  chandler: 'Cold-fire doesn\'t mind a rift storm. Buy a lantern. Or three. I\'m only half joking.',
  dockkid: 'The lantern-eels are going crazy! They bite more in storms. Or they\'re scared. Hard to tell.',
  // Halvard: the storm line + his quiet keys foreshadow (lead decision 7); the bounty is a hub option (OT.gatewright)
  gatewright: ['Storm on the bridge. The Guild pays a quarter extra for every rift sealed tonight. The board\'s up.',
               'Storms make the gates restless. I\'ll be up all night with the keys. Someone has to be.'],
  // denkeeper: Signe's storm line is already in her rotating hub line (denHubLine)
};
const AFTER_SAY = {
  baker: 'Rift-storm rolls! Same dough, more cinnamon. I name my bakes after weather now.',
  kid: 'Did you fight the storm? Did you win? Can I see your sword? Is it scorched?',
  elder: 'Quiet morning. The Rift\'s done stretching. Sit a while, you\'ve earned the bench.',
  hilde: 'Lamps held all night. So did you, I hear. The Order remembers that.',
  merchant: 'Bring me whatever the storm spat out. Storm-scorched finds fetch a storm-scorched price!',
  banker: 'Busy night for the vault. Everyone banks before a storm. Nobody banks after. Funny, that.',
  cat: 'Pudding emerges, dignified, as if nothing happened.',
  herbalist: 'The moonpetals hummed all night. They like a storm. Strange little flowers.',
  musician: 'Last night\'s song is finished. It\'s called \'Crust, Struck by Lightning\'. It\'s about bread.',
  gardener: 'Not a petal lost. The mint tried to escape in the confusion, though.',
  dog: 'Biscuit wags at you like you personally fixed the sky.',
  chicken: 'Bawk. (An egg, laid in protest, sits on the step.)',
  keeper: 'The moss is humming again. It remembers who walked through the storm for it.',
  owl: 'Hoo. (Hoot looks at you with something close to respect.)',
  gnome: 'We saved you a slice of storm cake. It\'s mostly crumbs. Gnomes get nervous-hungry.',
  riftkeeper: 'It\'s settled. For now. Every storm leaves the bridge a little thinner. I count the cracks.',
  warden: (S) => (((S.flags || {}).alliance || {}).vanaheim === 'conquer' ? 'Storm\'s gone. You\'re still here. Pity about one of those.'
                                                                          : 'Springs held. You held. Mossbrook toasts you, and gnome toasts are loud.'),
  tobble: 'I counted every rift you sealed. I ran out of fingers. I used toes. Gnome toes count double.',
  harbormaster: 'All boats home, all ropes counted. Twice. You can see the Rift\'s scorch marks from the pier.',
  quartermaster: 'Heard you were up on the bridge in that. Either brave or broke. Corsairs respect both.',
  chandler: 'Sold out of wicks by midnight! Storms are good for chandlers and bad for sleep.',
  dockkid: 'I caught a lantern-eel in the storm! It got away. But I caught it first. That counts.',
  gatewright: 'The ledger\'s thick this morning. Storms are bad for gates and good for Gate Runners.',
  denkeeper: 'Every stray accounted for. Pockets slept through it, the lump. Biscuit for your pet, for bravery.',
};
// the morning-after toast scenes: once per storm per host, when you sealed at least one rift; a gift at 3+
const TOASTS = {
  innkeeper: { pages: ['Cups up, Lane! To the hero who walked into the storm while the rest of us hid under the stew.', 'May the Rift stay stitched and the bread stay warm!'],
               gift: { pages: ['On the house. Storms are thirsty work.'], give: (G) => G.give('tonic', 1) }, town: 'Hearthmoor raised a cup to you.' },
  baker: { pages: ['To full ovens and empty skies! And to you, dear, for keeping one of them that way.'], gift: { give: (G) => G.give('loaf', 1) }, town: 'Hearthmoor raised a cup to you.' },
  harbormaster: { pages: ['Raise your mugs, you sorry sea-dogs! To the one who sealed the sky so the boats could sleep!'], town: 'Ravenhold raised a mug to you.' },
  // Sable's +15 Black Doubloons kept (lead decision 6; the MERIT.dues scale)
  quartermaster: { pages: ['To the Rift that didn\'t eat us. And to the fool who stood in front of it. Drink up.'], gift: { give: (G) => G.factions.add('corsair', MERIT.dues, 'stormtoast') }, town: 'Ravenhold raised a mug to you.' },
  gatewright: { pages: ['To the ledger, and every mark in it! And to keys that stay where they\'re put.'], town: 'The Crossing raised a glass to you.' },
  denkeeper: { pages: ['To brave pets and braver idiots. That\'s you. Cheers.'], gift: { give: (G) => G.give('denbiscuit', 1) }, town: 'The Crossing raised a glass to you.' },
  warden: { pages: ['Mushroom ale for everyone! To the big-folk who kept the rifts off our springs!'], town: 'Mossbrook raised a mushroom ale to you.',
            only: (S) => (((S.flags || {}).alliance || {}).vanaheim === 'befriend') },
  gnome: { pages: ['To the storm-walker! Hip hip... (the gnomes cheer from behind every door.)'], town: 'Mossbrook raised a mushroom ale to you.' },
};
const pick = (v, S, here) => (typeof v === 'function' ? v(S) : v && typeof v === 'object' && !Array.isArray(v) ? (here ? v.here : v.afar) : v);
// game.js onTalk runs every NPC's entry through this (TALK entries and plain `say` NPCs alike)
export function stormTalk(id, S, entry, area) {
  const F = S.flags || {}; if (!entry || !entry.pages || !entry.pages.length) return entry;
  const mk = markerFor(id, S); if (mk === 'quest_turnin' || (mk && !entry.choice)) return entry;   // mid-quest: quest pages win (a hub with a fresh offer still talks storm)
  const after = F.stormAfter != null && !F.storm && F.stormAfter === (S.day || 0);
  const T = TOASTS[id];
  if (after && T && (!T.only || T.only(S)) && ((F.toasted || {})[id] !== F.stormAfter)) {
    const big = ((S.storm || {}).last || 0) >= 3;
    return { pages: [...T.pages, ...(big && T.gift && T.gift.pages ? T.gift.pages : [])],
             then: (G) => { const Fx = flags(G.S); Fx.toasted = { ...(Fx.toasted || {}), [id]: Fx.stormAfter }; if (big && T.gift) T.gift.give(G); G.toast(T.town, 2.6); G.save && G.save(); } };
  }
  let line = null;
  if (F.storm) line = pick(STORM_SAY[id], S, stormHere(S, area));
  else if (after) line = pick(AFTER_SAY[id], S, false);
  if (!line) return entry;
  const lead = Array.isArray(line) ? line : [line];
  return { ...entry, pages: [...lead, ...entry.pages.slice(1)], storm: true };
}
// Halvard's Storm Watch: a hub option + the offer / reminder / turn-in (the turn-in comes first, quest pages win)
const OT2 = {};
OT2.gatewright = (S) => {
  const F = S.flags || {}, q = S.quests.stormwatch || 0, n = (S.storm || {}).sealed || 0;
  if (F.bf_done && (q === 2 || (q === 1 && n >= 3))) return {
    pages: [...(n >= 5 ? ['Five? Six? I stopped writing and started staring. Have an extra twenty.'] : []),
            'Three sealed in one storm. The ledger likes you. I like the ledger. So.',
            'Bounty paid: marks, gold and a rift shard. Come back next storm. There\'s always a next storm.'],
    then: (G) => { if (G.S.quests.stormwatch === 1) G.S.quests.stormwatch = 2;
                   G.setQuest('stormwatch', 3); G.factions.add('gate', MERIT.stormwatch, 'stormwatch'); gold(G, 40 + (n >= 5 ? 20 : 0)); gem(G, 'rift_shard');
                   G.toast('+1 Rift shard (a socket gem)', 2.2); },
  };
  const e = OT.gatewright(S);
  if (!e.choice || !F.bf_done) return e;
  const opt = { label: 'Any storm work?', pick: (G) => {
    const S2 = G.S, F2 = S2.flags || {}, q2 = S2.quests.stormwatch || 0;
    if (q2 === 1) return { pages: ['Three rifts, any tier. The board doesn\'t care how big, only how many. Neither do I. Much.'] };
    if (!F2.storm) return { pages: ['No storm, no Storm Watch. Enjoy the quiet. It never lasts.'] };
    if (q2 === 0) return { pages: ['Storm Watch, posted fresh. Seal three rifts before the storm blows out, anywhere it\'s raging.',
                                   'The Guild pays a quarter extra on every mark tonight, and a bounty on top. Go on, the keys can wait.'],
                           then: (G2) => { G2.setQuest('stormwatch', 1); if (((G2.S.storm || {}).sealed || 0) >= 3) G2.setQuest('stormwatch', 2); } };
    return { pages: ['The board\'s clear till the next storm. The ledger thanks you. I thank the ledger.'] };
  } };
  const opts = e.choice.options.slice(); opts.splice(opts.length - 1, 0, opt);
  return { ...e, choice: { ...e.choice, options: opts } };
};
Object.assign(TALK, OT2);

// quest tags over heads: '!' = has an errand for you, star = waiting for your delivery
export function markerFor(id, S) {
  const q = S.quests;
  if (id === 'gatewright') {   // 6.5 Storm Watch (the Guild posts it for any storm, wherever it rages)
    const F = S.flags || {};
    if (q.stormwatch === 2 || (q.stormwatch === 1 && ((S.storm || {}).sealed || 0) >= 3)) return 'quest_turnin';
    if (F.storm && !q.stormwatch && F.bf_done) return 'quest_mark';
  }
  if (id === 'baker' && q.bread === 0) return 'quest_mark';
  if (id === 'innkeeper' && q.bread === 1) return 'quest_turnin';
  if (id === 'herbalist' && q.tea === 0) return 'quest_mark';
  if (id === 'herbalist' && q.tea === 2) return 'quest_turnin';
  if (id === 'kid' && q.cat === 0) return 'quest_mark';
  if (id === 'kid' && q.cat === 2) return 'quest_turnin';
  if (id === 'harbormaster' && !q.harbor) return 'quest_mark';
  if (id === 'quartermaster' && q.harbor === 1) return 'quest_turnin';
  if (id === 'harbormaster' && q.harbor === 2 && (S.flags || {}).rh_gate && !(S.flags || {}).rh_road) return 'quest_turnin';
  if (id === 'gatewright' && q.harbor === 2 && (S.flags || {}).rh_road && !(S.flags || {}).bf_done) return 'quest_turnin';
  const F = S.flags || {}, inv = S.inv || {};
  // the Old Temple (6.3, old_temple.md section 9)
  if (id === 'hilde' && F.bf_done && !q.altar && S.met?.hilde) return 'quest_mark';
  if (id === 'priestess' && q.altar === 1 && inv.reliefbasket) return 'quest_turnin';
  if (id === 'priestess' && q.altar === 2 && clues(S) >= 3) return 'quest_turnin';
  if (id === 'elder' && q.gate === 1 && !inv.alder_charm) return 'quest_mark';
  if (id === 'chandler' && q.gate === 1 && inv.alder_charm && !F.tm_wick) return 'quest_turnin';
  if (id === 'priestess' && q.gate === 1 && F.tm_wick && tmBraziers(S) >= 3 && inv.alder_charm) return 'quest_turnin';
  if (id === 'priestess' && q.gate === 2 && F.tm_rift) return 'quest_turnin';
  if (id === 'gatewright' && F.temple_lit && !(S.met || {}).arch) return 'quest_turnin';
  // the Stray Den (pets doc 4.4)
  if (id === 'denkeeper' && F.bf_done && !q.strays) return 'quest_mark';
  if (id === 'denkeeper' && q.strays === 1 && denLit(S) >= 3 && !F.den_riftOpen) return 'quest_turnin';
  if (id === 'denkeeper' && q.strays === 1 && F.den_rift) return 'quest_turnin';
  if (id === 'denkeeper' && q.strays === 2 && !F.den_seed && ((S.inv.glowseed || 0) + (S.inv.moonpetal || 0)) > 0) return 'quest_turnin';
  if (id === 'denkeeper' && q.strays === 2 && F.den_seed) return 'quest_turnin';
  return null;
}
