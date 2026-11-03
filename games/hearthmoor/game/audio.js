// Hearthmoor ambient audio: tiny procedural WebAudio (no files). A soft two-voice pad, music-box plucks on a
// pentatonic scale, birds by day, crickets at night, a wind shimmer in Mossglen, and small event chimes.
// Starts on the first user gesture; M toggles mute (saved).
// Music (2026-10-19): realm loops from audio/music/*.ogg (procedural, CC0; tools/hearthmoor/gen_realm_music.py, ledger audio/LICENSES.md),
// decoded into AudioBuffers and looped by buffer length (gapless; not <audio loop>), crossfaded on area / battle / boss changes.
// While a track plays the ambient plucks, birds and crickets duck ~70% (not muted). A file that fails to load = the synth alone.
// Music volume + music mute live in the options card (saved: hearthmoor-music-vol, hearthmoor-music-mute).
const SCALE = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21];     // major pentatonic, two octaves
const CHORDS = [[0, 4, 7], [5, 9, 12], [-3, 0, 4], [7, 11, 14]];   // I IV vi V
const ROOT = 349.23;   // F4
const hz = (semi) => ROOT * Math.pow(2, semi / 12);
// area id -> realm theme (every live area; an unknown id falls back to Midgard)
const REALM_OF = {};
for (const a of ['plaza', 'lane', 'mossglen', 'hollows', 'rift', 'ravenhold', 'bifrost', 'temple', 'forge']) REALM_OF[a] = 'midgard';
for (const a of ['vanaheim', 'vh_village', 'vh_garden', 'rotwood', 'verdant']) REALM_OF[a] = 'mossbrook';   // [VANAHEIM] music_mossbrook.ogg (Sound, 2026-10-28)
for (const a of ['alfheim', 'lumen_court', 'wispwood', 'prismvault']) REALM_OF[a] = 'alfheim';
for (const a of ['svartalfheim', 'forge_hall', 'glowmines', 'clockdeep', 'clockdeep2']) REALM_OF[a] = 'svartalfheim';
for (const a of ['jotunheim', 'jt_hall', 'rimecaves', 'barrow', 'barrow2']) REALM_OF[a] = 'jotunheim';
for (const a of ['muspelheim', 'mp_hall', 'lavafalls', 'caldera', 'caldera2']) REALM_OF[a] = 'muspelheim';
for (const a of ['niflheim', 'nf_home', 'iceglow', 'frozenspire', 'frozenspire2', 'frozen_rift']) REALM_OF[a] = 'niflheim';
for (const a of ['asgard', 'gs_hall', 'gs_temple', 'reliquary', 'reliquary2']) REALM_OF[a] = 'asgard';
for (const a of ['helheim', 'hh_shore', 'hh_archive', 'ossuary', 'ossuary2']) REALM_OF[a] = 'helheim';   // [HELHEIM] music_helheim.ogg (Sound, 2026-10-29; waltz, 8-bar loop)
export const MUSIC_REALMS = REALM_OF;
export const MUSIC_TRACKS = ['midgard', 'mossbrook', 'helheim', 'alfheim', 'svartalfheim', 'jotunheim', 'muspelheim', 'niflheim', 'asgard', 'battle', 'boss'];
export const BOSS_TRACKS = [];   // boss ids that ship music_boss_<id>.ogg (add an id here when its file lands; empty = every boss plays music_boss.ogg)
const MUSIC_DIR = 'audio/music/';
// [SFX FILES 2026-11-03] sample SFX (Hearthmoor Sound packs 1-3 + Bloomtide; ledger audio/LICENSES.md) in audio/sfx/.
// kind -> [files (random-pick, no repeat of the last), volume, throttle ms, procedural fallback kind]. Lazy-loaded on first use and
// decoded with the shared AudioContext; until a buffer is ready, or if every file fails, the procedural sound below plays instead.
const SFX_DIR = 'audio/sfx/';
const v = (b, n) => [b, ...Array.from({ length: n - 1 }, (_, i) => b.replace(/(\.ogg)$/, '') + '_' + (i + 2))];
const SFX = {
  swing: [['melee_swing'], 0.5, 0], hit: [[...v('melee_hit', 3), 'hit_juice_1', 'hit_juice_2', 'hit_juice_3'], 0.6, 60], hurt: [['hurt'], 0.6, 150],
  guard: [['guard'], 0.55, 0], dodge: [['dodge'], 0.45, 0], defeat: [['defeat'], 0.55, 100], down: [['down'], 0.65, 0],
  rumble: [['rumble', 'thunder_far'], 0.5, 3000], spell: [['spell_coldfire'], 0.5, 0],
  spell_light: [['spell_light'], 0.5, 0, 'spell'], spell_dark: [['spell_dark'], 0.5, 0, 'spell'], spell_nature: [['spell_nature'], 0.5, 0, 'spell'],
  heal: [['heal'], 0.45, 400, 'save'], pickup: [['loot_pickup', 'pickup_juice_1', 'pickup_juice_2', 'pickup_juice_3'], 0.5, 80],
  coin: [['coin_pickup', 'coin_juice_1', 'coin_juice_2'], 0.5, 80, 'pickup'], chest: [['chest_open'], 0.6, 0, 'pickup'],
  blip: [['ui_click', 'ui_click_juice_1', 'ui_click_juice_2'], 0.35, 50], save: [['ui_confirm'], 0.45, 0], confirm: [['ui_confirm'], 0.45, 0, 'save'],
  levelup: [['levelup_chime'], 0.6, 0, 'quest'], portal: [['rift_open'], 0.55, 0], rift_seal: [['rift_seal'], 0.6, 0, 'quest'],
  pet: [['pet_chirp'], 0.4, 1000, 'blip'], door: [['door'], 0.5, 0, 'blip'], splash: [['water_splash'], 0.5, 0, 'pickup'],
  quest: [['stinger_quest_complete'], 0.55, 0], quest_progress: [['quest_progress'], 0.5, 0, 'quest'], quest_new: [['quest_new'], 0.5, 0, 'pickup'],
  summon: [['summon'], 0.5, 0], buy: [['shop_buy'], 0.5, 0, 'pickup'], bank: [['bank_coins'], 0.5, 0, 'pickup'],
  craft: [['craft_done'], 0.55, 0, 'quest'], craft_rare: [['stinger_craft_success'], 0.55, 0, 'quest'], plant: [['plant_seed'], 0.5, 0, 'pickup'],
  harvest: [['harvest'], 0.5, 0, 'quest'], stat: [['stat_point'], 0.5, 0, 'pickup'], equip: [['equip'], 0.5, 0, 'pickup'], gem: [['gem_socket'], 0.5, 0, 'quest'],
  menu_open: [['menu_open'], 0.4, 0, null], menu_close: [['menu_close'], 0.4, 0, null], error: [['ui_error'], 0.45, 0, 'blip'], gate_locked: [['gate_locked'], 0.5, 0, 'blip'],
  boss_crit: [['boss_crit'], 0.55, 100, 'hit'], boss_phase: [['boss_phase'], 0.6, 0, 'rumble'], soul: [['soul_pickup'], 0.5, 80, 'pickup'], gloam: [['gloam_wisp'], 0.4, 1000, null],
  discovery: [['stinger_discovery'], 0.55, 0, 'quest'], rare_pickup: [['stinger_rare_pickup'], 0.55, 0, 'pickup'],
  thunder_rune: [['thunder_rune', 'thunder_rune_juice_1', 'thunder_rune_juice_2'], 0.55, 200, 'rumble'], raven: [v('raven_caw', 3), 0.35, 1500, null],
  bloom_hit: [['harvest', 'pickup_juice_1', 'pickup_juice_2', 'pickup_juice_3'], 0.5, 0, 'lampchime'], bloom_perfect: [['bloom_perfect'], 0.55, 0, 'pickup'],
  bloom_miss: [['bloom_miss'], 0.45, 0, 'blip'], bloom_win: [['stinger_quest_complete'], 0.55, 0, 'quest'], bloom_lose: [['bloom_lose'], 0.5, 0, 'blip'],
};
// area -> ambience bed (looped on the ambient bus, so music ducks it like the plucks); Asgard exteriors per pack3/README
const BEDS = { asgard: 'amb_asgard_loop', gs_hall: 'amb_asgard_loop', gs_temple: 'amb_asgard_loop', reliquary: 'amb_asgard_loop', reliquary2: 'amb_asgard_loop',
  helheim: 'amb_helheim_loop', hh_shore: 'amb_helheim_loop', ossuary: 'amb_ossuary_loop', ossuary2: 'amb_ossuary_loop', plaza: 'amb_plaza_loop' };
for (const k of ['grass', 'stone', 'wood', 'snow']) SFX['step_' + k] = [v('footstep_' + k, 3), 0.25, 0, null];
for (const k of ['dirt', 'water']) SFX['step_' + k] = [v('footstep_' + k, 2), 0.25, 0, null];
// footstep surface by area (no per-tile lookup exists; EVENT_MAP default: halls wood, snow realms snow, dungeons stone, else grass)
const SURF = (a) => /hall|home|forge|temple|_court|archive/.test(a) ? 'wood' : /^(niflheim|nf_|iceglow|frozen|jotunheim|jt_|rimecaves)/.test(a) ? 'snow'
  : /hollows|ossuary|barrow|clockdeep|reliquary|glowmines|caldera|prismvault|rift/.test(a) ? 'stone' : /shore/.test(a) ? 'water' : /lane|rotwood|vh_garden/.test(a) ? 'dirt' : 'grass';
const RAVEN_AREAS = { asgard: 1, ravenhold: 1 };   // ambient raven caws (pack3)
const DUCK = 0.3;        // ambient level while music plays (a ~70% duck)
const XFADE = 1.6;       // crossfade seconds
const BATTLE_HOLD = 4;   // seconds the battle theme lingers after the last foe stops chasing

const WX_LOOPS = { drizzle: 'rain_light_loop', rain: 'rain_heavy_loop', snow: 'snow_hush_loop' };   // [SOUND] weather.js kinds -> loop files
export class Ambient {
  constructor() { this.ctx = null; this.muted = localStorage.getItem('hearthmoor-mute') === '1'; this.area = 'plaza'; this.night = 0; this.timers = [];
    const v = parseFloat(localStorage.getItem('hearthmoor-music-vol')); this.musicVol = Number.isFinite(v) ? Math.min(1, Math.max(0, v)) : 0.6;
    this.musicMuted = localStorage.getItem('hearthmoor-music-mute') === '1';
    const sv = parseFloat(localStorage.getItem('hearthmoor-sfx-vol')); this.sfxVol = Number.isFinite(sv) ? Math.min(1, Math.max(0, sv)) : 1;
    this.bufs = {}; this.failed = {}; this.cur = null; this.battle = false; this.boss = false; this.battleT = 0; }
  start() {
    if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
    const c = this.ctx = new AC();
    this.master = c.createGain(); this.master.gain.value = this.muted ? 0 : 0.5; this.master.connect(c.destination);
    this.sfxBus = c.createGain(); this.sfxBus.gain.value = this.sfxVol; this.sfxBus.connect(this.master);   // sound-effects bus; music and ambience stay on their own buses
    // ambient bus (plucks, birds, crickets, shimmer): ducked while music plays; sfx go through this.sfxBus into the master
    this.amb = c.createGain(); this.amb.gain.value = 1; this.amb.connect(this.master);
    this.musicBus = c.createGain(); this.musicBus.gain.value = this.musicGain(); this.musicBus.connect(this.master);
    // echo for the plucks
    this.echo = c.createDelay(1.0); this.echo.delayTime.value = 0.38;
    const fb = c.createGain(); fb.gain.value = 0.32; const ef = c.createBiquadFilter(); ef.type = 'lowpass'; ef.frequency.value = 2200;
    this.echo.connect(ef); ef.connect(fb); fb.connect(this.echo); ef.connect(this.master);
    this.ambEcho = c.createGain(); this.ambEcho.connect(this.echo); this.ambEcho.connect(this.master); this.ambEcho.gain.value = 1;   // ambient plucks (+ their echo), ducked with amb
    // pad: two detuned triangles per chord tone through a gentle lowpass
    this.padBus = c.createGain(); this.padBus.gain.value = 0.05;
    const lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900; this.padBus.connect(lp); lp.connect(this.amb);
    this.voices = [0, 1, 2].map(() => { const o1 = c.createOscillator(), o2 = c.createOscillator(); o1.type = o2.type = 'triangle'; o2.detune.value = 7;
      const g = c.createGain(); g.gain.value = 0.33; o1.connect(g); o2.connect(g); g.connect(this.padBus); o1.start(); o2.start(); return [o1, o2]; });
    this.chord = 0; this.setChord();
    this.loop(() => { this.chord = (this.chord + 1) % CHORDS.length; this.setChord(); }, 7000);
    this.tick();
    this.pickMusic(); this.bed(this.area);
  }
  // ---- music channel
  musicGain() { return this.musicMuted ? 0 : this.musicVol * 0.9; }
  // [ASGARD 2026-10-31] per-boss music hook: a boss id maps to music_boss_<id>.ogg when that file exists (fetch ok), else music_boss.ogg. No new files shipped.
  bossTrack() { const k = this.bossId && 'boss_' + this.bossId; return k && BOSS_TRACKS.includes(this.bossId) && !this.failed[k] ? k : 'boss'; }   // only ids with a shipped music_boss_<id>.ogg are requested (no 404s)
  want() { return this.boss ? this.bossTrack() : this.battle ? 'battle' : (REALM_OF[this.area] || 'midgard'); }
  load(name) {
    if (this.bufs[name] || this.failed[name] || !this.ctx) return this.bufs[name] || null;
    this.bufs[name] = fetch(MUSIC_DIR + 'music_' + name + '.ogg').then((r) => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
      .then((ab) => new Promise((ok, no) => this.ctx.decodeAudioData(ab, ok, no)))
      .catch(() => { this.failed[name] = true; delete this.bufs[name]; return null; });
    return this.bufs[name];
  }
  pickMusic() {
    if (!this.ctx) return;
    const name = this.want();
    if (this.cur && this.cur.name === name) return;
    if (this.musicMuted || this.musicVol <= 0) { this.stopMusic(); this.cur = { name, src: null, g: null }; return; }   // remember; play when unmuted
    const tok = this.pickTok = (this.pickTok || 0) + 1;
    const p = this.load(name); if (!p) { this.stopMusic(); return; }
    p.then((buf) => {
      if (tok !== this.pickTok || !this.ctx) return;
      if (!buf && name !== 'boss' && name.startsWith('boss_')) { this.cur = null; this.pickMusic(); return; }   // no music_boss_<id>.ogg: fall back to music_boss.ogg
      if (!buf) { this.stopMusic(); return; }   // no file: the procedural pad + plucks carry on alone
      const c = this.ctx, t = c.currentTime, src = c.createBufferSource(), g = c.createGain();
      src.buffer = buf; src.loop = true; src.loopStart = 0; src.loopEnd = buf.duration;   // loop by buffer length: gapless
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(1, t + XFADE);
      src.connect(g); g.connect(this.musicBus); src.start(t);
      this.fadeOut(this.cur); this.cur = { name, src, g }; this.duck(true);
    });
  }
  fadeOut(m) {
    if (!m || !m.src) return;
    const t = this.ctx.currentTime; m.g.gain.cancelScheduledValues(t); m.g.gain.setValueAtTime(Math.max(0.0001, m.g.gain.value), t);
    m.g.gain.exponentialRampToValueAtTime(0.0001, t + XFADE); try { m.src.stop(t + XFADE + 0.05); } catch (e) { /* already stopped */ }
  }
  stopMusic() { this.fadeOut(this.cur); this.cur = null; this.duck(false); }
  duck(on) { this.ducked = on; if (!this.amb) return; const t = this.ctx.currentTime; for (const n of [this.amb, this.ambEcho]) n.gain.setTargetAtTime(on ? DUCK : 1, t, 0.5); }
  // per frame from game.js: engaged = a foe is chasing / attacking; boss = one of them is a boss (sticky until the battle ends)
  setBattle(engaged, boss, dt = 0) {
    this.battleT = engaged ? BATTLE_HOLD : Math.max(0, this.battleT - dt);
    const b = this.battleT > 0, bs = b && (this.boss || (engaged && !!boss));
    const id = bs ? (typeof boss === 'string' && engaged ? boss : this.bossId) : null;   // boss may be the boss id (string) or a plain true
    if (b !== this.battle || bs !== this.boss || id !== this.bossId) { this.battle = b; this.boss = bs; this.bossId = id; this.pickMusic(); }
  }
  setMusicVol(v) {
    this.musicVol = Math.min(1, Math.max(0, v)); localStorage.setItem('hearthmoor-music-vol', String(this.musicVol)); this.applyMusic();
  }
  setSfxVol(v) {
    this.sfxVol = Math.min(1, Math.max(0, v));
    try { localStorage.setItem('hearthmoor-sfx-vol', String(this.sfxVol)); } catch (e) { /* private mode */ }
    if (this.sfxBus && this.ctx) this.sfxBus.gain.setTargetAtTime(this.sfxVol, this.ctx.currentTime, 0.05);
  }
  toggleMusic() { this.musicMuted = !this.musicMuted; localStorage.setItem('hearthmoor-music-mute', this.musicMuted ? '1' : '0'); this.applyMusic(); return this.musicMuted; }
  applyMusic() {
    if (!this.ctx) return;
    this.musicBus.gain.setTargetAtTime(this.musicGain(), this.ctx.currentTime, 0.1);
    if (this.musicGain() <= 0) { if (this.cur && this.cur.src) { const n = this.cur.name; this.stopMusic(); this.cur = { name: n, src: null, g: null }; } }
    else if (!this.cur || !this.cur.src) { this.cur = null; this.pickMusic(); }
  }
  musicState() { return { want: this.want(), track: this.cur && this.cur.src ? this.cur.name : null, vol: this.musicVol, muted: this.musicMuted, ducked: !!this.ducked,
    amb: this.amb ? this.amb.gain.value : null, battle: this.battle, boss: this.boss, bossId: this.bossId || null, failed: Object.keys(this.failed) }; }
  setChord() {
    const t = this.ctx.currentTime;
    CHORDS[this.chord].forEach((s, i) => { for (const o of this.voices[i]) o.frequency.setTargetAtTime(hz(s - 12), t, 0.8); });
  }
  loop(fn, ms) { this.timers.push(setInterval(fn, ms)); }
  tick() {
    // plucks, birds or crickets: schedule the next one at a random gap
    const gap = 700 + Math.random() * 1900;
    this.timers.push(setTimeout(() => {
      if (!this.muted && document.visibilityState !== 'hidden') {
        const glade = this.area === 'mossglen';
        if (Math.random() < (glade ? 0.75 : 0.55)) this.pluck(SCALE[Math.floor(Math.random() * SCALE.length)] + (glade ? 12 : 0), glade ? 0.07 : 0.06, 0, true);
        if (this.night < 0.5 && Math.random() < 0.18) this.bird();
        if (this.night > 0.5 && Math.random() < 0.35) this.cricket();
        if (glade && Math.random() < 0.2) this.shimmer();
        if (RAVEN_AREAS[this.area] && this.night < 0.5 && Math.random() < 0.04) this.sfx('raven');   // pack3 raven caw (Asgard / Ravenhold, by day)
      }
      this.tick();
    }, gap));
  }
  env(g, t, a, peak, d) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + d); }
  pluck(semi, vol = 0.06, when = 0, amb = false) {
    if (!this.ctx) return;
    const c = this.ctx, t = c.currentTime + when, o = c.createOscillator(), g = c.createGain();
    o.type = 'sine'; o.frequency.value = hz(semi); this.env(g, t, 0.006, vol, 0.9);
    o.connect(g); if (amb) g.connect(this.ambEcho); else { g.connect(this.sfxBus || this.master); g.connect(this.echo); } o.start(t); o.stop(t + 1.0);
  }
  bird() {
    const c = this.ctx, t = c.currentTime, o = c.createOscillator(), g = c.createGain();
    o.type = 'sine'; const f = 2400 + Math.random() * 1400;
    o.frequency.setValueAtTime(f, t); o.frequency.exponentialRampToValueAtTime(f * 1.5, t + 0.07); o.frequency.exponentialRampToValueAtTime(f * 1.1, t + 0.14);
    this.env(g, t, 0.01, 0.018, 0.14); o.connect(g); g.connect(this.amb); o.start(t); o.stop(t + 0.2);
  }
  cricket() {
    const c = this.ctx, t0 = c.currentTime;
    for (let i = 0; i < 3; i++) {
      const t = t0 + i * 0.09, o = c.createOscillator(), g = c.createGain();
      o.type = 'square'; o.frequency.value = 4300; this.env(g, t, 0.004, 0.006, 0.04);
      const bp = c.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 4300; bp.Q.value = 8;
      o.connect(bp); bp.connect(g); g.connect(this.amb); o.start(t); o.stop(t + 0.06);
    }
  }
  shimmer() { [19, 23, 26].forEach((s, i) => this.pluck(s + 12, 0.025, i * 0.11, true)); }
  // ---- sample SFX (files) with procedural fallback
  sbuf(f) {
    const k = this.sb || (this.sb = {});
    if (!(f in k)) k[f] = fetch(SFX_DIR + f + '.ogg').then((r) => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
      .then((ab) => new Promise((ok, no) => this.ctx.decodeAudioData(ab, ok, no))).then((b) => (k[f] = b)).catch(() => (k[f] = null));
    return k[f];
  }
  sample(kind) {   // true = handled by a file (or throttled); false = caller plays the procedural sound
    const e = SFX[kind]; if (!e) return false;
    const [files, vol, thr] = e, now = performance.now(), last = this.sLast || (this.sLast = {});
    if (thr && now - (last[kind] || -1e9) < thr) return true;
    files.forEach((f) => this.sbuf(f));
    const ready = files.filter((f) => this.sb[f] instanceof AudioBuffer); if (!ready.length) return false;
    const pick = this.sPick || (this.sPick = {}), pool = ready.length > 1 ? ready.filter((f) => f !== pick[kind]) : ready, f = pool[Math.floor(Math.random() * pool.length)];
    pick[kind] = f; last[kind] = now;
    const c = this.ctx, src = c.createBufferSource(), g = c.createGain();
    src.buffer = this.sb[f]; src.playbackRate.value = 0.95 + Math.random() * 0.1; g.gain.value = vol;
    src.connect(g); g.connect(this.sfxBus || this.master); src.start();
    return true;
  }
  bed(area) {   // ambience bed loop for the area (fade 1 s), on the ducked ambient bus
    const name = BEDS[area] || null; if (!this.ctx || (this.bedCur && this.bedCur.name === name)) return;
    const t = this.ctx.currentTime;
    if (this.bedCur && this.bedCur.src) { const o = this.bedCur; o.g.gain.setTargetAtTime(0.0001, t, 0.3); try { o.src.stop(t + 1.2); } catch (e) { /* stopped */ } }
    this.bedCur = { name, src: null };
    if (!name) return;
    const cur = this.bedCur, p = this.sbuf(name);
    Promise.resolve(p).then((b) => {
      if (this.bedCur !== cur || !(b instanceof AudioBuffer)) return;
      const c = this.ctx, src = c.createBufferSource(), g = c.createGain(), t2 = c.currentTime;
      src.buffer = b; src.loop = true; g.gain.setValueAtTime(0.0001, t2); g.gain.linearRampToValueAtTime(0.5, t2 + 1);
      src.connect(g); g.connect(this.amb); src.start(); cur.src = src; cur.g = g;
    });
  }
  wx(kind) {   // [SOUND] weather loop layer (drizzle / rain / snow), on the ambient bus beside the area bed; fade 1 s
    const name = WX_LOOPS[kind] || null; if (!this.ctx || (this.wxCur && this.wxCur.name === name)) return;
    const t = this.ctx.currentTime;
    if (this.wxCur && this.wxCur.src) { const o = this.wxCur; o.g.gain.setTargetAtTime(0.0001, t, 0.3); try { o.src.stop(t + 1.2); } catch (e) { /* stopped */ } }
    this.wxCur = { name, src: null };
    if (!name) return;
    const cur = this.wxCur;
    Promise.resolve(this.sbuf(name)).then((b) => {
      if (this.wxCur !== cur || !(b instanceof AudioBuffer)) return;
      const c = this.ctx, src = c.createBufferSource(), g = c.createGain(), t2 = c.currentTime;
      src.buffer = b; src.loop = true; g.gain.setValueAtTime(0.0001, t2); g.gain.linearRampToValueAtTime(0.4, t2 + 1);
      src.connect(g); g.connect(this.amb); src.start(); cur.src = src; cur.g = g;
    });
  }
  step() { this.sfx('step_' + SURF(this.area || 'plaza')); }   // per footfall from game.js (~0.32 s walk cadence)
  sfx(kind) {
    if (!this.ctx || this.muted) return;
    if (this.sample(kind)) return;
    const e = SFX[kind]; if (e && e.length > 3) { if (e[3]) this.sfx0(e[3]); return; }   // new kinds: their procedural stand-in (null = silent)
    this.sfx0(kind);
  }
  sfx0(kind) {
    if (!this.ctx || this.muted) return;
    if (kind === 'pickup') { this.pluck(14, 0.08); this.pluck(19, 0.08, 0.09); }
    if (kind === 'quest') [0, 4, 7, 12].forEach((s, i) => this.pluck(s + 12, 0.08, i * 0.1));
    if (kind === 'blip') this.pluck(24, 0.02);
    if (kind === 'lampchime') [19, 23, 26].forEach((s2, i) => this.pluck(s2 + 12, 0.03, i * 0.11));   // night lamp catches (engine onLampFlare): the Mossglen wind-shimmer chime, on the sfx bus so music doesn't duck it
    if (kind === 'save') this.pluck(12, 0.05);
    // combat: soft and woody, never harsh
    if (kind === 'swing') this.noise(0.08, 900, 2600, 0.05);
    if (kind === 'hit') { this.noise(0.06, 500, 300, 0.09); this.pluck(5, 0.03); }
    if (kind === 'hurt') { this.pluck(-5, 0.06); this.pluck(-8, 0.05, 0.06); }
    if (kind === 'guard') { this.pluck(17, 0.05); this.noise(0.05, 2400, 1800, 0.05); }
    if (kind === 'dodge') this.noise(0.14, 400, 1400, 0.05);
    if (kind === 'spell') [12, 16, 19].forEach((s2, i) => this.pluck(s2 + 7, 0.04, i * 0.05));
    if (kind === 'summon') [0, 7, 12, 19].forEach((s2, i) => this.pluck(s2 + 5, 0.05, i * 0.07));
    if (kind === 'defeat') [12, 7, 3].forEach((s2, i) => this.pluck(s2, 0.05, i * 0.08));
    if (kind === 'rumble') this.noise(1.1, 90, 50, 0.07);   // rift storm: a low, soft roll of thunder (6.5)
    if (kind === 'down') [7, 3, 0, -5].forEach((s2, i) => this.pluck(s2, 0.06, i * 0.14));
    if (kind === 'portal') {
      const c = this.ctx, t = c.currentTime, n = c.createBufferSource(), b = c.createBuffer(1, c.sampleRate * 0.9, c.sampleRate), d = b.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length);
      n.buffer = b; const f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 3;
      f.frequency.setValueAtTime(300, t); f.frequency.exponentialRampToValueAtTime(2600, t + 0.8);
      const g = c.createGain(); g.gain.value = 0.12; n.connect(f); f.connect(g); g.connect(this.sfxBus || this.master); n.start(t);
      [7, 12, 16, 19].forEach((s, i) => this.pluck(s + 12, 0.04, 0.1 + i * 0.08));
    }
  }
  noise(dur, f0, f1, vol) {
    const c = this.ctx, t = c.currentTime, n = c.createBufferSource(), b = c.createBuffer(1, Math.max(1, c.sampleRate * dur), c.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length);
    n.buffer = b; const f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 2;
    f.frequency.setValueAtTime(f0, t); f.frequency.exponentialRampToValueAtTime(f1, t + dur);
    const g = c.createGain(); g.gain.value = vol; n.connect(f); f.connect(g); g.connect(this.sfxBus || this.master); n.start(t);
  }
  setArea(a) { this.area = a; this.battle = this.boss = false; this.bossId = null; this.battleT = 0; this.pickMusic(); this.bed(a); }
  setNight(n) { this.night = n; }
  toggle() {
    this.muted = !this.muted; localStorage.setItem('hearthmoor-mute', this.muted ? '1' : '0');
    if (this.master) this.master.gain.setTargetAtTime(this.muted ? 0 : 0.5, this.ctx.currentTime, 0.1);
    return this.muted;
  }
}
