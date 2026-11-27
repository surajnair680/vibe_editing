"""v3 style sample: the drinks / pizza beat (edit 29.97 to 33.53 s). python3 work/build3/sample.py <t> [<t> ...]"""
import os, sys
sys.path.insert(0, "/home/user/vibe_editing/projects/reel-14/work/build3")
sys.path.insert(0, "/home/user/vibe_editing/projects/reel-14/work/build2")
sys.path.insert(0, "/home/user/vibe_editing/projects/reel-14/work/build")
os.chdir("/home/user/vibe_editing/projects/reel-14")
import numpy as np
from PIL import Image
import scene2, fx2, motion_kit
import vox
from vox import W, H, ease, span, twos

PIZZA = "assets/codex/pizza.png"
DRINKS = "assets/codex/drinks.png"
T_DRINKS, T_PIZZA, T_NO, T_X = 30.63, 32.17, 32.45, 30.90     # landing times from the words (drinks, pizza)


def caption(img, text, t0, t):
    p = ease(span(twos(t), t0, t0 + .25))
    if p <= 0: return img
    s = vox.strip(text, 64, bg=(20, 16, 16), fg=vox.BONE, seed=hash(text) % 999, font_path=vox.F_CAP, padx=26, pady=14)
    return vox.paste(img, s, W / 2 - 40, 300 - (1 - p) * 40, rot=-1.0, shadow=0.3)


def frame(t):
    f = scene2.fr(t)
    base = next(scene2.base_frames(f, 1))
    bg = fx2.vignette(fx2.bg_red(t), 0.40)
    tt = twos(t)
    # drinks: drop in from above, marker X
    if os.path.exists(DRINKS) and tt >= T_DRINKS - .35:
        p = ease(span(tt, T_DRINKS - .35, T_DRINKS))
        bg = vox.paste(bg, vox.cutout(DRINKS, 430, seed=11), 300, 610 - (1 - p) * 500, rot=6 - 4 * p)
        if tt >= T_X:
            bg = vox.marker_x(bg, 300, 610, 360, span(tt, T_X, T_X + .5), seed=4)
    # pizza: drop in, NO stamp slams
    if tt >= T_PIZZA - .35:
        p = ease(span(tt, T_PIZZA - .35, T_PIZZA))
        bg = vox.paste(bg, vox.cutout(PIZZA, 560, seed=12), 740, 590 - (1 - p) * 600, rot=-7 + 3 * p)
        if tt >= T_NO:
            q = ease(span(tt, T_NO, T_NO + .17))
            bg = vox.paste(bg, vox.stamp("NO", 210, seed=5), 760, 630, rot=-12, scale=1.6 - .6 * q, shadow=0)
    img = scene2.his_layer(bg, base, f, t)
    img = caption(img, "you skip the drinks," if t < 31.19 else "you say no to the pizza,", 29.97 if t < 31.19 else 31.19, t)
    return motion_kit.grain(np.ascontiguousarray(img), 0.08, seed=f)


if __name__ == "__main__" and sys.argv[1] != "clip":
    os.makedirs("out/stills/v3", exist_ok=True)
    for a in sys.argv[1:]:
        Image.fromarray(frame(float(a))).save(f"out/stills/v3/sample_{float(a):06.2f}.png")


def render_clip(a, b, out):
    """the sample range with voice + paper sounds (peaks on their frames)."""
    import subprocess, soundfile as sf
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30",
                            "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", "work/render/v3_sample_v.mp4"],
                           stdin=subprocess.PIPE)
    for f in range(scene2.fr(a), scene2.fr(b)):
        enc.stdin.write(np.ascontiguousarray(frame(f / 30)).tobytes())
    enc.stdin.close(); enc.wait()
    voice, sr = sf.read("work/audio/_stem_voice.wav", always_2d=True)
    seg = voice[int(a * sr):int(b * sr)].copy()
    if seg.shape[1] == 1: seg = np.repeat(seg, 2, 1)
    def put(name, t, db):
        s, r2 = sf.read(f"assets/sfx/openverse/vox/{name}.wav", always_2d=True)
        env = np.convolve(np.abs(s).mean(1), np.ones(240) / 240, "same"); pk = int(np.argmax(env))
        i = int((t - a) * sr) - pk; s = s[max(0, -i):]; i = max(0, i); n = min(len(s), len(seg) - i)
        seg[i:i + n] += s[:n, :2] * 10 ** (db / 20)
    for name, t, db in [("paper-01", T_DRINKS, -10), ("marker-01", T_X + .2, 6), ("paper-02", T_PIZZA, -10),
                        ("thud-03", T_NO + .08, -16), ("paper-03", T_NO + .08, -8)]:
        put(name, t, db)
    sf.write("work/render/v3_sample.wav", seg, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/render/v3_sample_v.mp4", "-i", "work/render/v3_sample.wav",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", out], check=True)

if __name__ == "__main__" and sys.argv[1] == "clip":
    render_clip(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
