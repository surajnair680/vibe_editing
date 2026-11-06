"""Split the original mix into voice (ElevenLabs isolation, aligned) and residual (music + SFX), then measure."""
import soundfile as sf, numpy as np, librosa, json
from scipy.signal import correlate
sr=44100
x,_=sf.read('work/audio/full.wav'); xm=x.mean(1)
v,_=sf.read('work/audio/voice_iso.wav'); v=v if v.ndim==1 else v.mean(1)
a=xm[20*sr:30*sr]; b=v[20*sr-4410:30*sr+4410]
lag=int(np.argmax(correlate(b,a,'valid'))-4410)
v=v[lag:] if lag>0 else np.concatenate([np.zeros(-lag),v])
v=np.pad(v,(0,max(0,len(xm)-len(v))))[:len(xm)]
sf.write('work/audio/voice_aligned.wav',v.astype(np.float32),sr)
# per 2 s block least-squares gain so residual = mix - g*voice
res=np.zeros_like(xm); B=2*sr
for i in range(0,len(xm),B):
    s=slice(i,i+B); vv=v[s]; g=(xm[s]@vv)/(vv@vv+1e-9) if vv@vv>1e-6 else 0
    res[s]=xm[s]-g*vv
sf.write('work/audio/residual.wav',res.astype(np.float32),sr)
def db(s): return 20*np.log10(np.sqrt((s**2).mean())+1e-9)
print('residual level per 2 s:')
print(' '.join(f'{t}:{db(res[t*sr:(t+2)*sr]):.0f}' for t in range(0,64,2)))
for name,(t0,t1) in {'song':(3.5,18.8),'talk':(19.5,63)}.items():
    seg=res[int(t0*sr):int(t1*sr)]
    tempo,beats=librosa.beat.beat_track(y=seg,sr=sr)
    bt=librosa.frames_to_time(beats,sr=sr)+t0
    print(name,'tempo',np.round(tempo,1),'first beats',np.round(bt[:8],2))
    S=np.abs(librosa.stft(seg,n_fft=4096)); f=librosa.fft_frequencies(sr=sr,n_fft=4096)
    tot=S.sum()
    for lo,hi in [(20,150),(150,600),(600,3000),(3000,20000)]:
        print(f'   {lo}-{hi} Hz: {S[(f>=lo)&(f<hi)].sum()/tot*100:.0f}%')
