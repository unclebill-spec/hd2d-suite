// [SVARTALFHEIM] The Clockwork Deep's gear and rail puzzles (story 7.1): C2 The Drive Shaft (cd_cog1), C4 The Assembly Line (cd_cog2),
// C6 The Switchyard (cd_cog3). Pieces are the puzzles-pack kit (pegs, cogs, levers, rails, the cart) that svart_art.py puts in the area's
// scene.json (objects carry `pz` ids, `scene.game.pz` holds the layout). Rules, in short:
//  * Gears: cogs are carried one at a time (E / A) from the floor to an empty peg. A cog turns when it meshes (0.8 m apart) with a turning
//    cog; the drive pegs always turn (clockwise). A frozen cog is stuck and turns nothing until a spell thaws it (within 2.6 m).
//    C4 has two drive cogs, one reaching the winch through 2 cogs (anticlockwise, belts run to the presses) and one through 1 (clockwise,
//    belts run to the exit). Both reaching the winch jams it. The reset lever sends every loose cog back to the floor.
//  * Rails: three switch levers (SW2 is frozen), the brake lever releases the cart (3 m/s). All three set straight: it rams the gate (30
//    damage to foes in the way) and the last cog drops. Any switch left on the branch: it bumps the buffer and rolls back after 3 s.
//  * Never a softlock: a solved puzzle stays solved (S.found.cd_cogN); unsolved ones reset on re-entry; chests only wait behind the gate.
// QA: ?cogs=solve / ?rails=solve solves C2 + C4 / C6 on entry.
const flags = (S) => (S.flags || (S.flags = {}));
const found = (S) => (S.found || (S.found = {}));
const SIZE = { s: { name: 'small cog', rate: 3.2, fx: 'cog_spin_small' }, m: { name: 'medium cog', rate: 2.0, fx: 'cog_spin_medium' }, l: { name: 'large cog', rate: 1.2, fx: 'cog_spin_large' } };
const SOLVED_SEATS = { c2: { A: 's1', B: 'm1' }, c4: { c: 's1' } };   // the solved layouts shown on re-entry
const HINT = {
  c2: ['A drive cog\'s jammed. Find the gap, fit the cog. Big cogs turn slow, small ones fast. Think like a clock.', 'Gears! I love gears. I don\'t understand them. I love them.'],
  c4: ['That\'s the Foreman. He used to keep this line running. He still thinks he does.', 'The belts go one way. You go the other way. That\'s the trick, I think.'],
  c6: ['Rail yard. Set the switches, send the cart, ram the gate. Dwarves love a simple plan.', 'Carts! Finally something I know! Left switch, then... no. Right. Hang on.'],
};
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);

export class Puzzles {
  constructor(sv) { this.sv = sv; this.G = sv.G; this.rooms = []; this.held = null; this.fx = []; this.t = 0; }
  get ctx() { return this.sv.ctx; }
  o(id) { const c = this.ctx; return c && c.pz ? c.pz(id) : null; }
  show(id, on) { const o = this.o(id); if (o) o.visible = !!on; }
  efx(n, x, y, z, o) { const E = this.ctx && this.ctx.effects; return E && E.meta.effects[n] ? E.spawn(n, x, y, z, o || {}) : null; }
  gfx(n, x, y, z, o) { const E = this.ctx && this.ctx.gamefx; return E && E.meta.effects[n] ? E.spawn(n, x, y, z, o || {}) : null; }
  spot(o) { this.sv.spot(Object.defineProperties({ pz: true }, Object.getOwnPropertyDescriptors(o))); }   // tagged so the qa `spots` count keeps meaning the realm's own spots
  solved(r) { return !!found(this.G.S)[r.flag]; }
  detach() {
    for (const f of this.fx) if (f) f.dur = f.t + 0.2;
    for (const r of this.rooms) for (const c of Object.values(r.cogs || {})) if (c.fxh) { c.fxh.dur = c.fxh.t + 0.2; c.fxh = null; }
    for (const r of this.rooms) for (const f of (r.frozenFx || [])) if (f) f.dur = f.t + 0.2;
    this.fx = []; this.rooms = []; this.held = null;
  }
  attach(ctx, area) {
    this.detach();
    const spec = ((ctx.scene.game || {}).pz) || []; if (!spec.length || !ctx.pz) return;
    const qs = (this.G.qs || new URLSearchParams(location.search));
    for (const sp of spec) {
      const r = sp.kind === 'gear' ? this.gearRoom(sp) : this.railRoom(sp); this.rooms.push(r);
      const q = qs.get(sp.kind === 'gear' ? 'cogs' : 'rails');
      if (q === 'solve' && !this.solved(r)) this.qaSolve(r);
      else if (this.solved(r)) this.applySolved(r);
    }
  }
  nearRoom(r) { const c = this.ctx; const p = r.kind === 'gear' ? r.pegs[r.order[0]].pos : [r.x, r.tiles[3].z]; return c && Math.hypot(c.player.x - p[0], c.player.z - p[1]) < 7; }
  // ---------------------------------------------------------------- gears
  gearRoom(sp) {
    const me = this;
    const r = { ...sp, kind: 'gear', pegs: {}, cogs: {}, spin: {}, jam: {}, dir: 0, dirty: true, hint: 0, lever: 0, press: [0, 0], pt: 0 };
    r.order = sp.pegs.map((p) => p.id);
    for (const p of sp.pegs) {
      r.pegs[p.id] = { id: p.id, pos: p.pos, y: p.y, role: p.role || '', fixed: !!p.fixed || !!p.role, frozen: !!p.frozen, cog: null };
      if (p.cog) { const id = `${sp.id}:${p.id}`; r.cogs[id] = { id, size: p.cog, at: p.id, home: null, fixed: true, frozen: !!p.frozen, rot: 0 }; r.pegs[p.id].cog = id; }
    }
    for (const l of sp.loose) { const id = `${sp.id}:${l.id}`; r.cogs[id] = { id, short: l.id, size: l.size, at: 'floor', home: [l.pos[0], l.pos[1], l.y], fixed: false, frozen: false, rot: 0 }; }
    r.frozenFx = [];
    for (const c of Object.values(r.cogs)) if (c.frozen) { const p = r.pegs[c.at]; const f = this.efx('coldfire_motes', p.pos[0], p.y + 0.3, p.pos[1], { duration: Infinity }); c.frost = f; r.frozenFx.push(f); }
    for (const id of r.order) { const p = r.pegs[id]; this.spot({ pos: p.pos, r: 1.0, get label() { return me.pegLabel(r, p); }, act: () => this.pegAct(r, p), show: () => true }); }
    for (const c of Object.values(r.cogs)) if (!c.fixed) this.spot({ pos: [c.home[0], c.home[1]], r: 1.0, get label() { return `pick up the ${SIZE[c.size].name} (E / A)`; }, act: () => this.pick(r, c.id), show: () => c.at === 'floor' && !this.held });
    this.spot({ pos: sp.reset, r: 1.2, label: 'pull the reset lever (E / A)', act: () => this.reset(r), show: () => true });
    if (sp.chest) this.chestSpot(r);
    this.layout(r);
    return r;
  }
  layout(r) {   // positions + visibility of every cog / peg glow / lever from the state
    for (const c of Object.values(r.cogs)) {
      const o = this.o(`${r.id}:cog:${c.id}`); if (!o) continue;
      if (this.held === c.id) { o.visible = false; continue; }
      o.visible = true;
      if (c.at === 'floor') o.position.set(c.home[0], c.home[2], c.home[1]);
      else { const p = r.pegs[c.at]; o.position.set(p.pos[0], p.y, p.pos[1]); }
    }
    for (const id of r.order) { const p = r.pegs[id]; this.show(`${r.id}:pf:${id}`, !!p.cog); this.show(`${r.id}:peg:${id}`, !p.cog); }
    this.show(`${r.id}:lv:up`, !r.lever); this.show(`${r.id}:lv:dn`, !!r.lever);
    r.dirty = true;
  }
  pegLabel(r, p) {
    const c = p.cog && r.cogs[p.cog];
    if (this.held) return p.cog ? 'this peg is taken' : `fit the ${SIZE[r.cogs[this.held].size].name} here (E / A)`;
    if (c && c.frozen) return 'a frozen cog (cast a spell on it)';
    if (c && !c.fixed) return `take the ${SIZE[c.size].name} (E / A)`;
    if (p.role === 'winch') return 'the winch peg (E / A to look)';
    return c ? 'a bolted cog (E / A to look)' : 'an empty peg (carry a cog here)';
  }
  pegAct(r, p) {
    const G = this.G, c = p.cog && r.cogs[p.cog];
    if (this.held) {
      if (p.cog) { G.toast('This peg already has a cog.', 1.6); return; }
      this.put(r, p.id); return;
    }
    if (c && c.frozen) { G.toast('The cog is frozen solid. A spell would thaw it.', 2.2); return; }
    if (c && !c.fixed) { this.pick(r, c.id); return; }
    if (p.role === 'winch') { G.toast(this.solved(r) ? 'The winch is turning. The chain rattles somewhere above.' : 'The winch peg. Get the right spin here.', 2.4); return; }
    if (c) { G.toast(p.role === 'drive' ? 'A drive cog, bolted to the shaft. It always turns.' : 'Bolted down tight.', 2.0); return; }
    G.toast('An empty peg. Carry a loose cog here.', 1.8);
  }
  pick(r, cid) {
    const c = r.cogs[cid]; if (!c || c.fixed || c.frozen || this.held) return false;
    if (c.at !== 'floor') r.pegs[c.at].cog = null;
    c.at = 'held'; this.held = cid; this.layout(r);
    this.G.toast(`You carry the ${SIZE[c.size].name}. Fit it on a peg (E / A).`, 2.0); return true;
  }
  put(r, pid) {
    const p = r.pegs[pid]; const c = this.held && r.cogs[this.held]; if (!p || !c || p.cog) return false;
    p.cog = c.id; c.at = pid; this.held = null; this.layout(r);
    this.efx('ember_pop', p.pos[0], p.y + 0.2, p.pos[1], {}); return true;
  }
  reset(r) {
    const G = this.G;
    for (const c of Object.values(r.cogs)) if (!c.fixed) { if (c.at !== 'floor' && c.at !== 'held') r.pegs[c.at].cog = null; c.at = 'floor'; }
    this.held = null; r.lever = 1; this.layout(r);
    setTimeout(() => { r.lever = 0; if (this.rooms.includes(r)) this.layout(r); }, 700);
    G.toast('Clunk. Every loose cog slides back to the floor.', 2.0);
  }
  spinCalc(r) {   // BFS through meshed, unfrozen cogs from the drive pegs; two directions meeting jam the peg (it stops, and so does everything past it)
    const turning = (id) => { const p = r.pegs[id], c = p.cog && r.cogs[p.cog]; return c && !c.frozen; };
    const nb = (a, b) => Math.abs(Math.hypot(a.pos[0] - b.pos[0], a.pos[1] - b.pos[1]) - 0.8) < 0.06;
    const jam = {};
    for (let it = 0; it < 8; it++) {
      const dir = {}, q = [];
      for (const id of r.order) if (r.pegs[id].role === 'drive' && turning(id)) { dir[id] = 1; q.push(id); }
      let again = false;
      while (q.length) {
        const id = q.shift(); if (jam[id]) continue;
        for (const o of r.order) {
          if (o === id || !turning(o) || !nb(r.pegs[id], r.pegs[o])) continue;
          const d = -dir[id];
          if (dir[o] === undefined) { dir[o] = d; q.push(o); }
          else if (dir[o] !== d && !jam[o]) { jam[o] = true; again = true; }
        }
      }
      if (!again) { r.jam = jam; r.spin = {}; for (const id of r.order) if (dir[id] !== undefined && !jam[id]) r.spin[id] = dir[id]; return; }
    }
    r.jam = jam; r.spin = {};
  }
  gearUpdate(r, dt) {
    const G = this.G;
    if (r.dirty) {
      r.dirty = false; this.spinCalc(r);
      const w = r.order.find((id) => r.pegs[id].role === 'winch'); const wd = r.spin[w] || 0;
      const was = r.dir; r.dir = wd;
      if (wd === 1 && !this.solved(r)) this.solve(r);
      else if (wd === -1 && was !== -1) G.toast('The belts lurch the wrong way, toward the presses! (anticlockwise)', 2.6);
      else if (r.jam[w] && !r.jamTold) { r.jamTold = 1; G.toast('Two drives fight over the winch. Everything jams.', 2.4); }
      if (!r.jam[w]) r.jamTold = 0;
    }
    const c = this.ctx;
    for (const cog of Object.values(r.cogs)) {
      const o = this.o(`${r.id}:cog:${cog.id}`); const d = cog.at !== 'floor' && cog.at !== 'held' ? (r.spin[cog.at] || 0) : 0;
      if (o && d) o.rotation.y -= d * SIZE[cog.size].rate * dt;
      if (d && !cog.fxh && c.gamefx) { const p = r.pegs[cog.at]; cog.fxh = this.gfx(SIZE[cog.size].fx, p.pos[0], p.y + 0.12, p.pos[1], { duration: Infinity, fadeIn: 0.2 }); }
      else if (!d && cog.fxh) { cog.fxh.dur = cog.fxh.t + 0.2; cog.fxh = null; }
    }
    if (r.belts) this.belts(r, dt);
  }
  belts(r, dt) {
    const c = this.ctx, p = c.player, b = r.belts, G = this.G;
    const dir = this.solved(r) || r.dir === 1 ? -1 : (r.dir === -1 ? 1 : 0);   // -z = toward the exit (C5), +z = toward the presses
    r.beltDir = dir;
    if (dir && p.x > b.x[0] && p.x < b.x[1] && p.z > b.z[0] && p.z < b.z[1] && !G.dlg) {
      const m = c.collide.move(p.x, p.z, p.y, 0, dir * 0.9 * dt, 0.28); if (m) { p.x = m[0]; p.z = m[1]; if (m[2] !== undefined) p.y = m[2]; }
    }
    if (dir === 1 && r.dir === -1) {   // the presses stamp every 3 s (tell first)
      r.pt += dt;
      b.presses.forEach((q, i) => {
        const ph = (r.pt + i * 1.5) % 3;
        if (ph > 2.2 && !r.press[i]) { r.press[i] = 1; this.efx('ember_pop', q[0], c.heightAt(q[0], q[1]) + 0.3, q[1], {}); }
        if (ph < 0.2 && r.press[i]) { r.press[i] = 0; if (Math.hypot(p.x - q[0], p.z - q[1]) < 0.9) { this.G.combat.hurtPlayer(8, { x: q[0], z: q[1] }, 0.8); this.note(r, 'press', 'A stamping press! The belts are running the wrong way.'); } }
      });
    }
  }
  note(r, k, m) { r.told = r.told || {}; if (!r.told[k]) { r.told[k] = 1; this.G.toast(m, 2.4); } }
  solve(r) {
    const G = this.G, F = found(G.S);
    F[r.flag] = 1; this.openGate(r);
    G.toast(r.id === 'c6' ? 'The ram gate splinters. The last cog drops into place.' : (r.id === 'c2' ? 'A cog bites. Somewhere a chain rattles, and a shutter rises.' : 'The winch turns true. The belts run toward the exit.'), 3.0);
    const n = ['cd_cog1', 'cd_cog2', 'cd_cog3'].filter((k) => F[k]).length;
    if (n === 3) setTimeout(() => G.toast('The binding runes stop stuttering for a moment.', 3.0), 3200); else setTimeout(() => G.toast(`Drive cogs: ${n}/3`, 2.0), 3200);
    this.efx('ember_pop', ...(r.kind === 'gear' ? [r.pegs[r.order.find((i) => r.pegs[i].role === 'winch')].pos[0], r.y + 0.8, r.pegs[r.order.find((i) => r.pegs[i].role === 'winch')].pos[1]] : [r.x, r.y + 0.8, -1.5]), {});
  }
  openGate(r) {
    const g = r.gate, c = this.ctx; if (!g || r.open) return;
    r.open = true; this.show(`${r.id}:gate`, false);
    const col = c.collide; for (const [i, j, v] of g.cells) col.d[j * col.w + i] = v;
    if (c.nav) Object.assign(c.nav, new c.nav.constructor(c.collide, 0.3));
  }
  applySolved(r) {
    if (r.kind === 'gear') {
      const seats = SOLVED_SEATS[r.id] || {};
      for (const [pid, sid] of Object.entries(seats)) { const c = r.cogs[`${r.id}:${sid}`], p = r.pegs[pid]; if (c && p && !p.cog) { c.at = pid; p.cog = c.id; } }
      for (const c of Object.values(r.cogs)) if (c.frozen) { c.frozen = false; if (c.frost) { c.frost.dur = c.frost.t + 0.2; c.frost = null; } }
      this.layout(r);
    } else { for (const k of ['sw1', 'sw2', 'sw3']) r.sw[k] = 'straight'; r.frozen = false; this.lvLayout(r); }
    this.openGate(r);
  }
  qaSolve(r) {
    if (r.kind === 'gear') { for (const [pid, sid] of Object.entries(SOLVED_SEATS[r.id] || {})) { const c = r.cogs[`${r.id}:${sid}`]; c.at = pid; r.pegs[pid].cog = c.id; } for (const c of Object.values(r.cogs)) if (c.frozen) c.frozen = false; this.layout(r); }
    else { for (const k of ['sw1', 'sw2', 'sw3']) r.sw[k] = 'straight'; r.frozen = false; this.lvLayout(r); this.solve(r); }   // the preset sends the cart through
  }
  // ---------------------------------------------------------------- chests
  chestSpot(r) {
    const ch = r.chest;
    const me = this;
    this.spot({ pos: ch.pos, r: 1.3, get label() { return me.solved(r) ? (found(me.G.S)[ch.flag] ? 'the chest is empty' : 'open the chest (E / A)') : 'a locked chest (E / A to look)'; },
      act: () => {
        const G = this.G, F = found(G.S);
        if (!this.solved(r)) { G.toast(r.gate && r.gate.kind === 'ram' ? 'A locked chest behind the ram gate. Break the gate first.' : 'A locked chest behind the shutter. The shutter rises when the wheel turns.', 2.6); return; }
        if (F[ch.flag]) { G.toast('Empty. You already took what was inside.', 1.8); return; }
        F[ch.flag] = 1; G.S.gold = (G.S.gold || 0) + ch.gold; G.toast(`+${ch.gold} gold`, 1.8); G.drawBag && G.drawBag(); G.give(ch.item, ch.n);
        this.efx('ember_pop', ch.pos[0], ch.y + 0.6, ch.pos[1], {});
      }, show: () => true });
  }
  // ---------------------------------------------------------------- rails
  railRoom(sp) {
    const r = { ...sp, kind: 'rails', sw: { sw1: 'branch', sw2: 'branch', sw3: 'branch' }, frozen: true, run: null, cartAt: [sp.start[0], sp.start[1]], runs: 0, hint: 0 };
    const me = this;
    for (const k of ['sw1', 'sw2', 'sw3']) {
      this.spot({ pos: sp.levers[k], r: 1.1, get label() { return me.swLabel(r, k); }, act: () => this.throwSw(r, k), show: () => true });
    }
    this.spot({ pos: sp.levers.brake, r: 1.2, get label() { return r.run ? 'the cart is rolling' : 'pull the brake lever (E / A)'; }, act: () => this.brake(r), show: () => true });
    this.chestSpot(r);
    r.frostFx = this.efx('coldfire_motes', sp.levers.sw2[0], r.lever_y + 0.5, sp.levers.sw2[1], { duration: Infinity }); r.frozenFx = [r.frostFx];
    this.lvLayout(r); this.cartTo(r, sp.start[0], sp.start[1], 0);
    return r;
  }
  swLabel(r, k) {
    if (k === 'sw2' && r.frozen) return 'a frozen switch (cast a spell on it)';
    return `switch ${k.slice(2)}: ${r.sw[k] === 'straight' ? 'straight on' : 'to the dead-end branch'} (E / A to throw)`;
  }
  lvLayout(r) {
    for (const k of ['sw1', 'sw2', 'sw3']) { const st = r.sw[k] === 'straight'; this.show(`${r.id}:${k}:up`, st); this.show(`${r.id}:${k}:dn`, !st); }
    this.show(`${r.id}:brake:up`, !r.run); this.show(`${r.id}:brake:dn`, !!r.run);
  }
  throwSw(r, k) {
    const G = this.G;
    if (k === 'sw2' && r.frozen) { G.toast('The switch is frozen solid. A spell would thaw it.', 2.2); return false; }
    r.sw[k] = r.sw[k] === 'straight' ? 'branch' : 'straight'; this.lvLayout(r);
    G.toast(`Switch ${k.slice(2)}: ${r.sw[k] === 'straight' ? 'straight on' : 'to the branch'}.`, 1.4); return true;
  }
  route(r) {   // the cart's polyline at the moment of release; ends at a buffer (bump) or at the ram gate
    const pts = [[r.start[0], r.start[1]]]; let bump = false;
    for (const t of r.tiles) {
      if (t.t === 'end') continue;
      pts.push([r.x, t.z]);
      if (t.t === 'sw' && r.sw[t.sw] === 'branch') { pts.push([r.branch_x, t.z]); bump = true; break; }
    }
    if (!bump) pts.push([r.x, r.gate.pos[1] + 0.7]);
    return { pts, bump };
  }
  brake(r) {
    const G = this.G; if (r.run) return false;
    if (this.solved(r)) { G.toast('The cart is spent. The gate is already open.', 2.0); return false; }
    const rt = this.route(r); r.run = { ...rt, i: 1, t: 0, back: 0 }; r.runs++;
    this.lvLayout(r); G.toast('Clack! The brake lets go. The cart rolls.', 1.6); return true;
  }
  cartTo(r, x, z, hd) { const o = this.o(`${r.id}:cart`); if (o) { o.position.set(x, r.cart_y, z); o.rotation.y = hd; } r.cartAt = [x, z]; }
  railUpdate(r, dt) {
    const c = this.ctx, run = r.run; if (!run) return;
    if (run.back > 0) {   // bumped the buffer: sits 3 s, then rolls back to the start
      run.back -= dt; if (run.back <= 0) { this.cartTo(r, r.start[0], r.start[1], 0); r.run = null; this.lvLayout(r); this.G.toast('The cart is back at the start. Check the switches.', 2.2); }
      return;
    }
    let step = 3 * dt;
    while (step > 0 && run.i < run.pts.length) {
      const a = r.cartAt, b = run.pts[run.i], d = dist(a, b);
      if (d <= step) { this.cartTo(r, b[0], b[1], Math.atan2(b[0] - a[0], b[1] - a[1])); step -= d; run.i++; } else { const k = step / d; this.cartTo(r, a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, Math.atan2(b[0] - a[0], b[1] - a[1])); step = 0; }
    }
    if (c && this.G.combat) for (const e of this.G.combat.alive()) if (Math.hypot(e.a.x - r.cartAt[0], e.a.z - r.cartAt[1]) < 0.9 && !(e.cartHit > this.t - 1)) { e.cartHit = this.t; this.G.combat.damageEnemy(e, 30, { x: r.cartAt[0], z: r.cartAt[1] }, 0.6); }
    if (run.i >= run.pts.length) {
      if (run.bump) { run.back = 3; this.G.toast('The cart slams into the buffer. Wrong way! It rolls back soon.', 2.6); this.efx('ember_pop', r.cartAt[0], r.cart_y + 0.4, r.cartAt[1], {}); }
      else { r.run = null; this.cartTo(r, r.cartAt[0], r.cartAt[1], Math.PI); this.lvLayout(r); this.solve(r); this.efx('ember_pop', r.x, r.cart_y + 0.4, r.gate.pos[1], {}); }
    }
  }
  // ---------------------------------------------------------------- spells, hints, frame
  onCast() {
    const c = this.ctx; if (!c) return;
    const pl = [c.player.x, c.player.z];
    for (const r of this.rooms) {
      if (r.kind === 'gear') for (const cog of Object.values(r.cogs)) if (cog.frozen) {
        const p = r.pegs[cog.at]; if (dist(pl, p.pos) > 2.6) continue;
        cog.frozen = false; p.frozen = false; if (cog.frost) { cog.frost.dur = cog.frost.t + 0.2; cog.frost = null; } r.dirty = true;
        this.G.toast('The rime cracks off the cog. It can turn again.', 2.2); this.efx('ember_pop', p.pos[0], p.y + 0.3, p.pos[1], {});
      }
      if (r.kind === 'rails' && r.frozen && dist(pl, r.levers.sw2) <= 2.6) {
        r.frozen = false; if (r.frostFx) { r.frostFx.dur = r.frostFx.t + 0.2; r.frostFx = null; }
        this.G.toast('The rime cracks off switch 2. It moves again.', 2.2); this.efx('ember_pop', r.levers.sw2[0], r.lever_y + 0.4, r.levers.sw2[1], {});
      }
    }
  }
  update(dt) {
    if (!this.rooms.length || !this.ctx) return;
    this.t += dt;
    for (const r of this.rooms) {
      if (r.kind === 'gear') this.gearUpdate(r, dt); else this.railUpdate(r, dt);
      if (!this.solved(r) && !r.hint && this.nearRoom(r)) { r.idle = (r.idle || 0) + dt; if (r.idle > 60) { r.hint = 1; this.hintFor(r); } }
    }
  }
  hintFor(r) {
    const L = HINT[r.id]; if (!L) return;
    const dagna = ((this.G.S.flags || {}).companion_active) === 'dagna';
    if (dagna && this.sv.follow && this.sv.follow.on) this.sv.follow.bark(L[0]); else this.G.toast(`Kesh: "${L[1]}"`, 3.4);
  }
  qa() {
    return { held: this.held, rooms: this.rooms.map((r) => r.kind === 'gear'
      ? { id: r.id, kind: 'gear', solved: this.solved(r), dir: r.dir, spin: r.spin, jam: Object.keys(r.jam || {}), belt: r.beltDir || 0, gate: !!r.open, pegs: Object.fromEntries(r.order.map((i) => [i, r.pegs[i].cog && r.pegs[i].cog.split(':')[1]])),
          frozen: Object.values(r.cogs).filter((c) => c.frozen).length, chest: r.chest ? !!found(this.G.S)[r.chest.flag] : null }
      : { id: r.id, kind: 'rails', solved: this.solved(r), sw: r.sw, frozen: r.frozen, run: !!r.run, bump: !!(r.run && r.run.back > 0), cart: r.cartAt.map((v) => +v.toFixed(2)), gate: !!r.open, runs: r.runs, chest: !!found(this.G.S)[r.chest.flag] }) };
  }
}
