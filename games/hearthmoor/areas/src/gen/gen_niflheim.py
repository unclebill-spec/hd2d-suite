"""[NIFLHEIM] One-off generator for the three Mistmere skeleton specs (story 2.1: niflheim, nf_home, iceglow). DO NOT RE-RUN once the JSON has been hand-edited:
the JSON files in areas/src/ are the source of truth. Stand-in kit only (stock realm_arch / realm_glow_ice); nifl_art.py places the real pieces when the pack is READY."""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parents[1]
ROLES = ["actors", "heroes", "combat", "lanternseller", "dwarftrader", "poolkeeper", "wispcatcher", "elffolk", "elffolk2", "innkeeper", "shopkeeper", "nightmerchant", "gnome"]
GRADES = {   # cold: black water, deep ice, snow-lit; lamps are the neon-blue cold fire (#3fb8ff) and stay warm-free
    "day": {"fog_color": "#6a7e9c", "sky_top": "#2a3a5a", "sky_bottom": "#9cb4d4", "hemi_sky": "#c8d6ec", "saturation": 0.95, "bugs": 0.0, "warmth": -0.05,
            "exposure": 0.82, "sun_intensity": 1.0, "hemi_intensity": 0.7, "sun_color": "#e8f0ff", "lamp_intensity": 0.85},
    "dusk": {"fog_color": "#1c2848", "sky_top": "#0c1430", "sky_bottom": "#34508c", "exposure": 0.95, "sun_intensity": 0.6, "warmth": -0.1, "sun_color": "#8cb0f0", "bugs": 0.5},
    "night": {"fog_color": "#0c1428", "sky_top": "#050a1c", "sky_bottom": "#1b2a4a", "hemi_sky": "#5c7cb0", "bugs": 1.0, "exposure": 1.0, "sun_intensity": 0.4, "hemi_intensity": 0.55, "sun_color": "#7ea0e0"},
}
H = 1.2   # real height: every Mistmere area has a 1.2 m terrace with a stair
WALL = lambda n, r: {"name": n, "rect": r, "h": 3.6, "top": "stone", "coping": True}
COLD = lambda rng=4.0, fx=0.7: {"color": "#3fb8ff", "range": rng, "fixed": fx}


def base(seed, name, about, walk, bounds, terraces, stairs, props, actors, player, game, emitters, size=(80, 70)):
    return {
        "seed": seed, "biome": "cozy-village", "time": {"start": "night", "speed": 0.0016}, "spells": True, "boss_roles": [],
        "camera": {"fov": 24, "pitch": 36, "distance": 33, "zoom": [24, 44], "look": [0, 0, -2.4], "bounds": bounds},
        "hedges": [], "trees": [], "backdrop": {}, "decks": [], "blocks": [], "buildings": [], "name": name, "about": about, "sprite_roles": ROLES,
        "ground": {"size": list(size), "mat": "stone", "walk": walk}, "slabs": [], "terraces": terraces, "stairs": stairs, "props": props,
        "emitters": emitters, "actors": actors, "player": player, "fx": [], "grades": GRADES, "game": game,
    }


def npc(i, role, name, pos, facing, say, behavior="idle"):
    return {"id": i, "role": role, "name": name, "pos": pos, "facing": facing, "behavior": behavior, "talkable": True, "say": [say]}


snow = lambda pos, area: {"preset": "snowfall", "pos": pos, "area": area, "min_gate": 0.0}
motes = lambda pos, area: {"preset": "fireflies", "pos": pos, "area": area, "min_gate": 0.0}

# ---- niflheim: Mistmere (story 2.3), 24 x 22 m. The hall terrace (Gudrun, the Cold Mark table) 1.2 m + stair at x 0; the ice arch [0, 10.6]; the lake in the middle.
hub = base(
    411, "Mistmere",
    "Niflheim, realm of ice, mist and water. Mistmere is a ring of pale-stone houses on the shore of a vast frozen lake: bridges of ice, a neon-blue cold-fire lantern on every post, "
    "frost runes on the gates and the aurora pouring green and violet over black mountains. Arrival from Bifrost through the ice arch; the Frost-Speaker's hall on the north terrace; "
    "the Quiet Shore path east; the cave stair west to the Glowpool Caverns.",
    [-12.0, -11.0, 12.0, 11.4], [-11.0, -9.0, 11.0, 10.8],
    [{"name": "hall_terrace", "rect": [-4.2, -9.8, 4.2, -5.6], "h": H, "top": "plaster", "gaps": [[-1.45, 1.45]]}, WALL("wall_w", [-30, -30, -12.0, 13]), WALL("wall_e", [12.0, -30, 30, 13]),
     WALL("wall_n", [-12.0, -30, 12.0, -11.0]), {"name": "wall_s", "rect": [-12, 12.4, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [{"name": "stair_hall", "x": 0.0, "z_top": -5.6, "width": 2.9, "rise": H, "base": 0.0}],
    [{"piece": "realm_arch", "pos": [0.0, 10.6], "glow": {"color": "#3fb8ff", "range": 6.0, "fixed": 0.8}}, {"piece": "realm_glow_ice", "pos": [0.0, 10.6]}],
    [npc("frostspeaker", "innkeeper", "Frost-Speaker Gudrun Hoarwick", [0.0, -8.2], "down", "Don't be loud. The lake listens."),
     npc("nf_trader", "dwarftrader", "Tove Lanternwright", [-8.5, -3.0], "right", "Eat. Mistmere hasn't had a guest in years."),
     npc("elkman", "wispcatcher", "Ketil Icehook", [9.0, -3.0], "left", "She bit you? Good. Elk say hello with their teeth."),
     npc("nf_a", "elffolk", "Mistmere villager", [-6.0, 7.4], "right", "The aurora hums, if you stand still."),
     npc("nf_b", "elffolk2", "Mistmere villager", [6.4, 7.0], "left", "We lit the lanterns for her anyway.")],
    {"role": "traveler", "pos": [-4.6, 4.6], "facing": "up"},
    {"id": "niflheim", "title": "Mistmere",
     "exits": [{"rect": [10.8, -10.2, 11.9, -8.0], "to": "nf_home", "spawn": "from_town", "label": "the Quiet Shore path"},
               {"rect": [-11.9, -10.2, -10.8, -8.0], "to": "iceglow", "spawn": "from_town", "label": "the cave stair to the Glowpool Caverns"}],
     "portals": [{"to": "bifrost", "spawn": "from_niflheim", "rect": [-0.9, 10.1, 0.9, 11.1], "label": "the ice arch back to Bifrost Crossing"}],
     "spawns": {"start": [-4.6, 4.6, "up"], "from_bifrost": [0.0, 9.2, "up"], "qa": [-4.6, 4.6, "up"], "lanterns": [0.0, 6.6, "up"], "stall": [-7.4, -1.6, "up"],
                "paddock": [8.0, -1.6, "up"], "hall": [0.0, -4.4, "up"], "from_shore": [10.2, -8.6, "left"], "from_caves": [-10.2, -8.6, "right"]},
     "spring": {"pos": [-11.5, -2.0], "r": 1.6, "secret": "nf_spring"}},
    [snow([0, 3.0, 2.0], [22, 3.0, 20])],
)

# ---- nf_home: The Quiet Shore and Ashmantle House (story 2.4), 16 x 16 m. Eira's grave on the raised shore ledge, the house east.
home = base(
    412, "The Quiet Shore",
    "Veyra's childhood shore: black water, a standing stone of glowing runes with violet shrine-lamps (Eira's grave) on a raised ledge, and the small stone house with a cold-fire hearth "
    "where Eira's room stays shut. The reveal of the Rift-Warden happens here.",
    [-8.0, -8.0, 8.0, 8.0], [-7.6, -6.6, 7.6, 7.8],
    [{"name": "grave_ledge", "rect": [-3.2, -7.8, 3.2, -2.9], "h": H, "top": "plaster", "gaps": [[-1.45, 1.45]]}, WALL("wall_w", [-30, -30, -8.2, 13]), WALL("wall_e", [8.2, -30, 30, 13]),
     WALL("wall_n", [-30, -30, 30, -8.2]), {"name": "wall_s", "rect": [-12, 8.6, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [{"name": "stair_grave", "x": 0.0, "z_top": -2.9, "width": 2.9, "rise": H, "base": 0.0}],
    [],
    [npc("nf_shore", "elffolk", "Mistmere mourner", [-5.4, 1.4], "right", "We never stopped missing her. We never said so."),
     npc("hrefna", "lanternseller", "Hrefna Frostveil", [4.4, 0.6], "left", "I know this fight. I learned it from her.")],
    {"role": "traveler", "pos": [0.0, 5.2], "facing": "up"},
    {"id": "nf_home", "title": "The Quiet Shore",
     "exits": [{"rect": [-1.5, 7.2, 1.5, 8.0], "to": "niflheim", "spawn": "from_shore", "label": "the path back to Mistmere"}], "portals": [],
     "spawns": {"start": [0.0, 5.2, "up"], "from_town": [0.0, 6.6, "up"], "qa": [0.0, 5.2, "up"], "shore": [0.0, 0.4, "up"], "grave": [0.0, -2.2, "up"], "house": [5.0, -1.0, "left"]}},
    [snow([0, 3.0, 0.0], [14, 3.0, 14])], size=(60, 60),
)

# ---- iceglow: The Glowpool Caverns (story 2.5), 20 x 16.8 m. The Spire mouth terrace north (1.2 m + stair), the rune-hall west, five pools.
cave = base(
    413, "The Glowpool Caverns",
    "Ice caves under the frozen lake, lit from below by bioluminescent pools; frost runes on every pillar, rime-glass glow orbs, the rune-hall of the Frost-Speaker to the west and, at the north end, "
    "the Spire mouth: a 6 m ice door sealed by three rune-locks (the Frozen Spire itself is a later area).",
    [-10.0, -8.4, 10.0, 8.4], [-9.6, -7.2, 9.6, 8.2],
    [{"name": "spire_terrace", "rect": [-3.1, -8.2, 3.1, -4.4], "h": H, "top": "plaster", "gaps": [[-1.45, 1.45]]}, WALL("wall_w", [-30, -30, -10.2, 13]), WALL("wall_e", [10.2, -30, 30, 13]),
     WALL("wall_n", [-30, -30, 30, -8.6]), {"name": "wall_s", "rect": [-12, 8.8, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [{"name": "stair_spire", "x": 0.0, "z_top": -4.4, "width": 2.9, "rise": H, "base": 0.0}],
    [],
    [npc("frostspeaker", "innkeeper", "Frost-Speaker Gudrun Hoarwick", [-6.0, -4.0], "right", "Frost isn't cruelty. It's patience.")],
    {"role": "traveler", "pos": [0.0, 5.4], "facing": "up"},
    {"id": "iceglow", "title": "The Glowpool Caverns",
     "exits": [{"rect": [9.7, -2.8, 10.9, -0.8], "to": "niflheim", "spawn": "from_caves", "label": "the cave stair back to Mistmere"}], "portals": [],
     "spawns": {"start": [0.0, 5.4, "up"], "from_town": [9.2, -1.8, "left"], "qa": [0.0, 5.4, "up"], "runehall": [-5.0, -2.0, "left"], "mouth": [0.0, -3.4, "up"], "pools": [4.0, 3.0, "up"]},
     "spring": {"pos": [7.6, 6.0], "r": 1.6, "secret": "ig_spring"}},
    [motes([0, 1.6, 0.0], [18, 1.6, 12])], size=(70, 60),
)
if __name__ == "__main__":
    for n, d in (("niflheim", hub), ("nf_home", home), ("iceglow", cave)):
        (OUT / f"{n}.json").write_text(json.dumps(d, indent=1) + "\n")
        print("wrote", n)
