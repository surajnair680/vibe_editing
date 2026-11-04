"""Sound for v1 (work/scene.py, 2.5 s): same ElevenLabs SFX as v2, retimed. -> work/audio/mix_v1.wav
Car pans right->left, bike left->right (following scene.py's drive curve), impact on the lock (0.95 s),
sunrise swell, shimmer under the letters, small hit on the red A (1.62 s)."""
import os, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mix as M          # reuse load / put / lowpass / db

M.DUR = 2.5
M.N = int(M.SR * M.DUR)
SR, N = M.SR, M.N


def drive_dx(t):
    u = np.clip((t - 0.10) / 0.85, 0, 1)
    return 1700 * (1 - (1 - (1 - u) ** 3))


def pan_car(t):
    return np.clip((720 + drive_dx(t) - 960) / 960, -1, 1) * 0.85


def pan_bike(t):
    return np.clip((1255 - drive_dx(t) - 960) / 960, -1, 1) * 0.85


def trim(x, s):
    x = x[int(s * SR):].copy()
    k = int(0.04 * SR)
    x[:k] *= np.linspace(0, 1, k)
    return x


def main():
    bus = np.zeros((N, 2))
    M.put(bus, trim(M.load("bike_pass"), 0.25), 0.0, -4.0, pan_bike, fade_in=0.0, fade_out=0.45, end=1.45)
    M.put(bus, trim(M.load("car_pass"), 0.60), 0.0, -4.5, pan_car, fade_in=0.0, fade_out=0.45, end=1.40)
    M.put(bus, M.lowpass(M.load("swell"), 2600), 0.05, -9.0, 0.0, fade_in=0.3, fade_out=0.3, end=1.0)
    imp = M.load("impact")
    M.put(bus, imp, 0.94, -2.0, 0.0, fade_in=0.002, fade_out=0.3)
    M.put(bus, M.lowpass(M.load("text_shimmer"), 5000, 0.4), 1.05, -9.0, 0.0, fade_in=0.02, fade_out=0.3)
    M.put(bus, M.lowpass(imp, 3000, 0.3), 1.61, -11.0, 0.05, fade_in=0.002, fade_out=0.25)
    k = int(0.15 * SR)
    bus[-k:] *= np.linspace(1, 0, k)[:, None]
    bus *= M.db(-3.0) / np.abs(bus).max()
    pcm = (np.clip(bus, -1, 1) * 32767).astype(np.int16)
    with wave.open(os.path.join(HERE, "audio", "mix_v1.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main()
