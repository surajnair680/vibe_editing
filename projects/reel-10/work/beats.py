"""reel-10 beat sheet: edit times on the song's bar grid (107.66 BPM, drop at 4.45 s edit time).
Each shot: (edit start, edit end, source, source start, what). Source start is chosen so a rep top
lands just after the cut. Hook (0 to 4.45 s) lives in work/hook/hook.py."""
B = 60 / 107.66; BAR = 4 * B; D = 17.45 - 13.0
def t(bars, beats=0): return round(D + bars * BAR + beats * B, 3)
SHOTS = [
    # phrase 1: pull-ups
    (t(0), t(1), "c_part3", 3.33, "close pull-up, full screen (hook breakout), tops at 4.65 / 6.09"),
    (t(1), t(2), "part3",   4.23, "wide doorway pull-ups, 2 reps"),
    (t(2), t(2, 2), "c_part4", 3.87, "close pull-up, one rep to the top"),
    (t(2, 2), t(3), "part4", 5.47, "wide pull-up, one rep"),
    (t(3), t(4), "c_part4", 9.70, "close: last rep, drop off, beard passes the lens"),
    # phrase 2: dips
    (t(4), t(5), "e_part3", 4.07, "backlit silhouette dip, light beam (mood)"),
    (t(5), t(6), "b_part3", 4.27, "front ring dip, low angle, lockout"),
    (t(6), t(6, 2), "e_part4", 5.99, "silhouette dip"),
    (t(6, 2), t(7), "b_part4", 4.87, "front ring dip"),
    (t(7), t(8), "b_part5", 7.20, "lets go of the rings, shakes the arms out"),
    # phrase 3: payoff
    (t(8), t(9), "d_part2", 3.00, "front physique, slow turn (horizontal clip, cropped 9:16)"),
    (t(9), t(10), "part4", 9.60, "walks back up to the camera, front close-up"),
    (t(10), t(11), "e_part5", 3.60, "turns, walks to the lens, eyes closed, exhale"),
    (t(11), t(12), "e_part5", 6.30, "empty rings swinging, music fades"),
]
END = t(12)
