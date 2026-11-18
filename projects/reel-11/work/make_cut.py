"""Rough cut for reel-11 from work/cut_plan.json -> out/reel-11-rough-v1.mp4.

Picture: each piece is its own ffmpeg input (-ss before -i), scaled to 1080x1920, 30 fps, exact frame count.
Sound: cut sample-accurately from WAVs decoded from the start of each source (never by seeking the MP4).
Her clip is the joined 4-part master work/her_full.mp4 + work/audio/her_full.wav (see RENDER.md).
Run from the project folder.
"""
import json
import subprocess
import numpy as np
import soundfile as sf

plan = json.load(open("work/cut_plan.json"))
FPS = plan["fps"]
SR = 48000
VIDEO = {"her_full": "work/her_full.mp4", "me_2": "raw/me_2.mp4", "me_3a": "raw/me_3a.mp4",
         "me_3b": "raw/me_3b.mp4", "me_3d": "raw/me_3d.mp4"}

pieces, audio = [], []
for k, g in enumerate(plan["segments"]):
    n = int(round((g["src_out"] - g["src_in"]) * FPS))
    out = f"work/cut/piece_{k:02d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{g['src_in']:.4f}", "-i", VIDEO[g["clip"]],
                    "-vf", "scale=1080:1920:flags=lanczos,fps=30,setsar=1", "-frames:v", str(n), "-an",
                    "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], check=True)
    got = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_packets", "-show_entries",
                              "stream=nb_read_packets", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
    assert got == n, (out, got, n)
    x, sr = sf.read(f"work/audio/{g['clip']}.wav")
    assert sr == SR
    a = int(round(g["src_in"] * SR))
    seg = x[a:a + int(round(n / FPS * SR))]
    seg = np.pad(seg, (0, int(round(n / FPS * SR)) - len(seg)))
    # 5 ms fades so no cut clicks (cuts are already in quiet spots)
    f = int(0.005 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    audio.append(seg)
    pieces.append(out)
    print(k, g["clip"], n, "frames")

mix = np.concatenate(audio)
sf.write("work/audio/rough_v1.wav", mix, SR, subtype="PCM_24")
with open("work/cut/list.txt", "w") as fh:
    for p in pieces:
        fh.write(f"file '{p.split('/')[-1]}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/cut/list.txt",
                "-i", "work/audio/rough_v1.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20",
                "-preset", "medium", "-g", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                "out/reel-11-rough-v1.mp4"], check=True)
print("total", len(mix) / SR, "s")
