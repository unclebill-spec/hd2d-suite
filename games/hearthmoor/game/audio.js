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
const MUSIC_DIR = 'audio/music/';
const DUCK = 0.3;        // ambient level while music plays (a ~70% duck)
const XFADE = 1.6;       // crossfade seconds
const BATTLE_HOLD = 4;   // seconds the battle theme lingers after the last foe stops chasing

export class Ambient {
  constructor() { this.ctx = null; this.muted = localStorage.getItem('hearthmoor-mute') === '1'; this.area = 'plaza'; this.night = 0; this.timers = [];
    const v = parseFloat(localStorage.getItem('hearthmoor-music-vol')); this.musicVol = Number.isFinite(v) ? Math.min(1, Math.max(0, v)) : 0.6;
    this.musicMuted = localStorage.getItem('hearthmoor-music-mute') === '1';
    this.bufs = {}; this.failed = {}; this.cur = null; this.battle = false; this.boss = false; this.battleT = 0; }
  start() {
    if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
    const c = this.ctx = new AC();
    this.master = c.createGain(); this.master.gain.value = this.muted ? 0 : 0.5; this.master.connect(c.destination);
    // ambient bus (plucks, birds, crickets, shimmer): ducked while music plays; sfx stay on the master
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
    this.pickMusic();
  }
  // ---- music channel
  musicGain() { return this.musicMuted ? 0 : this.musicVol * 0.9; }
  // [ASGARD 2026-10-31] per-boss music hook: a boss id maps to music_boss_<id>.ogg when that file exists (fetch ok), else music_boss.ogg. No new files shipped.
  bossTrack() { const k = this.bossId && 'boss_' + this.bossId; return k && !this.failed[k] ? k : 'boss'; }
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
      }
      this.tick();
    }, gap));
  }
  env(g, t, a, peak, d) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + d); }
  pluck(semi, vol = 0.06, when = 0, amb = false) {
    if (!this.ctx) return;
    const c = this.ctx, t = c.currentTime + when, o = c.createOscillator(), g = c.createGain();
    o.type = 'sine'; o.frequency.value = hz(semi); this.env(g, t, 0.006, vol, 0.9);
    o.connect(g); if (amb) g.connect(this.ambEcho); else { g.connect(this.master); g.connect(this.echo); } o.start(t); o.stop(t + 1.0);
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
  sfx(kind) {
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
      const g = c.createGain(); g.gain.value = 0.12; n.connect(f); f.connect(g); g.connect(this.master); n.start(t);
      [7, 12, 16, 19].forEach((s, i) => this.pluck(s + 12, 0.04, 0.1 + i * 0.08));
    }
  }
  noise(dur, f0, f1, vol) {
    const c = this.ctx, t = c.currentTime, n = c.createBufferSource(), b = c.createBuffer(1, Math.max(1, c.sampleRate * dur), c.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length);
    n.buffer = b; const f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 2;
    f.frequency.setValueAtTime(f0, t); f.frequency.exponentialRampToValueAtTime(f1, t + dur);
    const g = c.createGain(); g.gain.value = vol; n.connect(f); f.connect(g); g.connect(this.master); n.start(t);
  }
  setArea(a) { this.area = a; this.battle = this.boss = false; this.bossId = null; this.battleT = 0; this.pickMusic(); }
  setNight(n) { this.night = n; }
  toggle() {
    this.muted = !this.muted; localStorage.setItem('hearthmoor-mute', this.muted ? '1' : '0');
    if (this.master) this.master.gain.setTargetAtTime(this.muted ? 0 : 0.5, this.ctx.currentTime, 0.1);
    return this.muted;
  }
}
