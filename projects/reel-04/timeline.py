"""reel-04 timeline: the single source of truth for cut timing.

Music: assets/music/m3_moody.mp3, 92.3 BPM, beat = 0.6502 s.
Beat grid phase: beats at 0.61 + n*0.6502; bar downbeats at 2.56, 5.16, 7.76, 10.36, 12.96,
15.56, 18.16, 20.76, 23.36, 25.97, 28.57 (kick builds from ~10.4, full drop by 12.96,
final swell peaks 27.9 to 29.2, the main content ends at 28.57, low tail fades by 32.5).

Each shot: (clip, source_in, edit_end, speed, note). Edit start = previous edit_end.
Edit times are rounded to whole frames (30 fps) when built.
"""
FPS = 30
BEAT = 0.6502
MUSIC = "assets/music/m3_moody.mp3"
MUSIC_OFFSET = 0.0  # music time = edit time + offset

SHOTS = [
    # 1. Already at work (v2 note: open with him sitting and working)
    ("wide", 13.00, 3.86, 1.0, "wide, already sitting and working (v2: no walk-in)"),
    ("x1a", 5.00, 6.46, 1.0, "door frame: working (before the bottle reach)"),
    ("x5a", 7.00, 10.36, 1.0, "behind the chair, working; riser peaks"),
    # 2. Into the flow (bar 10.36 to 18.16, 12 beats)
    ("x4", 1.00, 11.66, 1.0, "hands hit the keys; SUB HIT at 10.36"),
    ("x3", 0.10, 12.31, 1.0, "dashboard graphs; tick"),
    ("x5b", 1.00, 12.96, 1.0, "over the shoulder typing; swish"),
    ("x4", 5.00, 13.61, 1.0, "hands, tighter crop; tick"),
    ("x3", 1.60, 14.26, 1.0, "tooltip pops; click"),
    ("x1a", 11.80, 15.56, 1.0, "drink, door frame"),
    ("x2", 4.70, 16.86, 1.0, "bottle set down"),
    ("x2", 7.80, 18.16, 1.0, "cap twisted on"),
    # 3. The breath (music low-passed)
    ("wide", 9.60, 20.76, 1.0, "wide, deep in work; reverse swell, music muffles"),
    ("x4", 8.00, 23.36, 1.0, "last keystrokes, hands lift off"),
    # 4. The exit
    ("x5b", 7.30, 26.62, 1.0, "stand, lean, walk off; swish"),
    ("x1b", 6.60, 28.57, 1.0, "walk toward the lens, body wipes the frame; riser"),
    ("wide", 20.60, 31.97, 0.5, "empty chair, half speed; low hit, fade to black"),
]


def shots():
    """Yield dicts with frame-accurate edit in/out and source in/duration."""
    start_f = 0
    for clip, src_in, end, speed, note in SHOTS:
        end_f = round(end * FPS)
        n = end_f - start_f
        yield dict(clip=clip, src_in=src_in, speed=speed, note=note,
                   start_f=start_f, frames=n, start=start_f / FPS, end=end_f / FPS,
                   src_dur=n / FPS * speed)
        start_f = end_f


def length():
    return round(SHOTS[-1][2] * FPS) / FPS
