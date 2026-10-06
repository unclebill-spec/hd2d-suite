// [ALFHEIM] The Prism Vault's light-beam puzzles (script alfheim.md section 7.1), realm-alfheim branch.
// Area data: scene.game.beams = { grid, sources: [{id, pos, dir, col, dark?, boss?}], mirrors: [{id, pos, rot, spin?, fixed?, boss?}],
//   splitters: [{id, pos}], receivers: [{id, pos, col, opens?, part?}], rooms: {P2: [x0, z0, x1, z1], ...} }.
//   * beams run in 8 directions (dir 0 = +x, 2 = +z, 45 degree steps) and stop at walls, receivers and the room edge
//   * a mirror has 4 orientations (rot 0-3 = a line at 0, 45, 90, 135 degrees); E / A (or a tap up close) turns it one
//     step; spin: N turns it by itself every N s. Reflection: out = (2 * rot - dir + 8) % 8
//   * a splitter breaks white into blue (straight on), violet (90 deg one way) and red (the other way)
//   * a dark source is lit by a spell landing within 2.6 m (the Hollows brazier rule); it stays lit (S.found[id])
//   * a receiver lit by its colour sets S.found[id] forever and fires `opens`; `part` receivers light their parent id
//     (pv_lens2) once every part is lit
//   * beams are drawn as 2 px-thick boxes in the sharp pass (no bloom) with a few small glows; they also hit foes
//     (hooks.onBeamHit: crystal golems stagger and drop their prism shield, Sylvaine's light shield breaks)
// QA: ?beams=solve lights every receiver of the room you stand in (G.alfheim.beams.solve()).
import * as THREE from 'three';

export const BEAM_COL = { white: '#fff8e6', violet: '#a45cf0', blue: '#5ac8ff', red: '#ff4a3a' };
const DV = [...Array(8)].map((_, d) => [Math.round(Math.cos(d * Math.PI / 4) * 1e6) / 1e6, Math.round(Math.sin(d * Math.PI / 4) * 1e6) / 1e6]);
const STEP = 0.1, HIT = 0.24, REC = 0.4, H = 0.95;
const inR = (r, x, z) => x >= r[0] && x <= r[2] && z >= r[1] && z <= r[3];

export class Beams {
  // hooks: { found(id) -> bool, setFound(id), onLit(rec), onBeamHit(target, col), targets() -> [{x, z, r, ref}], wall(x, z) -> bool }
  constructor(G, ctx, data, hooks) {
    this.G = G; this.ctx = ctx; this.hooks = hooks; this.t = 0;
    this.sources = (data.sources || []).map((s) => ({ ...s, lit: !s.dark || hooks.found(s.id) }));
    this.mirrors = (data.mirrors || []).map((m) => ({ ...m, rot: m.rot | 0, spinT: m.spin || 0 }));
    this.splitters = (data.splitters || []).map((s) => ({ ...s }));
    this.receivers = (data.receivers || []).map((r) => ({ ...r, lit: hooks.found(r.id) }));
    this.rooms = data.rooms || {};
    this.group = new THREE.Group(); this.group.name = 'alf_beams';
    this.sharp = ctx.effects && ctx.effects.sharp;
    if (this.sharp) this.sharp.add(this.group);
    this.mats = {}; this.glows = []; this.segs = []; this.dirty = true; this.hitT = new Map();
    this.faces = this.mirrors.map((m) => this.face(m));
    for (const s of this.sources) if (s.lit) this.lightFx(s);
    for (const r of this.receivers) if (r.lit) this.recFx(r, true);
  }
  dispose() {
    if (this.sharp) this.sharp.remove(this.group);
    this.group.traverse((o) => { if (o.geometry) o.geometry.dispose(); });
    for (const m of Object.values(this.mats)) m.dispose();
    for (const g of this.glows) g.kill = true;
    for (const s of this.sources) if (s.glow) s.glow.kill = true;
    for (const r of this.receivers) if (r.glow) r.glow.kill = true;
  }
  mat(c) { return this.mats[c] || (this.mats[c] = new THREE.MeshBasicMaterial({ color: new THREE.Color(c) })); }
  y(x, z) { return this.ctx.heightAt(x, z); }
  // a mirror's face: a pale glass plate on the stand, turned to its rot (0-3 x 45 degrees), with a violet rim
  face(m) {
    const g = new THREE.Group(), [x, z] = m.pos;
    const plate = new THREE.Mesh(new THREE.BoxGeometry(0.86, 0.62, 0.05), this.mat('#d8e4f6'));
    const rim = new THREE.Mesh(new THREE.BoxGeometry(0.94, 0.06, 0.07), this.mat(m.boss ? '#a45cf0' : '#6a34b8'));
    rim.position.y = 0.34; plate.position.y = 0;
    const rim2 = rim.clone(); rim2.position.y = -0.34;
    g.add(plate, rim, rim2); g.position.set(x, this.y(x, z) + 1.05, z);
    g.rotation.y = -m.rot * Math.PI / 4;
    this.group.add(g); m.mesh = g; return g;
  }
  near(x, z, r = 1.25) {
    let best = null, bd = r;
    for (const m of this.mirrors) { const d = Math.hypot(x - m.pos[0], z - m.pos[1]); if (d < bd && !m.fixed) { bd = d; best = m; } }
    return best;
  }
  turn(m, n = 1) {
    m.rot = (m.rot + n + 4) % 4; m.mesh.rotation.y = -m.rot * Math.PI / 4; this.dirty = true;
    if (this.ctx.effects) this.ctx.effects.spawn('glitter', m.pos[0], this.y(m.pos[0], m.pos[1]) + 0.9, m.pos[1] + 0.05, { duration: 0.6 });
    this.G.audio && this.G.audio.sfx('pickup');
  }
  // a spell landed at (x, z): dark sources within 2.6 m wake up
  spellAt(x, z) {
    let any = false;
    for (const s of this.sources) if (!s.lit && Math.hypot(x - s.pos[0], z - s.pos[1]) <= 2.6) {
      s.lit = true; this.hooks.setFound(s.id); this.lightFx(s); this.dirty = true; any = true;
    }
    return any;
  }
  lightFx(s) {
    const [x, z] = s.pos, y = this.y(x, z), c = this.ctx;
    if (c.effects) c.effects.spawn('beam_hit', x, y + 0.6, z + 0.05);
    if (c.addGlow && !s.glow) s.glow = c.addGlow(x, y, z, { color: '#fff8e6', intensity: 4, range: 3.2, lift: 1.0, fadeIn: 0.3 });
  }
  recFx(r, quiet) {
    const [x, z] = r.pos, y = this.y(x, z), c = this.ctx;
    if (!quiet && c.effects) { c.effects.spawn('beam_hit', x, y + 0.9, z + 0.05); c.effects.spawn('prism_pop', x, y + 0.4, z + 0.05); }
    if (c.addGlow && !r.glow) r.glow = c.addGlow(x, y, z, { color: BEAM_COL[r.col] || BEAM_COL.white, intensity: 6, range: 4.0, lift: 1.2, fadeIn: quiet ? 0.01 : 0.3 });
  }
  roomOf(x, z) { for (const [k, r] of Object.entries(this.rooms)) if (inR(r, x, z)) return k; return null; }
  // one beam from (x, z) heading dir; returns its segments; splitters recurse
  trace(x, z, dir, col, room, out, depth = 0, skip = null) {
    if (depth > 4) return;
    const R = this.rooms[room];
    let x0 = x, z0 = z, last = skip, bounces = 0, objs = 0;
    for (let i = 0; i < 700; i++) {
      x += DV[dir][0] * STEP; z += DV[dir][1] * STEP;
      if (R && !inR(R, x, z)) break;
      let hit = null;
      for (const m of this.mirrors) if (m !== last && Math.abs(x - m.pos[0]) < HIT && Math.abs(z - m.pos[1]) < HIT) { hit = m; break; }
      if (hit) {
        out.push([x0, z0, hit.pos[0], hit.pos[1], col]);
        x = x0 = hit.pos[0]; z = z0 = hit.pos[1]; last = hit;
        dir = (2 * hit.rot - dir + 16) % 8;
        if (++bounces > 14) return;
        continue;
      }
      const sp = this.splitters.find((s) => s !== last && Math.abs(x - s.pos[0]) < HIT && Math.abs(z - s.pos[1]) < HIT);
      if (sp) {
        if (col === 'white') {
          out.push([x0, z0, sp.pos[0], sp.pos[1], col]);
          this.trace(sp.pos[0], sp.pos[1], dir, 'blue', room, out, depth + 1, sp);
          this.trace(sp.pos[0], sp.pos[1], (dir + 2) % 8, 'violet', room, out, depth + 1, sp);
          this.trace(sp.pos[0], sp.pos[1], (dir + 6) % 8, 'red', room, out, depth + 1, sp);
          return;
        }
        last = sp;   // coloured light passes straight through the splitter
      }
      const rc = this.receivers.find((r) => Math.hypot(x - r.pos[0], z - r.pos[1]) < REC);
      if (rc) { out.push([x0, z0, rc.pos[0], rc.pos[1], col]); if (col === rc.col) this.lit(rc); return; }
      if (this.sources.find((s) => Math.hypot(x - s.pos[0], z - s.pos[1]) < 0.3 && Math.hypot(x0 - s.pos[0], z0 - s.pos[1]) > 0.3)) break;
      // walls: only away from the puzzle pieces (their own stands block the nav grid)
      if (++objs > 3 && !this.mirrors.some((m) => Math.hypot(x - m.pos[0], z - m.pos[1]) < 0.55) && !this.splitters.some((s) => Math.hypot(x - s.pos[0], z - s.pos[1]) < 0.55)
          && !this.receivers.some((r) => Math.hypot(x - r.pos[0], z - r.pos[1]) < 0.7) && this.hooks.wall(x, z)) break;
    }
    out.push([x0, z0, x, z, col]);
  }
  lit(rc) {
    if (rc.lit) return;
    rc.lit = true; this.hooks.setFound(rc.id); this.recFx(rc, false);
    const parent = rc.part;
    if (parent) {
      const all = this.receivers.filter((r) => r.part === parent);
      if (all.every((r) => r.lit)) { this.hooks.setFound(parent); this.hooks.onLit({ ...rc, id: parent }); }
      else this.G.toast && this.G.toast(`The ${rc.col} lens flares. ${all.filter((r) => r.lit).length}/${all.length}`, 2);
      return;
    }
    this.hooks.onLit(rc);
  }
  solve(room) {
    for (const r of this.receivers) if (!room || this.roomOf(r.pos[0], r.pos[1]) === room) this.lit(r);
    for (const s of this.sources) if (!s.lit && (!room || this.roomOf(s.pos[0], s.pos[1]) === room)) { s.lit = true; this.hooks.setFound(s.id); this.lightFx(s); }
    this.dirty = true;
  }
  rebuild() {
    for (const m of this.segMeshes || []) { this.group.remove(m); m.geometry.dispose(); }
    for (const g of this.glows) g.kill = true;
    this.segMeshes = []; this.glows = []; this.segs = [];
    for (const s of this.sources) {
      if (!s.lit || (s.boss && !this.bossOn)) continue;
      this.trace(s.pos[0], s.pos[1], s.dir, s.col || 'white', this.roomOf(s.pos[0], s.pos[1]), this.segs);
    }
    let gl = 0;
    for (const [x0, z0, x1, z1, col] of this.segs) {
      const L = Math.hypot(x1 - x0, z1 - z0); if (L < 0.05) continue;
      const mx = (x0 + x1) / 2, mz = (z0 + z1) / 2, y = Math.max(this.y(x0, z0), this.y(x1, z1)) + H;
      const core = new THREE.Mesh(new THREE.BoxGeometry(L, 0.07, 0.07), this.mat(BEAM_COL[col] || BEAM_COL.white));
      core.position.set(mx, y, mz); core.rotation.y = -Math.atan2(z1 - z0, x1 - x0);
      const hot = new THREE.Mesh(new THREE.BoxGeometry(L, 0.025, 0.11), this.mat('#ffffff'));
      hot.position.copy(core.position); hot.rotation.y = core.rotation.y;
      this.group.add(core, hot); this.segMeshes.push(core, hot);
      if (this.ctx.addGlow && gl < 4 && L > 1.5) { gl++; this.glows.push(this.ctx.addGlow(mx, y - H, mz, { color: BEAM_COL[col], intensity: 2.6, range: 2.6, lift: H, fadeIn: 0.05 })); }
    }
    this.dirty = false;
  }
  update(dt) {
    this.t += dt;
    for (const m of this.mirrors) if (m.spin) { m.spinT -= dt; if (m.spinT <= 0) { m.spinT = m.spin; m.rot = (m.rot + 1) % 4; m.mesh.rotation.y = -m.rot * Math.PI / 4; this.dirty = true; } }
    if (this.dirty) this.rebuild();
    // beams that cross a foe: hooks decide (stagger, shield break); each target once per 0.5 s
    const T = this.hooks.targets ? this.hooks.targets() : [];
    for (const tg of T) {
      const k = this.hitT.get(tg.ref) || 0; if (this.t < k) continue;
      for (const [x0, z0, x1, z1, col] of this.segs) {
        const vx = x1 - x0, vz = z1 - z0, L2 = vx * vx + vz * vz || 1, u = Math.max(0, Math.min(1, ((tg.x - x0) * vx + (tg.z - z0) * vz) / L2));
        if (Math.hypot(tg.x - (x0 + vx * u), tg.z - (z0 + vz * u)) < tg.r) { this.hitT.set(tg.ref, this.t + 0.5); this.hooks.onBeamHit(tg.ref, col); break; }
      }
    }
  }
  qa() {
    return { mirrors: this.mirrors.map((m) => [m.id, m.rot]), sources: this.sources.map((s) => [s.id, s.lit]), lit: this.receivers.filter((r) => r.lit).map((r) => r.id), segs: this.segs.length };
  }
}
