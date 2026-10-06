# HD-2D Cozy: style lock

This is Bill's standing art law for every hd2d-suite title. It takes its craft cues from Octopath, but uses none of its assets.
It is copied from the builder agent's law file. Where this file and a prompt disagree on camera, world or lighting, **this file wins**.

The references are HD-2D town and field screenshots (diorama cottages, cobble plazas, tilt-shift, pixel billboard actors). Learn the **rules** from them. **Never copy Square Enix characters, jobs, logos, HUD, "Sacred Flame", or maps.**

## Goal

Cozy games that look like a Super Famicom sprite dropped into a lit miniature.
- **World:** 3D (or fake-3D painted planes) with depth.
- **Actors:** 2D pixel billboards, nearest-neighbour, always facing a locked camera.
- **Quality:** light, depth and readable pixels. Not extra texels, and not Unreal photoreal.

Sprites always use nearest-neighbour scaling. Never bilinear-filter the characters.

## 1. Style lock (paste into every art / scene prompt)

- **Camera:** locked 3/4 high angle with slight tilt-shift, like a diorama or toy town. No free fly-cam, no first-person, no side-view beat-'em-up.
- **Actors:** 16-bit pixel billboards, about 16–24 px wide and 24–40 px tall. Nearest-neighbour only, 1 px outline, chunky silhouette, big readable head.
- **World:** 3D block-out or stacked painted planes with **real height** (stairs, terraces, roofs you can walk behind). Voxel-chunk houses are fine.
- **World materials:** painted or texel-snapped, not PBR chrome. Brick, timber, thatch and cobble should read as miniatures.
- **Light:** one key sun plus local lamps. Characters **cast shadows** on the ground. Warm gold day, cool blue dusk, orange windows at night.
- **Depth:** mild tilt-shift / depth of field (soft foreground and far hills) and volume haze in valleys. Not cinematic anamorphic blur.
- **Particles:** dust motes, chimney wisps, leaf bits, lamp bugs. Keep them cheap.
- **Palette per biome:** 16–28 colours. For cozy: cream plaster, timber, moss, flower spots.
- **Forbidden:**
  - photoreal skin, Unreal Megascans lawns, a flat Stardew-style 16×16 world;
  - copying Octopath travelers, towns or UI; logos; readable copyrighted text;
  - full-screen bloom, TAA smear on sprites, a 3D skinned player mesh.

## 2. What the reference pictures teach (rules only)

- Houses sit on terraces with stairs, and roofs have thickness.
- Cobble and timber have a chunky texel, then the **camera** makes them lush.
- Trees are layered cards or low-poly canopies, not 16×16 stamps.
- NPCs are small pixel dolls on the plaza. They don't scale with perspective the way a 3D mesh would; they stay billboard-sharp.
- The foreground wall or hedge is slightly soft (tilt-shift), and the focus band is the plaza.
- Market stalls, barrels, hanging signs and flower crates add density, not clutter spam.
- Don't copy named travelers, job icons, the turn-battle HUD, "Sacred Flame" copy, or the exact Timberain / Atlasdam / Clockbank layouts.

## 3. Two pipelines in one frame

**A. Sprites** (characters, items in hand, some props): native pixel art, nearest-neighbour, snapped to whole pixels on the billboard. Idle 4 frames, walk 4 frames, 4 facings for a fixed camera.

**B. World** (terrain, buildings, sky): 3D or pre-rendered 3D. It can use mipmaps, depth of field and haze. Prefer texel snap / posterize so it still feels pixel-adjacent. Stairs and rails must match the sprite scale (a sprite is about 1.6–2.0 m in world units).

Never run a sprite through the world's blur shader. Never flatten the world to a 16×16 look.

## 4. Cozy (mood law)

Warm hearths, market bunting, laundry, cats, pie steam, golden hour. Conflict can exist, but the default town is kind. No grimdark sludge unless asked for (for example a night dungeon).
The HUD is parchment or carved wood, never Octopath's exact chrome.

## 5. How to build a scene

1. Block the plaza in 3D: ground, 3 houses, 1 stair, 1 tree.
2. Lock the camera and add tilt-shift so only the walk band is sharp.
3. Place 2–4 pixel billboard actors at sprite scale.
4. Add one key light and 2 window lamps.
5. Do a prop pass (barrel, crate, flower, sign), then stop.
6. Screenshot test: if the sprites look smeared, the depth of field is too strong. If the town looks flat like Stardew, add height.

## 6. Game Layout One

The Layout One pad (stick, MAIN, potions, rail) may be used. Layout One's Stardew pixel lock does **not** apply to the world or camera of an HD-2D title. Gravewake's Layout Two is a different title unless Bill binds it.

## 7. Reject

- "Cozy Stardew but 3D"
- Photoreal cottages with a pixel sticker on top
- A copied Octopath party
- Soft-filtered sprites
- Mobile bloom soup

## 8. Overrides from Bill

- **Boss scale (2026-10-03):** the one-sprite-scale rule covers heroes, NPCs and ordinary enemies only. Bosses are drawn at least 5x the player's height; mini-bosses and rares at 2-3x (aim ~2.5x). Draw them at that size natively (more pixels, same texel density, nearest-neighbour); never upscale a small sprite. Hitboxes, shadows, attack reach and camera framing scale with them.
- **Clothing (2026-10-04):** character sprites must never read as onesies, diapers, padded suits or armour-like body suits. Draw normal clothing: a separate top and bottom (shirt / tunic / coat + trousers / skirt) in clearly different colours or values, a 1 px darker waist band between them (belt, sash), trousers with a visible leg split, and shoes in a colour distinct from the trousers. Robes stop at the hip / thigh as tunics; plate is an accent (one pauldron, bracers), never the body. Bosses and overlords may wear real armour plates; townsfolk and heroes wear clothes. (`tools/sprite`: every non-skirt human gets a belt row; `belt`, `sash`, `belt_w`, `tunic`, `collar`, `suspenders`, `tabard` and a skirt `belt` shape it.)

- **Neon pets (2026-10-05):** Bill approved neon pets. The Den pets' sprite sheet (`games/hearthmoor/art/pets/pets.png`: wisp-kit, glowmoth, lantern fox, moss-pup) may use the NEON blue / violet / red / lime ramps on their glowing parts. It is a scoped exception: `check-sprite`'s `NEON_PETS_ALLOW` covers only the `pet_*` roles, and everything else stays palette-locked.

- **Neon green + pink for effects and orbs (2026-10-06):** Bill allowed neon green `#3cf08a` (`#b8ffd4` / `#14a85a`) and neon pink `#ff4fc8` (`#ffb4ea` / `#b82a8c`) from the 2026-10 art packs (verdant_heart, orb_lanterns) **for effects and orbs only**: spell / particle / gamefx pixels and glow-orb pieces (`orb_*`, `glow_orb*`). Characters, creatures, props, world and HUD stay palette-locked. `games/hearthmoor/tests/check_palette.py` enforces it.

Applying the rules (not a new override): Bifrost Crossing's nine realm colours keep the neon-accent rule. Only Alfheim violet, Niflheim neon blue and Muspelheim red are NEON, along with the cold fire. Asgard gold, Vanaheim green, Jotunheim ice, Svartalfheim copper, Helheim rose and Midgard's rainbow use biome-palette tones on the self-lit glow material. Their light reaches the scene through the pooled point lights (the glow-light cap) and decals, never bloom.

## How this repo enforces it

- `hd2d check-sprite`: alpha is 0/255 only, palette-locked colours, a 1 px outline, every frame present.
- `hd2d check-scene`, which checks:
  - sprites are sharp k×k blocks that match the atlas;
  - the camera is locked;
  - there is no bloom;
  - there is real height;
  - the day / dusk / night grades;
  - effects stay sharp;
  - the phone layout and input.
