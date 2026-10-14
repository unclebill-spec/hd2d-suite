"""Stage 6.4: writes areas/src/rotwood.json (the Rotwood Hollow, 8 rooms R0-R7) and verdant.json (the Verdant Heart,
6 rooms V0-V5) from the Verdant Heart art pack's placement recipe (art/verdant_heart/README.md). Rooms run west->east
as a chain of 9 m root caverns split by cave walls with a 3 m gap. Re-run after editing: python3 gen_vh_dungeons.py"""
import json, copy
from pathlib import Path
SRC = Path(__file__).resolve().parents[1]
RW = 9.0   # room width (m)

def room_x(i, n): return -(n * RW) / 2 + RW * (i + 0.5)

def base(name, about, n, seed):
    half = n * RW / 2
    return {"name": name, "seed": seed, "biome": "cozy-village", "about": about,
            "time": {"start": "night", "speed": 0.0}, "spells": True,
            "sprite_roles": ["actors", "heroes", "combat", "sporeling", "mossgolem"], "boss_roles": [],
            "camera": {"fov": 24, "pitch": 38, "distance": 30, "zoom": [22, 40], "look": [0, 0, -1.0],
                       "bounds": [-half + 4.0, -2.0, half - 4.0, 1.5]},
            "ground": {"size": [n * RW + 40, 50], "mat": "moss", "walk": [-half, -5.0, half, 4.6]},
            "slabs": [], "terraces": [], "stairs": [], "decks": [], "buildings": [], "hedges": [], "trees": [],
            "blocks": [[-half - 1, -5.6, half + 1, -5.0], [-half - 1, 4.6, half + 1, 5.2],
                       [-half - 0.7, -5.6, -half, 5.2], [half, -5.6, half + 0.7, 5.2]],
            "props": [], "emitters": [], "actors": [], "fx": [],
            "backdrop": {"hills": [0, -40]},
            "grades": {"day": {"fog_color": "#0c1424", "sky_top": "#04060e", "sky_bottom": "#0e1830", "hemi_sky": "#24345c",
                               "sun_intensity": 0.25, "exposure": 0.95, "saturation": 1.05, "warmth": -0.1, "bugs": 1.0},
                       "night": {"fog_color": "#0a1022", "sky_top": "#03050c", "sky_bottom": "#0c1428", "hemi_sky": "#1c2a52",
                                 "hemi_intensity": 0.42, "exposure": 1.0, "sun_intensity": 0.18, "sun_color": "#6c8ad0", "bugs": 1.0}}}

def P(d, piece, x, z, rot=0): d["props"].append({"piece": piece, "pos": [round(x, 2), round(z, 2)], **({"rot": rot} if rot else {})})
def FX(d, name, x, y, z, i=None): d["fx"].append({**({"id": i} if i else {}), "name": name, "pos": [round(x, 2), y, round(z, 2)]})

def cave(d, n, gloom):
    """back wall + ceiling lip + vines, room-divider walls with a 3 m gap, a glowing stream down the length, fog,
    fireflies, glow frogs, red toadstools and neon mushrooms in every room"""
    half = n * RW / 2
    x = -half + 2
    while x < half:
        P(d, "vh_wall", x, -5.3); P(d, "vh_ceiling_lip", x, -4.6)
        x += 4
    cols = ["blue", "violet", "pink", "green"]
    for i in range(n):
        cx = room_x(i, n)
        if i:   # divider: two wall stubs, gap at z 0.4..3.4 (the path hugs the front)
            wx = cx - RW / 2
            d["blocks"].append([wx - 0.3, -5.0, wx + 0.3, 0.4]); P(d, "glowroot_arch", wx, 1.9, 90)
        P(d, "hanging_vines", cx - 1.6, -4.4); P(d, "stream_straight", cx - 2, -3.2, 90); P(d, "stream_straight", cx, -3.2, 90)
        P(d, "stream_straight", cx + 2, -3.2, 90)
        d["blocks"].append([cx - 3.2, -3.9, cx + 3.2, -2.5])   # the stream (black water, no wading)
        FX(d, "stream_flow", cx, 0.05, -3.2)
        P(d, "toadstool_giant", cx + 3.4, -1.6); d["blocks"].append([cx + 2.9, -2.1, cx + 3.9, -1.1])
        P(d, f"neon_mushrooms_{['blue', 'violet', 'pink'][i % 3]}", cx - 3.4, -1.8)
        P(d, "glowfern_blue" if i % 2 else "glowfern", cx - 2.6, 3.6)
        P(d, "toadstool_shelf", cx + 1.4, -4.6)
        if gloom: P(d, "blight_bloom", cx + 0.6, -2.0)
        FX(d, f"glow_mist_{'violet' if gloom else cols[i % 4]}", cx, 0.4, -2.6)
        FX(d, f"fireflies_{['blue', 'neon', 'violet', 'green', 'pink'][i % 5]}", cx - 1, 1.3, 0.5)
        FX(d, f"glowfrog_{cols[(i + 1) % 4]}_idle", cx - 2.2, 0.0, -2.2)
        FX(d, "toadstool_glow_pool", cx + 3.4, 0.02, -1.6)
        d["emitters"].append({"preset": "fireflies", "pos": [cx, 1.2, 0.0], "area": [6, 1.2, 4], "min_gate": 0.0})

def rotwood():
    n = 8; d = base("Vanaheim: the Rotwood Hollow",
        "Vanaheim's main dungeon (story/verdant_heart.md section 4): eight root caverns under the Old Bough running down to the Regent's Bower. Glowing stream, hanging vines, violet blight fog, glow frogs and red toadstools. Art: the Verdant Heart pack (art/verdant_heart/), blight_bloom + violet mist for the rot.", n, 211)
    cave(d, n, True)
    names = ["Root Gate", "Leaf-Litter Hall", "Toadstool Bridge", "Rune-Sealed Root Door", "Mire Gallery", "Gnome Larder", "The Weeping Root", "The Regent's Bower"]
    R = [room_x(i, n) for i in range(n)]
    P(d, "waterfall", R[6], -4.6); FX(d, "waterfall_sheet", R[6], 1.6, -4.4); FX(d, "waterfall_splash", R[6], 0.1, -3.6)
    P(d, "heart_spring", R[2] + 1.0, 2.6)
    P(d, "heartseed_cradle", R[7], -0.6)
    FX(d, "blight_aura", R[7], 0.03, -0.6, "rw_bower_blight")
    rx = R[3] - RW / 2 + RW   # the root door between R3 and R4
    g = {"id": "rotwood", "title": "The Rotwood Hollow", "rooms": [{"id": f"R{i}", "name": names[i], "x": round(R[i], 2)} for i in range(n)],
         "exits": [{"rect": [-n * RW / 2, 0.6, -n * RW / 2 + 0.8, 3.4], "to": "vanaheim", "spawn": "from_rotwood", "label": "the root-cave up to Mossbrook Springs"}],
         "portals": [], "doors": [],
         "spawns": {"start": [R[0] - 2.4, 2.0, "right"], "from_mossbrook": [R[0] - 2.4, 2.0, "right"], "from_verdant": [R[7] + 2.6, 2.6, "left"], "qa": [R[0], 2.0, "right"]},
         "braziers": [{"id": "rw_cp0", "pos": [round(R[0] + 1.2, 2), 0.6], "checkpoint": True},
                      {"id": "rw_lock_1", "pos": [round(R[3] - 2.4, 2), 0.2]}, {"id": "rw_lock_2", "pos": [round(R[3], 2), -0.6]},
                      {"id": "rw_lock_3", "pos": [round(R[3] + 2.4, 2), 0.2]},
                      {"id": "rw_cp6", "pos": [round(R[6] - 1.6, 2), 0.6], "checkpoint": True}]
                     + [{"id": f"rw_rim_{k}", "pos": [round(R[7] + dx, 2), dz]} for k, (dx, dz) in enumerate([(-3.2, -2.0), (3.2, -2.0), (-3.2, 2.6), (3.2, 2.6)])],
         "rootdoor": {"x": round(rx, 2), "block": [round(rx - 0.4, 2), 0.4, round(rx + 0.4, 2), 4.6], "order": ["rw_lock_2", "rw_lock_1", "rw_lock_3"]},
         "spring": {"pos": [round(R[2] + 1.0, 2), 2.6], "secret": "rw_spring"},
         "cages": [{"id": f"rw_cage_{k}", "pos": [round(R[5] - 2 + 2 * k, 2), -1.4]} for k in range(3)],
         "riddle": {"pos": [round(R[5] + 3.0, 2), 1.8]},
         "taproot": {"pos": [round(R[6] + 1.6, 2), -2.0]},
         "bower": {"pos": [round(R[7], 2), 0.0], "r": 4.2, "enter_x": round(R[7] - RW / 2 + 1.0, 2)},
         "sapling": {"pos": [round(R[7] + 1.0, 2), -1.6], "rect": [round(R[7] + 0.3, 2), -2.4, round(R[7] + 1.7, 2), -1.0], "to": "verdant", "spawn": "from_rotwood", "label": "the sapling's root-stair down to the Verdant Heart"},
         "art": {"_note": "Verdant Heart pack (art/verdant_heart/): rottreant / sporeelemental + boss sheets ride in their own sheets, verdant_fx + critters are appended to the gamefx atlas by build.py install_verdant_heart."}}
    d["game"] = g; d["player"] = {"role": "traveler", "pos": g["spawns"]["start"][:2], "facing": "right"}
    d["actors"].append({"id": "tobble", "role": "gnome", "name": "Tobble Capwhistle, gnome scout", "pos": [round(R[0] + 0.4, 2), 2.6], "facing": "right", "behavior": "idle", "talkable": True,
                        "say": ["Pocket lantern's lit. Stay close, big-folk, and don't step in anything purple."]})
    return d

def verdant():
    n = 6; d = base("Vanaheim: the Verdant Heart",
        "The optional deeper dungeon under the Regent's grave (story/verdant_heart.md section 5): six living-forest caverns in clean glow, the Moonwell and the Heart Glade where Hjortur the Greenheart waits. Glowing stream into a pool, a waterfall, hanging vines, glow fog, glow frogs and red toadstools.", n, 223)
    cave(d, n, False)
    names = ["Sapling Door", "Grove of Whispers", "Bloom Stair", "Firefly Maze", "Moonwell", "Heart Glade"]
    V = [room_x(i, n) for i in range(n)]
    P(d, "waterfall", V[2], -4.6); FX(d, "waterfall_sheet", V[2], 1.6, -4.4); FX(d, "waterfall_splash", V[2], 0.1, -3.6)
    P(d, "glow_pool", V[4], -0.6); d["blocks"].append([V[4] - 1.5, -2.1, V[4] + 1.5, 0.9]); FX(d, "pool_green", V[4], 0.02, -0.6)
    P(d, "heart_spring", V[3] + 0.6, 2.8)
    P(d, "heartseed_cradle", V[5], -0.6); FX(d, "greenheart_aura", V[5], 0.03, -0.6, "vh_glade_aura")
    for k, col in enumerate(["blue", "violet", "red", "green", "pink"]):
        FX(d, f"glow_orb_{col}", V[k] + 1.2, 1.1, 1.0)
    g = {"id": "verdant", "title": "The Verdant Heart", "rooms": [{"id": f"V{i}", "name": names[i], "x": round(V[i], 2)} for i in range(n)],
         "exits": [{"rect": [-n * RW / 2, 0.6, -n * RW / 2 + 0.8, 3.4], "to": "rotwood", "spawn": "from_verdant", "label": "the root-stair up to the Regent's Bower"}],
         "portals": [], "doors": [],
         "spawns": {"start": [V[0] - 2.4, 2.0, "right"], "from_rotwood": [V[0] - 2.4, 2.0, "right"], "qa": [V[0], 2.0, "right"], "glade": [V[5] - 3.0, 2.4, "right"]},
         "braziers": [{"id": "vh_cp0", "pos": [round(V[0] + 1.2, 2), 0.6], "checkpoint": True}]
                     + [{"id": f"vh_light_{k}", "pos": [round(V[5] + dx, 2), dz]} for k, (dx, dz) in enumerate([(-3.2, -2.0), (3.2, -2.0), (-3.2, 2.6), (3.2, 2.6)])],
         "bowls": [{"id": f"vh_bowl_{k}", "pos": [round(V[2] - 2 + 2 * k, 2), -1.8]} for k in range(3)],
         "spring": {"pos": [round(V[3] + 0.6, 2), 2.8], "secret": "vh_heart_spring"},
         "moonwell": {"pos": [round(V[4], 2), -0.6]},
         "glade": {"pos": [round(V[5], 2), 0.0], "r": 4.2, "enter_x": round(V[5] - RW / 2 + 1.0, 2)},
         "art": {"_note": "Verdant Heart pack (art/verdant_heart/), clean glow set + heartseed_cradle."}}
    d["game"] = g; d["player"] = {"role": "traveler", "pos": g["spawns"]["start"][:2], "facing": "right"}
    for k in range(3):
        d["actors"].append({"id": f"dryad_{k}", "role": "gnome", "name": "A dryad of the Grove", "pos": [round(V[1] - 2 + 2 * k, 2), -1.6], "facing": "down", "behavior": "idle", "talkable": True,
                            "say": [["Root: stand your ground when he charges; the roots hold the brave.", "Bloom: what you plant here, you may stand on.", "Light: four fires, and the Greenheart bows to the one who lights them."][k]]})
    return d

for name, fn in (("rotwood", rotwood), ("verdant", verdant)):
    (SRC / f"{name}.json").write_text(json.dumps(fn(), indent=1)); print("wrote", name)
