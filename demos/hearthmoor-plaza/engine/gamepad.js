// Bluetooth / USB controllers through the Gamepad API (W3C "standard" mapping), polled once per frame.
//   left stick + d-pad: walk (analog speed)   right stick up / down: zoom (analog)
//   A talk / advance (jump when nothing is near)   B cancel / close (dodge roll in the field)   X attack   Y cast
//   LB / RB: previous / next spell   LT: hold to guard   RT: summon   LS click: jump   RS click: attack
//   Start: menu (log / pause)   Select: pad
// Every button (triggers included, past half travel) fires onButton once per press and onRelease when let go, so
// LT is a real hold-to-guard; zoom moved to the right stick so no trigger is mapped twice.
// Hot-plug: a pad is announced the first time it shows up in getGamepads() (Chrome only lists a pad after
// its first button press) or on 'gamepadconnected'; announcements survive area changes (module-level set).
export const BUTTONS = ['a', 'b', 'x', 'y', 'lb', 'rb', 'lt', 'rt', 'select', 'start', 'ls', 'rs', 'up', 'down', 'left', 'right', 'home'];
const SEEN = (window.__hd2dPadsSeen = window.__hd2dPadsSeen || new Map());   // key -> label
const DEAD = 0.18;          // radial stick deadzone
const ZDEAD = 0.3;          // right-stick zoom deadzone

const keyOf = (gp) => `${gp.index}:${gp.id}`;
export const padLabel = (gp) => {
  const id = String(gp.id || 'controller').replace(/\(.*?\)/g, '').replace(/\s+/g, ' ').trim();
  return id.length > 28 ? id.slice(0, 26) + '…' : id || 'controller';
};
const pressedOf = (b) => (typeof b === 'object' && b ? (b.pressed || (b.value || 0) > 0.5) : b === 1 || b === true);

export class GamepadInput {
  constructor({ onButton, onRelease, onConnect, signal } = {}) {
    this.onButton = onButton || (() => {});
    this.onRelease = onRelease || (() => {});
    this.onConnect = onConnect || (() => {});
    this.prev = new Map();           // gamepad index -> pressed[]
    this.state = { x: 0, y: 0, mag: 0, zoom: 0, used: false, count: 0 };
    const sig = { signal };
    addEventListener('gamepadconnected', (e) => this._hello(e.gamepad), sig);
    addEventListener('gamepaddisconnected', (e) => {
      const k = keyOf(e.gamepad);
      if (SEEN.has(k)) { SEEN.delete(k); this.onConnect(false, e.gamepad); }
      this.prev.delete(e.gamepad.index);
    }, sig);
    // a button held across an area change must not fire again in the new area
    for (const gp of this.list()) this.prev.set(gp.index, Array.from(gp.buttons || [], pressedOf));
  }
  list() {
    let pads = [];
    try { pads = navigator.getGamepads ? Array.from(navigator.getGamepads() || []) : []; } catch (e) { /* blocked by permissions policy */ }
    return pads.filter((g) => g && g.connected !== false);
  }
  _hello(gp) {
    const k = keyOf(gp);
    if (SEEN.has(k)) return;
    SEEN.set(k, padLabel(gp));
    this.onConnect(true, gp);
  }
  // returns { x, y, mag (0..1), zoom (-1..1, + = in), used (any input this frame), count }
  poll(enabled = true) {
    const st = { x: 0, y: 0, mag: 0, zoom: 0, used: false, count: 0 };
    const pads = this.list();
    st.count = pads.length;
    // unplugged without an event (some Bluetooth stacks): it simply stops being listed
    const live = new Set(pads.map(keyOf));
    for (const [k] of SEEN) if (!live.has(k)) { SEEN.delete(k); this.onConnect(false, { id: k }); }
    for (const gp of pads) {
      this._hello(gp);
      const pressed = Array.from(gp.buttons || [], pressedOf);
      const prev = this.prev.get(gp.index) || [];
      this.prev.set(gp.index, pressed);
      const axes = gp.axes || [];
      // left stick, radial deadzone, rescaled so the walk starts gently
      let ax = axes[0] || 0, ay = axes[1] || 0;
      let m = Math.hypot(ax, ay);
      let x = 0, y = 0, mag = 0;
      if (m > DEAD) { mag = Math.min(1, (m - DEAD) / (1 - DEAD)); x = ax / m; y = ay / m; }
      // d-pad: digital walk at full walking speed (no run)
      const dx = (pressed[15] ? 1 : 0) - (pressed[14] ? 1 : 0), dy = (pressed[13] ? 1 : 0) - (pressed[12] ? 1 : 0);
      if ((dx || dy) && mag === 0) { const L = Math.hypot(dx, dy); x = dx / L; y = dy / L; mag = 0.85; }
      // right stick Y: push up = zoom in, pull down = zoom out
      const ry = axes[3] || 0;
      const zoom = Math.abs(ry) > ZDEAD ? -Math.sign(ry) * (Math.abs(ry) - ZDEAD) / (1 - ZDEAD) : 0;
      const any = pressed.some(Boolean) || mag > 0 || zoom !== 0;
      if (any) st.used = true;
      if (!enabled) continue;
      if (mag > st.mag) { st.x = x; st.y = y; st.mag = mag; }
      if (zoom && !st.zoom) st.zoom = zoom;
      for (let i = 0; i < pressed.length; i++) {
        if (!BUTTONS[i]) continue;   // d-pad presses also fire (menus); they keep walking through the axes above
        if (pressed[i] && !prev[i]) this.onButton(BUTTONS[i], gp);
        else if (!pressed[i] && prev[i]) this.onRelease(BUTTONS[i], gp);
      }
    }
    this.state = st;
    return st;
  }
}
