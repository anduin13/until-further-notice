"""Bridge (pendulums, the sky falls, the sun assembles) and outro."""
from lum import *
import sims
import v_b

T_BR = B(88)
T_FALL = 179.25
SUNC = (960, 470)
SUNR = 240.0
FLOORY = 960.0


def _stars(L, t, a=1.0, fall=False):
    S = sims.sky()
    x, y, mag = S['x'], S['y'], S['mag']
    n = len(x)
    born = T_BR + 0.5 + S['jit'] * 9.0
    vis = t >= born
    tw = 0.7 + 0.3 * np.sin(t * (1.5 + 3 * mag) + S['jit'] * 40)
    if not fall:
        P = np.stack([x, y], 1)
        L.dots(P[vis & (mag < 0.3)], DIM, d=2.4, a=0.8 * a)
        L.dots(P[vis & (mag >= 0.3) & (mag < 0.75)], ICE, d=3.0, a=0.8 * a)
        L.dots(P[vis & (mag >= 0.75)], WHITE, d=4.2, a=a)
        return None
    tau = np.clip(t - T_FALL - S['tf'], 0, None)
    g = 2600.0
    yy = np.minimum(y + 0.5 * g * tau ** 2, S['rest'])
    landed = yy >= S['rest'] - 0.01
    P = np.stack([x, yy], 1)
    vel = g * tau
    falling = (tau > 0) & ~landed
    L.dots(P[~falling & (mag < 0.3)], DIM, d=2.6, a=0.9)
    L.dots(P[~falling & (mag >= 0.3) & (mag < 0.75)], ICE, d=3.0, a=0.85)
    L.dots(P[~falling & (mag >= 0.75)], WHITE, d=4.0, a=1.0)
    if falling.any():
        ln = np.minimum(260, vel[falling] * 0.05)
        L.segs(np.stack([x[falling], yy[falling] - ln, x[falling], yy[falling]], 1), WHITE, 1.8, 0.9)
    return P


# ---------------------------------------------------------------- 19. maybe i'm wrong: double pendulums
def pendulums(L, t, u, d):
    L.begin(t)
    D = sims.pend()
    th = D['th']
    px, py, Ln = 960, 300, 205.0
    fi = min(len(th) - 1, u * 60.0)
    i = int(fi)
    out = 1 - ramp(t, 178.6, 179.0)
    _stars(L, t, a=0.75)
    n = th.shape[1]
    for k in range(n):
        a1, a2 = th[i, k]
        x1, y1 = px + Ln * math.sin(a1), py + Ln * math.cos(a1)
        x2, y2 = x1 + Ln * math.sin(a2), y1 + Ln * math.cos(a2)
        i0 = max(0, i - 100)
        tr = th[i0:i + 1, k]
        tx = px + Ln * np.sin(tr[:, 0]) + Ln * np.sin(tr[:, 1])
        ty = py + Ln * np.cos(tr[:, 0]) + Ln * np.cos(tr[:, 1])
        m = len(tx)
        if m > 3:
            L.lines([np.stack([tx[:m // 2 + 1], ty[:m // 2 + 1]], 1)], ICE, 1.3, 0.22 * out)
            L.lines([np.stack([tx[m // 2:], ty[m // 2:]], 1)], ICE, 1.6, 0.5 * out)
        L.lines([[(px, py), (x1, y1), (x2, y2)]], WHITE, 1.8, 0.42 * out)
        L.dots([(x1, y1)], WHITE, d=7, a=0.5 * out)
        L.dots([(x2, y2)], WHITE, d=9, a=0.8 * out)
    L.disc(px, py, 5, WHITE, out)
    ly = lyric_seq(t, [("and maybe i'm wrong", 170.56, 174.2), ("i've been wrong before", 175.08, 177.4)])
    label(L, t, 19, ly[0] if t > 170.3 else None, 'TWELVE DOUBLE PENDULUMS, RELEASED ONE MILLIONTH OF A RADIAN APART', ly[1], ly[2], T_BR + 1.0)
    return L.finish(bg('black'), gain=ramp(u, 0.0, 1.5))


# ---------------------------------------------------------------- 20. the sky falls
def skyfall(L, t, u, d):
    L.begin(t)
    _stars(L, t, fall=True)
    L.line(40, FLOORY + 8, W - 40, FLOORY + 8, DIM, 1.3, 0.5 * ramp(t, T_FALL, T_FALL + 1))
    crash = T_FALL + 3.25 + 0.75
    fl = 0.32 * (1 - ramp(t, crash, crash + 0.45)) * (1 if t >= crash else 0)
    ly = lyric_seq(t, [('maybe the sky will fall', 178.97, 181.1), ('and come crashing through the door', 181.46, 184.3)])
    label(L, t, 20, ly[0], 'GRAVITY, 1600 STARS', ly[1], ly[2], 179.0, y=H - 190)
    return L.finish(bg('black'), flash=fl)


# ---------------------------------------------------------------- 21. eyes on the sun
def sunrise(L, t, u, d):
    L.begin(t)
    S = sims.sky()
    n = len(S['x'])
    x0, y0 = S['x'], S['rest']
    td = 188.55 + S['jit'] * 2.3
    k = np.clip((t - td) / 1.15, 0, 1)
    e = k * k * (3 - 2 * k)
    grow = 1 + 0.22 * ease(ramp(t, B(110), B(112)))
    R = SUNR * grow
    kk = S['k']
    rot_ = t * 0.12
    pu = A.kick(t)
    rr = R * np.sqrt(kk / n) * (1 + 0.035 * pu * (k >= 1))
    th = kk * 2.39996323 + rot_
    tx = SUNC[0] + rr * np.cos(th)
    ty = SUNC[1] + rr * np.sin(th)
    arc = np.sin(e * math.pi) * (120 + 200 * S['mag']) * np.sign(x0 - 960)
    px = x0 + (tx - x0) * e + arc * 0.6
    py = y0 + (ty - y0) * e - np.sin(e * math.pi) * 60
    P = np.stack([px, py], 1)
    rest = k <= 0
    mov = (k > 0) & (k < 1)
    done = k >= 1
    L.dots(P[rest & (S['mag'] < 0.5)], DIM, d=2.6, a=0.9)
    L.dots(P[rest & (S['mag'] >= 0.5)], ICE, d=3.2, a=0.9)
    L.dots(P[mov], WHITE, d=3.6, a=1.0)
    inner = kk < n * 0.30
    midr = (kk >= n * 0.30) & (kk < n * 0.68)
    L.dots(P[done & inner], GOLD, d=3.8, a=1.0)
    L.dots(P[done & midr], AMBER, d=3.5, a=1.0)
    L.dots(P[done & ~inner & ~midr], CORAL, d=3.3, a=1.0)
    L.line(40, FLOORY + 8, W - 40, FLOORY + 8, DIM, 1.3, 0.5 * (1 - ramp(t, 191.0, 193.0)))
    # corona: the spectrum returns once the disc is whole
    cor = ramp(t, 191.6, 193.2)
    if cor > 0:
        sp = spectrum(t)
        m = len(sp)
        N = 2 * m
        segs = []
        rk = 1 + 1.6 * ein(ramp(t, B(110), B(112)), 2)
        for j in range(N):
            v = sp[j if j < m else N - 1 - j]
            an = -math.pi / 2 + (j + 0.5) * TAU / N
            r0 = R * 1.07
            r1 = r0 + R * (0.06 + 0.85 * v ** 1.5) * cor * rk
            segs.append((SUNC[0] + r0 * math.cos(an), SUNC[1] + r0 * math.sin(an), SUNC[0] + r1 * math.cos(an), SUNC[1] + r1 * math.sin(an)))
        L.segs(segs, AMBER, 3.0, cor)
        if t > B(110):
            v_b.rings(L, t, SUNC[0], SUNC[1], R * 1.1, AMBER, a=0.5 * ramp(t, B(110), B(110) + 0.5))
    ly = lyric_seq(t, [("but i'd rather be wrong", 184.80, 188.2), ('with my eyes on the sun', 188.74, 192.0), ('than right in the dark', 193.62, 195.7), ('when the dark has won', 196.62, 199.6)])
    algo = 'WHAT FELL: 1600 POINTS AT REST' if t < 188.55 else 'PHYLLOTAXIS: EACH POINT TURNED 137.5 DEGREES FROM THE LAST'
    label(L, t, 21, ly[0], algo, ly[1], ly[2], 184.6 if t < 188.55 else 188.55, y=H - 190 if t < 190.5 else H - 78)
    kb = ramp(t, 192.5, B(110))
    kd = ramp(t, B(110), B(112))
    bgi = bgmix('black', 'predawn', kb) if kd <= 0 else bgmix('predawn', 'dawn', kd)
    return L.finish(bgi, flash=0.95 * ein(ramp(t, B(112) - 0.3, B(112)), 2))


# ---------------------------------------------------------------- outro
def outro(L, t, u, d):
    L.begin(t)
    wt = v_b.WT[3]
    te = B(144)                       # the music stops
    rise = ease(ramp(t, B(128), B(136)))
    swell = ein(ramp(t, B(138), te), 2.2)
    sy = 520 - 80 * rise
    R = 235 + 25 * rise + 900 * swell
    hy = 640 + 500 * ein(ramp(t, B(136), B(142)), 2)
    if swell < 0.9:
        sun(L, t, 960, sy, R, cols=(WHITE, GOLD, ROSE), n=1900, rays=1.0, d=3.4 + 6 * swell)
        v_b.rings(L, t, 960, sy, R * 1.1, GOLD, a=0.35)
    if hy < H + 40:
        v_b.terrain(L, t, hy, 1.6, VIOLET, col2=ROSE, amp=1.0 + 0.25 * A.low(t), a=1 - ramp(t, B(136), B(141)))
    # the signal returns
    sg = ramp(t, B(132), B(134)) * (1 - ramp(t, 247.6, 249.4))
    if sg > 0:
        nn = 900
        wv = wave(t, nn, win=0.05)
        xs = np.linspace(120, 1800, nn)
        L.lines([np.stack([xs, 900 + 170 * wv * np.hanning(nn) ** 0.6], 1)], WHITE, 2.0, 0.9 * sg)
    if t < 249.6:
        ly = lyric_seq(t, [('until further notice...', 235.38, 238.3), ('until further notice...', 242.48, 245.3)])
        if t > 235.2:
            L.text(ly[0], 960, 1040, 38, font='timesi', col=WHITE, rev=ramp(t, ly[1], ly[2]), w=2.1, align='c', a=1 - ramp(t, 248.6, 249.6))
    else:
        L.text("it's not too late", 960, 1010, 64, font='timesi', col=WHITE, rev=ramp(t, 250.20, 252.7), w=3.2, align='c')
    kbg = ramp(t, B(128), B(140))
    white = ein(ramp(t, B(139), te - 0.3), 1.6)
    img = None
    if t >= te - 0.4:
        # light everywhere; one dark point, as it began
        k = ramp(t, te - 0.4, te + 0.6)
        ox = L.overlay()
        ox.new_path()
        ox.arc(960, 560, 5.0, 0, TAU)
        ox.set_source_rgba(0.10, 0.08, 0.14, k)
        ox.fill()
        L.otext("it's not too late", 960, 660, 34, font='timesi', col=(0.10, 0.08, 0.14), a=k, w=2.0, rev=ramp(t, te + 0.3, te + 1.6), align='c')
        L.otext('UNTIL FURTHER NOTICE', 960, 1000, 18, font='futural', col=(0.10, 0.08, 0.14), a=0.6 * ramp(t, te + 1.4, te + 2.2), w=1.4, align='c')
    return L.finish(bgmix('dawn', 'day', kbg), white=white, flash=0.4 * (1 - ramp(u, 0, 0.2)))


def timeline():
    return [
        (T_BR, 179.0, pendulums),
        (179.0, 184.6, skyfall),
        (184.6, B(112), sunrise),
        (B(128), A.dur + 1, outro),
    ]
