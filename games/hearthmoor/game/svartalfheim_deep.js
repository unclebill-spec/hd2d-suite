// [SVARTALFHEIM] Clockwork Deep room mechanics that need no companion and no alliance choice (story 7):
//   C1 Gearworks Hall: steam vents (0.6 s puff tell, then 1.5 s blast: 12 damage + a push)
//   C7 Bellows Bridge: a bellows gust every 6 s (1 s wheeze tell); hold a chain post (stand beside a bridge brazier) or be pushed back 3 m
// plus the rooms' foe pools (SPAWNS) per the story table (the conquer-only hushblades wait for the alliance choice).
export const VENTS = [[-2.4, 29.0], [2.4, 26.0], [-2.4, 22.0], [2.4, 20.0]];   // C1 (clockdeep, z 18..32)
export const POSTS = [[-4.4, -8.0], [4.4, -8.0], [-4.4, 0.0], [4.4, 0.0], [-4.4, -16.0], [4.4, -16.0]];   // C7 chain posts (clockdeep2, z -16..0): the bridge braziers

export class DeepRooms {
  constructor(sv) { this.sv = sv; this.G = sv.G; this.t = 0; this.v = []; this.gust = { t: 3, tell: false, n: 0 }; this.told = {}; this.hits = 0; }
  get ctx() { return this.sv.ctx; }
  fx(n, x, y, z, o) { const E = this.ctx && this.ctx.effects; return E && E.meta.effects[n] ? E.spawn(n, x, y, z, o || {}) : null; }
  reset() { this.t = 0; this.told = {}; this.hits = 0; this.v = VENTS.map((p, i) => ({ p, ph: 1.3 + i * 1.1, state: 'rest', hit: false })); this.gust = { t: 3, tell: false, n: 0 }; }
  note(k, msg, s = 2.6) { if (this.told[k]) return; this.told[k] = 1; this.G.toast(msg, s); }
  update(dt, area) {
    const c = this.ctx; if (!c || this.G.peace) return;
    this.t += dt;
    if (area === 'clockdeep') this.vents(dt, c);
    if (area === 'clockdeep2') this.gusts(dt, c);
  }
  vents(dt, c) {
    const p = c.player;
    for (const v of this.v) {
      v.ph -= dt;
      const [x, z] = v.p, y = c.heightAt(x, z);
      if (v.state === 'rest' && v.ph <= 0) { v.state = 'tell'; v.ph = 0.6; this.fx('frost_puff', x, y + 0.3, z + 0.05); }
      else if (v.state === 'tell' && v.ph <= 0) { v.state = 'blow'; v.n = (v.n || 0) + 1; v.ph = 1.5; v.hit = false; v.puff = 0; }
      else if (v.state === 'blow') {
        v.puff -= dt; if (v.puff <= 0) { v.puff = 0.35; this.fx('frost_puff', x, y + 0.6, z + 0.05); }
        if (!v.hit && Math.hypot(p.x - x, p.z - z) < 1.1 && Math.abs(p.y - y) < 1.0) {
          v.hit = true; this.hits++;
          this.sv.G.combat.hurtPlayer(12, { x, z }, 0.8);
          this.note('vent', 'A steam vent blasts you! Watch for the white puff first.', 2.4);
        }
        if (v.ph <= 0) { v.state = 'rest'; v.ph = 3.5; }
      }
    }
  }
  gusts(dt, c) {
    const p = c.player, g = this.gust;
    if (p.z > 1.0 || p.z < -17.0) { g.t = Math.max(g.t, 2); return; }   // only on the bridge
    g.t -= dt;
    if (!g.tell && g.t <= 1.0) { g.tell = true; this.fx('frost_puff', -5.4, c.heightAt(-5.4, p.z), p.z); this.fx('frost_puff', 5.4, c.heightAt(5.4, p.z), p.z); this.note('wheeze', 'The bellows wheeze. Hold a chain post (stand by a brazier) or be pushed back!', 2.8); }
    if (g.t <= 0) {
      g.t = 6; g.tell = false; g.n++;
      const post = POSTS.some((q) => Math.hypot(p.x - q[0], p.z - q[1]) < 1.5);
      this.fx('frost_puff', p.x, p.y + 0.5, p.z + 0.05);
      if (post) { this.note('held', 'You hold the chain post. The gust rolls past.', 1.8); return; }
      this.G.combat.shove(p, 0, 1, 3.0);   // pushed back 3 m (toward the south); cozy: no fall damage
      g.pushed = (g.pushed || 0) + 1;
    }
  }
}
// foe pools per room (story 7 table); positions kept off the spawn lines and clear of the bridge / vent lanes
export const ROOM_SPAWNS = {
  clockdeep: [
    { id: 'cd_fc1a', role: 'forgeconstruct', pos: [-1.2, 30.4] }, { id: 'cd_fc1b', role: 'forgeconstruct', pos: [1.4, 23.6] },
    { id: 'cd_so1a', role: 'sootling', pos: [1.0, 27.8] }, { id: 'cd_so1b', role: 'sootling', pos: [-1.0, 21.0] },
    { id: 'cd_fc2', role: 'forgeconstruct', pos: [-1.6, 9.0] }, { id: 'cd_sg2', role: 'sparkgolem', pos: [-1.4, 5.0] },
    { id: 'cd_so3a', role: 'sootling', pos: [1.6, -4.0] }, { id: 'cd_so3b', role: 'sootling', pos: [-1.6, -4.6] },
  ],
  clockdeep2: [
    { id: 'cd_sm5a', role: 'shadowsmith', pos: [-1.6, 17.6] }, { id: 'cd_sm5b', role: 'shadowsmith', pos: [1.6, 17.0] },
    { id: 'cd_sg6a', role: 'sparkgolem', pos: [-1.6, 10.0] }, { id: 'cd_sg6b', role: 'sparkgolem', pos: [-1.6, 3.0] }, { id: 'cd_fc6', role: 'forgeconstruct', pos: [-3.0, 7.0] },
    { id: 'cd_so7a', role: 'sootling', pos: [-1.2, -4.0] }, { id: 'cd_so7b', role: 'sootling', pos: [1.2, -12.0] }, { id: 'cd_sm7', role: 'shadowsmith', pos: [0.0, -2.0] },
  ],
};
