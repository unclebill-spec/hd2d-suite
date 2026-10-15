// [SVARTALFHEIM] The two Mines / Deep rares (story 8.3), on the existing procedural-rare system (rares.js): the Amethyst Basilisk
// (2.5x, roams the Mines and C3 / clockdeep) and the Soot Colossus (2.8x, roams the Mines and C7 / clockdeep2). Both have their own
// boss sheets (rare_basilisk / rare_sootcolossus, added to the area atlases by tools/hearthmoor/svart_art.py EXTRA).
// Basilisk: a gaze cone (1 s eye-flash tell, then -40% player speed for 3 s) and drops 3 amethyst. Colossus: always a Summoner
// (calls sootlings). Deviations: no soot-fall growth (+10% size and damage) and no smother cloud on the Colossus.
import { BASES, RARE_AREAS, Rares } from './rares.js';

Object.assign(BASES, {
  basilisk: { name: 'Amethyst Basilisk', scale: 2.5, hp: 300, dmg: 15, speed: 1.4, reach: 2.6, windup: 0.6, cd: 1.8, aggro: 8, r: 0.7, push: 0.3,
              gaze: { cone: 50, len: 5, slow: 0.4, life: 3, tell: 1.0, every: 7 }, xp: 185 },
  sootcolossus: { name: 'Soot Colossus', scale: 2.8, hp: 320, dmg: 16, speed: 1.0, reach: 2.4, windup: 0.7, cd: 2.0, aggro: 8, r: 0.8, push: 0.2,
                  minion: 'sootling', xp: 195 },
});
Object.assign(RARE_AREAS, {
  glowmines: { bases: ['basilisk', 'sootcolossus'], spots: [[7.4, -4.0], [-8.0, 2.4]] },
  clockdeep: { bases: ['basilisk'], spots: [[0.0, -6.0]] },      // C3 The Glowpool Cistern end of the hall
  clockdeep2: { bases: ['sootcolossus'], spots: [[0.0, -9.0]] },  // C7 Bellows Bridge
});

const BASE_SPEED = 2.6;
export const gaze = { slowT: 0, shown: 0 };
export function updateGaze(ctx, dt) {
  if (gaze.slowT > 0) { gaze.slowT -= dt; if (ctx && ctx.player) ctx.player.speed = BASE_SPEED * (1 - 0.4); if (gaze.slowT <= 0 && ctx && ctx.player) ctx.player.speed = BASE_SPEED; }
}
export function clearGaze(ctx) { gaze.slowT = 0; if (ctx && ctx.player && ctx.player.speed < BASE_SPEED) ctx.player.speed = BASE_SPEED; }

const spawn0 = Rares.prototype.spawn;
Rares.prototype.spawn = function spawn(o = {}) {
  if (o.base === 'sootcolossus' && !o.traits) o = { ...o, traits: ['summoner'] };
  const R = spawn0.call(this, o); if (!R || !R.e) return R;
  const e = R.e, G = this.G, D = R.D, t0 = e.tick, k0 = e.onKill;
  if (D.gaze) {
    let cd = 5, tell = 0, dir = 0;
    e.tick = (en, dt, frozen) => {
      t0(en, dt, frozen);
      const ctx = this.ctx; if (!ctx || frozen || en.state === 'dead' || en.state === 'idle') return;
      const a = en.a, p = ctx.player, d = Math.hypot(p.x - a.x, p.z - a.z);
      if (tell > 0) {
        tell -= dt;
        if (tell <= 0) {
          let da = Math.abs(Math.atan2(p.z - a.z, p.x - a.x) - dir); da = Math.min(da, Math.PI * 2 - da);
          if (d < D.gaze.len && da < D.gaze.cone * Math.PI / 360) { gaze.slowT = D.gaze.life; gaze.shown++; G.toast && G.toast('The basilisk\'s gaze crystallises your boots! (slowed)', 2); }
        }
      } else { cd -= dt; if (cd <= 0 && d < D.gaze.len + 0.5) { cd = D.gaze.every; tell = D.gaze.tell; dir = Math.atan2(p.z - a.z, p.x - a.x); if (ctx.effects && ctx.effects.meta.effects.glitter) ctx.effects.spawn('glitter', a.x, a.y + 1.8, a.z + 0.05, { duration: 1.0 }); } }
    };
    e.onKill = (en) => { k0 && k0(en); G.give && G.give('amethyst', 3); G.toast && G.toast('The basilisk shatters into amethyst. Found: 3 amethyst.', 2.4); };
  }
  return R;
};
