// SatzfunkPlayer: reusable source-bound audio-annotation adapter.
// This is an editorial player projection, not audio recognition or publication.
// Consumer is Fountain Coach's private Ear/Sing essay; source rights stay with Sing.
const HEX=/^[a-f0-9]{64}$/;
const EXPECTED="sing.synthetic.sustained-la-mi-na.v1";
// Frozen original Sing evidence and separately admitted AAC listening derivatives.
const WITNESSES=Object.freeze({
  plain:{pcm:"f4826365089889eafef579f5e0b3cf6f77d7bf570fcc0fa6e1d5f85ef191cf24",
    aac:"83b45c232a05abea5c3fe5fd25bee71630ce86e66eae78b9817cd60fd9ee8c21"},
  articulated:{pcm:"1d285c6b0a9dd2f7b7be58aac1509b5f55bcac5e3636c530cbec25f20db8f505",
    aac:"c27fe2ee9bd757b4b1d82aeb3f1ea82f7ff24b1b03741cc77408ebc1638cc807"},
  expressive:{pcm:"b7390503bdcb4669235fc417e0d21f8008c578f59228ab7ee0817e3df3ff8d27",
    aac:"acf902889e00a37bb832864ff826a612b468fb49900db8de02682cbefd6ab68f"}
});
const TYPES=new Set(["score","ear-measurement","editorial-observation"]);
const isNumber=x=>typeof x==="number"&&Number.isFinite(x);
const privateOrigin=origin=>{
  try {
    const u=new URL(origin);
    return u.protocol==="http:"&&(
      u.hostname==="localhost"||u.hostname==="127.0.0.1"||
      u.hostname==="192.168.8.50"||u.hostname==="benedikt-macmini.local"
    );
  }catch{return false}
};
export function bindEssayListening(manifest,origin){
  if(!privateOrigin(origin))throw new TypeError("Private owner WLAN or localhost required; no public media release");
  if(manifest?.schema!=="satzfunk.essay-listening.v1"||
    manifest.release!=="wlan-research-only"||
    manifest.sourceId!==EXPECTED||
    manifest.referenceHumanVoice===true||
    manifest.qualifiedSinging!==false||
    manifest.earRecognizedLyrics!==false||
    !Array.isArray(manifest.takes)||manifest.takes.length!==3)
      throw new TypeError("Essay source and release authority mismatch");
  const ids=new Set(),audio=new Map();
  for(const t of manifest.takes){
    if(!["plain","articulated","expressive"].includes(t.id)||
      ids.has(t.id)||t.media!==`media/sing-${t.id}-compare.m4a`||
      !HEX.test(t.sha256)||!HEX.test(t.deliverySHA256)||
      t.sha256!==WITNESSES[t.id]?.pcm||t.deliverySHA256!==WITNESSES[t.id]?.aac||
      t.durationSeconds!==5.2||
      !isNumber(t.sampleRate)||t.sampleRate!==48000||
      t.sourceId!==EXPECTED||typeof t.label!=="string"||
      !Array.isArray(t.comments)||t.comments.length<2)
       throw new TypeError("Unadmitted take or missing original media identity");
    ids.add(t.id);
    let prev=-1;
    const comments=t.comments.map(c=>{
      if(!TYPES.has(c.kind)||!isNumber(c.atSeconds)||
        c.atSeconds<0||c.atSeconds>=t.durationSeconds||
        c.atSeconds<=prev||typeof c.text!=="string"||
        !c.text.trim()||c.text.length>360)
          throw new TypeError("Invalid or invented time-addressed editorial comment");
      prev=c.atSeconds;
      return Object.freeze({...c});
    });
    audio.set(t.id,Object.freeze({...t,comments:Object.freeze(comments)}));
  }
  if(ids.size!==3)throw new TypeError("One plain, articulated and expressive witness required");
  return Object.freeze({sourceId:EXPECTED,release:"wlan-research-only",takes:audio});
}
export function listeningCitation(binding,takeId,atSeconds,comment=""){
  const t=binding?.takes?.get(takeId);
  if(!t||!isNumber(atSeconds)||atSeconds<0||atSeconds>t.durationSeconds||
    typeof comment!=="string"||comment.length>2000)
      throw new TypeError("Unbound source-time citation");
  const time=Math.max(0,Math.min(t.durationSeconds,atSeconds)).toFixed(2);
  return `The Ear That Learns — ${t.label} / ${time} s\n`+
    `Sing source: ${binding.sourceId}\nOriginal WAV SHA-256: ${t.sha256}\n`+
    (comment.trim()?`Comment: ${comment.trim()}\n`:"");
}
export function locateListeningComment(binding,takeId,atSeconds){
  const t=binding.takes.get(takeId);
  if(!t)return -1;
  let found=-1;
  for(let i=0;i<t.comments.length;i++)if(t.comments[i].atSeconds<=atSeconds+0.015)found=i;
  return found;
}
export function mountEssayListening(root,loc=globalThis.location){
  const node=root.querySelector("[data-essay-listening]");
  if(!node)return null;
  const status=node.querySelector("[data-listening-status]");
  let binding;
  try {
    const source=root.getElementById("ear-sing-audio-manifest");
    binding=bindEssayListening(JSON.parse(source.textContent),loc.origin);
  }catch(err){
    status.textContent="This audio is a private staging witness only. "+err.message;
    return null;
  }
  const audio=node.querySelector("audio");
  const tabs=node.querySelector("[data-take-buttons]");
  const notes=node.querySelector("[data-audio-comments]");
  const title=node.querySelector("[data-take-title]");
  const explanation=node.querySelector("[data-take-explanation]");
  const input=node.querySelector("[data-reader-note]");
  const fallback=node.querySelector("[data-note-fallback]");
  const copy=node.querySelector("[data-copy-citation]");
  let active="articulated",buttons=[];
  const labelSeconds=time=>time.toFixed(2).replace(/^0/,"0");
  const highlight=()=>{
    const index=locateListeningComment(binding,active,audio.currentTime||0);
    buttons.forEach((el,i)=>{
      el.classList.toggle("is-current",i===index);
      if(i===index)el.setAttribute("aria-current","true");
      else el.removeAttribute("aria-current");
    });
  };
  function select(id,at=null){
    const take=binding.takes.get(id);
    if(!take)return;
    active=id;
    audio.pause();
    audio.src=take.media;
    audio.load();
    title.textContent=take.label;
    explanation.textContent=take.description;
    tabs.querySelectorAll("button").forEach(btn=>{
      const selected=btn.dataset.take===id;
      btn.setAttribute("aria-pressed",selected?"true":"false");
      btn.classList.toggle("is-selected",selected);
    });
    notes.replaceChildren();
    buttons=[];
    for(const c of take.comments){
      const entry=root.createElement("li");
      const seek=root.createElement("button");
      seek.type="button";
      seek.className="listening-cue";
      seek.setAttribute("aria-label",`Play ${take.label} from ${labelSeconds(c.atSeconds)} seconds`);
      const time=root.createElement("time");
      time.textContent=labelSeconds(c.atSeconds)+" s";
      seek.append(time);
      const copyText=root.createElement("span");
      copyText.textContent=c.text;
      entry.dataset.kind=c.kind;
      entry.append(seek,copyText);
      seek.addEventListener("click",()=>{
        const go=()=>{
          audio.currentTime=c.atSeconds;
          // User-activated seek/play; do not autoplay from page load.
          audio.play().catch(()=>{status.textContent="Select Play in the audio controls."});
        };
        if(audio.readyState>=1)go();
        else audio.addEventListener("loadedmetadata",go,{once:true});
      });
      notes.append(entry);buttons.push(seek);
    }
    if(at!==null){
      const move=()=>{audio.currentTime=Math.max(0,Math.min(take.durationSeconds,at));highlight()};
      if(audio.readyState>=1)move();
      else audio.addEventListener("loadedmetadata",move,{once:true});
    }
    status.textContent="Sing AAC audition from pinned original PCM · "+take.label+
      " · synthetic exercise only, no singer/lyric qualification.";
    highlight();
  }
  for(const t of binding.takes.values()){
    const button=root.createElement("button");
    button.type="button";
    button.dataset.take=t.id;
    button.textContent=t.label;
    button.addEventListener("click",()=>select(t.id));
    tabs.append(button);
  }
  audio.addEventListener("timeupdate",highlight);
  audio.addEventListener("seeked",highlight);
  copy.addEventListener("click",async()=>{
    const text=listeningCitation(binding,active,Math.min(audio.currentTime||0,5.2),input.value);
    const params=new URLSearchParams({take:active,t:(audio.currentTime||0).toFixed(2)});
    const uri=loc.origin+loc.pathname+"?"+params.toString()+"#listening-exhibit";
    const content=text+"Listening address: "+uri;
    try{
      if(!navigator.clipboard?.writeText)throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(content);
      fallback.hidden=true;
      status.textContent="Source-time comment copied; nothing submitted to a server.";
    }catch{
      fallback.value=content;fallback.hidden=false;fallback.focus();fallback.select();
      status.textContent="Select and copy the source-time comment below. No data was sent.";
    }
  });
  const params=new URLSearchParams(loc.search);
  const chosen=params.get("take"),number=Number(params.get("t"));
  if(chosen&&binding.takes.has(chosen)&&params.has("t")&&
    isNumber(number)&&number>=0&&number<=5.2) select(chosen,number);
  else select(active);
  return binding;
}
if(typeof document!=="undefined"){
  const start=()=>mountEssayListening(document);
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start,{once:true});
  else start();
}
