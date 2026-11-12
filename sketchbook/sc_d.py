"""Bridge (night, the door, the sun), final build, outro."""
from motifs import *
import sc_b

DX, DY0 = 960, 620          # door centre
DW, DH = 160, 280
ZEND = 13.0
T_OPEN = 182.54


def _zoom(t):
    k = ease(ramp(t, 186.3, 192.3))
    return math.exp(math.log(ZEND * 1.06) * k), k


_ST = None


def stars():
    global _ST
    if _ST is None:
        n = 170
        r = rnds(n * 5, 99, 1).reshape(n, 5)
        x = r[:, 0] * (W + 200) - 100
        y = r[:, 1] ** 1.3 * 720
        keep = ~((np.abs(x - DX) < 130) & (y > 430))
        _ST = (x[keep], y[keep], r[keep, 2], r[keep, 3], r[keep, 4])
    return _ST


def _wheel_sketch(c, x, y, r, rev, seed):
    c.pl(circ(x, y, r), w=3.0, close=True, seed=seed, rev=ramp(rev, 0, 0.4), passes=2)
    for k in range(8):
        a = k * TAU / 8
        rr = ramp(rev, 0.3 + k * 0.05, 0.5 + k * 0.05)
        c.line(x, y, x + r * math.cos(a), y + r * math.sin(a), w=2.2, seed=seed + 1 + k, rev=rr, passes=1)
        if rr >= 1:
            c.pl(circ(x + r * 1.15 * math.cos(a + 0.25), y + r * 1.15 * math.sin(a + 0.25), r * 0.1), w=2.2, close=True, seed=seed + 20 + k, passes=1, wob=0.5)
    c.script('perpetual?', x, y + r + 62, 34, font='futural', rev=ramp(rev, 0.7, 1.0), w=1.8, a=0.8, seed=seed)


def _wing_sketch(c, x, y, s, rev, seed):
    c.line(x - s, y, x + s, y + s * 0.1, w=3.0, seed=seed, rev=ramp(rev, 0, 0.25), passes=2)
    for k, sg in enumerate((-1, 1)):
        u = np.linspace(0, 1, 16)
        wing = np.stack([x + sg * u * s * 1.5, y - s * 0.9 * np.sin(u * math.pi) * (0.6 + 0.4 * u) + u * s * 0.2], 1)
        c.pl(wing, w=3.0, seed=seed + 1 + k, rev=ramp(rev, 0.2 + k * 0.2, 0.55 + k * 0.2), passes=2)
        for j in range(1, 6):
            rr = ramp(rev, 0.5 + j * 0.05, 0.65 + j * 0.05)
            p = wing[j * 3 - 1]
            c.line(p[0], p[1], x + sg * j * s * 0.2, y + 6, w=1.8, seed=seed + 5 + k * 6 + j, rev=rr, passes=1)
    c.script('v = ?', x - s * 0.3, y + s * 0.55, 34, font='futural', align='l', rev=ramp(rev, 0.8, 1.0), w=1.8, a=0.8, seed=seed)


def _cross(c, x, y, s, t, t0, seed):
    r1 = eout(ramp(t, t0, t0 + 0.12))
    r2 = eout(ramp(t, t0 + 0.1, t0 + 0.22))
    c.line(x - s, y - s, x + s, y + s, w=11, col=CORAL, a=1.0, seed=seed, rev=r1, passes=1)
    c.line(x + s, y - s, x - s, y + s, w=11, col=CORAL, a=1.0, seed=seed + 1, rev=r2, passes=1)


def _day_world(c, t, big=1.0, rays=1.0):
    """the world on the other side of the door, in full-frame coordinates"""
    hy = 760
    pu = A.pulse(t, 5)
    sr = 300 * big * (1 + 0.02 * pu)
    sun_rays(c, 960, 470, sr + 30, sr + (130 + 60 * pu) * rays, n=28, ang=t * 0.3, seed=30, w=3.4)
    sun_disc(c, 960, 470, sr, phase=t * 1.1, cols=(YEL, CORAL, PINK), seed=1)
    c.pl(circ(960, 470, sr), w=3.8, close=True, seed=2, passes=3)
    c.fill(rect(-400, hy, W + 800, 2000), PAPER, mul=False, wob=0)
    c.line(-400, hy, W + 400, hy, w=3.6, seed=4, passes=3)
    gridfloor(c, hy, 960, t * 1.5, bottom=H + 40, col=CYAN, w=2.4, a=0.95, spacing=250, x0=-400, x1=W + 400)
    for k, (x, h) in enumerate(((250, 300), (480, 210), (1500, 250), (1720, 340))):
        turbine(c, x, hy, h, t * 3.5 + k, seed=50 + k * 20, w=3.0)


def bridge(c, t, u, d):
    z, zk = _zoom(t)
    cyS = DY0 - 80 * zk
    c.begin(t, paper=NIGHT, ink=CHALK, night=True)
    shake = (0.0, 0.0)
    sk = ramp(t, 179.4, T_OPEN) * (1 - ramp(t, T_OPEN, T_OPEN + 0.5))
    shx = 12 * sk * sn1(t * 9.0, 1)
    shy = 12 * sk * sn1(t * 9.0, 2)
    push = 1.0 + 0.07 * ramp(t, B(88), 186.3)       # slow drift in before the big push
    Z = z * push

    def S(x, y):
        return (DX + (x - DX) * Z + shx, cyS + (y - DY0) * Z + shy)

    hy = DY0 + DH / 2
    # ---- stars
    sx, sy, sr_, sb, sf = stars()
    n = len(sx)
    born = B(88) + 0.3 + sb * 8.5
    tf = 179.3 + sf * 4.3
    X = DX + (sx - DX) * Z + shx
    fall = np.clip(t - tf, 0, None)
    Y0 = cyS + (sy - DY0) * Z + shy
    Y = Y0 + 900 * fall ** 2 * Z
    vis = (t >= born) & (Y < cyS + (hy - DY0) * Z + 40)
    tw = 0.75 + 0.25 * np.sin(t * (2 + 4 * sr_) + sb * 20)
    rr = (1.6 + 3.2 * sr_ ** 2) * tw * np.minimum(1.0, (t - born) * 4) * (1 + 0.2 * (Z - 1))
    if Z < 9:
        m = vis & (X > -20) & (X < W + 20) & (Y > -20)
        c.dots(np.stack([X[m], Y[m]], 1), rr[m], col=CHALK)
        fm = m & (fall > 0)
        if fm.any():
            c.ticks(np.stack([X[fm], Y[fm], X[fm] + 3, Y[fm] - np.minimum(260, 1500 * fall[fm]) * Z], 1), w=2.2, a=0.8, jit=0.5, seed=5, boil=False)
        # constellations
        if t < 183.6:
            order = np.argsort(sx + sy * 0.3)
            for g in range(14):
                idx = order[g * 9 + 2: g * 9 + 9]
                for j in range(len(idx) - 1):
                    a_, b_ = idx[j], idx[j + 1]
                    if fall[a_] > 0 or fall[b_] > 0 or math.hypot(sx[a_] - sx[b_], sy[a_] - sy[b_]) > 250:
                        continue
                    r = ramp(t, max(born[a_], born[b_]) + 0.4 + j * 0.3, max(born[a_], born[b_]) + 1.2 + j * 0.3)
                    c.line(X[a_], Y[a_], X[b_], Y[b_], w=1.6, a=0.55, seed=100 + g * 10 + j, rev=r, passes=1)
    # ---- ground
    g0, g1 = S(-400, hy), S(W + 400, hy)
    if g0[1] < H + 50:
        c.line(g0[0], g0[1], g1[0], g1[1], w=3.4, seed=1, passes=3, rev=ease(ramp(t, B(88), B(88) + 1.6)))
        segs = []
        for k in range(26):
            gx = -300 + k * 100
            p0 = S(gx, hy + 14 + (k % 3) * 22)
            segs.append((p0[0], p0[1], p0[0] + 60 * Z, p0[1]))
        c.ticks(segs, w=1.6, a=0.5, jit=0.8, seed=2)
    # ---- wrong sketches
    if 170.2 < t and Z < 6:
        for k, (fn, x, y, s, ta, tx) in enumerate(((_wheel_sketch, 400, 500, 105, 170.5, 173.70), (_wing_sketch, 1510, 520, 150, 172.9, 176.42))):
            px, py = S(x, y)
            c.cx.save()
            c.cx.translate(px, py)
            c.cx.scale(Z, Z)
            fn(c, 0, 0, s, ramp(t, ta, ta + 2.3), 300 + k * 60)
            _cross(c, 0, 0, s * 1.1, t, tx, 400 + k * 10)
            c.cx.restore()
        if Z < 1.6:
            c.script("and maybe I'm wrong", *S(130, 250), 78 * Z, align='l', rev=ramp(t, 170.56, 174.2), w=3.4, seed=11)
            c.script("I've been wrong before", *S(1080, 250), 78 * Z, align='l', rev=ramp(t, 175.08, 177.3), w=3.4, seed=12)
            if t > 178.9:
                c.script('maybe the sky will fall', *S(130, 930), 70 * Z, align='l', rev=ramp(t, 178.97, 181.1), w=3.2, seed=13)
    # ---- the door
    x0, y0 = S(DX - DW / 2, DY0 - DH / 2)
    x1, y1 = S(DX + DW / 2, DY0 + DH / 2)
    opening = ease(ramp(t, T_OPEN, T_OPEN + 0.28))
    doorway = rect(x0, y0, x1 - x0, y1 - y0)
    lw = min(9.0, 3.4 * Z ** 0.5)
    if opening > 0:
        # through the door: daylight
        c.region(doorway, PAPER, ink=INK, night=False)
        sd = Z / ZEND
        c.cx.save()
        c.cx.translate(DX + shx, cyS + shy)
        c.cx.scale(sd, sd)
        c.cx.translate(-960, -540)
        _day_world(c, t)
        c.cx.restore()
        c.endregion()
        # light spilling onto the ground
        if Z < 5:
            spill = np.array([[x0, y1], [x1, y1], [x1 + 260 * Z, y1 + 330 * Z], [x0 - 260 * Z, y1 + 330 * Z]])
            c.fill(spill, YEL, a=0.9 * opening, wob=1.5, seed=20)
            for k in range(7):
                fx = x0 + (x1 - x0) * k / 6
                c.line(fx, y1 + 4, fx + (k - 3) * 86 * Z, y1 + 330 * Z, w=1.8, a=0.7, col=NIGHT, seed=30 + k, passes=1)
    # frame
    if x1 - x0 < W * 1.3:
        c.pl([[x0, y1], [x0, y0], [x1, y0], [x1, y1]], w=lw * 1.3, seed=40, passes=3)
        c.pl([[x0 - 12 * Z, y1], [x0 - 12 * Z, y0 - 12 * Z], [x1 + 12 * Z, y0 - 12 * Z], [x1 + 12 * Z, y1]], w=lw, seed=41, passes=2)
    # leaf
    if Z < 7:
        th = opening * 1.95
        wl = (x1 - x0)
        fx = x0 + wl * math.cos(th)
        sk_ = 34 * Z * math.sin(th)
        leaf = np.array([[x0, y0], [fx, y0 - sk_], [fx, y1 + sk_], [x0, y1]])
        c.fill(leaf, NIGHT, mul=False, wob=0)
        c.pl(leaf, w=lw, close=True, seed=42, passes=3)
        for j in (0.12, 0.55):
            pn = np.array([[x0 + (fx - x0) * 0.18, y0 + (y1 - y0) * j], [x0 + (fx - x0) * 0.82, y0 + (y1 - y0) * j - sk_ * 0.6 * (1 - j)],
                           [x0 + (fx - x0) * 0.82, y0 + (y1 - y0) * (j + 0.33) + sk_ * 0.3 * j], [x0 + (fx - x0) * 0.18, y0 + (y1 - y0) * (j + 0.33)]])
            c.pl(pn, w=lw * 0.6, close=True, seed=43 + int(j * 10), passes=1, wob=0.8)
        c.dots([(x0 + (fx - x0) * 0.86, (y0 + y1) / 2 + 10 * Z)], 4.5 * Z, col=YEL)
        if opening <= 0:
            # light leaking round the closed door
            gl = 0.6 + 0.4 * math.sin(t * 2.2)
            c.line(x0 + 4, y1 + 3, x1 - 4, y1 + 3, w=4.5, col=YEL, a=gl, seed=46, passes=1)
            c.line(x1 - 2, y0 + 8, x1 - 2, y1 - 4, w=2.0, col=YEL, a=gl * 0.8, seed=47, passes=1)
    # ---- crash: shards flying out of the door
    if T_OPEN <= t < T_OPEN + 1.6:
        p = (t - T_OPEN) / 1.6
        for k in range(16):
            a = k * TAU / 16 + rnd(k, 5) * 0.4
            dist = (60 + 1500 * p ** 0.8) * (0.6 + 0.8 * rnd(k, 6))
            s = (16 + 90 * p) * (0.6 + rnd(k, 7))
            q = rot(np.array([[0, -s], [s * 0.8, s * 0.6], [-s * 0.7, s * 0.5]]), a * 3 + p * 6 * (rnd(k, 8) - 0.5)) + (DX + dist * math.cos(a), cyS + dist * math.sin(a) * 0.8)
            c.fill(q, (YEL, CORAL, CHALK)[k % 3], mul=False, wob=0.8, seed=60 + k, a=1 - p ** 3)
            c.pl(q, w=2.6, close=True, seed=80 + k, wob=0.8, a=1 - p ** 3)
    # ---- sung lines
    if 184.7 <= t < 188.5:
        band_words(c, t, (('BUT', 184.80), ("I'D", 186.70), ('RATHER', 187.18), ('BE', 187.46), ('WRONG', 187.88)), cols=(CHALK, YEL, CORAL), seed=70)
    elif 188.5 <= t:
        c.ink, c.night = INK, False
        band_words(c, t, (('WITH', 188.74), ('MY', 190.28), ('EYES', 190.68), ('ON', 191.06), ('THE', 191.42), ('SUN', 191.68)), cols=(YEL, CORAL, CYAN), seed=80)
    fl = 0.85 * (1 - ramp(t, T_OPEN, T_OPEN + 0.3)) * (1 if t >= T_OPEN else 0)
    fl = max(fl, 0.0)
    return dict(flash=fl)


def bridge_day(c, t, u, d):
    """than right in the dark when the dark has won -> rub the dark out"""
    c.begin(t)
    wind_up = ramp(t, B(110), B(112))
    big = 1.0 + 0.35 * ease(wind_up)
    c.cx.save()
    c.cx.translate(0, 80 - 80 * 1.0)
    _day_world(c, t, big=big, rays=1.0 + 3.0 * ein(wind_up, 2))
    c.cx.restore()
    if wind_up > 0:
        sc_b.confetti(c, t, B(110), 30, seed=44, rate=4.0, avoid=lambda x, y: math.hypot(x - 960, y - 470) < 440)
    # the dark: a scribbled mass, erased
    erase = ease(ramp(t, 198.2, 201.2))
    grow = ease(ramp(t, 193.6, 196.2))
    scb = sc_b.scribble(900, 5) * (250, 150) + (1500, 880)
    if grow > 0 and erase < 1:
        n = len(scb)
        a_, b_ = int(n * erase), int(n * grow)
        if b_ - a_ > 3:
            for k in range(3):
                c.pl(scb[a_:b_] + (k * 5, k * 4), w=4.5, seed=20 + k, passes=1, wob=1.6, seg=9, a=0.95)
    c.script('than right in the dark', 110, 900, 84, align='l', rev=ramp(t, 193.62, 195.6), w=4.0, seed=3)
    c.script('when the dark has won', 110, 1010, 84, align='l', rev=ramp(t, 196.62, 201.3) if False else ramp(t, 196.62, 198.0), w=4.0, seed=4)
    if 198.0 <= t < 201.4:
        ex = 1500 + 240 * math.sin(t * 13) * (1 - erase * 0.5)
        ey = 880 + 110 * math.sin(t * 7.3)
        pencil(c, ex + 215 * 1.25 * math.cos(-0.9 + math.pi) * -1 * 0 + 0, ey, ang=-0.9 + math.pi + 0.15 * math.sin(t * 13), s=1.25) if False else \
            _pencil_eraser(c, ex, ey, t)
    fl = 0.5 * (1 - ramp(u, 0, 0.14)) + 0.9 * ein(ramp(t, B(112) - 0.25, B(112)), 2)
    return dict(flash=fl)


def _pencil_eraser(c, ex, ey, t):
    """pencil turned round, eraser end at (ex, ey)"""
    ang = -0.9 + 0.15 * math.sin(t * 13)
    L = (190 + 40) * 1.25
    tipx, tipy = ex + L * math.cos(ang) * -1, ey + L * math.sin(ang) * -1
    # draw the pencil with its tip up-left, body ending (eraser) at (ex, ey)
    pencil(c, ex - L * math.cos(ang + math.pi) * -1 * -1, ey - L * math.sin(ang + math.pi) * -1 * -1, ang=ang + math.pi, s=1.25) if False else \
        pencil(c, ex + L * math.cos(ang), ey + L * math.sin(ang), ang=ang + math.pi, s=1.25)


# ------------------------------------------------------------------ final build and outro
TB0, TB1 = B(124), B(128)


def final_build(c, t, u, d):
    return sc_b.ch_build(c, t, u, d, 3, sc_b.WT[3])


def _train(c, x, y, seed=0, n=4, s=1.0):
    for k in range(n):
        x0 = x + k * 196 * s
        q = rect(x0, y - 62 * s, 184 * s, 62 * s)
        if k == 0:
            q = np.array([[x0 + 46 * s, y - 62 * s], [x0 + 184 * s, y - 62 * s], [x0 + 184 * s, y], [x0, y], [x0 + 6 * s, y - 26 * s]])
        c.fill(q, PAPER, mul=False, wob=0)
        c.fill(q, CORAL if k % 2 == 0 else YEL, off=(5, 4), seed=seed + k)
        c.pl(q, w=3.2, close=True, seed=seed + 10 + k, wob=0.8)
        wins = [rect(x0 + (58 if k == 0 else 16) * s + j * 40 * s, y - 50 * s, 28 * s, 20 * s) for j in range(3 if k == 0 else 4)]
        c.fill(wins, PAPER, mul=False, wob=0)
        for j, w_ in enumerate(wins):
            c.pl(w_, w=1.8, close=True, seed=seed + 30 + k * 5 + j, wob=0.5, passes=1)


def panorama(c, t, grow=1.0):
    gy = 820
    d = TB1 - TB0

    def behind(c):
        for k, (x, h) in enumerate(((110, 520), (300, 640), (500, 470), (1430, 500), (1630, 660), (1830, 540))):
            turbine(c, x, gy, h, t * 3.4 + k * 1.3, seed=500 + k * 20, w=3.4, fillc=PAPER, rev=ramp(grow, k * 0.08, 0.5 + k * 0.08))
        for k in range(4):
            cxp = (k * 560 + 260 + (t - 231) * (16 + 5 * k)) % (W + 600) - 300
            cloud(c, cxp, 130 + 80 * (k % 2), 320 + 50 * k, 56, seed=520 + k, shade=0, fillc=PINK if k % 2 == 0 else CYAN, lw=3.0)
    sc_b.ch_build(c, t, d - 0.001, d, 3, sc_b.WT[3], begin=False, behind=behind)
    birds(c, t, n=12, seed=8, y0=230, speed=200, x0=-100, t0=TB1 - 6.0, w=3.0, scale=1.2)
    birds(c, t, n=9, seed=18, y0=330, speed=160, x0=-300, t0=TB1 + 6.0, w=3.0, scale=1.0)
    # viaduct + train
    vy = 905
    g2 = ease(ramp(grow, 0.15, 0.8))
    if g2 > 0:
        deck = rect(-40, vy, W + 80, 26)
        c.fill(rect(-40, vy, W + 80, 400), PAPER, mul=False, wob=0)
        tx = W + 200 - ((t - TB1 - 3.0) * 330) % (W + 1900)
        _train(c, tx, vy - 2, seed=600)
        c.fill(deck, PINK, seed=540, off=(5, 4))
        c.line(-40, vy, (W + 40) * g2, vy, w=4.0, seed=541, passes=3)
        c.line(-40, vy + 26, (W + 40) * g2, vy + 26, w=3.0, seed=542, passes=2)
        for k in range(9):
            if k / 9 > g2:
                break
            ax = 110 + k * 215
            c.pl(circ(ax, vy + 130, 88, math.pi, TAU), w=3.2, seed=550 + k, passes=2)
            c.line(ax - 88, vy + 130, ax - 88, H + 20, w=3.0, seed=570 + k, passes=1)
            c.line(ax + 88, vy + 130, ax + 88, H + 20, w=3.0, seed=590 + k, passes=1)
    # water
    g3 = ease(ramp(grow, 0.4, 1.0))
    if g3 > 0:
        sc_b.ridges(c, t, H + 40 - 95 * g3, H + 60, rows=5, amp=60, linec=PAPER, fillc=lambda k: mixc(CYAN, BLUE, k * 0.8), seed=700, lw=3.0)


PANEL = dict(cx=960, cy=455, s=0.60)


def outro(c, t, u, d):
    c.begin(t)
    grow = ramp(t, TB1, TB1 + 4.5)
    k = ease(ramp(t, B(136), B(138.5)))
    s = 1 - (1 - PANEL['s']) * k
    cyc = 540 + (PANEL['cy'] - 540) * k
    if k > 0:
        P = rect(960 - 960 * s, cyc - 540 * s, 1920 * s, 1080 * s)
        # rays round the finished page
        pu = A.pulse(t, 5)
        if t < B(144):
            for j in range(40):
                th = j * TAU / 40 + 0.05
                r0 = 1.0
                ex, ey = math.cos(th), math.sin(th)
                # start on the panel border
                sx_ = (960 * s + 26) / max(1e-6, abs(ex))
                sy_ = (540 * s + 26) / max(1e-6, abs(ey))
                r0 = min(sx_, sy_)
                ln = (26 + 46 * pu * (1 if j % 2 else 0.5)) * k
                c.line(960 + ex * r0, cyc + ey * r0, 960 + ex * (r0 + ln), cyc + ey * (r0 + ln), w=3.0, seed=900 + j, passes=1, a=0.9)
        c.fill(P + (14, 12), INK, mul=False, wob=1.0, seed=800)
        c.region(P, PAPER)
    c.cx.save()
    c.cx.translate(960, cyc)
    c.cx.scale(s, s)
    c.cx.translate(-960, -540)
    panorama(c, t, grow)
    c.cx.restore()
    if k > 0:
        c.endregion()
        panel_frame(c, P, seed=801, w=5.0)
    else:
        sc_b.caption(c, 'until further notice...', t, 235.38, 238.4, x=110, y=150, size=72, seed=11)
        if t > 242.0:
            sc_b.caption(c, 'until further notice...', t, 242.48, 245.3, x=1050, y=150, size=72, seed=12, rot=0.012)
    # the last line
    hp = c.script("It's not too late.", 960, 965, 150, rev=ramp(t, 250.20, 252.75), w=5.5, seed=21)
    ul = ease(ramp(t, 253.0, 253.9))
    hu = None
    if ul > 0:
        xs = np.linspace(430, 1500, 40)
        hu = c.pl(np.stack([xs, 1004 + 10 * np.sin(xs * 0.02)], 1), w=7, col=CORAL, a=1.0, seed=22, rev=ul, passes=1)
    if 249.6 <= t < 250.2:
        e = eout(ramp(t, 249.6, 250.2))
        pencil(c, 430 - 500 * (1 - e), 900 + 300 * (1 - e), ang=-0.9, s=1.4)
    elif 250.2 <= t < 253.0 and hp is not None:
        pencil(c, hp[0], hp[1], ang=-0.9 + 0.1 * math.sin(t * 16), s=1.4)
    elif 253.0 <= t < 253.9 and hu is not None:
        pencil(c, hu[0], hu[1], ang=-0.9, s=1.4)
    elif t >= 253.9:
        e = ease(ramp(t, 253.9, 254.8))
        pencil(c, 1500 + 40 * e, 1004 - 10 * e, ang=-0.9 + 0.62 * e, s=1.4)
    fade = ein(ramp(t, 260.6, 262.9), 1.5)
    return dict(flash=max(0.5 * (1 - ramp(u, 0, 0.12)), fade))


def timeline():
    return [
        (B(88), B(107), bridge),
        (B(107), B(112), bridge_day),
        (TB0, TB1, final_build),
        (TB1, A.dur + 1, outro),
    ]
