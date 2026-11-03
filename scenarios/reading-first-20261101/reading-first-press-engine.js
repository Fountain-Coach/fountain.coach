/* Linotype: measured sheets for the Solstice reading edition.
   Source HTML stays untouched, accessible without JavaScript. An accepted sheet
   is always fixed-size, never a browser multicolumn fragment.
*/
(() => {
"use strict";
const ROOT = document.documentElement;
const q = (s,r=document)=>r.querySelector(s);
const qa = (s,r=document)=>Array.from(r.querySelectorAll(s));
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const normalized=(n)=>n?.textContent||"";
const textNodes=(element)=>{
  const walker=document.createTreeWalker(element,NodeFilter.SHOW_TEXT);
  const list=[];let n;while((n=walker.nextNode()))list.push(n);
  return list;
};
// Keep a short closing phrase intact on the proof, without changing a
// single manuscript character. In particular, an author's "taste ' )"
// must not leave ')' standing alone on the next line. This is applied
// only to disposable typeset DOM clones, never the original source.
const protectClosingPhrase=(paragraph)=>{
  if(paragraph?.tagName!=="P"||paragraph.classList.contains("book-source-note")||
     paragraph.querySelector(".linotype-keep-tail"))return paragraph;
  const nodes=textNodes(paragraph);
  if(nodes.length!==1)return paragraph; // never disturb mixed inline markup
  const node=nodes[0],raw=node.nodeValue||"";
  const trimmed=raw.trimEnd();
  if(!trimmed)return paragraph;
  const closers=trimmed.match(/(?:[ \t]+[)'\]’”»"]+)+$/u);
  const prefix=closers?trimmed.slice(0,-closers[0].length):trimmed;
  const words=[...prefix.matchAll(/\S+/gu)];
  if(words.length<2)return paragraph;
  const start=words[words.length-2].index;
  const tail=raw.slice(start);
  // A prose line should never become a 60-character nonbreakable token.
  if(tail.length>29)return paragraph;
  const wrapper=document.createElement("span");
  wrapper.className="linotype-keep-tail";
  wrapper.textContent=tail;
  node.nodeValue=raw.slice(0,start);
  node.parentNode.insertBefore(wrapper,node.nextSibling);
  if(paragraph.textContent!==raw)throw Error("Prose source changed by punctuation layout");
  return paragraph;
};
const immutable=(node)=>{
  const clone=node.cloneNode(true);
  return protectClosingPhrase(clone);
};
const fragmentFor=(source,from,to)=>{
  const walker=textNodes(source);
  if(!walker.length)return null;
  const len=normalized(source).length;
  const point=(index)=>{
    let i=clamp(index,0,len);
    for(const node of walker){
      if(i<=node.length)return [node,i];
      i-=node.length;
    }
    return [walker[walker.length-1],walker[walker.length-1].length];
  };
  const range=document.createRange();
  const [sn,so]=point(from),[en,eo]=point(to);
  range.setStart(sn,so);range.setEnd(en,eo);
  const p=source.cloneNode(false);
  p.append(range.cloneContents());
  // Semantic block and original character range survive every measured split.
  // These addresses are optional and do not change legacy edition source.
  if(source.dataset.sourceBlock){
    const base=Number(source.dataset.sourceFrom||0);
    p.dataset.sourceFrom=String(base+from);
    p.dataset.sourceTo=String(base+to);
    p.removeAttribute("id");
  }
  return protectClosingPhrase(p);
};
const boundaries=(s)=>{
  const indices=[];
  for(const m of s.matchAll(/\s+/g)){
    const pos=m.index+m[0].length;
    if(pos>0&&pos<s.length)indices.push(pos);
  }
  // A very long nonbreaking word can still be split without dropping text.
  if(!indices.length&&s.length>2)for(let i=8;i<s.length;i+=8)indices.push(i);
  return indices;
};
class Linotype {
  constructor(viewport, source, options={}) {
    this.viewport=viewport;this.source=source;this.options=options;
    this.pageFrame=options.pageFrame===true;
    this.stage=document.createElement("div");
    this.stage.className="linotype-stage";
    this.stage.setAttribute("role","group");
    this.stage.setAttribute("aria-label",options.label||"Typeset pages of First Reading");
    if(this.pageFrame)this.stage.dataset.frame="viewport";
    viewport.append(this.stage);
    this.leaves=[];this.positions=new Map();this.css={};this.current=0;
  }
  geometry(){
    if(this.pageFrame){
      const w=Math.floor(this.viewport.clientWidth),h=Math.floor(this.viewport.clientHeight);
      if(w<120||h<100)throw Error("The available page is too small. Use continuous reading.");
      const font=parseFloat(getComputedStyle(this.viewport).fontSize)||18;
      const gutter=20,inset=2;
      const minLeaf=Math.max(340,font*20);
      const portrait=h>=w;
      // Scrollbars/toolbars must not dictate facing folios. When the owning
      // reader requests a retained mode during a same-width reflow, obey it.
      const eligible=!portrait&&w>=minLeaf*2+gutter+inset*2;
      const spread=typeof this.options.spreadOverride==='boolean'
        ? this.options.spreadOverride : eligible;
      const width=Math.floor(Math.min(spread?(w-gutter-inset*2)/2:w-inset*2,700));
      const height=h-4;
      this.css={spread,width,height,gutter,scale:1,viewportWidth:w,viewportHeight:h,
        insetX:Math.round(clamp(width*.06,16,38)),insetY:14,font};
      for(const [name,value] of Object.entries({"sheet-w":width+"px","sheet-h":height+"px",
        "sheet-gutter":gutter+"px","sheet-scale":1,"stage-base-w":(width*(spread?2:1)+(spread?gutter:0))+"px"}))
        this.stage.style.setProperty("--"+name,value);
      this.stage.dataset.mode=spread?"spread":"single";
      this.stage.dataset.paper="viewport";
      return this.css;
    }
    const w=Math.max(260,this.viewport.clientWidth);
    const h=Math.max(220,this.viewport.clientHeight);
    const inset=w<600?8:18;
    const gutter=clamp(w*.017,12,24);
    const ratio=Math.SQRT1_2; // A-series paper, portrait
    // Do not typeset a 339px-high miniature just because the viewport is
    // short (landscape mobile or an embedded browser). Typeset a real proof
    // and uniformly scale its visual surface into the available rectangle.
    const candidateH=clamp(h-20,560,790);
    const candidateW=candidateH*ratio;
    const possible=Math.floor((w-inset*2-gutter)/2);
    const spread=window.FountainReadingLayout.mode(w,h)==="spread";
    const width=Math.floor(Math.min(candidateW,spread?possible:Math.max(355,w-inset*2),spread?560:615));
    const height=Math.floor(width/ratio);
    const unscaledW=width*(spread?2:1)+(spread?gutter:0);
    const scale=Math.min(1,(w-inset*2)/unscaledW,(h-14)/height);
    this.css={spread,width,height,gutter,scale,viewportWidth:w,viewportHeight:h,
      insetX:Math.round(clamp(width*.105,27,62)),
      insetY:Math.round(clamp(height*.075,28,56))};
    this.stage.style.setProperty("--sheet-w",width+"px");
    this.stage.style.setProperty("--sheet-h",height+"px");
    this.stage.style.setProperty("--sheet-gutter",gutter+"px");
    this.stage.style.setProperty("--sheet-scale",scale);
    this.stage.style.setProperty("--stage-base-w",unscaledW+"px");
    this.stage.dataset.mode=spread?"spread":"single";
    this.stage.dataset.paper="a-series";
    return this.css;
  }
  reframe(){
    // Screen-frame hosts must recompose and restore an anchor, never scale text.
    if(this.pageFrame)return this.geometry();
    const w=Math.max(260,this.viewport.clientWidth);
    const h=Math.max(220,this.viewport.clientHeight);
    const {width,height,gutter,spread}=this.css;
    const unscaledW=width*(spread?2:1)+(spread?gutter:0);
    const inset=w<600?8:18;
    const scale=Math.min(1,(w-inset*2)/unscaledW,(h-14)/height);
    this.stage.style.setProperty("--sheet-scale",scale);
    this.css.scale=scale;
    this.css.viewportWidth=w;
    this.css.viewportHeight=h;
  }
  leaf(type,sectionId,chapterLabel=null){
    const el=document.createElement("section");
    el.className="linotype-sheet linotype-"+type;
    el.dataset.sourceId=sectionId;
    const heading=document.createElement(this.pageFrame?"h2":"div");heading.className="linotype-running";
    heading.textContent=(this.pageFrame&&this.options.runningTitle)||chapterLabel||document.body.dataset.editionRunningTitle||"FIRST READING";
    const area=document.createElement("div");area.className="linotype-area";
    const folio=document.createElement("div");folio.className="linotype-folio";
    const n=this.leaves.length+1;
    const imprint=this.options.imprint||document.body.dataset.editionImprint||"FOUNTAIN PRESS";
    folio.replaceChildren();
    const hasInfo=this.pageFrame&&this.options.folioInfo;
    const hasReturn=this.pageFrame&&this.options.folioReturn;
    const imprintSpan=document.createElement(hasInfo||hasReturn?"button":"span");
    if(hasInfo||hasReturn){
      imprintSpan.type="button";imprintSpan.className="linotype-info-link";
      if(hasReturn){
        imprintSpan.dataset.readerReturn="true";
        imprintSpan.setAttribute("aria-label","Return to previous reading position");
        imprintSpan.setAttribute("title","Return to reading");
        const mark=document.createElement("img");mark.src="/estate/assets/fountain-coach-logo-transparent.png";
        mark.alt="";mark.width=17;mark.height=17;mark.setAttribute("aria-hidden","true");
        imprintSpan.append(mark);
      }else{
        imprintSpan.dataset.readerInfo="true";
        imprintSpan.setAttribute("aria-label","Open publication notes and legal information");
        imprintSpan.setAttribute("title","Publication notes");imprintSpan.textContent="i";
      }
    }else imprintSpan.textContent=imprint;
    const countSpan=document.createElement("span");countSpan.textContent=String(n).padStart(3,"0");
    folio.append(imprintSpan,countSpan);
    el.append(heading,area,folio);
    el.style.width=this.css.width+"px";
    el.style.height=this.css.height+"px";
    const side=this.css.insetX;
    const top=this.css.insetY;
    el.style.setProperty("--sheet-side",side+"px");
    el.style.setProperty("--sheet-inset-y",top+"px");
    el.style.setProperty("--sheet-font",(this.pageFrame?this.css.font:clamp(this.css.width*.034,14.2,18.1)*(this.fontFactor||1))+"px");
    if(this.pageFrame){
      el.setAttribute("role","group");el.setAttribute("aria-label","Page "+n);
      el.tabIndex=-1;
      el.style.setProperty("--frame-plate-h",Math.max(48,Math.min(240,this.css.height*.42))+"px");
    }
    this.stage.append(el);
    if(this.pageFrame)el.style.setProperty("--frame-plate-h",Math.max(1,Math.min(240,area.clientHeight-1))+"px");
    const obj={el,area,type,sourceId:sectionId,n};
    this.leaves.push(obj);
    if(!this.positions.has(sectionId))this.positions.set(sectionId,n-1);
    return obj;
  }
  fits(area){
    return area.scrollHeight<=area.clientHeight+1.25 &&
           area.scrollWidth<=area.clientWidth+1.25;
  }
  leafOfText(id,label){
    const leaf=this.leaf("text",id,label);
    return leaf;
  }
  appendPiece(leaf,piece){
    leaf.area.append(piece);
    if(this.fits(leaf.area))return true;
    piece.remove();
    return false;
  }
  appendParagraph(leaf,p,sourceId,label,pageType="text"){
    const continuation=()=>pageType==="preface"?this.leaf("preface",sourceId,label):this.leafOfText(sourceId,label);
    if(this.appendPiece(leaf,immutable(p)))return leaf;
    const string=normalized(p);
    if(!string.length)return leaf;
    let offsets=boundaries(string);
    let remaining=p;
    let guard=0;
    while(remaining&&guard++<100){
      if(this.appendPiece(leaf,immutable(remaining)))return leaf;
      const contents=normalized(remaining);
      let breaks=boundaries(contents);
      if(!breaks.length){
        breaks=Array.from({length:Math.ceil(contents.length/6)},(_,i)=>Math.min(contents.length-1,(i+1)*6)).filter(x=>x>0&&x<contents.length);
      }
      let lo=0,hi=breaks.length-1,best=-1;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        const part=fragmentFor(remaining,0,breaks[mid]);
        leaf.area.append(part);
        const fits=this.fits(leaf.area);
        part.remove();
        if(fits){best=breaks[mid];lo=mid+1;}
        else hi=mid-1;
      }
      if(best<0){
        // Not enough room even for the first word; begin a fresh leaf.
        if(leaf.area.children.length){
          leaf=continuation();
          continue;
        }
        // A pathological unbroken token: permit character-level split.
        for(let i=Math.min(contents.length-1,1);i<contents.length;i++){
          const piece=fragmentFor(remaining,0,i+1);
          leaf.area.append(piece);
          const fits=this.fits(leaf.area);
          piece.remove();
          if(!fits){best=i;break;}
        }
        if(best<1)throw Error("Typesetter cannot fit source text on "+sourceId);
      }
      const part=fragmentFor(remaining,0,best);
      const rest=fragmentFor(remaining,best,contents.length);
      if(normalized(part)+normalized(rest)!==contents)throw Error("Source character loss in "+sourceId);
      if(!this.appendPiece(leaf,part))throw Error("Measured paragraph overflow: "+sourceId);
      leaf=continuation();
      remaining=rest;
    }
    if(guard>=100)throw Error("Typesetter stalled on "+sourceId);
    return leaf;
  }
  standard(section,type){
    const id=section.id;
    const sheet=this.leaf(type,id,id==="book-vergil"?"VERGIL · PROLOGUE":
      document.body.dataset.editionRunningTitle||"FIRST READING");
    const contents=immutable(section);
    contents.removeAttribute("id");
    contents.classList.add("linotype-content");
    sheet.area.append(contents);
    if(!this.fits(sheet.area)){
      // The introduction is editorial material, not unbreakable source.
      if(type==="cover")sheet.el.classList.add("linotype-condensed");
      if(type==="preface"){
        contents.remove();
        let page=sheet;
        const isVergil=section.dataset.seriesPreface==="vergil";
        const nodes=[...section.children];
        for(const node of nodes){
          if(!this.appendPiece(page,immutable(node))){
            page=this.leaf(type,id,isVergil?"VERGIL · PROLOGUE":"FIRST READING");
            if(!this.appendPiece(page,immutable(node))){
              if(isVergil&&node.matches("p.vergil-block"))
                page=this.appendParagraph(page,node,id,"VERGIL · PROLOGUE","preface");
              else throw Error("Preface stanza does not fit a full leaf: "+id+" / "+node.textContent.slice(0,35));
            }
          }
        }
      }
    }
    if(!this.fits(sheet.area))throw Error("Unsized "+type+" leaf; content="+sheet.area.scrollWidth+"x"+sheet.area.scrollHeight+" room="+sheet.area.clientWidth+"x"+sheet.area.clientHeight+" stage="+JSON.stringify(this.css));
  }
  image(section,sourceId,opener=false){
    const prior=this.leaves[this.leaves.length-1];
    // An essay's authored heading and following hero are a single chapter,
    // not two nearly empty folios. Continue the same measured page.
    const joinOpener=this.pageFrame&&!opener&&prior&&
      prior.type==="opener"&&prior.sourceId===sourceId&&
      !prior.area.querySelector("figure")&&
      !q(".book-chapter-heading",section);
    const leaf=joinOpener?prior:this.leaf(opener?"opener":"plate",sourceId);
    if(opener && this.pageFrame && !q("figure",section)){
      // A large accessible heading is source text too. Let it continue at
      // original type size rather than clipping or reducing its typography.
      let page=leaf;
      const heading=q(".book-chapter-heading",section);
      for(const node of [...(heading?.children||[])]){
        if(node.matches("h1,h2,h3,p"))page=this.appendParagraph(page,node,sourceId,this.options.runningTitle);
        else if(!this.appendPiece(page,immutable(node)))throw Error("Unbreakable frame heading: "+sourceId);
      }
      return;
    }
    if(opener){
      const heading=q(".book-chapter-heading",section);
      if(heading)leaf.area.append(immutable(heading));
    }
    const frame=document.createElement("div");
    frame.className="linotype-image-frame";
    const figure=q("figure",section);
    if(!figure){
      // A documented technical chapter can be a typographic opener without
      // an illustration. Never generate fake images to satisfy a book fixture.
      if(!this.fits(leaf.area))throw Error("Text-only chapter opener overflow: "+sourceId);
      return;
    }
    frame.append(immutable(figure));
    leaf.area.append(frame);
    const title=q(".book-chapter-heading",leaf.area);
    if(figure?.classList.contains("teatro-score")||figure?.classList.contains("frame-essay-hero")){
      // FCIS Largest Balanced Fit: measure the *real* source aspect ratio
      // against the remaining folio after the title/caption, never against
      // a generic 190px thumbnail or a decorative portrait/landscape box.
      const image=q("img",frame);
      const figureEl=q("figure",frame);
      const originalW=Number(image?.getAttribute("width"));
      const originalH=Number(image?.getAttribute("height"));
      if(!(originalW>0&&originalH>0))throw Error("Unmeasured Teatro Score "+sourceId);
      const caption=q("figcaption",figureEl);
      const titleH=title?title.getBoundingClientRect().height+14:0;
      const captionH=caption?Math.max(18,caption.getBoundingClientRect().height+12):0;
      const availableW=leaf.area.clientWidth-10;
      const availableH=leaf.area.clientHeight-titleH-captionH-24;
      if(availableH<=60||availableW<=70)throw Error("No readable Score folio "+sourceId);
      const fit=Math.min(availableW/originalW,availableH/originalH);
      let renderW=Math.floor(originalW*fit),renderH=Math.floor(originalH*fit);
      frame.dataset.aspect=(originalW/originalH).toFixed(4);
      const size=()=>{
        figureEl.style.width=renderW+"px";figureEl.style.maxWidth=renderW+"px";
        figureEl.style.height=(renderH+captionH)+"px";figureEl.style.maxHeight=(renderH+captionH)+"px";
        image.style.width=renderW+"px";image.style.height=renderH+"px";
        image.style.maxWidth=renderW+"px";image.style.maxHeight=renderH+"px";
        image.style.minHeight="0";image.style.objectFit="contain";
      };
      size();
      let attempts=0;
      while(!this.fits(leaf.area)&&attempts++<18){
        renderW=Math.floor(renderW*.95);renderH=Math.floor(renderH*.95);
        size();
      }
      if(!this.fits(leaf.area))throw Error("Oversize Score "+sourceId);
      if(figure.classList.contains("teatro-score"))figureEl.dataset.scoreFit="balanced";
      else figureEl.dataset.essayHeroFit="balanced";
      return;
    }
    // WebKit can report a transient zero-height heading before its font/layout
    // settles. Reserve the opener's full running-title height in every pass.
    const titleH=title?Math.max(124,title.getBoundingClientRect().height):0;
    const maxH=Math.max(90,leaf.area.clientHeight-titleH-66);
    const img=q("img",frame);
    const figureEl=q("figure",frame);
    const portrait=(Number(img.getAttribute("width"))/Number(img.getAttribute("height")))<1.14;
    frame.dataset.aspect=portrait?"portrait":"landscape";
    // The authored image aspect, not an ornamental golden-ratio placeholder,
    // determines the widest legible plate within the physical folio.
    const intrinsic=Number(img.getAttribute("width"))/Number(img.getAttribute("height"));
    const aspect=Number.isFinite(intrinsic)&&intrinsic>0?intrinsic:(portrait?1/1.618:1.618);
    const frameW=Math.floor(Math.min(leaf.area.clientWidth-10,maxH*aspect));
    const frameH=Math.floor(frameW/aspect);
    figureEl.style.width=frameW+"px";
    figureEl.style.height=frameH+"px";
    figureEl.style.maxWidth=frameW+"px";
    figureEl.style.maxHeight=frameH+"px";
    const caption=q("figcaption",frame);
    const capHeight=caption?Math.max(22,caption.getBoundingClientRect().height+12):14;
    img.style.maxHeight=Math.max(65,frameH-capHeight-20)+"px";
    img.style.maxWidth=Math.max(80,frameW-20)+"px";
    // Safari sometimes measures a plate before its image/caption has settled.
    // Resolve *both* horizontal and vertical overflow on every plate, not only
    // on illustrated chapter openers. Always shrink the frame, never crop art.
    let attempts=0;
    while(!this.fits(leaf.area)&&attempts++<14){
      const overW=leaf.area.scrollWidth>leaf.area.clientWidth+1;
      const overH=leaf.area.scrollHeight>leaf.area.clientHeight+1;
      if(title&&overH){
        const heading=q("h2",title);
        if(heading)heading.style.fontSize=Math.max(18,parseFloat(getComputedStyle(heading).fontSize)*.93)+"px";
      }
      const oldWidth=parseFloat(figureEl.style.width);
      const narrow=Math.max(120,Math.floor(oldWidth*(overW ? 0.88 : 0.94)));
      figureEl.style.width=narrow+"px";
      figureEl.style.maxWidth=narrow+"px";
      figureEl.style.height=Math.floor(narrow/aspect)+"px";
      figureEl.style.maxHeight=figureEl.style.height;
      img.style.maxWidth=Math.max(80,narrow-24)+"px";
      img.style.maxHeight=Math.max(70,Math.min(parseFloat(img.style.maxHeight)*.94,
        parseFloat(figureEl.style.height)-capHeight-20))+"px";
    }
    if(!this.fits(leaf.area))throw Error("Plate overflow "+sourceId+" "+JSON.stringify({area:[leaf.area.clientWidth,leaf.area.clientHeight,leaf.area.scrollWidth,leaf.area.scrollHeight],titleH,img:[img.getBoundingClientRect().width,img.getBoundingClientRect().height],fig:[q("figure",frame).getBoundingClientRect().width,q("figure",frame).getBoundingClientRect().height],frame:[frame.clientWidth,frame.clientHeight]}));
  }
  // An authored mixed-media object is part of the source sequence, not a
  // post-pagination overlay. When requested, compose its short preceding
  // source passage with the object atomically on one physical sheet.
  // This avoids an unanchored full-page "application" orphan.
  mediaWithAnchor(leaf,paragraph,media,sourceId,label){
    const pair=[immutable(paragraph),immutable(media)];
    const measure=(sheet)=>{
      sheet.area.append(...pair);
      if(this.fits(sheet.area))return true;
      pair.forEach(node=>node.remove());
      return false;
    };
    if(measure(leaf))return leaf;
    const following=this.leafOfText(sourceId,label);
    if(!measure(following)){
      // A short landscape screen cannot always hold text and player together.
      // Keep both authored objects, but permit an adjacent leaf instead of
      // refusing the entire book after rotation.
      this.appendParagraph(following,paragraph,sourceId,label);
      const mediaLeaf=this.leafOfText(sourceId,label);
      if(!this.appendPiece(mediaLeaf,immutable(media)))
        throw Error("Standalone media exceeds folio: "+media.dataset.pressMedia);
      return mediaLeaf;
    }
    return following;
  }
  inFlowFigure(leaf,source,sourceId,label){
    // Every authored illustration is measured against its real intrinsic
    // aspect. The old fixed 190px figure height produced thumbnail-sized
    // artwork alongside full-width body text.
    const prepare=(area)=>{
      const figure=immutable(source),image=q("img",figure);
      figure.classList.add("linotype-inline-illustration");
      if(image){
        const iw=Number(image.getAttribute("width")),ih=Number(image.getAttribute("height"));
        if(iw>0&&ih>0){
          // Secondary illustrations are substantial, but not principal
          // opener plates. Cap their folio height to leave prose readable.
          const maxH=Math.max(80,Math.floor(area.clientHeight*.66));
          const w=Math.max(70,Math.floor(Math.min(area.clientWidth-8,maxH*(iw/ih))));
          const h=Math.floor(w*ih/iw);
          image.style.width=w+"px";image.style.height=h+"px";
          image.style.minHeight="0";image.style.maxHeight=h+"px";
          image.style.maxWidth="100%";image.style.objectFit="contain";
        }
      }
      return figure;
    };
    const reserve=Math.max(76,this.css.font*4);
    const insert=(target)=>{
      const figure=prepare(target.area);
      if(!this.appendPiece(target,figure))return false;
      // Avoid a floating picture at the very foot of a page, with no room
      // for the manuscript to resume. This measurement uses actual layout.
      const bottom=target.area.getBoundingClientRect().bottom;
      const illustrationBottom=figure.getBoundingClientRect().bottom;
      if(bottom-illustrationBottom<reserve){
        figure.remove();
        return false;
      }
      return true;
    };
    if(insert(leaf))return leaf;
    leaf=this.leafOfText(sourceId,label);
    if(!insert(leaf))
      throw Error("Secondary illustration cannot fit with prose reserve: "+sourceId);
    return leaf;
  }
  text(section,sourceId,label){
    const last=this.leaves[this.leaves.length-1];
    // Preserve source order, but let an illustrated leaf carry prose whenever
    // measured free space can accommodate a useful paragraph beginning.
    // The ordinary appendParagraph fitter starts a new leaf if it cannot.
    const free=last ? last.area.getBoundingClientRect().bottom - (last.area.lastElementChild?.getBoundingClientRect().bottom ?? last.area.getBoundingClientRect().top) : 0;
    let sheet=last && last.sourceId===sourceId &&
      ((this.pageFrame && free >= Math.max(100,this.css.font*5)) ||
       (!last.area.querySelector(".linotype-image-frame figure") && (this.pageFrame || last.type==="opener")))
      ? last : this.leafOfText(sourceId,label);
    // Editorial proem belongs to the composed work, never to original
    // manuscript paragraphs. It follows the chapter image and precedes
    // narrative prose on a measured leaf, with a separate source-block.
    const editorial=q(".frame-editorial-proem[data-editorial-role=proem]",section);
    if(editorial){
      // Keep the illustration, editor's address and first narrative line
      // together whenever their actual geometry fits. Never orphan the proem
      // beneath a large plate with no space left for the story.
      if(sheet.area.querySelector(".linotype-image-frame figure")){
        const trial=immutable(editorial);
        const first=q(".book-prose > p",section);
        // Reserve a readable opening of the first paragraph, not the entire
        // paragraph (which may legitimately continue onto the next leaf).
        const firstText=first?normalized(first):"";
        const trialParagraph=first?fragmentFor(first,0,Math.min(firstText.length,110)):null;
        sheet.area.append(trial);
        if(trialParagraph)sheet.area.append(trialParagraph);
        const canFlow=this.fits(sheet.area);
        trialParagraph?.remove();trial.remove();
        if(!canFlow)sheet=this.leafOfText(sourceId,label);
      }
      if(!this.appendPiece(sheet,immutable(editorial))){
        sheet=this.leafOfText(sourceId,label);
        if(!this.appendPiece(sheet,immutable(editorial)))
          throw Error("Editorial preface will not fit: "+sourceId);
      }
    }
    const prose=q(".book-prose",section);
    if(!prose)throw Error("No prose for "+sourceId);
    const elements=[...prose.children];
    // The first Score belongs to the chapter opener. All subsequent
    // original-post images are authored within prose and belong in the
    // narrative rhythm, not a second/third autonomous opening plate.
    const secondary=elements.filter(e=>e.matches("figure.frame-reading-figure"));
    const narrative=elements.filter(e=>e.tagName==="P" &&
      !/^SOURCE · ORIGINAL AUTHOR TEXT ·/.test(e.textContent.trim()));
    const anchors=secondary.map((figure,index)=>{
      // The author can supply a precise text beat without changing prose.
      const appointed=Number(figure.dataset.inlineAfterParagraph);
      return Number.isInteger(appointed)&&appointed>=1&&appointed<=narrative.length
        ?appointed:Math.max(1,Math.round((index+1)*narrative.length/(secondary.length+1)));
    });
    let paragraphNumber=0,illustrationNumber=0;
    const appendDue=()=>{
      while(illustrationNumber<secondary.length &&
            anchors[illustrationNumber]<=paragraphNumber){
        const figure=secondary[illustrationNumber++];
        sheet=this.inFlowFigure(sheet,figure,sourceId,label);
      }
    };
    for(let i=0;i<elements.length;i++){
      const element=elements[i];
      const media=elements[i+1];
      if(element.tagName==="P" && media?.hasAttribute("data-press-media") &&
         media.dataset.keepWithAnchor==="previous" && element.textContent.length<=360){
        sheet=this.mediaWithAnchor(sheet,element,media,sourceId,label);
        i++; // the authored media is inseparable from the preceding passage
      }else if(element.matches("figure.frame-reading-figure")){
        // Defer the original-post supplementary illustration to its anchored
        // paragraph; never turn it into a second principal score plate.
        continue;
      }else if(element.matches("figure.teatro-score")){
        // A standalone score which is NOT an original-post supplementary
        // image retains its existing plate semantics.
        const plate=document.createElement("section");
        plate.append(element.cloneNode(true));
        this.image(plate,sourceId,false);
        const imageLeaf=this.leaves[this.leaves.length-1];
        const available=imageLeaf.area.getBoundingClientRect().bottom - (imageLeaf.area.lastElementChild?.getBoundingClientRect().bottom ?? imageLeaf.area.getBoundingClientRect().top);
        sheet=available>=Math.max(100,this.css.font*5)?imageLeaf:this.leafOfText(sourceId,label);
      }else if(element.tagName==="P" &&
        /^SOURCE · ORIGINAL AUTHOR TEXT · (\d{4}-\d{2}-\d{2}) SOURCE PAGE ↗$/.test(element.textContent.trim())){
        // The supplied provenance string is a source record, not a line of
        // narrative prose and not a real link. Keep its exact source block for
        // lossless audit, but print a genuine endnote after the closing rule.
        const original=element.cloneNode(true);
        original.hidden=true;
        original.setAttribute("aria-hidden","true");
        original.classList.add("linotype-source-record");
        sheet=this.appendParagraph(sheet,original,sourceId,label);
        const date=element.textContent.trim().match(/(\d{4})-(\d{2})-(\d{2})/);
        const months=["January","February","March","April","May","June",
          "July","August","September","October","November","December"];
        const published=Number(date[3])+" "+months[Number(date[2])-1]+" "+date[1];
        const notes=document.createElement("aside");
        notes.className="linotype-endnotes";
        notes.setAttribute("aria-label","Source notes");
        const rule=document.createElement("hr");
        const note=document.createElement("p");
        note.textContent="Source · Original author text · "+published;
        notes.append(rule,note);
        if(!this.appendPiece(sheet,notes)){
          // A provenance-only final leaf is not an acceptable editorial
          // ending. Bring the final source paragraph with its endnote when
          // the previous folio has a meaningful preceding passage.
          const prior=sheet;
          const visible=[...prior.area.children].filter(el=>
            el.tagName==="P"&&!el.hidden&&
            !el.classList.contains("linotype-source-record"));
          const tail=visible.length>=2?visible[visible.length-1]:null;
          const originalRecord=prior.area.querySelector(":scope > .linotype-source-record");
          sheet=this.leafOfText(sourceId,label);
          let moved=false;
          if(tail){
            // Keep source order: the original hidden provenance must follow
            // the relocated last prose paragraph, not precede it.
            sheet.area.append(tail);
            if(originalRecord)sheet.area.append(originalRecord);
            moved=this.appendPiece(sheet,notes);
            if(!moved){
              tail.remove();
              originalRecord?.remove();
              if(originalRecord){
                prior.area.append(originalRecord);
                prior.area.insertBefore(tail,originalRecord);
              }else prior.area.append(tail);
            }
          }
          if(!moved&&!this.appendPiece(sheet,notes))
            throw Error("Source endnote will not fit: "+sourceId);
        }
      }else if(element.tagName==="P"){
        sheet=this.appendParagraph(sheet,element,sourceId,label);
        paragraphNumber++;
        appendDue();
      }else{
        if(!this.appendPiece(sheet,immutable(element))){
          sheet=this.leafOfText(sourceId,label);
          if(!this.appendPiece(sheet,immutable(element)))throw Error("Oversize block in "+sourceId);
        }
      }
    }
    // An image is never discarded if a source contains too few paragraphs.
    while(illustrationNumber<secondary.length){
      sheet=this.inFlowFigure(sheet,secondary[illustrationNumber++],sourceId,label);
    }
    const sourceNote=q(".book-source-note",section);
    if(sourceNote && !this.appendPiece(sheet,immutable(sourceNote))){
      sheet=this.leafOfText(sourceId,label);
      if(!this.appendPiece(sheet,immutable(sourceNote)))throw Error("Source note won't fit");
    }
  }
  compose(fontFactor=1){
    this.fontFactor=fontFactor;
    this.stage.replaceChildren();
    this.leaves=[];this.positions.clear();
    this.geometry();
    this.stage.dataset.mode="measure";
    const nodes=[...this.source.children];
    let currentId="book-cover",label="FIRST READING";
    for(const node of nodes){
      if(node.classList.contains("book-score"))this.standard(node,"score");
      else if(node.classList.contains("book-cover"))this.standard(node,"cover");
      else if(node.classList.contains("book-preface"))this.standard(node,"preface");
      else if(node.classList.contains("book-chapter")){
        currentId=node.id;
        label=q("h2",node)?.textContent||"FIRST READING";
        this.image(node,currentId,true);
      }else if(node.classList.contains("book-art-leaf"))this.image(node,currentId);
      else if(node.classList.contains("book-chapter-text"))this.text(node,currentId,label);
      else if(node.classList.contains("book-end"))this.standard(node,"end");
    }
    // Trace IDs belong to source passages, never measured physical folios.
    // Refuse to publish an ambiguous or unresolvable address.
    for(const address of this.source.querySelectorAll('[data-score-trace-id]')){
      const traceId=address.dataset.scoreTraceId;
      if(!traceId||this.positions.has(traceId))throw Error('Duplicate Score trace identity: '+traceId);
      const matches=this.leaves.flatMap((leaf,i)=>
        leaf.area.querySelector('[data-score-trace-id="'+CSS.escape(traceId)+'"]')?[i]:[]);
      if(matches.length!==1)throw Error('Score trace has no unique typeset source: '+traceId);
      this.positions.set(traceId,matches[0]);
    }
    this.pages=this.leaves.length;
    const minLeaves=this.source.dataset.minLeaves===undefined?4:Number(this.source.dataset.minLeaves);
    if(!Number.isSafeInteger(minLeaves)||minLeaves<1||this.pages<minLeaves)
      throw Error("Insufficient typeset leaves");
    // Byte-for-byte equivalent text content across every deliberate split.
    // Paragraph boundaries and inline emphasis remain represented in DOM.
    const sourceChapterParagraphs=new Map();
    for(const original of this.source.querySelectorAll(".book-chapter-text")){
      let opener=original.previousElementSibling;
      while(opener&&!opener.classList.contains("book-chapter"))opener=opener.previousElementSibling;
      const id=opener?.id;
      if(!id)throw Error("Unbound manuscript passage");
      // Several prose sections can belong to the same chapter (e.g. an
      // image, score, or performance between paragraphs). Validate the
      // concatenated, ordered source once per chapter, not each section
      // against all pages of that chapter. Never weaken the exact-text test.
      const content=sourceChapterParagraphs.get(id)||[];
      content.push(...[...original.querySelectorAll(".book-prose p")].map(x=>x.textContent));
      sourceChapterParagraphs.set(id,content);
    }
    for(const [id,paragraphs] of sourceChapterParagraphs){
      const expected=paragraphs.join("");
      const received=this.leaves.filter(x=>x.sourceId===id &&
          (x.type==="text" || x.type==="opener" || x.type==="plate"))
        .flatMap(x=>[...x.area.querySelectorAll(":scope > p:not(.book-source-note):not(.frame-essay-abstract)")])
        .map(x=>x.textContent).join("");
      if(expected!==received)throw Error("Source text lost in pagination: "+id);
    }
    // The series prompt must survive typesetting without losing or inventing text.
    const vergil=this.source.querySelector('[data-series-preface="vergil"]');
    if(vergil){
      const expected=[...vergil.querySelectorAll('[data-vergil-block]')]
        .map(p=>[p.dataset.vergilBlock,p.textContent]);
      const pieces=this.leaves.filter(leaf=>leaf.sourceId==="book-vergil")
        .flatMap(leaf=>[...leaf.area.querySelectorAll('[data-vergil-block]')])
        .map(p=>[p.dataset.vergilBlock,p.textContent]);
      const actual=[];
      for(const [id,text] of pieces){
        const last=actual[actual.length-1];
        if(last&&last[0]===id)last[1]+=text;
        else actual.push([id,text]);
      }
      if(expected.length!==actual.length ||
         expected.some((item,i)=>item[0]!==actual[i][0]||item[1]!==actual[i][1]))
        throw Error("Vergil preface source lost during book composition");
    }
    // Verify addressed source blocks (including headings and definitions), not
    // just prose paragraphs. A page is a projection, never a source identity.
    if(this.pageFrame){
      const expected=[...this.source.querySelectorAll("[data-source-block]")];
      const ids=new Set();
      for(const block of expected){
        const id=block.dataset.sourceBlock;
        if(ids.has(id))throw Error("Duplicate semantic block: "+id);
        ids.add(id);
        const copies=this.leaves.flatMap(leaf=>[...leaf.area.querySelectorAll("[data-source-block]")])
          .filter(node=>node.dataset.sourceBlock===id);
        if(copies.map(node=>node.textContent).join("")!==block.textContent)
          throw Error("Source block lost in composition: "+id);
      }
    }
    // None of the accepted areas may clip their actual content.
    for(const item of this.leaves){
      if(!this.fits(item.area))throw Error("Oversized leaf "+item.n+" / "+item.sourceId);
      if(this.pageFrame){
        const bounds=item.area.getBoundingClientRect();
        for(const node of item.area.querySelectorAll('p,figure,figcaption,img,h2,h3')){
          // The original provenance record remains in the source audit, but
          // intentionally hidden nodes have no rendered box to clip.
          if(node.hidden || getComputedStyle(node).display==='none')continue;
          const rect=node.getBoundingClientRect();
          if(rect.bottom>bounds.bottom+1.25||rect.right>bounds.right+1.25||
             rect.top<bounds.top-1.25||rect.left<bounds.left-1.25)
            throw Error("Clipped content on leaf "+item.n+": "+node.tagName+
              " / "+item.sourceId+" / bottom "+rect.bottom+" > "+bounds.bottom);
        }
      }
    }
    return this;
  }
  spreadStart(index){
    const page=clamp(index,0,this.leaves.length-1);
    if(!this.css.spread)return page;
    if(this.pageFrame)return page-page%2;
    return page===0?0:page%2===0?page-1:page;
  }
  display(index){
    this.current=this.spreadStart(index);
    this.stage.replaceChildren();
    const items=this.css.spread
      ? (this.pageFrame?[this.leaves[this.current],this.leaves[this.current+1]||null]:
        this.current===0?[null,this.leaves[0]]:[this.leaves[this.current],this.leaves[this.current+1]||null])
      : [this.leaves[this.current]];
    this.stage.dataset.mode=this.css.spread?"spread":"single";
    for(let j=0;j<items.length;j++){
      const obj=items[j];
      if(obj){obj.el.dataset.verso=(j===0&&this.css.spread)?"left":"right";this.stage.append(obj.el);}
      else{
        const blank=document.createElement("div");
        blank.className="linotype-blank";
        if(this.pageFrame&&this.options.folioReturn){
          // Mirror the book's return at the same bottom-left folio coordinate
          // on an empty facing leaf: the finger need not change its location.
          blank.classList.add("linotype-addendum-facing");
          const action=this.leaves[0]?.el.querySelector("button[data-reader-return]")?.cloneNode(true);
          if(action){
            action.style.left=this.css.insetX+"px";
            action.style.bottom=this.css.insetY+"px";
            blank.append(action);
          }
        }else blank.setAttribute("aria-hidden","true");
        this.stage.append(blank);
      }
    }
    return this.current;
  }
  next(){
    const future=this.spreadStart(clamp(this.current+(this.css.spread?(this.pageFrame?2:this.current===0?1:2):1),0,this.pages-1));
    return future>this.current?future:this.current;
  }
  prev(){return clamp(this.current-(this.css.spread?2:1),0,this.pages-1);}
  currentChapter(){
    const sheet=this.leaves[this.current];
    // A chapter opener may be the right-hand page of the current spread.
    // The reading location then belongs to that selected chapter, rather
    // than the previous chapter's final verso.
    const right=this.css.spread && this.current>0?this.leaves[this.current+1]:null;
    if(right && right.type==="opener" && right.sourceId!==sheet?.sourceId)
      return right.sourceId;
    return sheet?.sourceId||"book-cover";
  }
  anchorAt(index=this.current){
    const leaf=this.leaves[index];
    const node=leaf?.area.querySelector("[data-source-block]");
    return node?{chapter:leaf.sourceId,block:node.dataset.sourceBlock,offset:Number(node.dataset.sourceFrom||0)}:null;
  }
  pageForAnchor(anchor){
    if(!anchor)return 0;
    const offset=Number(anchor.offset)||0;
    const hit=this.leaves.findIndex(leaf=>[...leaf.area.querySelectorAll("[data-source-block]")].some(node=>
      node.dataset.sourceBlock===anchor.block&&Number(node.dataset.sourceFrom||0)<=offset&&
      (offset<Number(node.dataset.sourceTo||node.textContent.length)||
       (offset===0&&!node.textContent.length))));
    if(hit<0 && this.pageFrame)throw Error("Unknown source passage or offset: "+anchor.block+"@"+offset);
    return hit<0?0:hit;
  }
  dispose(){
    this.stage.replaceChildren();
    this.leaves=[];this.positions.clear();
  }
}
window.SolsticeLinotype=Linotype;
})();