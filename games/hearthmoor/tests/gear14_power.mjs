// gear14 power check: average total mods of a full kit, live 6299ce7 (weapon+armor+trinket) vs gear14 (14 slots, GEAR_NORM).
// gearfx: the same kit is also compared to gear14 at 58c1998. New keys count as BASE rolls (they replace one optional). Procs are not mods. runePct / shieldPct stay out of the budget.
// run: node tests/gear14_power.mjs   (reads the old loot.js from git; no game state touched)
import { execSync } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const NEW = await import('../game/loot.js');
const d = mkdtempSync(join(tmpdir(), 'gear14-old-'));
const pull = async (rev, name) => { const f = join(d, name); writeFileSync(f, execSync(`git show ${rev}:games/hearthmoor/game/loot.js`)); return import(f); };
const OLD = await pull('6299ce7', 'loot_old.mjs'), G14 = await pull('58c1998', 'loot_g14.mjs');
const BASE = { hpAdd: 8, stAdd: 4, meleeMul: 0.04, spellMul: 0.04, crit: 0.01, critDmg: 0.05, guardMul: -0.015, healMul: 0.04, summonMul: 0.05, spellCd: 0.015, stRegen: 0.04, rollSpeed: 0.04, resFire: 6, resWater: 6, resLight: 6, resDark: 6, resAll: 3, avoid: 0.01, move: 0.015, haste: 0.015, block: 0.03 };   // gearfx: resX 6, resAll 3, avoid .01, move .015, haste .015, block .03
const N = 4000;
const kit = (L, slots, lv, rar) => { const m = {}; for (const sl of slots) for (const [k, v] of Object.entries(L.makeItem(lv, rar, sl).mods)) m[k] = (m[k] || 0) + v; return m; };
const avg = (L, slots, lv, rar) => { const t = {}; for (let i = 0; i < N; i++) for (const [k, v] of Object.entries(kit(L, slots, lv, rar))) t[k] = (t[k] || 0) + v / N; return t; };
const units = (m) => Object.entries(m).reduce((a, [k, v]) => (k === 'runePct' || k === 'shieldPct' || !(k in BASE) ? a : a + v / BASE[k]), 0);   // gearfx: each counted mod in base rolls; procs / runePct / shieldPct excluded
const f2 = (x) => (Math.abs(x) < 1 ? x.toFixed(3) : x.toFixed(1));
const pairs = [['Common', 0, 0], ['Rare', 2, 1], ['Epic', 3, 2], ['Legendary', 4, 3], ['Runeforged (vs old Legendary)', 4, 4]];
console.log(`GEAR_NORM = ${NEW.GEAR_NORM.toFixed(4)}  (3 / sum SLOT_W = 3 / ${(3 / NEW.GEAR_NORM).toFixed(2)})`);
console.log('| rarity | lv | old 3-piece units | new 14-piece units | new/old | old HP / melee / crit | new HP / melee / crit |');
console.log('|---|---|---|---|---|---|---|');
let worst = 0; const fxRows = [], fxBy = {};
for (const [name, ro, rn] of pairs) for (const lv of [1, 10, 20]) {
  const o = avg(OLD, ['weapon', 'armor', 'trinket'], lv, ro), n = avg(NEW, NEW.SLOTS, lv, rn), g = avg(G14, G14.SLOTS, lv, rn);
  const r = units(n) / units(o), rf = units(n) / units(g), label = name.startsWith('Runeforged') ? 'Runeforged' : name;
  if (rn < 4) worst = Math.max(worst, Math.abs(r - 1));
  fxBy[label] = Math.max(fxBy[label] || 0, Math.abs(rf - 1));
  fxRows.push(`| ${label} | ${lv} | ${units(g).toFixed(2)} | ${units(n).toFixed(2)} | ${rf.toFixed(3)} |`);
  console.log(`| ${name} | ${lv} | ${units(o).toFixed(2)} | ${units(n).toFixed(2)} | ${r.toFixed(2)} | ${f2(o.hpAdd || 0)} / ${f2(o.meleeMul || 0)} / ${f2(o.crit || 0)} | ${f2(n.hpAdd || 0)} / ${f2(n.meleeMul || 0)} / ${f2(n.crit || 0)} |`);
}
console.log(`${worst < 0.10 ? 'PASS' : 'FAIL'} same-name tiers within 10% of the old kit (worst ${(worst * 100).toFixed(0)}%)`);
console.log('| rarity | lv | gear14 58c1998 units | gearfx units | gearfx/gear14 |');
console.log('|---|---|---|---|---|');
fxRows.forEach((row) => console.log(row));
const fxMax = Math.max(...Object.values(fxBy)), fxBits = Object.entries(fxBy).map(([k, v]) => `${k} ${(v * 100).toFixed(1)}%`).join(', ');
console.log(`${fxMax < 0.10 ? 'PASS' : 'FAIL'} gearfx vs gear14 58c1998 within 10% (${fxBits}; new keys in BASE units, procs and runePct/shieldPct excluded)`);
process.exit(worst < 0.10 && fxMax < 0.10 ? 0 : 1);
