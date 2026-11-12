"""Render one cut from start to finish.

    python build.py sketchbook path/to/song.mp3
    python build.py in_light   path/to/song.mp3  [--jobs 2] [--chunks 16]

Renders the frames in chunks (several at once), joins them and adds the song.
Result: out/until_further_notice_<cut>.mp4
"""
import sys, os, subprocess, argparse
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument('cut', choices=['sketchbook', 'in_light'])
ap.add_argument('song')
ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2)))
ap.add_argument('--chunks', type=int, default=16)
a = ap.parse_args()

env = dict(os.environ)
env.setdefault('CRF', '22')
env.setdefault('PRESET', 'medium')
env.setdefault('MAXRATE', '6000k')
env.setdefault('BUFSIZE', '12M')
out = f'{ROOT}/out/{a.cut}'
os.makedirs(out, exist_ok=True)
if a.cut == 'in_light':      # compute the simulations once, before the workers start
    subprocess.run([sys.executable, f'{ROOT}/in_light/sims.py'], check=True)


def chunk(i):
    r = subprocess.run([sys.executable, f'{ROOT}/{a.cut}/render.py', 'chunk', str(i), str(a.chunks)], env=env, capture_output=True, text=True)
    print(f'chunk {i + 1}/{a.chunks} ' + ('done' if r.returncode == 0 else 'FAILED\n' + r.stderr[-2000:]), flush=True)
    return r.returncode


with ThreadPoolExecutor(a.jobs) as ex:
    if any(ex.map(chunk, range(a.chunks))):
        sys.exit('a chunk failed')
with open(f'{out}/list.txt', 'w') as f:
    for i in range(a.chunks):
        f.write(f"file 'chunk_{i:03d}.mp4'\n")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{out}/list.txt', '-c', 'copy', f'{out}/video_only.mp4'], check=True)
final = f'{ROOT}/out/until_further_notice_{a.cut}.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{out}/video_only.mp4', '-i', a.song, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', final], check=True)
print(final)
