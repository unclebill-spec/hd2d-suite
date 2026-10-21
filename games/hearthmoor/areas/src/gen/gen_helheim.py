"""[HELHEIM] Writes the five Helheim specs (story helheim.md 2.1, 7): helheim (Gloamhaven), hh_shore (the Lantern Shore), hh_archive (the Quiet Archive), and the
Ossuary of Whispers as two corridors like reliquary / reliquary2: ossuary (O1-O5) and ossuary2 (O6-O9), 14 m pitch. Every area / room has a real 1.34 m ledge
(the pack's mist_ledge pair) + one stair (mist_stair) at the pack's layout position; the spec owns the terrain, so tools/hearthmoor/hel_art.py does not place
mist_ledge / mist_stair. Kit pieces, floors, walls, lamps and fx come from hel_art.py (the pack's layout, metadata/helheim_layout.json).
Re-running overwrites the specs."""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parents[1]
LAY = Path("/workspace/hearthmoor-staging/art/helheim/metadata/helheim_layout.json")
ROLES = ["actors", "heroes", "combat", "lanternseller", "dwarftrader", "poolkeeper", "wispcatcher", "elffolk", "elffolk2", "innkeeper", "shopkeeper", "nightmerchant", "gnome"]
GRADES = {   # Gloamhaven: violet night, blue cold fire (lights only); the day is a pale lilac overcast
    "day": {"fog_color": "#9a94b0", "sky_top": "#3a3060", "sky_bottom": "#b8acd0", "hemi_sky": "#dcd4ec", "saturation": 0.9, "bugs": 0.0, "warmth": 0.0,
            "exposure": 0.84, "sun_intensity": 0.9, "hemi_intensity": 0.7, "sun_color": "#f0e8ff", "lamp_intensity": 0.85},
    "dusk": {"fog_color": "#2a2248", "sky_top": "#221c44", "sky_bottom": "#4e3a7a", "exposure": 0.95, "sun_intensity": 0.55, "warmth": -0.05, "sun_color": "#a49cf0", "bugs": 0.5},
    "night": {"fog_color": "#14102a", "sky_top": "#0a0820", "sky_bottom": "#261e48", "hemi_sky": "#6656a4", "bugs": 1.0, "exposure": 1.0, "sun_intensity": 0.4, "hemi_intensity": 0.55, "sun_color": "#9688dc"},
}
DUNGEON_GRADES = {"day": {**GRADES["day"], "exposure": 0.9, "sun_intensity": 0.9, "hemi_intensity": 0.75}, "dusk": dict(GRADES["dusk"]), "night": dict(GRADES["night"])}
H = 1.34   # mist_ledge height
WALL = lambda n, r, h=3.6: {"name": n, "rect": r, "h": h, "top": "stone", "coping": True}
motes = lambda pos, area: {"preset": "fireflies", "pos": pos, "area": area, "min_gate": 0.0}


def base(seed, name, about, walk, bounds, terraces, stairs, actors, player, game, emitters, size=(80, 70), blocks=(), grades=GRADES):
    return {
        "seed": seed, "biome": "cozy-village", "time": {"start": "night", "speed": 0.0016}, "spells": True, "boss_roles": [],
        "camera": {"fov": 24, "pitch": 36, "distance": 33, "zoom": [24, 44], "look": [0, 0, -2.4], "bounds": bounds},
        "hedges": [], "trees": [], "backdrop": {}, "decks": [], "blocks": [list(b) for b in blocks], "buildings": [], "name": name, "about": about, "sprite_roles": ROLES,
        "ground": {"size": list(size), "mat": "stone", "walk": walk}, "slabs": [], "terraces": terraces, "stairs": stairs, "props": [],
        "emitters": emitters, "actors": actors, "player": player, "fx": [], "grades": grades, "game": game,
    }


def npc(i, role, name, pos, facing, say, behavior="idle"):
    return {"id": i, "role": role, "name": name, "pos": [round(pos[0], 2), round(pos[1], 2)], "facing": facing, "behavior": behavior, "talkable": True, "say": [say]}


def ledge(lay, key, zc=0.0, name=None, w=2.6):
    """the pack's mist_ledge pair (3.1 x 2.1 each, side by side) + its mist_stair (top at the ledge's +z edge, running down toward +z)"""
    ps = lay[key]["pieces"]
    L = [p[1] for p in ps if p[0] == "mist_ledge"]; st = [p[1] for p in ps if p[0] == "mist_stair"][0]
    x0 = min(p[0] for p in L) - 1.55; x1 = max(p[0] for p in L) + 1.55; lz = L[0][2] + zc
    rect = [round(x0, 2), round(lz - 1.05, 2), round(x1, 2), round(lz + 1.05, 2)]
    nm = name or ("ledge_" + key)
    return ({"name": nm, "rect": rect, "h": H, "top": "plaster", "gaps": [[round(st[0] - w / 2, 2), round(st[0] + w / 2, 2)]]},
            {"name": "stair_" + nm, "x": round(st[0], 2), "z_top": rect[3], "width": w, "rise": H, "base": 0.0})


def main():
    lay = json.loads(LAY.read_text())
    out = {}
    # ---- Gloamhaven (24 x 22): Hel's arch south, the lake + Lantern Bridge in the middle, Hel's Hall north on its ledge, the inn west, the ferry steps east
    t, s = ledge(lay, "helheim", name="hall_ledge")
    out["helheim"] = base(461, "Gloamhaven", "Helheim, the quiet realm of the dead. Gloamhaven is a lantern-lit spirit town on a still black lake: crooked houses with violet windows, the Lantern Bridge, willows hung with glow orbs, and ghosts going about their evenings. Hel's arch south (to Bifrost), Hel's Hall north on its ledge, the Last Hearth Inn west, the ferry steps east (the Lantern Shore), the Archive door north-west.",
        [-12.0, -11.0, 12.0, 11.4], [-11.0, -9.0, 11.0, 10.8], [t, WALL("wall_w", [-30, -30, -12.0, 13]), WALL("wall_e", [12.0, -30, 30, 13]), WALL("wall_n", [-12.0, -30, 12.0, -11.0]), WALL("wall_s", [-12, 12.4, 12, 30], 1.0)], [s],
        [npc("hel", "innkeeper", "Hel", [3.15, -5.4], "down", "Mind your lamp. It's the only one like it here."),
         npc("ferryman", "dwarftrader", "Corvin Lanternmere", [9.45, -1.0], "left", "A lantern isn't for seeing. It's so you can be seen."),
         npc("innghost", "poolkeeper", "Hettie Tallow", [-7.35, 1.4], "right", "Sit, sit, love. Soup? No, you can't have it, you're alive. Smell it then."),
         npc("childghost", "wispcatcher", "Hollin", [-3.65, 7.9], "down", "...Are you living? You're very loud."),
         npc("bakerghost", "shopkeeper", "Old Marrow", [-10.65, -1.8], "down", "Best crust in Helheim. Only crust in Helheim."),
         npc("gloam_folk", "elffolk", "A Gloamhaven ghost", [-6.35, -7.85], "right", "Mind the road. It wails, but it doesn't bite.")],
        {"role": "traveler", "pos": [0.0, 8.6], "facing": "up"},
        {"id": "helheim", "title": "Gloamhaven",
         "exits": [{"rect": [-11.9, -10.2, -10.8, -8.0], "to": "hh_archive", "spawn": "from_town", "label": "the Quiet Archive"},
                   {"rect": [10.8, -4.2, 11.9, -1.8], "to": "hh_shore", "spawn": "from_town", "label": "the ferry steps to the Lantern Shore"}],
         "portals": [{"to": "bifrost", "spawn": "from_helheim", "rect": [-0.9, 10.1, 0.9, 11.1], "label": "Hel's arch back to Bifrost Crossing"}],
         "spawns": {"start": [0.0, 8.6, "up"], "from_bifrost": [0.0, 9.2, "up"], "qa": [0.0, 8.6, "up"], "bridge": [0.0, 5.0, "up"], "hall": [0.0, -3.0, "up"],
                    "inn": [-5.6, 1.0, "left"], "from_archive": [-9.4, -7.0, "right"], "from_shore": [9.8, 0.4, "left"], "spring": [-9.0, 2.2, "left"]},
         "spring": {"pos": [-11.0, 4.0], "r": 2.0, "secret": "hh_spring"}},
        [motes([0, 1.6, 0.0], [20, 1.6, 18])], blocks=[(-4.0, -2.0, -1.25, 4.0), (1.25, -2.0, 4.0, 4.0)])
    # ---- the Lantern Shore (16 x 16 + the stair run): the black lake north (blocked, the jetty strip open), willows, the reeds and ls_spring west
    t, s = ledge(lay, "hh_shore", name="shore_ledge")
    out["hh_shore"] = base(462, "The Lantern Shore", "A pebble shore on the black lake where the lantern-boats leave. Willows hung with glow orbs, the jetty, Eira's spirit at the water's edge, and a warm bubbling spring in the reeds.",
        [-8.0, -8.2, 8.0, 10.0], [-7.0, -6.0, 7.0, 9.0], [t, WALL("wall_w", [-30, -30, -8.2, 13]), WALL("wall_e", [8.2, -30, 30, 13]), WALL("wall_n", [-30, -30, 30, -8.4]), WALL("wall_s", [-12, 10.6, 12, 30], 1.0)], [s],
        [npc("eira_spirit", "lanternseller", "Eira Ashmantle", [4.0, -0.4], "left", "You're the one my sister keeps counting. Hello. I'm Eira."),
         npc("ferryman", "dwarftrader", "Corvin Lanternmere", [-1.6, 0.6], "down", "Ravens like bright things. Leave one a button. Then wait."),
         npc("childghost", "wispcatcher", "Hollin", [-3.2, 2.6], "up", "The lanterns go all the way across. I counted.")],
        {"role": "traveler", "pos": [0.9, 7.2], "facing": "up"},
        {"id": "hh_shore", "title": "The Lantern Shore",
         "exits": [{"rect": [-3.5, 9.2, -1.5, 10.0], "to": "helheim", "spawn": "from_shore", "label": "back to Gloamhaven"}], "portals": [],
         "spawns": {"start": [-2.4, 7.6, "up"], "from_town": [-2.4, 7.6, "up"], "qa": [-2.4, 7.6, "up"], "jetty": [0.0, 1.6, "up"], "eira": [2.4, 1.0, "right"]},
         "spring": {"pos": [-6.0, 5.4], "r": 2.0, "secret": "ls_spring"}},
        [motes([0, 1.6, 2.0], [14, 1.6, 12])], size=(60, 60), blocks=[(-8.0, -8.2, -1.0, -2.0), (1.0, -8.2, 8.0, -2.0), (-1.0, -8.2, 1.0, -4.0)])
    # ---- the Quiet Archive (14 x 16): shelves on three walls, the Ledger lectern, Quillon's desk, the bone-white Ossuary door north
    t, s = ledge(lay, "hh_archive", name="stack_ledge")
    out["hh_archive"] = base(463, "The Quiet Archive", "Tall shelves, floating candles in blue cold fire, the Ledger of Names on a lectern with torn pages, Quillon's desk, and the bone-white Ossuary door with violet runes.",
        [-7.6, -9.6, 7.6, 8.0], [-6.6, -8.4, 6.6, 7.8], [t, WALL("wall_w", [-30, -30, -8.0, 13]), WALL("wall_e", [8.0, -30, 30, 13]), WALL("wall_n", [-30, -30, 30, -10.0]), WALL("wall_s", [-12, 8.6, 12, 30], 1.0)], [s],
        [npc("archivist_hh", "innkeeper", "Quillon Greymarch", [-4.6, -1.8], "down", "The Ledger has eleven million names, and I've read them all twice."),
         npc("sailorghost", "dwarftrader", "A sailor ghost", [-1.4, 3.6], "left", "Have you seen my ship? She's small. Very small. I may have shrunk her.")],
        {"role": "traveler", "pos": [0.0, 6.0], "facing": "up"},
        {"id": "hh_archive", "title": "The Quiet Archive",
         "exits": [{"rect": [-1.5, 7.2, 1.5, 8.0], "to": "helheim", "spawn": "from_archive", "label": "back to Gloamhaven"}], "portals": [],
         "spawns": {"start": [0.0, 6.0, "up"], "from_town": [0.0, 6.4, "up"], "qa": [0.0, 6.0, "up"], "ledger": [0.0, -2.4, "up"], "door": [0.0, -6.4, "up"], "from_ossuary": [0.0, -6.4, "down"]}},
        [motes([0, 1.6, 0.0], [12, 1.6, 14])], size=(60, 60))
    # ---- the Ossuary of Whispers: O1-O5 (ossuary) and O6-O9 (ossuary2), rooms stacked north at a 14 m pitch
    def corridor(aid, rooms, top, seed, title, about, exits, spawns, extra=None):
        ts, ss = [], []
        for key, zc in rooms:
            t, s = ledge(lay, key, zc, name="plat_" + key.split("_")[1]); ts.append(t); ss.append(s)
        ts += [WALL("wall_w", [-30, top - 26, -8.2, 13], 5.0), WALL("wall_e", [8.2, top - 26, 30, 13], 5.0), WALL("wall_n", [-30, top - 26, 30, top + 0.6], 5.0)]
        g = {"id": aid, "title": title, "exits": exits, "portals": [], "spawns": spawns, **(extra or {})}
        return base(seed, title, about, [-8.0, top - 0.8, 8.0, 12.4], [-6.6, top + 2.0, 6.6, 12.0], ts, ss, [], {"role": "traveler", "pos": [0.0, 8.4], "facing": "up"}, g,
                    [motes([0, 1.6, 0.0], [14, 1.6, 12])], size=(80, 150), grades=DUNGEON_GRADES)
    R1 = [("ossuary_o1", 0.0), ("ossuary_o2", -14.0), ("ossuary_o3", -28.0), ("ossuary_o4", -42.0), ("ossuary_o5", -56.0)]
    R2 = [("ossuary_o6", 0.0), ("ossuary_o7", -14.0), ("ossuary_o8", -28.0), ("ossuary_o9", -42.0)]
    out["ossuary"] = corridor("ossuary", R1, -64.0, 464, "The Ossuary of Whispers",
        "Helheim's dungeon, rooms O1-O5 (story 7): the Bone Door, the Whispering Hall, the Lantern Graves, the Garnet Gallery and Vesperin's Salon.",
        [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "hh_archive", "spawn": "from_ossuary", "label": "back up to the Quiet Archive"},
         {"rect": [-1.5, -63.5, 1.5, -62.6], "to": "ossuary2", "spawn": "from_os1", "label": "deeper into the Ossuary"}],
        {"start": [0.0, 8.4, "up"], "from_archive": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "o1": [0.0, 5.0, "up"], "o2": [0.0, -9.0, "up"], "o3": [0.0, -23.0, "up"],
         "o4": [0.0, -37.0, "up"], "o5": [0.0, -51.0, "up"], "from_os2": [0.0, -61.0, "down"]},
        {"spring": {"pos": [5.0, -17.6], "r": 2.0, "secret": "os_spring"}})
    out["ossuary2"] = corridor("ossuary2", R2, -50.0, 465, "The Ossuary of Whispers: the Pale Throne",
        "Helheim's dungeon, rooms O6-O9 (story 7): the Choir Loft, the Sleeping Liches, Mordrath's Vault (a waystone) and the Pale Throne (Mordrath, the Pale Sovereign).",
        [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "ossuary", "spawn": "from_os2", "label": "back up to Vesperin's Salon"}],
        {"start": [0.0, 8.4, "up"], "from_os1": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "o6": [0.0, 5.0, "up"], "o7": [0.0, -9.0, "up"], "o8": [0.0, -23.0, "up"],
         "o9": [0.0, -37.0, "up"], "from_waystone": [1.6, -26.0, "down"]},
        {"waystone": {"pos": [3.6, -28.0]}})
    for k, v in out.items():
        (OUT / f"{k}.json").write_text(json.dumps(v, indent=1))
        print("wrote", k, [t["rect"] for t in v["terraces"] if not t["name"].startswith("wall")])


if __name__ == "__main__":
    main()
