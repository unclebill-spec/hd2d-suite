// Stage 5 part 3: factions + merit. Five factions, six ranks each (Stranger -> Legend), merit saved per slot (S.merit).
// Merit comes from real activity: errands, rift seals (Gatekeepers' Rift Marks + the realm's faction), rares and
// mini-bosses (the realm's faction), Gnome Council secrets / riddles, Rift Corsair black-market trade (which costs a
// little Order of the Hearth standing). Ranks never drop. Each faction's Friend rank unlocks one reward usable now,
// every rank unlocks a title. Signature glow colours are palette / NEON accents (HUD swatches, toasts, the rank-up glow).
export const RANKS = ['Stranger', 'Friend', 'Trusted', 'Honored', 'Champion', 'Legend'];
export const NEED = [0, 150, 400, 800, 1400, 2200];   // ~3-5 meaningful activities per rank
export const FACTIONS = {
  hearth: { name: 'Order of the Hearth', short: 'the Hearth', cur: 'Hearth Tokens', col: '#f2c24a', base: 'Midgard',
    earn: 'errands, village defence, Midgard rifts and rares',
    titles: ['', 'Friend of the Hearth', 'Hearthkeeper', 'Lamplighter', 'Warden of Midgard', 'Hearth Legend'],
    reward: 'Hearthmoor prices: 10% off at Odo\'s Wares', legend: 'Hearthstone Mantle' },
  gate: { name: "Gatekeepers' Guild", short: 'the Guild', cur: 'Rift Marks', col: '#6cc8ff', base: 'Bifrost Crossing',
    earn: 'sealing rifts (every tier), escorts, portal repairs',
    titles: ['', 'Rift Warden', 'Gate Runner', 'Keybearer', 'Bridge Champion', 'Keyless Legend'],
    reward: 'Rift bounty: +25% gold from every rift you seal', legend: 'Keyless Rune' },
  gnome: { name: 'Gnome Council', short: 'the Council', cur: 'Gilded Acorns', col: '#7ccf5a', base: 'hidden',
    earn: 'hidden springs, secrets, gnome riddles',
    titles: ['', 'Acorn Friend', 'Riddle Solver', 'Cap Tipper', 'Council Confidant', 'Pocket Legend'],
    reward: 'Acorn charm: +10% gold from everything you pick up', legend: "Gnome King's Pocket Engine" },
  corsair: { name: 'Rift Corsairs', short: 'the Corsairs', cur: 'Black Doubloons', col: '#e0302a', base: 'Ravenhold Harbor',
    earn: 'black-market trade with Sefa (costs a little Hearth standing), raids',
    titles: ['', 'Deckhand', 'Smuggler', 'Quartermaster', 'Corsair Captain', 'Black Sail Legend'],
    reward: 'Black-market rates: 15% off at the night merchant', legend: 'Black Sail Cutlass' },
  embassy: { name: 'Realm Embassies', short: 'the Embassies', cur: 'Realm Favor', col: '#a45cf0', base: 'Bifrost embassy quarters',
    earn: "each realm's quests, rifts and rares (Vanaheim so far)",
    titles: ['', 'Envoy', 'Emissary', 'Ambassador', 'Realm Champion', 'Nine-Realm Legend'],
    reward: 'Realm favor: +10% XP in the realms (Vanaheim)', legend: "the realm's legendary weapon quest" },
};
export const IDS = Object.keys(FACTIONS);
// the realm faction of each area: rifts, rares and mini-bosses there earn its merit
export const REALM = { plaza: 'hearth', lane: 'hearth', mossglen: 'hearth', hollows: 'hearth', vanaheim: 'embassy', rift: 'gate', ravenhold: 'corsair', bifrost: 'gate' };
export const MERIT = { errand: 40, rift: [30, 60, 120], rare: 50, rareTrait: 40, boss: 80, riddle: 60, secret: 40, smuggle: 15, rival: 5, warden: 20,
                        sable: 20, dues: 15, harbor: 40,     // Ravenhold: meeting Sable, paying harbor dues, the harbor story quest (all Corsair)
                        halvard: 20, road: 60 };             // Bifrost: meeting Gatewright Halvard, finishing 'The Road to the Rift' there (Guild)
export const rankOf = (m) => { let r = 0; for (let k = 1; k < NEED.length; k++) if (m >= NEED[k]) r = k; return r; };

// save migration: older saves get the merit their finished work would have earned (errands, rifts sealed, rares felled)
export function migrate(S) {
  if (S.merit && S.factionsV === 1) return false;
  const m = { hearth: 0, gate: 0, gnome: 0, corsair: 0, embassy: 0, ...(S.merit || {}) };
  if (!S.merit) {
    m.hearth += MERIT.errand * Object.values(S.quests || {}).filter((v) => v === 3).length;
    const R = S.rifts || {}; m.gate += MERIT.rift[0] * (R.minor || 0) + MERIT.rift[1] * (R.major || 0) + MERIT.rift[2] * (R.abyssal || 0);
    for (const h of Object.values(S.hunt || {})) m[h.base === 'sporemother' ? 'embassy' : 'hearth'] += (MERIT.rare + MERIT.rareTrait * ((h.traits || []).length - 1)) * (h.kills || 1);
    if ((S.flags || {}).riddle === 'solved') m.gnome += MERIT.riddle;
  }
  S.merit = m;
  S.ranks = Object.fromEntries(IDS.map((id) => [id, Math.max((S.ranks || {})[id] || 0, rankOf(m[id]))]));
  S.factionsV = 1;
  return true;
}

// the Order of the Hearth's local warden: the first faction contact (plaza, rune guard sprite)
export const WARDEN = { plaza: { id: 'hilde', role: 'runeguard', name: 'Warden Hilde of the Hearth', pos: [1.0, -5.4], facing: 'down',
  say: ['The Order keeps the lamps lit. Lend a hand and we remember it.'] } };

export class Factions {
  constructor(G) { this.G = G; }
  attach(ctx, area) {
    this.ctx = ctx; const W = WARDEN[area], G = this.G;
    if (G.introNext || (G.intro && G.intro.active)) return;   // Hilde arrives after Lantern Eve (she stays out of the opening's fight by the gate)
    if (W && ctx.actors.meta.roles[W.role] && !ctx.npc(W.id)) { const a = ctx.addNpc({ ...W, pos: W.pos.slice(), behavior: 'idle', talkable: true }); a.facing = W.facing; }
  }
  get S() { return this.G.S; }
  rank(id) { migrate(this.S); return this.S.ranks[id] || 0; }
  has(id, r = 1) { return this.rank(id) >= r; }
  // add merit; returns the new rank if it went up. Ranks never drop (rival losses stop at the current rank's floor)
  add(id, n, why = '') {
    const S = this.S, F = FACTIONS[id]; if (!F || !n) return 0;
    migrate(S);
    const r0 = S.ranks[id] || 0;
    S.merit[id] = Math.max(NEED[r0], (S.merit[id] || 0) + n);
    const r1 = Math.max(r0, rankOf(S.merit[id]));
    if (n > 0 && this.G.popText && this.G.ctx) { const p = this.G.ctx.player; this.G.popText(`+${n} ${F.cur}`, { x: p.x, y: p.y + 1.6, z: p.z }, F.col); }
    if (r1 > r0) { S.ranks[id] = r1; this.rankUp(id, r1); }
    this.G.drawFactions && this.G.drawFactions();
    return r1 > r0 ? r1 : 0;
  }
  rankUp(id, r) {
    const G = this.G, F = FACTIONS[id], ctx = G.ctx;
    const extra = r === 1 ? ` · unlocked: ${F.reward}` : r === 5 ? ` · ${F.legend} awaits` : '';
    G.toast && G.toast(`<span style="color:${F.col}">✦ ${F.name}: ${RANKS[r]}!</span> Title "${F.titles[r]}"${extra}`, 4.5, true, true);   // priority: later toasts queue behind it
    G.audio && G.audio.sfx('quest');
    let spark = false, glow = false;
    if (ctx && ctx.player) {
      const p = ctx.player;
      spark = !!(ctx.effects && ctx.effects.spawn('sparkle_burst', p.x, p.y, p.z + 0.05));
      if (ctx.addGlow) { const L = ctx.addGlow(p.x, p.y + 0.9, p.z + 0.2, { color: F.col, intensity: 6, range: 4, lift: 0, fadeIn: 0.2 }); glow = !!L; setTimeout(() => { if (L) L.kill = true; }, 1600); }
    }
    this.last = { id, r, t: Date.now(), spark, glow };
    G.save && G.save();
  }
  // activity hooks
  realm() { return REALM[this.G.area] || 'hearth'; }
  onErrand() { this.add('hearth', MERIT.errand, 'errand'); }
  onRift(tier) {
    const g = MERIT.rift[tier] || 0; this.add('gate', g, 'rift');
    const r = this.realm(); if (r !== 'gate') this.add(r, Math.round(g / 2), 'rift');
  }
  onRare(R) { this.add(this.realm(), MERIT.rare + MERIT.rareTrait * Math.max(0, (R.traits || []).length - 1), 'rare'); }
  onBoss() { this.add(this.realm(), MERIT.boss, 'boss'); }
  onSecret() { this.add('gnome', MERIT.secret, 'secret'); }
  onRiddle() { this.add('gnome', MERIT.riddle, 'riddle'); }
  onSmuggle() { this.add('corsair', MERIT.smuggle, 'smuggle'); this.add('hearth', -MERIT.rival, 'rival'); }
  // rewards usable now (Friend rank)
  priceMul(shop) { return shop === 'hearthmoor' && this.has('hearth') ? 0.9 : shop === 'night' && this.has('corsair') ? 0.85 : 1; }
  riftGoldMul() { return this.has('gate') ? 1.25 : 1; }
  pickupGoldMul() { return this.has('gnome') ? 1.1 : 1; }
  xpMul() { return this.G.area === 'vanaheim' && this.has('embassy') ? 1.1 : 1; }
  title() { const t = this.S.title; if (!t) return ''; const [id, r] = t.split(':'); const F = FACTIONS[id]; return F && this.rank(id) >= +r ? F.titles[+r] : ''; }
  setTitle(id) { const r = this.rank(id); if (!r) return false; this.S.title = this.S.title === `${id}:${r}` ? null : `${id}:${r}`; return true; }
  qa() { migrate(this.S); return { merit: { ...this.S.merit }, ranks: { ...this.S.ranks }, title: this.title(), last: this.last || null }; }
}
