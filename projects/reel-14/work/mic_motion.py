"""Motion in the lower half of the frame (mic hand) from 0.2 s before every in-point to the first word, and over
the last 0.3 s of every piece, to keep mic raises / drops out of the cut (copied from reel-13, reads work/full.mp4)."""
import json, subprocess, numpy as np
plan = json.load(open("work/cut_plan.json")); W = json.load(open("work/words_full.json"))
def frames(t0, t1):
    n = int(round((t1 - t0) * 30)) + 1
    d = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-i", "work/full.mp4", "-frames:v", str(n), "-vf",
                        "fps=30,crop=1080:900:0:1020,scale=108:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(d, np.uint8).reshape(-1, 90, 108).astype(float)
for g in plan["segments"][1:]:
    a, b = g["src_in"], g["src_out"]; w = [x for x in W if x["s"] >= a - 0.01][0]["s"]
    m = np.abs(np.diff(frames(a - 0.2, w + 0.1), axis=0)).mean((1, 2))
    m2 = np.abs(np.diff(frames(b - 0.3, b + 0.1), axis=0)).mean((1, 2))
    print(f"in {a:6.2f} w {w:6.2f} |" + " ".join(f"{v:3.0f}" for v in m) + f" || out {b:6.2f} |" + " ".join(f"{v:3.0f}" for v in m2) + " | " + g["text"][:20])
