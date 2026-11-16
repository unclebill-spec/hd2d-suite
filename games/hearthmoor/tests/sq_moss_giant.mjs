// Lullaby for a Hill: idle start, Ulfar's Walk and Dark Stonehollow stay first, lullaby retries, reward, save/load.
// jotunheim.js is loaded so the real TALK.ulfar (Walk + dark wrap) is what installSideQuests captures.
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
await import('../game/jotunheim.js');
const { installSideQuests, ulfar_hill } = await import('../game/side_quests.js');

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
    S, toasts: [],
    jot: { walks: 0, afterWalk() { g.jot.walks += 1; } },
    toast(m) { g.toasts.push(m); },
    give(id, n = 1) { S.inv = S.inv || {}; S.inv[id] = (S.inv[id] || 0) + n; },
    setQuest(id, stage) { S.quests = S.quests || {}; S.quests[id] = stage; },
  };
  return g;
}

function snap(S) {
  return JSON.parse(JSON.stringify({
    quests: S.quests, found: S.found, flags: S.flags, inv: S.inv, met: S.met, gems: S.gems,
  }));
}

installSideQuests(mock(fresh()));

const START = [
  'Hear that rumble? That is not a storm. That is Old Hrolf, asleep on the road. Snoring.',
  'Every snore cracks the ice. We sing him a lullaby, he rolls over, and the road is clear. Grandmother\'s way.',
  'The song needs three red toadstool caps, glowing. Ask me why and I will tell you: I do not know. Grandmother\'s way.',
];

test('quest text uses the existing redcap count and the Story steps', () => {
  assert.equal(QUESTS.sq_moss_giant.title, 'Lullaby for a Hill');
  assert.equal(QUESTS.sq_moss_giant.giver, 'Ulfar Mossback');
  assert.equal(QUESTS.sq_moss_giant.side, true);
  assert.equal(QUESTS.sq_moss_giant.steps[1]({}), 'Gather three red toadstool caps for the lullaby (0/3).');
  assert.equal(QUESTS.sq_moss_giant.steps[1]({ inv: { redcap: 2 } }), 'Gather three red toadstool caps for the lullaby (2/3).');
  assert.equal(QUESTS.sq_moss_giant.steps[1]({ inv: { redcap: 9 } }), 'Gather three red toadstool caps for the lullaby (3/3).');
  assert.equal(QUESTS.sq_moss_giant.steps[2], 'Sing to the hill. Low, high, low. Softly.');
  assert.equal(QUESTS.sq_moss_giant.steps[3], 'The hill sighs, rolls over, and shows you a hidden spring.');
  assert.equal(QUESTS.jt_ulfar.title, "Ulfar's Walk");
  assert.equal(QUESTS.jt_ulfar.story, true);
  assert.equal(ITEMS.redcap.name, 'Red toadstool cap');
  assert.equal(ITEMS.springwater.name, 'Spring water');
  assert.deepEqual(ulfar_hill(fresh()).pages, START);
});

test('the side quest starts from both idle lines and not from Ulfar\'s Walk', () => {
  const hello = fresh();
  const helloTalk = TALK.ulfar(hello);
  assert.deepEqual(helloTalk.pages, START);
  helloTalk.then(mock(hello));
  assert.equal(hello.quests.sq_moss_giant, 1);
  assert.equal(hello.quests.jt_ulfar, undefined);
  assert.equal(hello.met.ulfar, undefined);

  const snow = fresh({ met: { ulfar: 1 }, quests: { jt_ulfar: 3 }, flags: { alliance: { jotunheim: 'befriend' } } });
  const snowTalk = TALK.ulfar(snow);
  assert.deepEqual(snowTalk.pages, START);
  assert.doesNotMatch(snowTalk.pages[0], /Snow tastes like nothing/);

  const offer = fresh({ flags: { alliance: { jotunheim: 'befriend' } }, quests: { jt_welcome: 3 } });
  const offerTalk = TALK.ulfar(offer);
  assert.match(offerTalk.pages[0], /Small one\. You lifted our stones/);
  assert.doesNotMatch(offerTalk.pages.join(' '), /Old Hrolf|toadstool/);
  const offerG = mock(offer);
  offerTalk.then(offerG);
  assert.equal(offer.quests.jt_ulfar, 1);
  assert.equal(offer.quests.sq_moss_giant, undefined);
  assert.equal(offer.met.ulfar, 1);
  assert.match(offerG.toasts[0], /Ulfar's Walk/);

  const remind = fresh({
    met: { ulfar: 1 },
    flags: { alliance: { jotunheim: 'befriend' } },
    quests: { jt_welcome: 3, jt_ulfar: 1 },
    found: { uw_goat: 1 },
  });
  const remindTalk = TALK.ulfar(remind);
  assert.match(remindTalk.pages[0], /Turnip, the song, the mitten\. 1 of three/);
  assert.equal(remind.quests.sq_moss_giant, undefined);

  const walk = fresh({
    met: { ulfar: 1 },
    flags: { alliance: { jotunheim: 'befriend' } },
    quests: { jt_welcome: 3, jt_ulfar: 1 },
    found: { uw_goat: 1, uw_song: 1, uw_mitten: 1 },
  });
  const walkTalk = TALK.ulfar(walk);
  assert.match(walkTalk.pages[0], /All three!/);
  assert.match(walkTalk.pages[1], /Walk with me to the Barrow door/);
  const walkG = mock(walk);
  walkTalk.then(walkG);
  assert.equal(walk.quests.jt_ulfar, 2);
  assert.equal(walk.flags.uw_walk, 1);
  assert.equal(walkG.jot.walks, 1);
  assert.equal(walk.quests.sq_moss_giant, undefined);
});

test('Dark Stonehollow wins over the side quest start', () => {
  const dark = fresh({ flags: { jt_dark: 1, alliance: { jotunheim: 'conquer' } } });
  const talk = TALK.ulfar(dark);
  assert.match(talk.pages[0], /^\(Ulfar looks at the lake/);
  assert.match(talk.pages[1], /The fires went out/);
  assert.equal(talk.choice, undefined);
  assert.equal(dark.quests.sq_moss_giant, undefined);

  const metDark = fresh({ met: { ulfar: 1 }, flags: { jt_dark: 1, alliance: { jotunheim: 'conquer' } } });
  assert.match(TALK.ulfar(metDark).pages[0], /^\(Ulfar looks at the lake/);
});

test('the right lullaby spends three caps; both wrong notes retry', () => {
  const S = fresh({ met: { ulfar: 1 }, quests: { sq_moss_giant: 1 }, inv: { redcap: 5 } });
  const choice = TALK.ulfar(S);
  assert.equal(choice.choice.id, 'sq_lullaby');
  assert.deepEqual(choice.choice.options.map((o) => o.label), ['Low, high, low.', 'High, low, high.', 'Low, low, low.']);

  const high = choice.choice.options[1].pick(mock(S));
  assert.match(high.pages[0], /The hill grumbles/);
  assert.match(high.pages[1], /Wrong one first/);
  assert.equal(S.inv.redcap, 5);
  assert.equal(S.quests.sq_moss_giant, 1);

  const low = TALK.ulfar(S).choice.options[2].pick(mock(S));
  assert.match(low.pages[0], /snores louder/);
  assert.match(low.pages[1], /sleep deeper/);
  assert.equal(S.inv.redcap, 5);
  assert.equal(S.quests.sq_moss_giant, 1);
  assert.equal(TALK.ulfar(S).choice.id, 'sq_lullaby');

  const G = mock(S);
  const sung = TALK.ulfar(S).choice.options[0].pick(G);
  assert.equal(S.inv.redcap, 2);
  assert.equal(S.quests.sq_moss_giant, 2);
  assert.match(sung.pages[0], /The hill hums back/);
  assert.match(sung.pages[1], /best spring in Jotunheim/);
  assert.equal(S.inv.springwater, undefined);
  assert.equal(S.gems, undefined);

  const pay = TALK.ulfar(S);
  assert.match(pay.pages[0], /hidden spring, glowing blue/);
  assert.equal(pay.choice, undefined);
  pay.then(G);
  assert.equal(S.inv.springwater, 3);
  assert.equal(S.gems.moon_opal, 1);
  assert.equal(S.quests.sq_moss_giant, 3);
  assert.match(TALK.ulfar(S).pages[0], /^Snow tastes like nothing/);
  assert.match(ulfar_hill(S).pages[0], /snoring on the other side of the road/);
  assert.equal(ulfar_hill(fresh({ quests: { sq_moss_giant: 1 }, inv: { redcap: 2 } })).pages[0], 'Three red caps. You have 2.');
});

test('a ready lullaby or the spring reward beats Ulfar\'s Walk and the dark line', () => {
  const offer = fresh({
    flags: { alliance: { jotunheim: 'befriend' } },
    quests: { jt_welcome: 3, sq_moss_giant: 1 },
    inv: { redcap: 3 },
  });
  assert.equal(TALK.ulfar(offer).choice.id, 'sq_lullaby');
  assert.equal(offer.quests.jt_ulfar, undefined);

  const darkPay = fresh({
    met: { ulfar: 1 },
    flags: { jt_dark: 1, alliance: { jotunheim: 'conquer' } },
    quests: { sq_moss_giant: 2 },
  });
  assert.match(TALK.ulfar(darkPay).pages[0], /hidden spring, glowing blue/);
});

test('save and load keeps a half-sung lullaby and a paid one', () => {
  const mid = fresh({ met: { ulfar: 1 }, quests: { sq_moss_giant: 1 }, inv: { redcap: 2 } });
  const loaded = fresh(snap(mid));
  assert.equal(loaded.quests.sq_moss_giant, 1);
  assert.equal(loaded.inv.redcap, 2);
  assert.match(TALK.ulfar(loaded).pages[0], /^Snow tastes like nothing/);
  assert.equal(loaded.quests.sq_moss_giant, 1);
  assert.equal(QUESTS.sq_moss_giant.steps[1](loaded), 'Gather three red toadstool caps for the lullaby (2/3).');
  loaded.inv.redcap = 3;
  assert.equal(TALK.ulfar(loaded).choice.id, 'sq_lullaby');

  const done = fresh({
    met: { ulfar: 1 },
    quests: { sq_moss_giant: 3 },
    inv: { redcap: 2, springwater: 3 },
    gems: { moon_opal: 1 },
  });
  const back = fresh(snap(done));
  assert.equal(back.quests.sq_moss_giant, 3);
  assert.equal(back.inv.springwater, 3);
  assert.equal(back.inv.redcap, 2);
  assert.equal(back.gems.moon_opal, 1);
  assert.match(TALK.ulfar(back).pages[0], /^Snow tastes like nothing/);
  assert.match(ulfar_hill(back).pages[0], /other side of the road/);
  assert.equal(back.quests.sq_moss_giant, 3);
});

test('the side marker does not steal Ulfar\'s Walk, and marks a ready turn-in only', () => {
  // No start quest_mark: Ulfar's phone-landscape crop already clips the head, and a
  // start ! drops official sprites_sharp corr to ~0.72. Talk still starts the quest from idle.
  assert.equal(markerFor('ulfar', fresh()), null);
  assert.equal(markerFor('ulfar', fresh({ met: { ulfar: 1 } })), null);
  assert.equal(markerFor('ulfar', fresh({
    flags: { alliance: { jotunheim: 'befriend' } },
    quests: { jt_welcome: 3 },
  })), 'quest_mark');

  const overlap = fresh({
    flags: { alliance: { jotunheim: 'befriend' } },
    quests: { jt_welcome: 3, sq_moss_giant: 1 },
    inv: { redcap: 3 },
  });
  assert.equal(markerFor('ulfar', overlap), 'quest_mark');
  assert.equal(TALK.ulfar(overlap).choice.id, 'sq_lullaby');

  const walkReady = fresh({
    flags: { alliance: { jotunheim: 'befriend' } },
    quests: { jt_welcome: 3, jt_ulfar: 1, sq_moss_giant: 2 },
    found: { uw_goat: 1, uw_song: 1, uw_mitten: 1 },
  });
  assert.equal(markerFor('ulfar', walkReady), 'quest_mark');
  assert.match(TALK.ulfar(walkReady).pages[0], /hidden spring/);

  assert.equal(markerFor('ulfar', fresh({ met: { ulfar: 1 }, quests: { sq_moss_giant: 1 }, inv: { redcap: 3 } })), 'quest_turnin');
  assert.equal(markerFor('ulfar', fresh({ met: { ulfar: 1 }, quests: { sq_moss_giant: 2 } })), 'quest_turnin');
  assert.equal(markerFor('ulfar', fresh({ met: { ulfar: 1 }, quests: { sq_moss_giant: 1 }, inv: { redcap: 2 } })), null);
  assert.equal(markerFor('ulfar', fresh({ met: { ulfar: 1 }, quests: { sq_moss_giant: 3 } })), null);
  assert.equal(markerFor('ulfar', fresh({ flags: { jt_dark: 1, alliance: { jotunheim: 'conquer' } } })), null);
});
