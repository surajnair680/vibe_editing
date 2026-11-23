"""Motion in the lower half of the frame (mic hand) around every line's in-point, to keep the mic being
raised out of the cut. Prints, per line, the motion per frame from the planned in-point to the first word."""
import json, subprocess, numpy as np
P = json.load(open("work/parts.json")); plan = json.load(open("work/cut_plan.json"))
W = json.load(open("work/words_full.json"))
def frames(t0, t1):
    i = max(k for k, o in enumerate(P["offsets"]) if t0 >= o - 1e-6); lt = t0 - P["offsets"][i]
    n = int(round((t1 - t0) * 30)) + 1
    d = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{lt:.3f}", "-i", P["parts"][i], "-frames:v", str(n), "-vf",
                        "crop=1080:900:0:1020,scale=108:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(d, np.uint8).reshape(-1, 90, 108).astype(float)
for g in plan["segments"]:
    a = g["src_in"]; w = [x for x in W if x["s"] >= a - 0.01][0]["s"]
    f = frames(a - 0.2, w + 0.1); m = np.abs(np.diff(f, axis=0)).mean((1, 2))
    print(f"in {a:6.2f} word {w:6.2f} |", " ".join(f"{v:4.1f}" for v in m), "|", g["text"][:28])
