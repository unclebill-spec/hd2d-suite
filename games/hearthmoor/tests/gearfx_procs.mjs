// gearfx: proc table, tier rolls, chance caps, CAPS, canWear. Pure node, no DOM.
// run: node tests/gearfx_procs.mjs
import * as LO from '../game/loot.js';
import { Combat } from '../game/combat.js';
const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1; };
const lcg = (seed) => { let r = seed; return () => ((r = (r * 9301 + 49297) % 233280) / 233280); };
const withRand = (xs, fn) => { const orig = Math.random; let i = 0; Math.random = () => xs[Math.min(i++, Math.max(0, xs.length - 1))] ?? 0.99; try { return fn(); } finally { Math.random = orig; } };
const WANT = {
  lifeSteal: { school: 'dark', ch: .15, icd: 1, healPct: .15 },
  fireBolt: { school: 'fire', ch: .10, icd: 3, base: 8, perLv: 3 },
  freeze: { school: 'water', ch: .06, icd: 8, dur: 1, eliteDur: .5, bossSlow: .4, bossDur: 1.5, per: 'target' },
  root: { school: 'water', ch: .08, icd: 8, dur: 2, boss: 'immune', per: 'target' },
  heal: { school: 'light', ch: .10, icd: 4, healPct: .04 },
  damageShield: { school: 'fire', ch: .08, icd: 12, dur: 5, reflect: .2 },
  runeShield: { school: 'light', ch: .06, icd: 15, absorb: .08, dur: 6 },
};
const same = (a, b) => { const ka = Object.keys(a), kb = Object.keys(b); return ka.length === kb.length && ka.every((k) => a[k] === b[k]); };
ok(Object.keys(WANT).every((id) => LO.PROCS[id] && same(LO.PROCS[id], WANT[id])) && Object.keys(LO.PROCS).length === Object.keys(WANT).length, 'PROCS table: schools, chances, icds, heal/bolt/freeze/root/shield numbers');
ok(Object.values(LO.PROCS).every((p) => p.ch * 2 <= 0.35), 'every table chance, doubled, still sits at or under 0.35');
const schools = { fire: 'fire', ice: 'water', cold: 'water', water: 'water', light: 'light', lightning: 'light', dark: 'dark' };
ok(Object.entries(schools).every(([e, s]) => LO.SCHOOL_OF(e) === s) && LO.SCHOOL_OF() === 'physical' && LO.SCHOOL_OF('poison') === 'physical', 'SCHOOL_OF: ice/cold -> water, lightning -> light, missing -> physical');
// gearfx: seeded makeItem. Common/Rare never. Epic ~30% of one. Legendary always one. Runeforged one, plus ~35% a distinct second. Weapons only.
const tally = (rar, slot, n, seed) => {
  const rnd = lcg(seed); const c = { zero: 0, one: 0, two: 0, bad: 0, dup: 0 };
  for (let i = 0; i < n; i++) {
    const it = LO.makeItem(10, rar, slot, rnd), p = it.procs || [];
    if (p.length === 0) c.zero++; else if (p.length === 1) c.one++; else if (p.length === 2) c.two++; else c.bad++;
    if (p.length === 2 && p[0].id === p[1].id) c.dup++;
    for (const x of p) if (!LO.PROCS[x.id] || x.ch !== LO.PROCS[x.id].ch || x.icd !== LO.PROCS[x.id].icd || x.id == null) c.bad++;
  }
  return c;
};
for (const sl of ['primary', 'secondary', 'ranged']) {
  const C = tally(0, sl, 400, 11), R = tally(LO.R_RARE, sl, 400, 12), L = tally(LO.R_LEG, sl, 300, 14);
  ok(C.zero === 400 && C.bad === 0, `${sl} Common never procs`);
  ok(R.zero === 400 && R.bad === 0, `${sl} Rare never procs`);
  ok(L.one === 300 && L.bad === 0, `${sl} Legendary always exactly 1 proc`);
}
const epic = tally(LO.R_EPIC, 'primary', 4000, 3), rune = tally(LO.R_RUNE, 'primary', 4000, 5);
const epic2 = tally(LO.R_EPIC, 'secondary', 2000, 6), epic3 = tally(LO.R_EPIC, 'ranged', 2000, 7);
const rune2 = tally(LO.R_RUNE, 'secondary', 2000, 8), rune3 = tally(LO.R_RUNE, 'ranged', 2000, 9);
const rate = (c) => c.one / (c.zero + c.one + c.two);
ok(epic.two === 0 && epic.bad === 0 && rate(epic) > 0.25 && rate(epic) < 0.35, `Epic primary ~30% one proc (${(rate(epic) * 100).toFixed(1)}%)`);
ok(rate(epic2) > 0.24 && rate(epic2) < 0.36 && epic2.two === 0 && rate(epic3) > 0.24 && rate(epic3) < 0.36 && epic3.two === 0, `Epic secondary/ranged ~30% (${(rate(epic2) * 100).toFixed(1)}% / ${(rate(epic3) * 100).toFixed(1)}%)`);
ok(rune.zero === 0 && rune.bad === 0 && rune.dup === 0 && rune.two / 4000 > 0.30 && rune.two / 4000 < 0.40, `Runeforged primary always 1-2, ~35% two, distinct (${(rune.two / 40).toFixed(1)}%)`);
ok(rune2.zero === 0 && rune2.dup === 0 && rune2.bad === 0 && rune3.zero === 0 && rune3.dup === 0 && rune3.bad === 0, 'Runeforged secondary and ranged stay 1-2 distinct procs');
let armorProc = 0; const rndA = lcg(21);
for (const sl of ['helm', 'chest', 'neck', 'ringL', 'belt', 'cloak']) for (let i = 0; i < 40; i++) { const it = LO.makeItem(12, LO.R_RUNE, sl, rndA); if (it.procs) armorProc++; }
ok(armorProc === 0, 'procs only on primary / secondary / ranged');
// gearfx: chance = min(ch + crit*0.25, ch*2, 0.35). Checked on the formula and on Combat.rollProc.
const pch = (ch, crit) => Math.min(ch + crit * 0.25, ch * 2, 0.35);
ok(pch(0.15, 0) === 0.15 && pch(0.15, 1) === 0.30 && pch(0.25, 1) === 0.35 && pch(0.10, 0.4) === 0.20, 'chance formula caps at ch*2 and 0.35');
ok(Object.values(LO.PROCS).every((p) => pch(p.ch, 0) === p.ch && pch(p.ch, 1) === Math.min(p.ch * 2, 0.35)), 'every table chance obeys both caps');
const roll = (crit, procs, rand, dmg = 40, e) => {
  const c = Object.create(Combat.prototype); Object.defineProperty(c, 'M', { get() { return { crit, procs, spellMul: 1 }; } });
  c.procCd = {}; c.gfx = { procs: 0, lastProc: null }; c.layer = null; c._inProc = false;
  c.G = { S: { hp: 200, lv: 10 }, audio: { sfx() {} } }; c.ctx = { player: { x: 0, y: 0, z: 0 } }; c.maxHp = () => 200; c.heal = (n) => { c._heal = (c._heal || 0) + n; };
  const foe = e || { state: 'chase', D: {}, a: { x: 1, y: 0, z: 1 }, hp: 80 };
  withRand(rand, () => c.rollProc(foe, dmg)); return { c, foe };
};
const cap2 = roll(1, [{ id: 'lifeSteal', ch: 0.15, icd: 1 }], [0.31]);
const cap2hit = roll(1, [{ id: 'lifeSteal', ch: 0.15, icd: 1 }], [0.29], 40);
const cap35 = roll(1, [{ id: 'lifeSteal', ch: 0.25, icd: 1 }], [0.36]);
const cap35hit = roll(1, [{ id: 'lifeSteal', ch: 0.25, icd: 1 }], [0.34], 80);
ok(cap2.c.gfx.procs === 0 && cap2hit.c.gfx.procs === 1 && cap2hit.c._heal === 6, 'ch*2 cap: crit 1 on 15% stays 30% (0.31 misses, 0.29 leeches 15% of the hit)');
ok(cap35.c.gfx.procs === 0 && cap35hit.c.gfx.procs === 1, '0.35 cap: 0.36 misses, 0.34 hits even when ch + crit*0.25 and ch*2 are higher');
const one = roll(0, [{ id: 'lifeSteal', ch: 0.15, icd: 1 }, { id: 'heal', ch: 0.10, icd: 4 }], [0, 0, 0], 100);
ok(one.c.gfx.procs === 1, 'one proc per landed hit');
const icd = roll(0, [{ id: 'heal', ch: 0.10, icd: 4 }], [0, 0]);
withRand([0], () => icd.c.rollProc(icd.foe, 10));
ok(icd.c.gfx.procs === 1 && icd.c.procCd.heal === 4, 'a second roll inside the ICD does not fire');
const boss = roll(0, [{ id: 'root', ch: 0.08, icd: 8 }, { id: 'heal', ch: 0.10, icd: 4 }], [0], 10, { state: 'chase', D: { boss: true }, a: { x: 1, y: 0, z: 0 } });
ok(boss.c.gfx.lastProc === 'heal' && boss.foe.rootT == null, 'root is not offered to a boss, so the other proc can roll');
const chained = Object.create(Combat.prototype); Object.defineProperty(chained, 'M', { get() { return { crit: 0, procs: [{ id: 'lifeSteal', ch: 0.15, icd: 1 }] }; } });
chained.procCd = {}; chained.gfx = { procs: 0 }; chained.layer = null; chained._inProc = true;
withRand([0], () => chained.rollProc({ state: 'chase', D: {}, a: { x: 0, y: 0, z: 0 } }, 10));
ok(chained.gfx.procs === 0, 'procs never trigger procs');
const fr = Object.create(Combat.prototype); fr.layer = null;
const b = { D: { boss: true } }, el = { D: { elite: true } }, nm = { D: {} }; fr.procFreeze(b); fr.procFreeze(el); fr.procFreeze(nm);
ok(b.chillT === 1.5 && b.chillPct === 0.4 && b.rootT == null && el.rootT === 0.5 && el.frozenT === 0.5 && nm.rootT === 1 && nm.frozenT === 1, 'freeze: 1.0 s, elite/rare 0.5 s, boss 40% slow 1.5 s');
const ready = Object.create(Combat.prototype); ready.procCd = {};
ok(ready.procReady({ D: { boss: true } }, { id: 'root' }) === false && ready.procReady({ D: {}, procT: { freeze: 1 } }, { id: 'freeze' }) === false && ready.procReady({ D: {} }, { id: 'freeze' }) === true, 'per-target ICD and boss root immunity');
// gearfx: CAPS. Resist uses R/(R+K) then 60%. Avoid 25% (spells/bolts half). Move clamps at roll time. A connecting hit still deals at least 1.
const C = LO.CAPS;
ok(C.res === 0.6 && C.avoid === 0.25 && C.avoidSpell === 0.5 && C.move === 0.25 && C.moveFeet === 0.1 && C.moveCloak === 0.05 && C.haste === 0.5 && C.block === 0.5 && C.blockSoak === 0.5 && C.runePct === 0.2 && C.shieldPct === 0.2 && C.minHit === 1, 'CAPS values');
ok(C.resK(10, 1) === 150 && C.resK(null, 7) === 120 && C.resK(undefined, 7) === 120 && C.resK(0, 7) === 50, 'K = 50 + 10*foeLevel, else the player level');
const resistOf = (R, foeLv, playerLv) => { const c = Object.create(Combat.prototype); c.G = { S: { lv: playerLv } }; return c.resistPct(R, foeLv == null ? null : { lv: foeLv }); };
ok([1, 20, 50].every((lv) => resistOf(10000, lv, lv) === 0.6) && resistOf(10000, 10000, 1) < 0.6 && resistOf(10000, 1, 1) <= 0.6 && resistOf(0, 10, 10) === 0 && resistOf(30, 10, 1) === 30 / (30 + 150), 'resist reduction never above 60% even at R=10000');
const swing = (M, dmg, opt = {}) => {
  const p = { x: 0, z: 0, y: 0, iframes: 0, facing: 'down', act: null, r: 0.4 };
  const G = { S: { hp: opt.hp || 5000, mode: 'adventurer', lv: opt.lv || 20, cls: 'seer', gear: opt.shield ? { secondary: { name: 'Oak Buckler', slot: 'secondary' } } : {} }, audio: { sfx() {} } };
  const c = Object.create(Combat.prototype); Object.defineProperty(c, 'M', { get() { return M; } });
  const src = { x: 0, z: 3, proj: !!opt.proj, bolt: !!opt.bolt }; if (opt.fire) src.fire = true;
  c.ctx = { player: p }; c.G = G; c.godT = 0; c.skin = null; c.ward = null; c.runeAbs = 0; c.runeAbsT = 0; c.dmgShieldT = 0; c.layer = null; c.nums = [];
  c.enemies = [{ a: src, D: opt.element ? { element: opt.element } : {}, lv: opt.foeLv == null ? 20 : opt.foeLv }];
  const before = G.S.hp; withRand(opt.rand || [], () => c.hurtPlayer(dmg, src)); return { dealt: before - G.S.hp, c };
};
const bare = { avoid: 0, runePct: 0, shieldPct: 0, block: 0, guardMul: 1, resFire: 0, resWater: 0, resLight: 0, resDark: 0, resAll: 0 };
ok(swing({ ...bare, avoid: 1 }, 100, { rand: [0.24] }).dealt === 0 && swing({ ...bare, avoid: 1 }, 100, { rand: [0.26] }).dealt === 100, 'avoid never above 25% (0.24 dodges, 0.26 connects for full damage)');
ok(swing({ ...bare, avoid: 1 }, 100, { proj: true, rand: [0.12] }).dealt === 0 && swing({ ...bare, avoid: 1 }, 100, { proj: true, rand: [0.13] }).dealt === 100 && swing({ ...bare, avoid: 1 }, 100, { bolt: true, rand: [0.13] }).dealt === 100, 'spells/bolts use half avoid (12.5%)');
const full = { avoid: 0, runePct: 1, shieldPct: 1, block: 1, guardMul: 1, resFire: 10000, resWater: 10000, resLight: 10000, resDark: 10000, resAll: 10000 };
ok(swing(full, 100, { element: 'fire', shield: true, rand: [0] }).dealt === 16, 'fully capped fire + block: 100 -> 16 (60% resist, 20% shield, 50% soak), not immune');
ok(swing(full, 100, { element: 'fire', shield: true, rand: [0.99] }).dealt === 32, 'fully capped fire, block misses: 100 -> 32');
ok(swing(full, 100, { shield: true, rand: [0] }).dealt === 40, 'fully capped physical + block: 100 -> 40 (20% rune, 50% soak)');
ok(swing(full, 100, { shield: true, rand: [0.99] }).dealt === 80, 'fully capped physical, block misses: 100 -> 80');
ok(swing({ ...bare, runePct: 1 }, 100).dealt === 80 && swing({ ...bare, shieldPct: 1 }, 100, { element: 'fire' }).dealt === 80, 'runePct and shieldPct cap at 20% even when the stat is 100%');
ok(swing({ ...bare, block: 1 }, 100, { shield: true, rand: [0] }).dealt === 50 && swing({ ...bare, block: 1 }, 100, { shield: true, rand: [0.51] }).dealt === 100, 'block chance caps at 50% and a block soaks 50%');
ok([swing(full, 1, { element: 'fire', shield: true, rand: [0] }).dealt, swing(full, 1, { shield: true, rand: [0] }).dealt, swing(full, 1, { element: 'dark' }).dealt].every((n) => n >= 1), 'a 1-damage hit that connects still deals at least 1');
ok(swing({ ...bare, resLight: 10000 }, 100, { element: 'lightning' }).dealt === 40 && swing({ ...bare, resWater: 10000 }, 100, { element: 'cold' }).dealt === 40 && swing({ ...bare, resWater: 10000 }, 100, { element: 'ice' }).dealt === 40 && swing({ ...bare, resDark: 10000 }, 100, { element: 'dark' }).dealt === 40, 'lightning -> light, cold/ice -> water, dark -> dark');
const paceOf = (M) => { const c = Object.create(Combat.prototype); Object.defineProperty(c, 'M', { get() { return M; } }); return c; };
ok(paceOf({ haste: 9, move: 9 }).hasteMul() === 1.5 && paceOf({ haste: 9, move: 9 }).moveMul() === 1.25, 'haste caps at +50%, move at +25% total');
ok(paceOf({ haste: 0.2, move: 0.1 }).hasteMul() === 1.2 && paceOf({ haste: 0.2, move: 0.1 }).moveMul() === 1.1, 'haste and move under the cap pass through');
const moveCheck = (sl, lv, rar, cap, n, seed) => {
  const rnd = lcg(seed), k = LO.RARITY[rar].mul * (1 + (lv - 1) * 0.06) * LO.SLOT_W[sl] * LO.GEAR_NORM, expect = Math.min(cap, +(0.015 * k).toFixed(3));
  let seen = 0, bad = 0;
  for (let i = 0; i < n; i++) { const it = LO.makeItem(lv, rar, sl, rnd); if (it.mods.move == null) continue; seen++; if (Math.abs(it.mods.move - expect) > 1e-9 || it.mods.move - cap > 1e-9) bad++; }
  return { seen, bad, expect };
};
const feetHi = moveCheck('feet', 200, LO.R_RUNE, C.moveFeet, 400, 31), cloakHi = moveCheck('cloak', 200, LO.R_RUNE, C.moveCloak, 400, 32);
const feetLo = moveCheck('feet', 1, 0, C.moveFeet, 400, 33), cloakLo = moveCheck('cloak', 1, 0, C.moveCloak, 400, 34);
ok(feetHi.seen > 0 && feetHi.bad === 0 && feetHi.expect === 0.1 && cloakHi.seen > 0 && cloakHi.bad === 0 && cloakHi.expect === 0.05, `move clamp at roll time: feet ${feetHi.expect} (${feetHi.seen}), cloak ${cloakHi.expect} (${cloakHi.seen})`);
ok(feetLo.seen > 0 && feetLo.bad === 0 && feetLo.expect < C.moveFeet && cloakLo.seen > 0 && cloakLo.bad === 0 && cloakLo.expect < C.moveCloak, `low-level move is not clamped early (feet ${feetLo.expect}, cloak ${cloakLo.expect})`);
let blockSeen = 0, blockBad = 0; const rndB = lcg(41);
for (let i = 0; i < 500; i++) { const it = LO.makeItem(10, LO.R_RUNE, 'secondary', rndB), shield = /Buckler|Shield/.test(it.name); if (it.mods.block == null) continue; blockSeen++; if (!shield || it.mods.block - 0.5 > 1e-9) blockBad++; }
ok(blockSeen > 0 && blockBad === 0, `block is a shield-type secondary only (${blockSeen} rolled, none over the 50% cap)`);
const ORDER = ['plate', 'chain', 'leather', 'cloth'], CLASSES = ['runeguard', 'cinderknight', 'stormborn', 'grovekeeper', 'wildcaller', 'seer'];
const badWear = [];
ok(JSON.stringify(LO.CLASS_ARMOR) === JSON.stringify({ runeguard: 'plate', cinderknight: 'plate', stormborn: 'chain', grovekeeper: 'chain', wildcaller: 'leather', seer: 'cloth' }), 'CLASS_ARMOR');
for (const cls of CLASSES) for (const at of ORDER) {
  const allow = ORDER.indexOf(at) >= ORDER.indexOf(LO.CLASS_ARMOR[cls]);
  if (LO.canWear(cls, { at, slot: 'chest' }) !== allow) badWear.push(`${cls}/${at}`);
}
ok(!badWear.length && CLASSES.every((cls) => LO.canWear(cls, { slot: 'primary' }) && LO.canWear(cls, { slot: 'chest' })), 'canWear: plate all, chain down, leather leather/cloth, cloth cloth; untyped pieces are free (' + (badWear.join(', ') || '6 classes') + ')');
const pctOf = (v) => Math.round(v * 100);
const advBand = (rar, lo, hi, n, seed) => {
  const rnd = lcg(seed); let bad = 0, seen = 0; const vals = new Set();
  for (let i = 0; i < n; i++) {
    const it = LO.makeItem(15, rar, 'chest', rnd);
    const keys = ['runePct', 'shieldPct'].filter((k) => it.mods[k] != null);
    if (keys.length !== (rar === LO.R_RUNE ? 2 : 1)) bad++;
    for (const k of keys) { seen++; const pct = pctOf(it.mods[k]); vals.add(pct); if (pct < lo || pct > hi) bad++; }
  }
  return { bad, seen, vals: [...vals].sort((a, b) => a - b) };
};
const legBand = advBand(LO.R_LEG, 1, 2, 400, 51), runeBand = advBand(LO.R_RUNE, 3, 4, 400, 52);
ok(legBand.bad === 0 && legBand.seen === 400 && legBand.vals.includes(1) && legBand.vals.includes(2) && legBand.vals.every((p) => p >= 1 && p <= 2), `Legendary rune/shield rolls in [1,2]% (${legBand.vals.join(',')})`);
ok(runeBand.bad === 0 && runeBand.seen === 800 && runeBand.vals.includes(3) && runeBand.vals.includes(4) && runeBand.vals.every((p) => p >= 3 && p <= 4), `Runeforged rune/shield rolls in [3,4]% (${runeBand.vals.join(',')})`);
const slotsA = ['helm', 'chest', 'legs', 'feet', 'arms', 'gloves', 'belt', 'cloak'];
let nameBad = 0; const rndName = lcg(61);
for (let i = 0; i < 2000; i++) {
  const it = LO.makeItem(1 + (i % 20), i % 5, slotsA[i % slotsA.length], rndName, 0, CLASSES[i % CLASSES.length]);
  if (!it.at || LO.armorTypeOf(it.name) !== it.at) nameBad++;
}
ok(nameBad === 0, `2000 armor-slot drops across classes: armorTypeOf(name) === at (${nameBad} mismatch)`);
