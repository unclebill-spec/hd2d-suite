"""Niflheim bosses (boss_sheet layout, native big frames, palette only; neon glow is fx + light). Plate appears ONLY here.
 Veyra Ashmantle, the Rift-Warden: 4 phase roles + a mist-clone role. Rime-plate (ice-blue) over a violet-black long coat, crown of runes, frost-lantern.
   veyra_p1 (Mist, 5x) / veyra_p2 (Freeze, 5x, ice shards on the plate) / veyra_p3 (Warden, 6x, spiked plate, red grief-cracks) / veyra_p4 (Ask, 5x: plate pale and
   cracking, head bowed, lantern low and guttering, no attack; die = she dissolves into snow) / veyra_clone (mist clone: pale, dithered, NO breath-fog and NO shadow)
 Kael Frostfang (5.5x): black-iron plate, red-lined cape, frost-fang helm with red eyes; kael_p3 = plate frosted white.
 Glacier Colossus (6x): ice golem, hollow chest with the core (p1 hidden-ish, p2 exposed, p3 runes dim); golems are not plate."""
import math
import nf_common as C
from nf_common import R, hsh
from nf_giant import giant
from nf_golem import golem
from nf_npcs import combine

FRAME_VEYRA = (144, 200)
FRAME_KAEL = (144, 190)
FRAME_COLOSSUS = (144, 200)

RIME = ("sky", "flower_blue", "cloth", "shadow")            # hi, mid, lo, dark
IRON = ("stone", "stone_lo", "shadow", "ink")
FROST = ("white", "plaster_hi", "sky", "flower_blue")


def coat_tails(cv, c, col, line):
    """long coat: two back panels + two front flaps hanging below the plate to the calves (violet-black), lining colour on the inner edge"""
    CX, hip, Ht, hw, beltY, face = c["CX"], c["hip"], c["Ht"], c["hw"], c["beltY"], c["face"]
    G = c["G"]
    side, back = face == "left", face == "up"
    ylo = hip + Ht * .30
    for y in range(int(beltY), int(ylo)):
        t = (y - beltY) / max(1, ylo - beltY)
        for sd in ((-1, 1) if not side else (1, -1)):
            if side:
                x0, x1 = (CX - hw * .55 - t * 3, CX + hw * .5 + t * 4) if sd < 0 else (0, -1)
                if sd > 0:
                    continue
            else:
                gap = 0 if back else hw * .16
                x0, x1 = (CX + sd * (hw * (1.1 + .25 * t)), CX + sd * gap)
            a, b = (min(x0, x1), max(x0, x1))
            for x in range(int(a), int(b) + 1):
                u = (x - CX) / max(1, hw)
                cc = col[0] if (u < -.5) else col[2] if u > .55 else col[1]
                if not back and not side and abs(x - CX) <= gap + 1.5:
                    cc = line
                cv.set(x, y, cc)
        cv.set(CX - hw * (1.1 + .25 * t) if not side else CX - hw * .55 - t * 3, y, line if y % 3 == 0 else col[2])
    for x in range(int(CX - hw * 1.4), int(CX + hw * 1.4) + 1):
        if (x // 2) % 2 == 0:
            cv.set(x, ylo, "stone_lo")


def plate(S):
    """rime / iron plate with a configurable ramp, leak colour, spikes and cracks"""
    P = S["ramp"]; leak = S["leak"]; gem = S["gem"]
    def f(cv, c):
        CX, sh, hip, hw, Ht, k, face, beltY, G, hl = c["CX"], c["sh"], c["hip"], c["hw"], c["Ht"], c["k"], c["face"], c["beltY"], c["G"], c["i"]
        side, back = face == "left", face == "up"
        if S.get("coat"):
            coat_tails(cv, c, S["coat"], S["coat_line"])
        def shd(u):
            return P[2] if u < -.55 else P[3] if u > .55 else P[1]
        legs = [CX] if side else [CX - hw * .52, CX + hw * .52]
        for lx in legs:
            lw = c["legw"] * (.55 if not side else .6)
            for y in range(int(hip + Ht * .12), int(G - Ht * .02)):
                for x in range(int(lx - lw), int(lx + lw) + 1):
                    cv.set(x, y, shd((x - lx) / lw))
            ky = hip + Ht * .17
            cv.ell(lx, ky, lw * 1.1, Ht * .035, lambda u, v: P[0] if v < -.2 else P[2])
            for y in range(int(hip + Ht * .26), int(G - Ht * .06), int(max(4, Ht * .06))):
                cv.rect(lx - lw, y, lx + lw, y, leak if y % 2 == 0 else P[1])
        x0, x1 = CX - hw * 1.02, CX + hw * 1.02
        top, bot = sh + 2, beltY - 1
        for y in range(int(top), int(bot) + 1):
            t = (y - top) / max(1, bot - top)
            ins = (0 if t < .6 else (t - .6) * hw * .25)
            for x in range(int(x0 + ins), int(x1 - ins) + 1):
                u = (x - CX) / hw
                col = shd(u)
                if abs(u) < .06 and not side:
                    col = P[3]
                cv.set(x, y, col)
        step = int(max(5, Ht * .07))
        for y in range(int(top) + step, int(bot), step):
            cv.rect(x0 + 1, y, x1 - 1, y, P[1] if y % 2 == 0 else P[2])
            for x in range(int(x0 + 3), int(x1 - 2), int(max(4, Ht * .05))):
                cv.set(x, y - 1, leak)
        if not back and not side:
            cx_, cy_ = CX, top + (bot - top) * .38
            r = Ht * .06
            cv.poly([(cx_, cy_ - r), (cx_ + r, cy_), (cx_, cy_ + r), (cx_ - r, cy_)], lambda x, y: "white" if abs(x - cx_) + abs(y - cy_) < r * .45 else gem)
        for j in range(3):                                        # fauld
            y0 = beltY + 1 + j * Ht * .045
            w_ = hw * (1.05 + j * .12)
            for y in range(int(y0), int(y0 + Ht * .05)):
                for x in range(int(CX - w_), int(CX + w_) + 1):
                    cv.set(x, y, shd((x - CX) / w_) if y > y0 else P[0])
            for x in range(int(CX - w_) + 2, int(CX + w_) - 1, int(max(5, Ht * .06))):
                cv.set(x, y0 + Ht * .05, leak)
        for sd in ((-1, 1) if not side else (0,)):                # pauldrons + spikes
            px_ = CX + sd * hw
            for j in range(3):
                cv.ell(px_, sh + 2 + j * Ht * .04, Ht * (.115 - j * .008) * (1 if not side else .8), Ht * .06, lambda u, v: P[1] if (u < -.3 and v < 0) else P[2] if u < .5 else P[3])
            sp = px_ + sd * Ht * .06 if sd else px_ - Ht * .02
            sl = Ht * (.12 if not S.get("spikes") else .20)
            cv.poly([(sp - 3, sh - 2), (sp + 3, sh - 2), (sp + (sd or -1) * 2, sh - sl)], lambda x, y: P[0] if x < sp else P[2])
            if S.get("spikes"):
                sp2 = px_ + sd * Ht * .14 if sd else px_ - Ht * .08
                cv.poly([(sp2 - 2, sh + 3), (sp2 + 2, sh + 3), (sp2 + (sd or -1) * 5, sh - Ht * .08)], lambda x, y: P[1])
            cv.set(px_ + (sd or 0), sh + 4, leak)
            if S.get("shards"):
                for j in range(2):
                    cv.poly([(px_ + sd * (Ht * .12 + j * 5) - 1, sh + 2), (px_ + sd * (Ht * .12 + j * 5) + 1, sh + 2), (px_ + sd * (Ht * .15 + j * 5), sh - Ht * (.07 + .03 * j))], "white")
        cv.ell(CX, sh, hw * .55, Ht * .03, lambda u, v: P[1] if v < 0 else P[2])
        for hx, hy in c["hands"]:
            cv.ell(hx, hy, Ht * .05, Ht * .06, lambda u, v: P[1] if (u < -.3 and v < 0) else P[2] if u < .5 else P[3])
            cv.rect(hx - Ht * .045, hy - Ht * .055, hx + Ht * .045, hy - Ht * .05, leak)
        if S.get("cracks") and not back:                          # red grief-cracks on the plate (weak points)
            cx_ = CX
            for (ax, ay, bx, by) in ((-.45, .12, -.15, .5), (.4, .2, .1, .6), (-.1, .55, .3, .9)):
                n = 12
                for j in range(n + 1):
                    t = j / n
                    cv.set(CX + hw * (ax + (bx - ax) * t) + (1 if j % 3 == 1 else 0), top + (bot - top) * (ay + (by - ay) * t), "roof_hi" if j % 4 else "flower_rose")
    return f


def cape(inner, outer):
    """Kael's red-lined cape: drawn only where nothing else is (flanks + behind); lining colour inside"""
    def f(cv, c):
        CX, sh, Ht, hw, face, G = c["CX"], c["sh"], c["Ht"], c["hw"], c["face"], c["G"]
        side, back = face == "left", face == "up"
        i = c["i"]
        for y in range(int(sh), int(G - Ht * .06)):
            t = (y - sh) / max(1, (G - Ht * .06) - sh)
            wdt = hw * (1.25 + .55 * t) * (1 if not side else .75)
            sway = math.sin(i * .9 + t * 4) * 1.5 * t
            xa, xb = CX - wdt + sway, CX + wdt + sway
            if side:
                xa, xb = CX + 2, CX + wdt * 1.1 + sway
            for x in range(int(xa), int(xb) + 1):
                if cv.get(x, y) is None:
                    u = (x - CX) / max(1, wdt)
                    if back:
                        cv.set(x, y, outer[0] if u < -.5 else outer[2] if u > .5 else outer[1])
                    else:
                        cv.set(x, y, inner[1] if abs(u) > .8 or (x + y) % 5 else inner[2])
        for x in range(int(CX - hw * 1.8), int(CX + hw * 1.8) + 1):                  # ragged hem
            if cv.get(x, G - Ht * .06) is None and (x // 2) % 2 == 0:
                cv.set(x, G - Ht * .06, inner[2])
    return f


def fang_helm(frost=False):
    """Kael's frost-fang helm: iron dome, brow ridge, two fangs, red eye slits"""
    P = FROST if frost else IRON
    def f(cv, c):
        hcx, hcy, hh, hhw, side, back, Ht = c["hcx"], c["hcy"], c["hh"], c["hhw"], c["side"], c["back"], c["Ht"]
        cv.ell(hcx, hcy - hh * .1, hhw * 1.14, hh * 1.08, lambda u, v: P[0] if (u < -.4 and v < -.1) else P[2] if (u > .5 or v > .75) else P[1])
        for dy in (-.45, 0.0):
            cv.rect(hcx - hhw * 1.1, hcy + hh * dy, hcx + hhw * 1.1, hcy + hh * dy, P[3])
        if not back:
            ex = hhw * .42
            exs = [hcx - hhw * .5] if side else [hcx - ex, hcx + ex]
            for e in exs:
                cv.rect(e - 2, hcy + hh * .05, e + 2, hcy + hh * .15, "ink"); cv.rect(e - 1, hcy + hh * .06, e + 1, hcy + hh * .12, "roof_hi")
            for sd in ((-1, 1) if not side else (-1,)):
                fx = hcx + sd * hhw * (.55 if not side else .1) - (hhw * .5 if side else 0)
                cv.poly([(fx - 2, hcy + hh * .5), (fx + 2, hcy + hh * .5), (fx, hcy + hh * 1.05 + Ht * .02)], "white")
        for sd in (-1, 1):                                   # swept horn-crest
            cv.poly([(hcx + sd * hhw * .4 - 2, hcy - hh * .9), (hcx + sd * hhw * .4 + 2, hcy - hh * .9), (hcx + sd * hhw * .8, hcy - hh * 1.6)], P[1])
    return f


def crown(phase):
    """Veyra's crown of glowing runes: a rime band + rune-spikes (palette sky / white; the glow is fx)"""
    def f(cv, c):
        hcx, hcy, hh, hhw, side, back, Ht, i = c["hcx"], c["hcy"], c["hh"], c["hhw"], c["side"], c["back"], c["Ht"], c["i"]
        y = hcy - hh * .66
        cv.rect(hcx - hhw * .95, y, hcx + hhw * .95, y + max(1, Ht * .018), "flower_blue")
        cv.rect(hcx - hhw * .95, y - 1, hcx + hhw * .95, y - 1, "sky")
        n = {1: 5, 2: 5, 3: 7, 4: 3}[phase]
        for j in range(n):
            x = hcx + (j - (n - 1) / 2) * hhw * (.38 if n > 5 else .45)
            h = Ht * (.10 + .06 * (1 - abs(j - (n - 1) / 2) / max(1, n / 2))) * (1.25 if phase == 3 else 1.0 if phase != 4 else .7)
            cv.poly([(x - 2, y - 1), (x + 2, y - 1), (x, y - h)], lambda a, b: "sky" if a < x else "flower_blue")
            cv.set(x, y - h * .5, "white" if (phase != 4 or (i + j) % 2 == 0) else "flower_blue")
        if not back:
            ey = hcy + hh * .05
            for ex in ([hcx - hhw * .5] if side else [hcx - hhw * .42, hcx + hhw * .42]):
                cv.set(ex, ey + 1, "shadow")                 # tired shadows under the eyes
                if phase == 3:
                    cv.set(ex, ey, "roof_hi")                 # grief-red eyes
    return f


def lantern(phase):
    """frost-lantern in the left hand (cold-fire core white / sky; phase 4: low and guttering)"""
    def f(cv, c):
        hx, hy = c["hand_back"] if not c["side"] else c["hand"]
        Ht, i = c["Ht"], c["i"]
        drop = Ht * (.10 if phase == 4 else 0)
        cx, cy = hx - (Ht * .03 if not c["side"] else 0), hy + Ht * .06 + drop
        cv.seg(cx, hy + 1, cx, cy - Ht * .04, 1.5, 1.5, ("stone_hi", "stone", "stone_lo"))
        w, h = Ht * .045, Ht * .065
        cv.rect(cx - w, cy - h, cx + w, cy + h, "stone_lo")
        cv.rect(cx - w + 1, cy - h + 1, cx + w - 1, cy + h - 1, "sky" if (phase != 4 or i % 2 == 0) else "flower_blue")
        cv.rect(cx - 1, cy - h * .5, cx + 1, cy + h * .4, "white" if (phase != 4 or i % 2 == 0) else "sky")
        cv.rect(cx - w - 1, cy - h - 1, cx + w + 1, cy - h - 1, "stone"); cv.rect(cx - w - 1, cy + h + 1, cx + w + 1, cy + h + 1, "stone")
    return f


def veyra_P(phase):
    S = dict(ramp=RIME, leak="white", gem="sky", coat=("cloth", "shadow", "ink"), coat_line="flower_blue")
    if phase == 2:
        S["shards"] = True
    if phase == 3:
        S.update(spikes=True, cracks=True)
    if phase == 4:
        S.update(ramp=("plaster_hi", "sky", "flower_blue", "cloth"), leak="sky", cracks=True)
    return dict(skin="pale", hair=("stone", "stone_lo", "shadow"), hairstyle="long", tunic="cream", trousers="coat", belt=("stone_lo", "ink"), buckle="sky",
                width=1.0, head=1.0, plate=plate(S), extra=combine(crown(phase), lantern(phase)), raise_=1.2, brow="shadow", trim="stone_lo", cheeks=False, hem=.08,
                legs_w=1.05, arms_w=1.05)


def clone_of(draw):
    """mist clone: the same figure, drained to a pale mist ramp and dithered; no ground shadow, no breath (those two are the tell)"""
    PALE = {"sky": "plaster_hi", "flower_blue": "sky", "cloth": "sky", "shadow": "flower_blue", "ink": "flower_blue", "stone_lo": "sky", "stone": "plaster_hi",
            "stone_hi": "white", "skin": "plaster_hi", "skin_lo": "sky", "timber_hi": "sky", "timber": "flower_blue", "timber_lo": "flower_blue", "plaster": "plaster_hi",
            "plaster_lo": "sky", "flower_gold": "white", "roof_hi": "sky", "roof": "flower_blue", "roof_lo": "flower_blue"}
    PAL = C.H.PAL
    def d2(cv, face, anim, i):
        draw(cv, face, anim, i)
        p = cv.s.p
        for y in range(len(p)):
            for x in range(len(p[0])):
                c = p[y][x]
                if c is None:
                    continue
                nm = PAL.name_of(c)
                new = PALE.get(nm, nm)
                if y > len(p) * .52 and (x + y + i) % 2 == 0:
                    new = "white" if new != "white" else "plaster_hi"          # colour dither (hard alpha): the mist-clone fades toward the hem
                cv.s.set(x, y, new)
    d2.fall = True
    return d2


def veyra_roles():
    base = dict(enemy=True, kind="enemy", boss=True)
    def mk(phase, scale, anims, desc, light):
        return dict(draw=giant(veyra_P(phase), round(29 * scale) - 2), scale=scale, anims=anims, desc=desc, light=light,
                    stats_hint={"tier": "boss", "height_x_player": scale, "plate": True, "element": "ice", "phase": phase, "dungeon": "The Crown of Ice"}, **base)
    out = {
        "veyra_p1": mk(1, 5.0, ("idle", "walk", "cast", "attack"), "Veyra Ashmantle, Rift-Warden, phase 1 MIST (5x, rime-plate = boss plate): violet-black long coat under ice-blue rime-armour, crown of runes, frost-lantern. Real Veyra: breath-fog fx + shadow decal (the tell).", {"color": "#3fb8ff", "intensity": 1.4, "range": 9.0}),
        "veyra_p2": mk(2, 5.0, ("idle", "walk", "cast", "attack"), "Veyra phase 2 FREEZE (5x): ice shards grow off the pauldrons; she freezes the four portals.", {"color": "#7fd4ff", "intensity": 1.5, "range": 9.5}),
        "veyra_p3": mk(3, 6.0, ("idle", "walk", "cast", "attack"), "Veyra phase 3 WARDEN (6x): the plate grows spikes, red grief-cracks open on the weak points, red eyes; cold-fire beam (red ring telegraph).", {"color": "#a45cf0", "intensity": 1.7, "range": 11.0}),
        "veyra_p4": mk(4, 5.0, ("idle", "walk", "die"), "Veyra phase 4 ASK (5x): she stops attacking; plate pale and cracking, head bowed, lantern low and guttering. die = she dissolves into snow (Ending B) -- Ending A reuses idle.", {"color": "#d4a8ff", "intensity": 1.0, "range": 8.0}),
    }
    out["veyra_clone"] = dict(draw=clone_of(giant(veyra_P(1), round(29 * 5.0) - 2)), scale=5.0, anims=("idle", "walk", "cast", "attack"),
                              desc="Veyra mist clone (P1, x3): the P1 figure drained pale and dithered, NO breath-fog and NO shadow (the real one has both); Hrefna rings it violet.", enemy=True, kind="enemy",
                              stats_hint={"tier": "boss_add", "height_x_player": 5.0, "element": "ice"})
    return out


def kael_P(p3):
    S = dict(ramp=FROST if p3 else IRON, leak="roof_hi", gem="roof_hi", coat=None)
    return dict(skin="pale", hair=None, bald=True, hairstyle="none", tunic="coat", trousers="coat", belt=("roof_lo", "ink"), buckle="roof_hi",
                width=1.04, head=1.0, plate=plate(S), extra=combine(cape(("roof_hi", "roof", "roof_lo"), ("shadow", "ink", "ink")), fang_helm(p3), kael_blade), raise_=1.2,
                brow="shadow", trim="stone_lo", cheeks=False, hem=.08, legs_w=1.1, arms_w=1.15)


def kael_blade(cv, c):
    """Kael's long black blade with a frost edge; swept in blue arcs on the attack"""
    hx, hy = c["hand"]
    Ht, at, side = c["Ht"], c["at"], c["side"]
    x0, y0 = hx + (3 if not side else -1), hy + 2
    ln = Ht * (.46 + .1 * at)
    x1, y1 = x0 + (Ht * .03 if not side else -Ht * .12) * at, y0 - ln
    n = int(ln)
    for j in range(n):
        t = j / n
        x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
        w = Ht * .028 if j > 5 else Ht * .01
        for dx in range(-int(w), int(w) + 1):
            cv.set(x + dx, y, "stone" if dx < -w * .4 else "shadow" if dx > w * .4 else "stone_lo")
        cv.set(x - int(w) - 1, y, "white" if j % 3 else "sky")
    cv.rect(x0 - Ht * .05, y0 - 5, x0 + Ht * .05, y0 - 3, "shadow")


def kael_roles():
    base = dict(enemy=True, kind="enemy", boss=True, anims=("idle", "walk", "cast", "attack", "die"))
    def mk(p3, desc, light):
        return dict(draw=giant(kael_P(p3), round(29 * 5.5) - 2), scale=5.5, desc=desc, light=light,
                    stats_hint={"tier": "boss", "height_x_player": 5.5, "plate": True, "element": "ice", "dungeon": "The Frozen Spire F9"}, **base)
    out = {"kael": mk(False, "Kael Frostfang (boss, 5.5x, frost vampire; black-iron plate = boss plate): red-lined cape, frost-fang helm with red eyes, long black blade. Drains warmth, not blood. die = he crumbles to snow and cape.", {"color": "#e8321e", "intensity": 1.0, "range": 8.0}),
           "kael_p3": mk(True, "Kael phase 3 (25%): plate frosted white, red banners burn (fx), calls 2 Ice Wardens.", {"color": "#e8321e", "intensity": 1.4, "range": 9.0})}
    for r in out.values():
        r["draw"].fall = True
        r["draw"] = with_sink(r["draw"])
    return out


def with_sink(draw):
    def d(cv, face, anim, i):
        draw(cv, face, anim, i)
    d.fall = True
    d.die_mode = "sink"
    d.sink_cols = ("white", "plaster_hi", "sky", "flower_blue")
    return d


def squeeze(draw, f):
    """draw on a wider scratch canvas, then squeeze columns by f into the real frame (keeps the 144 px boss-frame width cap)"""
    def d(cv, face, anim, i):
        W = int(cv.w / f) + 8
        tmp = C.Cv(C.SP.HSprite(C.H.PAL, W, cv.h))
        draw(tmp, face, anim, i)
        p = tmp.s.p
        for y in range(cv.h):
            for x in range(W):
                if p[y][x] is not None:
                    nx = int(round(cv.w / 2 + (x - W / 2) * f))
                    if 1 <= nx < cv.w - 1:
                        cv.s.p[y][nx] = p[y][x]
    d.fall = False
    return d


def colossus_roles():
    out = {}
    for n, kind, desc in (("colossus", "colossus1", "Glacier Colossus (boss, 6x, Spire F5): stacked glacier blocks, a hollow chest with the cold-fire core, glowing frost runes on the shoulders. Golems are not plate. P1."),
                          ("colossus_p2", "colossus2", "Colossus phase 2 (60%): the core is exposed (bigger, white-hot) - hit it; summons 2 ice golems."),
                          ("colossus_p3", "colossus3", "Colossus phase 3 (25%): the runes dim and go dark; frost spirits swarm (fx).")):
        out[n] = dict(draw=squeeze(golem(kind, round(29 * 6.0) - 2), .80), scale=6.0, anims=("idle", "walk", "attack", "die"), desc=desc, enemy=True, boss=True, kind="enemy",
                      light={"color": "#3fb8ff", "intensity": 1.2, "range": 8.0}, stats_hint={"tier": "boss", "height_x_player": 6.0, "element": "ice", "golem": True, "dungeon": "The Frozen Spire F5"})
    return out
