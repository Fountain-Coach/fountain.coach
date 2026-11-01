const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const ROOT=__dirname,BASE='https://192.168.8.50:8243';
const intercepts={'/estate/':'index.html','/estate/assets/linotype/reading-first-app.js':'reading-first-app.js','/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css'};
const expected={'essays':7,'first-readings':32};
async function ready(page,volume){
 await page.waitForFunction(v=>{
  const p=document.querySelector('#page-viewport');
  return p&&p.dataset.volume===v&&p.dataset.layout==='ready';
 },volume,{timeout:23000});
}
(async()=>{
 const b=await webkit.launch({headless:true}),reports=[];
 for(const [profile,width,height] of [['landscape',1180,820],['portrait',820,1180],['phone',390,844]]){
  const ctx=await b.newContext({viewport:{width,height}});
  if(!process.env.LIVE)await ctx.route('**/*',r=>{
   const u=new URL(r.request().url()),f=intercepts[u.pathname];
   if(f&&u.host==='192.168.8.50:8243')return r.fulfill({status:200,body:fs.readFileSync(path.join(ROOT,f)),contentType:f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':'text/html'});
   return r.continue();
  });
  const page=await ctx.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(BASE+'/estate/#/read/library',{waitUntil:'domcontentloaded'});
  await ready(page,'library');
  const info=await page.evaluate(()=>{
   const outer=document.querySelector('.reader-bookshelf .reader-scroll-region');
   const panels=[...outer.children];
   const contents=[...document.querySelectorAll('.reader-collection-scroll')].map(p=>({
    id:p.dataset.collection,n:p.querySelectorAll('button.reader-shelf-contents-entry').length,
    ids:[...p.querySelectorAll('button.reader-shelf-contents-entry')].map(b=>b.dataset.readerTarget),
    overflowY:getComputedStyle(p).overflowY,scrollHeight:p.scrollHeight,clientHeight:p.clientHeight
   }));
   const galleries=[...document.querySelectorAll('.reader-gallery-scroll')].map(p=>({id:p.dataset.collection,count:p.querySelectorAll('.reader-gallery-item').length}));
   const foot=document.querySelector('.frame-controls').getBoundingClientRect();
   return {panels:panels.map(x=>x.classList.contains('reader-shelf-statement')?'contents':'gallery'),
    contents,galleries,footer:foot.bottom,viewport:innerHeight,oldLinks:outer.querySelectorAll('.reader-collection-open').length,
    outerWidth:outer.scrollWidth,outerClientWidth:outer.clientWidth};
  });
  assert.deepEqual(info.panels,['contents','gallery','contents','gallery']);
  assert.equal(info.oldLinks,0,'No old read-collection intermediary');
  assert.ok(info.outerWidth>info.outerClientWidth);
  assert.ok(Math.abs(info.footer-height)<15);
  for(const item of info.contents){
   assert.equal(item.n,expected[item.id],item.id+' must list all works');
   assert.equal(new Set(item.ids).size,item.n);
   assert.equal(item.overflowY,'auto');
   if(item.id==='first-readings')assert.ok(item.scrollHeight>item.clientHeight,'long contents must scroll');
  }
  assert.deepEqual(info.galleries.map(x=>x.count),[7,30]);
  await page.screenshot({path:path.join(ROOT,'bookshelf-restored-toc-'+profile+'.png')});
  // Save actual scroll coordinate at the moment of clicking a text entry;
  // browser auto-scroll of the clicked item is a legitimate user-initiated movement.
  const outer=page.locator('.reader-bookshelf .reader-scroll-region');
  await outer.evaluate(e=>e.scrollLeft=e.scrollWidth-e.clientWidth);
  await page.waitForTimeout(100);
  const toc=page.locator('.reader-collection-scroll[data-collection="first-readings"]');
  await toc.evaluate(e=>e.scrollTop=350);
  await page.waitForTimeout(130);
  const chosen=toc.locator('button').nth(9);
  const work=await chosen.getAttribute('data-reader-target');
  await chosen.evaluate(e=>e.addEventListener('click',()=>{
   window.__atTextClick={x:e.closest('.reader-scroll-region').scrollLeft,y:e.closest('.reader-collection-scroll').scrollTop};
  },{capture:true,once:true}));
  await chosen.click();
  const at=await page.evaluate(()=>window.__atTextClick);
  await ready(page,work);
  const crumb=await page.locator('#reader-parent').getAttribute('data-reader-target');
  assert.equal(crumb,'library','Direct shelf work returns directly to Bookshelf');
  await page.locator('#reader-parent').click();
  await ready(page,'library');await page.waitForTimeout(170);
  const restored=await page.evaluate(()=>({x:document.querySelector('.reader-bookshelf .reader-scroll-region').scrollLeft,
   y:document.querySelector('.reader-collection-scroll[data-collection="first-readings"]').scrollTop,
   foot:document.querySelector('.frame-controls').getBoundingClientRect().bottom}));
  assert.ok(Math.abs(restored.x-at.x)<20,JSON.stringify({profile,at,restored}));
  assert.ok(Math.abs(restored.y-at.y)<20,JSON.stringify({profile,at,restored}));
  assert.ok(Math.abs(restored.foot-height)<15);
  // Essays contents also open directly and return to Bookshelf, not via a new contents page.
  const essay=page.locator('.reader-collection-scroll[data-collection="essays"] button').nth(2);
  const essayId=await essay.getAttribute('data-reader-target');
  await essay.click();await ready(page,essayId);
  assert.equal(await page.locator('#reader-parent').getAttribute('data-reader-target'),'library');
  await page.locator('#reader-parent').click();await ready(page,'library');
  assert.deepEqual(errors,[]);
  reports.push({profile,counts:info.contents.map(c=>({id:c.id,count:c.n,scrollable:c.scrollHeight>c.clientHeight})),galleries:info.galleries,at,restored,errors});
  console.log('PASS',profile,JSON.stringify(reports.at(-1)));
  await ctx.close();
 }
 await b.close();
 fs.writeFileSync(path.join(ROOT,process.env.LIVE?'bookshelf-contents-live.json':'bookshelf-contents-preflight.json'),JSON.stringify({origin:BASE,sourceInterception:!process.env.LIVE,runs:reports,failures:0},null,2)+'\n');
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
