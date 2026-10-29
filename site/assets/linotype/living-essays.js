/* Fountain Coach living Essays: source-preserving semantic sequence projection.
 * The published chapter bodies remain static. Only reader-chosen order changes.
 * Run before Press book.js so the measured engine sees one fixed sequence.
 */
(() => {
  "use strict";
  const measureReader=()=>{
    const estate=document.querySelector("header.fc-estate-shell");
    const toolbar=document.querySelector("header.book-toolbar");
    const pager=document.querySelector("footer.book-pagination");
    const root=document.documentElement.style;
    root.setProperty("--living-estate-header",Math.round(estate?.getBoundingClientRect().height||0)+"px");
    root.setProperty("--living-toolbar",Math.round(toolbar?.getBoundingClientRect().height||62)+"px");
    root.setProperty("--living-pager",Math.round(pager?.getBoundingClientRect().height||90)+"px");
  };
  measureReader();
  window.addEventListener("resize",measureReader,{passive:true});
  const flow=document.getElementById("book-flow");
  const select=document.getElementById("living-reading-path");
  const toc=document.querySelector("#book-contents .book-toc-list");
  if(!flow||!select||!toc)return;
  const pairs=[...flow.children].filter(node=>node.matches(".book-chapter[data-book-chapter]"))
    .map((heading,index)=>{
      const blocks=[];
      for(let node=heading.nextElementSibling;node&&!node.matches(".book-chapter,#book-end");node=node.nextElementSibling){
        if(!node.matches(".book-chapter-text,.book-art-leaf"))
          throw new Error("Unexpected content type in the living book");
        blocks.push(node);
      }
      if(!blocks.some(x=>x.matches(".book-chapter-text[data-chapter-content]")))
        throw new Error("The living book must preserve every authored chapter");
      return {heading,blocks,id:heading.dataset.bookChapter,
        tags:(heading.dataset.semanticRoles||"").split(/\s+/),
        written:heading.dataset.writtenAt||null,
        editorialIndex:index};
    });
  if(pairs.length<1||new Set(pairs.map(p=>p.id)).size!==pairs.length)
    throw new Error("No unique published chapters");
  const written=pairs.filter(p=>p.written).sort((a,b)=>b.written.localeCompare(a.written));
  const newest=written[0]||pairs[0];
  const rules={
    recent:[],
    sound:["sound","listening","performance","theatre"],
    reading:["reading","composing","memory","publishing"],
    systems:["economics","systems","software","publisher"]
  };
  const url=new URL(window.location.href);
  const requested=url.searchParams.get("path")||"recent";
  const mode=Object.hasOwn(rules,requested)?requested:"recent";
  select.value=mode;
  const order=[newest,...pairs.filter(p=>p!==newest).sort((a,b)=>{
    if(mode==="recent")return a.editorialIndex-b.editorialIndex;
    const relevance=x=>Math.min(...x.tags.map(t=>{
      const rank=rules[mode].indexOf(t);return rank<0?999:rank;
    }));
    const left=relevance(a),right=relevance(b);
    return left-right||a.editorialIndex-b.editorialIndex;
  })];
  const end=flow.querySelector("#book-end");
  for(const [index,pair] of order.entries()){
    if(end){end.before(pair.heading);for(const block of pair.blocks)end.before(block);}
    else{flow.append(pair.heading,...pair.blocks);}
    pair.heading.dataset.chapterNumber=String(index+1);
    const ordinal=pair.heading.querySelector(".book-ordinal span");
    if(ordinal)ordinal.textContent=String(index+1).padStart(2,"0")+
      " / "+String(order.length).padStart(2,"0");
  }
  for(const [index,pair] of order.entries()){
    const link=toc.querySelector('[data-book-toc-target="'+CSS.escape(pair.id)+'"]');
    if(!link)throw new Error("Contents omits "+pair.id);
    const item=link.closest("li");
    const label=link.querySelector(".toc-number");
    if(label)label.textContent=String(index+1).padStart(2,"0");
    toc.append(item);
  }
  document.body.dataset.editionEntryAnchor="work-"+newest.id;
  document.body.dataset.latestWritten=newest.id;
  document.body.dataset.semanticReadingPath=mode;
  select.addEventListener("change",()=>{
    const chosen=select.value;
    if(!Object.hasOwn(rules,chosen))return;
    const next=new URL(location.href);
    if(chosen==="recent")next.searchParams.delete("path");
    else next.searchParams.set("path",chosen);
    // Preserve the semantic source work address, not a physical leaf number.
    window.location.assign(next.pathname+next.search+next.hash);
  });
  // The existing Press Contents dialog remains native and user-initiated.
})();
