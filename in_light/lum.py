"""Light-on-dark engine: additive vector strokes, point clouds, bloom."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common'))
import cairo, numpy as np, cv2, math
from engine import (ROOT, DATA, OUT, A, B, hershey, lerp, clamp, ramp, ease, eout, ein, back, rnd, rnds, sn1, SN, RN, NT, hsh, circ, rot, TAU, W, H, FPS, mixc)
import soundfile as sf

CACHE = os.path.join(ROOT, 'cache')
os.makedirs(CACHE, exist_ok=True)

# palette (RGB 0..1)
ICE = (0.62, 0.80, 1.00)
WHITE = (1.00, 0.96, 0.90)
AMBER = (1.00, 0.62, 0.16)
GOLD = (1.00, 0.80, 0.36)
CORAL = (1.00, 0.30, 0.28)
TEAL = (0.16, 0.90, 0.78)
VIOLET = (0.62, 0.44, 1.00)
ROSE = (1.00, 0.42, 0.62)
DIM = (0.42, 0.50, 0.64)

try:
    _wav, _sr = sf.read(os.path.join(ROOT, 'audio', 'stereo22.wav'), dtype='float32')
except Exception:
    raise SystemExit('audio/stereo22.wav is missing: run  python prepare.py path/to/song.mp3')
WAV = _wav
SR = _sr
MONO = _wav.mean(1)


def wave(t, n=800, win=0.045, ch=None):
    """n samples of the song around time t"""
    src = MONO if ch is None else WAV[:, ch]
    i0 = int((t - win / 2) * SR)
    m = int(win * SR)
    idx = np.clip(i0 + np.arange(m), 0, len(src) - 1)
    seg = src[idx]
    return np.interp(np.linspace(0, m - 1, n), np.arange(m), seg)


def _grad(stops, glow=None):
    """vertical gradient from list of (y 0..1, (r,g,b) 0..255) -> BGR uint8 with static dither"""
    ys = np.linspace(0, 1, H)
    img = np.zeros((H, W, 3), np.float32)
    sy = [s[0] for s in stops]
    for c in range(3):
        col = np.interp(ys, sy, [s[1][c] for s in stops])
        img[:, :, 2 - c] = col[:, None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if glow is not None:
        gx, gy, gr, gc = glow
        d = np.exp(-(((xx - gx) / gr) ** 2 + ((yy - gy) / (gr * 0.55)) ** 2))
        for c in range(3):
            img[:, :, 2 - c] += d * gc[c]
    vig = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    img *= (1 - 0.35 * np.clip(vig, 0, 1.2))[:, :, None]
    rs = np.random.RandomState(3)
    img += rs.randn(H, W, 1).astype(np.float32) * 0.9
    return np.clip(img, 0, 255).astype(np.uint8)


_BG = {}


def bg(name):
    if name not in _BG:
        if name == 'night':
            _BG[name] = _grad([(0, (7, 9, 20)), (1, (10, 13, 28))])
        elif name == 'black':
            _BG[name] = _grad([(0, (3, 3, 7)), (1, (4, 4, 9))])
        elif name == 'predawn':
            _BG[name] = _grad([(0, (9, 9, 30)), (0.6, (26, 16, 52)), (1, (38, 20, 54))])
        elif name == 'dawn':
            _BG[name] = _grad([(0, (12, 10, 40)), (0.45, (46, 20, 70)), (0.75, (120, 44, 70)), (1, (150, 70, 50))], glow=(960, 800, 900, (60, 30, 6)))
        elif name == 'day':
            _BG[name] = _grad([(0, (30, 26, 84)), (0.4, (110, 50, 104)), (0.72, (214, 100, 84)), (1, (240, 160, 80))], glow=(960, 780, 1000, (40, 30, 10)))
    return _BG[name]


def bgmix(a, b, k):
    if k <= 0:
        return bg(a)
    if k >= 1:
        return bg(b)
    return cv2.addWeighted(bg(a), 1 - k, bg(b), k, 0)


class Lum:
    def __init__(self):
        self.surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        self.cx = cairo.Context(self.surf)
        self.cx.set_line_cap(cairo.LINE_CAP_ROUND)
        self.cx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.buf = np.ndarray((H, W, 4), np.uint8, self.surf.get_data())
        self.ov = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.ovbuf = np.ndarray((H, W, 4), np.uint8, self.ov.get_data())
        self.ox = cairo.Context(self.ov)
        self.ox.set_line_cap(cairo.LINE_CAP_ROUND)
        self.ox.set_line_join(cairo.LINE_JOIN_ROUND)
        self.extra = []
        self.use_ov = False
        self.t = 0.0

    def begin(self, t):
        self.t = t
        cx = self.cx
        cx.identity_matrix()
        cx.reset_clip()
        cx.set_operator(cairo.OPERATOR_SOURCE)
        cx.set_source_rgb(0, 0, 0)
        cx.paint()
        cx.set_operator(cairo.OPERATOR_ADD)
        self.extra = []
        self.use_ov = False

    def _src(self, col, a):
        self.cx.set_source_rgb(col[0] * a, col[1] * a, col[2] * a)

    # ----- strokes
    def lines(self, polys, col=WHITE, w=2.0, a=1.0, close=False):
        if a <= 0.003:
            return
        cx = self.cx
        cx.new_path()
        for q in polys:
            n = len(q)
            if n < 2:
                continue
            cx.move_to(q[0][0], q[0][1])
            for i in range(1, n):
                cx.line_to(q[i][0], q[i][1])
            if close:
                cx.close_path()
        cx.set_line_width(w)
        self._src(col, min(1.0, a))
        cx.stroke()

    def line(self, x0, y0, x1, y1, col=WHITE, w=2.0, a=1.0):
        self.lines([((x0, y0), (x1, y1))], col, w, a)

    def segs(self, s, col=WHITE, w=2.0, a=1.0):
        if a <= 0.003 or len(s) == 0:
            return
        cx = self.cx
        cx.new_path()
        for i in range(len(s)):
            cx.move_to(s[i][0], s[i][1])
            cx.line_to(s[i][2], s[i][3])
        cx.set_line_width(w)
        self._src(col, min(1.0, a))
        cx.stroke()

    def dots(self, xy, col=WHITE, d=3.0, a=1.0):
        """round dots via zero-length round-capped strokes"""
        if a <= 0.003 or len(xy) == 0:
            return
        cx = self.cx
        cx.new_path()
        for i in range(len(xy)):
            x, y = xy[i][0], xy[i][1]
            cx.move_to(x, y)
            cx.line_to(x + 0.01, y)
        cx.set_line_width(d)
        self._src(col, min(1.0, a))
        cx.stroke()

    def disc(self, x, y, r, col=WHITE, a=1.0):
        cx = self.cx
        cx.new_path()
        cx.arc(x, y, r, 0, TAU)
        self._src(col, min(1.0, a))
        cx.fill()

    def fill(self, pts, col=WHITE, a=1.0):
        cx = self.cx
        cx.new_path()
        cx.move_to(pts[0][0], pts[0][1])
        for i in range(1, len(pts)):
            cx.line_to(pts[i][0], pts[i][1])
        cx.close_path()
        self._src(col, min(1.0, a))
        cx.fill()

    def black(self, pts):
        """opaque occluder"""
        cx = self.cx
        cx.new_path()
        cx.move_to(pts[0][0], pts[0][1])
        for i in range(1, len(pts)):
            cx.line_to(pts[i][0], pts[i][1])
        cx.close_path()
        cx.set_operator(cairo.OPERATOR_SOURCE)
        cx.set_source_rgb(0, 0, 0)
        cx.fill()
        cx.set_operator(cairo.OPERATOR_ADD)

    def splat(self, xy, col=WHITE, amp=1.0, blur=0.9, wts=None):
        """dense point cloud via histogram"""
        x = np.asarray(xy[:, 0])
        y = np.asarray(xy[:, 1])
        m = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
        if not m.any():
            return
        idx = (y[m].astype(np.int64)) * W + x[m].astype(np.int64)
        cnt = np.bincount(idx, weights=None if wts is None else wts[m], minlength=W * H).reshape(H, W).astype(np.float32)
        if blur > 0:
            cnt = cv2.GaussianBlur(cnt, (0, 0), blur)
        k = 255.0 * amp
        ch = [np.clip(cnt * (k * col[2 - c]), 0, 255).astype(np.uint8) for c in range(3)]
        self.extra.append(cv2.merge(ch))

    def image(self, img):
        self.extra.append(img)

    # ----- vector text
    def text(self, s, x, y, size, font='futural', col=WHITE, a=1.0, w=None, rev=1.0, align='l', track=0.0):
        """single-stroke text. returns width"""
        st, wd = hershey(s, size, font)
        if not st or a <= 0.003:
            return wd
        ox = x - (wd / 2 if align == 'c' else wd if align == 'r' else 0)
        if w is None:
            w = max(1.5, size * 0.055)
        if rev < 1.0:
            lens = np.array([np.hypot(np.diff(q[:, 0]), np.diff(q[:, 1])).sum() + 2 for q in st])
            cum = np.concatenate([[0], np.cumsum(lens)])
            tot = cum[-1] * max(0.0, rev)
            out = []
            for k, q in enumerate(st):
                if cum[k] >= tot:
                    break
                f = (tot - cum[k]) / lens[k]
                if f >= 1:
                    out.append(q + (ox, y))
                else:
                    n = max(2, int(len(q) * f) + 1)
                    out.append(q[:n] + (ox, y))
            st2 = out
        else:
            st2 = [q + (ox, y) for q in st]
        self.lines(st2, col, w, a)
        return wd

    # ----- output
    def finish(self, bgimg=None, bloom=1.0, squash=None, white=0.0, flash=0.0, gain=1.0):
        self.surf.flush()
        img = np.ascontiguousarray(self.buf[:, :, :3])
        for e in self.extra:
            img = cv2.add(img, e)
        if gain < 0.995:
            img = cv2.convertScaleAbs(img, alpha=max(0.0, gain))
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        b1 = cv2.GaussianBlur(small, (0, 0), 2.0)
        b2 = cv2.GaussianBlur(cv2.resize(small, (W // 8, H // 8), interpolation=cv2.INTER_AREA), (0, 0), 5.0)
        glow = cv2.addWeighted(cv2.resize(b1, (W, H), interpolation=cv2.INTER_LINEAR), 0.70 * bloom,
                               cv2.resize(b2, (W, H), interpolation=cv2.INTER_LINEAR), 0.85 * bloom, 0)
        out = cv2.add(img, glow)
        if squash is not None:
            sx, sy = squash
            ww, hh = max(2, int(W * sx)), max(2, int(H * sy))
            sm = cv2.resize(out, (ww, hh), interpolation=cv2.INTER_AREA)
            gain = min(6.0, 1.0 / max(0.03, (sx * sy) ** 0.5))
            sm = cv2.convertScaleAbs(sm, alpha=gain)
            out = np.zeros_like(out)
            x0, y0 = (W - ww) // 2, (H - hh) // 2
            out[y0:y0 + hh, x0:x0 + ww] = sm
            g2 = cv2.GaussianBlur(cv2.resize(out, (W // 8, H // 8), interpolation=cv2.INTER_AREA), (0, 0), 6)
            out = cv2.add(out, cv2.resize(g2, (W, H), interpolation=cv2.INTER_LINEAR))
        if bgimg is None:
            bgimg = bg('night')
        out = cv2.add(out, bgimg)
        if flash > 0.003:
            out = cv2.addWeighted(out, 1.0, np.full_like(out, 255), min(1.0, flash), 0)
        if white > 0.003:
            wimg = np.empty_like(out)
            wimg[:] = (214, 236, 250)
            out = cv2.addWeighted(out, 1 - min(1.0, white), wimg, min(1.0, white), 0)
        if self.use_ov:
            self.ov.flush()
            al = self.ovbuf[:, :, 3:4].astype(np.float32) / 255.0
            out = (out.astype(np.float32) * (1 - al) + self.ovbuf[:, :, :3].astype(np.float32)).clip(0, 255).astype(np.uint8)
        return out

    def otext(self, s, x, y, size, font='futural', col=(0.1, 0.08, 0.12), a=1.0, w=None, rev=1.0, align='l'):
        ox = self.overlay()
        st, wd = hershey(s, size, font)
        if not st:
            return
        x0 = x - (wd / 2 if align == 'c' else wd if align == 'r' else 0)
        lens = np.array([np.hypot(np.diff(q[:, 0]), np.diff(q[:, 1])).sum() + 2 for q in st])
        cum = np.concatenate([[0], np.cumsum(lens)])
        tot = cum[-1] * clamp(rev)
        ox.new_path()
        for k, q in enumerate(st):
            if cum[k] >= tot:
                break
            n = len(q) if tot >= cum[k + 1] else max(2, int(len(q) * (tot - cum[k]) / lens[k]) + 1)
            ox.move_to(q[0][0] + x0, q[0][1] + y)
            for i in range(1, n):
                ox.line_to(q[i][0] + x0, q[i][1] + y)
        ox.set_line_width(w if w else max(1.5, size * 0.055))
        ox.set_source_rgba(col[0], col[1], col[2], a)
        ox.stroke()

    def overlay(self):
        """a normal (non-additive) drawing context composited last; for dark marks on light"""
        if not self.use_ov:
            ox = self.ox
            ox.set_operator(cairo.OPERATOR_SOURCE)
            ox.set_source_rgba(0, 0, 0, 0)
            ox.paint()
            ox.set_operator(cairo.OPERATOR_OVER)
            self.use_ov = True
        return self.ox


def label(L, t, fig, lyric, algo, t0, t1, ts, x=92, y=H - 78, col=WHITE, a=1.0, box=False):
    """museum label: figure number, the sung line, the algorithm. ts = scene start"""
    if box:
        w1 = hershey(lyric, 38, 'timesi')[1] if lyric else 0
        w2 = hershey(algo, 20, 'futural')[1]
        L.black([(x - 40, y - 140), (x + max(w1, w2) + 50, y - 140), (x + max(w1, w2) + 50, H), (x - 40, H)])
    k = ramp(t, ts + 0.05, ts + 0.5)
    L.text('FIG. %02d' % fig, x, y - 96, 20, col=DIM, a=0.95 * a, rev=k, w=1.5)
    if lyric:
        L.text(lyric, x, y - 44, 38, font='timesi', col=col, a=a, rev=ramp(t, t0, t1), w=2.1)
    L.text(algo, x, y, 20, col=DIM, a=0.95 * a, rev=ramp(t, ts + 0.15, ts + 0.9), w=1.5)


def lyric_seq(t, seq):
    """seq: [(text, t0, t1), ...] -> the line currently being sung (or the last one)"""
    cur = (None, 0, 1)
    for it in seq:
        if t >= it[1] - 0.05:
            cur = it
    return cur


_spec_cache = {}


def spectrum(t, n=64):
    """log-spaced magnitude spectrum of the song at time t, 0..1"""
    key = (int(t * FPS), n)
    if key in _spec_cache:
        return _spec_cache[key]
    m = 2048
    out = np.zeros(n)
    edges = np.geomspace(3, 800, n + 1)
    for tt in (t, t - 0.035):
        i0 = int(tt * SR) - m // 2
        idx = np.clip(i0 + np.arange(m), 0, len(MONO) - 1)
        mag = np.abs(np.fft.rfft(MONO[idx] * np.hanning(m)))
        for k in range(n):
            a_, b_ = int(edges[k]), max(int(edges[k]) + 1, int(edges[k + 1]))
            out[k] += mag[a_:b_].max()
    out = np.clip((20 * np.log10(out / 2 + 1e-6) - 2) / 34, 0, 1)
    if len(_spec_cache) > 8:
        _spec_cache.clear()
    _spec_cache[key] = out
    return out


def sun(L, t, x, y, R, n=1400, rot=None, cols=(GOLD, AMBER, CORAL), a=1.0, rays=1.0, d=3.4, beat=True, ray_col=None):
    """the sun: a golden-angle disc of points with the song's spectrum as its corona"""
    if rot is None:
        rot = t * 0.12
    kk = np.arange(1, n + 1)
    pu = A.kick(t) if beat else 0.0
    r = R * np.sqrt(kk / n) * (1 + 0.035 * pu)
    th = kk * 2.39996323 + rot
    px = x + r * np.cos(th)
    py = y + r * np.sin(th)
    P = np.stack([px, py], 1)
    n1, n2 = int(n * 0.30), int(n * 0.68)
    L.dots(P[:n1], cols[0], d=d * 1.1, a=a)
    L.dots(P[n1:n2], cols[1], d=d, a=a)
    L.dots(P[n2:], cols[2], d=d * 0.95, a=a)
    if rays > 0:
        sp = spectrum(t)
        m = len(sp)
        N = 2 * m
        segs = []
        for j in range(N):
            v = sp[j if j < m else N - 1 - j]
            an = -math.pi / 2 + (j + 0.5) * TAU / N
            r0 = R * 1.07
            r1 = r0 + R * (0.06 + 0.85 * v ** 1.5) * rays
            segs.append((x + r0 * math.cos(an), y + r0 * math.sin(an), x + r1 * math.cos(an), y + r1 * math.sin(an)))
        L.segs(segs, ray_col if ray_col is not None else cols[1], w=3.0, a=a)
