// The Pale Road: start, orb+fish turn-in, three lights, gold, save/load.
// TALK.ferryman stays Corvin's raven quest. TALK.solvi starts sq_lantern_walk.
import test from 'node:test';
import assert from 'node:assert/strict';
import { registerHooks } from 'node:module';

// helheim.js loads alfheim, which imports the browser package `three`. Node has no import map.
// The stub exists only so this test can load Corvin's TALK.ferryman. It is not a game module.
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

const { TALK, QUESTS, markerFor } = await import('../game/data.js');
const { installSideQuests, solvi_ferry, LIGHT_SPOTS, collectLight, lightCount } = await import('../game/side_quests.js');
await import('../game/helheim.js');

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
  return JSON.parse(JSON.stringify({ quests: S.quests, found: S.found, flags: S.flags, inv: S.inv, gold: S.gold }));
}

const corvin = TALK.ferryman;
const shell = mock(fresh());
shell.area = 'hh_shore';
const hel = {
  G: shell,
  spots: [],
  fx: [],
  ctx: null,
  spot(o) { this.spots.push({ r: 1.6, show: () => true, ...o }); },
  look(id, name, pages, then) { this.looked = { id, name, pages, then }; },
  shore() { this.spots = []; },
  ctx: {},
  fxAt(ctx, name, x, y, z, o) { this.fx.push({ name, x, y, z, o }); },
};
installSideQuests(shell);
shell.hel = hel;

const START_PAGES = [
  '(An old man in a grey wool coat leans on a ferry pole. He speaks so quietly you lean in.)',
  'Sölvi. I take the lights across. But some walk the pale road and never find the ferry.',
  'They follow light. Bring me an empty orb and a glow-fish, and carry it down the road for them.',
];
const REMIND = ['An orb, and a fish to light it.'];
const NOD = ['(Sölvi nods once. That is all.)'];

test('quest text and light spots are the Story block', () => {
  assert.equal(QUESTS.sq_lantern_walk.title, 'The Pale Road');
  assert.equal(QUESTS.sq_lantern_walk.giver, 'Sölvi the Ferryman');
  assert.equal(QUESTS.sq_lantern_walk.side, true);
  assert.equal(QUESTS.sq_lamplit, undefined);
  assert.equal(QUESTS.sq_lantern_walk.steps[1], 'Bring an empty orb and a glow-fish to Sölvi, and carry the light down the pale road.');
  assert.equal(QUESTS.sq_lantern_walk.steps[2]({ found: {} }), 'Lead the lost lights back to the ferry (0/3).');
  assert.equal(QUESTS.sq_lantern_walk.steps[2]({ found: { sq_light1: 1, sq_light3: 1 } }), 'Lead the lost lights back to the ferry (2/3).');
  assert.equal(QUESTS.sq_lantern_walk.steps[3], 'Sölvi nods once. A little pale light follows you home.');
  assert.deepEqual(LIGHT_SPOTS.map((s) => s.id), ['sq_light1', 'sq_light2', 'sq_light3']);
  assert.equal(TALK.solvi, solvi_ferry);
  assert.deepEqual(solvi_ferry(fresh()).pages, START_PAGES);
});

test('start, mid reminder without items, then one orb and one fish', () => {
  const S = fresh();
  const G = mock(S);
  const start = TALK.solvi(S);
  assert.deepEqual(start.pages, START_PAGES);
  start.then(G);
  assert.equal(S.quests.sq_lantern_walk, 1);

  const bare = TALK.solvi(S);
  assert.deepEqual(bare.pages, REMIND);
  assert.equal(bare.then, undefined);

  S.inv.orblamp = 3;
  const fishless = TALK.solvi(S);
  assert.deepEqual(fishless.pages, REMIND);
  assert.equal(S.inv.orblamp, 3);

  S.inv.glowfish = 2;
  S.inv.tonic = 4;
  const turn = TALK.solvi(S);
  assert.match(turn.pages[0], /glow-fish in the orb/);
  turn.then(G);
  assert.equal(S.quests.sq_lantern_walk, 2);
  assert.equal(S.inv.orblamp, 2);
  assert.equal(S.inv.glowfish, 1);
  assert.equal(S.inv.tonic, 4);
  assert.deepEqual(TALK.solvi(S).pages, REMIND);
  assert.equal(S.inv.orblamp, 2);
  assert.equal(S.inv.glowfish, 1);
});

test('three lights stay at stage 2 until Sölvi pays 120 gold', () => {
  const S = fresh({ quests: { sq_lantern_walk: 2 }, inv: { orblamp: 2, glowfish: 1 } });
  const G = mock(S);
  assert.equal(collectLight(G, 'sq_light1'), 1);
  assert.equal(S.found.sq_light1, 1);
  assert.equal(lightCount(S), 1);
  assert.equal(S.quests.sq_lantern_walk, 2);
  collectLight(G, 'sq_light1');
  assert.equal(lightCount(S), 1);
  assert.deepEqual(G.toasts, ['Light 1/3']);
  collectLight(G, 'sq_light2');
  assert.equal(S.quests.sq_lantern_walk, 2);
  collectLight(G, 'sq_light3');
  assert.equal(S.found.sq_light2, 1);
  assert.equal(S.found.sq_light3, 1);
  assert.equal(lightCount(S), 3);
  assert.equal(S.quests.sq_lantern_walk, 2);
  assert.deepEqual(G.toasts.slice(-2), ['Light 3/3', 'They can be taken to the ferry.']);
  assert.equal(S.inv.orblamp, 2);
  assert.equal(S.inv.glowfish, 1);
  assert.ok(G.saves >= 3);

  const pay = TALK.solvi(S);
  assert.match(pay.pages[0], /Three small lights/);
  assert.equal(pay.pages[2], 'Take this. The dead have little use for gold, and the living have a lot.');
  pay.then(G);
  assert.equal(S.gold, 120);
  assert.equal(S.flags.sq_pale_follow, 1);
  assert.equal(S.quests.sq_lantern_walk, 3);
  assert.equal(S.inv.orblamp, 2);
  assert.equal(S.inv.glowfish, 1);
  assert.ok(G.toasts.includes('+120 gold'));
  assert.deepEqual(TALK.solvi(S).pages, NOD);
});

test('shore spots show only at stage 2 for lights still lost', () => {
  shell.S = fresh({ inv: { orblamp: 2, glowfish: 1 } });
  hel.fx = [];
  hel.shore();
  const ids = hel.spots.map((s) => s.id);
  for (const id of ['sq_light1', 'sq_light2', 'sq_light3']) assert.ok(ids.includes(id));
  const a = hel.spots.find((s) => s.id === 'sq_light1');
  assert.equal(a.show(), false);
  shell.S.quests.sq_lantern_walk = 2;
  assert.equal(a.show(), true);
  assert.equal(hel.spots.find((s) => s.id === 'sq_light3').show(), true);
  a.act();
  assert.match(hel.looked.pages[0], /shy/);
  shell.toasts = [];
  hel.looked.then(shell);
  assert.equal(shell.S.found.sq_light1, 1);
  assert.equal(a.show(), false);
  assert.equal(hel.spots.find((s) => s.id === 'sq_light2').show(), true);
  assert.equal(shell.S.quests.sq_lantern_walk, 2);
  assert.deepEqual(shell.toasts, ['Light 1/3']);
  assert.equal(hel.fx[0] && hel.fx[0].name, 'wisps_blue');
});

test('save and load keeps one found light and a finished walk', () => {
  const mid = fresh({
    quests: { sq_lantern_walk: 2 },
    found: { sq_light1: 1 },
    inv: { orblamp: 2, glowfish: 1 },
  });
  const loaded = fresh(snap(mid));
  assert.equal(loaded.quests.sq_lantern_walk, 2);
  assert.equal(loaded.found.sq_light1, 1);
  assert.equal(loaded.found.sq_light2, undefined);
  assert.equal(loaded.inv.orblamp, 2);
  assert.equal(loaded.inv.glowfish, 1);
  assert.deepEqual(TALK.solvi(loaded).pages, REMIND);
  assert.equal(lightCount(loaded), 1);

  const done = fresh({
    quests: { sq_lantern_walk: 3 },
    found: { sq_light1: 1, sq_light2: 1, sq_light3: 1 },
    flags: { sq_pale_follow: 1 },
    inv: { orblamp: 2, glowfish: 1 },
    gold: 120,
  });
  const back = fresh(snap(done));
  assert.equal(back.quests.sq_lantern_walk, 3);
  assert.equal(back.flags.sq_pale_follow, 1);
  assert.equal(back.gold, 120);
  assert.equal(back.inv.orblamp, 2);
  assert.equal(back.inv.glowfish, 1);
  assert.deepEqual(solvi_ferry(back).pages, NOD);
  assert.equal(solvi_ferry(back).then, undefined);
});

test('TALK.ferryman stays Corvin; TALK.solvi starts The Pale Road', () => {
  assert.equal(TALK.ferryman, corvin);
  const S = fresh();
  const G = mock(S);
  const ferryman = TALK.ferryman(S);
  assert.equal(ferryman.pages[0], '"Living? Lovely. Mind your lamp, love."');
  assert.doesNotMatch(ferryman.pages.join(' '), /pale road|Sölvi|glow-fish/i);
  if (ferryman.then) ferryman.then(G);
  assert.equal(S.quests.sq_lantern_walk, undefined);
  assert.equal(S.quests.hh_raven, undefined);

  const start = TALK.solvi(S);
  assert.deepEqual(start.pages, START_PAGES);
  start.then(G);
  assert.equal(S.quests.sq_lantern_walk, 1);

  assert.equal(markerFor('solvi', fresh()), 'quest_mark');
  assert.equal(markerFor('solvi', fresh({ quests: { sq_lantern_walk: 1 } })), null);
  assert.equal(markerFor('solvi', fresh({ quests: { sq_lantern_walk: 1 }, inv: { orblamp: 1, glowfish: 1 } })), 'quest_turnin');
  assert.equal(markerFor('solvi', fresh({ quests: { sq_lantern_walk: 2 }, found: { sq_light1: 1 } })), null);
  assert.equal(markerFor('solvi', fresh({
    quests: { sq_lantern_walk: 2 },
    found: { sq_light1: 1, sq_light2: 1, sq_light3: 1 },
  })), 'quest_turnin');
  assert.equal(markerFor('solvi', fresh({ quests: { sq_lantern_walk: 3 }, flags: { sq_pale_follow: 1 } })), null);
  assert.equal(markerFor('ferryman', fresh()), null);
});
