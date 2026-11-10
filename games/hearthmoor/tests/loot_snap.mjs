// node tests/loot_snap.mjs : blocked temple drops snap onto a walkable cell; court-stair rift gold stays put
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';
import { Collide } from '../engine/collide.js';
import { LOOT_SNAP_M, snapWalkable } from '../game/loot.js';

const here = dirname(fileURLToPath(import.meta.url));
const scene = JSON.parse(readFileSync(join(here, '../areas/temple/scene.json'), 'utf8'));
const collide = new Collide(scene.collision);

const BLOCKED = [
  { name: 'wraithL item offset', x: -1.5, z: -7.25 },
  { name: 'wraithR spawn', x: 1.4, z: -7.4 },
];
const RIFT_GOLD = { x: 0.4, z: -7.7 };

test('blocked temple points snap to a walkable cell with a real height', () => {
  for (const p of BLOCKED) {
    assert.equal(collide.blocked(p.x, p.z), true, p.name + ' starts blocked');
    assert.equal(collide.height(p.x, p.z), null, p.name + ' raw height is null (heightAt would force y=0)');
    const s = snapWalkable(collide, p.x, p.z);
    assert.equal(collide.blocked(s.x, s.z), false, p.name + ' snaps off the blocker');
    const h = collide.height(s.x, s.z);
    assert.notEqual(h, null, p.name + ' snapped height');
    assert.notEqual(h, 0, p.name + ' is not the blocked-path y=0');
    assert.ok(h > 1 && h < 2, p.name + ' court height ' + h);
    assert.ok(Math.hypot(s.x - p.x, s.z - p.z) <= LOOT_SNAP_M + 1e-9, p.name + ' within ' + LOOT_SNAP_M + ' m');
    assert.ok(Math.hypot(s.x - p.x, s.z - p.z) > 0, p.name + ' actually moved');
  }
});

test('already-walkable rift gold on the court stair is unchanged', () => {
  assert.equal(collide.blocked(RIFT_GOLD.x, RIFT_GOLD.z), false);
  const h = collide.height(RIFT_GOLD.x, RIFT_GOLD.z);
  assert.ok(h >= 1.46 && h <= 1.71, 'rift gold height ' + h);
  const s = snapWalkable(collide, RIFT_GOLD.x, RIFT_GOLD.z);
  assert.equal(s.x, RIFT_GOLD.x);
  assert.equal(s.z, RIFT_GOLD.z);
  assert.equal(collide.height(s.x, s.z), h);
});

// Pickup is xz only (game/loot.js Loot.update): hypot(hero.xz, drop.xz) < 0.75 and drop age > 0.4s.
// The hero does not have to canStand on the drop. Flood standable cells the way Collide.move does.
const PICKUP_M = 0.75;
const HERO_R = 0.28;
const REACH_SEEDS = [
  { name: 'court floor', x: 0, z: -9.6, h: 2 },
  { name: 'nave terrace', x: -2, z: -6, h: 1.2 },
];

function floodStandable(step, seed) {
  const i0 = Math.round(seed.x / step), j0 = Math.round(seed.z / step);
  const x0 = i0 * step, z0 = j0 * step;
  const h0 = collide.canStand(x0, z0, seed.h, HERO_R);
  if (h0 == null) return null;
  const seen = new Set([i0 + ':' + j0]);
  const cells = [{ x: x0, z: z0, h: h0 }];
  const q = [{ i: i0, j: j0, x: x0, z: z0, h: h0 }];
  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  let head = 0;
  while (head < q.length) {
    const cur = q[head++];
    for (const [di, dj] of dirs) {
      const i = cur.i + di, j = cur.j + dj, k = i + ':' + j;
      if (seen.has(k)) continue;
      const [nx, nz, nh, full] = collide.move(cur.x, cur.z, cur.h, di * step, dj * step, HERO_R);
      if (!full) continue;
      seen.add(k);
      const node = { x: nx, z: nz, h: nh };
      cells.push(node);
      q.push({ i, j, x: nx, z: nz, h: nh });
    }
  }
  return cells;
}

test('snapped temple drops are within hero pickup reach', () => {
  const step = 0.1;
  for (const seed of REACH_SEEDS) {
    assert.equal(collide.canStand(seed.x, seed.z, seed.h, HERO_R), seed.h, seed.name + ' stands');
    const cells = floodStandable(step, seed);
    assert.ok(cells && cells.length > 1000, seed.name + ' flood reached ' + (cells ? cells.length : 0));
    for (const p of BLOCKED) {
      const s = snapWalkable(collide, p.x, p.z);
      let best = Infinity;
      for (const n of cells) {
        const d = Math.hypot(n.x - s.x, n.z - s.z);
        if (d < best) best = d;
      }
      assert.ok(best < PICKUP_M, p.name + ' from ' + seed.name + ': nearest standable hero is ' + best.toFixed(3) + ' m from the snap, need < ' + PICKUP_M);
    }
  }
});
