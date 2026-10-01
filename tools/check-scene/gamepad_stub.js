// QA stub: a fake "standard" Bluetooth controller behind navigator.getGamepads() (unplugged until __padPlug()).
(() => {
  const mk = () => ({ id: 'Hearth Test Pad (STANDARD GAMEPAD Vendor: 0000 Product: 0000)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
    axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, touched: false, value: 0 })) });
  window.__fakePad = mk(); window.__fakePadOn = false;
  Object.defineProperty(navigator, 'getGamepads', { configurable: true, value: () => [window.__fakePadOn ? window.__fakePad : null, null, null, null] });
  window.__padPlug = (on = true) => { window.__fakePadOn = on; };
  window.__padBtn = (i, v = 1) => { const b = window.__fakePad.buttons[i]; b.pressed = v > 0.5; b.value = v; b.touched = v > 0; window.__fakePad.timestamp = performance.now(); };
  window.__padAxes = (x, y) => { window.__fakePad.axes[0] = x; window.__fakePad.axes[1] = y; window.__fakePad.timestamp = performance.now(); };
})();
