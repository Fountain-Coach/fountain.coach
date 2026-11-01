// Authoring-time, source-preserving projection of the already-staged editions.
// The resulting HTML is static. The browser reader never fetches another site's shell.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const W=__dirname;
const sources={teatro:fs.readFileSync(path.join(W,'original-teatro.html'),'utf8'),essays:fs.readFileSync(path.join(W,'original-essays-continuing.html'),'utf8'),first:fs.readFileSync(path.join(W,'original-first-readings.html'),'utf8')};
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--no-sandbox']});
 const page=await browser.newPage();
 const answer=await page.evaluate(input=>{
  const parse=x=>new DOMParser().parseFromString(x,'text/html');
  const es=parse(input.essays),tr=parse(input.teatro),first=parse(input.first);
  const esc=t=>String(t).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  const allow=new Set(['em','strong','b','i','code','sup','sub','cite','span','small','q']);
  const referenceCatalog=[];
  let currentReferenceScope=null;
  function cleanInline(node){
   if(node.nodeType===3)return esc(node.nodeValue);
   if(node.nodeType!==1)return '';
   const name=node.localName.toLowerCase();
   if(name==='br')return '<br/>';
   let content=[...node.childNodes].map(cleanInline).join('');
   if(name==='a'){
    const href=node.getAttribute('href')||'';
    if(!(/^(https?:\/\/|\/)/.test(href)))return content;
    const safe=esc(href);
    if(currentReferenceScope==='the-door-is-a-score' && /^https?:\/\//.test(href)){
      const number=referenceCatalog.length+1;
      referenceCatalog.push({number,label:plain(node),href});
      return '<a class="frame-note-link" href="#/read/notes--the-door-is-a-score" data-reader-target="notes--the-door-is-a-score" data-note-number="'+number+'">'+content+'</a>';
    }
    return '<a href="'+safe+'" target="_blank" rel="noopener noreferrer">'+content+'</a>';
   }
   if(allow.has(name))return '<'+name+'>'+content+'</'+name+'>';
   return content;
  }
  function plain(n){return n.textContent||''}
  function normalizeItem(el,slug,n){
   const tag=el.localName?.toLowerCase();
   const key=slug+'.p'+n;
   if(tag==='p'){
    const content=[...el.childNodes].map(cleanInline).join('');
    return '<p data-source-block="'+esc(key)+'" data-source-from="0" data-source-to="'+plain(el).length+'">'+content+'</p>';
   }
   if(['h2','h3','h4'].includes(tag)){
    const content=[...el.childNodes].map(cleanInline).join('');
    return '<p class="frame-subheading" data-source-block="'+esc(key)+'" data-source-from="0" data-source-to="'+plain(el).length+'">'+content+'</p>';
   }
   if(tag==='figure'){
    const img=el.querySelector('img'),caption=el.querySelector('figcaption');
    if(!img)return '';
    const src=img.getAttribute('src')||'';
    if(!src.startsWith('/estate/'))return '';
    const width=Number(img.getAttribute('width')),height=Number(img.getAttribute('height'));
    if(!(width>0&&height>0))throw Error('Authored image has no measurable dimensions: '+src);
    return '<figure class="frame-reading-figure'+(slug==='the-door-is-a-score'&&n===1?' frame-integrated-figure':'')+'" data-source-block="'+esc(key)+'"><img loading="eager" decoding="sync" src="'+esc(src)+'" alt="'+esc(img.getAttribute('alt')||'')+'" width="'+width+'" height="'+height+'"/>'+(caption?'<figcaption>'+esc(plain(caption))+'</figcaption>':'')+'</figure>';
   }
   return '';
  }
  function listeningFolio(slug){
    if(slug!=='the-door-is-a-score')return '';
    return '<figure class="frame-press-av" data-press-media="satzfunk-player.recorded-directions.v1" data-keep-with-anchor="previous" data-source-block="door.av.recorded"><satzfunk-player label="Four performed directions of the door closing"></satzfunk-player><p class="press-av-status" role="status"></p><figcaption>Four authored recordings · fourteen seconds each · source score and interpretation retained.</figcaption></figure>';
  }
  function buildChapter(node,slug,title){
   currentReferenceScope=slug;
   const items=[];
   let scan=node.nextElementSibling,number=0,paragraphs=0,figures=0;
   const seenPlateSources=new Set();
   const addPlate=figure=>{
    const src=figure.querySelector('img')?.getAttribute('src');
    if(!src||seenPlateSources.has(src))return;
    const image=normalizeItem(figure,slug,++number);
    if(image){items.push(image);figures++;seenPlateSources.add(src);}
   };
   // Original plate appears in both opener and body on some legacy essays.
   // This one authored illustration is one compositional occurrence.
   for(const figure of node.querySelectorAll('figure'))addPlate(figure);
   while(scan&&!scan.classList.contains('book-chapter')&&!scan.classList.contains('book-end')){
    if(scan.classList.contains('book-chapter-text')){
     for(const article of scan.querySelectorAll('article.book-prose')){
      for(const element of article.children){
       if(!['P','H2','H3','H4','FIGURE'].includes(element.tagName))continue;
       if(slug==='the-door-is-a-score'&&['door-small','door-note','door-sentence','door-source','book-inline-original'].some(cls=>element.classList.contains(cls))){
         // Original UI chrome, not editorial prose: replace with the admitted Player figure.
         continue;
       }
       if(slug==='the-door-is-a-score'&&(element.matches('[data-engine-status]')||element.classList.contains('book-original-exhibit-note')||['Perform it here','Recall the closing','Stop'].includes(plain(element).trim())))continue;
       if(element.tagName==='FIGURE'){addPlate(element);continue;}
       const html=normalizeItem(element,slug,++number);
       if(html){items.push(html);paragraphs++;}
       if(slug==='the-door-is-a-score'&&plain(element).startsWith('Four newly written microtexts direct three openly licensed recordings.')){
         items.push(listeningFolio(slug));
       }
      }
     }
    }
    if(scan.classList.contains('book-art-leaf')){
     for(const figure of scan.querySelectorAll('figure'))addPlate(figure);
    }
    scan=scan.nextElementSibling;
   }
   const c='<section class="book-chapter" id="work-'+esc(slug)+'"><div class="book-chapter-heading"><h2 data-source-block="'+esc(slug)+'.title">'+esc(title)+'</h2></div></section><section class="book-chapter-text"><article class="book-prose">'+items.join('')+'</article></section>';
   currentReferenceScope=null;
   return {slug,title,html:c,paragraphs,figures,characters:node.parentElement?.textContent?.length||0};
  }
  const chunks=[];
  const metadata=[];
  const tnode=tr.querySelector('#book-flow .book-chapter[data-book-chapter="teatro-an-unfinished-composition"]');
  if(!tnode)throw Error('Source-authenticated Teatro chapter missing');
  chunks.push(buildChapter(tnode,'teatro-an-unfinished-composition','Teatro — An Unfinished Composition'));
  for(const section of es.querySelectorAll('#book-flow .book-chapter[data-book-chapter]')){
   const slug=section.dataset.bookChapter, title=section.querySelector('h2')?.textContent?.trim();
   if(!slug||!title)throw Error('Unidentified essay');
   chunks.push(buildChapter(section,slug,title));
  }
  if(chunks.length!==8)throw Error('Expected one Teatro + seven Essays, got '+chunks.length);
  const tCover=first.querySelector('[data-book-id="teatro-an-unfinished-composition"] img')?.getAttribute('src');
  if(!tCover)throw Error('Original First Readings cover absent');
  const libraryItems=[
   {name:'Essays',detail:'Chronological essays',target:'essays',mark:'E'},
   {name:'Solstice (WT)',detail:'Reading 01 · First Reading',target:'solstice',mark:'✳'}
  ];
  const cover=({name,detail,target,image,mark})=>
    '<figure class="frame-book-cover"><a href="#/read/'+esc(target)+'" data-reader-target="'+esc(target)+'" aria-label="Open '+esc(name)+' inside this reader">'+(image?'<img src="'+esc(image)+'" alt="" loading="eager"/>':'<span class="frame-cover-mark" aria-hidden="true">' +esc(mark||'')+ '</span>')+'<span class="frame-cover-name">'+esc(name)+'</span></a><figcaption>'+esc(detail)+'</figcaption></figure>';
  const heading=(slug,title)=>'<section class="book-chapter" id="work-'+slug+'"><div class="book-chapter-heading"><h2>'+esc(title)+'</h2></div></section>';
  const page=(name,body,slug)=>heading(slug,name)+'<section class="book-chapter-text"><article class="book-prose">'+body+'</article></section>';
  const library=page('The Bookshelf','<div class="frame-shelf-grid">'+libraryItems.map(cover).join('')+'</div>','library');
  const firsts=page('First Readings',cover({name:'An Unfinished Composition',detail:'Teatro · Benedikt Eickhoff',target:'teatro',image:tCover}),'first-readings');
  // Chapters are encountered by turning pages, not by a hyperlink index.
  const essays=page('Essays','<p class="frame-edition-imprint">Seven essays · chronological edition</p>','essays');
  const noteItems=referenceCatalog.map(({number,label,href})=>'<p class="frame-reference-entry" data-source-block="door.note.'+number+'"><span class="frame-reference-number">'+number+'.</span> <a href="'+esc(href)+'" target="_blank" rel="noopener noreferrer" aria-label="Open cited source: '+esc(label)+'">'+esc(label)+'</a></p>').join('');
  const notes=page('References','<p class="frame-reference-intro">Sources cited in The Door Is a Score. Opening a source is a deliberate action outside this edition.</p>'+noteItems,'door-references');
  const out={
    templates:{
      library, 'first-readings':firsts, essays, teatro:chunks[0].html,
      'notes--the-door-is-a-score':notes,
      ...Object.fromEntries(chunks.slice(1).map(c=>['essay--'+c.slug,c.html]))
    },
    chapters:chunks.map(({slug,title,paragraphs,figures})=>({slug,title,paragraphs,figures})),
    sourceCover:tCover,
    noteCount:referenceCatalog.length
  };
  return out;
 },sources);
 await browser.close();
 const summary=answer.chapters;
 console.log(JSON.stringify({summary,sourceCover:answer.sourceCover},null,2));
 if(summary.some(x=>x.paragraphs<3))throw Error('Incomplete extracted source paragraphs');
 const templates=Object.entries(answer.templates).map(([id,html])=>'<template data-reader-volume="'+id+'"><div class="book-flow" data-min-leaves="1">'+html+'</div></template>').join('\n');
 fs.writeFileSync(path.join(W,'integrated-volumes.html'),templates+'\n');
 fs.writeFileSync(path.join(W,'integrated-manifest.json'),JSON.stringify({stageOnly:true,sourceSHA256:Object.fromEntries(Object.entries(sources).map(([n,x])=>[n,crypto.createHash('sha256').update(x).digest('hex')])),chapters:summary,volumes:Object.keys(answer.templates)},null,2)+'\n');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
