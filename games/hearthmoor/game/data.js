// Hearthmoor: items, quests and every line of dialogue (all original text).
// A talk() entry returns { pages: [...], then?: (G) => void } for the current save state S.

export const ITEMS = {
  loaf:      { name: 'Hearthloaf', icon: 0, about: 'A round loaf, still warm. Smells like Tuesday mornings.' },
  moonpetal: { name: 'Moonpetal', icon: 1, about: 'A pale glade flower. It hums faintly when you are not looking.' },
  coin:      { name: 'Copper bits', icon: 2, about: 'Small, round, and well loved.' },
  acorn:     { name: "Tib's lucky acorn", icon: 3, about: 'Polished smooth by a very small thumb.' },
  tea:       { name: 'Moonpetal tea', icon: 4, about: 'A tin of Wren\'s tea. Calms storms, and also grandparents.' },
  tonic:     { name: 'Hearth tonic', px: 'tonic', about: 'Heals 60 HP. Drink: U, right-stick click, or tap it here.' },
  glowseed:  { name: 'Glow seed', px: 'glowseed', about: 'Hums in the dark. Glow-gardens are coming.' },
};

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
  },
};

export const SPELL_NAMES = { sparkle_burst: 'sparkle burst', hearth_flame: 'hearth flame', light_orb: 'light orb', leaf_gust: 'leaf gust', healing_petals: 'healing petals' };

const petals = (S) => S.inv.moonpetal || 0;

export const TALK = {
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
    const first = !S.met?.banker;
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
    if (q === 3) return { pages: ['Room\'s warm, stew\'s warmer, and the bread was perfect.', 'The laundry over the stairs? That\'s mine. Mind the socks.'] };
    return { pages: ['Welcome to the Kettle & Key. We\'re waiting on Marla\'s bread for supper, if you\'re heading up to the plaza.'] };
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

// quest tags over heads: '!' = has an errand for you, star = waiting for your delivery
export function markerFor(id, S) {
  const q = S.quests;
  if (id === 'baker' && q.bread === 0) return 'quest_mark';
  if (id === 'innkeeper' && q.bread === 1) return 'quest_turnin';
  if (id === 'herbalist' && q.tea === 0) return 'quest_mark';
  if (id === 'herbalist' && q.tea === 2) return 'quest_turnin';
  if (id === 'kid' && q.cat === 0) return 'quest_mark';
  if (id === 'kid' && q.cat === 2) return 'quest_turnin';
  return null;
}
