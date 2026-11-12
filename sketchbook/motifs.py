"""Reusable code-drawn motifs."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common'))
from engine import *


def pencil(c, x, y, ang=-0.95, s=1.0, body=YEL, a=1.0):
    """a pencil whose tip is at (x, y); ang = direction the body extends from the tip"""
    L, wd, tip = 190 * s, 13 * s, 34 * s
    def P(u, v):
        ca, sa = math.cos(ang), math.sin(ang)
        return (x + u * ca - v * sa, y + u * sa + v * ca)
    tri = np.array([P(0, 0), P(tip, -wd), P(tip, wd)])
    lead = np.array([P(0, 0), P(tip * 0.34, -wd * 0.34), P(tip * 0.34, wd * 0.34)])
    bod = np.array([P(tip, -wd), P(L, -wd), P(L, wd), P(tip, wd)])
    fer = np.array([P(L, -wd), P(L + 18 * s, -wd), P(L + 18 * s, wd), P(L, wd)])
    era = np.array([P(L + 18 * s, -wd), P(L + 40 * s, -wd), P(L + 40 * s, wd), P(L + 18 * s, wd)])
    c.fill(np.vstack([tri, bod[1:3], era[1:3]]), (NIGHT if c.night else PAPER), mul=False, wob=0)
    c.fill(bod, body, a=a, wob=0.6, seed=1, off=(2, 2))
    c.fill(era, CORAL, a=a, wob=0.6, seed=2, off=(2, 2))
    c.fill(lead, c.ink, mul=False, wob=0)
    for k, q in enumerate((tri, bod, fer, era)):
        c.pl(q, w=2.2 * max(0.7, s), close=True, wob=0.7, seed=900 + k)
    c.line(*P(tip, 0), *P(L, 0), w=1.4, a=0.6, wob=0.6, seed=905)


def cloud_shape(x, y, w, h, seed=0, n=5):
    th = np.linspace(math.pi, TAU, 60)
    ph = rnd(seed, 1) * 3
    b = 0.20 * np.abs(np.sin(th * n * 0.5 + ph)) + 0.05 * np.sin(th * 3 + ph)
    top = np.stack([x + (w / 2) * np.cos(th) * (1 + b * 0.4), y + h * np.sin(th) * (1 + b * 1.6)], 1)
    xs = np.linspace(x + w / 2, x - w / 2, 12)[1:-1]
    bot = np.stack([xs, y + h * 0.10 * np.sin(xs * 0.03 + ph)], 1)
    return np.vstack([top, bot])


def cloud(c, x, y, w, h, seed=0, shade=0.5, rev=1.0, fillc=None, lw=2.4, gap=8, ang=-0.5):
    sh = cloud_shape(x, y, w, h, seed)
    if fillc is not None:
        c.fill(sh, fillc, off=(5, 4), seed=seed)
    if shade > 0:
        lower = sh.copy()
        lower[:, 1] = np.maximum(lower[:, 1], y - h * (0.15 + 0.8 * shade) + 12 * np.sin(lower[:, 0] * 0.02 + seed))
        c.hatch(lower, ang=ang, gap=gap, w=1.5, a=0.55, seed=seed, rev=rev)
    c.pl(sh, w=lw, close=True, seed=seed, rev=rev, wob=2.0)


def turbine(c, x, y, h, ang, seed=0, fillc=None, w=2.2, rev=1.0, a=0.92, col=None):
    """wind turbine with base at (x, y), tower height h, rotor angle ang"""
    bw, tw = h * 0.035, h * 0.014
    ty = y - h
    r2 = ramp(rev, 0.0, 0.5)
    c.pl([[x - bw, y], [x - tw, ty]], w=w, seed=seed, rev=r2, a=a, col=col, wob=1.0)
    c.pl([[x + bw, y], [x + tw, ty]], w=w, seed=seed + 1, rev=r2, a=a, col=col, wob=1.0)
    if rev < 0.5:
        return
    bl = h * 0.56 * ease(ramp(rev, 0.5, 1.0))
    for k in range(3):
        an = ang + k * TAU / 3
        u = np.array([0.0, 0.08, 0.3, 0.7, 1.0, 0.7, 0.3, 0.08])
        v = np.array([0.0, 0.050, 0.060, 0.030, 0.0, -0.012, -0.022, -0.030])
        pts = np.stack([u * bl, v * bl], 1)
        pts = rot(pts, an) + (x, ty)
        if fillc is not None:
            c.fill(pts, fillc, off=(3, 3), wob=0.5, seed=seed + k)
        c.pl(pts, w=w * 0.85, close=True, seed=seed + 10 + k, a=a, col=col, wob=0.6, boil=0.3, seg=14)
    hr = max(2.5, h * 0.022)
    c.fill(circ(x, ty, hr), PAPER if not c.night else NIGHT, mul=False, wob=0)
    c.pl(circ(x, ty, hr), w=w, close=True, seed=seed + 20, a=a, col=col, wob=0.4)


def sun_disc(c, x, y, r, phase=0.0, bands=7, cols=(YEL, CORAL, PINK), seed=0, a=1.0, top_only=False, gaps=True, bg=None):
    """retro striped sun: colour graded top to bottom, sliced by widening gaps"""
    c.clip(circ(x, y, r), wob=1.2, seed=seed)
    g = cairo.LinearGradient(0, y - r, 0, y + r)
    g.add_color_stop_rgba(0.0, *cols[0], a)
    g.add_color_stop_rgba(0.5, *cols[1], a)
    g.add_color_stop_rgba(1.0, *cols[2], a)
    cx = c.cx
    cx.rectangle(x - r - 4, y - r - 4, 2 * r + 8, 2 * r + 8)
    if not c.night:
        cx.set_operator(cairo.OPERATOR_MULTIPLY)
    cx.set_source(g)
    cx.fill()
    cx.set_operator(cairo.OPERATOR_OVER)
    if gaps:
        bgc = bg if bg is not None else (NIGHT if c.night else PAPER)
        for k in range(bands):
            p = ((k + phase) % bands) / bands
            yy = y - r * 0.12 + r * 1.15 * p ** 1.25
            th = r * (0.012 + 0.085 * p)
            c.fill(rect(x - r - 6, yy, 2 * r + 12, th), bgc, mul=False, wob=1.0, seed=seed + k)
    c.unclip()


def sun_rays(c, x, y, r0, r1, n=24, ang=0.0, seed=0, w=2.4, a=0.9, col=None, alt=0.55, rev=1.0):
    for k in range(n):
        th = ang + k * TAU / n
        l1 = r0 + (r1 - r0) * (1.0 if k % 2 == 0 else alt) * rev
        c.line(x + r0 * math.cos(th), y + r0 * math.sin(th), x + l1 * math.cos(th), y + l1 * math.sin(th),
               w=w, a=a, seed=seed + k, col=col, wob=1.0)


def gridfloor(c, hy, vx, scroll, bottom=H, cols=18, rows=11, spacing=210, col=None, w=1.8, a=0.8, rev=1.0, seed=0, x0=0, x1=W):
    """perspective grid receding to the horizon hy with vanishing point vx"""
    D = bottom - hy
    for k in range(-cols, cols + 1):
        xb = vx + k * spacing
        # clip the line to the frame width
        xe, ye = xb, bottom
        if xb < x0 - 600 or xb > x1 + 600:
            continue
        c.line(vx + (xb - vx) * 0.002, hy + D * 0.002, xe, ye, w=w, a=a, seed=seed + 100 + k, col=col, rev=rev, wob=0.8, passes=1)
    f = scroll % 1.0
    for k in range(rows):
        z = k + 1 - f
        if z <= 0.02:
            continue
        yy = hy + D / (z * 0.85 + 0.15) if z >= 1 else hy + D * (1 + (1 - z) * 0.9)
        yy = hy + D / max(0.2, z) * 1.0
        if yy > bottom + 4:
            continue
        aa = a * clamp((yy - hy) / 30.0)
        c.line(x0, yy, x1, yy, w=w, a=aa, seed=seed + 300 + k, col=col, rev=rev, wob=0.8, passes=1)


CAR_KINDS = [
    # sedan
    dict(body=[(0, -16), (2, -40), (20, -46), (58, -49), (84, -76), (150, -76), (178, -50), (228, -44), (236, -30), (236, -16)],
         win=[[(66, -52), (90, -71), (116, -71), (116, -52)], [(122, -52), (122, -71), (148, -71), (168, -52)]], wheels=(50, 186), L=236),
    # hatchback
    dict(body=[(0, -16), (2, -42), (16, -50), (60, -52), (86, -80), (176, -80), (206, -46), (214, -30), (214, -16)],
         win=[[(70, -55), (92, -75), (126, -75), (126, -55)], [(132, -55), (132, -75), (172, -75), (192, -55)]], wheels=(46, 170), L=214),
    # van
    dict(body=[(0, -16), (0, -50), (10, -58), (40, -62), (62, -98), (250, -98), (254, -16)],
         win=[[(48, -64), (66, -92), (104, -92), (104, -64)]], wheels=(52, 204), L=254),
    # lorry
    dict(body=[(0, -16), (0, -60), (14, -92), (58, -92), (58, -16)],
         box=[(66, -16), (66, -128), (330, -128), (330, -16)], win=[[(8, -62), (20, -86), (50, -86), (50, -62)]], wheels=(34, 250, 296), L=330),
]


def car(c, x, y, s=1.0, kind=0, wang=0.0, seed=0, fillc=None, face=1, light=None, col=None, w=2.2, rev=1.0):
    """side-view boxy car. (x, y) = ground point at the rear; face=1 faces left (front at x), -1 faces right"""
    K = CAR_KINDS[kind % len(CAR_KINDS)]
    def T(p):
        p = np.asarray(p, float) * s
        if face < 0:
            p[:, 0] = K['L'] * s - p[:, 0]
        return p + (x, y)
    body = T(K['body'])
    if fillc is not None:
        c.fill(body, fillc, off=(4, 3), seed=seed)
        if 'box' in K:
            c.fill(T(K['box']), fillc, off=(4, 3), seed=seed + 1)
    c.pl(body, w=w, close=True, seed=seed, col=col, rev=rev, wob=1.0)
    if 'box' in K:
        c.pl(T(K['box']), w=w, close=True, seed=seed + 1, col=col, rev=rev, wob=1.0)
    for k, wn in enumerate(K['win']):
        c.pl(T(wn), w=w * 0.75, close=True, seed=seed + 5 + k, col=col, rev=rev, wob=0.7, passes=1)
    r = 17 * s
    for k, wx in enumerate(K['wheels']):
        p = T([(wx, -17)])[0]
        c.fill(circ(p[0], p[1], r), NIGHT if c.night else PAPER, mul=False, wob=0)
        c.pl(circ(p[0], p[1], r), w=w * 1.2, close=True, seed=seed + 20 + k, col=col, wob=0.5, rev=rev)
        c.pl(circ(p[0], p[1], r * 0.45), w=w * 0.7, close=True, seed=seed + 30 + k, col=col, wob=0.3, passes=1, rev=rev)
        for j in range(4):
            an = wang * face + j * TAU / 4
            c.line(p[0], p[1], p[0] + r * 0.9 * math.cos(an), p[1] + r * 0.9 * math.sin(an), w=w * 0.6, seed=seed + 40 + j, col=col, wob=0.2, passes=1, a=0.7)
    if light is not None:
        fp = T([(4, -34)])[0]
        c.dots([fp], 5 * s, col=light)


def building(c, x, base, w, h, seed=0, lit=0.0, litc=YEL, rev=1.0, fillc=None, col=None, lw=2.2, win=True, t=0.0):
    """a building growing upward; rev 0..1 raises it"""
    hh = h * ease(rev)
    if hh < 3:
        return
    top = base - hh
    r = rect(x, top, w, hh)
    if fillc is not None:
        c.fill(r, fillc, off=(5, 4), seed=seed)
    style = int(rnd(seed, 3) * 5)
    c.pl([[x, base], [x, top], [x + w, top], [x + w, base]], w=lw, seed=seed, col=col, wob=1.0)
    if rev > 0.95:
        if style == 0:
            c.line(x + w * 0.5, top, x + w * 0.5, top - h * 0.16, w=lw * 0.8, seed=seed + 1, col=col, wob=0.5)
        elif style == 1:
            c.pl([[x + w * 0.2, top], [x + w * 0.2, top - 16], [x + w * 0.8, top - 16], [x + w * 0.8, top]], w=lw * 0.8, seed=seed + 1, col=col, wob=0.6)
        elif style == 2:
            c.pl([[x, top], [x + w * 0.5, top - w * 0.35], [x + w, top]], w=lw * 0.8, seed=seed + 1, col=col, wob=0.6)
        elif style == 3:
            c.pl(circ(x + w * 0.5, top, w * 0.3, math.pi, TAU), w=lw * 0.8, seed=seed + 1, col=col, wob=0.5)
    if win and w > 26:
        nx = max(2, int(w / 20))
        ny = max(1, int(hh / 24))
        gx = w / (nx + 0.5)
        gy = 24
        segs, lits = [], []
        for j in range(ny):
            yy = base - hh + 14 + j * gy
            if yy > base - 8:
                break
            for i in range(nx):
                xx = x + gx * (i + 0.45)
                rr = rnd(seed, i, j)
                if rr < lit:
                    lits.append(rect(xx, yy, gx * 0.55, 10))
                else:
                    segs.append((xx, yy + 5, xx + gx * 0.5, yy + 5))
        c.ticks(segs, w=1.4, a=0.55, jit=0.7, seed=seed, col=col)
        if lits:
            c.fill(lits, litc, wob=0, off=(1, 1))


def gear(c, x, y, r, teeth, ang, seed=0, fillc=None, depth=0.16, col=None, w=2.4, spokes=5, rev=1.0):
    n = teeth
    pts = []
    for k in range(n):
        a0 = ang + k * TAU / n
        d = TAU / n
        for (f, rr) in ((0.0, r), (0.18, r * (1 + depth)), (0.42, r * (1 + depth)), (0.60, r), ):
            pts.append((x + rr * math.cos(a0 + f * d), y + rr * math.sin(a0 + f * d)))
    pts = np.array(pts)
    hole = circ(x, y, r * 0.22)
    if fillc is not None:
        c.fill([pts, hole[::-1]], fillc, off=(5, 4), seed=seed, evenodd=True, wob=0.6)
    c.pl(pts, w=w, close=True, seed=seed, col=col, wob=0.5, boil=0.25, seg=7, rev=rev)
    c.pl(hole, w=w * 0.9, close=True, seed=seed + 1, col=col, wob=0.5, rev=rev)
    c.pl(circ(x, y, r * 0.78), w=w * 0.6, close=True, seed=seed + 2, col=col, wob=0.5, passes=1, a=0.7, rev=rev)
    for k in range(spokes):
        an = ang + k * TAU / spokes
        c.pl(circ(x + r * 0.5 * math.cos(an), y + r * 0.5 * math.sin(an), r * 0.13), w=w * 0.7, close=True, seed=seed + 5 + k, col=col, wob=0.4, passes=1, rev=rev)


def hypotrochoid(x, y, R, r, d, turns, n=900, ang=0.0):
    t = np.linspace(0, TAU * turns, n)
    k = (R - r) / r
    px = (R - r) * np.cos(t) + d * np.cos(k * t)
    py = (R - r) * np.sin(t) - d * np.sin(k * t)
    return rot(np.stack([px, py], 1), ang) + (x, y)


def sprout(c, x, y, h, grow, seed=0, leafc=None, col=None, w=2.0):
    """a seedling growing from (x, y)"""
    g = ease(grow)
    if g <= 0.02:
        return
    lean = (rnd(seed, 1) - 0.5) * 0.5
    u = np.linspace(0, 1, 12)
    st = np.stack([x + h * lean * u ** 2, y - h * u], 1)
    c.pl(st, w=w, seed=seed, rev=g, col=col, wob=0.8)
    for k, (uu, side) in enumerate(((0.45, -1), (0.7, 1), (1.0, -1), (1.0, 1))):
        lg = ease(ramp(g, uu * 0.8, uu * 0.8 + 0.3))
        if lg <= 0:
            continue
        bx, by = x + h * lean * uu ** 2, y - h * uu
        L = h * 0.42 * lg
        an = -math.pi / 2 + side * (0.9 - 0.2 * k)
        s = np.linspace(0, 1, 9)
        wd = np.sin(s * math.pi) * 0.24
        up = np.stack([s * L, -wd * L], 1)
        dn = np.stack([s[::-1] * L, wd[::-1] * L], 1)
        leaf = rot(np.vstack([up, dn[1:-1]]), an) + (bx, by)
        if leafc is not None:
            c.fill(leaf, leafc, off=(3, 2), wob=0.4, seed=seed + k)
        c.pl(leaf, w=w * 0.85, close=True, seed=seed + 3 + k, col=col, wob=0.5)


def sunflower(c, x, y, r, grow=1.0, seed=0, ang=0.0, petc=YEL, seedc=None, col=None, n=260, petals=21):
    g = ease(grow)
    if g <= 0.01:
        return
    # petals
    for k in range(petals):
        an = ang + k * TAU / petals
        pg = ease(ramp(g, 0.3 + 0.4 * k / petals, 0.6 + 0.4 * k / petals))
        if pg <= 0:
            continue
        L = r * 0.62 * pg
        s = np.linspace(0, 1, 8)
        wd = np.sin(s * math.pi) ** 0.8 * 0.2
        leaf = np.vstack([np.stack([r * 0.52 + s * L, -wd * L], 1), np.stack([r * 0.52 + s[::-1] * L, wd[::-1] * L], 1)[1:-1]])
        leaf = rot(leaf, an) + (x, y)
        if petc is not None:
            c.fill(leaf, petc, off=(3, 3), wob=0.4, seed=seed + k)
        c.pl(leaf, w=1.9, close=True, seed=seed + 50 + k, col=col, wob=0.5, passes=1)
    # phyllotaxis seeds
    m = int(n * ramp(g, 0.0, 0.7))
    k = np.arange(1, m + 1)
    rr = r * 0.52 * np.sqrt(k / n)
    th = k * 2.39996323 + ang
    pts = np.stack([x + rr * np.cos(th), y + rr * np.sin(th)], 1)
    c.dots(pts, np.clip(r * 0.012 + r * 0.02 * (k / n), 1.2, 9), col=seedc if seedc is not None else col, a=0.9)


def birds(c, t, n=9, seed=0, y0=260, spread=160, speed=120, x0=-200, col=None, w=2.2, scale=1.0, t0=0.0):
    for k in range(n):
        ph = rnd(seed, k) * 10
        bx = x0 + (t - t0) * speed * (0.85 + 0.3 * rnd(seed, k, 2)) - (k % 5) * 70 * scale - rnd(seed, k, 3) * 200
        by = y0 + ((k * 37) % 7 - 3) * spread / 7 + 14 * math.sin(t * 1.3 + ph) + abs(k % 5 - 2) * 30 * scale
        if bx < -60 or bx > W + 60:
            continue
        fl = math.sin(t * 9 + ph)
        s = (12 + 8 * rnd(seed, k, 4)) * scale
        lw = np.array([[bx - s * 1.5, by - s * (0.2 + 0.6 * fl)], [bx - s * 0.7, by - s * 0.35 * fl - s * 0.2], [bx, by]])
        rw = np.array([[bx, by], [bx + s * 0.7, by - s * 0.35 * fl - s * 0.2], [bx + s * 1.5, by - s * (0.2 + 0.6 * fl)]])
        c.pl(np.vstack([lw, rw[1:]]), w=w, seed=seed + k, col=col, wob=0.4, passes=1, boil=0.2, seg=6)


def memphis(c, kind, x, y, s, ang=0.0, col=CORAL, seed=0, pop=1.0, col2=None):
    """80s confetti shapes"""
    p = back(pop)
    if p <= 0.02:
        return
    s = s * p
    kind = kind % 7
    if kind == 0:   # squiggle
        u = np.linspace(-1, 1, 40)
        q = rot(np.stack([u * s, 0.22 * s * np.sin(u * 9)], 1), ang) + (x, y)
        c.pl(q, w=7, a=1.0, col=col, seed=seed, wob=0.6, passes=1)
    elif kind == 1:  # triangle with offset fill
        q = rot(np.array([[0, -s], [s * 0.9, s * 0.6], [-s * 0.9, s * 0.6]]), ang) + (x, y)
        c.fill(q, col, off=(8, 7), seed=seed)
        c.pl(q, w=2.6, close=True, seed=seed, wob=0.8)
    elif kind == 2:  # ring
        c.pl(circ(x, y, s * 0.7), w=8, a=1.0, col=col, seed=seed, close=True, wob=0.6, passes=1)
    elif kind == 3:  # zigzag
        u = np.arange(7)
        q = rot(np.stack([(u - 3) * s * 0.33, ((u % 2) - 0.5) * s * 0.5], 1), ang) + (x, y)
        c.pl(q, w=3.0, seed=seed, wob=0.6)
        c.pl(q + (7, 7), w=6, a=1.0, col=col, seed=seed + 1, wob=0.6, passes=1)
    elif kind == 4:  # plus
        for an in (ang, ang + math.pi / 2):
            c.line(x - s * 0.6 * math.cos(an), y - s * 0.6 * math.sin(an), x + s * 0.6 * math.cos(an), y + s * 0.6 * math.sin(an), w=8, a=1.0, col=col, seed=seed, wob=0.4, passes=1)
    elif kind == 5:  # half disc with outline
        q = circ(x, y, s * 0.75, ang, ang + math.pi)
        c.fill(q, col, off=(7, 6), seed=seed)
        c.pl(q, w=2.6, close=True, seed=seed, wob=0.7)
    else:            # dot grid
        g = np.array([(i, j) for i in range(-2, 3) for j in range(-2, 3)], float) * s * 0.3
        c.dots(rot(g, ang) + (x, y), s * 0.07, col=col2 if col2 is not None else col)


def panel_frame(c, poly, seed=0, w=4.5):
    c.pl(poly, w=w, close=True, seed=seed, wob=1.6, a=0.95, boil=0.4)
    c.pl(np.asarray(poly) + (3, 2), w=1.5, close=True, seed=seed + 1, wob=2.2, a=0.6, passes=1)


def pop_word(c, s, x, y, size, t, t0, fill=None, font='blk', rot=0.0, seed=0, dur=0.16, **k):
    """display word that snaps in at t0"""
    if t < t0:
        return
    p = (t - t0) / dur
    sc = back(min(1.0, p), 2.4)
    c.text(s, x, y + (1 - sc) * size * 0.08, size * (0.55 + 0.45 * sc), font=font, fill=fill, rot=rot, seed=seed, **k)


def band_words(c, t, words, y=1010, size=112, cols=(YEL, PINK, CYAN), seed=60, shadow=None, maxw=W - 150):
    """a paper strip with the sung line popping in word by word. words: ((text, time), ...)"""
    if t < words[0][1] - 0.12:
        return
    ws = [text_width(w_, size) for (w_, _) in words]
    tot = sum(ws) + size * 0.3 * (len(words) - 1)
    if tot > maxw:
        size = size * maxw / tot
        ws = [text_width(w_, size) for (w_, _) in words]
        tot = sum(ws) + size * 0.3 * (len(words) - 1)
    x = 960 - tot / 2
    p = back(ramp(t, words[0][1] - 0.12, words[0][1] + 0.05), 1.4)
    band = rot(rect(960 - (tot / 2 + 46) * p, y - size * 0.98, (tot + 92) * p, size * 1.36), -0.008, 960, y)
    bg = NIGHT if c.night else PAPER
    c.solid(band + (10, 9), c.ink, seed=seed + 40)
    c.solid(band, bg, seed=seed + 41)
    c.pl(band, w=3.4, close=True, seed=seed + 42, wob=1.0)
    for k, (w_, tw) in enumerate(words):
        pop_word(c, w_, x, y, size, t, tw, align='l', seed=seed + k, knock=True, fill=cols[k % len(cols)], off=(0, 0),
                 shadow=(shadow if shadow is not None else c.ink, (7, 6)) if not c.night else None, w=3.6)
        x += ws[k] + size * 0.3
