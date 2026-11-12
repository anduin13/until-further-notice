"""Code-drawing engine: pencil strokes with line boil, riso-style fills, paper tooth, lettering."""
import cairo, numpy as np, cv2, json, math, os
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)

# ---------- palette ----------
PAPER = (0.960, 0.940, 0.895)
INK = (0.12, 0.12, 0.17)
CORAL = (1.00, 0.33, 0.36)
YEL = (1.00, 0.79, 0.16)
CYAN = (0.08, 0.72, 0.80)
BLUE = (0.16, 0.24, 0.78)
PINK = (1.00, 0.48, 0.74)
NIGHT = (0.055, 0.065, 0.150)
CHALK = (0.96, 0.95, 0.90)
TAU = math.tau
TOOTH_HOLD = int(os.environ.get('TOOTH_HOLD', 1000000))
GRAIN_HOLD = int(os.environ.get('GRAIN_HOLD', 1000000))


def lerp(a, b, k):
    return a + (b - a) * k


def mixc(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ramp(t, a, b):
    """0 before a, 1 after b, linear between."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return clamp((t - a) / (b - a))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def eout(x, p=3):
    x = clamp(x)
    return 1 - (1 - x) ** p


def ein(x, p=3):
    return clamp(x) ** p


def back(x, s=1.9):
    """overshoot ease-out"""
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1


# ---------- noise tables ----------
NT = 1 << 16
_rs = np.random.RandomState(11)


def _smooth_table(sig):
    g = _rs.randn(NT)
    k = np.exp(-0.5 * (np.arange(-int(4 * sig), int(4 * sig) + 1) / sig) ** 2)
    s = np.convolve(np.concatenate([g[-len(k):], g, g[:len(k)]]), k, 'same')[len(k):-len(k)]
    return (s / s.std()).astype(np.float64)


SN = _smooth_table(5.0)     # wobble along strokes
RN = _rs.rand(NT)           # uniform randoms


def hsh(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def rnd(*a):
    return RN[hsh(*a) & (NT - 1)]


def rnds(n, *a):
    i0 = hsh(*a)
    return RN[(i0 + np.arange(n) * 7919) & (NT - 1)]


def sn(n, seed, step=1.0):
    return SN[(seed + (np.arange(n) * step).astype(np.int64)) & (NT - 1)]


def sn1(x, seed=0):
    """smooth noise of a scalar/array x (unit ~ correlation length)"""
    x = np.asarray(x, float) * 5.0 + seed * 131.7
    i = np.floor(x).astype(np.int64)
    f = x - i
    a = SN[i & (NT - 1)]
    b = SN[(i + 1) & (NT - 1)]
    return a + (b - a) * f


# ---------- audio ----------
class Audio:
    def __init__(self):
        try:
            d = json.load(open(os.path.join(DATA, 'audio.json')))
            b = json.load(open(os.path.join(DATA, 'beats.json')))
        except FileNotFoundError:
            raise SystemExit('data/audio.json and data/beats.json are missing: run  python prepare.py path/to/song.mp3')
        self.dur = d['dur']
        self.beats = np.array(b['beats'])
        self.off = b['first_tracked'] % 4
        self.bars = self.beats[self.off::4]
        for k in ('rms', 'low', 'mid', 'high', 'kick', 'snare', 'hat', 'onset'):
            setattr(self, '_' + k, np.array(d[k]))
        self.spec = np.array(d['spec'])
        # smoothed decaying envelopes
        for k in ('kick', 'snare', 'hat'):
            x = getattr(self, '_' + k)
            e = np.zeros_like(x)
            v = 0
            for i in range(len(x)):
                v = max(x[i], v * 0.80)
                e[i] = v
            setattr(self, '_' + k + 'e', e)

    def _g(self, name, t):
        a = getattr(self, '_' + name)
        return float(a[min(len(a) - 1, max(0, int(t * FPS)))])

    def kick(self, t): return self._g('kicke', t)
    def snare(self, t): return self._g('snaree', t)
    def hat(self, t): return self._g('hate', t)
    def rms(self, t): return self._g('rms', t)
    def low(self, t): return self._g('low', t)
    def high(self, t): return self._g('high', t)

    def bar(self, i):
        """time of bar i (float bars allowed, i.e. 12.5 = bar 12 beat 3)"""
        b = self.off + i * 4.0
        k = int(math.floor(b))
        k = max(0, min(len(self.beats) - 2, k))
        return float(self.beats[k] + (self.beats[k + 1] - self.beats[k]) * (b - k))

    def beatpos(self, t):
        """continuous beat coordinate (0 = bar 0 beat 1)"""
        i = int(np.searchsorted(self.beats, t, 'right')) - 1
        i = max(0, min(len(self.beats) - 2, i))
        return i + (t - self.beats[i]) / (self.beats[i + 1] - self.beats[i]) - self.off

    def pulse(self, t, decay=5.0, div=1.0):
        """1 at each beat (or every div beats) decaying exponentially"""
        p = self.beatpos(t) / div
        return math.exp(-decay * (p - math.floor(p)) * div)

    def spectrum(self, t):
        return self.spec[min(len(self.spec) - 1, max(0, int(t * FPS)))]


A = Audio()
B = A.bar


# ---------- fonts ----------
FONT_NAMES = {   # key -> file name; searched for in ./fonts and the usual system font folders
    'blk': 'Inter-BlackItalic.otf',
    'adv': 'texgyreadventor-bold.otf',
    'cn': 'texgyreheroscn-bold.otf',
}
FONT_DIRS = [os.path.join(ROOT, 'fonts'), '/usr/share/fonts', '/usr/share/texmf/fonts', '/usr/local/share/fonts',
             os.path.expanduser('~/.fonts'), os.path.expanduser('~/.local/share/fonts'),
             '/Library/Fonts', '/System/Library/Fonts', os.path.expanduser('~/Library/Fonts'), 'C:/Windows/Fonts']
_font_paths = {}


def font_path(key):
    if key not in _font_paths:
        want = FONT_NAMES[key].lower()
        for d in FONT_DIRS:
            for base, _, files in os.walk(d):
                for f in files:
                    if f.lower() == want:
                        _font_paths[key] = os.path.join(base, f)
                        return _font_paths[key]
        raise SystemExit(f'font {FONT_NAMES[key]} not found: install it or drop the file into ./fonts (see README)')
    return _font_paths[key]
_fonts = {}
_gcache = {}


class _FlatPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.cs = []
        self.cur = None

    def _moveTo(self, p):
        self.cur = [p]
        self.cs.append(self.cur)

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for k in range(1, 9):
            t = k / 8
            m = 1 - t
            self.cur.append((m ** 3 * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t ** 3 * p3[0],
                             m ** 3 * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for k in range(1, 7):
            t = k / 6
            m = 1 - t
            self.cur.append((m * m * p0[0] + 2 * m * t * p1[0] + t * t * p2[0],
                             m * m * p0[1] + 2 * m * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        pass


def _font(key):
    if key not in _fonts:
        f = TTFont(font_path(key))
        _fonts[key] = (f, f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm, f['hmtx'])
    return _fonts[key]


def glyph_contours(key, text, size, track=0.0):
    """returns (list of Nx2 arrays, y-down, baseline at y=0, starting x=0), total width"""
    ck = (key, text, track)
    if ck not in _gcache:
        f, gs, cmap, upm, hmtx = _font(key)
        x = 0.0
        out = []
        for ch in text:
            gn = cmap.get(ord(ch))
            if gn is None:
                x += upm * 0.3
                continue
            pen = _FlatPen(gs)
            gs[gn].draw(pen)
            for c in pen.cs:
                a = np.array(c, float)
                if len(a) > 2:
                    a[:, 0] += x
                    a[:, 1] *= -1
                    out.append(a / upm)
            x += hmtx[gn][0] + track * upm
        _gcache[ck] = (out, (x - track * upm) / upm)
    cs, wd = _gcache[ck]
    return [c * size for c in cs], wd * size


_hershey = {}


def hershey(text, size, font='scripts'):
    """single-stroke plotter font. returns (list of Nx2 strokes y-down, width)"""
    ck = (font, text)
    if ck not in _hershey:
        from HersheyFonts import HersheyFonts
        hf = HersheyFonts()
        hf.load_default_font(font)
        hf.normalize_rendering(1.0)
        st = [np.array(s, float) for s in hf.strokes_for_text(text)]
        st = [s for s in st if len(s) > 1]
        if st:
            allp = np.vstack(st)
            x0 = allp[:, 0].min()
            wd = allp[:, 0].max() - x0
            for s in st:
                s[:, 0] -= x0
                s[:, 1] *= -1
        else:
            wd = 0
        _hershey[ck] = (st, wd)
    st, wd = _hershey[ck]
    return [s * size for s in st], wd * size


# ---------- geometry helpers ----------
def circ(x, y, r, a0=0.0, a1=TAU, n=None):
    if n is None:
        n = max(8, int(abs(a1 - a0) * r / 9) + 2)
    a = np.linspace(a0, a1, n)
    return np.stack([x + r * np.cos(a), y + r * np.sin(a)], 1)


def rect(x, y, w, h):
    return np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], float)


def rot(pts, ang, cx=0.0, cy=0.0):
    pts = np.asarray(pts, float)
    c, s = math.cos(ang), math.sin(ang)
    x = pts[:, 0] - cx
    y = pts[:, 1] - cy
    return np.stack([cx + x * c - y * s, cy + x * s + y * c], 1)


def resample(pts, seg):
    pts = np.asarray(pts, float)
    d = np.hypot(np.diff(pts[:, 0]), np.diff(pts[:, 1]))
    L = np.concatenate([[0.0], np.cumsum(d)])
    tot = L[-1]
    if tot < 1e-6:
        return pts[:1], 0.0
    n = max(2, int(tot / seg) + 2)
    u = np.linspace(0, tot, n)
    return np.stack([np.interp(u, L, pts[:, 0]), np.interp(u, L, pts[:, 1])], 1), tot


# ---------- paper textures ----------
def _make_textures():
    rs = np.random.RandomState(5)
    n = rs.rand(H + 64, W + 64).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 0.75)
    n = (n - n.mean()) / n.std()
    # tooth: how much ink the paper takes (alpha mask), mostly high with pits
    TA = float(os.environ.get('TOOTH_AMT', 1.0))
    GA = float(os.environ.get('GRAIN_AMT', 1.0))
    tooth = np.clip(1 - TA * (0.07 - 0.14 * n), 0.45, 1.0)
    low = cv2.GaussianBlur(rs.rand(H + 64, W + 64).astype(np.float32), (0, 0), 2.2)
    low = (low - low.mean()) / low.std()
    tooth = np.clip(tooth - TA * 0.07 * np.clip(low, 0, 3), 0.40, 1.0)
    tooth8 = (tooth * 255).astype(np.uint8)
    # grain: brightness modulation of everything (128 = neutral)
    g2 = rs.rand(H + 64, W + 64).astype(np.float32)
    g2 = cv2.GaussianBlur(g2, (0, 0), 1.0)
    g2 = (g2 - g2.mean()) / g2.std()
    blot = cv2.GaussianBlur(rs.rand(H + 64, W + 64).astype(np.float32), (0, 0), 60)
    blot = (blot - blot.mean()) / blot.std()
    yy, xx = np.mgrid[0:H + 64, 0:W + 64].astype(np.float32)
    vig = ((xx - W / 2 - 32) / (W * 0.62)) ** 2 + ((yy - H / 2 - 32) / (H * 0.62)) ** 2
    grain = 128 * (1 + GA * 0.022 * g2 + 0.012 * blot - 0.06 * np.clip(vig - 0.40, 0, 2))
    grain8 = np.clip(grain, 0, 255).astype(np.uint8)
    return tooth8, grain8


_TOOTH8, _GRAIN8 = _make_textures()
_stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_A8, W + 64)
_tooth_buf = np.zeros((H + 64, _stride), np.uint8)
_tooth_buf[:, :W + 64] = _TOOTH8
_TOOTH_SURF = cairo.ImageSurface.create_for_data(memoryview(_tooth_buf), cairo.FORMAT_A8, W + 64, H + 64, _stride)
_GRAIN3 = cv2.merge([_GRAIN8] * 3)


class Canvas:
    def __init__(self):
        self.surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        self.cx = cairo.Context(self.surf)
        self.cx.set_line_cap(cairo.LINE_CAP_ROUND)
        self.cx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.buf = np.ndarray((H, W, 4), np.uint8, self.surf.get_data())
        self.ink = INK
        self.night = False
        self.boil = 0
        self.t = 0.0

    # ----- frame lifecycle -----
    def begin(self, t, paper=PAPER, ink=INK, night=False):
        self.t = t
        self.boil = int(t * FPS) // 3
        self.ink = ink
        self.night = night
        cx = self.cx
        cx.identity_matrix()
        cx.reset_clip()
        cx.set_operator(cairo.OPERATOR_OVER)
        cx.set_source_rgb(*paper)
        cx.paint()
        self._open()

    def _open(self):
        self.cx.push_group()

    def _close(self):
        cx = self.cx
        cx.pop_group_to_source()
        ox = -int(rnd(self.boil // TOOTH_HOLD, 1) * 60)
        oy = -int(rnd(self.boil // TOOTH_HOLD, 2) * 60)
        cx.mask_surface(_TOOTH_SURF, ox, oy)

    def flush(self):
        """composite what has been drawn so far through the paper tooth"""
        self._close()
        self._open()

    def paper(self, col, ink=None, night=None):
        """repaint the whole sheet (outside the tooth group)"""
        self._close()
        self.cx.set_source_rgb(*col)
        self.cx.paint()
        self._open()
        if ink is not None:
            self.ink = ink
        if night is not None:
            self.night = night

    def solid(self, contours, col, wob=1.0, seed=0):
        """opaque fill that bypasses the paper tooth (for light shapes on dark paper)"""
        self._close()
        if isinstance(contours, np.ndarray) and contours.ndim == 2:
            contours = [contours]
        self._path(contours, wob, seed, (0, 0))
        self.cx.set_source_rgb(*col)
        self.cx.fill()
        self._open()

    def region(self, contours, paper, ink=INK, night=False, wob=0.0, seed=0):
        """start drawing inside a clipped region with its own paper colour"""
        self._close()
        self._saved = (self.ink, self.night)
        if isinstance(contours, np.ndarray) and contours.ndim == 2:
            contours = [contours]
        self.cx.save()
        self._path(contours, wob, seed, (0, 0))
        self.cx.clip()
        if paper is not None:
            self.cx.set_source_rgb(*paper)
            self.cx.paint()
        self._open()
        self.ink, self.night = ink, night

    def endregion(self):
        self._close()
        self.cx.restore()
        self._open()
        self.ink, self.night = self._saved

    def finish(self, flash=0.0, shake=(0, 0)):
        self._close()
        self.surf.flush()
        img = np.ascontiguousarray(self.buf[:, :, :3])
        ox = int(rnd(self.boil // GRAIN_HOLD, 3) * 60)
        oy = int(rnd(self.boil // GRAIN_HOLD, 4) * 60)
        g = _GRAIN3[oy:oy + H, ox:ox + W]
        out = cv2.multiply(img, g, scale=1 / 128.0)
        if flash > 0.003:
            out = cv2.addWeighted(out, 1 - flash, np.full_like(out, 250), flash, 0)
        return out

    # ----- drawing primitives -----
    def _src(self, col, a):
        col = self.ink if col is None else col
        self.cx.set_source_rgba(col[0], col[1], col[2], a)

    def pl(self, pts, w=3.0, a=0.94, wob=1.7, seed=0, col=None, rev=1.0, close=False, boil=0.55, passes=2, seg=11.0):
        """pencil polyline. returns head point (x, y) of the revealed stroke"""
        if rev <= 0.0:
            return None
        pts = np.asarray(pts, float)
        if close:
            pts = np.vstack([pts, pts[:1]])
        dx = np.diff(pts[:, 0])
        dy = np.diff(pts[:, 1])
        d = np.hypot(dx, dy)
        L = np.concatenate([[0.0], np.cumsum(d)])
        tot = L[-1]
        if tot < 0.5:
            return None
        end = tot * min(1.0, rev)
        n = max(2, int(end / seg) + 2)
        u = np.arange(n) * seg
        u[-1] = end
        u = np.minimum(u, end)
        x = np.interp(u, L, pts[:, 0])
        y = np.interp(u, L, pts[:, 1])
        cx = self.cx
        col = self.ink if col is None else col
        h0 = hsh(seed, 77)
        hb = hsh(seed, self.boil, 5)
        idx = np.arange(n)
        taper = np.minimum(1.0, np.minimum(u, tot - u) / 18.0 + 0.25) if not close else 1.0
        for p in range(passes):
            o = p * 9001
            if p == 2:
                wob = wob * 1.8
            wx = (SN[(h0 + o + idx) & (NT - 1)] + boil * SN[(hb + o + idx) & (NT - 1)]) * wob * taper
            wy = (SN[(h0 + o + 30011 + idx) & (NT - 1)] + boil * SN[(hb + o + 30011 + idx) & (NT - 1)]) * wob * taper
            X = x + wx
            Y = y + wy
            cx.new_path()
            cx.move_to(X[0], Y[0])
            for i in range(1, n):
                cx.line_to(X[i], Y[i])
            if p == 0:
                cx.set_line_width(w)
                cx.set_source_rgba(col[0], col[1], col[2], a * (0.80 if passes > 1 else 1.0))
            elif p == 2:
                cx.set_line_width(w * 0.4)
                cx.set_source_rgba(col[0], col[1], col[2], a * 0.5)
            else:
                cx.set_line_width(w * 0.6)
                cx.set_source_rgba(col[0], col[1], col[2], a * 0.7)
            cx.stroke()
        return (float(x[-1]), float(y[-1]))

    def line(self, x0, y0, x1, y1, **k):
        return self.pl(np.array([[x0, y0], [x1, y1]], float), **k)

    def ticks(self, segs, w=1.6, a=0.7, jit=1.2, seed=0, col=None, boil=True):
        """many short straight strokes in one go. segs: Nx4"""
        segs = np.asarray(segs, float)
        n = len(segs)
        if n == 0:
            return
        h = hsh(seed, self.boil if boil else 0, 9)
        j = SN[(h + np.arange(n * 4) * 13) & (NT - 1)].reshape(n, 4) * jit
        s = segs + j
        cx = self.cx
        cx.new_path()
        for i in range(n):
            cx.move_to(s[i, 0], s[i, 1])
            cx.line_to(s[i, 2], s[i, 3])
        cx.set_line_width(w)
        self._src(col, a)
        cx.stroke()

    def _path(self, contours, wob, seed, off):
        cx = self.cx
        cx.new_path()
        for k, c in enumerate(contours):
            c = np.asarray(c, float)
            if wob > 0 and len(c) > 1:
                c, tot = resample(np.vstack([c, c[:1]]), 16.0)
                n = len(c)
                h0 = hsh(seed, k, 3)
                hb = hsh(seed, k, self.boil)
                c = c + np.stack([SN[(h0 + np.arange(n)) & (NT - 1)] + 0.4 * SN[(hb + np.arange(n)) & (NT - 1)],
                                  SN[(h0 + 999 + np.arange(n)) & (NT - 1)] + 0.4 * SN[(hb + 999 + np.arange(n)) & (NT - 1)]], 1) * wob
            cx.move_to(c[0, 0] + off[0], c[0, 1] + off[1])
            for i in range(1, len(c)):
                cx.line_to(c[i, 0] + off[0], c[i, 1] + off[1])
            cx.close_path()

    def fill(self, contours, col, a=1.0, off=(0, 0), wob=1.2, seed=0, mul=True, evenodd=False):
        """flat riso-style fill. contours: one Nx2 array or list of them"""
        if a <= 0:
            return
        if isinstance(contours, np.ndarray) and contours.ndim == 2:
            contours = [contours]
        cx = self.cx
        self._path(contours, wob, seed, off)
        cx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD if evenodd else cairo.FILL_RULE_WINDING)
        if mul and not self.night:
            cx.set_operator(cairo.OPERATOR_MULTIPLY)
        cx.set_source_rgba(col[0], col[1], col[2], a)
        cx.fill()
        cx.set_operator(cairo.OPERATOR_OVER)

    def clip(self, contours, wob=0.0, seed=0):
        if isinstance(contours, np.ndarray) and contours.ndim == 2:
            contours = [contours]
        self.cx.save()
        self._path(contours, wob, seed, (0, 0))
        self.cx.clip()

    def unclip(self):
        self.cx.restore()

    def hatch(self, contours, ang=-0.9, gap=9.0, w=1.5, a=0.6, seed=0, col=None, rev=1.0, jit=1.6, bbox=None):
        """hatch-fill a polygon with pencil lines"""
        if rev <= 0:
            return
        if isinstance(contours, np.ndarray) and contours.ndim == 2:
            contours = [contours]
        allp = np.vstack(contours)
        x0, y0 = allp.min(0)
        x1, y1 = allp.max(0)
        cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
        R = math.hypot(x1 - x0, y1 - y0) / 2 + 4
        n = int(2 * R / gap) + 1
        k = np.arange(n)
        offs = -R + k * gap + (RN[(hsh(seed, 4) + k) & (NT - 1)] - 0.5) * gap * 0.5
        ca, sa = math.cos(ang), math.sin(ang)
        nx, ny = -sa, ca
        ext = R * (0.9 + 0.1 * RN[(hsh(seed, 6) + k) & (NT - 1)])
        segs = np.stack([cxm + nx * offs - ca * ext, cym + ny * offs - sa * ext,
                         cxm + nx * offs + ca * ext, cym + ny * offs + sa * ext], 1)
        m = int(n * min(1.0, rev))
        self.clip(contours)
        self.ticks(segs[:m], w=w, a=a, jit=jit, seed=seed, col=col)
        self.unclip()

    # ----- lettering -----
    def text(self, s, x, y, size, font='blk', align='c', fill=None, fa=1.0, off=(6, 5), outline=True, w=2.6, a=0.95,
             hatch=None, rot=0.0, seed=0, rev=1.0, track=0.0, col=None, wob=1.3, shadow=None, knock=False):
        """outlined display lettering. (x, y) = baseline anchor. returns bbox (x0,y0,x1,y1)"""
        cs, wd = glyph_contours(font, s, size, track)
        if not cs:
            return (x, y, x, y)
        ox = x - (wd / 2 if align == 'c' else wd if align == 'r' else 0)
        cs = [c + (ox, y) for c in cs]
        if rot:
            cs = [rot_(c, rot, x, y - size * 0.35) for c in cs]
        if shadow is not None:
            self.fill(cs, shadow[0], a=fa, off=shadow[1], wob=0.8, seed=seed + 5)
        if knock:
            self.fill(cs, NIGHT if self.night else PAPER, mul=False, wob=0.8, seed=seed)
        if fill is not None:
            self.fill(cs, fill, a=fa, off=off, wob=0.8, seed=seed)
        if hatch is not None:
            self.hatch(cs, ang=hatch.get('ang', -0.8), gap=hatch.get('gap', 8), w=hatch.get('w', 1.4),
                       a=hatch.get('a', 0.6), seed=seed, col=hatch.get('col', col), rev=hatch.get('rev', 1.0))
        if outline:
            n = len(cs)
            for k, c in enumerate(cs):
                r = clamp(rev * n - k) if rev < 1 else 1.0
                self.pl(c, w=w, a=a, wob=wob, seed=seed * 131 + k, close=True, rev=r, col=col, seg=9.0)
        allp = np.vstack(cs)
        return (*allp.min(0), *allp.max(0))

    def script(self, s, x, y, size, font='scripts', align='c', rev=1.0, w=2.4, a=0.95, col=None, seed=0, rot=0.0, wob=0.8):
        """single-stroke handwriting / plotter text. returns pen head position"""
        st, wd = hershey(s, size, font)
        if not st:
            return None
        ox = x - (wd / 2 if align == 'c' else wd if align == 'r' else 0)
        lens = np.array([np.hypot(np.diff(q[:, 0]), np.diff(q[:, 1])).sum() + 6 for q in st])
        cum = np.concatenate([[0], np.cumsum(lens)])
        tot = cum[-1] * clamp(rev)
        head = None
        for k, q in enumerate(st):
            if cum[k] >= tot and rev < 1:
                break
            r = clamp((tot - cum[k]) / lens[k])
            q = q + (ox, y)
            if rot:
                q = rot_(q, rot, x, y)
            hp = self.pl(q, w=w, a=a, wob=wob, seed=seed * 977 + k, rev=r, col=col, seg=7.0, boil=0.4)
            if hp is not None:
                head = hp
        return head


rot_ = rot


def text_width(s, size, font='blk', track=0.0):
    return glyph_contours(font, s, size, track)[1]


def _polys(self, lines, w=1.6, a=0.8, col=None):
    """fast batch of plain polylines (no wobble) in a single stroke"""
    cx = self.cx
    cx.new_path()
    for q in lines:
        if len(q) < 2:
            continue
        cx.move_to(q[0][0], q[0][1])
        for i in range(1, len(q)):
            cx.line_to(q[i][0], q[i][1])
    cx.set_line_width(w)
    self._src(col, a)
    cx.stroke()


def _dots(self, pts, r, col=None, a=1.0, mul=False):
    """filled discs. r scalar or array"""
    cx = self.cx
    pts = np.asarray(pts, float)
    rr = np.broadcast_to(np.asarray(r, float), (len(pts),))
    cx.new_path()
    for i in range(len(pts)):
        if rr[i] <= 0.05:
            continue
        cx.new_sub_path()
        cx.arc(pts[i, 0], pts[i, 1], rr[i], 0, TAU)
    if mul and not self.night:
        cx.set_operator(cairo.OPERATOR_MULTIPLY)
    self._src(col, a)
    cx.fill()
    cx.set_operator(cairo.OPERATOR_OVER)


Canvas.polys = _polys
Canvas.dots = _dots
