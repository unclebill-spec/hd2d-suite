// Mordrath's name bar must sit under his feet, not on his crown or his face.
// node:test, no DOM. Reprojects the settled QA camera the way tests/mordrath_frame.mjs does,
// then places #bossbar from the numbers in game/game.css.
// Run: node --test tests/mordrath_frame.mjs tests/mordrath_nameplate.mjs
import { readFileSync } from 'node:fs';
import { inflateSync } from 'node:zlib';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../vendor/three.module.js';
import { framePullFor, frameLiftFor, bossBarLow } from '../game/combat.js';
import { ENEMIES } from '../game/heroes.js';
import { BOSS_AT, MORDRATH_ROLES } from '../game/helheim_boss.js';
import { Collide } from '../engine/collide.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (rel) => readFileSync(join(root, rel), 'utf8');
const scene = JSON.parse(read('areas/ossuary2/scene.json'));
const actorsMeta = JSON.parse(read('areas/ossuary2/public/art/sprite/actors.json'));
const bossMeta = JSON.parse(read('areas/ossuary2/public/art/sprite/boss_mordrath.json'));
const spritesSrc = read('engine/sprites.js');
const mainSrc = read('engine/main.js');
const combatSrc = read('game/combat.js');
const gameCss = read('game/game.css');
const hudCss = read('engine/hud.css');
const menuCss = read('game/menu.css');
const classicCss = read('game/menu-classic.css');

const C = scene.camera;
const HEIGHT_M = Number(spritesSrc.match(/this\.heightM = ([\d.]+)/)[1]);
const FEET_BIAS = Number(spritesSrc.match(/multiplyScalar\(([\d.]+)\)/)[1]);
const aspectFn = mainSrc.match(/function aspectScale\(\) \{[^}]+\}/)[0];
const ASPECT_WIDE = Number(aspectFn.match(/a < ([\d.]+)/)[1]);
const ASPECT_CAP = Number(aspectFn.match(/Math\.min\(([\d.]+)/)[1]);
const ASPECT_NUM = Number(aspectFn.match(/([\d.]+) \/ a/)[1]);
const FAR = Number(mainSrc.match(/new THREE\.PerspectiveCamera\(C\.fov,\s*1,\s*1,\s*([\d.]+)\)/)[1]);
const HERO_FH = actorsMeta.frame[1];
const BOSS_FW = bossMeta.frame[0];
const BOSS_FH = bossMeta.frame[1];
const PIVOT_Y = bossMeta.pivot[1];
const GROUND_ROW = bossMeta.ground_row;
const QA_HERO = { x: 0, z: -36.6 };
const GAP = 4;
const VIEWS = {
  qa: { w: 960, h: 540, label: '960x540' },
  phone: { w: 390, h: 844, label: '390x844 phone' },
};

const collide = new Collide(scene.collision);
const heroY = collide.height(QA_HERO.x, QA_HERO.z);
const bossPt = { x: BOSS_AT.mordrath[0], z: BOSS_AT.mordrath[1] };
const bossY = collide.height(bossPt.x, bossPt.z);

function aspectScale(w, h) {
  const a = w / h;
  return a < ASPECT_WIDE ? Math.min(ASPECT_CAP, ASPECT_NUM / a) : 1;
}

function project(pull, w, h, hero, lift = 0) {
  const pitch = THREE.MathUtils.degToRad(C.pitch);
  const camDir = new THREE.Vector3(0, Math.sin(pitch), Math.cos(pitch));
  const ground = (x, z, fallback) => { const y = collide.height(x, z); return y == null ? fallback : y; };
  const heroGround = ground(hero.x, hero.z, heroY ?? 0);
  const target = new THREE.Vector3(hero.x, heroGround, hero.z).add(new THREE.Vector3(...C.look));
  target.x = THREE.MathUtils.clamp(target.x, C.bounds[0], C.bounds[2]);
  target.z = THREE.MathUtils.clamp(target.z, C.bounds[1], C.bounds[3]);
  const d = C.distance * aspectScale(w, h) * pull;
  const camera = new THREE.PerspectiveCamera(C.fov, w / h, 1, FAR);
  camera.position.copy(target).addScaledVector(camDir, d);
  camera.position.y += lift || 0;
  camera.quaternion.setFromEuler(new THREE.Euler(-pitch, 0, 0, 'YXZ'));
  camera.updateMatrixWorld();
  const aim = new THREE.Vector3(target.x, target.y + (lift || 0), target.z);
  const p0 = aim.clone().project(camera);
  const p1 = new THREE.Vector3(aim.x, aim.y + HEIGHT_M, aim.z).project(camera);
  const px = Math.abs(p1.y - p0.y) * 0.5 * h;
  const k = Math.max(1, Math.round(px / (HERO_FH - 1)));
  const boss = new THREE.Vector3(bossPt.x, ground(bossPt.x, bossPt.z, bossY ?? 0), bossPt.z);
  function place(pt, fh, pivotX) {
    const toCam = camera.position.clone().sub(pt).normalize().multiplyScalar(FEET_BIAS);
    const feetW = pt.clone().add(toCam);
    const feet = feetW.clone().project(camera);
    const sx = Math.round((feet.x * 0.5 + 0.5) * w);
    const sy = Math.round((feet.y * 0.5 + 0.5) * h);
    const yTop = h - (sy + fh * k);
    return { sx, sy, yTop, x0: sx - pivotX * k };
  }
  const bq = place(boss, BOSS_FH, bossMeta.pivot[0]);
  return { pull, lift: lift || 0, k, yTop: bq.yTop, sx: bq.sx, x0: bq.x0 };
}

function decodePNG(path) {
  const buf = readFileSync(path);
  let o = 8, w = 0, h = 0, ctype = 0;
  const idat = [];
  while (o < buf.length) {
    const len = buf.readUInt32BE(o); o += 4;
    const type = buf.toString('ascii', o, o + 4); o += 4;
    const data = buf.subarray(o, o + len); o += len + 4;
    if (type === 'IHDR') { w = data.readUInt32BE(0); h = data.readUInt32BE(4); ctype = data[9]; }
    else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
  }
  if (ctype !== 6) throw new Error('expected RGBA png, ctype ' + ctype);
  const raw = inflateSync(Buffer.concat(idat));
  const stride = w * 4;
  const out = Buffer.alloc(h * stride);
  let s = 0, prev = Buffer.alloc(stride);
  for (let y = 0; y < h; y++) {
    const filter = raw[s++];
    const row = raw.subarray(s, s + stride); s += stride;
    const dst = out.subarray(y * stride, (y + 1) * stride);
    for (let i = 0; i < stride; i++) {
      const x = row[i];
      const a = i >= 4 ? dst[i - 4] : 0;
      const b = prev[i];
      const c = i >= 4 ? prev[i - 4] : 0;
      let v = x;
      if (filter === 1) v = (x + a) & 255;
      else if (filter === 2) v = (x + b) & 255;
      else if (filter === 3) v = (x + ((a + b) >> 1)) & 255;
      else if (filter === 4) {
        const p = a + b - c;
        const pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
        const pr = pa <= pb && pa <= pc ? a : pb <= pc ? b : c;
        v = (x + pr) & 255;
      } else if (filter !== 0) throw new Error('png filter ' + filter);
      dst[i] = v;
    }
    prev = Buffer.from(dst);
  }
  return { w, h, out };
}

const png = decodePNG(join(root, 'areas/ossuary2/public/art/sprite/boss_mordrath.png'));
const FACINGS = ['down', 'up', 'left', 'right'];
const COMBAT_ANIMS = ['idle', 'walk', 'cast', 'attack'];

function opaqueExtent(roleName) {
  const role = bossMeta.roles[roleName];
  let top = BOSS_FH, bot = -1;
  for (let fi = 0; fi < FACINGS.length; fi++) {
    for (const anim of COMBAT_ANIMS) {
      const spec = bossMeta.anims[anim];
      for (let i = 0; i < spec.count; i++) {
        const x0 = (spec.start + i) * BOSS_FW;
        const y0 = (role.row + fi) * BOSS_FH;
        for (let y = 0; y < BOSS_FH; y++) {
          const row = (y0 + y) * png.w * 4;
          for (let x = 0; x < BOSS_FW; x++) {
            if (png.out[row + (x0 + x) * 4 + 3] === 255) {
              if (y < top) top = y;
              if (y > bot) bot = y;
            }
          }
        }
      }
    }
  }
  return { top, bot };
}

function matchingBrace(src, open) {
  let i = open, depth = 0;
  while (i < src.length) {
    if (src.startsWith('/*', i)) { const n = src.indexOf('*/', i + 2); i = n < 0 ? src.length : n + 2; continue; }
    const c = src[i];
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return i; }
    i++;
  }
  throw new Error('unbalanced brace at ' + open);
}

function rulesIn(css) {
  const out = [];
  let i = 0;
  while (i < css.length) {
    if (css.startsWith('/*', i)) { const n = css.indexOf('*/', i + 2); i = n < 0 ? css.length : n + 2; continue; }
    if (/\s/.test(css[i])) { i++; continue; }
    if (css.startsWith('@media', i)) {
      const open = css.indexOf('{', i);
      const head = css.slice(i, open).trim();
      const close = matchingBrace(css, open);
      for (const r of rulesIn(css.slice(open + 1, close))) out.push({ sel: r.sel, body: r.body, media: r.media ? r.media + ' & ' + head : head });
      i = close + 1;
      continue;
    }
    if (css[i] === '@') {
      const open = css.indexOf('{', i);
      const semi = css.indexOf(';', i);
      if (open >= 0 && (semi < 0 || open < semi)) i = matchingBrace(css, open) + 1;
      else i = semi < 0 ? css.length : semi + 1;
      continue;
    }
    const open = css.indexOf('{', i);
    if (open < 0) break;
    const sel = css.slice(i, open).trim();
    const close = matchingBrace(css, open);
    out.push({ sel, body: css.slice(open + 1, close), media: null });
    i = close + 1;
  }
  return out;
}

function decl(body, prop) {
  const m = body.match(new RegExp('(?:^|;)\\s*' + prop + '\\s*:\\s*([^;]+)'));
  return m ? m[1].trim() : null;
}

function firstPx(value) {
  if (!value) return null;
  const m = String(value).match(/(-?\d+(?:\.\d+)?)px/);
  return m ? Number(m[1]) : null;
}

function minPxVw(expr, viewW) {
  const m = expr.match(/min\(\s*(\d+(?:\.\d+)?)px\s*,\s*(\d+(?:\.\d+)?)vw\s*\)/);
  if (!m) throw new Error('width ' + expr);
  return Math.min(Number(m[1]), Number(m[2]) / 100 * viewW);
}

function defText(file, name) {
  const src = read('game/' + file);
  const re = new RegExp('(?:^|\\n)\\s*' + name + '\\s*:\\s*\\{');
  const m = re.exec(src);
  assert.ok(m, file + ' missing ' + name);
  const open = src.indexOf('{', m.index);
  return src.slice(open, matchingBrace(src, open) + 1);
}

const gameRules = rulesIn(gameCss);
const hudRules = rulesIn(hudCss);
const classicRules = rulesIn(classicCss);
const baseBar = gameRules.find((r) => r.sel === '#bossbar' && !r.media);
const portraitBar = gameRules.find((r) => r.sel === '#bossbar' && r.media && /orientation:\s*portrait/.test(r.media));
const lowBar = gameRules.find((r) => r.sel === '#bossbar.low' && !r.media);
const lowPortrait = gameRules.find((r) => r.sel === '#bossbar.low' && r.media && /orientation:\s*portrait/.test(r.media));

function barHeightPx(rules) {
  const bar = rules.find((r) => r.sel === '#bossbar' && !r.media);
  const name = rules.find((r) => r.sel === '#bossbar b' && !r.media);
  const track = rules.find((r) => r.sel === '#bossbar span' && !r.media);
  const pad = bar.body.match(/padding:\s*(\d+)px\s+\d+px\s+(\d+)px/);
  const border = bar.body.match(/border:\s*(\d+)px/);
  const font = name.body.match(/(\d+)px\s*\/\s*([\d.]+)/);
  const trackH = track.body.match(/height:\s*(\d+)px/);
  const trackB = track.body.match(/border:\s*(\d+)px/);
  const line = Number(font[1]) * Number(font[2]);
  return Number(pad[1]) + Number(pad[2]) + Number(border[1]) * 2 + line + Number(trackH[1]) + Number(trackB[1]) * 2;
}

const barRawH = barHeightPx(gameRules);
const BAR_H = Math.ceil(barRawH);

function barRect(view, cssBottom, widthExpr) {
  const width = minPxVw(widthExpr, view.w);
  const x0 = (view.w - width) / 2;
  const y1 = view.h - cssBottom;
  return { x0, x1: x0 + width, y0: y1 - BAR_H, y1, width, cssBottom };
}

function separated(a, b, gap) {
  return a.x1 <= b.x0 - gap || b.x1 <= a.x0 - gap || a.y1 <= b.y0 - gap || b.y1 <= a.y0 - gap;
}

const extents = Object.fromEntries(MORDRATH_ROLES.map((role) => [role, opaqueExtent(role)]));
const pull = ENEMIES.mordrath.framePull > 0 ? ENEMIES.mordrath.framePull : framePullFor(ENEMIES.mordrath.scale);
const lift = frameLiftFor(ENEMIES.mordrath, QA_HERO, bossPt);

function placed(view) {
  const r = project(pull, view.w, view.h, QA_HERO, lift);
  return MORDRATH_ROLES.map((role) => {
    const ext = extents[role];
    return { role, crown: r.yTop + ext.top * r.k, feet: r.yTop + ext.bot * r.k, ...r };
  });
}

const posed = Object.fromEntries(Object.entries(VIEWS).map(([k, view]) => [k, placed(view)]));

test('Mordrath opts into a low nameplate; other bosses do not', () => {
  assert.equal(ENEMIES.mordrath.barLow, true);
  assert.equal(bossBarLow(ENEMIES.mordrath), true);
  assert.equal(bossBarLow(null), false);
  assert.equal(bossBarLow({}), false);
  assert.match(defText('helheim_boss.js', 'mordrath'), /barLow:\s*true/);
  const others = [
    ['helheim_boss.js', 'vesperin'],
    ['helheim_boss.js', 'odric'],
    ['asgard.js', 'aurelion'],
    ['muspelheim.js', 'vharzul'],
  ];
  for (const [file, id] of others) {
    assert.doesNotMatch(defText(file, id), /barLow/, id + ' must keep the top bar');
    if (ENEMIES[id]) assert.ok(!ENEMIES[id].barLow && !bossBarLow(ENEMIES[id]), id);
  }
  const fn = combatSrc.slice(combatSrc.indexOf('bossBar(e)'), combatSrc.indexOf('qa()'));
  assert.match(fn, /classList\.toggle\(\s*'low'\s*,\s*bossBarLow\(e\.D\)\s*\)/);
});

test('non-opted bosses keep the top bar, and menu sheets do not move it', () => {
  assert.ok(baseBar, 'desktop #bossbar');
  assert.ok(portraitBar, 'portrait #bossbar');
  assert.equal(decl(baseBar.body, 'top'), '10px');
  assert.equal(decl(portraitBar.body, 'top'), '190px');
  assert.equal(decl(baseBar.body, 'bottom'), null);
  assert.equal(decl(portraitBar.body, 'bottom'), null);
  assert.match(portraitBar.media, /max-width:\s*640px/);
  assert.match(portraitBar.media, /orientation:\s*portrait/);
  for (const [file, css] of [['menu.css', menuCss], ['menu-classic.css', classicCss]]) {
    for (const r of rulesIn(css)) {
      if (!/#bossbar\b/.test(r.sel)) continue;
      assert.equal(decl(r.body, 'top'), null, file + ' ' + r.sel);
      assert.equal(decl(r.body, 'bottom'), null, file + ' ' + r.sel);
      assert.equal(decl(r.body, 'position'), null, file + ' ' + r.sel);
    }
  }
});

test('the low bar clears crown-to-feet, the hint, the spell button, and the phone pad', () => {
  assert.ok(lowBar && lowPortrait, 'missing #bossbar.low rules');
  assert.equal(decl(lowBar.body, 'top'), 'auto');
  assert.equal(decl(lowPortrait.body, 'top'), 'auto');
  assert.ok(Math.abs(barRawH - 39) < 1, 'bar height from game.css padding/border/line/track, got ' + barRawH);
  assert.equal(BAR_H, 39);
  assert.equal(pull, 2.26);
  assert.equal(lift, 2);
  const deskBottom = firstPx(decl(lowBar.body, 'bottom'));
  const phoneBottom = firstPx(decl(lowPortrait.body, 'bottom'));
  const deskWidth = decl(baseBar.body, 'width');
  const phoneWidth = decl(portraitBar.body, 'width');
  assert.equal(deskWidth, 'min(340px, 62vw)');
  assert.equal(phoneWidth, 'min(300px, 72vw)');

  const hudFont = decl(hudRules.find((r) => r.sel === '#hud' && !r.media).body, 'font');
  const hint = hudRules.find((r) => r.sel === '.hint' && !r.media);
  const hintBottom = firstPx(decl(hint.body, 'bottom'));
  const hintFs = firstPx(decl(hint.body, 'font-size'));
  const hintLh = Number(hudFont.match(/px\s*\/\s*([\d.]+)/)[1]);
  const hintLine = hintFs * hintLh;

  const clusterRules = hudRules.filter((r) => r.sel === '#pad .cluster' && !r.media && decl(r.body, 'bottom'));
  const clusterBottom = firstPx(decl(clusterRules.at(-1).body, 'bottom'));
  const clusterRight = firstPx(decl(hudRules.find((r) => r.sel === '#pad .cluster' && decl(r.body, 'right')).body, 'right'));
  const act = gameRules.find((r) => r.sel === '#pad .cluster.act' && !r.media);
  const clusterH = firstPx(decl(act.body, 'height'));
  const clusterW = firstPx(decl(act.body, 'width'));

  const spell = classicRules.find((r) => r.sel === '#hud #btnSpell' && !r.media);
  const spellPad = classicRules.find((r) => r.sel === 'body.padon #hud #btnSpell' && !r.media);
  const spellRight = firstPx(decl(spell.body, 'right'));
  const spellDesk = {
    bottom: firstPx(decl(spell.body, 'bottom')),
    w: firstPx(decl(spell.body, 'min-width')),
    h: firstPx(decl(spell.body, 'min-height')),
  };
  const spellPhone = {
    bottom: firstPx(decl(spellPad.body, 'bottom')),
    w: firstPx(decl(spellPad.body, 'min-width')),
    h: firstPx(decl(spellPad.body, 'min-height')),
  };

  const desk = VIEWS.qa;
  const phone = VIEWS.phone;
  const deskBar = barRect(desk, deskBottom, deskWidth);
  const phoneBar = barRect(phone, phoneBottom, phoneWidth);
  const hintTop = desk.h - hintBottom - hintLine;

  for (const row of posed.qa) {
    assert.equal(row.crown, 14, row.role);
    assert.equal(row.feet, 253, row.role);
    assert.ok(deskBar.y0 >= row.feet + GAP, `${row.role} desktop bar ${deskBar.y0}-${deskBar.y1} overlaps crown ${row.crown} feet ${row.feet}`);
  }
  for (const row of posed.phone) {
    assert.equal(row.crown, 169, row.role);
    assert.equal(row.feet, 408, row.role);
    assert.ok(phoneBar.y0 >= row.feet + GAP, `${row.role} phone bar ${phoneBar.y0}-${phoneBar.y1} overlaps crown ${row.crown} feet ${row.feet}`);
  }

  const legacyDesk = { y0: firstPx(decl(baseBar.body, 'top')), y1: firstPx(decl(baseBar.body, 'top')) + BAR_H };
  const legacyPhone = { y0: firstPx(decl(portraitBar.body, 'top')), y1: firstPx(decl(portraitBar.body, 'top')) + BAR_H };
  assert.ok(legacyDesk.y0 < posed.qa[0].crown && legacyDesk.y1 > posed.qa[0].crown, 'the unchanged top bar is what covers the desktop crown');
  assert.ok(legacyPhone.y0 < posed.phone[0].feet && legacyPhone.y1 > posed.phone[0].crown, 'the unchanged portrait top bar is what covers his face');

  assert.ok(deskBar.y1 <= hintTop - GAP, `desktop bar bottom ${deskBar.y1} runs into the hint at ${hintTop}`);
  assert.ok(hintTop - deskBar.y1 <= 24, `desktop bar should sit just above the hint, gap ${hintTop - deskBar.y1}`);

  const spellBox = (view, spec) => {
    const x1 = view.w - spellRight;
    const y1 = view.h - spec.bottom;
    return { x0: x1 - spec.w, x1, y0: y1 - spec.h, y1 };
  };
  assert.ok(separated(deskBar, spellBox(desk, spellDesk), GAP), 'desktop bar meets #btnSpell');
  assert.ok(separated(phoneBar, spellBox(phone, spellPhone), GAP), 'phone bar meets the pad spell button');
  assert.ok(separated(phoneBar, spellBox(phone, spellDesk), GAP), 'phone bar meets #btnSpell when the pad is off');

  const cluster = {
    x0: phone.w - clusterRight - clusterW,
    x1: phone.w - clusterRight,
    y0: phone.h - clusterBottom - clusterH,
    y1: phone.h - clusterBottom,
  };
  assert.ok(separated(phoneBar, cluster, GAP), `phone bar ${phoneBar.y0}-${phoneBar.y1} overlaps the action cluster ${cluster.y0}-${cluster.y1}`);
  assert.equal(clusterBottom + clusterH, 190, 'cluster top is bottom 18px + height 172px');
  assert.ok(phoneBar.y1 <= cluster.y0 - GAP, 'phone bar must sit above the whole cluster band');

  console.log([
    `pull ${pull} lift ${lift} barH ${barRawH} -> ${BAR_H}`,
    `desktop crown ${posed.qa[0].crown} feet ${posed.qa[0].feet} bar y ${deskBar.y0}-${deskBar.y1} (bottom ${deskBottom}px) hintTop ${hintTop.toFixed(1)}`,
    `phone crown ${posed.phone[0].crown} feet ${posed.phone[0].feet} bar y ${phoneBar.y0}-${phoneBar.y1} (bottom ${phoneBottom}px) cluster y ${cluster.y0}-${cluster.y1}`,
  ].join('\n'));
});
