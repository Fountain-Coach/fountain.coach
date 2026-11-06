const fs=require('node:fs');
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const dir=process.env.PRESS_GOV_FIXTURE_DIR||'/tmp/press-governance-163', root='https://192.168.8.50:8243/estate/';
const live=process.env.PRESS_GOV_STAGE_LIVE==='1';
const manifest=JSON.parse(fs.readFileSync(dir+'/governance-press-manifest.json'));
(async()=>{const browser=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--no-sandbox','--ignore-certificate-errors']});const page=await browser.newPage();await page.setViewport({width:768,height:1024});
const errors=[],responses=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/governance/assets/illustrations/'))responses.push({u:r.url(),s:r.status()})});
if(!live){await page.setRequestInterception(true);page.on('request',r=>{if(r.isNavigationRequest()&&r.url().startsWith(root))return r.respond({status:200,contentType:'text/html; charset=utf-8',body:fs.readFileSync(dir+'/stage/index.html','utf8')});if(r.url()===root+'assets/linotype/reading-first-app.js')return r.respond({status:200,contentType:'application/javascript',body:fs.readFileSync(dir+'/stage/reading-first-app.js','utf8')});return r.continue()});}
try{
 await page.goto(root+'#/read/governance--00-abstract',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
 await page.evaluate(()=>{const proto=window.SolsticeLinotype.prototype,old=proto.compose;proto.compose=function(...args){const result=old.apply(this,args);window.__pressFigureWitness=this.leaves.flatMap((leaf,i)=>[...leaf.area.querySelectorAll('figure[data-source-illustration-id]')].map(f=>({id:f.dataset.sourceIllustrationId,role:f.dataset.pressIllustrationRole,anchor:Number(f.dataset.inlineAfterParagraph),leaf:i+1,src:f.querySelector('img')?.getAttribute('src')})));return result}});
 const results=[];
 for(const chapter of manifest.chapters){
   if(chapter.volumeId==='governance--00-abstract')continue;
   await page.evaluate(id=>location.hash='#/read/'+id,chapter.volumeId);
   await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:35000},chapter.volumeId);
   const v=await page.evaluate(()=>({source:[...document.querySelectorAll('#source-flow figure[data-source-illustration-id]')].map(f=>({id:f.dataset.sourceIllustrationId,role:f.dataset.pressIllustrationRole,anchor:Number(f.dataset.inlineAfterParagraph),src:f.querySelector('img')?.getAttribute('src')})),composed:window.__pressFigureWitness||[],pages:Number(document.querySelector('#page-viewport')?.dataset.pages)}));
   if(v.source.length!==chapter.figures.filter(s=>!s.startsWith('inline-svg:')).length || v.composed.length!==v.source.length)throw Error('Lost image '+chapter.slug+' '+JSON.stringify(v));
   for(let i=0;i<v.source.length;i++){const s=v.source[i],c=v.composed[i];if(s.id!==c.id||s.role!==c.role||s.anchor!==c.anchor||s.src!==c.src)throw Error('Image identity changed '+chapter.slug+' '+JSON.stringify({s,c}));}
   if(v.source.length&&v.composed[0].anchor<=4&&v.composed[0].leaf>3)throw Error('Hero unexpectedly late '+chapter.slug+' '+JSON.stringify(v.composed));
   if(['133-csound-auv3-instrument-boundary','159-userland-the-writers-books-outlive-the-device'].includes(chapter.slug)&&v.composed[0]?.leaf!==1)throw Error('Principal original illustration still missing from first folio '+chapter.slug);
   results.push({chapter:chapter.slug,pages:v.pages,figures:v.composed});
 }
 if(errors.length)throw Error('JS errors '+JSON.stringify(errors));
 console.log(JSON.stringify({status:'PASS',composedChapters:results.length,figureChapters:results.filter(x=>x.figures.length).length,renderedFigures:results.reduce((n,x)=>n+x.figures.length,0),samples:results.filter(x=>x.figures.length).slice(0,5),requestResponses:responses.length},null,2));
 fs.writeFileSync(dir+'/stage/figure-composition-'+(live?'live':'candidate')+'.json',JSON.stringify({status:'PASS',sourceRevision:manifest.sourceRevision,results},null,2));
}finally{await browser.close()}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
