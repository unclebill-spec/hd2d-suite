# hd2d particles

Pixel particle sheets + emitter presets.

```
hd2d particles --biome cozy-village --out PROJECT/public/art/particles
```

- 16 px cells, 4 frames per row.
- Presets:
  - Original: dust_motes, chimney_wisp, leaf_bits, lamp_bugs, lamp_flicker (a 4-frame dithered glow, not a blur halo).
  - Added: fireflies, petals, snowfall, rain, rain_splash, embers, oven_steam, pollen, fountain_spray, butterflies, footstep_dust.
- `particles.json` presets hold:
  - rate, life, velocity, gravity, sway, fps/mode, and `grade` gating (motes by day, bugs at dusk/night).
  - `weather` + `follow` + `y0`: snowfall and rain fall in a box that follows the camera and stop at the heightfield.
  - `on_floor`: rain spawns a `rain_splash` where a drop lands.
  - `manual` + `burst`: one-shot puffs that are never auto-emitted (rain_splash; footstep_dust, kicked up by the runtime on the player's walk frames 0 and 2).
  - `floor_rel`: fountain spray drops land on the basin water.
- The runtime draws particles as snapped pixel points in the sharp pass. The pool is capped at 600, and emitters pre-warm about 6 s so the air is already full on the first frame. They stay cheap.
- Scene use: `"emitters": [{"preset": "fireflies", "pos": [x, y, z], "area": [w, h, d]}]`. Weather: `"weather": "rain"|"snow"` in the scene spec, or `?weather=rain|snow` in the URL.
- Showcase: open a built scene with `?showcase=particles` to see every preset in a labelled grid. Actors are hidden and time gating is off.
- Also writes `lamp_flicker.png` (native strip) and `particles_preview_6x.png`.
- Readability pass (still cheap, still no bloom):
  - `rain_splash` is a jumping crown that spreads into a 2 px ring with a dark wet rim under it, so it reads on light cobbles as well as dark grass.
  - `footstep_dust` is a 4-puff, multi-tone plaster burst that lives about 0.6 s.
  - Both are hard-alpha pixel sprites with no glow.
