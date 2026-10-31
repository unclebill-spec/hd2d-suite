// [VANAHEIM C] the world (day clock + enemies) holds still while a Bloomtide minigame is open and resumes after.
import test from 'node:test'; import assert from 'node:assert/strict';
// engine/clock.js needs three; this mirrors its tick() line exactly: if (!this.paused) this.t = (this.t + dt * this.speed) % 1
class Clock { constructor(_b, start = 0.62, speed = 1 / 480) { this.t = start; this.speed = speed; this.paused = false; } tick(dt) { if (!this.paused) this.t = (this.t + dt * this.speed) % 1; } }
import { Combat } from '../game/combat.js';
globalThis.window ??= globalThis; globalThis.document ??= { getElementById: () => null };
const { freezeWorld } = await import('../game/minigames/bloomtide.js');
const enemiesPaused = (G) => Combat.prototype.paused.call({ G });
for (const how of ['win', 'quit']) test(`clock + enemies freeze while open, resume after a ${how}`, () => {
  const clock = new Clock(null, 0.5, 1 / 480), G = { busy: false, ctx: { clock } };
  clock.tick(1); const t1 = clock.t; assert.ok(t1 > 0.5); assert.equal(enemiesPaused(G), false);
  const thaw = freezeWorld(G);
  for (let i = 0; i < 60; i++) clock.tick(1 / 60);
  assert.equal(clock.t, t1, 'clock held'); assert.equal(enemiesPaused(G), true, 'enemies held');
  thaw();
  assert.equal(G.busy, false); assert.equal(clock.paused, false); assert.equal(enemiesPaused(G), false);
  clock.tick(1); assert.ok(clock.t > t1, 'clock resumes');
});
test('a clock already paused (e.g. &freeze) stays paused after', () => {
  const clock = new Clock(null, 0.5); clock.paused = true; const G = { busy: false, ctx: { clock } };
  freezeWorld(G)(); assert.equal(clock.paused, true);
});
