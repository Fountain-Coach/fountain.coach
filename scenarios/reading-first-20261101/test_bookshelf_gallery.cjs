const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const base='https://192.168.8.50:8243',folder=__dirname;
const overrides={'/estate/':'index.html',
 '/estate/assets/linotype/reading-first-app.js':'reading-first-app.js',
 '/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css'};
const expected={essays:7,'first-readings':30};
(async()=>{
 const browser=await webkit.launch({headless:true}),records=[];
 for(const [profile,width,height] of [['landscape',1180,820],['portrait',820,1180],['phone',390,844]]){
  const ctx=await browser.newContext({viewport:{width,height}});
  if(!process.env.LIVE)await ctx.route('**/*',route=>{
    const u=new URL(route.request().url()),file=overrides[u.pathname];
    if(file&&u.host==='192.168.8.50:8243')return route.fulfill({status:200,body:fs.readFileSync(path.join(folder,file)),contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html'});
    return route.continue();
  });
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const res=await page.goto(base+'/estate/#/read/library',{waitUntil:'domcontentloaded'});
  assert.equal(res.status(),200);
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:16000});
  const state=await page.evaluate(()=>{
   const vp=document.querySelector('#page-viewport'),track=vp.querySelector('.reader-scroll-region');
   const panels=[...track.querySelectorAll(':scope > .reader-shelf-panel')].map(x=>({type:x.classList.contains('reader-shelf-gallery')?'gallery':'text',label:x.getAttribute('aria-label')}));
   const gallery=[...vp.querySelectorAll('.reader-shelf-gallery')].map(g=>{
    const sc=g.querySelector('.reader-gallery-scroll'),tiles=[...g.querySelectorAll('.reader-gallery-item')];
    return {collection:sc.dataset.collection,n:tiles.length,scrollable:sc.scrollHeight>sc.clientHeight+1,overflowY:getComputedStyle(sc).overflowY,
     cells:tiles.map(t=>{const sq=t.querySelector('.reader-gallery-square'),img=t.querySelector('img'),rect=sq.getBoundingClientRect();
      return {id:t.dataset.readerTarget,w:rect.width,h:rect.height,fit:getComputedStyle(img).objectFit,src:img.getAttribute('src'),alt:img.alt,role:t.tagName}})};
   });
   const footer=document.querySelector('.frame-controls').getBoundingClientRect();
   return {panels,gallery,trackWidth:track.scrollWidth,trackClient:track.clientWidth,mode:vp.dataset.mode,footerY:footer.bottom,viewportHeight:innerHeight,pageCountHidden:document.querySelector('#page-count').offsetParent===null};
  });
  assert.deepEqual(state.panels.map(x=>x.type),['text','gallery','text','gallery']);
  assert.ok(state.trackWidth>state.trackClient+50);
  assert.equal(state.mode,'horizontal');assert.equal(state.pageCountHidden,true);
  assert.ok(Math.abs(state.footerY-height)<16);
  for(const g of state.gallery){
   assert.equal(g.n,expected[g.collection]);assert.equal(g.overflowY,'auto');
   if(g.collection==='first-readings')assert.ok(g.scrollable,'Reading gallery must overflow vertically');
   for(const cell of g.cells){
    assert.equal(cell.fit,'contain');
    assert.ok(cell.w>0&&Math.abs(cell.w-cell.h)<2,'square cell '+cell.id);
    assert.ok(cell.alt&&cell.src&&cell.role==='BUTTON');
   }
  }
  await page.screenshot({path:path.join(folder,'bookshelf-gallery-'+profile+'.png')});
  const outer=page.locator('.reader-bookshelf .reader-scroll-region').first();
  await outer.evaluate(e=>e.scrollLeft=e.scrollWidth-e.clientWidth);
  await page.waitForTimeout(120);
  const x=await outer.evaluate(e=>e.scrollLeft);assert.ok(x>90);
  const inner=page.locator('.reader-gallery-scroll[data-collection="first-readings"]');
  await inner.evaluate(e=>e.scrollTop=275);
  await page.waitForTimeout(180);
  const y=await inner.evaluate(e=>e.scrollTop);assert.ok(y>40);
  const footerBefore=await page.locator('.frame-controls').boundingBox();
  const tile=page.locator('.reader-gallery-scroll[data-collection="first-readings"] .reader-gallery-item').nth(3);
  const id=await tile.getAttribute('data-reader-target');
  await tile.evaluate(e=>e.addEventListener('click',()=>{window.__galleryYAtClick=e.closest('.reader-gallery-scroll').scrollTop},{capture:true,once:true}));
  await tile.click();
  const atClick=await page.evaluate(()=>window.__galleryYAtClick);
  console.log('GALLERY AT CLICK',profile,y,atClick);
  await page.waitForFunction(v=>document.querySelector('#page-viewport')?.dataset.volume===v&&document.querySelector('#page-viewport')?.dataset.layout==='ready',id,{timeout:18000});
  assert.equal(await page.locator('#reader-parent').getAttribute('data-reader-target'),'library');
  await page.locator('#reader-parent').click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library'&&document.querySelector('#page-viewport')?.dataset.layout==='ready');
  await page.waitForTimeout(150);
  const after=await page.evaluate(()=>{
   const track=document.querySelector('.reader-bookshelf .reader-scroll-region');
   return {x:track.scrollLeft,y:document.querySelector('.reader-gallery-scroll[data-collection="first-readings"]').scrollTop,
    footer:document.querySelector('.frame-controls').getBoundingClientRect().bottom};
  });
  assert.ok(Math.abs(x-after.x)<20,'Restore shelf horizontal position '+JSON.stringify({x,after}));
  assert.ok(Math.abs(atClick-after.y)<20,'Restore gallery vertical position '+JSON.stringify({atClick,after}));
  assert.ok(Math.abs(footerBefore.y+footerBefore.height-after.footer)<3);
  // Verify essay gallery's printing fallback remains a source-owned typeset page.
  const essays=page.locator('.reader-gallery-scroll[data-collection="essays"] .reader-gallery-item');
  assert.equal(await essays.count(),7);
  const imgs=await essays.locator('img').evaluateAll(items=>items.map(x=>x.getAttribute('src')));
  assert.ok(imgs.includes('/estate/assets/essay-share/did-the-machine-actually-read-the-book.png'));
  assert.deepEqual(errors,[]);
  records.push({profile,panels:state.panels.map(x=>x.type),counts:state.gallery.map(x=>({name:x.collection,n:x.n})),x,y,restored:after,errors});
  console.log('PASS',profile,JSON.stringify(records.at(-1)));
  await ctx.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(folder,process.env.LIVE?'bookshelf-gallery-live.json':'bookshelf-gallery-preflight.json'),JSON.stringify({origin:base,sourceInterception:!process.env.LIVE,profiles:records,errors:0},null,2)+'\n');
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
