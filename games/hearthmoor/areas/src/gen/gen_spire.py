"""[NIFLHEIM] Writes areas/src/frozenspire.json (F1-F5), frozenspire2.json (F6-F10) and frozen_rift.json (The Crown of Ice), the way caldera / caldera2 are built:
one long north-running corridor per area, 15.6 m wide, one 1.2 m ledge + stair per room (real height; the pack's frost_ledge / frost_stair are not placed, the spec owns the terrain).
Kit pieces, floors, walls, lamps and fx come from tools/hearthmoor/nifl_art.py (spire_layout); runtime rooms / bosses are in game/niflheim.js.
The generated JSON is the source of truth after hand edits: re-running overwrites them."""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parents[1]
src = Path(__file__).with_name("gen_niflheim.py").read_text().split("# ---- niflheim: Mistmere")[0]
ns = {"__file__": __file__}; exec(compile(src, "nf_base", "exec"), ns)
base, GRADES, WALL, H = ns["base"], ns["GRADES"], ns["WALL"], ns["H"]
DUNGEON_GRADES = {   # darker caves; the cold fire + warm lanterns carry the night (check_scene: night < day, dusk bluer than day)
    "day": {**GRADES["day"], "exposure": 0.9, "sun_intensity": 0.9, "hemi_intensity": 0.75},
    "dusk": dict(GRADES["dusk"]), "night": dict(GRADES["night"])}
Z_N = -64.0
snow = lambda pos, area: {"preset": "snowfall", "pos": pos, "area": area, "min_gate": 0.0}


def room_terrace(tag, cx, zl, x0, x1):
    """a ledge pad x0..x1 (6.2 m), depth 2.1 centred on z zl; its stair is centred at cx, top at the pad's front edge"""
    front = zl + 1.05
    return ({"name": f"plat_{tag}", "rect": [x0, zl - 1.05, x1, front], "h": H, "top": "plaster", "gaps": [[cx - 1.2, cx + 1.2]]},
            {"name": f"stair_{tag}", "x": cx, "z_top": front, "width": 2.2, "rise": H, "base": 0.0})


def corridor(seed, name, about, rooms, game, emitters, zc_list):
    terr, stairs = [], []
    for tag, zc, cx, x0, x1, zl in rooms:
        t, s = room_terrace(tag, cx, zc + zl, x0, x1); terr.append(t); stairs.append(s)
    d = base(seed, name, about, [-8.0, Z_N - 0.8, 8.0, 12.4], [-6.6, Z_N + 2.0, 6.6, 12.0],
             terr + [WALL("wall_w", [-30, Z_N - 26, -8.2, 13]), WALL("wall_e", [8.2, Z_N - 26, 30, 13]), WALL("wall_n", [-30, Z_N - 26, 30, Z_N - 0.2])],
             stairs, [], [], {"role": "traveler", "pos": [0.0, 8.4], "facing": "up"}, game, emitters, size=(80, 150))
    for w in d["terraces"]:
        if w["name"].startswith("wall"): w["h"] = 5.0
    d["grades"] = DUNGEON_GRADES
    return d


# (tag, room z centre, stair x, pad x0, pad x1, pad z within the room)
R1 = [("f1", 0.0, -4.4, -7.5, -1.3, -3.6), ("f2", -14.0, 4.4, 1.3, 7.5, -4.4), ("f3", -28.0, -4.4, -7.5, -1.3, -3.6), ("f4", -42.0, -4.4, -7.5, -1.3, -3.6), ("f5", -56.0, -4.4, -7.5, -1.3, -3.6)]
R2 = [("f6", 0.0, -4.4, -7.5, -1.3, -3.6), ("f7", -14.0, -4.4, -7.5, -1.3, 0.0), ("f8", -28.0, -4.6, -7.7, -1.5, 3.0), ("f9", -42.0, -4.4, -7.5, -1.3, -3.6), ("f10", -56.0, -4.4, -7.5, -1.3, -1.0)]
emb = lambda pos, area: {"preset": "snowfall", "pos": pos, "area": area, "min_gate": 0.0}

fs1 = corridor(
    421, "The Frozen Spire", "Niflheim's dungeon, rooms F1-F5 (story 7): the Spire Gate, the Banner Hall, the Glow Pool Gallery, the Mirror Stairs and the Glacier Heart. Rime-glass halls, rune locks, cold-fire braziers.",
    R1,
    {"id": "frozenspire", "title": "The Frozen Spire",
     "exits": [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "iceglow", "spawn": "mouth", "label": "back out to the Glowpool Caverns"},
               {"rect": [-1.5, Z_N + 0.5, 1.5, Z_N + 1.4], "to": "frozenspire2", "spawn": "from_spire", "label": "the Frozen Spire, higher"}], "portals": [],
     "spawns": {"start": [0.0, 8.4, "up"], "from_caves": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "f1": [0.0, 5.0, "up"], "f2": [0.0, -9.0, "up"], "f3": [0.0, -23.0, "up"], "f4": [0.0, -37.0, "up"],
                "f5": [0.0, -51.0, "up"], "from_spire2": [0.0, -61.0, "down"], "from_mouth": [0.0, 8.4, "up"], "from_mouth_key": [0.0, 8.4, "up"]},
     "spring": {"pos": [4.6, -32.4], "r": 1.8, "secret": "fs_spring"}},
    [snow([0, 3.0, 2.0], [14, 3.0, 12])], None)
fs2 = corridor(
    422, "The Frozen Spire: the Aerie", "Niflheim's dungeon, rooms F6-F10 (story 7): the Sister's Glass, the Aurora Archive, the Rime Bridge, Kael's Aerie and the Crown Stair up to the Rift.",
    R2,
    {"id": "frozenspire2", "title": "The Frozen Spire: the Aerie",
     "exits": [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "frozenspire", "spawn": "from_spire2", "label": "back down to the Glacier Heart"}], "portals": [],
     "spawns": {"start": [0.0, 8.4, "up"], "from_spire": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "f6": [0.0, 5.0, "up"], "f7": [0.0, -9.0, "up"], "f8": [0.0, -23.0, "up"], "f9": [0.0, -37.0, "up"],
                "f10": [0.0, -51.0, "up"], "door": [0.0, -59.0, "up"], "from_rift": [0.0, -59.0, "down"], "from_waystone": [2.6, -11.4, "down"]},
     "waystone": {"pos": [4.8, -13.8]}},
    [snow([0, 3.0, 2.0], [14, 3.0, 12])], None)
fs2["actors"].append({"id": "archivist", "role": "elffolk", "name": "Vigdis Stillwater", "pos": [-1.0, -17.2], "facing": "down", "behavior": "idle", "talkable": True, "say": ["The tablets are older than the Spire. The Spire is older than the quarrel."]})
for n, d in (("frozenspire", fs1), ("frozenspire2", fs2)):
    (OUT / f"{n}.json").write_text(json.dumps(d, indent=1) + "\n"); print("wrote", n)

# ---- frozen_rift: the Crown of Ice. Start on the ground (z 14), stair up to the 1.2 m landing (z 9..12 band), a second stair up to the 1.8 m round platform (10.4 x 10.4 at the origin).
HP = 1.8
rift = base(
    423, "The Crown of Ice", "Veyra's finale arena: a round ice platform above the void, the broken Rainbow Rift's colours frozen into the air, aurora overhead, four frozen portals at the edges.",
    [-6.6, -7.0, 6.6, 15.6], [-6.0, -6.0, 6.0, 14.4],
    [{"name": "landing", "rect": [-3.1, 6.4, 3.1, 10.0], "h": H, "top": "plaster", "gaps": [[-1.1, 1.1]]},
     {"name": "crown", "rect": [-5.2, -5.2, 5.2, 5.2], "h": HP, "top": "plaster", "gaps": [[-1.1, 1.1]]},
     WALL("wall_w", [-30, -30, -7.0, 18]), WALL("wall_e", [7.0, -30, 30, 18]), WALL("wall_n", [-30, -30, 30, -7.2])],
    [{"name": "stair_land", "x": 0.0, "z_top": 10.0, "width": 2.2, "rise": H, "base": 0.0}, {"name": "stair_crown", "x": 0.0, "z_top": 5.2, "width": 2.2, "rise": HP - H, "base": H}],
    [], [], {"role": "traveler", "pos": [0.0, 14.0], "facing": "up"},
    {"id": "frozen_rift", "title": "The Crown of Ice", "exits": [], "portals": [],
     "spawns": {"start": [0.0, 14.0, "up"], "from_spire": [0.0, 14.0, "up"], "qa": [0.0, 8.0, "up"], "landing": [0.0, 8.2, "up"], "arena": [0.0, 3.6, "up"]}},
    [snow([0, 3.0, 4.0], [12, 3.0, 14])], size=(60, 80))
for w in rift["terraces"]:
    if w["name"].startswith("wall"): w["h"] = 6.0
rift["grades"] = DUNGEON_GRADES
(OUT / "frozen_rift.json").write_text(json.dumps(rift, indent=1) + "\n"); print("wrote frozen_rift")
