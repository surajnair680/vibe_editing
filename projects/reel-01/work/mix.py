"""Mix reel-01: cleaned voice + music B (extended, ducked under the voice) + sound effects on their frames.

    python3 work/mix.py            # -> work/mix.wav, then muxes onto out/reel-01_silent.mp4 -> out/reel-01_v1.mp4

Every cue time comes from reel_scene.py, so picture and sound use the same clock.
Each SFX is placed so its loudest moment lands on the cue (measured, not guessed).
"""
import json
import subprocess
import sys

import numpy as np

sys.path.insert(0, ".")
import reel_scene as R

SR = 44100


def peak_offset(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.abs(np.frombuffer(raw, np.int16).astype(float))
    env = np.convolve(a, np.ones(80) / 80, "same")
    return float(np.argmax(env) / 8000), float(20 * np.log10(env.max() / 32768 + 1e-9))


wt = R.wt
CUES = []          # (file, time the peak should land, gain dB, pitch factor)
for i, mid in enumerate(m for m, *_ in R.WIPES):
    CUES.append(("brush-swoosh", mid - 0.04, -8 + (i % 3) * 1.5, (0.94, 1.0, 1.06)[i % 3]))
for t_hit, g in ((wt("addictions"), -3), (wt("yes", 3.5), -5), (wt("your", 15), -5), (wt("yourself", 37), -5),
                 (R.PAY_IN, -2), (wt("own"), -7), (wt("fix"), -2)):
    CUES.append(("low-hit", t_hit + 0.02, g, 1.0))
for t_hit in (wt("90%"), wt("genetics"), wt("family"), wt("circumstances"), wt("stepping"), wt("tracking")):
    CUES.append(("paper-slap", t_hit + 0.08, -12, 1.0))
for t_hit in (wt("their") + 0.12, wt("habits") + 0.12, wt("just") + 0.3, R.P2_OUT + 0.3, wt("look", 53) + 0.15):
    CUES.append(("pop", t_hit, -13, 1.0))
CUES += [("ink-stamp", wt("no") + 0.06, -5, 1.0), ("dice-rattle", wt("luck", 30) + 0.25, -9, 1.0),
         ("stone-crack", wt("mistakes") + 0.1, -7, 1.0)]

voice = "work/voice_cut.wav"
music = "work/music_b_extended.wav"
mix = json.load(open("work/music_mix.json"))
dur = R.DUR

inputs = ["-i", voice, "-i", music, "-i", "assets/sfx/waves.mp3"]
files = sorted({c[0] for c in CUES})
for f in files:
    inputs += ["-i", f"assets/sfx/{f}.mp3"]
idx = {f: 3 + i for i, f in enumerate(files)}
pk = {f: peak_offset(f"assets/sfx/{f}.mp3") for f in files}

fc = [
    # voice: gentle high-pass and compression, then split for the ducking key
    "[0:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=80,"
    "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,asplit=2[v][key]",
    # music: matched loudness, the B trim, ducked under the voice, fades
    f"[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=11,aresample=44100,aformat=channel_layouts=stereo,"
    f"volume={mix['trim_db']['b']}dB,afade=t=in:d=0.4,afade=t=out:st={dur - 0.6:.2f}:d=0.6[m]",
    f"[m][key]sidechaincompress=threshold={mix['duck']['threshold']}:ratio={mix['duck']['ratio']}:"
    f"attack={mix['duck']['attack_ms']}:release={mix['duck']['release_ms']}[md]",
    # waves under the first Seneca poster
    f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=-22dB,afade=t=in:d=0.6,"
    f"afade=t=out:st={R.P1_OUT - R.P1_IN - 0.9:.2f}:d=0.9,adelay={int(R.P1_IN * 1000)}:all=1[wv]",
]
labels = ["[v]", "[md]", "[wv]"]
uses = {}
for f, t_peak, g, pitch in CUES:
    uses.setdefault(f, []).append((t_peak, g, pitch))
for f, lst in uses.items():
    off, lvl = pk[f]
    fc.append(f"[{idx[f]}:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit={len(lst)}" +
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
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,apad,atrim=0:{dur},"
          "loudnorm=I=-14:TP=-1.5:LRA=11[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[out]",
                "-ar", "48000", "-c:a", "pcm_s16le", "work/mix.wav"], check=True)
print(f"mix -> work/mix.wav ({len(CUES)} sound effects)")
json.dump([{"sfx": f, "peak_at": round(t, 3), "gain_db": g} for f, t, g, _ in CUES], open("work/sfx_cues.json", "w"), indent=1)

if len(sys.argv) < 2 or sys.argv[1] != "--no-mux":
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "out/reel-01_silent.mp4", "-i", "work/mix.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", "out/reel-01_v1.mp4"], check=True)
    print("video -> out/reel-01_v1.mp4")
