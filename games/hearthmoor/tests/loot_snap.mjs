// node tests/loot_snap.mjs : blocked temple drops snap onto a walkable cell; court-stair rift gold stays put
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';
import { Collide } from '../engine/collide.js';
import { LOOT_SNAP_M, LOOT_SNAP_MAX_M, Loot, snapWalkable } from '../game/loot.js';
import * as LootApi from '../game/loot.js';

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

// Synthetic heightfields. Values are int16 centimetres; -32768 is Collide's blocked sentinel.
const CM = 120; // 1.2 m, distinct from the y=0 sink
const SENTINEL = -32768;

function gridSpec(w, h, cell, fill, ox = 0, oz = 0) {
  const d = new Int16Array(w * h);
  for (let j = 0; j < h; j++) {
    for (let i = 0; i < w; i++) d[j * w + i] = fill(i, j) ? CM : SENTINEL;
  }
  return { origin: [ox, oz], cell, w, h, max_step: 0.36, data: Buffer.from(d.buffer).toString('base64') };
}

function cellHitsDisk(i, j, x, z, cell, rad, ox = 0, oz = 0) {
  const x0 = ox + i * cell, z0 = oz + j * cell;
  const cx = Math.min(Math.max(x, x0), x0 + cell);
  const cz = Math.min(Math.max(z, z0), z0 + cell);
  return Math.hypot(cx - x, cz - z) <= rad + 1e-9;
}

// Same nearest-open scan the old snap used, so a test can show which bait that scan picks.
function nearestOpenSample(col, x, z, radius) {
  const step = col.cell, n = Math.ceil(radius / step);
  let best = null, bestD = radius + 1e-9;
  for (let j = -n; j <= n; j++) {
    for (let i = -n; i <= n; i++) {
      if (i === 0 && j === 0) continue;
      const d = Math.hypot(i * step, j * step);
      if (d > radius || d >= bestD) continue;
      const cx = x + i * step, cz = z + j * step;
      if (col.blocked(cx, cz)) continue;
      best = { x: cx, z: cz };
      bestD = d;
    }
  }
  return best;
}

// Standable cells a hero can actually walk to. Grid is collide.cell; stand test is canStand, r 0.28.
function reachableFrom(col, hero, cap = 8000) {
  const step = col.cell, r = HERO_R;
  const h0 = col.canStand(hero.x, hero.z, hero.y, r);
  if (h0 == null) return [];
  const ox = col.ox, oz = col.oz;
  const i0 = Math.floor((hero.x - ox) / step), j0 = Math.floor((hero.z - oz) / step);
  const seen = new Set([i0 + ':' + j0]);
  const cells = [{ x: hero.x, z: hero.z, h: h0 }];
  const q = [{ x: hero.x, z: hero.z, h: h0, i: i0, j: j0 }];
  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  let head = 0;
  while (head < q.length && cells.length < cap) {
    const cur = q[head++];
    for (const [di, dj] of dirs) {
      const i = cur.i + di, j = cur.j + dj;
      if (i < 0 || j < 0 || i >= col.w || j >= col.h) continue;
      const k = i + ':' + j;
      if (seen.has(k)) continue;
      seen.add(k);
      const nx = ox + (i + 0.5) * step, nz = oz + (j + 0.5) * step;
      const nh = col.canStand(nx, nz, cur.h, r);
      if (nh == null) continue;
      const node = { x: nx, z: nz, h: nh, i, j };
      cells.push(node);
      q.push(node);
    }
  }
  return cells;
}

function nearestReach(cells, x, z) {
  let best = Infinity;
  for (const n of cells) {
    const d = Math.hypot(n.x - x, n.z - z);
    if (d < best) best = d;
  }
  return best;
}

function countProbes(col, fn) {
  let probes = 0;
  const blocked = col.blocked.bind(col), canStand = col.canStand.bind(col);
  col.blocked = (x, z) => { probes++; return blocked(x, z); };
  col.canStand = (x, z, h, r) => { probes++; return canStand(x, z, h, r); };
  try {
    const result = fn();
    return { probes, result };
  } finally { col.blocked = blocked; col.canStand = canStand; }
}

test('blocked origin with no open cell within 1.25 m snaps beside reachable ground farther out', () => {
  const cell = 0.5, drop = { x: 5, z: 5 }, hero = { x: 8.5, y: CM / 100, z: 5 };
  const col = new Collide(gridSpec(24, 24, cell, (i, j) => !cellHitsDisk(i, j, drop.x, drop.z, cell, LOOT_SNAP_M)));
  assert.equal(col.blocked(drop.x, drop.z), true, 'origin is blocked');
  assert.equal(col.height(drop.x, drop.z), null);
  assert.equal(nearestOpenSample(col, drop.x, drop.z, LOOT_SNAP_M), null, 'nothing open inside 1.25 m');
  assert.equal(col.canStand(hero.x, hero.z, hero.y, HERO_R), hero.y, 'hero stands on open ground');
  const open = nearestOpenSample(col, drop.x, drop.z, 4);
  assert.ok(open && Math.hypot(open.x - drop.x, open.z - drop.z) > LOOT_SNAP_M, 'open ground exists inside the extended radius');
  const cells = reachableFrom(col, hero);
  assert.ok(cells.length > 8, 'hero region flood');
  const s = snapWalkable(col, drop.x, drop.z, LOOT_SNAP_M, { hero });
  assert.equal(col.blocked(s.x, s.z), false, 'snap is not blocked');
  const h = col.height(s.x, s.z);
  assert.equal(h, CM / 100, 'real height, not the y=0 sink');
  const reach = nearestReach(cells, s.x, s.z);
  assert.ok(reach < PICKUP_M, 'within pickup of a hero-reachable cell, got ' + reach);
  const moved = Math.hypot(s.x - drop.x, s.z - drop.z);
  assert.ok(moved > LOOT_SNAP_M && moved < Math.hypot(hero.x - drop.x, hero.z - drop.z), 'uses the nearer reachable ground, not the hero feet or the blocked origin');
});

test('open cell within 1.25 m across a wall is not chosen', () => {
  // Room A is x < 3, a solid wall fills x in [3, 6), room B is x >= 6. No gap to walk around.
  const cell = 0.5, drop = { x: 5.5, z: 4 }, hero = { x: 1, y: CM / 100, z: 4 };
  const col = new Collide(gridSpec(24, 16, cell, (i) => {
    const x0 = i * cell;
    return x0 < 3 || x0 >= 6;
  }));
  assert.equal(col.blocked(drop.x, drop.z), true, 'origin sits in the wall');
  const bait = nearestOpenSample(col, drop.x, drop.z, LOOT_SNAP_M);
  assert.ok(bait, 'old scan finds an open cell inside 1.25 m');
  assert.ok(bait.x >= 6, 'that cell is the far room');
  assert.equal(col.canStand(hero.x, hero.z, hero.y, HERO_R), hero.y);
  const cells = reachableFrom(col, hero);
  assert.ok(nearestReach(cells, bait.x, bait.z) >= PICKUP_M, 'bait is not hero-reachable');
  const s = snapWalkable(col, drop.x, drop.z, LOOT_SNAP_M, { hero });
  assert.equal(col.blocked(s.x, s.z), false);
  assert.equal(col.height(s.x, s.z), CM / 100);
  assert.ok(s.x < 3, 'snap stays in the hero room, got x=' + s.x);
  assert.ok(nearestReach(cells, s.x, s.z) < PICKUP_M, 'snap is inside pickup reach of the hero region');
  assert.ok(Math.hypot(s.x - bait.x, s.z - bait.z) > 1, 'did not take the walled-off cell');
});

test('no safe ground inside 4 m falls back to the hero, not the blocked origin', () => {
  const cell = 0.5, drop = { x: 8, z: 8 }, hero = { x: 8, y: CM / 100, z: 14.5 };
  const col = new Collide(gridSpec(40, 40, cell, (i, j) => !cellHitsDisk(i, j, drop.x, drop.z, cell, 4)));
  assert.equal(nearestOpenSample(col, drop.x, drop.z, 4), null, 'no open sample inside 4 m');
  assert.equal(col.canStand(hero.x, hero.z, hero.y, HERO_R), hero.y);
  const s = snapWalkable(col, drop.x, drop.z, LOOT_SNAP_M, { hero });
  assert.equal(s.x, hero.x);
  assert.equal(s.z, hero.z);
  assert.equal(col.blocked(s.x, s.z), false);
  assert.equal(col.height(s.x, s.z), CM / 100);
});

test('fully blocked grid with no hero stays inside the iteration cap and defers the drop', () => {
  const cell = 0.5, w = 90, h = 90; // 8100 cells: a full-grid walk blows past a 4000 cap
  const col = new Collide(gridSpec(w, h, cell, () => false));
  const x = 10, z = 10;
  assert.equal(col.blocked(x, z), true);
  assert.ok(w * h > 4000);
  const stats = {};
  const { probes, result: s } = countProbes(col, () => snapWalkable(col, x, z, LOOT_SNAP_M, { stats }));
  assert.equal(s.deferred, true, 'no open cell and no hero defers instead of returning the blocked origin');
  assert.ok(s.x === undefined || !col.blocked(s.x, s.z), 'blocked origin is not a placement');
  assert.equal(typeof LootApi.LOOT_SNAP_CAP, 'number');
  assert.ok(LootApi.LOOT_SNAP_CAP <= 4000 && LootApi.LOOT_SNAP_CAP >= 1);
  assert.ok(probes <= LootApi.LOOT_SNAP_CAP, 'probes ' + probes + ' exceeded cap ' + LootApi.LOOT_SNAP_CAP);
  assert.ok(stats.nodes <= LootApi.LOOT_SNAP_CAP, 'reported steps ' + stats.nodes);
  assert.ok(probes > 0 && probes <= stats.nodes, 'the reported cap counts the probes that actually ran (' + probes + ' probes, ' + stats.nodes + ' reported)');

  stubDocument();
  const G = fakeGame();
  const loot = new Loot(G);
  const ctx = fakeCtx(col, null);
  loot.attach(ctx);
  const item = { name: 'Kept Helm', slot: 'helm', rar: 3, mods: { hpAdd: 2 }, gems: [], up: 0, procs: [], rv: 3, at: 'plate' };
  const placed = loot.drop(x, z, { item, gold: 7 });
  assert.equal(placed, null, 'deferred drop is not spawned');
  assert.equal(loot.drops.length, 0, 'nothing is placed at the blocked y=0 sink');
  assert.equal(loot.pending.length, 1);
  assert.equal(loot.pending[0].item, item);
  assert.equal(loot.pending[0].gold, 7);

  // Area change must not delete the unpaid drop. Re-drop once the new hero has ground.
  const open = new Collide(gridSpec(8, 8, cell, () => true));
  const hero = { x: 2, y: CM / 100, z: 2 };
  loot.detach();
  assert.equal(loot.pending.length, 1, 'detach keeps the payload');
  loot.attach(fakeCtx(open, hero));
  assert.equal(loot.pending.length, 0, 'attach re-drops instead of deleting');
  assert.equal(loot.drops.length, 1);
  assert.equal(loot.drops[0].it, item);
  assert.equal(loot.drops[0].it.rar, 3);
  assert.equal(loot.drops[0].gold, 7);
  assert.equal(loot.drops[0].x, hero.x);
  assert.equal(loot.drops[0].z, hero.z);
  assert.equal(open.blocked(loot.drops[0].x, loot.drops[0].z), false);
  assert.equal(loot.drops[0].y, CM / 100);
  loot.update(0.05);
  assert.equal(loot.drops.length, 1, 'a second pass does not duplicate the re-drop');
  assert.equal(G.S.gold, 0, 'not picked up yet');
});

test('already-open origins are byte-unchanged and do no reachability search', () => {
  const col = new Collide(gridSpec(8, 8, 0.5, () => true));
  const x = 1.1 + 0.2, z = 2.5; // 1.1+0.2 is not 1.3; the bits have to survive
  assert.equal(col.blocked(x, z), false);
  const hero = { x: 3, y: CM / 100, z: 3 };
  let standN = 0;
  const canStand = col.canStand.bind(col);
  col.canStand = (...a) => { standN++; return canStand(...a); };
  const s = snapWalkable(col, x, z, LOOT_SNAP_M, { hero });
  assert.equal(standN, 0, 'open origin skips the BFS');
  assert.equal(s.x, x);
  assert.equal(s.z, z);
  assert.equal(Object.is(s.x, x), true);
  assert.equal(Object.is(s.z, z), true);
});

function stubDocument() {
  const make = (tag) => ({
    tagName: tag,
    className: '',
    style: {},
    width: 0,
    height: 0,
    children: [],
    appendChild(child) { this.children.push(child); return child; },
    remove() { this.removed = true; },
    getContext() {
      return { imageSmoothingEnabled: false, fillStyle: '', clearRect() {}, fillRect() {} };
    },
  });
  globalThis.document = { getElementById: () => make('div'), createElement: make };
}

function fakeGame() {
  return { S: { gear: {}, gold: 0, gems: {}, bag: [], mode: 'casual' }, title: null, downed: false, toast() {}, popText() {}, drawBag() {} };
}

function fakeCtx(col, player) {
  return {
    collide: col,
    player,
    heightAt: (x, z) => (col.height(x, z) ?? 0),
    project: () => ({ x: 0, y: 0 }),
  };
}

test('drop keeps gold, item identity, gem and purse through a snap and through deferral', () => {
  stubDocument();
  const cell = 0.5, drop = { x: 5, z: 5 }, hero = { x: 8.5, y: CM / 100, z: 5 };
  const col = new Collide(gridSpec(24, 24, cell, (i, j) => !cellHitsDisk(i, j, drop.x, drop.z, cell, LOOT_SNAP_M)));
  const G = fakeGame();
  const loot = new Loot(G);
  loot.attach(fakeCtx(col, hero));
  const item = { name: 'Kept Helm', slot: 'helm', rar: 2, mods: { hpAdd: 4 }, gems: [], up: 0, procs: [], rv: 3, at: 'cloth' };
  const payloads = [
    { what: { gold: 9 }, check: (d) => { assert.equal(d.gold, 9); assert.equal(d.gem, null); assert.equal(d.purse, false); assert.equal(d.it, null); } },
    { what: { item }, check: (d) => { assert.equal(d.it, item); assert.equal(d.it.rar, 2); assert.equal(d.gold, 0); } },
    { what: { gem: 'rift_shard' }, check: (d) => { assert.equal(d.gem, 'rift_shard'); assert.equal(d.it, null); } },
    { what: { gold: 12, purse: true }, check: (d) => { assert.equal(d.purse, true); assert.equal(d.gold, 12); assert.equal(d.gem, null); } },
  ];
  for (const p of payloads) {
    const d = loot.drop(drop.x, drop.z, p.what);
    assert.ok(d, 'snap path places the drop');
    assert.equal(col.blocked(d.x, d.z), false);
    assert.equal(d.y, CM / 100);
    assert.ok(nearestReach(reachableFrom(col, hero), d.x, d.z) < PICKUP_M);
    p.check(d);
  }
  assert.equal(loot.drops.length, 4);
  assert.equal(loot.pending.length, 0);

  // No hero: same payloads wait, then land once at the hero. Nothing is rerolled or dropped on the way.
  loot.detach();
  const blocked = new Collide(gridSpec(16, 16, cell, () => false));
  const waiting = new Loot(G);
  waiting.attach(fakeCtx(blocked, null));
  const item2 = { name: 'Waiting Helm', slot: 'chest', rar: 4, mods: { hpAdd: 1 }, gems: [], up: 0, procs: [], rv: 3, at: 'plate' };
  const again = [
    { gold: 3 },
    { item: item2 },
    { gem: 'golem_core' },
    { gold: 5, purse: true },
  ];
  for (const what of again) assert.equal(waiting.drop(1, 1, what), null);
  assert.equal(waiting.drops.length, 0, 'not sunk at y=0');
  assert.equal(waiting.pending.length, 4);
  assert.equal(waiting.pending[1].item, item2);
  const live = { x: 3, y: CM / 100, z: 3 };
  waiting.ctx.player = live;
  waiting.ctx.collide = col;
  waiting.ctx.heightAt = (x, z) => (col.height(x, z) ?? 0);
  waiting.update(0.05);
  assert.equal(waiting.pending.length, 0);
  assert.equal(waiting.drops.length, 4);
  assert.equal(waiting.drops[0].gold, 3);
  assert.equal(waiting.drops[0].purse, false);
  assert.equal(waiting.drops[1].it, item2);
  assert.equal(waiting.drops[1].it.rar, 4);
  assert.equal(waiting.drops[2].gem, 'golem_core');
  assert.equal(waiting.drops[3].purse, true);
  assert.equal(waiting.drops[3].gold, 5);
  for (const d of waiting.drops) {
    assert.equal(d.x, live.x);
    assert.equal(d.z, live.z);
    assert.equal(d.y, CM / 100);
    assert.equal(col.blocked(d.x, d.z), false);
  }
  waiting.update(0.05);
  assert.equal(waiting.drops.length, 4, 'second update does not duplicate');
  assert.equal(G.S.gold, 0);
});

// Temple reachable region is 4628 cells at 0.25 m, over LOOT_SNAP_CAP. A shared walk+scan budget
// lets the walk return early and leaves scanOpen with nothing, so Loot.drop falls back to the hero.
const TEMPLE_HEROES = [
  { name: 'court', x: 0, y: 2.0, z: -9.6 },
  { name: 'nave', x: -2, y: 1.2, z: -6 },
];

test('temple stair drops with a hero stay beside the blocked origin, not at the hero', () => {
  stubDocument();
  const item = { name: 'Stair Helm', slot: 'helm', rar: 2, mods: { hpAdd: 1 }, gems: [], up: 0, procs: [], rv: 3, at: 'plate' };
  for (const hero of TEMPLE_HEROES) {
    assert.equal(collide.canStand(hero.x, hero.z, hero.y, HERO_R), hero.y, hero.name + ' stands');
    const cells = reachableFrom(collide, hero, 20000);
    assert.ok(cells.length > 4000, hero.name + ' reachable region ' + cells.length + ' exceeds the shared snap cap');
    for (const origin of BLOCKED) {
      for (const what of [{ gold: 6 }, { item }]) {
        const kind = what.item ? 'item' : 'gold';
        const label = hero.name + ' ' + origin.name + ' ' + kind;
        const loot = new Loot(fakeGame());
        loot.attach(fakeCtx(collide, hero));
        const d = loot.drop(origin.x, origin.z, what);
        assert.ok(d, label + ' placed');
        assert.equal(collide.blocked(d.x, d.z), false, label + ' blocked');
        assert.notEqual(collide.height(d.x, d.z), null, label + ' height');
        const od = Math.hypot(d.x - origin.x, d.z - origin.z);
        assert.ok(od <= LOOT_SNAP_MAX_M + 1e-9, label + ' is ' + od.toFixed(3) + ' m from the origin');
        assert.ok(nearestReach(cells, d.x, d.z) < PICKUP_M, label + ' not within pickup of a hero-reachable cell');
        const hd = Math.hypot(d.x - hero.x, d.z - hero.z);
        assert.ok(hd >= PICKUP_M, label + ' is ' + hd.toFixed(3) + ' m from the hero; the walk spent the shared LOOT_SNAP_CAP so scanOpen returned null and drop() fell back to the hero feet');
        if (what.item) assert.equal(d.it, item, label + ' item identity');
        else assert.equal(d.gold, 6, label + ' gold');
      }
    }
  }
});

test('huge open grid snaps a blocked origin beside itself when the reachable region exceeds the cap', () => {
  const cell = 0.25, w = 160, h = 160; // 25600 cells, well past a 4000 walk cap
  const origin = { x: 20.125, z: 20.125 };
  const hero = { x: 22.125, y: CM / 100, z: 20.125 };
  const oi = Math.floor(origin.x / cell), oj = Math.floor(origin.z / cell);
  const col = new Collide(gridSpec(w, h, cell, (i, j) => !(i === oi && j === oj)));
  assert.equal(col.blocked(origin.x, origin.z), true, 'origin cell is blocked');
  assert.equal(col.height(origin.x, origin.z), null);
  assert.equal(col.canStand(hero.x, hero.z, hero.y, HERO_R), hero.y, 'hero stands on the open grid');
  const cells = reachableFrom(col, hero, 4500);
  assert.ok(cells.length > 4000, 'reachable region ' + cells.length + ' exceeds the shared snap cap');
  stubDocument();
  const loot = new Loot(fakeGame());
  loot.attach(fakeCtx(col, hero));
  const d = loot.drop(origin.x, origin.z, { gold: 3 });
  assert.ok(d, 'placed');
  assert.equal(col.blocked(d.x, d.z), false);
  assert.notEqual(col.height(d.x, d.z), null, 'height');
  const od = Math.hypot(d.x - origin.x, d.z - origin.z);
  assert.ok(od > 0 && od <= LOOT_SNAP_MAX_M + 1e-9, 'beside the origin, got ' + od.toFixed(3) + ' m');
  assert.ok(nearestReach(cells, d.x, d.z) < PICKUP_M, 'not within pickup of the hero region');
  const hd = Math.hypot(d.x - hero.x, d.z - hero.z);
  assert.ok(hd >= PICKUP_M, 'is ' + hd.toFixed(3) + ' m from the hero; the walk spent the shared LOOT_SNAP_CAP so scanOpen returned null and drop() fell back to the hero feet');
  assert.equal(d.gold, 3);
});
