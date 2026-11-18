# reel-11 revisions
- rough v1 (2026-11-18): cut and trim only (user: "just the cut and trim, don't do anything else"). Her clip trimmed
  to 0.43-8.40 + 20.00-24.90; take 2; take 3 middle; ending from take 3d ("since 2020" + follow CTA). 48.1 s.
- rough v2 (2026-11-18): note "while sitting on your ass gaining fat is not cut properly". Cause: me_3b's audio starts
  0.2604 s before its picture (negative pts); a normal decode dropped it, chopping "sitting on"; also 3a's picture was
  cut 0.3 s early and 5 ms fades dipped mid-word. Fix: one continuous seam piece (3a to its real end + 3b), audio from
  the raw AAC stream (me_3b_all.wav), no fades at the seam. Other pieces frame-identical to v1 (framemd5). 48.4 s.
