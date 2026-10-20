"""[ASGARD] Writes the five Asgard specs (story 2.1): asgard (Goldspire hub), gs_hall (the Thunder Hall), gs_temple (the Dawn Temple), and the Gilded Reliquary as two corridors
like frozenspire / frozenspire2: reliquary (G1-G5) and reliquary2 (G6-G9). Every area / room has a real 1.34 m ledge + stair (the pack's gold_ledge height; the spec owns the
terrain, so tools/hearthmoor/asg_art.py does not place gold_ledge / gold_stair). Kit pieces, floors, walls, lamps and fx come from asg_art.py (the pack's layout).
The generated JSON is the source of truth after hand edits: re-running overwrites them."""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parents[1]
ROLES = ["actors", "heroes", "combat", "lanternseller", "dwarftrader", "poolkeeper", "wispcatcher", "elffolk", "elffolk2", "innkeeper", "shopkeeper", "nightmerchant", "gnome"]
GRADES = {   # Goldspire: violet-blue dusk sky, gold lamp pools, neon-blue runes (lights only); day is the sky plains' full day
    "day": {"fog_color": "#a89cc0", "sky_top": "#3a3070", "sky_bottom": "#c8b0d8", "hemi_sky": "#e8dcf0", "saturation": 0.95, "bugs": 0.0, "warmth": 0.06,
            "exposure": 0.84, "sun_intensity": 1.0, "hemi_intensity": 0.7, "sun_color": "#fff0d0", "lamp_intensity": 0.85},
    "dusk": {"fog_color": "#2e2650", "sky_top": "#2a2350", "sky_bottom": "#5a3e8a", "exposure": 0.95, "sun_intensity": 0.6, "warmth": -0.04, "sun_color": "#a8a0f0", "bugs": 0.5},
    "night": {"fog_color": "#16122c", "sky_top": "#0a0820", "sky_bottom": "#2a2350", "hemi_sky": "#6a5ca8", "bugs": 1.0, "exposure": 1.0, "sun_intensity": 0.4, "hemi_intensity": 0.55, "sun_color": "#9a8ce0"},
}
DUNGEON_GRADES = {"day": {**GRADES["day"], "exposure": 0.9, "sun_intensity": 0.9, "hemi_intensity": 0.75}, "dusk": dict(GRADES["dusk"]), "night": dict(GRADES["night"])}
H = 1.34   # gold_ledge height (7 x 0.191 m)
WALL = lambda n, r, h=3.6: {"name": n, "rect": r, "h": h, "top": "stone", "coping": True}
motes = lambda pos, area: {"preset": "fireflies", "pos": pos, "area": area, "min_gate": 0.0}


def base(seed, name, about, walk, bounds, terraces, stairs, actors, player, game, emitters, size=(80, 70), blocks=()):
    return {
        "seed": seed, "biome": "cozy-village", "time": {"start": "night", "speed": 0.0016}, "spells": True, "boss_roles": [],
        "camera": {"fov": 24, "pitch": 36, "distance": 33, "zoom": [24, 44], "look": [0, 0, -2.4], "bounds": bounds},
        "hedges": [], "trees": [], "backdrop": {}, "decks": [], "blocks": list(blocks), "buildings": [], "name": name, "about": about, "sprite_roles": ROLES,
        "ground": {"size": list(size), "mat": "stone", "walk": walk}, "slabs": [], "terraces": terraces, "stairs": stairs, "props": [],
        "emitters": emitters, "actors": actors, "player": player, "fx": [], "grades": GRADES, "game": game,
    }


def npc(i, role, name, pos, facing, say, behavior="idle"):
    return {"id": i, "role": role, "name": name, "pos": pos, "facing": facing, "behavior": behavior, "talkable": True, "say": [say]}


def pad(name, rect, cx, w=2.6):
    """a ledge rect with a stair gap centred on cx; the stair's top is the rect's +z (front) edge and it runs down toward +z"""
    return ({"name": name, "rect": rect, "h": H, "top": "plaster", "gaps": [[cx - w / 2, cx + w / 2]]},
            {"name": "stair_" + name, "x": cx, "z_top": rect[3], "width": w, "rise": H, "base": 0.0})


# ---- asgard: Goldspire (story 2.3), 24 x 22 m. The Thunder Hall terrace north (1.34 m + stair), the gold arch [0, 10.6], three rune-pillars, the market, the Skyfield edge, the Moot ground.
t, s = pad("hall_terrace", [-3.6, -11.0, 3.6, -6.15], 0.0)
hub = base(
    431, "Goldspire",
    "Asgard, realm of light, thunder and runes. Goldspire is a hall-city above the clouds: tiered gold halls, rune-pillars crackling neon-blue, white stone going violet in the dusk, gold light pooled "
    "under every lamp. Arrival from Bifrost through the gold arch; the Thunder Hall on the north terrace; the Dawn Temple stair west; the Skyfield edge east.",
    [-12.0, -11.0, 12.0, 11.4], [-11.0, -9.0, 11.0, 10.8],
    [t, WALL("wall_w", [-30, -30, -12.0, 13]), WALL("wall_e", [12.0, -30, 30, 13]), WALL("wall_n", [-12.0, -30, 12.0, -11.0]), {"name": "wall_s", "rect": [-12, 12.4, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [s],
    [npc("envoy_as", "innkeeper", "Envoy Ingrith Goldrune", [4.2, -5.0], "down", "Welcome to Goldspire. Mind the dark halls."),
     npc("as_trader", "dwarftrader", "Nessa", [-8.0, 7.2], "right", "Mead-cakes, storm-charms, gold-glass lamps."),
     npc("groom", "wispcatcher", "Bodil Windmane", [9.6, -6.4], "left", "He bit you? Good. Sky-horses bite what they like."),
     npc("sigrun", "lanternseller", "Sigrun Stormwing", [-4.2, -3.2], "left", "Stay low. I'll go high.")],
    {"role": "traveler", "pos": [-3.4, 1.6], "facing": "up"},
    {"id": "asgard", "title": "Goldspire",
     "exits": [{"rect": [-1.2, -9.85, 1.2, -9.0], "to": "gs_hall", "spawn": "from_town", "label": "the Thunder Hall"},
               {"rect": [-11.9, -10.2, -10.8, -8.0], "to": "gs_temple", "spawn": "from_town", "label": "the Dawn Temple stair"}],
     "portals": [{"to": "bifrost", "spawn": "from_asgard", "rect": [-0.9, 10.1, 0.9, 11.1], "label": "the gold arch back to Bifrost Crossing"}],
     "spawns": {"start": [-3.4, 1.6, "up"], "from_bifrost": [0.0, 9.2, "up"], "qa": [-3.4, 1.6, "up"], "pillars": [0.0, 6.4, "up"], "stall": [-6.6, 6.4, "up"],
                "skyfield": [8.0, -3.0, "right"], "moot": [4.0, -4.0, "up"], "hall": [0.0, -2.0, "up"], "from_hall": [0.0, -8.4, "down"], "from_temple": [-10.2, -8.6, "right"],
                "from_waystone": [8.0, 6.0, "left"]},
     "spring": {"pos": [-11.0, -2.0], "r": 2.0, "secret": "gs_spring"}, "waystone": {"pos": [9.6, 7.0]}},
    [motes([0, 1.6, 0.0], [20, 1.6, 18])],
)

# ---- gs_hall: the Thunder Hall (story 2.4), 14 x 18 m. The high seat on its 1.34 m dais (+ stair), long tables, the rune-forge south-west.
t, s = pad("seat_dais", [-3.6, -9.0, 3.6, -5.95], 0.0)
hall = base(
    432, "The Thunder Hall",
    "The Lord-Warden's hall: a high seat on a gold dais between two rune-pillars, long tables under gold orbs on chains, and the rune-forge where Rune-Master Alrik runs the trial.",
    [-7.0, -9.0, 7.0, 9.0], [-6.4, -7.6, 6.4, 8.6],
    [t, WALL("wall_w", [-30, -30, -7.2, 13]), WALL("wall_e", [7.2, -30, 30, 13]), WALL("wall_n", [-30, -30, 30, -9.2]), {"name": "wall_s", "rect": [-12, 9.6, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [s],
    [npc("lordwarden", "innkeeper", "Lord-Warden Hallgerd Sunmantle", [-2.6, -4.4], "down", "Our dawn is dark. Speak."),
     npc("runemaster", "wispcatcher", "Rune-Master Alrik Runehammer", [-2.6, 5.6], "left", "A rune is a promise in metal."),
     npc("fridleif", "elffolk", "Captain Fridleif Thunderhelm", [4.4, 1.6], "left", "The hall is watched.")],
    {"role": "traveler", "pos": [0.0, 6.6], "facing": "up"},
    {"id": "gs_hall", "title": "The Thunder Hall",
     "exits": [{"rect": [-1.5, 8.2, 1.5, 9.0], "to": "asgard", "spawn": "from_hall", "label": "out to the Goldspire terraces"}], "portals": [],
     "spawns": {"start": [0.0, 6.6, "up"], "from_town": [0.0, 7.4, "up"], "qa": [0.0, 6.6, "up"], "forge": [-3.4, 4.8, "left"], "seat": [0.0, -3.2, "up"], "dais": [0.0, -7.0, "down"]}},
    [motes([0, 1.6, 0.0], [12, 1.6, 16])], size=(60, 60),
)

# ---- gs_temple: the Dawn Temple (story 2.5), 16 x 18 m. The dark altar, the Reliquary door behind it, the side-chapel ledge west (1.34 m + stair), the hidden spring.
t, s = pad("chapel_ledge", [-7.7, -7.05, -1.5, -4.95], -4.6)
temple = base(
    433, "The Dawn Temple",
    "A tall white temple: faceless angel statues, violet and gold stained glass, and a dark altar where a rime-glass copy of the Dawn-Flame drinks the light. Behind it, the gold door of the Reliquary under three rune-locks.",
    [-8.0, -10.0, 8.0, 8.0], [-7.6, -8.4, 7.6, 7.8],
    [t, WALL("wall_w", [-30, -30, -8.2, 13]), WALL("wall_e", [8.2, -30, 30, 13]), WALL("wall_n", [-30, -30, 30, -10.2]), {"name": "wall_s", "rect": [-12, 8.6, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [s],
    [npc("priestess", "innkeeper", "Priestess Sunna Dawnward", [2.4, -3.0], "down", "The dawn has never gone out. Someone carried it away."),
     npc("as_guide", "elffolk", "Orla", [-3.0, 1.4], "right", "I sweep the undercroft. I know every door down there.")],
    {"role": "traveler", "pos": [0.0, 5.2], "facing": "up"},
    {"id": "gs_temple", "title": "The Dawn Temple",
     "exits": [{"rect": [-1.5, 7.2, 1.5, 8.0], "to": "asgard", "spawn": "from_temple", "label": "back down to the Goldspire terraces"}], "portals": [],
     "spawns": {"start": [0.0, 5.2, "up"], "from_town": [0.0, 6.6, "up"], "qa": [0.0, 5.2, "up"], "altar": [0.0, -2.6, "up"], "door": [0.0, -6.8, "up"], "from_reliquary": [0.0, -7.0, "down"], "chapel": [-4.6, -6.2, "down"]},
     "spring": {"pos": [5.6, 6.0], "r": 2.0, "secret": "dt_spring"}},
    [motes([0, 1.6, 0.0], [14, 1.6, 14])], size=(60, 60),
)


# ---- the Gilded Reliquary (story 7): two north-running corridors, 16 m wide, rooms on a 14 m pitch. Room pads follow the pack's room layouts (metadata/asgard_layout.json).
def corridor(seed, name, about, rooms, game, z_n, blocks=()):
    terr, stairs = [], []
    for tag, zc, cx, x0, x1, zl in rooms:
        t, s = pad("plat_" + tag, [x0, zc + zl - 1.05, x1, zc + zl + 1.05], cx, 2.2); terr.append(t); stairs.append(s)
    d = base(seed, name, about, [-8.0, z_n - 0.8, 8.0, 12.4], [-6.6, z_n + 2.0, 6.6, 12.0],
             terr + [WALL("wall_w", [-30, z_n - 26, -8.2, 13], 5.0), WALL("wall_e", [8.2, z_n - 26, 30, 13], 5.0), WALL("wall_n", [-30, z_n - 26, 30, z_n - 0.2], 5.0)],
             stairs, [], {"role": "traveler", "pos": [0.0, 8.4], "facing": "up"}, game, [motes([0, 1.6, 0.0], [14, 1.6, 12])], size=(80, 150), blocks=blocks)
    d["grades"] = DUNGEON_GRADES
    return d


# (tag, room z centre, stair x, pad x0, pad x1, pad z within the room)
R1 = [("g1", 0.0, -4.4, -7.5, -1.3, -3.6), ("g2", -14.0, 4.4, 1.3, 7.5, -4.4), ("g3", -28.0, -4.4, -7.5, -1.3, -3.6), ("g4", -42.0, -4.6, -7.7, -1.5, -5.0), ("g5", -56.0, 4.4, 1.3, 7.5, -4.4)]
R2 = [("g6", 0.0, -4.4, -7.5, -1.3, -3.6), ("g7", -14.0, -4.6, -7.7, -1.5, 3.0), ("g8", -28.0, -4.4, -7.5, -1.3, -4.2), ("g9", -42.0, -4.6, -7.7, -1.5, -5.6)]
Z1, Z2 = -64.0, -50.0
rq1 = corridor(
    434, "The Gilded Reliquary", "Asgard's dungeon, rooms G1-G5 (story 7): the Gold Stair, the Hall of Faceless Angels, the Bright Fountains, the Storm Gallery (Storm Sentinel Prime) and the Inquisitors' Chapel.",
    R1,
    {"id": "reliquary", "title": "The Gilded Reliquary",
     "exits": [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "gs_temple", "spawn": "from_reliquary", "label": "back up to the Dawn Temple"},
               {"rect": [-1.5, Z1 + 0.5, 1.5, Z1 + 1.4], "to": "reliquary2", "spawn": "from_rq1", "label": "deeper into the Reliquary"}], "portals": [],
     "spawns": {"start": [0.0, 8.4, "up"], "from_temple": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "g1": [0.0, 5.0, "up"], "g2": [0.0, -9.0, "up"], "g3": [0.0, -23.0, "up"], "g4": [0.0, -37.0, "up"],
                "g5": [0.0, -51.0, "up"], "from_rq2": [0.0, -61.0, "down"], "undercroft": [0.0, -23.0, "up"]},
     "spring": {"pos": [5.2, -27.6], "r": 2.0, "secret": "rq_spring"}},
    Z1)
# G7 (zc -14): the Rune Bridge crosses a gold-lit void: everything off the bridge (|x| > 1.0) between the far landing and the near ledge is blocked
VOID = [[-8.2, -19.0, -1.0, -12.5], [1.0, -19.0, 8.2, -12.5]]
rq2 = corridor(
    435, "The Gilded Reliquary: the Crypt", "Asgard's dungeon, rooms G6-G9 (story 7): the Mirror of the Dawn (Veyra), the Rune Bridge, the Waystone Ossuary and the Sunless Crypt (Aurelion, the true Dawn-Flame).",
    R2,
    {"id": "reliquary2", "title": "The Gilded Reliquary: the Crypt",
     "exits": [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "reliquary", "spawn": "from_rq2", "label": "back up to the Inquisitors' Chapel"}], "portals": [],
     "spawns": {"start": [0.0, 8.4, "up"], "from_rq1": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "g6": [0.0, 5.0, "up"], "g7": [0.0, -10.4, "up"], "g8": [0.0, -23.0, "up"], "g9": [0.0, -36.0, "up"],
                "bridge_far": [0.0, -19.6, "up"], "from_waystone": [1.6, -26.0, "down"]},
     "waystone": {"pos": [3.6, -27.4]}},
    Z2, blocks=VOID)
rq2["actors"].append(npc("rq_guide", "elffolk", "Orla", [-1.2, -30.8], "down", "This is the guard's ossuary. They sealed the urns. Nobody comes down here."))
if __name__ == "__main__":
    for n, d in (("asgard", hub), ("gs_hall", hall), ("gs_temple", temple), ("reliquary", rq1), ("reliquary2", rq2)):
        (OUT / f"{n}.json").write_text(json.dumps(d, indent=1) + "\n"); print("wrote", n)
