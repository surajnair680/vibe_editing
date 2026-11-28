"""Builds the Kallaway-style planning table page for reel-13 (edit-like-kallawaymarketing, step 2).
Each row: time | spoken | layout | scene type | on screen | Kallaway reference frame | current cut frame."""
import base64, io, subprocess, html, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
REF = ROOT.parents[1] / ".claude/skills/edit-like-kallawaymarketing/references/frames"
CUT = ROOT / "out/reel-13-rough-v2.mp4"

ROWS = [
 (0.00, 2.90, "I am going to bulk until I look like an anime villain.", "SPLIT", "2 Word-by-word hook",
  "Two pictures only. The title builds one word at a time: <b>Bulking until I look like</b> / an <i>anime villain</i>. Under it, you (photo or clip) from \"I am going to bulk\" to \"look like\", then a hard cut to Toji on \"anime villain\", with a red glow on \"villain\".",
  "02-word-by-word-hook/09_s003_000.63.jpg", "A photo or clip of you, a Toji photo or clip"),
 (2.90, 4.70, "This is Toji Fushiguro.", "SPLIT", "8 Annotated example",
  "Title <b>This is</b> <i>Toji Fushiguro</i>. Toji card in the centre, slow push in.",
  "08-annotated-example/15_s025_041.88.jpg", "Toji image"),
 (4.70, 9.57, "Wide back, arms like carved stone, and a V-taper so sharp it looks fake.", "SPLIT", "8 Annotated example",
  "Same card. Red tags pop on each phrase with leader lines: <b>Wide back</b>, <b>Arms like stone</b>, <b>V-taper</b>. \"Looks fake\" lands in a red box.",
  "08-annotated-example/15_s011_018.73.jpg", "Toji image (back or full body)"),
 (9.57, 13.00, "But whenever I tell people they can build a body like this,", "FULL", "21 Full A-roll beat",
  "Snap back to you. One-word captions.", "21-full-aroll/01_s008_012.56.jpg", ""),
 (13.00, 19.80, "I hear the same three excuses. I don't have the genetics. I don't have the time. It's not possible naturally.", "SPLIT", "5a Tracker pills + visuals",
  "Title <b>The</b> <i>3 Excuses</i> with the three pills in a compact row under it (blurred until spoken, red tab on the current one). In the middle, one big visual per excuse, hard cut on its line: a glowing DNA strand that turns red and cracks (genetics), a clock with spinning hands (time), a syringe with a big question mark (naturally). Glossy 3D objects on black with red light, made by Codex (approved).",
  "05a-tracker-pills/01_s007_010.60.jpg", "DNA, clock, syringe renders (Codex)"),
 (19.80, 20.80, "So I am going to show you", "SPLIT", "5a Tracker pills",
  "The three visuals shrink into a row in about 0.2 s, then a red slash hits each one about 0.25 s apart, on \"going\", \"show\" and \"you\", with a marker sound each. DNA, clock and syringe crossed out: every excuse is gone.", "18-listicle-carousel/16_s008_007.30.jpg", ""),
 (20.80, 22.43, "what is possible", "FULL", "4 / 21 Serif caption beat",
  "Caption <i>possible.</i> in the serif.", "04-name-reveal/03_s003_003.83.jpg", ""),
 (22.43, 24.97, "This is me after seven years of training.", "SPLIT", "8 Annotated example",
  "Title <i>7 years</i> <b>of training</b>. Your physique photo (face showing) with a slow parallax push.",
  "08-annotated-example/02_s030_038.04.jpg", "Your physique photo with your face"),
 (24.97, 27.67, "Decent, but I'm not a genetic freak.", "FULL", "21 Full A-roll beat",
  "Honest beat on your face.", "21-full-aroll/03_s013_047.38.jpg", ""),
 (27.67, 28.90, "I am twenty-seven.", "SPLIT", "10 Big number",
  "Title <b>Just a</b> <i>normal</i> <b>guy</b>. A big glossy red 3D <b>27</b> (Codex).",
  "10-graph-gauge/16_s017_016.27.jpg", "27 render (Codex)"),
 (28.90, 30.70, "I work full time in tech,", "BROLL", "20 Full-screen B-roll",
  "Your real footage full screen: you at your laptop or desk, typing, on a work call or in the office. One-word captions keep running.",
  "21-full-aroll/01_s008_012.56.jpg", "B-roll: you at work (vertical, 5 to 10 s)"),
 (30.70, 32.50, "and I'm also a fitness coach.", "BROLL", "20 Full-screen B-roll",
  "Your real footage full screen: checking a client's form, writing a plan, replying to check-ins or on a coaching call. Client names and faces hidden.",
  "21-full-aroll/03_s013_047.38.jpg", "B-roll: you coaching (vertical, 5 to 10 s)"),
 (32.50, 36.20, "And I have been a type one diabetic since I was twelve.", "BROLL", "20 Full-screen B-roll",
  "Your real footage full screen: you taking your insulin injection. A small red tag stays on the whole time, <b>Type 1 diabetic since age</b> <i>12</i>, so nobody mixes it up with the syringe crossed out in scene 5. One-word captions keep running.",
  "21-full-aroll/01_s008_012.56.jpg", "B-roll: you taking insulin (vertical, 5 to 10 s; a pen if you use one)"),
 (36.20, 38.50, "If I can build this body, so can you.", "FULL", "4 / 21 Serif caption beat",
  "Caption <i>so can you.</i> in the serif.", "04-name-reveal/14_s003_004.21.jpg", ""),
 (38.50, 40.77, "I'm already two months into this bulk,", "SPLIT", "16 Line path with thumbnails",
  "Title <b>The</b> <i>bulk</i> <b>so far</b>. A line draws from <b>Day 1</b>. Small rounded video cards pop onto it one after another, each playing a second of you training or eating, while the camera slides along to a red dot: <b>Day 60, today</b>.",
  "16-line-path/16_s003_001.37.jpg", "4 to 6 clips from the last 2 months, training and eating (vertical, 2 s+ each)"),
 (40.77, 41.87, "but from today,", "FULL", "21 Full A-roll beat",
  "Turn beat. Added so the graphics never run longer than about 9 s in a row.", "21-full-aroll/01_s008_012.56.jpg", ""),
 (41.87, 43.27, "I'm filming all of it.", "SPLIT", "16 Line path with thumbnails",
  "Back on the same timeline, exactly where scene 15 stopped. The old clips dim (the past). At the red dot a new empty card appears with a blinking red <b>REC</b> badge, and the line starts drawing forward past today as a dashed line.",
  "16-line-path/16_s003_001.37.jpg", ""),
 (43.27, 45.53, "Training, food, supplements", "SPLIT", "18 Listicle carousel",
  "The REC card grows to fill the middle and becomes the carousel: one card per word, the row slides left (training, food, supplements). Active label bright, neighbours blurred.",
  "18-listicle-carousel/03_s028_069.71.jpg", "Training photo or clip, meal photo, your supplements (Codex fills gaps)"),
 (45.53, 47.80, "The wins and the days it goes wrong.", "SPLIT", "10 Graph",
  "No words, just two graphs on dark rounded cards, side by side. On \"the wins\" a green line climbs on the left card; on \"the days it goes wrong\" a red line drops on the right card. Drawn in code, no numbers on the axes.",
  "10-graph-gauge/01_s016_033.56.jpg", ""),
 (47.80, 50.60, "How long will it take? Six months? A year?", "SPLIT", "16 Line path",
  "Back to the same dashed line, further along past today. Tags pop on the words: <i>6 months?</i>, then <i>1 year?</i>", "16-line-path/16_s003_001.37.jpg", ""),
 (50.60, 51.30, "I don't know,", "FULL", "21 Full A-roll beat", "Shrug beat.", "21-full-aroll/03_s013_047.38.jpg", ""),
 (51.30, 53.67, "but I'm not stopping until I look like him", "SPLIT", "9 Side by side",
  "Title <b>Until I look like</b> <i>him</i>. You on the left, Toji on the right. The reel ends here.",
  "09-before-after/09_s008_012.30.jpg", "Your physique photo, Toji image"),
 (53.67, 55.67, "(silent)", "CARD", "22 CTA card",
  "Silent end card, no strip: title <b>Follow me on this</b> / <i>journey</i>, with the key line in the red box. Music carries on under it and lands a soft hit as it appears.",
  "22-cta/01_s044_124.52.jpg", ""),
]

def thumb(img, w=216):
    img = img.convert("RGB"); h = round(img.height * w / img.width)
    b = io.BytesIO(); img.resize((w, h), Image.LANCZOS).save(b, "JPEG", quality=72)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

def frame_at(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(CUT), "-frames:v", "1",
                          "-vf", "scale=216:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    if not raw:  # past the end of the cut (the new end card)
        from PIL import ImageDraw
        im = Image.new("RGB", (216, 384), (8, 8, 8)); ImageDraw.Draw(im).text((62, 185), "not in the cut yet", fill=(150, 150, 150))
        return thumb(im)
    return thumb(Image.open(io.BytesIO(raw)))

def ts(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"

rows_html = []
for i, (a, b, spoken, lay, typ, screen, ref, asset) in enumerate(ROWS, 1):
    rows_html.append(f"""
<article class="row {lay.lower()}">
  <div class="meta"><span class="num">{i:02d}</span><span class="time">{ts(a)} to {ts(b)}</span>
    <span class="dur">{b - a:.1f} s</span><span class="lay">{lay}</span></div>
  <div class="words"><p class="spoken">"{html.escape(spoken)}"</p>
    <p class="type">{html.escape(typ)}</p><p class="screen">{screen}</p>
    {f'<p class="asset">Needs: {html.escape(asset)}</p>' if asset else ''}</div>
  <figure><img src="{thumb(Image.open(REF / ref))}" alt="Kallaway reference for row {i}"><figcaption>Kallaway reference</figcaption></figure>
  <figure><img src="{frame_at((a + b) / 2)}" alt="Your cut at {ts((a + b) / 2)}"><figcaption>Your cut now</figcaption></figure>
</article>""")

split = sum(b - a for a, b, _, l, *_ in ROWS if l == "SPLIT"); full = sum(b - a for a, b, _, l, *_ in ROWS if l != "SPLIT")
tot = split + full
bar = "".join(f'<span class="seg {r[3].lower()}" style="flex:{r[1] - r[0]:.2f}" title="{i}"></span>' for i, r in enumerate(ROWS, 1))

page = f"""<title>Reel-13 Planning Table</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Instrument+Serif:ital@0;1&display=swap">
<style>
/* Layout: one card per script line, Kallaway dark dotted ground, red only for focus */
:root {{
  --bg:#070707; --card:#111111; --line:#262626; --fg:#f2f2f2; --dim:#9a9a9a; --red:#e3262c; --green:#3fbf6a;
  --sans:"Inter",system-ui,sans-serif; --serif:"Instrument Serif",Georgia,serif; color-scheme:dark;
}}
body {{ background:var(--bg); background-image:radial-gradient(rgba(255,255,255,.06) 1px,transparent 1px);
  background-size:14px 14px; color:var(--fg); font-family:var(--sans); margin:0;
  padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); padding-block:28px 60px; }}
.wrap {{ max-width:1100px; margin:0 auto; display:grid; gap:14px; }}
h1 {{ font-weight:800; font-size:clamp(28px,5vw,44px); margin:0; text-wrap:balance; line-height:1.05; }}
h1 i {{ font-family:var(--serif); font-weight:400; }}
.lede {{ color:var(--dim); margin:0; max-width:65ch; line-height:1.5; }}
.stats {{ display:flex; flex-wrap:wrap; gap:8px 18px; color:var(--dim); font-size:13px; font-variant-numeric:tabular-nums; }}
.stats b {{ color:var(--fg); }}
.bar {{ display:flex; height:14px; border-radius:7px; overflow:hidden; gap:2px; }}
.seg.split {{ background:#3a3a3a; }} .seg.full {{ background:var(--red); }} .seg.broll {{ background:var(--green); }} .seg.card {{ background:#f2f2f2; }}
.key {{ display:flex; flex-wrap:wrap; gap:8px 16px; font-size:12px; color:var(--dim); }}
.key span::before {{ content:""; display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:6px; vertical-align:-1px; }}
.key .k1::before {{ background:#3a3a3a; }} .key .k2::before {{ background:var(--red); }} .key .k3::before {{ background:var(--green); }}
.row {{ display:grid; grid-template-columns:150px minmax(0,1fr) 120px 120px; gap:16px; align-items:start;
  background:var(--card); border:1px solid var(--line); border-radius:16px; padding:14px; }}
.row.full {{ border-left:3px solid var(--red); }} .row.broll {{ border-left:3px solid var(--green); }}
.meta {{ display:grid; gap:4px; font-variant-numeric:tabular-nums; font-size:13px; color:var(--dim); }}
.num {{ font-size:22px; font-weight:800; color:var(--fg); }}
.lay {{ justify-self:start; font-size:11px; font-weight:600; letter-spacing:.08em; padding:3px 8px; border-radius:999px; border:1px solid var(--line); color:var(--fg); }}
.full .lay {{ background:var(--red); border-color:var(--red); }} .broll .lay {{ background:var(--green); border-color:var(--green); color:#04140a; }}
.words p {{ margin:0 0 8px; line-height:1.45; }}
.spoken {{ font-family:var(--serif); font-style:italic; font-size:20px; line-height:1.3 !important; }}
.type {{ font-size:11px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--red); }}
.screen {{ font-size:14px; color:#d6d6d6; }}
.screen i {{ font-family:var(--serif); font-size:1.15em; }}
.asset {{ font-size:13px; color:var(--green); }}
figure {{ margin:0; }} figure img {{ width:100%; border-radius:10px; display:block; border:1px solid var(--line); }}
figcaption {{ font-size:11px; color:var(--dim); margin-top:5px; text-align:center; }}
.notes {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:16px 18px; line-height:1.55; }}
.notes h2 {{ margin:0 0 8px; font-size:18px; }} .notes ul {{ margin:0; padding-left:18px; color:#d6d6d6; }}
@media (max-width:720px) {{
  .row {{ grid-template-columns:1fr 1fr; }}
  .meta {{ grid-column:1 / -1; grid-template-columns:auto auto auto auto; align-items:center; justify-content:start; gap:10px; }}
  .words {{ grid-column:1 / -1; }}
}}
</style>
<div class="wrap">
  <h1>Reel-13 <i>planning table</i></h1>
  <p class="lede"><b style="color:var(--green)">Approved 28 Nov 2026.</b> Waiting for footage.</p>
  <p class="lede">Bulking series, episode 0, cut in the Kallaway look. One row per line of the approved rough cut (v2). Each row has the scene type from the skill, a frame from a real Kallaway reel showing that type, and your cut as it looks now at that moment.</p>
  <div class="stats"><span><b>{tot:.1f} s</b> long</span><span><b>{len(ROWS)}</b> scenes</span>
    <span>Graphics (SPLIT) <b>{split / tot:.0%}</b></span><span>Full screen, you or B-roll <b>{full / tot:.0%}</b></span>
    <span>Longest graphic run <b>9.6 s</b></span></div>
  <div class="bar">{bar}</div>
  <div class="key"><span class="k1">SPLIT: graphic on top, you in the strip</span><span class="k2">FULL: you full screen</span><span class="k3">B-ROLL: your footage full screen</span></div>
  {''.join(rows_html)}
  <section class="notes"><h2>Open questions</h2><ul>
    <li>End: a 2 s silent card, Follow me on this <i>journey</i> (decided).</li>
    <li>In FULL beats the caption sits at chest height, near your mic. I'll check it on the stills.</li>
    <li>Sound: a real recorded sound on every pop, pill and slide, plus a low dark music bed from 0:00 kept well under your voice.</li>
  </ul></section>
</div>
"""
out = ROOT / "work/plan/planning.html"
out.write_text(page)
print(out, len(page) // 1024, "KB", f"split {split:.1f} full {full:.1f}")
