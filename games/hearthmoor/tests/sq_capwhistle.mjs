// Mother's Spring: idle start (mushroom and conquer hide), bubble-lamp stays first, verses, reward, save/load.
// vanaheim.js is loaded so the real TALK.tobble (Mother's bubble-lamp) is what installSideQuests captures.
// It pulls alfheim, which imports the browser package `three`. The stub is test-only.
import test from 'node:test';
import assert from 'node:assert/strict';
import { registerHooks } from 'node:module';

registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier === 'three' || specifier.startsWith('three/')) {
      return {
        url: 'data:text/javascript,' + encodeURIComponent('export default {};\n'),
        shortCircuit: true,
        format: 'module',
      };
    }
    return nextResolve(specifier, context);
  },
});

globalThis.window ??= globalThis;
globalThis.document ??= { getElementById: () => null, head: { appendChild() {} }, body: { appendChild() {}, classList: { add() {}, remove() {} } }, createElement: () => ({ style: {}, appendChild() {}, classList: { add() {} }, getContext: () => ({}) }) };
globalThis.localStorage ??= { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.location ??= { search: '' };

const { TALK, QUESTS, ITEMS, markerFor } = await import('../game/data.js');
const { Vanaheim } = await import('../game/vanaheim.js');
const { installSideQuests, tobble_spring, VERSE_SPOTS, verseCount, noteVerse } = await import('../game/side_quests.js');

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
    S, toasts: [], saves: 0, opened: null,
    toast(m) { g.toasts.push(m); },
    save() { g.saves += 1; },
    give(id, n = 1) { S.inv = S.inv || {}; S.inv[id] = (S.inv[id] || 0) + n; },
    setQuest(id, stage) { S.quests = S.quests || {}; S.quests[id] = stage; },
    openDialogue(who, entry) { g.opened = { who, entry }; },
  };
  return g;
}

function snap(S) {
  return JSON.parse(JSON.stringify({
    quests: S.quests, found: S.found, flags: S.flags, inv: S.inv, met: S.met,
  }));
}

function found3() {
  return { sq_verse1: 1, sq_verse2: 1, sq_verse3: 1 };
}

const benchBefore = TALK.tobble_bench;
const benchText = String(TALK.tobble_bench);
const shell = mock(fresh());
installSideQuests(shell);
globalThis.location.search = '?qa';
shell.vana = new Vanaheim(shell);

const SONG = 'My mother used to sing about a spring. "Past the three blue stones, under the singing water, where the moss is purple at noon."';
const START_HELP = 'I always thought it was made up. Will you help me look anyway?';
const START_WON = 'I would like to find it, if Hearthmoor allows us our own springs still.';
const VERSE_TURN = 'Three blue stones, singing water... the waterfall! Behind it. It has to be behind it.';
const PAY_WON = '(A hidden spring, glowing violet.) It is real. Thank you, Hearthmoor. Truly. Please take these, as is proper.';
const PAY_SIT = [
  '(Tobble sits by the violet spring. He does not say anything for a long while.)',
  'She used to hum the last verse wrong on purpose so I would correct her.',
  'Take these. Petals and bells from her spring. She would like you.',
];
const LAMP = "This is Mother's bubble-lamp. It went dark the night the spring went violet. I can fix it. Probably. Possibly.";
const HIDE = '(Tobble hides behind a toadstool and does not come out.)';
const MUSHROOM = "That mushroom is judging us. Don't look at it.";
const COMEBACK = "You came back! The lamp's fine. I told it I'd be brave. Let's go.";
const MONDAY = 'I come here on Mondays now. Mother liked Mondays.';

test('quest text is the Story block and the herbs already exist', () => {
  assert.equal(QUESTS.sq_capwhistle.title, "Mother's Spring");
  assert.equal(QUESTS.sq_capwhistle.giver, 'Tobble Capwhistle');
  assert.equal(QUESTS.sq_capwhistle.side, true);
  assert.equal(QUESTS.sq_capwhistle.steps[1]({ found: {} }), "Follow the verses of Tobble's mother's song (0/3).");
  assert.equal(QUESTS.sq_capwhistle.steps[1]({ found: { sq_verse1: 1, sq_verse3: 1 } }), "Follow the verses of Tobble's mother's song (2/3).");
  assert.equal(QUESTS.sq_capwhistle.steps[2], 'The last verse points behind the waterfall.');
  assert.equal(QUESTS.sq_capwhistle.steps[3](fresh()), 'A violet spring. Tobble sits and says nothing for a while.');
  assert.equal(QUESTS.sq_capwhistle.steps[3](fresh({ flags: { alliance: { vanaheim: 'conquer' } } })), 'A violet spring. Tobble thanks you very formally, and that hurts more.');
  assert.equal(QUESTS.vh_tobble.title, 'Small Brave Things');
  assert.equal(QUESTS.vh_tobble.story, true);
  assert.equal(ITEMS.coldpetal.name, 'Cold-fire petal');
  assert.equal(ITEMS.glowbell.name, 'Violet glowbell');
  assert.equal(ITEMS.springwater.name, 'Spring water');
  assert.deepEqual(VERSE_SPOTS.map((s) => s.id), ['sq_verse1', 'sq_verse2', 'sq_verse3']);
  assert.deepEqual(VERSE_SPOTS.map((s) => s.pos), [[-5.6, -0.8], [6.6, 0.8], [-3.4, -1.8]]);
  assert.deepEqual(tobble_spring(fresh()).pages, [SONG, START_HELP]);
  assert.deepEqual(tobble_spring(fresh({ flags: { alliance: { vanaheim: 'conquer' } } })).pages, [SONG, START_WON]);
});

test('the side quest starts from the mushroom idle and from the conquer hide line', () => {
  const mushroom = fresh({ flags: { alliance: { vanaheim: 'befriend' } } });
  const mushroomTalk = TALK.tobble(mushroom);
  assert.deepEqual(mushroomTalk.pages, [SONG, START_HELP]);
  mushroomTalk.then(mock(mushroom));
  assert.equal(mushroom.quests.sq_capwhistle, 1);
  assert.equal(mushroom.quests.vh_tobble, undefined);

  const hide = fresh({ flags: { alliance: { vanaheim: 'conquer' } } });
  const hideTalk = TALK.tobble(hide);
  assert.deepEqual(hideTalk.pages, [SONG, START_WON]);
  assert.doesNotMatch(hideTalk.pages[0], /hides behind a toadstool/);
  hideTalk.then(mock(hide));
  assert.equal(hide.quests.sq_capwhistle, 1);
  assert.equal(hide.quests.vh_tobble, undefined);
});

test("bubble-lamp offer, fizzstone/glowfry join, and the stage-2 come-back stay first", () => {
  const offer = fresh({ flags: { alliance: { vanaheim: 'befriend' } }, quests: { rotwood: 3 } });
  const offerTalk = TALK.tobble(offer);
  assert.equal(offerTalk.pages[0], LAMP);
  assert.match(offerTalk.pages[1], /fizzstone from a hidden spring/);
  assert.equal(offerTalk.choice, undefined);
  offerTalk.then(mock(offer));
  assert.equal(offer.quests.vh_tobble, 1);
  assert.equal(offer.quests.sq_capwhistle, undefined);

  const join = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { rotwood: 3, vh_tobble: 1 },
    inv: { fizzstone: 1, glowfry: 1, coldpetal: 4 },
  });
  const joinTalk = TALK.tobble(join);
  assert.match(joinTalk.pages[0], /tongue between his teeth/);
  assert.equal(joinTalk.choice.id, 'vh_tobble_join');
  assert.deepEqual(joinTalk.choice.options.map((o) => o.label), [
    'Come on, then. The big ones are waiting.',
    'Not yet. Stay with the lamp a while.',
  ]);
  const joinG = mock(join);
  const joined = joinTalk.choice.options[0].pick(joinG);
  assert.match(joined.pages[0], /other goggles/);
  assert.equal(join.flags.companions.tobble, 1);
  assert.equal(join.inv.fizzstone, 0);
  assert.equal(join.inv.glowfry, 0);
  assert.equal(join.inv.coldpetal, 4);
  assert.equal(join.quests.vh_tobble, 3);
  assert.equal(join.quests.sq_capwhistle, undefined);
  assert.match(joinG.toasts[0], /Tobble Capwhistle joins you/);

  const stay = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { vh_tobble: 1 },
    inv: { fizzstone: 2, glowfry: 1 },
  });
  const stayed = TALK.tobble(stay).choice.options[1].pick(mock(stay));
  assert.match(stayed.pages[0], /Gnome-promise/);
  assert.equal(stay.quests.vh_tobble, 2);
  assert.equal(stay.quests.sq_capwhistle, undefined);
  assert.equal(stay.inv.fizzstone, 2);
  assert.equal(stay.flags.companions, undefined);
  assert.equal(TALK.tobble(stay).pages[0], COMEBACK);

  const back = fresh({ flags: { alliance: { vanaheim: 'befriend' } }, quests: { vh_tobble: 2 } });
  const backTalk = TALK.tobble(back);
  assert.equal(backTalk.pages[0], COMEBACK);
  assert.equal(backTalk.choice, undefined);
  backTalk.then(mock(back));
  assert.equal(back.flags.companions.tobble, 1);
  assert.equal(back.quests.vh_tobble, 3);
  assert.equal(back.quests.sq_capwhistle, undefined);
  const after = TALK.tobble(back);
  assert.deepEqual(after.pages, [SONG, START_HELP]);
  assert.equal(back.quests.sq_capwhistle, undefined);
});

test('ready verses and the spring reward beat the bubble-lamp, the join, and the come-back', () => {
  const offer = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { rotwood: 3, sq_capwhistle: 1 },
    found: found3(),
  });
  const offerTalk = TALK.tobble(offer);
  assert.equal(offerTalk.pages[0], VERSE_TURN);
  assert.equal(offerTalk.choice, undefined);
  offerTalk.then(mock(offer));
  assert.equal(offer.quests.sq_capwhistle, 2);
  assert.equal(offer.quests.vh_tobble, undefined);

  const join = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { vh_tobble: 1, sq_capwhistle: 1 },
    inv: { fizzstone: 1, glowfry: 1 },
    found: found3(),
  });
  assert.equal(TALK.tobble(join).pages[0], VERSE_TURN);
  assert.equal(TALK.tobble(join).choice, undefined);
  assert.equal(join.inv.fizzstone, 1);

  const back = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { vh_tobble: 2, sq_capwhistle: 2 },
    inv: { coldpetal: 1 },
  });
  const backTalk = TALK.tobble(back);
  assert.deepEqual(backTalk.pages, PAY_SIT);
  const backG = mock(back);
  backTalk.then(backG);
  assert.equal(back.quests.sq_capwhistle, 3);
  assert.equal(back.quests.vh_tobble, 2);
  assert.equal(back.flags.companions, undefined);
  assert.equal(back.inv.coldpetal, 4);
  assert.equal(back.inv.glowbell, 3);
  assert.equal(back.inv.springwater, 2);

  const won = fresh({
    flags: { alliance: { vanaheim: 'conquer' } },
    quests: { vh_tobble: 2, sq_capwhistle: 2 },
  });
  const wonTalk = TALK.tobble(won);
  assert.deepEqual(wonTalk.pages, [PAY_WON]);
  wonTalk.then(mock(won));
  assert.equal(won.inv.coldpetal, 3);
  assert.equal(won.inv.glowbell, 3);
  assert.equal(won.inv.springwater, 2);
  assert.equal(won.quests.sq_capwhistle, 3);
  assert.equal(won.quests.vh_tobble, 2);
  assert.equal(TALK.tobble(won).pages[0], HIDE);
  assert.equal(tobble_spring(won).pages[0], MONDAY);
});

test('verse count, spots, and save/load', () => {
  const S = fresh({ flags: { alliance: { vanaheim: 'befriend' } }, quests: { sq_capwhistle: 1 } });
  const G = mock(S);
  assert.equal(noteVerse(G, 'sq_verse1'), 1);
  assert.equal(S.found.sq_verse1, 1);
  assert.equal(verseCount(S), 1);
  assert.deepEqual(G.toasts, ['Verse 1/3']);
  noteVerse(G, 'sq_verse1');
  assert.equal(verseCount(S), 1);
  noteVerse(G, 'sq_verse2');
  assert.equal(S.quests.sq_capwhistle, 1);
  assert.equal(TALK.tobble(S).pages[0], MUSHROOM);
  assert.equal(QUESTS.sq_capwhistle.steps[1](S), "Follow the verses of Tobble's mother's song (2/3).");
  assert.equal(tobble_spring(S).pages[0], MONDAY);

  const loaded = fresh(snap(S));
  assert.equal(loaded.quests.sq_capwhistle, 1);
  assert.equal(loaded.found.sq_verse1, 1);
  assert.equal(loaded.found.sq_verse2, 1);
  assert.equal(loaded.found.sq_verse3, undefined);
  assert.equal(verseCount(loaded), 2);
  assert.equal(TALK.tobble(loaded).pages[0], MUSHROOM);

  noteVerse(G, 'sq_verse3');
  assert.equal(verseCount(S), 3);
  assert.equal(S.quests.sq_capwhistle, 1);
  assert.deepEqual(G.toasts.slice(-2), ['Verse 3/3', 'Tobble can place the last line.']);
  assert.ok(G.saves >= 3);
  assert.equal(TALK.tobble(S).pages[0], VERSE_TURN);

  const ctx = { scene: {}, player: { x: 0, z: 0 } };
  shell.S = fresh();
  shell.vana.attach(ctx, 'vh_village');
  assert.equal(shell.vana.spots.some((s) => String(s.id || '').startsWith('sq_verse')), false);
  shell.vana.attach(ctx, 'vanaheim');
  const ids = shell.vana.spots.map((s) => s.id);
  assert.deepEqual(ids.filter((id) => String(id || '').startsWith('sq_verse')), ['sq_verse1', 'sq_verse2', 'sq_verse3']);
  const a = shell.vana.spots.find((s) => s.id === 'sq_verse1');
  assert.equal(a.show(), false);
  assert.equal(a.r, 1.2);
  assert.deepEqual(a.pos, [-5.6, -0.8]);
  shell.S.quests.sq_capwhistle = 1;
  assert.equal(a.show(), true);
  assert.equal(shell.vana.spots.find((s) => s.id === 'sq_verse3').show(), true);
  shell.toasts = [];
  a.act();
  assert.equal(shell.opened.who.name, 'Blue stones');
  assert.match(shell.opened.entry.pages[0], /three blue stones/);
  assert.doesNotMatch(shell.opened.entry.pages[0], /waterfall/);
  shell.opened.entry.then(shell);
  assert.equal(shell.S.found.sq_verse1, 1);
  assert.equal(a.show(), false);
  assert.equal(shell.vana.spots.find((s) => s.id === 'sq_verse2').show(), true);
  assert.deepEqual(shell.toasts, ['Verse 1/3']);
  assert.equal(shell.S.quests.sq_capwhistle, 1);

  const done = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { sq_capwhistle: 3 },
    found: found3(),
    inv: { coldpetal: 3, glowbell: 3, springwater: 2 },
  });
  const back = fresh(snap(done));
  assert.equal(back.quests.sq_capwhistle, 3);
  assert.equal(back.inv.coldpetal, 3);
  assert.equal(back.inv.glowbell, 3);
  assert.equal(back.inv.springwater, 2);
  assert.equal(verseCount(back), 3);
  assert.equal(TALK.tobble(back).pages[0], MUSHROOM);
  assert.equal(tobble_spring(back).pages[0], MONDAY);
});

test('the side marker does not steal vh_tobble, and marks a ready turn-in only', () => {
  assert.equal(markerFor('tobble', fresh()), null);
  assert.equal(markerFor('tobble', fresh({ flags: { alliance: { vanaheim: 'befriend' } } })), null);
  assert.equal(markerFor('tobble', fresh({ flags: { alliance: { vanaheim: 'conquer' } } })), null);
  assert.equal(markerFor('tobble', fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { rotwood: 3 },
  })), 'quest_mark');
  assert.equal(markerFor('tobble', fresh({
    quests: { vh_tobble: 1 },
    inv: { fizzstone: 1, glowfry: 1 },
  })), 'quest_turnin');

  const overlap = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { rotwood: 3, sq_capwhistle: 1 },
    found: found3(),
  });
  assert.equal(markerFor('tobble', overlap), 'quest_mark');
  assert.equal(TALK.tobble(overlap).pages[0], VERSE_TURN);

  const joinReady = fresh({
    quests: { vh_tobble: 1, sq_capwhistle: 2 },
    inv: { fizzstone: 1, glowfry: 1 },
  });
  assert.equal(markerFor('tobble', joinReady), 'quest_turnin');
  assert.equal(TALK.tobble(joinReady).pages[0], PAY_SIT[0]);

  assert.equal(markerFor('tobble', fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { sq_capwhistle: 1 },
    found: found3(),
  })), 'quest_turnin');
  assert.equal(markerFor('tobble', fresh({ quests: { sq_capwhistle: 2 } })), 'quest_turnin');
  assert.equal(markerFor('tobble', fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { vh_tobble: 2, sq_capwhistle: 2 },
  })), 'quest_turnin');
  assert.equal(markerFor('tobble', fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { vh_tobble: 2 },
  })), null);
  assert.equal(markerFor('tobble', fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { sq_capwhistle: 1 },
    found: { sq_verse1: 1, sq_verse2: 1 },
  })), null);
  assert.equal(markerFor('tobble', fresh({ quests: { sq_capwhistle: 3 }, found: found3() })), null);
});

test("TALK.tobble_bench still exists and is unchanged", () => {
  assert.equal(typeof TALK.tobble_bench, 'function');
  assert.equal(TALK.tobble_bench, benchBefore);
  assert.equal(String(TALK.tobble_bench), benchText);
  assert.deepEqual(TALK.tobble_bench(fresh()).pages, ['(A gnome workbench. Every drawer is labelled "NOT THIS ONE".)']);
  const staff = fresh({
    flags: { alliance: { vanaheim: 'befriend' } },
    quests: { vh_tobble: 3, verdant: 3 },
  });
  assert.match(TALK.tobble_bench(staff).pages[0], /three fizzstones/);
});
