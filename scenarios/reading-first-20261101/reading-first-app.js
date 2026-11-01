import { registerSatzfunkMedia } from "/estate/assets/satzfunk-player/satzfunk-media-element.mjs";
registerSatzfunkMedia();
/* A single Fountain Press application surface. Shelves and books are measured source pages,
   not links to a second site shell. All source templates were authored into static HTML. */
(() => {
'use strict';
const viewport=document.getElementById('page-viewport');
const source=document.getElementById('source-flow');
const previous=document.getElementById('previous-page');
const next=document.getElementById('next-page');
const counter=document.getElementById('page-count');
const status=document.getElementById('reader-status');
const section=document.getElementById('reader-section');
const theme=document.getElementById('reader-theme');
const parent=document.getElementById('reader-parent');
const templates=new Map([...document.querySelectorAll('template[data-reader-volume]')].map(t=>[t.dataset.readerVolume,t]));
const securePlayerOrigin=location.protocol==='https:' ||
 (location.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(location.hostname));
const soundEditionPromise=fetch('/estate/essays/the-door-is-a-score/media/edition.json',{cache:'no-store'})
 .then(r=>{if(!r.ok)throw Error('Sound study manifest unavailable');return r.json()})
 .then(m=>{if(m.schema!=='satzfunk.recorded-essay-rehearsal.v1'||m.tracks?.length!==4||
   !/^[a-f0-9]{64}$/.test(m.scoreSHA256)||m.tracks.some(t=>t.sourceSHA256!==m.scoreSHA256))
  throw Error('Invalid authenticated sound study');return m;});
if(!viewport||!source||!window.SolsticeLinotype) return;
const sourceLibrary=source.innerHTML;
const labels=new Map([['library','Bookshelf'],['essays','Essays'],['solstice','Solstice (WT)'],['solstice-reading-01','Reading 01 · First Reading'],['first-readings','First Readings (historical)'],['teatro','Teatro — An Unfinished Composition'],['notes--the-door-is-a-score','References · The Door Is a Score']]);
for(const [key,template] of templates){
 if(key.startsWith('essay--')||key.startsWith('solstice-reading-01--')){
  const label=template.content.querySelector('h2')?.textContent?.trim()||key;
  labels.set(key,label);
  const option=document.createElement('option');option.value=key;option.textContent=key.startsWith('essay--')?'Essays · '+label:'First Reading · '+label;
  section.append(option);
 }
}
const essaySequence=['essays',...[...templates.keys()].filter(x=>x.startsWith('essay--')).reverse()];
const solsticeSequence=['solstice','solstice-reading-01',...[...templates.keys()].filter(x=>x.startsWith('solstice-reading-01--'))];
function adjacentVolume(name,step){
 const sequence=[essaySequence,solsticeSequence].find(s=>s.includes(name));
 return sequence?.[sequence.indexOf(name)+step]||null;
}
let openAtEnd=null;
let engine=null,signature='',frame=0,pointer=null,volume='library',ready=false,entryUrl=null;
const positions=new Map();
const saved=(()=>{try{return localStorage.getItem('fountain-reader-theme')}catch{return null}})();
const systemDark=window.matchMedia?.('(prefers-color-scheme: dark)').matches;
document.documentElement.dataset.theme=saved==='dark'||(saved!=='light'&&systemDark)?'dark':'light';
function appearance(){theme.setAttribute('aria-label',document.documentElement.dataset.theme==='dark'?'Use light appearance':'Use dark appearance');}
appearance();
theme.addEventListener('click',()=>{const value=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=value;try{localStorage.setItem('fountain-reader-theme',value)}catch{}appearance();signature='';schedule();});
function routeFromUrl(){
 const pathname=location.pathname,match=location.hash.match(/^#\/read\/([\w-]+)/);
 if(match&&labels.has(match[1]))return match[1];
 if(pathname.includes('/collections/first-readings/'))return 'first-readings';
 if(pathname.includes('/bookshelf/'))return 'library';
 return document.body.dataset.initialVolume||'library';
}
function addressFromUrl(){
 const raw=new URLSearchParams(location.hash.split('?')[1]||'').get('at');
 if(!raw)return null;
 const at=raw.lastIndexOf('@'),offset=Number(raw.slice(at+1));
 return at>0&&Number.isSafeInteger(offset)&&offset>=0?{block:raw.slice(0,at),offset}:null;
}
function selectSource(name){
 if(name==='library')source.innerHTML=sourceLibrary;
 else {
  const template=templates.get(name);
  if(!template)throw Error('Unrecognized volume: '+name);
  const content=template.content.querySelector('.book-flow');
  if(!content)throw Error('No source-bearing book: '+name);
  source.innerHTML=content.innerHTML;
 }
 source.dataset.minLeaves='1';
 volume=name;
 section.value=volume;
 parent.hidden=['library','essays','solstice'].includes(name);
 if(!parent.hidden){const shelf=name==='notes--the-door-is-a-score'?'essay--the-door-is-a-score':name.startsWith('solstice-reading-01--')?'solstice-reading-01':name==='solstice-reading-01'?'solstice':name==='solstice'||name==='essays'?'library':name==='teatro'?'essays':name==='first-readings'?'library':'essays';parent.dataset.readerTarget=shelf;parent.dataset.readerResume=name==='notes--the-door-is-a-score'?'true':'false';parent.textContent=labels.get(shelf);parent.setAttribute('aria-label','Return to '+labels.get(shelf)+' inside the reader');}
 document.title='Benedikt Eickhoff · '+labels.get(volume);
 viewport.setAttribute('aria-label','Paginated '+labels.get(volume));
}
let positionTimer=0,lastPositionWrite=0,pendingPosition=null;
function flushPosition(){
 clearTimeout(positionTimer);positionTimer=0;
 if(!pendingPosition)return;
 const {v,anchor}=pendingPosition;pendingPosition=null;
 if(v!==volume)return;
 history.replaceState({volume:v},'','/estate/#/read/'+v+'?at='+encodeURIComponent(anchor.block+'@'+anchor.offset));
 lastPositionWrite=performance.now();
}
function remember(page){
 if(!engine)return;
 const anchor=engine.anchorAt(page);
 if(!anchor)return;
 positions.set(volume,anchor);
 pendingPosition={v:volume,anchor};
 clearTimeout(positionTimer);positionTimer=0;
 if(performance.now()-lastPositionWrite>200)flushPosition();
 else positionTimer=setTimeout(flushPosition,230);
}
function syncSatzfunkPlayer(){
 const player=viewport.querySelector('satzfunk-player');
 if(!player||player.dataset.bound)return;
 player.dataset.bound='pending';
 const status=player.closest('.frame-press-av')?.querySelector('.press-av-status');
 if(!securePlayerOrigin){
  player.hidden=true;
  if(status)status.textContent='Playback needs an HTTPS or local secure reader origin. This HTTP staging page displays the authored score only.';
  player.dataset.bound='insecure';
  return;
 }
 soundEditionPromise.then(edition=>{
  if(!player.isConnected||!viewport.contains(player))return;
  const tracks=edition.tracks;
  const choose=(id)=>{
   const track=tracks.find(t=>t.id===id);
   if(!track)throw Error('Unknown source-bound recording');
   const grant={scope:'private-wlan-rehearsal',origin:location.origin,trackID:track.id,
      mediaSHA256:track.mediaSHA256,sourceSHA256:track.sourceSHA256};
   return player.setEdition({origin:location.origin,
      mediaBasePrefix:edition.mediaBasePrefix,tracks,activeTrackID:id,rehearsalGrant:grant});
  };
  player.addEventListener('satzfunkplayer:refused',event=>{
   if(event.detail.reason!=='unreleased')return;
   const id=event.detail.trackID;
   queueMicrotask(()=>{if(player.isConnected&&viewport.contains(player))choose(id);});
  });
  const response=choose(tracks[0].id);
  player.dataset.bound=response.state;
  if(status)status.textContent='';
 }).catch(error=>{
  player.dataset.bound='error';
  if(status)status.textContent='The authored recording could not be admitted for playback.';
  console.error('SatzfunkPlayer source binding',error);
 });
}
function present(target,{write=true,focus=false}={}){
 if(!engine)return;
 const page=engine.display(target),end=Math.min(engine.pages,page+(engine.css.spread?2:1));
 syncSatzfunkPlayer();
 counter.value=(engine.css.spread&&page+1<engine.pages?String(page+1)+'–'+end:String(page+1))+' / '+engine.pages;
 counter.textContent=counter.value;
 previous.disabled=page===0&&!adjacentVolume(volume,-1);
 next.disabled=end>=engine.pages&&!adjacentVolume(volume,1);
 if(write)remember(page);
 status.textContent=(engine.css.spread?'Pages '+(page+1)+' to '+end:'Page '+(page+1))+' of '+engine.pages+'. '+labels.get(volume);
 if(focus){const leaf=engine.leaves[page]?.el;if(leaf){leaf.tabIndex=-1;leaf.focus({preventScroll:true});}}
}
/* A media leaf cannot be measured until its intrinsic image geometry is known.
   Never accept a page and then allow a late-decoded image to change its flow. */
const loadedImages=new Map();
let compositionToken=0;
function loadImage(src){
 if(!loadedImages.has(src)){
  loadedImages.set(src,new Promise((resolve,reject)=>{
   const image=new Image();
   image.onload=()=>{if(image.decode)image.decode().then(resolve,resolve);else resolve();};
   image.onerror=()=>reject(new Error('Unresolvable authored image: '+src));
   image.src=src;
   if(image.complete&&image.naturalWidth)resolve();
  }));
 }
 return loadedImages.get(src);
}
async function compose(){
 const token=++compositionToken,targetVolume=volume;
 const width=viewport.clientWidth,height=viewport.clientHeight;
 if(width<120||height<100)return;
 const style=getComputedStyle(viewport);
 const nextSig=[volume,width,height,style.fontSize,innerWidth,innerHeight,document.documentElement.dataset.theme].join(':');
 if(signature===nextSig&&engine&&viewport.dataset.layout==='ready')return;
 signature=nextSig;
 viewport.dataset.layout='loading';
 try{
  const srcs=[...new Set([...source.querySelectorAll('img[src]')].map(i=>i.src))];
  await Promise.all(srcs.map(loadImage));
  if(token!==compositionToken||targetVolume!==volume)return;
  const focused=viewport.contains(document.activeElement);
  engine?.dispose();engine=null;viewport.replaceChildren();
  const e=new window.SolsticeLinotype(viewport,source,{pageFrame:true,label:'Measured '+labels.get(volume)+' pages',runningTitle:'Benedikt Eickhoff',imprint:'Benedikt Eickhoff'});
  engine=e;
  // Fixed source-owned image dimensions and reserved Press plate geometry
  // are established before composition; never await offscreen lazy clones.
  e.compose();
  let target=0;
  const anchor=positions.get(volume);
  if(openAtEnd===volume){target=e.pages-1;openAtEnd=null;}
  else if(anchor){try{target=e.pageForAnchor(anchor)}catch{positions.delete(volume);}}
  present(target,{write:false,focus:focused});
  // Visible media are part of the printed page: a page is not ready while
  // its placed image is an undecoded placeholder.
  await Promise.all([...viewport.querySelectorAll('img')].map(img=>img.decode()));
  if(token!==compositionToken||targetVolume!==volume)return;
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  if(token!==compositionToken||targetVolume!==volume)return;
  viewport.dataset.layout='ready';
  viewport.dataset.pages=String(e.pages);
  viewport.dataset.mode=e.css.spread?'spread':'single';
  viewport.dataset.volume=volume;
 }catch(error){
  if(token!==compositionToken)return;
  console.error('Fountain Press reader failure',volume,error);
  viewport.dataset.layout='failed';
  status.textContent='The requested book could not be paginated. Its original source remains available.';
  counter.textContent='Unavailable';
 }
}
function schedule(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{void compose();});}
function openVolume(name,{navigate=true,resume=false,fromEnd=false}={}){
 if(fromEnd)openAtEnd=name;
 if(!labels.has(name))return;
 if(engine){const address=engine.anchorAt(engine.current);if(address)positions.set(volume,address);}
 if(navigate){
  clearTimeout(positionTimer);positionTimer=0;pendingPosition=null;
  history.pushState({volume:name},'', '/estate/#/read/'+name);
  if(!resume)positions.delete(name); // selecting a cover opens the edition at its beginning
 } else {
  const address=addressFromUrl();if(address)positions.set(name,address);
 }
 if(name!==volume || !engine){selectSource(name);signature='';schedule();}
 else {signature='';schedule();}
}
function handleHistory(){openVolume(routeFromUrl(),{navigate:false});}
section.addEventListener('change',()=>openVolume(section.value));
document.addEventListener('click',e=>{
 const link=e.target.closest('[data-reader-target]');
 if(!link)return;
 e.preventDefault();
 const key=link.dataset.readerTarget;
 openVolume(key,{resume:link.dataset.readerResume==='true'});
});
previous.addEventListener('click',()=>turn(-1,true));
next.addEventListener('click',()=>turn(1,true));
function turn(dir,focus=false){
 if(!engine||viewport.dataset.layout!=='ready')return;
 const target=dir>0?engine.next():engine.prev();
 if(target!==engine.current){present(target,{write:true,focus});return;}
 const sibling=adjacentVolume(volume,dir);
 if(sibling)openVolume(sibling,{fromEnd:dir<0});
}
viewport.addEventListener('keydown',event=>{
 if(event.target.closest('a,button,input,select,textarea')||event.altKey||event.ctrlKey||event.metaKey)return;
 if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();turn(event.key==='ArrowRight'?1:-1,true);}
});
viewport.addEventListener('pointerdown',event=>{
 if(event.pointerType!=='touch'||!event.isPrimary||event.target.closest('a,button,input,select,textarea'))return;
 pointer={id:event.pointerId,x:event.clientX,y:event.clientY,t:performance.now()};
});
viewport.addEventListener('pointerup',event=>{
 const p=pointer;pointer=null;
 if(!p||p.id!==event.pointerId||performance.now()-p.t>800||!window.getSelection()?.isCollapsed)return;
 const dx=event.clientX-p.x,dy=event.clientY-p.y;
 if(Math.abs(dx)>65&&Math.abs(dy)<Math.abs(dx)*.45)turn(dx<0?1:-1);
});
viewport.addEventListener('pointercancel',()=>pointer=null);
const resize=new ResizeObserver(schedule);resize.observe(viewport);
function height(){const v=window.visualViewport;document.documentElement.style.setProperty('--reader-height',(v?.height||innerHeight)+'px');schedule();}
window.addEventListener('resize',height);
window.visualViewport?.addEventListener('resize',height);
window.addEventListener('popstate',handleHistory);
window.addEventListener('hashchange',handleHistory);
document.fonts?.ready.then(schedule);
const initial=routeFromUrl();
selectSource(initial);
const anchored=addressFromUrl();if(anchored)positions.set(initial,anchored);
height();
})();
