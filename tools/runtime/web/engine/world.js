// World (the blurred-able diorama): kit .glb pieces, layered-card trees, lights. Lit Lambert, never PBR chrome.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';

const loader = new GLTFLoader();
const texLoader = new THREE.TextureLoader();
const glbCache = new Map();

export function loadGLB(url) {
  if (!glbCache.has(url)) glbCache.set(url, new Promise((res, rej) => loader.load(url, (g) => res(g.scene), undefined, rej)));
  return glbCache.get(url).then((s) => s.clone(true));
}

export function loadImage(url) {
  return new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = url; });
}

// glTF PBR(roughness 1) -> Lambert. Windows / lamp glass become emissive slots the clock drives.
export function litify(root, slots) {
  root.traverse((o) => {
    if (!o.isMesh) return;
    const src = o.material;
    const name = src.name || '';
    let m;
    const common = { vertexColors: true, side: src.side };
    if (src.map) {
      src.map.magFilter = THREE.NearestFilter;               // chunky texels up close
      src.map.minFilter = THREE.LinearMipmapLinearFilter;    // world may mipmap
      src.map.anisotropy = 4;
      src.map.colorSpace = THREE.SRGBColorSpace;
    }
    if (name === 'window') {
      m = new THREE.MeshLambertMaterial({ ...common, color: 0x6a7890, emissive: new THREE.Color(0x000000) });
      slots.windows.push(m);
    } else if (name === 'lamp') {
      m = new THREE.MeshLambertMaterial({ ...common, color: 0xffffff, emissive: new THREE.Color(0x000000) });
      slots.lamps.push(m);
    } else {
      m = new THREE.MeshLambertMaterial({ ...common, map: src.map || null, alphaTest: src.alphaTest || 0, transparent: false });
    }
    m.name = name;
    o.material = m;
    o.castShadow = true;
    o.receiveShadow = true;
  });
  return root;
}

export async function buildTrees(scene, base, treesMeta, placements, rnd) {
  const out = [];
  const texCache = {};
  const tex = (f) => texCache[f] ||= new Promise((res) => texLoader.load(base + f, (t) => {
    t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.generateMipmaps = false;
    t.colorSpace = THREE.SRGBColorSpace; res(t);
  }));
  for (const pl of placements) {
    const def = treesMeta.trees[pl.tree];
    if (!def) { console.warn('no tree', pl.tree); continue; }
    const g = new THREE.Group();
    g.position.set(pl.pos[0], pl.pos[1], pl.pos[2]);
    const s = pl.scale || 1;
    g.scale.setScalar(s);
    if (def.trunk) {
      const trunk = litify(await loadGLB(base + def.trunk), { windows: [], lamps: [] });
      g.add(trunk);
    }
    if (def.lowpoly && pl.lowpoly) {
      const lp = litify(await loadGLB(base + def.lowpoly), { windows: [], lamps: [] });
      g.add(lp);
    } else {
      for (const c of def.cards) {
        const t = await tex(c.image);
        const m = new THREE.MeshLambertMaterial({ map: t, alphaTest: 0.5, side: THREE.DoubleSide });
        const geo = new THREE.PlaneGeometry(c.w, c.h);
        geo.translate(0, c.h / 2, 0);
        const mesh = new THREE.Mesh(geo, m);
        mesh.position.set(c.offset[0], c.offset[1], c.offset[2]);
        // lean the card back so it faces the locked 3/4 camera a little more
        mesh.rotation.x = -THREE.MathUtils.degToRad(c.tilt ?? def.tilt ?? 0) * 0.6;
        mesh.castShadow = true; mesh.receiveShadow = true;
        mesh.userData.sway = { amp: 0.012 + rnd() * 0.01, ph: rnd() * 6.28, sp: 0.8 + rnd() * 0.5 };
        g.add(mesh);
      }
    }
    scene.add(g);
    out.push(g);
  }
  return out;
}

export function swayTrees(trees, t) {
  for (const g of trees) for (const c of g.children) {
    const s = c.userData.sway;
    if (s) c.rotation.z = Math.sin(t * s.sp + s.ph) * s.amp;
  }
}
