#!/usr/bin/env python3
"""Vox-style parallax: make a still photo feel like video (2.5D camera move).

The trick Vox uses on historical photos: split one image into foreground, midground and
background layers, patch the areas each layer hid, space the layers out in depth and move
a camera slowly through them. Near layers slide more than far ones, so the still gets depth.
In After Effects that is Photoshop layers + clone stamp + the Depth plugin + a camera dolly.
Here it is one script:

  layers   image -> depth map (Depth Anything V2, local ONNX) -> N layers split by depth,
           edges refined to the photo, hidden areas filled, layers.json with each layer's depth.
           Optional crisp subject cut-out (rembg isnet) or your own hand-made masks.
  render   layers -> MP4 of a camera move (dolly in/out, pan, rise), pre-scaled so frame 0 is
           exactly the original photo and the edges never show.
  stills   a labelled contact sheet of the move, for the stills-first rule.

Usage
  python3 tools/parallax.py layers photo.jpg -o work/parallax/beach --n 3 --subject
  python3 tools/parallax.py render work/parallax/beach -o out/beach.mp4 --move dolly-in --dur 6
  python3 tools/parallax.py render work/parallax/beach -o out/beach.mp4 --dolly 0.25 --pan-x 0.04
  python3 tools/parallax.py stills work/parallax/beach -o out/beach_stills.png --move dolly-in --dur 6

Check work/parallax/<name>/split.png after `layers`: each layer gets a colour. If a cut is
wrong, move the cuts (--cuts 0.35,0.7 on the 0..1 nearness scale, see depth.png), use
--subject, or paint masks yourself and pass --masks front.png,mid.png (white = layer, front first).
Models: ~/.cache/vibe/depth/depth_anything_v2_vits.onnx (downloaded on first use from GitHub
releases; Hugging Face is blocked from this container) and rembg's isnet-general-use.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import urllib.request

import cv2
import numpy as np

DEPTH_URL = ("https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/"
             "v2.0.0/depth_anything_v2_vits.onnx")
DEPTH_PATH = os.path.expanduser("~/.cache/vibe/depth/depth_anything_v2_vits.onnx")


# ---------------------------------------------------------------- depth and masks
def depth_map(rgb):
    """Relative nearness 0..1 (1 = nearest) at the image's size."""
    import onnxruntime as ort
    if not os.path.exists(DEPTH_PATH):
        os.makedirs(os.path.dirname(DEPTH_PATH), exist_ok=True)
        print("downloading depth model (99 MB) ...", file=sys.stderr)
        urllib.request.urlretrieve(DEPTH_URL, DEPTH_PATH)
    sess = ort.InferenceSession(DEPTH_PATH, providers=["CPUExecutionProvider"])
    h, w = rgb.shape[:2]
    x = cv2.resize(rgb, (518, 518), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    d = sess.run(None, {sess.get_inputs()[0].name: x})[0][0]
    d = cv2.resize(d, (w, h), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, [1, 99.5])
    return np.clip((d - lo) / (hi - lo + 1e-6), 0, 1).astype(np.float32)


def subject_alpha(rgb):
    from rembg import new_session, remove
    from PIL import Image
    out = remove(Image.fromarray(rgb), session=new_session("isnet-general-use"),
                 only_mask=True, post_process_mask=True)
    return np.asarray(out).astype(np.float32) / 255


def guided(guide, p, r, eps):
    """He's guided filter: snaps a soft mask to the photo's edges."""
    box = lambda a: cv2.boxFilter(a, -1, (2 * r + 1, 2 * r + 1))
    mi, mp = box(guide), box(p)
    a = (box(guide * p) - mi * mp) / (box(guide * guide) - mi * mi + eps)
    b = mp - a * mi
    return box(a) * guide + box(b)


def clean_mask(m, min_frac=0.002):
    """Drop specks and fill pinholes in a 0..1 mask."""
    hard = (m > 0.5).astype(np.uint8)
    area = hard.size * min_frac
    n, lab, st, _ = cv2.connectedComponentsWithStats(hard, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= area
    hard = keep[lab].astype(np.uint8)
    inv = 1 - hard
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 8)
    small = np.zeros(n, bool)
    small[1:] = st[1:, cv2.CC_STAT_AREA] < area
    hard[small[lab]] = 1
    return hard.astype(np.float32)


def kmeans_cuts(d, n):
    v = d.ravel()[::7].reshape(-1, 1).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 1e-4)
    _, _, c = cv2.kmeans(v, n, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    c = np.sort(c.ravel())
    return [float((c[i] + c[i + 1]) / 2) for i in range(n - 1)]


def push_pull_fill(img, hole):
    """Fill hole pixels with a smooth pyramid average of the known ones (no smears)."""
    known = (1 - hole).astype(np.float32)[..., None]
    levels = [(img.astype(np.float32) * known, known)]
    while min(levels[-1][1].shape[:2]) > 4:
        c, k = levels[-1]
        c2 = cv2.pyrDown(c)
        k2 = cv2.pyrDown(k)
        if k2.ndim == 2:
            k2 = k2[..., None]
        levels.append((c2, k2))
    c, k = levels[-1]
    fill = c / np.maximum(k, 1e-6)
    mean = (levels[0][0].reshape(-1, 3).sum(0) / max(1e-6, float(levels[0][1].sum())))
    fill = np.where(k > 1e-3, fill, mean)  # coarsest level: empty cells get the known average
    for c, k in reversed(levels[:-1]):
        up = cv2.resize(fill, (c.shape[1], c.shape[0]), interpolation=cv2.INTER_LINEAR)
        kk = np.clip(k * 4, 0, 1)  # trust levels where coverage is good
        fill = np.where(k > 1e-3, c / np.maximum(k, 1e-6), up)
        fill = kk * fill + (1 - kk) * up
    out = img.astype(np.float32) * known + fill * (1 - known)
    return np.clip(out, 0, 255).astype(np.uint8)


def mirror_texture(rgb, hole8):
    """Clone-stamp stand-in: each hidden pixel takes the texture of the known pixel mirrored
    across the nearest hole edge, so sand, grass or brick keeps its grain inside the patch.
    Returns (texture, valid mask)."""
    h, w = hole8.shape
    _, lab = cv2.distanceTransformWithLabels(hole8, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ky, kx = np.nonzero(hole8 == 0)  # known pixels in label order (row-major scan)
    idx = np.clip(lab.astype(np.int64) - 1, 0, len(ky) - 1)
    yy, xx = np.indices((h, w))
    ny, nx = ky[idx], kx[idx]
    sy = np.clip(2 * ny - yy, 0, h - 1)
    sx = np.clip(2 * nx - xx, 0, w - 1)
    ok = hole8[sy, sx] == 0
    tex = rgb[sy, sx]
    return tex, ok


def fill_hidden(rgb, hole, grain=True):
    """Patch what a nearer layer covered (the clone-stamp step). Colour comes from a smooth
    fill (Telea at the rim, push-pull inside); detail and grain come from mirrored real texture."""
    hole8 = (hole > 0.5).astype(np.uint8)
    if not hole8.any() or hole8.all():
        return rgb.copy()
    h, w = hole8.shape
    s = min(1.0, 900 / max(h, w))
    small = cv2.resize(rgb, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    hs = cv2.resize(hole8, small.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    hs = cv2.dilate(hs, np.ones((3, 3), np.uint8))
    # old prints have dark borders and vignettes: don't let the edge strip colour the fill
    b = max(2, int(0.02 * max(hs.shape)))
    edge = np.zeros_like(hs)
    edge[:b], edge[-b:], edge[:, :b], edge[:, -b:] = 1, 1, 1, 1
    if (hs & (1 - edge)).any() and ((hs | edge) == 0).any():
        hs = hs | edge
    pp = push_pull_fill(small, hs)
    tel = cv2.inpaint(small, hs, 6, cv2.INPAINT_TELEA)
    rim = cv2.GaussianBlur(cv2.distanceTransform(hs, cv2.DIST_L2, 5), (0, 0), 2)
    wt = np.clip(rim / 12.0, 0, 1)[..., None]  # 0 at the rim (Telea) -> 1 inside (push-pull)
    filled = (tel * (1 - wt) + pp * wt).astype(np.uint8)
    low = cv2.resize(filled, (w, h), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    low = cv2.GaussianBlur(low, (0, 0), 3)
    up = low
    if grain:
        f = rgb.astype(np.float32)
        tex, ok = mirror_texture(rgb, hole8)
        tex = tex.astype(np.float32)
        detail = tex - cv2.GaussianBlur(tex, (0, 0), 3)
        # mirrored texture only near the hole edge (where slides reveal it); deep inside, mirrors
        # of mirrors turn into streaks, so fade to plain matched grain there
        dist = cv2.distanceTransform(hole8, cv2.DIST_L2, 5)
        near = np.clip(1.5 - dist / (0.05 * max(h, w)), 0, 1)
        okf = cv2.GaussianBlur(ok.astype(np.float32) * near, (0, 0), 2)[..., None]
        # fallback grain where the mirror landed in the hole: the photo's own grain level
        g = cv2.GaussianBlur(np.random.default_rng(1).normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.7)
        gy = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
        hp = gy - cv2.GaussianBlur(gy, (0, 0), 1.5)
        amp = float(np.std(hp[hole8 == 0])) * 0.7
        up = low + detail * okf + (g * amp)[..., None] * (1 - okf)
    m = cv2.GaussianBlur(hole8.astype(np.float32), (0, 0), 1.0)[..., None]
    out = rgb.astype(np.float32) * (1 - m) + up * m
    return np.clip(out, 0, 255).astype(np.uint8)


def codex_plate(src_path, remove, out_path):
    """Ask Codex (signed in with the user's ChatGPT account) to paint the clean plate: the photo with
    the named things removed and what was behind them filled in. Best fill there is: real sand,
    crowd and shadows instead of a patch. Takes about a minute."""
    import shutil
    d = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(d, exist_ok=True)
    src = os.path.join(d, "plate_src" + os.path.splitext(src_path)[1])
    shutil.copy(src_path, src)
    name = os.path.basename(out_path)
    prompt = (f"Generate an image: edit the attached photo. Remove {remove} completely and fill where they were "
              "with what would be behind them, matching the photo's grain, lighting, colour and perspective. Remove "
              "their shadows too. Keep everything else exactly the same: same framing, same size and aspect ratio, "
              f"every other object in the same place. Save it here as {name}")
    log = open(os.path.join(d, "codex_plate.log"), "w")
    r = subprocess.run(["codex", "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", prompt,
                        "-i", os.path.basename(src)], cwd=d, stdout=log, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL)
    if r.returncode or not os.path.exists(out_path):
        sys.exit(f"Codex plate failed (is Codex signed in? `codex login status`), see {d}/codex_plate.log")
    return out_path


def align_plate(rgb, plate, known):
    """Fit a plate (Codex or hand-made) onto the photo: resize, ECC affine alignment on the parts both
    share, then match each channel's mean and spread there so the patch blends in."""
    h, w = rgb.shape[:2]
    plate = cv2.resize(plate, (w, h), interpolation=cv2.INTER_AREA)
    s = min(1.0, 800 / max(h, w))
    g1 = cv2.resize(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), None, fx=s, fy=s).astype(np.float32) / 255
    g2 = cv2.resize(cv2.cvtColor(plate, cv2.COLOR_RGB2GRAY), None, fx=s, fy=s).astype(np.float32) / 255
    km = cv2.resize(known.astype(np.uint8), g1.shape[::-1], interpolation=cv2.INTER_NEAREST)
    M = np.eye(2, 3, dtype=np.float32)
    try:
        _, M = cv2.findTransformECC(g1, g2, M, cv2.MOTION_AFFINE,
                                    (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-5), km, 5)
        M[:, 2] /= s
        plate = cv2.warpAffine(plate, M, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                               borderMode=cv2.BORDER_REPLICATE)
    except cv2.error:
        print("plate alignment did not converge, using it as is", file=sys.stderr)
    k = known.astype(bool)
    out = plate.astype(np.float32)
    for c in range(3):
        a, b = rgb[..., c][k].astype(np.float32), out[..., c][k]
        out[..., c] = (out[..., c] - b.mean()) * (a.std() / (b.std() + 1e-6)) + a.mean()
    print(f"plate aligned: shift {M[0, 2]:.1f},{M[1, 2]:.1f} px", file=sys.stderr)
    return np.clip(out, 0, 255).astype(np.uint8)


def plate_fill(rgb, hole, plate):
    m = cv2.GaussianBlur((hole > 0.5).astype(np.float32), (0, 0), 1.5)[..., None]
    return np.clip(rgb * (1 - m) + plate.astype(np.float32) * m, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- layers
def cmd_layers(a):
    bgr = cv2.imread(a.image, cv2.IMREAD_COLOR)
    if bgr is None:
        sys.exit(f"cannot read {a.image}")
    h0, w0 = bgr.shape[:2]
    s = min(1.0, a.max / max(h0, w0))
    if s < 1:
        bgr = cv2.resize(bgr, (int(w0 * s), int(h0 * s)), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    os.makedirs(a.out, exist_ok=True)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    r = max(4, int(max(h, w) / 160))

    d = depth_map(rgb)
    cv2.imwrite(os.path.join(a.out, "depth.png"), (d * 255).astype(np.uint8))
    sub = None
    if a.masks:  # hand-made masks, front first
        fronts = []
        for p in a.masks.split(","):
            m = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
            fronts.append(cv2.resize(m, (w, h)).astype(np.float32) / 255)
        n = len(fronts) + 1
        # cumulative: everything at or nearer than layer k
        cum = []
        acc = np.zeros((h, w), np.float32)
        for m in fronts:
            acc = np.maximum(acc, m)
            cum.append(acc.copy())
        cum = cum[::-1]  # back-most front layer first
        cuts = None
        nearness = [float(np.median(d[m > 0.5])) if (m > 0.5).any() else 0.5 for m in fronts][::-1]
        nearness = [float(np.median(d))] + nearness
    else:
        sub = subject_alpha(rgb) if a.subject else None
        if sub is not None and not (sub > 0.5).any():
            print("no subject found, splitting by depth only", file=sys.stderr)
            sub = None
        nd = a.n - 1 if sub is not None else a.n  # depth layers (the subject is a layer of its own)
        free = d[sub < 0.5] if sub is not None else d
        cuts = [float(c) for c in a.cuts.split(",")] if a.cuts else kmeans_cuts(free, max(2, nd))
        # soft cumulative depth masks (edge-snapped), then each depth layer's own pixels
        cd = [np.ones((h, w), np.float32)]
        for c in cuts:
            soft = np.clip((d - c) / 0.04 + 0.5, 0, 1)
            cd.append(clean_mask(guided(gray, soft, r, 1e-3)))
        for k in range(len(cd) - 2, 0, -1):
            cd[k] = np.maximum(cd[k], cd[k + 1])
        cd.append(np.zeros((h, w), np.float32))
        edges = [0.0] + cuts + [1.0]
        entries = []  # (nearness, own mask)
        for j in range(len(cuts) + 1):
            own = np.clip(cd[j] - cd[j + 1], 0, 1)
            sel = (d >= edges[j]) & (d <= edges[j + 1])
            if sub is not None:
                own = own * (1 - sub)
                sel &= sub < 0.5
            entries.append((float(np.median(d[sel])) if sel.any() else (edges[j] + edges[j + 1]) / 2, own))
        if sub is not None:
            # a standing subject sits in front of the ground it stands on: rank it by its nearest
            # part (feet), not its middle
            sd = float(np.percentile(d[sub > 0.5], 95))
            entries.append((max(sd, entries[0][0] + 1e-3), sub))  # never the back plate
        entries.sort(key=lambda e: e[0])
        n = len(entries)
        nearness = [e[0] for e in entries]
        cum = []
        for p_ in range(1, n):  # layer p and everything nearer
            cum.append(np.clip(sum(e[1] for e in entries[p_:]), 0, 1))

    # soft final alphas: a light blur only (depth edges are already snapped, the subject is rembg's)
    alphas = [np.clip(cv2.GaussianBlur(m, (0, 0), 0.8), 0, 1).astype(np.float32) for m in cum]

    # layer 0 = back plate (opaque), hidden area filled; layer k = its own pixels plus a
    # filled band reaching under the next nearer layer, so slides reveal plausible content
    margin = int(max(h, w) * a.band)
    grow = np.ones((max(5, max(h, w) // 150),) * 2, np.uint8)  # hole margin so no outline ghosts stay
    layers = []
    plate = None
    if a.plate:  # a clean plate fills every layer's hidden area (Codex paints one with --plate codex)
        if a.plate == "codex":
            if not a.remove:
                sys.exit('--plate codex needs --remove "what to remove", e.g. "the bodybuilder and the wooden bench"')
            ppath = codex_plate(a.image, a.remove, os.path.join(os.path.abspath(a.out), "plate.png"))
        else:
            ppath = a.plate
        pr = cv2.cvtColor(cv2.imread(ppath), cv2.COLOR_BGR2RGB)
        known = cv2.dilate((alphas[0] > 0.02).astype(np.uint8), grow) == 0
        plate = align_plate(rgb, pr, known)
        cv2.imwrite(os.path.join(a.out, "plate_aligned.jpg"), cv2.cvtColor(plate, cv2.COLOR_RGB2BGR))
    fill = (lambda img, hole: plate_fill(img, hole, plate)) if plate is not None else fill_hidden
    back = fill(rgb, cv2.dilate((alphas[0] > 0.02).astype(np.uint8), grow))
    layers.append(np.dstack([back, np.full((h, w), 255, np.uint8)]))
    for k in range(len(alphas)):
        own = alphas[k]
        nxt = alphas[k + 1] if k + 1 < len(alphas) else None
        if nxt is None:
            rgbk, ak = rgb, own
        else:
            hole = cv2.dilate((nxt > 0.02).astype(np.uint8), grow)
            rgbk = fill(rgb, hole)
            own_only = np.clip(own - nxt, 0, 1)
            # grow this layer under the nearer one by `margin` px
            k_ = max(3, margin | 1)
            grown = cv2.dilate((own_only > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_, k_)))
            grown = cv2.GaussianBlur(grown.astype(np.float32), (0, 0), max(1, margin / 6))
            ak = np.maximum(own_only, np.minimum(grown, (nxt > 0.02).astype(np.float32)))
        layers.append(np.dstack([rgbk, (np.clip(ak, 0, 1) * 255).astype(np.uint8)]))

    # depth (distance) per layer: nearer = smaller z. z = 1/(0.25 + nearness), front scaled to 1
    zs = [1.0 / (0.25 + max(0.0, min(1.0, v))) for v in nearness]
    zs = [z / zs[-1] for z in zs]
    zs = [max(z, zs[i + 1] * 1.15) if i + 1 < len(zs) else z for i, z in enumerate(zs)]
    for i in range(len(zs) - 2, -1, -1):
        zs[i] = max(zs[i], zs[i + 1] * 1.15)
    if a.spread != 1.0:
        zs = [1.0 + (z - 1.0) * a.spread for z in zs]

    files = []
    for k, L in enumerate(layers):
        fn = f"layer_{k}.png"
        cv2.imwrite(os.path.join(a.out, fn), cv2.cvtColor(L, cv2.COLOR_RGBA2BGRA))
        files.append(fn)
    meta = {"source": os.path.abspath(a.image), "size": [w, h], "layers": files,
            "z": [round(z, 4) for z in zs], "nearness": [round(v, 4) for v in nearness],
            "cuts": cuts, "subject": bool(a.subject)}
    json.dump(meta, open(os.path.join(a.out, "layers.json"), "w"), indent=2)

    # split preview: photo tinted by layer, plus each layer on a checkerboard
    cols = [(60, 110, 255), (60, 220, 120), (255, 170, 40), (240, 60, 200), (60, 230, 230)]
    tint = rgb.astype(np.float32) * 0.45
    for k in range(n):
        own = layers[k][..., 3] / 255.0 if k else np.ones((h, w))
        if k + 1 < n:
            own = own * (1 - alphas[k] if k < len(alphas) else 1)
        tint += (own[..., None] * np.array(cols[k % 5]) * 0.55)
    tint = np.clip(tint, 0, 255).astype(np.uint8)
    tiles = [tint]
    cb = ((np.indices((h, w)).sum(0) // max(8, w // 40)) % 2 * 60 + 150).astype(np.uint8)
    for L in layers:
        al = L[..., 3:4] / 255.0
        tiles.append((L[..., :3] * al + cb[..., None] * (1 - al)).astype(np.uint8))
    th = 640
    tiles = [cv2.resize(t, (int(w * th / h), th)) for t in tiles]
    sheet = np.hstack([np.pad(t, ((0, 0), (0, 8), (0, 0)), constant_values=255) for t in tiles])
    cv2.imwrite(os.path.join(a.out, "split.png"), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
    print(json.dumps(meta, indent=2))


# ---------------------------------------------------------------- camera
PRESETS = {  # dolly = fraction of the front layer's distance travelled; pan = front layer slide (frame widths)
    "dolly-in": dict(dolly=0.22),
    "dolly-out": dict(dolly=-0.22),
    "pan-left": dict(pan_x=-0.05, dolly=0.06),
    "pan-right": dict(pan_x=0.05, dolly=0.06),
    "rise": dict(pan_y=-0.05, dolly=0.06),
    "fall": dict(pan_y=0.05, dolly=0.06),
    "drift": dict(dolly=0.12, pan_x=0.03),
}


def ease(u, kind):
    if kind == "linear":
        return u
    if kind == "out":
        return 1 - (1 - u) ** 2
    if kind == "in":
        return u * u
    return 0.5 - 0.5 * math.cos(math.pi * u)  # inout (sine): Vox moves are slow and soft


def load(dirp):
    meta = json.load(open(os.path.join(dirp, "layers.json")))
    layers = [cv2.cvtColor(cv2.imread(os.path.join(dirp, f), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
              for f in meta["layers"]]
    return meta, layers


def camera(a):
    p = dict(dolly=0.0, pan_x=0.0, pan_y=0.0)
    if a.move:
        p.update(PRESETS[a.move])
    for k in ("dolly", "pan_x", "pan_y"):
        v = getattr(a, k)
        if v is not None:
            p[k] = v
    if a.strength != 1.0:
        p = {k: v * a.strength for k, v in p.items()}
    return p


def transforms(meta, cam, u, W, H, extra_zoom=1.0):
    """Per-layer (scale, dx, dy) mapping centred source px -> centred screen px at progress u."""
    w, h = meta["size"]
    fit = max(W / w, H / h) * extra_zoom
    zf = meta["z"][-1]
    if cam["dolly"] >= 0:
        cz0, cz1 = 0.0, cam["dolly"] * zf
    else:  # dolly out: start pushed in, end at the original framing
        cz0, cz1 = -cam["dolly"] * zf, 0.0
    cz = cz0 + (cz1 - cz0) * u
    out = []
    for z in meta["z"]:
        sc = z / (z - cz)
        # pan: the front layer slides pan*W over the shot; others slide less by 1/z
        dx = -(cam["pan_x"] * W) * (u - 0.5) * (zf / (z - cz))
        dy = -(cam["pan_y"] * H) * (u - 0.5) * (zf / (z - cz))
        out.append((fit * sc, dx, dy))
    return out


def needed_zoom(meta, cam, W, H, n=40):
    """Smallest extra zoom so no layer edge ever enters the frame (layers that cover the whole
    photo); computed over the whole move."""
    w, h = meta["size"]
    z = 1.0
    for i in range(n + 1):
        for sc, dx, dy in transforms(meta, cam, i / n, W, H):
            # screen half-extent of layer = sc*w/2 ; needs >= W/2 + |dx|
            z = max(z, (W / 2 + abs(dx)) / (sc * w / 2), (H / 2 + abs(dy)) / (sc * h / 2))
    return z * 1.002


def render_frame(layers, meta, cam, u, W, H, zoom, blur_back=0.0):
    w, h = meta["size"]
    acc = np.zeros((H, W, 3), np.float32)
    for k, (L, (sc, dx, dy)) in enumerate(zip(layers, transforms(meta, cam, u, W, H, zoom))):
        M = np.array([[sc, 0, W / 2 + dx - sc * w / 2], [0, sc, H / 2 + dy - sc * h / 2]], np.float32)
        warped = cv2.warpAffine(L, M, (W, H), flags=cv2.INTER_LINEAR if sc < 1.5 else cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        col = warped[..., :3].astype(np.float32)
        if k == 0 and blur_back > 0:
            col = cv2.GaussianBlur(col, (0, 0), blur_back)
        al = warped[..., 3:4].astype(np.float32) / 255
        acc = col * al + acc * (1 - al) if k else col
    return np.clip(acc, 0, 255).astype(np.uint8)


def cmd_render(a):
    meta, layers = load(a.dir)
    W, H = map(int, a.size.split("x"))
    cam = camera(a)
    zoom = needed_zoom(meta, cam, W, H)
    nfr = int(round(a.dur * a.fps))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(a.fps), "-i", "-", "-c:v", "libx264", "-crf", str(a.crf), "-preset", "veryfast",
           "-pix_fmt", "yuv420p", a.out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nfr):
        u = ease(i / max(1, nfr - 1), a.ease)
        pr.stdin.write(render_frame(layers, meta, cam, u, W, H, zoom, a.blur_back).tobytes())
    pr.stdin.close()
    pr.wait()
    print(f"{a.out}: {nfr} frames, camera {cam}, edge-safe zoom {zoom:.3f}")


def cmd_stills(a):
    meta, layers = load(a.dir)
    W, H = map(int, a.size.split("x"))
    cam = camera(a)
    zoom = needed_zoom(meta, cam, W, H)
    times = [float(t) for t in a.times.split(",")] if a.times else [0, a.dur / 2, a.dur]
    tiles = []
    for t in times:
        u = ease(min(1, t / a.dur), a.ease)
        f = render_frame(layers, meta, cam, u, W, H, zoom, a.blur_back)
        f = cv2.resize(f, (W * 480 // H, 480))
        cv2.putText(f, f"{t:.2f}s", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
        cv2.putText(f, f"{t:.2f}s", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 230, 0), 2)
        tiles.append(np.pad(f, ((0, 0), (0, 6), (0, 0)), constant_values=255))
    cv2.imwrite(a.out, cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR))
    print(a.out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("layers")
    l.add_argument("image")
    l.add_argument("-o", "--out", required=True)
    l.add_argument("--n", type=int, default=3, help="number of layers (2-5)")
    l.add_argument("--cuts", help="nearness cut points 0..1, back to front, e.g. 0.35,0.7")
    l.add_argument("--subject", action="store_true", help="cut the main subject cleanly with rembg isnet")
    l.add_argument("--masks", help="your own masks, front first, comma separated (white = layer)")
    l.add_argument("--plate", help='clean plate for the hidden areas: "codex" (Codex paints it, needs --remove) or an image path')
    l.add_argument("--remove", help='with --plate codex: what Codex removes, e.g. "the bodybuilder and the wooden bench"')
    l.add_argument("--band", type=float, default=0.10, help="how far each layer reaches under the next (fraction of size)")
    l.add_argument("--spread", type=float, default=1.0, help="exaggerate (>1) or flatten (<1) the depth spacing")
    l.add_argument("--max", type=int, default=2600, help="longest side to work at")
    l.set_defaults(fn=cmd_layers)
    for name, fn in (("render", cmd_render), ("stills", cmd_stills)):
        r = sp.add_parser(name)
        r.add_argument("dir")
        r.add_argument("-o", "--out", required=True)
        r.add_argument("--size", default="1080x1920")
        r.add_argument("--dur", type=float, default=6.0)
        r.add_argument("--fps", type=float, default=30)
        r.add_argument("--move", choices=sorted(PRESETS), default="dolly-in")
        r.add_argument("--dolly", type=float, help="camera travel as a fraction of the front layer's distance (+ in, - out)")
        r.add_argument("--pan-x", dest="pan_x", type=float, help="front layer slide in frame widths (+ = camera right)")
        r.add_argument("--pan-y", dest="pan_y", type=float, help="front layer slide in frame heights (+ = camera down)")
        r.add_argument("--strength", type=float, default=1.0, help="scale the whole move")
        r.add_argument("--ease", choices=["inout", "linear", "in", "out"], default="inout")
        r.add_argument("--blur-back", dest="blur_back", type=float, default=0.0, help="soft depth of field on the back plate (px)")
        r.add_argument("--crf", type=int, default=16)
        r.add_argument("--times", help="stills only: comma separated seconds")
        r.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
