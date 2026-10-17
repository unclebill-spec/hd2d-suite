"""Writes areas/src/caldera.json (The Ember Caldera C1-C4) and caldera2.json (C5-C9: Cold Seam, Cantor's Chapel, Springs of Glass, Waystone Landing,
the Ember Throne) the way barrow / barrow2 are built: one long north-running cavern per area with a stepped floor (real height, a stair per step), 12 m wide.
Kit pieces are placed by tools/hearthmoor/musp_art.py (EXTRA_PLACE); runtime rooms / wedges / lamps / Vharzul are in game/muspelheim.js.
Re-run after editing: python3 gen_caldera.py (then areas build + musp_art)."""
import json, importlib.util
from pathlib import Path
OUT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("town", Path(__file__).with_name("gen_muspelheim_town.py"))
# reuse base() / GRADES / WALL from the town generator without letting it rewrite the town specs
src = Path(__file__).with_name("gen_muspelheim_town.py").read_text().split("# ---- muspelheim: Cinderhold")[0]
ns = {"__file__": __file__}; exec(compile(src, "town_base", "exec"), ns)
base, GRADES, WALL = ns["base"], ns["GRADES"], ns["WALL"]
H1, H2, H3 = 1.2, 2.4, 3.6
DUNGEON_GRADES = {   # darker caves: warm forge glow and lava orange carry the night, cold blue / violet only as accents (check_scene grades: night < day, warm pixels, dusk bluer than day)
    "day": {**GRADES["day"], "exposure": 0.9, "sun_intensity": 0.9, "hemi_intensity": 0.75},
    "dusk": dict(GRADES["dusk"]), "night": dict(GRADES["night"])}


def cave(seed, name, about, z_n, terr, stairs, blocks, game, emitters, actors=()):
    d = base(seed, name, about, [-11.6, z_n - 0.8, 11.6, 12.4], [-10.4, z_n + 2.0, 10.4, 12.0], [],
             terr + [WALL("wall_w", [-30, z_n - 26, -12.0, 13]), WALL("wall_e", [12.0, z_n - 26, 30, 13]), WALL("wall_n", [-30, z_n - 26, 30, z_n - 0.2])],
             stairs, [], list(actors), {"role": "traveler", "pos": [0.0, 8.4], "facing": "up"}, game, emitters, size=(80, 150))
    for w in d["terraces"]:
        if w["name"].startswith("wall"): w["h"] = 7.0 if "caldera2" in name.lower() else 4.8
    d["blocks"] = blocks
    d["grades"] = DUNGEON_GRADES
    return d


emb = lambda pos, area: {"preset": "embers", "pos": pos, "area": area, "min_gate": 0.0}
# ---- caldera: C1 Mouth (z 12 .. -4), C2 Ashen Stair (plat 1.2, -4.2 .. -16), C3 Glass Bridge (2.4, -16.4 .. -30.2), C4 Furnace Hall (2.4, -30.2 .. -44)
c1 = cave(321, "The Ember Caldera", "Muspelheim's dungeon, rooms C1-C4 (story 7): the Caldera Mouth, the Ashen Stair, the Glass Bridge over the lava and the Furnace Hall. Basalt, lava glow, ember-lamps.",
          -44.0,
          [{"name": "plat_c2", "rect": [-11.9, -16.0, 11.9, -4.2], "h": H1, "top": "plaster", "gaps": [[-1.5, 1.5]]},
           {"name": "bridge_c3", "rect": [-2.6, -30.2, 2.6, -16.4], "h": H2, "top": "plaster", "gaps": [[-1.5, 1.5]]},
           {"name": "plat_c4", "rect": [-11.9, -44.0, 11.9, -30.2], "h": H2, "top": "plaster"}],
          [{"name": "stair_c2", "x": 0.0, "z_top": -4.2, "width": 3.0, "rise": H1, "base": 0.0}, {"name": "stair_c3", "x": 0.0, "z_top": -16.4, "width": 3.0, "rise": H1, "base": H1}],
          [[-11.9, -30.2, -2.8, -16.4], [2.8, -30.2, 11.9, -16.4]],   # the lava either side of the glass bridge
          {"id": "caldera", "title": "The Ember Caldera",
           "exits": [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "lavafalls", "spawn": "mouth", "label": "back out to the Lavafalls"},
                     {"rect": [-1.5, -43.9, 1.5, -43.0], "to": "caldera2", "spawn": "from_caldera", "label": "the Ember Caldera, deeper"}], "portals": [],
           "spawns": {"start": [0.0, 8.4, "up"], "from_falls": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "walk": [0.0, 3.0, "up"], "stair": [0.0, -5.6, "up"], "bridge": [0.0, -15.0, "up"],
                      "furnace": [0.0, -31.6, "up"], "tunnel": [0.0, -31.6, "up"], "from_caldera2": [0.0, -41.4, "down"]}},
          [emb([0, 2.0, 2.0], [20, 2.0, 10]), emb([0, 2.0, -24.0], [8, 2.0, 12])])
c2 = cave(322, "The Ember Caldera: the Throne", "Muspelheim's dungeon, rooms C5-C9 (story 7): the Cold Seam, the Cantor's Chapel, the Springs of Glass, the Waystone Landing and the Ember Throne where Vharzul waits.",
          -58.0,
          [{"name": "plat_c6", "rect": [-11.9, -17.0, 11.9, -4.2], "h": H1, "top": "plaster", "gaps": [[-1.5, 1.5]]},
           {"name": "plat_c7", "rect": [-11.9, -42.0, 11.9, -17.4], "h": H2, "top": "plaster", "gaps": [[-1.5, 1.5]]},
           {"name": "plat_c9", "rect": [-11.9, -58.0, 11.9, -42.4], "h": H3, "top": "plaster", "gaps": [[-1.5, 1.5]]}],
          [{"name": "stair_c6", "x": 0.0, "z_top": -4.2, "width": 3.0, "rise": H1, "base": 0.0}, {"name": "stair_c7", "x": 0.0, "z_top": -17.4, "width": 3.0, "rise": H1, "base": H1},
           {"name": "stair_c9", "x": 0.0, "z_top": -42.4, "width": 3.0, "rise": H1, "base": H2}],
          [],
          {"id": "caldera2", "title": "The Ember Caldera: the Throne",
           "exits": [{"rect": [-1.5, 10.4, 1.5, 11.4], "to": "caldera", "spawn": "from_caldera2", "label": "back up the Furnace Hall"}], "portals": [],
           "spawns": {"start": [0.0, 8.4, "up"], "from_caldera": [0.0, 8.4, "up"], "qa": [0.0, 8.0, "up"], "walk": [0.0, 3.0, "up"], "chapel": [0.0, -5.6, "up"], "springs": [0.0, -18.8, "up"],
                      "landing": [0.0, -32.0, "up"], "throne": [0.0, -43.6, "up"], "from_waystone": [-3.6, -34.8, "down"]},
           "spring": {"pos": [-6.0, -24.0], "r": 1.8, "secret": "cd_spring"}, "waystone": {"pos": [-3.6, -37.0]}},
          [emb([0, 2.0, 2.0], [20, 2.0, 10]), emb([0, 2.0, -34.0], [14, 2.0, 12])])
for n, d in (("caldera", c1), ("caldera2", c2)):
    (OUT / f"{n}.json").write_text(json.dumps(d, indent=1) + "\n"); print("wrote", n)
