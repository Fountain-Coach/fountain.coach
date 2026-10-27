"""Independent decoded-audio checks for the listening exhibit's actual claims."""
from pathlib import Path
import hashlib,json,subprocess,wave
import numpy as np
BASE=Path(__file__).resolve().parents[2]/'site/essays/the-door-is-a-score/assets'
evidence=json.loads((BASE/'evidence.json').read_text())
late={}
for item in evidence['renders']:
    name=item['id'];source=BASE/(name+'.wav');delivery=BASE/(name+'.mp3')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==item['wavSHA256']
    assert hashlib.sha256(delivery.read_bytes()).hexdigest()==item['mp3SHA256']
    with wave.open(str(source)) as w:
        assert (w.getframerate(),w.getnchannels(),w.getnframes())==(48000,2,672000)
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,2)/32768
    decoded=subprocess.run(['ffmpeg','-v','error','-i',str(delivery),'-f','f32le','-ar','48000','-ac','2','-'],check=True,capture_output=True).stdout
    decoded=np.frombuffer(decoded,dtype='<f4').reshape(-1,2)
    assert decoded.shape==pcm.shape,(name,'delivery duration changed')
    assert np.isfinite(decoded).all() and np.max(abs(pcm))<1
    assert np.sqrt(np.mean(pcm**2))>0.0001,(name,'silent rendering')
    correlation=float(np.corrcoef(pcm.reshape(-1),decoded.reshape(-1))[0,1])
    assert correlation>.96,(name,'delivery does not match master',correlation)
    late[name]=float(np.sqrt(np.mean(pcm[264000:]**2)))
    print('DECODED_AUDIO',name,'14 seconds','correlation',round(correlation,6),'late RMS',late[name])
assert late['withheld']==0,'Withheld closing is not silent after preparation'
assert late['memory']>late['present']*20,'Remembered returns are absent'
assert evidence['semanticModelExecuted'] is False and evidence['midi2Dispatched'] is False
assert evidence['openAIVoiceExecuted'] is False and evidence['nativeTeatroAdmission'] is False
print('DOOR_SOUND_STUDY_ACCEPTED','rendering and delivery only; no automatic semantics or estate release claim')
