// One real Linotype browser, every canonical Governance chapter, source identity
// and paginator through the existing edition route. No second compositor.
const fs=require('node:fs');
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const ROOT='https://192.168.8.50:8243/estate/';
const FIXTURE=process.env.PRESS_GOV_FIXTURE_DIR || '/tmp/press-governance-161';
const DIR=FIXTURE+'/stage';
const live=process.env.PRESS_GOV_STAGE_LIVE==='1';
const manifest=JSON.parse(fs.readFileSync(FIXTURE+'/governance-press-manifest.json','utf8'));
(async()=>{
 const b=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
 args:['--no-sandbox','--ignore-certificate-errors']});
 const p=await b.newPage();await p.setViewport({width:768,height:1024});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 if(!live){
  await p.setRequestInterception(true);
  p.on('request',q=>{
   if(q.isNavigationRequest()&&q.url().startsWith(ROOT))
    q.respond({status:200,contentType:'text/html',body:fs.readFileSync(DIR+'/index.html','utf8')});
   else if(q.url()===ROOT+'assets/linotype/reading-first-app.js')
    q.respond({status:200,contentType:'application/javascript',body:fs.readFileSync(DIR+'/reading-first-app.js','utf8')});
   else q.continue();
  });
 }
 const results=[];
 try {
  await p.goto(ROOT+'#/read/'+manifest.chapters[0].volumeId,{waitUntil:'domcontentloaded'});
  for(const chapter of manifest.chapters){
   if(results.length)await p.evaluate(id=>location.hash='#/read/'+id,chapter.volumeId);
   try{
    await p.waitForFunction(id=>{
     const el=document.querySelector('#page-viewport');
     return el?.dataset.volume===id && el?.dataset.layout==='ready';
    },{timeout:15000},chapter.volumeId);
    const entry=await p.evaluate(()=>({
      pages:document.querySelector('#page-viewport')?.dataset.pages,
      blocks:document.querySelectorAll('#source-flow p.gov-source-block').length,
      figures:document.querySelectorAll('#source-flow figure.gov-reading-figure').length,
      source:document.querySelector('template[data-reader-volume="'+document.querySelector('#page-viewport')?.dataset.volume+'"]')?.dataset.sourceSha256,
      overflow:document.documentElement.scrollWidth>innerWidth+2
    }));
    if(entry.source!==chapter.sourceSha256 || entry.blocks!==chapter.projectedBlocks ||
       entry.figures!==chapter.figures.length || entry.overflow || errors.length)
      throw Error('Wrong reader source/composition: '+JSON.stringify({entry,errors}));
    results.push({id:chapter.volumeId,pages:entry.pages,blocks:entry.blocks,figures:entry.figures,status:'pass'});
   }catch(error){
    const state=await p.evaluate(()=>({
     volume:document.querySelector('#page-viewport')?.dataset.volume,
     layout:document.querySelector('#page-viewport')?.dataset.layout,
     status:document.querySelector('#reader-status')?.textContent,
     failure:document.querySelector('#page-viewport')?.textContent?.slice(0,220)
    }));
    throw Error('GOV CHAPTER '+chapter.slug+' failed after '+results.length+' / '+manifest.chapters.length+': '+error.message+' '+JSON.stringify({state,errors}));
   }
  }
  fs.writeFileSync(DIR+(live?'/governance-corpus-live.json':'/governance-corpus-preflight.json'),JSON.stringify({
   schema:'fountain.press.governance.corpus-browser-acceptance.v1',mode:live?'live':'preflight',
   passed:results.length,sourceRevision:manifest.sourceRevision,status:'pass',results},null,2));
  console.log('GOVERNANCE_CORPUS_'+(live?'LIVE_':'')+'PASS',results.length);
 } finally {await b.close();}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
