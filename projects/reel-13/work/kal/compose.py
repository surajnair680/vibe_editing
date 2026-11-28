"""compose: build the Kallaway-style video from the rendered panel, the talking head, its matte and the words.

    python3 compose.py plan.json -o out/v1.mp4                     # full render (with the speaker's audio)
    python3 compose.py plan.json --stills 0,2.5,5 --dir out/stills  # chosen frames as PNG (stills-first rule)
    python3 compose.py plan.json --every 2.5 --sheet out/sheet.jpg  # contact sheet every 2.5 s
    python3 compose.py plan.json -o out/part.mp4 --start 10 --end 14   # one range (revisions)

Layouts per segment (plan.json "segments"):
    split  panel frame + rounded speaker strip at the bottom + pop-out cut-out + caption above the strip
    full   talking head full frame (punched in) + caption over the chest
    broll  full-frame clip ("src", "src_start") + caption

plan.json (paths relative to the plan file):
{
  "fps": 30, "duration": 15.0,
  "speaker": "raw/cut.mp4",               the cut talking head; timeline time = speaker time
  "matte": "work/matte/cut_alpha.mp4",    vibe/matte.py output (white = person), same size and fps as speaker
  "panel": "out/panel.mp4",               the kit page rendered with tools/seek_render.mjs, same timeline
  "words": "work/words_cut.json",         [{"w","s","e"}] re-timed to the cut
  "strip": {"scale": 0.7, "band_top": "auto", "popout": 60},   scale 1.0 for 16:9 footage, ~0.7 for 9:16;
                                          band_top "auto" = head pokes out popout px above the strip
  "full": {"zoom": 1.1, "anchor": [0.5, 0.33]},
  "serif": ["Comprehension", "Maxing", "\"hooks\""],   words shown in the serif italic
  "caption_hold": 0.6,                     keep a word up to this long after it ends if no next word
  "segments": [{"start": 0, "end": 3.0, "layout": "split"}, {"start": 3.0, "end": 4.2, "layout": "full"}]
}
Needs numpy, opencv-python, Pillow and ffmpeg (all in the vibe setup). Fonts are read from ../assets/fonts.
"""
import argparse, json, os, subprocess, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
STRIP_X0, STRIP_X1, STRIP_TOP, RADIUS = 68, 1012, 1403, 50
CAP_Y_SPLIT, CAP_Y_FULL = 1285, 1165          # caption centre lines (measured)
FONT_DIR = Path(__file__).resolve().parents[4] / ".claude/skills/edit-like-kallawaymarketing/assets/fonts"  # reel-13 copy
FF = os.environ.get("FFMPEG", "ffmpeg")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    w, h = out.strip().split("\n")[0].split(",")
    return int(w), int(h)


class Reader:
    """Sequential frame reader with cheap forward seeking (re-opens on backward jumps)."""
    def __init__(self, path, fps, gray=False):
        self.path, self.fps, self.gray = str(path), fps, gray
        self.w, self.h = probe(path)
        self.proc, self.idx, self.last = None, -1, None

    def _open(self, t):
        if self.proc: self.proc.kill()
        pix = "gray" if self.gray else "rgb24"
        self.proc = subprocess.Popen([FF, "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", self.path, "-vf", f"fps={self.fps}",
                                      "-f", "rawvideo", "-pix_fmt", pix, "-"], stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL)
        self.idx = int(round(max(t, 0) * self.fps)) - 1

    def at(self, t):
        want = int(round(t * self.fps))
        if self.proc is None or want <= self.idx - 1 or want > self.idx + 3 * self.fps:
            self._open(t)
        n = self.w * self.h * (1 if self.gray else 3)
        while self.idx < want:
            buf = self.proc.stdout.read(n)
            if len(buf) < n: break
            self.idx += 1
            a = np.frombuffer(buf, np.uint8)
            self.last = a.reshape(self.h, self.w) if self.gray else a.reshape(self.h, self.w, 3)
        return self.last


def rounded_mask(w, h, r):
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1); cv2.rectangle(m, (0, r), (w, h), 255, -1)
    for cx, cy in [(r, r), (w - r - 1, r)]: cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return m.astype(np.float32) / 255


class Captions:
    def __init__(self, words, serif, hold):
        self.words, self.hold = words, hold
        self.serif = {s.strip('"').lower() for s in serif}
        self.cache = {}
        self.sans = ImageFont.truetype(str(FONT_DIR / "Inter-Variable.ttf"), 56)
        try: self.sans.set_variation_by_name("Bold")
        except Exception: pass
        self.ser = ImageFont.truetype(str(FONT_DIR / "InstrumentSerif-Italic.ttf"), 66)

    def word_at(self, t):
        for i, w in enumerate(self.words):
            nxt = self.words[i + 1]["s"] if i + 1 < len(self.words) else 1e9
            if w["s"] <= t < min(nxt, w["e"] + self.hold) or (w["s"] <= t < nxt and nxt - w["e"] < self.hold):
                return w["w"]
        return None

    def image(self, text, dark_text):
        key = (text, dark_text)
        if key not in self.cache:
            bare = text.strip('.,!?;:').strip('"“”').lower()
            f = self.ser if bare in self.serif else self.sans
            track = -0.03 * f.size if f is self.sans else 0.0       # tight tracking like the reference
            widths = [f.getlength(ch) + track for ch in text]
            box = f.getbbox(text)
            tw = int(sum(widths) - track) + 24
            im = Image.new("RGBA", (tw, box[3] - box[1] + 30), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            col = (17, 17, 17, 255) if dark_text else (255, 255, 255, 255)
            for dx, dy, c in ([(2, 3, (0, 0, 0, 90))] if not dark_text else []) + [(0, 0, col)]:
                x = 12
                for ch, wch in zip(text, widths):
                    d.text((x + dx, 12 - box[1] + dy), ch, font=f, fill=c); x += wch
            self.cache[key] = np.asarray(im).astype(np.float32) / 255
        return self.cache[key]


def paste(dst, rgba, cx, cy):
    h, w = rgba.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe <= xs or ye <= ys: return
    src = rgba[ys - y0:ye - y0, xs - x0:xe - x0]
    a = src[..., 3:4]
    dst[ys:ye, xs:xe] = dst[ys:ye, xs:xe] * (1 - a) + src[..., :3] * 255 * a


def cover(frame, zoom, anchor):
    fh, fw = frame.shape[:2]; s = max(W / fw, H / fh) * zoom
    rw, rh = int(fw * s), int(fh * s)
    big = cv2.resize(frame, (rw, rh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
    x0 = int(np.clip(anchor[0] * rw - W / 2, 0, rw - W)); y0 = int(np.clip(anchor[1] * rh - H * 0.4, 0, rh - H))
    return big[y0:y0 + H, x0:x0 + W].astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan"); ap.add_argument("-o", "--out")
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float)
    ap.add_argument("--stills"); ap.add_argument("--dir", default="out/stills")
    ap.add_argument("--every", type=float); ap.add_argument("--sheet")
    ap.add_argument("--crf", default="14")
    a = ap.parse_args()

    base = Path(a.plan).resolve().parent
    P = json.loads(Path(a.plan).read_text())
    rp = lambda k: str((base / P[k]).resolve()) if P.get(k) else None
    fps, dur = P.get("fps", 30), P["duration"]
    spk = Reader(rp("speaker"), fps); mat = Reader(rp("matte"), fps, gray=True) if P.get("matte") else None
    pan = Reader(rp("panel"), fps) if P.get("panel") else None
    words = json.loads(Path(rp("words")).read_text()) if P.get("words") else []
    words = [{"w": w.get("w", w.get("word", "")), "s": float(w.get("s", w.get("start", 0))), "e": float(w.get("e", w.get("end", 0)))} for w in words]
    caps = Captions(words, P.get("serif", []), P.get("caption_hold", 0.6))
    segs = P["segments"]; brolls = {}

    # strip geometry. The speaker frame is scaled by strip.scale x (strip width / frame width): 1.0 for wide
    # (16:9) footage like Kallaway's, about 0.7 for vertical phone footage so the shot is chest-up. Any gap at the
    # sides is filled with a blurred copy of the same frame. band_top "auto" puts the top of the head about
    # strip.popout px above the window's top edge (measured once from the matte, so it never jitters).
    scfg = P.get("strip", {})
    sw = STRIP_X1 - STRIP_X0
    s = sw / spk.w * scfg.get("scale", 1.0 if spk.w > spk.h else 0.7)
    fw, sh = int(spk.w * s), int(spk.h * s)
    fx = (sw - fw) // 2                                # x offset of the scaled frame inside the window
    band_top = scfg.get("band_top", "auto")
    if band_top == "auto" and mat is not None:
        tops = []
        for tt in np.linspace(0, min(dur, 6), 7):
            m = mat.at(tt)
            if m is None: continue
            rows = np.where((m > 128).mean(1) > 0.01)[0]
            if len(rows): tops.append(rows[0] / m.shape[0])
        head = float(np.median(tops)) if tops else 0.1
        oy = int(STRIP_TOP - scfg.get("popout", 60) - head * sh)
        mat._open(0)
    else:
        oy = int(STRIP_TOP - (0.06 if band_top == "auto" else band_top) * sh)
    win = rounded_mask(sw, H - STRIP_TOP, RADIUS)
    full_cfg = P.get("full", {})

    def seg_at(t):
        for g in segs:
            if g["start"] <= t < g["end"]: return g
        return segs[-1]

    def frame(t):
        g = seg_at(t); lay = g.get("layout", "split")
        cap = caps.word_at(t)
        if lay == "split":
            out = pan.at(t).astype(np.float32).copy() if pan else np.full((H, W, 3), 7, np.float32)
            src = spk.at(t)
            sp = cv2.resize(src, (fw, sh), interpolation=cv2.INTER_AREA).astype(np.float32)
            winh = H - STRIP_TOP
            # window content: blurred fill, then the scaled frame (top edge at oy on the canvas)
            fill = cv2.GaussianBlur(cv2.resize(src, (sw, int(src.shape[0] * sw / src.shape[1])), interpolation=cv2.INTER_AREA), (0, 0), 25).astype(np.float32)
            fy = int(np.clip((STRIP_TOP - oy) * sw / fw, 0, max(fill.shape[0] - winh, 0)))
            content = fill[fy:fy + winh]
            if content.shape[0] < winh: content = np.pad(content, ((0, winh - content.shape[0]), (0, 0), (0, 0)), mode="edge")
            y0 = STRIP_TOP - oy; part = sp[max(y0, 0):max(y0, 0) + winh]
            content = content.copy()
            if fx > 0:   # feather the frame's side edges into the blurred fill (no hard seam)
                ramp = np.clip(np.minimum(np.arange(fw), np.arange(fw)[::-1]) / 40.0, 0, 1)[None, :, None]
                tgt = content[:part.shape[0], fx:fx + fw]
                content[:part.shape[0], fx:fx + fw] = tgt * (1 - ramp) + part * ramp
            else:
                content[:part.shape[0], fx:fx + fw] = part
            m = win[:, :, None]
            region = out[STRIP_TOP:H, STRIP_X0:STRIP_X1]
            region[:] = region * (1 - m) + content * m
            # pop-out: the cut-out above the window's top edge (inside the window it matches the footage exactly)
            if mat is not None and oy < STRIP_TOP:
                al = cv2.resize(mat.at(t), (fw, sh), interpolation=cv2.INTER_LINEAR).astype(np.float32)[:, :, None] / 255
                top = max(0, oy); src0 = top - oy
                al_up, sp_up = al[src0:STRIP_TOP - oy], sp[src0:STRIP_TOP - oy]
                reg = out[top:STRIP_TOP, STRIP_X0 + fx:STRIP_X0 + fx + fw]
                reg[:] = reg * (1 - al_up) + sp_up * al_up
            if cap:
                bright = out[CAP_Y_SPLIT - 40:CAP_Y_SPLIT + 40, 200:880].mean() > 140
                paste(out, caps.image(cap, bright), W / 2, CAP_Y_SPLIT)
        elif lay == "panel":   # reel-13: the panel full frame (B-roll placeholders, end card), caption at FULL height
            out = pan.at(t).astype(np.float32).copy()
            if cap: paste(out, caps.image(cap, False), W / 2, CAP_Y_FULL)
        elif lay == "broll":
            src = g["src"]
            if src not in brolls: brolls[src] = Reader(str((base / src).resolve()), fps)
            out = cover(brolls[src].at(g.get("src_start", 0) + t - g["start"]), g.get("zoom", 1.0), g.get("anchor", [.5, .5]))
            if cap: paste(out, caps.image(cap, False), W / 2, CAP_Y_FULL)
        else:
            out = cover(spk.at(t), g.get("zoom", full_cfg.get("zoom", 1.1)), g.get("anchor", full_cfg.get("anchor", [.5, .33])))
            # reel-13: his face and beard fill the middle and the mic sits on the chest, so the FULL caption
            # goes in the clear wall above his head (full.caption_y)
            if cap: paste(out, caps.image(cap, False), W / 2, full_cfg.get("caption_y", CAP_Y_FULL))
        return np.clip(out, 0, 255).astype(np.uint8)

    if a.stills or a.every:
        ts = [float(x) for x in a.stills.split(",")] if a.stills else list(np.arange(0, dur, a.every))
        os.makedirs(a.dir, exist_ok=True); ims = []
        for t in ts:
            im = Image.fromarray(frame(t)); im.save(f"{a.dir}/still_{t:06.2f}.png"); ims.append((t, im))
        if a.sheet:
            cols, tw = 6, 180; th = 320; rows = (len(ims) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * tw, rows * (th + 24)), (30, 30, 30)); d = ImageDraw.Draw(sheet)
            for i, (t, im) in enumerate(ims):
                x, y = (i % cols) * tw, (i // cols) * (th + 24)
                sheet.paste(im.resize((tw, th)), (x, y + 24)); d.text((x + 4, y + 4), f"{t:.1f}s", fill=(255, 220, 0))
            sheet.save(a.sheet, quality=88)
        print(f"{len(ims)} stills -> {a.dir}" + (f", sheet {a.sheet}" if a.sheet else ""))
        return

    end = a.end if a.end is not None else dur
    out = a.out or "out/kallaway.mp4"; os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    cmd = [FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-ss", f"{a.start:.3f}", "-t", f"{end - a.start:.3f}", "-i", rp("speaker"), "-map", "0:v", "-map", "1:a?",
           "-c:v", "libx264", "-crf", a.crf, "-preset", "veryfast", "-pix_fmt", "yuv420p", "-af", "apad", "-c:a", "aac", "-b:a", "256k",
           "-shortest", "-movflags", "+faststart", out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((end - a.start) * fps))
    for i in range(n):
        enc.stdin.write(frame(a.start + i / fps).tobytes())
        if i % (fps * 5) == 0: print(f"  {a.start + i / fps:6.1f}s / {end:.1f}s", file=sys.stderr)
    enc.stdin.close(); enc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
