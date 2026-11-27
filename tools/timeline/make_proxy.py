"""Low-res live-cut proxy for the timeline editor: all raw parts joined in source time, small picture,
keyframe every 0.5 s (fast seeking), the project's voice WAV as sound.
  python3 tools/timeline/make_proxy.py projects/<name> [--voice work/audio/full_iso.wav] [--height 640]
Needs work/parts.json (or a single raw file via --src). Writes work/timeline/proxy.mp4."""
import argparse, json, os, subprocess
ap = argparse.ArgumentParser()
ap.add_argument("project"); ap.add_argument("--voice", default="work/audio/full_iso.wav")
ap.add_argument("--height", type=int, default=640); ap.add_argument("--src", default=None)
a = ap.parse_args(); P = a.project.rstrip("/")
files = [a.src] if a.src else json.load(open(f"{P}/work/parts.json"))["parts"]
ins, fl = [], []
for i, f in enumerate(files):
    ins += ["-i", f"{P}/{f}"]
    fl.append(f"[{i}:v]scale=-2:{a.height},fps=30,setsar=1,setpts=PTS-STARTPTS[v{i}]")
fl.append("".join(f"[v{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=1:a=0[v]")
out = f"{P}/work/timeline/proxy.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", f"{P}/{a.voice}", "-filter_complex", ";".join(fl),
                "-map", "[v]", "-map", f"{len(files)}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "30",
                "-g", "15", "-keyint_min", "15", "-sc_threshold", "0", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-movflags", "+faststart", out], check=True)
print(out, round(os.path.getsize(out) / 2**20, 2), "MiB")
