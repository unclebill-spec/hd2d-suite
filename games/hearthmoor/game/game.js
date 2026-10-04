// Hearthmoor: a cozy HD-2D action RPG on the hd2d runtime (engine/main.js boot + hooks).
// Area manager (fresh canvas per area, fade), hero picker (6 starters), real-time combat (combat.js), dialogue,
// 3 errands + quest log, bag, persistent clock, 4 spell slots, save/load (localStorage hearthmoor-slot-1-v2, migrates
// v1), ambient audio, PWA install + fullscreen + display presets.
import { boot, DISPLAY_PRESETS, getDisplay, setDisplay } from '../engine/main.js';
import { ITEMS, QUESTS, TALK, SPELL_NAMES, markerFor } from './data.js';
import { Ambient } from './audio.js';
import * as PR from './progress.js';
import { HEROES, HERO, SPELLS, SUMMONS, CHARM_DMG, CHARM_CD } from './heroes.js';
import { Combat } from './combat.js';
import { Glow } from './glow.js';
import { Hollows } from './hollows.js';
import { Garden } from './garden.js';
import { Weather, weatherAt } from './weather.js';
import * as LO from './loot.js';
import { Shop, drinkTonic, goodIconURL } from './shop.js';

// PWA install: catch the browser's prompt as early as possible (Chrome / Edge / Android); iPhone gets a tip instead
let installEvt = null;
addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); installEvt = e; syncInstall(); });
addEventListener('appinstalled', () => { installEvt = null; syncInstall(); });

const Q = new URLSearchParams(location.search);
// 3 save slots: hearthmoor-slot-<n>-v2. Slot 1 keeps the old single-slot key, so an existing save simply is slot 1.
const SLOT_N = 3;
const slotKey = (n) => `hearthmoor-slot-${n}-v2`;
const SLOT_V2 = slotKey(1);
const SLOT_V1 = 'hearthmoor-slot-1-v1';       // read once for migration (into slot 1), never written or deleted
const V1_DONE = 'hearthmoor-v1-migrated';     // set when slot 1 is deleted, so the old v1 save doesn't come back
const LAST_SLOT = 'hearthmoor-lastslot';
const QA = Q.has('qa');                       // check-scene / screenshots: straight into ?area=, fresh state, no title, no saving
const AREAS = { plaza: 'areas/plaza/', lane: 'areas/lane/', mossglen: 'areas/mossglen/', hollows: 'areas/hollows/',
                rift: 'areas/rift/', vanaheim: 'areas/vanaheim/' };
const DAY_SECONDS = Number(Q.get('day') || 1440);  // one whole day = 24 real minutes (day, dusk, night, dawn)
const $ = (id) => document.getElementById(id);

// v2 adds the hero class (cls) and current HP; everything from v1 carries over unchanged
const fresh = () => ({ v: 2, cls: null, hp: null, area: 'plaza', pos: null, t: 0.62, inv: {}, quests: { bread: 0, tea: 0, cat: 0 }, picked: {}, flags: {},
                       cat: 'glade', spells: ['sparkle_burst'], played: 0, savedAt: null });

const G = {
  S: fresh(), game: null, ctx: null, busy: false, title: !QA, dlg: null, log: false, markers: {}, scenes: {}, armed: false,
  audio: new Ambient(), autosave: 20, near: null, downed: false, opts: false, picking: false,
  peace: Q.has('peace') || (QA && !Q.has('combat')),
  qaStill: QA && !Q.has('combat'),   // QA screenshots / check-scene: enemies stand around unless &combat
};
G.combat = new Combat(G);
G.glow = new Glow(G);
G.hollows = new Hollows(G);
G.garden = new Garden(G);
G.weather = new Weather(G);
G.weatherAt = weatherAt;   // smoke: the weather calendar
G.loot = new LO.Loot(G); G.LO = LO; G.PR = PR;
G.shopUI = new Shop(G); G.drinkTonic = () => drinkTonic(G);
window.__hm = G;   // smoke tests + debugging

// ------------------------------------------------------------------ save / load
G.slot = Math.min(SLOT_N, Math.max(1, +(Q.get('slot') || localStorage.getItem(LAST_SLOT)) || 1));
function readSave(n = G.slot) {
  try { const s = JSON.parse(localStorage.getItem(slotKey(n))); if (s && s.v === 2) return s; } catch (e) { /* corrupt: fall through */ }
  if (n !== 1 || localStorage.getItem(V1_DONE)) return null;
  try {   // migrate a v1 save: same fields, no class yet (Continue asks who you are, then carries on)
    const o = JSON.parse(localStorage.getItem(SLOT_V1));
    if (o && o.v === 1) return { ...fresh(), ...o, v: 2, cls: null, hp: null, migrated: 1 };
  } catch (e) { /* ignore */ }
  return null;
}
// the 4 spell slots: the hero's own spell first, then the newest three charms
function defaultSlots() { const h = HERO[G.S.cls]; return [...(h ? [h.spell] : []), ...G.S.spells.slice(-3)].slice(0, 4); }
// every spell this hero can slot: the class spell + every charm learned on errands
function knownSpells() { const h = HERO[G.S.cls]; return [...new Set([...(h ? [h.spell] : []), ...G.S.spells])]; }
// the spellbook (hero screen, Spells tab) can set G.S.slots (4 ids or null); otherwise the default above
function slots() {
  const known = knownSpells();
  if (!Array.isArray(G.S.slots)) return defaultSlots();
  const out = G.S.slots.filter((id) => id && known.includes(id));
  return out.length ? out.slice(0, 4) : defaultSlots();
}
function slotSpell(k, dir = 1) {   // cycle slot k through the known spells (slots 2-4 can be empty)
  const known = knownSpells();
  const cur = Array.isArray(G.S.slots) ? [...G.S.slots] : [...defaultSlots()];
  while (cur.length < 4) cur.push(null);
  const others = cur.filter((_, j) => j !== k);
  const opts = [...known.filter((id) => !others.includes(id)), ...(k > 0 ? [null] : [])];
  if (!opts.length) return false;
  const i = opts.indexOf(cur[k]);
  cur[k] = opts[(i + dir + opts.length) % opts.length];
  if (!cur.some(Boolean)) return false;
  G.S.slots = cur.map((id) => id || null);
  if (G.ctx) G.ctx.setSpellCycle(slots());
  return true;
}
G.slotSpell = slotSpell; G.knownSpells = knownSpells;
G.slots = slots;
function save(note) {
  if (QA || G.title) return false;
  const p = G.ctx && G.ctx.player;
  if (p) G.S.pos = [+p.x.toFixed(2), +p.z.toFixed(2), p.facing];
  G.S.area = G.area; G.S.savedAt = new Date().toISOString();
  localStorage.setItem(slotKey(G.slot), JSON.stringify(G.S)); localStorage.setItem(LAST_SLOT, String(G.slot));
  if (note) { toast('Saved ✓'); G.audio.sfx('save'); }
  return true;
}
G.save = save; G.readSave = readSave;

// ------------------------------------------------------------------ inventory + quests (used by data.js)
G.give = (id, n = 1) => { G.S.inv[id] = (G.S.inv[id] || 0) + n; drawBag(id); toast(`+${n} ${ITEMS[id].name}`); };
G.take = (id, n = 1) => { G.S.inv[id] = Math.max(0, (G.S.inv[id] || 0) - n); if (!G.S.inv[id]) delete G.S.inv[id]; drawBag(); };
G.setQuest = (id, stage) => {
  const was = G.S.quests[id]; G.S.quests[id] = stage; drawLog();
  if (stage === 3 && was !== 3) { toast(`Errand done: ${QUESTS[id].title}`, 2.6); G.audio.sfx('quest'); G.gainXP(PR.XP.errand); }
  else if (was === 0 && stage > 0) { toast(`New errand: ${QUESTS[id].title}`, 2.6); G.audio.sfx('pickup'); flashLog(); }
  refreshMarkers(); save();
};
G.learn = (spell) => {
  if (G.S.spells.includes(spell)) return;
  G.S.spells.push(spell);
  if (Array.isArray(G.S.slots)) { const i = G.S.slots.indexOf(null); if (i >= 0) G.S.slots[i] = spell; else if (G.S.slots.length < 4) G.S.slots.push(spell); }
  if (G.ctx) G.ctx.setSpellCycle(slots());
  toast(`Learned a charm: ${SPELL_NAMES[spell] || spell} (F to cast, Q to switch)`, 3.2);
};
G.catFollow = () => {
  G.S.cat = 'follow';
  const a = G.ctx.npc('cat'); if (a) { a.behavior = 'follow'; a.speed = 2.4; }
};
G.catHome = () => {
  G.S.cat = 'home';
  const a = G.ctx && G.ctx.npc('cat');
  if (a) { a.behavior = 'wander'; a.home = [4.8, 3.4]; a.radius = 1.4; a.speed = 1.4; a.target = null; a.wait = 2; }
};

// ------------------------------------------------------------------ HUD: bag, quest log, toast, prompt
const ICON = 32;   // 16 px icons drawn at 2x
const PXURL = {};
function iconHTML(id) {
  if (ITEMS[id].px) { const u = PXURL[id] || (PXURL[id] = goodIconURL(ITEMS[id].px)); return `<img class="ico" alt="" src="${u}">`; }
  const i = ITEMS[id].icon; return `<span class="ico" style="background-position:-${i * ICON}px 0"></span>`;
}
function drawBag(flash) {
  const el = $('bag'); if (!el) return;
  const ids = Object.keys(ITEMS).filter((k) => G.S.inv[k]);
  const nGear = (G.S.bag || []).length, gold = G.S.gold || 0;
  const gear = nGear || gold ? `<span class="gearchip" title="Gear in the bag (G)">⚔ ${nGear}</span><span class="goldchip" title="Gold">● ${gold}</span>` : '';
  el.innerHTML = ids.length || gear ? ids.map((k) => `<span class="slot${k === flash ? ' new' : ''}" data-item="${k}" title="${ITEMS[k].name}: ${ITEMS[k].about}">${iconHTML(k)}<b>${G.S.inv[k]}</b></span>`).join('') + gear
                            : '<span class="empty">bag: empty</span>';
  const tn = el.querySelector('[data-item="tonic"]'); if (tn) tn.onclick = (e) => { e.stopPropagation(); G.drinkTonic(); };   // tap the tonic to drink it
  const rail = $('rail');
  if (rail) rail.innerHTML = '';   // the bag chip (top left) is the one inventory display; the pad rail stays empty
}
function drawLog() {
  const el = $('logList'); if (!el) return;
  const rows = Object.entries(QUESTS).map(([id, q]) => {
    const st = G.S.quests[id];
    if (!st) return `<li class="todo"><b>${q.title}</b><span>Someone in town may need a hand… (${q.giver})</span></li>`;
    let step = q.steps[st] || '';
    if (id === 'tea' && st === 1) step += ` (${G.S.inv.moonpetal || 0}/3)`;
    return `<li class="${st === 3 ? 'done' : 'active'}"><b>${st === 3 ? '✓ ' : '◆ '}${q.title}</b><span>${step}</span></li>`;
  });
  el.innerHTML = rows.join('');
  const n = Object.values(G.S.quests).filter((v) => v === 3).length;
  $('logCount').textContent = `${n}/3 done`;
  $('btnLog').textContent = `quests ${n}/3`;
  const sp = $('logSpells');
  if (sp) sp.textContent = 'Spell slots: ' + slots().map((s) => spellName(s)).join(' · ') + '  ·  Charms known: ' + G.S.spells.map((s) => SPELL_NAMES[s] || s).join(' · ');
}
function spellBlurb(id) {
  const S = SPELLS[id];
  if (S) return `class spell · ${S.kind}${S.dmg ? ` · ${S.dmg} dmg` : ''}${S.heal ? ` · heals ${S.heal}` : ''} · ${S.cd}s`;
  const d = CHARM_DMG[id]; return `charm${d ? ` · ${d} dmg` : ' · no damage'} · ${CHARM_CD}s`;
}
function spellName(id) { return (SPELLS[id] && SPELLS[id].name) || SPELL_NAMES[id] || String(id).replace(/_/g, ' '); }
G.spellName = spellName;
function flashLog() { const b = $('btnLog'); b.classList.add('ping'); setTimeout(() => b.classList.remove('ping'), 1600); }
function setLog(open) { G.log = open; $('log').hidden = !open; $('btnLog').classList.toggle('on', open); if (open) drawLog(); }
let toastT = 0;
function toast(msg, s = 2.0, html = false) { const el = $('toast'); if (html) el.innerHTML = msg; else el.textContent = msg; el.hidden = false; el.classList.remove('out'); toastT = s; }
G.toast = toast;
G.say = (npc, page) => openDialogue(npc, { pages: Array.isArray(page) ? page : [page] });
G.itemName = (id) => (ITEMS[id] ? ITEMS[id].name : id);
G.drawBag = (f) => drawBag(f);
G.popText = (txt, at, col) => G.combat.number(txt, at.x, at.y + 0.9, at.z, col);

// ------------------------------------------------------------------ dialogue (carved-wood frame, parchment page)
let portraitImg = null;
function openDialogue(npc, entry) {
  G.dlg = { npc, pages: entry.pages, i: 0, then: entry.then, shown: 0, full: false, choice: entry.choice || null, ci: 0, picking: false };
  $('dlgName').textContent = npc.name || npc.role;
  drawPortrait(npc);
  $('dlg').hidden = false; document.body.classList.add('dlgopen');
  G.audio.sfx('blip');
  showPage();
}
function showPage() {
  const d = G.dlg; d.shown = 0; d.full = false;
  $('dlgText').textContent = ''; $('dlgChoices').hidden = true; d.picking = false;
  $('dlgMore').textContent = d.i < d.pages.length - 1 ? '▼' : '✕';
  $('dlgPage').textContent = `${d.i + 1}/${d.pages.length}`;
}
function advanceDialogue() {
  const d = G.dlg; if (!d) return;
  if (d.picking) { choicePick(d.ci); return; }   // E / Enter / A on a choice page picks the highlighted answer
  if (!d.full) { d.shown = 1e9; typeDialogue(0); return; }       // first press finishes the line
  if (d.i < d.pages.length - 1) { d.i++; G.audio.sfx('blip'); showPage(); return; }
  closeDialogue();
}
function closeDialogue() {
  if (G.dlg && G.dlg.picking) { choiceCancel(); return; }   // Esc / B on a choice page = the "not now" answer
  const d = G.dlg; G.dlg = null; $('dlg').hidden = true; document.body.classList.remove('dlgopen');
  if (d && d.then) d.then(G);
}
function typeDialogue(dt) {
  const d = G.dlg; if (!d || d.full) return;
  d.shown += dt * 55;
  const txt = d.pages[d.i];
  const n = Math.min(txt.length, Math.floor(d.shown));
  $('dlgText').textContent = txt.slice(0, n);
  if (n >= txt.length) { d.full = true; if (d.choice && d.i === d.pages.length - 1) showChoices(); }
}
// ---- dialogue choices: entry.choice = { options: [{ label, pick(G) -> next entry | null, cancel? }] } on the last page.
// A pick replaces the entry's own `then` (the option's reply entry carries its own). Keys: arrows / W S, 1-4, E / Enter;
// controller: d-pad, A, B (cancel); touch / mouse: tap a row. Esc / B picks the option marked cancel (or just closes).
function showChoices() {
  const d = G.dlg, box = $('dlgChoices'); d.picking = true; d.ci = Math.min(d.ci, d.choice.options.length - 1);
  box.innerHTML = d.choice.options.map((o, i) => `<button class="choice" data-i="${i}"><span class="k">${i + 1}</span><span>${o.label}</span></button>`).join('');
  box.hidden = false; $('dlgMore').textContent = ''; syncChoices();
}
function syncChoices() { const d = G.dlg; document.querySelectorAll('#dlgChoices .choice').forEach((b, i) => b.classList.toggle('sel', i === d.ci)); }
function choiceMove(dir) { const d = G.dlg; if (!d || !d.picking) return; const n = d.choice.options.length; d.ci = (d.ci + dir + n) % n; G.audio.sfx('blip'); syncChoices(); }
function choicePick(i) {
  const d = G.dlg; if (!d || !d.picking || !d.choice.options[i]) return;
  const o = d.choice.options[i]; d.picking = false; $('dlgChoices').hidden = true;
  G.S.flags = G.S.flags || {};
  (G.S.chose = G.S.chose || {})[d.choice.id || d.npc.id] = i;
  const next = o.pick ? o.pick(G) : null;
  if (next) openDialogue(d.npc, next); else { G.dlg = null; $('dlg').hidden = true; document.body.classList.remove('dlgopen'); }
  save();
}
function choiceCancel() { const d = G.dlg, k = d.choice.options.findIndex((o) => o.cancel); if (k >= 0) choicePick(k); else { d.picking = false; d.then = null; closeDialogue(); } }
G.dlgChoice = () => (G.dlg && G.dlg.picking ? { options: G.dlg.choice.options.map((o) => o.label), ci: G.dlg.ci } : null);
G.choicePick = (i) => choicePick(i);
function drawPortrait(npc) {
  const cv = $('dlgFace'), g = cv.getContext('2d');
  g.imageSmoothingEnabled = false; g.clearRect(0, 0, cv.width, cv.height);
  const r = npc.rect; if (!r || !portraitImg) return;
  const fw = r.w / r.k, fh = r.h / r.k;
  // the idle-down frame of this role row (column 0), cropped to the head and shoulders
  const fy = r.frame[1];
  const sh = Math.min(fh, 22), sy = fy + Math.max(0, fh - 34);
  const s = Math.floor(Math.min(cv.width / fw, cv.height / sh));
  g.drawImage(portraitImg, 0, sy, fw, sh, Math.round((cv.width - fw * s) / 2), cv.height - sh * s, fw * s, sh * s);
}

// ------------------------------------------------------------------ area manager
async function sceneOf(id) {
  if (!G.scenes[id]) G.scenes[id] = await (await fetch(AREAS[id] + 'scene.json')).json();
  return G.scenes[id];
}
async function loadArea(id, spawnKey, pos) {
  const sc = await sceneOf(id);
  const gm = sc.game || {};
  let sp = pos ? { x: pos[0], z: pos[1], facing: pos[2] } : null;
  if (!sp) { const s = (gm.spawns || {})[spawnKey] || (gm.spawns || {}).start; if (s) sp = { x: s[0], z: s[1], facing: s[2] }; }
  if (G.game) { G.game.dispose(); G.game = null; G.ctx = null; }
  G.markers = {};
  const old = $('view'); if (old) old.remove();
  const canvas = document.createElement('canvas'); canvas.id = 'view'; document.body.prepend(canvas);
  G.area = id; G.S.area = id; G.armed = false;
  G.combat.detach(); G.glow.detach(); G.hollows.detach(); G.garden.detach(); G.weather.detach(); G.loot.detach(); G.shopUI.detach();
  G.game = await boot({ base: AREAS[id], canvas, spawn: sp, startT: G.S.t, glowLights: glowCap(), clockSpeed: 1 / DAY_SECONDS, spellCycle: slots(),
                        player: { role: G.S.cls || G.preview || 'wildcaller' }, castAdvance: false,
                        keepTitle: true, padHandled: true, hooks, toast: (m, t) => toast(m, t) });
  const ctx = G.ctx = G.game.ctx;
  G.combat.attach(ctx, id); G.glow.attach(ctx, id); G.hollows.attach(ctx); G.garden.attach(ctx); G.weather.attach(ctx, id); G.loot.attach(ctx); G.shopUI.attach(ctx, id); PR.ensure(G.S); G.loot.restorePurse(id);
  // portrait source: this area's actor atlas
  portraitImg = new Image(); portraitImg.src = AREAS[id] + ctx.scene.atlas.image;
  // pickups already taken stay gone
  for (const pk of gm.pickups || []) if (G.S.picked[pk.fx] && ctx.fx[pk.fx]) { ctx.gamefx.remove(ctx.fx[pk.fx]); delete ctx.fx[pk.fx]; }
  applySwaps(ctx);
  // Pudding tags along between areas
  if (G.S.cat === 'follow' && !ctx.npc('cat')) {
    ctx.addNpc({ id: 'cat', role: 'cat', name: 'Pudding', pos: [ctx.player.x - 0.7, ctx.player.z + 0.5], behavior: 'follow', speed: 2.4, say: ['Mrrp!'] });
  } else if (G.S.cat === 'follow') { const a = ctx.npc('cat'); a.behavior = 'follow'; a.speed = 2.4; }
  G.audio.setArea(id);
  refreshMarkers();
  drawBag(); drawLog();
  document.title = `Hearthmoor · ${ctx.scene.name}`;
}
G.loadArea = loadArea;
// flag-driven fx swaps (game.swaps: [{ fx, flag, is, name }]): e.g. Vanaheim's poisoned spring water becomes the
// cleansed one once S.flags.vanaheim_spring === 'cleansed' (a later befriend quest sets it)
function applySwaps(ctx) {
  const F = G.S.flags || {};
  for (const sw of ctx.scene.game?.swaps || []) {
    const f = ctx.fx[sw.fx]; if (!f) continue;
    const want = F[sw.flag] === sw.is ? sw.name : (sw.base || f.name);
    if (f.name !== want) { ctx.gamefx.remove(f); ctx.fx[sw.fx] = ctx.gamefx.spawn(want, f.x, f.y, f.z, { duration: Infinity }); }
  }
}
G.applySwaps = () => G.ctx && applySwaps(G.ctx);

// ---- the Rainbow Rift (Stage 4): the Plaza's moss gate also opens on the Rift Shrine once the three errands are done
// (or S.flags.rift, or ?rift for QA). Stepping in then asks where to go with the dialogue choice panel.
function riftOpen() {
  const S = G.S; return Q.has('rift') || !!(S.flags && S.flags.rift) || Object.values(S.quests || {}).filter((v) => v === 3).length >= 3;
}
G.riftOpen = riftOpen;
function gateChoice(po) {
  const opts = po.choose.map((c) => ({ label: c.label, pick: () => { go(c.to, c.spawn, 'portal'); return null; } }));
  opts.push({ label: 'Stay here.', cancel: true, pick: () => null });
  openDialogue({ id: 'moss_gate', name: po.gate_name || 'The moss gate' },
    { pages: [po.ask || 'The swirl hums with two pulls. Where do you step?'], choice: { id: 'moss_gate', options: opts } });
}
// sealed realm gates (Rift Shrine): a prompt nearby, and E / A shows why it will not open
function sealedNear(ctx) {
  const p = ctx.player; return (ctx.scene.game?.sealed || []).find((g) => Math.abs(p.x - g.pos[0]) < 1.3 && p.z > g.pos[1] && p.z < g.pos[1] + 2.0) || null;
}
const SEAL_SAY = {
  violet: 'Violet light pulses behind the stone, slow as a sleeping heart. Frost rimes the seal from the other side: someone froze it shut.',
  blue: 'Cold-fire flickers blue under a skin of ice. The seal breathes mist, and the mist smells of Niflheim snow.',
  red: 'A red glow beats behind the seal like embers under ash. It is warm to the touch, and locked tight.',
};
function sealedLook(ctx) {
  const g = sealedNear(ctx); if (!g) return false;
  openDialogue({ id: 'sealed_' + g.realm.toLowerCase(), name: `${g.realm}'s gate (sealed)` }, { pages: [SEAL_SAY[g.hue] || 'The gate is sealed.', 'It will not open yet. Bifrost Crossing has keys for gates like this, they say.'] });
  return true;
}

async function go(to, spawnKey, how) {
  if (G.busy) return; G.busy = true;
  const f = $('fade'); f.className = how === 'portal' ? 'portal on' : 'on';
  if (how === 'portal') { G.audio.sfx('portal'); const p = G.ctx.player; G.ctx.effects && G.ctx.effects.spawn('sparkle_burst', p.x, p.y, p.z); }
  await new Promise((r) => setTimeout(r, how === 'portal' ? 620 : 380));
  G.S.pos = null;
  try { await loadArea(to, spawnKey); } catch (e) { console.error(e); }
  save();
  f.className = how === 'portal' ? 'portal' : '';
  await new Promise((r) => setTimeout(r, 360));
  G.busy = false;
  toast(G.ctx.scene.name, 1.6);
}
G.go = go;

// ------------------------------------------------------------------ quest tags over heads
function refreshMarkers() {
  const ctx = G.ctx; if (!ctx || !ctx.gamefx) return;
  for (const a of ctx.actors.list) {
    if (a.id === 'player') continue;
    const want = markerFor(a.id, G.S);
    const have = G.markers[a.id];
    if (have && have.name !== want) { ctx.gamefx.remove(have); delete G.markers[a.id]; }
    if (want && !G.markers[a.id]) G.markers[a.id] = ctx.gamefx.spawn(want, a.x, a.y, a.z, { duration: Infinity });
  }
}
function syncMarkers() {
  for (const [id, f] of Object.entries(G.markers)) { const a = G.ctx.npc(id); if (a) { f.x = a.x; f.y = a.y; f.z = a.z; } }
}

// ------------------------------------------------------------------ per-frame game logic
const inRect = (p, r) => p.x >= r[0] && p.x <= r[2] && p.z >= r[1] && p.z <= r[3];
function nearPickup(ctx, d = 0.85) {
  for (const pk of ctx.scene.game?.pickups || []) {
    const f = ctx.fx[pk.fx]; if (!f || G.S.picked[pk.fx]) continue;
    if (Math.hypot(f.x - ctx.player.x, f.z - ctx.player.z) < d) return pk;
  }
  return null;
}
function pick(ctx, pk) {
  const f = ctx.fx[pk.fx];
  G.S.picked[pk.fx] = true;
  ctx.gamefx.remove(f); delete ctx.fx[pk.fx];
  ctx.effects && ctx.effects.spawn('sparkle_burst', f.x, f.y, f.z);
  G.give(pk.item, 1);
  G.audio.sfx('pickup');
  if (G.S.quests.tea === 1 && (G.S.inv.moonpetal || 0) >= 3) G.setQuest('tea', 2); else { drawLog(); save(); }
}
function onFrame(dt, ctx) {
  const p = ctx.player, gm = ctx.scene.game || {};
  G.S.t = ctx.clock.t;
  G.S.played += dt;
  typeDialogue(dt);
  if (toastT > 0) { toastT -= dt; const el = $('toast'); if (toastT <= 0.35) el.classList.add('out'); if (toastT <= 0) { el.hidden = true; el.classList.remove('out'); } }
  syncMarkers();
  padWheel();
  G.hollows.update(dt); G.garden.update(dt); G.glow.update(dt); G.weather.update(dt);
  G.loot.update(dt); G.shopUI.update(dt);
  G.combat.update(dt, ctx);
  drawVitals(ctx);
  if (G.title || G.busy) return;
  // exits + portals: arm once the player has stood outside every trigger (no bounce on arrival)
  const trig = [...(gm.exits || []).map((e) => ({ ...e, how: 'walk' })), ...(gm.portals || []).map((e) => ({ ...e, how: 'portal' }))];
  const inside = trig.find((e) => inRect(p, e.rect));
  if (!inside) G.armed = true;
  else if (G.armed && !G.dlg) {
    if (inside.choose && riftOpen()) { G.armed = false; gateChoice(inside); return; }   // the moss gate: Mossglen or the Rift
    go(inside.to, inside.spawn, inside.how); return;
  }
  // pickups: walk over a glimmer
  const pk = nearPickup(ctx, 0.7); if (pk) pick(ctx, pk);
  // prompt near a gate or a glimmer
  let prompt = '';
  const close = trig.find((e) => Math.max(e.rect[0] - p.x, p.x - e.rect[2], e.rect[1] - p.z, p.z - e.rect[3]) < 1.6);
  if (close) prompt = close.how === 'portal' ? `step into the swirl: ${close.choose && riftOpen() ? close.label_rift || close.label : close.label}` : close.label;
  else { const sg = sealedNear(ctx); if (sg) prompt = `${sg.realm}'s gate is sealed (E / A to look)`; }
  const pe = $('prompt'); if (pe.textContent !== prompt) { pe.textContent = prompt; pe.hidden = !prompt; }
  G.audio.setNight(ctx.clock.grade ? (ctx.clock.grade().bugs ?? 0) : 0);
  G.autosave -= dt; if (G.autosave <= 0) { G.autosave = 20; save(); }
}

// ------------------------------------------------------------------ vitals + touch-button cooldowns (cheap DOM writes)
const last = {};
function setTxt(id, v) { if (last[id] !== v) { last[id] = v; const el = $(id); if (el) el.textContent = v; } }
function setW(id, f) { const v = Math.round(Math.max(0, Math.min(1, f)) * 100); if (last[id] !== v) { last[id] = v; const el = $(id); if (el) el.style.width = v + '%'; } }
function setCd(id, sec) { const v = sec > 0.05 ? String(Math.ceil(sec)) : ''; if (last[id] !== v) { last[id] = v; const el = $(id); if (el) { if (v) el.dataset.cd = v; else delete el.dataset.cd; } } }
function drawVitals(ctx) {
  const C = G.combat, hp = G.S.hp ?? C.maxHp(), max = C.maxHp();
  setW('hpFill', hp / max); setW('stFill', C.st / C.maxSt());
  const S = G.S; if (S.lv) { setW('xpFill', S.lv >= PR.LEVEL_CAP ? 1 : S.xp / PR.xpNeed(S.lv)); setTxt('lvTxt', 'Lv' + S.lv); setTxt('ptsTxt', (S.free || S.sp) ? `+${S.free + S.sp}` : ''); }
  setTxt('hpTxt', `${Math.ceil(hp)}`);
  const cur = ctx.spellCycle()[ctx.spellIndex()] || '';
  const cd = SPELLS[cur] ? C.cd.spell : C.cd.charm;
  setTxt('spellTxt', '✦ ' + spellName(cur) + (cd > 0.05 ? ` ${cd.toFixed(1)}` : ''));
  setTxt('padSpellName', (spellName(cur).split(' ')[0] || 'spell').slice(0, 7).toLowerCase());
  setCd('padSpell', cd); setCd('padSummon', C.cd.summon);
  const v = $('vitals'), bag = $('bag');
  if (v && bag) {   // sit just under the bag, whatever its height (icons make it taller than the empty chip)
    const top = bag.offsetTop + bag.offsetHeight + 4;
    if (last.vtop !== top) { last.vtop = top; v.style.top = top + 'px'; }
  }
  if (v) { const low = hp / max < 0.3; if (last.low !== low) { last.low = low; v.classList.toggle('low', low); } }
  const near = $('mainGlyph') && $('mainGlyph').textContent === '💬';
  if (last.talk !== near) { last.talk = near; $('padMain').classList.toggle('talk', near); }
}

const hooks = {
  blockInput: () => !!(G.dlg || G.busy || G.title || G.log || G.downed || G.opts || G.picking || G.heroUI || G.shop || G.asking || WHEEL.open || G.hollows.busy()),
  rollMods: () => { const M = G.combat.M; return { speed: M.rollSpeed, iframes: M.rollIframes }; },
  onCast: (name) => {
    const C = G.combat, s0 = C.cd.spell || 0, c0 = C.cd.charm || 0, ok = C.cast(name);
    // a cast really happened when its cooldown just started (spells return false so the engine skips its own fx)
    if ((C.cd.spell || 0) > s0 || (C.cd.charm || 0) > c0) G.hollows.onCast();
    return ok;
  },
  onSummon: () => G.combat.doSummon(),
  onDodge: () => G.combat.onDodge(),
  onAct: (name) => { if (name === 'jump') G.hollows.onJump(); G.combat.onAct(name); },
  skipActor: (spec) => spec.id === 'cat' && ((G.area === 'plaza' && G.S.cat !== 'home') || (G.area === 'mossglen' && G.S.cat !== 'glade')),
  onInteract: (ctx, kind) => {
    if (G.title) return true;
    if (G.dlg) { advanceDialogue(); return true; }
    if (G.log) { setLog(false); return true; }
    if (G.busy) return true;
    if (kind !== 'tap' && G.hollows.interact()) return true;   // gnome doors
    if (kind !== 'tap' && sealedLook(ctx)) return true;        // sealed Rift gates
    if (kind !== 'tap' && G.garden.interact()) return true;    // glow-garden plots: plant / check / harvest
    return false;
  },
  onTalk: (npc, ctx) => {
    const fn = TALK[npc.id];
    const entry = fn ? fn(G.S) : { pages: (Array.isArray(npc.say) ? npc.say : [npc.say || '…']) };
    openDialogue(npc, entry);
    return true;
  },
  onTap: (hit, ctx) => {
    // tapping a glimmer walks onto it; tapping the swirl walks into the gate
    for (const pk of ctx.scene.game?.pickups || []) {
      const f = ctx.fx[pk.fx]; if (!f) continue;
      if (Math.hypot(f.x - hit.x, f.z - hit.z) < 1.0) { ctx.walkTo(f.x, f.z); return true; }
    }
    for (const po of ctx.scene.game?.portals || []) {
      const f = ctx.fx[po.fx]; if (!f) continue;
      if (Math.abs(f.x - hit.x) < 1.2 && hit.z > f.z - 1.2 && hit.z < f.z + 2.0) { ctx.walkTo(f.x, (po.rect[1] + po.rect[3]) / 2); return true; }
    }
    for (const g of ctx.scene.game?.sealed || []) {   // tapping a sealed gate walks up to it; tapping it again up close looks
      if (Math.abs(g.pos[0] - hit.x) < 1.3 && hit.z > g.pos[1] - 1.2 && hit.z < g.pos[1] + 2.0) {
        if (sealedNear(ctx)) sealedLook(ctx); else ctx.walkTo(g.pos[0], g.pos[1] + 1.2);
        return true;
      }
    }
    return false;
  },
  // controller buttons (standard mapping) before the engine defaults: title, dialogue, quest log, Start = log
  onPad: (name, ctx) => {
    if (G.picking) {
      if (name === 'left' || name === 'lb') pickMove(-1); else if (name === 'right' || name === 'rb') pickMove(1);
      else if (name === 'up') pickMove(-3); else if (name === 'down') pickMove(3);
      else if (name === 'a' || name === 'start') pickBegin(); else if (name === 'b') closePicker();
      else if (name === 'y' || name === 'x') pickMode();
      return true;
    }
    if (G.title) {
      if (name === 'a' || name === 'start') (readSave() ? cont : newGame)();
      else if (name === 'x') newGame();
      else if (name === 'left' || name === 'lb') slotMove(-1); else if (name === 'right' || name === 'rb') slotMove(1);
      else if (name === 'y') slotCopy(); else if (name === 'rt') slotDelete();
      return true;
    }
    if (G.asking) { if (name === 'left' || name === 'right' || name === 'up' || name === 'down') askMove(); else if (name === 'a') askPick(ASK.yes); else if (name === 'b') askPick(false); return true; }
    if (G.heroUI) { heroPad(name); return true; }
    if (G.shop) { G.shopUI.pad(name); return true; }
    if (G.opts) { if (name === 'y') cycleWeather(); else if (name === 'b' || name === 'start' || name === 'a') setOpts(false); return true; }
    if (G.busy || G.downed) return true;
    if (G.dlg && G.dlg.picking) { if (name === 'up') choiceMove(-1); else if (name === 'down') choiceMove(1); else if (name === 'a') choicePick(G.dlg.ci); else if (name === 'b') choiceCancel(); return true; }
    if (G.dlg) { if (name === 'a') advanceDialogue(); else if (name === 'b') closeDialogue(); return name !== 'select'; }
    if (G.log) { if (name === 'y' || name === 'rb' || name === 'lb') { setLog(false); setHeroUI(true); return true; } if (name === 'a' || name === 'b' || name === 'start') setLog(false); return name !== 'select'; }
    if (name === 'start') { setLog(true); return true; }
    if (name === 'rs') { G.drinkTonic(); return true; }   // right-stick click drinks a tonic
    if (name === 'y') { PADW.t = performance.now(); PADW.f = (window.__hd2d && window.__hd2d.frames) || 0; PADW.on = true; PADW.fired = false; return true; }   // tap casts, hold opens the wheel
    return false;
  },
  onPadRelease: (name) => {
    if (name !== 'y' || !PADW.on) return false;
    PADW.on = false;
    if (PADW.fired) closeWheel(true); else if (G.ctx && !hooks.blockInput()) G.ctx.playerCast();
    return true;
  },
  onFrame,
  nearThing: (ctx) => !!nearPickup(ctx, 1.4) || G.hollows.nearThing(ctx) || G.garden.nearThing(ctx) || !!sealedNear(ctx),
};

// ------------------------------------------------------------------ touch action buttons + slow-time spell wheel
function press(id, down, up) {
  const el = $(id); if (!el) return;
  el.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); try { el.setPointerCapture(e.pointerId); } catch (err) { /* synthetic */ } down(e); });
  if (up) for (const t of ['pointerup', 'pointercancel', 'lostpointercapture']) el.addEventListener(t, (e) => up(e));
}
const WHEEL = { open: false, x0: 0, y0: 0, sel: -1, timer: null };
// controller: hold Y for 0.35 s -> the same slow-time wheel; the left stick (or d-pad) picks, letting go of Y casts
const PADW = { on: false, t: 0, f: 0, fired: false };   // f = drawn-frame count at the press (a frame hitch must not turn a tap into a hold)
function padWheel() {
  if (!PADW.on) return;
  if (!PADW.fired) {
    if (performance.now() - PADW.t < 350 || ((window.__hd2d && window.__hd2d.frames) || 0) - PADW.f < 3) return;
    if (hooks.blockInput()) { PADW.on = false; return; }
    PADW.fired = true; openWheel(innerWidth / 2, innerHeight / 2);
    return;
  }
  if (!WHEEL.open) return;
  let st = { x: 0, y: 0, mag: 0 };
  try {
    for (const gp of navigator.getGamepads ? navigator.getGamepads() : []) {
      if (!gp) continue;
      let x = gp.axes[0] || 0, y = gp.axes[1] || 0;
      const b = (i) => gp.buttons[i] && (gp.buttons[i].pressed || gp.buttons[i].value > 0.5);
      if (Math.hypot(x, y) < 0.35) { x = (b(15) ? 1 : 0) - (b(14) ? 1 : 0); y = (b(13) ? 1 : 0) - (b(12) ? 1 : 0); }
      if (Math.hypot(x, y) > st.mag) st = { x, y, mag: Math.hypot(x, y) };
    }
  } catch (e) { /* no gamepad access */ }
  if (st.mag > 0.4) moveWheel(WHEEL.x0 + st.x / st.mag * 60, WHEEL.y0 + st.y / st.mag * 60);
}
G.padWheel = PADW;
function openWheel(x, y) {
  const ctx = G.ctx; if (!ctx || hooks.blockInput()) return;
  WHEEL.open = true; WHEEL.x0 = x; WHEEL.y0 = y; WHEEL.sel = -1;
  const cyc = ctx.spellCycle(), cur = ctx.spellIndex();
  document.querySelectorAll('#wheel .slot').forEach((el, i) => { el.textContent = cyc[i] ? spellName(cyc[i]) : ''; el.classList.toggle('cur', i === cur); el.classList.remove('on'); });
  $('wheel').hidden = false;
  ctx.setTimeScale(0.2);
}
function moveWheel(x, y) {
  if (!WHEEL.open) return;
  const dx = x - WHEEL.x0, dy = y - WHEEL.y0, n = G.ctx.spellCycle().length;
  let sel = -1;
  if (Math.hypot(dx, dy) > 22) sel = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 1 : 3) : (dy > 0 ? 2 : 0);
  if (sel >= n) sel = -1;
  WHEEL.sel = sel;
  document.querySelectorAll('#wheel .slot').forEach((el, i) => el.classList.toggle('on', i === sel));
}
function closeWheel(cast) {
  if (!WHEEL.open) return;
  WHEEL.open = false; $('wheel').hidden = true;
  const ctx = G.ctx; if (!ctx) return;
  ctx.setTimeScale(1);
  if (cast && WHEEL.sel >= 0) { ctx.selectSpell(WHEEL.sel); ctx.playerCast(); }
}
G.wheel = { open: openWheel, move: moveWheel, close: closeWheel, state: () => ({ ...WHEEL, timer: undefined }) };
function wirePad() {
  const C = () => G.ctx;
  press('padGuard', () => { if (C()) { C().act('defend', null, { hold: true }); $('padGuard').classList.add('on'); } },
                    () => { if (C()) C().release('defend'); $('padGuard').classList.remove('on'); });
  press('padJump', () => C() && C().act('jump'));
  press('padDodge', () => C() && C().dodge());
  press('padSummon', () => C() && C().summon());
  const sp = $('padSpell');
  press('padSpell', (e) => {
    clearTimeout(WHEEL.timer);
    const x = e.clientX, y = e.clientY;
    WHEEL.timer = setTimeout(() => { WHEEL.timer = 'fired'; openWheel(x, y); }, 350);
  }, (e) => {
    if (e.type === 'lostpointercapture' && !WHEEL.open && WHEEL.timer === null) return;
    if (WHEEL.timer === 'fired') { WHEEL.timer = null; closeWheel(e.type === 'pointerup'); return; }
    if (WHEEL.timer) { clearTimeout(WHEEL.timer); WHEEL.timer = null; if (e.type === 'pointerup' && C()) C().playerCast(); }
  });
  sp.addEventListener('pointermove', (e) => moveWheel(e.clientX, e.clientY));
  press('pad3rd', () => setLog(!G.log));
}

// ------------------------------------------------------------------ options: display presets, fullscreen, install
const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
const standalone = () => matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches || navigator.standalone === true;
const canFull = () => !!(document.documentElement.requestFullscreen || document.documentElement.webkitRequestFullscreen) && !isIOS;
function syncInstall() {
  const show = !standalone();
  for (const id of ['btnInstall', 'btnInstallT']) { const b = $(id); if (b) b.hidden = !show; }
}
function doInstall(tipId) {
  const tip = $(tipId);
  if (installEvt) { installEvt.prompt(); installEvt.userChoice.finally(() => { installEvt = null; syncInstall(); }); return; }
  const msg = isIOS ? 'iPhone / iPad: tap the Share button (□↑) in Safari, then "Add to Home Screen". Hearthmoor then opens full screen and works offline.'
                    : 'Use your browser menu: "Install app" or "Add to Home screen". Hearthmoor then works offline.';
  if (tip) { tip.textContent = msg; tip.hidden = false; }
}
function toggleFull() {
  const d = document, el = d.documentElement;
  if (d.fullscreenElement || d.webkitFullscreenElement) { (d.exitFullscreen || d.webkitExitFullscreen).call(d); return; }
  const p = (el.requestFullscreen || el.webkitRequestFullscreen).call(el, { navigationUI: 'hide' });
  if (p && p.then) p.then(() => { try { screen.orientation.lock('landscape').catch(() => {}); } catch (e) { /* not supported */ } }).catch(() => {});
}
function syncDisplay() {
  const p = getDisplay();
  document.querySelectorAll('#displayRow [data-p]').forEach((b) => b.classList.toggle('on', b.dataset.p === p));
  const t = $('btnDisplayT'); if (t) t.textContent = 'Display: ' + DISPLAY_PRESETS[p].label;
}
function setOpts(open) {
  G.opts = open; $('opts').hidden = !open; $('btnOpts').classList.toggle('on', open); syncAutoBtn(); syncModeBtn();
  if (open) { syncDisplay(); syncInstall(); $('btnFull').hidden = !canFull(); }
}
G.setOpts = setOpts;
// extra glow lights (pooled point lights for spell pools, drops, lanterns): 3, or 2 on phones (lighter on the GPU).
// Saved per device (not in the save slot); ?glow=2 / ?glow=3 overrides; changing it re-opens the area in place.
const GLOW_KEY = 'hearthmoor-glowlights';
function glowCap() {
  const q = +Q.get('glow'); if (q === 2 || q === 3) return q;
  const s = +localStorage.getItem(GLOW_KEY); if (s === 2 || s === 3) return s;
  return matchMedia('(pointer: coarse)').matches ? 2 : 3;
}
G.glowCap = glowCap;
function syncGlowBtn() { const b = $('btnGlow'); if (b) b.textContent = `glow lights: ${glowCap()}${glowCap() === 2 ? ' (phone)' : ''}`; }
async function toggleGlow() {
  localStorage.setItem(GLOW_KEY, String(glowCap() === 3 ? 2 : 3)); syncGlowBtn();
  if (G.ctx && !G.title) { const p = G.ctx.player; save(); await loadArea(G.area, null, [p.x, p.z, p.facing]); }
  toast(`Glow lights: ${glowCap()}`, 1.6);
}
// weather: on / light (default on phones: half the drops, mist and glints) / off; saved per device, not per slot
function syncWeatherBtn() { const b = $('btnWeather'), m = G.weather.mode; if (b) b.textContent = `weather: ${m}${m === 'light' ? ' (phone)' : ''}`; }
function cycleWeather() { const m = G.weather.cycle(); syncWeatherBtn(); toast(`Weather: ${m}`, 1.4); return m; }
G.cycleWeather = cycleWeather;
function wireOptions() {
  $('btnGlow').onclick = () => toggleGlow(); syncGlowBtn();
  $('btnWeather').onclick = () => cycleWeather(); syncWeatherBtn();
  $('btnOpts').onclick = () => setOpts(!G.opts);
  $('optsClose').onclick = () => setOpts(false);
  $('opts').addEventListener('pointerdown', (e) => { if (e.target === $('opts')) setOpts(false); });
  document.querySelectorAll('#displayRow [data-p]').forEach((b) => { b.onclick = () => { setDisplay(b.dataset.p); syncDisplay(); }; });
  const order = Object.keys(DISPLAY_PRESETS);
  $('btnDisplayT').onclick = () => { setDisplay(order[(order.indexOf(getDisplay()) + 1) % order.length]); syncDisplay(); };
  $('btnFull').onclick = toggleFull; $('btnFullT').onclick = toggleFull;
  $('btnFullT').hidden = !canFull();
  $('btnInstall').onclick = () => doInstall('installTip'); $('btnInstallT').onclick = () => doInstall('installTipT');
  syncInstall(); syncDisplay();
  // rotate prompt: portrait phones only, dismissible, never blocks play (hidden for QA captures)
  const portrait = matchMedia('(orientation: portrait) and (pointer: coarse)');
  let dismissed = false;
  const rot = () => { const show = portrait.matches && !dismissed && !QA && !Q.has('norotate'); $('rotate').hidden = !show; };
  $('rotateX').onclick = () => { dismissed = true; rot(); };
  $('rotate').addEventListener('pointerdown', (e) => { e.stopPropagation(); });
  portrait.addEventListener ? portrait.addEventListener('change', rot) : portrait.addListener(rot);
  rot();
  setTimeout(() => { dismissed = true; rot(); }, 9000);
}

// ------------------------------------------------------------------ hero picker (title -> New game, or a v1 save on Continue)
const PICK = { i: 0, meta: null, img: null, raf: 0, then: null, t0: 0 };
async function heroAtlas() {
  if (PICK.meta) return;
  const base = AREAS.plaza + 'public/art/sprite/';
  PICK.meta = await (await fetch(base + 'actors.json')).json();
  PICK.img = await new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = base + 'actors.png'; });
}
function buildCards() {
  const wrap = $('cards'); wrap.innerHTML = '';
  HEROES.forEach((h, i) => {
    const b = document.createElement('button');
    b.className = 'card'; b.dataset.i = i; b.id = 'hero_' + h.id;
    b.innerHTML = `<canvas width="20" height="32"></canvas><b>${h.cls}</b><i>${h.kind}</i>`;
    b.onclick = () => { if (PICK.i === i && PICK.tapped) pickBegin(); else { PICK.i = i; PICK.tapped = true; pickShow(); } };
    wrap.appendChild(b);
  });
}
function pickShow() {
  const h = HEROES[PICK.i];
  document.querySelectorAll('#cards .card').forEach((c, i) => c.classList.toggle('sel', i === PICK.i));
  $('heroDetail').innerHTML = `<b>${h.cls}</b> <span class="tag">${h.origin}</span><span class="tag ${h.kind}">${h.kind}</span><span class="tag">${h.style}</span><br>${h.blurb}`
    + `<span class="kit">First spell: ${SPELLS[h.spell].name} · Summon: ${SUMMONS[h.summon].name} · ${h.hp} HP</span>`;
  G.preview = h.id;
  if (G.ctx && G.ctx.actors.meta.roles[h.id]) { G.ctx.actors.setRole(G.ctx.player, h.id); G.ctx.actors.act(G.ctx.player, 'attack'); }
  PICK.t0 = performance.now();
}
function drawPreviews(now) {
  if (!G.picking) return;
  const M = PICK.meta, fw = M.frame[0], fh = M.frame[1];
  document.querySelectorAll('#cards .card').forEach((c, i) => {
    const h = HEROES[i], r = M.roles[h.id]; if (!r) return;
    const cv = c.querySelector('canvas'), g = cv.getContext('2d');
    g.imageSmoothingEnabled = false; g.clearRect(0, 0, fw, fh);
    let anim = 'idle', fr = Math.floor(now / 330) % 4;
    if (i === PICK.i) {   // the chosen hero shows off: attack, cast, jump, idle
      const seq = ['attack', 'cast', 'jump', 'idle'], ph = Math.floor((now - PICK.t0) / 900) % 4;
      anim = seq[ph]; if (!r.anims.includes(anim)) anim = 'idle';
      fr = Math.min(3, Math.floor(((now - PICK.t0) % 900) / 180));
    }
    const col = M.anims[anim].start + fr;
    g.drawImage(PICK.img, col * fw, r.row * fh, fw, fh, 0, 0, fw, fh);
  });
  PICK.raf = requestAnimationFrame(drawPreviews);
}
async function openPicker(then) {
  try { await heroAtlas(); } catch (e) { console.error(e); }
  PICK.then = then; PICK.tapped = false;
  const cur = HEROES.findIndex((h) => h.id === (G.S.cls || G.preview));
  PICK.i = cur >= 0 ? cur : 0;
  G.picking = true;
  $('plaque').hidden = true; $('picker').hidden = false;
  if (!$('cards').children.length) buildCards();
  pickShow(); syncPickMode();
  cancelAnimationFrame(PICK.raf); PICK.raf = requestAnimationFrame(drawPreviews);
}
function closePicker() {
  G.picking = false; cancelAnimationFrame(PICK.raf);
  $('picker').hidden = true; $('plaque').hidden = false;
}
// difficulty is chosen with the hero (Story / Adventurer / Hero); options can change it later
function pickMode(d = 1) {
  const i = PR.MODE_IDS.indexOf(PICK.mode || 'adventurer');
  PICK.mode = PR.MODE_IDS[(i + d + 3) % 3]; syncPickMode();
}
function syncPickMode() {
  PICK.mode = PICK.mode || (PR.MODES[Q.get('mode')] ? Q.get('mode') : 'adventurer');
  if ($('btnPickMode')) $('btnPickMode').textContent = 'mode: ' + PR.MODES[PICK.mode].name;
  if ($('pickModeTip')) $('pickModeTip').textContent = MODE_TIP[PICK.mode];
}
G.pickMode = pickMode;
function pickMove(d) { PICK.i = (PICK.i + d + HEROES.length * 3) % HEROES.length; PICK.tapped = false; pickShow(); }
function pickBegin() {
  const id = HEROES[PICK.i].id, then = PICK.then;
  closePicker();
  if (then) then(id);
}
G.picker = { open: openPicker, move: pickMove, begin: pickBegin, close: closePicker, mode: pickMode, state: () => ({ open: G.picking, i: PICK.i, id: HEROES[PICK.i].id, mode: PICK.mode }) };

// ------------------------------------------------------------------ title screen, buttons, keys
function wire() {
  $('btnLog').onclick = () => setLog(!G.log);
  $('logClose').onclick = () => setLog(false);
  $('btnSave').onclick = () => save(true);
  $('btnSound').onclick = () => { G.audio.start(); const m = G.audio.toggle(); $('btnSound').textContent = m ? 'sound: off' : 'sound: on'; };
  $('btnSound').textContent = G.audio.muted ? 'sound: off' : 'sound: on';
  $('dlg').addEventListener('pointerdown', (e) => {
    e.preventDefault();
    const row = e.target.closest && e.target.closest('#dlgChoices .choice');
    if (G.dlg && G.dlg.picking) { if (row) choicePick(+row.dataset.i); return; }
    advanceDialogue();
  });
  wirePad(); wireOptions(); wireLeveling(); G.shopUI.wire();
  $('btnBack').onclick = () => closePicker();
  $('btnBegin').onclick = () => pickBegin();
  $('btnPickMode').onclick = () => pickMode();
  addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (G.picking || G.title) e.stopImmediatePropagation();   // the engine's own keys (talk on Enter) wait for the field
    if (G.dlg && G.dlg.picking) {   // choice page: arrows / W S move, 1-4 pick (E / Enter / Esc go through the usual dialogue keys)
      const n = '1234'.indexOf(k);
      if (k === 'arrowup' || k === 'w') { choiceMove(-1); e.preventDefault(); e.stopImmediatePropagation(); return; }
      if (k === 'arrowdown' || k === 's') { choiceMove(1); e.preventDefault(); e.stopImmediatePropagation(); return; }
      if (n >= 0) { choicePick(n); e.stopImmediatePropagation(); return; }
    }
    if (G.picking) {
      if (k === 'arrowleft' || k === 'a') pickMove(-1); else if (k === 'arrowright' || k === 'd') pickMove(1);
      else if (k === 'arrowup' || k === 'w') pickMove(-3); else if (k === 'arrowdown' || k === 's') pickMove(3);
      else if (k === 'enter' || k === ' ') { e.preventDefault(); pickBegin(); } else if (k === 'escape') closePicker();
      else if (k === 'm') pickMode();
      return;
    }
    if (G.title) {
      if (k === 'enter' || k === ' ') { e.preventDefault(); (readSave() ? cont : newGame)(); } else if (k === 'n') newGame();
      else if (k === 'arrowleft' || k === 'a') slotMove(-1); else if (k === 'arrowright' || k === 'd') slotMove(1);
      else if (k === '1' || k === '2' || k === '3') slotPick(+k);
      else if (k === 'c') slotCopy(); else if (k === 'delete' || k === 'backspace') { e.preventDefault(); slotDelete(); }
      return;
    }
    if (G.asking) { if (k === 'y') askPick(true); else if (k === 'n' || k === 'escape') askPick(false); else if (k.startsWith('arrow') || k === 'a' || k === 'd') askMove(); else if (k === 'enter' || k === ' ') { e.preventDefault(); askPick(ASK.yes); } e.stopImmediatePropagation(); return; }
    if (G.heroUI) { e.stopImmediatePropagation(); heroKey(k, e); return; }
    if (G.shop) { e.stopImmediatePropagation(); G.shopUI.key(k, e); return; }
    if (k === 'u' && !hooks.blockInput()) { G.drinkTonic(); return; }
    if (k === 'i') { setHeroUI(true); return; }
    if (k === 'b') { HUI.tab = 2; HUI.i = 0; setHeroUI(true); return; }   // spellbook
    if (k === 'g') { HUI.tab = 3; HUI.i = 0; setHeroUI(true); return; }   // gear + bag
    if (k === 'o') { setOpts(!G.opts); return; }
    if (k === 'r' && G.opts) { cycleWeather(); return; }   // R in Options: weather on / light / off
    if (k === 'j' || k === 'l') setLog(!G.log);
    if (k === 'escape') { if (G.opts) setOpts(false); else if (G.dlg) closeDialogue(); else if (G.log) setLog(false); }
    if (k === 'k' || ((e.ctrlKey || e.metaKey) && k === 's')) { e.preventDefault(); save(true); }
    if (k === 'm') { G.audio.start(); const m = G.audio.toggle(); $('btnSound').textContent = m ? 'sound: off' : 'sound: on'; }
  });
  addEventListener('pointerdown', () => G.audio.start(), { once: true });
  addEventListener('keydown', () => G.audio.start(), { once: true });
  addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') save(); });
  addEventListener('pagehide', () => save());
  $('btnNew').onclick = () => newGame();
  $('btnCont').onclick = () => cont();
  $('btnCopy').onclick = () => slotCopy();
  $('btnDel').onclick = () => slotDelete();
}
// ------------------------------------------------------------------ save slots on the title (3 cards: pixel hero, level, area, play time)
const AREA_NAME = { plaza: 'Hearthmoor Plaza', lane: 'Bakery Lane', mossglen: 'Mossglen', hollows: 'Toadstool Hollows' };
const HERO_ATLAS = 'areas/plaza/public/art/sprite/';   // the plaza sheet carries all six heroes
let heroSheet = null, heroMeta = null;
function loadHeroSheet() {
  if (heroSheet) return;
  heroSheet = new Image(); heroSheet.onload = () => syncSlots(); heroSheet.src = HERO_ATLAS + 'actors.png';
  fetch(HERO_ATLAS + 'actors.json').then((r) => r.json()).then((m) => { heroMeta = m; syncSlots(); }).catch(() => {});
}
function heroIcon(cv, cls) {
  const g = cv.getContext('2d'); g.imageSmoothingEnabled = false; g.clearRect(0, 0, cv.width, cv.height);
  const r = heroMeta && heroMeta.roles[cls]; if (!r || !heroSheet || !heroSheet.complete || !heroSheet.naturalWidth) return false;
  const f = r.frames.find((q) => q.facing === 'down' && q.anim === 'idle') || r.frames[0];
  const k = Math.max(1, Math.floor(Math.min(cv.width / f.w, cv.height / f.h)));   // integer scale only, nearest-neighbour
  g.drawImage(heroSheet, f.x, f.y, f.w, f.h, Math.round((cv.width - f.w * k) / 2), cv.height - f.h * k, f.w * k, f.h * k);
  return true;
}
const playTime = (sec) => { const m = Math.floor((sec || 0) / 60); return m < 60 ? `${m}m played` : `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, '0')}m played`; };
function slotInfo(n) {
  const s = readSave(n); if (!s) return null;
  return { cls: s.cls, hero: s.cls ? HERO[s.cls].cls : 'Older save', lv: s.lv || 1, area: AREA_NAME[s.area] || s.area || 'Hearthmoor Plaza',
           played: s.played || 0, errands: Object.values(s.quests || {}).filter((v) => v === 3).length, savedAt: s.savedAt, migrated: !!s.migrated };
}
G.slotInfo = slotInfo;
function syncSlots() {
  const row = $('slotRow'); if (!row) return;
  if (!row.children.length) {
    for (let n = 1; n <= SLOT_N; n++) {
      const b = document.createElement('button'); b.className = 'slotcard'; b.dataset.slot = n;
      b.innerHTML = `<canvas width="40" height="64"></canvas><span class="st"></span>`;
      b.onclick = () => { if (G.slot === n && readSave(n)) cont(); else slotPick(n); };
      row.appendChild(b);
    }
  }
  [...row.children].forEach((b) => {
    const n = +b.dataset.slot, i = slotInfo(n);
    b.classList.toggle('on', n === G.slot); b.classList.toggle('empty', !i);
    const cv = b.querySelector('canvas');
    b.dataset.icon = i && i.cls && heroIcon(cv, i.cls) ? i.cls : (cv.getContext('2d').clearRect(0, 0, cv.width, cv.height), '');
    b.querySelector('.st').innerHTML = i ? `<b>Slot ${n}</b><em>${i.hero}</em><i>Lv ${i.lv} · ${i.area}</i><i>${playTime(i.played)}</i>`
      : `<b>Slot ${n}</b><em>— empty —</em><i>New game starts here</i>`;
  });
  const s = readSave();
  $('btnCont').hidden = !s;
  $('btnCopy').disabled = !s; $('btnDel').disabled = !s;
  $('saveInfo').textContent = s ? `Slot ${G.slot} · Saved: ${new Date(s.savedAt).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })} · ${s.cls ? HERO[s.cls].cls + ' · ' : ''}${Object.values(s.quests).filter((v) => v === 3).length}/3 errands${s.migrated ? ' · (older save: pick your hero to continue)' : ''}`
    : `Slot ${G.slot} is empty: New game starts here.`;
  if (!delArmed) { $('btnDel').textContent = 'Delete'; $('btnDel').classList.remove('warn'); }
}
function slotPick(n) {
  if (!G.title || G.picking || n < 1 || n > SLOT_N) return;
  if (n !== G.slot) { G.slot = n; localStorage.setItem(LAST_SLOT, String(n)); delArmed = 0; newArmed = 0; $('btnNew').textContent = 'New game'; $('btnNew').classList.remove('warn'); G.audio.sfx('blip'); }
  syncSlots();
}
function slotMove(d) { slotPick(((G.slot - 1 + d + SLOT_N) % SLOT_N) + 1); }
function slotCopy() {   // copy the chosen slot into the first empty one
  if (!G.title || G.picking) return false;
  const s = localStorage.getItem(slotKey(G.slot)) || (readSave() && JSON.stringify(readSave()));
  if (!s) { toast('This slot is empty: nothing to copy', 1.6); return false; }
  let to = 0; for (let n = 1; n <= SLOT_N; n++) if (n !== G.slot && !readSave(n)) { to = n; break; }
  if (!to) { toast('All three slots are full: delete one first', 2.0); return false; }
  localStorage.setItem(slotKey(to), s); G.audio.sfx('save'); toast(`Slot ${G.slot} copied to slot ${to}`, 1.8); syncSlots();
  return to;
}
// deleting takes a second press (touch, mouse, keys and the controller alike; no browser dialog)
let delArmed = 0;
function slotDelete() {
  if (!G.title || G.picking || !readSave()) return false;
  const b = $('btnDel');
  if (performance.now() >= delArmed) {
    delArmed = performance.now() + 4000; b.textContent = `Delete slot ${G.slot}? Press again`; b.classList.add('warn');
    setTimeout(() => { if (delArmed && performance.now() >= delArmed) { delArmed = 0; syncSlots(); } }, 4100);
    return false;
  }
  delArmed = 0; localStorage.removeItem(slotKey(G.slot)); if (G.slot === 1) localStorage.setItem(V1_DONE, '1');
  G.audio.sfx('blip'); toast(`Slot ${G.slot} deleted`, 1.6); syncSlots();
  return true;
}
G.slots3 = { pick: slotPick, move: slotMove, copy: slotCopy, del: slotDelete, key: slotKey, state: () => ({ slot: G.slot, armed: delArmed > 0 }) };
function closeTitle() { G.title = false; $('titlescreen').hidden = true; document.body.classList.remove('titled'); $('vitals').hidden = false; G.audio.start(); }
function applyHero() {
  const ctx = G.ctx; if (!ctx) return;
  if (ctx.actors.meta.roles[G.S.cls]) ctx.actors.setRole(ctx.player, G.S.cls);
  ctx.setSpellCycle(slots()); ctx.selectSpell(0);
  if (G.S.hp == null) G.S.hp = G.combat.maxHp();
}
async function newGame() {
  if (G.busy || G.picking) return;
  const had = readSave();
  if (had && !confirmNew()) return;
  openPicker((cls) => startNew(cls));
}
async function startNew(cls) {
  G.S = fresh(); G.S.cls = cls; G.S.mode = PICK.mode || 'adventurer'; PR.ensure(G.S); G.S.hp = HERO[cls].hp;
  closeTitle();
  if (G.area !== 'plaza') await go('plaza', 'start', 'walk');
  else { const s = G.ctx.scene.game.spawns.start; G.ctx.player.x = s[0]; G.ctx.player.z = s[1]; G.ctx.player.y = G.ctx.heightAt(s[0], s[1]); G.ctx.player.facing = s[2]; G.ctx.clock.set(G.S.t); }
  applyHero();
  drawBag(); drawLog(); refreshMarkers();
  save();
  toast(`Welcome to Hearthmoor, ${HERO[cls].cls}. Marla the baker is waving at you.`, 3.2);
  if (G.S.autoLevel == null && !Q.has('autolevel')) askAuto();
  else if (Q.has('autolevel')) G.S.autoLevel = Q.get('autolevel') !== '0';
  if (Q.has('mode') && PR.MODES[Q.get('mode')]) G.S.mode = Q.get('mode');
}
// replacing a save takes a second press of New game (works with touch, mouse, keys and a controller; no browser dialog)
let newArmed = 0;
function confirmNew() {
  if (Q.has('force') || performance.now() < newArmed) { newArmed = 0; return true; }
  newArmed = performance.now() + 4000;
  const b = $('btnNew'); b.textContent = 'Replace save? Press again'; b.classList.add('warn');
  setTimeout(() => { if (performance.now() >= newArmed) { b.textContent = 'New game'; b.classList.remove('warn'); } }, 4100);
  return false;
}
async function cont() {
  if (G.busy || G.picking) return;
  const s = readSave(); if (!s) return newGame();
  if (!s.cls) {   // a migrated v1 save: choose your hero once, keep everything else
    openPicker((cls) => { s.cls = cls; s.hp = HERO[cls].hp; delete s.migrated; resume(s); });
    return;
  }
  resume(s);
}
async function resume(s) {
  G.S = { ...fresh(), ...s, v: 2 }; PR.ensure(G.S);
  closeTitle();
  G.busy = true;
  $('fade').className = 'on';
  await new Promise((r) => setTimeout(r, 300));
  await loadArea(s.area || 'plaza', 'start', s.pos);
  applyHero();
  save();
  $('fade').className = '';
  G.busy = false;
  toast(`Welcome back. ${G.ctx.scene.name}, ${$('clocktxt').textContent}`, 2.6);
}

// ------------------------------------------------------------------ leveling: XP, level-up glow, auto-level ask, hero screen
G.gainXP = (n, src) => {
  PR.ensure(G.S);
  const up = PR.addXP(G.S, n);
  const ctx = G.ctx, p = ctx && ctx.player;
  if (p && G.combat.ctx === ctx) G.combat.number('+' + Math.round(n) + 'xp', p.x + 0.4, p.y + 2.3, p.z, '#8ec8e8');
  if (up && p) levelUp();
  return up;
};
function levelUp() {
  const ctx = G.ctx, p = ctx.player, C = G.combat;
  G.S.hp = C.maxHp(); C.st = C.maxSt();
  if (ctx.effects) { ctx.effects.spawn('bloom_ring', p.x, p.y, p.z + 0.04); ctx.effects.spawn('sparkle_burst', p.x, p.y, p.z + 0.06); ctx.effects.spawn('light_orb', p.x, p.y + 0.4, p.z + 0.07); }
  if (ctx.burst) for (let i = 0; i < 3; i++) setTimeout(() => ctx.burst('sparkle', p.x, p.y + 1.0, p.z + 0.1), i * 160);
  G.audio.sfx('quest');
  const pts = G.S.autoLevel ? '' : ` ${G.S.free} stat point${G.S.free === 1 ? '' : 's'} to spend (I).`;
  toast(`Level ${G.S.lv}!${pts}${G.S.sp ? ' A skill point is ready.' : ''}`, 3.0);
  $('vitals').classList.add('lvup'); setTimeout(() => $('vitals').classList.remove('lvup'), 1600);
  save();
}
const ASK = { yes: true };
function askAuto() { G.asking = true; ASK.yes = true; $('autolv').hidden = false; syncAsk(); }
function syncAsk() { $('btnAutoYes').classList.toggle('on', ASK.yes); $('btnAutoNo').classList.toggle('on', !ASK.yes); }
function askMove() { ASK.yes = !ASK.yes; syncAsk(); }
function askPick(yes) {
  G.asking = false; $('autolv').hidden = true;
  G.S.autoLevel = !!yes; if (yes) PR.autoSpend(G.S);
  syncAutoBtn(); save();
  toast(yes ? 'Auto level on: stat points follow your class. Change it in options (O).' : 'Manual leveling: spend points on the hero screen (I).', 3.2);
}
const MODE_TIP = { story: 'Story mode: gentle hits, no faint penalty.', adventurer: 'Adventurer mode: fainting drops 10% of your gold (walk back for it).', hero: 'Hero mode: foes hit harder, better loot; fainting drops 10% of your gold.' };
function syncModeBtn() { const b = $('btnMode'); if (b) b.textContent = 'mode: ' + (PR.MODES[G.S.mode] || PR.MODES.adventurer).name; }
G.syncModeBtn = syncModeBtn;
function syncAutoBtn() { const b = $('btnAuto'); if (b) b.textContent = 'auto level: ' + (G.S.autoLevel ? 'on' : 'off'); }
const HUI = { tab: 0, i: 0 };
function setHeroUI(open) {
  if (open && (G.title || G.busy || G.dlg || G.picking || G.shop)) return;
  G.heroUI = open; $('heroui').hidden = !open;
  if (open) { if (G.log) setLog(false); if (G.opts) setOpts(false); PR.ensure(G.S); drawHero(); }
}
G.setHeroUI = setHeroUI;
function drawHero() {
  drawBag();
  const S = G.S, C = G.combat, h = HERO[S.cls], M = C.M, tree = PR.TREES[S.cls] || [];
  $('heroHead').innerHTML = `<b>${h.cls}</b> <span class="tag">Lv ${S.lv}</span> <span class="tag">${S.lv >= PR.LEVEL_CAP ? 'max level' : `${S.xp} / ${PR.xpNeed(S.lv)} xp`}</span>`
    + `<span class="tag">${(PR.MODES[S.mode] || PR.MODES.adventurer).name}</span><span class="tag">gold ${S.gold || 0}</span><span class="tag">HP ${C.maxHp()}</span><span class="tag">ST ${C.maxSt()}</span><span class="tag">crit ${Math.round(M.crit * 100)}%</span>`;
  document.querySelectorAll('#heroTabs button').forEach((b, k) => b.classList.toggle('on', k === HUI.tab));
  const body = $('heroBody');
  if (HUI.tab === 0) {
    HUI.n = PR.STATS.length;
    body.innerHTML = `<p class="pts">${S.free} stat point${S.free === 1 ? '' : 's'} free${S.autoLevel ? ' · auto level is on (class picks)' : ''}</p>`
      + PR.STATS.map((st, k) => `<div class="row${k === HUI.i ? ' sel' : ''}" data-k="${k}"><b>${st.name}</b><em>${S.stats[st.id]}</em><span>${st.does}</span>`
      + `<button class="wbtn sm plus" data-stat="${st.id}" ${S.free ? '' : 'disabled'}>+</button></div>`).join('');
    body.querySelectorAll('[data-stat]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); if (PR.spendStat(S, b.dataset.stat)) { G.audio.sfx('pickup'); save(); drawHero(); } }; });
  } else if (HUI.tab === 3) {
    LO.ensure(S);
    const eq = LO.SLOTS.map((sl) => [sl, S.gear[sl]]);
    HUI.n = 3 + S.bag.length;
    const rowOf = (it, k, label, btns) => `<div class="row gear${it ? ' r' + it.rar : ' none'}${k === HUI.i ? ' sel' : ''}" data-k="${k}">`
      + `<b>${label}</b><em class="iname">${it ? `<i class="ic" data-ic="${it.slot}:${it.rar}:${(it.gems || []).map((g) => g || '-').join(',')}"></i>${it.name}` : '— empty —'}</em>`
      + `<span>${it ? `<u>${LO.RARITY[it.rar].name}</u> · ${LO.describe(it)}` : ''}</span><span class="bb">${btns}</span></div>`;
    const owned = LO.GEM_IDS.filter((g) => S.gems[g] > 0);
    if (!owned.includes(HUI.gem)) HUI.gem = owned[0] || null;
    const sockBtn = (it, k) => (it && (it.gems || []).includes(null) && HUI.gem ? `<button class="wbtn sm plus" data-sock="${k}">socket</button>` : '');
    body.innerHTML = `<p class="pts">Gold ${S.gold} · bag ${S.bag.length} / ${LO.BAG_MAX} · Enter / A equip · X scrap for gold</p>`
      + `<p class="pts gems">${owned.length ? `gems: ${owned.map((g) => `<span class="gemtag${g === HUI.gem ? ' on' : ''}" style="--gc:${LO.GEMS[g].col}">◆ ${LO.GEMS[g].name} ×${S.gems[g]}</span>`).join(' ')}`
        + ` <button class="wbtn sm" id="gemCycle">gem ▸</button> · R / Y socket into the chosen row · T / RT next gem` : 'gems: none yet (golem cores, rift shards: beat foes, or ask the night merchant)'}</p>`
      + eq.map(([sl, it], k) => rowOf(it, k, sl, (it ? `<button class="wbtn sm plus" data-uneq="${sl}">take off</button>` : '') + sockBtn(it, k))).join('')
      + (S.bag.length ? '<p class="pts">bag</p>' : '<p class="pts">bag is empty: beat enemies, walk over the beams</p>')
      + S.bag.map((it, i) => rowOf(it, 3 + i, it.slot, `<button class="wbtn sm plus" data-eq="${i}">equip</button>${sockBtn(it, 3 + i)}<button class="wbtn sm plus" data-scrap="${i}">scrap</button>`)).join('');
    body.querySelectorAll('[data-ic]').forEach((el) => { const [sl, r, gs] = el.dataset.ic.split(':'); const cv = LO.iconCanvas(sl, +r, 3, gs ? gs.split(',').map((g) => (g === '-' ? null : g)) : null); el.replaceWith(cv); cv.className = 'gicon'; });
    body.querySelectorAll('[data-sock]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); HUI.i = +b.dataset.sock; heroSocket(); }; });
    const gc = $('gemCycle'); if (gc) gc.onclick = (e) => { e.stopPropagation(); gemCycle(); };
    body.querySelectorAll('[data-eq]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); if (LO.equip(S, +b.dataset.eq)) { G.audio.sfx('pickup'); save(); drawHero(); } }; });
    body.querySelectorAll('[data-uneq]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); if (LO.unequip(S, b.dataset.uneq)) { save(); drawHero(); } }; });
    body.querySelectorAll('[data-scrap]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); HUI.i = 3 + +b.dataset.scrap; heroScrap(); }; });
    const sel = body.querySelector('.row.sel'); if (sel && sel.scrollIntoView) sel.scrollIntoView({ block: 'nearest' });
  } else if (HUI.tab === 2) {
    const cur = slots(), raw = Array.isArray(S.slots) ? S.slots : cur;
    HUI.n = 4;
    body.innerHTML = `<p class="pts">Spellbook: ${knownSpells().length} known · put any of them in the four slots (1-4, LB / RB, the wheel)</p>`
      + [0, 1, 2, 3].map((k) => { const id = raw[k] || null;
        return `<div class="row sbslot${k === HUI.i ? ' sel' : ''}" data-k="${k}"><b>slot ${k + 1}</b><em>${id ? spellName(id) : '— empty —'}</em><span>${id ? spellBlurb(id) : 'tap change to fill'}</span>`
        + `<button class="wbtn sm plus" data-slot="${k}">change</button></div>`; }).join('');
    body.querySelectorAll('[data-slot]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); if (slotSpell(+b.dataset.slot)) { G.audio.sfx('pickup'); save(); drawHero(); } }; });
  } else {
    HUI.n = tree.length;
    const RN = ['', 'I', 'II', 'III', 'IV'], TL = { 1: 'tier I · 1 point', 2: 'tier II · 1 point · Lv 5', 3: 'tier III capstones · 2 points · Lv 10' };
    const st = PR.summonTier(S);
    body.innerHTML = `<p class="pts">${S.sp} skill point${S.sp === 1 ? '' : 's'} · summon tier ${RN[st]}</p>`
      + tree.map((n, k) => {
        const lock = PR.lockOf(S, n), got = lock === 'learned';
        const head = (k === 0 || tree[k - 1].tier !== n.tier) ? `<p class="tierhd t${n.tier}">${TL[n.tier]}</p>` : '';
        return head + `<div class="row node t${n.tier}${got ? ' got' : ''}${lock && !got ? ' locked' : ''}${k === HUI.i ? ' sel' : ''}" data-k="${k}"><b>${n.branch}</b><em>${n.name}</em><span>${n.desc}</span>`
          + `<button class="wbtn sm plus" data-node="${n.id}" ${lock ? 'disabled' : ''}>${got ? '✓' : lock || 'learn'}</button></div>`;
      }).join('');
    body.querySelectorAll('[data-node]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); if (PR.learn(S, b.dataset.node)) { G.audio.sfx('quest'); save(); drawHero(); } }; });
    const sel = body.querySelector('.row.sel'); if (sel && sel.scrollIntoView) sel.scrollIntoView({ block: 'nearest' });
  }
  body.querySelectorAll('.row').forEach((r) => { r.onclick = () => { HUI.i = +r.dataset.k; drawHero(); }; });
}
function heroAct() {
  const S = G.S, b = $('heroBody').querySelector(`.row[data-k="${HUI.i}"] button`);
  if (b && !b.disabled) b.click();
}
function heroScrap() {
  drawBag();
  if (HUI.tab !== 3 || HUI.i < 3) return;
  const g = LO.scrap(G.S, HUI.i - 3);
  if (g) { toast(`Scrapped for ${g} gold`, 1.4); G.audio.sfx('pickup'); HUI.i = Math.min(HUI.i, 2 + G.S.bag.length); save(); drawHero(); }
}
// sockets: put the chosen gem into the selected row's first empty socket (gems stay until a jeweler clears them)
function gearAt(k) { const S = G.S; return k < 3 ? S.gear[LO.SLOTS[k]] : S.bag[k - 3]; }
function heroSocket() {
  if (HUI.tab !== 3) return false;
  const it = gearAt(HUI.i);
  if (!it || !(it.gems || []).includes(null)) { toast(it ? 'No empty socket on this piece' : 'Pick a piece of gear first', 1.4); return false; }
  if (!HUI.gem) { toast('No gems yet', 1.2); return false; }
  const name = LO.GEMS[HUI.gem].name;
  if (!LO.socketGem(G.S, it, HUI.gem)) return false;
  toast(`${name} set into ${it.name}`, 1.8); G.audio.sfx('quest'); save(); drawHero();
  return true;
}
function gemCycle() {
  const owned = LO.GEM_IDS.filter((g) => G.S.gems[g] > 0); if (!owned.length) return;
  HUI.gem = owned[(owned.indexOf(HUI.gem) + 1) % owned.length]; drawHero();
}
G.heroSocket = heroSocket; G.gemCycle = gemCycle;
function heroTab(d) { HUI.tab = (HUI.tab + d + 4) % 4; HUI.i = 0; drawHero(); }
function heroMove(d) { HUI.i = Math.max(0, Math.min((HUI.n || 1) - 1, HUI.i + d)); drawHero(); }
function heroPad(name) {
  if (name === 'b' || name === 'start') setHeroUI(false);
  else if (name === 'lb' || name === 'left') heroTab(-1); else if (name === 'rb' || name === 'right') heroTab(1);
  else if (name === 'up') heroMove(-1); else if (name === 'down') heroMove(1);
  else if (name === 'x' && HUI.tab === 3) heroScrap();
  else if (name === 'y' && HUI.tab === 3) heroSocket();
  else if (name === 'rt' && HUI.tab === 3) gemCycle();
  else if (name === 'a' || name === 'x') heroAct();
}
function heroKey(k, e) {
  if (k === 'escape' || k === 'i' || k === 'b' || k === 'g') setHeroUI(false);
  else if (HUI.tab === 3 && (k === 'x' || k === 'delete' || k === 'backspace')) { e.preventDefault(); heroScrap(); }
  else if (HUI.tab === 3 && k === 'r') heroSocket();
  else if (HUI.tab === 3 && k === 't') gemCycle();
  else if (k === 'arrowleft' || k === 'a' || k === 'q') heroTab(-1); else if (k === 'arrowright' || k === 'd' || k === 'e') heroTab(1);
  else if (k === 'arrowup' || k === 'w') heroMove(-1); else if (k === 'arrowdown' || k === 's') heroMove(1);
  else if (k === 'enter' || k === ' ' || k === 'f') { e.preventDefault(); heroAct(); }
}
function wireLeveling() {
  $('btnAutoYes').onclick = () => askPick(true); $('btnAutoNo').onclick = () => askPick(false);
  $('btnMode').onclick = () => { const i = PR.MODE_IDS.indexOf(G.S.mode); G.S.mode = PR.MODE_IDS[(i + 1) % 3]; syncModeBtn(); save(); toast(MODE_TIP[G.S.mode], 3); };
  $('btnAuto').onclick = () => { G.S.autoLevel = !G.S.autoLevel; if (G.S.autoLevel) PR.autoSpend(G.S); syncAutoBtn(); save(); };
  $('heroClose').onclick = () => setHeroUI(false);
  document.querySelectorAll('#heroTabs button').forEach((b, k) => { b.onclick = () => { HUI.tab = k; HUI.i = 0; drawHero(); }; });
  $('vitals').addEventListener('click', () => setHeroUI(true));
  $('heroui').addEventListener('pointerdown', (e) => { if (e.target === $('heroui')) setHeroUI(false); });
}
G.ask = { open: askAuto, pick: askPick };

// ------------------------------------------------------------------ start
async function main() {
  wire();
  if (Q.has('reset')) localStorage.removeItem(slotKey(G.slot));
  if (Q.has('pad') || (matchMedia('(pointer: coarse)').matches && !Q.has('nopad') && !QA)) document.body.classList.add('padon');
  const s = readSave();
  if (QA) {
    G.title = false; $('titlescreen').hidden = true; $('vitals').hidden = false;
    G.S.cls = HERO[Q.get('hero')] ? Q.get('hero') : 'wildcaller'; PR.ensure(G.S); G.S.autoLevel = true;
    if (Q.get('state')) Object.assign(G.S, JSON.parse(Q.get('state')));
    await loadArea(Q.get('area') || 'plaza', Q.get('spawn') || 'start');
  } else {
    document.body.classList.add('titled');
    loadHeroSheet(); syncSlots();
    G.preview = (s && s.cls) || 'wildcaller';
    await loadArea('plaza', 'start');    // the plaza idles behind the title card
  }
  if ($('pad')) $('btnPad') && $('btnPad').classList.toggle('on', document.body.classList.contains('padon'));
  G.ready = true;
  if (!QA && 'serviceWorker' in navigator && location.protocol.startsWith('http') && !Q.has('nosw')) navigator.serviceWorker.register('sw.js').catch(() => {});
}
main().catch((e) => { console.error(e); const b = $('boot'); if (b) { b.classList.remove('gone'); b.textContent = 'Hearthmoor failed to load: ' + e.message; } });
