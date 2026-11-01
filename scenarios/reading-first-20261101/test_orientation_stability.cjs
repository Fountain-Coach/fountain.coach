const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const ROOT=__dirname,BASE='https://192.168.8.50:8243/estate/#/read/library';
const routes={'/estate/':'index.html','/estate/assets/linotype/reading-first-app.js':'reading-first-app.js','/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css'};
(async()=>{
 const browser=await webkit.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1180,height:820},isMobile:true,hasTouch:true,deviceScaleFactor:2});
 if(!process.env.LIVE)await context.route('**/*',r=>{
  const u=new URL(r.request().url()),file=routes[u.pathname];
  return file&&u.host==='192.168.8.50:8243'?r.fulfill({status:200,body:fs.readFileSync(path.join(ROOT,file)),contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html'}):r.continue();
 });
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(BASE,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
 await page.locator('#next-page').click();
 await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.collection==='first-readings');
 const first=page.locator('.reader-collection-page[data-collection=first-readings]');
 await first.locator('.reader-shelf-contents-entry').nth(7).focus();
 await page.waitForTimeout(120);
 const before=await page.evaluate(()=>({
  id:document.querySelector('.reader-collection-page[data-collection=first-readings] [aria-current=true]')?.dataset.workId,
  active:document.querySelector('#page-viewport').dataset.collection
 }));
 await page.evaluate(()=>{
  const vp=document.querySelector('#page-viewport');
  window.__turns={replacements:0,blankSamples:0,layoutTransitions:[],snapshots:[],events:[]};
  const obs=new MutationObserver(m=>{
   for(const entry of m){
    if(entry.type==='childList'&&entry.target===vp&&entry.removedNodes.length)window.__turns.replacements++;
    if(entry.type==='attributes'&&entry.attributeName==='data-layout')window.__turns.layoutTransitions.push(vp.dataset.layout);
   }
  });obs.observe(vp,{childList:true,subtree:false,attributes:true,attributeFilter:['data-layout']});
  window.__turnsObserver=obs;
  window.addEventListener('resize',()=>window.__turns.events.push(['resize',innerWidth,innerHeight]));
  visualViewport?.addEventListener('resize',()=>window.__turns.events.push(['visual',visualViewport.width,visualViewport.height]));
 });
 for(const [name,w,h] of [['portrait',820,1180],['rotating-a',862,1115],['rotating-b',888,1040],['landscape',1180,820],['portrait2',820,1180]]){
  await page.setViewportSize({width:w,height:h});
  await page.waitForTimeout(160);
  const snapshot=await page.evaluate(()=>{
   const vp=document.querySelector('#page-viewport'),track=vp.querySelector('.reader-scroll-region');
   const book=vp.querySelector('.reader-collection-page[data-collection=first-readings]');
   const footer=document.querySelector('.frame-controls').getBoundingClientRect();
   const selected=book?[...book.querySelectorAll('[aria-current=true]')].map(x=>x.dataset.workId):[];
   return {mode:vp.dataset.layout,collection:vp.dataset.collection,pages:vp.querySelectorAll('.reader-collection-page').length,
    selected,compact:matchMedia('(max-width:900px)').matches,footerBottom:footer.bottom,
    h:innerHeight,readerHeight:document.querySelector('.reading-shell').getBoundingClientRect().height,
    presentation:book?.dataset.presentation||null,trackX:track?.scrollLeft||0};
  });
  await page.evaluate(s=>window.__turns.snapshots.push(s),snapshot);
  console.log(name,JSON.stringify(snapshot));
  if(name==='portrait2')await page.screenshot({path:path.join(ROOT,'orientation-transition-candidate.png')});
 }
 await page.waitForTimeout(550);
 const result=await page.evaluate(()=>{
  window.__turnsObserver.disconnect();
  return window.__turns;
 });
 const counts=result.snapshots.map(x=>x.pages),identities=result.snapshots.map(x=>x.selected);
 result.baseSelected=before.id;result.errors=errors;
 result.intercepted=!process.env.LIVE;
 console.log('METRICS',JSON.stringify({replacements:result.replacements,layouts:result.layoutTransitions,counts,identities,events:result.events.length,errors}));
 fs.writeFileSync(path.join(ROOT,process.env.LIVE?'orientation-live.json':'orientation-preflight.json'),JSON.stringify(result,null,2)+'\n');
 await browser.close();
 if(process.env.STRICT) {
   assert.equal(result.replacements,0,'The Bookshelf must not be destroyed during rotation');
   assert.equal(result.layoutTransitions.length,0,'Rotation must not unset the Bookshelf readiness');
   assert.ok(result.snapshots.every(x=>x.pages===2&&x.collection==='first-readings'));
   assert.ok(result.snapshots.every(x=>x.selected.length===2&&x.selected.every(id=>id===before.id)));
   assert.ok(result.snapshots.every(x=>Math.abs(x.footerBottom-x.h)<14));
   assert.deepEqual(errors,[]);
 }
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
