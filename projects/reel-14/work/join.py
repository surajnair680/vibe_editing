"""Join the 5 phone parts into one source (lines run across the p1/p2 and p2/p3 seams).
Picture: work/full.mp4 (stream copy, all parts 60 fps CFR). Sound: work/audio/full.wav, each part decoded from its
start, placed at its audio start_time (4 to 13 ms, no negative pre-roll this time), padded/trimmed to its picture
length, so global time = part offset + local time. Writes work/parts.json. Copied from reel-12. Run from the project."""
import json, subprocess
import numpy as np, soundfile as sf
SR = 48000
parts = [f"raw/part{i}.mp4" for i in range(1, 6)]
out, offs, t = [], [], 0.0
for p in parts:
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration,start_time,nb_frames",
                                      "-of", "json", p], capture_output=True, text=True).stdout)["streams"]
    v = next(s for s in info if s["codec_type"] == "video"); a = next(s for s in info if s["codec_type"] == "audio")
    vd, ast = int(v["nb_frames"]) / 60, float(a["start_time"])
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32)
    x = np.concatenate([np.zeros(int(round(ast * SR)), np.float32), x])
    n = int(round(vd * SR)); x = np.pad(x, (0, max(0, n - len(x))))[:n]
    out.append(x); offs.append(round(t, 4)); t += vd
    print(p, "frames", v["nb_frames"], "video", round(vd, 4), "audio start", ast)
sf.write("work/audio/full.wav", np.concatenate(out), SR, subtype="FLOAT")
with open("work/cut/join.txt", "w") as fh:
    fh.writelines(f"file '../../{p}'\n" for p in parts)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/cut/join.txt", "-an", "-c", "copy",
                "work/full.mp4"], check=True)
json.dump({"parts": parts, "offsets": offs, "length": round(t, 4)}, open("work/parts.json", "w"), indent=1)
print("offsets", offs, "total", round(t, 3))
