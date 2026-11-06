// Governance book in the CURRENT Linotype compositor. No alternative renderer.
// Default is candidate interception against real WLAN stage dependencies.
// PRESS_GOV_STAGE_LIVE=1 runs independent direct HTTPS acceptance.
const fs = require('node:fs');
const puppeteer = require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const ROOT = 'https://192.168.8.50:8243/estate/';
const OUTPUT = '/tmp/press-governance-161/stage';
const live = process.env.PRESS_GOV_STAGE_LIVE === '1';
const manifest = JSON.parse(fs.readFileSync('/tmp/press-governance-161/governance-press-manifest.json','utf8'));
const chapters = manifest.chapters;
const samples = ['00-abstract','07-agent-operating-guide','08-validation-and-acceptance',
 '124-midi2-timed-webkit-transitions','127-estate-template-publishing-path',
 '145-one-estate-one-publication-state-estatepublisher-and-reframe-semantic-browser',
 '148-production-runtime-artifact-only','159-userland-the-writers-books-outlive-the-device'];
const launch={headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
 args:['--no-sandbox','--ignore-certificate-errors']};
async function pageSetup(browser,w=768,h=1024) {
 const page=await browser.newPage();
 await page.setViewport({width:w,height:h,deviceScaleFactor:1});
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 if(!live){
  await page.setRequestInterception(true);
  page.on('request',req=>{
   if(req.isNavigationRequest() && req.url().startsWith(ROOT)){
    req.respond({status:200,contentType:'text/html; charset=utf-8',
     body:fs.readFileSync(OUTPUT+'/index.html','utf8')}).catch(e=>errors.push(e.message));
   }else if(req.url()===ROOT+'assets/linotype/reading-first-app.js'){
    req.respond({status:200,contentType:'application/javascript; charset=utf-8',
     body:fs.readFileSync(OUTPUT+'/reading-first-app.js','utf8')}).catch(e=>errors.push(e.message));
   }else req.continue().catch(e=>errors.push(e.message));
  });
 }
 return {page,errors};
}
async function open(page,id,limit=35000){
 await page.goto(ROOT+'#/read/'+id,{waitUntil:'domcontentloaded',timeout:30000});
 await page.waitForFunction(id=>{
  const v=document.querySelector('#page-viewport');
  return v?.dataset.volume===id&&v.dataset.layout==='ready';
 },{timeout:limit},id);
 return page.evaluate(()=>({
  volume:document.querySelector('#page-viewport')?.dataset.volume,
  pages:document.querySelector('#page-viewport')?.dataset.pages,
  first:document.querySelector('#source-flow [data-source-block^="gov."]')?.dataset.sourceBlock,
  paragraphCount:document.querySelectorAll('#source-flow p.gov-source-block').length,
  figures:document.querySelectorAll('#source-flow figure.gov-reading-figure').length,
  pageOverflow:document.documentElement.scrollWidth>innerWidth+2,
  header:document.querySelector('#source-flow .book-chapter-heading h2')?.textContent
 }));
}
(async()=>{
 const browser=await puppeteer.launch(launch),out=[];
 try{
  for(const slug of samples){
   const {page,errors}=await pageSetup(browser);
   const id='governance--'+slug;
   const before=await open(page,id);
   const chapter=chapters.find(x=>x.volumeId===id);
   if(!chapter||before.paragraphCount!==chapter.projectedBlocks || before.figures!==chapter.figures.length||
       before.pageOverflow||errors.length)throw Error('Source/pagination mismatch '+slug+' '+JSON.stringify({before,chapter,errors}));
   await page.evaluate(()=>document.querySelector('[data-reader-info]')?.click());
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes'&&
    document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
   const notes=await page.evaluate(()=>document.querySelector('#source-flow')?.textContent||'');
   if(!notes.includes(chapter.sourceSha256)||!notes.includes(manifest.sourceRevision))
    throw Error('Lost Governance source identity in same-folio addendum '+slug);
   await page.evaluate(()=>document.querySelector('[data-reader-return]')?.click());
   await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id&&
    document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000},id);
   out.push({slug,pages:before.pages,paragraphs:before.paragraphCount,figures:before.figures,return:true});
   await page.close();
  }
  const {page,errors}=await pageSetup(browser,1194,834);
  await page.goto(ROOT+'#/read/governance',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='governance'&&
    document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000});
  const contents=await page.evaluate(()=>({
   entries:document.querySelectorAll('#page-viewport [data-reader-target^="governance--"]').length,
   first:document.querySelector('#page-viewport [data-reader-target^="governance--"]')?.textContent,
   last:[...document.querySelectorAll('#page-viewport [data-reader-target^="governance--"]')].at(-1)?.textContent
  }));
  if(contents.entries!==160||errors.length)throw Error('Governance Contents lacks all 160 chapters '+JSON.stringify({contents,errors}));
  await page.evaluate(()=>document.querySelector('#page-viewport [data-reader-target^="governance--"]')?.click());
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='governance--00-abstract'&&
   document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
  out.push({contents});
  await page.close();
  const {page:shelf,errors:shelfErr}=await pageSetup(browser,768,1024);
  await shelf.goto(ROOT+'#/read/library',{waitUntil:'domcontentloaded'});
  await shelf.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library'&&
   document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000});
  const books=await shelf.evaluate(()=>[...document.querySelectorAll('.reader-collection-page')].map(x=>x.dataset.collection));
  if(books.join(',')!=='essays,first-readings,governance'||shelfErr.length)
   throw Error('Governance is not in original Bookshelf '+JSON.stringify({books,shelfErr}));
  out.push({books});
  await shelf.close();
  fs.writeFileSync(OUTPUT+(live?'/governance-live-browser.json':'/governance-preflight-browser.json'),
    JSON.stringify({mode:live?'live':'preflight',status:'pass',chapters:160,views:out},null,2)+'\n');
  console.log('GOVERNANCE_LINOTYPE_'+(live?'LIVE_':'')+'PASS',out.length,'journeys');
 } finally {await browser.close();}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
