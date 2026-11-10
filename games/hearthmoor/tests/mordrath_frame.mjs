// Mordrath crown framing. node:test, no DOM.
// Reprojects the settled O9 camera from the real scene, sheet, and sprite placement,
// then checks the pull combat actually requests.
// Run: node --test tests/mordrath_frame.mjs
import { readFileSync, readdirSync } from 'node:fs';
import { inflateSync } from 'node:zlib';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../vendor/three.module.js';
import { framePullFor } from '../game/combat.js';
import * as combat from '../game/combat.js';
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
const helSrc = read('game/helheim.js');

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
// Settled QA stance (hero pinned, boss left on his mark). Engage is the O9 trigger just south of it.
const QA_HERO = { x: 0, z: -36.6 };
const engageLine = helSrc.match(/sp\.o9 && p\.z < (-[\d.]+)/);
const ENGAGE_Z = Number(engageLine[1]);
const MARGIN = 4;
const VIEWS = {
  qa: { w: 960, h: 540, label: '960x540' },
  phone: { w: 390, h: 844, label: '390x844 phone' },
};

const collide = new Collide(scene.collision);
const heroY = collide.height(QA_HERO.x, QA_HERO.z);
const bossY = collide.height(BOSS_AT.mordrath[0], BOSS_AT.mordrath[1]);

function aspectScale(w, h) {
  const a = w / h;
  return a < ASPECT_WIDE ? Math.min(ASPECT_CAP, ASPECT_NUM / a) : 1;
}

function project(pull, w, h, hero, lift = 0) {
  const pitch = THREE.MathUtils.degToRad(C.pitch);
  const camDir = new THREE.Vector3(0, Math.sin(pitch), Math.cos(pitch));
  // Settled frameLook raises the aim. Locked orientation, so camera = (target + up*lift) + camDir * d.
  const target = new THREE.Vector3(hero.x, (heroY ?? 0) + (lift || 0), hero.z).add(new THREE.Vector3(...C.look));
  target.x = THREE.MathUtils.clamp(target.x, C.bounds[0], C.bounds[2]);
  target.z = THREE.MathUtils.clamp(target.z, C.bounds[1], C.bounds[3]);
  const d = C.distance * aspectScale(w, h) * pull;
  const camera = new THREE.PerspectiveCamera(C.fov, w / h, 1, FAR);
  camera.position.copy(target).addScaledVector(camDir, d);
  camera.quaternion.setFromEuler(new THREE.Euler(-pitch, 0, 0, 'YXZ'));
  camera.updateMatrixWorld();
  const p0 = target.clone().project(camera);
  const p1 = new THREE.Vector3(target.x, target.y + HEIGHT_M, target.z).project(camera);
  const px = Math.abs(p1.y - p0.y) * 0.5 * h;
  const k = Math.max(1, Math.round(px / (HERO_FH - 1)));
  const boss = new THREE.Vector3(BOSS_AT.mordrath[0], bossY ?? 0, BOSS_AT.mordrath[1]);
  const toCam = camera.position.clone().sub(boss).normalize().multiplyScalar(FEET_BIAS);
  const feetW = boss.clone().add(toCam);
  const bossDist = camera.position.distanceTo(feetW);
  const feet = feetW.clone().project(camera);
  const sx = Math.round((feet.x * 0.5 + 0.5) * w);
  const sy = Math.round((feet.y * 0.5 + 0.5) * h);
  const yTop = h - (sy + PIVOT_Y * k);
  const topPx = sy + PIVOT_Y * k;
  const ndcTop = (topPx / h) * 2 - 1;
  const overPx = (ndcTop - 1) * h / 2;
  const tall = BOSS_FH / HERO_FH;
  const head = new THREE.Vector3(boss.x, boss.y + HEIGHT_M * tall, boss.z).project(camera);
  const headTop = h - (head.y * 0.5 + 0.5) * h;
  const depthHead = feetW.clone();
  depthHead.y += HEIGHT_M * tall;
  const depthZ = depthHead.project(camera).z;
  return { pull, lift: lift || 0, k, sx, sy, yTop, ndcTop, overPx, headTop, x0: sx - bossMeta.pivot[0] * k, d, px, bossDist, feetZ: feet.z, depthZ };
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

function skipSpace(src, i) {
  for (;;) {
    while (i < src.length && /\s/.test(src[i])) i++;
    if (src.startsWith('//', i)) { const n = src.indexOf('\n', i); i = n < 0 ? src.length : n + 1; continue; }
    if (src.startsWith('/*', i)) { const n = src.indexOf('*/', i + 2); i = n < 0 ? src.length : n + 2; continue; }
    return i;
  }
}

function matchingBrace(src, open) {
  let i = open, depth = 0, str = null;
  while (i < src.length) {
    const c = src[i];
    if (str) {
      if (c === '\\') { i += 2; continue; }
      if (c === str) str = null;
      i++; continue;
    }
    if (c === '/' && src[i + 1] === '/') { const n = src.indexOf('\n', i); i = n < 0 ? src.length : n + 1; continue; }
    if (c === '/' && src[i + 1] === '*') { const n = src.indexOf('*/', i + 2); i = n < 0 ? src.length : n + 2; continue; }
    if (c === '"' || c === "'" || c === '`') { str = c; i++; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return i; }
    i++;
  }
  throw new Error('unbalanced brace at ' + open);
}

function fieldAtDepth1(body, name) {
  let i = 0, depth = 1, str = null;
  const key = name;
  while (i < body.length) {
    const c = body[i];
    if (str) {
      if (c === '\\') { i += 2; continue; }
      if (c === str) str = null;
      i++; continue;
    }
    if (c === '/' && body[i + 1] === '/') { const n = body.indexOf('\n', i); i = n < 0 ? body.length : n + 1; continue; }
    if (c === '/' && body[i + 1] === '*') { const n = body.indexOf('*/', i + 2); i = n < 0 ? body.length : n + 2; continue; }
    if (c === '"' || c === "'" || c === '`') { str = c; i++; continue; }
    if (c === '{') depth++;
    else if (c === '}') depth--;
    else if (depth === 1 && body.startsWith(key, i) && !/[\w$]/.test(body[i + key.length] || '')) {
      let j = skipSpace(body, i + key.length);
      if (body[j] === ':') {
        j = skipSpace(body, j + 1);
        const m = body.slice(j).match(/^(-?\d+(?:\.\d+)?)/);
        if (m) return Number(m[1]);
      }
    }
    i++;
  }
  return undefined;
}

function entriesOf(objSrc) {
  const open = objSrc.indexOf('{');
  const close = matchingBrace(objSrc, open);
  const body = objSrc.slice(open + 1, close);
  const out = {};
  let i = 0, depth = 0, str = null, keyStart = -1, valueOpen = -1;
  while (i < body.length) {
    const c = body[i];
    if (str) {
      if (c === '\\') { i += 2; continue; }
      if (c === str) str = null;
      i++; continue;
    }
    if (c === '/' && body[i + 1] === '/') { const n = body.indexOf('\n', i); i = n < 0 ? body.length : n + 1; continue; }
    if (c === '/' && body[i + 1] === '*') { const n = body.indexOf('*/', i + 2); i = n < 0 ? body.length : n + 2; continue; }
    if (c === '"' || c === "'" || c === '`') { str = c; i++; continue; }
    if (depth === 0 && keyStart < 0 && /[A-Za-z_$]/.test(c)) keyStart = i;
    if (c === '{' || c === '(' || c === '[') {
      if (depth === 0 && c === '{' && keyStart >= 0) valueOpen = i;
      depth++;
    } else if (c === '}' || c === ')' || c === ']') {
      depth--;
      if (depth === 0 && c === '}' && keyStart >= 0 && valueOpen >= 0) {
        const colon = body.indexOf(':', keyStart);
        const key = body.slice(keyStart, colon).trim().replace(/^['"]|['"]$/g, '');
        const interior = body.slice(valueOpen + 1, i);
        out[key] = { scale: fieldAtDepth1(interior, 'scale'), framePull: fieldAtDepth1(interior, 'framePull'), frameLift: fieldAtDepth1(interior, 'frameLift') };
        keyStart = -1;
        valueOpen = -1;
      }
    }
    i++;
  }
  return out;
}

function enemyCatalog() {
  const found = {};
  const files = readdirSync(join(root, 'game')).filter((n) => n.endsWith('.js'));
  for (const file of files) {
    const src = read('game/' + file);
    const take = (objSrc) => {
      let table;
      try { table = entriesOf(objSrc); } catch { return; }
      for (const [k, v] of Object.entries(table)) {
        if (v.scale >= 4) found[k] = { ...v, file };
      }
    };
    let idx = 0;
    while ((idx = src.indexOf('Object.assign(ENEMIES', idx)) >= 0) {
      const paren = src.indexOf('(', idx);
      const arg = skipSpace(src, paren + 'Object.assign(ENEMIES'.length - 'Object.assign'.length);
      // recompute arg start after the comma
      const comma = src.indexOf(',', idx);
      const after = skipSpace(src, comma + 1);
      if (src[after] === '{') {
        const end = matchingBrace(src, after);
        take(src.slice(after, end + 1));
      } else {
        const name = src.slice(after).match(/^([A-Za-z_$][\w$]*)/)[1];
        const decl = src.search(new RegExp('(?:export\\s+)?const\\s+' + name + '\\s*=\\s*\\{'));
        if (decl >= 0) {
          const brace = src.indexOf('{', decl);
          take(src.slice(brace, matchingBrace(src, brace) + 1));
        }
      }
      idx = comma + 1;
    }
    const decl = src.search(/(?:export\s+)?const\s+ENEMIES\s*=\s*\{/);
    if (decl >= 0) {
      const brace = src.indexOf('{', decl);
      take(src.slice(brace, matchingBrace(src, brace) + 1));
    }
  }
  return found;
}

function pullLoop(src) {
  const start = src.indexOf('let pullF = 1');
  const end = src.indexOf('ctx.framePull', start);
  return src.slice(start, end);
}

function sourceRequested(def) {
  const loop = pullLoop(combatSrc);
  const honors = /requestedPull\s*\(/.test(loop) || /\bframePull\b/.test(loop) && /D\.framePull/.test(loop);
  if (honors && Number(def.framePull) > 0) return Number(def.framePull);
  return framePullFor(def.scale || 1);
}

function engineCap(override) {
  const at = mainSrc.indexOf('framePull:');
  const snippet = mainSrc.slice(at, at + 360);
  const honors = /framePull:\s*\(\s*f\s*,\s*cap\s*\)/.test(snippet) && /cap\s*>\s*2\.4/.test(snippet);
  return honors && typeof override === 'number' && override > 2.4 ? override : 2.4;
}

function acceptedPull(def) {
  const req = sourceRequested(def);
  const hi = engineCap(Number(def.framePull) > 0 ? Number(def.framePull) : undefined);
  return Math.min(hi, Math.max(1, req || 1));
}

// Look-target lift is applied only when combat passes D.frameLift through frameLook and the engine eases lookLift onto the aim.
function sourceLift(def) {
  const loop = pullLoop(combatSrc);
  const honors = /frameLook\s*\(/.test(loop) && /D\.frameLift/.test(loop)
    && /lookLiftTo/.test(mainSrc) && /frameLook\s*:/.test(mainSrc)
    && /position\.y\s*\+=\s*lookLift/.test(mainSrc);
  if (honors && Number(def.frameLift) > 0) return Number(def.frameLift);
  return 0;
}

const extents = Object.fromEntries(MORDRATH_ROLES.map((role) => [role, opaqueExtent(role)]));
const catalog = enemyCatalog();

function placed(pull, view, hero, lift = 0) {
  const r = project(pull, view.w, view.h, hero, lift);
  return MORDRATH_ROLES.map((role) => {
    const ext = extents[role];
    return { role, crown: r.yTop + ext.top * r.k, feet: r.yTop + ext.bot * r.k, ...r };
  });
}

test('pull 2.26 on 960x540 reproduces the settled crown clip', () => {
  const r = project(2.26, 960, 540, QA_HERO);
  const ext = extents.mordrath;
  const crown = r.yTop + ext.top * r.k;
  const feet = r.yTop + ext.bot * r.k;
  console.log([
    `camera ossuary2 fov ${C.fov} pitch ${C.pitch} distance ${C.distance} look ${JSON.stringify(C.look)} bounds ${JSON.stringify(C.bounds)}`,
    `heights hero ${heroY} boss ${bossY}  bossAt ${JSON.stringify(BOSS_AT.mordrath)} qaHero ${JSON.stringify(QA_HERO)} engage z < ${ENGAGE_Z}`,
    `sheet ${BOSS_FW}x${BOSS_FH} pivot ${JSON.stringify(bossMeta.pivot)} ground_row ${GROUND_ROW} heroFh ${HERO_FH} heightM ${HEIGHT_M} feetBias ${FEET_BIAS} tall ${BOSS_FH / HERO_FH}`,
    `opaque crown row ${ext.top} feet row ${ext.bot} (combat frames, all 3 roles ${JSON.stringify(extents)})`,
    `pull 2.26 k ${r.k} anchor (${r.sx},${r.sy}) frame x ${r.x0} yTop ${r.yTop} ndcTop ${r.ndcTop.toFixed(5)} overPx ${r.overPx.toFixed(2)} headProxy ${r.headTop.toFixed(2)} round ${Math.round(r.headTop)}`,
    `crown screen ${crown} feet screen ${feet}  (QA rect y -12, feet 228, opaque feet 227, head 26)`,
  ].join('\n'));
  assert.equal(heroY, 0);
  assert.equal(bossY, 0);
  assert.equal(ext.top, 0, 'crown pixels start on frame row 0');
  assert.equal(ext.bot, GROUND_ROW);
  assert.equal(r.k, 1);
  assert.equal(r.yTop, -12);
  assert.equal(r.x0, 408);
  assert.equal(crown, -12);
  assert.equal(feet, 227);
  assert.ok(Math.abs(r.overPx - 12) < 0.05, 'ndc overshoot ' + r.overPx);
  assert.equal(Math.round(r.headTop), 26);
  assert.equal(framePullFor(8), 2.26);
});

test('Mordrath phases get a pull that fits crown and feet; other scale>=4 foes stay on the curve', () => {
  assert.deepEqual([...MORDRATH_ROLES], ['mordrath', 'mordrath_p2', 'mordrath_p3']);
  assert.equal(catalog.mordrath.scale, 8);
  assert.equal(ENEMIES.mordrath.scale, catalog.mordrath.scale);
  assert.equal(ENEMIES.mordrath.framePull, catalog.mordrath.framePull);
  const must = ['vharzul', 'aurelion', 'hrimgard', 'sylvaine', 'sylvaine_reflection', 'gorrak', 'colossus', 'kael', 'veyra', 'nettlecrown', 'blightregent', 'hjortur', 'hjortur_corrupted', 'sentinelprime', 'mordrath'];
  for (const id of must) assert.ok(catalog[id], 'missing ENEMIES.' + id);
  assert.equal(Object.keys(catalog).length, must.length);

  const def = catalog.mordrath;
  const accepted = acceptedPull(def);
  const lift = sourceLift(def);
  if (typeof combat.requestedPull === 'function') {
    assert.equal(combat.requestedPull(ENEMIES.mordrath), sourceRequested(def));
  }
  const stances = [
    { name: 'qa settled', hero: QA_HERO },
    { name: 'o9 engage', hero: { x: 0, z: ENGAGE_Z - 1e-3 } },
  ];
  for (const stance of stances) {
    for (const view of Object.values(VIEWS)) {
      const rows = placed(accepted, view, stance.hero, lift);
      for (const row of rows) {
        assert.ok(row.crown >= MARGIN && row.feet <= view.h - MARGIN,
          `${stance.name} ${view.label} ${row.role} pull ${accepted} lift ${lift} crown ${row.crown} feet ${row.feet} (need crown >= ${MARGIN} and feet <= ${view.h - MARGIN}). scale curve 2.26 with no look lift leaves the quad 12px above 960x540.`);
        assert.ok(row.bossDist < FAR && row.feetZ < 1 && row.depthZ < 1,
          `${stance.name} ${view.label} boss depth ${row.bossDist.toFixed(2)} feetZ ${row.feetZ.toFixed(3)} headZ ${row.depthZ.toFixed(3)} crosses far plane ${FAR}`);
      }
    }
  }
  for (const [id, foe] of Object.entries(catalog)) {
    if (id === 'mordrath') continue;
    const got = acceptedPull(foe);
    const curve = framePullFor(foe.scale);
    assert.equal(got, curve, `${id} scale ${foe.scale} pull ${got} changed from framePullFor ${curve}`);
    assert.equal(sourceLift(foe), 0, id + ' must not take Mordrath\'s look lift');
    assert.ok(got <= 2.4, id + ' stayed under the ordinary cap');
  }
  console.log(`accepted Mordrath pull ${accepted} lift ${lift} (framePullFor 8 = ${framePullFor(8)}, engine cap for an override ${engineCap(def.framePull)}, far ${FAR})`);
});
