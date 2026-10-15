// [SVARTALFHEIM] Dagna and Tobble as followers. Extends the Lumi follower mechanics (alfheim_lumi.js): a ground-walking actor sprite
// that trails the player, hops over when left far behind, and (Dagna) brawls / mends. Only the ACTIVE companion follows (see
// svartalfheim_companions.js); Lumi keeps her own module and checks the same flag.
// Sheets: Dagna = role 'dagna' (exists in the 5 realm areas; she is not shown in forge_hall, where she is at her forge).
// Tobble = role 'gnome' in the areas where that is still his sheet (outside the realm areas, which repaint 'gnome' as Dagna).
// Elsewhere the companion is still "with you" (flag, swap, toast) but has no body. Deviations: no temper buff (+10% melee), Tobble has no kit.
import { active } from './svartalfheim_companions.js';

const SV = ['svartalfheim', 'forge_hall', 'glowmines', 'clockdeep', 'clockdeep2'];
const KIT = {
  dagna: { role: 'dagna', dist: 1.2, speed: 2.8, brawl: { dmg: 10, reach: 1.2, cd: 1.6, knock: 0.6 }, mend: { below: 0.3, heal: 40 }, light: '#f2a63a',
    follow: ['Walk where I walk. The floor here bites.', 'Your boots are Midgard-made. I can tell. They squeak.'] },
  tobble: { role: 'gnome', dist: 1.3, speed: 2.8, follow: ['Home is wherever the mushrooms are. Lead on!', 'Two of us means twice the gossip. Walk faster.'] },
};

export class Follow {
  constructor(G) { this.G = G; this.ctx = null; this.on = false; this.id = null; this.sprite = null; this.t = 0; this.cd = 0; this.mended = false; this.idleT = 40; this.hits = 0; this.tmT = 0; this.tempT = 0; }
  qa() { return { on: this.on, id: this.id, role: this.sprite && this.sprite.role, x: this.sprite && +this.sprite.x.toFixed(2), z: this.sprite && +this.sprite.z.toFixed(2), hits: this.hits, mended: this.mended }; }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    const id = active(this.G.S), k = KIT[id]; this.id = id || null;
    if (!k || !ctx.actors) return;
    if (id === 'dagna' && (area === 'forge_hall' || !SV.includes(area))) return;   // at her forge / no sheet in this atlas
    if (id === 'tobble' && SV.includes(area)) return;                                 // 'gnome' is Dagna's sheet in the realm areas
    if (!ctx.actors.meta.roles[k.role]) return;
    const p = ctx.player, x = p.x + 0.8, z = p.z + 0.4;
    this.sprite = ctx.actors.add({ role: k.role, id: 'comp_' + id, pos: [x, z], behavior: 'none', turn: false }); this.sprite.ai = true;
    this.sprite.x = x; this.sprite.z = z; this.sprite.y = ctx.heightAt(x, z);
    if (k.light && ctx.addGlow) this.light = ctx.addGlow(x, this.sprite.y, z, { color: k.light, intensity: 2.0, range: 1.8, lift: 0.6, fadeIn: 0.4 });
    this.on = true; this.mended = false;
  }
  detach() {
    if (this.light) this.light.kill = true;
    if (this.sprite && this.ctx && this.ctx.actors) this.ctx.actors.remove(this.sprite);
    this.sprite = null; this.light = null; this.on = false; this.ctx = null;
  }
  bark(line) {
    const el = document.getElementById('say'); if (!el) return;
    el.innerHTML = `<b>${this.id === 'dagna' ? 'Dagna' : 'Tobble'}</b> — ${line}`; el.hidden = false;
    const tok = (this.tok = (this.tok || 0) + 1); setTimeout(() => { if (this.tok === tok) el.hidden = true; }, 4600);
  }
  mend() {
    const G = this.G, C = G.combat, k = KIT.dagna.mend; if (this.mended || !C || !C.maxHp) return false;
    this.mended = true; G.S.hp = Math.min(C.maxHp(), (G.S.hp || 0) + k.heal); this.bark('Hold still. There. Don\'t make me do that twice.'); return true;
  }
  temperNow() {   // every 20 s in a fight: a spark burst on your blade, +10% melee for 8 s (read by svart.tempMul)
    this.tmT = 20; this.tempT = 8; const c = this.ctx, p = c && c.player;
    if (c && c.effects && c.effects.meta.effects.glitter) c.effects.spawn('glitter', p.x, c.heightAt(p.x, p.z) + 0.9, p.z + 0.05, { duration: 0.8 });
    this.bark('Sharpened. Try not to dull it on the rock.');
  }
  brawl(foes) {
    const a = this.sprite, C = this.G.combat, k = KIT.dagna.brawl; this.cd = k.cd;
    const tgt = foes.filter((e) => Math.hypot(e.a.x - a.x, e.a.z - a.z) < k.reach + (e.def && e.def.scale ? e.def.scale * 0.25 : 0.2)).sort((u, v) => Math.hypot(u.a.x - a.x, u.a.z - a.z) - Math.hypot(v.a.x - a.x, v.a.z - a.z))[0];
    if (!tgt) { this.cd = 0.3; return; }
    this.hits++; C.damageEnemy(tgt, k.dmg, { x: a.x, z: a.z }, k.knock, KIT.dagna.light);
  }
  update(dt) {
    const c = this.ctx; if (!c || !this.on || !this.sprite) return;
    this.t += dt; this.cd -= dt;
    const a = this.sprite, A = c.actors, p = c.player, G = this.G, C = G.combat, k = KIT[this.id];
    const foes = C && C.alive ? C.alive().filter((e) => Math.hypot(e.a.x - p.x, e.a.z - p.z) < 6 && (e.state === 'chase' || e.state === 'attack')) : [];
    let tx, tz;
    const near = k.brawl && foes.length ? foes.sort((u, v) => Math.hypot(u.a.x - a.x, u.a.z - a.z) - Math.hypot(v.a.x - a.x, v.a.z - a.z))[0] : null;
    if (near) { tx = near.a.x - 0.9 * Math.sign(near.a.x - a.x || 1); tz = near.a.z; }
    else { const fv = { up: [0, 1], down: [0, -1], left: [1, 0], right: [-1, 0] }[p.facing] || [0, -1]; tx = p.x + fv[0] * k.dist + 0.5; tz = p.z + fv[1] * 0.5 + 0.3; }
    const dx = tx - a.x, dz = tz - a.z, d = Math.hypot(dx, dz);
    if (d > 9) { a.x = tx; a.z = tz; }
    else if (d > 0.15) { const st = Math.min(d, dt * k.speed * (d > 2.5 ? 1.8 : 1)); a.x += dx / d * st; a.z += dz / d * st; }
    a.y = c.heightAt(a.x, a.z); a.lift = (p.lift || 0) * 0.5;
    const mv = d > 0.2; if (mv) A.setFacingFromVec(a, dx, dz); else a.facing = p.facing;
    A.animate(a, dt, mv);
    if (this.light) { this.light.pos.set(a.x, a.y, a.z); this.light.base = 2.0; }
    this.tmT -= dt; this.tempT -= dt;
    if (this.id === 'dagna' && foes.length && this.tmT <= 0) this.temperNow();
    if (!C || !C.ctx || G.downed) return;
    if (near && this.cd <= 0) this.brawl(foes);
    if (this.id === 'dagna' && G.S.hp != null && C.maxHp && G.S.hp < C.maxHp() * KIT.dagna.mend.below && foes.length) this.mend();
    if (!foes.length) this.mended = false;
    if (!foes.length && (this.idleT -= dt) <= 0) { this.idleT = 60 + Math.random() * 50; this.bark(k.follow[Math.floor(Math.random() * k.follow.length)]); }
  }
  // QA: put Dagna on the nearest live enemy and brawl; returns the HP it lost
  qaBrawl() {
    const C = this.G.combat, a = this.sprite; if (!a || !C) return null;
    const foes = C.alive().sort((u, v) => Math.hypot(u.a.x - a.x, u.a.z - a.z) - Math.hypot(v.a.x - a.x, v.a.z - a.z)); if (!foes.length) return null;
    a.x = foes[0].a.x - 0.5; a.z = foes[0].a.z; const h = foes[0].hp; this.brawl(foes); return Math.round(h - foes[0].hp);
  }
  qaMend() { const C = this.G.combat; this.mended = false; this.G.S.hp = 5; const a = this.mend(), hp = this.G.S.hp, b = this.mend(); return [a, b, hp >= 45]; }
}
