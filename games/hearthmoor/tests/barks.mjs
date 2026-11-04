// node --test tests/barks.mjs : Bifrost ambient bark picker + quiet-gap timer
import test from 'node:test';
import assert from 'node:assert/strict';
import * as mod from '../game/barks.js';
import { BARKS, NEAR, SHOW, GAP_MIN, GAP_MAX, pickLine, rollGap, freshSim, tick } from '../game/barks.js';

const ANY = BARKS.bifrost.any;
const LIT = BARKS.bifrost.temple_lit;
const seq = (xs) => { let i = 0; return () => xs[i++]; };

test('bifrost pool only, every line at most 70 characters, no codex', () => {
  assert.deepEqual(Object.keys(BARKS), ['bifrost']);
  assert.deepEqual(Object.keys(BARKS.bifrost).sort(), ['any', 'temple_lit']);
  assert.equal(ANY.length, 10);
  assert.equal(LIT.length, 3);
  assert.equal(ANY[0], 'Nine gates, nine colours. My eyes have never been so busy.');
  assert.equal(LIT[2], "Rainbow light on the plaza stones again. Hearthmoor's next door now.");
  for (const line of [...ANY, ...LIT]) assert.ok(line.length > 0 && line.length <= 70, line);
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
