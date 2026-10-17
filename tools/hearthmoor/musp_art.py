"""[MUSPELHEIM] Art installer for the Muspelheim areas (realm-muspelheim branch). Modeled on jot_art.py / svart_art.py / alf_art.py.

Wires the staging art in games/hearthmoor/art/muspelheim/ (copied from /workspace/hearthmoor-staging/art/muspelheim/) into the BUILT Muspelheim
areas without re-assembling:
  sprites  ember-kin / fire-giant NPC sheets, enemy sheets, the boss / mini-boss / rare sheets and Kindle become extra sheets of each area's actors.json
  kit      staging .glb files are copied in; a name clash takes the staging piece
  gamefx   staging mu_fx rows are appended under the area's gamefx atlas (48 px cells), plus the plaza's quest_mark / quest_turnin glyphs
Props: PLACE puts staging kit pieces into scene.json (objects + lamps + collision blockers). Only adds or overwrites files: it never deletes anything
(only its own earlier placements, marked "musp_art", are re-made). The area's original gamefx atlas is kept once as gamefx.base.(png|json) and every
run rebuilds from that. Idempotent.
LAMP_CAP: the warm decor lamps (lava channels, braziers, forge windows) are dimmed in reach so they do not tint the few-colour ember-kin sprites standing near
them (check_scene colours); the lights stay, only their reach shrinks. Add a piece to LAMP_CAP when check_scene's colour check names it.
NEON: scoped allow-lists only. This script NEVER edits tools/check-sprite/check_sprite.py and never widens any list. `neon_audit()` runs on every sheet before it is
installed: off-palette (neon) colours are allowed only for the roles and hexes in MUSP_NEON_SCOPE (mirrors MUSP_NEON_ALLOW in check_sprite.py; filled from the art README's
"Neon flag" + a ruling, expected: Kindle only). A role outside the scope that carries off-palette colours is NOT installed (its palette-safe `_safe` twin is installed instead
when the pack ships one; otherwise the sheet is skipped with a message).

STATUS: WIRED to the real pack (art README, Oct 17 2026). The sheet / role / kit names below are the pack's. Missing staging files are SKIPPED with a message, never an error.
Not in the pack (stand-ins / later): item icons, the Emberfang prop, Orm's mount lizard, Vharzul cast frames, Caldera rooms C1-C8 scenes, a Hall of Wardens interior, Kindle's fx rows
(pets/kindle_fx is copied to art/muspelheim/ but no area atlas carries it yet, like Flurry's). Dagny: the pack has her as the 2.5x NPC role `cindercaptain` (idle / walk only).
Decisions on the README's four questions (Cozy Builder's spirit, Oct 17): (1) Dagny 2.5x (the roster, and the pack); (2) ember-kin stay on the 40x44 frame at 1x; (3) Vharzul 144x256 with
folded wings is fine; (4) the Red arch keeps its warm cream pane (the hub stays warm).

usage: python3 tools/hearthmoor/musp_art.py [--force] [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
STAGING = Path("/workspace/hearthmoor-staging/art/muspelheim")
ST = GAME / "art" / "muspelheim"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
PLANNED = ["muspelheim", "mp_hall", "lavafalls", "caldera", "caldera2"]   # story 2.1; the Caldera is two areas (like clockdeep / barrow), see MUSPELHEIM_PROGRESS.md
AREAS = ARGS or PLANNED

# stock actor role (what the area spec's actors use) -> the pack's role, per area (re-pointed only if the area's actors.json has that stock role)
TOWNS = {
    "muspelheim": {"dwarftrader": "mp_trader", "wispcatcher": "lizardman", "lanternseller": "mp_guide"},
    "mp_hall": {"shopkeeper": "envoy_mp", "innkeeper": "warden_mp"},
    "lavafalls": {"nightmerchant": "forgejudge", "poolkeeper": "springkeeper"},
    "caldera": {}, "caldera2": {},
}
FOLK = ["envoy_mp", "springkeeper", "lizardman", "mp_trader", "mp_guide"]   # mp_folk (40x44, 1x ember-kin)
GIANTS = ["warden_mp", "forgejudge", "cindercaptain"]                        # mp_giants (64x100, 2.5-2.6x)
FOES = ["ashen_cultist", "magma_hound", "flame_elemental", "fire_golem"]     # mp_enemies (56x68)
SHEETS = {  # sheet name -> (staging json, {area role: staging role}); every area gets the folk / giant / foe sheets (their own role names are added too)
    "mpfolk": (ST / "sprite" / "mp_folk.json", {r: r for r in FOLK}),
    "mpgiant": (ST / "sprite" / "mp_giants.json", {r: r for r in GIANTS}),
    "mpenemy": (ST / "sprite" / "mp_enemies.json", {r: r for r in FOES}),
    "kindle": (ST / "pets" / "kindle.json", {"pet_kindle": "pet_kindle"}),   # the companion: kindle_neon.png is her main look (scoped allow-list, see NEON above)
    "kindle_safe": (ST / "pets" / "kindle.json", {"pet_kindle_safe": "pet_kindle"}),   # palette-safe fallback twin (its own role, not placed)
}
IMAGE = {"kindle": "kindle_neon.png", "kindle_safe": "kindle.png"}   # sheet -> staging png when it is not the json's own image
EXTRA = {    # sheets only where the fight / scene is (their own frame size)
    "muspelheim": {"mpelite": (ST / "sprite" / "mp_elites.json", {"magma_hound_gate": "magma_hound_gate"})},   # the Armed Crossing's 2x hound
    "lavafalls": {"mpelite": (ST / "sprite" / "mp_elites.json", {"ashalpha": "ashalpha", "pyreling": "pyreling"})},   # the two rares
    "caldera2": {"boss_vharzul": (ST / "sprite" / "boss_vharzul.json", {"vharzul": "vharzul", "vharzul_p3": "vharzul_p3"}),   # 8x, black-iron plate, crown of fire
                 "mpelite": (ST / "sprite" / "mp_elites.json", {"kilnmother": "kilnmother"})},
}
# Scoped neon (art README "Neon flag", lead ruling): Kindle only, her three neon-red hexes. Mirrors MUSP_NEON_ALLOW in check_sprite.py, never wider.
MUSP_NEON_SCOPE = {"pet_kindle": {"#a81c22", "#e0302a", "#ff5a4a"}}
FX_SKIP = {"heat_shimmer"}   # check_scene gamefx_sharp: its crop never matches the atlas frame (a near-transparent distortion strip); the pack keeps it, the area atlases do not list it (the row stays unused)
FX_FILE = ("gamefx", "mp_fx.json")   # staging gamefx rows: ST / "gamefx" / "mp_fx.json"


def neon_audit(src, sm, img_name, roles):
    """off-palette colours per staging role of a sheet -> {role: set(hex)}; only roles in `roles` (staging names) are looked at"""
    sys.path.insert(0, str(GAME.parents[1]))
    from hd2d_common import load_biome  # noqa: E402
    pal = set(load_biome(sm.get("biome", "cozy-village"))["colors"].values())
    im = Image.open(src.parent / img_name).convert("RGBA"); px = im.load(); fw, fh = sm["frame"]; bad = {}
    for sr in roles:
        r = sm["roles"].get(sr)
        if not r: continue
        got = set()
        for fr in r.get("frames", []):
            for y in range(fh):
                for x in range(fw):
                    p = px[fr["x"] + x, fr["y"] + y]
                    if p[3] == 255:
                        h = "#%02x%02x%02x" % p[:3]
                        if h not in pal: got.add(h)
        if got - MUSP_NEON_SCOPE.get(sr, set()): bad[sr] = got - MUSP_NEON_SCOPE.get(sr, set())
    return bad

def have(p):
    if not Path(p).exists():
        print(f"  skip (not in the pack yet): {Path(p).relative_to(GAME) if str(p).startswith(str(GAME)) else p}")
        return False
    return True


def copy_staging():
    """Copy the staging pack into art/muspelheim/ (add / overwrite only)."""
    if not STAGING.exists():
        return False
    ST.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STAGING, ST, dirs_exist_ok=True)
    return True


def sprites(area):
    d = GAME / "areas" / area / "public" / "art" / "sprite"
    mp = d / "actors.json"; m = json.loads(mp.read_text()); m.setdefault("sheets", {})
    for nm, (src, roles) in {**SHEETS, **EXTRA.get(area, {})}.items():
        if not have(src): continue
        sm = json.loads(src.read_text())
        bad = neon_audit(src, sm, IMAGE.get(nm, sm["image"]), set(roles.values()))
        if bad:
            print(f"  {nm}: NOT installed, off-palette colours outside MUSP_NEON_SCOPE: " + "; ".join(f"{r} {sorted(h)[:4]}" for r, h in bad.items()))
            continue
        shutil.copy2(src.parent / IMAGE.get(nm, sm["image"]), d / f"{nm}.png")
        out = {k: sm[k] for k in ("tool", "biome", "frame", "pivot", "ground_row", "facings", "anims", "cols", "size")}
        out["image"] = f"{nm}.png"; out["roles"] = {}
        if nm in ("mpfolk", "mpgiant"):   # stock stand-in roles of this area point at the pack's roles (only roles the area's actors.json has)
            roles = {**roles, **{k: v for k, v in TOWNS.get(area, {}).items() if v in sm["roles"] and k in m["roles"]}}
        for ar, sr in roles.items():
            if sr not in sm["roles"]: print(f"  {nm}: no staging role {sr}"); continue
            r = sm["roles"][sr]
            out["roles"][ar] = {k: v for k, v in r.items() if k != "frames"}
            prev = m["roles"].get(ar, {})
            m["roles"][ar] = {"sheet": nm, "row": r["row"], "kind": r.get("kind", prev.get("kind", "creature")),
                              "anims": r.get("anims", ["idle", "walk"]), "desc": r.get("desc", ""),
                              **({"enemy": True} if r.get("enemy") or prev.get("enemy") else {}),
                              **({"pet": True, "follower": True} if nm == "kindle" else {})}
        (d / f"{nm}.json").write_text(json.dumps(out, indent=1))
        m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
    mp.write_text(json.dumps(m, indent=1))


def kit(area):
    d = GAME / "areas" / area / "public" / "art" / "kit"
    for g in sorted((ST / "kit").glob("*.glb")):
        shutil.copy2(g, d / g.name)


def gamefx(area):
    if not have(ST / "gamefx" / "mp_fx.json"): return False
    d = GAME / "areas" / area / "public" / "art" / "gamefx"
    if not (d / "gamefx.json").exists() and not (d / "gamefx.base.json").exists():
        # no atlas yet (wispwood): start from an empty base so the staging rows are the whole atlas, and point the scene at it
        d.mkdir(parents=True, exist_ok=True)
        sj = json.loads((ST / "gamefx" / "mp_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((ST / "gamefx" / "mp_fx.json").read_text())
    assert base["cell"] == sj["cell"], "cell size mismatch"
    bi, si = Image.open(bp).convert("RGBA"), Image.open(ST / "gamefx" / sj["image"]).convert("RGBA")
    # the ! / ? quest-marker glyphs (quest_mark, quest_turnin) copied from the plaza atlas (same 48 px cell): the realm areas' atlases had none,
    # so the Muspelheim NPC markers (Aska, Torka, Svala...) spawned nothing
    pm = json.loads((GAME / "areas/plaza/public/art/gamefx/gamefx.json").read_text()); pim = Image.open(GAME / "areas/plaza/public/art/gamefx/gamefx.png").convert("RGBA")
    c = base["cell"]; assert pm["cell"] == c
    mk = [("quest_mark", pm["effects"]["quest_mark"]), ("quest_turnin", pm["effects"]["quest_turnin"])]
    strip = Image.new("RGBA", (pim.width, c * len(mk)), (0, 0, 0, 0))
    for i, (_, e) in enumerate(mk):
        strip.paste(pim.crop((0, e["row"] * c, pim.width, (e["row"] + 1) * c)), (0, i * c))
    im = Image.new("RGBA", (max(bi.width, si.width, strip.width), bi.height + si.height + strip.height), (0, 0, 0, 0))
    im.paste(bi, (0, 0)); im.paste(si, (0, bi.height)); im.paste(strip, (0, bi.height + si.height)); im.save(d / "gamefx.png")
    off = bi.height // base["cell"]
    for i, (k, e) in enumerate(mk):
        base["effects"][k] = {**{kk: vv for kk, vv in e.items() if kk != "frame_list"}, "row": off + si.height // c + i}
    for k, e in sj["effects"].items():
        if k in FX_SKIP: continue
        e = {kk: vv for kk, vv in e.items() if kk not in ("frame_list", "strip")}
        e["row"] = e["row"] + off
        base["effects"][k] = e
    base["size"] = [im.width, im.height]
    (d / "gamefx.json").write_text(json.dumps(base, indent=1))
    return True


# props placed per area: (piece, preferred [x, z], "fixed"?); the spot is searched outward on flat, walkable, uncrowded ground unless "fixed".
# Coordinates are the art README's Stonehollow layout (metadata/muspelheim.json), moved where the area spec's own terrain (plateau + stair come
# from the spec, so the kit's stone_ledge / stone_stair are not placed) or an actor stands. Keep-clear: nothing on the stair + 1 m, 2.5 m in
# front of longhouse doors, 1.5 m around the from_bifrost spawn.

NOBLOCK = {"amber_orb_chain", "hanging_crystals", "warden_stones", "glass_bridge", "dance_ring", "basalt_floor", "forge_floor", "glass_terrace", "basalt_stair"}   # kit.json blockers [] (walkable / hanging): no blocker
WALK = {"warden_stones", "glass_bridge", "dance_ring", "basalt_floor", "forge_floor"}   # flat, walkable, never cast shadows
# The real props come from the art README's layout (metadata/muspelheim_layout.json), area spec <- layout area. The spec owns the terrain (its terrace + stair, 1.34 m, replace the kit's
# basalt_ledge / basalt_stair / glass_terrace, like Jotunheim's plateau), so those three are not placed; floor tiles are laid only on flat ground (not over a terrace or stair).
LAYOUT_AREA = {"muspelheim": "cinderhold", "mp_hall": "sigil_forge", "lavafalls": "lavafalls"}   # caldera / caldera2: later (only the throne room has a layout: caldera_throne)
SPEC_TERRAIN = {"basalt_ledge", "basalt_stair", "glass_terrace"}
NO_TILE = {"muspelheim": (-3.4, -9.8, 3.4, -1.6), "mp_hall": (2.8, -7.6, 6.4, 0.6), "lavafalls": (-9.2, -1.2, -5.6, 4.8)}   # terrace + stair footprints (+ a margin): no floor tiles over them
EXTRA_PLACE = {}   # area -> [(piece, [x, z], "fixed", {rot, y})] added after the layout (hand-placed extras)
# ---- the Ember Caldera (no layout in the pack except the throne render): hand-placed from the kit's own notes (keep_clear, blockers, hanging heights). x, z, optional quarter turn.
Q = 1.5707963267948966
CALDERA = {
    "caldera": [   # C1 Mouth (ember-lamps down to the stair, lava sunk along both walls), C2 Ashen Stair, C3 Glass Bridge (lava either side), C4 Furnace Hall (furnace in the west alcove, exit north stays open)
        ("brazier_stand", -3.4, 7.0), ("brazier_stand", 3.4, 7.0), ("warm_lantern", -5.4, 2.0), ("warm_lantern", 5.4, 2.0), ("warm_lantern", -2.8, -2.0), ("warm_lantern", 2.8, -2.0),
        ("lava_channel", -9.0, 6.0), ("lava_channel", -9.0, 2.0), ("lava_channel", 9.0, 6.0), ("lava_channel", 9.0, 2.0), ("obsidian_pillar", -7.6, -1.6), ("obsidian_pillar", 7.6, -1.6),
        ("brazier_stand", -4.6, -6.6), ("brazier_stand", 4.6, -6.6), ("warm_lantern", -3.0, -10.0), ("warm_lantern", 3.0, -10.0), ("obsidian_pillar", -8.0, -9.6), ("obsidian_pillar", 8.0, -12.6),
        ("cinder_cairn", -9.6, -13.6), ("lava_channel", -9.4, -7.0), ("lava_channel", 9.4, -7.0),
        ("glass_bridge", 0.0, -18.4), ("glass_bridge", 0.0, -22.4), ("glass_bridge", 0.0, -26.4),
        ("lava_channel", -3.7, -18.4), ("lava_channel", -3.7, -22.4), ("lava_channel", -3.7, -26.4), ("lava_channel", 3.7, -18.4), ("lava_channel", 3.7, -22.4), ("lava_channel", 3.7, -26.4),
        ("lava_pool", -7.6, -22.4), ("lava_pool", 7.6, -22.4), ("cold_brazier", -2.4, -29.6), ("warm_lantern", 2.4, -29.6),
        ("furnace", -6.4, -37.4), ("brazier_stand", 5.6, -33.6), ("brazier_stand", -8.6, -32.4), ("warm_lantern", 4.0, -40.6), ("obsidian_pillar", 8.6, -38.0), ("cinder_cairn", 8.0, -42.0),
    ],
    "caldera2": [   # C5 Cold Seam, C6 Cantor's Chapel, C7 Springs of Glass, C8 Waystone Landing, C9 Ember Throne
        ("cold_seam_wall", -8.0, -2.4), ("cold_seam_wall", -6.0, -2.4), ("cold_seam_wall", -4.0, -2.4), ("cold_seam_wall", 4.0, -2.4), ("cold_seam_wall", 6.0, -2.4), ("cold_seam_wall", 8.0, -2.4),
        ("cold_brazier", -2.8, 3.0), ("cold_brazier", 2.8, 3.0), ("hanging_crystals", -5.0, 0.0, 0, 3.0), ("hanging_crystals", 5.0, 0.0, 0, 3.0), ("warm_lantern", -6.2, 7.0), ("warm_lantern", 6.2, 7.0),
        ("brazier_stand", -5.6, -6.6), ("brazier_stand", 5.6, -6.6), ("shrine_lamp", -3.6, -13.4), ("shrine_lamp", 3.6, -13.4), ("wardens_seat", 0.0, -15.2), ("obsidian_pillar", -9.0, -11.0), ("obsidian_pillar", 9.0, -11.0),
        ("warm_lantern", -8.0, -8.0), ("warm_lantern", 8.0, -8.0),
        ("spring_pool", -6.0, -24.0), ("shrine_lamp", -8.8, -22.4), ("shrine_lamp", -3.4, -22.4), ("hanging_crystals", -4.0, -21.0, 0, 3.0), ("hanging_crystals", 5.0, -23.0, 0, 3.0),
        ("cold_brazier", 6.0, -24.6), ("obsidian_pillar", 9.2, -20.6), ("warm_lantern", 3.4, -19.8), ("cinder_cairn", 9.0, -28.6),
        ("muspel_waystone", -3.6, -37.0), ("brazier_stand", -7.2, -32.4), ("brazier_stand", 7.2, -32.4), ("cinder_cairn", 5.0, -36.0), ("cinder_cairn", 7.6, -34.0), ("warm_lantern", 3.0, -32.8),
        ("ember_throne", 0.0, -55.6), ("warden_lamp_stand", 0.0, -45.2), ("warden_lamp_stand", -4.5, -53.0), ("warden_lamp_stand", 4.5, -53.0),   # the pack's throne scene: arena centre (0, -50), Vharzul at (0, -51.8)
        ("lava_channel", -9.4, -54.0), ("lava_channel", -9.4, -50.0), ("lava_channel", -9.4, -46.0), ("lava_channel", 9.4, -54.0), ("lava_channel", 9.4, -50.0), ("lava_channel", 9.4, -46.0),
        ("cold_brazier", -5.4, -43.4), ("cold_brazier", 5.4, -43.4), ("hanging_crystals", -6.0, -52.0, 0, 3.0), ("hanging_crystals", 6.0, -52.0, 0, 3.0), ("hanging_crystals", 0.0, -44.0, 0, 3.0),
    ],
}
TILE_ZONES = {   # flat zones (z range, [x0, x1]) of the caldera areas that get basalt floor tiles; stair strips are skipped
    "caldera": [(11.0, -3.2), (-5.2, -15.0), (-31.2, -43.0)],
    "caldera2": [(11.0, -3.2), (-5.2, -16.0), (-18.4, -41.0), (-43.4, -57.0)],
}
STAIR_Z = {"caldera": [-4.2, -16.4], "caldera2": [-4.2, -17.4, -42.4]}


def caldera_place(area):
    out = []
    for e in CALDERA.get(area, []):
        name, x, z = e[:3]; ex = {}
        if len(e) > 3 and e[3]: ex["rot"] = e[3]
        if len(e) > 4: ex["y"] = e[4]
        out.append((name, [x, z], "fixed", ex))
    sz = STAIR_Z.get(area, [])
    for z0, z1 in TILE_ZONES.get(area, []):
        z = z0
        while z >= z1:
            for xi in range(-11, 12, 2):
                if any(-1.0 <= z - st <= 3.6 and abs(xi) <= 2.5 for st in sz): continue
                if area == "caldera" and -30.2 < z < -16.4 and abs(xi) > 2.8: continue   # lava either side of the bridge
                if area == "caldera" and -30.2 < z < -16.4: continue                       # the glass bridge is its own piece
                out.append(("basalt_floor", [float(xi), z], "fixed", {}))
            z -= 2.0
    return out


def layout_place(area):
    la = LAYOUT_AREA.get(area)
    lp = ST / "metadata" / "muspelheim_layout.json"
    if not la or not lp.exists(): return caldera_place(area) + EXTRA_PLACE.get(area, [])
    out = []
    nt = NO_TILE.get(area)
    for p in json.loads(lp.read_text())[la]["pieces"]:
        name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
        if name in SPEC_TERRAIN: continue
        if name in ("basalt_floor", "forge_floor") and nt and nt[0] <= x <= nt[2] and nt[1] <= z <= nt[3]: continue
        ex = {}
        if rot: ex["rot"] = rot
        if name in ("amber_orb_chain", "hanging_crystals"): ex["y"] = y   # hanging pieces keep the layout height
        out.append((name, [x, z], "fixed", ex))
    return out + EXTRA_PLACE.get(area, []) + caldera_place(area)


# Decor lamps (lava, forge windows, braziers, glass orbs) are dimmed in reach so they do not tint the few-colour ember-kin sprites standing near them (check_scene colours:
# crop colours / source colours <= 2). The lights stay; only their reach shrinks. Tune from check_scene's colour check (add a piece when it names it).
LAMP_CAP = {"basalt_house": 3.0, "forge_hall": 3.5, "lava_channel": 3.0, "lava_pool": 3.0, "red_arch": 3.2, "spice_stall": 3.0, "brazier_stand": 2.8, "cold_brazier": 2.4,
            "shrine_lamp": 2.6, "glass_bridge": 3.0, "lizard_stable": 3.0, "emberfall_anvil": 2.4, "obsidian_pillar": 2.5, "amber_orb_chain": 2.4, "spring_pool": 3.0,
            "muspel_waystone": 3.5, "cinder_cairn": 2.0, "warm_lantern": 2.6, "forge_wall": 3.0, "wardens_seat": 3.0, "warden_stones": 3.5, "lava_fall_cliff": 4.0,
            "caldera_mouth_arch": 4.0, "furnace": 4.0, "ember_throne": 5.0, "warden_lamp_stand": 3.5, "hanging_crystals": 4.0, "cold_seam_wall": 3.5, "seal_cast_bed": 3.0, "stamp_press": 2.6, "ledger_desk": 2.4, "sigil_mould_wall": 3.0}
LAMP_CAP_AREA = {a: dict(LAMP_CAP) for a in PLANNED}
# per-area tightening where a tall giant stands near decor lamps (check_scene colours: crop colours / source colours <= 2): Aska by the seat lamps, Torka by her anvils and the fall pools
LAMP_CAP_AREA["mp_hall"].update({"wardens_seat": 1.4, "shrine_lamp": 1.6, "amber_orb_chain": 1.6})
LAMP_CAP_AREA["lavafalls"].update({"emberfall_anvil": 1.2, "lava_pool": 2.0, "cold_brazier": 2.0})


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("musp_art")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("musp_art")]
    g = sc["game"]
    keep = [(a["pos"][0], a["pos"][1], 1.6) for a in sc.get("actors", []) if "pos" in a]
    keep += [(v[0], v[1], 2.0) for v in g.get("spawns", {}).values()]
    for e in g.get("exits", []) + g.get("portals", []):
        r = e.get("rect")
        if r: keep.append(((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, 2.4 + max(r[2] - r[0], r[3] - r[1]) / 2))
    keep += [(o["pos"][0], o["pos"][2], 1.4) for o in sc["objects"] if not o.get("walkable") and "scene_" not in o["glb"]]
    cam = sc["camera"].get("bounds")
    # phone-portrait view box around the start spawn (about +-6 m wide, 14 m deep at the default zoom): props go where
    # the arrival view shows them. The vault keeps its own room-by-room preferences (no box).
    st = g.get("spawns", {}).get("start")
    vbox = None if not st else (st[0] - 6.0, st[1] - 16.0, st[0] + 6.0, st[1] + 1.0)
    # never hide a character: no tall prop in a band in front of (camera side, +z) an actor or spawn
    front = [(a["pos"][0], a["pos"][1]) for a in sc.get("actors", []) if "pos" in a] + [(v[0], v[1]) for v in g.get("spawns", {}).values()]

    def cells(x, z, hw, hd):
        for j in range(int((z - hd - oz) / cl), int((z + hd - oz) / cl) + 1):
            for i in range(int((x - hw - ox) / cl), int((x + hw - ox) / cl) + 1):
                yield i, j

    nonlocal_tall = [False]

    def ok(x, z, hw, hd):
        if vbox and not (vbox[0] < x < vbox[2] and vbox[1] < z < vbox[3]):
            return None
        if nonlocal_tall[0] and any(abs(x - fx_) < hw + 0.8 and 0 < z - fz < 2.0 for fx_, fz in front):
            return None
        if cam and not (cam[0] + 1 < x < cam[2] - 1 and cam[1] + 1 < z < cam[3] - 1):
            return None
        hs = []
        for i, j in cells(x, z, hw + 0.5, hd + 0.5):
            if not (0 <= i < W and 0 <= j < H) or d[j * W + i] == -32768: return None
            hs.append(d[j * W + i])
        if max(hs) - min(hs) > 6: return None
        if any(math.hypot(x - kx, z - kz) < kr + max(hw, hd) for kx, kz, kr in keep): return None
        return hs[len(hs) // 2] / 100

    for name, (px, pz), *fixed in layout_place(area):
        extra = next((f for f in fixed if isinstance(f, dict)), {}); fixed = [f for f in fixed if not isinstance(f, dict)]
        if name not in pieces: print(f"  {area}: no kit piece {name} yet"); continue
        pc = pieces[name]; hw, hd = pc["size"][0] / 2, pc["size"][2] / 2
        rot = extra.get("rot", 0)
        if abs(abs(rot) - math.pi / 2) < 0.1: hw, hd = hd, hw   # a quarter turn swaps the footprint
        nonlocal_tall[0] = pc["size"][1] > 1.2
        spot = None
        if fixed:   # hand-placed against the side walls (the vault corridor is too narrow for the search)
            i_, j_ = int((px - ox) / cl), int((pz - oz) / cl)
            gy = max(0, d[j_ * W + i_]) / 100 if (0 <= i_ < W and 0 <= j_ < H) else 0.0   # pieces on the wall line may sit off the collision grid
            spot = (px, extra["y"] if "y" in extra else gy, pz)
        for r in ([] if spot else [0] + [x * 0.5 for x in range(1, 30)]):
            for k in range(max(1, int(r * 8))):
                a = 2 * math.pi * k / max(1, int(r * 8)); x, z = round(px + r * math.cos(a), 2), round(pz + r * math.sin(a), 2)
                y = ok(x, z, hw, hd)
                if y is not None: spot = (x, y, z); break
            if spot: break
        if not spot: print(f"  {area}: no spot for {name}"); continue
        x, y, z = spot
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": rot, "musp_art": True}
        if name in WALK: o.update(walkable=True, cast=False)
        if extra.get("pz"): o["pz"] = extra["pz"]
        if extra.get("hidden"): o["hidden"] = True
        sc["objects"].append(o)
        keep.append((x, z, max(hw, hd) + 0.6))
        if name not in WALK and name not in NOBLOCK:
            for i, j in cells(x, z, hw * 0.8, hd * 0.8):
                if 0 <= i < W and 0 <= j < H: d[j * W + i] = -32768   # off-grid cells (the wall line) are already solid
        mk = pc["markers"]
        for lp in ([] if extra.get("hidden") else mk.get("lamps", [])):   # a hidden piece (cairn_toppled) is lit at runtime when the game shows it
            sc["lamps"].append({"pos": [x + lp[0], y + lp[1], z + lp[2]], "range": min(mk.get("lamp_range", 5.0), LAMP_CAP_AREA[area].get(name, 9.0)) if area in LAMP_CAP_AREA else mk.get("lamp_range", 5.0), "kind": name,
                                "color": mk.get("lamp_color", "#a45cf0"), "fixed": mk.get("lamp_fixed", 0.5), "musp_art": True})
        print(f"  {area}: {name} at ({x}, {z})")
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))





def main():
    if not (STAGING / "READY.txt").exists() and not FORCE:
        print("musp_art: /workspace/hearthmoor-staging/art/muspelheim/READY.txt is missing: the art pack is not ready. Nothing done (use --force for a dry look).")
        return 0
    copy_staging()
    for a in AREAS:
        d = GAME / "areas" / a
        if not (d / "scene.json").exists():
            print(f"{a}: not built yet (areas/{a}/scene.json missing): skipped"); continue
        sprites(a)
        if (ST / "kit" / "kit.json").exists(): kit(a); place(a)
        fx = gamefx(a)
        print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
