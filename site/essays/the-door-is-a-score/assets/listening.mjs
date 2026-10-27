import { directions, sourceFiles, csdFor, duration } from './score.mjs';
const root=document.querySelector('[data-door-study]');
if(root){
 const audio=root.querySelector('audio');
 const sentence=root.querySelector('[data-sentence]'),note=root.querySelector('[data-direction-note]');
 const status=root.querySelector('[data-engine-status]');
 const perform=root.querySelector('[data-perform]'),stop=root.querySelector('[data-stop]'),recall=root.querySelector('[data-recall]');
 let selected='present',engine=null,context=null,epoch=0,timer=null,analysisTimer=null,startedAt=0,starting=false;
 const state={running:false,engineVersion:null,recalls:0,ended:false,maxRms:0,observedWindows:0};
 // Read-only diagnostics for the source-owned acceptance check, not an admission receipt.
 Object.defineProperty(root,'studyState',{get:()=>({...state,selected,contextState:context?.state??'none'})});
 async function end(message='Stopped. The room is quiet.'){
  ++epoch; clearTimeout(timer);clearInterval(analysisTimer);state.running=false;starting=false;recall.disabled=true;stop.disabled=true;perform.disabled=false;
  const old=engine,ctx=context;engine=null;
  if(ctx&&ctx.state!=='closed')await ctx.close().catch(()=>{});
  state.ended=true;status.textContent=message;
  // The closed output context establishes silence. Host cleanup is separate
  // and must not keep the visible transport waiting after the sound stops.
  if(old)void(async()=>{await old.stop().catch(()=>{});await old.cleanup?.().catch(()=>{});await old.destroy?.().catch(()=>{});})();
 }
 function choose(id){
  selected=id;const d=directions[id];
  root.querySelectorAll('[data-direction]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.direction===id)));
  audio.pause();audio.src=new URL(`${id}.mp3`,import.meta.url).href;audio.load();
  root.querySelector('[data-download]').href=new URL(`${id}.wav`,import.meta.url).href;
  sentence.textContent=d.sentence;note.textContent=d.note;
 }
 root.querySelectorAll('[data-direction]').forEach(button=>button.addEventListener('click',async()=>{
  await end('Direction selected. Listen to the recording or perform it live.');choose(button.dataset.direction);
 }));
 audio.addEventListener('play',()=>{if(state.running||starting)void end('Recorded audition playing.');});
 perform.addEventListener('click',async()=>{
  if(starting||state.running)return;
  starting=true;state.ended=false;perform.disabled=true;stop.disabled=false;audio.pause();
  const token=++epoch;
  // AudioContext creation/resume occurs directly in the trusted activation.
  context=new AudioContext({sampleRate:48000});await context.resume();
  const ctx=context;
  status.textContent='Preparing the Csound room…';
  try{
   const {Csound}=await import('./vendor/csound.js');
   if(token!==epoch)return;
   const cs=await Csound({audioContext:ctx,useWorker:false,useSAB:false});
   if(token!==epoch){await cs.destroy?.();return;}
   engine=cs;state.maxRms=0;state.observedWindows=0;
   cs.on('onAudioNodeCreated',node=>{
    const analyser=ctx.createAnalyser();analyser.fftSize=2048;
    const silent=ctx.createGain();silent.gain.value=0;
    node.connect(analyser);analyser.connect(silent);silent.connect(ctx.destination);
    const samples=new Float32Array(analyser.fftSize);
    analysisTimer=setInterval(()=>{
     if(token!==epoch)return;
     analyser.getFloatTimeDomainData(samples);let sum=0;for(const v of samples)sum+=v*v;
     state.maxRms=Math.max(state.maxRms,Math.sqrt(sum/samples.length));state.observedWindows++;
    },20);
   });
   const logs=[];cs.on('message',m=>logs.push(String(m)));
   for(const name of sourceFiles){
    const response=await fetch(new URL(name,import.meta.url));if(!response.ok)throw new Error(`Source unavailable: ${name}`);
    await cs.fs.writeFile(name,new Uint8Array(await response.arrayBuffer()));
   }
   if(token!==epoch)return;
   const compiled=await cs.compileCSD(csdFor(selected,'-odac'));if(compiled!==0)throw new Error(`Csound compilation failed (${compiled})`);
   state.engineVersion=await cs.getVersion();
   await cs.start();if(token!==epoch)return;
   state.running=true;starting=false;state.recalls=0;startedAt=performance.now();
   status.textContent='Live Csound performance. The sound is being made here.';
   const check=()=>{
    if(token!==epoch||!state.running)return;
    const elapsed=(performance.now()-startedAt)/1000;
    recall.disabled=selected==='withheld'||elapsed<4.5||elapsed>10.8||state.recalls>=2;
    if(elapsed>=duration){void end('Performance ended. The room is quiet.');return;}
    timer=setTimeout(check,150);
   };check();
  }catch(error){
   await end('Live engine could not start. The recorded Csound auditions remain available.');
   console.error(error);
  }
 });
 recall.addEventListener('click',async()=>{
  if(!state.running||!engine||recall.disabled)return;
  recall.disabled=true;state.recalls++;
  await engine.inputMessage(`i 1 0 3 3 ${0.25/state.recalls} 0.66 ${state.recalls===1?0.76:0.30} 3200 0.77`);
  status.textContent='The closing returns. This additional gesture is being performed live.';
 });
 stop.addEventListener('click',()=>void end());
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&(state.running||starting))void end();});
 window.addEventListener('pagehide',()=>{++epoch;audio.pause();if(context&&context.state!=='closed')void context.close();});
 choose('present');
}
