"""usage: render.py stills name t1 t2 ... | render.py chunk i n [f0 f1] | render.py sweep [step]"""
import sys, os, subprocess, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lum import *
import scenes as vscenes

TL = vscenes.timeline()
DUR = A.dur
NFR = int(round(DUR * FPS))


def draw(L, t):
    for (t0, t1, f) in TL:
        if t0 <= t < t1:
            return f(L, t, t - t0, t1 - t0)
    L.begin(t)
    return L.finish(bg('black'))


if __name__ == '__main__':
    L = Lum()
    mode = sys.argv[1]
    if mode == 'stills':
        name = sys.argv[2]
        ims = []
        for t in [float(x) for x in sys.argv[3:]]:
            t0 = time.time()
            im = draw(L, t).copy()
            ms = (time.time() - t0) * 1000
            cv2.putText(im, f'{t:.2f}s {ms:.0f}ms', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            ims.append(im)
        cols = 2 if len(ims) > 1 else 1
        while len(ims) % cols:
            ims.append(np.zeros_like(ims[0]))
        sheet = np.vstack([np.hstack(ims[i:i + cols]) for i in range(0, len(ims), cols)])
        sheet = cv2.resize(sheet, (sheet.shape[1] // 2, sheet.shape[0] // 2), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{OUT}/in_light_{name}.jpg', sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
    elif mode == 'sweep':
        step = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        tl = TL
        for a, b in zip(tl, tl[1:]):
            if abs(a[1] - b[0]) > 1e-6:
                print('GAP/OVERLAP', a[1], b[0])
        t = 0.0; n = 0; tot = 0; errs = 0; per = {}
        while t < DUR:
            t0 = time.time()
            try:
                draw(L, t)
            except Exception:
                errs += 1
                if errs < 5:
                    print('ERR at', t); traceback.print_exc()
                L = Lum()
            dt = time.time() - t0
            tot += dt; n += 1
            k = int(t // 10) * 10
            per[k] = per.get(k, 0) + dt
            t += step
        print('frames', n, 'avg ms', tot / n * 1000, 'errors', errs)
        print({k: round(v / (10 / step) * 1000) for k, v in per.items()})
    elif mode == 'chunk':
        i, n = int(sys.argv[2]), int(sys.argv[3])
        f0, f1 = NFR * i // n, NFR * (i + 1) // n
        if len(sys.argv) > 5:
            f0, f1 = int(sys.argv[4]), int(sys.argv[5])
        os.makedirs(f'{OUT}/in_light', exist_ok=True)
        out = f'{OUT}/in_light/chunk_{i:03d}.mp4'
        tmp = f'{OUT}/in_light/tmp_{i:03d}.mp4'
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
               '-c:v', 'libx264', '-preset', os.environ.get('PRESET', 'medium'), '-crf', os.environ.get('CRF', '19'), '-pix_fmt', 'yuv420p',
               '-g', '60', '-threads', '1'] + (['-maxrate', os.environ['MAXRATE'], '-bufsize', os.environ.get('BUFSIZE', '10M')] if os.environ.get('MAXRATE') else []) + [tmp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(f0, f1):
            p.stdin.write(draw(L, f / FPS).tobytes())
            if (f - f0) % 150 == 0:
                print(f'chunk {i}: {f - f0}/{f1 - f0} {time.time() - t0:.0f}s', flush=True)
        p.stdin.close()
        rc = p.wait()
        if rc == 0:
            os.replace(tmp, out)
        print(f'chunk {i} done rc={rc} {time.time() - t0:.0f}s', flush=True)
        sys.exit(rc)
