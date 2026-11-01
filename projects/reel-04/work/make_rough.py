"""Rough cut (no grade, no effects): picture from timeline.py, music + quiet room sound.

python3 work/make_rough.py [--w 540]   ->  out/rough_v2.mp4
One ffmpeg input per piece (never long trim chains). Audio is cut from WAV decoded from
the start of each clip (never by seeking the phone MP4's AAC).
"""
import argparse, os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import timeline as T

ap = argparse.ArgumentParser(); ap.add_argument("--w", type=int, default=540)
a = ap.parse_args()
W, H = a.w, a.w * 16 // 9
os.makedirs("work/pieces", exist_ok=True); os.makedirs("work/audio", exist_ok=True)
os.makedirs("out", exist_ok=True)
SR = 48000

def wav(clip):
    p = f"work/audio/{clip}.wav"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"raw/{clip}.mp4", "-vn",
                        "-ar", str(SR), "-ac", "2", p], check=True)
    return sf.read(p)[0]

parts, room = [], []
for i, s in enumerate(T.shots()):
    out = f"work/pieces/r{i:02d}.mp4"
    vf = f"setpts=PTS/{s['speed']}," if s["speed"] != 1 else ""
    vf += f"scale={W}:{H},fps={T.FPS},setsar=1"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['src_in']:.3f}",
                    "-t", f"{s['src_dur'] + 0.5:.3f}", "-i", f"raw/{s['clip']}.mp4",
                    "-vf", vf, "-frames:v", str(s["frames"]), "-an",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out], check=True)
    parts.append(out)
    y = wav(s["clip"])
    a0 = int(s["src_in"] * SR); n_src = int(round(s["src_dur"] * SR))
    seg = y[a0:a0 + n_src]
    n_out = int(round(s["frames"] / T.FPS * SR))
    if s["speed"] != 1:  # simple resample for the slowed shot
        idx = np.linspace(0, len(seg) - 1, n_out).astype(int); seg = seg[idx]
    seg = np.pad(seg, ((0, max(0, n_out - len(seg))), (0, 0)))[:n_out]
    f = min(len(seg) // 2, int(0.01 * SR))  # 10 ms de-click
    if f:
        ramp = np.linspace(0, 1, f)[:, None]; seg[:f] *= ramp; seg[-f:] *= ramp[::-1]
    room.append(seg)
    print(f"{i+1:2d} {s['start']:6.2f}-{s['end']:6.2f}  {s['clip']:5s} {s['src_in']:.2f}  {s['note']}")

open("work/pieces/list.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                "work/pieces/list.txt", "-c", "copy", "work/rough_video.mp4"], check=True)

room = np.concatenate(room)
m, _ = sf.read("work/audio/m3_moody.wav")
L = len(room)
m = np.pad(m, ((0, max(0, L - len(m))), (0, 0)))[:L]
mix = 0.9 * m + 0.35 * room
fade = int(1.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= max(1.0, np.abs(mix).max() / 0.89)
sf.write("work/rough_mix.wav", mix, SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/rough_video.mp4", "-i", "work/rough_mix.wav",
                "-vf", f"fade=t=in:st=0:d=0.8,fade=t=out:st={T.length()-1.5:.2f}:d=1.5",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "out/rough_v2.mp4"], check=True)
print("out/rough_v2.mp4", T.length(), "s")
