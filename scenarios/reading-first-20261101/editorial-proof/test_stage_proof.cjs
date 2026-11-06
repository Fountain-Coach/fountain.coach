// Browser preflight against the REAL live stage assets, overriding only two
// candidate source-owned files in memory. No staging mutation.
const fs=require('node:fs');
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const ROOT='https://192.168.8.50:8243/estate/';
const proof='/tmp/press-sound-essay-proof-v160';
const html=fs.readFileSync(proof+'/index.html','utf8');
const app=fs.readFileSync(proof+'/reading-first-app.js','utf8');
const code='essay--a-sound-must-earn-its-place';
const live=process.env.PRESS_LIVE_STAGE==='1';
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--no-sandbox','--ignore-certificate-errors']});
 let passed=0; const output=[];
 try{
  for(const [width,height] of [[768,1024],[1194,834],[390,844]]){
   const page=await browser.newPage();
   await page.setViewport({width,height,deviceScaleFactor:1});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   if(!live){
   await page.setRequestInterception(true);
   page.on('request',req=>{
    if(req.isNavigationRequest() && req.url().startsWith('https://192.168.8.50:8243/estate')){
     req.respond({status:200,contentType:'text/html; charset=utf-8',body:html}).catch(e=>errors.push(e.message));
    }else if(req.url()===ROOT+'assets/linotype/reading-first-app.js'){
     req.respond({status:200,contentType:'application/javascript; charset=utf-8',body:app}).catch(e=>errors.push(e.message));
    }else req.continue().catch(e=>errors.push(e.message));
   });
   }
   await page.goto(ROOT+'#/read/'+code,{waitUntil:'domcontentloaded',timeout:20000});
   await page.waitForFunction((vol)=>document.querySelector('#page-viewport')?.dataset.volume===vol &&
    document.querySelector('#page-viewport')?.dataset.layout==='ready', {timeout:25000},code);
   const before=await page.evaluate(()=>{
    const view=document.getElementById('page-viewport'),flow=document.getElementById('source-flow');
    return {volume:view.dataset.volume,mode:view.dataset.mode,layout:view.dataset.layout,
      counter:document.getElementById('page-count')?.textContent,
      textLength:flow.innerText.length,
      endPresent:flow.textContent.includes('It is ready when the work can answer for it.'),
      paragraphs:flow.querySelectorAll('p[data-source-block^="a-sound-must-earn"]').length,
      infoCount:document.querySelectorAll('[data-reader-info]').length,
      pageOverflows:document.documentElement.scrollWidth>innerWidth+2};
   });
   if(!before.endPresent||before.paragraphs!==61||before.infoCount<1||before.pageOverflows)
      throw Error('Missing source, info, or viewport failure '+JSON.stringify(before)+' '+errors);
   await page.evaluate(()=>document.querySelector('[data-reader-info]').click());
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes'&&
    document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000});
   const notes=await page.evaluate(()=>({
      related:[...document.querySelectorAll('#source-flow [data-reader-related-public]')].map(a=>a.href),
      proposed:document.querySelector('#source-flow')?.textContent.includes('not an adopted Governance chapter'),
      privateAudioLink:[...document.querySelectorAll('#source-flow a')].some(a=>a.href.includes('192.168.')||a.href.includes('kino')),
      returnCount:document.querySelectorAll('[data-reader-return]').length
   }));
   if(notes.related.length!==2||!notes.proposed||notes.privateAudioLink||notes.returnCount<1)
    throw Error('Incomplete source-bound addendum '+JSON.stringify(notes)+' '+errors);
   await page.evaluate(()=>document.querySelector('[data-reader-return]').click());
   await page.waitForFunction((vol)=>document.querySelector('#page-viewport')?.dataset.volume===vol&&
    document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000},code);
   if(errors.length)throw Error('Browser errors: '+errors.join('; '));
   output.push({width,height,source:before,addendum:notes,returnVolume:await page.evaluate(()=>document.querySelector('#page-viewport')?.dataset.volume),errors});
   passed++;
   await page.close();
  }
  fs.writeFileSync(proof+(live?'/browser-live-acceptance.json':'/browser-preflight.json'),JSON.stringify({status:'PASS',mode:live?'live':'preflight',passed,output},null,2)+'\n');
  console.log(live?'BROWSER_LIVE_EDITORIAL_PROOF_PASS':'BROWSER_EDITORIAL_PROOF_PASS',passed,'layouts');
 } finally {await browser.close();}
})().catch(e=>{console.error(e.stack||String(e));process.exit(1)});
