# hd2d kit

Town-kit .glb generator. It extends the n64-suite mesh code; the original is vendored as vendor/n64_mesh.py.

```
hd2d kit --biome cozy-village --out PROJECT/public/art/kit --texel PROJECT/public/art/texel
```

- Base pieces:
  - Ground and levels: terrace (stair gaps, coping), stairs, retaining_wall, ground_slab, hills.
  - 4 cottages (cottage_baker, cottage_tall, cottage_stone, cottage_shop) with thick gable roofs, timber framing, flower boxes, chimneys and wall lamps.
  - Props: market_stall (awning + bread), barrel, crate, sign, flower_crate, bunting, lamp_post, fence, bench, hedge, well.
- Added for Bakery Lane:
  - `bakery`: brick bread oven on the gable with a glowing mouth (a lamp marker) and an `ovens` marker at the flue for oven steam. Hanging loaf sign.
  - `inn`: 2 storeys with a stone ground floor, jetty and dormer. Hanging mug sign.
  - `flower_shop`: thatched shopfront with flower pots/crates out front and a hanging flower sign.
  - `hanging_sign_{loaf,mug,flower,key}`: iron bracket, chains and board, also as standalone pieces.
  - `laundry`: a washing line between two world points with posts, sheets and shirts. Scene spec `"laundry": [{"from": [x,y,z], "to": [...], "sag": 0.3, "base": [y0, y1]}]`.
  - `fountain`: small open basin with a visible water disc and a top bowl. Markers: `spray` (jet top) and `water` (water height).
- Added for Ravenhold Harbor (`kit_harbor.py`): `harbor_water` (64 x 34 m dark water with faint swell lines), `pier` (plank jetty, deck at y 0, posts into the water; pair it with a spec `decks` rect), `rowboat`, `skiff` (furled sail, cold-fire stern lamp), `pier_lantern` / `quay_lantern` (cold-fire `#5ab4f0` glow panes and a dashed glow reflection on the water below; markers `lamp_color` / `lamp_fixed` / `lamp_range`), `bollard`, `waystone` (glowing rune stone), `district_gate` (stone arch, barred oak doors, chain; no text).
- Added for Bifrost Crossing (`kit_bifrost.py`): `bifrost_plaza` (27 x 19.5 m chamfered flagstone deck, top y 0, a seven-band rainbow inlay, a kerb rim with a bridge gap, a tapering rock root with roots and cold-fire crystals), `bifrost_bridge` (2.8 x 5.6 m rainbow bridge of glow bands between stone kerbs, light dripping off the underside), `bifrost_landing` (8 x 4 m floating plank jetty, two cold-fire mooring lamps), `skiff_keel` (the cold-fire wake a floating skiff rides on), `realm_arch` (tall gloom-stone realm gate, jagged crown; `rift` marker + the prop's `glow` light it) with `realm_glow_<gold|green|violet|ice|amber|red|blue|rose|rainbow>` (its rune rim, keystone crystal, crown tips and sigil: glow pixels only, place at the same pos), `guild_kiosk` (Gatekeepers' Guild counter, ledger, key banner, cold-fire lamp), `rift_brazier_cold / _violet / _red` (jagged neon cone flames).
- `meshlib.py`: list-based mesh builder with UVs in metres and normals. glTF PBR uses metallic 0 / roughness 1 (no chrome), a nearest-mag + mipmapped-min sampler, and sRGB vertex colours (tint + contact AO).
- `kit.json`: sizes, collision blockers, markers (lamps, chimneys, windows, doors, stall vendor, ovens, spray, water).
- Scale: 1 unit = 1 m. A sprite is 1.8 m, doors are 2.0 m, storeys are 2.4-2.9 m.
- Glade pieces (`kit_glade.py`, for Mossglen):
  - `portal_arch`: a stone-arch gate of stacked mossy pillars and a voussoir ring with a keystone, on a plinth, with two little lanterns. Its `portal` marker sits in the opening, and the pillars are the only blockers, so you can walk through.
  - `shrine`: a small glade shrine: two stone steps, a timber hut with a thick shingle roof, an offering bowl, a candle lamp and moss.
  - `standing_stone`, `stone_lantern` (lamp marker), `mushroom_ring`, `fern_bush`.
