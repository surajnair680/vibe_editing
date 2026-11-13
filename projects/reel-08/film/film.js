// reel-08 "Comeback Day 1": Urban Sketch · Pen & Wash, vertical 1080x1920, 24 fps.
// One tall sketchbook page; the camera travels down it. Film time = voice time + 0.40 s.
// Engine copied from the Lemo-Opuscar urban-sketch demo (engine.js, poses.js); everything below is this film's own.
import { clamp, lerp, ss, TAU, rng, n2, fbm, hex, mix3, INK, PAPER, rgba, rough, ellipse, spline, penStroke, drawPen, wash, reserve, dab, foliage, figure, drawPrims, handwrite, R3 } from './engine.js';
import { walk, stand, wave, mixPose } from './poses.js';
const { V } = R3;

const DUR = 36.5;
const q = new URLSearchParams(location.search);
await Promise.all([document.fonts.load('80px Caveat'), document.fonts.load('600 80px Caveat'), document.fonts.load('80px "Reenie Beanie"')]);

const cvs = document.getElementById('c');
const SW = innerWidth, SH = innerHeight;
cvs.width = SW; cvs.height = SH;
const ctx = cvs.getContext('2d');
const K = SW / 1080;                       // screen scale (1 at 1080x1920, 0.5 for the draft size)

// ---------------- helpers ----------------
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eo = t => 1 - Math.pow(1 - clamp(t), 3), ei = t => Math.pow(clamp(t), 3);
const seg = (t, a, b) => clamp((t - a) / (b - a));
const rect = (x, y, w, h, rot = 0) => { const c = [x + w / 2, y + h / 2]; return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(([px, py]) => { const dx = px - c[0], dy = py - c[1]; return [c[0] + dx * Math.cos(rot) - dy * Math.sin(rot), c[1] + dx * Math.sin(rot) + dy * Math.cos(rot)]; }); };
const C = {
  coral: hex('#e0705a'), coralD: hex('#c4543f'), note: hex('#efe1a2'), skin: hex('#e2b393'), hair: hex('#4a3226'), legging: hex('#3e4456'),
  sky: hex('#b9cddb'), skyD: hex('#9fbcd6'), cloud: hex('#b7b3c9'), sea: hex('#7fa6b8'), seaD: hex('#5f8aa0'), mount: hex('#8b8fa6'), mountD: hex('#6c7090'),
  tree: hex('#6f9a5a'), stone: hex('#cdbd9f'), stoneD: hex('#a8987c'), path: hex('#ddd0b4'), rain: hex('#8f9cab'), rainD: hex('#76839a'),
  wood: hex('#c09a6a'), mirror: hex('#c9d6dc'), floor: hex('#d8c3a0'), grey: hex('#9a9a9a'), steel: hex('#8d929c'), bottle: hex('#86b3c4'), cup: hex('#d9c3a3'),
};
const LOOK_HER = { skin: C.skin, top: C.coral, bottom: C.legging, pants: 1, hair: C.hair, hairLong: 1, sleeve: 'none', torso: [.074, .064, .088], shoe: hex('#eeebe3') };

// ---------------- the page: wash layers + ink strokes ----------------
class Layer {   // a wash canvas over a world rectangle, at half resolution
  constructor(x0, y0, x1, y1, reveal, s = .5) { this.x0 = x0; this.y0 = y0; this.x1 = x1; this.y1 = y1; this.s = s; this.reveal = reveal;
    this.c = document.createElement('canvas'); this.c.width = Math.ceil((x1 - x0) * s); this.c.height = Math.ceil((y1 - y0) * s);
    this.x = this.c.getContext('2d'); this.x.fillStyle = '#fff'; this.x.fillRect(0, 0, this.c.width, this.c.height); this.x.setTransform(s, 0, 0, s, -x0 * s, -y0 * s); }
}
const LAYERS = [], STROKES = [], EV = [], NOTES = [];
const bbox = P => { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; for (const [x, y] of P) { a = Math.min(a, x); b = Math.min(b, y); c = Math.max(c, x); d = Math.max(d, y); } return [a - 10, b - 10, c + 10, d + 10]; };
let SEED = 100;
function ink(pts, t0, d, o = {}) {   // a fineliner stroke drawn on between t0 and t0+d (world coords)
  const st = penStroke(pts, { w: o.w ?? 2.6, wob: o.wob ?? 1.1, over: o.over ?? 5, gap: o.gap ?? .4, seed: SEED++, smooth: o.smooth ?? false });
  const s = { st, t0, d, a: o.a ?? 1, bb: bbox(st.P), fade: o.fade, col: o.col };
  STROKES.push(s); if (d > 0 && t0 > -.5 && !o.silent) EV.push({ t: +t0.toFixed(3), type: 'pen', d: +d.toFixed(3), len: Math.round(st.L) });
  return s;
}
const closed = P => [...P, P[0], P[1]];
function shape(L, poly, col, t0, d, o = {}) {   // wash on a layer + its ink outline
  if (col && L) wash(L.x, poly, col, { a: o.a ?? .55, j: o.j ?? 5, layers: 3, edge: .32, dx: o.dx ?? 3, dy: o.dy ?? 2, seed: SEED++ });
  if (o.noInk) return null;
  return ink(o.open ? poly : closed(poly), t0, d, { w: o.w, smooth: o.smooth ?? false, gap: .5, fade: o.fade });
}
const noisyCircle = (cx, cy, R, seed, sy = 1) => c => { c.beginPath(); const n = 40; for (let i = 0; i <= n; i++) { const a = i / n * TAU, r = R * (.78 + .44 * fbm(Math.cos(a) * 1.6 + seed, Math.sin(a) * 1.6, seed, 3)); const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r * sy; i ? c.lineTo(x, y) : c.moveTo(x, y); } c.closePath(); };

// ======================= SCENE A: the gym mirror (0 to 3.4 s) =======================
const A = { mx0: 300, my0: 250, mx1: 1300, my1: 1760, gx: 800, gy: 1620, S: 1060 };
const LA = new Layer(0, 0, 1600, 2000, t => t < 0.35 ? null : t > 1.6 ? 'full' : noisyCircle(800, 1100, 1300 * eo(seg(t, .35, 1.6)), 3, 1.2));
LAYERS.push(LA);
{
  const L = LA, { mx0, my0, mx1, my1 } = A;
  // mirror glass: pale blue-grey wash with diagonal glints left as paper
  wash(L.x, rect(mx0 - 26, my0 - 26, mx1 - mx0 + 52, my1 - my0 + 52), C.wood, { a: .5, j: 4, layers: 3, edge: .3, seed: 10 });
  reserve(L.x, rect(mx0, my0, mx1 - mx0, my1 - my0), 1, 0);
  wash(L.x, rect(mx0, my0, mx1 - mx0, my1 - my0), C.mirror, { a: .42, j: 7, layers: 3, edge: .25, seed: 11 });
  for (const [x, y] of [[420, 330], [1120, 1240]]) reserve(L.x, [[x, y], [x + 70, y], [x + 230, y + 260], [x + 160, y + 260]], .8, 3, 7);
  // mirror frame (wood) as two nested boxes, drawn before t=0 so frame 1 is never blank
  ink(closed(rect(mx0 - 26, my0 - 26, mx1 - mx0 + 52, my1 - my0 + 52)), -1, .1);
  ink(closed(rect(mx0, my0, mx1 - mx0, my1 - my0)), -1, .1);
  // reflected floor and wall line
  shape(L, [[mx0, 1520], [mx1, 1520], [mx1, my1], [mx0, my1]], C.floor, -1, .1, { a: .45, noInk: true });
  ink([[mx0 + 10, 1522], [mx1 - 10, 1516]], -1, .1, { w: 2.2 });
  for (let k = 0; k < 5; k++) ink([[mx0 + 60 + k * 230, 1540 + k * 6], [mx0 + 20 + k * 260, my1 - 10]], -1, .1, { w: 1.6, a: .7 });
  // dumbbell rack outside the mirror (left)
  ink([[120, 1820], [140, 900]], -1, .1); ink([[280, 1820], [270, 900]], -1, .1);
  for (let k = 0; k < 3; k++) {
    const y = 1080 + k * 230; ink([[110, y + 40], [290, y + 34]], -1, .1, { w: 2.2 });
    for (const x of [150, 250]) shape(L, ellipse(x, y, 26 + k * 4, 34 + k * 5, 14), C.steel, -1, .1, { a: .5, smooth: true });
    ink([[150, y], [250, y]], -1, .1, { w: 3.4 });
  }
  // a plant on the right, for life in the frame
  for (let k = 0; k < 7; k++) { const a = -2.2 + k * .35; ink([[1460, 1800], [1460 + Math.cos(a) * 170, 1800 + Math.sin(a) * 260]], -1, .1, { w: 2 }); dab(L.x, 1460 + Math.cos(a) * 160, 1800 + Math.sin(a) * 250, 30, a, C.tree, .5, 50 + k); }
  shape(L, [[1400, 1800], [1520, 1800], [1500, 1960], [1420, 1960]], C.coralD, -1, .1, { a: .35 });
  // the week tracker: a sticky note on the mirror, right of her
  shape(L, rect(1035, 880, 230, 210, .05), C.note, -1, .1, { a: .6 });
}
const TRACK = { x: 1050, y: 955, days: 'M T W T F S S' };
const tickT = k => 1.26 + k * .1;                     // ticks land on "five days a week"

// ======================= SCENE B: life happened (3.4 to 10.1 s), ink only + grey rain =======================
const LB = new Layer(0, 2000, 1600, 4700, t => t < 7.35 ? null : t > 9.6 ? 'full' : noisyCircle(1000, 3950, 1400 * eo(seg(t, 7.35, 9.6)), 8, .7));
LAYERS.push(LB);
const DUMB = [];   // the coral dumbbell's strokes, erased on "slowly disappeared"
{
  const L = LB, ink0 = 3.75;
  // 1. books, laptop, grad cap (centre 520, 2450) on "final year of uni"
  const tb = 4.0;
  ink(closed(rect(330, 2560, 340, 46, -.03)), tb, .22); ink(closed(rect(350, 2514, 300, 44, .04)), tb + .12, .2); ink(closed(rect(320, 2470, 330, 42, -.02)), tb + .22, .2);
  ink([[700, 2600], [930, 2600]], tb + .3, .15);                             // laptop base
  ink(closed([[720, 2596], [910, 2596], [950, 2420], [760, 2420]]), tb + .35, .28);
  ink([[775, 2440], [930, 2440], [900, 2570], [745, 2570]], tb + .5, .2, { a: .5, w: 1.6 });
  ink(closed([[380, 2400], [500, 2350], [620, 2400], [500, 2440]]), tb + .45, .25);   // cap
  ink([[440, 2420], [440, 2465]], tb + .6, .08); ink([[560, 2420], [560, 2465]], tb + .62, .08);
  ink([[500, 2395], [610, 2410], [612, 2470]], tb + .65, .15, { w: 1.8 });
  // 2. suitcase + plane path (centre 1050, 2980) on "moved countries"
  const ts = 5.25;
  ink(closed(rect(880, 2900, 330, 230, .02)), ts, .3); ink([[990, 2900], [992, 2860], [1100, 2858], [1102, 2900]], ts + .25, .15);
  ink([[905, 2960], [1190, 2964]], ts + .3, .12, { w: 1.6 }); ink([[905, 3070], [1190, 3074]], ts + .35, .12, { w: 1.6 });
  ink(ellipse(940, 3150, 18, 18, 10), ts + .4, .08); ink(ellipse(1150, 3150, 18, 18, 10), ts + .42, .08);
  for (let k = 0; k < 9; k++) { const u0 = k / 9, u1 = u0 + .05; const P = u => [lerp(330, 1350, u), 2820 - Math.sin(u * Math.PI) * 220]; ink([P(u0), P(u1)], ts + .1 + k * .07, .06, { w: 2 }); }
  // 3. café: cup + apron (centre 520, 3560) on "started working part-time"
  const tc = 6.45;
  ink(closed([[420, 3520], [560, 3520], [540, 3700], [440, 3700]]), tc, .25); ink(closed(rect(408, 3490, 164, 30)), tc + .18, .12);
  ink([[440, 3580], [540, 3580]], tc + .25, .08, { w: 1.8 }); ink([[470, 3470], [480, 3440], [470, 3410]], tc + .3, .1, { w: 1.6, a: .7 }); ink([[515, 3470], [525, 3440], [515, 3410]], tc + .32, .1, { w: 1.6, a: .7 });
  ink([[650, 3380], [700, 3380], [760, 3460], [780, 3720], [600, 3720], [620, 3460], [650, 3380]], tc + .25, .3);   // apron
  ink([[620, 3470], [540, 3440]], tc + .45, .1, { w: 1.6 }); ink([[760, 3470], [840, 3440]], tc + .47, .1, { w: 1.6 });
  ink(closed(rect(650, 3560, 90, 60)), tc + .55, .1, { w: 1.6 });
  // 4. rainy city (centre 1000, 4000): towers, mountains behind, rain wash
  const tr = 7.3;
  const ridge = [[520, 3850], [640, 3760], [760, 3800], [880, 3700], [1010, 3780], [1150, 3690], [1290, 3790], [1420, 3740]];
  ink(ridge, tr, .3, { smooth: true, a: .6 });
  const towers = [[560, 3880, 90, 300], [670, 3800, 70, 380], [760, 3860, 110, 320], [890, 3760, 80, 420], [990, 3830, 120, 350], [1130, 3880, 80, 300], [1230, 3820, 100, 360], [1350, 3900, 70, 280]];
  towers.forEach(([x, y, w, h], i) => { ink([[x, y + h], [x, y], [x + w, y], [x + w, y + h]], tr + .05 + i * .05, .14, { w: 2.2 }); for (let k = 0; k < 4; k++) ink([[x + w * .3, y + 40 + k * 60], [x + w * .5, y + 40 + k * 60]], tr + .2 + i * .05, .04, { w: 1.4, a: .6, silent: true }); });
  ink([[500, 4180], [1450, 4180]], tr + .4, .2);
  wash(L.x, [[500, 3600], [1460, 3600], [1460, 4185], [500, 4185]], C.rain, { a: .4, j: 14, layers: 3, edge: .2, seed: 31 });
  wash(L.x, [[500, 4180], [1460, 4180], [1460, 4280], [500, 4280]], C.rainD, { a: .35, j: 8, layers: 2, edge: .2, seed: 32 });
  for (const [x, y, w, h] of towers) wash(L.x, rect(x, y, w, h), C.rainD, { a: .18, j: 3, layers: 2, edge: .1, seed: SEED++ });
  // umbrella walker (carrot person) on the street
  ink([[1000, 4060], [1080, 4020], [1160, 4060]], tr + .45, .15, { smooth: true }); ink([[1000, 4060], [1160, 4060]], tr + .5, .1, { w: 1.6 });
  ink([[1080, 4060], [1080, 4170]], tr + .55, .08, { w: 1.8 }); ink([[1068, 4110], [1060, 4175]], tr + .58, .06, { w: 1.8 }); ink([[1092, 4110], [1100, 4175]], tr + .6, .06, { w: 1.8 });
  // 5. the coral dumbbell (420, 4290): there since the strip began, lifts away 8.5 to 10.0
  const dx = 420, dy = 4300;
  for (const [x, s] of [[dx - 90, 1], [dx + 90, 1]]) { const P = rect(x - 30, dy - 60, 60, 120); DUMB.push({ poly: P, st: ink(closed(P), ink0, .2, { fade: [8.5, 9.9] }) }); }
  DUMB.push({ poly: rect(dx - 60, dy - 12, 120, 24), st: ink(closed(rect(dx - 60, dy - 12, 120, 24)), ink0 + .15, .15, { fade: [8.5, 9.9] }) });
  // handwritten notes in the margin (not meant to be read in full)
  NOTES.push({ text: 'final year!', x: 690, y: 2380, size: 50, t: 4.5, font: '"Reenie Beanie"' }, { text: 'Vancouver ->', x: 1180, y: 2840, size: 50, t: 5.8, font: '"Reenie Beanie"' }, { text: 'shifts', x: 820, y: 3640, size: 50, t: 7.0, font: '"Reenie Beanie"' });
}

// ======================= SCENE C: the gym floor (11.1 to 17.2 s) =======================
const Cn = { gx: 820, gy: 5900, S: 1120 };
const LC = new Layer(0, 4800, 1600, 6200, t => t < 12.25 ? null : t > 13.8 ? 'full' : noisyCircle(700, 5500, 1300 * eo(seg(t, 12.25, 13.8)), 21, .9));
LAYERS.push(LC);
{
  const L = LC, t0 = 11.2;
  ink([[60, 5905], [1540, 5895]], t0, .25);
  shape(L, [[230, 5870], [1350, 5866], [1380, 5935], [200, 5940]], C.coral, t0 + .1, .3, { a: .5 });   // yoga mat
  shape(L, rect(1220, 5700, 70, 190, 0), C.bottle, t0 + .2, .2, { a: .55 }); shape(L, rect(1228, 5670, 54, 32), C.steel, t0 + .3, .1, { a: .6 });
  shape(L, [[1330, 5880], [1480, 5876], [1500, 5900], [1310, 5904]], C.note, t0 + .3, .15, { a: .5 });   // towel
  // wall behind: a window and a clock, light ink
  ink(closed(rect(1000, 5000, 380, 300)), t0 + .15, .2, { w: 2, a: .7 }); ink([[1190, 5000], [1190, 5300]], t0 + .25, .08, { w: 1.6, a: .6 }); ink([[1000, 5150], [1380, 5150]], t0 + .27, .08, { w: 1.6, a: .6 });
  wash(L.x, rect(1000, 5000, 380, 300), C.sky, { a: .35, j: 6, layers: 2, edge: .2, seed: 41 });
  ink(ellipse(300, 5080, 60, 60, 16), t0 + .2, .15, { w: 2, a: .7 }); ink([[300, 5080], [300, 5040], [300, 5080], [330, 5095]], t0 + .3, .08, { w: 1.6, a: .7 });
  wash(L.x, [[0, 4900], [1600, 4900], [1600, 5900], [0, 5900]], hex('#e8dcc6'), { a: .25, j: 30, layers: 2, edge: 0, seed: 42 });
}

// ======================= SCENE D: the seawall (17.2 to 33 s) =======================
const WALK0 = 17.75, WALK1 = 27.55, STEP = 1 / 1.4;          // steps at 84 BPM (one per beat)
const Dn = { gy: 8200, S: 760, x0: 260 };
const STRIDE = .36 * Dn.S;
const herX = t => Dn.x0 + STRIDE * 1.4 * (clamp(t, WALK0, WALK1) - WALK0) - (t < WALK0 + .4 ? STRIDE * 1.4 * (WALK0 + .4 - Math.max(t, WALK0)) * .5 * (1 - seg(t, WALK0, WALK0 + .4)) : 0);
const XEND = herX(WALK1);
const frontX = t => t < 17.4 ? -1e4 : herX(t) - 700 + 4200 * eo(seg(t, 17.4, 19.4)) + 3000 * seg(t, 19.4, 33);   // colour sweeps in past her and stays ahead
const LD = new Layer(-300, 6300, XEND + 1000, 8800, t => {
  if (t < 17.4) return null;
  const fx = frontX(t), sky = eo(seg(t, 17.4, 18.6));
  return c => { c.beginPath(); c.moveTo(-400, 6200); const n = 60; for (let i = 0; i <= n; i++) { const y = 6200 + i / n * 2700; const x = fx + (fbm(y * .004, t * .2, 9, 3) - .5) * 360 + (y < 7300 ? 600 * sky : 0); c.lineTo(x, y); } c.lineTo(-400, 8900); c.closePath(); };
});
LAYERS.push(LD);
const inkAt = x => Math.max(17.05, WALK0 + (x - Dn.x0 - 1300) / (STRIDE * 1.4));   // the pen draws each part of the seawall before she reaches it
{
  const L = LD, X0 = -300, X1 = XEND + 1000;
  // sky washes and clouds
  for (let k = 0; k < 6; k++) wash(L.x, ellipse(X0 + 300 + k * 900, 6700 + (k % 2) * 120, 700, 260, 22), k % 2 ? C.skyD : C.sky, { a: .22, j: 40, layers: 2, edge: 0, seed: 60 + k });
  for (let k = 0; k < 5; k++) { const cx = X0 + 600 + k * 1100, cy = 6620 + (k % 3) * 70; reserve(L.x, ellipse(cx, cy, 260, 70, 18), .7, 20, 70 + k); wash(L.x, ellipse(cx + 20, cy + 40, 230, 30, 14), C.cloud, { a: .25, j: 10, layers: 2, edge: .1, seed: 80 + k }); ink(ellipse(cx, cy, 250, 66, 18).slice(9, 19), inkAt(cx - 400), .3, { w: 1.8, a: .6, smooth: true }); }
  // mountains (violet-grey) with snow left as paper
  const ridge = []; for (let x = X0; x <= X1; x += 120) ridge.push([x, 7220 - 230 * Math.abs(Math.sin(x * .0016 + 1)) - 120 * fbm(x * .004, 1, 3, 3)]);
  wash(L.x, [...ridge, [X1, 7470], [X0, 7470]], C.mount, { a: .3, j: 12, layers: 3, edge: .25, seed: 90 });
  for (let i = 1; i < ridge.length - 1; i += 3) { const [x, y] = ridge[i]; if (y < 7100) reserve(L.x, [[x - 70, y + 6], [x, y - 4], [x + 70, y + 6], [x + 30, y + 40], [x - 10, y + 22], [x - 40, y + 44]], .75, 4, i); }
  for (let i = 0; i < ridge.length - 1; i += 4) ink(ridge.slice(i, i + 5), inkAt(ridge[i][0]), .35, { smooth: true, w: 2.2 });
  // sea with wave ticks
  wash(L.x, [[X0, 7460], [X1, 7460], [X1, 8000], [X0, 8000]], C.sea, { a: .5, j: 10, layers: 3, edge: .2, seed: 95 });
  wash(L.x, [[X0, 7760], [X1, 7760], [X1, 8000], [X0, 8000]], C.seaD, { a: .25, j: 14, layers: 2, edge: 0, seed: 96 });
  ink([[X0, 7462], [X1, 7458]], -1, .1, { w: 2, silent: true });
  const RW = rng(7); for (let k = 0; k < 110; k++) { const x = X0 + RW() * (X1 - X0), y = 7500 + RW() * 460, w = 20 + RW() * 40; ink([[x, y], [x + w * .5, y - 6], [x + w, y]], inkAt(x), .1, { w: 1.6, a: .65, smooth: true, silent: true }); }
  // railing on the far edge of the walkway, posts every 220 px
  ink([[X0, 7990], [X1, 7985]], 17.0, .6, { w: 2.4 }); ink([[X0, 8040], [X1, 8036]], 17.1, .6, { w: 2 });
  for (let x = X0 + 40; x < X1; x += 220) ink([[x, 7980], [x + 2, 8070]], inkAt(x), .08, { w: 2.2, silent: true });
  // walkway and the stone wall face below it
  wash(L.x, [[X0, 8060], [X1, 8060], [X1, 8240], [X0, 8240]], C.path, { a: .5, j: 8, layers: 3, edge: .2, seed: 97 });
  wash(L.x, [[X0, 8240], [X1, 8240], [X1, 8420], [X0, 8420]], C.stone, { a: .55, j: 6, layers: 3, edge: .25, seed: 98 });
  ink([[X0, 8242], [X1, 8238]], 17.15, .7, { w: 2.6 }); ink([[X0, 8420], [X1, 8414]], 17.2, .7, { w: 2.4 });
  for (let row = 0; row < 3; row++) for (let x = X0 + (row % 2) * 90; x < X1; x += 180) { ink([[x, 8240 + row * 60], [x + 2, 8300 + row * 60]], inkAt(x), .05, { w: 1.5, a: .6, silent: true }); ink([[x, 8300 + row * 60], [x + 180, 8300 + row * 60]], inkAt(x), .08, { w: 1.4, a: .45, silent: true }); }
  // lamp posts
  for (let x = X0 + 520; x < X1; x += 1100) { ink([[x, 8060], [x + 3, 7380]], inkAt(x), .2, { w: 3 }); shape(L, [[x - 34, 7380], [x + 38, 7380], [x + 26, 7310], [x - 22, 7310]], hex('#e2b04a'), inkAt(x) + .15, .12, { a: .5 }); ink([[x - 40, 7380], [x + 44, 7380]], inkAt(x) + .2, .06); }
  // foreground shrubs below the wall
  for (let x = X0 + 200; x < X1; x += 760) { foliage(L.x, [{ x, y: 8640, r: 190 }, { x: x + 210, y: 8600, r: 150 }, { x: x - 170, y: 8680, r: 130 }], { seed: x | 0, dens: .8 }); for (let k = 0; k < 6; k++) { const a = Math.PI + k * .55; ink(ellipse(x + Math.cos(a) * 170, 8640 + Math.sin(a) * 150, 50, 40, 10).slice(5, 10), inkAt(x), .1, { w: 1.8, a: .8, smooth: true, silent: true }); } }
  // the ending: her stopping point gets a bench behind her
  const bx = XEND + 380;
  shape(L, rect(bx - 160, 8130, 320, 26), C.wood, inkAt(bx), .2, { a: .5 }); ink([[bx - 140, 8156], [bx - 145, 8215]], inkAt(bx) + .15, .05); ink([[bx + 140, 8156], [bx + 145, 8215]], inkAt(bx) + .17, .05);
}
// checklist written in the sky ahead of her
const CHECK = [
  { text: 'every step', t: 18.45, mark: 'tick' },
  { text: 'from day 1', t: 22.7, mark: 'tick' },
  { text: 'extreme diets', t: 24.3, mark: 'cross', mt: 25.1 },
  { text: '5 a.m. punishment', t: 25.6, mark: 'cross', mt: 26.6 },
].map(c => ({ ...c, x: herX(c.t) + 330, y: 7110 }));
CHECK.forEach((c, i) => { c.y = 7020 + (i % 2) * 120; });

// ---------------- paper ----------------
const WX0 = -800, WY0 = -800, WX1 = XEND + 1600, WY1 = 9400;
const mott = (() => { const s = 1 / 8, w = Math.ceil((WX1 - WX0) * s), h = Math.ceil((WY1 - WY0) * s), c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'), im = x.createImageData(w, h);
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const X = WX0 + i / s, Y = WY0 + j / s; const m = fbm(X * .0011, Y * .0011, 2, 3) * .6 + fbm(X * .0062 + 9, Y * .0062, 4, 2) * .4; const k = 1 - .05 * (m - .45); const o = (j * w + i) * 4; im.data[o] = PAPER[0] * k; im.data[o + 1] = PAPER[1] * k; im.data[o + 2] = PAPER[2] * k; im.data[o + 3] = 255; }
  x.putImageData(im, 0, 0); return c; })();
const tooth = (() => { const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d'); const im = x.createImageData(512, 512); const R = rng(77);
  for (let j = 0; j < 512; j++) for (let i = 0; i < 512; i++) { const v = n2(i * .35, j * .35, 3) * .6 + n2(i * .09, j * .09, 5) * .4; const g = 255 - Math.max(0, (v - .55)) * 55 - (R() < .004 ? 25 : 0); const k = (j * 512 + i) * 4; im.data[k] = g; im.data[k + 1] = g * .995; im.data[k + 2] = g * .985; im.data[k + 3] = 255; }
  x.putImageData(im, 0, 0); return c; })();
const toothPat = ctx.createPattern(tooth, 'repeat');

// ---------------- camera ----------------
// keys: [t, cx, cy, z]; eased (in-out cubic) between keys, so the camera always moves
const KEYS = [
  [0, 800, 1010, 1.15], [0.95, 800, 1000, .965], [3.3, 790, 1060, .93],
  [4.0, 640, 2500, 1.3], [5.15, 660, 2490, 1.36], [5.6, 1020, 2960, 1.3], [6.35, 1000, 2975, 1.36], [6.8, 610, 3540, 1.3], [7.3, 615, 3560, 1.34], [7.9, 900, 3990, .98], [8.5, 870, 4060, .95], [10.0, 560, 4230, 1.22], [11.05, 590, 4250, 1.26],
  [11.5, 760, 5420, .98], [15.9, 700, 5380, 1.14], [16.12, 640, 5020, 1.42], [17.0, 650, 5030, 1.38],
];
const followD = t => [herX(t) + 260, 7820, .86];
function camRaw(t) {
  if (t >= 17.0) {   // seawall: tilt down onto the walkway, then a spring follow, then the push-in to her
    const a = KEYS[KEYS.length - 1];
    if (t < 17.75) { const u = eio(seg(t, 17.0, 17.75)); const f = followD(17.75); return [lerp(a[1], f[0], u), lerp(a[2], f[1], u), lerp(a[3], f[2], u)]; }
    const f = SPRING(t);
    if (t < WALK1) return f;
    const u = eio(seg(t, WALK1, WALK1 + 1.6)), z = lerp(f[2], 1.85, u) + .05 * seg(t, WALK1 + 1.6, 33);
    return [lerp(f[0], XEND, u), lerp(f[1], Dn.gy - Dn.S * .62, u), z];
  }
  let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++;
  const a = KEYS[i], b = KEYS[i + 1], u = eio(seg(t, a[0], b[0]));
  return [lerp(a[1], b[1], u), lerp(a[2], b[2], u), lerp(a[3], b[3], u)];
}
const SPR = []; { let p = followD(17.75), v = [0, 0, 0]; const dt = 1 / 240; for (let t = 17.75; t <= 34; t += dt) { const k = 26, d = 2 * Math.sqrt(k), g = followD(t + .35); for (let j = 0; j < 3; j++) { const acc = k * (g[j] - p[j]) - d * v[j]; v[j] += acc * dt; p[j] += v[j] * dt; } SPR.push(p.slice()); } }
function SPRING(t) { return SPR[clamp(Math.round((t - 17.75) * 240), 0, SPR.length - 1)]; }
function camera(t) {
  const [cx, cy, z] = camRaw(Math.min(t, 33.0));
  let rot = 0, sx = 0, sy = 0;
  if (t > 11.05 && t < 11.6) rot = .045 * Math.sin(seg(t, 11.05, 11.6) * Math.PI);          // whip-tilt with a slight roll
  if (t > 16.1 && t < 16.5) { const k = (1 - seg(t, 16.1, 16.5)) * 9; sx = Math.sin(t * 93) * k; sy = Math.cos(t * 71) * k; }   // punch-in shake
  if (t < 0.9) rot = -.02 * (1 - eo(t / .9));
  return { cx: cx + sx, cy: cy + sy, z: z * K, rot };
}

// ---------------- her (Codex pen-and-wash drawings, cut out by work/cutout.py) ----------------
const boil = t => Math.floor(t * 12);
const HM = await (await fetch('her/her.json')).json();
const IMG = {};
await Promise.all(Object.keys(HM).flatMap(n => ['', '_ink', '_mask'].map(sfx => new Promise((res, rej) => { const im = new Image(); im.onload = res; im.onerror = rej; im.src = `her/${n}${sfx}.png`; IMG[n + sfx] = im; }))));
// Draw pose n with her feet on (x, y), h world units tall. ink 0..1 = the pen drawing her (top to bottom), col 0..1 = colour bloom.
// o.sx / o.sy breathing scale, o.alpha fade, o.arm = { poly, pivot, ang } rotates a cut-out region (the waving forearm).
function her(n, x, y, h, ink, col, o = {}) {
  const m = HM[n], s = h / (m.footY - m.top), ax = m.bodyX, W = m.w, H = m.h, A0 = o.alpha ?? 1;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (o.sx ?? 1), s * (o.sy ?? 1)); ctx.translate(-ax, -m.footY);
  const inkClip = c => { c.beginPath(); c.moveTo(-60, -60); const yy = -60 + (H + 220) * ink; for (let i = 0; i <= 24; i++) { const xx = -60 + (W + 120) * i / 24; c.lineTo(xx, yy + (fbm(xx * .01, 3, 7, 2) - .5) * 200); } c.lineTo(W + 60, -60); c.closePath(); };
  const paint = () => {
    if (ink <= 0) return;
    ctx.save(); if (ink < 1) { inkClip(ctx); ctx.clip(); }
    ctx.globalAlpha = A0; ctx.drawImage(IMG[n + '_mask'], 0, 0);
    if (col > 0) { ctx.save(); if (col < 1) { noisyCircle(W * .5, H * .42, Math.hypot(W, H) * .62 * col + 1, 11)(ctx); ctx.clip(); } ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = A0; ctx.drawImage(IMG[n], 0, 0); ctx.restore(); }
    ctx.globalAlpha = A0 * (1 - .8 * col); ctx.drawImage(IMG[n + '_ink'], 0, 0);
    ctx.restore();
  };
  const path = poly => { poly.forEach(([px, py], i) => i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)); ctx.closePath(); };
  if (o.arm) {
    const { poly, pivot, ang } = o.arm;
    ctx.save(); ctx.beginPath(); ctx.rect(-80, -80, W + 160, H + 160); path(poly); ctx.clip('evenodd'); paint(); ctx.restore();
    ctx.save(); ctx.translate(pivot[0], pivot[1]); ctx.rotate(ang); ctx.translate(-pivot[0], -pivot[1]); ctx.beginPath(); path(poly); ctx.clip(); paint(); ctx.restore();
  } else paint();
  ctx.restore();
  return { s, at: (px, py) => [x + (px - ax) * s * (o.sx ?? 1), y + (py - m.footY) * s * (o.sy ?? 1)] };
}
const ARM = { poly: [[0, 120], [150, 120], [150, 230], [110, 300], [98, 385], [82, 440], [20, 444], [4, 300], [0, 250]], pivot: [52, 446] };
function shadow(x, y, S, a) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = rgba(hex('#8a8070'), a); ctx.beginPath(); ctx.ellipse(x + S * .02, y + S * .004, S * .19, S * .028, 0, 0, TAU); ctx.fill(); ctx.restore(); }


// ---------------- dynamic bits ----------------
function weekTracker(t) {
  handwrite(ctx, TRACK.days, TRACK.x, TRACK.y, 38, eo(seg(t, -.2, .5)), { font: '"Reenie Beanie"', rot: .05 });
  const grey = seg(t, 2.6, 3.2);
  for (let k = 0; k < 5; k++) {
    const p = eo(seg(t, tickT(k), tickT(k) + .12)); if (p <= 0) continue;
    const x = TRACK.x + 5 + k * 26.5, y = TRACK.y + 24 + k * 1.3;
    drawPen(ctx, penStroke([[x - 8, y], [x - 2, y + 9], [x + 12, y - 12]], { w: 4, wob: .5, seed: 300 + k, over: 2 }), p, mix3(C.coralD, [130, 128, 124], grey), 1);
  }
  const sc = eo(seg(t, 2.75, 3.25));   // "then life happened": scribbled out
  if (sc > 0) { const P = []; for (let i = 0; i < 9; i++) P.push([TRACK.x - 6 + i * 23, TRACK.y + (i % 2 ? 50 : -14)]); drawPen(ctx, penStroke(P, { w: 3, wob: 1, seed: 330, over: 3, smooth: false }), sc, INK, .85); }
  handwrite(ctx, '5 days!', TRACK.x + 30, TRACK.y + 110, 50, eo(seg(t, 1.5, 1.95)), { font: 'Caveat', weight: 600, col: C.coralD, rot: .05 });
}
function title(t) {
  const p = eo(seg(t, .05, .85)); if (p <= 0) return;
  ctx.save(); ctx.translate(800, 420); ctx.rotate(-.025);
  handwrite(ctx, 'COMEBACK DAY 1', 0, 0, 132, p, { font: 'Caveat', weight: 700, align: 'center' });
  const u = eo(seg(t, .7, 1.05)); if (u > 0) drawPen(ctx, penStroke([[-330, 30], [0, 40], [340, 26]], { w: 7, wob: 1.6, seed: 9, over: 8 }), u, C.coral, .95);
  ctx.restore();
}
function rain(t) {   // rain lines over the city, 7.35 to 11.1, drawn fresh every 1/12 s
  if (t < 7.35 || t > 11.2) return; const a = seg(t, 7.35, 7.8) * (1 - seg(t, 10.9, 11.2)), R = rng(boil(t) + 900);
  ctx.save(); ctx.strokeStyle = rgba(hex('#5d6a7d'), .55 * a); ctx.lineWidth = 2; ctx.lineCap = 'round';
  for (let k = 0; k < 70; k++) { const x = 300 + R() * 1300, y = 3560 + R() * 900, l = 30 + R() * 30; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - l * .25, y + l); ctx.stroke(); }
  ctx.restore();
}
function plane(t) {   // a little plane flying the dotted line on "moved countries"
  const u = seg(t, 5.3, 6.5); if (u <= 0 || u >= 1) return;
  const P = v => [lerp(330, 1350, v), 2820 - Math.sin(v * Math.PI) * 220], [x, y] = P(u), [x2, y2] = P(u + .01), a = Math.atan2(y2 - y, x2 - x);
  ctx.save(); ctx.translate(x, y); ctx.rotate(a);
  const body = [[-40, -6], [30, -6], [44, 0], [30, 6], [-40, 6]];
  drawPrims(ctx, [{ k: 'knock', poly: body }, { k: 'ink', st: penStroke(closed(body), { w: 2.2, wob: .5, seed: 5, smooth: false }) }, { k: 'ink', st: penStroke([[-5, -6], [-20, -30], [5, -6]], { w: 2, wob: .4, seed: 6, smooth: false }) }, { k: 'ink', st: penStroke([[-5, 6], [-20, 30], [5, 6]], { w: 2, wob: .4, seed: 7, smooth: false }) }], {});
  ctx.restore();
}
function dumbbell(t) {   // coral wash on the dumbbell, fading as its ink erases (8.5 to 9.9)
  if (t < 3.75) return; const f = 1 - seg(t, 8.5, 9.9), app = eo(seg(t, 3.9, 4.4)); if (f <= 0) return;
  for (const d of DUMB) { ctx.save(); ctx.globalAlpha = f * app; wash(ctx, d.poly, C.coral, { a: .7, j: 2.5, layers: 2, edge: .35, seed: 400, dx: 3, dy: 2 }); ctx.restore(); }
  if (t > 8.5) { const R = rng(500 + boil(t)); ctx.save(); ctx.fillStyle = rgba(C.coral, .5 * f); for (let k = 0; k < 14; k++) { const x = 420 + (R() - .5) * 260, y = 4300 - seg(t, 8.5, 9.9) * 140 * R() - 70 * R(); ctx.beginPath(); ctx.arc(x, y, 3 + R() * 4, 0, TAU); ctx.fill(); } ctx.restore(); }
}
function breath(t, mouth, h) {   // breath drawn as ink curls from her mouth, 13.6 to 16.6
  if (t < 13.55 || t > 16.9) return;
  for (let k = 0; k < 6; k++) {
    const tk = 13.6 + k * .5, age = t - tk; if (age < 0 || age > 1.0 || tk > 16.0) continue;
    const pts = []; for (let i = 0; i <= 20; i++) { const u = i / 20; pts.push([mouth[0] - u * 170, mouth[1] + Math.sin(u * 7 + k) * 16 - u * 30]); }
    const cx = mouth[0] - 185, cy = mouth[1] - 44; for (let i = 1; i <= 14; i++) { const a = i / 14 * TAU * .9, r = 24 * (1 - i / 14 * .5); pts.push([cx - Math.sin(a) * r, cy + 14 - Math.cos(a) * r]); }
    drawPen(ctx, penStroke(pts, { w: 2.6, wob: .7, seed: 700 + k, over: 1 }), eo(age / .35), INK, .8, ei(clamp((age - .45) / .5)));
  }
  if (t > 14.4 && t < 15.6) { const u = seg(t, 14.4, 15.6); for (let k = 0; k < 3; k++) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; dab(ctx, h.c[0] + 30 + k * 40 + u * 60, h.c[1] - h.r - 20 - u * 80 + u * u * 160 + k * 10, 9, 1.2, C.bottle, .8 * (1 - u), 800 + k); ctx.restore(); } }
}
function thought(t, h) {   // "nothing.": an empty thought bubble pops up
  const p = eo(seg(t, 16.12, 16.5)); if (p <= 0 || t > 17.4) return; const cx = h.c[0] + 60, cy = h.c[1] - h.r * 3.3;
  const bub = ellipse(cx + 80, cy - 70, 150, 100, 24);
  drawPrims(ctx, [{ k: 'knock', poly: bub, a: .95 * p }], {});
  drawPen(ctx, penStroke(closed(bub), { w: 3, wob: 1.2, seed: 901, over: 4 }), p);
  drawPen(ctx, penStroke(ellipse(cx - 10, cy + 60, 22, 18, 12), { w: 2.6, wob: .6, seed: 902 }), eo(seg(t, 16.05, 16.25)));
  drawPen(ctx, penStroke(ellipse(cx - 40, cy + 110, 12, 10, 10), { w: 2.4, wob: .5, seed: 903 }), eo(seg(t, 16.0, 16.15)));
}
function checklist(t) {
  for (const c of CHECK) {
    const p = eo(seg(t, c.t, c.t + .6)); if (p <= 0) continue;
    const w = handwrite(ctx, c.text, c.x, c.y, 74, p, { font: 'Caveat', weight: 600, rot: -.02 });
    if (c.mark === 'tick') { const m = eo(seg(t, c.t + .6, c.t + .8)), x = c.x - 60, y = c.y - 20; drawPen(ctx, penStroke([[x - 16, y], [x - 4, y + 18], [x + 24, y - 26]], { w: 6, wob: .8, seed: 950, over: 3 }), m, C.coralD); }
    else { const m = eo(seg(t, c.mt, c.mt + .35)), x0 = c.x - 10, x1 = c.x + (w ?? 300) + 10, y = c.y - 22; drawPen(ctx, penStroke([[x0, y + 6], [lerp(x0, x1, .5), y - 4], [x1, y + 4]], { w: 6, wob: 1.4, seed: 960 + c.t | 0, over: 6 }), m, C.coralD); }
  }
}
function gulls(t) {
  if (t < 17.2 || t > 33) return;
  for (let k = 0; k < 5; k++) {
    const x = 400 + k * 900 + (t - 17) * (40 + k * 8), y = 6850 + (k % 3) * 90 + 20 * Math.sin(t * .8 + k), f = Math.sin(t * (6 + k) + k) * 14, s = 26 + (k % 2) * 8;
    drawPen(ctx, penStroke([[x - s, y - f], [x - s * .35, y - 4], [x, y + 4], [x + s * .35, y - 4], [x + s, y - f]], { w: 2.2, wob: .4, seed: 980 + k + boil(t) % 3, over: 1 }), 1, INK, .85);
  }
}
function notesMargin(t) { for (const n of NOTES) handwrite(ctx, n.text, n.x, n.y, n.size, eo(seg(t, n.t, n.t + .5)), { font: n.font, alpha: .85, rot: -.04 }); }

// ---------------- captions (handwritten, lower margin, above the UI zone) ----------------
const CAPS = [
  [0.40, 2.45, 'I used to work out five days a week.'], [2.45, 4.25, 'Then life happened.'],
  [4.25, 6.40, 'Final year of uni, moved countries,'], [6.40, 8.25, 'started working part-time...'], [8.25, 10.65, 'and the gym just slowly disappeared.'],
  [11.10, 13.70, "So today, I'm starting again."], [13.70, 16.05, 'And my body remembers...'], [16.05, 17.50, 'nothing.'],
  [17.55, 20.40, "I'm posting every step of this comeback."], [20.40, 22.45, "Not after I'm back in shape."], [22.45, 24.25, 'From day 1.'],
  [24.25, 27.60, 'No extreme diets, no 5 a.m. punishment.'], [27.80, 29.75, "If you've fallen off too,"], [29.75, 31.80, 'come do this with me.'], [31.80, 33.30, 'See you on Day 2.'],
];
const CAP_Y = 1395, CAP_SIZE = 70, CAP_MAX = 920;
function wrap(text) {
  ctx.font = `500 ${CAP_SIZE * K}px Caveat`; if (ctx.measureText(text).width <= CAP_MAX * K) return [text];
  const w = text.split(' '); let best = [text], bd = 1e9;
  for (let i = 1; i < w.length; i++) { const a = w.slice(0, i).join(' '), b = w.slice(i).join(' '), d = Math.abs(ctx.measureText(a).width - ctx.measureText(b).width); if (d < bd) { bd = d; best = [a, b]; } }
  return best;
}
function captions(t) {
  for (const [t0, t1, text] of CAPS) {
    if (t < t0 || t > t1) continue;
    const lines = wrap(text), p = eo(seg(t, t0, t0 + .35)), fade = 1 - seg(t, t1 - .12, t1);
    ctx.save(); ctx.globalAlpha = fade;
    lines.forEach((ln, i) => {
      const y = (CAP_Y + (i - (lines.length - 1)) * CAP_SIZE * 1.02) * K;
      ctx.font = `500 ${CAP_SIZE * K}px Caveat`; const w = ctx.measureText(ln).width;
      // soft paper halo so the line reads over the drawing
      ctx.save(); ctx.globalCompositeOperation = 'source-over';
      const g = rough(ellipse(SW / 2, y - CAP_SIZE * .3 * K, w * .56 + 30 * K, CAP_SIZE * .62 * K, 26), 8 * K, 5 + i, 9 * K);
      ctx.fillStyle = rgba(PAPER, .8); ctx.beginPath(); g.forEach(([x, yy], k) => k ? ctx.lineTo(x, yy) : ctx.moveTo(x, yy)); ctx.closePath(); ctx.filter = `blur(${10 * K}px)`; ctx.fill(); ctx.restore();
      handwrite(ctx, ln, SW / 2, y, CAP_SIZE * K, clamp(p * 1.15 - i * .15), { font: 'Caveat', weight: 500, align: 'center' });
    });
    ctx.restore();
  }
}
window.TEXTS = t => CAPS.filter(c => t >= c[0] + .35 && t <= c[1] - .12).map((c, i) => ({ id: 'cap' + c[0], text: c[2], x0: 60, y0: 1250 * K, x1: SW - 60, y1: 1440 * K }));

// ---------------- page turn + Day 2 ----------------
const TURN0 = 33.05, TURN1 = 33.85;
function nextPage(t) {
  ctx.save(); ctx.setTransform(K, 0, 0, K, 0, 0);
  ctx.drawImage(mott, 0, 0, 200, 300, 0, 0, 1080, 1920);
  ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = toothPat; ctx.fillRect(0, 0, 1080, 1920); ctx.globalCompositeOperation = 'source-over';
  handwrite(ctx, 'day 2 . same seawall, probably', 120, 330, 52, eo(seg(t, 34.0, 34.6)), { font: '"Reenie Beanie"', alpha: .85, rot: -.03 });
  ctx.translate(540, 900); ctx.rotate(-.03);
  handwrite(ctx, 'Day 2', 0, 0, 260, eo(seg(t, 34.0, 34.9)), { font: 'Caveat', weight: 700, align: 'center' });
  const u = eo(seg(t, 34.8, 35.15)); if (u > 0) drawPen(ctx, penStroke([[-240, 50], [0, 62], [250, 44]], { w: 9, wob: 2, seed: 19, over: 10 }), u, C.coral, .95);
  const s = eo(seg(t, 35.1, 35.6)); if (s > 0) handwrite(ctx, 'see you there', 0, 190, 70, s, { font: 'Caveat', weight: 500, align: 'center', alpha: .85 });
  ctx.restore();
}
function pageTurn(t) {   // the current page lifts from the right and turns over to the left, the next page underneath
  const u = eio(seg(t, TURN0, TURN1)), ex = lerp(SW * 1.05, -SW * .6, u), tilt = .22 * SW;
  const edge = y => ex + tilt * (y / SH - .5) * (1 - u * .5);
  ctx.save(); ctx.beginPath(); ctx.moveTo(SW + 10, -10); ctx.lineTo(edge(0), -10); for (let y = 0; y <= SH; y += 40) ctx.lineTo(edge(y), y); ctx.lineTo(SW + 10, SH + 10); ctx.closePath(); ctx.clip(); nextPage(t); ctx.restore();
  const bw = SW * .32 * Math.sin(u * Math.PI);   // the back of the turning page
  if (bw > 2) {
    ctx.save(); ctx.beginPath(); ctx.moveTo(edge(0), 0); for (let y = 0; y <= SH; y += 40) ctx.lineTo(edge(y), y); for (let y = SH; y >= 0; y -= 40) ctx.lineTo(edge(y) - bw, y); ctx.closePath();
    const g = ctx.createLinearGradient(ex, 0, ex - bw, 0); g.addColorStop(0, '#d9d0bc'); g.addColorStop(.35, '#f3ecdc'); g.addColorStop(1, '#ebe3d0');
    ctx.fillStyle = g; ctx.shadowColor = 'rgba(40,30,20,.35)'; ctx.shadowBlur = 40 * K; ctx.shadowOffsetX = -14 * K; ctx.fill(); ctx.restore();
  }
}

// ---------------- render ----------------
function renderPage(t) {
  const cam = camera(t), c = Math.cos(cam.rot), s = Math.sin(cam.rot);
  const tf = [cam.z * c, cam.z * s, -cam.z * s, cam.z * c, SW / 2 - cam.z * (c * cam.cx - s * cam.cy), SH / 2 - cam.z * (s * cam.cx + c * cam.cy)];
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = '#f5eede'; ctx.fillRect(0, 0, SW, SH);
  ctx.setTransform(...tf);
  const r = Math.hypot(SW, SH) / 2 / cam.z, vx0 = cam.cx - r, vx1 = cam.cx + r, vy0 = cam.cy - r, vy1 = cam.cy + r;
  ctx.imageSmoothingEnabled = true; ctx.drawImage(mott, WX0, WY0, WX1 - WX0, WY1 - WY0);
  // washes, revealed by their colour arrival
  for (const L of LAYERS) {
    if (L.x1 < vx0 || L.x0 > vx1 || L.y1 < vy0 || L.y0 > vy1) continue;
    const rv = L.reveal(t); if (!rv) continue;
    ctx.save(); if (rv !== 'full') { rv(ctx); ctx.clip(); }
    ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(L.c, L.x0, L.y0, L.x1 - L.x0, L.y1 - L.y0); ctx.restore();
  }
  dumbbell(t);
  // ink in stroke order
  for (const S of STROKES) {
    const [a, b, cc, d] = S.bb; if (cc < vx0 || a > vx1 || d < vy0 || b > vy1) continue;
    const p = S.d > 0 ? clamp((t - S.t0) / S.d) : (t >= S.t0 ? 1 : 0); if (p <= 0) continue;
    let al = S.a, from = 0; if (S.fade) { const f = seg(t, S.fade[0], S.fade[1]); from = ei(f); al *= 1 - f * .6; }
    drawPen(ctx, S.st, eo(p), S.col ?? INK, al, from);
  }
  notesMargin(t); rain(t); plane(t);
  // her, in the scene the camera is on
  if (cam.cy < 2400) {
    const col = eo(seg(t, .45, 1.25));
    shadow(A.gx, A.gy, A.S, .3 * col);
    her('selfie', A.gx, A.gy, A.S, eo(seg(t, -.35, .6)), col, { sy: 1 + .004 * Math.sin(t * 2.2) });
    weekTracker(t); title(t);
  }
  if (cam.cy > 4700 && cam.cy < 6300 && t > 11.0) {
    const col = eo(seg(t, 12.3, 13.2)), br = Math.sin((t - 11) * TAU * 1.45) * (1 - .6 * seg(t, 16.1, 17));
    shadow(Cn.gx + 60, Cn.gy, 1100, .3 * col);
    const f = her('tired', Cn.gx, Cn.gy, 880, eo(seg(t, 11.3, 12.3)), col, { sy: 1 + .012 * br, sx: 1 - .004 * br });
    const head = { c: f.at(115, 150), r: 70 * f.s };
    breath(t, f.at(37, 193), head); thought(t, head);
  }
  if (t > 17.0) {
    gulls(t); checklist(t);
    const x = herX(t), H = 770;
    shadow(x, Dn.gy, H, .3);
    if (t < WALK1 + .3) {
      const k = t < WALK0 ? 0 : Math.floor((t - WALK0) / (STEP / 2)) % 4;
      her('walk' + k, x, Dn.gy, H, eo(seg(t, 17.2, 17.8)), eo(seg(t, 17.5, 18.2)), { alpha: 1 - seg(t, WALK1 + .05, WALK1 + .3) });
    }
    if (t >= WALK1) {
      const w = clamp((t - WALK1 - .6) / .4) * (1 - seg(t, 31.2, 31.7));
      her('wave', x, Dn.gy, H * 1.02, eo(seg(t, WALK1 - .05, WALK1 + .22)), eo(seg(t, WALK1 + .05, WALK1 + .4)), { sy: 1 + .004 * Math.sin(t * 2.4), arm: { ...ARM, ang: -.13 * Math.sin((t - WALK1) * TAU * 1.5) * w } });
    }
  }
  // paper tooth over everything
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = toothPat; ctx.setTransform(tf[0] * .8, tf[1] * .8, tf[2] * .8, tf[3] * .8, tf[4], tf[5]);
  ctx.fillRect((vx0 - 200) / .8, (vy0 - 200) / .8, (vx1 - vx0 + 400) / .8, (vy1 - vy0 + 400) / .8); ctx.restore();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
}
window.DUR = DUR;
window.render = t => {
  renderPage(Math.min(t, TURN1));
  if (t < TURN0) captions(t);
  if (t >= TURN0) pageTurn(t);
};

// ---------------- sound cues for the mixer ----------------
EV.push({ t: 0.0, type: 'title' }, { t: 2.75, type: 'scribble' }, { t: 3.3, type: 'whoosh', d: .8 }, { t: 5.3, type: 'plane' }, { t: 7.0, type: 'rainIn' },
  { t: 8.5, type: 'erase', d: 1.4 }, { t: 11.05, type: 'whip' }, { t: 12.3, type: 'bloom' }, { t: 16.1, type: 'punch' }, { t: 16.12, type: 'pop' },
  { t: 17.0, type: 'whoosh', d: .75 }, { t: 17.2, type: 'seaIn' }, { t: 18.1, type: 'bloom' }, { t: TURN0, type: 'pageTurn' }, { t: 34.0, type: 'writeDay2', d: .9 });
for (let k = 0; k < 5; k++) EV.push({ t: +tickT(k).toFixed(3), type: 'tick' });
for (const c of CHECK) { EV.push({ t: c.t, type: 'write', d: .6 }); EV.push({ t: c.mark === 'tick' ? c.t + .6 : c.mt, type: c.mark }); }
for (let k = 0; k < 6; k++) { const tk = 13.6 + k * .5; if (tk <= 16.0) EV.push({ t: +tk.toFixed(3), type: 'breath' }); }
for (let t = WALK0 + STEP * .5; t < WALK1; t += STEP) EV.push({ t: +t.toFixed(3), type: 'step' });
CAPS.forEach(c => EV.push({ t: c[0], type: 'capWrite', d: .35 }));
EV.sort((a, b) => a.t - b.t);
window.EV = EV;
window.READY = true;
