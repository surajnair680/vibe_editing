// Render a "window.seek(seconds)" HTML page (the motion-graphics-skills pack format) to stills or an MP4.
// Works with any page that draws a frame from the time alone: window.seek(t) or window.renderFrame(t).
// Uses the container's preinstalled Chromium through Playwright. Never run "playwright install".
//
// Stills (the user rule: send these before any full render):
//   node tools/seek_render.mjs page.html --size 1080x1920 --dur 14 --every 2.5 --sheet out/sheet.png
//   node tools/seek_render.mjs page.html --size 1080x1920 --at 0.5,3.2,7 --dir out/stills
// Video:
//   node tools/seek_render.mjs page.html --size 1080x1920 --fps 30 --dur 14 -o out/master.mp4 [--audio work/mix.wav]
//   add --start a --end b to render only part of it (revisions), --scale 0.5 for a quick low-res draft,
//   --jpeg for faster frames (drafts; masters default to lossless png frames).
//
// The page is opened as file://page.html?render=1&w=W&h=H. It may define window.ready (a promise) to wait for
// images; fonts are awaited through document.fonts.ready. Each frame is drawn by seek(t) then screenshotted.
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
let chromium;
for (const p of ['playwright', '/opt/node-tools/node_modules/playwright', '/usr/local/lib/node_modules_global/playwright']) {
  try { ({ chromium } = require(p)); break; } catch { /* try next */ }
}
if (!chromium) { console.error('x Playwright not found (it is preinstalled in this container; never install a browser)'); process.exit(1); }

const args = process.argv.slice(2);
const has = k => args.includes('--' + k) || args.includes(k);
const opt = (k, d) => { const i = args.indexOf(k.startsWith('-') ? k : '--' + k); return i >= 0 ? args[i + 1] : d; };
if (!args[0] || args[0].startsWith('-')) { console.error('usage: node tools/seek_render.mjs page.html --size WxH ...'); process.exit(1); }
const html = path.resolve(args[0]);
const [W, H] = (opt('size', '1080x1920')).split('x').map(Number);
const FPS = +opt('fps', 30);
const DUR = +opt('dur', 0);
const scale = +opt('scale', 1);
const out = opt('-o', null);
const audio = opt('audio', null);
const start = +opt('start', 0);
const end = +opt('end', DUR);
const crf = opt('crf', '14');

async function openPage() {
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: scale });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(`file://${html}?render=1&w=${W}&h=${H}`);
  try {
    await page.waitForFunction(() => typeof window.seek === 'function' || typeof window.renderFrame === 'function', null, { timeout: 15000 });
  } catch {
    console.error('x the page has no window.seek(t) or window.renderFrame(t)');
    if (errors.length) console.error('  page errors:\n  ' + errors.join('\n  '));
    await browser.close(); process.exit(1);
  }
  await page.evaluate(async () => { if (window.ready) await window.ready; if (document.fonts) await document.fonts.ready; });
  const draw = async t => page.evaluate(async t => { const f = window.seek || window.renderFrame; await f(t); }, t);
  // Draw once so lazily used fonts load before the first real frame (the pack's "frame 0 in the wrong font" bug).
  await draw(0); await page.evaluate(async () => { if (document.fonts) await document.fonts.ready; });
  return { browser, page, draw, errors };
}
const shot = (page, type = 'png') => page.screenshot({ type, ...(type === 'jpeg' ? { quality: 92 } : {}), clip: { x: 0, y: 0, width: W, height: H } });
const fmt = t => (Math.round(t * 100) / 100).toFixed(t % 1 ? (t * 10 % 1 ? 2 : 1) : 0);

async function stills() {
  let times;
  if (opt('at', null)) times = opt('at').split(',').map(Number);
  else {
    const every = +opt('every', 2.5);
    if (!DUR) { console.error('x --dur is needed with --every'); process.exit(1); }
    times = []; for (let t = 0; t < DUR - 1e-6; t += every) times.push(+t.toFixed(3));
  }
  const dir = path.resolve(opt('dir', path.join(path.dirname(path.resolve(opt('sheet', 'out/sheet.png'))), 'stills')));
  fs.mkdirSync(dir, { recursive: true });
  const { browser, page, draw, errors } = await openPage();
  const files = [];
  for (const t of times) {
    await draw(t);
    const f = path.join(dir, `t${fmt(t).padStart(5, '0')}.png`);
    fs.writeFileSync(f, await shot(page));
    files.push([t, f]);
  }
  if (opt('sheet', null)) {
    const sheet = path.resolve(opt('sheet'));
    fs.mkdirSync(path.dirname(sheet), { recursive: true });
    const cols = +opt('cols', 6), tw = 300, th = Math.round(tw * H / W);
    const rows = Math.ceil(files.length / cols);
    const sw = cols * (tw + 12) + 12, sh = rows * (th + 40) + 12;
    await page.setViewportSize({ width: sw, height: sh });
    const cells = files.map(([t, f]) => `<div class=c><img src="file://${f}"><b>${fmt(t)} s</b></div>`).join('');
    await page.setContent(`<style>body{margin:0;background:#111;display:flex;flex-wrap:wrap;padding:6px;width:${sw - 12}px}
      .c{width:${tw}px;margin:6px;color:#fff;font:600 18px sans-serif;text-align:center}
      img{width:${tw}px;height:${th}px;display:block;background:#333}</style>${cells}`);
    await page.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 1 : new Promise(r => i.onload = i.onerror = r))));
    await page.screenshot({ path: sheet, fullPage: true });
    console.log(`sheet -> ${sheet}`);
  }
  await browser.close();
  if (errors.length) console.log('! page errors:\n  ' + errors.join('\n  '));
  console.log(`${files.length} stills -> ${dir}`);
}

async function video() {
  if (!DUR) { console.error('x --dur is needed for a video'); process.exit(1); }
  const o = path.resolve(out);
  fs.mkdirSync(path.dirname(o), { recursive: true });
  const ow = Math.round(W * scale / 2) * 2, oh = Math.round(H * scale / 2) * 2;
  const jpg = has('jpeg') || scale < 1;  // png is lossless; --jpeg (q 92) is faster for drafts
  const ff = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', jpg ? 'mjpeg' : 'png', '-framerate', String(FPS), '-i', '-'];
  if (audio) ff.push('-ss', String(start), '-t', String(end - start), '-i', path.resolve(audio), '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-shortest');
  ff.push('-vf', `scale=${ow}:${oh}:flags=lanczos:out_color_matrix=bt709:out_range=tv,format=yuv420p`,
    '-c:v', 'libx264', '-crf', crf, '-preset', 'veryfast', '-colorspace', 'bt709', '-color_primaries', 'bt709',
    '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', o);
  const enc = spawn('ffmpeg', ff, { stdio: ['pipe', 'inherit', 'inherit'] });
  const { browser, page, draw, errors } = await openPage();
  const i0 = Math.round(start * FPS), i1 = Math.round(end * FPS);
  const t0 = Date.now();
  for (let i = i0; i < i1; i++) {
    await draw(i / FPS);
    const buf = await shot(page, jpg ? 'jpeg' : 'png');
    if (!enc.stdin.write(buf)) await new Promise(r => enc.stdin.once('drain', r));
    if ((i - i0) % FPS === 0) process.stdout.write(`\r  frame ${i - i0}/${i1 - i0}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  enc.stdin.end();
  await browser.close();
  await new Promise(r => enc.on('close', r));
  if (errors.length) console.log('\n! page errors:\n  ' + errors.join('\n  '));
  console.log(`\ndone -> ${o}`);
}

if (out) await video(); else await stills();
