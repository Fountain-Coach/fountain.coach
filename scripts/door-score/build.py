"""Compose this one essay with the accepted complete static essay shell."""
from pathlib import Path
from html import escape
import hashlib,json,re,wave
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'site/essays/the-door-is-a-score'
ASSETS=BASE/'assets'
TITLE='The Door Is a Score'
DESCRIPTION='Geräuschemachen, semantic reading, and the passage from an audio file to a performance. Four openly licensed Csound listening studies.'
CANONICAL='https://fountain.coach/essays/the-door-is-a-score/'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    names=['present','beyond','memory','withheld']
    labels=['A careful closing','From the next room','A remembered closing','The door stays open']
    evidence={'kind':'authored-csound-sound-study','engine':'@csound/browser','packageVersion':'7.0.0','engineVersion':7000,'sourceURL':'https://opengameart.org/content/100-cc0-metal-and-wood-sfx','sourceAuthor':'rubberduck','sourceLicense':'CC0-1.0','renderRights':'Fountain Coach authored sound studies; source recordings remain CC0-1.0','sourceArchiveSHA256':sha(ROOT.parent/'wood-metal-source.zip'),'engineBundleSHA256':sha(ASSETS/'vendor/csound.js'),'scoreSHA256':sha(ASSETS/'score.mjs'),'noPerTakeNormalization':True,'semanticModelExecuted':False,'openAIVoiceExecuted':False,'nativeTeatroAdmission':False,'midi2Dispatched':False,'publicRelease':False,'sources':[],'renders':[]}
    for original,local in [('keys_01.ogg','keys'),('wood_squeak_01.ogg','wood-hinge'),('wood_close_01.ogg','wood-close')]:
        evidence['sources'].append({'originalFilename':original,'retainedAsset':local+'.ogg','originalSHA256':sha(ASSETS/(local+'.ogg')),'pcmAsset':local+'.wav','pcmSHA256':sha(ASSETS/(local+'.wav'))})
    fig,axes=plt.subplots(4,1,figsize=(12,6),sharex=True)
    fig.patch.set_facecolor('#f8f5ee')
    for ax,id,label in zip(axes,names,labels):
        with wave.open(str(ASSETS/(id+'.wav'))) as f:
            assert f.getframerate()==48000 and f.getnchannels()==2
            data=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float).reshape(-1,2)/32768
        evidence['renders'].append({'id':id,'wavSHA256':sha(ASSETS/(id+'.wav')),'mp3SHA256':sha(ASSETS/(id+'.mp3')),'sampleRate':48000,'channels':2,'durationSeconds':len(data)/48000,'peak':float(np.abs(data).max()),'rms':float(np.sqrt(np.mean(data**2))),'lateRmsAfter5_5Seconds':float(np.sqrt(np.mean(data[int(5.5*48000):]**2)))})
        envelope=np.max(np.abs(data[:len(data)//480*480].reshape(-1,480,2)),axis=(1,2))
        x=np.arange(len(envelope))*.01
        ax.fill_between(x,-envelope,envelope,color='#6f3024',linewidth=0)
        ax.set_ylim(-.42,.42);ax.set_xlim(0,14);ax.set_yticks([]);ax.set_facecolor('#f8f5ee')
        ax.set_ylabel(label,rotation=0,ha='right',va='center',fontsize=11,labelpad=14,color='#302a25')
        for s in ax.spines.values():s.set_visible(False)
        ax.axhline(0,color='#bdb4a7',linewidth=.45,zorder=0)
        ax.tick_params(axis='x',colors='#51483f',labelsize=9,length=2)
    axes[-1].set_xlabel('Seconds · shared amplitude scale · actual Csound outputs',fontsize=10,color='#51483f')
    fig.subplots_adjust(left=.24,right=.96,top=.96,bottom=.12,hspace=.45)
    fig.savefig(ASSETS/'listening-score.png',dpi=128,facecolor=fig.get_facecolor())
    plt.close(fig)
    (ASSETS/'evidence.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n')
    source=(ROOT/'site/essays/the-ear-that-learns/index.html').read_text()
    prefix=source.split('<article class="essay-article"',1)[0]
    prefix=prefix.replace('The Ear That Learns',TITLE).replace('the-ear-that-learns','the-door-is-a-score')
    prefix=re.sub(r'<meta (?:property|name)="(?:og:image[^\"]*|twitter:image[^\"]*)"[^>]*>','',prefix)
    prefix=re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*(">)',lambda m:m[1]+escape(DESCRIPTION,quote=True)+m[2],prefix)
    prefix=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda _:'<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@type':'Article','headline':TITLE,'description':DESCRIPTION,'mainEntityOfPage':CANONICAL,'dateCreated':'2026-10-27','author':{'@type':'Organization','name':'Fountain Coach'},'publisher':{'@type':'Organization','name':'Fountain Coach'}})+'</script>',prefix,flags=re.S)
    alt='Measured waveforms of four Csound performances, showing the returning closing in memory and its absence in the withheld version.'
    social_alt='Teatro graphic score: orange impacts and returning traces cross black spatial planes; a narrow threshold and a wide open interval hold the action in suspense.'
    image=CANONICAL+'assets/teatro-door-score.png'
    meta=''.join(f'<meta property="{k}" content="{v}">' for k,v in [('og:image',image),('og:image:secure_url',image),('og:image:type','image/png'),('og:image:width','1774'),('og:image:height','887'),('og:image:alt',social_alt)])+f'<meta name="twitter:image" content="{image}"><meta name="twitter:image:alt" content="{social_alt}">'
    prefix=prefix.replace('</head>',meta+'<link rel="stylesheet" href="assets/study.css"></head>')
    body=(ROOT/'scripts/door-score/essay-body.html').read_text()
    # The graph is a source-derived listening aid, not a new illustrative identity.
    body=body.replace('<details><summary>Source recordings',f'<figure><img src="assets/listening-score.png" width="1536" height="768" alt="{alt}"><figcaption>Actual rendered amplitudes on one scale. The graphic cannot decide whether the gesture is convincing.</figcaption></figure><details><summary>Source recordings')
    footer=source[source.index('<footer id="footer"'):source.index('</main>',source.index('<footer id="footer"'))]
    (BASE/'index.html').write_text(prefix+'<article class="essay-article" data-essay-revision="door-score-v1">\n'+body+'\n</article>\n'+footer+'</main>\n<script src="/assets/site.js" defer></script><script type="module" src="assets/listening.mjs"></script></body></html>\n')
    gallery=ROOT/'site/essays/index.html';s=gallery.read_text()
    marker='data-essay-route="/essays/the-door-is-a-score/"'
    if marker not in s:
        card=f'<article class="essay-gallery-card" {marker}><a class="essay-gallery-image" href="/essays/the-door-is-a-score/" aria-label="Read The Door Is a Score"><img src="/essays/the-door-is-a-score/assets/teatro-door-score.png" width="1774" height="887" alt="{social_alt}"></a><div class="essay-gallery-copy"><div class="eyebrow">LISTENING ESSAY · OCTOBER 2026</div><h3><a href="/essays/the-door-is-a-score/">The Door Is a Score</a></h3><p>Geräuschemachen, semantic reading, and four audible Csound directions from one open sound source.</p></div></article>'
        s=s.replace('data-page-size="6">','data-page-size="6">'+card,1);gallery.write_text(s)
    gallery.write_text(gallery.read_text().replace('/essays/the-door-is-a-score/assets/listening-score.png', '/essays/the-door-is-a-score/assets/teatro-door-score.png').replace('width="1536" height="768" alt="'+alt+'"', 'width="1774" height="887" alt="'+social_alt+'"'))
    print('Built essay route, credited audio evidence and one collection entry; existing essays preserved.')

if __name__=='__main__':build()
