"""Interlude (the city builds itself), verse 2 (four strips), pre-chorus 2 (the network)."""
from motifs import *
import sc_b


# ------------------------------------------------------------------ interlude
def _crane(c, x, gy, h, ang, seed=0, w=3.0, rev=1.0):
    if rev <= 0:
        return
    hh = h * ease(rev)
    c.line(x - 9, gy, x - 9, gy - hh, w=w, seed=seed)
    c.line(x + 9, gy, x + 9, gy - hh, w=w, seed=seed + 1)
    n = int(hh / 22)
    segs = []
    for k in range(n):
        y0 = gy - k * 22
        segs.append((x - 9, y0, x + 9, y0 - 22) if k % 2 else (x + 9, y0, x - 9, y0 - 22))
    c.ticks(segs, w=1.6, a=0.8, seed=seed + 2, jit=0.6)
    if rev < 1:
        return
    ty = gy - hh
    L = 300 * math.cos(ang)
    c.line(x - L * 0.3, ty, x + L, ty - 6, w=w * 1.1, seed=seed + 3, passes=3)
    c.line(x, ty - 60, x + L, ty - 6, w=w * 0.6, seed=seed + 4, passes=1)
    c.line(x, ty - 60, x - L * 0.3, ty, w=w * 0.6, seed=seed + 5, passes=1)
    c.line(x, ty, x, ty - 60, w=w, seed=seed + 6)
    hx = x + L * (0.55 + 0.25 * math.sin(c.t * 0.9 + seed))
    hl = 90 + 50 * math.sin(c.t * 1.3 + seed)
    c.line(hx, ty - 4, hx, ty + hl, w=1.8, seed=seed + 7, passes=1, wob=0.5)
    c.pl(rect(hx - 16, ty + hl, 32, 24), w=2.4, close=True, seed=seed + 8, wob=0.6)
    c.pl(rect(x - L * 0.3 - 4, ty - 2, 30, 26), w=2.4, close=True, seed=seed + 9, wob=0.6)


FRONT = [(k * 139 - 30 + 40 * rnd(k, 71), 60 + 80 * rnd(k, 72), 150 + 330 * rnd(k, 73) ** 1.3) for k in range(15)]


def interlude(c, t, u, d):
    c.begin(t)
    wt = sc_b.WT[1]
    gy = 820
    pu = A.pulse(t, 5)
    N = 900
    target = sc_b._resample_n(sc_b.skyline_line(seed=1, gy=gy), N)
    sy = 520 - 150 * ease(ramp(u, 0, d))
    sr = 280 * (1 + 0.02 * pu)
    sun_rays(c, 960, sy, sr + 30, sr + 110 + 60 * pu, n=26, ang=t * 0.3, seed=30, w=3.2)
    sun_disc(c, 960, sy, sr, phase=t * 1.2, cols=(YEL, YEL, CORAL), seed=1)
    c.pl(circ(960, sy, sr), w=3.6, close=True, seed=2, passes=2)
    # clouds
    for k in range(4):
        cxp = (k * 560 + 200 + (t - 87) * (14 + 5 * k)) % (W + 600) - 300
        cloud(c, cxp, 150 + 70 * (k % 2), 330 + 60 * k, 60, seed=20 + k, shade=0, fillc=CYAN if k % 2 == 0 else None, lw=3.0)
    birds(c, t, n=10, seed=8, y0=260, speed=210, x0=-100, t0=B(48) - 2.0, w=3.0, scale=1.2)
    # cranes behind
    _crane(c, 500, gy, 560, 0.6 * math.sin(t * 0.5), seed=40, rev=ramp(u, 0.2, 1.4))
    _crane(c, 1490, gy, 640, math.pi + 0.7 * math.sin(t * 0.4 + 1), seed=50, rev=ramp(u, 1.1, 2.3))
    # the first skyline
    poly = np.vstack([target, [[W + 40, H + 40], [-40, H + 40]]])
    c.fill(poly, PAPER, mul=False, wob=0)
    c.fill(poly, CYAN, seed=3, off=(8, 6))
    rs = rnds(400, 1, 8).reshape(200, 2)
    wins = []
    for q in rs:
        x, y = 80 + q[0] * (W - 160), gy - 20 - q[1] * 420
        j = min(N - 1, max(1, np.searchsorted(target[:, 0], x)))
        if y > min(target[j, 1], target[j - 1, 1]) + 16:
            wins.append(rect(x, y, 16, 10))
    c.fill(wins, YEL, mul=False, wob=0)
    c.pl(target, w=4.0, seed=7, passes=2, wob=0.9, seg=8)
    # a new front row rises, one building per beat
    base = H + 10
    b0 = A.beatpos(B(48))
    bn = A.beatpos(t)
    order = [7, 3, 11, 5, 9, 1, 13, 6, 10, 2, 12, 4, 8, 0, 14]
    cols = (None, CORAL, YEL, None, CORAL, None, YEL)
    for k in sorted(range(15), key=lambda i: FRONT[i][2]):
        birth = b0 + 1 + order.index(k) * 1.5
        g = (bn - birth) / 1.2
        if g <= 0:
            continue
        x, wd, h = FRONT[k]
        hh = h * back(min(1.0, g), 1.2)
        q = rect(x, base - hh, wd + 40, hh + 10)
        c.fill(q, PAPER, mul=False, wob=0)
        building(c, x, base, wd + 40, h, seed=200 + k, lit=0.35 if g > 1 else 0.0, rev=min(1.0, g), fillc=cols[k % len(cols)], lw=3.4)
    # the echo
    sc_b.caption(c, "we'll build our way out again", t, 91.78, 94.3, x=110, y=150, size=70)
    return dict(flash=0.3 * (1 - ramp(u, 0, 0.12)))


# ------------------------------------------------------------------ verse 2: four strips
def _strip(i):
    x0 = 70 + i * 450
    return np.array([[x0 + 56, 60], [x0 + 56 + 420, 60], [x0 + 420, 1020], [x0, 1020]], float)


def _field(c, t, sx, hy, seed=0, rainy=True):
    """ploughed field receding to a horizon. sx = strip centre x"""
    c.line(sx - 300, hy, sx + 300, hy, w=3.0, seed=seed)
    for k in range(-9, 10):
        c.line(sx + k * 9, hy + 2, sx + k * 150, 1040, w=2.2 + 0.2 * abs(k), seed=seed + 10 + k, passes=1 if abs(k) > 2 else 2, wob=1.2)


def strip_rain(c, t, u, P):
    sx = P[:, 0].mean()
    hy = 430
    c.hatch(rect(sx - 300, 40, 600, hy - 40), ang=-0.5, gap=9, a=0.5, seed=1)
    c.hatch(rect(sx - 300, 40, 600, hy - 180), ang=0.35, gap=11, a=0.45, seed=2)
    for k in range(2):
        cxp = sx - 60 + k * 190 + 30 * math.sin(t * 0.3 + k)
        sh = cloud_shape(cxp, 230 + k * 90, 380, 80, 30 + k)
        c.fill(sh, PAPER, mul=False, wob=0)
        cloud(c, cxp, 230 + k * 90, 380, 80, seed=30 + k, shade=0.9, gap=6, lw=3.0)
    _field(c, t, sx, hy, seed=40)
    # puddle rings
    for k in range(5):
        ph = (t * 0.9 + k * 0.37) % 1.0
        px = sx - 150 + ((k * 97) % 300)
        py = 600 + ((k * 151) % 380)
        sc = (py - hy) / 500.0
        for j in range(2):
            rr = (20 + 90 * ph + j * 26) * sc
            q = circ(px, py, rr)
            q[:, 1] = py + (q[:, 1] - py) * 0.32
            c.pl(q, w=3.0, col=CYAN, a=(1 - ph), close=True, seed=60 + k * 2 + j, passes=1, wob=0.5)
    n = 110
    r = rnds(n * 3, 7, 7).reshape(n, 3)
    x = sx - 320 + (r[:, 0] * 640 - t * 150 * (0.8 + 0.4 * r[:, 2])) % 640
    y = (r[:, 1] * 1100 + t * 1300 * (0.8 + 0.4 * r[:, 2])) % 1100 - 40
    ln = 40 + 40 * r[:, 2]
    c.ticks(np.stack([x, y, x - ln * 0.12, y + ln], 1), w=1.8, a=0.7, jit=0.5, seed=70, boil=False)


def strip_harvest(c, t, u, P):
    sx = P[:, 0].mean()
    hy = 430
    sun_disc(c, sx + 80, 250, 110, phase=t, cols=(YEL, YEL, CORAL), seed=1)
    c.pl(circ(sx + 80, 250, 110), w=3.2, close=True, seed=2, passes=2)
    sun_rays(c, sx + 80, 250, 130, 190 + 30 * A.pulse(t, 5), n=16, ang=t * 0.4, seed=10, w=2.8)
    c.fill(rect(sx - 320, hy, 640, 700), PAPER, mul=False, wob=0)
    _field(c, t, sx, hy, seed=40)
    # sprouts in the furrows, growing in sequence
    rows = []
    for j in range(5):
        z = 1 + j * 0.9
        for k in (-2, -1, 0, 1, 2):
            rows.append((z, k, j))
    for (z, k, j) in sorted(rows, key=lambda q: -q[0]):
        yy = hy + 560 / z
        xx = sx + (k * 150 + 75) * (yy - hy) / 610.0
        g = ramp(u, 0.25 + j * 0.25 + abs(k) * 0.08, 1.4 + j * 0.25 + abs(k) * 0.08)
        sprout(c, xx, yy, 190 / z, g, seed=100 + j * 7 + k, leafc=mixc(YEL, CYAN, 0.55), w=max(1.8, 3.0 / z))
    # one big sunflower in front
    g = ramp(u, 0.9, 2.8)
    fx, fy = sx - 70, 1020
    st = np.stack([fx + 40 * np.sin(np.linspace(0, 2, 12)), fy - np.linspace(0, 1, 12) * 430 * ease(g)], 1)
    c.pl(st, w=5, seed=3, passes=3)
    if g > 0.3:
        hx, hy2 = st[-1]
        sunflower(c, hx, hy2, 150 * ease(ramp(g, 0.3, 1.0)), grow=ramp(g, 0.3, 1.0), seed=5, ang=t * 0.25, petc=YEL)


def strip_factory(c, t, u, P):
    sx = P[:, 0].mean()
    gy = 880
    # staff lines of clean notes rising from the chimneys
    lv = A.rms(t)
    for k, (cxp, ch) in enumerate(((sx - 110, 360), (sx + 40, 470))):
        top = gy - ch
        g = ramp(u, 0.4 + k * 0.3, 2.2 + k * 0.3)
        s = np.linspace(0, 1, 60)
        for j in range(5):
            xs = cxp + (j - 2) * 12 + s * (130 - k * 230) + 26 * np.sin(s * 9 + t * 3 + k) * s
            ys = top - 10 - s * (top - 80)
            c.pl(np.stack([xs, ys], 1), w=2.6, col=CYAN if k == 0 else CORAL, seed=20 + k * 5 + j, rev=g, passes=1, wob=0.5, a=1.0)
        notes, stems = [], []
        for m in range(7):
            ph = (m / 7 + t * 0.16) % 1.0
            if ph > g:
                continue
            xs = cxp + ((m * 3) % 5 - 2) * 12 + ph * (130 - k * 230) + 26 * math.sin(ph * 9 + t * 3 + k) * ph
            ys = top - 10 - ph * (top - 80)
            notes.append((xs, ys))
            stems.append((xs + 9, ys, xs + 9, ys - 46))
        if notes:
            c.dots(notes, 11 + 3 * lv)
            c.ticks(stems, w=3.0, a=0.95, jit=0.4, seed=40 + k)
    # factory: saw-tooth roof and two chimneys
    for k, (cxp, ch, wd) in enumerate(((sx - 110, 360, 46), (sx + 40, 470, 54))):
        q = np.array([[cxp - wd / 2, gy], [cxp - wd * 0.36, gy - ch], [cxp + wd * 0.36, gy - ch], [cxp + wd / 2, gy]])
        c.fill(q, PAPER, mul=False, wob=0)
        c.pl(q, w=3.6, seed=50 + k, passes=3)
        c.ticks([(cxp - wd * 0.4, gy - ch + 22 + j * 14, cxp + wd * 0.4, gy - ch + 22 + j * 14) for j in range(3)], w=2.0, a=0.85, seed=60 + k)
    roof = [(sx - 260, gy)]
    for k in range(5):
        x0 = sx - 260 + k * 104
        roof += [(x0, gy - 190), (x0 + 104, gy - 120)]
    roof += [(sx + 260, gy)]
    roof = np.array(roof, float)
    c.fill(roof, PAPER, mul=False, wob=0)
    c.fill(roof, YEL, seed=4, off=(6, 5))
    c.pl(roof, w=3.8, close=True, seed=5, passes=3)
    for k in range(5):
        x0 = sx - 260 + k * 104
        c.hatch(np.array([[x0 + 6, gy - 180], [x0 + 98, gy - 120], [x0 + 6, gy - 120]]), ang=1.2, gap=7, a=0.6, seed=70 + k)
    wins = [rect(sx - 236 + k * 62, gy - 84, 40, 48) for k in range(8)]
    for k, q in enumerate(wins):
        c.fill(q, PAPER, mul=False, wob=0)
        c.pl(q, w=2.4, close=True, seed=80 + k, wob=0.7)
    c.line(sx - 320, gy, sx + 320, gy, w=3.6, seed=6, passes=3)
    c.hatch(rect(sx - 320, gy, 640, 200), ang=0.15, gap=9, a=0.5, seed=7)
    # a hum: lissajous in the corner
    th = np.linspace(0, TAU, 140)
    c.pl(np.stack([sx - 150 + 62 * np.sin(3 * th + t * 2), 1000 - 30 + 30 * np.sin(2 * th)], 1) * 1.0 + (0, -40), w=2.4, col=CORAL, seed=9, passes=1, wob=0.3, close=True)


def _ik(hx, hy, fx, fy, a, b):
    dx, dy = fx - hx, fy - hy
    dd = min(a + b - 0.5, max(1.0, math.hypot(dx, dy)))
    ca = (a * a + dd * dd - b * b) / (2 * a * dd)
    al = math.acos(max(-1, min(1, ca)))
    base = math.atan2(dy, dx)
    return hx + a * math.cos(base - al), hy + a * math.sin(base - al)


def cyclist(c, x, y, s, wang, seed=0, w=3.4, col=None, wheelc=None):
    """side-view rider; (x, y) = rear hub. heading right"""
    def P(px, py):
        return (x + px * s, y + py * s)
    R = 70 * s
    rear, front = P(0, 0), P(205, 0)
    bb, seat, head, bar = P(82, 6), P(62, -108), P(170, -112), P(184, -134)
    for k, hub in enumerate((rear, front)):
        if wheelc is not None:
            c.pl(circ(hub[0], hub[1], R * 0.86), w=9 * s, col=wheelc, close=True, seed=seed + 60 + k, passes=1, wob=0.5, a=1.0)
        c.pl(circ(hub[0], hub[1], R), w=w * 1.3, close=True, seed=seed + k, passes=3, col=col, wob=0.8)
        segs = [(hub[0], hub[1], hub[0] + R * 0.95 * math.cos(wang + j * TAU / 10), hub[1] + R * 0.95 * math.sin(wang + j * TAU / 10)) for j in range(10)]
        c.ticks(segs, w=1.4, a=0.75, jit=0.4, seed=seed + 5 + k, col=col, boil=False)
    for k, (p0, p1) in enumerate(((rear, bb), (bb, seat), (seat, head), (bb, head), (rear, seat), (head, front), (head, bar))):
        c.line(p0[0], p0[1], p1[0], p1[1], w=w, seed=seed + 10 + k, col=col, wob=0.6)
    c.line(seat[0] - 16 * s, seat[1] - 4 * s, seat[0] + 18 * s, seat[1] - 6 * s, w=w * 1.8, seed=seed + 20, col=col, wob=0.4)
    c.line(bar[0] - 4 * s, bar[1], bar[0] + 22 * s, bar[1] + 8 * s, w=w * 1.3, seed=seed + 21, col=col, wob=0.4)
    hip = (seat[0] + 2 * s, seat[1] - 14 * s)
    sh = (hip[0] + 62 * s, hip[1] - 96 * s)
    hd = (sh[0] + 22 * s, sh[1] - 40 * s)
    cr = 30 * s
    for k, ph in enumerate((math.pi, 0.0)):   # far leg first
        an = wang * 0.5 + ph
        ft = (bb[0] + cr * math.cos(an), bb[1] + cr * math.sin(an))
        kn = _ik(hip[0], hip[1], ft[0], ft[1], 80 * s, 80 * s)
        aa = 0.55 if k == 0 else 0.95
        c.line(bb[0], bb[1], ft[0], ft[1], w=w * 0.9, seed=seed + 30 + k, col=col, wob=0.3, a=aa)
        c.pl([hip, kn, ft], w=w * 2.0 if k else w * 1.5, seed=seed + 32 + k, col=col, wob=0.8, a=aa, passes=2)
        c.line(ft[0] - 12 * s, ft[1], ft[0] + 16 * s, ft[1], w=w * 1.6, seed=seed + 34 + k, col=col, wob=0.3, a=aa)
    el = ((sh[0] + bar[0]) / 2 - 4 * s, (sh[1] + bar[1]) / 2 + 18 * s)
    c.pl([hip, ((hip[0] + sh[0]) / 2 - 8 * s, (hip[1] + sh[1]) / 2 - 4 * s), sh], w=w * 2.4, seed=seed + 40, col=col, wob=0.8, passes=3)
    c.pl([sh, el, (bar[0] + 8 * s, bar[1] + 2 * s)], w=w * 1.5, seed=seed + 41, col=col, wob=0.7)
    c.fill(circ(hd[0], hd[1], 23 * s), NIGHT if c.night else PAPER, mul=False, wob=0)
    c.pl(circ(hd[0], hd[1], 23 * s), w=w * 1.1, close=True, seed=seed + 42, col=col, passes=3, wob=0.8)
    # scarf
    u = np.linspace(0, 1, 14)
    c.pl(np.stack([sh[0] + 6 * s - u * 120 * s, sh[1] - 12 * s + 14 * s * np.sin(u * 7 + c.t * 9) * u - u * 16 * s], 1), w=7 * s, col=CORAL, seed=seed + 50, passes=1, wob=0.5, a=1.0)


def strip_wheels(c, t, u, P):
    sx = P[:, 0].mean()
    gy = 840
    v = 330.0
    # overhead wires + lamp posts streaming by
    for k in range(4):
        px = sx + 330 - ((t * v + k * 230) % 920)
        c.line(px, gy, px, 300, w=3.6, seed=10 + k, passes=2)
        c.pl([[px, 300], [px + 14, 280], [px + 70, 276]], w=3.0, seed=14 + k)
        c.dots([(px + 70, 288)], 9, col=YEL)
    for k in range(2):
        yy = 190 + k * 26
        xs = np.linspace(sx - 320, sx + 320, 30)
        c.pl(np.stack([xs, yy + 10 * np.sin((xs + t * v) * 0.0068)], 1), w=2.0, seed=20 + k, passes=1)
    # far skyline
    for k in range(7):
        bx = sx + 330 - ((t * v * 0.25 + k * 110) % 770)
        building(c, bx, gy, 70, 120 + 160 * rnd(k, 9), seed=300 + k, lit=0.3, lw=2.2)
    c.line(sx - 330, gy, sx + 330, gy, w=3.8, seed=1, passes=3)
    segs = [(sx + 330 - ((t * v + k * 120) % 760), gy + 46, sx + 330 - ((t * v + k * 120) % 760) + 50, gy + 46) for k in range(7)]
    c.ticks(segs, w=3.2, a=0.85, jit=0.6, seed=2, boil=False)
    c.hatch(rect(sx - 330, gy + 90, 660, 200), ang=0.1, gap=8, a=0.5, seed=3)
    bob = 3 * math.sin(t * 9)
    cyclist(c, sx - 150, gy - 100 + bob, 1.42, t * 8.5, seed=40, wheelc=CYAN)
    # speed lines
    n = 9
    r = rnds(n * 2, 3, 3).reshape(n, 2)
    xs = sx + 330 - ((t * 900 * (0.6 + r[:, 0]) + r[:, 1] * 700) % 700)
    ys = 420 + r[:, 1] * 380
    c.ticks(np.stack([xs, ys, xs + 60 + 80 * r[:, 0], ys], 1), w=2.0, a=0.6, jit=0.4, seed=4, boil=False)


STRIPS = ((strip_rain, 99.92), (strip_harvest, 104.25), (strip_factory, 107.85), (strip_wheels, 111.45))


def verse2(c, t, u, d):
    c.begin(t)
    for i, (fn, t0) in enumerate(STRIPS):
        P = _strip(i)
        if t < t0:
            # empty frame waiting, lightly sketched
            c.pl(P, w=1.6, a=0.35, close=True, seed=90 + i, passes=1, wob=1.5)
            continue
        uu = t - t0
        sl = eout(ramp(uu, 0, 0.3))
        c.region(P, PAPER)
        c.cx.save()
        c.cx.translate(0, (1 - sl) * 70)
        fn(c, t, uu, P)
        c.cx.restore()
        c.endregion()
        panel_frame(c, P, seed=i + 1, w=5.0)
    fl = 0.3 * (1 - ramp(u, 0, 0.12))
    for (fn, t0) in STRIPS[1:]:
        if t >= t0:
            fl = max(fl, 0.35 * (1 - ramp(t - t0, 0, 0.12)))
    return dict(flash=fl)


# ------------------------------------------------------------------ pre-chorus 2: give it to everyone
_NET = None


def network():
    global _NET
    if _NET is None:
        pts = [(0.0, 0.0)]
        k = 0
        for j in range(-7, 8):
            for i in range(-11, 12):
                if i == 0 and j == 0:
                    continue
                x = i * 200 + (100 if j % 2 else 0) + (rnd(i, j, 1) - 0.5) * 110
                y = j * 172 + (rnd(i, j, 2) - 0.5) * 100
                pts.append((x, y))
        P = np.array(pts)
        n = len(P)
        D = np.hypot(P[:, None, 0] - P[None, :, 0], P[:, None, 1] - P[None, :, 1])
        nb = np.argsort(D, 1)[:, 1:5]
        depth = np.full(n, -1)
        parent = np.full(n, -1)
        depth[0] = 0
        q = [0]
        while q:
            a = q.pop(0)
            for b in nb[a]:
                if depth[b] < 0:
                    depth[b] = depth[a] + 1
                    parent[b] = a
                    q.append(b)
        for a in range(n):
            if depth[a] < 0:
                b = nb[a][0]
                depth[a] = 12
                parent[a] = b
        _NET = (P, nb, depth, parent)
    return _NET


def _glyph(c, kind, x, y, s, seed, t):
    kind = kind % 6
    w = max(1.6, s * 0.09)
    if kind == 0:   # sun
        c.pl(circ(x, y, s * 0.3), w=w, close=True, seed=seed, wob=0.4, passes=1)
        c.ticks([(x + s * 0.42 * math.cos(a), y + s * 0.42 * math.sin(a), x + s * 0.62 * math.cos(a), y + s * 0.62 * math.sin(a)) for a in np.arange(8) * TAU / 8 + t], w=w, a=0.9, jit=0.3, seed=seed)
    elif kind == 1:  # house
        c.pl([[x - s * 0.45, y + s * 0.5], [x - s * 0.45, y - s * 0.05], [x, y - s * 0.55], [x + s * 0.45, y - s * 0.05], [x + s * 0.45, y + s * 0.5]], w=w, close=True, seed=seed, wob=0.5, passes=1)
    elif kind == 2:  # turbine
        c.line(x, y + s * 0.6, x, y - s * 0.15, w=w, seed=seed, wob=0.3, passes=1)
        c.ticks([(x, y - s * 0.15, x + s * 0.55 * math.cos(a), y - s * 0.15 + s * 0.55 * math.sin(a)) for a in np.arange(3) * TAU / 3 + t * 3], w=w, a=0.95, jit=0.3, seed=seed, boil=False)
    elif kind == 3:  # bolt
        c.pl(np.array([[0.1, -0.6], [-0.3, 0.05], [0.0, 0.05], [-0.15, 0.6], [0.32, -0.12], [0.02, -0.12]]) * s + (x, y), w=w, close=True, seed=seed, wob=0.4, passes=1)
    elif kind == 4:  # sprout
        c.line(x, y + s * 0.55, x, y - s * 0.1, w=w, seed=seed, wob=0.3, passes=1)
        c.pl(circ(x - s * 0.22, y - s * 0.22, s * 0.25, 0.4, 3.6), w=w, seed=seed + 1, wob=0.3, passes=1)
        c.pl(circ(x + s * 0.22, y - s * 0.22, s * 0.25, -0.4, -3.6), w=w, seed=seed + 2, wob=0.3, passes=1)
    else:            # gear
        c.pl(circ(x, y, s * 0.36), w=w, close=True, seed=seed, wob=0.4, passes=1)
        c.dots([(x, y)], s * 0.1)
        c.ticks([(x + s * 0.36 * math.cos(a), y + s * 0.36 * math.sin(a), x + s * 0.56 * math.cos(a), y + s * 0.56 * math.sin(a)) for a in np.arange(8) * TAU / 8 - t], w=w * 1.6, a=0.95, jit=0.3, seed=seed, boil=False)


PHR = [
    ((('GIVE', 116.78), ('IT', 118.14), ('TO', 118.32), ('EVERYONE', 118.64)), 120.62),
    ((('NOT', 120.78), ('JUST', 122.00), ('THE', 122.78), ('FEW', 123.16)), 123.36),
    ((('THE', 123.42), ('TOOLS', 124.82), ('THAT', 125.42), ('WE', 126.08), ('SHARE', 126.46)), 127.32),
    ((('ARE', 127.40), ('THE', 128.28), ('TOOLS', 128.42), ('THAT', 129.12), ('COME', 129.68), ('TRUE', 130.12)), 999.0),
]


def pre2(c, t, u, d):
    c.begin(t)
    P, nb, depth, parent = network()
    n = len(P)
    z = 2.3 - 1.45 * ease(ramp(u, 0.5, d - 0.6))
    cxm, cym = 960, 500
    S = P * z + (cxm, cym)
    t0 = (t - u) + 0.55
    beat = 0.4528
    act = t0 + depth * beat * 1.75 + (RN[(np.arange(n) * 31) & (NT - 1)] * 0.5) * (depth > 0)
    on = t >= act
    cols = (YEL, CORAL, CYAN, PINK)
    pu = A.pulse(t, 5)
    # edges
    for b in range(1, n):
        a = parent[b]
        r = ramp(t, act[b] - 0.4, act[b])
        if r <= 0 or not (-200 < S[b, 0] < W + 200 and -200 < S[b, 1] < H + 200 or -200 < S[a, 0] < W + 200 and -200 < S[a, 1] < H + 200):
            continue
        c.line(S[a, 0], S[a, 1], S[b, 0], S[b, 1], w=2.8, seed=b, rev=eout(r), passes=2 if z > 1.3 else 1, wob=1.0)
    ex = []
    for a in range(n):
        if not on[a]:
            continue
        for b in nb[a][:3]:
            if b > a and on[b] and parent[b] != a and parent[a] != b and t > max(act[a], act[b]) + 0.8:
                ex.append((S[a, 0], S[a, 1], S[b, 0], S[b, 1]))
    c.ticks(ex, w=1.5, a=0.5, jit=1.0, seed=3)
    # nodes
    for a in np.argsort(-act):
        if not on[a]:
            continue
        x, y = S[a]
        if not (-80 < x < W + 80 and -80 < y < H + 80):
            continue
        p = back(ramp(t, act[a], act[a] + 0.22), 2.6)
        r = (30 + 14 * z) * p * (1 + 0.06 * pu)
        if a == 0:
            r *= 1.6
        q = circ(x, y, r)
        c.fill(q, PAPER, mul=False, wob=0)
        c.fill(q, cols[a % 4] if a else YEL, seed=a, off=(4, 4), wob=0.8)
        c.pl(q, w=3.0, close=True, seed=a + 500, wob=0.8, passes=2)
        if p > 0.8:
            _glyph(c, a if a else 0, x, y, r * 1.05, a + 900, t)
    # the line, word by word
    for (words, tend) in PHR:
        if t < tend:
            band_words(c, t, words)
            break
    return dict(flash=0.4 * (1 - ramp(u, 0, 0.12)))


def timeline():
    return [
        (B(48), B(55), interlude),
        (B(55), B(64), verse2),
        (B(64), B(72), pre2),
    ]
