// node --test games/hearthmoor/tests/test_bloom_rules.mjs : timing windows + scoring for the Bloomtide minigames
import test from 'node:test';
import assert from 'node:assert/strict';
import { WINDOW, POINTS, GAMES, chart, judge, tapAt, expire, score } from '../game/minigames/bloom_rules.js';

test('windows: edges are inclusive, symmetric', () => {
  assert.equal(judge(0), 'perfect'); assert.equal(judge(WINDOW.perfect), 'perfect'); assert.equal(judge(-WINDOW.perfect), 'perfect');
  assert.equal(judge(WINDOW.perfect + 1), 'good'); assert.equal(judge(-WINDOW.good), 'good');
  assert.equal(judge(WINDOW.good + 1), 'miss'); assert.equal(judge(-WINDOW.good - 1), 'miss');
});
test('charts: counts, order, dance on the beat after the count-in', () => {
  for (const k of ['harvest', 'dance']) { const c = chart(k); assert.equal(c.length, GAMES[k].cues); for (let i = 1; i < c.length; i++) assert.ok(c[i] - c[i - 1] > 2 * WINDOW.good); }
  const d = chart('dance'); assert.equal(d[0], 2500); assert.equal(d[1] - d[0], 625);
  assert.equal(chart('harvest')[0], 1600); assert.throws(() => chart('nope'));
});
test('tapAt: nearest open cue, stray taps ignored, a cue is judged once', () => {
  const t = [1000, 2000], j = [];
  assert.equal(tapAt(t, j, 1500), null);
  const a = tapAt(t, j, 1040); assert.deepEqual([a.i, a.grade], [0, 'perfect']); j[a.i] = a.grade;
  assert.equal(tapAt(t, j, 1040), null);
  assert.equal(tapAt(t, j, 1880).grade, 'good');
});
test('expire: misses only after the good window', () => {
  const t = [1000], j = [];
  assert.deepEqual(expire(t, j, 1000 + WINDOW.good), []); assert.deepEqual(expire(t, j, 1000 + WINDOW.good + 1), [0]); assert.equal(j[0], 'miss');
});
test('score + win thresholds', () => {
  const h = (p, g, m) => [...Array(p).fill('perfect'), ...Array(g).fill('good'), ...Array(m).fill('miss')];
  assert.deepEqual(score('harvest', h(8, 0, 0)), { score: 800, hits: 8, perfect: 8, need: 5, of: 8, won: true, max: 800 });
  assert.equal(score('harvest', h(0, 5, 3)).won, true); assert.equal(score('harvest', h(0, 5, 3)).score, 250);
  assert.equal(score('harvest', h(4, 0, 4)).won, false);
  assert.equal(score('dance', h(2, 6, 4)).won, true); assert.equal(score('dance', h(7, 0, 5)).won, false);
  assert.equal(score('dance', h(12, 0, 0)).score, 12 * POINTS.perfect);
});
