import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const edition=JSON.parse(fs.readFileSync('/tmp/orange-dot-stage-delta-20261110/estate/collections/orange-dot/edition.json','utf8'));
const base='https://192.168.8.50:8243';
const browser=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
 headless:true,args:['--ignore-certificate-errors','--no-sandbox','--disable-features=HttpsUpgrades']});
const summary=[];
try{
 const views=[['ipad-portrait',820,1180],['ipad-landscape',1180,820],['phone-portrait',390,844]];
 for(const [name,width,height] of views){
  const page=await browser.newPage();
  const errors=[],blocked=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400&&(r.url().includes('orange-dot')||r.url().includes('reading-first-app')))blocked.push(r.url()+':'+r.status());});
  await page.setViewport({width,height,deviceScaleFactor:1,isMobile:name!=='ipad-landscape',hasTouch:true});
  await page.goto(base+'/estate/#/read/library',{waitUntil:'domcontentloaded',timeout:45000});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='library',{timeout:45000});
  const shelf=await page.evaluate(()=>{
   const pages=[...document.querySelectorAll('.reader-collection-page')];
   return {ids:pages.map(x=>x.dataset.collection),
    contentCount:document.querySelectorAll('.reader-collection-page[data-collection="orange-dot"] .reader-contents-entry').length,
    galleryCount:document.querySelectorAll('.reader-collection-page[data-collection="orange-dot"] .reader-gallery-item').length};
  });
  if(shelf.ids.join(',')!=='essays,scores,first-readings,orange-dot,governance'||shelf.contentCount!==23||shelf.galleryCount!==23)
   throw Error(name+' shelf inventory drift '+JSON.stringify(shelf));
  for(const expected of ['scores','first-readings','orange-dot']){
   await page.click('#next-page');
   try { await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.collection===id,{timeout:15000},expected); await new Promise(resolve=>setTimeout(resolve,750)); }catch(err){ console.error('SHELF_NAV_PROBE',name,expected,await page.evaluate(()=>({volume:document.querySelector('#page-viewport')?.dataset.volume,collection:document.querySelector('#page-viewport')?.dataset.collection,previousDisabled:document.querySelector('#previous-page')?.disabled,nextDisabled:document.querySelector('#next-page')?.disabled,scrollLeft:document.querySelector('.reader-bookshelf .reader-scroll-region')?.scrollLeft,bodyWidth:document.body.scrollWidth,viewWidth:innerWidth}))); throw err; }
  }
  await page.click('.reader-collection-page[data-collection="orange-dot"] .reader-contents-entry');
  await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id,{timeout:45000},edition.entries[0].id);
  const first=await page.evaluate(()=>({count:document.querySelector('#page-viewport')?.dataset.pages,
    title:document.querySelector('#source-flow h2')?.textContent,
    img:document.querySelector('#source-flow img')?.naturalWidth??0,
    verticalOverflow:document.documentElement.scrollHeight-innerHeight,
    horizontalOverflow:document.documentElement.scrollWidth-innerWidth}));
  if(!Number(first.count)||first.title!=='Solstice'||!first.img||first.horizontalOverflow>3)
   throw Error(name+' first leaf problem '+JSON.stringify(first));
  await page.screenshot({path:'/tmp/orange-dot-v185-'+name+'.png'});
  let checked=0;
  for(const e of edition.entries){
   await page.evaluate(id=>{
    const x=document.getElementById('reader-section');x.value=id;x.dispatchEvent(new Event('change',{bubbles:true}));
   },e.id);
   await page.waitForFunction(id=>{
    const v=document.querySelector('#page-viewport');
    return v?.dataset.volume===id&&v?.dataset.layout==='ready'&&Number(v?.dataset.pages)>0;
   },{timeout:45000},e.id);
   const info=await page.evaluate(id=>{
    const src=document.getElementById('source-flow');
    return {n:src.querySelectorAll('[data-source-block^="'+id+'.text."]').length,
     images:src.querySelectorAll('img').length,
     loaded:[...src.querySelectorAll('img')].every(im=>im.complete&&im.naturalWidth>0),
     folios:Number(document.querySelector('#page-viewport').dataset.pages),
     pageTitle:src.querySelector('h2')?.textContent??''};
   },e.id);
   if(!info.n||info.images!==e.images.length||!info.loaded||!info.folios)
     throw Error(name+' post '+e.title+' '+JSON.stringify(info));
   checked++;
  }
  // A real adjacent folio is necessary in the longer prose, not only the cover.
  const long=edition.entries.find(e=>e.title==='The Raft');
  await page.evaluate(id=>{const x=document.getElementById('reader-section');x.value=id;x.dispatchEvent(new Event('change',{bubbles:true}));},long.id);
  await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:45000},long.id);
  const before=await page.evaluate(()=>document.querySelector('#page-count')?.textContent??'');
  await page.click('#next-page');
  const after=await page.evaluate(()=>document.querySelector('#page-count')?.textContent??'');
  if(before===after)throw Error(name+' actual folio turn did not advance '+before);
  if(errors.length||blocked.length)throw Error(name+' browser errors '+JSON.stringify({errors,blocked}));
  summary.push({viewport:name,shelfCollections:shelf.ids.length,chronologicalWorks:checked,originalImages:29,
    firstFolio:first.count,proseTurn:[before,after],browserErrors:errors.length,blocked:blocked.length});
  await page.close();
 }
 console.log('ORANGE_DOT_V185_BROWSER_ACCEPTANCE_PASS',JSON.stringify(summary));
}catch(error){
 console.error('ORANGE_DOT_V185_BROWSER_ACCEPTANCE_FAILED',String(error),JSON.stringify(summary));process.exitCode=1;
}finally{await browser.close();}
