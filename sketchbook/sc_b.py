"""The chorus, in three escalating levels."""
from motifs import *

CONF_COLS = (CORAL, YEL, CYAN, PINK, BLUE)


def caption(c, s, t, t0, t1, x=110, y=1000, size=62, rot=-0.012, seed=0):
    """comic caption box with the line written in as it is sung"""
    if t < t0 - 0.2:
        return
    st, wd = hershey(s, size)
    p = back(ramp(t, t0 - 0.2, t0 - 0.02), 1.6)
    bx = rect(x - 30, y - size * 1.25, (wd + 60) * p, size * 1.75)
    bx = rot_(bx, rot, x, y)
    c.fill(bx + (9, 8), c.ink, mul=False, wob=1.0, seed=seed + 1)
    c.fill(bx, PAPER if not c.night else NIGHT, mul=False, wob=1.0, seed=seed)
    c.pl(bx, w=3.2, close=True, seed=seed + 2, wob=1.0)
    c.script(s, x, y, size, align='l', rev=ramp(t, t0, t1), w=3.3, seed=seed + 3, rot=rot)


def confetti(c, t, t0, n, seed, cols=CONF_COLS, avoid=None, rate=2.0, size=(36, 70)):
    """memphis shapes popping in on successive half-beats from t0"""
    b0 = A.beatpos(t0)
    bn = A.beatpos(t)
    for k in range(n):
        birth = b0 + k / rate
        if bn < birth:
            break
        x = 80 + rnd(seed, k, 1) * (W - 160)
        y = 70 + rnd(seed, k, 2) * (H - 140)
        if avoid is not None and avoid(x, y):
            continue
        s = size[0] + rnd(seed, k, 3) * (size[1] - size[0])
        pop = min(1.0, (bn - birth) * 3.0)
        memphis(c, int(rnd(seed, k, 4) * 7), x, y, s, ang=rnd(seed, k, 5) * TAU + 0.3 * math.sin(t * 2 + k), col=cols[k % len(cols)],
                seed=seed * 100 + k, pop=pop, col2=c.ink)


# ------------------------------------------------------------------ 1. UNTIL / FURTHER / NOTICE
def ch_title(c, t, u, d, lvl, wt):
    c.begin(t)
    pu = A.pulse(t, 5)
    sx, sy = (1500, 560) if lvl < 3 else (1420, 540)
    sr = (380 + 40 * lvl) * (1 + 0.035 * pu) * back(ramp(u, 0, 0.3), 1.2)
    cols = ((YEL, YEL, CORAL), (YEL, CORAL, PINK), (YEL, CORAL, PINK))[lvl - 1]
    sun_rays(c, sx, sy, sr + 34, sr + 150 + 60 * pu, n=30, ang=t * 0.35, seed=60, w=3.6, alt=0.5, col=None)
    if lvl >= 2:
        sun_rays(c, sx, sy, sr + 34, sr + 420, n=15, ang=t * 0.35 + 0.1, seed=90, w=9, alt=1.0, col=CYAN if lvl == 2 else PINK, a=1.0)
    sun_disc(c, sx, sy, sr, phase=t * 1.1, cols=cols, seed=1)
    c.pl(circ(sx, sy, sr), w=4.2, close=True, seed=2, passes=3)
    if lvl >= 2:
        confetti(c, t, t - u, 26 if lvl == 2 else 44, seed=lvl * 7, avoid=lambda x, y: (x < 1560 and 120 < y < 990), rate=3.0 if lvl == 3 else 2.0)
    words = (('UNTIL', 340, 'until'), ('FURTHER', 640, 'further'), ('NOTICE', 940, 'notice'))
    fills = ((None, None, None), (CYAN, PINK, YEL), (YEL, CYAN, PINK))[lvl - 1]
    shadows = ((CORAL, CORAL, CORAL), (BLUE, BLUE, BLUE), (BLUE, CORAL, BLUE))[lvl - 1]
    for k, (w_, y, key) in enumerate(words):
        t0 = wt[key]
        if t < t0:
            continue
        sc = back(min(1.0, (t - t0) / 0.15), 2.6)
        size = 318 * (0.62 + 0.38 * sc) * (1 + 0.012 * pu * lvl)
        c.text(w_, 96, y, size, align='l', seed=10 + k, knock=True, fill=fills[k], off=(0, 0), shadow=(shadows[k], (16, 14)), w=5.0,
                   rot=(-0.02, 0.012, -0.012)[k])
    return dict(flash=0.7 * (1 - ramp(u, 0, 0.14)))


# ------------------------------------------------------------------ 2. I believe in the machine
def _gear_train(c, t, specs, th0, fills, seed=0, w=3.0):
    """specs: list of (x, y, teeth). radius follows teeth so that the train meshes"""
    mod = specs[0][3]
    ang = [th0]
    for i in range(1, len(specs)):
        x0, y0, n0, _ = specs[i - 1]
        x1, y1, n1, _ = specs[i]
        phi = math.atan2(y1 - y0, x1 - x0)
        ang.append(-(ang[i - 1] - phi) * n0 / n1 + phi + math.pi + math.pi / n1 * 0.2)
    for i, (x, y, n, _) in enumerate(specs):
        gear(c, x, y, mod * n, n, ang[i], seed=seed + i * 20, fillc=fills[i % len(fills)], w=w, spokes=5 if n > 9 else 3, depth=1.9 / n)


def ch_machine(c, t, u, d, lvl, wt):
    c.begin(t)
    bp = A.beatpos(t)
    th = 0.42 * (math.floor(bp) + eout(min(1.0, (bp - math.floor(bp)) * 2.2), 3))
    m = 15.5
    def chain(x, y, teeth, a0):
        out = [(x, y, teeth[0], m)]
        for i in range(1, len(teeth)):
            px, py, pn, _ = out[-1]
            dist = m * (pn + teeth[i]) * 1.035 + m * 1.9 * 0.5
            an = a0[i - 1]
            out.append((px + dist * math.cos(an), py + dist * math.sin(an), teeth[i], m))
        return out
    if lvl == 1:
        specs = chain(330, 560, (20, 11, 16, 9, 22), (-0.42, 0.55, -0.5, 0.42))
        _gear_train(c, t, specs, th, (CORAL, YEL, None, CORAL, YEL), seed=5)
        caption(c, 'I believe in the machine', t, wt['believe'] - 0.5, wt['machine'] + 0.7, x=1000, y=1000)
    else:
        # the plotter: a rosette being drawn while the gears drive it
        cols = (CORAL, CYAN, YEL, PINK, BLUE)
        cxp, cyp = 1160, 540
        nlay = 3 if lvl == 2 else 5
        for k in range(nlay):
            R = 470 - k * 22
            r_ = (R * (5 / 17), R * (7 / 23), R * (3 / 11), R * (8 / 19), R * (4 / 13))[k]
            turns = (5, 7, 3, 8, 4)[k]
            pts = hypotrochoid(cxp, cyp, R, r_, r_ * (0.9 - 0.1 * k), turns, n=1100, ang=t * (0.12 + 0.05 * k) * (1 if k % 2 else -1))
            rv = ease(ramp(u, k * 0.25, 1.9 + k * 0.3)) if lvl == 2 else 1.0
            hp = c.pl(pts, w=2.6, a=0.95, col=cols[k], seed=40 + k, rev=rv, passes=1, wob=0.4, boil=0.3, seg=9)
            if hp is not None and rv < 1:
                c.dots([hp], 9, col=c.ink)
        specs = chain(250, 300, (16, 9, 13), (1.25, 0.25))
        _gear_train(c, t, specs, th, (YEL, CORAL, CYAN), seed=5)
        if lvl == 3:
            specs2 = chain(1740, 830, (14, 9), (-1.9,))
            _gear_train(c, t, specs2, -th, (PINK, YEL), seed=95)
            c.pl(circ(cxp, cyp, 500), w=3.4, close=True, seed=70, passes=2)
            sun_rays(c, cxp, cyp, 520, 580 + 50 * A.pulse(t, 5), n=48, ang=-t * 0.25, seed=71, w=2.8)
    return dict(flash=0.5 * (1 - ramp(u, 0, 0.12)))


# ------------------------------------------------------------------ 3. turning the wind into light
_FL = None


def flowlines():
    global _FL
    if _FL is None:
        rs = np.random.RandomState(4)
        N, M, step = 620, 120, 11.0
        p = np.stack([rs.rand(N) * (W + 900) - 700, rs.rand(N) * (H + 200) - 100], 1)
        out = np.zeros((N, M, 2))
        for i in range(M):
            out[:, i] = p
            x, y = p[:, 0], p[:, 1]
            th = 0.55 * np.sin(x * 0.0035 + 1.3) * np.cos(y * 0.0052 + 0.4) + 0.35 * np.sin((x * 0.6 + y) * 0.008 + 2.0) + 0.2 * np.sin(y * 0.013)
            p = p + step * np.stack([np.cos(th), np.sin(th)], 1)
        _FL = (out, rs.rand(N), rs.rand(N))
    return _FL


def wind(c, t, n=400, L=26, speed=46.0, split=None, cols=(None, YEL), w=(2.0, 3.6), a=(0.75, 1.0), seed=0):
    fl, ph, sp = flowlines()
    N, M, _ = fl.shape
    left, right = [], []
    for i in range(min(n, N)):
        h = (t * speed * (0.6 + 0.8 * sp[i]) + ph[i] * (M + L)) % (M + L)
        a0, b0 = int(max(0, h - L)), int(min(M, h))
        if b0 - a0 < 2:
            continue
        q = fl[i, a0:b0]
        if split is not None and q[-1, 0] > split(q[-1, 1]):
            right.append(q)
        else:
            left.append(q)
    if left:
        c.polys(left, w=w[0], a=a[0], col=cols[0])
    if right:
        c.polys(right, w=w[1], a=a[1], col=cols[1])


def ch_wind(c, t, u, d, lvl, wt):
    c.begin(t)
    spin = t * (3.2 + 0.6 * lvl)
    if lvl == 1:
        wind(c, t, n=330, split=lambda y: 1000 + 0.12 * (y - 540), cols=(None, YEL), w=(2.2, 4.2))
        gy = 930
        c.line(-20, gy, W + 20, gy, w=3.4, seed=1, passes=3)
        c.hatch(rect(-20, gy, W + 40, 200), ang=0.1, gap=11, a=0.5, seed=2)
        for k, (x, h) in enumerate(((560, 520), (840, 640), (1130, 470))):
            turbine(c, x, gy, h, spin * (1 + 0.1 * k) + k * 0.7, seed=10 + 30 * k, w=3.4, rev=ramp(u, 0.05 * k, 0.45 + 0.05 * k))
        # light on the right
        lx, ly = 1640, 400
        pu = A.pulse(t, 4)
        c.fill(circ(lx, ly, 150 * (1 + 0.05 * pu)), YEL, seed=3)
        c.pl(circ(lx + 6, ly + 5, 156), w=3.6, close=True, seed=4, passes=3)
        sun_rays(c, lx, ly, 185, 300 + 60 * pu, n=18, ang=t * 0.5, seed=20, w=3.4)
        caption(c, 'turning the wind into light', t, wt['turning'], wt['light'] + 0.6)
    elif lvl == 2:
        # a field of turbines marching to the horizon, sun low
        hy = 610
        sun_disc(c, 960, hy, 300, phase=t, cols=(YEL, CORAL, PINK), seed=1)
        c.fill(rect(-10, hy, W + 20, H - hy + 10), PAPER, mul=False, wob=0)
        c.pl(circ(960, hy, 300, math.pi, TAU), w=3.6, seed=2, passes=3)
        wind(c, t, n=300, split=lambda y: -1e9 if y < hy else 1e9, cols=(None, CYAN), w=(2.0, 3.0), a=(0.5, 0.9), L=20)
        c.fill(rect(-10, hy, W + 20, H - hy + 10), PAPER, mul=False, wob=0)
        c.line(-20, hy, W + 20, hy, w=3.4, seed=3, passes=3)
        gridfloor(c, hy, 960, t * 1.2, col=CYAN, w=2.4, a=0.9, spacing=260)
        rows = []
        for r in range(5):
            z = 1.0 + r * 0.75 - ((t * 0.5) % 0.75)
            for sgn in (-1, 1):
                for j in range(1, 4):
                    rows.append((z, sgn * (j - 0.35) * 620))
        for (z, xw) in sorted(rows, key=lambda q: -q[0]):
            if z < 0.72:
                continue
            x = 960 + xw / z
            gy = hy + 300 / z
            h = 470 / z
            if x < -200 or x > W + 200:
                continue
            turbine(c, x, gy, h, spin + xw * 0.01 + z, seed=int(abs(xw)) + 7, w=max(1.6, 3.6 / z), fillc=PAPER if False else None)
    else:
        # everything at once: colour wind through a wall of turbines
        fl_cols = (CYAN, BLUE)
        wind(c, t, n=620, split=lambda y: 900 + 0.3 * (y - 540), cols=(CYAN, YEL), w=(3.0, 4.4), a=(1.0, 1.0), L=32, speed=58)
        wind(c, t + 9.3, n=260, cols=(PINK, PINK), w=(2.6, 2.6), a=(0.95, 0.95), L=22, speed=64)
        gy = 1010
        c.line(-20, gy, W + 20, gy, w=3.6, seed=1, passes=3)
        for k, (x, h) in enumerate(((240, 560), (520, 760), (830, 640), (1120, 840), (1420, 600), (1700, 720))):
            turbine(c, x, gy, h, spin * (1 + 0.07 * k) + k * 0.9, seed=10 + 30 * k, w=3.8, fillc=PAPER)
    return dict(flash=0.5 * (1 - ramp(u, 0, 0.12)))


# ------------------------------------------------------------------ 4. making the dirty things clean
_SCRIB = None


def scribble(n=900, seed=3):
    """a chaotic single line (unit box -1..1)"""
    global _SCRIB
    if _SCRIB is None:
        _SCRIB = {}
    if (n, seed) not in _SCRIB:
        s = np.linspace(0, TAU, n)
        r1, r2, r3 = rnd(seed, 1), rnd(seed, 2), rnd(seed, 3)
        x = 0.55 * np.sin(s * (17.3 + r1 * 3) + r2 * 6) + 0.30 * np.sin(s * 41.7 + 1 + r3 * 5) + 0.15 * np.sin(s * 89.1)
        y = 0.55 * np.cos(s * (23.1 + r2 * 3) + 0.5 + r1 * 6) + 0.30 * np.sin(s * 37.9 + r2) + 0.15 * np.cos(s * 71.3)
        env = 0.75 + 0.25 * np.sin(s * 3 + r3 * 6)
        _SCRIB[(n, seed)] = np.stack([x * env, y * env], 1)
    return _SCRIB[(n, seed)]


def ridges(c, t, y0, y1, rows=16, amp=150, linec=None, fillc=None, x0=-20, x1=W + 20, seed=0, lw=3.0, cxm=960, a=1.0):
    n = 130
    xs = np.linspace(x0, x1, n)
    dc = np.abs(xs - cxm) / (W * 0.5)
    for r in range(rows):
        k = r / max(1, rows - 1)
        yy = y0 + (y1 - y0) * k ** 1.25
        sp = A.spectrum(t - (rows - 1 - r) * 0.085)
        prof = np.interp(np.clip(dc * 1.15, 0, 1) * 23, np.arange(24), sp)
        win = np.exp(-(dc / 0.62) ** 2.2)
        noise = sn1(xs * 0.012 + r * 3.1 + t * 0.6, seed + r)
        hgt = (prof ** 1.6 * win * amp * (0.55 + 0.75 * k) + 7 * noise * (0.3 + win))
        line = np.stack([xs, yy - hgt], 1)
        poly = np.vstack([line, [[x1, yy + 400], [x0, yy + 400]]])
        if callable(fillc):
            fc = fillc(k)
        else:
            fc = fillc
        c.fill(poly, NIGHT if c.night else PAPER, mul=False, wob=0)
        if fc is not None:
            c.fill(poly, fc, wob=0, mul=False, a=a)
        c.pl(line, w=lw * (0.7 + 0.6 * k), col=linec, seed=seed + r, wob=0.6, boil=0.25, passes=1, seg=14)


def ch_clean(c, t, u, d, lvl, wt):
    c.begin(t)
    if lvl == 1:
        gy = 860
        wipe = -300 + (W + 700) * ease(ramp(u, 0.5, d - 0.35))
        wx = lambda y: wipe + 60 * math.sin(y * 0.012 + t * 5)
        ys = np.linspace(-20, H + 20, 40)
        edge = np.array([[wx(y), y] for y in ys])
        clean_poly = np.vstack([[[-40, -20]], edge, [[-40, H + 20]]])
        dirty_poly = np.vstack([edge, [[W + 40, H + 20], [W + 40, -20]]])
        def stacks(clean):
            c.line(-20, gy, W + 20, gy, w=3.4, seed=1, passes=3)
            for k, (x, wd, h) in enumerate(((300, 90, 420), (640, 70, 330), (1000, 110, 480), (1420, 80, 380), (1700, 60, 290))):
                q = np.array([[x - wd / 2, gy], [x - wd * 0.36, gy - h], [x + wd * 0.36, gy - h], [x + wd / 2, gy]])
                c.pl(q, w=3.4, seed=10 + k, passes=3)
                c.ticks([(x - wd * 0.40, gy - h + 26 + j * 16, x + wd * 0.40, gy - h + 26 + j * 16) for j in range(3)], w=2.0, a=0.8, seed=20 + k)
                if not clean:
                    c.hatch(q, ang=1.2, gap=6, a=0.6, seed=30 + k)
                    sc = scribble(700, 3 + k)
                    grow = ramp(u, 0, 0.5)
                    c.pl(sc * (190 + 60 * (k % 2), 150) * (0.7 + 0.3 * grow) + (x + 30 * math.sin(t * 2 + k), gy - h - 130 - 20 * math.sin(t * 3 + k)),
                         w=2.6, a=0.9, seed=40 + k, passes=1, wob=1.2, seg=9)
        # dirty world
        c.region(dirty_poly, PAPER)
        c.hatch(rect(-20, -20, W + 40, gy), ang=-0.4, gap=12, a=0.4, seed=5)
        stacks(False)
        c.hatch(rect(-20, gy, W + 40, 300), ang=0.2, gap=7, a=0.7, seed=6)
        c.endregion()
        # clean world
        c.region(clean_poly, PAPER)
        sun_disc(c, 420, 300, 150, phase=t, cols=(YEL, YEL, CORAL), seed=7)
        c.pl(circ(420, 300, 150), w=3.4, close=True, seed=8, passes=2)
        stacks(True)
        for j in range(7):
            yy = gy + 26 + j * 30
            xs = np.linspace(-20, W + 20, 90)
            c.pl(np.stack([xs, yy + 9 * np.sin(xs * 0.02 + t * 3 + j * 1.3)], 1), w=4.0, col=CYAN, seed=60 + j, passes=1, wob=0.4, a=1.0)
        c.endregion()
        # the wipe edge itself
        c.pl(edge, w=12, col=CYAN, a=1.0, seed=70, passes=1, wob=0.8)
        c.pl(edge + (16, 0), w=3.2, seed=71, passes=2)
        caption(c, 'making the dirty things clean', t, wt['making'], wt['clean'] + 0.5, x=110, y=1010)
    else:
        hy = 430
        sr = 250 if lvl == 2 else 330
        cols = (YEL, CORAL, PINK)
        sun_rays(c, 960, hy, sr + 30, sr + 150 + 70 * A.pulse(t, 5), n=26, ang=t * 0.3, seed=30, w=3.4)
        sun_disc(c, 960, hy, sr, phase=t * 1.0, cols=cols, seed=1)
        c.pl(circ(960, hy, sr), w=3.8, close=True, seed=2, passes=3)
        if lvl == 3:
            birds(c, t, n=11, seed=4, y0=170, speed=260, x0=-100, t0=t - u, w=3.0, scale=1.3)
        fc = (lambda k: mixc(CYAN, BLUE, k * 0.9)) if lvl == 3 else (lambda k: mixc(PAPER, CYAN, 0.25 + 0.75 * k))
        ridges(c, t, hy + 60, H + 40, rows=15 if lvl == 2 else 18, amp=190 if lvl == 2 else 260, linec=None if lvl == 2 else PAPER, fillc=fc, seed=5,
               lw=3.0)
    return dict(flash=0.5 * (1 - ramp(u, 0, 0.12)))


# ------------------------------------------------------------------ 5. until further notice / tomorrow's not a dream
def _mountains(c, hy, seed, amp, col=None, fillc=None, x0=-20, x1=W + 20, w=3.0, rev=1.0, gap=260):
    n = 28
    xs = np.linspace(x0, x1, n)
    dc = np.abs(xs - 960)
    ys = hy - amp * (0.35 + 0.65 * rnds(n, seed, 1)) * np.clip((dc - gap) / 500.0, 0, 1) ** 0.8
    line = np.stack([xs, ys], 1)
    poly = np.vstack([line, [[x1, hy], [x0, hy]]])
    c.fill(poly, NIGHT if c.night else PAPER, mul=False, wob=0)
    if fillc is not None:
        c.fill(poly, fillc, seed=seed, off=(6, 4))
    c.pl(line, w=w, col=col, seed=seed, rev=rev)
    segs = []
    for i in range(1, n - 1):
        if ys[i] < hy - 12:
            for j in (-1, 1):
                segs.append((xs[i], ys[i], xs[i] + j * (xs[1] - xs[0]) * 0.8, hy))
    c.ticks(segs, w=1.6, a=0.6, seed=seed, col=col)


def ch_grid(c, t, u, d, lvl, wt):
    c.begin(t)
    hy = 600
    pu = A.pulse(t, 5)
    half = d / 2
    punch = 1.0 + 0.35 * ease(ramp(u, half - 0.25, half + 0.15))
    sr = (250 + 25 * lvl) * punch * (1 + 0.02 * pu)
    sy = hy - 40 - 130 * ease(ramp(u, 0, d * 0.8))
    cols = ((YEL, YEL, CORAL), (YEL, CORAL, PINK), (YEL, CORAL, PINK))[lvl - 1]
    sun_rays(c, 960, sy, sr + 30, sr + 120 + 60 * pu, n=28, ang=t * 0.3, seed=30, w=3.2)
    sun_disc(c, 960, sy, sr, phase=t * 1.2, cols=cols, seed=1)
    c.pl(circ(960, sy, sr), w=3.8, close=True, seed=2, passes=3)
    if lvl >= 2:
        birds(c, t, n=9, seed=3, y0=200, speed=220, x0=-150, t0=t - u, w=3.0, scale=1.2)
    _mountains(c, hy, 5, 250, fillc=None if lvl == 1 else (CYAN if lvl == 2 else BLUE), col=None)
    if lvl == 3:
        _mountains(c, hy, 9, 140, fillc=PINK, gap=420)
    c.fill(rect(-20, hy, W + 40, H), PAPER, mul=False, wob=0)
    if lvl == 3:
        c.fill(rect(-20, hy, W + 40, H), mixc(PAPER, PINK, 0.35), wob=0)
    c.line(-20, hy, W + 20, hy, w=3.6, seed=4, passes=3)
    speed = 1.6 + 0.5 * lvl
    gridfloor(c, hy, 960, t * speed, col=(None, CYAN, BLUE)[lvl - 1], w=2.6 if lvl > 1 else 2.2, a=0.95, spacing=250)
    # things streaming past on both sides
    if lvl >= 2:
        for k in range(7, -1, -1):
            z = (k + 1 - (t * speed * 0.5) % 1.0) * 0.55
            if z < 0.3:
                continue
            for sgn in (-1, 1):
                x = 960 + sgn * 820 / z
                gy = hy + (H - hy) / z * 0.62
                if -300 < x < W + 300:
                    turbine(c, x, gy, 520 / z, t * 4 + k + sgn, seed=40 + k * 3 + sgn, w=max(1.8, 3.6 / z), fillc=PAPER)
    # lettering
    t1 = wt['until2']
    if t < u * 0 + (t - u) + half + 0.1:
        sz = 128
        ws = [text_width(w_, sz) for w_ in ('UNTIL', 'FURTHER', 'NOTICE')]
        gap = (W - 160 - sum(ws)) / 2
        x = 80
        for k, (w_, key) in enumerate((('UNTIL', 'until2'), ('FURTHER', 'further2'), ('NOTICE', 'notice2'))):
            pop_word(c, w_, x, 210 + (0, 26, 0)[k], sz, t, wt[key], seed=20 + k, knock=True, align='l',
                     fill=(None, (CYAN, PINK, YEL)[k], (YEL, CYAN, PINK)[k])[lvl - 1], off=(0, 0), shadow=((CORAL, BLUE, BLUE)[lvl - 1], (10, 9)), w=4.0,
                     rot=(-0.03, 0.0, 0.03)[k])
            x += ws[k] + gap
    else:
        if lvl == 1:
            caption(c, "tomorrow's not a dream", t, wt['tomorrow'], wt['dream'] + 0.5, x=110, y=1000)
        else:
            for k, (w_, key, x, y, sz) in enumerate((("TOMORROW'S", 'tomorrow', 960, 190, 150), ('NOT A', 'not', 600, 1010, 120), ('DREAM', 'dream', 1340, 1010, 150))):
                pop_word(c, w_, x, y, sz, t, wt[key], seed=30 + k, knock=True, fill=(YEL, PINK, CYAN)[k] if lvl == 3 else (PINK, YEL, CYAN)[k], off=(0, 0),
                         shadow=(BLUE, (10, 9)), w=4.0)
    fl = 0.5 * (1 - ramp(u, 0, 0.12)) + 0.4 * (1 - ramp(abs(u - half - 0.05), 0, 0.12)) * (1 if u > half else 0)
    return dict(flash=fl)


# ------------------------------------------------------------------ 6. we built the problem / we'll build our way out
def _resample_n(pts, n):
    pts = np.asarray(pts, float)
    d = np.hypot(np.diff(pts[:, 0]), np.diff(pts[:, 1]))
    L = np.concatenate([[0], np.cumsum(d)])
    u = np.linspace(0, L[-1], n)
    return np.stack([np.interp(u, L, pts[:, 0]), np.interp(u, L, pts[:, 1])], 1)


def skyline_line(seed=1, gy=820, x0=-40, x1=W + 40, hmax=520):
    pts = [(x0, gy)]
    x = 60.0
    k = 0
    while x < x1 - 120:
        wd = 60 + 110 * rnd(seed, k, 1)
        h = (90 + hmax * rnd(seed, k, 2) ** 1.5) * (0.55 + 0.45 * math.sin(math.pi * min(1, max(0, x / W))) )
        style = int(rnd(seed, k, 3) * 5)
        pts.append((x, gy))
        pts.append((x, gy - h))
        if style == 0:
            pts += [(x + wd * 0.5, gy - h), (x + wd * 0.5, gy - h - 70), (x + wd * 0.5, gy - h)]
        elif style == 1:
            pts += [(x + wd * 0.5, gy - h - wd * 0.4)]
        elif style == 2:
            pts += [(x + wd * 0.25, gy - h), (x + wd * 0.25, gy - h - 30), (x + wd * 0.75, gy - h - 30), (x + wd * 0.75, gy - h)]
        elif style == 3:
            pts += [tuple(p) for p in circ(x + wd / 2, gy - h, wd / 2, math.pi, TAU, n=9)]
        pts.append((x + wd, gy - h))
        pts.append((x + wd, gy))
        x += wd + 14 + 40 * rnd(seed, k, 4)
        k += 1
    pts.append((x1, gy))
    return np.array(pts, float)


def bridge_line(gy=800):
    pts = [(-40, gy), (330, gy), (330, 250)]
    xs = np.linspace(330, 1590, 40)
    pts += [(x, 250 + 430 * (1 - ((x - 960) / 630) ** 2)) for x in xs[1:-1]]
    pts += [(1590, 250), (1590, gy), (W + 40, gy)]
    return np.array(pts, float)


def ch_build(c, t, u, d, lvl, wt, hold=0.0, begin=True, behind=None):
    """tangle (the problem) -> unravels into something built"""
    if begin:
        c.begin(t)
    N = 900
    half = d / 2 if hold == 0 else (d - hold) / 2
    sc = scribble(N, 11 + lvl)
    tangle = sc * (560, 330) + (960, 500)
    gy = 820 if lvl != 2 else 800
    target = _resample_n(skyline_line(seed=lvl, gy=gy) if lvl != 2 else bridge_line(gy), N)
    grow = ease(ramp(u, 0.0, half * 0.92))
    m = ease(ramp(u, half, half * 2 - 1.5))
    built = ramp(u, half * 2 - 1.6, half * 2 - 0.9)
    idx = np.arange(N) / N
    # stagger: points resolve left to right
    k = np.clip(m * 1.6 - idx * 0.6, 0, 1)
    k = (k * k * (3 - 2 * k))[:, None]
    wig = (1 - k) * 1.0
    jit = np.stack([sn(N, 5 + int(t * 10), 3), sn(N, 905 + int(t * 10), 3)], 1) * 6 * wig * (0.3 + A.kick(t))
    pts = tangle * (1 - k) + target * k + jit
    pu = A.pulse(t, 5)
    if m > 0:
        # sun comes up behind what gets built
        sy = gy + 120 - 420 * ease(m)
        sr = 250 + 30 * lvl
        cols = ((YEL, YEL, CORAL), (YEL, CORAL, PINK), (YEL, CORAL, PINK))[lvl - 1]
        sun_rays(c, 960, sy, sr + 30, sr + 110 + 60 * pu, n=26, ang=t * 0.3, seed=30, w=3.2, rev=m)
        sun_disc(c, 960, sy, sr, phase=t * 1.2, cols=cols, seed=1, a=m)
        c.pl(circ(960, sy, sr), w=3.6, close=True, seed=2, passes=2, a=0.9 * m)
        c.fill(rect(-20, gy, W + 40, H), PAPER, mul=False, wob=0)
    if behind is not None:
        behind(c)
    if m > 0.8:
        poly = np.vstack([pts, [[W + 40, H + 40], [-40, H + 40]]])
        c.fill(poly, PAPER, mul=False, wob=0)
    if built > 0:
        poly = np.vstack([target, [[W + 40, H + 40], [-40, H + 40]]])
        if lvl != 2:
            c.fill(poly, (CYAN, None, BLUE)[lvl - 1], a=built, seed=3, off=(8, 6))
            # lit windows
            rs = rnds(400, lvl, 8).reshape(200, 2)
            wins = []
            for q in rs[: int(200 * built)]:
                x, y = 80 + q[0] * (W - 160), gy - 20 - q[1] * 420
                j = np.searchsorted(target[:, 0], x)
                j = min(N - 1, max(1, j))
                if y > min(target[j, 1], target[j - 1, 1]) + 16:
                    wins.append(rect(x, y, 16, 10))
            if wins:
                c.fill(wins, YEL, mul=False, wob=0)
        else:
            # deck + hangers
            c.line(-40, 640, W + 40, 640, w=4.5, seed=4, rev=built, passes=3)
            segs = [(x, 250 + 430 * (1 - ((x - 960) / 630) ** 2), x, 640) for x in np.linspace(380, 1540, 30) if 250 + 430 * (1 - ((x - 960) / 630) ** 2) < 632]
            c.ticks(segs[: int(len(segs) * built)], w=2.2, a=0.9, seed=5)
            for j in range(6):
                yy = gy + 40 + j * 34
                xs = np.linspace(-20, W + 20, 80)
                c.pl(np.stack([xs, yy + 8 * np.sin(xs * 0.02 + t * 3 + j * 1.3)], 1), w=4.0, col=CYAN, seed=60 + j, passes=1, wob=0.4, a=built)
    rv = grow if m <= 0 else 1.0
    c.pl(pts, w=3.0 + 1.2 * k.mean(), seed=7, rev=rv, passes=2 if m > 0.6 else 1, wob=0.8 + 1.0 * (1 - m), seg=8, a=0.95)
    if m <= 0 and rv < 1:
        hp = pts[min(N - 1, int(rv * N))]
        pencil(c, hp[0], hp[1], ang=-0.9 + 0.2 * math.sin(t * 14), s=1.3)
    if lvl == 1:
        if u < half:
            caption(c, 'we built the problem with our hands', t, wt['we'], wt['hands'] + 0.4, x=110, y=1010)
        else:
            caption(c, "we'll build our way out again", t, wt['well'], wt['again'] + 0.4, x=110, y=1010)
    elif lvl >= 2 and built > 0 and begin:
        birds(c, t, n=9, seed=8, y0=170, speed=240, x0=-100, t0=(t - u) + half * 2 - 1.6, w=3.0, scale=1.2)
    fl = 0.5 * (1 - ramp(u, 0, 0.12)) + 0.5 * (1 - ramp(abs(u - half), 0, 0.12)) * (1 if u > half else 0)
    return dict(flash=fl)


# ------------------------------------------------------------------ timeline
WT = {
    1: dict(until=58.46, further=60.44, notice=61.20, believe=63.16, machine=64.64, turning=65.60, light=67.96, making=69.38, clean=71.66,
            until2=73.46, further2=74.84, notice2=75.68, tomorrow=77.52, **{'not': 78.80}, dream=79.42, we=80.32, hands=83.20, well=84.04, again=86.52),
    2: dict(until=131.78, further=132.60, notice=133.48, believe=135.46, machine=136.92, turning=137.80, light=140.66, making=141.80, clean=143.92,
            until2=145.88, further2=147.08, notice2=147.90, tomorrow=149.80, **{'not': 151.00}, dream=151.66, we=152.62, hands=155.46, well=156.42, again=158.76),
    3: dict(until=203.44, further=204.44, notice=205.34, believe=207.32, machine=208.76, turning=209.66, light=212.42, making=212.84, clean=215.66,
            until2=217.86, further2=218.82, notice2=219.62, tomorrow=220.68, **{'not': 222.76}, dream=223.40, we=223.80, hands=227.12, well=228.18, again=230.44),
}


def _bind(fn, lvl):
    return lambda c, t, u, d: fn(c, t, u, d, lvl, WT[lvl])


def chorus(b0, lvl, with_build=True):
    tl = [
        (B(b0), B(b0 + 2), _bind(ch_title, lvl)),
        (B(b0 + 2), B(b0 + 4), _bind(ch_machine, lvl)),
        (B(b0 + 4), B(b0 + 6), _bind(ch_wind, lvl)),
        (B(b0 + 6), B(b0 + 8), _bind(ch_clean, lvl)),
        (B(b0 + 8), B(b0 + 12), _bind(ch_grid, lvl)),
    ]
    if with_build:
        tl.append((B(b0 + 12), B(b0 + 16), _bind(ch_build, lvl)))
    return tl


def timeline():
    return chorus(32, 1) + chorus(72, 2) + chorus(112, 3, with_build=False)
