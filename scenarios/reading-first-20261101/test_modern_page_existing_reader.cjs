const path=require('node:path'), fs=require('node:fs'), assert=require('node:assert/strict');
const { chromium, webkit }=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const root=__dirname;
const base='http://192.168.8.50:8200';
const passage='essay--what-makes-a-page-modern';
const assetRoot=path.resolve(root,'../../site/essays/what-makes-a-page-modern/assets');
const routes={
 '/estate/':{file:path.join(root,'index.html'),kind:'text/html'},
 '/estate/assets/linotype/reading-first-app.js':{file:path.join(root,'reading-first-app.js'),kind:'text/javascript'},
};
async function run(browserType,label){
 const browser=await browserType.launch(label==='chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 try{
  for(const [width,height] of [[1200,860],[820,1120],[390,844]]){
   const ctx=await browser.newContext({viewport:{width,height},colorScheme:'light'});
   await ctx.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.host!=='192.168.8.50:8200')return route.continue();
    const override=routes[url.pathname];
    if(override) return route.fulfill({status:200,body:fs.readFileSync(override.file),contentType:override.kind});
    if(url.pathname.startsWith('/estate/essays/what-makes-a-page-modern/assets/')){
      const name=path.basename(url.pathname);const file=path.join(assetRoot,name);
      if(!file.startsWith(assetRoot+'/')||!fs.existsSync(file))return route.abort();
      return route.fulfill({status:200,body:fs.readFileSync(file),contentType:'image/svg+xml'});
    }
    return route.fulfill({response:await route.fetch()});
   });
   const page=await ctx.newPage(); const errors=[];
   page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push('CONSOLE '+m.text())});page.on('requestfailed',q=>errors.push('FAIL '+q.url()+' '+q.failure()?.errorText));page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url())});
   await page.goto(base+'/estate/#/read/'+passage,{waitUntil:'domcontentloaded'});
   try{await page.waitForFunction(v=>{
      const vp=document.querySelector('#page-viewport');
      return vp?.dataset.volume===v&&vp?.dataset.layout==='ready';
   },passage,{timeout:12000});}catch(e){console.log('DEBUG',label,width,height,'errors',errors,'html', (await page.content()).slice(0,500));console.log('STATE',await page.evaluate(()=>({v:document.querySelector('#page-viewport')?.dataset,main:document.querySelector('#source-flow')?.innerText?.slice(0,120),error:document.body.innerText.slice(0,240),solstice:!!window.SolsticeLinotype,scripts:[...document.querySelectorAll('script[src]')].map(x=>x.src).slice(0,12)})));throw e;}
   const state=await page.evaluate(()=>{
     const vp=document.querySelector('#page-viewport');
     const arts=[...vp.querySelectorAll('img[src*="/what-makes-a-page-modern/assets/"]')];
     return {layout:vp.dataset.layout,mode:vp.dataset.mode,volume:vp.dataset.volume,
       pages:Number(vp.dataset.pages),nImages:arts.length,
       okImages:arts.filter(x=>x.complete&&x.naturalWidth>0).length,
       blocks:document.querySelector('template[data-reader-volume="essay--what-makes-a-page-modern"]')?.content.querySelectorAll('[data-source-block]').length,
       activeCopy:document.querySelector('#source-flow')?.innerText?.slice(0,90),
       parent:document.querySelector('#reader-parent')?.getAttribute('data-reader-target'),
       viewportOverflow:document.documentElement.scrollWidth-innerWidth
     };
   });
   assert.equal(state.layout,'ready');
   assert.equal(state.volume,passage);
   assert.ok(state.pages>=10,JSON.stringify(state));
   assert.ok(state.blocks>=50,JSON.stringify(state));
   assert.equal(state.parent,'essays',JSON.stringify(state));
   assert.ok(state.viewportOverflow<=3,JSON.stringify(state));
   assert.equal(errors.length,0,errors.join('\n'));
   await page.screenshot({path:path.join('/Users/benedikteickhoff/Developer/.modern-page-existing-reader-QA',label+'-'+width+'x'+height+'.png')});
   await page.goto(base+'/estate/#/read/essays',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='essays' && document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
   const contents=await page.locator('.reader-contents [data-reader-target]').count();
   assert.ok(contents>=6,'Existing Essays contents must list six entries');
   await page.goto(base+'/estate/#/read/library',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library' && document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
   const collection=await page.locator('.reader-gallery-scroll[data-collection="essays"] .reader-gallery-item').count();
   assert.equal(collection,6,'6 essays, existing gallery');
   await page.goto(base+'/estate/#/read/teatro',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='teatro'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
   console.log('PASS',label,width,height,JSON.stringify(state),'essays=',collection,'teatro=ready');
   await ctx.unrouteAll({behavior:'ignoreErrors'}); await ctx.close();
  }
 }finally{await browser.close()}
}
(async()=>{
 fs.mkdirSync('/Users/benedikteickhoff/Developer/.modern-page-existing-reader-QA',{recursive:true});
 await run(chromium,'chromium');
 await run(webkit,'webkit');
})().catch(e=>{console.error(e);process.exitCode=1});
