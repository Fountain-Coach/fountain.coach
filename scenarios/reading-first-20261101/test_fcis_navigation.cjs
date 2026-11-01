const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=__dirname,base='https://192.168.8.50:8243';
const overrides={
 '/estate/':'index.html',
 '/estate/assets/linotype/reading-first-app.js':'reading-first-app.js',
 '/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css',
 '/estate/assets/linotype/reading-first-press-engine.js':'press-viewport-engine.js'
};
async function run(){
 const browser=await webkit.launch({headless:true});const reports=[];
 for(const [profile,width,height] of [['landscape',1180,820],['portrait',820,1180],['phone',390,844]]){
  const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1});
  if(!process.env.LIVE)await context.route('**/*',route=>{
   const url=new URL(route.request().url());
   const file=overrides[url.pathname];
   if(file && url.host==='192.168.8.50:8243')return route.fulfill({body:fs.readFileSync(path.join(root,file)),contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html',status:200});
   return route.continue();
  });
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  const r=await page.goto(base+'/estate/',{waitUntil:'domcontentloaded'});
  assert.equal(r.status(),200);
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:24000});
  const editorial=await page.evaluate(()=>({v:document.querySelector('#page-viewport').dataset.volume,
    title:document.querySelector('#source-flow h2')?.textContent,
    paragraphs:[...document.querySelectorAll('#page-viewport .linotype-area p')].map(x=>x.textContent).join(' ').slice(0,160),
    pages:document.querySelector('#page-viewport').dataset.pages}));
  assert.equal(editorial.v,'continuity');assert.equal(editorial.title,'On Continuity');
  assert.ok(editorial.paragraphs.includes('Fountain Coach began'));
  await page.screenshot({path:path.join(root,'fcis-next-editorial-'+profile+'.png')});
  for(let i=0;i<12;i++){
   if(await page.locator('#page-viewport').getAttribute('data-volume')==='library')break;
   await page.locator('#next-page').click();
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
   await page.waitForTimeout(35);
  }
  assert.equal(await page.locator('#page-viewport').getAttribute('data-volume'),'library');
  const shelf=await page.evaluate(()=>{const s=document.querySelector('.reader-scroll-region');return{
   titles:[...s.querySelectorAll('button')].map(b=>b.innerText),scrollable:s.scrollWidth>s.clientWidth+5,
   fullWindowScroll:document.documentElement.scrollHeight>innerHeight+2,
   foot:document.querySelector('.frame-controls').getBoundingClientRect().bottom,
   available:innerHeight,
   mode:document.querySelector('#page-viewport').dataset.mode,
   pageNumbers:document.querySelector('#page-count').offsetParent!==null};});
  assert.deepEqual(shelf.titles.map(s=>s.split('\n')[0]),['Essays','First Readings']);
  assert.equal(shelf.mode,'horizontal');assert.ok(shelf.scrollable);assert.equal(shelf.pageNumbers,false);
  await page.screenshot({path:path.join(root,'fcis-next-bookshelf-'+profile+'.png')});
  const scroll=page.locator('.reader-scroll-region');await scroll.evaluate(e=>{e.scrollTo({left:e.scrollWidth,behavior:'instant'})});
  await page.waitForTimeout(120);
  const stats=await scroll.evaluate(e=>({left:e.scrollLeft,max:e.scrollWidth-e.clientWidth,width:e.clientWidth,snap:getComputedStyle(e).scrollSnapType}));
  console.log('SCROLL_HORIZ',profile,JSON.stringify(stats));
  const left=stats.left;assert.ok(left>0);
  await page.locator('[data-reader-target="first-readings"]').last().click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.volume==='first-readings'&&document.querySelector('#page-viewport').dataset.layout==='ready');
  const toc=await page.evaluate(()=>{const s=document.querySelector('.reader-scroll-region');return{
   entries:s.querySelectorAll('.reader-contents-entry').length, scrollable:s.scrollHeight>s.clientHeight+10,mode:document.querySelector('#page-viewport').dataset.mode,
   noNumbers:document.querySelector('#page-count').offsetParent===null,
   fixedFooter:Math.abs(document.querySelector('.frame-controls').getBoundingClientRect().bottom-innerHeight)<15,
   head:document.querySelector('.reader-contents h1')?.textContent
  };});
  assert.equal(toc.entries,32);assert.equal(toc.mode,'vertical');assert.equal(toc.noNumbers,true);assert.ok(toc.scrollable);assert.ok(toc.fixedFooter);
  await page.screenshot({path:path.join(root,'fcis-next-first-readings-'+profile+'.png')});
  await page.locator('.reader-scroll-region').evaluate(e=>e.scrollTop=130);
  const yBefore=await page.locator('.reader-scroll-region').evaluate(e=>e.scrollTop);assert.ok(yBefore>0);
  await page.evaluate(()=>document.querySelector('.reader-contents-entry[data-reader-target="solstice-reading-01--2025-12-22-anweisung-an-den-schmerz"]').addEventListener('click',()=>{window.__tocClickedAt=document.querySelector('.reader-scroll-region').scrollTop},{capture:true}));
  const work='solstice-reading-01--2025-12-22-anweisung-an-den-schmerz';
  await page.locator('.reader-contents-entry[data-reader-target="'+work+'"]').click();
  try{await page.waitForFunction(id=>document.querySelector('#page-viewport').dataset.volume===id&&document.querySelector('#page-viewport').dataset.layout==='ready',work,{timeout:12000})}catch(e){console.log('WORK_FAILURE',profile,JSON.stringify(await page.evaluate(()=>({layout:document.querySelector('#page-viewport').dataset.layout,status:document.querySelector('#reader-status').textContent,geometry:{width:innerWidth,height:innerHeight}}))),errors);throw e;}
  const score=await page.evaluate(()=>{
   const fig=document.querySelector('#page-viewport figure.teatro-score');
   const img=fig?.querySelector('img');const bounds=img?.getBoundingClientRect();
   const area=fig?.closest('.linotype-area')?.getBoundingClientRect();
   return {fig:!!fig,src:img?.getAttribute('src'),width:bounds?.width,height:bounds?.height,
    original:[img?.naturalWidth,img?.naturalHeight],fit:fig?.dataset.scoreFit,
    within:bounds && area ? bounds.left>=area.left-2&&bounds.right<=area.right+2&&bounds.bottom<=area.bottom+2 :false,
    pages:document.querySelector('#page-viewport').dataset.pages};
  });
  assert.ok(score.fig);assert.ok(score.width>100);assert.ok(score.height>100);assert.ok(score.within);assert.equal(score.fit,'balanced');assert.equal(errors.length,0,errors.join('; '));
  await page.screenshot({path:path.join(root,'fcis-next-score-'+profile+'.png')});
  await page.locator('#reader-parent').click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.volume==='first-readings'&&document.querySelector('#page-viewport').dataset.layout==='ready');
  const yAfter=await page.locator('.reader-scroll-region').evaluate(e=>e.scrollTop);
  const clickPosition=await page.evaluate(()=>window.__tocClickedAt);
  console.log('SCROLL_RESTORE',profile,yBefore,clickPosition,yAfter);
  assert.ok(Math.abs(yAfter-clickPosition)<8,'restore contents scroll');
  await page.locator('#reader-parent').click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.volume==='library'&&document.querySelector('#page-viewport').dataset.layout==='ready');
  const afterShelf=await page.locator('.reader-scroll-region').evaluate(e=>e.scrollLeft);
  assert.ok(afterShelf>0,'restore horizontal shelf scroll');
  await page.locator('.reader-shelf-book[data-reader-target="essays"]').click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.volume==='essays'&&document.querySelector('#page-viewport').dataset.layout==='ready');
  assert.equal(await page.locator('.reader-contents-entry').count(),7);
  await page.locator('.reader-contents-entry').first().click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport').dataset.volume==='essay--reframe-and-the-business-value-of-the-estate'&&document.querySelector('#page-viewport').dataset.layout==='ready');
  const essay=await page.locator('#source-flow h2').textContent();assert.equal(essay,'Reframe and the Business Value of the Estate');
  reports.push({profile,editorial,shelf,toc,score,essay,errors});
  console.log('PASS',profile,JSON.stringify({editorial:editorial.v,shelf,toc,score,errors}));
  await context.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(root,process.env.LIVE?'fcis-navigation-live.json':'fcis-navigation-preflight.json'),JSON.stringify({origin:base,sourceOverrides:!process.env.LIVE,runs:reports,failures:0},null,2)+'\n');
}
run().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
