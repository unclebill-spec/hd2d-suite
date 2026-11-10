// node --test tests/gear_markers.mjs
// World / bag / tooltip compare markers. Equal-score gear draws a blue "=" on the same
// placeWorld path as the green up and red down arrows (33×39, z-index 5).
// Blue ramp: check_palette.py NEON "neon blue (portal / temple)" #2ab4ff / #a6ecff / #1c62d8.
import test from 'node:test';
import assert from 'node:assert/strict';
import { Loot } from '../game/loot.js';
import { attachArrows, arrowKind, ARROW_PAL } from '../game/gear_arrows.js';

const BLUE = { hi: '#a6ecff', mid: '#2ab4ff', lo: '#1c62d8' };

function classListFor(node) {
  const parts = () => node.className.split(/\s+/).filter(Boolean);
  return {
    contains: (c) => parts().includes(c),
    add: (c) => { if (!parts().includes(c)) node.className = [...parts(), c].join(' '); },
    remove: (c) => { node.className = parts().filter((x) => x !== c).join(' '); },
  };
}

function matches(node, sel) {
  if (sel.startsWith('#')) return node.id === sel.slice(1);
  const m = sel.match(/^([a-z]+)?(?:\.([a-z0-9_-]+))?$/i);
  if (!m) return false;
  if (m[1] && node.tagName !== m[1]) return false;
  if (m[2] && !node.className.split(/\s+/).includes(m[2])) return false;
  return true;
}

function queryAll(node, sel) {
  const out = [];
  const walk = (n) => {
    for (const c of n.children) {
      if (matches(c, sel)) out.push(c);
      walk(c);
    }
  };
  walk(node);
  return out;
}

function connected(node) {
  let n = node;
  while (n) {
    if (n === document.body || n === document.head) return true;
    n = n.parentNode;
  }
  return false;
}

function makeCtx(node) {
  const ctx = {
    imageSmoothingEnabled: false,
    fillStyle: '#000',
    fillRect(x, y, w, h) {
      if (!(w > 0) || !(h > 0)) return;
      node.paint.push({ x: x / w, y: y / h, c: ctx.fillStyle });
    },
    clearRect() { node.paint.length = 0; },
  };
  return ctx;
}

function el(tag) {
  const node = {
    tagName: tag,
    className: '',
    id: '',
    style: {},
    dataset: {},
    children: [],
    parentNode: null,
    hidden: false,
    textContent: '',
    width: 0,
    height: 0,
    offsetWidth: 120,
    offsetHeight: 48,
    paint: [],
  };
  Object.defineProperty(node, 'classList', { get() { return classListFor(node); } });
  Object.defineProperty(node, 'innerHTML', {
    get() { return node._html || ''; },
    set(v) { node._html = String(v); node.children.length = 0; },
  });
  Object.defineProperty(node, 'isConnected', { get() { return connected(node); } });
  node.appendChild = (c) => { c.parentNode = node; node.children.push(c); return c; };
  node.prepend = (c) => { c.parentNode = node; node.children.unshift(c); return c; };
  node.remove = () => {
    const p = node.parentNode;
    if (!p) return;
    const i = p.children.indexOf(node);
    if (i >= 0) p.children.splice(i, 1);
    node.parentNode = null;
  };
  node.addEventListener = () => {};
  node.getContext = () => makeCtx(node);
  node.querySelectorAll = (sel) => queryAll(node, sel);
  node.querySelector = (sel) => queryAll(node, sel)[0] || null;
  node.getBoundingClientRect = () => {
    const w = node.width || 33;
    const h = node.height || 39;
    return { x: 100, y: 80, left: 100, top: 80, right: 100 + w, bottom: 80 + h, width: w, height: h };
  };
  return node;
}

const head = el('head');
const body = el('body');
globalThis.document = {
  head,
  body,
  createElement: (tag) => el(tag),
  getElementById(id) {
    const walk = (n) => {
      if (!n) return null;
      if (n.id === id) return n;
      for (const c of n.children) {
        const f = walk(c);
        if (f) return f;
      }
      return null;
    };
    return walk(body) || walk(head);
  },
};
globalThis.window = { innerWidth: 1280, innerHeight: 720 };
globalThis.MutationObserver = class { observe() {} disconnect() {} };

function piece(slot, name, mods, rar = 1) {
  return { slot, name, mods, rar, gems: [], up: 0, procs: [], lv: 8 };
}

function setup() {
  for (const c of [...document.body.children]) c.remove();
  for (const c of [...document.head.children]) c.remove();
  const layer = document.createElement('div');
  layer.id = 'fxlayer';
  document.body.appendChild(layer);
  const hero = document.createElement('div');
  hero.id = 'heroBody';
  document.body.appendChild(hero);
  const G = {
    S: { gear: {}, bag: [], mode: 'adventurer', gems: {} },
    title: false,
    downed: false,
    toast() {},
  };
  const loot = new Loot(G);
  loot.ctx = {
    collide: null,
    heightAt: () => 1,
    project: () => ({ x: 400, y: 300 }),
    player: { x: 0, y: 0, z: 0, quad: { visible: true } },
  };
  G.loot = loot;
  G.ctx = loot.ctx;
  const arrows = attachArrows(G);
  return { G, loot, arrows, hero };
}

function garrow(drop) {
  return drop && drop.el ? drop.el.querySelector('canvas.garrow') : null;
}

function lastPaint(cv) {
  const cells = new Map();
  for (const p of cv.paint) cells.set(p.x + ',' + p.y, p.c);
  return cells;
}

// Rows whose glyph (hi or mid, not the lo outline) is a wide bar. Groups are separated by a gap row.
function barGroups(cv, ramp) {
  const cells = lastPaint(cv);
  const ys = [];
  for (let y = 0; y < 13; y++) {
    let n = 0;
    for (let x = 0; x < 11; x++) {
      const c = cells.get(x + ',' + y);
      if (c === ramp.hi || c === ramp.mid) n++;
    }
    if (n >= 7) ys.push(y);
  }
  const groups = [];
  for (const y of ys) {
    if (!groups.length || y > groups[groups.length - 1].at(-1) + 1) groups.push([y]);
    else groups[groups.length - 1].push(y);
  }
  return groups;
}

const gloves = piece('gloves', 'Kept gloves', { crit: 0.01 });
const same = piece('gloves', 'Same gloves', { meleeMul: 0.03 });
const better = piece('gloves', 'Better gloves', { meleeMul: 0.05 });
const worse = piece('gloves', 'Worse gloves', { hpAdd: 1 });

test('better is up green, worse is down red, empty slot is up', () => {
  assert.equal(arrowKind(better, { gloves }), 'up');
  assert.equal(arrowKind(worse, { gloves }), 'down');
  assert.equal(arrowKind(worse, {}), 'up');
  assert.equal(arrowKind(worse, { gloves: null }), 'up');
  const { G, arrows } = setup();
  G.S.gear = { gloves };
  arrows.spawn(better, 4, 4);
  arrows.spawn(worse, 4, 6);
  const lootDrops = document.getElementById('fxlayer').querySelectorAll('canvas.garrow');
  assert.equal(lootDrops.length, 2);
  const dirs = lootDrops.map((cv) => cv.dataset.dir).sort();
  assert.deepEqual(dirs, ['down', 'up']);
  const upCv = lootDrops.find((cv) => cv.dataset.dir === 'up');
  const downCv = lootDrops.find((cv) => cv.dataset.dir === 'down');
  assert.ok(upCv.paint.some((p) => p.c === ARROW_PAL.up.mid));
  assert.ok(downCv.paint.some((p) => p.c === ARROW_PAL.down.mid));
  assert.equal(upCv.width, 33);
  assert.equal(upCv.height, 39);
  assert.equal(upCv.style.zIndex, '5');
  assert.equal(barGroups(upCv, ARROW_PAL.up).length, 1);
  assert.equal(barGroups(downCv, ARROW_PAL.down).length, 1);
});

test('ring slot rules stay on compareToEquipped; equal ring is an equals marker', () => {
  const rings = {
    ringL: piece('ringL', 'strong', { crit: 0.04 }),
    ringR: piece('ringR', 'weak', { crit: 0.01 }),
  };
  assert.equal(arrowKind(piece('ringL', 'above', { crit: 0.02 }), rings), 'up');
  assert.equal(arrowKind(piece('ringR', 'under', { crit: 0.005 }), rings), 'down');
  assert.equal(arrowKind(piece('ringL', 'tie', { crit: 0.01 }), rings), 'equal');
  assert.equal(arrowKind(piece('ringL', 'open', { hpAdd: 1 }), { ringL: rings.ringL, ringR: null }), 'up');
  assert.equal(arrowKind(piece('ringR', 'open', { hpAdd: 1 }), { ringL: null, ringR: null }), 'up');
  assert.equal(arrowKind(piece('helm', 'filled', { hpAdd: 1 }), { helm: piece('helm', 'big', { meleeMul: 0.2 }) }), 'down');
  assert.equal(arrowKind(piece('primary', 'same hand', { meleeMul: 0.04, spellMul: 0.04 }), { primary: piece('primary', 'kept', { meleeMul: 0.04, spellMul: 0.04 }) }), 'equal');
});

test('consumables, gold, gems and purse get no marker', () => {
  assert.equal(arrowKind({ name: 'Hearth tonic' }, {}), 'none');
  assert.equal(arrowKind({ name: 'brew' }, { gloves }), 'none');
  const { G, loot, arrows } = setup();
  G.S.gear = { gloves };
  const gold = loot.drop(3, 3, { gold: 4 });
  const gem = loot.drop(3, 5, { gem: 'rift_shard' });
  const purse = loot.drop(5, 3, { gold: 9, purse: true });
  const tonic = loot.drop(5, 5, { item: { name: 'Hearth tonic', mods: {} } });
  loot.update(0.05);
  loot.update(0.05);
  for (const d of [gold, gem, purse, tonic]) {
    assert.equal(d.el.querySelectorAll('canvas.garrow').length, 0, d.el.className);
  }
  assert.equal(arrows.qa().length, 1);
  assert.equal(arrows.qa()[0].arrow, 'none');
  assert.equal(arrows.qa()[0].shown, false);
});

test('equal-score gear uses the same placeWorld size as up and down and survives update', () => {
  const { G, loot, arrows } = setup();
  G.S.gear = { gloves };
  const dEq = arrows.spawn(same, 5, 5);
  const dUp = arrows.spawn(better, 7, 5);
  const dDn = arrows.spawn(worse, 9, 5);
  for (let i = 0; i < 4; i++) loot.update(0.05);
  const eq = garrow(dEq);
  const up = garrow(dUp);
  const dn = garrow(dDn);
  assert.ok(eq && eq.isConnected);
  assert.equal(eq.dataset.dir, 'equal');
  assert.equal(eq.parentNode, dEq.el);
  assert.equal(eq.width, up.width);
  assert.equal(eq.height, up.height);
  assert.equal(eq.width, 33);
  assert.equal(eq.height, 39);
  assert.equal(eq.style.width, up.style.width);
  assert.equal(eq.style.height, dn.style.height);
  assert.equal(eq.style.left, up.style.left);
  assert.equal(eq.style.top, up.style.top);
  assert.equal(eq.style.zIndex, up.style.zIndex);
  assert.equal(eq.style.zIndex, '5');
  assert.equal(eq.style.left, (-eq.width / 2) + 'px');
  const colors = new Set(eq.paint.map((p) => p.c));
  for (const c of colors) assert.ok(c === BLUE.hi || c === BLUE.mid || c === BLUE.lo, c);
  assert.ok(colors.has(BLUE.mid));
  assert.equal(barGroups(eq, BLUE).length, 2);
  assert.ok(barGroups(eq, BLUE)[1][0] - barGroups(eq, BLUE)[0].at(-1) >= 2);
  assert.equal(dEq.el.querySelector('canvas.beam') != null, dUp.el.querySelector('canvas.beam') != null);
});

test('qa reports arrow equal with shown true', () => {
  const { G, arrows } = setup();
  G.S.gear = { gloves };
  arrows.spawn(same, 5, 5);
  arrows.spawn(better, 7, 5);
  const rows = arrows.qa();
  const eq = rows.find((r) => r.name === 'Same gloves');
  const up = rows.find((r) => r.name === 'Better gloves');
  assert.equal(eq.dir, 0);
  assert.equal(eq.arrow, 'equal');
  assert.equal(eq.shown, true);
  assert.equal(eq.color, BLUE.mid);
  assert.equal(up.arrow, 'up');
  assert.equal(up.color, ARROW_PAL.up.mid);
  assert.equal(up.shown, true);
});

test('bag rows and tooltip show up, down, and SAME', () => {
  const { G, arrows, hero } = setup();
  G.S.gear = { gloves };
  G.S.bag = [same, better, worse, { name: 'Hearth tonic' }];
  for (const it of G.S.bag) {
    const row = document.createElement('div');
    row.className = 'row gear';
    const name = document.createElement('em');
    name.className = 'iname';
    name.textContent = it.name;
    row.appendChild(name);
    hero.appendChild(row);
  }
  arrows.markBag();
  const rows = [...hero.children].filter((el) => el.classList.contains('row'));
  const mark = (row) => row.querySelector('canvas.garrow');
  assert.ok(mark(rows[0]), 'equal bag row has a marker');
  assert.equal(mark(rows[0]).dataset.dir, 'equal');
  assert.equal(mark(rows[1]).dataset.dir, 'up');
  assert.equal(mark(rows[2]).dataset.dir, 'down');
  assert.equal(mark(rows[3]), null);
  assert.equal(mark(rows[0]).width, mark(rows[1]).width);
  assert.equal(mark(rows[0]).height, 26);
  assert.equal(arrows.showTip(0), true);
  const tip = document.getElementById('gearArrowTip');
  assert.equal(tip.dataset.kind, 'equal');
  assert.equal(tip.hidden, false);
  assert.equal(tip.querySelector('.gat-tag').textContent, 'SAME');
  assert.equal(tip.querySelector('.gat-tag').style.color, BLUE.mid);
  assert.equal(tip.querySelector('canvas.garrow').dataset.dir, 'equal');
  assert.equal(arrows.showTip(1), true);
  assert.equal(tip.dataset.kind, 'up');
  assert.equal(tip.querySelector('.gat-tag').textContent, 'UPGRADE');
  assert.equal(tip.querySelector('.gat-tag').style.color, ARROW_PAL.up.mid);
  assert.equal(arrows.showTip(2), true);
  assert.equal(tip.dataset.kind, 'down');
  assert.equal(tip.querySelector('.gat-tag').textContent, 'WORSE');
  assert.equal(tip.querySelector('.gat-tag').style.color, ARROW_PAL.down.mid);
});
