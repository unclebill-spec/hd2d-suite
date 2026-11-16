// Letters in the Ice: start, chip, deliver either order, reward choices, save/load, talk wraps.
import test from 'node:test';
import assert from 'node:assert/strict';

globalThis.window ??= globalThis;
globalThis.document ??= { getElementById: () => null, head: { appendChild() {} }, body: { appendChild() {}, classList: { add() {}, remove() {} } }, createElement: () => ({ style: {}, appendChild() {}, classList: { add() {} }, getContext: () => ({}) }) };
globalThis.localStorage ??= { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.location ??= { search: '' };

const { TALK, TALK_TAMSIN, ITEMS, QUESTS, markerFor } = await import('../game/data.js');
const { installSideQuests, letterCount, chipLetter, noteLetterDelivered, hrefna_letters, LETTER_SPOTS } = await import('../game/side_quests.js');

// niflheim.js overwrites these keys at runtime. Stub that previous layer so this test does not load the realm graph.
TALK.hrefna = (S) => {
  const al = ((S.flags || {}).alliance || {}).niflheim;
  const q = S.quests || {};
  if (al === 'befriend' && (q.nf_cold || 0) >= 3 && !q.nf_hrefna) {
    return { pages: ['I carved a rune for her once. I never finished it.', 'Bring me tea that is warm, my mitten from the lake, and a blue rune on the sill. Then maybe I will talk.'] };
  }
  if ((q.nf_hrefna || 0) === 1) return { pages: ['Tea from Tove, the mitten on the lake, the rune on the sill. 0/3.'] };
  return { pages: ['I know this fight. I learned it from her.'] };
};
TALK.archivist = () => ({ pages: ['Vigdis Stillwater. The frost-witches kept their tablets in this room. Mind the ink; it is older than you.'] });

function fresh(extra = {}) {
  return {
    flags: {}, quests: {}, found: {}, inv: {}, met: {},
    ...extra,
    flags: extra.flags || {},
    quests: extra.quests || {},
    found: extra.found || {},
    inv: extra.inv || {},
    met: extra.met || {},
  };
}

function mock(S) {
  const g = {
    S, toasts: [], saves: 0,
    toast(m) { g.toasts.push(m); },
    save() { g.saves += 1; },
    give(id, n = 1) { S.inv = S.inv || {}; S.inv[id] = (S.inv[id] || 0) + n; },
    setQuest(id, stage) { S.quests = S.quests || {}; S.quests[id] = stage; },
  };
  return g;
}

function snap(S) {
  return JSON.parse(JSON.stringify({ quests: S.quests, found: S.found, flags: S.flags, inv: S.inv, met: S.met }));
}

const shell = mock(fresh());
shell.area = 'temple';
shell.nifl = {
  G: shell,
  spots: [],
  spot(o) { this.spots.push({ r: 1.6, show: () => true, ...o }); },
  look(id, name, pages, then) { this.looked = { id, name, pages, then }; },
  home() { this.spots = [{ id: 'grave' }]; },
};
installSideQuests(shell);

const START_PAGES = [
  'The ice wall here keeps things. Breath, light, words. People wrote letters and never sent them, and the cold took them in.',
  'Some of them are still going somewhere. Chip out three. Gently. I will tell you where they belong.',
];
const ADDRESS = 'A fisher in Ravenhold. Brother Tamsin at the temple. And this one... no name. Bring me back the last one when the others are delivered.';

test('item, quest text, and letter spots are the Story block', () => {
  assert.equal(ITEMS.frostveil_gloves.name, 'Frostveil Gloves');
  assert.equal(ITEMS.frostveil_gloves.px, 'tonic');
  assert.equal(ITEMS.frostveil_gloves.about, 'Grey wool, lined with frost-silk. Your fingers stay warm, and cold fire burns a little brighter in them. (Trinket.)');
  assert.equal(QUESTS.sq_frost_letters.title, 'Letters in the Ice');
  assert.equal(QUESTS.sq_frost_letters.side, true);
  assert.equal(QUESTS.sq_lamplit, undefined);
  assert.equal(QUESTS.sq_frost_letters.steps[1]({ found: {} }), 'Chip the unsent letters out of the Gloamhaven ice wall (0/3).');
  assert.equal(QUESTS.sq_frost_letters.steps[1]({ found: { sq_letter1: 1, sq_letter3: 1 } }), 'Chip the unsent letters out of the Gloamhaven ice wall (2/3).');
  assert.equal(QUESTS.sq_frost_letters.steps[2], 'Deliver them: a fisher in Ravenhold, Brother Tamsin, and one with no name on it.');
  assert.equal(QUESTS.sq_frost_letters.steps[3], 'Hrefna kept the last letter.');
  assert.deepEqual(LETTER_SPOTS.map((s) => s.id), ['sq_letter1', 'sq_letter2', 'sq_letter3']);
  assert.deepEqual(hrefna_letters(fresh()).pages, START_PAGES);
});

test('start, chip three letters, Hrefna advances to stage 2', () => {
  const S = fresh();
  const G = mock(S);
  const start = TALK.hrefna(S);
  assert.deepEqual(start.pages, START_PAGES);
  start.then(G);
  assert.equal(S.quests.sq_frost_letters, 1);

  assert.equal(chipLetter(G, 'sq_letter1'), 1);
  assert.equal(S.found.sq_letter1, 1);
  assert.equal(letterCount(S), 1);
  assert.deepEqual(G.toasts, ['Letter 1/3']);
  chipLetter(G, 'sq_letter2');
  assert.equal(letterCount(S), 2);
  assert.equal(S.quests.sq_frost_letters, 1);
  chipLetter(G, 'sq_letter3');
  assert.equal(letterCount(S), 3);
  assert.equal(S.found.sq_letter2, 1);
  assert.equal(S.found.sq_letter3, 1);
  assert.equal(S.quests.sq_frost_letters, 1);
  assert.deepEqual(G.toasts.slice(-2), ['Letter 3/3', 'Hrefna can tell you where they belong.']);
  assert.ok(G.saves >= 3);

  const turn = TALK.hrefna(S);
  assert.equal(turn.pages[0], ADDRESS);
  turn.then(G);
  assert.equal(S.quests.sq_frost_letters, 2);
});

test('home spots show only at stage 1 for letters still in the ice', () => {
  shell.S = fresh();
  shell.nifl.home();
  const ids = shell.nifl.spots.map((s) => s.id);
  assert.ok(ids.includes('grave'));
  for (const id of ['sq_letter1', 'sq_letter2', 'sq_letter3']) assert.ok(ids.includes(id));
  const a = shell.nifl.spots.find((s) => s.id === 'sq_letter1');
  assert.equal(a.show(), false);
  shell.S.quests.sq_frost_letters = 1;
  assert.equal(a.show(), true);
  assert.equal(shell.nifl.spots.find((s) => s.id === 'sq_letter2').show(), true);
  a.act();
  assert.match(shell.nifl.looked.pages[0], /chip it free, gently/);
  shell.toasts = [];
  shell.nifl.looked.then(shell);
  assert.equal(shell.S.found.sq_letter1, 1);
  assert.equal(a.show(), false);
  assert.equal(shell.nifl.spots.find((s) => s.id === 'sq_letter2').show(), true);
  assert.deepEqual(shell.toasts, ['Letter 1/3']);
});

function hand(S, which) {
  const G = mock(S);
  const talk = which === 'fisher' ? TALK.harbormaster(S) : (shell.area = 'temple', TALK.archivist(S));
  talk.then(G);
  return G;
}

test('fisher then Tamsin, and the reverse: sq_letters_given only after both', () => {
  const fisherFirst = fresh({ quests: { sq_frost_letters: 2 } });
  const g1 = hand(fisherFirst, 'fisher');
  assert.equal(fisherFirst.flags.sq_letter_fisher, 1);
  assert.equal(fisherFirst.flags.sq_letter_tamsin, undefined);
  assert.equal(fisherFirst.flags.sq_letters_given, undefined);
  assert.equal(fisherFirst.quests.harbor, undefined);
  assert.equal(fisherFirst.quests.sq_frost_letters, 2);
  assert.equal(g1.S.gold, undefined);
  hand(fisherFirst, 'tamsin');
  assert.equal(fisherFirst.flags.sq_letter_tamsin, 1);
  assert.equal(fisherFirst.flags.sq_letters_given, 1);
  assert.equal(fisherFirst.met.tamsin, undefined);

  const tamsinFirst = fresh({ quests: { sq_frost_letters: 2 } });
  hand(tamsinFirst, 'tamsin');
  assert.equal(tamsinFirst.flags.sq_letter_tamsin, 1);
  assert.equal(tamsinFirst.flags.sq_letters_given, undefined);
  assert.equal(tamsinFirst.quests.harbor, undefined);
  hand(tamsinFirst, 'fisher');
  assert.equal(tamsinFirst.flags.sq_letter_fisher, 1);
  assert.equal(tamsinFirst.flags.sq_letters_given, 1);
  assert.equal(tamsinFirst.quests.harbor, undefined);
});

test('harbormaster letter does not start the harbor quest', () => {
  const S = fresh({ quests: { sq_frost_letters: 2 }, flags: {} });
  const G = mock(S);
  const letter = TALK.harbormaster(S);
  assert.match(letter.pages[0], /fisher in Ravenhold/);
  assert.match(letter.pages[1], /Brannoc/);
  letter.then(G);
  assert.equal(S.quests.harbor, undefined);
  assert.equal(S.gold, undefined);
  assert.equal(S.flags.sq_letter_fisher, 1);
  const next = TALK.harbormaster(S);
  assert.match(next.pages[0], /Harbormaster Brannoc/);
  assert.equal(S.quests.harbor, undefined);
});

test('reward choice A keeps the letter unread; choice B sets sq_letter_read', () => {
  const keepS = fresh({ quests: { sq_frost_letters: 2 }, flags: { sq_letter_fisher: 1, sq_letter_tamsin: 1, sq_letters_given: 1 } });
  const keep = hrefna_letters(keepS);
  assert.equal(keep.choice.id, 'sq_letter_ask');
  const stay = keep.choice.options.find((o) => o.label === 'Keep it. It\'s yours.');
  const gA = mock(keepS);
  const pagesA = stay.pick(gA);
  assert.equal(keepS.inv.frostveil_gloves, 1);
  assert.equal(keepS.quests.sq_frost_letters, 3);
  assert.equal(keepS.flags.sq_letter_read, undefined);
  assert.match(pagesA.pages[0], /Thank you/);

  const askS = fresh({ quests: { sq_frost_letters: 2 }, flags: { sq_letter_fisher: 1, sq_letter_tamsin: 1, sq_letters_given: 1 } });
  const ask = TALK.hrefna(askS);
  const read = ask.choice.options.find((o) => o.label === 'What does it say?');
  const gB = mock(askS);
  const pagesB = read.pick(gB);
  assert.equal(askS.inv.frostveil_gloves, 1);
  assert.equal(askS.quests.sq_frost_letters, 3);
  assert.equal(askS.flags.sq_letter_read, 1);
  assert.match(pagesB.pages[0], /from a sister/);
  assert.match(pagesB.pages[1], /Do not ask again/);
});

test('save and load keeps a half-delivered quest and a finished one', () => {
  const mid = fresh({ quests: { sq_frost_letters: 2 }, found: { sq_letter1: 1, sq_letter2: 1, sq_letter3: 1 } });
  noteLetterDelivered(mock(mid), 'fisher');
  const loaded = fresh(snap(mid));
  assert.equal(loaded.flags.sq_letter_fisher, 1);
  assert.equal(loaded.flags.sq_letter_tamsin, undefined);
  assert.equal(loaded.flags.sq_letters_given, undefined);
  assert.equal(loaded.quests.sq_frost_letters, 2);
  shell.area = 'temple';
  const tamsin = TALK.archivist(loaded);
  assert.match(tamsin.pages[1], /my name on it/);
  const harbor = TALK.harbormaster(loaded);
  assert.match(harbor.pages[0], /Harbormaster Brannoc/);
  assert.equal(loaded.quests.harbor, undefined);

  const done = fresh({
    quests: { sq_frost_letters: 3 },
    found: { sq_letter1: 1, sq_letter2: 1, sq_letter3: 1 },
    flags: { sq_letter_fisher: 1, sq_letter_tamsin: 1, sq_letters_given: 1, sq_letter_read: 1 },
    inv: { frostveil_gloves: 1 },
  });
  const back = fresh(snap(done));
  assert.equal(back.inv.frostveil_gloves, 1);
  assert.equal(back.quests.sq_frost_letters, 3);
  assert.equal(back.flags.sq_letter_read, 1);
  assert.match(hrefna_letters(back).pages[0], /a little emptier/);
  assert.equal(hrefna_letters(back).choice, undefined);
});

test('Hrefna offers the side quest only from her idle line, not a main-quest offer', () => {
  const offer = TALK.hrefna(fresh({ flags: { alliance: { niflheim: 'befriend' } }, quests: { nf_cold: 3 } }));
  assert.match(offer.pages.join(' '), /never finished/);
  assert.match(offer.pages.join(' '), /tea/i);
  assert.doesNotMatch(offer.pages.join(' '), /ice wall/);

  const mid = TALK.hrefna(fresh({ flags: { alliance: { niflheim: 'befriend' } }, quests: { nf_cold: 3, nf_hrefna: 1 } }));
  assert.match(mid.pages[0], /Tea from Tove/);
  assert.doesNotMatch(mid.pages.join(' '), /ice wall/);

  const idle = TALK.hrefna(fresh());
  assert.deepEqual(idle.pages, START_PAGES);
  const conquered = TALK.hrefna(fresh({ flags: { alliance: { niflheim: 'conquer' } } }));
  assert.deepEqual(conquered.pages, START_PAGES);

  const turnIn = TALK.hrefna(fresh({
    flags: { alliance: { niflheim: 'befriend' } },
    quests: { nf_cold: 3, sq_frost_letters: 1 },
    found: { sq_letter1: 1, sq_letter2: 1, sq_letter3: 1 },
  }));
  assert.equal(turnIn.pages[0], ADDRESS);

  assert.equal(markerFor('hrefna', fresh()), 'quest_mark');
  assert.equal(markerFor('hrefna', fresh({
    quests: { sq_frost_letters: 1 },
    found: { sq_letter1: 1, sq_letter2: 1, sq_letter3: 1 },
  })), 'quest_turnin');
  assert.equal(markerFor('hrefna', fresh({
    quests: { sq_frost_letters: 2 },
    flags: { sq_letters_given: 1 },
  })), 'quest_turnin');
});

test('temple shows Tamsin, the Spire shows Vigdis, and markers prefer the harbor turn-in', () => {
  assert.match(TALK_TAMSIN(fresh()).pages[0], /Tamsin, archivist/);
  assert.doesNotMatch(TALK_TAMSIN(fresh()).pages.join(' '), /Vigdis/);

  shell.area = 'temple';
  const meet = TALK.archivist(fresh());
  assert.match(meet.pages[0], /Tamsin, archivist/);
  assert.doesNotMatch(meet.pages.join(' '), /Vigdis/);
  const pending = fresh({ quests: { sq_frost_letters: 2 } });
  const letter = TALK.archivist(pending);
  assert.match(letter.pages[1], /my name on it/);
  letter.then(mock(pending));
  assert.equal(pending.met.tamsin, undefined);
  const later = TALK.archivist(pending);
  assert.match(later.pages[0], /Tamsin, archivist/);

  shell.area = 'frozenspire2';
  const vig = TALK.archivist(fresh({ quests: { sq_frost_letters: 2 } }));
  assert.match(vig.pages[0], /Vigdis Stillwater/);
  assert.doesNotMatch(vig.pages.join(' '), /Tamsin/);

  const letterMark = fresh({ quests: { sq_frost_letters: 2, harbor: 3 } });
  assert.equal(markerFor('harbormaster', letterMark), 'quest_turnin');
  const harborStart = fresh({ quests: { sq_frost_letters: 2 } });
  assert.equal(markerFor('harbormaster', harborStart), 'quest_mark');
  const harborTurn = fresh({ quests: { sq_frost_letters: 2, harbor: 2 }, flags: { rh_gate: 1 } });
  assert.equal(markerFor('harbormaster', harborTurn), 'quest_turnin');
  assert.equal(markerFor('archivist', fresh({ quests: { sq_frost_letters: 2 } })), 'quest_turnin');
  assert.equal(markerFor('archivist', fresh({ quests: { sq_frost_letters: 2 }, flags: { sq_letter_tamsin: 1 } })), null);
});
