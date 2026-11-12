"""Intro, verse 1, pre-chorus 1."""
from lum import *
import sims


def fade_in(u, dur=0.25):
    return ramp(u, 0, dur)


# ---------------------------------------------------------------- 0. signal
def intro_a(L, t, u, d):
    L.begin(t)
    cx, cy = 960, 560
    kd = ease(ramp(t, 0.6, 1.6))
    kl = ease(ramp(t, B(1), B(2) + 0.8))
    if kl <= 0:
        L.disc(cx, cy, 3.2 + 1.2 * math.sin(t * 3), WHITE, kd)
    else:
        n = 900
        wv = wave(t, n, win=0.05)
        half = 780 * kl
        xs = np.linspace(cx - half, cx + half, n)
        env = np.hanning(n) ** 0.6
        ys = cy + 420 * wv * env * ramp(t, B(1), B(2.5))
        L.lines([np.stack([xs, ys], 1)], ICE, 2.2, 1.0)
        L.dots([(cx - half, cy), (cx + half, cy)], WHITE, d=5, a=0.9)
    rt = ramp(t, B(4), B(6.2))
    if rt > 0:
        L.text('UNTIL FURTHER NOTICE', cx, 330, 92, font='futuram', align='c', col=WHITE, w=3.0, rev=rt)
    if t > B(2):
        label(L, t, 0, None, 'THE SONG ITSELF: 50 MILLISECONDS OF ITS SIGNAL', 0, 1, B(2))
    return L.finish(bg('night'), gain=ramp(t, 0.3, 1.2))


# ---------------------------------------------------------------- 1. successive pulses
def intro_b(L, t, u, d):
    L.begin(t)
    rows = 46
    dlt = 0.2264 / 2          # one new slice every quarter beat
    sp = 15.0
    yb = 930
    x0, x1 = 500, 1420
    n = 230
    xs = np.linspace(x0, x1, n)
    win = np.exp(-((xs - 960) / 250.0) ** 2)
    J = t / dlt
    j0 = int(math.floor(J))
    grow = ramp(u, 0, 5.0)
    ker = np.ones(7) / 7
    for j in range(j0 - rows, j0 + 1):
        age = J - j                      # 0 = newest (front, bottom)
        if j * dlt < B(8) - 0.01 or age > rows * grow + 1:
            continue
        y = yb - age * sp
        w_ = wave(j * dlt, n + 6, win=0.028)
        e = np.convolve(np.abs(w_), ker, 'valid')[:n]
        prof = e * win * 330 + 1.5 * sn1(xs * 0.02 + j * 7.3, j % 97)
        pts = np.stack([xs, y - prof], 1)
        L.black(np.vstack([pts, [[x1, y + 40], [x0, y + 40]]]))
        a = min(1.0, age * 2.0) * (1.0 - 0.55 * age / rows) * ramp(rows * grow + 1 - age, 0, 2)
        L.lines([pts], WHITE, 1.9, a)
    label(L, t, 1, None, 'SUCCESSIVE SLICES OF THE WAVEFORM, STACKED (AFTER PULSAR CP 1919)', 0, 1, B(8))
    return L.finish(bg('night'), gain=fade_in(u, 0.2), bloom=0.8)


# ---------------------------------------------------------------- 2. traffic
def traffic(L, t, u, d):
    L.begin(t)
    D = sims.nasch()
    lanes, cells, steps = [int(v) for v in D['meta']]
    cw = 17.5
    step = 0.2264
    sf_ = min(steps - 2.001, u / step + 4)
    s = int(sf_)
    f = sf_ - s
    cx = L.cx
    cx.save()
    cx.translate(960, 520)
    cx.rotate(-0.115)
    cx.translate(-960, -520)
    sp = 64
    ytop = 520 - (lanes - 1) / 2 * sp
    # lane markings
    marks = []
    for k in range(lanes + 1):
        y = ytop - sp / 2 + k * sp
        if k in (0, lanes):
            L.line(-300, y, W + 300, y, DIM, 1.6, 0.8)
        elif k == lanes // 2 + 1 or k == lanes // 2:
            L.line(-300, y, W + 300, y, DIM, 1.4, 0.55) if k == lanes // 2 else None
        if 0 < k < lanes:
            for x in range(-300, W + 300, 70):
                marks.append((x, y, x + 26, y))
    L.segs(marks, DIM, 1.2, 0.35)
    slow, mid, fast = [], [], []
    for ln in range(lanes):
        P = D[f'P{ln}']
        V = D[f'V{ln}']
        pos = P[s] + (P[s + 1] - P[s]) * f
        v = V[s + 1]
        x = (pos % cells) * cw - 190
        if ln >= lanes // 2 + 1:
            x = W + 190 - (pos % cells) * cw
            sgn = -1
        else:
            sgn = 1
        y = ytop + ln * sp
        for i in range(len(x)):
            ln_ = 15 + 7 * v[i]
            seg = (x[i] - sgn * ln_, y, x[i], y)
            (slow if v[i] == 0 else mid if v[i] <= 2 else fast).append(seg)
    L.segs(fast, ICE, 5.0, 0.85)
    L.segs(mid, WHITE, 5.0, 0.6)
    L.segs(slow, CORAL, 5.5, 0.9)
    cx.restore()
    # rain
    n = 110
    r = rnds(n * 3, 5, 5).reshape(n, 3)
    rx = (r[:, 0] * (W + 300) - t * 220 * (0.8 + 0.4 * r[:, 2])) % (W + 300) - 100
    ry = (r[:, 1] * (H + 200) + t * 1500 * (0.8 + 0.4 * r[:, 2])) % (H + 200) - 100
    L.segs(np.stack([rx, ry, rx - 9, ry + 60 + 40 * r[:, 2]], 1), DIM, 1.2, 0.33)
    ly = lyric_seq(t, [('grey skies over the motorway', 30.0, 32.3), ("everyone's waiting for the end of the day", 32.96, 38.5)])
    label(L, t, 2, ly[0], 'NAGEL-SCHRECKENBERG TRAFFIC MODEL, CHANCE OF BRAKING 0.3', ly[1], ly[2], B(16), box=True)
    return L.finish(bg('night'), gain=fade_in(u, 0.2))


# ---------------------------------------------------------------- 3. the fall, for sale
def walks(L, t, u, d):
    L.begin(t)
    toff = 47.72
    n = 36
    m = 260
    pr = ramp(t, B(23) + 0.2, 46.9)
    k = max(2, int(m * pr))
    xs = np.linspace(120, 1800, m)
    heads = []
    for i in range(n):
        steps_ = SN[(hsh(i, 3) + np.arange(m) * 3) & (NT - 1)] * 7.0 + 1.55 + 0.9 * rnd(i, 9)
        steps_[:1] = 0
        ys = 300 + np.cumsum(steps_)
        fall = np.clip((ys - 300) / 470.0, 0, 1)
        # colour slides from ice to red as it falls: draw in three pieces
        yv = ys[:k]
        xv = xs[:k]
        pts = np.stack([xv, yv], 1)
        b1 = int(np.searchsorted(fall[:k], 0.33))
        b2 = int(np.searchsorted(fall[:k], 0.66))
        L.lines([pts[:b1 + 1]], ICE, 1.7, 0.6)
        if b2 > b1:
            L.lines([pts[b1:b2 + 1]], ROSE, 1.7, 0.75)
        if k > b2:
            L.lines([pts[b2:]], CORAL, 1.8, 0.9)
        heads.append(pts[-1])
    L.dots(heads, WHITE, d=5, a=1.0 if pr < 1 else 0.5)
    # axis
    L.line(120, 300, 1800, 300, DIM, 1.2, 0.6)
    L.segs([(120 + j * 140, 294, 120 + j * 140, 306) for j in range(13)], DIM, 1.2, 0.7)
    label(L, t, 3, "the radio's selling the fall of man", 'RANDOM WALKS WITH A DOWNWARD DRIFT, N = 36', 43.1, 46.3, B(23))
    sq = None
    gain = fade_in(u, 0.2)
    if t >= toff:
        sy = max(0.004, 1 - eout(ramp(t, toff, toff + 0.13), 2))
        sx = max(0.004, 1 - eout(ramp(t, toff + 0.12, toff + 0.30), 2))
        sq = (sx, sy)
        gain = 1.0 - 0.75 * ramp(t, toff + 0.3, 48.3)
    return L.finish(bg('night'), squash=sq, gain=gain)


# ---------------------------------------------------------------- 4. a better plan: one point
APEX = (960, 132)


def point(L, t, u, d):
    L.begin(t)
    pu = A.pulse(t, 5)
    k = ease(ramp(t, 49.4, 50.3))
    x = 960
    y = 540 + (APEX[1] - 540) * k
    warm_ = ramp(t, 48.45, 48.75)
    col = mixc(WHITE, AMBER, warm_)
    r = 5.0 + 5.0 * warm_ * (1 - 0.5 * k) + 2.5 * pu * warm_
    L.disc(x, y, r, col, 1.0)
    if warm_ > 0 and k < 1:
        for j in range(3):
            ph = (A.beatpos(t) - j) % 4 / 4.0
            if t - 48.5 > j * 0.45:
                L.lines([circ(x, y, 14 + 240 * ph)], AMBER, 1.6, 0.5 * (1 - ph) * (1 - k), close=True)
    label(L, t, 4, "i've got a better plan", 'ONE POINT OF LIGHT', 48.5, 49.5, 48.3)
    return L.finish(bg('night'))


# ---------------------------------------------------------------- 5. the odds
ROWS = 12
GDX, GDY = 58.0, 44.0
GY0 = 190.0
FLOOR = 996.0
HOP = 0.088


def _peg(k, j):
    return (960 + (j - k / 2.0) * GDX, GY0 + k * GDY)


def galton(L, t, u, d):
    L.begin(t)
    G = sims.galton()
    cum, rel, binn, stack = G['cum'], G['rel'], G['bin'], G['stack']
    n = len(rel)
    trev = 56.55
    if t < trev:
        tau = t
    else:
        tau = trev - 6.4 * ein(ramp(t, trev, 58.12), 1.7)
    rev = t >= trev
    # lattice of every possible path ("the future's not written")
    lat = ramp(t, 54.36, 55.9)
    if lat > 0:
        segs = []
        for k in range(ROWS):
            if k / ROWS > lat:
                break
            for j in range(k + 1):
                p = _peg(k, j)
                if k + 1 < ROWS:
                    a_, b_ = _peg(k + 1, j), _peg(k + 1, j + 1)
                else:
                    a_, b_ = (p[0] - GDX / 2, p[1] + GDY), (p[0] + GDX / 2, p[1] + GDY)
                segs.append((p[0], p[1], a_[0], a_[1]))
                segs.append((p[0], p[1], b_[0], b_[1]))
        L.segs(segs, AMBER, 1.5, 0.55)
    # pegs
    pegs = [_peg(k, j) for k in range(ROWS) for j in range(k + 1)]
    L.dots(pegs, DIM, d=5, a=0.9 * ramp(u, 0.0, 0.5))
    L.line(APEX[0], APEX[1], 960, GY0 - 8, DIM, 1.2, 0.5)
    # bins
    by = GY0 + ROWS * GDY
    L.segs([(960 + (b - 6.5) * GDX, by + 10, 960 + (b - 6.5) * GDX, FLOOR + 6) for b in range(14)], DIM, 1.2, 0.5 * ramp(u, 0.2, 0.8))
    L.line(960 - 6.5 * GDX, FLOOR + 6, 960 + 6.5 * GDX, FLOOR + 6, DIM, 1.4, 0.6)
    # the odds: the bell curve it must fill
    odds = ramp(t, 51.66, 52.3) * (1 - ramp(t, 57.2, 58.0))
    if odds > 0:
        bx = np.linspace(-6.5, 6.5, 80)
        hh = n * np.exp(-bx ** 2 / (2 * 3.0)) / math.sqrt(TAU * 3.0) * 5.6
        L.lines([np.stack([960 + bx * GDX, FLOOR - hh], 1)], ICE, 1.6, 0.7 * odds)
    # balls
    r_i = 50.45 + rel * 3.6
    tp = tau - r_i
    lv = np.clip(np.floor(tp / HOP), 0, ROWS).astype(int)
    f = np.clip(tp / HOP - lv, 0, 1)
    idx = np.arange(n)
    lv2 = np.minimum(lv + 1, ROWS)
    X = 960 + (cum[idx, lv] - lv / 2.0) * GDX
    X2 = 960 + (cum[idx, lv2] - lv2 / 2.0) * GDX
    Y = GY0 + lv * GDY - 12
    x = X + (X2 - X) * f
    y = Y + GDY * f - 15 * 4 * f * (1 - f)
    fin = lv >= ROWS
    tf_ = np.maximum(0, tp - ROWS * HOP)
    rest = FLOOR - 2 - stack * 5.6
    yf = np.minimum(GY0 + ROWS * GDY - 12 + 0.5 * 2600 * tf_ ** 2, rest)
    y = np.where(fin, yf, y)
    x = np.where(fin, 960 + (binn - 6) * GDX, x)
    vis = tp > 0
    P = np.stack([x, y], 1)[vis]
    L.dots(P, GOLD if rev else WHITE, d=6.4, a=1.0)
    # the source point
    wait = (~vis).sum() / n
    L.disc(APEX[0], APEX[1], 5 + 9 * wait + 2 * A.pulse(t, 5), AMBER, 1.0)
    ly = lyric_seq(t, [("don't tell me the odds", 50.54, 51.95), ("don't tell me the date", 52.34, 53.8), ("the future's not written", 54.36, 56.2), ("it's not too late", 56.70, 58.1)])
    label(L, t, 5, ly[0], 'GALTON BOARD, 240 BALLS, RUN BACKWARDS' if rev else 'GALTON BOARD, 12 ROWS, 240 BALLS', ly[1], ly[2], 50.3)
    return L.finish(bg('night'), flash=0.9 * ein(ramp(t, 58.05, 58.28), 2))


def timeline():
    return [
        (0.0, B(8), intro_a),
        (B(8), B(16), intro_b),
        (B(16), B(23), traffic),
        (B(23), 48.30, walks),
        (48.30, 50.30, point),
        (50.30, B(32), galton),
    ]
