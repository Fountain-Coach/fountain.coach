const {webkit,chromium}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path');
const base='http://192.168.8.50:8200/estate/';
const volumes=['continuity','library','first-readings','teatro','essays','essay--the-door-is-a-score','notes--the-door-is-a-score','essay--the-ear-that-learns','essay--the-composable-book','essay--to-read-is-not-to-remember','essay--semantic-compilation-the-archive-is-not-the-edition','essay--teatro-an-unfinished-composition','essay--reframe-and-the-business-value-of-the-estate'];
const profiles=[['ipad-landscape',1180,820],['ipad-portrait',820,1180],['phone',390,844]];
const runs=[['webkit',webkit,{}],['chromium',chromium,{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}]];
(async()=>{
const results=[],allFailures=[];let nSheets=0;
for(const [engine,type,launch] of runs){
const browser=await type.launch({headless:true,...launch});
for(const [profile,width,height] of profiles){
 for(const volume of volumes){
  // Independent browser document for each work; no stale page-position
  // timers or session history from the previously audited book.
  const page=await browser.newPage({viewport:{width,height}});
  const errors=[];
  page.on('pageerror',e=>errors.push('page: '+e.message));
  page.on('console',m=>{if(m.type()==='error')errors.push('console: '+m.text())});
  let record={engine,profile,volume,total:0,spreads:0,errors:[]};
  const firstError=0;
  try{
   await page.goto(base+'#/read/'+volume,{waitUntil:'domcontentloaded',timeout:18000});
   await page.waitForFunction(name=>{const v=document.getElementById('page-viewport');return v?.dataset.volume===name&&v?.dataset.layout==='ready'},volume,{timeout:22000});
   const outcome=await page.evaluate(async ()=>{
    const issues=[],read=new Map(),seenPages=new Set();
    const source=document.getElementById('source-flow');
    const expected=new Map([...source.querySelectorAll('[data-source-block]')].filter(n=>!n.closest('[data-press-media]')).map(n=>[n.dataset.sourceBlock,n.textContent]));
    const images=[...source.querySelectorAll('img[src]')];
    const duplicateSources=images.map(i=>i.getAttribute('src')).filter((v,i,a)=>a.indexOf(v)!==i);
    if(duplicateSources.length)issues.push({kind:'duplicate-plate',sources:duplicateSources});
    if(images.some(i=>!i.getAttribute('width')||!i.getAttribute('height'))&&document.getElementById('page-viewport').dataset.volume.startsWith('essay--'))
      issues.push({kind:'source-image-missing-dimensions'});
    let spreads=0,folios=0,previous='',pageTotal=0;
    while(spreads<300){
      const viewport=document.getElementById('page-viewport');
      // A visible folio, unlike an offscreen measurement clone, can be decoded.
      // Inspect the final geometry after its image load, not before.
      await Promise.all([...viewport.querySelectorAll('img')].map(async img=>{
        try{if(!img.complete||!img.naturalWidth)await img.decode();}
        catch(error){issues.push({kind:'visible-image-decode-failed',src:img.src,message:String(error)});}
      }));
      const current=document.getElementById('page-count').textContent;
      const total=Number(current.split('/').pop()?.trim());
      if(!Number.isSafeInteger(total)||total<1)issues.push({kind:'invalid-page-count',current});
      pageTotal=total;
      if(seenPages.has(current)){issues.push({kind:'pagination-cycle',current});break}
      seenPages.add(current);
      const leaves=[...viewport.querySelectorAll('.linotype-sheet')];
      if(!leaves.length)issues.push({kind:'missing-folio',current});
      for(const sheet of leaves){
        folios++;
        const area=sheet.querySelector('.linotype-area');
        if(!area){issues.push({kind:'missing-measured-area',current});continue}
        const bound=area.getBoundingClientRect();
        if(area.scrollHeight>area.clientHeight+1.25||area.scrollWidth>area.clientWidth+1.25)
          issues.push({kind:'scroll-clipping',current,scroll:area.scrollHeight,client:area.clientHeight});
        for(const node of area.querySelectorAll('p,figure,figcaption,img,h2,h3')){
          const rect=node.getBoundingClientRect();
          if(rect.bottom>bound.bottom+1.25||rect.top<bound.top-1.25||rect.right>bound.right+1.25||rect.left<bound.left-1.25)
            issues.push({kind:'visual-clip',current,tag:node.tagName,deltaBottom:Math.round((rect.bottom-bound.bottom)*10)/10,text:node.textContent.slice(0,65)});
        }
        for(const img of area.querySelectorAll('img')){
          if(!img.complete||img.naturalWidth<=0)issues.push({kind:'unloaded-visible-image',current,src:img.src});
        }
        for(const node of area.querySelectorAll('[data-source-block]')){
          if(node.closest('[data-press-media]'))continue; // Player runtime state is not manuscript text.
          const id=node.dataset.sourceBlock;read.set(id,(read.get(id)||'')+node.textContent);
        }
      }
      const button=document.getElementById('next-page');
      if(button.disabled)break;
      button.click();
      if(document.getElementById('page-count').textContent===current){issues.push({kind:'stalled-next-page',current});break}
      spreads++;
      previous=current;
    }
    if(spreads>=300)issues.push({kind:'exceeded-pagination-guard'});
    for(const [id,text] of expected){
     if(text!==read.get(id))issues.push({kind:'missing-or-altered-source',id,wanted:text.length,received:(read.get(id)||'').length});
    }
    for(const id of read.keys())if(!expected.has(id))issues.push({kind:'unexpected-source-block',id});
    if(document.documentElement.scrollHeight>innerHeight+2||document.documentElement.scrollWidth>innerWidth+2)
     issues.push({kind:'document-escape'});
    return {issues,pages:pageTotal,folios,spreads:seenPages.size,sourceBlocks:expected.size,media:images.length};
   });
   record={...record,total:outcome.pages,folios:outcome.folios,spreads:outcome.spreads,sourceBlocks:outcome.sourceBlocks,media:outcome.media,errors:[...outcome.issues,...errors.slice(firstError)]};
   nSheets+=outcome.folios;
   if(volume==='essay--the-door-is-a-score'&&profile==='ipad-landscape'&&engine==='webkit'){
    // Evidence screenshot of the final spread, plus a separate first-spread screenshot.
    await page.screenshot({path:path.join(__dirname,'audit-door-final-webkit.png')});
    await page.goto(base+'#/read/'+volume,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
    await page.screenshot({path:path.join(__dirname,'audit-door-first-webkit.png')});
   }
  }catch(err){record.errors.push({kind:'script-error',message:String(err)})}
  results.push(record);
  if(record.errors.length)allFailures.push(record);
  console.log(JSON.stringify({profile:engine+'/'+profile,volume,pages:record.total,spreads:record.spreads,blocks:record.sourceBlocks,media:record.media,errors:record.errors.slice(0,4),errorCount:record.errors.length}));
  await page.close().catch(()=>{});
 }
}
await browser.close();
}
const receipt={date:'2026-11-01',server:base,runs:results.length,observedFolios:nSheets,failures:allFailures,results};
fs.writeFileSync(path.join(__dirname,'folio-audit-evidence.json'),JSON.stringify(receipt,null,2)+'\n');
console.log('FINAL',JSON.stringify({runs:results.length,folios:nSheets,failed:allFailures.length,firstFailures:allFailures.slice(0,3)}));
if(allFailures.length)process.exitCode=2;
})().catch(err=>{console.error(err.stack);process.exitCode=1});
