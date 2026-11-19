"""Map Scribe words (joined source times, work/words_full.json) to edit times of the current cut plan
(speed-aware) -> work/words_edit.json. Run from the project folder."""
import json
plan = json.load(open("work/cut_plan.json"))
W = json.load(open("work/words_full.json"))
out = []
for w in W:
    for g in plan["segments"]:
        if g["src_in"] - 0.02 <= w["s"] < g["src_out"]:
            sp = g.get("speed", 1.0)
            out.append(dict(w=w["w"], s=round(g["edit_in"] + (w["s"] - g["src_in"]) / sp, 3),
                            e=round(g["edit_in"] + (min(w["e"], g["src_out"]) - g["src_in"]) / sp, 3), x=sp))
            break
json.dump(out, open("work/words_edit.json", "w"), ensure_ascii=False, indent=0)
line, t0 = [], None
for w in out:
    if w["s"] < 24.7:
        continue
    if t0 is None: t0 = w["s"]
    line.append(w["w"])
    if w["w"][-1] in "।?.!," and len(line) > 3 or w["w"][-1] in "।?.!":
        print(f"{t0:6.2f}-{w['e']:6.2f} x{w['x']}  {' '.join(line)}"); line, t0 = [], None
if line: print(f"{t0:6.2f}  {' '.join(line)}")
