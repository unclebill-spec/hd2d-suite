// Hearthmoor rift storms (Stage 6.5, story: rift_storms.md). A storm is a night event seeded by the day, so a reload
// gives the same night. 'bifrost' covers both void areas (Bifrost Crossing + the Rift Shrine), 1 night in 4 once the
// Crossing has been seen (never on day 0, never two nights running); 'mossglen' / 'hollows' / 'vanaheim' are the rarer
// world event (1 night in 10, only when there's no Bifrost storm). It starts as dusk turns to night (t 0.8) and ends at
// dawn (t 0.25). In the storm region: rifts open far more often (FIRST 10-20 s, EVERY 40-70 s, still one at a time),
// tier weights [35, 45, 20], Rift Marks +25% (factions.onRift), storm-only rift spots (Bifrost, the Shrine), violet /
// red sky cracks (rift_tear_minor high up), cold-fire motes and short point-light flashes; no bloom, no screen flash.
// Ravenhold sees the Bifrost storm in its sky. NPC storm / morning-after lines, morning toast scenes, pet barks and the
// Guild's repeatable Storm Watch bounty hang off S.flags.storm / S.storm / S.flags.stormAfter (data.js).
// QA: ?storm=bifrost|mossglen|hollows|vanaheim forces tonight's region (still night-only), ?storm=off disables storms.
// Smoke / ?peace / ?qa runs have no scheduled storms (deterministic captures) unless ?storm is given or force() is called.
export const STORM_REGIONS = { bifrost: ['bifrost', 'rift'], mossglen: ['mossglen'], hollows: ['hollows'], vanaheim: ['vanaheim'] };
export const STORM_NAME = { bifrost: 'over Bifrost Crossing', mossglen: 'in Mossglen', hollows: 'in the Toadstool Hollows', vanaheim: 'in Vanaheim' };
export const STORM = { first: [10, 20], every: [40, 70], weights: [35, 45, 20], markBonus: 0.25 };
const NIGHT = (t) => t > 0.8 || t < 0.25;
const hash = (n) => { let x = (n | 0) * 374761393 + 668265263; x = (x ^ (x >>> 13)) * 1274126177; return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };
// Bifrost: a raw 1-in-3 roll per night; inside a run of rolled nights only every other one storms (never two nights
// running), which works out at p / (1 + p) = 1 night in 4
const rawB = (day) => day > 0 && hash(day * 7 + 4242) < 1 / 3;
const isB = (day) => { let k = 0; while (k < 64 && rawB(day - k)) k++; return k % 2 === 1; };
// the storm calendar: which region storms on the night that starts on `day` (pure, so smoke can check it)
export function stormAt(day) {
  if (!day || day < 1) return null;
  if (isB(day)) return 'bifrost';
  if (hash(day * 13 + 77) < 0.1) return ['mossglen', 'hollows', 'vanaheim'][Math.floor(hash(day * 5 + 3) * 3) % 3];
  return null;
}
export const stormName = (S) => STORM_NAME[(S.storm || {}).region] || 'tonight';
export const stormHere = (S, area) => { const r = (S.flags || {}).storm; return !!r && (STORM_REGIONS[r] || []).includes(area); };

const BANNER = {
  bifrost: ['RIFT STORM', 'The bridge is cracking with light. Rifts will open tonight. Rift Marks +25%.'],
  mossglen: ['RIFT STORM OVER MOSSGLEN', 'The glade\'s sky is splitting. Rifts will open tonight. Rift Marks +25%.'],
  hollows: ['RIFT STORM IN THE HOLLOWS', 'Cold fire flickers between the toadstools. Rifts tonight. Rift Marks +25%.'],
  vanaheim: ['RIFT STORM OVER MOSSBROOK', 'Violet light cracks over the springs. Rifts tonight. Rift Marks +25%.'],
};
const AFAR = {
  bifrost: 'The Rift above Ravenhold flickers violet and red. A rift storm is breaking over Bifrost Crossing.',
  mossglen: 'Cracks of cold fire over Mossglen. A rift storm is breaking in the glade.',
  hollows: 'The Hollows\' glow-mist turns violet. A rift storm is breaking under the toadstools.',
  vanaheim: 'A violet glow over the vine gate. A rift storm is breaking in Vanaheim.',
};
const END_HERE = { bifrost: 'over the bridge', mossglen: 'over the glade', hollows: 'under the caps', vanaheim: 'over the springs' };
export const STORM_OPEN = ['The storm tears a rift open nearby!', 'Another rift splits the dark!', 'The sky cracks, and something steps through.'];
export const PET_STORM = {   // [onset, during, morning after]; {name} = the pet's name
  wispkit: ['({name} flares bright blue and won\'t leave your shoulder.)', '({name} hums louder with every crack, like it\'s arguing with the sky.)', '({name} dozes, glowing a tired, happy blue.)'],
  glowmoth: ['({name} tucks itself into your collar.)', '({name}\'s eyespots flash violet at every crack of the sky.)', '({name} shakes out its wings and dusts you, pleased.)'],
  lanternfox: ['({name}\'s ears flatten. The light-fish in its tail is racing.)', '({name} points its nose. Another tear, that way!)', '({name} sleeps with its tail over its nose. The fish sleeps too.)'],
  mosspup: ['({name} growls at the sky, then hides behind your boot.)', '({name} digs a little burrow and peeks out of it.)', '({name} shakes off, spraying moss everywhere.)'],
};
const FLASH = ['#c03cc8', '#e0302a'];   // storm lightning: a short point-light flash, violet or red

export class Storms {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.fxT = 6; this.barkT = 70; this.flashes = []; this.lastT = null; this.forced = undefined; }
  get S() { return this.G.S; }
  get F() { return (this.S.flags = this.S.flags || {}); }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.flashes = []; this.fxT = 2 + Math.random() * 3; this.lastT = ctx.clock.t;
    const q = this.G.qs, s = q && q.get('storm');
    if (s && this.forced === undefined) this.forced = s === 'off' ? 'off' : STORM_REGIONS[s] ? s : undefined;
    this.tick(true);
    if (this.F.storm && stormHere(this.S, area) && this.S.storm && this.S.storm.day === this.nightDay()) this.G.toast && setTimeout(() => this.ctx === ctx && this.G.toast('The air crackles. You\'re inside the rift storm.', 2.4), 1900);
  }
  detach() { for (const f of this.flashes) if (f.l) f.l.kill = true; this.flashes = []; this.ctx = null; }
  nightDay() { const t = this.ctx ? this.ctx.clock.t : this.S.t || 0; return t > 0.8 ? (this.S.day || 0) : (this.S.day || 0) - 1; }
  // QA / smoke: force tonight's region ('off' = none, undefined = the calendar again)
  force(region) { this.forced = region; this.tick(false); return this.F.storm || null; }
  scheduled() {
    const G = this.G, S = this.S, F = this.F, t = this.ctx ? this.ctx.clock.t : 0;
    if (!NIGHT(t) || this.forced === 'off') return null;
    if (G.intro && G.intro.active) return null;
    if (!F.intro || F.intro === 'playing') return null;
    if (this.forced) return this.forced;
    if (G.qa || G.peace) return null;   // deterministic captures + smoke: storms only on request
    const r = stormAt(this.nightDay());
    if (r === 'bifrost' && !F.bf_seen) return null;
    return r;
  }
  tick(quiet) {
    const F = this.F, want = this.scheduled(), was = F.storm || null;
    if (want && want !== was) this.onset(want, quiet && was === null && this.S.storm && this.S.storm.day === this.nightDay() && this.S.storm.region === want);
    else if (!want && was) this.end(quiet);
  }
  onset(region, resume) {
    const G = this.G, S = this.S, F = this.F;
    F.storm = region;
    if (resume) return;   // a reload mid-storm: the same storm keeps going (its count is in the save)
    const best = (S.storm && S.storm.best) || 0;
    S.storm = { region, day: this.nightDay(), sealed: 0, best };
    if ((S.quests || {}).stormwatch === 3) S.quests.stormwatch = 0;   // the Guild posts a fresh Storm Watch
    if (stormHere(S, this.area)) { const [a, b] = BANNER[region]; G.toast && G.toast(`<b class="storm">${a}</b><br>${b}`, 4.2, true, true); }
    else G.toast && G.toast(AFAR[region], 3.4);
    this.bark(0, 4.6);
    this.barkT = 60 + Math.random() * 40;
    if (this.G.rifts && stormHere(S, this.area)) this.G.rifts.stormKick();
    G.refreshMarkers && G.refreshMarkers(); G.drawLog && G.drawLog(); G.save && G.save();
  }
  end(quiet) {
    const G = this.G, S = this.S, F = this.F, region = F.storm, st = S.storm || {};
    F.storm = null;
    if ((st.sealed || 0) >= 1) { F.stormAfter = S.day || 0; st.last = st.sealed; }
    if (!quiet && G.toast) {
      const n = st.sealed || 0;
      if (stormHere({ flags: { storm: region } }, this.area)) G.toast(`<b class="storm">DAWN</b><br>The rift storm blows itself out. Gold light spills ${END_HERE[region] || 'over the bridge'}.`, 3.6, true, true);
      else G.toast('Dawn. The Rift above Ravenhold goes quiet again.', 2.6, false, true);   // prio: the summary waits its turn
      G.toast(n ? `Storm weathered: ${n} rift${n > 1 ? 's' : ''} sealed. Folk will want to raise a cup.` : 'The storm passed you by. There\'ll be others.', 3.0);
      if (n) this.bark(2, 6.4);
    }
    G.refreshMarkers && G.refreshMarkers(); G.drawLog && G.drawLog(); G.save && G.save();
  }
  bark(k, delay = 0) {
    const p = this.S.pet, L = p && PET_STORM[p.id]; if (!L || !this.G.toast) return;
    const say = () => this.G.toast(L[k].replace('{name}', p.name), 2.6);
    if (delay) setTimeout(() => this.ctx && say(), delay * 1000); else say();
  }
  // rifts.js: a rift sealed in the storm region
  onSeal(T) {
    const G = this.G, S = this.S; if (!S.storm) return;
    S.storm.sealed = (S.storm.sealed || 0) + 1; S.storm.best = Math.max(S.storm.best || 0, S.storm.sealed);
    const n = S.storm.sealed;
    G.toast && G.toast(`${T.name} sealed! Storm bonus: +25% Rift Marks.`, 2.6);
    if (n === 3) G.toast && G.toast('Three rifts sealed tonight. The storm is losing its temper.', 2.8);
    if (n === 5) G.toast && G.toast('Five! The Guild will be talking about this one for weeks.', 2.8);
    if ((S.quests || {}).stormwatch === 1 && n >= 3) G.setQuest('stormwatch', 2);
    G.drawLog && G.drawLog(); G.refreshMarkers && G.refreshMarkers();
  }
  update(dt) {
    const ctx = this.ctx; if (!ctx) return;
    const t = ctx.clock.t, t0 = this.lastT ?? t; this.lastT = t;
    this.tick(false);
    const F = this.F; if (!F.storm) return;
    const here = stormHere(this.S, this.area), sky = here || (F.storm === 'bifrost' && this.area === 'ravenhold');
    if (here) {   // the midnight / last-hour toasts
      if (t0 > 0.9 && t < 0.1) this.G.toast && this.G.toast('Midnight. The storm is at its loudest.', 2.4);
      if (t0 < 0.2 && t >= 0.2) this.G.toast && this.G.toast('The storm\'s edge is fraying. Dawn\'s coming.', 2.4);
      if (!this.G.dlg && !this.G.busy && (this.barkT -= dt) <= 0) { this.barkT = 70 + Math.random() * 50; this.bark(1); }
    }
    for (const f of this.flashes) { f.t += dt; if (f.l) f.l.scale = Math.max(0, 1 - f.t / f.dur) * (0.6 + Math.random() * 0.5); if (f.t >= f.dur && f.l) { f.l.kill = true; f.l = null; } }
    this.flashes = this.flashes.filter((f) => f.l);
    if (!sky || (this.fxT -= dt) > 0) return;
    this.fxT = here ? 6 + Math.random() * 4 : 10 + Math.random() * 6;
    this.crack(here ? 1 : 0.55);
  }
  // a sky crack: rift_tear_minor high above and ahead of the hero, cold-fire motes drifting down, a short point-light flash
  crack(k = 1) {
    const ctx = this.ctx, p = ctx.player, E = ctx.effects; if (!p) return;
    const x = p.x + (Math.random() * 2 - 1) * 5, z = p.z - 3 - Math.random() * 4, y = ctx.heightAt(p.x, p.z) + 4.2 + Math.random() * 1.2;
    if (E) { E.spawn('rift_tear_minor', x, y, z, { duration: 1.1 + Math.random() * 0.6, fadeIn: 0.12 }); E.spawn('coldfire_motes', x * 0.5 + p.x * 0.5, y - 2.4, z + 1.5, { duration: 2.4 }); }
    const col = FLASH[Math.random() < 0.5 ? 0 : 1];
    const l = ctx.addGlow ? ctx.addGlow(x, y - 1.2, z + 1.0, { color: col, intensity: 5 * k, range: 7, fadeIn: 0.02, lift: 0 }) : null;
    if (l) this.flashes.push({ l, t: 0, dur: 0.35 + Math.random() * 0.2 });
    this.G.audio && this.G.audio.sfx && this.G.audio.sfx('rumble');
    this.cracks = (this.cracks || 0) + 1;
  }
  state() { const S = this.S; return { storm: this.F.storm || null, here: stormHere(S, this.area), sched: this.scheduled(), forced: this.forced ?? null, run: S.storm || null, after: this.F.stormAfter ?? null, cracks: this.cracks || 0, flashes: this.flashes.length }; }
}
