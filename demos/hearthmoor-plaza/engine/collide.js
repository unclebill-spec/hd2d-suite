// Heightfield + blockers baked by `hd2d assemble` (cell grid; int16 centimetres, -32768 = blocked).
export class Collide {
  constructor(spec) {
    this.ox = spec.origin[0]; this.oz = spec.origin[1];
    this.cell = spec.cell; this.w = spec.w; this.h = spec.h;
    const bin = atob(spec.data);
    const buf = new ArrayBuffer(bin.length);
    const u8 = new Uint8Array(buf);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    this.d = new Int16Array(buf);
    this.maxStep = spec.max_step ?? 0.36;
    let lo = 1e9, hi = -1e9;
    for (const v of this.d) if (v !== -32768) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
    this.range = [lo / 100, hi / 100];
  }
  idx(x, z) {
    const i = Math.floor((x - this.ox) / this.cell), j = Math.floor((z - this.oz) / this.cell);
    if (i < 0 || j < 0 || i >= this.w || j >= this.h) return -1;
    return j * this.w + i;
  }
  raw(x, z) { const k = this.idx(x, z); return k < 0 ? -32768 : this.d[k]; }
  blocked(x, z) { return this.raw(x, z) === -32768; }
  height(x, z) { const v = this.raw(x, z); return v === -32768 ? null : v / 100; }
  // can an actor of radius r stand at (x,z) coming from height h0?
  canStand(x, z, h0, r = 0.28) {
    const pts = [[0, 0], [r, 0], [-r, 0], [0, r], [0, -r]];
    let hc = null;
    for (const [dx, dz] of pts) {
      const h = this.height(x + dx, z + dz);
      if (h === null) return null;
      if (dx === 0 && dz === 0) hc = h;
      if (Math.abs(h - h0) > this.maxStep * 1.6) return null;
    }
    if (Math.abs(hc - h0) > this.maxStep) return null;
    return hc;
  }
  // slide-move: returns [x, z, h]
  move(x, z, h, dx, dz, r) {
    let nh = this.canStand(x + dx, z + dz, h, r);
    if (nh !== null) return [x + dx, z + dz, nh, true];
    nh = this.canStand(x + dx, z, h, r);
    if (nh !== null && Math.abs(dx) > 1e-5) return [x + dx, z, nh, false];
    nh = this.canStand(x, z + dz, h, r);
    if (nh !== null && Math.abs(dz) > 1e-5) return [x, z + dz, nh, false];
    return [x, z, h, false];
  }
}
