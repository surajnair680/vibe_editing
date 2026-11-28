# Animation rules

## The core idea
Something changes on screen every 0.5 to 1 s, and every change lands ON a spoken word (Scribe word start time).
A "long" scene (4 to 15 s) is never static: it is one canvas where items build per word and the camera moves.

## Timing defaults (30 fps)
| move | duration | easing |
|---|---|---|
| Title word in (fade + 12 px rise, or blur 8 px to 0) | 0.25 s | easeOutCubic |
| Card / object pop in (scale 0.9 to 1, opacity 0 to 1) | 0.3 s | easeOutBack (overshoot 1.2) |
| List item / node in | 0.25 s, stagger 0.06 to 0.1 s | easeOutCubic |
| Line draw (stroke dash) | 0.3 to 0.5 s | easeInOutCubic |
| Camera push in on the canvas | 0.4 to 0.6 s | easeInOutCubic |
| Whip pan / jump between items | 0.15 to 0.25 s with motion blur | easeInOutQuart |
| Blur reveal (upcoming item sharpens) | 0.3 s | easeOutCubic |
| Number count up | 0.6 to 1.0 s | easeOutExpo |
| Type-on label | 0.03 s per letter | linear |
| Caption word swap | hard cut on the word start, no fade | |

## Entrances
- Title is on screen at frame 0 of the video (a blank first frame loses the hook).
- Title words build in reading order, each on its spoken word, when the line is spoken over the scene.
- Objects pop with a small overshoot. Lists stagger. Lines draw. Nothing slides in from off-screen in the body
  except carousels.

## Camera moves (inside one HTML page)
- Treat the graphic panel as a big canvas: push in to the active item, pull out for the overview, slide sideways along a
  timeline or carousel. One move per spoken phrase.
- Hero-object trackers (ladder, loop): quick 0.2 s steps between labels with motion blur, then settle.

## Exits and cuts
- Most changes are hard cuts on the word. No crossfades between scenes.
- Inside a scene, old items blur and dim instead of leaving.
- Transition to a FULL beat is always a hard cut.
- Whip blur between two phone screens is allowed (motion blur 20 to 40 px, 0.2 s).

## Emphasis moves
- Highlight a line: colour wash sweeps left to right in 0.3 s.
- Red hand-drawn ellipse draws around one item in 0.4 s.
- Neon highlight box flickers on (2 frames off, then on).
- Screen colour flash: the phone screen tints (green) for 3 to 4 frames on a payoff word.
- Brain colour change red to yellow to green over 0.3 s on the key word.

## What not to do
- No bouncing text, no spinning, no glitch effects, no particle confetti. The look is calm, precise, premium.
- No element moving without a reason in the script.
