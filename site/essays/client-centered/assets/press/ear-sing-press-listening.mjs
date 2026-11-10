/* One source-bound listening exhibit, projected into the existing paginated book.
   Original public Sing PCM/AAC witnesses are fixed; no private studio media. */
const EXPECTED='sing.synthetic.sustained-la-mi-na.v1';
const APPROVAL='Fountain-Coach-Ear-Sing-2026-10-25';
const IDS=['plain','articulated','expressive'];
const MEDIA='/essays/the-ear-that-learns/media/';
const AUDIO_WITNESSES={
  plain:['f4826365089889eafef579f5e0b3cf6f77d7bf570fcc0fa6e1d5f85ef191cf24','83b45c232a05abea5c3fe5fd25bee71630ce86e66eae78b9817cd60fd9ee8c21'],
  articulated:['1d285c6b0a9dd2f7b7be58aac1509b5f55bcac5e3636c530cbec25f20db8f505','c27fe2ee9bd757b4b1d82aeb3f1ea82f7ff24b1b03741cc77408ebc1638cc807'],
  expressive:['b7390503bdcb4669235fc417e0d21f8008c578f59228ab7ee0817e3df3ff8d27','acf902889e00a37bb832864ff826a612b468fb49900db8de02682cbefd6ab68f']
};
function admit() {
  const element=document.getElementById('ear-sing-press-manifest');
  if(!element||location.origin!=='https://fountain.coach'&&!['localhost','127.0.0.1'].includes(location.hostname))
    throw Error('Listening release origin not admitted');
  const m=JSON.parse(element.textContent);
  if(m.schema!=='satzfunk.essay-listening.v1'||m.release!=='public-original-synthetic-v1'||
     m.publicationGrant!==APPROVAL||m.sourceId!==EXPECTED||m.referenceHumanVoice!==false||
     m.qualifiedSinging!==false||m.earRecognizedLyrics!==false||
     !Array.isArray(m.takes)||m.takes.length!==3) throw Error('Original synthetic source not admitted');
  const takes=new Map();
  for(const t of m.takes){
    if(!IDS.includes(t.id)||takes.has(t.id)||t.sourceId!==EXPECTED||
       t.media!==`media/sing-${t.id}-compare.m4a`||
       t.sha256!==AUDIO_WITNESSES[t.id][0]||t.deliverySHA256!==AUDIO_WITNESSES[t.id][1]||
       t.durationSeconds!==5.2||t.sampleRate!==48000||!Array.isArray(t.comments)||
       t.comments.length<2) throw Error('Unrecognized source-bound audio take');
    takes.set(t.id,t);
  }
  if(takes.size!==3)throw Error('One of three source-bound takes missing');
  return takes;
}
function mount(node,takes){
  if(node.dataset.earMounted==='true')return;
  node.dataset.earMounted='true';
  const audio=node.querySelector('audio');
  const status=node.querySelector('[data-ear-status]');
  const description=node.querySelector('[data-ear-description]');
  const cues=node.querySelector('[data-ear-cues]');
  const current=node.querySelector('[data-ear-current]');
  const note=node.querySelector('[data-ear-note]');
  const fallback=node.querySelector('[data-ear-fallback]');
  let active='articulated',buttons=[];
  function highlight(){
    const t=takes.get(active);
    let index=0;
    t.comments.forEach((c,i)=>{if(c.atSeconds<=(audio.currentTime||0)+.015)index=i});
    buttons.forEach((button,i)=>{
      button.setAttribute('aria-pressed',i===index?'true':'false');
    });
    current.textContent=t.comments[index].text;
  }
  function select(id,at=null){
    const t=takes.get(id);
    if(!t)return;
    active=id;
    audio.pause();
    audio.src=MEDIA+t.media.split('/').pop();
    audio.load();
    node.querySelectorAll('[data-ear-take]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.earTake===id?'true':'false'));
    description.textContent=t.description;
    cues.replaceChildren();buttons=[];
    for(const comment of t.comments){
      const button=document.createElement('button');
      button.type='button';
      button.textContent=comment.atSeconds.toFixed(2)+' s';
      button.setAttribute('aria-label',`Play ${t.label} from ${comment.atSeconds.toFixed(2)} seconds: ${comment.text}`);
      cues.append(button);buttons.push(button);
      button.addEventListener('click',()=>{
        const go=()=>{audio.currentTime=comment.atSeconds;audio.play().catch(()=>{status.textContent='Select Play in the native audio controls.'})};
        if(audio.readyState>0)go();
        else audio.addEventListener('loadedmetadata',go,{once:true});
      });
    }
    if(Number.isFinite(at)&&at>=0&&at<=t.durationSeconds){
      const seek=()=>{if(audio.readyState>0){audio.currentTime=at;highlight()}};
      audio.addEventListener('loadedmetadata',seek,{once:true});
      audio.addEventListener('canplay',seek,{once:true});
      if(audio.readyState>0)seek();
    }
    status.textContent=`${t.label} · Source-bound original Sing AAC · synthetic exercise, not a qualified singing voice.`;
    highlight();
  }
  for(const button of node.querySelectorAll('[data-ear-take]'))
    button.addEventListener('click',()=>select(button.dataset.earTake));
  audio.addEventListener('timeupdate',highlight);
  audio.addEventListener('seeked',highlight);
  node.querySelector('[data-ear-copy]').addEventListener('click',async()=>{
    const t=takes.get(active),at=Math.max(0,Math.min(audio.currentTime||0,t.durationSeconds));
    const addr='https://fountain.coach/estate/read/essay--the-ear-that-learns/?take='+encodeURIComponent(active)+'&t='+at.toFixed(2);
    const text=`The Ear That Learns — ${t.label} / ${at.toFixed(2)} s\nSing source: ${EXPECTED}\nOriginal WAV SHA-256: ${t.sha256}\n`+
      (note.value.trim()?'Comment: '+note.value.trim()+'\n':'')+'Listening address: '+addr;
    try {
      if(!navigator.clipboard?.writeText) throw Error('Copy unavailable');
      await navigator.clipboard.writeText(text);
      fallback.hidden=true;status.textContent='Source-time comment copied; no comment was submitted.';
    }catch {
      fallback.value=text;fallback.hidden=false;fallback.focus();fallback.select();
      status.textContent='Select and copy this source-time comment. No data was submitted.';
    }
  });
  const initial=new URLSearchParams(location.search);
  const wanted=initial.get('take'),at=Number(initial.get('t'));
  select(takes.has(wanted)?wanted:active,initial.has('t')&&Number.isFinite(at)?at:null);
}
let takes;
try{takes=admit()}catch(e){console.error('Ear listening',e)}
if(takes){
  const viewport=document.getElementById('page-viewport');
  const refresh=()=>viewport?.querySelectorAll('[data-ear-listening]').forEach(node=>mount(node,takes));
  document.addEventListener('fountain:linotype-composed',refresh);
  if(viewport) {
    const observer=new MutationObserver(refresh);
    observer.observe(viewport,{childList:true,subtree:true});
  }
  refresh();
}
