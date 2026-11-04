"""reel-05 sound mix (3.0 s, 48 kHz stereo) -> work/audio/mix.wav
Engines pan with the vehicles on screen (bike left->right, car right->left), impact on the lock,
sunrise swell (low-passed, it is bright), shimmer + small hit for the wordmark."""
import os, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scene2 import BIKE_L, CAR_L, T_LOCK, T_REDA   # noqa: E402

SR, DUR = 48000, 3.0
N = int(SR * DUR)


def load(name):
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "..", "assets", "sfx", name + ".mp3"),
                        "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(a, np.float32).astype(np.float64)


def db(x):
    return 10 ** (x / 20)


def lowpass(x, hz, dry=0.15):
    sos = butter(2, hz, "low", fs=SR, output="sos")
    return sosfilt(sos, x) * (1 - dry) + x * dry


def put(bus, clip, start, gain_db=0.0, pan=None, fade_in=0.01, fade_out=0.08, end=None):
    """add a mono clip at start (s). pan: function t -> -1..1, or a number."""
    i0 = int(start * SR)
    clip = clip.copy() * db(gain_db)
    if end is not None:
        clip = clip[: max(0, int((end - start) * SR))]
    n = len(clip)
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    if fi:
        clip[:fi] *= np.linspace(0, 1, fi)
    if fo:
        clip[-fo:] *= np.linspace(1, 0, fo)
    seg = slice(max(0, i0), min(N, i0 + n))
    c = clip[seg.start - i0: seg.stop - i0]
    t = np.arange(seg.start, seg.stop) / SR
    p = np.full_like(t, 0.0) if pan is None else (pan(t) if callable(pan) else np.full_like(t, pan))
    ang = (np.clip(p, -1, 1) + 1) * np.pi / 4
    bus[seg, 0] += c * np.cos(ang)
    bus[seg, 1] += c * np.sin(ang)


def pan_of(curve, width, t0):
    def f(t):
        x = curve(np.clip(t, t0, 2.3)) + width / 2           # centre of the vehicle on screen
        return np.clip((x - 960) / 960, -1, 1) * 0.85
    return f


def main():
    bus = np.zeros((N, 2))
    # engines
    put(bus, load("bike_pass"), 0.45, -4.0, pan_of(BIKE_L, 650, 0.78), fade_in=0.25, fade_out=0.45, end=2.45)
    put(bus, load("car_pass"), 0.35, -4.5, pan_of(CAR_L, 770, 0.98), fade_in=0.35, fade_out=0.45, end=2.40)
    # sunrise swell, softened
    put(bus, lowpass(load("swell"), 2600), 0.15, -9.0, 0.0, fade_in=0.3, fade_out=0.35)
    # lock impact and the red A
    imp = load("impact")
    put(bus, imp, T_LOCK - 0.01, -2.0, 0.0, fade_in=0.002, fade_out=0.3)
    put(bus, lowpass(imp, 3000, 0.3), T_REDA[1] - 0.01, -11.0, 0.05, fade_in=0.002, fade_out=0.25)
    # wordmark shimmer (peaks about 0.3 s in)
    put(bus, lowpass(load("text_shimmer"), 5000, 0.4), 2.05, -9.0, 0.0, fade_in=0.02, fade_out=0.3)
    # end of the intro: gentle 0.15 s fade
    k = int(0.15 * SR)
    bus[-k:] *= np.linspace(1, 0, k)[:, None]
    peak = np.abs(bus).max()
    bus *= db(-3.0) / peak
    out = os.path.join(HERE, "audio")
    os.makedirs(out, exist_ok=True)
    pcm = (np.clip(bus, -1, 1) * 32767).astype(np.int16)
    import wave
    with wave.open(os.path.join(out, "mix.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print("peak normalised to -3 dBFS (gain %.1f dB)" % (20 * np.log10(db(-3.0) / peak)))


if __name__ == "__main__":
    main()
