"""Cut both clips by work/cut_plan.json -> work/cut.mp4 (1080x1920, 30 fps, original audio).
Each audio piece gets 8 ms fades so the joins never click. Pass --draft for a small preview (out/rough-cut-draft.mp4)."""
import json, subprocess, sys
plan = json.load(open("work/cut_plan.json"))
# one seeked input per segment: reusing one input across many trims buffers the whole clip in memory
ins, parts = [], []
for i, s in enumerate(plan["segments"]):
    k, d = i, s["src_out"] - s["src_in"]
    ins += ["-ss", f"{s['src_in']:.5f}", "-t", f"{d + 0.5:.5f}", "-i", s["src"]]
    parts.append(f"[{k}:v]setpts=PTS-STARTPTS,fps=30,trim=end_frame={round(d * 30)},"
                 f"scale=1080:1920,setsar=1,format=yuv420p[v{i}];"
                 f"[{k}:a]asetpts=PTS-STARTPTS,atrim=0:{d:.5f},aformat=sample_rates=48000:channel_layouts=stereo,"
                 f"afade=t=in:d=0.008,afade=t=out:st={d - 0.008:.3f}:d=0.008[a{i}]")
n = len(parts)
fc = ";".join(parts) + ";" + "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
draft = "--draft" in sys.argv
if draft:
    fc = fc.replace("concat=n=%d:v=1:a=1[v][a]" % n, "concat=n=%d:v=1:a=1[vc][a];[vc]scale=540:960[v]" % n)
out = "out/rough-cut-draft.mp4" if draft else "work/cut.mp4"
cmd = ["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-crf", "23" if draft else "14", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k",
       "-movflags", "+faststart", out]
subprocess.run(cmd, check=True)
print("cut ->", out)
