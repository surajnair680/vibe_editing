// Kallaway-style panel kit: every frame is drawn from the time alone, so tools/seek_render.mjs can render it.
// Mark up the page with data attributes (all times are seconds on the edit timeline):
//   <section class="k-scene dark|light" data-start="0" data-end="3.2">   visible only in [start, end)
//   data-in="1.25" data-anim="rise|pop|blur|fade|draw|wipe|type|underline" [data-dur="0.3"]   entrance
//   data-states='[[0,"blur"],[4.1,"on"],[9.2,"done"]]'   upcoming / active / done (tracker rows, list items)
//   data-cam='[[0,1,0,0],[2.4,1.6,-180,120]]'   on .k-canvas: [time, scale, x, y], eased between keys
//   data-camblur="1"   motion blur on fast camera moves (whip pans)
//   data-count="11000,44000,2.0,0.8" data-fmt="k"   number counts from a to b, starting at t, over dur
// Open the page with ?t=2.5 to see one frame in a browser; ?guides=1 shows the speaker strip area.
(function () {
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const E = {
    outCubic: x => 1 - Math.pow(1 - x, 3),
    inOutCubic: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
    outBack: x => { const c1 = 1.2, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
    outExpo: x => x === 1 ? 1 : 1 - Math.pow(2, -10 * x),
  };
  const DUR = { rise: .25, pop: .3, blur: .3, fade: .25, draw: .45, wipe: .3, type: 0, underline: .35 };
  const STATE = {
    hidden: { o: 0, b: 0, s: 1 }, blur: { o: .4, b: 8, s: 1 }, on: { o: 1, b: 0, s: 1.04 },
    done: { o: .55, b: 0, s: 1 }, plain: { o: 1, b: 0, s: 1 },
  };
  const num = (el, k, d) => el.dataset[k] !== undefined ? parseFloat(el.dataset[k]) : d;

  let scenes = [], animEls = [], stateEls = [], cams = [], counts = [];

  function init() {
    scenes = [...document.querySelectorAll('.k-scene')];
    animEls = [...document.querySelectorAll('[data-in]')];
    stateEls = [...document.querySelectorAll('[data-states]')].map(el => ({ el, st: JSON.parse(el.dataset.states) }));
    cams = [...document.querySelectorAll('[data-cam]')].map(el => ({ el, keys: JSON.parse(el.dataset.cam), blur: el.dataset.camblur }));
    counts = [...document.querySelectorAll('[data-count]')].map(el => {
      const [a, b, t, d] = el.dataset.count.split(',').map(Number); return { el, a, b, t, d, fmt: el.dataset.fmt };
    });
    animEls.forEach(el => {
      if (el.dataset.anim === 'type') { el.dataset.full = el.textContent; }
      if (el.dataset.anim === 'draw' && el.getTotalLength) { const L = el.getTotalLength(); el.style.strokeDasharray = L; el.dataset.len = L; }
    });
    window.KDUR = Math.max(0, ...scenes.map(s => num(s, 'end', 0)));
  }

  function camAt(keys, t) {
    if (t <= keys[0][0]) return keys[0].slice(1);
    for (let i = 0; i < keys.length - 1; i++) {
      const [t0, ...a] = keys[i], [t1, ...b] = keys[i + 1];
      if (t < t1) { const u = E.inOutCubic(clamp((t - t0) / (t1 - t0))); return a.map((v, j) => v + (b[j] - v) * u); }
    }
    return keys[keys.length - 1].slice(1);
  }

  function seek(t) {
    scenes.forEach(s => { s.style.display = (t >= num(s, 'start', 0) && t < num(s, 'end', 1e9)) ? 'block' : 'none'; });

    animEls.forEach(el => {
      const t0 = num(el, 'in', 0), kind = el.dataset.anim || 'rise', d = num(el, 'dur', DUR[kind] ?? .3);
      const u = clamp((t - t0) / Math.max(d, 1e-3));
      let o = 1, tr = '', f = '';
      if (kind === 'rise') { const e = E.outCubic(u); o = e; tr = `translateY(${(1 - e) * 14}px)`; }
      else if (kind === 'pop') { o = clamp(u * 2.5); tr = `scale(${.9 + .1 * E.outBack(u)})`; }
      else if (kind === 'blur') { const e = E.outCubic(u); o = e; f = `blur(${(1 - e) * 10}px)`; }
      else if (kind === 'fade') { o = E.outCubic(u); }
      else if (kind === 'wipe') { o = u > 0 ? 1 : 0; tr = `scaleX(${E.outCubic(u)})`; }
      else if (kind === 'underline') { el.style.setProperty('--u', E.outCubic(u)); }
      else if (kind === 'draw') { el.style.strokeDashoffset = (1 - E.inOutCubic(u)) * num(el, 'len', 0); }
      else if (kind === 'type') { const full = el.dataset.full || ''; const n = t < t0 ? 0 : Math.floor((t - t0) / .03) + 1; el.textContent = full.slice(0, n); }
      if (!['underline', 'draw', 'type'].includes(kind)) { el.style.opacity = o; el.style.transform = (el.dataset.base || '') + ' ' + tr; el.style.filter = f; }
    });

    stateEls.forEach(({ el, st }) => {
      let cur = st[0][1], prev = st[0][1], since = -1e9;
      for (const [ts, name] of st) if (t >= ts) { prev = cur; cur = name; since = ts; }
      const u = E.outCubic(clamp((t - since) / .3)), A = STATE[prev] || STATE.plain, B = STATE[cur] || STATE.plain;
      const mix = k => A[k] + (B[k] - A[k]) * u;
      el.style.opacity = mix('o'); el.style.filter = `blur(${mix('b')}px)`;
      el.style.transform = (el.dataset.base || '') + ` scale(${mix('s')})`;
      el.classList.toggle('is-on', cur === 'on');
    });

    cams.forEach(({ el, keys, blur }) => {
      const [s, x, y] = camAt(keys, t), [s2, x2, y2] = camAt(keys, t + 1 / 30);
      el.style.transform = `translate(${x}px, ${y}px) scale(${s})`;
      if (blur) { const v = Math.hypot(x2 - x, y2 - y) + Math.abs(s2 - s) * 600; el.style.filter = v > 6 ? `blur(${Math.min(24, v / 4)}px)` : ''; }
    });

    counts.forEach(({ el, a, b, t: t0, d, fmt }) => {
      const v = a + (b - a) * E.outExpo(clamp((t - t0) / d));
      el.textContent = fmt === 'k' ? (v >= 1000 ? Math.round(v / 1000) + 'k' : Math.round(v)) : Math.round(v).toLocaleString('en-US');
    });
  }

  window.seek = seek;
  window.ready = new Promise(res => {
    const go = () => {
      init();
      const imgs = [...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }));
      Promise.all([document.fonts.ready, ...imgs]).then(() => {
        const q = new URLSearchParams(location.search);
        if (q.get('guides')) document.body.classList.add('guides');
        seek(parseFloat(q.get('t') || '0')); res();
      });
    };
    document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', go) : go();
  });
})();
