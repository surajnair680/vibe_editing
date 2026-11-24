// Photo parallax for canvas pages (vox-explainer and any window.seek(t) page). Same camera maths as
// tools/parallax.py, so a shot looks the same in a page as in a render.
//
// Make the layers:  python3 tools/parallax.py layers photo.jpg -o <page>/assets/parallax/<key> --n 4 --subject \
//                       --plate codex --remove "..." --web 1600
// In the page:      <script src="parallax.js"></script>
//                   <script src="assets/parallax/<key>/layers.js"></script>
//                   await Parallax.load('<key>', 'assets/parallax/<key>/');            // in window.ready
//                   Parallax.draw(x, '<key>', u, {dolly: .22, focus: [.5, .3]}, rx, ry, rw, rh);  // u = 0..1
// focus: the point the camera pushes toward (0..1 of the photo). Put it on the face so a push-in never crops it.
//
// u is the move's progress (0..1); ease it yourself. Keep the camera smooth (real time, not twos): Vox steps its
// graphics on twos but the photo move is a smooth camera. The original framing shows at the start of a dolly-in,
// the end of a dolly-out and the middle of a pan. Edges never show (the extra zoom is computed for the whole move).
(function () {
  const sets = {};
  const loadImg = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.onerror = () => r(null); i.src = src; });

  function cam(c) {
    const p = Object.assign({ dolly: 0, panX: 0, panY: 0, focus: [.5, .5] }, c || {});
    const k = p.strength == null ? 1 : p.strength;
    return { dolly: p.dolly * k, panX: p.panX * k, panY: p.panY * k, focus: p.focus };
  }

  // per layer [scale, dx, dy] mapping centred layer px -> centred rect px
  function transforms(m, c, u, rw, rh, zoom) {
    const [w, h] = m.size, fit = Math.max(rw / w, rh / h) * zoom, zf = m.z[m.z.length - 1];
    const cz0 = c.dolly >= 0 ? 0 : -c.dolly * zf, cz1 = c.dolly >= 0 ? c.dolly * zf : 0;
    const cz = cz0 + (cz1 - cz0) * u;
    return m.z.map(z => {
      const sc = z / (z - cz), k = zf / (z - cz);
      // push toward the focus point (0..1 in the photo): it stays put while the rest grows around it
      const fx = (c.focus[0] - .5) * w * fit, fy = (c.focus[1] - .5) * h * fit;
      return [fit * sc, -c.panX * rw * (u - .5) * k + fx * (1 - sc), -c.panY * rh * (u - .5) * k + fy * (1 - sc)];
    });
  }

  function neededZoom(m, c, rw, rh) {
    const [w, h] = m.size;
    let z = 1;
    for (let i = 0; i <= 40; i++)
      for (const [sc, dx, dy] of transforms(m, c, i / 40, rw, rh, 1))
        z = Math.max(z, (rw / 2 + Math.abs(dx)) / (sc * w / 2), (rh / 2 + Math.abs(dy)) / (sc * h / 2));
    return z * 1.002;
  }

  window.Parallax = {
    async load(key, base) {
      const m = (window.PARALLAX || {})[key];
      if (!m) throw new Error('Parallax: include assets/parallax/' + key + '/layers.js first');
      const imgs = await Promise.all(m.files.map(f => loadImg(base + f)));
      sets[key] = { m, imgs, zooms: {} };
      return sets[key];
    },
    // draw the shot into the rectangle (rx, ry, rw, rh) on context x, clipped to it
    draw(x, key, u, camera, rx, ry, rw, rh) {
      const S = sets[key];
      if (!S) return;
      const c = cam(camera), id = [c.dolly, c.panX, c.panY, c.focus, rw, rh].join(',');
      const zoom = S.zooms[id] || (S.zooms[id] = neededZoom(S.m, c, rw, rh));
      const [w, h] = S.m.size;
      x.save();
      x.beginPath(); x.rect(rx, ry, rw, rh); x.clip();
      x.imageSmoothingQuality = 'high';
      transforms(S.m, c, Math.max(0, Math.min(1, u)), rw, rh, zoom).forEach(([sc, dx, dy], i) => {
        const im = S.imgs[i];
        if (im) x.drawImage(im, rx + rw / 2 + dx - sc * w / 2, ry + rh / 2 + dy - sc * h / 2, sc * w, sc * h);
      });
      x.restore();
    },
    presets: {
      'dolly-in': { dolly: .22 }, 'dolly-out': { dolly: -.22 }, 'pan-left': { panX: -.05, dolly: .06 },
      'pan-right': { panX: .05, dolly: .06 }, rise: { panY: -.05, dolly: .06 }, fall: { panY: .05, dolly: .06 },
      drift: { dolly: .12, panX: .03 },
    },
  };
})();
