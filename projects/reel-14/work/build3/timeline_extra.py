"""Writes work/timeline_extra.json for the timeline editor page: graphics beats, physique shots, sound effects,
music and captions of the current version (edit times). python3 work/build3/timeline_extra.py"""
import json, os, sys
sys.argv = [sys.argv[0]]
sys.path.insert(0, "/home/user/vibe_editing/projects/reel-14/work/build3")
import scene3 as S
s = S.s
L = round(S.LEN, 3)
it = lambda i, lab, a, b, d="": {"id": i, "label": lab, "start": round(a, 3), "end": round(b, 3), "anchor": "edit", "detail": d}
G = [it("g00", "Her clip (untouched)", 0, S.HIS),
     it("g01", "NORMAL PEOPLE figures", S.HIS, S.P_MIRROR[0]),
     it("g02", "Drinks X, pizza NO stamp", S.P_MIRROR[1], s("and", 33.63)),
     it("g03", "Group chat bubbles", s("and", 33.63), s("So", 36.91)),
     it("g04", "SOMETHING WRONG WITH YOU? form, YES ticked", s("So", 36.91), s("You", 40.25)),
     it("g05", "Bell curve: MOST PEOPLE crowd, YOU dot", s("You", 40.25), s("Success", 42.62)),
     it("g06", "Dictionary 'abnormal' + Steve Jobs", s("Success", 42.62), s("Successful", 44.89)),
     it("g07", "Curve: OUTLIERS Musk + Arnold on the right", s("Successful", 44.89), s("Which", 48.95)),
     it("g08", "Receipt: the price", s("Which", 48.95), S.P_PAIN[0]),
     it("g09", "MOST PEOPLE STOP HERE line", S.P_PULL[1], s("That's", 56.82)),
     it("g10", "BALANCE scale wobbles", s("That's", 56.82), S.SEC_CREAM[0]),
     it("g11", "Cream section: EVERYBODY CAN DO IT, NO VALUE", S.SEC_CREAM[0], s("It's", 65.25)),
     it("g12", "Report cards, the A crossed out", s("It's", 65.25), S.SEC_CREAM[1]),
     it("g13", "Scale tears in half", S.SEC_CREAM[1], S.P_CLOSE[0]),
     it("g14", "THE PROBLEM tape", S.P_CLOSE[1], 73.15),
     it("g15", "Progress bar into UNCOMFORTABLE", 73.15, S.P_INCL[0]),
     it("g16", "Sisyphus statue", s("That", 76.87), S.P_FLEX[0]),
     it("g17", "Self-made man statue", S.P_FLEX[1], S.P_DUMB[0]),
     it("g18", "Sofa, COMFORT, crawling figures", S.P_DUMB[1], S.P_OUT[0]),
     it("g19", "Judging eyes, JUDGING", S.P_OUT[1], s("Normal", 91.37)),
     it("g20", "Mirror crossed out, pointing hands", s("Normal", 91.37), s("Crazy", 94.24)),
     it("g21", "Musk CRAZY, Jobs BORING, Arnold OBSESSED", s("Crazy", 94.24), s("whatever", 96.09)),
     it("g22", "Dictionary 'mediocrity', grey figures", s("whatever", 96.09), s("You", 99.05))]
P = [it(f"p{k:02d}", lab, a, min(b, L), d) for k, (a, b, lab, d) in enumerate([
     (*S.P_MIRROR, "Mirror physique photo", "photo, unfiltered"), (*S.P_PAIN, "Press clip", "HDR"),
     (*S.P_PULL, "Pull-ups", "HDR"), (*S.P_CLOSE, "Close press, full frame", "HDR"),
     (*S.P_INCL, "Incline press, KEEP GOING", "HDR"), (*S.P_FLEX, "Flex clip + Sisyphus", "HDR"),
     (*S.P_DUMB, "Dumbbell photo", "photo"), (*S.P_OUT, "Flex clip, OUTLIERS", "HDR"),
     (S.P_FRONT[0], L, "Front physique photo, YOU.", "photo")])]
him = [it(f"h{k:02d}", {"BIG": "You: big, centre", "SR": "You: small, right", "SL": "You: small, left"}[n], a,
          (S.STATES[k + 1][0] if k + 1 < len(S.STATES) else L)) for k, (a, n) in enumerate(S.STATES)]
caps = []
for k, b in enumerate(S.scene2.BL):
    caps.append(it(f"t{k:03d}", " ".join(w["w"] for w in b), b[0]["s"], b[-1]["e"]))
out = {"tracks": [
    {"id": "graphics", "label": "Graphics", "items": G},
    {"id": "physique", "label": "Physique shots", "items": P},
    {"id": "you", "label": "Your circle", "items": him},
    {"id": "captions", "label": "Captions", "items": caps},
    {"id": "music", "label": "Music", "items": [it("m1", "Jake Chudnow, Turquoise", 0, L, "about 10 dB under the voice, fades on the last 'normal'")]}]}
# sound effects: same list as work/build3/mix3.py
import mix3
out["tracks"].insert(3, {"id": "sfx", "label": "Sound effects", "items":
    [it(f"s{k:03d}", n.replace("-0", " ").replace("thud 3", "thud"), t - .05, t + .25, f"{g:+.0f} dB") for k, (t, n, g) in enumerate(sorted(mix3.E))]})
json.dump(out, open("work/timeline_extra.json", "w"), indent=1, ensure_ascii=False)
print({t["id"]: len(t["items"]) for t in out["tracks"]})
