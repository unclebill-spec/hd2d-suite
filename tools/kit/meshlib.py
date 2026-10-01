"""Mesh kit for hd2d (extends n64-suite's mesh.py, vendored at vendor/n64_mesh.py).

Changes from n64: list-backed (fast for thousands of tris), UVs stored in METRES and divided by the
material's tile size at export, flat NORMALs exported, LIT materials (no KHR_materials_unlit,
metallic 0, roughness 1), samplers use NEAREST magnification + trilinear mipmaps (world may mip),
vertex colours converted sRGB -> linear, optional alphaMode MASK for card textures, emissive factors.
"""
from __future__ import annotations

import json
import math
import struct

import numpy as np


def hex2rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def srgb_to_lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


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
    """Triangle soup. pos/col/uv are arrays (N*3 rows), mat = one name per triangle."""

    def __init__(self):
        self._p, self._c, self._u, self.mat = [], [], [], []
        self._arr = None

    # --- building
    def tri(self, a, b, c, col="#ffffff", uvs=((0, 0), (1, 0), (0, 1)), mat="paint"):
        cols = col if (isinstance(col, (list, tuple)) and len(col) == 3 and not isinstance(col[0], (int, float))) else (col, col, col)
        self._p.extend([a, b, c])
        self._c.extend([_col(x) for x in cols])
        self._u.extend(uvs)
        self.mat.append(mat)
        self._arr = None
        return self

    def quad(self, a, b, c, d, col="#ffffff", uvs=((0, 0), (1, 0), (1, 1), (0, 1)), mat="paint"):
        cols = col if (isinstance(col, (list, tuple)) and len(col) == 4 and not isinstance(col[0], (int, float))) else (col,) * 4
        self.tri(a, b, c, (cols[0], cols[1], cols[2]), (uvs[0], uvs[1], uvs[2]), mat)
        self.tri(a, c, d, (cols[0], cols[2], cols[3]), (uvs[0], uvs[2], uvs[3]), mat)
        return self

    def add(self, other: "Mesh"):
        p, c, u = other.arrays()
        self._p.extend(list(p)); self._c.extend(list(c)); self._u.extend(list(u))
        self.mat += list(other.mat)
        self._arr = None
        return self

    def arrays(self):
        if self._arr is None:
            self._arr = (np.array(self._p, float).reshape(-1, 3), np.array(self._c, float).reshape(-1, 3),
                         np.array(self._u, float).reshape(-1, 2))
        return self._arr

    @property
    def pos(self):
        return self.arrays()[0]

    @property
    def tris(self):
        return len(self.mat)

    def _from(self, p, c, u, mat):
        m = Mesh()
        m._p, m._c, m._u, m.mat = list(p), list(c), list(u), list(mat)
        return m

    def xf(self, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        p, c, u = self.arrays()
        s = np.array(scale if hasattr(scale, "__len__") else (scale,) * 3, float)
        p2 = (p * s) @ rot_matrix(*rot).T + np.array(pos, float)
        return self._from(p2, c, u, self.mat)

    def tint(self, f):
        p, c, u = self.arrays()
        return self._from(p, np.clip(c * np.asarray(f, float), 0, 1), u, self.mat)

    def retex(self, mat):
        p, c, u = self.arrays()
        return self._from(p, c, u, [mat] * len(self.mat))

    def bounds(self):
        p = self.pos
        return p.min(0), p.max(0)

    def normals(self):
        p = self.pos.reshape(-1, 3, 3)
        n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        ln[ln == 0] = 1
        return n / ln

    def ao(self, y0=0.0, height=1.0, amount=0.28):
        """Darken vertex colours near the ground (contact AO): miniature read."""
        p, c, u = self.arrays()
        f = 1 - amount * (1 - np.clip((p[:, 1] - y0) / height, 0, 1))
        return self._from(p, c * f[:, None], u, self.mat)


def fix_winding(m: Mesh, center=None) -> Mesh:
    p, c, u = m.arrays()
    p = p.copy(); c = c.copy(); u = u.copy()
    P = p.reshape(-1, 3, 3)
    cen = P.mean(axis=(0, 1)) if center is None else np.array(center, float)
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    out = P.mean(1) - cen
    flip = (n * out).sum(1) < 0
    for t in np.where(flip)[0]:
        for arr in (p, c, u):
            arr[t * 3 + 1], arr[t * 3 + 2] = arr[t * 3 + 2].copy(), arr[t * 3 + 1].copy()
    return m._from(p, c, u, m.mat)


# ------------------------------------------------------------------ primitives (UVs in metres)
def box(w=1, h=1, d=1, col="#ffffff", mat="paint", y0=None, mats=None, cols=None, uvoff=(0, 0)):
    """Axis box centred on xz; base at y0 (or centred). mats/cols: per face (+x -x +y -y +z -z)."""
    x, z = w / 2, d / 2
    lo = -h / 2 if y0 is None else y0
    hi = lo + h
    m = Mesh()
    fm = mats or [mat] * 6
    fc = cols or [col] * 6
    ox, oy = uvoff

    def us(a0, a1, b0, b1):
        return ((a0 + ox, b0 + oy), (a1 + ox, b0 + oy), (a1 + ox, b1 + oy), (a0 + ox, b1 + oy))
    m.quad((x, lo, z), (x, lo, -z), (x, hi, -z), (x, hi, z), fc[0], us(-z, z, lo, hi), fm[0])
    m.quad((-x, lo, -z), (-x, lo, z), (-x, hi, z), (-x, hi, -z), fc[1], us(-z, z, lo, hi), fm[1])
    m.quad((-x, hi, z), (x, hi, z), (x, hi, -z), (-x, hi, -z), fc[2], us(-x, x, -z, z), fm[2])
    m.quad((-x, lo, -z), (x, lo, -z), (x, lo, z), (-x, lo, z), fc[3], us(-x, x, -z, z), fm[3])
    m.quad((-x, lo, z), (x, lo, z), (x, hi, z), (-x, hi, z), fc[4], us(-x, x, lo, hi), fm[4])
    m.quad((x, lo, -z), (-x, lo, -z), (-x, hi, -z), (x, hi, -z), fc[5], us(-x, x, lo, hi), fm[5])
    return fix_winding(m, (0, (lo + hi) / 2, 0))


def cylinder(r0=0.5, r1=0.5, h=1, seg=8, col="#ffffff", mat="paint", caps=True, y0=0.0, cap_mat=None, col_top=None):
    m = Mesh()
    ct = col_top or col
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        p0 = (r0 * math.cos(a0), y0, r0 * math.sin(a0))
        p1 = (r0 * math.cos(a1), y0, r0 * math.sin(a1))
        q0 = (r1 * math.cos(a0), y0 + h, r1 * math.sin(a0))
        q1 = (r1 * math.cos(a1), y0 + h, r1 * math.sin(a1))
        u0, u1 = a0 * max(r0, r1), a1 * max(r0, r1)
        if r1 <= 1e-6:
            m.tri(p1, p0, q0, (col, col, ct), ((u1, y0), (u0, y0), ((u0 + u1) / 2, y0 + h)), mat)
        else:
            m.quad(p1, p0, q0, q1, (col, col, ct, ct), ((u1, y0), (u0, y0), (u0, y0 + h), (u1, y0 + h)), mat)
        if caps:
            cm = cap_mat or mat
            m.tri((0, y0, 0), p0, p1, col, ((0, 0), (p0[0], p0[2]), (p1[0], p1[2])), cm)
            if r1 > 1e-6:
                m.tri((0, y0 + h, 0), q1, q0, ct, ((0, 0), (q1[0], q1[2]), (q0[0], q0[2])), cm)
    return fix_winding(m, (0, y0 + h * (0.25 if r1 <= 1e-6 else 0.5), 0))


def sphere(r=0.5, seg=7, rings=5, col="#ffffff", mat="paint", squash=(1, 1, 1), noise=0.0, rnd=None, col_bottom=None):
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
            grid[("p", j, i)] = (r * k * math.sin(th) * math.cos(ph) * squash[0], r * k * math.cos(th) * squash[1],
                                 r * k * math.sin(th) * math.sin(ph) * squash[2])
    for j in range(rings):
        for i in range(seg):
            a, b = grid[("p", j, i)], grid[("p", j, i + 1)]
            c, d = grid[("p", j + 1, i + 1)], grid[("p", j + 1, i)]
            ca = _col(col) * (1 - j / rings) + _col(cb) * (j / rings)
            cc = _col(col) * (1 - (j + 1) / rings) + _col(cb) * ((j + 1) / rings)
            uv = ((a[0], a[1]), (b[0], b[1]), (c[0], c[1]), (d[0], d[1]))
            if j == 0:
                m.tri(a, c, d, (ca, cc, cc), (uv[0], uv[2], uv[3]), mat)
            elif j == rings - 1:
                m.tri(a, b, d, (ca, ca, cc), (uv[0], uv[1], uv[3]), mat)
            else:
                m.quad(a, b, c, d, (ca, ca, cc, cc), uv, mat)
    return fix_winding(m, (0, 0, 0))


def beam(p0, p1, t=0.16, col="#ffffff", mat="timber", depth=None):
    """Square beam from p0 to p1 (any direction)."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    if L < 1e-9:
        return Mesh()
    b = box(t, L, depth or t, col, mat, y0=0)
    d /= L
    th = math.acos(max(-1.0, min(1.0, d[1])))
    ph = math.atan2(d[0], d[2])
    return b.xf(tuple(p0), rot=(th, ph, 0))


def prism_x(w, profile, col="#ffffff", mat="paint", side_mat=None):
    """Extrude a 2D (z, y) polygon along x (width w, centred). Used for gables and stairs."""
    m = Mesh()
    x0, x1 = -w / 2, w / 2
    n = len(profile)
    cz = sum(p[0] for p in profile) / n
    cy = sum(p[1] for p in profile) / n
    sm = side_mat or mat
    for i in range(1, n - 1):
        a, b, c = profile[0], profile[i], profile[i + 1]
        m.tri((x1, a[1], a[0]), (x1, b[1], b[0]), (x1, c[1], c[0]), col, ((a[0], a[1]), (b[0], b[1]), (c[0], c[1])), sm)
        m.tri((x0, a[1], a[0]), (x0, c[1], c[0]), (x0, b[1], b[0]), col, ((a[0], a[1]), (c[0], c[1]), (b[0], b[1])), sm)
    for i in range(n):
        a, b = profile[i], profile[(i + 1) % n]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        m.quad((x0, a[1], a[0]), (x1, a[1], a[0]), (x1, b[1], b[0]), (x0, b[1], b[0]), col,
               ((x0, 0), (x1, 0), (x1, L), (x0, L)), mat)
    return fix_winding(m, (0, cy, cz))


# ------------------------------------------------------------------ export
def export_glb(m: Mesh, path, textures: dict, tile_m: dict, name="model", emissive: dict | None = None,
               mask: set | None = None, double: set | None = None):
    """Binary glTF 2.0, one primitive per material: POSITION, NORMAL, COLOR_0 (linear), TEXCOORD_0."""
    emissive = emissive or {}
    mask = mask or set()
    double = double or set()
    p_all, c_all, u_all = m.arrays()
    n_all = np.repeat(m.normals(), 3, axis=0)
    bin_chunks, views, accessors = [], [], []

    def add_view(data: bytes, target=None):
        off = sum(len(b) for b in bin_chunks)
        bin_chunks.append(data + b"\x00" * ((-len(data)) % 4))
        v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target:
            v["target"] = target
        views.append(v)
        return len(views) - 1

    def add_acc(arr, typ, ctype=5126, target=34962, minmax=False):
        vi = add_view(arr.tobytes(), target)
        a = {"bufferView": vi, "componentType": ctype, "count": int(arr.shape[0]), "type": typ}
        if minmax:
            a["min"] = arr.min(0).tolist()
            a["max"] = arr.max(0).tolist()
        accessors.append(a)
        return len(accessors) - 1

    mats = sorted(set(m.mat))
    images, gl_tex, materials, prims = [], [], [], []
    img_index = {}
    for mi, mat in enumerate(mats):
        md = {"name": mat, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0, "roughnessFactor": 1}}
        if mat in emissive:
            md["emissiveFactor"] = list(emissive[mat])
        if mat in mask:
            md["alphaMode"] = "MASK"
            md["alphaCutoff"] = 0.5
        if mat in double:
            md["doubleSided"] = True
        tex = textures.get(mat)
        if tex:
            if tex not in img_index:
                with open(tex, "rb") as f:
                    iv = add_view(f.read())
                images.append({"bufferView": iv, "mimeType": "image/png", "name": mat})
                gl_tex.append({"sampler": 1 if mat in mask else 0, "source": len(images) - 1})
                img_index[tex] = len(gl_tex) - 1
            md["pbrMetallicRoughness"]["baseColorTexture"] = {"index": img_index[tex]}
        materials.append(md)
        sel = np.array([t for t, x in enumerate(m.mat) if x == mat])
        vidx = (sel[:, None] * 3 + np.arange(3)).ravel()
        pos = p_all[vidx].astype(np.float32)
        nrm = n_all[vidx].astype(np.float32)
        col = np.hstack([srgb_to_lin(c_all[vidx]), np.ones((len(vidx), 1))]).astype(np.float32)
        uv = u_all[vidx].copy() / float(tile_m.get(mat, 1.0))
        uv[:, 1] = -uv[:, 1]  # v down in glTF; texture top = up in the world
        uv = uv.astype(np.float32)
        ind = np.arange(len(vidx), dtype=np.uint16 if len(vidx) < 65535 else np.uint32)
        prims.append({"attributes": {"POSITION": add_acc(pos, "VEC3", minmax=True), "NORMAL": add_acc(nrm, "VEC3"),
                                     "COLOR_0": add_acc(col, "VEC4"), "TEXCOORD_0": add_acc(uv, "VEC2")},
                      "indices": add_acc(ind, "SCALAR", 5123 if ind.dtype == np.uint16 else 5125, 34963),
                      "material": mi})
    gltf = {"asset": {"version": "2.0", "generator": "hd2d-suite kit (from n64-suite mesh)"},
            "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": name}],
            "meshes": [{"name": name, "primitives": prims}], "materials": materials,
            "buffers": [{"byteLength": sum(len(b) for b in bin_chunks)}], "bufferViews": views, "accessors": accessors}
    if images:
        gltf.update({"images": images, "textures": gl_tex,
                     "samplers": [{"magFilter": 9728, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497},
                                  {"magFilter": 9728, "minFilter": 9728, "wrapS": 33071, "wrapT": 33071}]})
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((-len(js)) % 4)
    binb = b"".join(bin_chunks)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binb)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(binb), 0x004E4942) + binb)
    return path
