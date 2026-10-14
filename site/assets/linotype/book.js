/* Solstice Essays: paginated Linotype print-proof reading surface.
   Normal HTML is the source-of-truth fallback without JS.
*/
(() => {
"use strict";
const body=document.body;
const viewport=document.getElementById("book-viewport");
const source=document.getElementById("book-flow");
if(!viewport||!source||!window.SolsticeLinotype)return;
const engine=new window.SolsticeLinotype(viewport,source);
const mobileAtlas=window.FountainMobilePageAtlas?
  new window.FountainMobilePageAtlas(document.getElementById("book-pages"),engine,index=>turn(index)):null;
// Safari must never present the long source DOM while measurement is pending.
// The no-JavaScript original remains untouched and readable.
body.classList.add("linotype-boot");
body.dataset.bookReady="composing";
viewport.setAttribute("aria-busy","true");
const previous=document.getElementById("book-prev");
const next=document.getElementById("book-next");
const pageCount=document.getElementById("book-page-count");
const locationLabel=document.getElementById("book-location");
const progress=document.getElementById("book-progress-fill");
const contents=document.getElementById("book-contents");
const appearance=document.getElementById("book-appearance");
const radios=[...document.querySelectorAll('input[name="book-theme"]')];
const anchors=[...source.querySelectorAll("[id^='book-'],[id^='work-']")].filter(n=>n.classList.contains("book-cover")||n.classList.contains("book-preface")||n.classList.contains("book-chapter")||n.classList.contains("book-end"));
const STORAGE="fountain.essays.linotype.v1."+(document.body.dataset.editionId||"essays");
let fontSize=100,theme="paper",ready=false;
let resizeRaf=0;
let resizeTimer=0;
let acceptedPlace={anchor:"book-cover",offset:0};
let finishTurnMotion=null;
let dragSession=null;
let pendingFontReflow=false;
const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
function store(){
 try{localStorage.setItem(STORAGE,JSON.stringify({fontSize,theme,anchor:engine.currentChapter(),leaf:engine.current,pageWithin:engine.current-(engine.positions.get(engine.currentChapter())||0),span:engine.pages}))}catch{}
}
function restore(){
 try{return JSON.parse(localStorage.getItem(STORAGE)||"{}")}catch{return {}}
}
function titleFor(id){
 if(id==="book-cover")return "Cover";
 if(id==="book-preface")return "The edition";
 if(id==="book-end")return "End of edition";
 const node=document.getElementById(id);
 return node?.querySelector("h2")?.textContent||"Essays";
}
function update(){
 const first=engine.current;
 const second=engine.css.spread&&first>0&&first+1<engine.pages?first+1:null;
 pageCount.textContent=(second===null?String(first+1):String(first+1)+"–"+String(second+1))+" / "+engine.pages;
 locationLabel.textContent=titleFor(engine.currentChapter());
 progress.style.width=((first+1)/engine.pages*100).toFixed(2)+"%";
 previous.disabled=first===0;
 next.disabled=engine.next()<=first;
 document.querySelectorAll("[data-book-toc-target]").forEach(a=>{
   const id=a.dataset.bookTocTarget;
   const match=(id==="cover"?"book-cover":id==="preface"?"book-preface":id==="vergil"?"book-vergil":"work-"+id)===engine.currentChapter();
   if(match)a.setAttribute("aria-current","location");
   else a.removeAttribute("aria-current");
 });
 body.dataset.bookMode=engine.css.spread?"spread":"single";
 body.dataset.bookPageCount=String(engine.pages);
 body.dataset.bookReady="true";
 acceptedPlace={anchor:engine.currentChapter(),
   offset:engine.current-(engine.positions.get(engine.currentChapter())||0)};
 mobileAtlas?.sync();
 store();
}
function turn(to,{animate=false,velocity=0}={}){
 if(!ready)return;
 if(dragSession)cancelDrag();
 const previousIndex=engine.current;
 const direction=Math.sign(to-previousIndex);
 if(direction===0)return;
 const reduced=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
 const motion=animate&&!reduced&&typeof engine.stage.animate==="function";
 // Never keep an obsolete overlay alive during a subsequent turn.
 if(finishTurnMotion){finishTurnMotion();finishTurnMotion=null;}
 const previous=motion?engine.stage.cloneNode(true):null;
 engine.display(to);
 update();
 if(!previous||engine.current===previousIndex)return;
 const v=clamp(Number(velocity)||0,0,3.5);
 // A slow, intentional gesture unfolds; a quick flick resolves briskly.
 const duration=Math.round(clamp(395-v*100,145,395));
 const travel=Math.round(clamp(46+v*24,46,130));
 const sign=direction>0?-1:1;
 const overlay=document.createElement("div");
 overlay.className="linotype-turn-ghost";
 overlay.setAttribute("aria-hidden","true");
 overlay.append(previous);
 viewport.append(overlay);
 const outgoing=overlay.animate([
   {opacity:1,transform:"translate3d(0,0,0) rotateY(0deg)"},
   {opacity:0,transform:"translate3d("+sign*travel+"px,0,0)"}
 ],{duration,easing:"cubic-bezier(.22,.72,.16,1)",fill:"forwards"});
 const incoming=engine.stage.animate([
   {opacity:.48,filter:"brightness(.975)"},
   {opacity:1,filter:"brightness(1)"}
 ],{duration:Math.round(duration*.83),easing:"cubic-bezier(.18,1,.25,1)"});
 body.dataset.turnDuration=String(duration);
 body.dataset.turnVelocity=v.toFixed(3);
 body.dataset.turnMotion="active";
 const cleanup=()=>{
   outgoing.onfinish=null;
   outgoing.cancel();
   incoming.cancel();
   overlay.remove();
   body.dataset.turnMotion="idle";
   if(finishTurnMotion===cleanup)finishTurnMotion=null;
   processFontReflow();
 };
 finishTurnMotion=cleanup;
 outgoing.onfinish=cleanup;
}
function seek(id){
 const index=engine.positions.get(id);
 if(index===undefined)return false;
 turn(index);
 return true;
}
function compose({anchor=null,offset=0}={}){
 gesture=null;
 cancelDrag();
 if(finishTurnMotion){finishTurnMotion();finishTurnMotion=null;}
 const old=engine.currentChapter();
 try{
   body.classList.add("linotype-boot");
   engine.compose(fontSize/100);
   const desired=anchor||old;
   const index=engine.positions.get(desired);
   const target=(index??0)+Math.max(0,offset);
   engine.display(clamp(target,0,engine.pages-1));
   body.classList.add("reader-ready");
   body.classList.remove("linotype-boot");
   ready=true;
   delete body.dataset.bookError;
   viewport.removeAttribute("aria-busy");
   update();
   window.scrollTo(0,0);
 }catch(error){
   console.error("Solstice Linotype pagination fallback:",error);
   body.dataset.bookError=String(error);
   body.classList.remove("reader-ready","linotype-boot");
   body.dataset.bookReady="fallback";
   viewport.removeAttribute("aria-busy");
   // Preserve the entire original manuscript as linear HTML on failure.
   engine.stage.remove();
   ready=false;
 }
}
function open(dialog){
 if(contents.open)contents.close();
 if(appearance.open)appearance.close();
 dialog.showModal();
}
document.getElementById("book-toc-button")?.addEventListener("click",()=>open(contents));
document.getElementById("book-type-button")?.addEventListener("click",()=>open(appearance));
document.querySelectorAll("[data-close-dialog]").forEach(button=>button.addEventListener("click",()=>button.closest("dialog")?.close()));
for(const dialog of [contents,appearance])dialog.addEventListener("click",event=>{if(event.target===dialog)dialog.close()});
document.querySelectorAll("[data-book-toc-target]").forEach(link=>link.addEventListener("click",event=>{
 const target=link.dataset.bookTocTarget;
 const id=target==="cover"?"book-cover":target==="preface"?"book-preface":target==="vergil"?"book-vergil":"work-"+target;
 if(!ready||!engine.positions.has(id))return;
 event.preventDefault();
 contents.close();
 history.replaceState(null,"","#"+id);
 seek(id);
 viewport.focus({preventScroll:true});
}));
previous?.addEventListener("click",()=>turn(engine.prev(),{animate:true,velocity:.55}));
next?.addEventListener("click",()=>turn(engine.next(),{animate:true,velocity:.55}));
document.addEventListener("keydown",event=>{
 if(!ready||contents.open||appearance.open||event.altKey||event.metaKey||event.ctrlKey)return;
 if(["INPUT","TEXTAREA","SELECT"].includes(document.activeElement?.tagName)||
    document.activeElement?.closest("#book-page-atlas"))return;
 if(["ArrowRight","PageDown"," "].includes(event.key)){event.preventDefault();turn(engine.next(),{animate:true,velocity:.7});}
 if(["ArrowLeft","PageUp"].includes(event.key)){event.preventDefault();turn(engine.prev(),{animate:true,velocity:.7});}
 if(event.key==="Home"){event.preventDefault();turn(0);}
 if(event.key==="End"){event.preventDefault();turn(engine.pages-1);}
});
// Paper drag: an inert preview of the target leaf sits beneath a duplicate of
// the current leaf. The edition/reading position does not change before the
// release animation has passed the acceptance threshold.
const prefersReducedMotion=()=>window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const TURN_THRESHOLD=.34;  // minimum 34% of the *physical leaf*, not viewport
const FLICK_VELOCITY=.85; // CSS px per millisecond, with directional intent
const FLICK_MIN_TRAVEL=46;
function pageStage(index){
 const stage=engine.stage.cloneNode(false);
 stage.removeAttribute("id");
 const first=engine.spreadStart(index);
 const slots=engine.css.spread
   ? (first===0?[null,engine.leaves[0]]:[engine.leaves[first],engine.leaves[first+1]||null])
   : [engine.leaves[first]];
 for(let i=0;i<slots.length;i++){
   const item=slots[i];
   if(item){
     const sheet=item.el.cloneNode(true);
     sheet.dataset.verso=i===0&&engine.css.spread?"left":"right";
     stage.append(sheet);
   }else{
     const blank=document.createElement("div");
     blank.className="linotype-blank";
     blank.setAttribute("aria-hidden","true");
     stage.append(blank);
   }
 }
 return stage;
}
function dragTransform(sign,progress){
 // Paper slides on the table. Its translation is proportional to the
 // finger, with no rotating rigid panel or perspective foreshortening.
 // Translation is in sheet-local coordinates (stage scaling happens after).
 const fraction=clamp(progress,0,1);
 const movement=engine.css.width*1.055*fraction;
 return "translate3d("+(sign*movement).toFixed(2)+"px,0,0)";
}
function previewPose(session,progress){
 const p=clamp(progress,0,1);
 session.progress=p;
 session.paper.style.transform=dragTransform(session.sign,p);
 session.outgoing.style.opacity="1";
 session.incoming.style.opacity="1";
 session.incoming.style.transform="none";
 // A narrow, soft shadow suggests a flexible paper edge; it is not
 // a three-dimensional rigid hinge or a translucent text overlay.
 session.fold.style.opacity=String(Math.min(.9,.12+p*.62));
 session.paper.style.setProperty("--paper-roll",Math.min(.95,p*1.4).toFixed(3));
 body.dataset.dragProgress=p.toFixed(3);
}
function cancelDrag({animateBack=false}={}){
 const session=dragSession;
 dragSession=null;
 if(!session)return;
 if(session.animations)session.animations.forEach(a=>a.cancel());
 const dispose=()=>{
   engine.stage.style.visibility="";
   session.root.remove();
   if(body.dataset.turnMotion==="drag"||body.dataset.turnMotion==="rebound")
     body.dataset.turnMotion="idle";
   body.dataset.dragProgress="0";
 };
 if(!animateBack||prefersReducedMotion()){dispose();return;}
 body.dataset.turnMotion="rebound";
 const distance=session.progress;
 // The rejected sheet gently slides home; no spring, acceleration burst,
 // overshoot or change of the manuscript's accepted reading position.
 const duration=Math.round(300+Math.min(140,distance*140));
 const from=session.paper.style.transform;
 const back=session.paper.animate([
   {transform:from},
   {transform:dragTransform(session.sign,0)}
 ],{duration,easing:"cubic-bezier(.4,0,.6,1)",fill:"forwards"});
 const underneath=session.incoming.animate([
   {opacity:session.incoming.style.opacity},
   {opacity:0}
 ],{duration,easing:"ease-out",fill:"forwards"});
 session.animations=[back,underneath];
 // Keep the noninteractive preview until its page settles back in place.
 const cleanup=()=>{
   back.onfinish=null;
   back.cancel();underneath.cancel();dispose();
   if(finishTurnMotion===cleanup)finishTurnMotion=null;
   processFontReflow();
 };
 finishTurnMotion=cleanup;
 back.onfinish=cleanup;
}
function createDrag(direction){
 if(!ready||prefersReducedMotion())return null;
 const to=direction>0?engine.next():engine.prev();
 if(to===engine.current)return null;
 if(finishTurnMotion){finishTurnMotion();finishTurnMotion=null;}
 const root=document.createElement("div");
 root.className="linotype-drag-preview";
 root.setAttribute("aria-hidden","true");
 const next=document.createElement("div");
 next.className="linotype-drag-incoming";
 next.append(pageStage(to));
 const outgoing=document.createElement("div");
 outgoing.className="linotype-drag-outgoing";
 outgoing.append(engine.stage.cloneNode(true));
 const paper=outgoing.querySelector(
   direction>0?".linotype-sheet[data-verso='right']":".linotype-sheet[data-verso='left']"
 )||outgoing.querySelector(".linotype-sheet:last-of-type");
 if(!paper)return null;
 const fold=document.createElement("div");
 fold.className="linotype-drag-fold";
 paper.append(fold);
 root.append(next,outgoing);
 viewport.append(root);
 engine.stage.style.visibility="hidden";
 const session={root,incoming:next,outgoing,paper,fold,to,
   direction,sign:direction>0?-1:1,progress:0,animations:null};
 paper.style.transformOrigin="center center";
 paper.dataset.paperDirection=direction>0?"next":"previous";
 previewPose(session,0);
 body.dataset.turnMotion="drag";
 return session;
}
function acceptDrag(session,velocity){
 dragSession=null;
 if(!session||!ready)return;
 if(prefersReducedMotion()){
   session.root.remove();
   engine.display(session.to);
   engine.stage.style.visibility="";
   update();
   body.dataset.turnMotion="idle";
   processFontReflow();
   return;
 }
 // Crossing the threshold authorizes a turn; it must NOT launch the
 // sheet offscreen. Hold the exact finger-defined position and dissolve
 // its opacity over the already-accepted next page. No velocity-proportional
 // acceleration, no movement beyond the released finger position.
 const duration=460;
 body.dataset.turnDuration=String(duration);
 body.dataset.turnVelocity=clamp(velocity,0,3.5).toFixed(3);
 body.dataset.turnEffect="dissolve";
 body.dataset.turnMotion="finishing";
 const frozenPosition=session.paper.style.transform;
 // Phase 1: the ink recedes while the old sheet remains opaque.
 // Phase 2: the unprinted sheet itself dissolves to the next page.
 // This prevents two competing passages of prose from being readable
 // simultaneously at the midpoint of the turn.
 const inkElements=[...session.paper.children].filter(el=>
   el.matches(".linotype-running,.linotype-area,.linotype-folio"));
 const inkAnimations=inkElements.map(el=>el.animate([
   {opacity:1,offset:0},
   {opacity:1,offset:.09},
   {opacity:0,offset:1}
 ],{duration:240,easing:"cubic-bezier(.42,0,.58,1)",fill:"forwards"}));
 const outgoing=session.paper.animate([
   {transform:frozenPosition,opacity:1,offset:0},
   {transform:frozenPosition,opacity:1,offset:.48},
   {transform:frozenPosition,opacity:0,offset:1}
 ],{duration,easing:"cubic-bezier(.42,0,.58,1)",fill:"forwards"});
 session.animations=[outgoing,...inkAnimations];
 const finalize=()=>{
   outgoing.onfinish=null;
   outgoing.cancel();
   inkAnimations.forEach(a=>a.cancel());
   engine.display(session.to);
   engine.stage.style.visibility="";
   update();
   session.root.remove();
   body.dataset.turnMotion="idle";
   body.dataset.dragProgress="0";
   if(finishTurnMotion===finalize)finishTurnMotion=null;
   processFontReflow();
 };
 finishTurnMotion=finalize;
 outgoing.onfinish=finalize;
}
let gesture=null;
viewport.addEventListener("touchstart",event=>{
 if(!ready||contents.open||appearance.open)return;
 if(event.touches.length!==1){
   gesture=null;
   cancelDrag({animateBack:true});
   return;
 }
 const t=event.touches[0];
 const now=performance.now();
 gesture={identifier:t.identifier,x:t.clientX,y:t.clientY,started:now,
          lastX:t.clientX,lastAt:now,active:false,aborted:false};
 // Register the new finger BEFORE an interrupted animation can finish;
 // its completion must not launch a pending typography reflow mid-gesture.
 if(finishTurnMotion){finishTurnMotion();finishTurnMotion=null;}
},{passive:true});
viewport.addEventListener("touchmove",event=>{
 if(!gesture||gesture.aborted)return;
 if(event.touches.length!==1){
   gesture.aborted=true;
   cancelDrag({animateBack:true});
   return;
 }
 const t=event.touches[0];
 if(t.identifier!==gesture.identifier)return;
 const dx=t.clientX-gesture.x,dy=t.clientY-gesture.y;
 const now=performance.now();
 if(!gesture.active){
   if(Math.abs(dy)>14&&Math.abs(dy)>Math.abs(dx)*1.05){
     gesture.aborted=true;return; // vertical scroll is not a page turn
   }
   if(Math.abs(dx)<12||Math.abs(dx)<=Math.abs(dy)*1.2)return;
   gesture.active=true;
 }
 if(event.cancelable)event.preventDefault();
 const direction=dx<0?1:-1;
 if(dragSession&&dragSession.direction!==direction){
   cancelDrag();
 }
 if(!dragSession)dragSession=createDrag(direction);
 if(dragSession){
   const pageWidth=Math.max(180,engine.css.width*engine.css.scale);
   previewPose(dragSession,Math.abs(dx)/pageWidth);
 }
 if(now-gesture.lastAt>20){gesture.lastX=t.clientX;gesture.lastAt=now;}
},{passive:false});
viewport.addEventListener("touchcancel",()=>{
 gesture=null;
 cancelDrag({animateBack:true});
},{passive:true});
viewport.addEventListener("touchend",event=>{
 if(!gesture||!event.changedTouches.length)return;
 const t=[...event.changedTouches].find(t=>t.identifier===gesture.identifier);
 if(!t)return;
 const record=gesture;gesture=null;
 if(record.aborted){cancelDrag({animateBack:true});return;}
 const dx=t.clientX-record.x,dy=t.clientY-record.y;
 const elapsed=Math.max(24,performance.now()-record.started);
 const moment=Math.max(20,performance.now()-record.lastAt);
 const recent=Math.abs(t.clientX-record.lastX)/moment;
 const velocity=clamp(Math.max(Math.abs(dx)/elapsed,recent),0,3.5);
 if(Math.abs(dx)<12||Math.abs(dx)<Math.abs(dy)*1.25){
   cancelDrag({animateBack:true});return;
 }
 const direction=dx<0?1:-1;
 const to=direction>0?engine.next():engine.prev();
 if(to===engine.current){cancelDrag({animateBack:true});return;}
 const pageWidth=Math.max(180,engine.css.width*engine.css.scale);
 const progress=clamp(Math.abs(dx)/pageWidth,0,1);
 if(dragSession){
   previewPose(dragSession,progress);
   const committed=progress>=TURN_THRESHOLD ||
     (Math.abs(dx)>=FLICK_MIN_TRAVEL && velocity>=FLICK_VELOCITY && elapsed<=350);
   if(committed)acceptDrag(dragSession,velocity);
   else cancelDrag({animateBack:true});
 }else if(progress>=TURN_THRESHOLD ||
          (Math.abs(dx)>=FLICK_MIN_TRAVEL && velocity>=FLICK_VELOCITY)){
   // Some WebKit gestures arrive as a single touchstart/touchend pair.
   // They use the same slow opacity dissolve as a continuously dragged
   // leaf, never the old velocity-accelerated exit animation.
   const paper=createDrag(direction);
   if(paper){
     previewPose(paper,progress);
     acceptDrag(paper,velocity);
   }else{
     // Reduced Motion: preserve the same threshold without animation.
     turn(to,{animate:false,velocity});
   }
 }
},{passive:true});
// A pending font proof may also complete during an ordinary tap or vertical
// scroll with no drag overlay. Flush only after the gesture callback returns.
viewport.addEventListener("touchend",()=>queueMicrotask(processFontReflow),{passive:true});
viewport.addEventListener("touchcancel",()=>queueMicrotask(processFontReflow),{passive:true});
function setFont(n){
 const nextSize=clamp(n,85,145);
 if(nextSize===fontSize)return;
 const anchor=engine.currentChapter();
 const offset=engine.current-(engine.positions.get(anchor)||0);
 fontSize=nextSize;
 document.getElementById("book-font-value").value=fontSize+"%";
 compose({anchor,offset});
}
document.getElementById("book-font-smaller")?.addEventListener("click",()=>setFont(fontSize-10));
document.getElementById("book-font-larger")?.addEventListener("click",()=>setFont(fontSize+10));
for(const input of radios)input.addEventListener("change",()=>{
 if(input.checked){theme=input.value;body.dataset.bookTheme=theme;store();}
});
window.addEventListener("resize",()=>{
 // The viewport dimensions and the orientation media queries must agree before
 // remeasuring paper. A delayed stable check also recovers a transient fallback.
 clearTimeout(resizeTimer);
 resizeTimer=setTimeout(()=>{
 cancelAnimationFrame(resizeRaf);
 resizeRaf=requestAnimationFrame(()=>{
  if(!ready){compose(acceptedPlace);return;}
  const w=viewport.clientWidth,h=viewport.clientHeight;
  const nextMode=window.FountainReadingLayout.mode(w,h);
  const activeMode=engine.css.spread?"spread":"single";
  // Safari expands/collapses browser chrome on scroll and focus. A change
  // in available HEIGHT does not justify rebreaking 30 complete works.
  // Preserve the accepted sheets and adjust their visual scale instead.
  if(nextMode===activeMode && Math.abs(w-engine.css.viewportWidth)<20){
    engine.reframe();
    mobileAtlas?.onResize();
    return;
  }
  const anchor=engine.currentChapter(),offset=engine.current-(engine.positions.get(anchor)||0);
  compose({anchor,offset});
 });
 },140);
},{passive:true});
window.addEventListener("hashchange",()=>{
 const id=decodeURIComponent(location.hash.slice(1));
 if(ready&&engine.positions.has(id))seek(id);
});
const prefs=restore();
fontSize=clamp(Number(prefs.fontSize)||100,85,145);
theme=prefs.theme==="night"?"night":"paper";
body.dataset.bookTheme=theme;
radios.find(r=>r.value===theme).checked=true;
document.getElementById("book-font-value").value=fontSize+"%";
const hash=decodeURIComponent(location.hash.slice(1));
const requested=hash&&document.getElementById(hash)?hash:prefs.anchor||"book-cover";
// The first visible leaf must already have its final font, image and viewport
// geometry. Start on load/font readiness (not requestAnimationFrame: Safari
// throttles that in background tabs). A bounded timer guarantees fallback.
let bookStarted=false;
const startBook=()=>{
 if(bookStarted)return;
 bookStarted=true;
 clearTimeout(startupLimit);
 compose({anchor:requested,offset:hash?0:Number(prefs.pageWithin)||0});
 document.documentElement.classList.remove("book-hydrating");
};
const onResourcesReady=()=>{
 Promise.resolve(document.fonts?.ready).then(startBook,startBook);
};
const startupLimit=setTimeout(startBook,4500);
if(document.readyState==="complete")onResourcesReady();
else window.addEventListener("load",onResourcesReady,{once:true});
// Font readiness is a measurement boundary, not permission to interrupt
// a physical interaction. Public Safari/Chrome may finish font loading in the
// middle of a slow page drag; defer until it has settled before recompiling.
function processFontReflow(){
 if(!pendingFontReflow||!ready||gesture||dragSession||finishTurnMotion)return;
 pendingFontReflow=false;
 const anchor=engine.currentChapter();
 const offset=engine.current-(engine.positions.get(anchor)||0);
 compose({anchor,offset});
}

})();