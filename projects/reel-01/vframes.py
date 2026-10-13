"""Stream video frames on demand (low memory). Fast when times are requested in order, like a render chunk does.

    v = StreamFrames("work/cut.mp4", fps=30)       # optional w, h
    rgba = v.array(t)                               # HxWx4 uint8 at time t (holds the last frame past the end)
"""
import subprocess

import numpy as np


class StreamFrames:
    def __init__(self, path, fps=30, w=None, h=None, offset=0.0):
        self.path, self.fps, self.offset = str(path), fps, offset
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                              "stream=width,height:format=duration", "-of", "default=nw=1", self.path],
                             capture_output=True, text=True).stdout
        kv = dict(l.split("=", 1) for l in out.split() if "=" in l)
        self.w, self.h = w or int(kv["width"]), h or int(kv["height"])
        self.n = int(float(kv["duration"]) * fps + 1e-6)
        self.proc, self.next_i, self.last = None, None, None

    def _open(self, i):
        if self.proc:
            self.proc.kill()
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{i / self.fps:.4f}", "-i", self.path, "-vf",
                                      f"fps={self.fps},scale={self.w}:{self.h}", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=self.w * self.h * 4 * 2)
        self.next_i = i

    def array(self, t):
        i = int(max(0, min(self.n - 1, round((t - self.offset) * self.fps))))
        if self.last is not None and self.last[0] == i:
            return self.last[1]
        if self.proc is None or i < self.next_i or i > self.next_i + 45:
            self._open(i)
        size = self.w * self.h * 4
        while True:
            b = self.proc.stdout.read(size)
            if len(b) < size:                                  # past the end: hold the last frame
                return self.last[1] if self.last is not None else np.zeros((self.h, self.w, 4), np.uint8)
            j = self.next_i; self.next_i += 1
            if j == i:
                arr = np.frombuffer(b, np.uint8).reshape(self.h, self.w, 4)
                self.last = (i, arr)
                return arr
