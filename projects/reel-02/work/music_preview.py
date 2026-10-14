"""Music option previews: draft picture + isolated voice + option a/b ducked under the voice.
    python3 work/music_preview.py a   -> out/music-option-a.mp4"""
import subprocess, sys
k = sys.argv[1]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            "work/voice_cut.wav"], capture_output=True, text=True).stdout)
fc = ("[1:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,"
      "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,asplit=2[v][key];"
      f"[2:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,"
      f"aformat=channel_layouts=stereo,volume=-3dB,afade=t=out:st={dur - 0.8:.2f}:d=0.8[m];"
      "[m][key]sidechaincompress=threshold=0.12:ratio=3:attack=15:release=300[md];"
      "[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "out/rough-cut-draft.mp4", "-i", "work/voice_cut.wav",
                "-i", f"assets/music/option-{k}.mp3", "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"out/music-option-{k}.mp4"], check=True)
print("->", f"out/music-option-{k}.mp4")
