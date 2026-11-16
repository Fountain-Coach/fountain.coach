// Browser acceptance of the exact compiled static overlay in the actual public
// Fountain Press environment. Overrides only the output paths; no proxy/deploy.
import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {webkit,chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const output=process.env.PRESS_FRONTEND_CANDIDATE;
assert.ok(output && fs.statSync(output).isDirectory(),'PRESS_FRONTEND_CANDIDATE must be an existing immutable build');
const resultPath=process.env.PRESS_FRONTEND_TEST_RESULT || path.join(output,'../browser-proof.json');
const screenDir=process.env.PRESS_FRONTEND_SCREEN_DIR;
const base=process.env.PRESS_FRONTEND_BASE_URL||'https://fountain.coach/';
const origin=new URL(base).origin;
const previewLane=base.includes('192.168.8.50');
if(screenDir)fs.mkdirSync(screenDir,{recursive:true});
const mime={'.html':'text/html;charset=utf-8','.js':'text/javascript;charset=utf-8','.json':'application/json;charset=utf-8','.css':'text/css;charset=utf-8'};
const scenarios=[['desktop',1180,820],['tablet-portrait',820,1180],['phone',390,844]];
const counts={'essays':10,'first-readings':32,'orange-dot':23};
const photos={'essays':10,'first-readings':30,'orange-dot':23};
const books=['essays','first-readings','orange-dot'];
const reports=[];
const configured=(process.env.PRESS_FRONTEND_BROWSERS||'webkit').split(',');
const browserKinds={webkit,chromium};
for(const browserName of configured){
 const browserType=browserKinds[browserName];
 assert.ok(browserType,'Unknown browser: '+browserName);
 const browser=await browserType.launch({headless:true});
 try{
  for(const [name,width,height] of scenarios){
   const context=await browser.newContext({viewport:{width,height}});
   await context.route(origin+'/**',route=>{
    let pathname=new URL(route.request().url()).pathname;
    if(pathname.endsWith('/'))pathname+='index.html';
    const filename=path.join(output,pathname.replace(/^\//,''));
    if(fs.existsSync(filename)&&fs.statSync(filename).isFile()){
     return route.fulfill({status:200,contentType:mime[path.extname(filename)]||'application/octet-stream',body:fs.readFileSync(filename)});
    }
    return route.continue();
   });
   const page=await context.newPage(),errors=[];
   page.on('pageerror',err=>errors.push(err.message));
   const response=await page.goto(base,{waitUntil:'domcontentloaded',timeout:30000});
   assert.equal(response.status(),200);
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000});
   const first=await page.evaluate(()=>({
    volume:document.querySelector('#page-viewport')?.dataset.volume,
    collections:[...document.querySelectorAll('.reader-collection-page')].map(p=>({
      id:p.dataset.collection,contents:p.querySelectorAll('.reader-shelf-contents-entry').length,
      illustrated:p.querySelectorAll('.reader-gallery-item').length,
      next:p.querySelector('.reader-shelf-leaf-next')?.getAttribute('aria-label')||null,
      previous:p.querySelector('.reader-shelf-leaf-previous')?.getAttribute('aria-label')||null,
      position:p.querySelector('.reader-shelf-leaf-position')?.textContent,
    })),
    scrollWidth:document.querySelector('.reader-bookshelf .reader-scroll-region')?.scrollWidth,
    clientWidth:document.querySelector('.reader-bookshelf .reader-scroll-region')?.clientWidth,
    bottom:document.querySelector('.frame-controls')?.getBoundingClientRect().bottom,
  }));
   assert.equal(first.volume,'library');
   const sourceLane=await page.evaluate(()=>JSON.parse(document.querySelector('#reader-publication-data').textContent).publicationLane||'public-production');
   assert.equal(sourceLane,previewLane?'private-owner-WLAN-editorial-review':'public-production');
   if(previewLane)assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'noindex,nofollow');
   assert.deepEqual(first.collections.map(x=>x.id),books);
   for(const col of first.collections){
    assert.equal(col.contents,counts[col.id]);assert.equal(col.illustrated,photos[col.id]);
   }
   assert.equal(first.collections[0].next,'Next published book: First Readings');
   assert.equal(first.collections[1].next,'Next published book: Orange Dot');
   assert.equal(first.collections[1].previous,'Previous published book: Essays');
   assert.equal(first.collections[2].next,null);
   assert.deepEqual(first.collections.map(x=>x.position),['01 / 03','02 / 03','03 / 03']);
   assert.ok(first.scrollWidth>first.clientWidth*2.5);
   assert.ok(Math.abs(first.bottom-height)<15,'footer fixed to viewport');
   if(screenDir)await page.screenshot({path:path.join(screenDir,browserName+'-'+name+'-first.png'),fullPage:false});
   const measured=await page.evaluate(()=>{
    const page=document.querySelector('.reader-collection-page[data-collection="essays"]');
    const headline=page.querySelector('h2').getBoundingClientRect();
    const control=page.querySelector('.reader-shelf-leaf-navigation').getBoundingClientRect();
    const frame=document.querySelector('#page-viewport').getBoundingClientRect();
    return {controlInside:control.left>=frame.left && control.right<=frame.right+2,
            headlineOverlaps:!(control.right<headline.left||control.left>headline.right||control.bottom<headline.top||control.top>headline.bottom),
            compact:document.documentElement.dataset.bookColumns==='single'};
   });
   assert.ok(measured.controlInside,'book navigation must be visible inside frame');
   assert.equal(measured.headlineOverlaps,false,'running book navigation must not overlap title');
   if(measured.compact){
    const area=page.locator('.reader-collection-page[data-collection="essays"]');
    await area.locator('.reader-presentation-button[data-presentation="images"]').click();
    assert.equal(await area.locator('.reader-shelf-gallery').getAttribute('hidden'),null);
    await area.locator('.reader-presentation-button[data-presentation="contents"]').click();
    assert.notEqual(await area.locator('.reader-shelf-gallery').getAttribute('hidden'),null);
   }
   await page.locator('.reader-collection-page[data-collection="essays"] .reader-shelf-leaf-next').click();
   await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.collection==='first-readings',{timeout:6000});
   await page.waitForTimeout(500);
   assert.equal(await page.locator('.reader-collection-page[data-collection="first-readings"] h2').textContent(),'First Readings');
   await page.locator('.reader-collection-page[data-collection="first-readings"] .reader-shelf-leaf-next').click();
   await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.collection==='orange-dot',{timeout:6000});
   await page.waitForTimeout(500);
   const position=await page.evaluate(()=>document.querySelector('.reader-bookshelf .reader-scroll-region').scrollLeft);
   assert.ok(position>first.clientWidth*1.8,'real horizontal scroll to third collection');
   if(screenDir)await page.screenshot({path:path.join(screenDir,browserName+'-'+name+'-orange.png'),fullPage:false});
   await page.locator('.reader-collection-page[data-collection="orange-dot"] .reader-shelf-leaf-previous').click();
   await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.collection==='first-readings',{timeout:6000});
   const historical=await context.newPage(),legacyErrors=[];
   historical.on('pageerror',err=>legacyErrors.push(err.message));
   await historical.goto(origin+'/estate/read/library/',{waitUntil:'domcontentloaded',timeout:30000});
   await historical.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000});
   const legacy=await historical.locator('.reader-collection-page').count();
   assert.equal(legacy,3,'legacy library route must carry the complete current Bookshelf');
   const legacySource=await historical.evaluate(()=>document.querySelector('#reader-publication-data')?.textContent);
   assert.ok(legacySource?.includes('"orange-dot"'),'legacy route includes Orange Dot');
   assert.deepEqual(legacyErrors,[],'legacy route errors');
   await historical.close();
   for(const book of books){
    const detail=await context.newPage(),detailErrors=[];
    detail.on('pageerror',err=>detailErrors.push(err.message));
    await detail.goto(origin+'/estate/books/'+book+'/',{waitUntil:'domcontentloaded',timeout:30000});
    await detail.waitForFunction(expected=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===expected,book,{timeout:25000});
    assert.equal(await detail.locator('.reader-contents-entry').count(),counts[book],book+' direct contents');
    assert.deepEqual(detailErrors,[],book+' direct route JS errors');
    if(previewLane)assert.equal(await detail.locator('meta[name="robots"]').getAttribute('content'),'noindex,nofollow');
    await detail.close();
   }
   assert.deepEqual(errors,[],browserName+' '+name+' runtime errors');
   const row={browser:browserName,viewport:name,first,legacy,scrollLeft:position,errors};
   reports.push(row);console.log('PASS',browserName,name,JSON.stringify({collections:books,counts,photos,legacy,scrollLeft:position}));
   await context.close();
  }
 } finally {await browser.close();}
}
fs.writeFileSync(resultPath,JSON.stringify({candidate:output,verified:reports.length,reports},null,2)+'\n');
console.log('TOTAL',reports.length,'source-authentic frontend browser sessions passed');
