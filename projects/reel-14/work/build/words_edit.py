"""Map the source word times (work/words_full.json) into edit time of the approved rough v1 cut
(work/cut_plan.json) -> work/words_edit.json. Only his words (segment 1 on). Run from the project folder."""
import json
plan = json.load(open("work/cut_plan.json")); W = json.load(open("work/words_full.json"))
out = []
for g in plan["segments"][1:]:
    for w in W:
        if w["s"] >= g["src_in"] - 0.02 and w["s"] < g["src_out"]:
            out.append({"w": w["w"], "s": round(g["edit_in"] + w["s"] - g["src_in"], 3),
                        "e": round(min(g["edit_in"] + w["e"] - g["src_in"], g["edit_in"] + g["src_out"] - g["src_in"]), 3)})
json.dump(out, open("work/words_edit.json", "w"), indent=0)
print(len(out), "words")
print(" ".join(f"{w['w']}@{w['s']:.2f}" for w in out))
