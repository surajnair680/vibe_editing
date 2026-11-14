#!/usr/bin/env python3
"""Fallback cue sounds made in code (lemo-opuscar core/audio/sfx.py) when real recorded sounds are not ready yet:
    sh tools/lemo.sh .venv/bin/python <kit>/make_code_sfx.py <abs project>/assets/sfx/code
Writes whoosh.wav, whoosh2.wav, pop.wav, tick.wav, type.wav, chime.wav and prints each one's peak time for reel.json.
Real sounds come first (CLAUDE.md Openverse rule); use these for drafts or where Openverse has nothing usable."""
import os, sys, numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.environ.get('LIB', os.path.expanduser('~/lemo-opuscar')), 'core/audio'))
import sfx
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
def save(name, x):
    x = sfx.norm(np.asarray(x, float), 0.9); pk = int(np.argmax(np.abs(x)))
    sf.write(f'{out}/{name}.wav', x.astype(np.float32), sfx.SR); print(name, round(len(x) / sfx.SR, 3), 's, peak', round(pk / sfx.SR, 3))
save('whoosh', sfx.whoosh(.35)); save('whoosh2', sfx.whoosh(.28)); save('pop', sfx.pop()); save('tick', sfx.click(1.4)); save('chime', sfx.ding())
save('type', np.concatenate([np.concatenate([sfx.click(1.0 + 0.4 * ((i * 7) % 5) / 5, 0.6), np.zeros(int(sfx.SR * 0.055))]) for i in range(8)]))
