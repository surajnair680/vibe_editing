"""Word times in edit time -> work/words_cut.json and work/word_times_edit.txt (for the beat sheet and scene code)."""
import json
plan = json.load(open("work/cut_plan.json"))
WJ = {"raw/VID20261007161237.mp4": "work/short/words.json", "raw/1000097826.mp4": "work/main/words.json"}
src = {k: (lambda w: w["words"] if isinstance(w, dict) else w)(json.load(open(v))) for k, v in WJ.items()}
out = []
for s in plan["segments"]:
    for x in src[s["src"]]:
        if x["s"] >= s["src_in"] - 0.02 and x["e"] <= s["src_out"] + 0.05:
            out.append({"w": x["w"], "s": round(x["s"] - s["src_in"] + s["edit_in"], 3),
                        "e": round(min(x["e"], s["src_out"]) - s["src_in"] + s["edit_in"], 3)})
json.dump(out, open("work/words_cut.json", "w"), indent=0)
with open("work/word_times_edit.txt", "w") as f:
    for x in out:
        f.write(f"{x['s']:6.2f}  {x['w']}\n")
print(len(out), "words;", " ".join(f"{x['w']}@{x['s']:.2f}" for x in out))
