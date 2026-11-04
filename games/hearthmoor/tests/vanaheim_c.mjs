// Pure flag logic for Vanaheim Stage C: star count, hushed Mossbrook, Hollis, riddle answers.
import test from 'node:test';
import assert from 'node:assert/strict';

globalThis.window ??= globalThis;
globalThis.document ??= { getElementById: () => null, head: { appendChild() {} }, body: { appendChild() {}, classList: { add() {}, remove() {} } }, createElement: () => ({ style: {}, appendChild() {}, classList: { add() {} } }) };
globalThis.localStorage ??= { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.location ??= { search: '' };

const { HUSHED, HUSHED_BARKS, hushedBark, HOLLIS, STARS, readStar, bloomRiddle, BLOOM_RIDDLES, VH_NIGHT, vhMarkerC } = await import('../game/vanaheim_c.js');
const { TALK } = await import('../game/data.js');

function mock(S) {
  const g = {
    S, secrets: 0, riddles: 0, merit: [],
    factions: {
      onSecret() { g.secrets += 1; },
      onRiddle() { g.riddles += 1; },
      add(id, n, why) { g.merit.push([id, n, why]); },
    },
    toast() {},
    save() {},
    give(id, n = 1) { S.inv = S.inv || {}; S.inv[id] = (S.inv[id] || 0) + n; },
    take(id, n = 1) { S.inv[id] = Math.max(0, (S.inv[id] || 0) - n); if (!S.inv[id]) delete S.inv[id]; },
    setQuest(id, stage) { S.quests = S.quests || {}; S.quests[id] = stage; },
    drawBag() {},
  };
  return g;
}

test('stars: three toadstools count once each, and mood < 0 withholds them', () => {
  assert.equal(STARS.length, 3);
  const S = { flags: { realm_mood: { vanaheim: 0 } } };
  assert.equal(readStar(S, 0), 1);
  assert.equal(readStar(S, 0), 1);
  assert.equal(readStar(S, 2), 2);
  assert.equal(readStar(S, 1), 3);
  assert.equal(S.flags.vh_stars, 3);
  const sulk = { flags: { realm_mood: { vanaheim: -1 } } };
  assert.equal(readStar(sulk, 0), 0);
  assert.equal(sulk.flags.vh_stars, undefined);
  assert.equal(readStar(S, 0), 3);
  S.flags.realm_mood.vanaheim = -1;
  assert.equal(readStar(S, 0), 3);
  const turn = TALK.stargnome(S);
  assert.match(turn.pages[0], /telescope/);
  assert.equal(turn.then, undefined);
  S.flags.realm_mood.vanaheim = 0;
  const pay = TALK.stargnome(S);
  const G = mock(S);
  S.bag = [];
  pay.then(G);
  assert.equal(S.flags.vh_stars_done, 1);
  assert.equal(S.bag[0].unique, 'foresight_charm');
  assert.deepEqual(G.merit[0], ['embassy', 40, 'vh_stars']);
  assert.equal(readStar(S, 1), 3);
});

test('hushed Mossbrook is conquer plus a finished tithe, one bark per day', () => {
  assert.equal(HUSHED({ flags: { alliance: { vanaheim: 'conquer' } }, quests: { vh_tithe: 3 } }), true);
  assert.equal(HUSHED({ flags: { alliance: { vanaheim: 'befriend' } }, quests: { vh_tithe: 3 } }), false);
  assert.equal(HUSHED({ flags: { alliance: { vanaheim: 'conquer' } }, quests: { vh_tithe: 2 } }), false);
  assert.equal(HUSHED({ flags: { alliance: { vanaheim: 'conquer' } } }), false);
  assert.equal(HUSHED_BARKS.length, 3);
  assert.equal(hushedBark({ day: 0 }), HUSHED_BARKS[0]);
  assert.equal(hushedBark({ day: 1 }), HUSHED_BARKS[1]);
  assert.equal(hushedBark({ day: 4 }), HUSHED_BARKS[1]);
});

test('Hollis sets vh_hollis on an answer and not on Leave, night only', () => {
  assert.equal(HOLLIS.night, true);
  assert.deepEqual(HOLLIS.pos, [-1.2, 1.4]);
  const S = { flags: {} };
  const e = TALK.hollis(S);
  assert.equal(e.choice.options.length, 3);
  const leave = e.choice.options.find((o) => o.cancel);
  leave.pick(mock(S));
  assert.equal(S.flags.vh_hollis, undefined);
  const yes = e.choice.options.find((o) => o.label.startsWith('Yes'));
  const G = mock(S);
  const next = yes.pick(G);
  assert.equal(S.flags.vh_hollis, 1);
  assert.equal(G.secrets, 1);
  assert.match(next.pages[0], /no curse/);
  const again = TALK.hollis(S);
  assert.equal(again.choice, undefined);
  assert.match(again.pages[0], /Still not cursed/);
});

test('riddle stump and Bloomtide riddles pay only on the right answers', () => {
  const S = { flags: {} };
  const stump = TALK.riddlestump(S);
  const G = mock(S);
  const wrong = stump.choice.options.find((o) => o.label === 'A very old gnome');
  const no = wrong.pick(G);
  assert.match(no.pages[0], /Tempting/);
  assert.equal(S.flags.vh_stump, undefined);
  assert.equal(G.riddles, 0);
  const right = stump.choice.options.find((o) => o.label === 'A tree stump');
  const yes = right.pick(G);
  assert.equal(S.flags.vh_stump, 1);
  assert.equal(G.riddles, 1);
  assert.match(yes.pages[0], /Correct/);
  assert.match(TALK.riddlestump(S).pages[0], /asleep/);

  const R = mock({ flags: {} });
  let node = bloomRiddle(R, 0);
  assert.equal(BLOOM_RIDDLES.length, 3);
  for (let i = 0; i < BLOOM_RIDDLES.length; i++) {
    const r = BLOOM_RIDDLES[i];
    const miss = node.choice.options.find((o) => o.label === r.wrong[0]).pick(R);
    assert.match(miss.pages[0], /Pibb/);
    assert.equal(R.S.flags.vh_bloom_games, undefined);
    assert.equal(R.riddles, 0);
    node = node.choice.options.find((o) => o.label === r.right).pick(R);
  }
  assert.equal(R.S.flags.vh_bloom_games.riddle, 1);
  assert.equal(R.riddles, 1);
  assert.match(node.pages[0], /Three for three/);
});

test('night window matches the realm clock, and Morel turns in five caps', () => {
  assert.equal(VH_NIGHT(0), true);
  assert.equal(VH_NIGHT(0.24), true);
  assert.equal(VH_NIGHT(0.25), false);
  assert.equal(VH_NIGHT(0.5), false);
  assert.equal(VH_NIGHT(0.8), false);
  assert.equal(VH_NIGHT(0.81), true);
  assert.equal(VH_NIGHT(undefined), false);
  const S = { flags: {}, inv: { glowcap: 5 }, gold: 3 };
  const open = TALK.capseller(S);
  const G = mock(S);
  open.then(G);
  assert.equal(S.flags.vh_morel, 1);
  assert.match(TALK.capseller(S).pages[0], /Five glow-caps/);
  const turn = TALK.capseller(S);
  turn.then(G);
  assert.equal(S.flags.vh_morel, 2);
  assert.equal(S.inv.glowcap, undefined);
  assert.equal(S.gold, 43);
  assert.deepEqual(G.merit[0], ['embassy', 40, 'vh_morel']);
  assert.equal(vhMarkerC({ flags: { vh_morel: 1 }, inv: { glowcap: 5 } }, 'capseller'), 'quest_turnin');
  assert.equal(vhMarkerC({ flags: { alliance: { vanaheim: 'befriend' }, vh_bloom_games: { harvest: 1, dance: 1, riddle: 1 } }, quests: { vh_bloom: 1 } }, 'nymph_vh'), 'quest_turnin');
  assert.equal(vhMarkerC({ flags: { alliance: { vanaheim: 'befriend' } }, quests: { vh_hex: 3 } }, 'warden'), 'quest_mark');
  assert.equal(vhMarkerC({ flags: { alliance: { vanaheim: 'befriend' }, gr_i: 1 }, quests: { vh_hex: 3 }, lv: 4, ranks: { embassy: 2 } }, 'warden'), null);
});
