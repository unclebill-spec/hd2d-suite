// Hearthmoor, Stage 5 part 1: the Lantern Eve opening (day 0, dusk, the Plaza). Plays once, on a new game only:
//   lanterns  villagers light fish-orb lanterns (sky_lantern + a warm light_pool under each + sparkles) and let them go;
//             they float up as glowing points of light (two warm point lights ride along, inside the glow-light cap)
//   talk      Bram, Grandpa Alder, Tib and Marla say a few lines in the dialogue panel
//   tear      a violet-red tear (rift_tear) flickers open over the moss gate; the lanterns stop dead in the air
//   fight     a cold-fire wraith slips out of it (def 'evewraith': not light-shy, gentle) and the first fight happens
//             under the lanterns; input is free, the skip chip stays up
//   after     the tear seals, the lanterns drift on, a few lines, and the three errands follow as the Lantern Eve tasks
// Skip any time: Esc, controller B, or a tap / click on the 'skip' chip. S.flags.intro = 'done' | 'skipped' is saved,
// and Continue never replays it (a save made mid-intro, 'playing', counts as skipped on load).
export const EVE_T = 0.76;   // named dusk: blue sky, lamps coming on
const RELEASE = [[-2.4, -1.4], [-0.9, 0.7], [1.3, 1.1], [2.7, -0.5], [-3.3, 1.5], [0.4, -2.3], [3.3, 2.4]];
const BRAM_AT = [-0.9, 1.9];
const WRAITH = { id: 'eve_wraith', role: 'wraith', def: 'evewraith', noLoot: true };

export class Intro {
  constructor(G) { this.G = G; this.active = false; this.step = null; this.t = 0; this.lan = []; this.drift = []; this.lights = []; }
  blocking() { return this.active && (this.step === 'lanterns' || this.step === 'tear'); }   // cinematic beats: no walking
  state() {
    return { active: this.active, step: this.step, flag: (this.G.S.flags || {}).intro || null,
             lanterns: this.lan.length, rising: this.lan.filter((l) => l.up > 0.05).length, maxUp: Math.max(0, ...this.lan.map((l) => l.up)),
             tear: !!this.tear, wraith: !!(this.wraith && this.wraith.state !== 'dead' && this.wraith.state !== 'gone'), frozen: !!this.frozen };
  }
  // new game in the Plaza -> play; `force` lets the smoke test replay it to check the skip paths
  start(force = false) {
    const G = this.G, ctx = G.ctx, F = (G.S.flags = G.S.flags || {});
    if (!ctx || G.area !== 'plaza' || this.active || (F.intro && !force)) return false;
    this.active = true; this.step = 'lanterns'; this.t = 0; this.frozen = false; F.intro = 'playing';
    G.S.t = EVE_T; ctx.clock.set(EVE_T);
    $('introSkip').hidden = false;
    const fx = ctx.effects;
    this.lan = RELEASE.map(([x, z], i) => {
      const y = ctx.heightAt(x, z);
      const l = { x, z, y0: y + 0.8, up: 0, rel: 0.5 + i * 0.32, sway: i * 1.7, f: null, pool: null };
      l.f = fx && fx.spawn('sky_lantern', x, l.y0, z, { duration: 1e9, fadeIn: 0.6 });
      l.pool = fx && fx.spawn('light_pool', x, y, z + 0.03, { duration: 1e9, fadeIn: 0.6 });
      return l;
    });
    this.lights = [0, 2].map((i) => ctx.addGlow ? ctx.addGlow(RELEASE[i][0], this.lan[i].y0, RELEASE[i][1], { color: '#ffb84a', intensity: 6, range: 5.0, fadeIn: 0.8, lift: 0 }) : null);
    this.bram = ctx.npc('eve_bram') || ctx.addNpc({ id: 'eve_bram', role: 'innkeeper', name: 'Bram of the Kettle & Key', pos: BRAM_AT.slice(), facing: 'down', behavior: 'idle' });
    G.audio.sfx('quest');
    return true;
  }
  update(dt) {
    const G = this.G, ctx = G.ctx; if (!ctx) return;
    if (this.drift && this.drift.length) {
      for (const l of this.drift) if (l.f) { l.up += dt * 0.5; l.f.y = l.y0 + l.up; }
      if (this.drift.every((l) => !l.f || l.f.t >= l.f.dur)) this.drift = [];
    }
    if (!this.active) return;
    this.t += dt;
    for (const l of this.lan) {   // rise (unless the tear has frozen them), sway, and carry their lights
      if (this.t < l.rel || this.frozen) continue;
      if (!l.sent) { l.sent = true; ctx.effects && ctx.effects.spawn('sparkle_burst', l.x, l.y0 - 0.3, l.z + 0.05); if (l.pool) l.pool.dur = l.pool.t + 6; }
      l.up += dt * (0.42 + (l.sway % 1) * 0.12);
      if (l.f) { l.f.y = l.y0 + l.up; l.f.x = l.x + Math.sin(this.t * 0.8 + l.sway) * 0.18; }
      if (l.up > 9 && l.f && l.f.dur > 1e8) l.f.dur = l.f.t + 0.3;   // gone into the sky: dither out
    }
    this.lights.forEach((g, k) => { const l = this.lan[k * 2]; if (g && l && l.f) { g.pos.set(l.f.x, l.f.y, l.z); g.scale = Math.max(0, 1 - l.up / 8); } });
    if (this.step === 'lanterns' && this.t > 3.2 && !G.dlg) { this.step = 'talk'; this.talk(); }
    else if (this.step === 'tear' && this.t - this.t0 > 2.2 && !this.wraith) this.spawnWraith();
    else if (this.step === 'fight') {
      const e = this.wraith;
      if (!e || e.state === 'dead' || e.state === 'gone') { this.step = 'after'; this.after(); }
    }
  }
  say(id, pages, then) {
    const G = this.G, a = G.ctx.npc(id) || { id, name: id, role: id };
    G.openDialogue(a, { pages, then: () => { if (this.active && then) then(); } });
  }
  talk() {
    this.say('eve_bram', ['Lantern Eve, friends! Light your lantern, whisper your wish to the little fish inside, and let it go.',
                          'Up they swim, all the way to the Rainbow Rift. My gran swore the Rift reads every single wish.'],
      () => this.say('elder', ['Look at them rise. Forty Lantern Eves I have watched, and the sky has never once looked back at us.'],
        () => this.say('kid', ['Mine is the wobbly one! I wished for Pudding to come home. She ran off chasing moths again.'],
          () => this.say('baker', ['And I wished for an extra pair of hands with the bread. Welcome to Hearthmoor, dear. You picked a lovely night to arrive.'],
            () => this.openTear()))));
  }
  openTear() {
    const G = this.G, ctx = G.ctx;
    this.step = 'tear'; this.t0 = this.t; this.frozen = true;
    const g = ctx.fx && ctx.fx.portal_0, x = g ? g.x : -1.4, z = g ? g.z : -8.5, y = (g ? g.y : ctx.heightAt(x, z)) + 0.7;
    this.tearAt = [x, y, z];
    this.tear = ctx.effects && ctx.effects.spawn('rift_tear', x, y, z + 0.45, { duration: 1e9, fadeIn: 0.5, onTop: true });
    this.tearLight = ctx.addGlow ? ctx.addGlow(x, y + 0.6, z + 0.6, { color: '#c03cc8', intensity: 7, range: 6, fadeIn: 0.6, lift: 0 }) : null;
    ctx.effects && ctx.effects.spawn('glyph_burst', x, y - 0.6, z + 0.3);
    G.audio.sfx('portal');
    G.toast('A violet-red tear flickers open over the moss gate. The lanterns stop dead in the air.', 3.0);
  }
  spawnWraith() {
    const G = this.G, ctx = G.ctx, C = G.combat;
    const [x, , z] = this.tearAt;
    const sp = { ...WRAITH, pos: [x + 0.2, z + 1.6] };
    this.wraith = C.spawnEnemy(sp, true);
    this.wraith.home = [0.2, -0.6];   // it means the Plaza: leash from the square, not the gate
    if (!C.peace) { this.wraith.state = 'chase'; this.wraith.target = ctx.player; }
    this.say('eve_bram', ['Cold fire?! Everyone behind me! Hero, the lanterns are with you: drive it back!'], () => {
      this.step = 'fight';
      G.toast(G.hintFight ? G.hintFight() : 'Fight! Attack: R (controller X, ⚔ on the pad). Guard C, roll X.', 3.4);
    });
  }
  after() {
    const G = this.G, ctx = G.ctx;
    this.frozen = false;
    if (this.tear) { this.tear.dur = this.tear.t + 0.4; this.tear = null; }
    if (this.tearLight) { this.tearLight.kill = true; this.tearLight = null; }
    G.audio.sfx('quest');
    this.say('elder', ['That tear was no Lantern Eve trick. Something cold is leaning on the Rift.'],
      () => this.say('baker', ['Shoo the worry for tonight, Alder. The festival still needs us. Come by my stall, dear: Bram is waiting on his Lantern Eve loaf.'],
        () => this.say('kid', ['And Pudding! Please find Pudding?'], () => this.finish('done'))));
  }
  finish(how) {
    const G = this.G, ctx = G.ctx;
    this.cleanup(how === 'skipped');
    G.S.flags.intro = how;
    G.toast(how === 'done' ? 'Lantern Eve tasks are in your quest log (J): Marla, Wren and Tib need a hand.' : 'Intro skipped. Lantern Eve tasks are in your quest log (J).', 3.2);
    G.refreshMarkers && G.refreshMarkers();
    G.save();
  }
  skip() { if (this.active) this.finish('skipped'); return true; }
  cleanup(hard) {
    const G = this.G, ctx = G.ctx;
    this.active = false; this.step = null; this.frozen = false;
    $('introSkip').hidden = true;
    if (G.dlg) G.dropDialogue();
    for (const l of this.lan) { if (l.f) l.f.dur = l.f.t + (hard ? 0.3 : 0.3 + 6 + Math.random() * 3); if (l.pool) l.pool.dur = l.pool.t + 0.3; }
    this.drift = hard ? [] : this.lan;   // after the fight the lanterns drift on into the dusk, still rising
    this.lan = [];
    for (const g of this.lights) if (g) g.kill = true;
    this.lights = [];
    if (this.tear) { this.tear.dur = this.tear.t + 0.3; this.tear = null; }
    if (this.tearLight) { this.tearLight.kill = true; this.tearLight = null; }
    const e = this.wraith; this.wraith = null;
    if (e && e.state !== 'dead' && e.state !== 'gone' && G.combat.ctx) G.combat.kill(e, true);
    if (this.bram && ctx) { ctx.removeNpc(this.bram); this.bram = null; }
  }
  // a load / area change mid-intro drops it (the flag says 'skipped' so it never replays)
  abandon() { this.drift = []; if (this.active) { this.active = false; this.step = null; this.lan = []; this.lights = []; this.tear = null; this.tearLight = null; this.wraith = null; this.bram = null; $('introSkip').hidden = true; this.G.S.flags.intro = 'skipped'; } }
}
const $ = (id) => document.getElementById(id);
