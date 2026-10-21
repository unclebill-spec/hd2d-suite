"""Goldspire / Reliquary foes: light wraiths, storm sentinels (lightning golems), storm-centaurs, Gilded Inquisitors; mini-boss Abbot Severin, gate foe
storm sentinel 2x, Captain Fridleif 3x (conquer), rares centaurchamp 2.5x + elderwraith 3x. Native scale, palette only (glow = fx + light)."""
from as_common import R
from as_giant import giant
from as_golem import golem
from as_beasts import wraith, centaur
from as_npcs import combine, hood, tabard, mace, lance, spear, shield

INQ = dict(skin="skin", hair=None, bald=True, hairstyle="none", tunic="cream", trousers="grey", belt=("timber_lo", "ink"), buckle="flower_gold",
           boots=("timber", "timber_lo"), extra=combine(tabard, hood(), mace), cheeks=False)
SEVERIN = dict(INQ, tunic="rust", width=1.1, extra=combine(tabard, hood("white"), mace))
FRID = dict(skin="skin", hair="timber_lo", hairstyle="short", tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), extra=combine(tabard, spear, shield), width=1.05)
CENT = dict(skin="skin", hair="timber", hairstyle="short", tunic="slate", trousers="slate", belt=("timber_lo", "ink"), buckle="flower_gold", extra=lance, cheeks=False)
CHAMP = dict(CENT, hair="plaster_hi", tunic="slate")

ENEM = {
 "light_wraith": dict(scale=1.2, W=1, desc="Light wraith (1.2x): a gold-white drifting shroud with a halo; no gore.", tier="enemy"),
 "storm_sentinel": dict(scale=1.8, G="storm", desc="Storm sentinel (1.8x): lightning golem of white stone + gold bands, a caged blue storm in the chest.", tier="enemy"),
 "storm_centaur": dict(scale=1.6, C=CENT, desc="Storm-centaur (1.6x, sky plains): bay horse body, a storm-blue belted tunic, gold lance.", tier="enemy"),
 "gilded_inquisitor": dict(scale=1.0, P=INQ, desc="Gilded Inquisitor (elite, 1x): hooded gold tabard over a cream tunic, belted, gold mask with red eyes, mace of light. No plate.", tier="elite"),
}
ELITE = {
 "severin": dict(scale=3.0, P=SEVERIN, desc="Abbot Severin (mini-boss, 3x, G5): hooded gold tabard over a wine tunic, belted, gold mask, mace of light. No plate.", tier="miniboss"),
 "storm_sentinel_gate": dict(scale=2.0, G="storm", desc="Storm sentinel, gate foe (2x): the same lightning golem, bigger.", tier="gate"),
 "fridleif_boss": dict(scale=3.0, P=FRID, desc="Captain Fridleif Thunderhelm (3x, conquer): leather jerkin + gilded tabard, spear and shield; yields at 25%. No plate.", tier="miniboss"),
 "centaurchamp": dict(scale=2.5, C=CHAMP, M=1, desc="Centaur champion (rare, 2.5x): white-maned centaur in a storm-blue belted tunic, lightning lance.", tier="rare"),
 "elderwraith": dict(scale=3.0, W=2, desc="Elder light wraith (rare, 3x): tall gold shroud with a cracked halo; drinks lamp light.", tier="rare"),
}


def Ht(s):
    return round(29 * s) - 2


def make(d, anims, kind="enemy"):
    out = {}
    for n, r in d.items():
        h = Ht(r["scale"])
        dr = (golem(r["G"], h) if r.get("G") else wraith(h, cracked=r["W"] == 2) if r.get("W") else centaur(h, r["C"], giant, mane=bool(r.get("M"))) if r.get("C") else giant(r["P"], h))
        out[n] = dict(draw=dr, scale=r["scale"], desc=r["desc"], anims=anims, kind=kind, enemy=True, stats_hint={"tier": r["tier"], "height_x_player": r["scale"]})
    return out
