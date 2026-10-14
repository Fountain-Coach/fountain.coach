/* Linotype mobile page atlas. The real composed leaves are the sole page source.
   Portrait: the selected leaf is the reading focus, with a short atlas strip.
   Landscape: a draggable page atlas (33%-67%) beside the same single leaf.
   No new pagination, surrogate manuscript, model interpretation or text truncation.
*/
(() => {
"use strict";
class MobilePageAtlas {
  constructor(main, engine, turn) {
    this.main=main;
    this.engine=engine;
    this.turn=turn;
    this.panel=document.getElementById("book-page-atlas");
    this.grid=document.getElementById("book-atlas-grid");
    this.range=document.getElementById("book-atlas-range");
    this.handle=document.getElementById("book-atlas-resize");
    this.prev=document.getElementById("book-atlas-prev");
    this.next=document.getElementById("book-atlas-next");
    this.start=0; this.capacity=0; this.width=45; this.drag=null;
    this.swipe=null; this.suppressSwipeClick=false; this.lastSwipeAt=0;
    this.panel.hidden=false;
    this.handle.addEventListener("pointerdown",e=>this.startResize(e));
    this.handle.addEventListener("pointermove",e=>this.moveResize(e));
    this.handle.addEventListener("pointerup",e=>this.endResize(e));
    this.handle.addEventListener("pointercancel",e=>this.endResize(e));
    this.handle.addEventListener("keydown",e=>{
      if(!["ArrowLeft","ArrowRight","Home","End"].includes(e.key))return;
      e.preventDefault(); e.stopPropagation();
      this.setWidth(e.key==="Home"?33:e.key==="End"?67:this.width+(e.key==="ArrowLeft"?3:-3));
    });
    this.prev.addEventListener("click",()=>this.go(-1));
    this.next.addEventListener("click",()=>this.go(1));
    // The atlas owns horizontal page-set swipes. Vertical gestures stay native,
    // while taps still select the exact source leaf in the main reading pane.
    this.grid.addEventListener("touchstart",e=>this.startSwipe(e),{passive:true});
    this.grid.addEventListener("touchmove",e=>this.moveSwipe(e),{passive:false});
    this.grid.addEventListener("touchend",e=>this.endSwipe(e),{passive:false});
    this.grid.addEventListener("touchcancel",()=>this.cancelSwipe(),{passive:true});
    this.grid.addEventListener("click",e=>{
      if(!this.suppressSwipeClick)return;
      const ghost=performance.now()-this.lastSwipeAt<450 && e.detail!==0;
      this.suppressSwipeClick=false;
      if(ghost){e.preventDefault();e.stopImmediatePropagation();}
    },true);
  }
  get mode(){
    // Phone-sized reading only. A coarse pointer does NOT identify a phone:
    // iPad uses the full measured Linotype page (or facing spread).
    if(matchMedia("(orientation:portrait) and (max-width:650px)").matches)return "portrait";
    if(matchMedia("(orientation:landscape) and (max-height:650px) and (max-width:950px)").matches)return "landscape";
    return null;
  }
  setWidth(value){
    this.width=Math.min(67,Math.max(33,value));
    this.main.style.setProperty("--book-atlas-width",this.width.toFixed(2)+"%");
    this.handle.setAttribute("aria-valuenow",String(Math.round(this.width)));
    this.handle.setAttribute("aria-valuetext",Math.round(this.width)+" percent of the viewport for page navigation");
    // Original measured sheets remain unchanged. Only their visual scale moves.
    if(this.engine.pages&&this.mode==="landscape")this.engine.reframe();
    this.paint({preserveStart:true});
  }
  startResize(e){
    if(this.mode!=="landscape"||e.button!==0)return;
    e.preventDefault();e.stopPropagation();
    this.drag={x:e.clientX,width:this.width,full:Math.max(1,this.main.clientWidth)};
    this.handle.setPointerCapture(e.pointerId);
    this.main.dataset.atlasDragging="true";
  }
  moveResize(e){
    if(!this.drag)return;
    e.preventDefault();e.stopPropagation();
    this.setWidth(this.drag.width+100*(this.drag.x-e.clientX)/this.drag.full);
  }
  endResize(e){
    if(!this.drag)return;
    e.stopPropagation();
    this.drag=null;
    delete this.main.dataset.atlasDragging;
    if(this.handle.hasPointerCapture(e.pointerId))this.handle.releasePointerCapture(e.pointerId);
    this.paint({preserveStart:true});
  }
  go(direction){
    if(!this.capacity)return false;
    const to=Math.max(0,Math.min(Math.max(0,this.engine.pages-this.capacity),this.start+this.capacity*direction));
    if(to===this.start)return false;
    this.start=to;
    this.paint({preserveStart:true});
    return true;
  }
  startSwipe(e){
    this.suppressSwipeClick=false;
    this.cancelSwipe();
    if(!this.mode||e.touches.length!==1)return;
    const finger=e.touches[0];
    this.swipe={identifier:finger.identifier,x:finger.clientX,y:finger.clientY,
      time:performance.now(),dx:0,claimed:false,aborted:false};
  }
  moveSwipe(e){
    const s=this.swipe;
    if(!s||s.aborted||e.touches.length!==1){this.cancelSwipe();return;}
    const finger=[...e.touches].find(t=>t.identifier===s.identifier);
    if(!finger){this.cancelSwipe();return;}
    const dx=finger.clientX-s.x,dy=finger.clientY-s.y;
    if(!s.claimed){
      if(Math.abs(dy)>12&&Math.abs(dy)>Math.abs(dx)*1.1){
        s.aborted=true;return;
      }
      if(Math.abs(dx)<10||Math.abs(dx)<=Math.abs(dy)*1.2)return;
      s.claimed=true;
      this.grid.classList.add("is-swiping");
      this.grid.classList.remove("is-settling");
    }
    if(e.cancelable)e.preventDefault();
    s.dx=dx;
    const travel=Math.sign(dx)*Math.min(Math.abs(dx)*.38,Math.min(115,this.grid.clientWidth*.3));
    this.grid.style.transform="translate3d("+travel.toFixed(1)+"px,0,0)";
  }
  endSwipe(e){
    const s=this.swipe;
    this.swipe=null;
    if(!s||s.aborted||!e.changedTouches.length){this.resetSwipeMotion();return;}
    const finger=[...e.changedTouches].find(t=>t.identifier===s.identifier);
    if(!finger){this.resetSwipeMotion();return;}
    const dx=finger.clientX-s.x,dy=finger.clientY-s.y;
    if(!s.claimed&&Math.abs(dx)<24){this.resetSwipeMotion();return;}
    if(Math.abs(dx)<Math.abs(dy)*1.2){this.resetSwipeMotion();return;}
    const elapsed=Math.max(16,performance.now()-s.time);
    const threshold=Math.min(78,Math.max(38,this.grid.clientWidth*.15));
    const accepted=Math.abs(dx)>=threshold||
      (Math.abs(dx)>=27&&Math.abs(dx)/elapsed>=.55);
    // A swipe is not a tap, including at the first/last screenful.
    if(s.claimed||accepted){
      if(e.cancelable)e.preventDefault();
      this.suppressSwipeClick=true;
      this.lastSwipeAt=performance.now();
    }
    this.resetSwipeMotion();
    if(accepted&&this.go(dx<0?1:-1)){
      if(!matchMedia("(prefers-reduced-motion: reduce)").matches){
        this.grid.classList.add("is-new-page");
        this.grid.addEventListener("animationend",()=>this.grid.classList.remove("is-new-page"),{once:true});
      }
    }
  }
  resetSwipeMotion(){
    this.grid.classList.remove("is-swiping");
    this.grid.classList.add("is-settling");
    this.grid.style.transform="";
  }
  cancelSwipe(){
    this.swipe=null;
    this.resetSwipeMotion();
  }
  pageTitle(leaf){
    if(!leaf)return "First Reading";
    if(leaf.sourceId==="book-cover")return "First Reading";
    if(leaf.sourceId==="book-vergil")return "Vergil";
    if(leaf.sourceId==="book-preface")return "The edition";
    if(leaf.sourceId==="book-end")return "End of edition";
    return this.engine.leaves.find(item=>item.sourceId===leaf.sourceId&&item.type==="opener")
      ?.el.querySelector("h2")?.textContent?.trim()
      || this.engine.source.querySelector("#"+CSS.escape(leaf.sourceId)+" h2")?.textContent?.trim()
      || leaf.label || "First Reading";
  }
  paint({preserveStart=false}={}){
    const mode=this.mode;
    // The atlas must never leak into the full iPad compositor while a
    // browser updates its viewport/orientation media queries.
    document.body.dataset.deviceNavigation=mode?"phone":"book";
    this.panel.hidden=!mode;
    this.panel.dataset.atlasMode=mode||"";
    if(!mode||!this.engine.pages){
      this.grid.replaceChildren();
      this.grid.style.transform="";
      return;
    }
    const w=this.panel.clientWidth,h=this.panel.clientHeight;
    if(w<50||h<70)return;
    // Screenfuls, not a scrolling catalogue. Each atlas leaf is a real page.
    const cols=mode==="portrait"
      ? Math.max(2,Math.min(4,Math.floor((w-44)/91)))
      : Math.max(1,Math.min(5,Math.floor((w-32)/110)));
    const rows=mode==="portrait"?1:Math.max(1,Math.min(3,Math.floor((h-47)/140)));
    const capacity=cols*rows;
    const current=this.engine.current;
    if(!preserveStart||this.capacity!==capacity)
      this.start=Math.floor(current/capacity)*capacity;
    else this.start=Math.max(0,Math.min(this.start,Math.max(0,this.engine.pages-capacity)));
    this.capacity=capacity;
    this.grid.style.setProperty("--atlas-columns",String(cols));
    this.grid.style.setProperty("--atlas-rows",String(rows));
    const gap=10,head=40;
    const cellW=(w-32-(cols-1)*gap)/cols;
    const cellH=(h-head-(rows-1)*gap)/rows;
    const paperW=Math.max(25,Math.min(cellW-5,(cellH-20)*Math.SQRT1_2));
    const paperH=paperW/Math.SQRT1_2;
    const scale=paperW/this.engine.css.width;
    const end=Math.min(this.engine.pages,this.start+capacity);
    const fragment=document.createDocumentFragment();
    for(let i=this.start;i<end;i++){
      const leaf=this.engine.leaves[i];
      const button=document.createElement("button");
      button.type="button";button.className="book-atlas-page";
      const title=this.pageTitle(leaf);
      button.setAttribute("aria-label","Read page "+(i+1)+" of "+this.engine.pages+", "+title);
      button.dataset.page=String(i);
      if(i===current){button.classList.add("is-selected");button.setAttribute("aria-current","page");}
      const paper=document.createElement("span");
      paper.className="book-atlas-paper";
      paper.style.width=paperW+"px";paper.style.height=paperH+"px";
      const miniature=leaf.el.cloneNode(true);
      miniature.classList.add("book-atlas-miniature");
      miniature.setAttribute("aria-hidden","true");
      miniature.querySelectorAll("[id]").forEach(el=>el.removeAttribute("id"));
      miniature.querySelectorAll("a").forEach(a=>a.removeAttribute("href"));
      miniature.style.width=this.engine.css.width+"px";
      miniature.style.height=this.engine.css.height+"px";
      miniature.style.transform="scale("+scale+")";
      paper.append(miniature);
      const heading=document.createElement("span");
      heading.className="book-atlas-title";
      heading.textContent=title;
      paper.append(heading);
      const folio=document.createElement("span");
      folio.className="book-atlas-folio";folio.textContent=String(i+1).padStart(3,"0");
      button.append(paper,folio);
      button.addEventListener("click",()=>this.turn(i));
      fragment.append(button);
    }
    this.grid.replaceChildren(fragment);
    this.range.textContent=(this.start+1)+"–"+end+" / "+this.engine.pages;
    this.prev.disabled=this.start===0;
    this.next.disabled=end>=this.engine.pages;
    this.handle.hidden=mode!=="landscape";
    this.panel.dataset.atlasMode=mode;
  }
  sync(){this.paint();}
  onResize(){
    if(!this.mode){this.paint();return;}
    // Orientation change retains the author-selected leaf; the reading
    // controller recompiles only when its actual paper geometry demands it.
    this.paint();
  }
}
window.FountainMobilePageAtlas=MobilePageAtlas;
})();
