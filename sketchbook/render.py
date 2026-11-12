"""Timeline + renderer. usage: render.py stills name t1 t2 ... | render.py chunk i n | render.py bench t"""
import sys, os, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motifs import *
import scenes

TL = scenes.timeline()   # list of (t0, t1, fn)
DUR = A.dur
NFR = int(round(DUR * FPS))


def draw(c, t):
    fn = None
    for (t0, t1, f) in TL:
        if t0 <= t < t1:
            fn = f
            break
    if fn is None:
        c.begin(t)
        return c.finish()
    r = fn(c, t, t - t0, t1 - t0)
    return c.finish(**(r or {}))


if __name__ == '__main__':
    c = Canvas()
    mode = sys.argv[1]
    if mode == 'stills':
        name = sys.argv[2]
        ts = [float(x) for x in sys.argv[3:]]
        ims = []
        for t in ts:
            t0 = time.time()
            im = draw(c, t).copy()
            ms = (time.time() - t0) * 1000
            cv2.putText(im, f'{t:.2f}s {ms:.0f}ms', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            ims.append(im)
        cols = 2 if len(ims) > 1 else 1
        while len(ims) % cols:
            ims.append(np.zeros_like(ims[0]))
        rows = [np.hstack(ims[i:i + cols]) for i in range(0, len(ims), cols)]
        sheet = np.vstack(rows)
        sheet = cv2.resize(sheet, (sheet.shape[1] // 2, sheet.shape[0] // 2), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{OUT}/sketchbook_{name}.jpg', sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    elif mode == 'chunk':
        i, n = int(sys.argv[2]), int(sys.argv[3])
        f0 = NFR * i // n
        f1 = NFR * (i + 1) // n
        if len(sys.argv) > 5:
            f0, f1 = int(sys.argv[4]), int(sys.argv[5])
        os.makedirs(f'{OUT}/sketchbook', exist_ok=True)
        out = f'{OUT}/sketchbook/chunk_{i:03d}.mp4'
        tmp = f'{OUT}/sketchbook/tmp_{i:03d}.mp4'
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
               '-c:v', 'libx264', '-preset', os.environ.get('PRESET', 'veryfast'), '-crf', os.environ.get('CRF', '19'), '-pix_fmt', 'yuv420p',
               '-g', '60', '-threads', '1'] + (['-maxrate', os.environ['MAXRATE'], '-bufsize', os.environ.get('BUFSIZE', '10M')] if os.environ.get('MAXRATE') else []) + [tmp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(f0, f1):
            im = draw(c, f / FPS)
            p.stdin.write(im.tobytes())
            if (f - f0) % 150 == 0:
                print(f'chunk {i}: {f - f0}/{f1 - f0} {time.time() - t0:.0f}s', flush=True)
        p.stdin.close()
        rc = p.wait()
        if rc == 0:
            os.replace(tmp, out)
        print(f'chunk {i} done rc={rc} {time.time() - t0:.0f}s', flush=True)
        sys.exit(rc)
