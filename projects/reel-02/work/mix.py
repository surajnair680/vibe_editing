"""Mix reel-02: isolated voice + music B (extended, ducked under the voice) + sound effects on their frames.

    python3 work/mix.py            # -> work/mix.wav, then muxes onto out/reel-02_silent.mp4 -> out/reel-02_v1.mp4

Levels (user notes): music exactly as in the approved B preview (work/music_preview.py), voice about 10% louder
(+1.4 dB). So the ducking key is the voice before the boost (same ducking as the preview), and the master gain is
fixed to the preview's: G = -14 LUFS minus the loudness of the preview mix before its loudnorm.
Every cue time comes from reel_scene.py, so picture and sound use the same clock. Each SFX is placed so its
loudest moment lands on the cue (measured, not guessed).
"""
import json
import subprocess
import sys

import numpy as np

sys.path.insert(0, ".")
import reel_scene as R

SR = 48000
VOICE_BOOST_DB = 1.4
DUR = R.DUR
VOICE = "work/voice_cut.wav"
MUSIC_SRC = "assets/music/option-b.mp3"
MUSIC = "work/music_b_extended.wav"


def run(cmd):
    subprocess.run(cmd, check=True)


def loudness(path):
    out = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float([l for l in out.splitlines() if l.strip().startswith("I:")][-1].split()[1])


def peak_offset(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.abs(np.frombuffer(raw, np.int16).astype(float))
    env = np.convolve(a, np.ones(80) / 80, "same")
    return float(np.argmax(env) / 8000), float(20 * np.log10(env.max() / 32768 + 1e-9))


# ---------------------------------------------------------------- music: repeat one phrase so the beat reaches the end card
# The track ends at 41.6 s. It runs in 4-bar phrases (6.4 s; phrase starts 24.035, 30.435, 36.835 match at r > 0.9),
# so a 2-bar repeat would jump mid-phrase. Repeat the whole phrase 30.435..36.835 at a phrase boundary instead;
# the beat then runs under the end card and fades with the video.
JOIN, BACK = 36.835, 6.4
run(["ffmpeg", "-v", "error", "-y", "-i", MUSIC_SRC, "-filter_complex",
     f"[0:a]asplit=2[x][y];[x]atrim=0:{JOIN + 0.01},asetpts=PTS-STARTPTS[p1];[y]atrim={JOIN - BACK - 0.01},asetpts=PTS-STARTPTS[p2];"
     f"[p1][p2]acrossfade=d=0.02:c1=tri:c2=tri,aresample={SR}", MUSIC])

# ---------------------------------------------------------------- the preview chain (music identical to what was approved)
def music_chain(i_music, key):
    return (f"[{i_music}:a]atrim=0:{DUR:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=11,aresample={SR},"
            f"aformat=channel_layouts=stereo,volume=-3dB,afade=t=out:st={DUR - 0.8:.2f}:d=0.8[m];"
            f"[m][{key}]sidechaincompress=threshold=0.12:ratio=3:attack=15:release=300[md]")

VOICE_CHAIN = (f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo,highpass=f=80,"
               "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,apad,"
               f"atrim=0:{DUR:.3f},asplit=2[v][key]")

# reference: the preview's mix before its loudnorm, measured to fix the master gain
run(["ffmpeg", "-v", "error", "-y", "-i", VOICE, "-i", MUSIC, "-filter_complex",
     VOICE_CHAIN + ";" + music_chain(1, "key") + ";[v][md]amix=inputs=2:normalize=0[a]", "-map", "[a]", "-c:a", "pcm_s16le",
     "work/mix_reference.wav"])
G = -14.0 - loudness("work/mix_reference.wav")

# ---------------------------------------------------------------- sound effects
wt = R.wt
CUES = []          # (file, time the peak should land, gain dB, pitch factor)
for i, (mid, *_rest) in enumerate(R.WIPES):
    CUES.append(("brush-swoosh", mid - 0.04, -9 + (i % 3) * 1.5, (0.94, 1.0, 1.07, 0.97, 1.03, 0.91, 1.05)[i]))
for t_hit, g in ((wt("you"), -4), (wt("paralysis"), -4), (R.W_POSTER + 0.05, -6), (wt("start", 42.3), -2)):
    CUES.append(("low-hit", t_hit + 0.02, g, 1.0))
for t_hit, g in ((R.W_ROOM1 + 0.12, -14), (wt("one", 9.0) + 0.1, -15), (wt("the", 12.0) + 0.1, -15),
                 (wt("the", 20.0) + 0.15, -14), (wt("stop") + 0.1, -14), (wt("perfect", 30.4), -16), (wt("perfect", 31.6), -16),
                 (wt("perfect", 32.7), -16), (R.FLIP, -9)):
    CUES.append(("paper-slap", t_hit, g, 1.0))
CUES.append(("camera-shutter", wt("photography") + 0.05, -10, 1.0))
p0, p1 = wt("graded"), wt("took") + 0.4
for k, u in enumerate((0.0, 0.13, 0.31, 0.46, 0.64, 0.83)):          # the pile: a few uneven clicks, quiet
    CUES.append(("camera-shutter", p0 + u * (p1 - p0), -17 - (k % 2) * 2, 1.0 + 0.04 * (k % 3)))
CUES.append(("camera-shutter", wt("one", 13.4), -11, 0.95))
for t_hit, g in ((wt("photos", 16.8), -6), (wt("perfection"), -8), (wt("way", 38.9), -7)):
    CUES.append(("stamp-thud", t_hit + 0.03, g, 1.0))
CUES.append(("brush-swoosh", wt("program") + 0.45, -13, 1.25))       # the red strike through the three items

files = sorted({c[0] for c in CUES})
inputs = ["-i", VOICE, "-i", MUSIC]
for f in files:
    inputs += ["-i", f"assets/sfx/{f}.mp3"]
idx = {f: 2 + i for i, f in enumerate(files)}
pk = {f: peak_offset(f"assets/sfx/{f}.mp3") for f in files}

fc = [VOICE_CHAIN, f"[v]volume={VOICE_BOOST_DB}dB[vb]", music_chain(1, "key")]
labels = ["[vb]", "[md]"]
uses = {}
for f, t_peak, g, pitch in CUES:
    uses.setdefault(f, []).append((t_peak, g, pitch))
for f, lst in uses.items():
    off, lvl = pk[f]
    fc.append(f"[{idx[f]}:a]aformat=sample_rates={SR}:channel_layouts=stereo,asplit={len(lst)}" +
              "".join(f"[{f}{k}]" for k in range(len(lst))))
    for k, (t_peak, g, pitch) in enumerate(lst):
        start = max(0.0, t_peak - off / pitch)
        norm = -6 - lvl                                                 # every effect peaks at -6 dBFS before its gain
        chain = f"[{f}{k}]"
        if pitch != 1.0:
            chain += f"asetrate={int(SR * pitch)},aresample={SR},"
        chain += f"volume={norm + g:.1f}dB,adelay={int(start * 1000)}:all=1[{f}{k}o]"
        fc.append(chain)
        labels.append(f"[{f}{k}o]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{DUR:.3f},"
          f"volume={G:.2f}dB,alimiter=limit=0.79:attack=3:release=60:level=disabled[a]")
run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[a]", "-c:a", "pcm_s16le",
     "-ar", str(SR), "work/mix.wav"])
json.dump({"master_gain_db": round(G, 2), "voice_boost_db": VOICE_BOOST_DB, "music_join": [JOIN, BACK],
           "cues": [(f, round(t, 3), g, p) for f, t, g, p in CUES]}, open("work/mix_cues.json", "w"), indent=1)
print(f"mix -> work/mix.wav  master gain {G:+.2f} dB, loudness {loudness('work/mix.wav'):.1f} LUFS")

if "--no-mux" not in sys.argv:
    run(["ffmpeg", "-v", "error", "-y", "-i", "out/reel-02_silent.mp4", "-i", "work/mix.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", "out/reel-02_v1.mp4"])
    print("-> out/reel-02_v1.mp4")
