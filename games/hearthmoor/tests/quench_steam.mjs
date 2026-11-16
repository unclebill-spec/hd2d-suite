// node --test tests/quench_steam.mjs : ambient tank steam retriggers (frames keep advancing past 0.8s);
// a +7/+10 burst plays once and hides — it never holds the last frame.
import test from 'node:test';
import assert from 'node:assert/strict';
import { Forge, QUENCH_STEAM } from '../game/forge.js';

function mockFx() {
  const list = [];
  return {
    meta: { effects: { quench_steam: { frames: QUENCH_STEAM.frames, fps: QUENCH_STEAM.fps, duration: QUENCH_STEAM.duration, loop: false } } },
    list,
    spawn(name, x, y, z, opts = {}) {
      const e = this.meta.effects[name];
      if (!e) return null;
      const f = { name, e, x, y, z, t: 0, frame: 0, fade: 0, dur: opts.duration ?? e.duration, onDone: opts.onDone || null, hidden: false };
      list.push(f);
      return f;
    },
    update(dt) {
      const keep = [], done = [];
      for (const f of list) {
        f.t += dt;
        f.frame = Math.min(f.e.frames - 1, Math.floor(f.t * f.e.fps));
        if (f.t >= f.dur) { f.hidden = true; done.push(f); }
        else keep.push(f);
      }
      list.length = 0;
      list.push(...keep);
      for (const f of done) if (f.onDone) f.onDone(f);
    },
  };
}

function attachForge(opts = {}) {
  const fx = mockFx();
  const G = { S: { flags: {}, quests: { forge_riot: 3, altar: 3 } }, qaStill: !!opts.qaStill };
  const F = new Forge(G);
  const ctx = {
    scene: { game: { forgefx: [
      { name: 'quench_steam', pos: [-1.8, 0.65, -8.0] },
      { name: 'quench_steam', pos: [7.4, 0.65, -7.8] },
      { name: 'quench_steam', pos: [6.4, 0.65, -1.6] },
    ] } },
    heightAt: () => 0,
    gamefx: fx,
  };
  F.attach(ctx, 'forge');
  return { F, fx, ctx, G };
}

test('ambient tank steam keeps advancing frames over more than 0.8s in an unfrozen session', () => {
  const { fx } = attachForge();
  assert.equal(fx.list.length, 3);
  assert.ok(fx.list.every((f) => f.dur === QUENCH_STEAM.duration && f.dur !== Infinity));

  fx.update(0.5);
  const mid = fx.list.map((f) => f.frame);
  assert.ok(mid.every((fr) => fr === 5), `at 0.5s expected frame 5, got ${mid}`);
  assert.ok(fx.list.every((f) => !f.hidden));

  fx.update(0.4);   // clock 0.9: first puff hid at 0.8 and retriggered (new puff starts at t=0 this step)
  assert.equal(fx.list.length, 3, 'all three tanks retrigger after hide');
  const after = fx.list.map((f) => f.frame);
  assert.ok(after.every((fr) => fr === 0), `new puff starts at frame 0, got ${after}`);
  assert.ok(after.every((fr) => fr !== QUENCH_STEAM.frames - 1), 'must not sit on the last frame');

  fx.update(0.3);   // new puff t=0.3, clock 1.2: mid-cycle, well past 0.8s
  const late = fx.list.map((f) => f.frame);
  assert.equal(fx.list.length, 3);
  assert.ok(late.every((fr) => fr === 3), `at 1.2s expected frame 3 of the second puff, got ${late}`);

  const seen = new Set();
  const { fx: fx2 } = attachForge();
  let t = 0;
  while (t < 2.0) { fx2.update(0.1); t += 0.1; for (const f of fx2.list) seen.add(f.frame); }
  assert.ok(seen.has(0) && seen.has(5) && seen.has(7) && seen.size >= 8, `ambient should visit every frame over 2s, saw ${[...seen]}`);
});

test('a +7/+10 temper burst plays once, then hides; it never holds its last frame', () => {
  const { F, fx } = attachForge();
  fx.update(0.2);
  const ambientIds = new Set(fx.list);
  F.burst('quench_steam', -1.8, -8.0);
  const burst = fx.list.find((f) => !ambientIds.has(f));
  assert.ok(burst, 'burst should spawn a one-shot puff');
  assert.equal(burst.dur, QUENCH_STEAM.duration);
  assert.equal(burst.onDone, null);

  fx.update(0.7);   // burst t=0.7: last frame is on screen only as the final anim frame
  assert.equal(burst.frame, 7);
  assert.equal(burst.hidden, false);
  assert.ok(fx.list.includes(burst));

  fx.update(0.15);  // burst t=0.85: hidden and gone from the list
  assert.equal(burst.hidden, true);
  assert.ok(!fx.list.includes(burst), 'burst must be removed after 0.8s, not held');
  // ambients still present (retriggered or mid-puff), none of them is the burst
  assert.ok(fx.list.every((f) => f !== burst));
  assert.equal(fx.list.length, 3);
});
