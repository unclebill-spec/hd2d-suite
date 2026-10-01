// Bluetooth / USB controllers through the Gamepad API (W3C "standard" mapping), polled once per frame.
//   left stick + d-pad: walk (analog speed)   A talk/advance   B cancel/close   X cast   Y next charm
//   LB / RB: previous / next charm   LT / RT: zoom out / in (analog)   Start: menu (log / pause)   Select: pad
// Hot-plug: a pad is announced the first time it shows up in getGamepads() (Chrome only lists a pad after
// its first button press) or on 'gamepadconnected'; announcements survive area changes (module-level set).
export const BUTTONS = ['a', 'b', 'x', 'y', 'lb', 'rb', 'lt', 'rt', 'select', 'start', 'ls', 'rs', 'up', 'down', 'left', 'right', 'home'];
const SEEN = (window.__hd2dPadsSeen = window.__hd2dPadsSeen || new Map());   // key -> label
const DEAD = 0.18;          // radial stick deadzone
const TRIG = 0.12;          // trigger deadzone

const keyOf = (gp) => `${gp.index}:${gp.id}`;
export const padLabel = (gp) => {
  const id = String(gp.id || 'controller').replace(/\(.*?\)/g, '').replace(/\s+/g, ' ').trim();
  return id.length > 28 ? id.slice(0, 26) + '…' : id || 'controller';
};
const pressedOf = (b) => (typeof b === 'object' && b ? (b.pressed || (b.value || 0) > 0.5) : b === 1 || b === true);
const valueOf = (b) => (typeof b === 'object' && b ? (b.value ?? (b.pressed ? 1 : 0)) : Number(b) || 0);

export class GamepadInput {
  constructor({ onButton, onConnect, signal } = {}) {
    this.onButton = onButton || (() => {});
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
      const lt = valueOf(gp.buttons?.[6]), rt = valueOf(gp.buttons?.[7]);
      const zoom = (rt > TRIG ? rt : 0) - (lt > TRIG ? lt : 0);
      const any = pressed.some(Boolean) || mag > 0 || zoom !== 0;
      if (any) st.used = true;
      if (!enabled) continue;
      if (mag > st.mag) { st.x = x; st.y = y; st.mag = mag; }
      if (zoom && !st.zoom) st.zoom = zoom;
      for (let i = 0; i < pressed.length; i++) {
        if (pressed[i] && !prev[i] && BUTTONS[i] && i !== 6 && i !== 7 && (i < 12 || i > 15)) this.onButton(BUTTONS[i], gp);
      }
    }
    this.state = st;
    return st;
  }
}
