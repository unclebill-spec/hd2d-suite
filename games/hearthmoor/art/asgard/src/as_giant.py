"""Parametric giant humanoid (front / back / side), drawn natively at game scale. Used for the Stonehollow townsfolk, Ulfar,
frost trolls, berserkers and (with plate=True) Hrimgard. Real clothes: wool tunic + belt + belted trousers + boots (+ fur mantle);
no onesies, no padded suits. Figure height Ht = round(29*scale) px (the hero's visible height is 29)."""
import math
from as_common import Cv, R, shade, hsh

DEF = dict(skin="skin", hair="timber", hairstyle="braids", beard=None, beard_c=None, tunic="slate", trim="plaster_lo", trousers="grey",
           boots=("timber", "timber_lo"), belt=("timber_lo", "ink"), buckle="flower_gold", mantle=None, apron=None, jerkin=None, skirt=None,
           width=1.0, hunch=0.0, head=1.14, brow="shadow", eyes="ink", extra=None, hand=None, tusks=False, bald=False, plate=None,
           legs_w=1.0, arms_w=1.0, cheeks=True, raise_=1.0, sleeves="tunic", hem=0.09)


def idle_pose(anim, i, k):
    """(bob, blink, stride, lift_l, lift_r, swing, atk, cast)"""
    b = bl = st = ll = lr = sw = 0
    at = ca = 0.0
    if anim == "idle":
        b = [0, 1, 1, 0][i] * max(1, round(k * .7)); bl = 1 if i == 3 else 0
    elif anim in ("walk", "follow"):
        t = i
        b = [0, -1, 0, -1][t] * max(1, round(k * .8))
        st = [1, 0, -1, 0][t]
        ll = [0, 1, 0, 0][t]; lr = [0, 0, 0, 1][t]
        sw = [1, 0, -1, 0][t]
    elif anim == "attack":
        at = [0.0, 0.5, 1.0, 0.7][i]; b = [0, -1, 1, 0][i]
    elif anim == "cast":
        ca = [0.0, 0.6, 1.0, 0.6][i]; b = [0, -1, -1, 0][i]
    elif anim == "die":
        b = 0
    return b, bl, st, ll, lr, sw, at, ca


def giant(P, ht):
    P = {**DEF, **P}
    def draw(cv, face, anim, i):
        G = cv.h - 2
        CX = cv.w // 2
        Ht = ht
        k = Ht / 29.0
        W = P["width"]
        b, bl, st, ll, lr, sw, at, ca = idle_pose(anim, i, k)
        if anim == "die":
            at = 0
        sk = R[P["skin"]] if isinstance(P["skin"], str) else P["skin"]
        tu = R[P["tunic"]] if isinstance(P["tunic"], str) else P["tunic"]
        tr = R[P["trousers"]] if isinstance(P["trousers"], str) else P["trousers"]
        hair = R[P["hair"]] if isinstance(P["hair"], str) and P["hair"] in R else (P["hair"] if P["hair"] else None)
        if isinstance(hair, str):
            hair = ("timber_hi", hair, "timber_lo")
        leg_len = Ht * 0.43
        hip = G - leg_len
        torso_h = Ht * 0.29 * (1 - P["hunch"] * 0.15)
        sh = hip - torso_h + b + P["hunch"] * k * 2
        hw = Ht * 0.17 * W * (0.62 if face == "left" else 1.0)         # torso half width
        hhw = Ht * 0.135 * P["head"] * (0.9 if face == "left" else 1.0)
        hh = Ht * 0.135 * P["head"] * 1.02
        hcy = sh - hh * 0.85 + P["hunch"] * k
        hcx = CX + (-P["hunch"] * k * 2 if face == "left" else 0)
        legw = Ht * 0.105 * P["legs_w"]
        armw = Ht * 0.085 * P["arms_w"]
        bs, bl_ = P["boots"]
        bootR = (bs, bs, bl_)
        side = face == "left"
        back = face == "up"
        beltY = hip - Ht * 0.02 + b
        # ------------------------------------------------ legs + boots
        def leg(x_hip, x_foot, lift, far=False):
            yf = G - lift * 2
            rm = tr
            if far:
                rm = (tr[1], tr[2], tr[2])
            cv.seg(x_hip, hip + b, x_foot, yf - Ht * 0.12, legw, legw * 0.95, rm)
            # trouser belt-tuck / ankle wrap
            cv.seg(x_foot, yf - Ht * 0.15, x_foot, yf - Ht * 0.10, legw * 0.9, legw * 0.9, (P["trim"], P["trim"], tr[2]))
            # boot
            bh = Ht * 0.11
            fw = legw * (0.7 if not side else 1.05)
            fx = x_foot + (-fw * (0.35 if side else 0) if True else 0)
            cv.rect(x_foot - legw * .55, yf - bh, x_foot + legw * .55, yf, bs if not far else bl_)
            cv.rect(x_foot - legw * .55, yf - bh, x_foot - legw * .55 + 1, yf, R["leather"][0] if not far else bl_)
            cv.rect(x_foot - legw * .55, yf - 1, x_foot + legw * .55, yf, bl_)           # sole
            if side:
                cv.rect(x_foot - legw * 1.1, yf - bh * .55, x_foot - legw * .3, yf, bs if not far else bl_)   # toe
                cv.rect(x_foot - legw * 1.1, yf - 1, x_foot - legw * .3, yf, bl_)
            cv.rect(x_foot - legw * .55, yf - bh, x_foot + legw * .55, yf - bh + 0, P["trim"])  # cuff line
        if side:
            s_ = st * Ht * 0.09
            o = legw * .26
            leg(CX + 1 + o + s_ * -1, CX + o + s_ * -1.2 + 1, lr, far=True)
            leg(CX - 1 + o + s_, CX + o + s_ * 1.2 - 1, ll)
        else:
            lx, rx = CX - hw * 0.52, CX + hw * 0.52
            leg(lx, lx - 1 * (st), ll)
            leg(rx, rx + 1 * (st), lr)
        # ------------------------------------------------ plate / body helpers
        top_y = sh + 2
        def arm(sx, ex_off, hand_dx, hand_dy, far=False, sleeve=True):
            ex, ey = sx + ex_off, top_y + Ht * 0.17
            hx, hy = ex + hand_dx, ey + Ht * 0.13 + hand_dy
            ramp = tu if P["sleeves"] == "tunic" else (R[P["sleeves"]] if isinstance(P["sleeves"], str) else P["sleeves"])
            if far:
                ramp = (ramp[1], ramp[2], ramp[2])
            cv.seg(sx, top_y + 1, ex, ey, armw, armw * 0.95, ramp)
            cv.seg(ex, ey, hx, hy - armw * .6, armw * .95, armw * .85, ramp)
            cv.rect(hx - armw * .55, hy - armw * .7, hx + armw * .55, hy - armw * .55, P["trim"])       # cuff
            sc = (sk[1], sk[2], sk[2]) if far else sk
            cv.ell(hx, hy, armw * .55, armw * .7, lambda u, v: sc[0] if u < -.4 else sc[2] if u > .5 else sc[1])
            return hx, hy
        # ------------------------------------------------ torso (tunic over belted trousers)
        def torso():
            x0, x1 = CX - hw, CX + hw
            hem_y = hip + Ht * P["hem"] + b
            jk = R[P["jerkin"]] if P["jerkin"] else None
            for y in range(int(sh), int(hem_y) + 1):
                t = (y - sh) / max(1, hem_y - sh)
                flare = 0 if y < beltY else (y - beltY) * 0.35
                xa, xb = x0 - flare - (1 if t < 0.12 else 0), x1 + flare + (1 if t < 0.12 else 0)
                if y < sh + Ht * .035:
                    xa, xb = xa + 1, xb - 1
                for x in range(int(round(xa)), int(round(xb)) + 1):
                    u = (x - CX) / max(1, hw)
                    c = tu[0] if u < -0.55 else tu[2] if u > 0.6 else tu[1]
                    if y > beltY and (x - xa) < 2:
                        c = tu[0]
                    if y > beltY and (xb - x) < 2:
                        c = tu[2]
                    # wool fleck
                    if hsh("w", x, y, P["tunic"] if isinstance(P["tunic"], str) else 0) > .975 and y < hem_y - 1:
                        c = tu[0] if c == tu[1] else tu[1]
                    cv.set(x, y, c)
            for x in range(int(round(x0 - (hem_y - beltY) * .35)), int(round(x1 + (hem_y - beltY) * .35)) + 1):
                cv.set(x, hem_y, P["trim"]); cv.set(x, hem_y - 1 if (x // 2) % 2 else hem_y, P["trim"])   # embroidered hem
            if jk and not back:
                # leather jerkin over the tunic: two panels laced down the front
                for y in range(int(sh + 2), int(beltY)):
                    for x in range(int(CX - hw + 1), int(CX + hw)):
                        if abs(x - CX) > 1:
                            cv.set(x, y, jk[0] if x < CX - hw * .5 else jk[2] if x > CX + hw * .5 else jk[1])
                for y in range(int(sh + 3), int(beltY), 2):
                    cv.set(CX, y, "plaster_lo"); cv.set(CX - 1, y + 1, "timber_hi")
            if P["apron"]:
                ap = R[P["apron"]]
                for y in range(int(sh + Ht * .08), int(hem_y + Ht * .08)):
                    for x in range(int(CX - hw * .62), int(CX + hw * .62) + 1):
                        cv.set(x, y, ap[0] if x < CX - hw * .3 else ap[2] if x > CX + hw * .3 else ap[1])
                cv.rect(CX - hw * .62, sh + Ht * .08, CX + hw * .62, sh + Ht * .08, ap[0])
            if P["skirt"]:
                skr = R[P["skirt"]]
                for y in range(int(beltY), int(hip + Ht * .24 + b)):
                    f = (y - beltY) * .3
                    for x in range(int(CX - hw - f), int(CX + hw + f) + 1):
                        cv.set(x, y, skr[0] if x < CX - hw * .5 else skr[2] if x > CX + hw * .5 else skr[1])
                for x in range(int(CX - hw - Ht * .06), int(CX + hw + Ht * .06) + 1):
                    cv.set(x, hip + Ht * .24 + b - 1, P["trim"])
            # belt
            bw = max(2, Ht * 0.05)
            cv.rect(x0 - 1, beltY - bw / 2, x1 + 1, beltY + bw / 2, P["belt"][0])
            cv.rect(x0 - 1, beltY + bw / 2, x1 + 1, beltY + bw / 2, P["belt"][1])
            if not back and not side:
                cv.rect(CX - 2, beltY - bw / 2 - 1, CX + 2, beltY + bw / 2 + 1, P["buckle"])
                cv.rect(CX - 1, beltY - 1, CX + 1, beltY + 1, P["belt"][1])
            if side:
                cv.rect(CX - hw - 1, beltY - bw / 2 - 1, CX - hw + 1, beltY + bw / 2 + 1, P["buckle"])
        # ------------------------------------------------ order
        if side:
            hxs = arm(CX + 1, 1, 1, 0, far=True)
            torso()
            sw_ = sw * Ht * 0.10
            if at:
                ax = -at * Ht * 0.28
                hx, hy = arm(CX - 1, ax * .5 - 1, ax * .5, -at * Ht * .12)
            elif ca:
                hx, hy = arm(CX - 1, -ca * Ht * .1, -ca * Ht * .16, -ca * Ht * .14)
            else:
                hx, hy = arm(CX - 1, sw_ * .5, sw_ * .5, 0)
            hand_front = (hx, hy)
        else:
            alx = CX - hw - armw * .3
            arx = CX + hw + armw * .3
            torso()
            if at:
                hl = arm(alx, -2, -Ht * .05, -at * Ht * .30 * P['raise_'])
                hr = arm(arx, 2, Ht * .05, -at * Ht * .30 * P['raise_'])
            elif ca:
                hl = arm(alx, -Ht * .03, -Ht * .02, -ca * Ht * .20 * P['raise_'])
                hr = arm(arx, Ht * .03, Ht * .02, -ca * Ht * .20 * P['raise_'])
            elif anim in ("walk", "follow"):
                hl = arm(alx, -1, 0, -sw * Ht * .05)
                hr = arm(arx, 1, 0, sw * Ht * .05)
            else:
                hl = arm(alx, -1, 0, 0)
                hr = arm(arx, 1, 0, 0)
            hand_front = hr
            hand_back = hl
        # ------------------------------------------------ mantle (fur over the shoulders)
        if P["mantle"]:
            m = R[P["mantle"]]
            mw = hw * 1.35 + (0 if not side else Ht * 0.03)
            md = Ht * 0.115
            for y in range(int(sh - 1), int(sh + md)):
                t = (y - sh) / md
                ext = mw * (1 - 0.18 * t * t)
                jag = int(hsh("m", int(y), 3) * 2)
                for x in range(int(CX - ext), int(CX + ext) + 1):
                    # ragged lower edge
                    edge = sh + md * (0.78 + 0.22 * hsh("f", x, 5))
                    if y <= edge:
                        u = (x - CX) / max(1, ext)
                        c = m[0] if u < -0.4 else m[2] if u > 0.5 else m[1]
                        if hsh("t", x, y) > .9:
                            c = m[0] if c != m[0] else m[1]
                        cv.set(x, y, c)
            if not back:
                for x in range(int(CX - mw * .3), int(CX + mw * .3) + 1):   # neck opening
                    cv.set(x, sh - 1, sk[2])
        # ------------------------------------------------ plate (bosses only)
        if P["plate"]:
            P["plate"](cv, dict(CX=CX, sh=sh, hip=hip, hw=hw, b=b, Ht=Ht, k=k, face=face, G=G, at=at, i=i, anim=anim, beltY=beltY,
                                hcy=hcy, hcx=hcx, hh=hh, hhw=hhw, legw=legw, st=st, hands=(hand_front, hand_back if not side else hand_front)))
        # ------------------------------------------------ neck + head
        cv.rect(hcx - hhw * .45, hcy + hh * .6, hcx + hhw * .45, sh + 2, sk[2])
        def headfill(u, v):
            return sk[0] if (u < -0.45 and v < 0.35) else sk[2] if (u > 0.62 or v > 0.82) else sk[1]
        cv.ell(hcx, hcy, hhw, hh, headfill)
        if P["tusks"]:
            pass
        # hair back layer / style
        if hair and not P["bald"]:
            hs = P["hairstyle"]
            for y in range(int(hcy - hh - 1), int(hcy - hh * 0.15)):
                for x in range(int(hcx - hhw - 1), int(hcx + hhw + 2)):
                    u, v = (x - hcx) / hhw, (y - hcy) / hh
                    if u * u + v * v <= 1.18 and (v < -0.52 + (0.30 if not back else 1.5) * abs(u) ** 1.5 * (0.8 if not back else 1)):
                        cv.set(x, y, hair[0] if u < -.3 else hair[2] if u > .55 else hair[1])
            if back:
                for y in range(int(hcy), int(hcy + hh * .9)):
                    for x in range(int(hcx - hhw), int(hcx + hhw) + 1):
                        u, v = (x - hcx) / hhw, (y - hcy) / hh
                        if u * u + v * v <= 1.0:
                            cv.set(x, y, hair[0] if u < -.4 else hair[2] if u > .5 else hair[1])
            if side:    # hair falls behind the ear
                cv.rect(hcx + hhw * .15, hcy - hh * .4, hcx + hhw + 1, hcy + hh * .5, hair[1])
                cv.rect(hcx + hhw * .6, hcy - hh * .3, hcx + hhw + 1, hcy + hh * .5, hair[2])
            if hs == "bun":
                cv.ell(hcx + (hhw * .5 if side else 0), hcy - hh - 3 * k * .5, hhw * .45, hhw * .4, lambda u, v: hair[0] if u < -.2 else hair[1])
            if hs == "topknot":
                cv.ell(hcx, hcy - hh - 2 * k * .5, hhw * .3, hhw * .35, lambda u, v: hair[0] if u < -.2 else hair[1])
            if hs == "braids":
                for sd in ((-1, 1) if not side else (1,)):
                    bx = hcx + sd * (hhw + 1)
                    for j in range(int(Ht * .30)):
                        cv.set(bx, hcy + hh * .1 + j, hair[1] if j % 2 else hair[0])
                        cv.set(bx + sd * (1 if j % 2 else 0) + (0 if sd > 0 else 0), hcy + hh * .1 + j, hair[2] if j % 4 > 1 else hair[1])
                    cv.rect(bx - 1, hcy + hh * .1 + Ht * .30, bx + 1, hcy + hh * .1 + Ht * .30 + 1, "flower_gold")
            if hs == "long":
                for sd in ((-1, 1) if not side else (1,)):
                    cv.rect(hcx + sd * (hhw - 1) - 1, hcy, hcx + sd * (hhw + 2), hcy + hh * 1.5, hair[1])
        # face
        if not back:
            ex = hhw * .42
            ey = hcy + hh * .05
            eyeS = max(1, round(k * .5))
            if side:
                exs = [hcx - hhw * .5]
            else:
                exs = [hcx - ex, hcx + ex]
            for exx in exs:
                if bl:
                    cv.rect(exx - eyeS, ey + 1, exx + eyeS, ey + 1, P["eyes"])
                else:
                    cv.rect(exx - eyeS * .5, ey - eyeS, exx + eyeS * .5, ey + eyeS * .5 + .5, P["eyes"])
                    cv.set(exx - eyeS * .5, ey - eyeS, "white")
                if P["brow"]:
                    cv.rect(exx - eyeS - 1, ey - eyeS - 2, exx + eyeS, ey - eyeS - 2, P["brow"] if not hair else hair[2])
            if side:
                cv.rect(hcx - hhw - 1, ey + 1, hcx - hhw, ey + 3, sk[2]); cv.set(hcx - hhw - 1, ey + 2, sk[1])    # nose
            else:
                cv.rect(hcx - 1, ey + 2, hcx, ey + max(3, hh * .3), sk[2])
            if P["cheeks"]:
                for exx in exs:
                    cv.set(exx + (-1 if not side else 1), ey + hh * .38, "flower_rose" if sk[1] in ("skin", "plaster") else sk[2])
            if not P["beard"]:
                mx = hcx - (hhw * .45 if side else 0)
                cv.rect(mx - 1, hcy + hh * .62, mx + 1, hcy + hh * .62, "roof")
        # beard
        if P["beard"] and not back:
            bc = P["beard_c"] or hair or R["grey"]
            st_ = P["beard"]
            by0 = hcy + hh * .35
            L_ = {"full": Ht * .34, "braids": Ht * .30, "short": Ht * .08}[st_]
            if side:
                bw0 = hhw * .8
                for y in range(int(by0), int(by0 + hh * .6 + L_)):
                    t = (y - by0) / max(1, hh * .6 + L_)
                    for x in range(int(hcx - hhw - 1), int(hcx - hhw + bw0 * (1 - t * .5))):
                        cv.set(x, y, bc[0] if x < hcx - hhw + 2 else bc[1])
            elif st_ == "braids":
                for bx in (hcx - hhw * .5, hcx, hcx + hhw * .5):
                    for j in range(int(hh * .55 + L_)):
                        cv.set(bx, by0 + j, bc[1] if j % 2 else bc[0]); cv.set(bx + 1, by0 + j, bc[2] if j % 2 else bc[1])
                        if j % 5 == 4:
                            cv.set(bx, by0 + j, "flower_gold")
                cv.rect(hcx - hhw * .8, by0 - 1, hcx + hhw * .8, by0 + hh * .3, bc[1])
            else:
                for y in range(int(by0), int(by0 + hh * .6 + L_)):
                    t = (y - by0) / max(1, hh * .6 + L_)
                    wd = hhw * (0.95 - 0.55 * t * t)
                    for x in range(int(hcx - wd), int(hcx + wd) + 1):
                        u = (x - hcx) / max(1, wd)
                        cv.set(x, y, bc[0] if u < -.35 else bc[2] if u > .5 else bc[1])
                cv.rect(hcx - 1, by0 + hh * .15, hcx + 1, by0 + hh * .15 + 1, sk[2])    # mouth
        # tusks / extras
        ctx = dict(CX=CX, hcx=hcx, hcy=hcy, hh=hh, hhw=hhw, sh=sh, hip=hip, hw=hw, b=b, Ht=Ht, k=k, face=face, G=G, anim=anim, i=i, at=at, ca=ca,
                   hands=(hand_front, hand_back if not side else hand_front), hand=hand_front, hand_back=(hand_back if not side else hand_front), side=side, back=back, beltY=beltY, st=st, sw=sw)
        if P["extra"]:
            P["extra"](cv, ctx)
    draw.fall = True
    return draw
