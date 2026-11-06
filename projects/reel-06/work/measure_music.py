import librosa, numpy as np, sys
for fn in sys.argv[1:]:
    y,sr=librosa.load(fn,sr=22050)
    d=len(y)/sr; rms=librosa.feature.rms(y=y,hop_length=512)[0]; t=librosa.times_like(rms,sr=sr,hop_length=512)
    nz=t[rms>rms.max()*0.02]; tempo,beats=librosa.beat.beat_track(y=y,sr=sr); bt=librosa.frames_to_time(beats,sr=sr)
    prof=' '.join(f'{20*np.log10(rms[(t>=a)&(t<a+1)].mean()+1e-9):.0f}' for a in range(int(d)))
    print(f'{fn}: {d:.1f}s sound until {nz.max():.1f}s tempo {float(tempo[0]) if np.ndim(tempo) else tempo:.1f} beats from {bt[:3].round(2)}')
    print('   dB/s:',prof)
