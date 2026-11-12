"""The chorus: six figures, three levels."""
from lum import *
import sims

WT = {
    1: dict(until=58.46, further=60.44, notice=61.20, believe=63.16, machine=64.64, turning=65.60, light=67.96, making=69.38, clean=71.66,
            until2=73.46, further2=74.84, notice2=75.68, tomorrow=77.52, dream=79.42, we=80.32, hands=83.20, well=84.04, again=86.52),
    2: dict(until=131.78, further=132.60, notice=133.48, believe=135.46, machine=136.92, turning=137.80, light=140.66, making=141.80, clean=143.92,
            until2=145.88, further2=147.08, notice2=147.90, tomorrow=149.80, dream=151.66, we=152.62, hands=155.46, well=156.42, again=158.76),
    3: dict(until=203.44, further=204.44, notice=205.34, believe=207.32, machine=208.76, turning=209.66, light=212.42, making=212.84, clean=215.66,
            until2=217.86, further2=218.82, notice2=219.62, tomorrow=220.68, dream=223.40, we=223.80, hands=227.12, well=228.18, again=230.44),
}
BGS = {1: 'night', 2: 'night', 3: 'dawn'}


def _cutflash(u, k=0.35):
    return k * (1 - ramp(u, 0, 0.16))


def title_words(L, t, wt, keys, y, size, cols, cx=960):
    words = ('UNTIL', 'FURTHER', 'NOTICE')
    ws = [hershey(w_, size, 'futuram')[1] for w_ in words]
    gap = size * 0.62
    x = cx - (sum(ws) + 2 * gap) / 2
    for k, w_ in enumerate(words):
        t0 = wt[keys[k]]
        if t >= t0:
            hit = 1 - ramp(t, t0, t0 + 0.35)
            L.text(w_, x, y, size, font='futuram', col=mixc(cols[k], WHITE, hit), w=size * 0.034 + 2.5 * hit, rev=ramp(t, t0 - 0.02, t0 + 0.16))
        x += ws[k] + gap


def rings(L, t, x, y, r0, col, n=4, span=520, a=0.5, t_start=0.0):
    bp = A.beatpos(t)
    for j in range(n):
        ph = ((bp - j) % n) / n
        L.lines([circ(x, y, r0 + span * ph)], col, 1.6, a * (1 - ph) ** 1.5, close=True)


# ---------------------------------------------------------------- 6. until further notice: the sun
def ch_title(L, t, u, d, lvl, wt):
    L.begin(t)
    R = (190, 215, 250)[lvl - 1] * back(ramp(u, 0, 0.35), 1.3)
    y = 430
    cols = ((GOLD, AMBER, AMBER), (GOLD, AMBER, CORAL), (WHITE, GOLD, ROSE))[lvl - 1]
    rings(L, t, 960, y, R * 1.1, cols[1], a=0.45)
    sun(L, t, 960, y, R, cols=cols, n=1100 + 300 * lvl)
    tc = ((WHITE, WHITE, WHITE), (ICE, WHITE, GOLD), (GOLD, WHITE, ROSE))[lvl - 1]
    title_words(L, t, wt, ('until', 'further', 'notice'), 930, 104, tc)
    L.text('FIG. 06', 92, H - 174, 20, col=DIM, a=0.95, rev=ramp(u, 0.05, 0.5), w=1.5)
    L.text("THE SONG'S OWN SPECTRUM, WRAPPED ROUND A DISC OF %d POINTS" % (1100 + 300 * lvl), 92, H - 142, 20, col=DIM, a=0.95, rev=ramp(u, 0.15, 0.9), w=1.5)
    return L.finish(bg(BGS[lvl]), flash=_cutflash(u, 0.6))


# ---------------------------------------------------------------- 7. i believe in the machine: life
_cellmask = {}


def cell_image(grid, col_img, cell):
    """grid-shaped colour image (h, w, 3 uint8) -> full frame with gaps between cells"""
    big = cv2.resize(col_img, (W, H), interpolation=cv2.INTER_NEAREST)
    if cell not in _cellmask:
        m = np.ones((H, W), np.uint8)
        g = 2 if cell >= 16 else 1
        for k in range(g):
            m[k::cell, :] = 0
            m[:, k::cell] = 0
        _cellmask[cell] = cv2.merge([m * 255] * 3)
    return cv2.bitwise_and(big, _cellmask[cell])


def _life_img(D, gf, cell, young, old):
    g0 = int(gf)
    f = gf - g0
    G = D['g']
    AG = D['age']
    g0 = min(g0, len(G) - 2)
    def frame(k):
        alive = G[k]
        ag = AG[k]
        kold = np.clip((ag.astype(np.float32) - 2) / 10.0, 0, 1)[:, :, None]
        colr = (np.array(young[::-1], np.float32) * (1 - kold) + np.array(old[::-1], np.float32) * kold) * 255
        return (colr * alive[:, :, None]).astype(np.uint8)
    a_, b_ = frame(g0), frame(g0 + 1)
    img = cv2.addWeighted(a_, 1 - f, b_, f, 0)
    return cell_image(G[g0], img, cell)


def ch_machine(L, t, u, d, lvl, wt):
    L.begin(t)
    if lvl == 1:
        D = sims.life_gun()
        gf = 196 + u * 16.56
        img = _life_img(D, gf, 20, WHITE, AMBER)
        img[H - 250:, :760] = 0
        L.image(img)
        label(L, t, 7, 'i believe in the machine', 'GAME OF LIFE: TWO GOSPER GLIDER GUNS', wt['believe'] - 0.5, wt['machine'] + 0.6, t - u)
    elif lvl == 3:
        D = sims.life_soup()
        gf = 3 + u * 60.0
        img = _life_img(D, gf, 10, WHITE, GOLD)
        img[H - 250:, :1100] = 0
        L.image(img)
        label(L, t, 7, 'i believe in the machine', 'GAME OF LIFE FROM RANDOM NOISE, 20736 CELLS, SIXTY GENERATIONS A SECOND', wt['believe'] - 0.5, wt['machine'] + 0.6, t - u)
    else:
        E = sims.epicycles()
        c, f, down = E['c'], E['f'], E['down']
        S = 430.0
        cx, cy = 960, 520
        N = len(down)
        pr = ramp(u, 0.12, d - 0.45)
        if 'path' not in E:
            j = np.arange(N)
            E['path'] = (c[None, :] * np.exp(1j * f[None, :] * TAU * j[:, None] / N)).sum(1)
        path = E['path']
        m = int(pr * (N - 1))
        # the machine: a chain of turning circles
        z = cx + 1j * cy
        terms = S * c * np.exp(1j * f * TAU * pr)
        pos = z + np.concatenate([[0], np.cumsum(terms)])
        rad = np.abs(terms)
        fade = 1 - ramp(u, d - 0.5, d - 0.1)
        if fade > 0:
            for k in range(len(c)):
                if rad[k] < 2.5:
                    break
                L.lines([circ(pos[k].real, pos[k].imag, rad[k])], ICE, 1.2, 0.33 * fade, close=True)
            arm = np.stack([pos.real, pos.imag], 1)
            L.lines([arm], WHITE, 1.6, 0.9 * fade)
            L.disc(pos[-1].real, pos[-1].imag, 6, WHITE, fade)
        # what it writes
        P = np.stack([cx + S * path.real, cy + S * path.imag], 1)
        runs = []
        st = None
        for i in range(m + 1):
            if down[i] and st is None:
                st = i
            if (not down[i] or i == m) and st is not None:
                if i - st > 1:
                    runs.append(P[st:i + 1 if down[i] else i])
                st = None
        L.lines(runs, AMBER, 4.2, 1.0)
        L.lines(runs, GOLD, 1.6, 0.8)
        label(L, t, 18, 'i believe in the machine', 'FOURIER EPICYCLES: 150 TURNING CIRCLES WRITING ONE WORD', wt['believe'] - 0.5, wt['machine'] + 0.6, t - u)
    return L.finish(bg(BGS[lvl]), flash=_cutflash(u))


# ---------------------------------------------------------------- 8. turning the wind into light
def _rotor(L, x, y, r, ang, col, a=1.0):
    segs = [(x, y, x + r * math.cos(ang + k * TAU / 3), y + r * math.sin(ang + k * TAU / 3)) for k in range(3)]
    L.segs(segs, col, 3.0, a)
    L.lines([circ(x, y, r * 1.06)], col, 1.3, 0.4 * a, close=True)
    L.disc(x, y, 5, col, a)


def ch_wind(L, t, u, d, lvl, wt):
    L.begin(t)
    D = sims.flow(lvl)
    P, off = D['p'], D['off']
    T, n, _ = P.shape
    fr = int(round(u * FPS))
    idx = (fr + off) % T
    ar = np.arange(n)
    cur = P[idx, ar]
    lag = 4
    prev = P[(idx - lag) % T, ar]
    ok = (idx >= lag) & (np.abs(cur[:, 0] - prev[:, 0]) < 150) & (np.abs(cur[:, 1] - prev[:, 1]) < 150)
    env = np.sin(np.pi * idx / T) ** 0.5
    seg = np.concatenate([prev, cur], 1)
    if lvl == 1:
        split = 960
        left = ok & (cur[:, 0] < split - 60)
        mid = ok & (cur[:, 0] >= split - 60) & (cur[:, 0] < split + 160)
        right = ok & (cur[:, 0] >= split + 160)
        L.segs(seg[left], ICE, 1.5, 0.55)
        L.segs(seg[mid], WHITE, 1.8, 0.8)
        L.segs(seg[right & (env > 0.5)], AMBER, 2.2, 1.0)
        L.segs(seg[right & (env <= 0.5)], AMBER, 1.6, 0.55)
        _rotor(L, 960, 540, 150, t * 4.2, WHITE)
        name = 'A FLOW FIELD THROUGH ONE VORTEX, 7000 PARTICLES'
    elif lvl == 2:
        x = cur[:, 0]
        L.segs(seg[ok & (x < 520)], ICE, 1.5, 0.55)
        L.segs(seg[ok & (x >= 520) & (x < 980)], TEAL, 1.7, 0.75)
        L.segs(seg[ok & (x >= 980) & (x < 1400)], GOLD, 1.9, 0.9)
        L.segs(seg[ok & (x >= 1400)], AMBER, 2.3, 1.0)
        for k, (vx, vy, g) in enumerate(((560, 420, 1), (1000, 660, -1), (1420, 400, 1))):
            _rotor(L, vx, vy, 110, g * t * 4.5 + k, WHITE)
        name = 'A FLOW FIELD THROUGH THREE VORTICES, 7000 PARTICLES'
    else:
        dd = np.hypot(cur[:, 0] - 960, cur[:, 1] - 480)
        L.segs(seg[ok & (dd > 620)], VIOLET, 1.6, 0.8)
        L.segs(seg[ok & (dd <= 620) & (dd > 380)], ROSE, 1.8, 0.9)
        L.segs(seg[ok & (dd <= 380) & (dd > 215)], GOLD, 2.0, 1.0)
        sun(L, t, 960, 480, 200, cols=(WHITE, GOLD, AMBER), n=1200, rays=0.6)
        name = 'A FLOW FIELD ROUND THE SUN, 11000 PARTICLES'
    label(L, t, 8, 'turning the wind into light', name, wt['turning'], wt['light'] + 0.6, t - u, box=True)
    return L.finish(bg(BGS[lvl]), flash=_cutflash(u))


# ---------------------------------------------------------------- 9. making the dirty things clean
_LUT = None


def _lut(n):
    stops = [ICE, TEAL, GOLD, AMBER, CORAL]
    out = np.zeros((n, 3), np.float32)
    for i in range(n):
        k = i / (n - 1) * (len(stops) - 1)
        j = min(len(stops) - 2, int(k))
        out[i] = mixc(stops[j], stops[j + 1], k - j)
    return out


def ch_clean(L, t, u, d, lvl, wt):
    L.begin(t)
    t_clean = wt['clean'] + 0.45
    ts = t - u
    pr = ramp(t, ts + 0.3, t_clean)
    if lvl == 2:
        S = sims.oddeven()['s']
        lut = (_lut(96)[:, ::-1] * 150).astype(np.uint8)
        kf = pr * (len(S) - 1)
        k0 = min(len(S) - 2, int(kf))
        a_ = lut[S[k0]]
        b_ = lut[S[k0 + 1]]
        img = cv2.addWeighted(a_, 1 - (kf - k0), b_, kf - k0, 0)
        img = cell_image(None, img, 20)
        img[H - 250:, :820] = 0
        L.image(img)
        label(L, t, 9, 'making the dirty things clean', 'ODD-EVEN TRANSPOSITION SORT, 54 ROWS OF 96', wt['making'], wt['clean'] + 0.5, ts)
        return L.finish(bg(BGS[lvl]), flash=_cutflash(u), bloom=0.3)
    Q = sims.quicksort()
    S, act = Q['s'], Q['act']
    k = int(pr * (len(S) - 1))
    a = S[k]
    n = len(a)
    placed = a == np.arange(n)
    sweep = ramp(t, t_clean, t_clean + 0.5)
    if lvl == 1:
        xs = np.linspace(200, 1720, n)
        base = 850
        hh = (a + 1) / n * 560
        segs = np.stack([xs, np.full(n, base), xs, base - hh], 1)
        L.segs(segs[~placed], DIM, 4.5, 0.85)
        for b in range(4):
            m = placed & (a * 4 // n == b)
            L.segs(segs[m], mixc(AMBER, GOLD, b / 3), 4.5, 1.0)
        if pr < 1:
            L.segs(segs[list(act[k])], WHITE, 6.5, 1.0)
        if 0 < sweep < 1:
            j = int(sweep * (n - 1))
            L.segs(segs[max(0, j - 3):j + 1], WHITE, 7, 1.0)
        L.line(180, base + 8, 1740, base + 8, DIM, 1.3, 0.6)
        name = 'QUICKSORT, N = 160, %d SWAPS' % (len(S) - 1)
    else:
        cx, cy, R0 = 960, 480, 215
        an = -math.pi / 2 + np.arange(n) * TAU / n + t * 0.25
        r1 = R0 + 26 + (a + 1) / n * 300
        segs = np.stack([cx + (R0 + 14) * np.cos(an), cy + (R0 + 14) * np.sin(an), cx + r1 * np.cos(an), cy + r1 * np.sin(an)], 1)
        L.segs(segs[~placed], VIOLET, 3.4, 0.8)
        for b in range(4):
            m = placed & (a * 4 // n == b)
            L.segs(segs[m], mixc(GOLD, ROSE, b / 3), 3.6, 1.0)
        if pr < 1:
            L.segs(segs[list(act[k])], WHITE, 6, 1.0)
        sun(L, t, cx, cy, R0 * 0.94, cols=(WHITE, GOLD, AMBER), n=1300, rays=0)
        name = 'QUICKSORT ROUND THE SUN, N = 160'
    label(L, t, 9, 'making the dirty things clean', name, wt['making'], wt['clean'] + 0.5, ts)
    return L.finish(bg(BGS[lvl]), flash=_cutflash(u))


# ---------------------------------------------------------------- 10. tomorrow's not a dream: terrain
def _height(x, z):
    h = 0.50 * np.sin(1.3 * x + 0.7 * z) + 0.35 * np.sin(2.1 * x - 1.1 * z + 1.0) + 0.22 * np.sin(3.9 * x + 0.5 * z + 2.0) + 0.3 * np.sin(0.5 * x + 1.7 * z)
    valley = np.clip((np.abs(x) - 0.5) / 2.2, 0, 1) ** 1.3
    return (h * 0.5 + 0.62) * valley


def terrain(L, t, hy, speed, col, col2=None, amp=1.0, nx=64, nz=34, a=1.0, lw=1.6):
    F_, camh = 620.0, 0.95
    dz = 0.42
    zc = t * speed
    fr = (zc / dz) % 1.0
    zb = math.floor(zc / dz) * dz
    xs = np.linspace(-7.5, 7.5, nx)
    prev = None
    for j in range(nz, -1, -1):
        z = 0.9 + (j - fr) * dz
        if z < 0.5:
            continue
        zw = zb + j * dz
        h = _height(xs, zw) * amp * 1.5
        sx = 960 + F_ * xs / z
        sy = hy + F_ * (camh - h) / z
        pts = np.stack([sx, sy], 1)
        fade = a * min(1.0, (nz - j + fr) / 6.0)
        L.black(np.vstack([pts, [[sx[-1] + 50, H + 50], [sx[0] - 50, H + 50]]]))
        L.lines([pts], col, lw + 1.6 / z, fade)
        if prev is not None:
            L.segs(np.concatenate([prev[::2], pts[::2]], 1), col2 if col2 is not None else col, lw * 0.75, fade * 0.55)
        prev = pts


def ch_grid(L, t, u, d, lvl, wt):
    L.begin(t)
    hy = 600
    half = d / 2
    R = (180, 205, 240)[lvl - 1]
    sy = hy + 30 - (250 + 30 * lvl) * ease(ramp(u, 0, d * 0.85))
    cols = ((GOLD, AMBER, AMBER), (GOLD, AMBER, CORAL), (WHITE, GOLD, ROSE))[lvl - 1]
    sun(L, t, 960, sy, R, cols=cols, n=1100 + 200 * lvl)
    tcol = (ICE, TEAL, VIOLET)[lvl - 1]
    terrain(L, t, hy, 1.5 + 0.4 * lvl, tcol, col2=(ICE, ICE, ROSE)[lvl - 1], amp=1.0 + 0.25 * A.low(t))
    if u < half + 0.2:
        tc = ((WHITE, WHITE, WHITE), (ICE, WHITE, GOLD), (GOLD, WHITE, ROSE))[lvl - 1]
        title_words(L, t, wt, ('until2', 'further2', 'notice2'), 150, 84, tc)
    label(L, t, 10, "tomorrow's not a dream", 'WIREFRAME TERRAIN FROM A SUM OF SINES, 64 x 34', wt['tomorrow'], wt['dream'] + 0.6, t - u, box=True)
    return L.finish(bg(BGS[lvl]), flash=_cutflash(u))


# ---------------------------------------------------------------- 11. the maze
def ch_maze(L, t, u, d, lvl, wt):
    L.begin(t)
    ts = t - u
    half = d / 2
    build = ramp(u, 0.05, half - 0.35)
    t_sol = wt['well'] - 0.25
    if lvl == 2:
        M = sims.polar_maze()
        rings_, sect = [int(v) for v in M['dims']]
        cx, cy = 960, 520
        def P(r, s):
            rad = 118 + r * 36
            an = s * TAU / sect - math.pi / 2
            return (cx + rad * math.cos(an), cy + rad * math.sin(an))
        def edge_pts(e):
            r0, s0, r1, s1 = e
            if r0 == r1:
                ds = ((s1 - s0 + sect // 2) % sect) - sect // 2
                return [P(r0, s0 + ds * k / 3.0) for k in range(4)]
            return [P(r0, s0), P(r1, s1)]
        name1, name2 = 'A CIRCULAR MAZE, 11 RINGS OF 44', 'BREADTH-FIRST SEARCH: OUT IN %d STEPS' % (len(M['path']) - 1)
    else:
        M = sims.maze(big=(lvl == 3))
        cols_, rows_ = [int(v) for v in M['dims']]
        cell = 36 if lvl == 1 else 28
        x0 = (W - cols_ * cell) / 2 + cell / 2
        y0 = (60 if lvl == 1 else 44) + cell / 2
        def P(x, y):
            return (x0 + x * cell, y0 + y * cell)
        def edge_pts(e):
            return [P(e[0], e[1]), P(e[2], e[3])]
        name1 = 'A MAZE BY RECURSIVE BACKTRACKING, %d x %d' % (cols_, rows_)
        name2 = 'BREADTH-FIRST SEARCH: OUT IN %d STEPS' % (len(M['path']) - 1)
    E = M['edges']
    m = int(len(E) * build)
    wall = (ICE, ICE, VIOLET)[lvl - 1]
    L.lines([edge_pts(e) for e in E[:m]], wall, 2.6 if lvl != 3 else 2.2, 0.75)
    if 0 < build < 1:
        hp = edge_pts(E[m - 1])[-1] if m > 0 else edge_pts(E[0])[0]
        L.disc(hp[0], hp[1], 7, WHITE, 1.0)
    path = M['path']
    dist = M['dist']
    if t >= t_sol:
        maxd = int(dist.max())
        fl = ramp(t, t_sol, t_sol + 1.25)
        Dn = fl * maxd
        if lvl == 2:
            rr, ss = np.where((dist >= 0) & (dist <= Dn))
            pts = [P(r, s) for r, s in zip(rr, ss)]
            near = [P(r, s) for r, s in zip(*np.where((dist > Dn - 6) & (dist <= Dn)))]
        else:
            yy, xx = np.where((dist >= 0) & (dist <= Dn))
            pts = [P(x, y) for x, y in zip(xx, yy)]
            near = [P(x, y) for y, x in zip(*np.where((dist > Dn - 6) & (dist <= Dn)))]
        fade = 1 - 0.75 * ramp(t, t_sol + 1.25, t_sol + 2.0)
        L.dots(pts, TEAL, d=5, a=0.55 * fade)
        if fl < 1:
            L.dots(near, WHITE, d=7, a=1.0)
        pp = ramp(t, t_sol + 1.15, t_sol + 2.3)
        if pp > 0:
            k = max(2, int(len(path) * pp))
            pl = [P(a_, b_) for a_, b_ in path[:k]]
            if pp >= 1:
                e0, e1 = np.array(pl[-2]), np.array(pl[-1])
                ext = ramp(t, t_sol + 2.3, t_sol + 2.7)
                if lvl == 2:
                    dv = (e1 - (cx, cy)) / np.hypot(*(e1 - (cx, cy)))
                else:
                    dv = np.array([1.0, 0.0])
                pl.append(tuple(e1 + dv * 900 * ext))
            pc = (AMBER, AMBER, WHITE)[lvl - 1]
            L.lines([pl], pc, 7.0, 1.0)
            L.lines([pl], GOLD if lvl != 3 else GOLD, 2.6, 1.0)
            L.disc(pl[-1][0], pl[-1][1], 9, WHITE, 1.0)
    if lvl == 2:
        sun(L, t, cx, cy, 78, cols=(GOLD, AMBER, CORAL), n=420, rays=0, d=3.0)
    s0 = P(*path[0])
    L.disc(s0[0], s0[1], 8, AMBER, 1.0)
    if t < t_sol:
        label(L, t, 11, 'we built the problem with our hands', name1, wt['we'], wt['hands'] + 0.5, ts, box=True)
    else:
        label(L, t, 11, "we'll build our way out again", name2, wt['well'], wt['again'] + 0.5, t_sol - 0.3, box=True)
    return L.finish(bg(BGS[lvl]), flash=_cutflash(u))


def _bind(fn, lvl):
    return lambda L, t, u, d: fn(L, t, u, d, lvl, WT[lvl])


def chorus(b0, lvl):
    return [
        (B(b0), B(b0 + 2), _bind(ch_title, lvl)),
        (B(b0 + 2), B(b0 + 4), _bind(ch_machine, lvl)),
        (B(b0 + 4), B(b0 + 6), _bind(ch_wind, lvl)),
        (B(b0 + 6), B(b0 + 8), _bind(ch_clean, lvl)),
        (B(b0 + 8), B(b0 + 12), _bind(ch_grid, lvl)),
        (B(b0 + 12), B(b0 + 16), _bind(ch_maze, lvl)),
    ]


def timeline():
    return chorus(32, 1) + chorus(72, 2) + chorus(112, 3)
