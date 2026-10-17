"""Cinderhold foes: ashen cultists, magma hounds, flame elementals, fire golems; rares ashalpha + pyreling, mini-boss Kilnmother. Native scale, palette only."""
from mp_common import R
from mp_giant import giant
from mp_golem import golem
from mp_beasts import hound, elemental
from mp_npcs import combine, hood, sash, veins

CULT = dict(skin="ember", hair=None, bald=True, hairstyle="none", tunic="ashgrey", trousers="black", belt=("roof_lo", "ink"), buckle="lamp",
            boots=("stone_lo", "ink"), trim="stone_lo", extra=combine(hood, sash), cheeks=False, hem=.09)

ENEM = {
 "ashen_cultist": dict(scale=1.0, P=CULT, desc="Ashen Cultist (elite, 1x): ash-grey hooded tunic, belted charcoal trousers, wide red sash, ember eyes. No plate.", tier="elite"),
 "magma_hound": dict(scale=1.4, H=1, desc="Magma hound (1.4x; gate foe at 2x): coal-black hound with glowing lava seams and ember eyes; pounces.", tier="enemy"),
 "flame_elemental": dict(scale=1.5, E=1, desc="Flame elemental (1.5x): a spinning column of flame with a white-hot core and a dark little face.", tier="enemy"),
 "fire_golem": dict(scale=2.0, G="fire", desc="Fire golem (2x, slow): stacked obsidian chunks with glowing lava seams; wakes from the furnace walls.", tier="enemy"),
}
ELITE = {
 "magma_hound_gate": dict(scale=2.0, H=1, desc="Magma hound, gate foe (2x): the Caldera mouth guard; same coal hide, bigger, pounces.", tier="gate"),
 "ashalpha": dict(scale=2.0, H=2, desc="Ash-alpha (rare, 2x): the magma hound pack leader with a glowing flame mane; calls 2 hounds.", tier="rare"),
 "pyreling": dict(scale=3.0, E=2, desc="Pyreling (rare, 3x): a flame elemental with a violet core; flicker-step and ember-burst.", tier="rare"),
 "kilnmother": dict(scale=3.0, G="kiln", desc="Kilnmother (mini-boss, 3x): fire golem of fused kiln brick and glass, leaking embers, throws a molten fist.", tier="miniboss"),
}


def Ht(s):
    return round(29 * s) - 2


def make(d, anims, kind="enemy"):
    out = {}
    for n, r in d.items():
        dr = golem(r["G"], Ht(r["scale"])) if r.get("G") else hound(Ht(r["scale"]), alpha=r["H"] == 2) if r.get("H") else elemental(Ht(r["scale"]), violet=r["E"] == 2) if r.get("E") else giant(r["P"], Ht(r["scale"]))
        out[n] = dict(draw=dr, scale=r["scale"], desc=r["desc"], anims=anims, kind=kind, enemy=True, stats_hint={"tier": r["tier"], "height_x_player": r["scale"]})
    return out


