// node tests/gear_arrows.mjs — compare arrows: upgrade / downgrade / equal / empty slot / weaker ring
import { compareToEquipped, score } from '../game/loot.js';
import { arrowDir, arrowKind, ARROW_PAL } from '../game/gear_arrows.js';

const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1; };
const it = (slot, mods, extra = {}) => ({ slot, mods, gems: extra.gems || [], up: extra.up || 0, procs: extra.procs || [] });

const gloves = it('gloves', { crit: 0.01 });          // score 0.03
const same = it('gloves', { meleeMul: 0.03 });        // score 0.03, different mods
const better = it('gloves', { meleeMul: 0.05 });      // score 0.05
const worse = it('gloves', { hpAdd: 1 });             // score 0.005
ok(score(gloves) === score(same) && score(better) > score(gloves) && score(worse) < score(gloves), 'fixture scores: equal pair, upgrade, downgrade');

ok(compareToEquipped(better, { gloves }) === 1 && arrowKind(better, { gloves }) === 'up', 'upgrade over equipped');
ok(compareToEquipped(worse, { gloves }) === -1 && arrowKind(worse, { gloves }) === 'down', 'downgrade under equipped');
ok(compareToEquipped(same, { gloves }) === 0 && arrowDir(same, { gloves }) === 0 && arrowKind(same, { gloves }) === 'none', 'equal score draws no arrow');
ok(compareToEquipped(worse, { gloves: null }) === 1 && compareToEquipped(worse, {}) === 1 && arrowKind(worse, {}) === 'up', 'empty slot is an upgrade');

const rings = {
  ringL: it('ringL', { crit: 0.04 }),   // 0.12
  ringR: it('ringR', { crit: 0.01 }),   // 0.03, the weaker ring
};
ok(score(rings.ringR) < score(rings.ringL), 'fixture: ringR is the weaker ring');
ok(compareToEquipped(it('ringL', { crit: 0.02 }), rings) === 1, 'ring above the weaker ring is an upgrade');
ok(compareToEquipped(it('ringR', { crit: 0.005 }), rings) === -1, 'ring under the weaker ring is a downgrade');
ok(compareToEquipped(it('ringL', { crit: 0.01 }), rings) === 0, 'ring equal to the weaker ring is equal');
ok(compareToEquipped(it('ringL', { hpAdd: 1 }), { ringL: rings.ringL, ringR: null }) === 1, 'one empty ring slot is an upgrade');
ok(compareToEquipped(it('ringR', { hpAdd: 1 }), { ringL: null, ringR: null }) === 1, 'both ring slots empty is an upgrade');
ok(compareToEquipped(it('helm', { hpAdd: 1 }), { helm: it('helm', { meleeMul: 0.2 }), ringL: null }) === -1, 'a filled non-ring slot does not use the empty ring');

const neck = it('neck', { crit: 0.01 });
ok(compareToEquipped(it('neck', { crit: 0.01 }, { gems: ['rift_shard'] }), { neck }) === 1, 'gems count through score()');
ok(ARROW_PAL.up.mid === '#3cf08a' && ARROW_PAL.up.hi === '#b8ffd4' && ARROW_PAL.up.lo === '#14a85a', 'up arrow uses ORB_NEON green');
ok(ARROW_PAL.down.hi === '#ff5a4a' && ARROW_PAL.down.mid === '#e0302a' && ARROW_PAL.down.lo === '#a81c22', 'down arrow uses NEON red');

if (!process.exitCode) console.log('gear arrows: all checks passed');
