// Voxel reels: the world and the box-built characters. Everything is set from t alone (deterministic).
import * as THREE from '/node_modules/three/build/three.module.js';

export { THREE };
const box = (w, h, d, color, opts = {}) => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d),
    new THREE.MeshStandardMaterial({ color, roughness: opts.rough ?? 0.75, metalness: 0, emissive: opts.emissive ?? 0x000000, emissiveIntensity: opts.ei ?? 1 }));
  m.castShadow = opts.shadow ?? true; m.receiveShadow = true;
  return m;
};
const at = (m, x, y, z) => { m.position.set(x, y, z); return m; };
const hash = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };

// ---- world -------------------------------------------------------------------------------------------------
export function makeWorld(renderer, W, H, look = {}) {
  const L = Object.assign({ sky: 0x0b1030, fog: 0x0b1030, grid: 0x5a6cff, floor: 0x0d1238, key: 0xffd9a8, rim: 0x9b6bff, bokeh: [0x6c7bff, 0xff7ad9, 0x5ce1e6, 0xffd60a] }, look);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(L.sky); scene.fog = new THREE.Fog(L.fog, 9, 26);
  const camera = new THREE.PerspectiveCamera(32, W / H, 0.1, 100);

  // floor + glowing grid
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: L.floor, roughness: 0.9 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const grid = new THREE.GridHelper(60, 60, L.grid, L.grid); grid.position.y = 0.002;
  grid.material.transparent = true; grid.material.opacity = 0.45; scene.add(grid);

  // soft blurred bokeh dots far behind (sprites with a radial gradient)
  const cv = document.createElement('canvas'); cv.width = cv.height = 128;
  const g = cv.getContext('2d'), rg = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  rg.addColorStop(0, 'rgba(255,255,255,0.9)'); rg.addColorStop(0.4, 'rgba(255,255,255,0.35)'); rg.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = rg; g.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const bokeh = [];
  for (let i = 0; i < 40; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color: L.bokeh[i % L.bokeh.length], transparent: true, opacity: 0.25 + 0.35 * hash(i * 3.1), depthWrite: false, fog: false }));
    const sc = 0.4 + 1.4 * hash(i * 7.7);
    s.scale.set(sc, sc, 1);
    s.userData = { x: (hash(i) - 0.5) * 22, y: 0.5 + hash(i * 1.9) * 7, z: -8 - hash(i * 5.3) * 10, ph: hash(i * 9.1) * 6.28 };
    scene.add(s); bokeh.push(s);
  }

  // lights: warm key with soft shadows, purple rim from behind, weak fill
  const key = new THREE.DirectionalLight(L.key, 2.4); key.position.set(3.5, 6, 5); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024); key.shadow.camera.left = -5; key.shadow.camera.right = 5; key.shadow.camera.top = 5; key.shadow.camera.bottom = -2;
  key.shadow.radius = 4; key.shadow.bias = -0.0005; scene.add(key);
  const rim = new THREE.DirectionalLight(L.rim, 2.2); rim.position.set(-3, 4, -5); scene.add(rim);
  scene.add(new THREE.HemisphereLight(0x8090ff, 0x101030, 0.55));

  function update(t) {
    for (const s of bokeh) { const u = s.userData; s.position.set(u.x + Math.sin(t * 0.15 + u.ph) * 0.3, u.y + Math.sin(t * 0.22 + u.ph) * 0.2, u.z); }
  }
  return { scene, camera, update };
}

// ---- characters --------------------------------------------------------------------------------------------
// A human: {kind:'human', skin, hair, shirt, pants, shoes, height (1 = normal), hairStyle:'short'|'long'|'bald'|'bun', beard}
// A buddy: {kind:'buddy', body, face, accent, antenna:true} : a small box creature whose eyes switch ^ ^ / | | / o o
export function makeCharacter(o) {
  return o.kind === 'buddy' ? makeBuddy(o) : makeHuman(o);
}

function eyes(parent, y, z, spread, size, opts = {}) {
  const out = [];
  for (const sx of [-1, 1]) {
    const e = new THREE.Group(); at(e, sx * spread, y, z);
    const white = box(size, size, 0.04, 0xffffff, { shadow: false, rough: 0.4 });
    const pupil = at(box(size * 0.62, size * 0.62, 0.05, 0x14141c, { shadow: false, rough: 0.3 }), 0, 0, 0.012);
    const glint = at(box(size * 0.2, size * 0.2, 0.05, 0xffffff, { shadow: false, emissive: 0xffffff, ei: 0.6 }), size * 0.14, size * 0.14, 0.03);
    e.add(white, pupil, glint); parent.add(e);
    out.push({ g: e, white, pupil, glint });
  }
  return out;
}

function makeHuman(o) {
  const C = Object.assign({ skin: 0xe0ac85, hair: 0x2b1a12, shirt: 0x2d7dff, pants: 0x1f2433, shoes: 0xf2f2f2, height: 1, hairStyle: 'short', beard: false }, o);
  const root = new THREE.Group(), body = new THREE.Group(); root.add(body);
  const hs = C.height;
  const legL = at(box(0.2, 0.62 * hs, 0.24, C.pants), -0.13, 0.31 * hs + 0.08, 0), legR = at(box(0.2, 0.62 * hs, 0.24, C.pants), 0.13, 0.31 * hs + 0.08, 0);
  const shoeL = at(box(0.22, 0.1, 0.32, C.shoes), -0.13, 0.05, 0.04), shoeR = at(box(0.22, 0.1, 0.32, C.shoes), 0.13, 0.05, 0.04);
  const hip = 0.7 * hs + 0.08;
  const torso = at(box(0.6, 0.66 * hs, 0.34, C.shirt), 0, hip + 0.33 * hs, 0);
  body.add(legL, legR, shoeL, shoeR, torso);
  const shoulderY = hip + 0.6 * hs;
  const arm = sx => { const p = new THREE.Group(); at(p, sx * 0.4, shoulderY, 0);
    const sleeve = at(box(0.19, 0.3, 0.22, C.shirt), 0, -0.13, 0), fore = at(box(0.16, 0.34, 0.18, C.skin), 0, -0.44, 0), hand = at(box(0.18, 0.14, 0.2, C.skin), 0, -0.66, 0);
    p.add(sleeve, fore, hand); body.add(p); return p; };
  const armL = arm(-1), armR = arm(1);
  // big head
  const head = new THREE.Group(); at(head, 0, shoulderY + 0.06, 0); body.add(head);
  const skull = at(box(0.78, 0.74, 0.7, C.skin), 0, 0.42, 0); head.add(skull);
  if (C.hairStyle !== 'bald') {
    head.add(at(box(0.84, 0.2, 0.76, C.hair), 0, 0.84, -0.01), at(box(0.84, 0.46, 0.18, C.hair), 0, 0.6, -0.31));
    head.add(at(box(0.1, 0.3, 0.6, C.hair), -0.41, 0.62, -0.04), at(box(0.1, 0.3, 0.6, C.hair), 0.41, 0.62, -0.04));
    if (C.hairStyle === 'long') head.add(at(box(0.86, 0.62, 0.2, C.hair), 0, 0.22, -0.33), at(box(0.12, 0.6, 0.3, C.hair), -0.42, 0.28, -0.18), at(box(0.12, 0.6, 0.3, C.hair), 0.42, 0.28, -0.18));
    if (C.hairStyle === 'bun') head.add(at(box(0.3, 0.26, 0.3, C.hair), 0, 1.02, -0.12));
  }
  // beard: chin block plus side strips, leaving the mouth area open
  if (C.beard) head.add(at(box(0.8, 0.14, 0.2, C.hair), 0, 0.1, 0.28), at(box(0.16, 0.24, 0.2, C.hair), -0.31, 0.2, 0.28), at(box(0.16, 0.24, 0.2, C.hair), 0.31, 0.2, 0.28), at(box(0.34, 0.05, 0.05, C.hair, { shadow: false }), 0, 0.31, 0.36));
  const ey = eyes(head, 0.5, 0.355, 0.17, 0.15);
  const brows = [-1, 1].map(sx => { const b = at(box(0.2, 0.06, 0.05, C.hairStyle === 'bald' ? 0x2b1a12 : C.hair, { shadow: false }), sx * 0.17, 0.66, 0.36); head.add(b); return b; });
  const mouth = at(box(0.2, 0.05, 0.05, 0x8a2a35, { shadow: false, rough: 0.5 }), 0, 0.24, 0.37); head.add(mouth);
  const ch = { root, body, head, mouth, eyes: ey, brows, armL, armR, kind: 'human', headY: shoulderY + 0.48, height: shoulderY + 0.95 };
  return ch;
}

function makeBuddy(o) {
  const C = Object.assign({ body: 0x2ec4b6, face: 0x0f1a2a, accent: 0xffd60a, antenna: true, size: 0.75 }, o);
  const root = new THREE.Group(), body = new THREE.Group(); root.add(body);
  const s = C.size;
  const legL = at(box(0.14 * s, 0.22 * s, 0.16 * s, C.body), -0.16 * s, 0.11 * s, 0), legR = at(box(0.14 * s, 0.22 * s, 0.16 * s, C.body), 0.16 * s, 0.11 * s, 0);
  body.add(legL, legR);
  const head = new THREE.Group(); at(head, 0, 0.2 * s, 0); body.add(head);
  const cube = at(box(0.9 * s, 0.78 * s, 0.7 * s, C.body), 0, 0.39 * s, 0); head.add(cube);
  const screen = at(box(0.7 * s, 0.46 * s, 0.03, C.face, { shadow: false, rough: 0.3 }), 0, 0.42 * s, 0.355 * s); head.add(screen);
  // eye shapes drawn with small emissive boxes so they can switch: normal o o, happy ^ ^, serious | |
  const eyeCol = { emissive: C.accent, ei: 1.2, shadow: false };
  const mk = () => box(0.07 * s, 0.07 * s, 0.03, C.accent, eyeCol);
  const ey = [-1, 1].map(sx => {
    const g = new THREE.Group(); at(g, sx * 0.17 * s, 0.47 * s, 0.375 * s); head.add(g);
    const dot = box(0.12 * s, 0.12 * s, 0.03, C.accent, eyeCol);
    const up1 = mk(), up2 = mk(); up1.scale.set(1.5, 0.6, 1); up2.scale.set(1.5, 0.6, 1);
    at(up1, -0.035 * s, 0, 0); up1.rotation.z = 0.7; at(up2, 0.035 * s, 0, 0); up2.rotation.z = -0.7;
    const bar = box(0.05 * s, 0.17 * s, 0.03, C.accent, eyeCol);
    g.add(dot, up1, up2, bar);
    return { g, dot, happy: [up1, up2], bar };
  });
  const mouth = at(box(0.16 * s, 0.04 * s, 0.03, C.accent, eyeCol), 0, 0.3 * s, 0.375 * s); head.add(mouth);
  const arm = sx => { const p = new THREE.Group(); at(p, sx * 0.5 * s, 0.42 * s, 0); p.add(at(box(0.1 * s, 0.3 * s, 0.12 * s, C.body), 0, -0.13 * s, 0)); head.add(p); return p; };
  const armL = arm(-1), armR = arm(1);
  if (C.antenna) { head.add(at(box(0.04, 0.2 * s, 0.04, 0x9aa4b8), 0, 0.88 * s, 0)); head.add(at(box(0.1 * s, 0.1 * s, 0.1 * s, C.accent, { emissive: C.accent, ei: 1.5 }), 0, 1.0 * s, 0)); }
  return { root, body, head, mouth, eyes: ey, armL, armR, kind: 'buddy', headY: 0.6 * s, height: 1.1 * s, size: s };
}

// ---- performance -------------------------------------------------------------------------------------------
// p: {talk 0..1 (loudness while this character speaks), speaking bool, look: yaw toward the other, mood:'normal'|'happy'|'serious', seed}
const blinkAt = (t, seed) => {   // a blink every 2.5 to 5 s, 0.14 s long
  let x = 0.6 + hash(seed) * 2, i = 0;
  while (x < t + 1 && i < 200) { const d = t - x; if (d >= 0 && d < 0.14) return 1 - Math.abs(d / 0.07 - 1); x += 2.5 + hash(seed * 13 + i++) * 2.5; }
  return 0;
};
export function perform(ch, t, p) {
  const talk = p.talk || 0, sd = p.seed || 1;
  const breathe = Math.sin(t * 2.1 + sd) * 0.012;
  ch.root.rotation.y += ((p.look ?? 0) - ch.root.rotation.y) * 1;     // set directly (deterministic)
  ch.root.rotation.y = p.look ?? 0;
  const bl = blinkAt(t, sd);
  if (ch.kind === 'human') {
    ch.body.position.y = breathe * 0.5;
    ch.body.scale.set(1, 1 + breathe, 1);
    ch.mouth.scale.set(1 - talk * 0.25, 1 + talk * 4.2, 1);
    ch.mouth.position.y = 0.24 - talk * 0.045;
    for (const e of ch.eyes) e.g.scale.y = 1 - 0.9 * bl;
    const lift = p.speaking ? 0.06 + 0.05 * Math.sin(t * 5.3 + sd) * talk : 0;
    for (const b of ch.brows) b.position.y = 0.66 + lift * 0.6;
    ch.head.rotation.x = p.speaking ? -0.03 * talk + 0.02 * Math.sin(t * 3.1 + sd) : 0.01 * Math.sin(t * 0.9 + sd);
    ch.head.rotation.z = 0.025 * Math.sin(t * 1.3 + sd * 2);
    // gestures: arms swing out a little while talking
    const g = p.speaking ? (0.35 + 0.25 * Math.sin(t * 4.1 + sd)) * Math.min(1, talk * 2) : 0;
    ch.armR.rotation.z = 0.08 + g * 0.9; ch.armR.rotation.x = -g * 0.6;
    ch.armL.rotation.z = -0.08 - (p.speaking ? 0.15 * Math.sin(t * 2.7 + sd) * talk : 0); ch.armL.rotation.x = 0;
    if (p.wave) { ch.armR.rotation.z = 2.6; ch.armR.rotation.x = 0.2 * Math.sin(t * 9); }
  } else {
    // bounce and squash with the voice
    const b = p.speaking ? Math.abs(Math.sin(t * 7.5 + sd)) * talk : 0;
    ch.body.position.y = b * 0.12 * ch.size + Math.abs(breathe) * 0.4;
    const sq = 1 - b * 0.08;
    ch.head.scale.set(1 / Math.sqrt(sq), sq, 1 / Math.sqrt(sq));
    ch.mouth.scale.set(1, 1 + talk * 3.5, 1);
    const mood = p.mood || 'normal';
    for (const e of ch.eyes) {
      e.dot.visible = mood === 'normal'; e.happy.forEach(m => m.visible = mood === 'happy'); e.bar.visible = mood === 'serious';
      e.g.scale.y = mood === 'normal' ? 1 - 0.9 * bl : 1;
    }
    const wave = p.speaking ? Math.sin(t * 6 + sd) * 0.5 * talk : 0;
    ch.armL.rotation.z = -0.2 - wave; ch.armR.rotation.z = 0.2 + wave;
    ch.head.rotation.z = 0.04 * Math.sin(t * 1.7 + sd);
  }
}
