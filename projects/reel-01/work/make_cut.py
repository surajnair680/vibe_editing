"""Cut the take by work/cut_plan.json -> work/cut.mp4 (30 fps, no audio) and work/voice_cut.wav (isolated voice).
Each audio piece gets 8 ms fades so the joins never click."""
import json, subprocess
plan = json.load(open("work/cut_plan.json"))["segments"]
v, a = [], []
for i, s in enumerate(plan):
    d = s["src_out"] - s["src_in"]
    v.append(f"[0:v]trim={s['src_in']}:{s['src_out']},setpts=PTS-STARTPTS,fps=30[v{i}]")
    a.append(f"[1:a]atrim={s['src_in']}:{s['src_out']},asetpts=PTS-STARTPTS,aformat=sample_rates=44100:channel_layouts=mono,"
             f"afade=t=in:d=0.008,afade=t=out:st={d - 0.008:.3f}:d=0.008,"
             f"adelay={int(round(s['edit_in'] * 1000))}:all=1[a{i}]")          # each piece starts exactly where its picture starts
n = len(plan)
fc = ";".join(v + a) + ";" + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v];" + \
     "".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,apad,atrim=0:{json.load(open('work/cut_plan.json'))['length']}[a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw/take-01.mp4", "-i", "work/voice_isolated.mp3", "-filter_complex", fc,
                "-map", "[v]", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "work/cut.mp4",
                "-map", "[a]", "-c:a", "pcm_s16le", "work/voice_cut.wav"], check=True)
print("cut ->", "work/cut.mp4", "work/voice_cut.wav")
