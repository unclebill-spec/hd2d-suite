"""One-off generator for the three Muspelheim town specs. DO NOT RUN: the JSON files in areas/src/ were hand-edited afterwards (start spawn, actors) and are the source of truth.
It stays because gen_caldera.py reuses its base() / GRADES / WALL helpers (it execs only the part above the Cinderhold spec)."""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parents[1]
ROLES = ["actors", "heroes", "combat", "lanternseller", "dwarftrader", "poolkeeper", "wispcatcher", "elffolk", "elffolk2", "innkeeper", "shopkeeper", "nightmerchant", "gnome"]
GRADES = {
    "day": {"fog_color": "#5a3030", "sky_top": "#2a1418", "sky_bottom": "#c8783a", "hemi_sky": "#f0c8a0", "saturation": 0.95, "bugs": 0.0, "warmth": 0.08,
            "exposure": 0.84, "sun_intensity": 1.0, "hemi_intensity": 0.7, "sun_color": "#ffd8b0", "lamp_intensity": 0.85},
    "dusk": {"fog_color": "#2c1418", "sky_top": "#14080c", "sky_bottom": "#7a3018", "exposure": 0.95, "sun_intensity": 0.6, "warmth": 0.1, "sun_color": "#ff9a60", "bugs": 0.5},
    "night": {"fog_color": "#180c10", "sky_top": "#08040a", "sky_bottom": "#4a1c14", "hemi_sky": "#8a5a50", "bugs": 1.0, "exposure": 1.0, "sun_intensity": 0.4, "hemi_intensity": 0.55, "sun_color": "#d08060"},
}
WALL = lambda n, r: {"name": n, "rect": r, "h": 3.6, "top": "stone", "coping": True}
ORANGE = lambda rng=4.5, fx=0.7: {"color": "#ff7a1a", "range": rng, "fixed": fx}
RED = lambda rng=5.0, fx=0.8: {"color": "#ff5a4a", "range": rng, "fixed": fx}


def base(seed, name, about, walk, bounds, slabs, terraces, stairs, props, actors, player, game, emitters, size=(80, 70)):
    return {
        "seed": seed, "biome": "cozy-village", "time": {"start": "night", "speed": 0.0016}, "spells": True, "boss_roles": [],
        "camera": {"fov": 24, "pitch": 36, "distance": 33, "zoom": [24, 44], "look": [0, 0, -2.4], "bounds": bounds},
        "hedges": [], "trees": [], "backdrop": {}, "decks": [], "blocks": [], "buildings": [], "name": name, "about": about, "sprite_roles": ROLES,
        "ground": {"size": list(size), "mat": "stone", "walk": walk}, "slabs": slabs, "terraces": terraces, "stairs": stairs, "props": props,
        "emitters": emitters, "actors": actors, "player": player, "fx": [], "grades": GRADES, "game": game,
    }


def npc(i, role, name, pos, facing, say, behavior="idle"):
    return {"id": i, "role": role, "name": name, "pos": pos, "facing": facing, "behavior": behavior, "talkable": True, "say": [say]}


embers = lambda pos, area: {"preset": "embers", "pos": pos, "area": area, "min_gate": 0.0}

# ---- muspelheim: Cinderhold (story 2.3), 24 x 22 m. v2: follows the art pack's layout (metadata/muspelheim_layout.json); musp_art.py places the real kit pieces.
H = 1.34   # the pack's ledge height
hub = base(
    311, "Cinderhold",
    "Muspelheim, realm of fire. Cinderhold is built on terraces down the wall of a vast caldera: black basalt houses with copper-red roofs, lava-falls pouring into glowing channels, "
    "bridges of cooled glass, forge-glow in every window and drifting ember motes. Arrival from Bifrost through the red arch; the Sigil Forge on the upper terrace; the glass bridge east to the Lavafalls.",
    [-12.0, -11.0, 12.0, 11.4], [-11.0, -9.0, 11.0, 10.8],
    [],
    [{"name": "warden_terrace", "rect": [-3.1, -9.6, 3.1, -5.15], "h": H, "top": "plaster", "gaps": [[-1.45, 1.45]]}, WALL("wall_w", [-30, -30, -12.0, 13]), WALL("wall_e", [12.0, -30, 30, 13]),
     WALL("wall_n", [-12.0, -30, 12.0, -11.0]), {"name": "wall_s", "rect": [-12, 12.4, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [{"name": "stair_warden", "x": 0.0, "z_top": -5.15, "width": 2.9, "rise": H, "base": 0.0}],
    [],
    [npc("mp_trader", "dwarftrader", "Svala, spice trader", [-7.0, 7.2], "down", "Spice, charms, tea. Everything sized for the small. Haggle warm."),
     npc("lizardman", "wispcatcher", "Orm Kettlebrand", [-8.8, -0.2], "right", "She bit you? Good. Biting is how lizards say hello."),
     npc("mp_guide", "lanternseller", "Grettir Ashmarch", [4.6, -4.4], "left", "Contracts, tunnels, tolls. Nothing for free but the view.")],
    {"role": "traveler", "pos": [-4.6, 4.6], "facing": "up"},
    {"id": "muspelheim", "title": "Cinderhold",
     "exits": [{"rect": [-0.9, -9.5, 0.9, -8.7], "to": "mp_hall", "spawn": "from_town", "label": "the Sigil Forge"},
               {"rect": [10.8, -10.2, 11.9, -8.0], "to": "lavafalls", "spawn": "from_town", "label": "the glass bridge to the Lavafalls"}],
     "portals": [{"to": "bifrost", "spawn": "from_muspelheim", "rect": [-0.9, 10.1, 0.9, 11.1], "label": "the red arch back to Bifrost Crossing"}],
     "spawns": {"start": [-4.6, 4.6, "up"], "from_bifrost": [0.0, 9.2, "up"], "qa": [-4.6, 4.6, "up"], "walk": [0.0, 4.9, "up"], "stall": [-5.0, 6.0, "up"], "stables": [-5.6, -0.2, "up"],
                "emberfall": [8.0, -5.6, "up"], "from_hall": [0.0, -7.6, "down"], "from_falls": [10.2, -8.6, "left"]},
     "spring": {"pos": [-11.0, -9.2], "r": 1.6, "secret": "mp_spring"}},
    [embers([0, 1.6, 3.0], [22, 1.6, 12]), embers([0, 1.4, 9.0], [10, 1.0, 3])],
)

# ---- mp_hall: The Sigil Forge (story 2.4), 14 x 18 m (the pack: east gallery 1.34 m + stair)
hall = base(
    312, "The Sigil Forge",
    "The Ember-Warden's hall and the seal foundry of Cinderhold. The Warden's seat before the north wall with a violet shrine-lamp either side; the seal foundry (cooling bed, stamp-press, ledger desk, "
    "the sigil mould wall) along the west wall; a raised gallery with a cold brazier to the east.",
    [-7.0, -9.0, 7.0, 9.0], [-6.8, -7.0, 6.8, 8.8],
    [],
    [{"name": "east_gallery", "rect": [3.0, -7.3, 6.2, -3.15], "h": H, "top": "plaster", "gaps": [[3.15, 6.05]]}, WALL("wall_w", [-30, -30, -7.2, 13]), WALL("wall_e", [7.2, -30, 30, 13]),
     WALL("wall_n", [-30, -30, 30, -9.2]), {"name": "wall_s", "rect": [-12, 9.6, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [{"name": "stair_gallery", "x": 4.6, "z_top": -3.15, "width": 2.9, "rise": H, "base": 0.0}],
    [],
    [npc("envoy_mp", "shopkeeper", "Envoy Sunndis Embervane", [2.6, 6.4], "left", "Muspelheim doesn't welcome tourists. Be a Gate Runner. Be armed."),
     npc("warden_mp", "innkeeper", "Ember-Warden Aska Cindervane", [0.0, -1.0], "down", "Midgard blames us for a sigil. Frost blames us for a war. Who are you?")],
    {"role": "traveler", "pos": [0.0, 5.2], "facing": "up"},
    {"id": "mp_hall", "title": "The Sigil Forge",
     "exits": [{"rect": [-1.5, 8.2, 1.5, 9.0], "to": "muspelheim", "spawn": "from_hall", "label": "the great doors out to Cinderhold"}], "portals": [],
     "spawns": {"start": [0.0, 5.2, "up"], "from_town": [0.0, 7.4, "up"], "qa": [0.0, 5.2, "up"], "hearth": [0.0, 1.0, "up"], "dais": [0.0, -2.0, "up"], "foundry": [-3.0, -1.6, "left"], "gallery": [4.6, -4.8, "down"]}},
    [embers([-5.0, 1.8, 0.0], [4, 1.2, 6])], size=(60, 60),
)

# ---- lavafalls: The Lavafalls (story 2.5), 20 x 16.8 m (the pack: a 1.34 m glass terrace + stair at the west, the Caldera mouth arch north)
falls = base(
    313, "The Lavafalls",
    "Molten falls pour into glowing channels under glass walkways; ember-kin pilgrims, Torka's contest anvils, a cool spring grotto with violet lamps and, at the north end, "
    "the Caldera mouth: a 6 m basalt arch sealed by three seal-doors (the Caldera itself is a later area).",
    [-10.0, -8.4, 10.0, 8.4], [-9.6, -7.2, 9.6, 8.2],
    [],
    [{"name": "glass_terrace", "rect": [-9.0, -0.9, -5.8, 1.25], "h": H, "top": "plaster", "gaps": [[-8.85, -5.95]]}, WALL("wall_w", [-30, -30, -10.2, 13]), WALL("wall_e", [10.2, -30, 30, 13]),
     WALL("wall_n", [-30, -30, 30, -8.6]), {"name": "wall_s", "rect": [-12, 8.8, 12, 30], "h": 1.0, "top": "stone", "coping": True}],
    [{"name": "stair_glass", "x": -7.4, "z_top": 1.25, "width": 2.9, "rise": H, "base": 0.0}],
    [],
    [npc("forgejudge", "nightmerchant", "Torka Ashgrip", [-4.8, -1.0], "right", "Hot iron says what a smith won't. Let it."),
     npc("springkeeper", "poolkeeper", "Yrsa Brightwell", [-6.0, 7.4], "right", "Springs are shy. Whistle, and they bubble.")],
    {"role": "traveler", "pos": [0.0, 5.4], "facing": "up"},
    {"id": "lavafalls", "title": "The Lavafalls",
     "exits": [{"rect": [-10.9, -2.8, -9.7, -0.8], "to": "muspelheim", "spawn": "from_falls", "label": "the glass bridge back to Cinderhold"}], "portals": [],
     "spawns": {"start": [0.0, 5.4, "up"], "from_town": [-9.2, -1.8, "right"], "qa": [0.0, 5.4, "up"], "anvils": [-5.0, 0.2, "left"], "mouth": [0.0, -3.2, "up"], "grotto": [-5.0, 5.0, "left"], "terrace": [-7.4, -0.2, "down"]},
     "spring": {"pos": [-7.4, 6.0], "r": 1.6, "secret": "lf_spring"}},
    [embers([0, 1.6, 0.0], [18, 1.6, 12]), embers([0, 1.4, -6.0], [10, 1.0, 3])], size=(70, 60),
)
for n, d in (("muspelheim", hub), ("mp_hall", hall), ("lavafalls", falls)):
    (OUT / f"{n}.json").write_text(json.dumps(d, indent=1) + "\n")
    print("wrote", n)
