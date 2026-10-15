/* Content-free Fountain Press reading session, anchored in its containing space.
   Page authority is the deep-link address; gestures animate, never invent pages. */
const pages=[...document.querySelectorAll(".visual-page")];
const frame=document.getElementById("visual-book");
const previous=document.getElementById("visual-previous");
const next=document.getElementById("visual-next");
const progress=document.querySelector(".visual-track");
const fill=document.querySelector(".visual-progress-fill");
const status=document.getElementById("visual-status");
const parent=document.querySelector(".reader-parent-circle");
const members=[...document.querySelectorAll(".reader-member")];
const count=pages.length;
if(!count||count!==Number(document.body.dataset.pageCount)||
   !parent||members.filter(x=>x.classList.contains("is-current")).length!==1)
 throw Error("Reading session has no uniquely selected book or bounded page count");
const reducedMotion=matchMedia("(prefers-reduced-motion: reduce)");
const parseAddress=()=>{
 if(!location.hash)return 1;
 const match=/^#plate-([1-9][0-9]*)$/.exec(location.hash);
 if(!match)return null;
 const number=Number(match[1]);
 return number<=count?number:null;
};
let current=null;
let drag=null;
let settleToken=0;
const restoreMotion=()=>{
 frame.style.transform="";
 frame.style.opacity="";
 frame.dataset.transition="rest";
};
const settle=()=>{
 const token=++settleToken;
 if(reducedMotion.matches){restoreMotion();return;}
 frame.dataset.transition="settling";
 frame.style.transform="translate3d(0,0,0)";
 frame.style.opacity="1";
 setTimeout(()=>{if(token===settleToken&&!drag)restoreMotion()},250);
};
const render=()=>{
 current=parseAddress();
 frame.dataset.invalid=current===null?"true":"false";
 frame.dataset.page=current===null?"invalid":String(current);
 pages.forEach((page,index)=>{page.hidden=index+1!==current;});
 previous.disabled=current===null||current===1;
 next.disabled=current===null||current===count;
 progress.setAttribute("aria-valuenow",String(current??1));
 fill.style.transform="scaleX("+(current?current/count:0)+")";
 status.textContent=current===null?"Unrecognized page address":
  "Blank test leaf "+current+" of "+count;
};
const enterLeaf=(direction)=>{
 if(reducedMotion.matches)return;
 const distance=direction<0?18:-18;
 // The page settles softly after the semantic state has changed.
 frame.animate([{opacity:.62,transform:"translate3d("+distance+"px,0,0)"},
                {opacity:1,transform:"translate3d(0,0,0)"}],
   {duration:300,easing:"cubic-bezier(.2,.7,.3,1)"});
};
const show=(number,direction=1)=>{
 if(drag||current===null||number<1||number>count||number===current)return false;
 restoreMotion();
 history.pushState({blankLeaf:number},"",location.pathname+location.search+"#plate-"+number);
 render();
 enterLeaf(direction);
 return true;
};
previous.addEventListener("click",()=>show(current-1,-1));
next.addEventListener("click",()=>show(current+1,1));
addEventListener("popstate",()=>{restoreMotion();render();});
addEventListener("hashchange",()=>{restoreMotion();render();});
addEventListener("keydown",event=>{
 if(event.defaultPrevented||event.metaKey||event.altKey||event.ctrlKey||
    /^(INPUT|TEXTAREA|SELECT)$/.test(event.target?.tagName||""))return;
 if(event.key==="ArrowRight"){event.preventDefault();show(current+1,1);}
 if(event.key==="ArrowLeft"){event.preventDefault();show(current-1,-1);}
 if(event.key==="Escape"){event.preventDefault();location.assign(parent.href);}
});
const DRAG_THRESHOLD=.34; // Distance relative to the physical displayed leaf.
frame.addEventListener("pointerdown",event=>{
 if(!event.isPrimary||current===null)return;
 drag={id:event.pointerId,x:event.clientX,y:event.clientY,dx:0,active:false,aborted:false};
 frame.dataset.transition="drag";
});
frame.addEventListener("pointermove",event=>{
 if(!drag||drag.id!==event.pointerId||drag.aborted)return;
 const dx=event.clientX-drag.x,dy=event.clientY-drag.y;
 if(!drag.active){
   if(Math.abs(dy)>12&&Math.abs(dy)>Math.abs(dx)*1.25){
     drag.aborted=true;settle();return;
   }
   if(Math.abs(dx)<8)return;
   drag.active=true;
 }
 drag.dx=dx;
 const width=Math.max(1,pages[current-1]?.getBoundingClientRect().width||frame.clientWidth);
 const p=Math.min(1,Math.abs(dx)/width);
 const canTurn=dx<0?current<count:current>1;
 frame.style.transform="translate3d("+(canTurn?dx*.22:dx*.065)+"px,0,0)";
 frame.style.opacity=String(1-(canTurn?.18:.08)*p);
});
const finish=event=>{
 if(!drag||drag.id!==event.pointerId)return;
 const gesture=drag;drag=null;
 const dx=event.clientX-gesture.x;
 const dy=event.clientY-gesture.y;
 const width=Math.max(1,pages[current-1]?.getBoundingClientRect().width||frame.clientWidth);
 const progress=Math.abs(dx)/width;
 const direction=dx<0?1:-1;
 if(gesture.active&&!gesture.aborted&&Math.abs(dx)>Math.abs(dy)*1.3&&
    progress>=DRAG_THRESHOLD&&current+direction>=1&&current+direction<=count){
   restoreMotion();
   show(current+direction,direction);
 }else settle();
};
frame.addEventListener("pointerup",finish);
frame.addEventListener("pointercancel",()=>{
 if(!drag)return;
 drag=null;settle();
});
render();
