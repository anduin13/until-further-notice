"""Precomputed simulations (cached on disk so the render workers share them)."""
import os, math, numpy as np
from lum import CACHE, W, H, hershey, TAU

_mem = {}


def cached(name, fn):
    if name in _mem:
        return _mem[name]
    p = f'{CACHE}/{name}.npz'
    if os.path.exists(p):
        d = dict(np.load(p, allow_pickle=True))
    else:
        d = fn()
        tmp = f'{CACHE}/{name}.{os.getpid()}.tmp.npz'
        np.savez(tmp, **d)
        os.replace(tmp, p)
    _mem[name] = d
    return d


# ---------------------------------------------------------------- Nagel-Schreckenberg traffic
def _nasch(lanes=9, cells=132, steps=150, vmax=5, p=0.30, seed=4):
    rs = np.random.RandomState(seed)
    out = {}
    for ln in range(lanes):
        dens = 0.17 + 0.16 * rs.rand()
        n = int(cells * dens)
        pos = np.sort(rs.choice(cells, n, replace=False)).astype(np.int64)
        v = rs.randint(0, vmax + 1, n)
        P = np.zeros((steps, n), np.int64)
        V = np.zeros((steps, n), np.int64)
        unw = pos.copy()
        for s in range(-400, steps):
            v = np.minimum(v + 1, vmax)
            gap = (np.roll(unw, -1) - unw - 1)
            gap[-1] = unw[0] + cells - unw[-1] - 1
            v = np.minimum(v, gap)
            brake = rs.rand(n) < p
            v = np.where(brake, np.maximum(v - 1, 0), v)
            unw = unw + v
            if s >= 0:
                P[s] = unw
                V[s] = v
        out[f'P{ln}'] = P
        out[f'V{ln}'] = V
    out['meta'] = np.array([lanes, cells, steps])
    return out


def nasch():
    return cached('nasch', _nasch)


# ---------------------------------------------------------------- Galton board
def _galton(rows=12, n=240, seed=6):
    rs = np.random.RandomState(seed)
    bits = (rs.rand(n, rows) < 0.5).astype(np.int64)
    cum = np.concatenate([np.zeros((n, 1), np.int64), np.cumsum(bits, 1)], 1)
    rel = np.sort(rs.rand(n)) ** 0.9
    binn = cum[:, -1]
    stack = np.zeros(n, np.int64)
    cnt = np.zeros(rows + 1, np.int64)
    for i in np.argsort(rel):
        stack[i] = cnt[binn[i]]
        cnt[binn[i]] += 1
    return dict(cum=cum, rel=rel, bin=binn, stack=stack, rows=np.array(rows))


def galton():
    return cached('galton', _galton)


# ---------------------------------------------------------------- Game of Life
GOSPER = """........................O...........
......................O.O...........
............OO......OO............OO
...........O...O....OO............OO
OO........O.....O...OO..............
OO........O...O.OO....O.O...........
..........O.....O.......O...........
...........O...O....................
............OO......................"""
ACORN = """.O.....
...O...
OO..OOO"""


def _life_step(g):
    n = sum(np.roll(np.roll(g, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx, dy) != (0, 0))
    return ((n == 3) | ((g == 1) & (n == 2))).astype(np.uint8)


def _place(g, pat, x, y, flipx=False, flipy=False):
    rows = pat.split('\n')
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == 'O':
                xx = x + (len(r) - 1 - i if flipx else i)
                yy = y + (len(rows) - 1 - j if flipy else j)
                g[yy, xx] = 1


def _life_gun():
    gw, gh, m = 96, 54, 24
    g = np.zeros((gh + 2 * m, gw + 2 * m), np.uint8)
    _place(g, GOSPER, m + 3, m + 3)
    _place(g, GOSPER, m + 50, m + 3)
    gens = 420
    out = np.zeros((gens, gh, gw), np.uint8)
    age = np.zeros_like(g, dtype=np.int32)
    ages = np.zeros((gens, gh, gw), np.uint8)
    for k in range(gens):
        age = np.where(g == 1, age + 1, 0)
        out[k] = g[m:m + gh, m:m + gw]
        ages[k] = np.minimum(age, 255)[m:m + gh, m:m + gw]
        g = _life_step(g)
        g[:3] = 0; g[-3:] = 0; g[:, :3] = 0; g[:, -3:] = 0
    return dict(g=out, age=ages)


def life_gun():
    return cached('life_gun', _life_gun)


def _life_soup():
    """a random soup on a torus"""
    gw, gh = 192, 108
    rs = np.random.RandomState(31)
    g = (rs.rand(gh, gw) < 0.34).astype(np.uint8)
    gens = 300
    out = np.zeros((gens, gh, gw), np.uint8)
    ages = np.zeros((gens, gh, gw), np.uint8)
    age = np.zeros_like(g, dtype=np.int32)
    for k in range(gens):
        age = np.where(g == 1, age + 1, 0)
        out[k] = g
        ages[k] = np.minimum(age, 255)
        g = _life_step(g)
    return dict(g=out, age=ages)


def life_soup():
    return cached('life_soup', _life_soup)


# ---------------------------------------------------------------- flow field
def _flow(n=7000, T=260, seed=8, vort=((960, 540, 1.0),)):
    rs = np.random.RandomState(seed)
    p = np.stack([rs.rand(n) * (W + 700) - 350, rs.rand(n) * (H + 160) - 80], 1)
    out = np.zeros((T, n, 2), np.float32)
    dt = 9.0
    for s in range(T):
        out[s] = p
        x, y = p[:, 0], p[:, 1]
        # curl of a smooth potential
        u = 1.0 + 0.55 * np.cos(y * 0.0061 + 1.1) * np.sin(x * 0.0037 + 0.3) + 0.3 * np.cos(y * 0.013 + x * 0.004)
        v = 0.50 * np.sin(x * 0.0052 + 2.0) * np.cos(y * 0.0045) + 0.25 * np.sin(x * 0.011 - y * 0.006)
        for (vx, vy, g) in vort:
            dx, dy = x - vx, y - vy
            r2 = dx * dx + dy * dy
            k = g * 230.0 / (r2 + 160.0 ** 2) * 160.0
            u += -dy / 160.0 * k * 0.9
            v += dx / 160.0 * k * 0.9
        p = p + dt * np.stack([u, v], 1)
        wrap = p[:, 0] > W + 350
        p[wrap, 0] -= W + 700
        p[wrap, 1] = rs.rand(wrap.sum()) * (H + 160) - 80
        p[:, 1] = (p[:, 1] + 80) % (H + 160) - 80
    return dict(p=out, off=rs.randint(0, T, n))


def flow(kind=1):
    if kind == 1:
        return cached('flow1', lambda: _flow())
    if kind == 2:
        return cached('flow2', lambda: _flow(seed=9, vort=((560, 420, 1.0), (1000, 660, -1.0), (1420, 400, 1.0))))
    return cached('flow3', lambda: _flow(n=11000, seed=10, vort=((960, 480, 1.6),)))


# ---------------------------------------------------------------- sorting
def _quicksort(n=160, seed=3):
    rs = np.random.RandomState(seed)
    a = rs.permutation(n)
    snaps = [a.copy()]
    act = [(0, 0)]

    def qs(lo, hi):
        if lo >= hi:
            return
        piv = a[(lo + hi) // 2]
        i, j = lo, hi
        while i <= j:
            while a[i] < piv:
                i += 1
            while a[j] > piv:
                j -= 1
            if i <= j:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    snaps.append(a.copy())
                    act.append((i, j))
                i += 1
                j -= 1
        qs(lo, j)
        qs(i, hi)
    qs(0, n - 1)
    return dict(s=np.array(snaps), act=np.array(act))


def quicksort():
    return cached('quicksort', _quicksort)


def _oddeven(rows=54, cols=96, seed=5):
    rs = np.random.RandomState(seed)
    a = np.stack([rs.permutation(cols) for _ in range(rows)])
    out = [a.copy()]
    for r in range(cols + 2):
        s = r % 2
        left = a[:, s:cols - 1:2]
        right = a[:, s + 1:cols:2]
        m = left > right
        l2 = np.where(m, right, left)
        r2 = np.where(m, left, right)
        a = a.copy()
        a[:, s:cols - 1:2] = l2
        a[:, s + 1:cols:2] = r2
        out.append(a.copy())
    return dict(s=np.array(out).astype(np.uint8))


def oddeven():
    return cached('oddeven', _oddeven)


# ---------------------------------------------------------------- mazes
def _maze(cols=48, rows=24, seed=12):
    rs = np.random.RandomState(seed)
    start = (0, rows // 2)
    seen = np.zeros((rows, cols), bool)
    stack = [start]
    seen[start[1], start[0]] = True
    edges = []
    adj = {}
    while stack:
        x, y = stack[-1]
        nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < cols and 0 <= y + dy < rows and not seen[y + dy, x + dx]]
        if not nb:
            stack.pop()
            continue
        nx, ny = nb[rs.randint(len(nb))]
        seen[ny, nx] = True
        edges.append((x, y, nx, ny))
        adj.setdefault((x, y), []).append((nx, ny))
        adj.setdefault((nx, ny), []).append((x, y))
        stack.append((nx, ny))
    goal = (cols - 1, rows // 2)
    dist = -np.ones((rows, cols), np.int64)
    par = {}
    q = [start]
    dist[start[1], start[0]] = 0
    while q:
        c = q.pop(0)
        for nb_ in adj.get(c, []):
            if dist[nb_[1], nb_[0]] < 0:
                dist[nb_[1], nb_[0]] = dist[c[1], c[0]] + 1
                par[nb_] = c
                q.append(nb_)
    path = [goal]
    while path[-1] != start:
        path.append(par[path[-1]])
    path = path[::-1]
    return dict(edges=np.array(edges), dist=dist, path=np.array(path), dims=np.array([cols, rows]))


def maze(big=False):
    if big:
        return cached('maze_big', lambda: _maze(64, 32, seed=14))
    return cached('maze', _maze)


def _polar_maze(rings=11, sect=44, seed=21):
    """nodes (r, s). start at innermost ring, exit at outermost"""
    rs = np.random.RandomState(seed)
    start = (0, 0)
    seen = np.zeros((rings, sect), bool)
    seen[0, 0] = True
    stack = [start]
    edges = []
    adj = {}
    while stack:
        r, s = stack[-1]
        cand = [(r, (s + 1) % sect), (r, (s - 1) % sect)]
        if r + 1 < rings:
            cand.append((r + 1, s))
        if r - 1 >= 0:
            cand.append((r - 1, s))
        nb = [c for c in cand if not seen[c]]
        if not nb:
            stack.pop()
            continue
        # bias towards moving round the ring for longer arcs
        wts = np.array([2.0 if c[0] == r else 1.0 for c in nb])
        c = nb[rs.choice(len(nb), p=wts / wts.sum())]
        seen[c] = True
        edges.append((r, s, c[0], c[1]))
        adj.setdefault((r, s), []).append(c)
        adj.setdefault(c, []).append((r, s))
        stack.append(c)
    goal = (rings - 1, sect // 3)
    dist = -np.ones((rings, sect), np.int64)
    par = {}
    dist[start] = 0
    q = [start]
    while q:
        c = q.pop(0)
        for nb_ in adj.get(c, []):
            if dist[nb_] < 0:
                dist[nb_] = dist[c] + 1
                par[nb_] = c
                q.append(nb_)
    path = [goal]
    while path[-1] != start:
        path.append(par[path[-1]])
    return dict(edges=np.array(edges), dist=dist, path=np.array(path[::-1]), dims=np.array([rings, sect]))


def polar_maze():
    return cached('polar_maze', _polar_maze)


# ---------------------------------------------------------------- L-systems
def _lsys(seed=1, iters=5, ang=25.0):
    rs = np.random.RandomState(seed)
    s = 'X'
    for _ in range(iters):
        s = ''.join({'X': 'F+[[X]-X]-F[-FX]+X', 'F': 'FF'}.get(ch, ch) for ch in s)
    x, y, a = 0.0, 0.0, -90.0
    st = []
    segs = []
    depth = 0
    for ch in s:
        if ch == 'F':
            nx = x + math.cos(math.radians(a))
            ny = y + math.sin(math.radians(a))
            segs.append((x, y, nx, ny, depth))
            x, y = nx, ny
        elif ch == '+':
            a += ang * (0.8 + 0.4 * rs.rand())
        elif ch == '-':
            a -= ang * (0.8 + 0.4 * rs.rand())
        elif ch == '[':
            st.append((x, y, a, depth))
            depth += 1
        elif ch == ']':
            x, y, a, depth = st.pop()
    segs = np.array(segs)
    # growth order: distance from the root along the plant (height proxy)
    order = np.hypot(segs[:, 0], segs[:, 1])
    order = order / order.max()
    hgt = -segs[:, 1].min()
    segs[:, :4] /= hgt
    return dict(segs=segs, order=order)


def lsys(k):
    return cached(f'lsys{k}', lambda: _lsys(seed=k, ang=(25.0, 22.0, 28.0, 20.0, 26.0)[k % 5]))


# ---------------------------------------------------------------- Chladni figures
MODES = [(1, 2), (2, 3), (1, 4), (3, 4), (2, 5), (3, 5), (1, 6), (4, 5), (3, 7), (5, 6)]


def _chladni(n=9000, seed=2):
    rs = np.random.RandomState(seed)
    out = {}
    for k, (a, b) in enumerate(MODES):
        pts = []
        tot = 0
        while tot < n:
            xy = rs.rand(120000, 2)
            f = np.cos(a * math.pi * xy[:, 0]) * np.cos(b * math.pi * xy[:, 1]) - np.cos(b * math.pi * xy[:, 0]) * np.cos(a * math.pi * xy[:, 1])
            keep = rs.rand(len(f)) < np.exp(-(f / 0.07) ** 2)
            pts.append(xy[keep])
            tot += keep.sum()
        p = np.vstack(pts)[:n]
        key = (np.floor(p[:, 0] * 10) * 10 + np.floor(p[:, 1] * 10)) + rs.rand(n) * 0.5
        out[f'm{k}'] = p[np.argsort(key)].astype(np.float32)
    return out


def chladni():
    return cached('chladni', _chladni)


# ---------------------------------------------------------------- Fourier epicycles
def _epicycles(word='believe', K=150, N=2048):
    st, wd = hershey(word, 1.0, 'scripts')
    pts = []
    pen = []
    for q in st:
        if pts:
            # pen-up jump
            a = pts[-1][-1]
            jump = np.linspace(a, q[0], 6)[1:-1]
            pts.append(jump)
            pen.append(np.zeros(len(jump), bool))
        pts.append(q)
        pen.append(np.ones(len(q), bool))
    P = np.vstack(pts)
    pen = np.concatenate(pen)
    # close the loop back to the start
    back_ = np.linspace(P[-1], P[0], 12)[1:]
    P = np.vstack([P, back_])
    pen = np.concatenate([pen, np.zeros(len(back_), bool)])
    d = np.hypot(np.diff(P[:, 0]), np.diff(P[:, 1]))
    Lc = np.concatenate([[0], np.cumsum(d)])
    u = np.linspace(0, Lc[-1], N, endpoint=False)
    x = np.interp(u, Lc, P[:, 0])
    y = np.interp(u, Lc, P[:, 1])
    idx = np.clip(np.searchsorted(Lc, u, 'right') - 1, 0, len(pen) - 1)
    down = pen[idx] & pen[np.minimum(idx + 1, len(pen) - 1)]
    z = (x - wd / 2) + 1j * (y + 0.3)
    c = np.fft.fft(z) / N
    freqs = np.fft.fftfreq(N, 1.0 / N)
    order = np.argsort(-np.abs(c))
    order = order[freqs[order] != 0][:K]
    return dict(c=c[order], f=freqs[order], dc=np.array([c[0]]), down=down, wd=np.array(wd))


def epicycles():
    return cached('epicycles', _epicycles)


# ---------------------------------------------------------------- double pendulums
def _pend(n=12, dur=24.0, d0=None, seed=1):
    g = 9.81

    def acc(th1, th2, w1, w2):
        d = th1 - th2
        den = 3 - np.cos(2 * d)
        a1 = (-3 * g * np.sin(th1) - g * np.sin(th1 - 2 * th2) - 2 * np.sin(d) * (w2 * w2 + w1 * w1 * np.cos(d))) / den
        a2 = (2 * np.sin(d) * (2 * w1 * w1 + 2 * g * np.cos(th1) + w2 * w2 * np.cos(d))) / den
        return a1, a2

    def run(delta):
        th1 = np.full(n, 2.05) + np.arange(n) * delta
        th2 = np.full(n, 2.75) + np.arange(n) * delta * 0.5
        w1 = np.zeros(n)
        w2 = np.zeros(n)
        dt = 1 / 480.0
        steps = int(dur / dt)
        rec = np.zeros((int(dur * 60) + 1, n, 2), np.float32)
        for s in range(steps):
            if s % 8 == 0:
                rec[s // 8, :, 0] = th1
                rec[s // 8, :, 1] = th2
            k1 = (w1, w2) + acc(th1, th2, w1, w2)
            k2 = (w1 + 0.5 * dt * k1[2], w2 + 0.5 * dt * k1[3]) + acc(th1 + 0.5 * dt * k1[0], th2 + 0.5 * dt * k1[1], w1 + 0.5 * dt * k1[2], w2 + 0.5 * dt * k1[3])
            k3 = (w1 + 0.5 * dt * k2[2], w2 + 0.5 * dt * k2[3]) + acc(th1 + 0.5 * dt * k2[0], th2 + 0.5 * dt * k2[1], w1 + 0.5 * dt * k2[2], w2 + 0.5 * dt * k2[3])
            k4 = (w1 + dt * k3[2], w2 + dt * k3[3]) + acc(th1 + dt * k3[0], th2 + dt * k3[1], w1 + dt * k3[2], w2 + dt * k3[3])
            th1 = th1 + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            th2 = th2 + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            w1 = w1 + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
            w2 = w2 + dt / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        return rec

    best = None
    for delta in (1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6):
        rec = run(delta)
        x2 = np.sin(rec[:, :, 0]) + np.sin(rec[:, :, 1])
        spread = x2.max(1) - x2.min(1)
        tdiv = np.argmax(spread > 0.25) / 60.0 if (spread > 0.25).any() else 99
        if best is None or abs(tdiv - 11.5) < abs(best[0] - 11.5):
            best = (tdiv, delta, rec)
    return dict(th=best[2], delta=np.array(best[1]), tdiv=np.array(best[0]))


def pend():
    return cached('pend', _pend)


# ---------------------------------------------------------------- the sky falls, the sun assembles
def _sky(n=1600, seed=7):
    rs = np.random.RandomState(seed)
    x = rs.rand(n) * (W - 80) + 40
    y = rs.rand(n) ** 0.9 * 800 + 40
    mag = rs.rand(n) ** 2
    tf = np.where(rs.rand(n) < 0.45, rs.rand(n) * 3.0, 3.25 + rs.rand(n) * 0.35)   # fall start, s after t0
    floor = 960.0
    g = 2600.0
    tl = tf + np.sqrt(2 * (floor - y) / g)
    binw = 14.0
    b = (x / binw).astype(int)
    cnt = {}
    rest = np.zeros(n)
    for i in np.argsort(tl):
        c = cnt.get(b[i], 0)
        rest[i] = floor - c * 5.0
        cnt[b[i]] = c + 1
    tl = tf + np.sqrt(2 * np.maximum(1.0, rest - y) / g)
    # sun targets: golden-angle disc, assigned by x order so the heap sweeps inward
    k = np.arange(1, n + 1)
    perm = rs.permutation(n)
    return dict(x=x, y=y, mag=mag, tf=tf, tl=tl, rest=rest, k=k[perm], jit=rs.rand(n))


def sky():
    return cached('sky', _sky)


def warm():
    for f in (nasch, galton, life_gun, life_soup, lambda: flow(1), lambda: flow(2), lambda: flow(3), quicksort, oddeven, maze, lambda: maze(True),
              polar_maze, chladni, epicycles, pend, sky, *[(lambda k=k: lsys(k)) for k in range(5)]):
        f()


if __name__ == '__main__':
    import time
    t0 = time.time()
    warm()
    p = pend()
    print('pendulum delta', p['delta'], 'diverges at', p['tdiv'])
    print('quicksort swaps', len(quicksort()['s']), 'maze path', len(maze()['path']), 'polar path', len(polar_maze()['path']))
    print('warm', time.time() - t0)
