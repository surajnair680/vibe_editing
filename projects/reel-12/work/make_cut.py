"""Rough cut for reel-12 from work/cut_plan.json -> out/reel-12-rough-<ver>.mp4 (+ a small preview for the chat).

Picture: each piece is its own ffmpeg input (-ss before -i) from the joined source work/full.mp4 (60 fps),
taken to 30 fps with an exact frame count. Sound: cut sample-accurately from WAVs decoded from the start:
her clip (0-24.70) from work/audio/full.wav (original), his lines from work/audio/full_iso.wav (ElevenLabs
voice isolation, aligned within about 1 ms). 5 ms fades at every cut. Usage: python3 work/make_cut.py v1
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
plan = json.load(open("work/cut_plan.json"))
FPS, SR, HIM = plan["fps"], 48000, 24.70
FADE = int(0.005 * SR)
orig, _ = sf.read("work/audio/full.wav"); iso, _ = sf.read("work/audio/full_iso.wav")
os.makedirs("work/cut", exist_ok=True)
pieces, audio = [], []
for k, g in enumerate(plan["segments"]):
    n = int(round((g["src_out"] - g["src_in"]) * FPS))
    out = f"work/cut/piece_{k:02d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{g['src_in']:.4f}", "-i", "work/full.mp4", "-vf",
                    "fps=30,setsar=1", "-an", "-frames:v", str(n), "-c:v", "libx264", "-crf", "14", "-preset",
                    "veryfast", "-pix_fmt", "yuv420p", out], check=True)
    got = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_packets", "-show_entries",
                              "stream=nb_read_packets", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
    assert got == n, (k, got, n)
    src = orig if g["src_out"] <= HIM + 1e-6 else iso
    a = int(round(g["src_in"] * SR)); m = int(round(n / FPS * SR))
    seg = src[a:a + m].copy(); seg = np.pad(seg, (0, m - len(seg)))
    if k: seg[:FADE] *= np.linspace(0, 1, FADE)
    seg[-FADE:] *= np.linspace(1, 0, FADE)
    audio.append(seg); pieces.append(out)
    print(k, n, "frames")
mix = np.concatenate(audio)
sf.write(f"work/audio/rough_{VER}.wav", mix, SR, subtype="PCM_24")
with open("work/cut/list.txt", "w") as fh:
    fh.writelines(f"file '{os.path.basename(p)}'\n" for p in pieces)
master = f"out/reel-12-rough-{VER}.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/cut/list.txt", "-i",
                f"work/audio/rough_{VER}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18",
                "-preset", "medium", "-g", "30", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", master], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", master, "-vf", "scale=720:1280", "-c:v", "libx264", "-crf", "24",
                "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                f"out/reel-12-rough-{VER}-preview.mp4"], check=True)
print("total", round(len(mix) / SR, 3), "s")
