"""Interlude (the city), verse 2 (four figures), pre-chorus 2 (fireflies)."""
from lum import *
import sims


def _cutflash(u, k=0.3):
    return k * (1 - ramp(u, 0, 0.16))


# ---------------------------------------------------------------- 12. a city builds itself
NC = 13
_CITY = None


def _city():
    global _CITY
    if _CITY is None:
        rs = np.random.RandomState(8)
        ij = np.array([(i, j) for i in range(NC) for j in range(NC)], float) - (NC - 1) / 2
        dist = np.hypot(ij[:, 0], ij[:, 1])
        h = 0.5 + 3.6 * rs.rand(len(ij)) ** 1.6 * np.exp(-(dist / 5.5) ** 2) + 0.8 * rs.rand(len(ij))
        order = np.argsort(np.argsort(dist + rs.rand(len(ij)) * 2.5))
        _CITY = (ij, h, order, rs.rand(len(ij)))
    return _CITY


def city(L, t, u, d):
    L.begin(t)
    ij, h0, order, rr = _city()
    n = len(ij)
    phi = 0.55 + 0.11 * u
    el = 0.56
    sp = spectrum(t, 64)
    cph, sph = math.cos(phi), math.sin(phi)
    ce, se = math.cos(el), math.sin(el)
    S = 90.0
    cx, cy = 960, 670

    def proj(x, y, z):
        xr = x * cph - z * sph
        zr = x * sph + z * cph
        sy = -y * ce + zr * se
        depth = zr * ce + y * se
        k = 1.0 / (1.0 + depth * 0.018)
        return cx + xr * S * k, cy + sy * S * k

    # ground grid
    g = (NC + 1) / 2.0
    segs = []
    for k in range(NC + 2):
        a = -g + k
        p0, p1 = proj(a, 0, -g), proj(a, 0, g)
        q0, q1 = proj(-g, 0, a), proj(g, 0, a)
        segs.append((*p0, *p1))
        segs.append((*q0, *q1))
    L.segs(segs, DIM, 1.2, 0.45 * ramp(u, 0, 1.0))
    depth = ij[:, 0] * sph + ij[:, 1] * cph
    w = 0.31
    for b in np.argsort(-depth):
        g_ = ramp(u, 0.3 + order[b] * 0.045, 0.3 + order[b] * 0.045 + 0.7)
        if g_ <= 0:
            continue
        band = int(rr[b] * 40) + 4
        hh = h0[b] * back(g_, 1.4) * (1 + 0.38 * sp[band] * g_)
        x, z = ij[b]
        corners = [(x - w, z - w), (x + w, z - w), (x + w, z + w), (x - w, z + w)]
        base = [proj(cx_, 0, cz) for cx_, cz in corners]
        top = [proj(cx_, hh, cz) for cx_, cz in corners]
        # the two faces turned to the viewer + roof
        faces = []
        for k in range(4):
            k2 = (k + 1) % 4
            mx, mz = (corners[k][0] + corners[k2][0]) / 2 - x, (corners[k][1] + corners[k2][1]) / 2 - z
            if mx * sph + mz * cph < 0:
                faces.append((k, k2))
        for (k, k2) in faces:
            quad = [base[k], base[k2], top[k2], top[k]]
            L.black(quad)
            L.lines([quad], ICE, 1.5, 0.75, close=True)
            nfl = int(hh * 2.2)
            if nfl > 0:
                fl = []
                for m in range(1, nfl + 1):
                    f = m / (nfl + 1)
                    fl.append((base[k][0] + (top[k][0] - base[k][0]) * f, base[k][1] + (top[k][1] - base[k][1]) * f,
                               base[k2][0] + (top[k2][0] - base[k2][0]) * f, base[k2][1] + (top[k2][1] - base[k2][1]) * f))
                L.segs(fl, AMBER if (b + k) % 3 == 0 else DIM, 1.2, 0.75 if (b + k) % 3 == 0 else 0.5)
        L.black(top)
        L.lines([top], AMBER if g_ >= 1 else WHITE, 2.0, 1.0, close=True)
    label(L, t, 12, "we'll build our way out again", 'A CITY OF 169 BLOCKS, EACH ROOF RIDING ONE BAND OF THE SPECTRUM', 91.78, 94.2, t - u, box=True)
    return L.finish(bg('night'), flash=_cutflash(u))


# ---------------------------------------------------------------- 13. cold rain: ripples
_RG = None


def ripples(L, t, u, d):
    L.begin(t)
    global _RG
    if _RG is None:
        gx, gz = np.meshgrid(np.linspace(-11, 11, 150), np.linspace(1.3, 15, 70) ** 1.0)
        _RG = (gx.ravel(), gz.ravel())
    gx, gz = _RG
    hgt = np.zeros_like(gx)
    k0 = int(t / 0.34)
    for k in range(k0 - 9, k0 + 1):
        td = k * 0.34
        age = t - td
        if age <= 0:
            continue
        dx, dz = (rnd(k, 1) - 0.5) * 15, 2.0 + rnd(k, 2) * 9.5
        r = np.hypot(gx - dx, gz - dz)
        front = 2.9 * age
        hgt += 0.55 * math.exp(-age * 0.8) * np.sin(5.0 * (r - front)) * np.exp(-((r - front) / 0.8) ** 2)
    F_, camh, hy = 640.0, 2.1, 330
    sx = 960 + F_ * gx / gz
    sy = hy + F_ * (camh - hgt) / gz
    wts = (0.5 + 6.0 * np.abs(hgt)) * np.clip(4.0 / gz, 0.3, 2.2)
    L.splat(np.stack([sx, sy], 1), ICE, amp=2.6, blur=1.0, wts=wts)
    L.line(0, hy + F_ * camh / 15, W, hy + F_ * camh / 15, DIM, 1.2, 0.4)
    n = 130
    r = rnds(n * 3, 15, 5).reshape(n, 3)
    rx = (r[:, 0] * (W + 300) - t * 160 * (0.8 + 0.4 * r[:, 2])) % (W + 300) - 100
    ry = (r[:, 1] * (H + 200) + t * 1500 * (0.8 + 0.4 * r[:, 2])) % (H + 200) - 100
    L.segs(np.stack([rx, ry, rx - 7, ry + 60 + 50 * r[:, 2]], 1), ICE, 1.3, 0.38)
    label(L, t, 13, 'cold rain falling on the empty fields', 'RIPPLES FROM POINT SOURCES ACROSS 10500 POINTS', 101.14, 103.9, t - u)
    return L.finish(bg('night'), flash=_cutflash(u), gain=ramp(u, 0, 0.25))


# ---------------------------------------------------------------- 14. a harvest: L-systems
def harvest(L, t, u, d):
    L.begin(t)
    gy = 940
    L.line(60, gy, W - 60, gy, DIM, 1.3, 0.6)
    g = ease(ramp(u, 0.05, d - 0.5))
    tips = []
    for k, (x, hh) in enumerate(((250, 560), (590, 700), (960, 620), (1320, 740), (1670, 580))):
        D = sims.lsys(k)
        S, order = D['segs'], D['order']
        gk = clamp(g * 1.15 - 0.03 * k)
        m = order <= gk
        if not m.any():
            continue
        s = S[m]
        sway = 26 * math.sin(t * 1.4 + k * 1.3)
        y0 = s[:, 1] * hh
        y1 = s[:, 3] * hh
        x0 = x + s[:, 0] * hh + sway * (y0 / hh) ** 2
        x1 = x + s[:, 2] * hh + sway * (y1 / hh) ** 2
        seg = np.stack([x0, gy + y0, x1, gy + y1], 1)
        dp = s[:, 4]
        L.segs(seg[dp <= 1], WHITE, 2.4, 0.85)
        L.segs(seg[(dp > 1) & (dp <= 3)], TEAL, 1.6, 0.8)
        L.segs(seg[dp > 3], GOLD if k % 2 == 0 else TEAL, 1.3, 0.8)
        front = (order[m] > gk - 0.03) & (gk < 1)
        tips.append(seg[front][:, 2:])
    if tips:
        tp = np.vstack(tips)
        if len(tp):
            L.dots(tp, WHITE, d=4, a=1.0)
    label(L, t, 14, 'cleverer ways to make a harvest yield', 'L-SYSTEM: X > F+[[X]-X]-F[-FX]+X, F > FF, FIVE GENERATIONS', 104.62, 107.5, t - u, box=True)
    return L.finish(bg('night'), flash=_cutflash(u))


# ---------------------------------------------------------------- 15. a cleaner key: Chladni
def chladni(L, t, u, d):
    L.begin(t)
    C = sims.chladni()
    bp = A.beatpos(t - 0.02)
    q = int(math.floor(bp / 2.0))
    fr = (bp / 2.0 - q)
    k1 = q % len(sims.MODES)
    k0 = (q - 1) % len(sims.MODES)
    mv = ease(ramp(fr, 0.0, 0.28))
    a_, b_ = C[f'm{k0}'], C[f'm{k1}']
    n = len(a_)
    p = a_ + (b_ - a_) * mv
    shake = 0.004 + 0.03 * (1 - mv) * (1 if fr < 0.3 else 0) + 0.006 * A.kick(t)
    jit = np.stack([RN[(hsh(int(t * 30), 1) + np.arange(n) * 3) & (NT - 1)], RN[(hsh(int(t * 30), 2) + np.arange(n) * 5) & (NT - 1)]], 1) - 0.5
    p = p + jit * shake
    side = 760
    x0, y0 = 960 - side / 2, 70
    L.splat(p * side + (x0, y0), GOLD, amp=2.6, blur=1.0)
    L.lines([[(x0, y0), (x0 + side, y0), (x0 + side, y0 + side), (x0, y0 + side)]], DIM, 1.4, 0.7, close=True)
    md = sims.MODES[k1]
    L.text('MODE (%d, %d)' % md, x0 + side + 40, y0 + 30, 22, col=DIM, w=1.6, rev=ramp(fr, 0, 0.2))
    label(L, t, 15, 'factories humming in a cleaner key', 'CHLADNI FIGURES: 9000 GRAINS OF SAND ON A VIBRATING PLATE', 108.18, 111.2, t - u)
    return L.finish(bg('night'), flash=_cutflash(u), bloom=0.8)


# ---------------------------------------------------------------- 16. quiet wheels: cycloids
def wheels(L, t, u, d):
    L.begin(t)
    for k, (y, r, col, spd, lead) in enumerate(((330, 78, AMBER, 520, 0.0), (590, 112, TEAL, 470, 0.35), (850, 58, WHITE, 560, 0.15))):
        x0 = -220.0
        xc = x0 + (u - lead) * spd
        th = (xc - x0) / r
        L.line(0, y, W, y, DIM, 1.2, 0.5)
        if th <= 0:
            continue
        cyy = y - r
        # the wheel
        L.lines([circ(xc, cyy, r)], col, 2.2, 0.9, close=True)
        L.segs([(xc, cyy, xc + r * math.sin(th + j * TAU / 8) * -1, cyy + r * math.cos(th + j * TAU / 8)) for j in range(8)], col, 1.2, 0.5)
        # the curve a point on the rim draws
        tt = np.linspace(0, th, max(8, int(th * 14)))
        cyc = np.stack([x0 + r * (tt - np.sin(tt)), y - r * (1 - np.cos(tt))], 1)
        L.lines([cyc], col, 3.0, 1.0)
        cur = np.stack([x0 + r * tt - 0.5 * r * np.sin(tt), y - r + 0.5 * r * np.cos(tt)], 1)
        L.lines([cur], col, 1.4, 0.5)
        L.disc(cyc[-1, 0], cyc[-1, 1], 6, WHITE, 1.0)
        L.disc(xc, cyy, 4, col, 1.0)
    label(L, t, 16, 'quiet wheels turning down the street', 'CYCLOIDS: x = r(t - sin t), y = r(1 - cos t)', 111.78, 114.6, t - u, box=True)
    return L.finish(bg('night'), flash=_cutflash(u))


# ---------------------------------------------------------------- 17. give it to everyone: fireflies
_FF = None


def _flies():
    global _FF
    if _FF is None:
        rs = np.random.RandomState(17)
        pts = []
        for j in range(21):
            for i in range(39):
                pts.append((i * 50 + 10 + (25 if j % 2 else 0) + rs.rand() * 34 - 17, j * 52 + 20 + rs.rand() * 34 - 17))
        P = np.array(pts)
        c = np.argmin(np.hypot(P[:, 0] - 960, P[:, 1] - 500))
        dist = np.hypot(P[:, 0] - P[c, 0], P[:, 1] - P[c, 1])
        D = np.hypot(P[:, None, 0] - P[None, :, 0], P[:, None, 1] - P[None, :, 1])
        nb = np.argsort(D, 1)[:, 1:3]
        _FF = (P, dist, nb, rs.rand(len(P)), rs.rand(len(P)), c)
    return _FF


def fireflies(L, t, u, d):
    L.begin(t)
    P, dist, nb, r1, r2, c = _flies()
    n = len(P)
    ts = t - u
    # how far the light has been handed on
    R = 150 * ramp(t, 117.2, 120.4) + 430 * ease(ramp(t, 120.8, 123.4)) + 700 * ease(ramp(t, 123.4, 126.6))
    ta_reach = dist <= R
    # per-fly time since it was reached (approximate from radius history)
    def reach_time(dd):
        # invert R(t) piecewise
        tt = np.where(dd <= 150, 117.2 + 3.2 * dd / 150.0,
                      np.where(dd <= 580, 120.8 + 2.6 * np.clip((dd - 150) / 430.0, 0, 1) ** 0.6, 123.4 + 3.2 * np.clip((dd - 580) / 700.0, 0, 1) ** 0.6))
        return tt
    ta = reach_time(dist)
    ta[c] = ts
    on = t >= ta
    sync = np.clip((t - ta - 0.6) / 2.6, 0, 1)
    sync = np.maximum(sync, ramp(t, 127.2, 128.6))
    bp = A.beatpos(t)
    own = t * (0.9 + 0.8 * r1) + r2 * 7
    ph = own * (1 - sync) + bp * sync
    fl = np.exp(-3.4 * (ph - np.floor(ph))) * on
    fl[c] = math.exp(-4.5 * (bp - math.floor(bp)))
    # resting dots
    L.dots(P[~on], DIM, d=3.0, a=0.6)
    L.dots(P[on & (sync < 0.5)], ICE, d=3.6, a=0.6)
    L.dots(P[on & (sync >= 0.5)], AMBER, d=4.0, a=0.75)
    for lo, hi, dsz in ((0.12, 0.35, 6.5), (0.35, 0.65, 10.0), (0.65, 1.01, 14.0)):
        m = (fl >= lo) & (fl < hi)
        L.dots(P[m & (sync < 0.5)], ICE, d=dsz, a=0.9)
        L.dots(P[m & (sync >= 0.5)], GOLD, d=dsz, a=1.0)
    # the lattice lights up between flies that keep time together
    segs = []
    for i in np.where(sync > 0.85)[0]:
        for j in nb[i]:
            if sync[j] > 0.85:
                segs.append((P[i, 0], P[i, 1], P[j, 0], P[j, 1]))
    beat_fl = math.exp(-3.4 * (bp - math.floor(bp)))
    L.segs(segs, AMBER, 1.5, 0.2 + 0.6 * beat_fl)
    L.disc(P[c, 0], P[c, 1], 5 + 9 * fl[c], AMBER, 1.0)
    if R > 0 and t < 126.6:
        L.lines([circ(P[c, 0], P[c, 1], R)], AMBER, 1.3, 0.35, close=True)
    ly = lyric_seq(t, [('give it to everyone', 116.78, 119.4), ('not just the few', 120.78, 123.3), ('the tools that we share', 123.42, 126.9), ('are the tools that come true', 127.40, 130.3)])
    label(L, t, 17, ly[0], 'COUPLED OSCILLATORS FALLING INTO STEP (KURAMOTO), N = %d' % n, ly[1], ly[2], ts, box=True)
    return L.finish(bg('night'), flash=_cutflash(u) + 0.8 * ein(ramp(t, B(72) - 0.2, B(72)), 2))


def timeline():
    return [
        (B(48), B(55), city),
        (B(55), 104.25, ripples),
        (104.25, 107.85, harvest),
        (107.85, 111.45, chladni),
        (111.45, B(64), wheels),
        (B(64), B(72), fireflies),
    ]
