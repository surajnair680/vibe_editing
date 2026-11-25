"""reel-15 ZAZI coat season promo, 1920x1080 25 fps.

python3 scene.py stills out/stills_v1 0,2.5,5,7.5,10      # PNG per time + contact sheet
python3 scene.py render out/draft.mp4 0 10 --scale 0.5     # draft (half size) of a range
python3 scene.py render out/master.mp4 0 25                # full quality

Shots come from tools/parallax.py layers (work/parallax/<shot>/). Cuts sit on the music's beats
(m1: one beat a second, from 0.07 s). Every cut is a soft 0.6 s dissolve centred on the beat.
Brand look: Tenor Sans uppercase with wide tracking, Outfit Light for small lines, cream text.
Photos keep their own colours: no grade, no grain.
"""
import math, os, subprocess, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '..', '..', 'tools'))
import parallax as px  # shared tool

W, H, FPS = 1920, 1080, 25
CREAM = (251, 248, 244)
INK = (38, 36, 40)
FONT_T = os.path.join(ROOT, 'assets/fonts/TenorSans-400.ttf')
FONT_O = os.path.join(ROOT, 'assets/fonts/Outfit-300.ttf')
XF = 0.6  # dissolve length

# shot: name, start, end, camera, focus (0..1 of photo)
SHOTS = [
    dict(name='hero', a=0.0, b=4.0, cam=dict(dolly=0.07, pan_x=0.0, pan_y=0.0), focus=(0.45, 0.16)),
    dict(name='hang', a=4.0, b=6.0, flat='assets/wide/hang.jpg', z=(1.02, 1.07), focus=(0.48, 0.45)),
    dict(name='spin', a=6.0, b=8.0, flat='assets/wide/spin.jpg', z=(1.02, 1.08), focus=(0.68, 0.35)),
    dict(name='pair', a=8.0, b=10.0, flat='assets/wide/pair.jpg', z=(1.07, 1.02), focus=(0.45, 0.35)),
    dict(name='coats', a=10.0, b=18.0, coats=True),
    dict(name='shop', a=18.0, b=25.0 + XF / 2, flat='assets/wide/shop.jpg', z=(1.0, 1.10), focus=(0.62, 0.45)),
]
PINK = (248, 240, 240)  # studio backdrop of the product photos
# coat run: (front, back, line); one pair every 2 s on the beat, gliding like a rail
COATS = [
    ('Correct_0017_ZAZI_Afghan_Coat34.jpg', 'Correct_0024_ZAZI_Afghan_Coat27.jpg', 'THE ZEBAY COAT'),
    ('Correct_0028_ZAZI_Afghan_Coat23.jpg', 'Correct_0029_ZAZI_Afghan_Coat22.jpg', 'THE MADINA COAT'),
    ('Correct_0001_Laag1.jpg', 'Correct_0034_ZAZI_Afghan_Coat17.jpg', 'EMBROIDERED BY HAND'),
    ('Correct_0049_ZAZI_Afghan_Coat2.jpg', 'Correct_0048_ZAZI_Afghan_Coat3.jpg', 'PIECES FOR A LIFETIME'),
]
STEPS = [10.0, 12.0, 14.0, 16.0, 18.0]
END = 21.3  # end card: the boutique softens and darkens, the gold logo arrives

# text: lines, font, size, tracking, centre x,y (0..1), in, out, stagger per letter
TEXTS = [
    dict(s="FALL / WINTER '26", font=FONT_O, size=30, track=12, x=0.80, y=0.365, t0=0.3, t1=3.55, stag=0.0),
    dict(s="IT'S COAT", font=FONT_T, size=84, track=16, x=0.80, y=0.46, t0=0.7, t1=3.55, stag=0.07),
    dict(s="SEASON", font=FONT_T, size=84, track=16, x=0.80, y=0.56, t0=1.2, t1=3.55, stag=0.07),
    dict(s="HANDMADE.", font=FONT_T, size=40, track=10, x=0.19, y=0.30, t0=4.35, t1=5.6, stag=0.04),
    dict(s="ONE OF A KIND.", font=FONT_T, size=40, track=10, x=0.19, y=0.36, t0=4.7, t1=5.6, stag=0.04),
    dict(s="FROM HER HANDS", font=FONT_T, size=64, track=14, x=0.27, y=0.84, t0=6.35, t1=7.6, stag=0.045),
    dict(s="TO YOURS", font=FONT_T, size=64, track=14, x=0.80, y=0.10, t0=8.35, t1=9.3, stag=0.06),
    dict(s="VISIT US", font=FONT_T, size=56, track=14, x=0.5, y=0.84, t0=18.35, t1=20.8, stag=0.05),
    dict(s="HERENGRACHT 394, AMSTERDAM", font=FONT_O, size=30, track=8, x=0.5, y=0.905, t0=18.8, t1=20.8, stag=0.0),
    dict(s="LIMITED DROPS EVERY MONTH", font=FONT_T, size=34, track=12, x=0.5, y=0.68, t0=22.5, t1=30, stag=0.03),
    dict(s="theworldofzazi.com", font=FONT_O, size=30, track=4, x=0.5, y=0.75, t0=23.2, t1=30, stag=0.0),
]

_cache = {}


def shot_data(name):
    if name not in _cache:
        meta, layers = px.load(os.path.join(ROOT, 'work/parallax', name))
        _cache[name] = (meta, layers)
    return _cache[name]


def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def render_flat(sh, t, Wr, Hr):
    """Slow camera push / pull on the whole photo (used where a cut-out would show halos)."""
    key = ('flat', sh['flat'])
    if key not in _cache:
        _cache[key] = cv2.cvtColor(cv2.imread(os.path.join(ROOT, sh['flat'])), cv2.COLOR_BGR2RGB)
    img = _cache[key]; h, w = img.shape[:2]
    a, b = sh['a'] - XF / 2, sh['b'] + XF / 2
    u = px.ease(min(1, max(0, (t - a) / (b - a))), 'inout')
    z = sh['z'][0] + (sh['z'][1] - sh['z'][0]) * u
    sc = max(Wr / w, Hr / h) * z
    fx, fy = sh['focus'][0] * w, sh['focus'][1] * h
    # keep the focus point where it sits at zoom 1, clamp so edges never show
    tx = Wr / 2 + (fx - w / 2) * max(Wr / w, Hr / h) - fx * sc
    ty = Hr / 2 + (fy - h / 2) * max(Wr / w, Hr / h) - fy * sc
    tx = min(0, max(Wr - w * sc, tx)); ty = min(0, max(Hr - h * sc, ty))
    M = np.array([[sc, 0, tx], [0, sc, ty]], np.float32)
    return cv2.warpAffine(img, M, (Wr, Hr), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32)


def coat_img(f, Hc):
    key = ('coat', f, Hc)
    if key not in _cache:
        im = cv2.cvtColor(cv2.imread(os.path.join(ROOT, 'refs/site/img', f)), cv2.COLOR_BGR2RGB).astype(np.float32)
        corner = np.median(np.concatenate([im[:20, :20].reshape(-1, 3), im[:20, -20:].reshape(-1, 3)]), 0)
        im = im * (np.array(PINK, np.float32) / corner)  # match each photo's backdrop to the canvas
        h, w = im.shape[:2]; Wc = int(round(w * Hc / h))
        im = cv2.resize(im, (Wc, Hc), interpolation=cv2.INTER_AREA)
        # key the coat off its plain studio backdrop (soft ramp keeps fur edges and the soft shadow)
        dist = np.abs(im - np.array(PINK, np.float32)).max(2)
        m = np.clip((cv2.GaussianBlur(dist, (0, 0), 1.5) - 4) / 10, 0, 1)
        m = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5), np.uint8)), (0, 0), 2)
        e = Hc // 30; edge = np.zeros_like(m); edge[e:-e, e:-e] = 1
        m = m * cv2.GaussianBlur(edge, (0, 0), e / 2)
        _cache[key] = (im, m)
    return _cache[key]


def paste(canvas, im, m, cx, cy, alpha):
    if alpha <= 0:
        return
    Hr, Wr = canvas.shape[:2]; h, w = m.shape
    x, y = int(round(cx - w / 2)), int(round(cy - h / 2))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(Wr, x + w), min(Hr, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    a = m[y0 - y:y1 - y, x0 - x:x1 - x, None] * alpha
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + im[y0 - y:y1 - y, x0 - x:x1 - x] * a


def rail_pos(t):
    """-1 before the run, 0..3 = coat pair on screen, 4 = gone; each step glides over 0.8 s on its beat."""
    return -1 + sum(smooth((t - (T - 0.4)) / 0.8) for T in STEPS)


def render_coats(t, Wr, Hr, scale):
    canvas = np.empty((Hr, Wr, 3), np.float32); canvas[:] = PINK
    p = rail_pos(t)
    Hc = int(Hr * 0.98)
    for k, (fr, bk, line) in enumerate(COATS):
        d = k - p
        if abs(d) >= 1:
            continue
        al = 1 - smooth(abs(d))
        imf, mf = coat_img(fr, Hc); imb, mb = coat_img(bk, Hc)
        cy = Hr * 0.56
        paste(canvas, imf, mf, Wr * (0.315 + 0.30 * d), cy, al)
        paste(canvas, imb, mb, Wr * (0.685 + 0.42 * d), cy, al)  # the back glides a little further: depth
        spec = dict(s=line, font=FONT_T, size=40, track=12, x=0.5 + 0.18 * d, y=0.085, t0=-9, t1=99, stag=0, col='ink')
        lay = draw_text(canvas.copy(), spec, 0, scale)
        ta = 1 - smooth(abs(d) / 0.5)  # the line only shows while its pair has arrived
        canvas = canvas * (1 - ta) + lay * ta
    return canvas


def shop_shade(f, t):
    """Soft darkening at the bottom of the boutique shot while its text is up."""
    if not 18.0 < t < 21.5:
        return f
    Hr = f.shape[0]
    a = smooth((t - 18.0) / 0.6) * (1 - smooth((t - 20.8) / 0.5))
    y = np.linspace(0, 1, Hr)[:, None, None]
    return f * (1 - np.clip((y - 0.62) / 0.38, 0, 1) ** 1.3 * 0.55 * a)


def end_card(f, t, scale):
    """Boutique softens and darkens; gold logo arrives with a light passing across it."""
    if t < END - 0.3:
        return f
    Hr, Wr = f.shape[:2]
    k = smooth((t - (END - 0.3)) / 1.0)
    soft = cv2.GaussianBlur(f, (0, 0), 1 + 22 * scale * k)
    f = soft * (1 - 0.62 * k) + np.array(INK, np.float32) * 0.62 * k * 0.6
    key = ('logo', scale)
    if key not in _cache:
        lg = cv2.imread(os.path.join(ROOT, 'refs/site/img/zazi_golden.png'), cv2.IMREAD_UNCHANGED)
        lg = cv2.cvtColor(lg, cv2.COLOR_BGRA2RGBA).astype(np.float32)
        w = int(Wr * 0.36); h = int(lg.shape[0] * w / lg.shape[1])
        _cache[key] = cv2.resize(lg, (w, h), interpolation=cv2.INTER_AREA)
    lg = _cache[key]
    la = smooth((t - END) / 1.1)
    if la <= 0:
        return f
    sc = 1.04 - 0.04 * smooth((t - END) / 2.5)
    h, w = lg.shape[:2]
    lgs = cv2.resize(lg, (int(w * sc), int(h * sc)), interpolation=cv2.INTER_LINEAR)
    rgb, a = lgs[..., :3].copy(), lgs[..., 3] / 255 * la
    # light sweep: a soft diagonal band crosses the gold once
    u = (t - (END + 0.5)) / 1.4
    if 0 < u < 1:
        hh, ww = a.shape
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        pos = (xx + 0.35 * yy) / (ww + 0.35 * hh)
        band = np.exp(-((pos - (u * 1.3 - 0.15)) / 0.07) ** 2)
        rgb = rgb + (255 - rgb) * band[..., None] * 0.55
    paste(f, rgb, a, Wr / 2, Hr * 0.47, 1.0)
    return f


def render_shot(sh, t, Wr, Hr, scale=1.0):
    if sh.get('coats'):
        return render_coats(t, Wr, Hr, scale)
    if 'flat' in sh:
        return render_flat(sh, t, Wr, Hr)
    meta, layers = shot_data(sh['name'])
    cam = dict(sh['cam']); cam['focus'] = sh['focus']
    key = ('zoom', sh['name'], Wr)
    if key not in _cache:
        _cache[key] = px.needed_zoom(meta, cam, Wr, Hr)
    a, b = sh['a'] - XF / 2, sh['b'] + XF / 2
    u = px.ease(min(1, max(0, (t - a) / (b - a))), 'inout')
    return px.render_frame(layers, meta, cam, u, Wr, Hr, _cache[key]).astype(np.float32)


def letters(spec, scale):
    """Per-letter RGBA sprites (cream) and their x offsets, centred line."""
    key = ('txt', spec['s'], scale)
    if key in _cache:
        return _cache[key]
    f = ImageFont.truetype(spec['font'], max(8, round(spec['size'] * scale)))
    tr = spec['track'] * scale
    xs, ws = [], []
    x = 0.0
    for ch in spec['s']:
        xs.append(x)
        w = f.getlength(ch)
        ws.append(w)
        x += w + tr
    total = x - tr
    asc, desc = f.getmetrics()
    hh = asc + desc
    pad = int(20 * scale) + 4
    sprites = []
    for ch, x0 in zip(spec['s'], xs):
        im = Image.new('L', (int(f.getlength(ch)) + 2 * pad, hh + 2 * pad), 0)
        ImageDraw.Draw(im).text((pad, pad), ch, font=f, fill=255)
        sprites.append((np.asarray(im, np.float32) / 255, x0 - total / 2 - pad, -hh / 2 - pad))
    _cache[key] = sprites
    return sprites


def draw_text(frame, spec, t, scale):
    if t < spec['t0'] or t > spec['t1'] + 0.5:
        return frame
    Hr, Wr = frame.shape[:2]
    cx, cy = spec['x'] * Wr, spec['y'] * Hr
    out_a = 1 - smooth((t - spec['t1']) / 0.5)
    alpha_layer = np.zeros((Hr, Wr), np.float32)
    for i, (m, ox, oy) in enumerate(letters(spec, scale)):
        a = smooth((t - spec['t0'] - i * spec['stag']) / 0.7) * out_a
        if a <= 0:
            continue
        x, y = int(round(cx + ox)), int(round(cy + oy))
        h, w = m.shape
        x0, y0, x1, y1 = max(0, x), max(0, y), min(Wr, x + w), min(Hr, y + h)
        if x1 <= x0 or y1 <= y0:
            continue
        sub = m[y0 - y:y1 - y, x0 - x:x1 - x] * a
        alpha_layer[y0:y1, x0:x1] = np.maximum(alpha_layer[y0:y1, x0:x1], sub)
    if alpha_layer.max() <= 0:
        return frame
    # soft shadow for legibility on photos (never a box)
    col = INK if spec.get('col') == 'ink' else CREAM
    if col == CREAM:
        sh = cv2.GaussianBlur(alpha_layer, (0, 0), 10 * scale + 1) * 0.55
        frame = frame * (1 - sh[..., None])
    else:  # ink on a light area: a faint light glow keeps it clean
        sh = cv2.GaussianBlur(alpha_layer, (0, 0), 14 * scale + 1) * 0.35
        frame = frame * (1 - sh[..., None]) + 255 * sh[..., None]
    frame = frame * (1 - alpha_layer[..., None]) + np.array(col, np.float32) * alpha_layer[..., None]
    return frame


def door_shade(frame, t):
    """Very soft darkening of the red door behind the hero title so cream type reads (fades with it)."""
    if t > 4.2:
        return frame
    Hr, Wr = frame.shape[:2]
    a = 1 - smooth((t - 3.55) / 0.5)
    yy, xx = np.mgrid[0:Hr, 0:Wr].astype(np.float32)
    d = ((xx / Wr - 0.80) / 0.24) ** 2 + ((yy / Hr - 0.47) / 0.30) ** 2
    g = np.exp(-d * 1.6) * 0.30 * a
    return frame * (1 - g[..., None])


def frame_at(t, scale=1.0):
    Wr, Hr = int(W * scale), int(H * scale)
    act = [s for s in SHOTS if s['a'] - XF / 2 <= t < s['b'] + XF / 2]
    if not act:
        f = np.full((Hr, Wr, 3), CREAM, np.float32)
    else:
        f = None
        for s in act:
            img = render_shot(s, t, Wr, Hr, scale)
            if f is None:
                f = img
            else:  # dissolve centred on the cut
                w = smooth((t - (s['a'] - XF / 2)) / XF)
                f = f * (1 - w) + img * w
        if t < SHOTS[0]['a'] + 0.0:
            pass
    f = door_shade(f, t)
    f = shop_shade(f, t)
    f = end_card(f, t, scale)
    for spec in TEXTS:
        f = draw_text(f, spec, t, scale)
    return np.clip(f, 0, 255).astype(np.uint8)


def cmd_stills(outdir, times):
    os.makedirs(outdir, exist_ok=True)
    tiles = []
    for t in times:
        fr = frame_at(t)
        cv2.imwrite(os.path.join(outdir, f't_{t:05.2f}.png'), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
        sm = cv2.resize(fr, (640, 360), interpolation=cv2.INTER_AREA)
        sm = cv2.cvtColor(sm, cv2.COLOR_RGB2BGR)
        cv2.putText(sm, f'{t:.1f}s', (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4)
        cv2.putText(sm, f'{t:.1f}s', (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 220, 255), 2)
        tiles.append(np.pad(sm, ((4, 4), (4, 4), (0, 0)), constant_values=255))
    cols = 3
    while len(tiles) % cols:
        tiles.append(np.full_like(tiles[0], 255))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(os.path.join(outdir, 'contact.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])


def cmd_render(out, a, b, scale=1.0, crf=14):
    Wr, Hr = int(W * scale), int(H * scale)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{Wr}x{Hr}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-crf', str(crf), '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
           '-g', str(FPS), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n0, n1 = int(round(a * FPS)), int(round(b * FPS))
    for n in range(n0, n1):
        p.stdin.write(frame_at(n / FPS, scale).tobytes())
    p.stdin.close(); p.wait()
    print(out, n1 - n0, 'frames')


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'stills':
        cmd_stills(sys.argv[2], [float(x) for x in sys.argv[3].split(',')])
    elif c == 'render':
        sc = float(sys.argv[sys.argv.index('--scale') + 1]) if '--scale' in sys.argv else 1.0
        cmd_render(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sc, 23 if sc < 1 else 14)
