// Ravenhold Harbor (Stage 5 part 4): the waystones (Bakery Lane <-> Ravenhold Harbor), the harbor's sealed district
// gates' story hook (looking at the Market Terraces gate during "The Road to the Rift"), and the district gate text.
// Area data: scene.game.waystone {pos}, scene.game.sealed [{id, pos, name, district, say}].
// Inputs: E / A / Enter near a waystone opens its travel choice; tapping / clicking it walks up, a second tap opens it.
export const WAYS = {   // where each attuned waystone sends you (area -> [label, to, spawn])
  lane: ['Bakery Lane, Hearthmoor', 'lane', 'from_ravenhold'],
  ravenhold: ['Ravenhold Harbor', 'ravenhold', 'from_waystone'],
};
export class Harbor {
  constructor(G) { this.G = G; this.ctx = null; this.way = null; this.area = null; }
  attach(ctx, id) {
    this.ctx = ctx; this.area = id; this.way = ctx.scene.game?.waystone || null;
    if (ctx.effects && ctx.scene.game?.shimmer) this.shimmer(ctx, ctx.scene.game.shimmer);
    const F = (this.G.S.flags = this.G.S.flags || {});
    if (this.way) { F.ways = F.ways || {}; if (!F.ways[id]) { F.ways[id] = 1; } }
  }
  detach() { this.ctx = null; this.way = null; }
  // the harbor's water: twinkling glitter on each lantern's reflection and cold-fire wisps drifting low over the water
  // (game.shimmer: {glints: [[x, z]], wisps: [[x, z]]}); animated sprites only, no lights (the glow-light cap holds)
  shimmer(ctx, sh) {
    const still = !!this.G.qaStill, fr = (f) => (still ? { frame: f } : {});
    (sh.glints || []).forEach(([x, z], i) => ctx.effects.spawn('glitter', x, 0.07, z, { duration: 1e9, fadeIn: still ? 0 : 1, ...fr(i % 4) }));
    (sh.wisps || []).forEach(([x, z], i) => ctx.effects.spawn('coldfire_motes', x, 0.5, z, { duration: 1e9, fadeIn: still ? 0 : 1.4, ...fr((i + 1) % 4) }));
  }
  near(r = 1.7) {
    const c = this.ctx, w = this.way; if (!c || !w) return false;
    return Math.hypot(c.player.x - w.pos[0], c.player.z - w.pos[1]) < r;
  }
  nearThing() { return this.near(); }
  prompt() { return this.near() ? 'the waystone hums (E / A to travel)' : ''; }
  interact() { if (!this.near()) return false; this.open(); return true; }
  open() {
    const G = this.G, F = G.S.flags || {}, ways = F.ways || {};
    const opts = Object.entries(WAYS).filter(([a]) => a !== this.area && (ways[a] || a === 'lane' || a === 'ravenhold'))
      .map(([, [label, to, spawn]]) => ({ label: `Travel to ${label}.`, pick: () => { G.go(to, spawn, 'portal'); return null; } }));
    opts.push({ label: 'Stay here.', cancel: true, pick: () => null });
    G.openDialogue({ id: 'waystone', name: 'A waystone' }, {
      pages: [this.area === 'ravenhold' ? 'Cold-fire runes glow along the waystone. Its twin stands at the west end of Bakery Lane.'
                                        : 'Cold-fire runes glow along the waystone. The west road runs from here to Ravenhold, at the foot of the Rainbow Rift.'],
      choice: { id: 'waystone', options: opts } });
  }
  onTap(hit) {
    const c = this.ctx, w = this.way; if (!c || !w) return false;
    if (Math.abs(hit.x - w.pos[0]) < 1.0 && hit.z > w.pos[1] - 1.0 && hit.z < w.pos[1] + 1.4) {
      if (this.near()) this.open(); else c.walkTo(w.pos[0], w.pos[1] + 1.1);
      return true;
    }
    return false;
  }
  // a district gate was looked at (sealedLook): the harbor story quest's second step
  onSealedLook(g) {
    const G = this.G, S = G.S; S.flags = S.flags || {};
    if (g.id === 'market' && S.quests.harbor === 2 && !S.flags.rh_gate) {
      S.flags.rh_gate = 1; G.toast('You have seen the Market Terraces gate. Tell Harbormaster Brannoc.', 2.6); G.refreshMarkers && G.refreshMarkers(); G.save();
    }
  }
}
