// Ambient barks for every realm (Hearthmoor Story, 2026-10-26). One pool per realm, one bubble.
// A line shows over a nearby talkable NPC (and, on the Bifrost only, a traveller spot): one at a time,
// ~3 s, then a quiet 8–14 s. Not during dialogue, menus, combat, or pause.
// Colours are the existing parchment bubble.

export const NEAR = 3.5;
export const SHOW = 3;
export const GAP_MIN = 8;
export const GAP_MAX = 14;

export const BARKS = {
  "midgard": {
    "any": [
      "Warden Hilde says lamps first, gossip second. I do both at once.",
      "Odo's Wares has new jars. Same jam. Better jars.",
      "Mind the plaza puddle. It's been there since my granny's day.",
      "Hearthloaf's fresh! Well, fresh-ish. Fresh enough to argue over.",
      "The Rift's rainbow is extra bright tonight. Show-off.",
      "Ravenhold sailors say the water's colder than it looks. It is.",
      "I swept the lane twice. The leaves came back to say hello.",
      "Glenheart nodded at me in Mossglen. I'm telling everyone.",
      "Hearth Tokens? Keep 'em safe. Odo counts every one.",
      "If you see my cat, she's not lost. She's supervising.",
      "Gatekeepers' folk walk by here humming. Means rifts are quiet.",
      "Storm's coming? Count between the flashes, my grandpa says.",
      "Guard tip: smile at the geese. They respect confidence.",
      "Nothing beats a Midgard evening and a warm mug."
    ],
    "befriended": [],
    "conquered": [],
    "redeemed": [
      "The Rift hums like a kettle now. A happy kettle.",
      "Heard the Rift-Warden mended things. Not alone, they say.",
      "Every gate at Bifrost is lit. My knees want to visit all nine."
    ]
  },
  "alfheim": {
    "any": [
      "Mind the boughs. Lumenvale was built for elves, not elbows.",
      "The glowfrogs are singing in the root-pools. Tenor section's flat.",
      "Lavender dusk again. We have about forty words for it.",
      "Don't wave at the wisps. They take it very personally.",
      "Glow orbs drift where they like. Rather like my nephew.",
      "The silverbarks creak when they're content. Listen.",
      "Aurora tonight. Bring a cushion. We stare for hours.",
      "We did not poison anyone's springs. Please tell the gnomes.",
      "My vines glow violet on Tuesdays. Don't ask how I know.",
      "Guard post: no running on the canopy bridges. Gliding, fine.",
      "A wisp sat on my teacup this morning. Best tea of my life.",
      "Elf-runes in the moss? Burnt crooked. No elf writes like that."
    ],
    "befriended": [
      "Lumi waved at me! A wisp, waving! I nearly fell off a branch.",
      "The wisps burn again. My lantern feels quite redundant.",
      "Wisp Night is back. Wear something that glows. Or blink a lot.",
      "Our queen sleeps. We hum quietly near the Vault, just in case."
    ],
    "conquered": [
      "It's dim here now. We light candles and talk softer.",
      "Rift Marks bought you a road, outsider. Not our songs.",
      "The canopy's quiet. The glowfrogs still try, bless them."
    ],
    "redeemed": [
      "The aurora looks gentler lately. Even the frost seems sorry."
    ]
  },
  "svartalfheim": {
    "any": [
      "Mind the chain-bridge. It sways when it's in a mood.",
      "The Great Forge is the size of a hill. My chimney's jealous.",
      "Copper roofs need polishing. Copper roofs always need polishing.",
      "Rune-light's cold blue. Hands off, it bites like winter.",
      "Amethyst grows like frost down the mines. Pretty. Sharp.",
      "Dwarf proverb: measure twice, hammer once, nap thrice.",
      "Soot fall today. Hats on, everyone. Yes, even you.",
      "Felt a tremor? That's just the mountain clearing its throat.",
      "Guard says: no tinkering with the clockwork. Again.",
      "My beard's singed. Forgefire Week came early this year.",
      "Frost on a lock doesn't mean dark elves. Folk forget that.",
      "Tick the owl blinked at me. Tick-tick. I felt judged.",
      "Cooling forge, cold suppers. Let's fix it, eh?"
    ],
    "befriended": [
      "The Anvil-Heart's home! Listen. Thump, thump. Lovely.",
      "Forge is roaring again. My soup's never been warmer.",
      "Dagna says you swing a fair hammer. High praise, that.",
      "Forgefire Week's on! Bring earplugs and an appetite."
    ],
    "conquered": [
      "The Heart's gone with you. The forge sulks without it.",
      "Rift Marks paid for this quiet. Keep your boots clean.",
      "We hammer softer now. Habit, mostly."
    ],
    "redeemed": [
      "Word is the frost-witch mended the Rift. Odd. Good, though."
    ]
  },
  "jotunheim": {
    "any": [
      "Doors here fit a cart. Knock anyway. It's polite.",
      "Goat races at noon. My goat has no idea. That's her strategy.",
      "Cold fire burns blue and never warms your toes. Pity.",
      "Mind the lake. Ice is thick. Giants are thicker.",
      "The standing stones hum in the aurora. They're old friends.",
      "Small folk, big welcome. Sit. That stool is your size. Mostly.",
      "Blizzard coming. Drink your Moonpetal tea and stay close.",
      "We didn't steal any Heart. We found a fake one. Rude gift.",
      "Stone-Toss Games next week. I've been lifting my porridge pot.",
      "Guard says: no climbing the longhouses. They're three storeys!",
      "Rime Caves glow at night. Bring mittens and a sense of wonder.",
      "My hare found a secret snow path. Then sat on it.",
      "Slow words are kind words. I'll finish this one by spring."
    ],
    "befriended": [
      "The gate's open and the kettle's on. Small friend's back!",
      "Ulfar says you lift stones well. For a small person.",
      "Stone-Toss Games! Throw something big. Not the goats.",
      "The blizzards are easing. Pass the Moonpetal tea."
    ],
    "conquered": [
      "We bow, small one. Bowing hurts our backs, mind.",
      "Rift Marks don't buy a giant's laugh. Earn that slow.",
      "The lake's still frozen. So are our smiles, for now."
    ],
    "redeemed": [
      "The snow falls softer. Even the Barrow seems to sigh."
    ]
  },
  "muspelheim": {
    "any": [
      "Careful, the floor's extra toasty this morning.",
      "A pinch of cinder-salt makes the stew sing.",
      "Ember motes drifting like orange snow. Catch one? Don't.",
      "Lava-falls are lovely. Lava-baths are not. Learn the difference.",
      "Pass me a stone, I'm toasting bread.",
      "The glass bridges are cooled. Mostly. Walk briskly.",
      "Ash fall today. Cover your tea, it's peppery enough.",
      "That sigil curled the wrong way. Our flames curl proper.",
      "Fire-giants keep the forges. Ask nicely, they'll warm your hands.",
      "Guard says: no juggling embers on the terraces. Again.",
      "That crackle? The song of a happy home.",
      "Emberfall's dancing gets wild. Wear sensible shoes.",
      "Welcome to the glow, traveler. Stay a while."
    ],
    "befriended": [
      "Kindle's flame is back! Look at that little red scarf!",
      "The seals hold and the lava's settling. Lovely and warm.",
      "Emberfall's on! Bring your best ember for the forging contest.",
      "You've a Warden's welcome here. Mind your eyebrows."
    ],
    "conquered": [
      "Rift Marks keep the gate open. They don't keep us chatty.",
      "We forge for you now. We don't sing while we do it.",
      "The terraces glow. Not as bright as they used to."
    ],
    "redeemed": [
      "Frost and fire shook hands? I'll believe it when I see tea."
    ]
  },
  "niflheim": {
    "any": [
      "Visitors. We'd almost forgotten how to say hello. Hello.",
      "Blue lanterns on every post. We never let them go out.",
      "Mind the ice bridge. It sings when you step on it.",
      "Freezing mist today. Hold a lantern and a friend's hand.",
      "The aurora pours over the mountains. Free show, nightly.",
      "We've been alone a long while. Stay for soup?",
      "Frost elk wander by the shore. They like hat-chewing.",
      "The Glowpool Caverns glow from below. Ice that dreams.",
      "Guard says: no skating on the lake during the Vigil.",
      "Cold fire keeps the dark polite. That's all we ask.",
      "I knit a scarf a winter. I'm on my three-hundredth.",
      "Still frost tonight. Even the snowflakes are whispering."
    ],
    "befriended": [
      "Hrefna says you're kind. She doesn't say that lightly.",
      "Frost Vigil's on. Light a lantern for someone you miss.",
      "Mistmere has guests again. The kettles can't keep up.",
      "Strange to have friends past the gate. Nice strange."
    ],
    "conquered": [
      "Rift Marks open doors. They don't warm Mistmere.",
      "We keep the lanterns lit. Out of habit, now.",
      "The lake listens. It hasn't decided about you yet."
    ],
    "redeemed": [
      "She's home. Veyra lit a lantern on the shore last night.",
      "Eira's grave has fresh flowers every morning now.",
      "The portals are thawing. The ice is crying the happy kind."
    ]
  },
  "asgard": {
    "any": [
      "Goldspire's halls are golden. Polishing them is my life.",
      "Always dusk up here. The light's indoors, hoarded proper.",
      "Rune-pillars crackle. Don't lean on them. Trust me.",
      "Sky-horses graze past the plains. They steal apples. Rude.",
      "The Dawn-Flame's dim. We whisper about it. Loudly.",
      "Generous to friends, slow to forgive. That's Asgard.",
      "Thunderstorm coming. Good weather for hammer practice.",
      "Guard says: no racing sky-horses through the upper halls.",
      "That ember brand? Flames curl the wrong way. Just saying.",
      "Thunder Moot's coming. Brag early, it saves time.",
      "We don't talk about who we sided with. Please don't ask.",
      "Storm-centaurs on the plains. Nod politely. They nod back."
    ],
    "befriended": [
      "The Dawn-Flame's lit! I can see my own boots again!",
      "Sigrun says you fly well. For someone without wings.",
      "Thunder Moot's on! Win the rune trial, don't get struck.",
      "We asked first this time. Felt rather grown-up."
    ],
    "conquered": [
      "Rift Marks bought you the gate. Not the mead-hall seat.",
      "The halls stay lit. Our pride stays sore.",
      "We'll forgive you in a century or two. Asgard is slow."
    ],
    "redeemed": [
      "Fire and frost made peace. Maybe we owe an apology too."
    ]
  },
  "vanaheim": {
    "any": [
      "Riddle me this: what fizzes and gossips? Mossbrook!",
      "The springs fizz cyan tonight. Means they're in a good mood.",
      "A gnome remembers everything. Especially your hat.",
      "Spore drizzle. Lovely for mushrooms, ticklish for noses.",
      "Mind the toadstool caps. They glow, they don't hold weight.",
      "Elder Burrowmoss is napping. Whisper your complaints.",
      "Fireflies pulse lime-neon. They're showing off for the fish.",
      "Warm rain again. Moss loves it. Socks do not.",
      "Gnome Council? Never heard of it. Wink.",
      "Guard says: no pranking visitors before supper.",
      "Bloomtide's soon. Mushroom harvest, spring dances, riddles!",
      "Orb lanterns have glowing fish. Don't tap the glass.",
      "Elf-runes in the moss, they said. Hmm. Crooked runes."
    ],
    "befriended": [
      "Springs run clear again! I had a bubble bath to celebrate.",
      "Tobble says you're nearly as clever as a gnome. Nearly.",
      "Bloomtide's on! Dance with a nymph. Mind her feet.",
      "Mossbrook pays its tithe of spring water. Gladly, for you."
    ],
    "conquered": [
      "The tithe's paid. The giggles are rationed.",
      "Rift Marks don't fizz, friend. Springs do.",
      "We still riddle. You just won't hear the good ones."
    ],
    "redeemed": [
      "Foresight says sunny days. Well, glowing dusk. Close enough."
    ]
  },
  "helheim": {
    "any": [
      "Evening, living one. Mind the lake, it's very still.",
      "I baked a pie. I can't eat it, but the smell's lovely.",
      "The lantern bridge sways. The ghosts don't mind. Do you?",
      "Glow orbs in the willows. Grandmother hangs a new one yearly.",
      "Gloam fog tonight. Stay on the lit path, dear.",
      "Hel keeps every name in her Ledger. She has neat handwriting.",
      "We argue about the old days. Nobody's right. It's nice.",
      "Soul lights over the water. Count them, it's soothing.",
      "Guard says: the living walk on the left. Ghosts float anywhere.",
      "Ghost story? Grab a cushion. This one has a happy end.",
      "Eerie, yes. Unkind, never. That's Gloamhaven.",
      "Lantern-Boat Night's coming. Bring someone to remember."
    ],
    "befriended": [
      "You asked Hel's leave. The lanterns on the bridge like you.",
      "Lantern-Boat Night! Float one for whoever you miss.",
      "The names are back in the Ledger. Everyone's sleeping better."
    ],
    "conquered": [
      "The bridge lanterns stay dark for you. Hel remembers.",
      "No ghost stories for the defiant one. Sorry, dear.",
      "You forced the Bone Gate. The willows whisper about it."
    ],
    "redeemed": [
      "A girl with a lantern said her piece. Her sister listened."
    ]
  },
  "bifrost": {
    "any": [
      "Nine gates, nine colours. My eyes have never been so busy.",
      "Gatewright Halvard says 'coming soon' like it's a blessing.",
      "Vanaheim's gate is the only one open. Smells like moss and rain.",
      "Mind the frozen gate. Niflheim's seal bites back when you lean on it.",
      "Gatekeepers' Guild polishes the arches daily. Tidy lot.",
      "I came for the view, stayed because I lost my way. Again.",
      "Muspelheim's seal is warm. People toast bread on it. Don't.",
      "Asgard's gate hums like a hall fire. Rather smug, I find.",
      "Helheim's gate breathes on the glass. Polite, but chilly.",
      "Earn your merit, get your key. The Guild has a pamphlet."
    ],
    "temple_lit": [
      "Old Temple's relit! The Midgard gate is open and singing.",
      "No more Corsair skiffs to get home. My stomach thanks the Temple.",
      "Rainbow light on the plaza stones again. Hearthmoor's next door now."
    ]
  }
};

// Area id -> bark realm. Same area lists as REALM_OF in audio.js, except Bifrost keeps its own pool,
// Mossbrook areas speak as vanaheim, and Ravenhold stays with the Midgard hub.
export const BARK_REALM = {};
for (const a of ['plaza', 'lane', 'mossglen', 'hollows', 'ravenhold', 'temple', 'forge', 'rift']) BARK_REALM[a] = 'midgard';
BARK_REALM.bifrost = 'bifrost';
for (const a of ['vanaheim', 'vh_village', 'vh_garden', 'rotwood', 'verdant']) BARK_REALM[a] = 'vanaheim';
for (const a of ['alfheim', 'lumen_court', 'wispwood', 'prismvault']) BARK_REALM[a] = 'alfheim';
for (const a of ['svartalfheim', 'forge_hall', 'glowmines', 'clockdeep', 'clockdeep2']) BARK_REALM[a] = 'svartalfheim';
for (const a of ['jotunheim', 'jt_hall', 'rimecaves', 'barrow', 'barrow2']) BARK_REALM[a] = 'jotunheim';
for (const a of ['muspelheim', 'mp_hall', 'lavafalls', 'caldera', 'caldera2']) BARK_REALM[a] = 'muspelheim';
for (const a of ['niflheim', 'nf_home', 'iceglow', 'frozenspire', 'frozenspire2', 'frozen_rift']) BARK_REALM[a] = 'niflheim';
for (const a of ['asgard', 'gs_hall', 'gs_temple', 'reliquary', 'reliquary2']) BARK_REALM[a] = 'asgard';
for (const a of ['helheim', 'hh_shore', 'hh_archive', 'ossuary', 'ossuary2']) BARK_REALM[a] = 'helheim';

// Which non-any pools apply. Empty pools are skipped. Contract paths set no alliance of befriend/conquer, so they stay on any.
export function statePools(realm, flags) {
  const table = BARKS[realm];
  if (!table) return [];
  const f = flags || {};
  const out = [];
  const add = (key) => { const lines = table[key]; if (lines && lines.length) out.push(key); };
  if (realm === 'bifrost') {
    if (f.temple_lit) add('temple_lit');
  } else if (realm === 'helheim') {
    if (f.hel === 'kind') add('befriended');
    else if (f.hel === 'defiant') add('conquered');
  } else {
    const al = f.alliance && f.alliance[realm];
    if (al === 'befriend') add('befriended');
    else if (al === 'conquer') add('conquered');
  }
  if (f.veyra_redeemed) add('redeemed');
  return out;
}

// One rng() for the state-vs-any choice, and only when a state pool applies (same short-circuit as the old temple_lit check).
function linePool(realm, flags, rng) {
  const table = BARKS[realm] || BARKS.bifrost;
  const states = statePools(realm, flags);
  const useState = states.length > 0 && rng() >= 1 / 3;
  if (!useState) return table.any;
  const pool = [];
  for (const key of states) pool.push(...table[key]);
  return pool;
}

function pickFrom(realm, flags, rng, avoid) {
  const pool = linePool(realm, flags, rng);
  let i = Math.floor(rng() * pool.length) % pool.length;
  if (pool.length > 1 && pool[i] === avoid) i = (i + 1) % pool.length;
  return { pool, i, line: pool[i] };
}

// realm defaults to bifrost so the original call shape is unchanged.
export function pickLine(flags, rng, avoid, realm = 'bifrost') {
  return pickFrom(realm, flags, rng, avoid).line;
}

export function rollGap(rng) {
  return GAP_MIN + rng() * (GAP_MAX - GAP_MIN);
}

export function freshSim(rng = Math.random) {
  return { wait: rollGap(rng), left: 0, line: null, spot: null, last: null, pin: false };
}

// sim.wait is the quiet gap. sim.left is the one visible bark.
// world: { blocked, spots: [{id, d, label?}], flags, rng, near, show, realm }. A pinned bark ignores range (QA force).
// realm defaults to bifrost. A spot label of 3+ characters that appears in the line steps to the next line in that same pool.
export function tick(sim, dt, world) {
  const rng = world.rng || Math.random;
  const near = world.near ?? NEAR;
  const show = world.show ?? SHOW;
  if (world.blocked) {
    if (sim.left > 0) { sim.left = 0; sim.line = null; sim.spot = null; sim.pin = false; }
    return sim;
  }
  if (sim.left > 0) {
    const spots = world.spots || [];
    const here = sim.pin || spots.some((s) => s.id === sim.spot && s.d <= near);
    sim.left -= dt;
    if (!here || sim.left <= 0) { sim.left = 0; sim.line = null; sim.spot = null; sim.pin = false; }
    return sim;
  }
  sim.wait -= dt;
  if (sim.wait > 0) return sim;
  const spots = (world.spots || []).filter((s) => s.d <= near);
  if (!spots.length) { sim.wait = 0; return sim; }
  const spot = spots[Math.floor(rng() * spots.length) % spots.length];
  const realm = world.realm || 'bifrost';
  const picked = pickFrom(realm, world.flags, rng, sim.last);
  let i = picked.i;
  const pool = picked.pool;
  const label = spot.label == null ? '' : String(spot.label);
  if (label.length >= 3) {
    const needle = label.toLowerCase();
    let tries = 0;
    while (tries < pool.length && pool[i].toLowerCase().includes(needle)) {
      i = (i + 1) % pool.length;
      tries += 1;
    }
    if (tries >= pool.length) {
      sim.wait = Math.max(0.05, rollGap(rng) - show);
      return sim;
    }
  }
  sim.line = pool[i];
  sim.last = sim.line;
  sim.spot = spot.id;
  sim.left = show;
  sim.pin = false;
  sim.wait = Math.max(0.05, rollGap(rng) - show);
  return sim;
}

const AMBIENT = [
  { id: 'arch', x: 2.2, z: -8.2, label: 'A traveller' },
  { id: 'skiff', x: 2.4, z: 10.5, label: 'A traveller' },
  { id: 'west', x: -7.2, z: -3.8, label: 'A traveller' },
  { id: 'east', x: 8.2, z: -2.4, label: 'A traveller' },
];
const TITLES = /^(gatewright|warden|keeper|elder|captain|lady|mother)$/i;

function shortName(a) {
  const raw = String(a.name || '').split(',')[0].trim();
  const bits = raw.split(/\s+/).filter(Boolean);
  if (bits.length >= 2 && TITLES.test(bits[0])) return bits[1];
  if (bits.length) return bits[0];
  return a.role || 'Someone';
}

export class Barks {
  constructor(G) {
    this.G = G;
    this.rng = Math.random;
    this.sim = freshSim(this.rng);
    this.here = false;
    this.area = null;
    this.el = null;
  }
  blocked() {
    const G = this.G;
    let wheel = false;
    try { wheel = !!(G.wheel && G.wheel.state && G.wheel.state().open); } catch (e) { wheel = false; }
    const foes = G.combat && G.combat.enemies;
    const fight = !!(foes && foes.some((e) => e.state === 'chase' || e.state === 'attack'));
    const intro = !!(G.intro && G.intro.blocking && G.intro.blocking());
    return !!(G.dlg || G.log || G.opts || G.pause || G.heroUI || G.shop || G.picking || G.title || G.asking || G.busy || G.downed || wheel || fight || intro);
  }
  spots(ctx) {
    const p = ctx.player, out = [];
    for (const a of ctx.npcs || []) {
      if (!a || a.ai || a.noTalk || a.kind === 'enemy' || a.behavior === 'follow') continue;
      if (!(a.talkable || a.say)) continue;
      if (a.quad && a.quad.visible === false) continue;
      out.push({ id: a.id, x: a.x, z: a.z, y: a.y || 0, lift: (a.lift || 0) + 2.15, label: shortName(a), d: Math.hypot(a.x - p.x, a.z - p.z) });
    }
    if (this.G.area === 'bifrost') {
      for (const s of AMBIENT) {
        const y = ctx.heightAt ? (ctx.heightAt(s.x, s.z) || 0) : 0;
        out.push({ id: s.id, x: s.x, z: s.z, y, lift: 1.85, label: s.label, d: Math.hypot(s.x - p.x, s.z - p.z) });
      }
    }
    return out;
  }
  ensure() {
    if (this.el || typeof document === 'undefined') return this.el;
    const layer = document.getElementById('fxlayer');
    if (!layer) return null;
    const el = document.createElement('div');
    el.id = 'bark'; el.className = 'bark'; el.hidden = true; el.setAttribute('aria-hidden', 'true');
    layer.appendChild(el);
    this.el = el;
    return el;
  }
  hide() { if (this.el) this.el.hidden = true; }
  paint(ctx, spots) {
    const sim = this.sim;
    const shot = !!(this.G.qs && this.G.qs.has('shot') && !sim.pin);
    if (!sim.line || shot) { this.hide(); return; }
    const spot = spots.find((s) => s.id === sim.spot);
    const el = this.ensure();
    if (!spot || !el || !ctx.project) { this.hide(); return; }
    const s = ctx.project(spot.x, spot.y + spot.lift, spot.z);
    if (!s || s.z > 1) { el.hidden = true; return; }
    if (el.dataset.line !== sim.line || el.dataset.who !== spot.label) {
      el.dataset.line = sim.line; el.dataset.who = spot.label;
      el.replaceChildren();
      const b = document.createElement('b'); b.textContent = spot.label;
      const span = document.createElement('span'); span.textContent = sim.line;
      el.append(b, span);
    }
    el.hidden = false;
    el.style.transform = `translate(${Math.round(s.x)}px, ${Math.round(s.y)}px) translate(-50%, -100%)`;
  }
  update(dt) {
    const G = this.G, ctx = G.ctx;
    const realm = ctx && BARK_REALM[G.area];
    if (!ctx || !realm) {
      this.here = false;
      this.area = null;
      if (this.sim.line) { this.sim.left = 0; this.sim.line = null; this.sim.spot = null; this.sim.pin = false; }
      this.hide();
      return;
    }
    if (!this.here || this.area !== G.area) { this.here = true; this.area = G.area; this.sim = freshSim(this.rng); }
    const spots = this.spots(ctx);
    tick(this.sim, dt, { blocked: this.blocked(), spots, flags: (G.S && G.S.flags) || {}, rng: this.rng, near: NEAR, show: SHOW, realm });
    this.paint(ctx, spots);
  }
  // QA / screenshots: show one line now, over the nearest speaker, ignoring range and the quiet gap.
  force(line) {
    const ctx = this.G.ctx;
    const realm = BARK_REALM[this.G.area];
    if (!ctx || !realm) return null;
    const spots = this.spots(ctx);
    if (!spots.length) return null;
    spots.sort((a, b) => a.d - b.d);
    const spot = spots[0];
    const text = line || pickLine((this.G.S && this.G.S.flags) || {}, this.rng, this.sim.last, realm);
    this.here = true;
    this.area = this.G.area;
    this.sim.line = text; this.sim.last = text; this.sim.spot = spot.id; this.sim.left = SHOW; this.sim.pin = true;
    this.sim.wait = Math.max(0.05, rollGap(this.rng) - SHOW);
    this.paint(ctx, spots);
    const el = this.el;
    return { line: text, id: spot.id, x: spot.x, z: spot.z, shown: !!(el && !el.hidden) };
  }
}
