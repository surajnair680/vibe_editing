"""Gym clips -> tight, warmed print clips at 30 fps (picture only).
    python3 work/prep_gym.py
gym1_print.mp4  raw/gym-1.mp4 1.30 to 3.40 s, crop 710x888 at (280,200): head to mid chest, people behind cut out.
gym3_lat.mp4    raw/gym-3.mp4 2.40 to 4.60 s, crop 1080x1080 at (0,440): lat spread, arms in frame.
gym3_side.mp4   raw/gym-3.mp4 0.60 to 2.00 s, crop 900x1124 at (100,160): side chest, half speed (60 fps source).
Warm grade like reel-01's gym print (the gym's blue light pulled towards the poster's warm paper)."""
import subprocess
WARM = "colorchannelmixer=rr=1.06:gg=1.0:bb=0.80,eq=saturation=0.80:contrast=1.06:brightness=0.02"
JOBS = [("raw/gym-1.mp4", 1.30, 2.10, "crop=710:888:280:200", 1.0, "work/gym1_print.mp4"),
        ("raw/gym-3.mp4", 2.40, 2.20, "crop=1080:1080:0:440", 1.0, "work/gym3_lat.mp4"),
        ("raw/gym-3.mp4", 0.60, 1.40, "crop=900:1124:100:160", 2.0, "work/gym3_side.mp4")]
for src, ss, t, crop, slow, out in JOBS:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(t), "-i", src, "-vf",
                    f"{crop},setpts={slow}*(PTS-STARTPTS),fps=30,{WARM}", "-an", "-c:v", "libx264", "-crf", "12",
                    "-preset", "veryfast", "-pix_fmt", "yuv420p", out], check=True)
    print(out)
