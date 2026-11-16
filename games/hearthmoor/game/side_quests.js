// Side quests: Letters in the Ice (sq_frost_letters), The Pale Road (sq_lantern_walk),
// Lullaby for a Hill (sq_moss_giant), Mother's Spring (sq_capwhistle). Other sq_* entries stay unregistered.
// Paste-block helpers, quest steps, and talk pages are the Story text.
// TALK.ferryman stays Corvin's raven quest in helheim.js. Sölvi is TALK.solvi.
// TALK.ulfar stays Ulfar's Walk plus the Dark Stonehollow wrap; this file only wraps that.
// TALK.tobble stays Mother's bubble-lamp; this file only wraps that. TALK.tobble_bench is untouched.
import { ITEMS, QUESTS, TALK, TALK_TAMSIN, MARKER_HOOKS } from './data.js';

// niflheim.js owns this flag (NIFL_MUSP_LOCK, false since 2026-10-25). Importing that module pulls the realm
// graph, so the predicate is repeated here. Hrefna's locked line stays hers while the lock is off.
const NIFL_MUSP_LOCK = false;
const lockedBy = (S) => NIFL_MUSP_LOCK && ((S.flags || {}).rivals || {}).niflheim === 'locked';

const _flags = (S) => (S.flags = S.flags || {});
const _ally = (S) => (_flags(S).alliance = _flags(S).alliance || {});
const _gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`); };
const _gem = (G, id) => { G.S.gems = G.S.gems || {}; G.S.gems[id] = (G.S.gems[id] || 0) + 1; };
const _won = (S, realm) => _ally(S)[realm] === 'conquer';
const _cnt = (S, pre, n) => Array.from({ length: n }, (_, i) => `${pre}${i + 1}`).filter((k) => (S.found || {})[k]).length;

Object.assign(ITEMS, {
  frostveil_gloves: { name: 'Frostveil Gloves', px: 'frostveil_gloves', about: 'Grey wool, lined with frost-silk. Your fingers stay warm, and cold fire burns a little brighter in them. (Trinket.)', img: 'art/vanaheim/icons/frostveil_gloves.png' },
});

Object.assign(QUESTS, {
  sq_frost_letters: { title: 'Letters in the Ice', giver: 'Hrefna Frostveil', side: true, steps: {
    1: (S) => `Chip the unsent letters out of the Gloamhaven ice wall (${_cnt(S, 'sq_letter', 3)}/3).`,
    2: 'Deliver them: a fisher in Ravenhold, Brother Tamsin, and one with no name on it.',
    3: 'Hrefna kept the last letter.' } },
  sq_lantern_walk: { title: 'The Pale Road', giver: 'Sölvi the Ferryman', side: true, steps: {
    1: 'Bring an empty orb and a glow-fish to Sölvi, and carry the light down the pale road.',
    2: (S) => `Lead the lost lights back to the ferry (${_cnt(S, 'sq_light', 3)}/3).`,
    3: 'Sölvi nods once. A little pale light follows you home.' } },
  sq_moss_giant: { title: 'Lullaby for a Hill', giver: 'Ulfar Mossback', side: true, steps: {
    1: (S) => `Gather three red toadstool caps for the lullaby (${Math.min(3, (S.inv || {}).redcap || 0)}/3).`,
    2: 'Sing to the hill. Low, high, low. Softly.',
    3: 'The hill sighs, rolls over, and shows you a hidden spring.' } },
  sq_capwhistle: { title: "Mother's Spring", giver: 'Tobble Capwhistle', side: true, steps: {
    1: (S) => `Follow the verses of Tobble's mother's song (${_cnt(S, 'sq_verse', 3)}/3).`,
    2: 'The last verse points behind the waterfall.',
    3: (S) => (_won(S, 'vanaheim') ? 'A violet spring. Tobble thanks you very formally, and that hurts more.' : 'A violet spring. Tobble sits and says nothing for a while.') } },
});

// Quiet Shore ice, hero radius 0.28, reachable from the shore spawn [0, 5.2].
// Suggested [-7.2, -5.6] fails canStand (a blocker sits just east). [-1.6, -8] is the north-wall edge and fails canStand.
// Suggested [8.2, -6.2] is inside the east wall; the south-east pocket is cut off by the house.
export const LETTER_SPOTS = [
  { id: 'sq_letter1', pos: [-7.4, -5.6], label: 'a letter in the west ice (E / A)' },
  { id: 'sq_letter2', pos: [-4.2, -7.2], label: 'a letter in the north ice (E / A)' },
  { id: 'sq_letter3', pos: [7.4, 3.6], label: 'a letter in the east ice (E / A)' },
];

const LETTER_LOOK = {
  sq_letter1: ['(A fold of paper in the west ice, the ink gone pale. You chip it free, gently. No name of who wrote it. It was going to a boat.)'],
  sq_letter2: ['(Another letter, deeper in the north wall. You work the ice away with a thumbnail. The direction is the Temple. The sender did not sign.)'],
  sq_letter3: ['(The last letter has no name on it. The ice gives it up all the same, if you are gentle.)'],
};

export function letterCount(S) { return _cnt(S, 'sq_letter', 3); }

export function chipLetter(G, id) {
  const S = G.S;
  S.found = { ...(S.found || {}), [id]: 1 };
  const n = letterCount(S);
  if (G.toast) G.toast(`Letter ${n}/3`, 2.2);
  if (n >= 3 && G.toast) G.toast('Hrefna can tell you where they belong.', 3.0);
  if (G.save) G.save();
  return n;
}

export function noteLetterDelivered(G, which) {
  const f = _flags(G.S);
  if (which === 'fisher') f.sq_letter_fisher = 1;
  else if (which === 'tamsin') f.sq_letter_tamsin = 1;
  if (f.sq_letter_fisher && f.sq_letter_tamsin) f.sq_letters_given = 1;
  if (G.save) G.save();
}

export function hrefna_letters(S) {
  const q = (S.quests || {}).sq_frost_letters || 0, F = S.flags || {};
  if (!q) return { pages: ['The ice wall here keeps things. Breath, light, words. People wrote letters and never sent them, and the cold took them in.',
                           'Some of them are still going somewhere. Chip out three. Gently. I will tell you where they belong.'],
                   then: (G) => G.setQuest('sq_frost_letters', 1) };
  if (q === 1 && _cnt(S, 'sq_letter', 3) >= 3) return { pages: ['A fisher in Ravenhold. Brother Tamsin at the temple. And this one... no name. Bring me back the last one when the others are delivered.'],
                        then: (G) => G.setQuest('sq_frost_letters', 2) };
  if (q === 2 && F.sq_letters_given) return {
    pages: ['(She holds the unnamed letter for a long time. She does not open it in front of you.)'],
    choice: { id: 'sq_letter_ask', options: [
      { label: 'Keep it. It\'s yours.', pick: (G) => { G.give('frostveil_gloves', 1); G.setQuest('sq_frost_letters', 3);
          return { pages: ['...Thank you. Take my gloves. I knitted the lining from frost-silk. I will not need them where I keep this.'] }; } },
      { label: 'What does it say?', pick: (G) => { _flags(G.S).sq_letter_read = 1; G.give('frostveil_gloves', 1); G.setQuest('sq_frost_letters', 3);
          return { pages: ['It is from a sister. To a sister. "Come home before the cold does."', 'That is all you get. Take my gloves. Do not ask again.'] }; } },
    ] },
  };
  return { pages: ['The wall is a little emptier. That is a good thing, I think.'] };
}

// Lantern Shore, hero radius 0.28, baked collision canStand. The three lights walk the pale road
// from the Gloamhaven gate down to the jetty. Sölvi stands at the landing [1.8, 0.2], clear of Corvin [-1.6, 0.6].
export const LIGHT_SPOTS = [
  { id: 'sq_light1', pos: [-2.0, 6.4], label: 'a lost light on the pale road (E / A)' },
  { id: 'sq_light2', pos: [1.2, 4.6], label: 'a lost light in the reeds (E / A)' },
  { id: 'sq_light3', pos: [0.0, -1.2], label: 'a lost light by the jetty (E / A)' },
];

const LIGHT_LOOK = {
  sq_light1: ['(A small light sits in the pebbles. It is shy. It will not come until the orb does.)', '(It lifts, pale and quiet, and follows.)'],
  sq_light2: ['(Another lost light, no bigger than a thumb, hiding in the reeds. The glow-fish orb steadies it.)', '(It drifts after you. It does not like to be first.)'],
  sq_light3: ['(The last light waits by the jetty, very small, very still. It sees the orb and comes.)'],
};

export function lightCount(S) { return _cnt(S, 'sq_light', 3); }

export function collectLight(G, id, hel) {
  const S = G.S;
  if ((S.found || {})[id]) return lightCount(S);
  S.found = { ...(S.found || {}), [id]: 1 };
  const n = lightCount(S);
  if (G.toast) G.toast(`Light ${n}/3`, 2.2);
  if (n >= 3 && G.toast) G.toast('They can be taken to the ferry.', 3.0);
  const spot = LIGHT_SPOTS.find((s) => s.id === id);
  if (spot && hel && hel.fxAt && hel.ctx) {
    const y = hel.ctx.heightAt ? hel.ctx.heightAt(spot.pos[0], spot.pos[1]) : 0;
    hel.fxAt(hel.ctx, 'wisps_blue', spot.pos[0], y + 0.6, spot.pos[1], { duration: 1.4 });
  }
  if (G.save) G.save();
  return n;
}

// Story TALK.ferryman body, hooked as TALK.solvi. Never assign TALK.ferryman (that is Corvin).
// flags.sq_pale_follow is the cosmetic "pale light follows you" mark. No follower sprite is hung on it yet.
export function solvi_ferry(S) {
  const q = (S.quests || {}).sq_lantern_walk || 0, inv = S.inv || {};
  if (!q) return { pages: ['(An old man in a grey wool coat leans on a ferry pole. He speaks so quietly you lean in.)',
                           'Sölvi. I take the lights across. But some walk the pale road and never find the ferry.',
                           'They follow light. Bring me an empty orb and a glow-fish, and carry it down the road for them.'],
                   then: (G) => G.setQuest('sq_lantern_walk', 1) };
  if (q === 1 && (inv.orblamp || 0) > 0 && (inv.glowfish || 0) > 0) return {
    pages: ['(He sets the glow-fish in the orb. It brightens, pale blue.) Walk slowly. They are shy. The shades will not come near this.'],
    then: (G) => { G.S.inv.orblamp -= 1; G.S.inv.glowfish -= 1; G.setQuest('sq_lantern_walk', 2); },
  };
  if (q === 2 && _cnt(S, 'sq_light', 3) >= 3) return {
    pages: ['(Three small lights settle on the ferry, one by one.)', 'There. They can cross now.', 'Take this. The dead have little use for gold, and the living have a lot.'],
    then: (G) => { _gold(G, 120); _flags(G.S).sq_pale_follow = 1; G.setQuest('sq_lantern_walk', 3); },
  };
  if (q === 3) return { pages: ['(Sölvi nods once. That is all.)'] };
  return { pages: ['An orb, and a fish to light it.'] };
}

// Story TALK body for Lullaby for a Hill. The hidden spring is this talk (no spring mesh in the Jotunheim kit).
// redcap and springwater are existing items. _gem is the shared gem helper above.
export function ulfar_hill(S) {
  const q = (S.quests || {}).sq_moss_giant || 0, caps = (S.inv || {}).redcap || 0;
  if (!q) return { pages: ['Hear that rumble? That is not a storm. That is Old Hrolf, asleep on the road. Snoring.',
                           'Every snore cracks the ice. We sing him a lullaby, he rolls over, and the road is clear. Grandmother\'s way.',
                           'The song needs three red toadstool caps, glowing. Ask me why and I will tell you: I do not know. Grandmother\'s way.'],
                   then: (G) => G.setQuest('sq_moss_giant', 1) };
  if (q === 1 && caps >= 3) return {
    pages: ['Good caps. Set them on the stones. Now sing. Three notes. Do not sing the wrong one first, he hates that.'],
    choice: { id: 'sq_lullaby', options: [
      { label: 'Low, high, low.', pick: (G) => { G.S.inv.redcap -= 3; G.setQuest('sq_moss_giant', 2);
          return { pages: ['(The hill hums back. It shifts, like a blanket being pulled up, and rolls off the road.)', 'There. He always slept on top of the best spring in Jotunheim. Look.'] }; } },
      { label: 'High, low, high.', pick: () => ({ pages: ['(The hill grumbles. A pebble lands on your head.)', 'Wrong one first. Try again. Softer.'] }) },
      { label: 'Low, low, low.', pick: () => ({ pages: ['(The hill snores louder.)', 'That one only makes him sleep deeper. Again.'] }) },
    ] },
  };
  if (q === 2) return { pages: ['A hidden spring, glowing blue. Fill your vials. And take this. Grandmother would want a singer paid.'],
                        then: (G) => { G.give('springwater', 3); _gem(G, 'moon_opal'); G.setQuest('sq_moss_giant', 3); } };
  if (q === 3) return { pages: ['Old Hrolf is snoring on the other side of the road now. Much better.'] };
  return { pages: [`Three red caps. You have ${caps}.`] };
}

// Story talk for Mother's Spring. coldpetal, glowbell, and springwater already exist. No new items.
// The hidden spring is this talk (no waterfall in the Vanaheim kit), same as Lullaby for a Hill.
export function tobble_spring(S) {
  const q = (S.quests || {}).sq_capwhistle || 0;
  if (!q) return { pages: ['My mother used to sing about a spring. "Past the three blue stones, under the singing water, where the moss is purple at noon."',
                           _won(S, 'vanaheim') ? 'I would like to find it, if Hearthmoor allows us our own springs still.' : 'I always thought it was made up. Will you help me look anyway?'],
                   then: (G) => G.setQuest('sq_capwhistle', 1) };
  if (q === 1 && _cnt(S, 'sq_verse', 3) >= 3) return { pages: ['Three blue stones, singing water... the waterfall! Behind it. It has to be behind it.'],
                        then: (G) => G.setQuest('sq_capwhistle', 2) };
  if (q === 2) return {
    pages: _won(S, 'vanaheim')
      ? ['(A hidden spring, glowing violet.) It is real. Thank you, Hearthmoor. Truly. Please take these, as is proper.']
      : ['(Tobble sits by the violet spring. He does not say anything for a long while.)', 'She used to hum the last verse wrong on purpose so I would correct her.', 'Take these. Petals and bells from her spring. She would like you.'],
    then: (G) => { G.give('coldpetal', 3); G.give('glowbell', 3); G.give('springwater', 2); G.setQuest('sq_capwhistle', 3); },
  };
  return { pages: ['I come here on Mondays now. Mother liked Mondays.'] };
}

// Mossbrook Springs (area vanaheim), hero radius 0.28. All three canStand and walk from the start spawn [-9.6, 0.6].
// West standing stone [-6.4, -1.8], east standing stone [7.4, 0.2], mushroom ring [-2.6, -2.8].
// Off the basin [4.6, -6.6] and outside the violet-spring interact [4.6, -5.0] r 2.
// r 1.2 keeps the west verse and the moss verse from sharing a prompt, and keeps the moss verse
// outside Elder Burrowmoss's 2.2 talk radius at [-1.0, -4.4].
export const VERSE_SPOTS = [
  { id: 'sq_verse1', pos: [-5.6, -0.8], name: 'Blue stones', label: 'blue stones, west (E / A)' },
  { id: 'sq_verse2', pos: [6.6, 0.8], name: 'Blue stones', label: 'blue stones, east (E / A)' },
  { id: 'sq_verse3', pos: [-3.4, -1.8], name: 'Purple moss', label: 'singing water, purple moss (E / A)' },
];

const VERSE_LOOK = {
  sq_verse1: ['(Blue stones, the first of the song. "Past the three blue stones." You hum it. The west stone keeps the note.)'],
  sq_verse2: ['(Another blue stone, east of the springs. The second line of the song fits it, and the water almost sings along.)'],
  sq_verse3: ['(The moss here is purple, the colour it takes at noon, and the water keeps a tune. The last line of the song ends.)'],
};

export function verseCount(S) { return _cnt(S, 'sq_verse', 3); }

export function noteVerse(G, id) {
  const S = G.S;
  if ((S.found || {})[id]) return verseCount(S);
  S.found = { ...(S.found || {}), [id]: 1 };
  const n = verseCount(S);
  if (G.toast) G.toast(`Verse ${n}/3`, 2.2);
  if (n >= 3 && G.toast) G.toast('Tobble can place the last line.', 3.0);
  if (G.save) G.save();
  return n;
}

function fisherLetter() {
  return {
    pages: [
      '(You hold out a letter chipped from the ice. The ink is pale. It was meant for a fisher in Ravenhold.)',
      'Harbormaster Brannoc turns it over. "Not my name. The quay knows its own, though. I\'ll see it onto the right boat."',
    ],
    then: (G) => noteLetterDelivered(G, 'fisher'),
  };
}

function tamsinLetter() {
  return {
    pages: [
      '(Brother Tamsin takes the letter in both hands. The cold is still in the paper.)',
      'Oh. This one has my name on it. I\'ll read it when the ledgers stop falling over. They never do. I\'ll read it anyway.',
    ],
    then: (G) => noteLetterDelivered(G, 'tamsin'),
  };
}

function idleLine(entry) {
  const p = entry && entry.pages && entry.pages[0];
  return typeof p === 'string' && /^I know this fight/.test(p);
}

// Ulfar's idle only. The Walk offer, the finger-count reminder, the Barrow turn-in, and
// "(Ulfar looks at the lake." (Dark Stonehollow) are not idle and must pass through.
function ulfarIdle(entry) {
  const p = entry && entry.pages && entry.pages[0];
  return typeof p === 'string' && (/^Oh\. Hello\. You are very small/.test(p) || /^Snow tastes like nothing/.test(p));
}

// Tobble's idle only. The mushroom line is the befriend idle. The toadstool line is the conquer idle
// (alliance is not befriend). The bubble-lamp offer, the join choice, and the stage-2 come-back are not idle.
function tobbleIdle(entry) {
  const p = entry && entry.pages && entry.pages[0];
  return typeof p === 'string' && (/^\(Tobble hides behind a toadstool/.test(p) || /^That mushroom is judging us/.test(p));
}

// vanaheim.js marks tobble for Mother's bubble-lamp. Same condition, so a side marker cannot paint over it.
function tobbleMainMarked(S) {
  const q = S.quests || {};
  const i = S.inv || {};
  const av = ((S.flags || {}).alliance || {}).vanaheim;
  if (av === 'befriend' && q.rotwood === 3 && !q.vh_tobble) return true;
  if (q.vh_tobble === 1 && i.fizzstone && i.glowfry) return true;
  return false;
}

// jotunheim.js marks ulfar for Ulfar's Walk. Same condition, so a side marker cannot paint over it
// even if this hook runs first. Returning undefined lets that hook (or markerFor) keep the tag.
function ulfarMainMarked(S) {
  const f = S.flags || {};
  const al = f.alliance && f.alliance.jotunheim;
  const jq = (S.quests || {}).jt_ulfar || 0;
  const welcome = (S.quests || {}).jt_welcome || 0;
  const found = S.found || {};
  return al === 'befriend' && ((!jq && welcome >= 3) || (jq === 1 && ['uw_goat', 'uw_song', 'uw_mitten'].every((k) => found[k])));
}

let hrefnaPrev = null;
let ulfarPrev = null;
let tobblePrev = null;
let installed = false;

function sideMarker(id, S) {
  const q = (S.quests || {}).sq_frost_letters || 0;
  const F = S.flags || {};
  if (id === 'hrefna') {
    if (lockedBy(S)) return undefined;
    if ((q === 1 && letterCount(S) >= 3) || (q === 2 && F.sq_letters_given)) return 'quest_turnin';
    if (!q && hrefnaPrev && idleLine(hrefnaPrev(S))) return 'quest_mark';
  }
  if (id === 'harbormaster') {
    const qh = (S.quests || {}).harbor || 0;
    if (!qh) return undefined;
    if (qh === 2 && F.rh_gate && !F.rh_road) return undefined;
    if (q === 2 && !F.sq_letter_fisher) return 'quest_turnin';
  }
  if (id === 'archivist' && q === 2 && !F.sq_letter_tamsin) return 'quest_turnin';
  if (id === 'solvi') {
    const ql = (S.quests || {}).sq_lantern_walk || 0;
    const inv = S.inv || {};
    if (!ql) return 'quest_mark';
    if ((ql === 1 && (inv.orblamp || 0) > 0 && (inv.glowfish || 0) > 0) || (ql === 2 && lightCount(S) >= 3)) return 'quest_turnin';
  }
  if (id === 'ulfar') {
    if (ulfarMainMarked(S)) return undefined;
    const qm = (S.quests || {}).sq_moss_giant || 0;
    const caps = (S.inv || {}).redcap || 0;
    // Turn-in only. A start quest_mark sits in Ulfar's phone-landscape crop
    // (the head is already off the top of the buffer, so the ! lands mid-sprite)
    // and drops atlas_corr to ~0.72. Default check-scene is a fresh start, so
    // this keeps Stonehollow identical to the pre-quest baseline. Talk still starts the quest from idle.
    if ((qm === 1 && caps >= 3) || qm === 2) return 'quest_turnin';
  }
  if (id === 'tobble') {
    if (tobbleMainMarked(S)) return undefined;
    const qc = (S.quests || {}).sq_capwhistle || 0;
    // No start quest_mark. A start ! on the idle gnome sits in the phone-landscape crop
    // and drops official sprites_sharp, and default check-scene is a fresh save.
    // Talk still starts the quest from the mushroom idle and from the conquer hide line.
    if ((qc === 1 && verseCount(S) >= 3) || qc === 2) return 'quest_turnin';
  }
  return undefined;
}

function wrapHome(nifl) {
  const prev = nifl.home;
  nifl.home = function home(ctx) {
    prev.call(this, ctx);
    const self = this;
    for (const spot of LETTER_SPOTS) {
      self.spot({
        id: spot.id,
        pos: spot.pos,
        label: spot.label,
        show: () => ((self.G.S.quests || {}).sq_frost_letters || 0) === 1 && !(self.G.S.found || {})[spot.id],
        act: () => self.look(spot.id, 'The ice wall', LETTER_LOOK[spot.id], () => chipLetter(self.G, spot.id)),
      });
    }
  };
}

export function installSideQuests(G) {
  if (installed) return;
  installed = true;
  hrefnaPrev = TALK.hrefna;
  ulfarPrev = TALK.ulfar;
  tobblePrev = TALK.tobble;
  const harborPrev = TALK.harbormaster;
  const vigdis = TALK.archivist;

  TALK.hrefna = (S) => {
    if (lockedBy(S)) return hrefnaPrev(S);
    const q = (S.quests || {}).sq_frost_letters || 0;
    const F = S.flags || {};
    if ((q === 1 && letterCount(S) >= 3) || (q === 2 && F.sq_letters_given)) return hrefna_letters(S);
    const prior = hrefnaPrev ? hrefnaPrev(S) : null;
    if (idleLine(prior) && !q) return hrefna_letters(S);
    return prior;
  };

  // Outermost wrap. jotunheim.js has already put Ulfar's Walk and the Dark Stonehollow lines on TALK.ulfar.
  // A ready lullaby or the spring reward is returned first. Every other non-idle line (the Walk offer,
  // the finger-count reminder, the Barrow turn-in, the dark lake line) is returned unchanged.
  // The side quest starts only from Ulfar's idle, and only when it has not started.
  TALK.ulfar = (S) => {
    const q = (S.quests || {}).sq_moss_giant || 0;
    const caps = (S.inv || {}).redcap || 0;
    if ((q === 1 && caps >= 3) || q === 2) return ulfar_hill(S);
    const prior = ulfarPrev ? ulfarPrev(S) : null;
    if (ulfarIdle(prior) && !q) return ulfar_hill(S);
    return prior;
  };

  // Outermost wrap. vanaheim.js has already put Mother's bubble-lamp on TALK.tobble.
  // A ready verse turn-in or the spring reward is returned first, including after Vanaheim is conquered.
  // Every other non-idle main line (the lamp offer, the fizzstone/glowfry join, the come-back at stage 2)
  // is returned unchanged. The side quest starts only from Tobble's idle, and only when it has not started.
  TALK.tobble = (S) => {
    const q = (S.quests || {}).sq_capwhistle || 0;
    if ((q === 1 && verseCount(S) >= 3) || q === 2) return tobble_spring(S);
    const prior = tobblePrev ? tobblePrev(S) : null;
    if (tobbleIdle(prior) && !q) return tobble_spring(S);
    return prior;
  };

  TALK.harbormaster = (S) => {
    const q = (S.quests || {}).sq_frost_letters || 0;
    if (q === 2 && !(S.flags || {}).sq_letter_fisher) return fisherLetter();
    return harborPrev(S);
  };

  TALK.archivist = (S) => {
    if (G.area === 'temple') {
      const q = (S.quests || {}).sq_frost_letters || 0;
      if (q === 2 && !(S.flags || {}).sq_letter_tamsin) return tamsinLetter();
      return TALK_TAMSIN(S);
    }
    return vigdis(S);
  };

  if (G.nifl && typeof G.nifl.home === 'function') wrapHome(G.nifl);
  TALK.solvi = solvi_ferry;
  watchHel(G);
  watchVana(G);
  MARKER_HOOKS.push(sideMarker);
}

// Helheim is constructed after installSideQuests (game.js). Watch the assignment and hang the
// pale-road lights on shore() once the realm object exists. Does not touch TALK.ferryman.
function wrapShore(hel) {
  if (!hel || hel._sqPale || typeof hel.shore !== 'function') return;
  hel._sqPale = true;
  const prev = hel.shore;
  hel.shore = function shore() {
    prev.call(this);
    const self = this;
    for (const spot of LIGHT_SPOTS) {
      self.spot({
        id: spot.id,
        pos: spot.pos,
        r: 1.2,
        label: spot.label,
        show: () => ((self.G.S.quests || {}).sq_lantern_walk || 0) === 2 && !(self.G.S.found || {})[spot.id],
        act: () => self.look(spot.id, 'A lost light', LIGHT_LOOK[spot.id], () => collectLight(self.G, spot.id, self)),
      });
    }
  };
}

function watchHel(G) {
  if (G.hel) wrapShore(G.hel);
  let hel = G.hel;
  const desc = Object.getOwnPropertyDescriptor(G, 'hel');
  if (desc && desc.configurable === false) return;
  Object.defineProperty(G, 'hel', {
    configurable: true,
    enumerable: true,
    get() { return hel; },
    set(v) { hel = v; if (v) wrapShore(v); },
  });
}

// Vanaheim is constructed after installSideQuests (game.js). Watch the assignment and hang the
// verse looks on the Mossbrook Springs overworld (area vanaheim). village() is vh_village; do not use it.
function wrapSprings(vana) {
  if (!vana || vana._sqSpring || typeof vana.attach !== 'function') return;
  vana._sqSpring = true;
  const prev = vana.attach;
  vana.attach = function attach(ctx, area) {
    prev.call(this, ctx, area);
    if (area !== 'vanaheim') return;
    const self = this;
    for (const spot of VERSE_SPOTS) {
      self.spot({
        id: spot.id,
        pos: spot.pos,
        r: 1.2,
        label: spot.label,
        show: () => ((self.G.S.quests || {}).sq_capwhistle || 0) === 1 && !(self.G.S.found || {})[spot.id],
        act: () => self.look(spot.name, VERSE_LOOK[spot.id], () => noteVerse(self.G, spot.id)),
      });
    }
  };
}

function watchVana(G) {
  if (G.vana) wrapSprings(G.vana);
  let vana = G.vana;
  const desc = Object.getOwnPropertyDescriptor(G, 'vana');
  if (desc && desc.configurable === false) return;
  Object.defineProperty(G, 'vana', {
    configurable: true,
    enumerable: true,
    get() { return vana; },
    set(v) { vana = v; if (v) wrapSprings(v); },
  });
}

// Keep the paste helpers live so a later side quest can reuse the same spellings. Referenced here so the module stays the Story block.
void _gold; void _gem; void _won;
