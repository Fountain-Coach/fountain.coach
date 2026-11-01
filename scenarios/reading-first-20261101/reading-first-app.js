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
const sourceLibrary=templates.get('library')?.content.querySelector('.book-flow')?.innerHTML;
if(!sourceLibrary)throw Error('Authored Bookshelf is unavailable');
const labels=new Map([['continuity','On Continuity'],['library','Bookshelf'],['essays','Essays'],['first-readings','First Readings'],['solstice','First Readings'],['solstice-reading-01','First Readings'],['teatro','Teatro — An Unfinished Composition'],['notes--the-door-is-a-score','References · The Door Is a Score']]);
for(const [key,template] of templates){
 if(key.startsWith('essay--')||key.startsWith('solstice-reading-01--')){
  const label=template.content.querySelector('h2')?.textContent?.trim()||key;
  labels.set(key,label);
  const option=document.createElement('option');option.value=key;option.textContent=key.startsWith('essay--')?'Essays · '+label:'First Reading · '+label;
  section.append(option);
 }
}
const essaySequence=[...templates.keys()].filter(x=>x.startsWith('essay--')).reverse();
const solsticeSequence=[...templates.keys()].filter(x=>x.startsWith('solstice-reading-01--'));
if(essaySequence.length!==7||solsticeSequence.length!==32)throw Error('Admitted collection inventory changed');
const contents={essays:essaySequence,'first-readings':solsticeSequence};
const galleryData=JSON.parse(document.getElementById('reader-gallery-data')?.textContent||'null');
if(galleryData?.schema!=='fountain.press.bookshelf-gallery.v1')throw Error('Bookshelf gallery source missing');
const galleries=galleryData.collections;
if(galleries.essays.length!==7||galleries['first-readings'].length!==30 ||
 galleries.essays.some((e,i)=>e.id!==essaySequence[i]) ||
 galleries['first-readings'].some((e,i)=>e.id!==solsticeSequence[i+2]))
 throw Error('Gallery no longer matches admitted source ordering');
function entryVolume(name){
 if(name==='solstice'||name==='solstice-reading-01')return 'first-readings';
 return name;
}
const isContents=name=>name==='essays'||name==='first-readings';
const isSurface=name=>name==='library'||isContents(name);
function owningContents(name){
 if(essaySequence.includes(name)||name==='teatro'||name==='notes--the-door-is-a-score')return 'essays';
 if(solsticeSequence.includes(name))return 'first-readings';
 return null;
}
function adjacentVolume(name,step){
 if(name==='continuity'&&step>0)return 'library';
 const sequence=[essaySequence,solsticeSequence].find(s=>s.includes(name));
 if(!sequence)return null;
 const at=sequence.indexOf(name)+step;
 return sequence[at]|| (at<0?(sequence===essaySequence?'essays':'first-readings'):null);
}
const surfaceOffsets={shelf:0,essays:0,'first-readings':0};
const galleryOffsets={essays:0,'first-readings':0};
const shelfContentsOffsets={essays:0,'first-readings':0};
const collectionOrder=['essays','first-readings'];
let activeCollection='essays';
const selectedWork={essays:null,'first-readings':null};
const compactPresentation={essays:'contents','first-readings':'contents'};
let shelfOriginWork=null;
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
 if(match&&labels.has(match[1]))return entryVolume(match[1]);
 if(pathname.includes('/collections/first-readings/'))return 'first-readings';
 if(pathname.includes('/bookshelf/'))return 'library';
 return entryVolume(document.body.dataset.initialVolume||'continuity');
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
 const parentName=name==='library'?'continuity':isContents(name)?'library':
   name===shelfOriginWork?'library':
   name==='notes--the-door-is-a-score'?'essay--the-door-is-a-score':owningContents(name);
 parent.hidden=!parentName;
 if(parentName){
  parent.dataset.readerTarget=parentName;
  parent.dataset.readerResume='true';
  parent.textContent=labels.get(parentName);
  parent.setAttribute('aria-label','Return to '+labels.get(parentName)+' inside the reader');
 }
 document.title='Benedikt Eickhoff · '+labels.get(volume);
 viewport.setAttribute('aria-label',(isSurface(name)?'Navigable ': 'Paginated ')+labels.get(volume));
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
function recordSurfaceOffset(){
 const area=viewport.querySelector('.reader-scroll-region');
 if(!area)return;
 if(volume==='library'){
  surfaceOffsets.shelf=area.scrollLeft;
  for(const scroller of viewport.querySelectorAll('.reader-gallery-scroll')){
   galleryOffsets[scroller.dataset.collection]=scroller.scrollTop;
  }
  for(const scroller of viewport.querySelectorAll('.reader-collection-scroll')){
   shelfContentsOffsets[scroller.dataset.collection]=scroller.scrollTop;
  }
 }
 else if(isContents(volume))surfaceOffsets[volume]=area.scrollTop;
}
function compactBookshelf(){return window.matchMedia('(max-width:900px)').matches;}
function shelfTrack(){return viewport.querySelector('.reader-bookshelf .reader-scroll-region');}
function updateShelfButtons(){
 if(volume!=='library')return;
 const i=collectionOrder.indexOf(activeCollection);
 previous.disabled=false; // left at the first book returns to the editorial
 next.disabled=i===collectionOrder.length-1;
 previous.setAttribute('aria-label',i===0?'Return to On Continuity':'Previous collection: '+labels.get(collectionOrder[i-1]));
 next.setAttribute('aria-label',next.disabled?'End of Bookshelf':'Next collection: '+labels.get(collectionOrder[i+1]));
 status.textContent='Bookshelf. '+labels.get(activeCollection)+'. '+(i+1)+' of '+collectionOrder.length+' collections.';
 viewport.dataset.collection=activeCollection;
}
function shelfSnapTo(id,{smooth=false}={}){
 if(volume!=='library'||!collectionOrder.includes(id))return;
 const track=shelfTrack();
 const target=track?.querySelector('.reader-collection-page[data-collection="'+id+'"]');
 if(!track||!target)return;
 activeCollection=id;
 const x=target.offsetLeft-track.offsetLeft;
 track.scrollTo({left:x,behavior:smooth?'smooth':'instant'});
 surfaceOffsets.shelf=x;
 updateShelfButtons();
}
function setShelfSelection(collection,id,{showPair=true}={}){
 if(!collectionOrder.includes(collection))return;
 selectedWork[collection]=id;
 const page=viewport.querySelector('.reader-collection-page[data-collection="'+collection+'"]');
 if(!page)return;
 for(const item of page.querySelectorAll('[data-work-id]')){
  const selected=item.dataset.workId===id;
  item.classList.toggle('is-selected',selected);
  if(selected)item.setAttribute('aria-current','true');
  else item.removeAttribute('aria-current');
 }
 if(showPair){
  // Scroll the counterpart *within its own vertical region* only.
  for(const region of page.querySelectorAll('.reader-collection-scroll,.reader-gallery-scroll')){
   const target=[...region.querySelectorAll('[data-work-id]')].find(e=>e.dataset.workId===id);
   if(!target)continue; // introductory prose has no fabricated illustration
   const box=target.getBoundingClientRect(),bounds=region.getBoundingClientRect();
   if(box.top<bounds.top)region.scrollTop+=box.top-bounds.top-6;
   else if(box.bottom>bounds.bottom)region.scrollTop+=box.bottom-bounds.bottom+6;
  }
 }
}
function showCollectionPresentation(id,presentation,{restore=false}={}){
 if(!collectionOrder.includes(id)||!['contents','images'].includes(presentation))return;
 compactPresentation[id]=presentation;
 const page=viewport.querySelector('.reader-collection-page[data-collection="'+id+'"]');
 if(!page)return;
 page.dataset.presentation=presentation;
 const compact=compactBookshelf();
 for(const panel of page.querySelectorAll('.reader-shelf-panel')){
  panel.hidden=compact && panel.dataset.presentation!==presentation;
 }
 for(const button of page.querySelectorAll('.reader-presentation-button')){
  const current=button.dataset.presentation===presentation;
  button.setAttribute('aria-pressed',String(current));
  button.classList.toggle('is-active',current);
 }
 if(!restore){
  const target=page.querySelector('.reader-shelf-panel[data-presentation="'+presentation+'"] .reader-collection-scroll, .reader-shelf-panel[data-presentation="'+presentation+'"] .reader-gallery-scroll');
  target?.focus({preventScroll:true});
 }
}
function renderSurface(){
 engine?.dispose();engine=null;
 viewport.replaceChildren();
 viewport.dataset.layout='loading';
 const outer=document.createElement('section');
 outer.className='reader-scroll-surface '+(volume==='library'?'reader-bookshelf':'reader-contents');
 outer.setAttribute('aria-label',volume==='library'?'Bookshelf':'Contents of '+labels.get(volume));
 const title=document.createElement('h1');
 title.textContent=labels.get(volume);outer.append(title);
 const scroll=document.createElement('div');
 scroll.className='reader-scroll-region';scroll.tabIndex=0;scroll.setAttribute('role','region');
 scroll.setAttribute('aria-label',volume==='library'?'Bookshelf: browse collections horizontally':'Scroll '+labels.get(volume)+' contents vertically');
 if(volume==='library'){
  const savedContents={...shelfContentsOffsets},savedGalleries={...galleryOffsets};
  let restoreComplete=false;
  for(const id of collectionOrder){
   const book=document.createElement('section');
   book.className='reader-collection-page';book.dataset.collection=id;
   book.setAttribute('aria-label',labels.get(id)+' collection: contents and illustrations');
   const header=document.createElement('header');header.className='reader-collection-heading';
   const name=document.createElement('h2');name.textContent=labels.get(id);
   const subtitle=document.createElement('p');
   subtitle.textContent=id==='essays'?'Seven essays · chronological':'Reading 01 · First Reading';
   header.append(name,subtitle);book.append(header);
   const toggle=document.createElement('div');toggle.className='reader-presentation-switch';
   toggle.setAttribute('role','group');toggle.setAttribute('aria-label',labels.get(id)+' presentation');
   for(const presentation of ['contents','images']){
    const b=document.createElement('button');b.type='button';b.className='reader-presentation-button';
    b.dataset.presentation=presentation;b.textContent=presentation==='contents'?'Contents':'Images';
    b.addEventListener('click',()=>showCollectionPresentation(id,presentation));
    toggle.append(b);
   }
   book.append(toggle);
   const pair=document.createElement('div');pair.className='reader-collection-pair';
   const statement=document.createElement('section');statement.className='reader-shelf-panel reader-shelf-statement';
   statement.dataset.presentation='contents';statement.setAttribute('aria-label',labels.get(id)+' complete contents');
   const label=document.createElement('h3');label.textContent='Contents';statement.append(label);
   const list=document.createElement('div');list.className='reader-collection-scroll';
   list.dataset.collection=id;list.tabIndex=0;list.setAttribute('role','region');
   list.setAttribute('aria-label',labels.get(id)+' complete contents, scroll vertically');
   for(const work of contents[id]){
    const entry=document.createElement('button');
    entry.type='button';entry.className='reader-contents-entry reader-shelf-contents-entry';
    entry.dataset.readerTarget=work;entry.dataset.workId=work;
    entry.textContent=labels.get(work);
    entry.setAttribute('aria-label','Read '+labels.get(work)+' in '+labels.get(id));
    list.append(entry);
   }
   statement.append(list);pair.append(statement);
   const gallery=document.createElement('section');gallery.className='reader-shelf-panel reader-shelf-gallery';
   gallery.dataset.presentation='images';gallery.setAttribute('aria-label',labels.get(id)+' illustrated contents');
   const galleryTitle=document.createElement('h3');galleryTitle.textContent='Illustrations';gallery.append(galleryTitle);
   const vertical=document.createElement('div');vertical.className='reader-gallery-scroll';
   vertical.dataset.collection=id;vertical.tabIndex=0;vertical.setAttribute('role','region');
   vertical.setAttribute('aria-label',labels.get(id)+' illustrated gallery, scroll vertically');
   const tiles=document.createElement('div');tiles.className='reader-gallery-grid';
   for(const item of galleries[id]){
    const tile=document.createElement('button');tile.className='reader-gallery-item';
    tile.type='button';tile.dataset.readerTarget=item.id;tile.dataset.workId=item.id;
    tile.setAttribute('aria-label','Read '+labels.get(item.id)+' in '+labels.get(id));
    const square=document.createElement('span');square.className='reader-gallery-square';
    const image=document.createElement('img');image.src=item.src;
    image.alt=item.alt||labels.get(item.id);
    image.loading=id==='essays'?'eager':'lazy';image.decoding='async';
    square.append(image);
    const caption=document.createElement('span');caption.className='reader-gallery-title';
    caption.textContent=labels.get(item.id);tile.append(square,caption);tiles.append(tile);
   }
   vertical.append(tiles);gallery.append(vertical);pair.append(gallery);book.append(pair);scroll.append(book);
   for(const [region,offsets] of [[list,savedContents],[vertical,savedGalleries]]){
    region.scrollTop=offsets[id];
    region.addEventListener('scroll',()=>{
     if(!restoreComplete||!region.isConnected||volume!=='library')return;
     offsets===savedContents?shelfContentsOffsets[id]=region.scrollTop:galleryOffsets[id]=region.scrollTop;
    },{passive:true});
   }
  }
  outer.append(scroll);viewport.append(outer);
  // Same work identity is selected by either projection; focus only selects,
  // activating the button is the separate action opening that work.
  scroll.addEventListener('focusin',event=>{
   const item=event.target.closest('[data-work-id]');
   if(item){
    const book=item.closest('.reader-collection-page');
    setShelfSelection(book.dataset.collection,item.dataset.workId);
   }
  });
  scroll.addEventListener('keydown',event=>{
   const item=event.target.closest('[data-work-id]');
   if(item&&['ArrowUp','ArrowDown'].includes(event.key)){
    event.preventDefault();
    const siblingItems=[...item.closest('.reader-collection-scroll,.reader-gallery-scroll').querySelectorAll('[data-work-id]')];
    const index=siblingItems.indexOf(item);
    const step=event.key==='ArrowDown'?1:-1;
    const nextItem=siblingItems[Math.max(0,Math.min(siblingItems.length-1,index+step))];
    nextItem?.focus({preventScroll:true});
    return;
   }
   if(['ArrowRight','ArrowLeft'].includes(event.key) && !event.target.closest('.reader-collection-scroll,.reader-gallery-scroll')){
    event.preventDefault();moveShelf(event.key==='ArrowRight'?1:-1);
   }
  });
  scroll.addEventListener('wheel',event=>{
   if(event.target.closest('.reader-collection-scroll,.reader-gallery-scroll'))return;
   if(Math.abs(event.deltaY)>Math.abs(event.deltaX)){
    event.preventDefault();scroll.scrollLeft+=event.deltaY;
   }
  },{passive:false});
  let scrollFrame=0;
  scroll.addEventListener('scroll',()=>{
   if(scrollFrame)cancelAnimationFrame(scrollFrame);
   scrollFrame=requestAnimationFrame(()=>{
    const pages=[...scroll.querySelectorAll('.reader-collection-page')];
    if(!pages.length)return;
    const start=scroll.getBoundingClientRect().left;
    const closest=pages.reduce((best,item)=>{
     const distance=Math.abs(item.getBoundingClientRect().left-start);
     return distance<best.distance?{id:item.dataset.collection,distance}:best;
    },{id:activeCollection,distance:Infinity});
    activeCollection=closest.id;updateShelfButtons();
   });
  },{passive:true});
  const finish=()=>{
   if(volume!=='library'||!scroll.isConnected)return;
   for(const id of collectionOrder){
    const page=scroll.querySelector('.reader-collection-page[data-collection="'+id+'"]');
    // Establish the active pane *before* restoring its vertical position.
    // A hidden gallery has zero layout height and rejects a saved scrollTop.
    showCollectionPresentation(id,compactPresentation[id],{restore:true});
    page.querySelector('.reader-collection-scroll').scrollTop=savedContents[id];
    page.querySelector('.reader-gallery-scroll').scrollTop=savedGalleries[id];
    setShelfSelection(id,selectedWork[id],{showPair:false});
   }
   restoreComplete=true;
   shelfSnapTo(activeCollection);
  };
  requestAnimationFrame(()=>requestAnimationFrame(finish));
  updateShelfButtons();
 }else{
  if(volume==='first-readings'){
   const caption=document.createElement('p');caption.className='reader-contents-reading';
   caption.textContent='Reading 01 — First Reading';outer.append(caption);
  }
  for(const id of contents[volume]){
   const button=document.createElement('button');button.type='button';
   button.className='reader-contents-entry';button.dataset.readerTarget=id;
   button.textContent=labels.get(id)||id;scroll.append(button);
  }
  outer.append(scroll);viewport.append(outer);
  const saved=surfaceOffsets[volume];scroll.scrollTop=saved;
  requestAnimationFrame(()=>{if(isContents(volume))scroll.scrollTop=saved});
  scroll.addEventListener('scroll',()=>surfaceOffsets[volume]=scroll.scrollTop,{passive:true});
  previous.disabled=false;next.disabled=true;
 }
 counter.hidden=true;counter.textContent='';
 viewport.dataset.layout='ready';
 viewport.dataset.mode=volume==='library'?'horizontal':'vertical';
 viewport.dataset.volume=volume;viewport.dataset.pages='0';
}
function moveShelf(step){
 if(volume!=='library')return;
 const index=collectionOrder.indexOf(activeCollection),target=index+step;
 if(target<0){openVolume('continuity',{resume:true});return;}
 if(target>=collectionOrder.length)return;
 shelfSnapTo(collectionOrder[target],{smooth:true});
}
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
 if(isSurface(volume)){renderSurface();return;}
 counter.hidden=false;
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
 name=entryVolume(name);
 if(fromEnd)openAtEnd=name;
 if(!labels.has(name))return;
 recordSurfaceOffset();
 if(engine){const address=engine.anchorAt(engine.current);if(address)positions.set(volume,address);}
 if(navigate){
  clearTimeout(positionTimer);positionTimer=0;pendingPosition=null;
  history.pushState({volume:name},'', '/estate/#/read/'+name);
  if(!resume)positions.delete(name); // selecting a cover opens the edition at its beginning
 } else {
  const address=addressFromUrl();if(address)positions.set(name,address);
 }
 viewport.dataset.layout='loading';
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
 const galleryAtActivation=volume==='library'?link.closest('.reader-gallery-scroll'):null;
 const galleryPosition=galleryAtActivation?.scrollTop;
 const galleryCollection=galleryAtActivation?.dataset.collection;
 // A direct contents/gallery selection returns to the same facing Bookshelf,
 // without a newly imposed intermediary collection page.
 shelfOriginWork=volume==='library'&&owningContents(key)?key:null;
 if(shelfOriginWork)setShelfSelection(owningContents(key),key,{showPair:false});
 openVolume(key,{resume:link.dataset.readerResume==='true'});
 // Preserve the last visible gallery coordinate at the activation boundary,
 // before pagination changes the geometry of the old, soon-to-be-detached DOM.
 if(galleryCollection && Number.isFinite(galleryPosition))galleryOffsets[galleryCollection]=galleryPosition;
});
previous.addEventListener('click',()=>turn(-1,true));
next.addEventListener('click',()=>turn(1,true));
function turn(dir,focus=false){
 if(viewport.dataset.layout!=='ready')return;
 if(isSurface(volume)){
  if(volume==='library')moveShelf(dir);
  else if(dir<0)openVolume('library',{resume:true});
  return;
 }
 if(!engine)return;
 const target=dir>0?engine.next():engine.prev();
 if(target!==engine.current){present(target,{write:true,focus});return;}
 const sibling=adjacentVolume(volume,dir);
 if(sibling)openVolume(sibling,{fromEnd:dir<0});
}
viewport.addEventListener('keydown',event=>{
 if(event.target.closest('.reader-scroll-surface,a,button,input,select,textarea')||event.altKey||event.ctrlKey||event.metaKey)return;
 if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();turn(event.key==='ArrowRight'?1:-1,true);}
});
viewport.addEventListener('pointerdown',event=>{
 if(event.pointerType!=='touch'||!event.isPrimary||event.target.closest('.reader-scroll-surface,a,button,input,select,textarea'))return;
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
