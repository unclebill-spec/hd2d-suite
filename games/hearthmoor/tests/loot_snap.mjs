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
