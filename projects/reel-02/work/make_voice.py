"""Cut the ElevenLabs-isolated voice by work/cut_plan.json -> work/voice_cut.wav (48 kHz mono).
Same in/out points as work/make_cut.py, so it lines up with work/cut.mp4 frame for frame.
Isolated files: work/audio/<clip>-isolated.wav, decoded from the .mp3 that came back from (POST /v1/audio-isolation on each full clip, in sync within 5 ms).
Cut from WAV, not MP3: seeking inside the MP3 lands up to 100 ms off."""
import json, os, subprocess
plan = json.load(open("work/cut_plan.json"))
segs = plan["segments"]
ins, parts = [], []
for i, s in enumerate(segs):
    d = s["src_out"] - s["src_in"]
    iso = "work/audio/" + os.path.basename(s["src"]).replace(".mp4", "-isolated.wav")
    fo = 0.15 if i == len(segs) - 1 else 0.008
    ins += ["-ss", f"{s['src_in']:.5f}", "-t", f"{d + 0.5:.5f}", "-i", iso]
    parts.append(f"[{i}:a]asetpts=PTS-STARTPTS,atrim=0:{d:.5f},aresample=48000,aformat=channel_layouts=mono,"
                 f"apad=whole_dur={d:.5f},afade=t=in:d=0.008,afade=t=out:st={d - fo:.3f}:d={fo}[a{i}]")
fc = ";".join(parts) + ";" + "".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[a]"
subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[a]", "-c:a", "pcm_s16le",
                "work/voice_cut.wav"], check=True)
print("voice ->", "work/voice_cut.wav")
