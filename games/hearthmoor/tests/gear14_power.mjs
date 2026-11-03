// gear14 power check: average total mods of a full kit, live 6299ce7 (weapon+armor+trinket) vs gear14 (14 slots, GEAR_NORM).
// run: node tests/gear14_power.mjs   (reads the old loot.js from git; no game state touched)
import { execSync } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const NEW = await import('../game/loot.js');
const d = mkdtempSync(join(tmpdir(), 'gear14-old-')), f = join(d, 'loot_old.mjs');
writeFileSync(f, execSync('git show 6299ce7:games/hearthmoor/game/loot.js'));
const OLD = await import(f);
const BASE = { hpAdd: 8, stAdd: 4, meleeMul: 0.04, spellMul: 0.04, crit: 0.01, critDmg: 0.05, guardMul: -0.015, healMul: 0.04, summonMul: 0.05, spellCd: 0.015, stRegen: 0.04, rollSpeed: 0.04 };
const N = 4000;
const kit = (L, slots, lv, rar) => { const m = {}; for (const sl of slots) for (const [k, v] of Object.entries(L.makeItem(lv, rar, sl).mods)) m[k] = (m[k] || 0) + v; return m; };
const avg = (L, slots, lv, rar) => { const t = {}; for (let i = 0; i < N; i++) for (const [k, v] of Object.entries(kit(L, slots, lv, rar))) t[k] = (t[k] || 0) + v / N; return t; };
const units = (m) => Object.entries(m).reduce((a, [k, v]) => a + v / BASE[k], 0);   // each mod in "base rolls" so % and flat mods add up
const f2 = (x) => (Math.abs(x) < 1 ? x.toFixed(3) : x.toFixed(1));
const pairs = [['Common', 0, 0], ['Rare', 2, 1], ['Epic', 3, 2], ['Legendary', 4, 3], ['Runeforged (vs old Legendary)', 4, 4]];
console.log(`GEAR_NORM = ${NEW.GEAR_NORM.toFixed(4)}  (3 / sum SLOT_W = 3 / ${(3 / NEW.GEAR_NORM).toFixed(2)})`);
console.log('| rarity | lv | old 3-piece units | new 14-piece units | new/old | old HP / melee / crit | new HP / melee / crit |');
console.log('|---|---|---|---|---|---|---|');
let worst = 0;
for (const [name, ro, rn] of pairs) for (const lv of [1, 10, 20]) {
  const o = avg(OLD, ['weapon', 'armor', 'trinket'], lv, ro), n = avg(NEW, NEW.SLOTS, lv, rn), r = units(n) / units(o);
  if (rn < 4) worst = Math.max(worst, Math.abs(r - 1));
  console.log(`| ${name} | ${lv} | ${units(o).toFixed(2)} | ${units(n).toFixed(2)} | ${r.toFixed(2)} | ${f2(o.hpAdd || 0)} / ${f2(o.meleeMul || 0)} / ${f2(o.crit || 0)} | ${f2(n.hpAdd || 0)} / ${f2(n.meleeMul || 0)} / ${f2(n.crit || 0)} |`);
}
console.log(`${worst < 0.35 ? 'PASS' : 'FAIL'} same-name tiers within 35% of the old kit (worst ${(worst * 100).toFixed(0)}%; rare/epic gaps are the template mul change 1.9->1.5, 2.6->2.0)`);
process.exit(worst < 0.35 ? 0 : 1);
