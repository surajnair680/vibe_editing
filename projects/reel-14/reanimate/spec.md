# reanimate spec: reel-14 look from refs/ref_klickpin.mp4 (720x1280, 30 fps)

- Target: the look and motion grammar of the reference (word-by-word captions, condensed title letter reveal,
  dark red backgrounds with drifting hairlines, light grey section with red circles, frosted caption boxes).
- Destination: projects/reel-14/work/build2/ (Python, numpy/cv2/PIL, same renderer as v1).
- Fidelity: motion-faithful (copy, colours of real assets, fonts may differ: Bebas Neue + Inter, both OFL).

| element | trigger | start | duration | from -> to | easing | source |
|---|---|---|---|---|---|---|
| caption word | spoken word onset | word start | about 60 % in 0.15 s, full by about 0.8 s (10-90 % about 0.65 s; energy curve rises smoothly with overlap) | opacity 0 -> 1, blur about 4 px -> 0 | ease-out (fast first 0.15 s) | caption energy per frame 16.3-18.7 s, strips work/ref/z/caption.png |
| caption block | sentence | first word | holds until the sentence ends, words stay | left aligned, light grey #E8E2DC sans, 2-3 lines | - | frames 16.4-18.8 |
| title letters | key word | word start | letters in random order over about 0.6 s, each fades about 0.4 s | opacity 0 -> 1 (no movement) | ease-out | strips work/ref/z/title.png (R E D C A R) |
| title | - | - | holds about 1 s or more | off-white #EDE7E1 or red | cut out | frames 4.6-6.2 |
| background | always | - | slow drift | deep red #6b0707 centre to #1c0202 edges, darker vertical bars, hairline circles and lines at low alpha | linear | frames 4.7-20 |
| frosted box | caption over busy picture | - | - | blurred, darkened backdrop, 1 px light border, radius about 16 px | - | frame 6.3 |

Checks: every element on screen at least 0.8 s (user note on v1: words "like a stun grenade").
