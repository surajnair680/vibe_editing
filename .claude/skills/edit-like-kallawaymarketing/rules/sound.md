# Sound rules

Kallaway's editor builds a cue sheet: every on-screen event, its time, its sound. In this repo the sounds come from
Openverse first (`tools/openverse_sfx.py`, CLAUDE.md rule), placed so each sound's measured peak lands on its frame.

| on-screen event | sound | level under voice |
|---|---|---|
| Hook per-word cuts | soft clicks or ticks | -22 dB |
| Card / object pop | short soft pop or "tick" | -20 dB |
| Tracker step change | one clean swish | -18 dB |
| Whip pan / carousel slide | short whoosh (under 0.4 s), vary the file, never the same one twice in a row | -18 dB |
| Line draw | faint pencil or string sweep | -26 dB |
| Number count up | quick tick roll | -24 dB |
| Red circle / highlight | marker squeak or soft hit | -22 dB |
| Theme switch dark to light | airy swoosh | -18 dB |
| Hard cut to FULL beat | nothing, or a low thud on a big word | -16 dB |
| CTA card in | rise into a soft hit | -16 dB |

- Music: a low, steady bed (lo-fi or minimal electronic), ducked 18 to 20 dB under the voice. Optional.
- Voice always on top. If an effect masks a word, drop the effect.
- Write the cue sheet (`work/cues.md`: time, event, sound file, gain) before mixing, and show it with the beat sheet.
