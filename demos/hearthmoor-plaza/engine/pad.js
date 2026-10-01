// Game Layout One pad (PAD ONLY): FLOATING stick (appears where the thumb lands inside the movement zone,
// follows a sliding finger and re-centres when dragged past its radius; deadzone 13 %, outer ring = run,
// analog speed in between), MAIN verb (+ hold 0.35 s = interact), two mediums (the first is the SPELL
// button when the scene has spells: tap = cast, hold = next spell), two potion pills (greyed), rail (max 4).
// A quick tap inside the movement zone (no drag) is handed to tap-to-walk, so the zone never eats a tap.
// Left-handed layout is pure CSS (body.lefthand mirrors the zone, the resting stick and the button cluster).
export const STICK_R = 64;          // px: knob travel radius (and the re-centre radius)
export class Pad {
  constructor({ onMain, near, onSpell = null, onSpellHold = null, onTap = null, blockStart = null, signal = undefined }) {
    this.el = document.getElementById('pad');
    this.on = document.body.classList.contains('padon'); this.onMain = onMain;   // survives an area change
    if (this.el) this.el.hidden = !this.on;
    const sig = { signal };
    this.st = { active: false, x: 0, y: 0, mag: 0, run: false };
    const stick = document.getElementById('stick'), knob = document.getElementById('knob');
    this.stickEl = stick;
    // the movement zone: created on demand so older pages (fixed stick markup) get the floating stick too
    let zone = document.getElementById('stickZone');
    if (!zone && this.el) { zone = document.createElement('div'); zone.id = 'stickZone'; zone.className = 'zone'; this.el.prepend(zone); }
    this.zone = zone;
    let pid = null, cx = 0, cy = 0, x0 = 0, y0 = 0, t0 = 0, far = 0;
    const R = STICK_R;
    this.base = null;                // {x, y} centre of the live stick (QA)
    const place = () => {
      // keep the whole ring on screen
      const half = stick.offsetWidth / 2 || R;
      cx = Math.min(Math.max(cx, half + 2), innerWidth - half - 2);
      cy = Math.min(Math.max(cy, half + 2), innerHeight - half - 2);
      stick.style.left = (cx - half) + 'px'; stick.style.top = (cy - half) + 'px';
      stick.style.right = 'auto'; stick.style.bottom = 'auto';
      this.base = { x: cx, y: cy };
    };
    const set = (e) => {
      let dx = e.clientX - cx, dy = e.clientY - cy;
      let d = Math.hypot(dx, dy);
      if (d > R) {             // dragged past the rim: the stick slides after the thumb
        cx += dx / d * (d - R); cy += dy / d * (d - R); place();
        dx = e.clientX - cx; dy = e.clientY - cy; d = Math.hypot(dx, dy);
      }
      const m = Math.min(d, R), nx = d > 0 ? dx / d : 0, ny = d > 0 ? dy / d : 0;
      knob.style.transform = `translate(${nx * m * 0.7}px, ${ny * m * 0.7}px)`;
      const mag = m / R;
      if (mag < 0.13) { this.st = { active: true, x: 0, y: 0, mag: 0, run: false }; return; }
      this.st = { active: true, x: nx, y: ny, mag, run: mag > 0.85 };
    };
    const rest = () => {
      pid = null; this.base = null;
      stick.classList.remove('live');
      stick.style.left = stick.style.top = stick.style.right = stick.style.bottom = '';
      knob.style.transform = '';
      this.st = { active: false, x: 0, y: 0, mag: 0, run: false };
    };
    if (zone) {
      zone.addEventListener('pointerdown', (e) => {
        e.preventDefault(); e.stopPropagation();
        if (pid !== null || (blockStart && blockStart())) return;   // one thumb drives the stick; not during a pinch
        pid = e.pointerId; cx = x0 = e.clientX; cy = y0 = e.clientY; t0 = e.timeStamp; far = 0;
        try { zone.setPointerCapture(pid); } catch (err) { /* synthetic */ }
        stick.classList.add('live'); place(); set(e);
      }, sig);
      zone.addEventListener('pointermove', (e) => {
        if (e.pointerId !== pid) return;
        far = Math.max(far, Math.hypot(e.clientX - x0, e.clientY - y0));
        set(e);
      }, sig);
      const end = (e) => {
        if (e.pointerId !== pid) return;
        const tap = e.type === 'pointerup' && far < 12 && e.timeStamp - t0 < 350;
        rest();
        if (tap && onTap) onTap(x0, y0);                // a tap in the zone still walks there
      };
      zone.addEventListener('pointerup', end, sig); zone.addEventListener('pointercancel', end, sig);
      zone.addEventListener('lostpointercapture', end, sig);
    }
    const main = document.getElementById('padMain');
    let held = null;
    main.addEventListener('pointerdown', (e) => { e.stopPropagation(); e.preventDefault(); held = setTimeout(() => { held = 'fired'; this.onMain(); }, 350); }, sig);
    main.addEventListener('pointerup', () => { if (held && held !== 'fired') { clearTimeout(held); this.onMain(); } held = null; }, sig);
    this.glyph = document.getElementById('mainGlyph');
    const sec = document.getElementById('padSec');
    if (onSpell && sec) {
      sec.disabled = false; sec.textContent = '✦'; sec.title = 'tap: cast · hold: next spell';
      let h2 = null;
      sec.addEventListener('pointerdown', (e) => { e.stopPropagation(); e.preventDefault(); h2 = setTimeout(() => { h2 = 'fired'; onSpellHold && onSpellHold(); }, 450); }, sig);
      sec.addEventListener('pointerup', () => { if (h2 && h2 !== 'fired') { clearTimeout(h2); onSpell(); } h2 = null; }, sig);
    }
    this._rest = rest;
    // pinch hand-off: a stick that was only just put down (not dragged, < 300 ms) gives way to a two-finger pinch
    this.fresh = (now) => pid === null || (far < 12 && now - t0 < 300);
    this.release = () => { if (pid !== null) rest(); };
  }
  dispose() { this._rest && this._rest(); }
  toggle(v) { this.on = v ?? !this.on; this.el.hidden = !this.on; document.body.classList.toggle('padon', this.on); if (!this.on) this._rest(); }
  stick() { return this.on && !document.body.classList.contains('ctrl') ? this.st : { active: false }; }
  update(near) { if (this.on) this.glyph.textContent = near ? '💬' : '✋'; }
}
