// node tests/gear14_migration.mjs : an old 3-slot / 5-rarity save migrates to 14 slots / template tiers
import * as LO from '../game/loot.js';
const old = {
  v: 2, gold: 10,
  gear: { weapon: { uid: 'a', slot: 'weapon', name: 'Sunfire Ember Blade', rar: 4, lv: 6, mods: { meleeMul: 0.2 }, gems: ['frost_core', null], up: 7, rr: 2 },
          armor: { uid: 'b', slot: 'armor', name: 'Gleaming Moss Mail', rar: 1, lv: 3, mods: { hpAdd: 11 }, gems: [null], up: 2 },
          trinket: { uid: 'c', slot: 'trinket', name: 'Starlit Locket', rar: 3, lv: 4, mods: { crit: 0.03 }, gems: ['rift_shard'], up: 0 } },
  bag: [{ uid: 'd', slot: 'weapon', name: 'Plain Oak Wand', rar: 0, lv: 1, mods: {}, gems: [] },
        { uid: 'e', slot: 'trinket', name: 'Runed Glow Ring', rar: 2, lv: 2, mods: {}, gems: [null, null] }],
};
const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1; };
const S = JSON.parse(JSON.stringify(old)); LO.ensure(S);
ok(Object.keys(S.gear).length === 14 && LO.SLOTS.every((s) => s in S.gear), '14 gear slots: ' + Object.keys(S.gear).join(','));
ok(S.gear.primary && S.gear.primary.uid === 'a' && S.gear.primary.slot === 'primary', 'weapon -> primary');
ok(S.gear.chest && S.gear.chest.uid === 'b', 'armor -> chest');
ok(S.gear.neck && S.gear.neck.uid === 'c', 'trinket -> neck');
ok(S.gear.primary.rar === 3 && S.gear.chest.rar === 0 && S.gear.neck.rar === 2, 'rarities legendary->Legendary, uncommon->Common, epic->Epic: ' + [S.gear.primary, S.gear.chest, S.gear.neck].map((i) => LO.RARITY[i.rar].name).join('/'));
ok(S.bag[0].rar === 0 && S.bag[1].rar === 1 && S.bag[0].slot === 'primary' && S.bag[1].slot === 'neck', 'bag: common->Common, rare->Rare, slots mapped');
ok(JSON.stringify(S.gear.primary.gems) === '["frost_core",null]' && S.gear.primary.up === 7 && S.gear.primary.rr === 2 && S.gear.neck.gems[0] === 'rift_shard', 'gems, sockets, temper, rerolls kept');
const twice = JSON.stringify(S); LO.ensure(S); LO.migrateGear(S); ok(JSON.stringify(S) === twice, 'idempotent (second load changes nothing)');
const bank = { v: 1, items: JSON.parse(JSON.stringify(old.bag)), gems: {}, gold: 0 }; bank.items.forEach(LO.migrateItem);
ok(bank.items.map((i) => i.slot + ':' + LO.RARITY[i.rar].name).join() === 'primary:Common,neck:Rare', 'bank items migrated: ' + bank.items.map((i) => i.slot + ':' + LO.RARITY[i.rar].name).join());
// new drops, rings, compare
let r = 0; const rnd = () => ((r = (r * 9301 + 49297) % 233280) / 233280);
const ring1 = LO.makeItem(5, 1, 'ringL', rnd), ring2 = LO.makeItem(5, 3, 'ringL', rnd), ring3 = LO.makeItem(5, 2, 'ringL', rnd);
S.bag = [ring1, ring2, ring3]; LO.equip(S, 0); LO.equip(S, 0);
ok(S.gear.ringL === ring1 && S.gear.ringR === ring2, 'two rings fill ringL then ringR');
const weak = LO.targetSlot(S, ring3); ok(weak === 'ringL', 'third ring compares/replaces the weaker ring: ' + weak + ' | ' + LO.compare(S, ring3).replace(/<[^>]+>/g, ''));
const counts = [0, 0, 0, 0, 0]; for (let i = 0; i < 20000; i++) counts[LO.rollRarity(2, 0, 0, Math.random)]++;
console.log('boss-column sample (20k):', counts.map((c, i) => LO.RARITY[i].name + ' ' + (c / 200).toFixed(1) + '%').join(', '));
const sl = new Set(); for (let i = 0; i < 2000; i++) sl.add(LO.makeItem(3, null, null).slot);
ok(sl.size === 13 && !sl.has('ringR'), 'random drops cover 13 kinds (rings roll once): ' + [...sl].join(','));
