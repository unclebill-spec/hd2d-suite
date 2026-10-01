"""Tiny low-poly mesh kit: primitives, vertex-color baking, OBJ/GLB export, software preview."""
from __future__ import annotations

import io
import json
import math
import struct

import numpy as np
from PIL import Image

from .core import hex2rgb


def _col(c):
    if isinstance(c, str):
        return np.array(hex2rgb(c), float) / 255.0
    return np.array(c, float)


def rot_matrix(rx=0.0, ry=0.0, rz=0.0):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Y @ X @ Z


class Mesh:
    """Non-indexed triangle soup: every triangle owns 3 vertices (flat, crunchy, N64-like)."""

    def __init__(self):
        self.pos = np.zeros((0, 3))
        self.col = np.zeros((0, 3))
        self.uv = np.zeros((0, 2))
        self.mat: list[str] = []  # one material name per triangle

    @property
    def tris(self) -> int:
        return len(self.pos) // 3

    def tri(self, a, b, c, col, uvs=((0, 0), (1, 0), (0, 1)), mat="white"):
        cols = col if isinstance(col, (list, tuple)) and len(col) == 3 and not isinstance(col[0], (int, float)) else (col, col, col)
        self.pos = np.vstack([self.pos, np.array([a, b, c], float)])
        self.col = np.vstack([self.col, np.array([_col(x) for x in cols])])
        self.uv = np.vstack([self.uv, np.array(uvs, float)])
        self.mat.append(mat)
        return self

    def quad(self, a, b, c, d, col, uvs=((0, 0), (1, 0), (1, 1), (0, 1)), mat="white"):
        cols = col if isinstance(col, (list, tuple)) and len(col) == 4 and not isinstance(col[0], (int, float)) else (col,) * 4
        self.tri(a, b, c, (cols[0], cols[1], cols[2]), (uvs[0], uvs[1], uvs[2]), mat)
        self.tri(a, c, d, (cols[0], cols[2], cols[3]), (uvs[0], uvs[2], uvs[3]), mat)
        return self

    def add(self, other: "Mesh"):
        self.pos = np.vstack([self.pos, other.pos])
        self.col = np.vstack([self.col, other.col])
        self.uv = np.vstack([self.uv, other.uv])
        self.mat += list(other.mat)
        return self

    def copy(self) -> "Mesh":
        m = Mesh()
        m.pos, m.col, m.uv, m.mat = self.pos.copy(), self.col.copy(), self.uv.copy(), list(self.mat)
        return m

    def xf(self, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)) -> "Mesh":
        m = self.copy()
        s = np.array(scale if hasattr(scale, "__len__") else (scale,) * 3, float)
        m.pos = (m.pos * s) @ rot_matrix(*rot).T + np.array(pos, float)
        return m

    def tint(self, f) -> "Mesh":
        m = self.copy()
        m.col = np.clip(m.col * f, 0, 1)
        return m

    def bounds(self):
        return self.pos.min(0), self.pos.max(0)

    def normals(self):
        p = self.pos.reshape(-1, 3, 3)
        n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        ln[ln == 0] = 1
        return n / ln

    def bake_light(self, light=(0.4, 0.8, 0.45), ambient=0.55, ao=0.25):
        """Bake directional light + height AO into vertex colors (N64 games did this offline)."""
        L = np.array(light, float)
        L /= np.linalg.norm(L)
        n = self.normals()
        lam = np.clip(n @ L, 0, 1)
        f = ambient + (1 - ambient) * lam
        f = np.repeat(f, 3)[:, None]
        lo, hi = self.bounds()
        h = max(hi[1] - lo[1], 1e-6)
        aof = (1 - ao) + ao * np.clip((self.pos[:, 1] - lo[1]) / h * 1.6, 0, 1)
        self.col = np.clip(self.col * f * aof[:, None], 0, 1)
        return self

    def ground(self):
        """Shift so the lowest point sits at y=0 and center on xz."""
        lo, hi = self.bounds()
        self.pos -= np.array([(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2])
        return self


# ---------------------------------------------------------------- primitives

def box(w=1, h=1, d=1, col="#ffffff", mat="white", uvscale=1.0, cols=None, y0=None):
    """Axis box centered on origin (or base at y0). cols: optional 6 face colors (+x -x +y -y +z -z)."""
    x, z = w / 2, d / 2
    lo = -h / 2 if y0 is None else y0
    hi = lo + h
    m = Mesh()
    fc = cols or [col] * 6
    us = lambda a, b: ((0, 0), (a * uvscale, 0), (a * uvscale, b * uvscale), (0, b * uvscale))
    m.quad((x, lo, z), (x, lo, -z), (x, hi, -z), (x, hi, z), fc[0], us(d, h), mat)
    m.quad((-x, lo, -z), (-x, lo, z), (-x, hi, z), (-x, hi, -z), fc[1], us(d, h), mat)
    m.quad((-x, hi, z), (x, hi, z), (x, hi, -z), (-x, hi, -z), fc[2], us(w, d), mat)
    m.quad((-x, lo, -z), (x, lo, -z), (x, lo, z), (-x, lo, z), fc[3], us(w, d), mat)
    m.quad((-x, lo, z), (x, lo, z), (x, hi, z), (-x, hi, z), fc[4], us(w, h), mat)
    m.quad((x, lo, -z), (-x, lo, -z), (-x, hi, -z), (x, hi, -z), fc[5], us(w, h), mat)
    return fix_winding(m, (0, (lo + hi) / 2, 0))


def cylinder(r0=0.5, r1=0.5, h=1, seg=6, col="#ffffff", col_top=None, mat="white", caps=True, uvscale=1.0, y0=0.0):
    """Tapered cylinder / cone (r1=0) with base at y0."""
    m = Mesh()
    ct = col_top or col
    circ = 2 * math.pi * max(r0, r1)
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        p0 = (r0 * math.cos(a0), y0, r0 * math.sin(a0))
        p1 = (r0 * math.cos(a1), y0, r0 * math.sin(a1))
        q0 = (r1 * math.cos(a0), y0 + h, r1 * math.sin(a0))
        q1 = (r1 * math.cos(a1), y0 + h, r1 * math.sin(a1))
        u0, u1 = i / seg * circ * uvscale, (i + 1) / seg * circ * uvscale
        v = h * uvscale
        if r1 <= 1e-6:
            m.tri(p1, p0, q0, (col, col, ct), ((u1, 0), (u0, 0), ((u0 + u1) / 2, v)), mat)
        else:
            m.quad(p1, p0, q0, q1, (col, col, ct, ct), ((u1, 0), (u0, 0), (u0, v), (u1, v)), mat)
        if caps:
            m.tri((0, y0, 0), p0, p1, col, ((0.5, 0.5), (0.5 + 0.5 * math.cos(a0), 0.5 + 0.5 * math.sin(a0)), (0.5 + 0.5 * math.cos(a1), 0.5 + 0.5 * math.sin(a1))), mat)
            if r1 > 1e-6:
                m.tri((0, y0 + h, 0), q1, q0, ct, ((0.5, 0.5), (0.5 + 0.5 * math.cos(a1), 0.5 + 0.5 * math.sin(a1)), (0.5 + 0.5 * math.cos(a0), 0.5 + 0.5 * math.sin(a0))), mat)
    return fix_winding(m, (0, y0 + h * (0.25 if r1 <= 1e-6 else 0.5), 0))


def sphere(r=0.5, seg=6, rings=4, col="#ffffff", col_bottom=None, mat="white", squash=(1, 1, 1), noise=None, rnd=None):
    """Low-poly UV sphere centered on origin. Optional per-vertex noise for rocks/foliage."""
    m = Mesh()
    cb = col_bottom or col
    grid = {}
    for j in range(rings + 1):
        for i in range(seg + 1):
            th = math.pi * j / rings
            ph = 2 * math.pi * (i % seg) / seg
            k = 1.0
            if noise and rnd is not None and 0 < j < rings:
                key = (j, i % seg)
                if key not in grid:
                    grid[key] = 1 + rnd.uniform(-noise, noise)
                k = grid[key]
            grid[("p", j, i)] = (r * k * math.sin(th) * math.cos(ph) * squash[0], r * k * math.cos(th) * squash[1], r * k * math.sin(th) * math.sin(ph) * squash[2])
    for j in range(rings):
        for i in range(seg):
            a, b = grid[("p", j, i)], grid[("p", j, i + 1)]
            c, d = grid[("p", j + 1, i + 1)], grid[("p", j + 1, i)]
            ca = _col(col) * (1 - j / rings) + _col(cb) * (j / rings)
            cc = _col(col) * (1 - (j + 1) / rings) + _col(cb) * ((j + 1) / rings)
            uv = ((i / seg, 1 - j / rings), ((i + 1) / seg, 1 - j / rings), ((i + 1) / seg, 1 - (j + 1) / rings), (i / seg, 1 - (j + 1) / rings))
            if j == 0:
                m.tri(a, c, d, (ca, cc, cc), (uv[0], uv[2], uv[3]), mat)
            elif j == rings - 1:
                m.tri(a, b, d, (ca, ca, cc), (uv[0], uv[1], uv[3]), mat)
            else:
                m.quad(a, b, c, d, (ca, ca, cc, cc), uv, mat)
    return fix_winding(m, (0, 0, 0))


def prism(poly2d, depth=0.1, col="#ffffff", mat="white", col_side=None):
    """Extrude a convex-ish 2D polygon (x,y) along z. Used for blades, leaves, stars."""
    m = Mesh()
    z = depth / 2
    cs = col_side or col
    n = len(poly2d)
    cx = sum(p[0] for p in poly2d) / n
    cy = sum(p[1] for p in poly2d) / n
    for i in range(n):
        a, b = poly2d[i], poly2d[(i + 1) % n]
        m.tri((cx, cy, z), (a[0], a[1], z), (b[0], b[1], z), col, ((0.5, 0.5), (a[0] + 0.5, a[1]), (b[0] + 0.5, b[1])), mat)
        m.tri((cx, cy, -z), (b[0], b[1], -z), (a[0], a[1], -z), col, ((0.5, 0.5), (b[0] + 0.5, b[1]), (a[0] + 0.5, a[1])), mat)
        m.quad((a[0], a[1], -z), (b[0], b[1], -z), (b[0], b[1], z), (a[0], a[1], z), cs, mat=mat)
    return fix_winding(m, (cx, cy, 0))


def fix_winding(m: Mesh, center=None) -> Mesh:
    """Flip triangles whose normal points toward the mesh center (cheap outward fix for convex parts)."""
    p = m.pos.reshape(-1, 3, 3)
    c = p.mean(axis=(0, 1)) if center is None else np.array(center)
    n = m.normals()
    out = (p.mean(1) - c)
    flip = (n * out).sum(1) < 0
    if flip.any():
        idx = np.where(flip)[0]
        for t in idx:
            for arr in (m.pos, m.col, m.uv):
                arr[t * 3 + 1], arr[t * 3 + 2] = arr[t * 3 + 2].copy(), arr[t * 3 + 1].copy()
    return m


# ---------------------------------------------------------------- export

def export_obj(m: Mesh, path_obj: str, textures: dict[str, str]):
    """OBJ with per-vertex colors (v x y z r g b) and an MTL that references texture PNGs."""
    import os
    base = os.path.splitext(os.path.basename(path_obj))[0]
    mtl_path = os.path.splitext(path_obj)[0] + ".mtl"
    lines = [f"# n64-suite low-poly model, {m.tris} tris", f"mtllib {base}.mtl"]
    for p, c in zip(m.pos, m.col):
        lines.append("v %.4f %.4f %.4f %.3f %.3f %.3f" % (p[0], p[1], p[2], c[0], c[1], c[2]))
    for uv in m.uv:
        lines.append("vt %.4f %.4f" % (uv[0], uv[1]))
    cur = None
    for t, mat in enumerate(m.mat):
        if mat != cur:
            lines.append(f"usemtl {mat}")
            cur = mat
        i = t * 3 + 1
        lines.append(f"f {i}/{i} {i+1}/{i+1} {i+2}/{i+2}")
    with open(path_obj, "w") as f:
        f.write("\n".join(lines) + "\n")
    ml = []
    for mat in sorted(set(m.mat)):
        ml += [f"newmtl {mat}", "Kd 1 1 1", "illum 0"]
        if mat in textures:
            ml.append(f"map_Kd {os.path.basename(textures[mat])}")
    with open(mtl_path, "w") as f:
        f.write("\n".join(ml) + "\n")
    return [path_obj, mtl_path]


def export_glb(m: Mesh, path: str, textures: dict[str, str], name="model"):
    """Binary glTF 2.0: one primitive per material, COLOR_0 + TEXCOORD_0, unlit, bilinear sampler."""
    bin_chunks = []
    views, accessors = [], []

    def add_view(data: bytes, target=None):
        off = sum(len(b) for b in bin_chunks)
        pad = (-len(data)) % 4
        bin_chunks.append(data + b"\x00" * pad)
        v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target:
            v["target"] = target
        views.append(v)
        return len(views) - 1

    def add_acc(arr: np.ndarray, typ: str, ctype=5126, target=34962, minmax=False):
        vi = add_view(arr.tobytes(), target)
        a = {"bufferView": vi, "componentType": ctype, "count": int(arr.shape[0]), "type": typ}
        if minmax:
            a["min"] = arr.min(0).tolist()
            a["max"] = arr.max(0).tolist()
        accessors.append(a)
        return len(accessors) - 1

    mats = sorted(set(m.mat))
    images, gl_textures, materials, prims = [], [], [], []
    for mi, mat in enumerate(mats):
        mat_def = {"name": mat, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0, "roughnessFactor": 1},
                   "extensions": {"KHR_materials_unlit": {}}}
        if mat in textures:
            with open(textures[mat], "rb") as f:
                png = f.read()
            iv = add_view(png)
            images.append({"bufferView": iv, "mimeType": "image/png", "name": mat})
            gl_textures.append({"sampler": 0, "source": len(images) - 1})
            mat_def["pbrMetallicRoughness"]["baseColorTexture"] = {"index": len(gl_textures) - 1}
        materials.append(mat_def)
        sel = np.array([t for t, x in enumerate(m.mat) if x == mat])
        vidx = (sel[:, None] * 3 + np.arange(3)).ravel()
        pos = m.pos[vidx].astype(np.float32)
        col = np.hstack([m.col[vidx], np.ones((len(vidx), 1))]).astype(np.float32)
        uv = m.uv[vidx].copy().astype(np.float32)
        uv[:, 1] = 1 - uv[:, 1]
        ind = np.arange(len(vidx), dtype=np.uint16 if len(vidx) < 65535 else np.uint32)
        prims.append({
            "attributes": {"POSITION": add_acc(pos, "VEC3", minmax=True), "COLOR_0": add_acc(col, "VEC4"), "TEXCOORD_0": add_acc(uv, "VEC2")},
            "indices": add_acc(ind, "SCALAR", 5123 if ind.dtype == np.uint16 else 5125, 34963),
            "material": mi,
        })
    gltf = {
        "asset": {"version": "2.0", "generator": "n64-suite"},
        "extensionsUsed": ["KHR_materials_unlit"],
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": name}],
        "meshes": [{"name": name, "primitives": prims}],
        "materials": materials,
        "buffers": [{"byteLength": sum(len(b) for b in bin_chunks)}],
        "bufferViews": views, "accessors": accessors,
    }
    if images:
        gltf.update({"images": images, "textures": gl_textures,
                     "samplers": [{"magFilter": 9729, "minFilter": 9729, "wrapS": 10497, "wrapT": 10497}]})
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((-len(js)) % 4)
    binb = b"".join(bin_chunks)
    total = 12 + 8 + len(js) + 8 + len(binb)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(binb), 0x004E4942) + binb)
    return path


# ---------------------------------------------------------------- software preview renderer

def _sample(tex: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Bilinear, wrapping texture fetch (the N64 'blurry' look). tex: HxWx3 float."""
    h, w = tex.shape[:2]
    x = (u * w - 0.5) % w
    y = ((1 - v) * h - 0.5) % h
    x0 = np.floor(x).astype(int) % w
    y0 = np.floor(y).astype(int) % h
    fx, fy = (x - np.floor(x))[:, None], (y - np.floor(y))[:, None]
    x1, y1 = (x0 + 1) % w, (y0 + 1) % h
    a = tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx
    b = tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx
    return a * (1 - fy) + b * fy


def render(m: Mesh, textures: dict[str, str] | None = None, size=160, yaw=0.6, pitch=0.35,
           bg=(0.16, 0.18, 0.28), fog=None, dist_mul=2.6) -> Image.Image:
    textures = textures or {}
    texarr = {k: np.asarray(Image.open(p).convert("RGB"), float) / 255.0 for k, p in textures.items()}
    lo, hi = m.bounds()
    center = (lo + hi) / 2
    radius = max(np.linalg.norm(hi - lo) / 2, 1e-3)
    R = rot_matrix(pitch, 0, 0) @ rot_matrix(0, yaw, 0)  # spin about Y first, then tilt camera
    p = (m.pos - center) @ R.T
    dist = radius * dist_mul
    z = dist - p[:, 2]
    f = size / (2 * math.tan(math.radians(20)))
    sx = size / 2 + p[:, 0] * f / z
    sy = size / 2 - p[:, 1] * f / z
    img = np.zeros((size, size, 3))
    img[:] = bg
    zbuf = np.full((size, size), np.inf)
    ys = np.arange(size)[:, None]
    xs = np.arange(size)[None, :]
    for t in range(m.tris):
        i = t * 3
        x0, x1, x2 = sx[i:i + 3]
        y0, y1, y2 = sy[i:i + 3]
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-9:
            continue
        minx, maxx = int(max(0, math.floor(min(x0, x1, x2)))), int(min(size - 1, math.ceil(max(x0, x1, x2))))
        miny, maxy = int(max(0, math.floor(min(y0, y1, y2)))), int(min(size - 1, math.ceil(max(y0, y1, y2))))
        if minx > maxx or miny > maxy:
            continue
        X = xs[:, minx:maxx + 1] + 0.5
        Y = ys[miny:maxy + 1, :] + 0.5
        w0 = ((x1 - X) * (y2 - Y) - (x2 - X) * (y1 - Y)) / area
        w1 = ((x2 - X) * (y0 - Y) - (x0 - X) * (y2 - Y)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        zz = w0 * z[i] + w1 * z[i + 1] + w2 * z[i + 2]
        sub = zbuf[miny:maxy + 1, minx:maxx + 1]
        ok = inside & (zz < sub)
        if not ok.any():
            continue
        sub[ok] = zz[ok]
        # perspective-correct interpolation
        iz = np.stack([w0[ok] / z[i], w1[ok] / z[i + 1], w2[ok] / z[i + 2]], 1)
        iz /= iz.sum(1, keepdims=True)
        col = iz @ m.col[i:i + 3]
        tex = texarr.get(m.mat[t])
        if tex is not None:
            uv = iz @ m.uv[i:i + 3]
            col = col * _sample(tex, uv[:, 0], uv[:, 1])
        if fog is not None:
            fz = np.clip((zz[ok] - dist * 0.8) / (radius * 1.6), 0, 1)[:, None] * 0.6
            col = col * (1 - fz) + np.array(fog) * fz
        region = img[miny:maxy + 1, minx:maxx + 1]
        region[ok] = col
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return out


def turntable(m: Mesh, textures=None, views=8, size=128, scale=2, label=None) -> Image.Image:
    cols = 4
    rows = math.ceil(views / cols)
    sheet = Image.new("RGB", (cols * size, rows * size))
    for k in range(views):
        im = render(m, textures, size=size, yaw=2 * math.pi * k / views + 0.4)
        sheet.paste(im, ((k % cols) * size, (k // cols) * size))
    sheet = sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST)
    if label:
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet)
        d.rectangle([0, 0, len(label) * 6 + 8, 14], fill=(0, 0, 0))
        d.text((4, 2), label, fill=(255, 255, 140))
    return sheet


def png_bytes(im: Image.Image) -> bytes:
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def segment(p0, p1, r0=0.05, r1=None, seg=5, col="#ffffff", col_top=None, mat="white", caps=True):
    """Cylinder from point p0 to point p1 (limbs, branches, bow arcs)."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    if L < 1e-9:
        return Mesh()
    d /= L
    th = math.acos(max(-1.0, min(1.0, d[1])))
    ph = math.atan2(d[0], d[2])
    c = cylinder(r0, r0 if r1 is None else r1, L, seg, col, col_top, mat, caps)
    return c.xf(tuple(p0), rot=(th, ph, 0))
