"""Join the three parts' audio into one timeline -> work/audio/full.wav (mono 48 kHz).
Parts are separate takes (no line crosses a seam). Part p sits at OFFSET[p] (= sum of earlier video lengths,
36.0 / 36.0 / 13.1 s), its audio placed on its own timestamps (aresample first_pts=0 pads to pts 0) and padded/trimmed to
the part's video length, so global time = OFFSET + local video time. Run from the project folder."""
import subprocess, json
import numpy as np, soundfile as sf
SR = 48000
PARTS = ["raw/ep0_part1.mp4", "raw/ep0_part2.mp4", "raw/ep0_part3.mp4"]
out, offs, t = [], [], 0.0
for p in PARTS:
    pr = lambda s, e: float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", s, "-show_entries", f"stream={e}",
                                             "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
    vd, st = pr("v", "duration"), pr("a", "start_time")
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-af", "aresample=async=1:first_pts=0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32).astype(float)
    n = int(round(vd * SR)); # aresample first_pts=0 pads the gap before the first audio pts (start_time and dropped priming)
    a = np.pad(a, (0, max(0, n - len(a))))[:n]
    out.append(a); offs.append(t); t += vd
    print(p, "video", vd, "audio start", st, "-> offset", offs[-1])
sf.write("work/audio/full.wav", np.concatenate(out), SR, subtype="FLOAT")
json.dump({"parts": PARTS, "offsets": offs, "length": t}, open("work/parts.json", "w"), indent=1)
print("total", t)
