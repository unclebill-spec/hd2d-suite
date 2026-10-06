// Ravenhold Harbor (Stage 5 part 4): the waystones (Bakery Lane <-> Ravenhold Harbor <-> Bifrost Crossing), the harbor's
// sealed district gates' story hook (looking at the Market Terraces gate during "The Road to the Rift"), the district
// gate text, and (Stage 6 part 1) Sable's rift-skiff ferry between Ravenhold's east pier and Bifrost Crossing's landing.
// Area data: scene.game.waystone {pos}, scene.game.ferry {pos, to, spawn, tap: [x0, z0, x1, z1], name},
// scene.game.sealed [{id, pos, name, district, say}].
// Inputs: E / A / Enter near a waystone or the skiff opens its travel choice; tapping / clicking it walks up, a second
// tap opens it.
export const WAYS = {   // where each attuned waystone sends you (area -> [label, to, spawn]); Bifrost once visited
  lane: ['Bakery Lane, Hearthmoor', 'lane', 'from_ravenhold'],
  ravenhold: ['Ravenhold Harbor', 'ravenhold', 'from_waystone'],
  bifrost: ['Bifrost Crossing', 'bifrost', 'from_waystone'],
  temple: ['the Old Temple, Ravenhold', 'temple', 'from_waystone'],   // Stage 6.3
};
const WAY_SAY = {
  ravenhold: 'Cold-fire runes glow along the waystone. Its twin stands at the west end of Bakery Lane.',
  lane: 'Cold-fire runes glow along the waystone. The west road runs from here to Ravenhold, at the foot of the Rainbow Rift.',
  temple: 'Cold-fire runes glow along the waystone. The Temple\'s old stones remember every pilgrim.',
  bifrost: 'Cold-fire runes glow along the Guild\'s waystone. Its stones link the Crossing to Midgard\'s roads, no skiff needed.',
};
// the ferry may sail once Brannoc has pointed you at it (or the harbor quest was finished before the Crossing existed)
export const ferryOpen = (S) => !!((S.flags || {}).rh_road || (S.quests || {}).harbor === 3);
export class Harbor {
  constructor(G) { this.G = G; this.ctx = null; this.way = null; this.ferry = null; this.area = null; }
  attach(ctx, id) {
    this.ctx = ctx; this.area = id; this.way = ctx.scene.game?.waystone || null; this.ferry = ctx.scene.game?.ferry || null;
    if (ctx.effects && ctx.scene.game?.shimmer) this.shimmer(ctx, ctx.scene.game.shimmer);
    const F = (this.G.S.flags = this.G.S.flags || {});
    if (this.way) { F.ways = F.ways || {}; if (!F.ways[id]) { F.ways[id] = 1; } }
  }
  detach() { this.ctx = null; this.way = null; this.ferry = null; }
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
  nearFerry(r = 1.6) {
    const c = this.ctx, f = this.ferry; if (!c || !f) return false;
    return Math.hypot(c.player.x - f.pos[0], c.player.z - f.pos[1]) < r;
  }
  nearThing() { return this.near() || this.nearFerry(); }
  prompt() {
    if (this.nearFerry()) return this.area === 'ravenhold' && !ferryOpen(this.G.S) ? `${this.ferry.name}: Corsair business (E / A to look)` : `${this.ferry.name} (E / A to sail)`;
    return this.near() ? 'the waystone hums (E / A to travel)' : '';
  }
  interact() {
    if (this.nearFerry()) { this.openFerry(); return true; }
    if (!this.near()) return false; this.open(); return true;
  }
  open() {
    const G = this.G, F = G.S.flags || {}, ways = F.ways || {};
    const opts = Object.entries(WAYS).filter(([a]) => a !== this.area && (ways[a] || a === 'lane' || a === 'ravenhold'))
      .map(([, [label, to, spawn]]) => ({ label: `Travel to ${label}.`, pick: () => { G.go(to, spawn, 'portal'); return null; } }));
    opts.push({ label: 'Stay here.', cancel: true, pick: () => null });
    G.openDialogue({ id: 'waystone', name: 'A waystone' }, { pages: [WAY_SAY[this.area] || WAY_SAY.lane], choice: { id: 'waystone', options: opts } });
  }
  // Sable's rift-skiff: Ravenhold's east pier <-> Bifrost Crossing's landing (the Corsairs sail the Rift's under-currents)
  openFerry() {
    const G = this.G, f = this.ferry, npc = { id: 'ferry', name: f.name };
    if (this.area === 'ravenhold' && !ferryOpen(G.S)) {
      G.openDialogue(npc, { pages: ['Sable\'s rift-skiff rocks at the pier, its keel lamp burning blue. The Corsairs sail the Rift\'s under-currents in her.',
                                    'Nobody casts off without Corsair say-so. Harbormaster Brannoc decides who gets a berth.'] });
      return;
    }
    const there = this.area === 'ravenhold' ? 'Bifrost Crossing' : 'Ravenhold Harbor';
    // 6.5: the skiff still sails in a Bifrost rift storm (never strand the player), with a warning line on each side
    const storm = (G.S.flags || {}).storm === 'bifrost';
    const sailLine = storm ? (this.area === 'ravenhold' ? 'The deckhand grins through the spray: \'Under-current\'s wild tonight. Hold the rail and don\'t look up.\''
                                                        : 'The skiff bucks on its cold-fire wake. \'Storm\'s pushing the current. Quick trip, rough trip. Sit low.\'')
      : this.area === 'ravenhold' ? 'Sable\'s rift-skiff, keel lamp burning blue. A Corsair deckhand nods you aboard: the under-current runs up to Bifrost Crossing tonight.'
        : 'The rift-skiff waits at the landing, rocking on its cold-fire wake. The current runs back down to Ravenhold.';
    G.openDialogue(npc, {
      pages: [sailLine],
      choice: { id: 'ferry', options: [{ label: `Sail to ${there}.`, pick: () => { G.go(f.to, f.spawn, 'sail').then(() => { if (storm) setTimeout(() => G.toast('A rough crossing. Your boots are wet, but you\'re in one piece.', 2.6), 1700); }); return null; } },
                                       { label: 'Stay here.', cancel: true, pick: () => null }] } });
  }
  onTap(hit) {
    const c = this.ctx, w = this.way, f = this.ferry; if (!c) return false;
    if (w && Math.abs(hit.x - w.pos[0]) < 1.0 && hit.z > w.pos[1] - 1.0 && hit.z < w.pos[1] + 1.4) {
      if (this.near()) this.open(); else c.walkTo(w.pos[0], w.pos[1] + 1.1);
      return true;
    }
    // the skiff itself (its hull rect) or the boarding spot: walk to the boarding spot, a second tap opens the choice
    if (f && ((f.tap && hit.x >= f.tap[0] && hit.x <= f.tap[2] && hit.z >= f.tap[1] && hit.z <= f.tap[3]) || Math.hypot(hit.x - f.pos[0], hit.z - f.pos[1]) < 0.8)) {
      if (this.nearFerry()) this.openFerry(); else c.walkTo(f.pos[0], f.pos[1]);
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
