// Voxel reels: timeline. Reads reel.json (script, characters, on-screen notes) and build/timing.json (from voice.py),
// then window.render(t) sets the whole frame from t (lemo-opuscar page contract: READY, render, DUR, EV).
import { THREE, makeWorld, makeCharacter, perform } from './voxel.js';

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eo = t => 1 - Math.pow(1 - clamp(t), 3);
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const back = (t, s = 2.2) => { t = clamp(t) - 1; return 1 + t * t * ((s + 1) * t + s); };
const hash = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };
const norm = w => w.toLowerCase().replace(/[^a-z0-9']/g, '');
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
// *word* in chip or card text marks a keyword (yellow)
const mark = s => esc(s).replace(/\*([^*]+)\*/g, '<span class="kw">$1</span>');

const [R, T] = await Promise.all([fetch('reel.json').then(r => r.json()), fetch('build/timing.json').then(r => r.json())]);
const W = innerWidth, H = innerHeight, U = W / 1080;
const FPS = T.fps || 30, TAIL = R.tail ?? 1.6;
window.DUR = T.dur + TAIL;

// ---- 3D -----------------------------------------------------------------------------------------------------
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
const { scene, camera, update } = makeWorld(renderer, W, H, R.look || {});
const who = Object.keys(R.characters);              // e.g. ["ME", "SIDEKICK"]
const POS = R.positions || { [who[0]]: [-0.5, 0, 0], [who[1]]: [0.62, 0, 0.3] };
const C = {};
who.forEach((k, i) => { C[k] = makeCharacter(R.characters[k]); C[k].root.position.set(...POS[k]); C[k].seed = i * 7 + 3; scene.add(C[k].root); });

// ---- lines, shots and on-screen notes -------------------------------------------------------------------------
const lines = T.lines.map(l => Object.assign({}, R.lines.find(x => x.id === l.id), l));
const words = T.words;
const wordTime = (line, w, after = 0) => {           // time of word w (text) in this line, or null
  const n = norm(w); const hit = words.find(x => x.line === line.id && norm(x.w) === n && x.start >= after);
  return hit ? hit.start : null;
};
const steps = lines.filter(l => l.step).length;
// shots: cut on every line. Default: close-up of the speaker; a line with a card or a step goes wide.
const shots = lines.map((l, i) => ({ t0: i === 0 ? 0 : l.start - 0.06, kind: l.shot || (l.card || l.step || (R.cta && i === lines.length - 1) ? 'wide' : 'cu'), who: l.who, i }));
function shotCam(s, t) {
  const p = seg(t, s.t0, (shots[s.i + 1]?.t0 ?? window.DUR));
  const push = eio(p) * 0.35;
  const side = s.i % 2 ? 1 : -1;
  if (s.kind === 'cu') {
    const ch = C[s.who], base = ch.root.position;
    const hy = ch.headY;
    const d = (ch.kind === 'human' ? 5.2 : 4.0) - push;   // head about 45 % of the frame width, gentle push-in
    // aim below the head so the head sits in the upper third, clear of the captions
    return { pos: new THREE.Vector3(base.x + side * 0.7, hy + 0.15, base.z + d), target: new THREE.Vector3(base.x, hy - 0.42 * d / 5.4, base.z) };
  }
  if (s.kind === 'two') {
    return { pos: new THREE.Vector3(side * 0.35, 1.6, 7.6 - push * 1.5), target: new THREE.Vector3(0, 1.15, 0) };
  }
  // wide: both characters in the lower half, room above for the card
  return { pos: new THREE.Vector3(side * 0.35, 2.0, 11.0 - push * 1.5), target: new THREE.Vector3(0, 1.5, 0) };   // heads below the card, captions under the faces
}

// captions: 2 to 3 words at a time, split at punctuation
const chunks = [];
for (const l of lines) {
  const ws = words.filter(w => w.line === l.id); let cur = [];
  ws.forEach((w, k) => {
    cur.push(w);
    const brk = /[.,!?:;]$/.test(w.w) || cur.length >= 3 || (cur.length >= 2 && k + 1 < ws.length && ws[k + 1].w.length > 7);
    if (brk || k === ws.length - 1) { chunks.push({ line: l, ws: cur }); cur = []; }
  });
}
chunks.forEach(c => c.t0 = c.ws[0].start);
chunks.forEach((c, i) => { const nx = chunks[i + 1]; c.t1 = nx && nx.line === c.line ? nx.t0 : Math.min(c.line.end + 0.25, nx ? nx.t0 : 1e9); });
const KW = new Set((R.keywords || []).map(norm));

// chip and card spans: a chip or card stays until the next line that sets one (or "clear": true)
const chipSpans = [], cardSpans = [];
lines.forEach((l, i) => {
  if (l.chip) chipSpans.push({ t0: l.start, text: l.chip, step: lines.slice(0, i + 1).filter(x => x.step).length });
  if (l.card || l.clear) cardSpans.push({ t0: l.start, card: l.card || null, line: l });
});
chipSpans.forEach((s, i) => s.t1 = chipSpans[i + 1]?.t0 ?? 1e9);
cardSpans.forEach((s, i) => s.t1 = cardSpans[i + 1]?.t0 ?? 1e9);
// cue times inside cards: list ticks land on a named word (item.at), else spread over the line
for (const s of cardSpans) {
  const c = s.card; if (!c) continue;
  if (c.type === 'list') {
    let after = s.t0;
    c.items.forEach((it, k) => {
      const wt = it.at ? wordTime(s.line, it.at, after) ?? lines.map(l => wordTime(l, it.at, after)).find(x => x != null) : null;
      it.t = wt ?? (s.line.start + (s.line.end - s.line.start) * (k + 1) / (c.items.length + 1));
      after = it.t;
    });
  }
  if (c.type === 'count') c.t = c.at ? (wordTime(s.line, c.at) ?? s.t0 + 0.2) : s.t0 + 0.2;
}
// ending: the keyword box pops when the keyword is spoken
const last = lines[lines.length - 1];
const ctaT = R.cta ? (wordTime(last, R.cta.kw) ?? last.start + 0.3) : null;

// sound cues for mix.py (exported by core/render/events.mjs)
const EV = [];
shots.slice(1).forEach(s => EV.push({ t: +s.t0.toFixed(3), type: 'cut' }));
chipSpans.forEach(s => EV.push({ t: s.t0, type: 'pop', what: 'chip' }));
cardSpans.forEach(s => {
  if (!s.card) return; EV.push({ t: s.t0, type: 'pop', what: 'card' });
  if (s.card.type === 'list') s.card.items.forEach(it => EV.push({ t: +it.t.toFixed(3), type: 'tick' }));
  if (s.card.type === 'count') EV.push({ t: s.card.t, type: 'count', dur: 0.8 });
  if (s.card.type === 'type') EV.push({ t: s.t0 + 0.15, type: 'type', dur: Math.min(s.card.text.length / 18, s.line.end - s.t0) });
});
if (ctaT != null) EV.push({ t: +ctaT.toFixed(3), type: 'chime' });
EV.sort((a, b) => a.t - b.t);
window.EV = EV;

// ---- overlay --------------------------------------------------------------------------------------------------
const $ = id => document.getElementById(id);
const chip = $('chip'), chipText = $('chipText'), dashes = $('dashes'), cap = $('cap'), card = $('card'), cta = $('cta');
dashes.innerHTML = '<i></i>'.repeat(steps);
$('ctaSmall').textContent = R.cta?.small || 'Comment';
$('ctaBox').textContent = R.cta?.kw || '';
const conf = $('confetti'); conf.width = W; conf.height = H; const cg = conf.getContext('2d');
const COLS = ['#ffd60a', '#ff5d8f', '#5ce1e6', '#7b61ff', '#ffffff', '#3ddc84'];
let lastChunk = null, lastCard = null;

function drawCard(s, t) {
  const c = s.card;
  if (lastCard !== s) {
    lastCard = s;
    if (c.type === 'list') card.innerHTML = (c.title ? `<div class="title">${mark(c.title)}</div>` : '') + c.items.map(it => `<div class="row"><div class="tick">✓</div><div>${mark(it.text)}</div></div>`).join('');
    else if (c.type === 'count') card.innerHTML = `<div class="big"></div>${c.sub ? `<div class="sub">${mark(c.sub)}</div>` : ''}`;
    else if (c.type === 'type') card.innerHTML = (c.title ? `<div class="title">${mark(c.title)}</div>` : '') + `<div class="type"></div>`;
    else card.innerHTML = (c.title ? `<div class="title">${mark(c.title)}</div>` : '') + `<div class="row">${mark(c.text || '')}</div>`;
  }
  if (c.type === 'list') card.querySelectorAll('.tick').forEach((el, k) => {
    const on = t >= c.items[k].t; el.classList.toggle('on', on);
    el.style.transform = `scale(${on ? 1 + 0.35 * (1 - seg(t, c.items[k].t, c.items[k].t + 0.25)) : 1})`;
  });
  if (c.type === 'count') {
    const v = c.from + (c.to - c.from) * eo(seg(t, c.t, c.t + 0.8));
    card.querySelector('.big').textContent = (c.prefix || '') + (c.decimals ? v.toFixed(c.decimals) : Math.round(v).toLocaleString('en-US')) + (c.suffix || '');
  }
  if (c.type === 'type') {
    const n = Math.floor(clamp((t - s.t0 - 0.15) * 18, 0, c.text.length));
    card.querySelector('.type').innerHTML = esc(c.text.slice(0, n)) + (Math.floor(t * 2.5) % 2 || n < c.text.length ? '<b></b>' : '');
  }
}

window.render = t => {
  // performance
  const f = Math.min(T.env.length - 1, Math.max(0, Math.round(t * FPS)));
  const speaking = lines.find(l => t >= l.start - 0.02 && t <= l.end + 0.02);
  who.forEach(k => {
    const other = who.find(x => x !== k), sp = speaking && speaking.who === k;
    const dx = C[other].root.position.x - C[k].root.position.x;
    // the speaker faces the camera a bit more; the listener looks at the speaker
    const look = sp ? Math.sign(dx) * 0.25 : Math.sign(dx) * 0.55;
    const mood = (speaking && speaking.mood && speaking.who === k) ? speaking.mood : (R.characters[k].mood || 'normal');
    perform(C[k], t, { talk: sp ? T.env[f] : 0, speaking: sp, look, mood, seed: C[k].seed, wave: ctaT != null && k === who[0] && t > ctaT + 0.2 });
  });
  update(t);
  // camera
  const s = shots.filter(x => x.t0 <= t).pop() || shots[0];
  const { pos, target } = shotCam(s, t);
  camera.position.copy(pos); camera.lookAt(target);
  renderer.render(scene, camera);

  // captions
  const ch = chunks.find(c => t >= c.t0 - 0.02 && t < c.t1);
  if (ch !== lastChunk) { lastChunk = ch; cap.innerHTML = ch ? ch.ws.map(w => `<span class="${KW.has(norm(w.w)) ? 'kw' : ''}">${esc(w.w)}</span>`).join('') : ''; }
  if (ch) cap.querySelectorAll('span').forEach((el, k) => {
    const p = seg(t, ch.ws[k].start - 0.03, ch.ws[k].start + 0.12);
    el.style.opacity = p > 0 ? 1 : 0; el.style.transform = `scale(${0.6 + 0.4 * back(p)})`;
  });
  const endFade = ctaT != null ? 1 - seg(t, ctaT - 0.1, ctaT + 0.15) : 1;
  // chip
  const cs = chipSpans.find(x => t >= x.t0 && t < x.t1);
  if (cs) {
    if (chipText.dataset.k !== String(cs.t0)) { chipText.dataset.k = String(cs.t0); chipText.innerHTML = mark(cs.text); }
    const p = seg(t, cs.t0, cs.t0 + 0.25);
    chip.style.opacity = endFade; chip.style.transform = `translateX(-50%) scale(${0.7 + 0.3 * back(p)})`;
    dashes.querySelectorAll('i').forEach((el, k) => el.classList.toggle('on', k < cs.step));
  } else chip.style.opacity = 0;
  // card
  const ks = cardSpans.find(x => t >= x.t0 && t < x.t1);
  if (ks && ks.card) {
    drawCard(ks, t);
    const p = seg(t, ks.t0, ks.t0 + 0.3), out = seg(t, ks.t1 - 0.2, ks.t1);
    card.style.opacity = Math.min(1 - out, endFade);
    card.style.transform = `translateX(-50%) translateY(${(1 - eo(p)) * 60 * U}px) scale(${0.85 + 0.15 * back(p)})`;
  } else card.style.opacity = 0;
  // ending
  cg.clearRect(0, 0, W, H);
  if (ctaT != null && t >= ctaT) {
    const p = seg(t, ctaT, ctaT + 0.35);
    cta.style.opacity = clamp(p * 3); cta.style.transform = `scale(${0.5 + 0.5 * back(p)})`;
    const dt = t - ctaT;
    for (let i = 0; i < 140; i++) {
      const x0 = W * (0.15 + 0.7 * hash(i)), vx = (hash(i * 3.3) - 0.5) * 900 * U, vy = -(900 + 900 * hash(i * 5.1)) * U;
      const x = x0 + vx * dt, y = H * 0.42 + vy * dt + 0.5 * 2400 * U * dt * dt;
      if (y > H + 40) continue;
      cg.save(); cg.translate(x, y); cg.rotate(dt * (4 + 8 * hash(i * 7.9)) + i);
      cg.fillStyle = COLS[i % COLS.length]; cg.fillRect(-9 * U, -5 * U, 18 * U, 10 * U * (0.4 + 0.6 * Math.abs(Math.sin(dt * 9 + i)))); cg.restore();
    }
  } else cta.style.opacity = 0;
};

await document.fonts.ready;
window.render(0);
window.READY = true;
