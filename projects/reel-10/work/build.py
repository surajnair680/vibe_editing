"""reel-10 build: hook (work/hook/hook.py) + 14 beat-synced shots (work/beats.py), grade, grain, song.

    python3 work/build.py stills            -> out/stills_vN/ (every 2.5 s) + contact sheet
    python3 work/build.py draft             -> out/reel-10_draft.mp4 (540x960, crf 23, song)
    python3 work/build.py master            -> out/reel-10_master.mp4 (1080x1920, crf 14) + mix
Env: VER=v1 (stills folder name).
"""
import cv2, numpy as np, subprocess, sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "work")); sys.path.insert(0, os.path.join(ROOT, "work", "hook"))
from beats import SHOTS, END
import hook as hk
from look import Grain

W, H, FPS = 1080, 1920, 30
OUT = os.path.join(ROOT, "out")
SONG_IN = hk.SONG_IN
HOOK_END = hk.DROP + hk.BREAK            # hook.py draws until the breakout has settled
TARGET_RG, TARGET_BG = 1.12, 0.79         # colour balance most shots already share
MATCH = 0.7
PUSH = 0.045                              # slow push-in per shot (alternating centre drift)


def curve_lut():
    x = np.arange(256) / 255.0
    y = x + 0.06 * np.sin(2 * np.pi * (x - 0.5)) * (x * (1 - x)) * 4        # gentle S
    y = 0.025 + y * (1 - 0.025)                                              # slightly lifted blacks
    y = np.where(y > 0.85, 0.85 + (y - 0.85) * 0.7, y)                       # highlight roll-off
    return np.clip(y * 255, 0, 255).astype(np.uint8)


LUT = curve_lut()


def grade_matrix(sample):
    """3x4 matrix: per-shot balance toward the shared warm look, plus saturation 0.92."""
    f = sample.astype(np.float32); l = f.mean(2); m = (l > 50) & (l < 200)
    b, g, r = [f[..., c][m].mean() for c in range(3)]
    gr = (TARGET_RG / (r / g)) ** MATCH; gb = (TARGET_BG / (b / g)) ** MATCH
    gain = np.diag([gb, 1.0, gr]).astype(np.float32)
    s = 0.92; lw = np.float32([0.114, 0.587, 0.299])
    sat = (1 - s) * np.outer(np.ones(3), lw) + s * np.eye(3)
    M = (sat @ gain).astype(np.float32)
    return np.hstack([M, np.zeros((3, 1), np.float32)])


def cover(img, tw, th):
    return hk.cover(img, tw, th)


class Reel:
    def __init__(self):
        self.hook = hk.Hook()
        self.grain = self.hook.grain
        self.cache = {}

    def shot(self, i):
        if i not in self.cache:
            self.cache = {}
            a, b, src, ss, _ = SHOTS[i]
            fr = hk.read_frames(f"raw/{src}.mp4", ss, b - a + 0.15)
            mid = fr[len(fr) // 2]
            self.cache[i] = (fr, grade_matrix(mid))
        return self.cache[i]

    def frame(self, t):
        n = int(round(t * FPS))
        if t < HOOK_END:
            return self.hook.frame(t)
        i = max(k for k, s in enumerate(SHOTS) if s[0] <= t + 1e-6)
        a, b, src, ss, _ = SHOTS[i]
        fr, M = self.shot(i)
        j = min(int(round((t - a) * FPS)), len(fr) - 1)
        img = cover(fr[j], W, H)
        # slow push; shot 0 continues the breakout (starts at 1.0), others alternate a small drift
        k = (t - a) / (b - a)
        z = 1.0 + PUSH * k
        dx = (0 if i == 0 else (12 if i % 2 else -12)) * k
        A = cv2.getRotationMatrix2D((W / 2 + dx, H / 2), 0, z)
        img = cv2.warpAffine(img, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = cv2.transform(img, M)
        img = cv2.LUT(img, LUT)
        if i == len(SHOTS) - 1:   # last 0.5 s fades to black with the music
            fade = min(1.0, max(0.0, (END - t) / 0.5))
            img = (img * fade).astype(np.uint8)
        return self.grain(img, n)


def mix(path_wav):
    """Song only (user: no SFX): from SONG_IN, 30 ms fade in, fade out over the last shot, -14 LUFS-ish."""
    wav = os.path.join(ROOT, "work", "audio", "thebox.wav")
    last = SHOTS[-1][0]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{SONG_IN}", "-t", f"{END:.3f}", "-i", wav,
                    "-af", f"afade=t=in:d=0.03,afade=t=out:st={last:.3f}:d={END - last:.3f},"
                           "loudnorm=I=-14:TP=-1.5:LRA=11:linear=true",
                    "-ar", "48000", path_wav], check=True)


def encode(r, path, scale=1.0, crf=14):
    w, h = int(W * scale), int(H * scale)
    tmp = path + ".pic.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(int(round(END * FPS))):
        f = r.frame(n / FPS)
        if scale != 1.0:
            f = cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    wav = path + ".mix.wav"; mix(wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", path], check=True)
    os.remove(tmp)
    os.replace(wav, os.path.join(ROOT, "work", "audio", "mix.wav"))


def stills(r, ver):
    d = os.path.join(OUT, f"stills_{ver}"); os.makedirs(d, exist_ok=True)
    ts = [k * 2.5 for k in range(int(END / 2.5) + 1)]
    tiles = []
    for t in ts:
        f = r.frame(t)
        cv2.imwrite(os.path.join(d, f"t_{t:05.2f}.png"), f)
        s = cv2.resize(f, (270, 480), interpolation=cv2.INTER_AREA)
        cv2.rectangle(s, (0, 0), (84, 26), (0, 0, 0), -1)
        cv2.putText(s, f"{t:.1f}s", (4, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        tiles.append(s)
    while len(tiles) % 7: tiles.append(np.zeros_like(tiles[0]))
    sheet = np.vstack([np.hstack(tiles[i:i + 7]) for i in range(0, len(tiles), 7)])
    cv2.imwrite(os.path.join(OUT, f"contact_{ver}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])


if __name__ == "__main__":
    r = Reel(); ver = os.environ.get("VER", "v1")
    for a in sys.argv[1:] or ["stills"]:
        if a == "stills": stills(r, ver)
        elif a == "draft": encode(r, os.path.join(OUT, "reel-10_draft.mp4"), 0.5, 23)
        elif a == "master": encode(r, os.path.join(OUT, "reel-10_master.mp4"), 1.0, 14)
    print("ok")
