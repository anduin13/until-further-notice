"""Turn the song into the data both videos are drawn from.

    python prepare.py path/to/Until_Further_Notice.mp3

Writes audio/mono22.wav and audio/stereo22.wav (not committed) and data/audio.json and
data/beats.json (beat grid, energy curves, a 24-band spectrum per frame). Needs ffmpeg and librosa.
"""
import sys, os, json, subprocess
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 30


def main(src):
    import librosa
    os.makedirs(f'{ROOT}/audio', exist_ok=True)
    os.makedirs(f'{ROOT}/data', exist_ok=True)
    for ch, name in ((1, 'mono22'), (2, 'stereo22')):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', str(ch), '-ar', '22050', f'{ROOT}/audio/{name}.wav'], check=True)
    y, sr = librosa.load(f'{ROOT}/audio/mono22.wav', sr=22050)
    dur = len(y) / sr
    hop = 256
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=hop, units='time', tightness=200)
    tempo = float(np.atleast_1d(tempo)[0])
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=hop, n_mels=64, fmax=11000)
    fr_t = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
    low, mid, high = S[0:5].sum(0), S[8:30].sum(0), S[40:64].sum(0)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    T = np.arange(int(dur * FPS) + 2) / FPS

    def res(x):
        return np.interp(T, fr_t[:len(x)], x)

    def norm(x):
        x = np.log1p(x / np.percentile(x, 50))
        return np.clip(x / np.percentile(x, 99.5), 0, 1)

    def flux(e):
        le = np.log1p(e / np.median(e))
        return np.maximum(0, np.diff(le, prepend=le[0]))

    def peaknorm(x):
        return np.clip(x / np.percentile(x, 99.7), 0, 1)

    def pool(x):
        out = np.zeros(len(T))
        idx = np.clip((fr_t[:len(x)] * FPS).astype(int), 0, len(T) - 1)
        np.maximum.at(out, idx, x)
        return out

    data = {
        'dur': dur, 'tempo': tempo, 'beats': [float(b) for b in beats],
        'rms': norm(res(rms)).tolist(), 'low': norm(res(low)).tolist(), 'mid': norm(res(mid)).tolist(), 'high': norm(res(high)).tolist(),
        'kick': peaknorm(pool(flux(low))).tolist(), 'snare': peaknorm(pool(flux(mid))).tolist(), 'hat': peaknorm(pool(flux(high))).tolist(),
        'onset': peaknorm(pool(oenv)).tolist(),
    }
    M = librosa.power_to_db(S, ref=np.max)
    bands = np.stack([M[int(i * 64 / 24):int((i + 1) * 64 / 24)].mean(0) for i in range(24)])
    bands = (bands + 70) / 70
    data['spec'] = np.round(np.stack([np.interp(T, fr_t, b) for b in bands]).clip(0, 1).T, 3).tolist()
    json.dump(data, open(f'{ROOT}/data/audio.json', 'w'))
    # extend the tracked beats at a steady period to cover the very start and end
    b = np.array(data['beats'])
    p = np.median(np.diff(b))
    pre, t = [], b[0] - p
    while t > 0:
        pre.append(t)
        t -= p
    post, t = [], b[-1] + p
    while t < dur:
        post.append(t)
        t += p
    json.dump({'beats': pre[::-1] + list(b) + post, 'first_tracked': len(pre)}, open(f'{ROOT}/data/beats.json', 'w'))
    print(f'{dur:.2f} s, {tempo:.1f} bpm, {len(pre) + len(b) + len(post)} beats -> data/audio.json, data/beats.json')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
