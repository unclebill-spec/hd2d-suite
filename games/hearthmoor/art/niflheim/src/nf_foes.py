"""Niflheim foes: frost spirits, mist stalkers, ice golems, frost wraiths, ice wardens; rares mistalpha + spiritprime, mini-boss Brisa, Kael's bat forms. Native scale, palette only."""
from nf_common import R
from nf_giant import giant
from nf_golem import golem
from nf_beasts import hound, elemental, wraith, bat
from nf_npcs import combine, hood, icelance, frostshield, iceblades

WARDEN = dict(skin="pale", hair=None, bald=True, hairstyle="none", tunic="slate", jerkin="grey", trousers="grey", belt=("stone_lo", "ink"), buckle="sky",
              boots=("stone_lo", "ink"), trim="stone_lo", extra=combine(hood, icelance, frostshield), cheeks=False, hem=.09)
BRISA = dict(skin="pale", hair="timber_lo", hairstyle="braids", tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), buckle="sky",
             extra=combine(frostshield, iceblades), cheeks=False, width=1.1)

ENEM = {
 "frost_spirit": dict(scale=1.2, E=1, desc="Frost spirit (1.2x): a blue-white flame spirit with a dark core; ice bolt.", tier="enemy"),
 "mist_stalker": dict(scale=1.5, H=1, desc="Mist stalker (1.5x): a lithe pale cat-shape with frost seams; pounces out of the mist.", tier="enemy"),
 "ice_golem": dict(scale=1.8, G="ice", desc="Ice golem (1.8x, slow): stacked glacier ice, sky cracks; slam + ice-block throw.", tier="enemy"),
 "frost_wraith": dict(scale=1.4, W=1, desc="Frost wraith (1.4x): a drifting blue-white shroud with two glowing eyes; chill touch.", tier="enemy"),
 "ice_warden": dict(scale=1.0, P=WARDEN, desc="Ice Warden (elite, 1x): grey-blue hooded tunic, grey jerkin, belted trousers, ice lance + shield-bash. No plate.", tier="elite"),
}
ELITE = {
 "brisa_mini": dict(scale=3.0, P=BRISA, desc="Rimewarden Brisa Rimeheart (mini-boss, 3x; conquer-only): leather jerkin over a belted tunic, frost shield + two ice blades. No plate.", tier="miniboss"),
 "mistalpha": dict(scale=2.0, H=2, desc="Mist-alpha (rare, 2x): a pale mist-stalker with a mist mane; calls 2 stalkers (violet mist halo = fx).", tier="rare"),
 "spiritprime": dict(scale=3.0, E=3, desc="Spirit prime (rare, 3x): a tall blue flame column inside a ring of glowing runes; rune burst.", tier="rare"),
 "kael_bat": dict(scale=2.0, B=1, desc="Kael bat form (2x): one of Kael's three bat-shaped mist forms (phase 2); splits and returns.", tier="boss_add"),
}


def Ht(s):
    return round(29 * s) - 2


def make(d, anims, kind="enemy"):
    out = {}
    for n, r in d.items():
        h = Ht(r["scale"])
        dr = (golem(r["G"], h) if r.get("G") else hound(h, alpha=r["H"] == 2) if r.get("H") else
              elemental(h, violet=False, ring=r["E"] == 3) if r.get("E") else wraith(h) if r.get("W") else bat(h) if r.get("B") else giant(r["P"], h))
        out[n] = dict(draw=dr, scale=r["scale"], desc=r["desc"], anims=anims, kind=kind, enemy=True, stats_hint={"tier": r["tier"], "height_x_player": r["scale"]})
    return out
