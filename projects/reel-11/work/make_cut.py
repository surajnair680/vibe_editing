"""Rough cut for reel-11 from work/cut_plan.json -> out/reel-11-rough-<ver>.mp4.

Picture: each piece is its own ffmpeg input (-ss before -i), scaled to 1080x1920, 30 fps, exact frame count.
Sound: cut sample-accurately from WAVs decoded from the start of each source (never by seeking the MP4).
Her clip is the joined 4-part master work/her_full.mp4 + work/audio/her_full.wav (see RENDER.md).

Part seam (rough v2 fix): the phone split me_3b (and 3c, 3d) with its audio starting 0.2604 s BEFORE its picture
(negative pts). A normal decode drops that pre-roll, which chopped "sitting on". The segment that runs to the end of
me_3a and the next one that starts at 0 in me_3b are built as ONE piece: picture = 3a to its real end + 3b,
audio = 3a WAV to its end + work/audio/me_3b_all.wav (decoded from the raw AAC stream, pre-roll kept), no fades at
the seam. Picture frames are fitted to the audio length (the seam lands within about 16 ms).

Usage: python3 work/make_cut.py v2      (run from the project folder)
"""
import json
import subprocess
import sys
import numpy as np
import soundfile as sf

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
plan = json.load(open("work/cut_plan.json"))
FPS = plan["fps"]
SR = 48000
VIDEO = {"her_full": "work/her_full.mp4", "me_2": "raw/me_2.mp4", "me_3a": "raw/me_3a.mp4",
         "me_3b": "raw/me_3b.mp4", "me_3d": "raw/me_3d.mp4"}
PREROLL = {"me_3b": 0.2604}      # audio before picture start, measured by cross-correlation (work/seam/)
FADE = int(0.005 * SR)


def render(src, ss, n, out):
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.4f}", "-i", src,
           "-vf", "scale=1080:1920:flags=lanczos,fps=30,setsar=1", "-an",
           "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p"]
    if n is not None:
        cmd += ["-frames:v", str(n)]
    subprocess.run(cmd + [out], check=True)
    return int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_packets", "-show_entries",
                               "stream=nb_read_packets", "-of", "csv=p=0", out],
                              capture_output=True, text=True).stdout)


def wav(clip):
    x, sr = sf.read(f"work/audio/{clip}.wav")
    assert sr == SR
    return x


segs = plan["segments"]
pieces, audio, k = [], [], 0
while k < len(segs):
    g = segs[k]
    out = f"work/cut/piece_{len(pieces):02d}.mp4"
    nxt = segs[k + 1] if k + 1 < len(segs) else None
    if g["clip"] == "me_3a" and nxt and nxt["clip"] == "me_3b" and nxt["src_in"] == 0:
        # continuous seam piece
        a3 = wav("me_3a")[int(round(g["src_in"] * SR)):]
        b3 = wav("me_3b_all")[:int(round((PREROLL["me_3b"] + nxt["src_out"]) * SR))]
        seg = np.concatenate([a3, b3])
        n_total = int(round(len(seg) / SR * FPS))
        n_b = int(round(nxt["src_out"] * FPS))
        n_a = n_total - n_b
        tmp_a, tmp_b = "work/cut/_seam_a.mp4", "work/cut/_seam_b.mp4"
        assert render(VIDEO["me_3a"], g["src_in"], n_a, tmp_a) == n_a
        assert render(VIDEO["me_3b"], 0.0, n_b, tmp_b) == n_b
        with open("work/cut/_seam.txt", "w") as fh:
            fh.write("file '_seam_a.mp4'\nfile '_seam_b.mp4'\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/cut/_seam.txt",
                        "-c", "copy", out], check=True)
        n = n_total
        seg = np.pad(seg, (0, max(0, int(round(n / FPS * SR)) - len(seg))))[:int(round(n / FPS * SR))]
        print(len(pieces), "seam 3a+3b", n_a, "+", n_b, "frames; 3b picture starts",
              round(n_a / FPS - (len(a3) / SR + PREROLL["me_3b"]), 4), "s off its audio")
        k += 2
    else:
        n = int(round((g["src_out"] - g["src_in"]) * FPS))
        assert render(VIDEO[g["clip"]], g["src_in"], n, out) == n
        x = wav(g["clip"])
        a = int(round(g["src_in"] * SR))
        seg = x[a:a + int(round(n / FPS * SR))]
        seg = np.pad(seg, (0, int(round(n / FPS * SR)) - len(seg)))
        print(len(pieces), g["clip"], n, "frames")
        k += 1
    seg = seg.copy()
    seg[:FADE] *= np.linspace(0, 1, FADE)      # 5 ms fades only at real cuts (both ends are quiet)
    seg[-FADE:] *= np.linspace(1, 0, FADE)
    audio.append(seg)
    pieces.append(out)

mix = np.concatenate(audio)
sf.write(f"work/audio/rough_{VER}.wav", mix, SR, subtype="PCM_24")
with open("work/cut/list.txt", "w") as fh:
    for p in pieces:
        fh.write(f"file '{p.split('/')[-1]}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/cut/list.txt",
                "-i", f"work/audio/rough_{VER}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20",
                "-preset", "medium", "-g", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                f"out/reel-11-rough-{VER}.mp4"], check=True)
print("total", len(mix) / SR, "s")
