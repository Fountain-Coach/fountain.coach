#!/usr/bin/env node
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium,webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const root=__dirname;
const html=fs.readFileSync(root+'/stage-v152-archived.html','utf8');
const old=fs.readFileSync(root+'/stage-v151-before-archive.html','utf8');
const app=fs.readFileSync(root+'/reading-first-app.js');
const work='essay--to-read-is-not-to-remember';
const historical='https://192.168.8.50:8243/estate/essays/to-read-is-not-to-remember/';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const rootURI='https://192.168.8.50:8243/estate/';
(async()=>{
const evidence=[];
for(const [browserName,driver]of[['webkit',webkit],['chromium',chromium]]){
 const browser=await driver.launch(browserName==='chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 try{
 for(const [w,h] of [[390,844],[820,1120],[1440,900]]){
  const context=await browser.newContext({viewport:{width:w,height:h},ignoreHTTPSErrors:true});
  await context.route('**/estate/',r=>r.fulfill({status:200,contentType:'text/html',body:html}));
  await context.route('**/estate/assets/linotype/reading-first-app.js',r=>r.fulfill({status:200,contentType:'text/javascript',body:app}));
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error'&&m.text().includes('Fountain Press reader failure'))errors.push(m.text())});
  try{
   await page.goto(rootURI+'#/read/essays',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='essays'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:24000});
   const inventory=await page.evaluate(work=>{
    const template=document.querySelector('template[data-reader-volume="'+work+'"]');
    const archiveStatus=template.content.querySelector('[data-editorial-role="archive-status"]');
    const galleries=JSON.parse(document.querySelector('#reader-gallery-data').textContent).collections;
    const section=[...document.querySelector('#reader-section').options].map(x=>x.value);
    const links=[...document.querySelectorAll('#page-viewport [data-reader-target]')].map(x=>x.dataset.readerTarget);
    const archivedHTML=template.content.querySelector('article.book-prose')?.innerHTML;
    return {gallery:galleries.essays.map(x=>x.id),section,links,archiveStatus:archiveStatus?.textContent,
      archivedFlag:template.dataset.editorialState,archivedHTML,
      currentCount:document.querySelector('#source-flow')?.innerText?.slice(0,180),
      overflow:document.documentElement.scrollWidth-window.innerWidth};
   },work);
   assert.equal(inventory.gallery.length,5);
   assert.ok(!inventory.gallery.includes(work));
   assert.ok(!inventory.section.includes(work));
   assert.ok(!inventory.links.includes(work));
   assert.equal(inventory.archivedFlag,'archived');
   assert.match(inventory.archiveStatus,/Archived on 5 November 2026/);
   assert.ok(inventory.overflow<=3);
   assert.equal(errors.length,0);
   await page.goto(rootURI+'#/read/'+work,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(work=>document.querySelector('#page-viewport')?.dataset.volume===work&&document.querySelector('#page-viewport')?.dataset.layout==='ready',work,{timeout:20000});
   const direct=await page.evaluate(()=>({
      source:document.querySelector('#source-flow')?.textContent?.slice(0,490),
      pages:document.querySelector('#page-viewport')?.dataset.pages,
      back:document.querySelector('#reader-parent')?.dataset.readerTarget,
      sourceBlocks:[...document.querySelectorAll('#source-flow [data-source-block]')].map(x=>x.dataset.sourceBlock),
      overflow:document.documentElement.scrollWidth-innerWidth
   }));
   assert.match(direct.source,/Did the Machine Actually Read the Book/);
   assert.match(direct.source,/Archived on 5 November 2026/);
   assert.equal(direct.back,'essays');
   assert.ok(direct.sourceBlocks.includes('editorial.archive.to-read-is-not-to-remember'));
   assert.ok(direct.overflow<=3);
   const original=await context.request.get(historical);
   assert.equal(original.status(),200);
   assert.equal(sha(await original.body()),'2eb20df27e4b1a85c2c531f061a712f2aaf66f792df5cda518bb14b62d0822b3');
   const caseReport={browserName,w,h,currentEssays:inventory.gallery.length,archiveDeepLink:true,archivalNote:true,
      originalDirectRouteUnchanged:true,readerParent:'essays',sourceAddressPresent:true,errors};
   evidence.push(caseReport);console.log('ARCHIVE_PREVIEW_PASS',JSON.stringify(caseReport));
  }finally{await context.close()}
 }
 }finally{await browser.close()}
}
const write=root+'/editorial-archive-preflight.json';
fs.writeFileSync(write,JSON.stringify({schema:'fountain.press.archive-preview.v1',sourceRootSHA256:sha(Buffer.from(old)),candidateRootSHA256:sha(Buffer.from(html)),results:evidence},null,2)+'\n');
console.log('ARCHIVE_PREVIEW_VERIFIED',evidence.length,write);
})().catch(e=>{console.error('ARCHIVE_PREVIEW_FAILED',e);process.exitCode=1});
