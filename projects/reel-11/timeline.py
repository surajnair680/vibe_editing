"""reel-11 timeline: the single source of timings (edit time, seconds, 30 fps).

Pieces come from the approved rough cut v2 (work/cut_plan.json + the 3a/3b seam piece of work/make_cut.py).
Word times are Scribe word starts/ends mapped into edit time.
"""
import json

FPS = 30
CUT_END = 48.4                 # end of the approved cut (voice ends 48.25)
TAIL = 1.5                     # physique hold + FOLLOW card after the voice
DUR = round(CUT_END + TAIL, 4)  # 49.9

# (clip, source in, edit in) per piece of rough v2; the seam piece holds 3a then 3b
PIECES = [("her", 0.4333, 0.0), ("her", 20.0, 7.9667), ("me_2", 1.4667, 12.8667), ("me_3a", 0.5667, 15.6333),
          ("me_3a", 12.7333, 25.8667), ("me_3b", -(25.8667 + 106 / 30 + 0.0151 - 25.8667) + 0.0, 25.8667 + 106 / 30 + 0.0151),
          ("me_3b", 3.4333, 31.0), ("me_3d", 1.3, 35.3667)]
# word ranges used per piece (source seconds)
RANGES = [("me_2", 1.4, 4.3, 12.8667, 1.4667), ("me_3a", 0.5, 10.9, 15.6333, 0.5667),
          ("me_3a", 12.7, 16.1, 25.8667, 12.7333), ("me_3b", -0.3, 1.7, 25.8667 + 106 / 30 + 0.0151, 0.0),
          ("me_3b", 3.4, 7.9, 31.0, 3.4333), ("me_3d", 1.2, 14.4, 35.3667, 1.3)]


def words():
    out = []
    for clip, lo, hi, e0, s0 in RANGES:
        for w in json.load(open(f"work/transcripts/{clip}/words.json")):
            if lo <= w["s"] < hi:
                text = w["w"].rstrip("-")
                if text == "On":
                    text = "on"
                out.append({"w": text, "s": round(e0 + w["s"] - s0, 3), "e": round(e0 + w["e"] - s0, 3)})
    return out


# beats (edit seconds): name -> (start, end)
BEATS = {
    "her": (0.0, 12.70),
    "pause": (12.70, 13.10),          # her last frame mosaics, PAUSED, cut to him
    "deadpan": (13.10, 15.6333),      # him full screen
    "quest": (15.6333, 19.0),         # QUEST window, Tiger card on "celebrity"
    "calendar": (19.0, 21.10),        # six months
    "menu": (21.10, 25.90),           # keto / IF / PPL, perfect plan 99 %
    "save": (25.90, 29.05),           # wait for next Monday
    "couch": (29.05, 31.0),           # sitting on your ass gaining fat
    "item": (31.0, 35.3667),          # protect a physique you are unhappy with
    "lady": (35.3667, 38.10),         # just ignore this lady
    "share": (38.10, 41.0),           # do not share with that one friend
    "questlog": (41.0, 45.17),        # since 2020
    "breakout": (45.17, DUR),         # real footage montage + FOLLOW
}

if __name__ == "__main__":
    W = words()
    json.dump(W, open("work/words_edit.json", "w"), indent=0)
    for w in W:
        print(f"{w['s']:7.2f} {w['e']:7.2f} {w['w']}")
