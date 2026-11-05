#!/usr/bin/env node
const fs=require('fs'),assert=require('node:assert/strict');
const {chromium,webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const blob=fs.readFileSync(__dirname+'/stage-v152-legacy-essays-index.html');
(async()=>{
 for(const [name,browserType]of[['webkit',webkit],['chromium',chromium]]){
 const browser=await browserType.launch(name==='chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 try{
  for(const [width,height]of[[390,844],[1440,900]]){
   const ctx=await browser.newContext({viewport:{width,height},ignoreHTTPSErrors:true});
   await ctx.route('**/estate/essays/',route=>route.fulfill({body:blob,status:200,contentType:'text/html'}));
   const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto('https://192.168.8.50:8243/estate/essays/',{waitUntil:'domcontentloaded'});
   const state=await page.evaluate(()=>({
      liveGallery:[...document.querySelectorAll('[data-essay-gallery] [data-essay-route]')].map(x=>x.getAttribute('data-essay-route')),
      archiveNotes:[...document.querySelectorAll('[aria-label="Archived essays"]')].map(x=>({text:x.textContent,href:x.querySelector('a')?.getAttribute('href')})),
      bodyWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth,
      titles:[...document.querySelectorAll('[data-essay-gallery] h3')].map(x=>x.textContent.trim())
   }));
   assert.equal(state.archiveNotes.length,1);
   assert.match(state.archiveNotes[0].text,/Did the Machine Actually Read the Book\?/);
   assert.equal(state.archiveNotes[0].href,'/estate/essays/to-read-is-not-to-remember/');
   assert.ok(!state.liveGallery.some(x=>x.includes('to-read-is-not-to-remember')));
   assert.ok(state.bodyWidth-state.viewportWidth<=3);
   assert.deepEqual(errors,[]);
   console.log('ARCHIVE_GALLERY_PREVIEW_PASS',name,width,height,JSON.stringify({activeCards:state.liveGallery.length,archiveReferences:state.archiveNotes.length,overflows:false}));
   await ctx.close();
  }
 }finally{await browser.close()}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
