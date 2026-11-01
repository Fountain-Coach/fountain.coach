/* Recompose only the already-published Solstice First Reading source as Fountain Press pages. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const W=__dirname;
const source=fs.readFileSync(path.join(W,'solstice-first-reading-source.html'),'utf8');
const manifest=JSON.parse(fs.readFileSync(path.join(W,'solstice-first-reading-manifest.json'),'utf8'));
if(manifest.edition!=='first-reading'||manifest.publishedWorks!==30||manifest.entries?.length!==30)throw Error('Unaccepted Solstice edition');
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--no-sandbox']});
 const pg=await browser.newPage();
 const edition=await pg.evaluate(({source,manifest})=>{
  const doc=new DOMParser().parseFromString(source,'text/html'),flow=doc.querySelector('#book-flow');
  if(!flow)throw Error('No original Solstice book flow');
  const esc=t=>String(t).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  const permitted=new Set(['em','strong','i','b','cite','small','sup','sub','q','code','span','u']);
  const inline=n=>{
   if(n.nodeType===3)return esc(n.nodeValue);
   if(n.nodeType!==1)return '';
   const tag=n.localName.toLowerCase();
   if(tag==='br')return '<br/>';
   const body=[...n.childNodes].map(inline).join('');
   if(tag==='a'){
    const href=n.getAttribute('href')||'';
    return /^https:\/\//.test(href)?'<a href="'+esc(href)+'" rel="noopener noreferrer" target="_blank">'+body+'</a>':body;
   }
   return permitted.has(tag)?'<'+tag+'>'+body+'</'+tag+'>':body;
  };
  const heading=(name,id)=>'<section class="book-chapter" id="work-'+esc(id)+'"><div class="book-chapter-heading"><h2>'+esc(name)+'</h2></div></section>';
  const article=html=>'<section class="book-chapter-text"><article class="book-prose">'+html+'</article></section>';
  const blocks=(section,slug,seen)=> {
   const out=[];
   for(const n of section.querySelectorAll('p,h2,h3,h4,figure')){
    if(n.closest('figure')&&n.tagName!=='FIGURE')continue;
    if(n.tagName==='FIGURE'){
     const im=n.querySelector('img');if(!im)continue;
     let src=im.getAttribute('src')||'';
     if(!src.startsWith('../../assets/edition/'))continue;
     src='/solstice/assets/edition/'+src.split('/').pop();
     if(seen.has(src))continue;seen.add(src);
     const w=Number(im.getAttribute('width')),h=Number(im.getAttribute('height'));
     if(!(w>0&&h>0))throw Error('Solstice source image missing intrinsic size: '+src);
     const caption=n.querySelector('figcaption');
     out.push('<figure class="frame-reading-figure" data-source-block="'+slug+'.image.'+seen.size+'"><img loading="eager" src="'+esc(src)+'" alt="'+esc(im.getAttribute('alt')||'')+'" width="'+w+'" height="'+h+'"/>'+(caption?'<figcaption>'+esc(caption.textContent)+'</figcaption>':'')+'</figure>');
    }else{
     const text=n.textContent;
     if(!text.trim())continue;
     const tag=/^H[234]$/.test(n.tagName)?'p':'p';
     const key=slug+'.text.'+(out.length+1);
     out.push('<'+tag+' data-source-block="'+key+'" data-source-from="0" data-source-to="'+text.length+'"'+(/^H[234]$/.test(n.tagName)?' class="frame-subheading"':'')+'>'+[...n.childNodes].map(inline).join('')+'</'+tag+'>');
    }
   }
   return out;
  };
  const templates={},inventory=[];
  const sections=[...flow.children];
  const prefaces=sections.filter(s=>s.classList.contains('book-preface'));
  for(let i=0;i<prefaces.length;i++){
   const sec=prefaces[i],id=i===0?'solstice-reading-01--vergil':'solstice-reading-01--preface';
   const title=i===0?'Vergil':'First Reading — Preface';
   const nodes=blocks(sec,id,new Set());
   templates[id]=heading(title,id)+article(nodes.join(''));
   inventory.push({id,title,kind:'preface',sourceParagraphs:nodes.length});
  }
  const originalWorks=sections.filter(s=>s.classList.contains('book-chapter')&&s.id.startsWith('work-'));
  if(originalWorks.length!==30)throw Error('Solstice work inventory mismatch '+originalWorks.length);
  let imageCount=0;
  for(let i=0;i<originalWorks.length;i++){
   const sec=originalWorks[i],entry=manifest.entries[i];
   const slug=sec.id.slice(5),title=sec.querySelector('h2')?.textContent.trim();
   if(!slug||title!==entry.title||!slug.startsWith(entry.date))throw Error('Solstice manifest/source mismatch '+slug);
   const id='solstice-reading-01--'+slug,seen=new Set();
   const openers=blocks(sec,id+'.opener',seen).filter(x=>x.includes('<figure'));
   const prose=[];
   let following=sec.nextElementSibling;
   while(following&&!following.classList.contains('book-chapter')&&!following.classList.contains('book-end')){
    if(following.classList.contains('book-chapter-text')||following.classList.contains('book-art-leaf')){
      prose.push(...blocks(following,id+(following.classList.contains('book-art-leaf')?'.plate':''),seen));
    }
    following=following.nextElementSibling;
   }
   if(seen.size!==entry.images.length)throw Error('Image count mismatch '+slug+' '+seen.size+' / '+entry.images.length);
   imageCount+=seen.size;
   templates[id]=heading(title,id)+article(openers.concat(prose).join(''));
   inventory.push({id,title,kind:'work',date:entry.date,images:seen.size,sourceParagraphs:prose.length});
  }
  if(imageCount!==41)throw Error('Incomplete original image inventory '+imageCount);
  const cover=(name,detail,target,mark)=>'<figure class="frame-book-cover frame-type-cover"><a href="#/read/'+esc(target)+'" data-reader-target="'+esc(target)+'" aria-label="Open '+esc(name)+' in this reader"><span aria-hidden="true" class="frame-cover-mark">'+mark+'</span><span class="frame-cover-name">'+esc(name)+'</span></a><figcaption>'+esc(detail)+'</figcaption></figure>';
  const solstice=heading('Solstice (WT)','solstice')+article(cover('Reading 01','First Reading · published','solstice-reading-01','✳'));
  const index=inventory.map((item,i)=>'<p class="frame-toc-item" data-source-block="solstice-reading-01.index.'+(i+1)+'"><a data-reader-target="'+esc(item.id)+'" href="#/read/'+esc(item.id)+'">'+(item.kind==='work'?String(i-1).padStart(2,'0')+' · ':'')+esc(item.title)+'</a></p>').join('');
  const first=heading('First Reading','solstice-reading-01')+article('<p class="frame-lead">Solstice · Reading 01 · 30 works · 41 original images</p>'+index);
  return {templates:{solstice,'solstice-reading-01':first,...templates},inventory,imageCount};
 },{source,manifest});
 await browser.close();
 const html=Object.entries(edition.templates).map(([id,html])=>'<template data-reader-volume="'+id+'"><div class="book-flow" data-min-leaves="1">'+html+'</div></template>').join('\n');
 fs.writeFileSync(path.join(W,'solstice-volumes.html'),html+'\n');
 fs.writeFileSync(path.join(W,'solstice-source-inventory.json'),JSON.stringify({sourceOwner:'Fountain-Coach/solstice.fountain.coach',sourceSHA256:crypto.createHash('sha256').update(source).digest('hex'),manifestSHA256:crypto.createHash('sha256').update(JSON.stringify(manifest)).digest('hex'),reading:'01',publishedWorks:30,images:edition.imageCount,inventory:edition.inventory},null,2)+'\n');
 console.log('Solstice source projection:',edition.inventory.length,'segments',edition.imageCount,'original images',html.length,'HTML bytes');
})().catch(e=>{console.error(e.stack);process.exitCode=1});
