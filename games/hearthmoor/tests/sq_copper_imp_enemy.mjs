// The Humming Golem: sparkImp spawns role `emberimp` through Combat.spawnEnemy, which reads ENEMIES[role].
// Regression for the b270676 official FAIL (emberimp was in SUMMONS only, so spawnEnemy threw on D.name).
import test from 'node:test';
import assert from 'node:assert/strict';
import { registerHooks } from 'node:module';

registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier === 'three' || specifier.startsWith('three/')) {
      return { url: 'data:text/javascript,' + encodeURIComponent('export default {};\n'), shortCircuit: true, format: 'module' };
    }
    return nextResolve(specifier, context);
  },
});
globalThis.window ??= globalThis;
globalThis.document ??= { getElementById: () => null, head: { appendChild() {} }, body: { appendChild() {}, classList: { add() {}, remove() {} } }, createElement: () => ({ style: {}, appendChild() {}, classList: { add() {} }, getContext: () => ({}) }) };
globalThis.localStorage ??= { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.location ??= { search: '' };

const { ENEMIES, SUMMONS } = await import('../game/heroes.js');
const { Combat } = await import('../game/combat.js');

test('emberimp has an ENEMIES row with the fields spawnEnemy and the AI read', () => {
  assert.ok(SUMMONS.emberimp, 'summon row still present');
  const D = ENEMIES.emberimp;
  assert.ok(D, 'ENEMIES.emberimp exists');
  assert.equal(D.name, 'Ember imp');
  for (const k of ['hp', 'dmg', 'speed', 'reach', 'windup', 'cd', 'aggro', 'r', 'push']) assert.equal(typeof D[k], 'number', k);
  assert.ok(!D.ranged || D.keep > 0, 'ranged foes need keep');
});

test('Combat.spawnEnemy spawns the Copper Row imp without throwing', () => {
  const npcs = [], fx = [];
  const ctx = {
    addNpc: (o) => { const a = { ...o, x: o.pos[0], y: 0, z: o.pos[1] }; npcs.push(a); return a; },
    effects: { spawn: (id) => fx.push(id) },
  };
  const self = { ctx, enemies: [] };
  const e = Combat.prototype.spawnEnemy.call(self, { id: 'sq_copper_imp', role: 'emberimp', pos: [-5.0, 2.0], once: true }, true);
  assert.equal(self.enemies.length, 1);
  assert.equal(e.D, ENEMIES.emberimp);
  assert.equal(e.hp, ENEMIES.emberimp.hp);
  assert.equal(npcs[0].role, 'emberimp');
  assert.equal(npcs[0].name, 'Ember imp');
  assert.equal(e.a.ai, true);
  assert.deepEqual(fx, ['summon_poof']);
});
