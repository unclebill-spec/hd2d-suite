// Letters in the Ice (sq_frost_letters). One side quest. Other sq_* entries stay unregistered.
// Paste-block helpers, the gloves item, the quest steps, and hrefna_letters are the Story text.
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
  frostveil_gloves: { name: 'Frostveil Gloves', px: 'tonic', about: 'Grey wool, lined with frost-silk. Your fingers stay warm, and cold fire burns a little brighter in them. (Trinket.)' },
});

Object.assign(QUESTS, {
  sq_frost_letters: { title: 'Letters in the Ice', giver: 'Hrefna Frostveil', side: true, steps: {
    1: (S) => `Chip the unsent letters out of the Gloamhaven ice wall (${_cnt(S, 'sq_letter', 3)}/3).`,
    2: 'Deliver them: a fisher in Ravenhold, Brother Tamsin, and one with no name on it.',
    3: 'Hrefna kept the last letter.' } },
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

let hrefnaPrev = null;
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
  MARKER_HOOKS.push(sideMarker);
}

// Keep the paste helpers live so a later side quest can reuse the same spellings. Referenced here so the module stays the Story block.
void _gold; void _gem; void _won;
