// Hearthmoor: a small cozy HD-2D village loop on the hd2d runtime (engine/main.js boot + hooks).
// Area manager (fresh canvas per area, fade), dialogue, 3 errands + quest log, bag, persistent clock,
// spells as rewards, save/load (localStorage hearthmoor-slot-1-v1), ambient audio, PWA.
import { boot } from '../engine/main.js';
import { ITEMS, QUESTS, TALK, SPELL_NAMES, markerFor } from './data.js';
import { Ambient } from './audio.js';

const Q = new URLSearchParams(location.search);
const KEY = 'hearthmoor-slot-1-v1';
const QA = Q.has('qa');                       // check-scene / screenshots: straight into ?area=, fresh state, no title, no saving
const AREAS = { plaza: 'areas/plaza/', lane: 'areas/lane/', mossglen: 'areas/mossglen/' };
const DAY_SECONDS = Number(Q.get('day') || 720);  // one whole day = 12 real minutes (day, dusk, night, dawn)
const $ = (id) => document.getElementById(id);

const fresh = () => ({ v: 1, area: 'plaza', pos: null, t: 0.62, inv: {}, quests: { bread: 0, tea: 0, cat: 0 }, picked: {},
                       cat: 'glade', spells: ['sparkle_burst'], played: 0, savedAt: null });

const G = {
  S: fresh(), game: null, ctx: null, busy: false, title: !QA, dlg: null, log: false, markers: {}, scenes: {}, armed: false,
  audio: new Ambient(), autosave: 20, near: null,
};
window.__hm = G;   // smoke tests + debugging

// ------------------------------------------------------------------ save / load
function readSave() { try { const s = JSON.parse(localStorage.getItem(KEY)); return s && s.v === 1 ? s : null; } catch (e) { return null; } }
function save(note) {
  if (QA || G.title) return false;
  const p = G.ctx && G.ctx.player;
  if (p) G.S.pos = [+p.x.toFixed(2), +p.z.toFixed(2), p.facing];
  G.S.area = G.area; G.S.savedAt = new Date().toISOString();
  localStorage.setItem(KEY, JSON.stringify(G.S));
  if (note) { toast('Saved ✓'); G.audio.sfx('save'); }
  return true;
}
G.save = save; G.readSave = readSave;

// ------------------------------------------------------------------ inventory + quests (used by data.js)
G.give = (id, n = 1) => { G.S.inv[id] = (G.S.inv[id] || 0) + n; drawBag(id); toast(`+${n} ${ITEMS[id].name}`); };
G.take = (id, n = 1) => { G.S.inv[id] = Math.max(0, (G.S.inv[id] || 0) - n); if (!G.S.inv[id]) delete G.S.inv[id]; drawBag(); };
G.setQuest = (id, stage) => {
  const was = G.S.quests[id]; G.S.quests[id] = stage; drawLog();
  if (stage === 3 && was !== 3) { toast(`Errand done: ${QUESTS[id].title}`, 2.6); G.audio.sfx('quest'); }
  else if (was === 0 && stage > 0) { toast(`New errand: ${QUESTS[id].title}`, 2.6); G.audio.sfx('pickup'); flashLog(); }
  refreshMarkers(); save();
};
G.learn = (spell) => {
  if (G.S.spells.includes(spell)) return;
  G.S.spells.push(spell);
  if (G.ctx) G.ctx.setSpellCycle(G.S.spells);
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
function iconHTML(id) { const i = ITEMS[id].icon; return `<span class="ico" style="background-position:-${i * ICON}px 0"></span>`; }
function drawBag(flash) {
  const el = $('bag'); if (!el) return;
  const ids = Object.keys(ITEMS).filter((k) => G.S.inv[k]);
  el.innerHTML = ids.length ? ids.map((k) => `<span class="slot${k === flash ? ' new' : ''}" title="${ITEMS[k].name}: ${ITEMS[k].about}">${iconHTML(k)}<b>${G.S.inv[k]}</b></span>`).join('')
                            : '<span class="empty">bag: empty</span>';
  const rail = $('rail');
  if (rail) rail.innerHTML = ids.slice(0, 4).map((k) => `<span class="rslot">${iconHTML(k)}<b>${G.S.inv[k]}</b></span>`).join('');
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
  const sp = $('logSpells'); if (sp) sp.textContent = 'Charms: ' + G.S.spells.map((s) => SPELL_NAMES[s] || s).join(' · ');
}
function flashLog() { const b = $('btnLog'); b.classList.add('ping'); setTimeout(() => b.classList.remove('ping'), 1600); }
function setLog(open) { G.log = open; $('log').hidden = !open; $('btnLog').classList.toggle('on', open); if (open) drawLog(); }
let toastT = 0;
function toast(msg, s = 2.0) { const el = $('toast'); el.textContent = msg; el.hidden = false; toastT = s; }
G.toast = toast;

// ------------------------------------------------------------------ dialogue (carved-wood frame, parchment page)
let portraitImg = null;
function openDialogue(npc, entry) {
  G.dlg = { npc, pages: entry.pages, i: 0, then: entry.then, shown: 0, full: false };
  $('dlgName').textContent = npc.name || npc.role;
  drawPortrait(npc);
  $('dlg').hidden = false; document.body.classList.add('dlgopen');
  G.audio.sfx('blip');
  showPage();
}
function showPage() {
  const d = G.dlg; d.shown = 0; d.full = false;
  $('dlgText').textContent = '';
  $('dlgMore').textContent = d.i < d.pages.length - 1 ? '▼' : '✕';
  $('dlgPage').textContent = `${d.i + 1}/${d.pages.length}`;
}
function advanceDialogue() {
  const d = G.dlg; if (!d) return;
  if (!d.full) { d.shown = 1e9; return; }       // first press finishes the line
  if (d.i < d.pages.length - 1) { d.i++; G.audio.sfx('blip'); showPage(); return; }
  closeDialogue();
}
function closeDialogue() {
  const d = G.dlg; G.dlg = null; $('dlg').hidden = true; document.body.classList.remove('dlgopen');
  if (d && d.then) d.then(G);
}
function typeDialogue(dt) {
  const d = G.dlg; if (!d || d.full) return;
  d.shown += dt * 55;
  const txt = d.pages[d.i];
  const n = Math.min(txt.length, Math.floor(d.shown));
  $('dlgText').textContent = txt.slice(0, n);
  if (n >= txt.length) d.full = true;
}
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
  G.game = await boot({ base: AREAS[id], canvas, spawn: sp, startT: G.S.t, clockSpeed: 1 / DAY_SECONDS, spellCycle: G.S.spells,
                        keepTitle: true, padHandled: true, hooks, toast: (m, t) => toast(m, t) });
  const ctx = G.ctx = G.game.ctx;
  // portrait source: this area's actor atlas
  portraitImg = new Image(); portraitImg.src = AREAS[id] + ctx.scene.atlas.image;
  // pickups already taken stay gone
  for (const pk of gm.pickups || []) if (G.S.picked[pk.fx] && ctx.fx[pk.fx]) { ctx.gamefx.remove(ctx.fx[pk.fx]); delete ctx.fx[pk.fx]; }
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
  if (toastT > 0) { toastT -= dt; if (toastT <= 0) $('toast').hidden = true; }
  syncMarkers();
  if (G.title || G.busy) return;
  // exits + portals: arm once the player has stood outside every trigger (no bounce on arrival)
  const trig = [...(gm.exits || []).map((e) => ({ ...e, how: 'walk' })), ...(gm.portals || []).map((e) => ({ ...e, how: 'portal' }))];
  const inside = trig.find((e) => inRect(p, e.rect));
  if (!inside) G.armed = true;
  else if (G.armed && !G.dlg) { go(inside.to, inside.spawn, inside.how); return; }
  // pickups: walk over a glimmer
  const pk = nearPickup(ctx, 0.7); if (pk) pick(ctx, pk);
  // prompt near a gate or a glimmer
  let prompt = '';
  const close = trig.find((e) => Math.max(e.rect[0] - p.x, p.x - e.rect[2], e.rect[1] - p.z, p.z - e.rect[3]) < 1.6);
  if (close) prompt = close.how === 'portal' ? `step into the swirl: ${close.label}` : close.label;
  const pe = $('prompt'); if (pe.textContent !== prompt) { pe.textContent = prompt; pe.hidden = !prompt; }
  G.audio.setNight(ctx.clock.grade ? (ctx.clock.grade().bugs ?? 0) : 0);
  G.autosave -= dt; if (G.autosave <= 0) { G.autosave = 20; save(); }
}

const hooks = {
  blockInput: () => !!(G.dlg || G.busy || G.title || G.log),
  skipActor: (spec) => spec.id === 'cat' && ((G.area === 'plaza' && G.S.cat !== 'home') || (G.area === 'mossglen' && G.S.cat !== 'glade')),
  onInteract: (ctx, kind) => {
    if (G.title) return true;
    if (G.dlg) { advanceDialogue(); return true; }
    if (G.log) { setLog(false); return true; }
    if (G.busy) return true;
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
    return false;
  },
  // controller buttons (standard mapping) before the engine defaults: title, dialogue, quest log, Start = log
  onPad: (name, ctx) => {
    if (G.title) {
      if (name === 'a' || name === 'start') (readSave() ? cont : newGame)();
      else if (name === 'x') newGame();
      return true;
    }
    if (G.busy) return true;
    if (G.dlg) { if (name === 'a') advanceDialogue(); else if (name === 'b') closeDialogue(); return name !== 'select'; }
    if (G.log) { if (name === 'a' || name === 'b' || name === 'start') setLog(false); return name !== 'select'; }
    if (name === 'start') { setLog(true); return true; }
    return false;
  },
  onFrame,
  nearThing: (ctx) => !!nearPickup(ctx, 1.4),
};

// ------------------------------------------------------------------ title screen, buttons, keys
function wire() {
  $('btnLog').onclick = () => setLog(!G.log);
  $('logClose').onclick = () => setLog(false);
  $('btnSave').onclick = () => save(true);
  $('btnSound').onclick = () => { G.audio.start(); const m = G.audio.toggle(); $('btnSound').textContent = m ? 'sound: off' : 'sound: on'; };
  $('btnSound').textContent = G.audio.muted ? 'sound: off' : 'sound: on';
  $('dlg').addEventListener('pointerdown', (e) => { e.preventDefault(); advanceDialogue(); });
  const third = $('pad3rd');
  if (third) { third.disabled = false; third.textContent = '☰'; third.title = 'quest log'; third.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); setLog(!G.log); }); }
  addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (G.title) { if (k === 'enter' || k === ' ') { e.preventDefault(); (readSave() ? cont : newGame)(); } else if (k === 'n') newGame(); return; }
    if (k === 'j' || k === 'l') setLog(!G.log);
    if (k === 'escape') { if (G.dlg) closeDialogue(); else if (G.log) setLog(false); }
    if (k === 'k' || ((e.ctrlKey || e.metaKey) && k === 's')) { e.preventDefault(); save(true); }
    if (k === 'm') { G.audio.start(); const m = G.audio.toggle(); $('btnSound').textContent = m ? 'sound: off' : 'sound: on'; }
  });
  addEventListener('pointerdown', () => G.audio.start(), { once: true });
  addEventListener('keydown', () => G.audio.start(), { once: true });
  addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') save(); });
  addEventListener('pagehide', () => save());
  $('btnNew').onclick = () => newGame();
  $('btnCont').onclick = () => cont();
}
function closeTitle() { G.title = false; $('titlescreen').hidden = true; document.body.classList.remove('titled'); G.audio.start(); }
async function newGame() {
  if (G.busy) return;
  const had = readSave();
  if (had && !confirmNew()) return;
  G.S = fresh();
  closeTitle();
  if (G.area !== 'plaza') await go('plaza', 'start', 'walk');
  else { const s = G.ctx.scene.game.spawns.start; G.ctx.player.x = s[0]; G.ctx.player.z = s[1]; G.ctx.player.y = G.ctx.heightAt(s[0], s[1]); G.ctx.player.facing = s[2]; G.ctx.clock.set(G.S.t); }
  drawBag(); drawLog(); refreshMarkers();
  save();
  toast('Welcome to Hearthmoor. Marla the baker is waving at you.', 3.2);
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
  const s = readSave(); if (!s) return newGame();
  G.S = { ...fresh(), ...s };
  closeTitle();
  G.busy = true;
  $('fade').className = 'on';
  await new Promise((r) => setTimeout(r, 300));
  await loadArea(s.area || 'plaza', 'start', s.pos);
  $('fade').className = '';
  G.busy = false;
  toast(`Welcome back. ${G.ctx.scene.name}, ${$('clocktxt').textContent}`, 2.6);
}

// ------------------------------------------------------------------ start
async function main() {
  wire();
  if (Q.has('reset')) localStorage.removeItem(KEY);
  if (Q.has('pad') || (matchMedia('(pointer: coarse)').matches && !Q.has('nopad') && !QA)) document.body.classList.add('padon');
  const s = readSave();
  if (QA) {
    G.title = false; $('titlescreen').hidden = true;
    if (Q.get('state')) Object.assign(G.S, JSON.parse(Q.get('state')));
    await loadArea(Q.get('area') || 'plaza', Q.get('spawn') || 'start');
  } else {
    document.body.classList.add('titled');
    $('btnCont').hidden = !s;
    if (s) $('saveInfo').textContent = `Saved: ${new Date(s.savedAt).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })} · ${Object.values(s.quests).filter((v) => v === 3).length}/3 errands`;
    await loadArea('plaza', 'start');    // the plaza idles behind the title card
  }
  if ($('pad')) $('btnPad') && $('btnPad').classList.toggle('on', document.body.classList.contains('padon'));
  G.ready = true;
  if (!QA && 'serviceWorker' in navigator && location.protocol.startsWith('http') && !Q.has('nosw')) navigator.serviceWorker.register('sw.js').catch(() => {});
}
main().catch((e) => { console.error(e); const b = $('boot'); if (b) { b.classList.remove('gone'); b.textContent = 'Hearthmoor failed to load: ' + e.message; } });
