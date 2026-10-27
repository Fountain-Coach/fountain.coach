"""Export a self-contained listening edition and a four-direction audio suite."""
from pathlib import Path
import base64,json,mimetypes,re,wave,subprocess
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'site/essays/the-door-is-a-score'
OUT=ROOT.parent/'exports'

def data(path):
    mime={'.mjs':'text/javascript','.js':'text/javascript','.wav':'audio/wav','.mp3':'audio/mpeg','.ogg':'audio/ogg','.json':'application/json'}.get(path.suffix,mimetypes.guess_type(str(path))[0] or 'text/plain')
    return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()

def export():
    OUT.mkdir(exist_ok=True)
    html=(BASE/'index.html').read_text()
    css='\n'.join((ROOT/'site'/x).read_text() for x in ['assets/site.css','assets/estate-core.css'])+'\n'+(BASE/'assets/study.css').read_text()
    html=re.sub(r'<link rel="stylesheet"[^>]*>','',html)
    html=html.replace('</head>','<style>'+css+'</style></head>')
    html=re.sub(r'<script[^>]*src="[^"]*"[^>]*></script>','',html)
    score=(BASE/'assets/score.mjs').read_text().replace('export const ','const ').replace('export function ','function ')
    module=(BASE/'assets/listening.mjs').read_text()
    module=re.sub(r'^import[^\n]*\n','',module,count=1)
    names=['present','beyond','memory','withheld']
    recordings={id:data(BASE/'assets'/(id+'.mp3')) for id in names}
    samples={name:data(BASE/'assets'/name) for name in ['keys.wav','wood-hinge.wav','wood-close.wav']}
    module=module.replace("import('./vendor/csound.js')",'import('+json.dumps(data(BASE/'assets/vendor/csound.js'))+')')
    module=module.replace('new URL(`${id}.mp3`,import.meta.url).href','recordings[id]')
    module=module.replace('new URL(`${id}.wav`,import.meta.url).href','recordings[id]')
    module=module.replace('fetch(new URL(name,import.meta.url))','fetch(samples[name])')
    html=html.replace('Download this direction as WAV','Download this direction as MP3')
    # All local source links and figures become embedded assets; estate reading links remain canonical.
    def local(match):
        attr,rel=match.groups();p=BASE/rel
        if rel=='assets/present.wav':p=BASE/'assets/present.mp3'
        return attr+'="'+data(p)+'"' if p.is_file() else match.group(0)
    html=re.sub(r'(src|href)="(assets/[^"]+)"',local,html)
    html=re.sub(r'src="(/assets/[^"]+)"',lambda m:'src="'+data(ROOT/'site'/m[1].lstrip('/'))+'"' if (ROOT/'site'/m[1].lstrip('/')).is_file() else m[0],html)
    for suffix in ['/essays/','/essays/the-ear-that-learns/','/essays/semantic-compilation-the-archive-is-not-the-edition/','/essays/teatro-an-unfinished-composition/','/']:
        html=html.replace('href="'+suffix+'"','href="https://fountain.coach'+suffix+'"')
    html=html.replace('<body>','<body><p style="padding:.6rem 1rem;margin:0;border-bottom:1px solid #b9afa1;font-size:.9rem">Listening edition · source candidate · estate publication pending.</p>')
    payload='const recordings='+json.dumps(recordings)+';const samples='+json.dumps(samples)+';\n'+score+'\n'+module
    html=html.replace('</body>','<script type="module">'+payload.replace('</script','<\\/script')+'</script></body>')
    (OUT/'The_Door_Is_a_Score_Listening_Edition.html').write_text(html)
    with wave.open(str(OUT/'suite.wav'),'wb') as output:
        output.setnchannels(2);output.setsampwidth(2);output.setframerate(48000)
        for i,id in enumerate(names):
            if i:output.writeframes(bytes(48000*4))
            with wave.open(str(BASE/'assets'/(id+'.wav'))) as source:output.writeframes(source.readframes(source.getnframes()))
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT/'suite.wav'),'-c:a','libmp3lame','-b:a','256k',str(OUT/'The_Door_Is_a_Score_Listening_Suite.mp3')],check=True)
    (OUT/'suite.wav').unlink()
    print('Exported self-contained listening edition and 59-second suite: careful / next room / memory / withheld.')

if __name__=='__main__':export()
