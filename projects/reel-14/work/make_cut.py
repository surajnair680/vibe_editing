"""Rough cut for reel-14 from work/cut_plan.json -> out/reel-14-rough-<ver>.mp4 (+ a 720p preview).
Picture: each piece is its own ffmpeg input (-ss before -i) from work/full.mp4 (joined 60 fps source), exact frame
count at 30 fps. Sound: segment 0 (her clip + his reaction) from work/audio/full.wav untouched; his takes cut
sample-accurately from work/audio/full_iso.wav (ElevenLabs isolation, aligned within 1 ms). Her part is matched to
his speech level (speech RMS), then the whole cut peaks at -1.5 dBFS. 5 ms fades at every cut. Copied from reel-13.
Usage: python3 work/make_cut.py v1"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
plan = json.load(open("work/cut_plan.json"))
FPS, SR = plan["fps"], 48000
FADE = int(0.005 * SR)
src = {"iso": sf.read("work/audio/full_iso.wav")[0], "orig": sf.read("work/audio/full.wav")[0]}
os.makedirs("work/cut", exist_ok=True)
pieces, audio = [], []
for k, g in enumerate(plan["segments"]):
    n = int(round((g["src_out"] - g["src_in"]) * FPS))
    out = f"work/cut/piece_{k:02d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{g['src_in']:.4f}", "-i", "work/full.mp4",
                    "-vf", "setpts=PTS-STARTPTS,fps=30,setsar=1", "-an", "-frames:v", str(n), "-c:v", "libx264",
                    "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], check=True)
    got = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_packets", "-show_entries",
                              "stream=nb_read_packets", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
    assert got == n, (k, got, n)
    a = int(round(g["src_in"] * SR)); m = int(round(n / FPS * SR))
    seg = src[g["audio"]][a:a + m].copy(); seg = np.pad(seg, (0, m - len(seg)))
    if k: seg[:FADE] *= np.linspace(0, 1, FADE)
    seg[-FADE:] *= np.linspace(1, 0, FADE)
    audio.append(seg); pieces.append(out)
def speech_rms(x):
    h = SR // 20; f = np.sqrt((x[:len(x) // h * h].reshape(-1, h) ** 2).mean(1)); return np.sqrt(np.mean(f[f > np.percentile(f, 50)] ** 2))
him = np.concatenate(audio[1:]); g0 = speech_rms(him) / speech_rms(audio[0]); audio[0] = audio[0] * g0
mix = np.concatenate(audio)
pk = np.abs(mix).max(); gain = 10 ** (-1.5 / 20) / pk; mix = mix * gain
sf.write(f"work/audio/rough_{VER}.wav", mix, SR, subtype="PCM_24")
with open("work/cut/list.txt", "w") as fh:
    fh.writelines(f"file '{os.path.basename(p)}'\n" for p in pieces)
master = f"out/reel-14-rough-{VER}.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/cut/list.txt", "-i",
                f"work/audio/rough_{VER}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18",
                "-preset", "medium", "-g", "30", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", master], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", master, "-vf", "scale=720:1280", "-c:v", "libx264", "-crf", "23",
                "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                f"out/reel-14-rough-{VER}-preview.mp4"], check=True)
print("pieces", len(pieces), "total", round(len(mix) / SR, 3), "s, her part", round(20 * np.log10(g0), 1), "dB, master gain", round(20 * np.log10(gain), 1), "dB")
