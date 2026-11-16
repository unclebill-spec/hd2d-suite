// node --test tests/barks.mjs : Bifrost ambient bark picker + quiet-gap timer
import test from 'node:test';
import assert from 'node:assert/strict';
import * as mod from '../game/barks.js';
import { BARKS, BARK_REALM, NEAR, SHOW, GAP_MIN, GAP_MAX, pickLine, statePools, rollGap, freshSim, tick } from '../game/barks.js';

const ANY = BARKS.bifrost.any;
const LIT = BARKS.bifrost.temple_lit;
const seq = (xs) => { let i = 0; return () => xs[i++]; };

const STATE_KEYS = {
  midgard: ['any', 'befriended', 'conquered', 'redeemed'],
  alfheim: ['any', 'befriended', 'conquered', 'redeemed'],
  svartalfheim: ['any', 'befriended', 'conquered', 'redeemed'],
  jotunheim: ['any', 'befriended', 'conquered', 'redeemed'],
  muspelheim: ['any', 'befriended', 'conquered', 'redeemed'],
  niflheim: ['any', 'befriended', 'conquered', 'redeemed'],
  asgard: ['any', 'befriended', 'conquered', 'redeemed'],
  vanaheim: ['any', 'befriended', 'conquered', 'redeemed'],
  helheim: ['any', 'befriended', 'conquered', 'redeemed'],
  bifrost: ['any', 'temple_lit'],
};

test('every realm pool, lines of 1 to 70 characters, bifrost lines unchanged, no codex', () => {
  assert.deepEqual(Object.keys(BARKS), Object.keys(STATE_KEYS));
  assert.equal(Object.keys(BARKS).length, 10);
  let n = 0;
  for (const [realm, keys] of Object.entries(STATE_KEYS)) {
    assert.deepEqual(Object.keys(BARKS[realm]), keys);
    for (const key of keys) {
      for (const line of BARKS[realm][key]) {
        assert.equal(typeof line, 'string');
        assert.ok(line.length >= 1 && line.length <= 70, `${realm}.${key} ${line.length}: ${line}`);
        n += 1;
      }
    }
  }
  assert.equal(n, 195);
  assert.deepEqual(ANY, [
    'Nine gates, nine colours. My eyes have never been so busy.',
    "Gatewright Halvard says 'coming soon' like it's a blessing.",
    "Vanaheim's gate is the only one open. Smells like moss and rain.",
    "Mind the frozen gate. Niflheim's seal bites back when you lean on it.",
    "Gatekeepers' Guild polishes the arches daily. Tidy lot.",
    'I came for the view, stayed because I lost my way. Again.',
    "Muspelheim's seal is warm. People toast bread on it. Don't.",
    "Asgard's gate hums like a hall fire. Rather smug, I find.",
    "Helheim's gate breathes on the glass. Polite, but chilly.",
    'Earn your merit, get your key. The Guild has a pamphlet.',
  ]);
  assert.deepEqual(LIT, [
    "Old Temple's relit! The Midgard gate is open and singing.",
    'No more Corsair skiffs to get home. My stomach thanks the Temple.',
    "Rainbow light on the plaza stones again. Hearthmoor's next door now.",
  ]);
  assert.equal('CODEX' in mod, false);
});

test('pick: any until the temple is lit; then the state pool, any one time in three', () => {
  for (let n = 0; n < 6; n++) assert.ok(ANY.includes(pickLine({}, seq([0.2, 0.4]))));
  assert.equal(pickLine({ temple_lit: true }, seq([0, 0])), ANY[0]);
  assert.equal(pickLine({ temple_lit: true }, seq([0.5, 0])), LIT[0]);
  assert.equal(pickLine({ temple_lit: true }, seq([1, 0.99])), LIT[2]);
  assert.notEqual(pickLine({}, seq([0]), ANY[0]), ANY[0]);
});

test('quiet gap is 8 to 14 seconds', () => {
  assert.equal(rollGap(() => 0), GAP_MIN);
  assert.equal(rollGap(() => 1), GAP_MAX);
  const mid = rollGap(() => 0.5);
  assert.ok(mid > GAP_MIN && mid < GAP_MAX);
});

test('timer: one bark for ~3 s, only inside 3.5, frozen while a menu or fight is up', () => {
  const rng = () => 0;
  const sim = freshSim(rng);
  assert.equal(sim.wait, GAP_MIN);
  const far = [{ id: 'gatewright', d: NEAR + 0.2 }];
  tick(sim, 7.9, { spots: far, flags: {}, rng });
  assert.equal(sim.line, null);
  tick(sim, 0.2, { spots: far, flags: {}, rng });
  assert.equal(sim.wait, 0);
  assert.equal(sim.line, null);
  const near = [{ id: 'gatewright', d: NEAR }, { id: 'skiff', d: 9 }];
  tick(sim, 0.01, { spots: near, flags: {}, rng });
  assert.equal(sim.line, ANY[0]);
  assert.equal(sim.spot, 'gatewright');
  assert.equal(sim.left, SHOW);
  const shown = sim.line, wait = sim.wait;
  tick(sim, 1, { spots: near, flags: {}, rng });
  assert.equal(sim.line, shown);
  assert.ok(Math.abs(sim.left - (SHOW - 1)) < 1e-9);
  tick(sim, 5, { blocked: true, spots: near, flags: {}, rng });
  assert.equal(sim.line, null);
  assert.equal(sim.wait, wait);
  tick(sim, 0.1, { spots: near, flags: {}, rng });
  assert.equal(sim.line, null);
  assert.ok(sim.wait < wait && sim.wait > 0);
});

test('walking out of range hides the bark; a pinned bark stays for the shot', () => {
  const rng = () => 0;
  const sim = freshSim(rng);
  sim.wait = 0;
  tick(sim, 0.01, { spots: [{ id: 'a', d: 1 }], flags: {}, rng });
  assert.ok(sim.line);
  tick(sim, 0.2, { spots: [{ id: 'a', d: NEAR + 0.1 }], flags: {}, rng });
  assert.equal(sim.line, null);
  const pin = freshSim(rng);
  pin.line = 'hi'; pin.spot = 'a'; pin.left = SHOW; pin.pin = true; pin.wait = 5;
  tick(pin, 1, { spots: [{ id: 'a', d: 9 }], flags: {}, rng });
  assert.equal(pin.line, 'hi');
  assert.ok(Math.abs(pin.left - (SHOW - 1)) < 1e-9);
});

test('BARK_REALM maps areas onto bark realms', () => {
  assert.equal(BARK_REALM.plaza, 'midgard');
  assert.equal(BARK_REALM.ravenhold, 'midgard');
  assert.equal(BARK_REALM.forge, 'midgard');
  assert.equal(BARK_REALM.rift, 'midgard');
  assert.equal(BARK_REALM.bifrost, 'bifrost');
  assert.equal(BARK_REALM.vh_garden, 'vanaheim');
  assert.equal(BARK_REALM.ossuary2, 'helheim');
  assert.equal(BARK_REALM.frozen_rift, 'niflheim');
  assert.equal(BARK_REALM.lumen_court, 'alfheim');
  assert.ok(BARK_REALM.unknown == null);
});

test('statePools: befriend, conquer, contract, Hel, redeemed', () => {
  assert.deepEqual(statePools('alfheim', { alliance: { alfheim: 'befriend' } }), ['befriended']);
  assert.deepEqual(statePools('jotunheim', { alliance: { jotunheim: 'conquer' } }), ['conquered']);
  assert.deepEqual(statePools('muspelheim', { alliance: { muspelheim: 'contract' } }), []);
  assert.deepEqual(statePools('jotunheim', { jt_contract: 1 }), []);
  assert.deepEqual(statePools('helheim', { hel: 'kind' }), ['befriended']);
  assert.deepEqual(statePools('helheim', { hel: 'defiant' }), ['conquered']);
  assert.deepEqual(statePools('niflheim', { veyra_redeemed: 1 }), ['redeemed']);
  assert.deepEqual(statePools('alfheim', { alliance: { alfheim: 'befriend' }, veyra_redeemed: 1 }), ['befriended', 'redeemed']);
  assert.deepEqual(statePools('midgard', { alliance: { midgard: 'befriend' } }), []);
  assert.deepEqual(statePools('midgard', { alliance: { midgard: 'befriend' }, veyra_redeemed: 1 }), ['redeemed']);
  assert.deepEqual(statePools('bifrost', { temple_lit: true }), ['temple_lit']);
  assert.deepEqual(statePools('bifrost', { temple_lit: true, veyra_redeemed: 1 }), ['temple_lit']);
  assert.deepEqual(statePools('bifrost', {}), []);
});

test('pickLine reads the realm state pools with the same rng order', () => {
  assert.equal(pickLine({ alliance: { alfheim: 'befriend' } }, seq([0.5, 0]), null, 'alfheim'), BARKS.alfheim.befriended[0]);
  assert.equal(pickLine({ alliance: { alfheim: 'befriend' } }, seq([0, 0]), null, 'alfheim'), BARKS.alfheim.any[0]);
  assert.equal(pickLine({ alliance: { alfheim: 'conquer' } }, seq([1, 0]), null, 'alfheim'), BARKS.alfheim.conquered[0]);
  assert.equal(pickLine({ alliance: { jotunheim: 'contract' } }, seq([0]), null, 'jotunheim'), BARKS.jotunheim.any[0]);
  assert.equal(pickLine({ hel: 'kind' }, seq([0.5, 0]), null, 'helheim'), BARKS.helheim.befriended[0]);
  assert.equal(pickLine({ hel: 'defiant' }, seq([0.5, 0]), null, 'helheim'), BARKS.helheim.conquered[0]);
  assert.equal(pickLine({ veyra_redeemed: 1 }, seq([0.5, 0]), null, 'niflheim'), BARKS.niflheim.redeemed[0]);
  const joined = [...BARKS.niflheim.befriended, ...BARKS.niflheim.redeemed];
  assert.equal(pickLine({ alliance: { niflheim: 'befriend' }, veyra_redeemed: 1 }, seq([1, 0.99]), null, 'niflheim'), joined[joined.length - 1]);
  assert.equal(joined[joined.length - 1], BARKS.niflheim.redeemed[BARKS.niflheim.redeemed.length - 1]);
});

test('speaker-name guard skips a line that names the spot', () => {
  const sim = freshSim(() => 0);
  sim.wait = 0;
  tick(sim, 0.01, { spots: [{ id: 'h', d: 1, label: 'Hilde' }], flags: {}, rng: seq([0, 0, 0]), realm: 'midgard' });
  assert.equal(sim.line, BARKS.midgard.any[1]);
  assert.equal(sim.spot, 'h');
  assert.ok(!sim.line.toLowerCase().includes('hilde'));

  const named = freshSim(() => 0);
  named.wait = 0;
  tick(named, 0.01, { spots: [{ id: 'o', d: 1, label: 'Odo' }], flags: {}, rng: seq([0, 0, 0]), realm: 'midgard' });
  assert.equal(named.line, BARKS.midgard.any[0]);

  const none = freshSim(() => 0);
  none.wait = 0;
  tick(none, 0.01, { spots: [{ id: 't', d: 1, label: 'the' }], flags: { temple_lit: true }, rng: seq([0, 0.5, 0, 0]), realm: 'bifrost' });
  assert.equal(none.line, null);
  assert.equal(none.spot, null);
  assert.ok(none.wait > 0);
});
