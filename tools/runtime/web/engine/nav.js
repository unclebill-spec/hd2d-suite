// Grid A* over the baked collision heightfield (the same 0.25 m cells collide.js uses).
// A cell is walkable when the actor's footprint fits (no blocked cell within its radius) and the ground under the
// footprint is roughly level; a step between neighbours must stay under max_step, so terraces are only entered by
// their stairs and walls / props / trees are walked around. Paths are string-pulled with the real slide-move test.
export class Nav {
  constructor(collide, radius = 0.28) {
    this.c = collide; this.r = radius;
    const { w, h, d } = collide;
    this.w = w; this.h = h;
    const rc = Math.ceil(radius / collide.cell);
    const ok = new Uint8Array(w * h);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      const v = d[j * w + i];
      if (v === -32768) continue;
      let good = true;
      for (let dj = -rc; dj <= rc && good; dj++) for (let di = -rc; di <= rc; di++) {
        if (di * di + dj * dj > (rc + 0.5) * (rc + 0.5)) continue;
        const ii = i + di, jj = j + dj;
        if (ii < 0 || jj < 0 || ii >= w || jj >= h) { good = false; break; }
        const u = d[jj * w + ii];
        if (u === -32768 || Math.abs(u - v) > collide.maxStep * 160) { good = false; break; }
      }
      ok[j * w + i] = good ? 1 : 0;
    }
    this.ok = ok;
    this.g = new Float32Array(w * h); this.came = new Int32Array(w * h); this.seen = new Uint32Array(w * h); this.stamp = 0;
  }
  cellOf(x, z) { return [Math.floor((x - this.c.ox) / this.c.cell), Math.floor((z - this.c.oz) / this.c.cell)]; }
  center(i, j) { return [this.c.ox + (i + 0.5) * this.c.cell, this.c.oz + (j + 0.5) * this.c.cell]; }
  walkable(i, j) { return i >= 0 && j >= 0 && i < this.w && j < this.h && this.ok[j * this.w + i] === 1; }
  // nearest walkable cell to (i, j) within maxR cells, preferring the same height as hRef
  nearest(i, j, maxR = 10, hRef = null) {
    if (this.walkable(i, j) && (hRef === null || Math.abs(this.c.d[j * this.w + i] / 100 - hRef) < 0.5)) return [i, j];
    let best = null, bd = 1e9;
    for (let r = 1; r <= maxR; r++) {
      for (let dj = -r; dj <= r; dj++) for (let di = -r; di <= r; di++) {
        if (Math.max(Math.abs(di), Math.abs(dj)) !== r || !this.walkable(i + di, j + dj)) continue;
        let dd = di * di + dj * dj;
        if (hRef !== null && Math.abs(this.c.d[(j + dj) * this.w + i + di] / 100 - hRef) > 0.5) dd += 400;
        if (dd < bd) { bd = dd; best = [i + di, j + dj]; }
      }
      if (best && bd < 400) return best;
    }
    return best;
  }
  // returns [[x, z], ...] from start (exclusive) to goal, or null when unreachable
  path(sx, sz, gx, gz, maxExpand = 90000) {
    const W = this.w, d = this.c.d, step = this.c.maxStep * 100;
    let [si, sj] = this.cellOf(sx, sz);
    const s = this.nearest(si, sj, 4); if (!s) return null; [si, sj] = s;
    const gc = this.cellOf(gx, gz);
    const g = this.nearest(gc[0], gc[1], 10, this.c.height(gx, gz)); if (!g) return null;
    const [gi, gj] = g;
    const start = sj * W + si, goal = gj * W + gi;
    this.stamp++;
    const st = this.stamp, G = this.g, came = this.came, seen = this.seen;
    const heap = new MinHeap();
    const hfun = (i, j) => { const dx = Math.abs(i - gi), dz = Math.abs(j - gj); return Math.max(dx, dz) + 0.41421 * Math.min(dx, dz); };
    G[start] = 0; came[start] = -1; seen[start] = st;
    heap.push(hfun(si, sj), start);
    const closed = new Set();
    let n = 0, found = false;
    const NB = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, 1.41421], [1, -1, 1.41421], [-1, 1, 1.41421], [-1, -1, 1.41421]];
    while (heap.size) {
      const cur = heap.pop();
      if (cur === goal) { found = true; break; }
      if (closed.has(cur)) continue;
      closed.add(cur);
      if (++n > maxExpand) break;
      const ci = cur % W, cj = (cur / W) | 0, hc = d[cur];
      for (const [di, dj, cost] of NB) {
        const ni = ci + di, nj = cj + dj;
        if (!this.walkable(ni, nj)) continue;
        if (di && dj && (!this.walkable(ci + di, cj) || !this.walkable(ci, cj + dj))) continue;   // no corner cutting
        const k = nj * W + ni;
        if (Math.abs(d[k] - hc) > step) continue;
        const ng = G[cur] + cost;
        if (seen[k] !== st || ng < G[k]) {
          seen[k] = st; G[k] = ng; came[k] = cur;
          heap.push(ng + hfun(ni, nj), k);
        }
      }
    }
    if (!found) return null;
    const cells = [];
    for (let k = goal; k !== -1; k = came[k]) cells.push(k);
    cells.reverse();
    const pts = cells.map((k) => this.center(k % W, (k / W) | 0));
    pts[pts.length - 1] = this.walkable(...this.cellOf(gx, gz)) && Math.abs((this.c.height(gx, gz) ?? -99) - d[goal] / 100) < 0.05 ? [gx, gz] : pts[pts.length - 1];
    return this.smooth([sx, sz], pts);
  }
  // string pulling: keep a point only when the straight segment from the last kept point would leave the walkable set
  clear(a, b) {
    const L = Math.hypot(b[0] - a[0], b[1] - a[1]), n = Math.ceil(L / (this.c.cell * 0.5));
    let h0 = this.c.height(a[0], a[1]);
    for (let s = 1; s <= n; s++) {
      const x = a[0] + (b[0] - a[0]) * s / n, z = a[1] + (b[1] - a[1]) * s / n;
      const [i, j] = this.cellOf(x, z);
      if (!this.walkable(i, j)) return false;
      const h = this.c.d[j * this.w + i] / 100;
      if (Math.abs(h - h0) > this.c.maxStep) return false;
      h0 = h;
    }
    return true;
  }
  smooth(start, pts) {
    const out = [];
    let anchor = start, i = 0;
    while (i < pts.length) {
      let j = pts.length - 1;
      while (j > i && !this.clear(anchor, pts[j])) j--;
      out.push(pts[j]); anchor = pts[j]; i = j + 1;
    }
    return out;
  }
}

class MinHeap {
  constructor() { this.k = []; this.v = []; }
  get size() { return this.k.length; }
  push(key, val) {
    const K = this.k, V = this.v; let i = K.length; K.push(key); V.push(val);
    while (i > 0) { const p = (i - 1) >> 1; if (K[p] <= key) break; K[i] = K[p]; V[i] = V[p]; i = p; }
    K[i] = key; V[i] = val;
  }
  pop() {
    const K = this.k, V = this.v, top = V[0], lk = K.pop(), lv = V.pop();
    if (K.length) {
      let i = 0; const n = K.length;
      for (;;) { let c = 2 * i + 1; if (c >= n) break; if (c + 1 < n && K[c + 1] < K[c]) c++; if (K[c] >= lk) break; K[i] = K[c]; V[i] = V[c]; i = c; }
      K[i] = lk; V[i] = lv;
    }
    return top;
  }
}
