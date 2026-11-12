"""Intro, verse 1, pre-chorus 1."""
from motifs import *

HY = 640


# ------------------------------------------------------------------ intro A: the first line
def intro_a(c, t, u, d):
    c.begin(t)
    vx = 960
    # horizon
    r = ease(ramp(t, 0.7, B(2)))
    head = c.line(150, HY, 1770, HY, w=3.4, seed=1, rev=r, passes=3)
    pen = head if r < 1 else None
    # sun arc on the horizon
    r2 = ease(ramp(t, B(2), B(3)))
    if r2 > 0:
        h2 = c.pl(circ(vx, HY, 170, math.pi, TAU), w=3.2, seed=2, rev=r2, passes=3)
        if r2 < 1:
            pen = h2
        # construction marks
        c.line(vx, HY - 200, vx, HY + 26, w=1.4, a=0.5, seed=3, rev=ramp(t, B(2), B(2.5)), passes=1)
        c.script('0,0', vx + 14, HY + 44, 22, font='futural', align='l', rev=ramp(t, B(2.5), B(3)), w=1.4, a=0.6)
    # road edges falling away from the vanishing point
    r3 = ease(ramp(t, B(3), B(3.5)))
    r4 = ease(ramp(t, B(3.5), B(4)))
    if r3 > 0:
        h3 = c.line(vx - 30, HY + 4, -260, H + 40, w=3.2, seed=4, rev=r3, passes=3)
        if r3 < 1:
            pen = h3
    if r4 > 0:
        h4 = c.line(vx + 30, HY + 4, W + 260, H + 40, w=3.2, seed=5, rev=r4, passes=3)
        if r4 < 1:
            pen = h4
        for k in range(6):
            z0, z1 = 1.25 ** k, 1.25 ** k * 1.1
            y0, y1 = HY + 440 / z0 / 1.0, HY + 440 / z1
            c.line(vx, y0, vx, y1, w=5.5 / z0 + 1.2, seed=20 + k, rev=ramp(t, B(3.6) + k * 0.06, B(3.8) + k * 0.06), passes=1, wob=0.5)
    # title
    ts = B(4)
    rt = ramp(t, ts, B(6.6))
    if rt > 0:
        size = 132
        wd = text_width('UNTIL FURTHER NOTICE', size, track=0.02)
        hr = ramp(t, B(6), B(7.6))
        c.text('UNTIL FURTHER NOTICE', 960, 400, size, seed=7, rev=rt, track=0.02, w=3.2,
               hatch=dict(gap=7, a=0.62, rev=hr, ang=-0.85) if hr > 0 else None)
        if rt < 1:
            pen = (960 - wd / 2 + wd * rt, 400 - size * 0.4 + 26 * math.sin(t * 23))
        elif hr < 1 and hr > 0:
            pen = (960 - wd / 2 + wd * hr, 400 - size * 0.4 + 40 * math.sin(t * 31))
    # rays on the beat before the drums
    for k in range(9):
        tb = B(7) + k * (B(8) - B(7)) / 9.5
        if t >= tb:
            th = math.pi + (k + 0.5) * math.pi / 9
            p = eout(ramp(t, tb, tb + 0.15))
            c.line(vx + 205 * math.cos(th), HY + 205 * math.sin(th), vx + (205 + 70 * p) * math.cos(th), HY + (205 + 70 * p) * math.sin(th), w=3.2, seed=40 + k)
    if pen is not None and t > 0.7:
        pencil(c, pen[0], pen[1], ang=-0.95 + 0.06 * math.sin(t * 5), s=1.15)
    elif t < 0.7:
        k = eout(ramp(t, 0.2, 0.7))
        pencil(c, 150 - 300 * (1 - k), HY - 260 * (1 - k), ang=-0.95, s=1.15)
    return dict(flash=0.9 * (1 - ramp(t, 0.0, 0.5)))


# ------------------------------------------------------------------ intro B: motorway, driving
F = 900.0
CAMH = 1.25
VEH = [  # lane x, final gap (m), kind (0 car, 1 lorry, 2 van), seed
    (0.0, 13.0, 0, 1), (3.6, 9.5, 1, 2), (-3.6, 17.0, 2, 3), (0.0, 30.0, 1, 4), (3.6, 34.0, 0, 5), (-3.6, 44.0, 0, 6),
    (0.0, 62.0, 2, 7), (3.6, 70.0, 1, 8), (-3.6, 85.0, 1, 9), (0.0, 110.0, 0, 10), (3.6, 120.0, 0, 11), (-3.6, 140, 2, 12),
]


def _dist(t):
    """distance travelled along the motorway (m): cruising, then slowing into the jam"""
    t0, t1, t2 = B(8), B(12), B(16)
    v0, v1 = 31.0, 1.2
    if t < t1:
        return v0 * (t - t0)
    k = min(1.0, (t - t1) / (t2 - t1))
    return v0 * (t1 - t0) + (t2 - t1) * (v0 * k - (v0 - v1) * (k * k / 2)) + max(0.0, t - t2) * v1


def motorway(c, t, hy, vx, s, jam, rain, dark, seed=0, gantry_text=True, sway=0.0):
    """POV motorway. s = distance travelled, jam 0..1 (vehicles closing up), rain 0..1, dark 0..1 (sky weight)"""
    def P(x, y, z):
        return (vx - F * x / z, hy + F * (CAMH - y) / z)   # mirrored: drive on the left
    # ---- sky: hatched weight + clouds
    if dark > 0:
        for k in range(3):
            dk = ramp(dark, k * 0.3, k * 0.3 + 0.4)
            if dk > 0:
                c.hatch(rect(-10, -10, W + 20, hy - 60 - k * 90 + 10), ang=-0.35 - k * 0.45, gap=13 - k * 2, w=1.6, a=0.42, seed=seed + 50 + k, rev=dk)
    for k in range(6):
        cxp = (k * 397 + 130 + t * (6 + k)) % (W + 500) - 250
        cy = hy - 110 - (k % 3) * 95 - 20 * (k % 2)
        cw = 420 + 130 * (k % 3)
        sh = cloud_shape(cxp, cy, cw, 70 + 22 * (k % 2), seed + k)
        c.fill(sh, PAPER, mul=False, wob=0)
        cloud(c, cxp, cy, cw, 70 + 22 * (k % 2), seed=seed + k, shade=0.35 + 0.6 * dark, gap=7, lw=2.8)
    # ---- horizon + far skyline
    c.line(-20, hy, W + 20, hy, w=2.6, seed=seed + 90)
    segs = []
    for k in range(46):
        x = k * 44 - 30 + vx * 0.02
        hh = 6 + 26 * rnd(seed, k, 5) ** 2
        segs.append((x, hy, x, hy - hh))
        segs.append((x, hy - hh, x + 30, hy - hh))
        segs.append((x + 30, hy - hh, x + 30, hy))
    c.ticks(segs, w=1.5, a=0.6, jit=0.8, seed=seed + 91)
    # ---- road surface
    for k, xr in enumerate((-9.2, -7.4, 6.0, 9.0)):
        a_ = P(xr, 0, 600)
        b_ = P(xr, 0, 1.2)
        c.line(a_[0], a_[1], b_[0], b_[1], w=3.4 if k in (1, 2) else 2.2, seed=seed + 100 + k, passes=2 if k in (1, 2) else 1)
    # central barrier
    a_, b_ = P(-7.4, 0.9, 600), P(-7.4, 0.9, 1.2)
    c.line(a_[0], a_[1], b_[0], b_[1], w=2.4, seed=seed + 106)
    # lane dashes
    L = 12.0
    off = s % L
    for lane in (-1.8, 1.8):
        for k in range(26):
            z0 = k * L - off + 2.0
            z1 = z0 + 4.0
            if z0 < 1.5:
                continue
            p0, p1 = P(lane, 0, z0), P(lane, 0, z1)
            wd = max(1.0, F * 0.16 / z0)
            q = np.array([[p0[0] - wd / 2, p0[1]], [p0[0] + wd / 2, p0[1]], [p1[0] + wd / 2 * z0 / z1, p1[1]], [p1[0] - wd / 2 * z0 / z1, p1[1]]])
            if wd > 3:
                c.pl(q, w=1.8, close=True, seed=seed + 200 + k, wob=0.5, passes=1)
                c.hatch(q, ang=0.5, gap=5, w=1.2, a=0.5, seed=seed + k)
            else:
                c.line(p0[0], p0[1], p1[0], p1[1], w=wd + 0.6, passes=1, wob=0.2, seed=seed + 230 + k)
    # ---- lamp posts
    LP = 42.0
    offp = s % LP
    for k in range(9, -1, -1):
        z = k * LP - offp + 3
        if z < 2.5:
            continue
        for side, xx in ((1, 9.6), (-1, -7.4)):
            b0 = P(xx, 0, z)
            t0_ = P(xx, 11, z)
            arm = P(xx - side * 2.6, 11.5, z)
            lw = max(1.2, min(5.0, F * 0.14 / z))
            c.pl([b0, t0_, arm], w=lw, seed=seed + 300 + (int(s // LP) + k) * 2 + side, wob=min(1.4, 30 / z), passes=1 if z > 60 else 2, seg=20)
    # ---- gantries
    GP = 260.0
    offg = (s + 150) % GP
    for k in range(2, -1, -1):
        z = k * GP - offg + 3
        if z < 3:
            continue
        gid = int((s + 150) // GP) + k
        lw = max(1.3, min(12.0, F * 0.22 / z))
        l0, l1 = P(-7.6, 0, z), P(-7.6, 7.6, z)
        r0, r1 = P(9.8, 0, z), P(9.8, 7.6, z)
        l2, r2 = P(-7.6, 6.8, z), P(9.8, 6.8, z)
        c.pl([l0, l1, r1, r0], w=lw, seed=seed + 400 + gid, wob=min(1.5, 40 / z), seg=20)
        c.line(l2[0], l2[1], r2[0], r2[1], w=lw * 0.7, seed=seed + 410 + gid, wob=min(1.5, 40 / z))
        # sign
        s0, s1 = P(-4.8, 9.4, z), P(4.8, 6.0, z)
        sg = rect(min(s0[0], s1[0]), s0[1], abs(s1[0] - s0[0]), s1[1] - s0[1])
        c.fill(sg, PAPER, mul=False, wob=0)
        c.pl(sg, w=lw * 0.6, close=True, seed=seed + 420 + gid, wob=min(1.5, 40 / z))
        if gantry_text and z < 170:
            sz = (s1[1] - s0[1]) * 0.20
            mx = (s0[0] + s1[0]) / 2
            c.script('DELAYS', mx, s0[1] + sz * 1.9, sz, font='futural', w=max(1.0, sz * 0.09), wob=0.3, seed=1)
            c.script('UNTIL FURTHER NOTICE', mx, s0[1] + sz * 3.9, sz * 0.8, font='futural', w=max(1.0, sz * 0.08), wob=0.3, seed=2)
    # ---- vehicles
    order = sorted(VEH, key=lambda v: -v[1])
    for (lx, gap, kind, sd) in order:
        z = gap + (1 - jam) * (110 + gap * 4.5) + 1.2 * math.sin(t * 0.7 + sd)
        if z < 4 or z > 500:
            continue
        wd, ht = ((1.8, 1.45), (2.5, 3.8), (2.0, 2.3))[kind]
        x0, yb = P(lx - wd / 2, 0.25, z)
        x1, yt = P(lx + wd / 2, ht, z)
        gx0, gy = P(lx - wd / 2, 0, z)
        lw = max(1.2, min(4.0, 60 / z))
        x0, x1 = min(x0, x1), max(x0, x1)
        gx0 = x0
        body = rect(x0, yt, x1 - x0, yb - yt)
        if kind == 0:
            wdt = (x1 - x0)
            body = np.array([[x0, yb], [x0, yt + (yb - yt) * 0.42], [x0 + wdt * 0.14, yt], [x1 - wdt * 0.14, yt], [x1, yt + (yb - yt) * 0.42], [x1, yb]])
        # ground shadow
        sh = rect(x0 - (x1 - x0) * 0.05, gy - (yb - yt) * 0.02, (x1 - x0) * 1.1, max(3, (gy - yb) * 1.6))
        c.hatch(sh, ang=0.05, gap=max(2.0, 4 - z * 0.02), w=1.4, a=0.75, seed=seed + 500 + sd)
        c.fill(body, PAPER, mul=False, wob=0)
        c.pl(body, w=lw, close=True, seed=seed + 510 + sd, wob=min(1.3, 25 / z), passes=3 if z < 40 else 1)
        if z < 160:
            if kind == 1:
                c.hatch(body, ang=math.pi / 2 - 0.02, gap=max(4, 420 / z), w=1.2, a=0.45, seed=seed + 520 + sd)
                c.line(x0, yt + (yb - yt) * 0.5, x1, yt + (yb - yt) * 0.5, w=lw * 0.6, seed=seed + 530 + sd, wob=0.5, passes=1)
            else:
                iw = (x1 - x0)
                wn = rect(x0 + iw * 0.18, yt + (yb - yt) * 0.10, iw * 0.64, (yb - yt) * 0.30)
                c.pl(wn, w=lw * 0.7, close=True, seed=seed + 530 + sd, wob=0.6, passes=1)
                c.hatch(wn, ang=-0.8, gap=max(3, 200 / z), w=1.1, a=0.5, seed=seed + 535 + sd)
            # tail lights
            iw = (x1 - x0)
            lh = (yb - yt) * (0.12 if kind != 1 else 0.05)
            ly = yt + (yb - yt) * (0.56 if kind != 1 else 0.9)
            for q in (rect(x0 + iw * 0.04, ly, iw * 0.2, lh), rect(x1 - iw * 0.24, ly, iw * 0.2, lh)):
                c.hatch(q, ang=0.0, gap=2.2, w=1.4, a=0.5 + 0.45 * jam, seed=seed + 540 + sd)
                c.pl(q, w=lw * 0.6, close=True, seed=seed + 545 + sd, wob=0.4, passes=1)
            # wheels
            for q in (rect(x0 + iw * 0.04, yb, iw * 0.16, gy - yb), rect(x1 - iw * 0.20, yb, iw * 0.16, gy - yb)):
                c.hatch(q, ang=math.pi / 2, gap=2.0, w=1.5, a=0.9, seed=seed + 550 + sd)
    # ---- rain
    if rain > 0:
        n = int(260 * rain)
        r = rnds(n * 3, seed, 7).reshape(n, 3)
        x = (r[:, 0] * (W + 400) - 200 + t * 0 - t * 260 * (0.8 + 0.4 * r[:, 2])) % (W + 400) - 200
        y = (r[:, 1] * (H + 200) + t * 1500 * (0.8 + 0.4 * r[:, 2])) % (H + 200) - 100
        ln = 38 + 50 * r[:, 2]
        c.ticks(np.stack([x, y, x - ln * 0.17, y + ln], 1), w=1.5, a=0.55, jit=0.5, seed=seed + 600, boil=False)


def intro_b(c, t, u, d):
    c.begin(t)
    s = _dist(t)
    jam = ease(ramp(t, B(10), B(15.6)))
    dark = ramp(t, B(9), B(15))
    rain = ramp(t, B(12), B(14))
    sway = 14 * math.sin(t * 0.9)
    bump = 3 * math.sin(t * 2.1) + 5 * A.kick(t)
    motorway(c, t, 420 + bump, 960 + sway, s, jam, rain, dark)
    # speed streaks on the tarmac
    v = 1 - jam
    if v > 0.05:
        n = 26
        r = rnds(n * 2, 5, 5).reshape(n, 2)
        ph = (r[:, 0] + t * (1.5 + r[:, 1])) % 1.0
        xw = (r[:, 1] - 0.5) * 10
        z0 = 2 + 30 * (1 - ph) ** 2
        z1 = z0 * (1 + 0.5 * v)
        segs = np.stack([960 + sway - F * xw / z0, 420 + F * CAMH / z0, 960 + sway - F * xw / z1, 420 + F * CAMH / z1], 1)
        c.ticks(segs, w=1.6, a=0.5 * v, jit=0.6, seed=7, boil=False)
    # ---- inside the car: wiper, mirror, dashboard, wheel
    if rain > 0:
        bp = A.beatpos(t) / 2
        sw = 0.5 - 0.5 * math.cos(bp * TAU)
        an = -2.75 + 1.75 * sw
        px, py = 700, 960
        ex, ey = px + 700 * math.cos(an), py + 700 * math.sin(an)
        c.line(px, py, ex, ey, w=7, seed=20, wob=0.8, a=0.95 * rain)
        bx, by = px + 420 * math.cos(an), py + 420 * math.sin(an)
        nx, ny = -math.sin(an), math.cos(an)
        c.line(bx - nx * 0 + 0, by, ex, ey, w=3, seed=21, wob=0.5, a=rain)
        c.line(px + 250 * math.cos(an) + nx * 12, py + 250 * math.sin(an) + ny * 12, ex + nx * 12, ey + ny * 12, w=10, seed=22, wob=0.8, a=0.95 * rain)
    mir = np.array([[820, 34], [1100, 30], [1112, 112], [808, 118]], float)
    c.fill(mir, PAPER, mul=False, wob=0)
    c.hatch(mir, ang=0.3, gap=4.5, w=1.6, a=0.8, seed=30)
    c.pl(mir, w=4.5, close=True, seed=31, passes=3)
    c.line(960, -10, 960, 32, w=7, seed=32)
    xs = np.linspace(-20, W + 20, 40)
    top = 915 + 46 * np.cos((xs - 1380) / 420.0).clip(-1, 1) * 0 - 40 * np.exp(-((xs - 1400) / 330.0) ** 2) + 10 * np.sin(xs * 0.004)
    dash = np.vstack([np.stack([xs, top], 1), [[W + 20, H + 20], [-20, H + 20]]])
    c.fill(dash, PAPER, mul=False, wob=0)
    c.hatch(dash, ang=-0.7, gap=5, w=1.8, a=0.85, seed=33)
    c.hatch(dash, ang=0.75, gap=7, w=1.6, a=0.7, seed=34)
    c.pl(np.stack([xs, top], 1), w=5, seed=35, passes=3)
    # steering wheel (right-hand drive)
    wx, wy = 1400, 1190
    ring = [circ(wx, wy, 345, n=80), circ(wx, wy, 292, n=80)[::-1]]
    c.fill(ring, PAPER, mul=False, wob=0, evenodd=True)
    c.clip(ring[0])
    c.hatch([ring[0]], ang=0.2, gap=6, w=1.6, a=0.5, seed=36)
    c.unclip()
    c.fill([ring[1][::-1]], PAPER, mul=False, wob=0)
    c.hatch([ring[1][::-1]], ang=-0.7, gap=5, w=1.8, a=0.85, seed=33)
    c.hatch([ring[1][::-1]], ang=0.75, gap=7, w=1.6, a=0.7, seed=34)
    rk = 0.03 * math.sin(t * 1.3)
    c.pl(rot(circ(wx, wy, 345, n=80), rk, wx, wy), w=5, close=True, seed=37, passes=3)
    c.pl(rot(circ(wx, wy, 292, n=80), rk, wx, wy), w=3.4, close=True, seed=38, passes=2)
    return dict(flash=0.55 * (1 - ramp(u, 0, 0.18)))


# ------------------------------------------------------------------ verse 1: a comic page of waiting
PA = np.array([[70, 56], [1850, 56], [1850, 520], [70, 566]], float)
PB = np.array([[70, 596], [930, 574], [884, 1024], [70, 1024]], float)
PC = np.array([[962, 573], [1850, 550], [1850, 1024], [916, 1024]], float)


def _clock(c, t, cx_, cy_, r, seed=0, speed=1.0, rev=1.0, back_=False):
    c.pl(circ(cx_, cy_, r), w=4.5, close=True, seed=seed, passes=3, rev=rev)
    c.pl(circ(cx_, cy_, r * 0.93), w=1.8, close=True, seed=seed + 1, passes=1, rev=rev)
    segs = []
    for k in range(60):
        th = k * TAU / 60
        r0 = r * (0.80 if k % 5 == 0 else 0.87)
        segs.append((cx_ + r0 * math.cos(th), cy_ + r0 * math.sin(th), cx_ + r * 0.91 * math.cos(th), cy_ + r * 0.91 * math.sin(th)))
    segs = np.array(segs)
    m = int(60 * rev)
    c.ticks(segs[:m][np.arange(m) % 5 != 0], w=1.6, a=0.8, jit=0.5, seed=seed + 2)
    c.ticks(segs[:m][np.arange(m) % 5 == 0], w=4.2, a=0.95, jit=0.6, seed=seed + 3)
    if rev < 1:
        return
    bp = A.beatpos(t)
    tick = math.floor(bp) + eout(min(1.0, (bp - math.floor(bp)) * 5), 2) - 1
    if back_:
        ms = -speed
        ang_s = ms
        ang_m = ms / 12
    else:
        ang_s = tick * TAU / 60 * speed
        ang_m = 4.9 + tick * TAU / 60 / 14
    for (an, ln, lw, sd) in ((ang_m / 1.0 - 1.2, 0.52, 9, 5), (ang_m * 3, 0.72, 6.5, 6), (ang_s, 0.84, 2.6, 7)):
        an = an - math.pi / 2
        c.line(cx_ - r * 0.1 * math.cos(an), cy_ - r * 0.1 * math.sin(an), cx_ + r * ln * math.cos(an), cy_ + r * ln * math.sin(an), w=lw, seed=seed + sd, wob=0.6, passes=2)
    c.dots([(cx_, cy_)], r * 0.035)


def verse1(c, t, u, d):
    c.begin(t)
    tA, tB, tC = B(16), 32.55, B(23)
    toff = 47.72   # "switch it off"
    # ---------- panel A: grey skies over the motorway
    ra = ramp(t, tA, tA + 0.35)
    c.region(PA, PAPER)
    creep = _dist(B(16)) + 1.2 * (t - B(16))
    motorway(c, t, 300, 900 + 10 * math.sin(t * 0.6), creep, 1.0, 1.0, 1.0, gantry_text=True)
    c.endregion()
    panel_frame(c, PA, seed=1)
    # ---------- panel B: everyone's waiting for the end of the day
    if t >= tB:
        rb = ramp(t, tB, tB + 0.5)
        c.region(PB, PAPER)
        # office windows behind
        segs = []
        for j in range(12):
            for i in range(22):
                x = 80 + i * 40 + (j % 2) * 6
                y = 600 + j * 38
                if rnd(i, j, 3) < 0.75:
                    segs.append((x, y, x + 24, y))
                    segs.append((x, y + 16, x + 24, y + 16))
                    segs.append((x, y, x, y + 16))
                    segs.append((x + 24, y, x + 24, y + 16))
        segs = np.array(segs)
        c.ticks(segs[:int(len(segs) * rb)], w=1.3, a=0.45, jit=0.8, seed=31)
        c.fill(circ(330, 880, 318), PAPER, mul=False, wob=0)
        _clock(c, t, 330, 880, 310, seed=40, rev=ease(ramp(t, tB + 0.1, tB + 0.9)))
        c.endregion()
        panel_frame(c, PB, seed=2)
    # ---------- panel C: the radio's selling the fall of man
    if t >= tC:
        rc = ramp(t, tC, tC + 0.6)
        on = 1.0 if t < toff else 0.0
        c.region(PC, PAPER)
        lv = A.rms(t) * 0.5 + A.kick(t) * 0.8
        # speaker
        sx, sy, sr = 1180, 800, 170
        body = np.array([[985, 620], [1640, 606], [1650, 1000], [975, 1000]], float)
        c.pl(body, w=4.2, close=True, seed=50, passes=3, rev=rc)
        c.hatch(np.array([[985, 620], [1640, 606], [1642, 650], [984, 664]]), ang=0.6, gap=6, a=0.6, seed=51, rev=rc)
        for k in range(5):
            rr = sr * (1 - k * 0.19) * (1 + 0.05 * lv * on * (1 if k % 2 else -1))
            c.pl(circ(sx, sy, rr), w=3.6 if k == 0 else 2.2, close=True, seed=52 + k, rev=rc, passes=2 if k == 0 else 1)
        c.dots([(sx, sy)], 16)
        # dial + knobs
        c.pl(rect(1400, 700, 210, 70), w=2.6, close=True, seed=60, rev=rc)
        c.ticks([(1410 + k * 13, 700, 1410 + k * 13, 716 if k % 4 else 730) for k in range(15)], w=1.4, a=0.8, seed=61)
        nx = 1420 + 170 * (0.5 + 0.4 * math.sin(t * 0.8))
        c.line(nx, 696, nx, 774, w=3.2, seed=62, col=None)
        for k in range(3):
            c.pl(circ(1430 + k * 75, 880, 26), w=2.8, close=True, seed=63 + k, rev=rc)
            an = 0.6 * k + (2.2 if (k == 2 and not on) else 0.7)
            c.line(1430 + k * 75, 880, 1430 + k * 75 + 24 * math.cos(an), 880 + 24 * math.sin(an), w=3.0, seed=66 + k)
        # antenna
        c.line(1600, 610, 1790, 520, w=3.0, seed=70, rev=rc)
        if on and rc >= 1:
            # falling chart: the fall of man, for sale
            pr = ramp(t, tC + 1.1, tC + 3.4)
            n = 13
            xs = np.linspace(1668, 1826, n)
            ys = np.linspace(668, 968, n) + ((np.arange(n) % 2) * 2 - 1) * 20 * (np.arange(n) > 0) * (np.arange(n) < n - 1)
            hp = c.pl(np.stack([xs, ys], 1), w=4.6, seed=75, rev=pr, wob=0.8)
            if pr >= 1:
                c.pl([[1790, 962], [1826, 968], [1822, 930]], w=4.6, seed=76, wob=0.5)
            # jagged broadcast bolts from the antenna
            for k in range(5):
                ph = (t * 1.6 + k * 0.2) % 1.0
                rr = 30 + 190 * ph
                th = np.linspace(-2.5, -0.2, 14)
                jag = rr * (1 + 0.13 * ((np.arange(14) % 2) * 2 - 1))
                c.pl(np.stack([1790 + jag * np.cos(th), 520 + jag * np.sin(th)], 1), w=2.6, a=0.95 * (1 - ph), seed=80 + k, passes=1, wob=0.8)
        c.endregion()
        if on and rc >= 1:
            pass
        panel_frame(c, PC, seed=3)
        if not on:
            # click: little burst at the knob
            p = ramp(t, toff, toff + 0.25)
            for k in range(7):
                th = k * TAU / 7 + 0.3
                c.line(1580 + (34 + 30 * p) * math.cos(th), 880 + (34 + 30 * p) * math.sin(th), 1580 + (46 + 60 * p) * math.cos(th), 880 + (46 + 60 * p) * math.sin(th),
                       w=3.2, seed=90 + k, a=1 - p * 0.5)
            c.script('off', 1700, 990, 60, rev=ramp(t, toff, toff + 0.3), w=3.0, seed=9, align='l')
    return dict(flash=0.35 * (1 - ramp(u, 0, 0.15)))


# ------------------------------------------------------------------ "I've got a better plan": first colour
def plan_dot(c, t, u, d):
    c.begin(t)
    p = back(ramp(u, 0.0, 0.22), 3.0)
    x, y = 960, 540
    pl_ = A.pulse(t, 5)
    r = 46 * p * (1 + 0.12 * pl_)
    c.fill(circ(x, y, r), CORAL, wob=1.2, seed=1, off=(0, 0))
    c.pl(circ(x + 5, y + 4, r + 4), w=3.2, close=True, seed=2, rev=ramp(u, 0.1, 0.4), passes=3)
    # rays grow on the beats
    n = 16
    for k in range(n):
        tb = 48.55 + k * 0.11
        g = eout(ramp(t, tb, tb + 0.35))
        if g <= 0:
            continue
        th = k * TAU / n - math.pi / 2
        r0 = 80 + 10 * pl_
        r1 = r0 + (120 + 420 * ramp(t, 49.2, 50.4) + (40 if k % 2 else 0)) * g
        c.line(x + r0 * math.cos(th), y + r0 * math.sin(th), x + r1 * math.cos(th), y + r1 * math.sin(th), w=3.4, seed=10 + k, passes=2)
    return dict(flash=0.8 * (1 - ramp(u, 0, 0.2)))


# ------------------------------------------------------------------ pre-chorus 1: lettering
def _lay(items, size, x0, gap=0.26, font='blk'):
    xs = []
    x = x0
    for it in items:
        w_ = text_width(it[0], size, font)
        xs.append(x)
        x += w_ + size * gap
    return xs, x - size * gap


CUBE_V = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
CUBE_E = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
PIPS = {1: [(0, 0)], 2: [(-.5, -.5), (.5, .5)], 3: [(-.5, -.5), (0, 0), (.5, .5)], 4: [(-.5, -.5), (.5, .5), (-.5, .5), (.5, -.5)],
        5: [(-.5, -.5), (.5, .5), (-.5, .5), (.5, -.5), (0, 0)], 6: [(-.5, -.55), (.5, .55), (-.5, .55), (.5, -.55), (-.5, 0), (.5, 0)]}
FACES = [((1, 0, 0), (0, 1, 0), (0, 0, 1), 1), ((-1, 0, 0), (0, 1, 0), (0, 0, 1), 6), ((0, 1, 0), (1, 0, 0), (0, 0, 1), 2),
         ((0, -1, 0), (1, 0, 0), (0, 0, 1), 5), ((0, 0, 1), (1, 0, 0), (0, 1, 0), 3), ((0, 0, -1), (1, 0, 0), (0, 1, 0), 4)]


def _rotm(ax, ay, az):
    cx_, sx_ = math.cos(ax), math.sin(ax)
    cy_, sy_ = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx_, -sx_], [0, sx_, cx_]])
    Ry = np.array([[cy_, 0, sy_], [0, 1, 0], [-sy_, 0, cy_]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def die(c, x, y, s, ax, ay, az, seed=0, fillc=None):
    R = _rotm(ax, ay, az)
    V = CUBE_V @ R.T
    P2 = V[:, :2] * s + (x, y)
    hull = cv2.convexHull(P2.astype(np.float32)).reshape(-1, 2).astype(float)
    c.fill(hull, PAPER, mul=False, wob=0)
    if fillc is not None:
        c.fill(hull, fillc, off=(7, 6), seed=seed)
    pips = []
    for (nrm, a_, b_, num) in FACES:
        n3 = R @ np.array(nrm, float)
        if n3[2] <= 0.05:
            continue
        ua, ub = R @ np.array(a_, float), R @ np.array(b_, float)
        corners = [n3 + sa * ua + sb * ub for (sa, sb) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        q = np.array([(x + p[0] * s, y + p[1] * s) for p in corners])
        c.pl(q, w=3.2, close=True, seed=seed + num, wob=0.9)
        for (pu, pv) in PIPS[num]:
            p = n3 + pu * ua * 1.0 + pv * ub * 1.0
            pips.append((x + p[0] * s, y + p[1] * s, s * 0.11 * (0.5 + 0.5 * n3[2])))
    if pips:
        pp = np.array(pips)
        c.dots(pp[:, :2], pp[:, 2])


def _strike(c, bb, t, t0, col=CORAL, seed=0):
    r = eout(ramp(t, t0, t0 + 0.16))
    if r <= 0:
        return
    x0, y0, x1, y1 = bb
    my = (y0 + y1) / 2
    c.line(x0 - 40, my + 26, x1 + 40, my - 30, w=17, col=col, a=1.0, seed=seed, rev=r, passes=1, wob=1.5)
    c.line(x0 - 30, my + 44, x1 + 46, my - 8, w=9, col=col, a=1.0, seed=seed + 1, rev=ramp(t, t0 + 0.08, t0 + 0.22), passes=1, wob=1.5)


def _topline(c, t, T, keys, x, align, size=128):
    words = ("DON'T", 'TELL', 'ME', 'THE')
    xs, tw = _lay([(w_,) for w_ in words], size, 0)
    x0 = x if align == 'l' else x - tw
    for (w_, key, xx) in zip(words, keys, xs):
        pop_word(c, w_, x0 + xx, 330, size, t, T[key], align='l', seed=sum(map(ord, key)) % 99, hatch=dict(gap=7, a=0.6))


def pre1_odds(c, t, u, d):
    c.begin(t)
    T = {'dont': 50.54, 'tell': 50.74, 'me': 51.12, 'the': 51.38, 'odds': 51.66}
    _topline(c, t, T, ('dont', 'tell', 'me', 'the'), 130, 'l')
    if t >= T['odds']:
        sc = back(min(1.0, (t - T['odds']) / 0.16), 2.4)
        bb = c.text('ODDS', 120, 800, 470 * (0.6 + 0.4 * sc), align='l', seed=6, fill=YEL, off=(12, 10), w=4.5, rot=-0.035)
        _strike(c, bb, t, 51.95, seed=7)
    # dice tumble through
    for k in range(4):
        px = 2150 - (u + 0.2) * (560 + 90 * k) - k * 190
        py = 200 + k * 215 + 60 * math.sin(u * 5 + k)
        die(c, px, py, 84 + 20 * (k % 2), u * (2.2 + k * 0.5) + k, u * (1.7 + 0.3 * k) + 2 * k, u * 1.3 + k, seed=20 + k * 10, fillc=YEL if k % 2 == 0 else None)
    return dict(flash=0.5 * (1 - ramp(u, 0, 0.12)))


def _calpage(c, x, y, s, ang, num, seed=0, fillc=None):
    pg = rot(rect(-s * 0.5, -s * 0.6, s, s * 1.2), ang) + (x, y)
    c.fill(pg, PAPER, mul=False, wob=0)
    hd = rot(rect(-s * 0.5, -s * 0.6, s, s * 0.26), ang) + (x, y)
    c.fill(hd, fillc if fillc is not None else CORAL, off=(5, 4), seed=seed)
    c.pl(pg, w=3.2, close=True, seed=seed, wob=1.0)
    c.pl(hd, w=2.4, close=True, seed=seed + 1, wob=0.8, passes=1)
    cs, wd = glyph_contours('adv', num, s * 0.62)
    cs = [rot(q + (-wd / 2, s * 0.42), ang) + (x, y) for q in cs]
    c.fill(cs, c.ink, mul=False, wob=0.5, seed=seed + 2)
    for k in (-1, 1):
        p = rot(np.array([[k * s * 0.25, -s * 0.68], [k * s * 0.25, -s * 0.52]]), ang) + (x, y)
        c.pl(p, w=5, seed=seed + 5 + k, wob=0.3, passes=1)


def pre1_date(c, t, u, d):
    c.begin(t)
    T = {'dont': 52.34, 'tell': 52.54, 'me': 52.96, 'the': 53.22, 'date': 53.42}
    _topline(c, t, T, ('dont', 'tell', 'me', 'the'), 1790, 'r')
    if t >= T['date']:
        sc = back(min(1.0, (t - T['date']) / 0.16), 2.4)
        bb = c.text('DATE', 1800, 800, 470 * (0.6 + 0.4 * sc), align='r', seed=6, fill=CORAL, off=(12, 10), w=4.5, rot=0.03)
        _strike(c, bb, t, 53.72, col=YEL, seed=7)
    for k in range(6):
        ph = u * (0.9 + 0.13 * k) + k * 0.31
        px = 160 + ((k * 331) % 1000) * 0.9 + 60 * math.sin(ph * 3 + k)
        py = -260 + ph * 620 + (k % 3) * 80 - k * 70
        _calpage(c, px + (780 if k % 2 else -40), py, 170 + 30 * (k % 3), 0.5 * math.sin(ph * 2.6 + k * 2), str(31 - k * 5 if k % 2 else k * 3 + 1), seed=30 + k * 10,
                 fillc=CORAL if k % 2 else YEL)
    return dict(flash=0.5 * (1 - ramp(u, 0, 0.12)))


def pre1_future(c, t, u, d):
    c.begin(t)
    # ruled page
    for k in range(9):
        y = 190 + k * 105
        c.line(120, y, 1800, y, w=1.6, a=0.55, seed=10 + k, rev=eout(ramp(u, k * 0.03, 0.25 + k * 0.03)), passes=1, col=CYAN if True else None)
    c.line(300, 60, 300, 1030, w=2.2, a=0.9, seed=30, rev=eout(ramp(u, 0.05, 0.35)), col=CORAL, passes=1)
    h1 = c.script("The future's", 360, 400, 215, align='l', rev=ramp(t, 54.36, 55.0), w=5.0, seed=1)
    h2 = c.script('not written', 520, 610, 215, align='l', rev=ramp(t, 55.02, 56.25), w=5.0, seed=2)
    head = h2 if t >= 55.02 and h2 is not None else h1
    if head is not None and t < 56.3:
        pencil(c, head[0], head[1], ang=-0.9 + 0.08 * math.sin(t * 17), s=1.5)
    elif t >= 56.3:
        k = ein(ramp(t, 56.3, 56.5))
        pencil(c, (head or (1500, 610))[0] + 500 * k, (head or (1500, 610))[1] - 300 * k, ang=-0.9, s=1.5)
    return dict(flash=0.5 * (1 - ramp(u, 0, 0.12)))


def pre1_late(c, t, u, d):
    c.begin(t)
    T = {'its': 56.70, 'not': 57.08, 'too': 57.32, 'late': 57.80}
    x, y = 960, 540
    g = ramp(u, 0, d)
    # sunburst winding up
    r = 120 + 900 * ein(g, 2.2)
    c.fill(circ(x, y, r), YEL, wob=2.0, seed=1)
    sun_rays(c, x, y, r + 30, r + 160 + 80 * A.pulse(t, 6), n=28, ang=-t * 1.4, seed=40, w=3.4)
    # a clock running backwards
    cr = 300
    c.pl(circ(x, y, cr), w=5, close=True, seed=2, passes=3)
    segs = [(x + cr * 0.82 * math.cos(k * TAU / 12), y + cr * 0.82 * math.sin(k * TAU / 12), x + cr * 0.93 * math.cos(k * TAU / 12), y + cr * 0.93 * math.sin(k * TAU / 12)) for k in range(12)]
    c.ticks(segs, w=5, a=0.95, seed=3)
    back_ang = -u * 9.0 * (1 + u)
    for (an, ln, lw, sd) in ((back_ang / 12 + 1.0, 0.5, 11, 5), (back_ang, 0.78, 7, 6)):
        an -= math.pi / 2
        c.line(x, y, x + cr * ln * math.cos(an), y + cr * ln * math.sin(an), w=lw, seed=sd, wob=0.6)
    c.dots([(x, y)], 14)
    pop_word(c, "IT'S", 250, 300, 200, t, T['its'], align='l', seed=11, fill=CORAL, off=(9, 8), w=3.6)
    pop_word(c, 'NOT', 1690, 300, 200, t, T['not'], align='r', seed=12, fill=CORAL, off=(9, 8), w=3.6)
    pop_word(c, 'TOO', 250, 960, 230, t, T['too'], align='l', seed=13, fill=CORAL, off=(9, 8), w=3.6)
    pop_word(c, 'LATE', 1690, 960, 230, t, T['late'], align='r', seed=14, fill=CORAL, off=(9, 8), w=3.6)
    return dict(flash=0.5 * (1 - ramp(u, 0, 0.12)))


def timeline():
    return [
        (0.0, B(8), intro_a),
        (B(8), B(16), intro_b),
        (B(16), 48.30, verse1),
        (48.30, 50.40, plan_dot),
        (50.40, 52.20, pre1_odds),
        (52.20, 54.20, pre1_date),
        (54.20, 56.50, pre1_future),
        (56.50, B(32), pre1_late),
    ]
