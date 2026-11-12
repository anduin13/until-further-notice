# Until Further Notice — two music videos drawn in code

Two complete videos for the same song, with every frame drawn by Python. No image
generation and no footage: just lines, points and fills, timed to the music.

| Cut | Folder | What it is |
|---|---|---|
| **Sketchbook** | `sketchbook/` | Pencil line on paper with flat, grainy print colour; an 80s comic-and-poster look. |
| **In light** | `in_light/` | Glowing lines on darkness. Each lyric line is paired with a classic algorithm that does what the line says (a traffic model, a Galton board run backwards, Game of Life, a flow field, quicksort, a maze built then solved, fireflies falling into step, double pendulums, and so on). |

The videos themselves are not in this repository (too large). 
Links: 

Sketchbook version: https://youtu.be/J86AUUIsn1Y 

Light version: https://youtu.be/9eWxpWKkhqc?si=SPEwD6Qj8WzNv0UW 

The song is on Suno: https://suno.com/s/R5lbZtSwFFDPE0v0. Download it and save it as audio/Until_Further_Notice.mp3.

## Layout

```
common/engine.py   shared: beat grid and audio lookups, pencil engine, fonts, easing
sketchbook/        first cut: motifs.py (reusable drawings), sc_*.py (scenes), render.py
in_light/          second cut: lum.py (light engine), sims.py (simulations), v_*.py (scenes), render.py
data/              beat grid, energy curves and word timings extracted from the song
prepare.py         song -> data/ and audio/
build.py           render a whole cut and add the song
```

## Running it

You need Python 3.10+, `ffmpeg` on the path, the cairo library, and the song as an audio file
(not included).

```
pip install -r requirements.txt
python prepare.py path/to/song.mp3            # once: writes audio/*.wav, refreshes data/*.json
python build.py in_light   path/to/song.mp3   # -> out/until_further_notice_in_light.mp4
python build.py sketchbook path/to/song.mp3   # -> out/until_further_notice_sketchbook.mp4
```

A full render is 7,895 frames at 1920x1080 and takes roughly ten minutes on two cores.
To look at single moments instead (times in seconds; writes a contact sheet to `out/`):

```
python in_light/render.py stills test 68.3 129.3 190.4
python sketchbook/render.py stills test 61.7 122.3 190.4
```

### Fonts

*In light* only uses the Hershey plotter fonts, which come with the `Hershey-Fonts` package.

*Sketchbook* also needs three font files, looked up by file name in `./fonts` and the usual
system font folders:

- `Inter-BlackItalic.otf` (Inter)
- `texgyreadventor-bold.otf` and `texgyreheroscn-bold.otf` (TeX Gyre)

On Debian or Ubuntu: `apt install fonts-inter tex-gyre`. Otherwise download them and drop
the files into `fonts/` (ignored by git).

## How it works

- Every frame is a pure function of time, so chunks render independently and in parallel.
- Cuts sit on the song's bar lines (`B(n)` is the time of bar *n*); lettering lands on the
  sung words, using timings from a speech-to-text pass (`data/words.json`).
- The scenes are written for this song: bar numbers and word times are in the scene files.
  Pointing it at a different track will run, but nothing will line up.
- *In light* precomputes its simulations once into `cache/`.

## Credits

Song, lyrics and concept: Andres Guadamuz. Code written with Claude (Anthropic).

## Licence

Creative Commons Zero v1.0 Universal
