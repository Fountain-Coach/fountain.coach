const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const BASE='https://192.168.8.50:8243',FILES={'/estate/':'index.html','/estate/assets/linotype/reading-first-app.js':'reading-first-app.js','/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css'};
async function ready(p,v){await p.waitForFunction(x=>{const el=document.querySelector('#page-viewport');return el?.dataset.volume===x&&el.dataset.layout==='ready'},v,{timeout:22000});}
(async()=>{
 const b=await webkit.launch({headless:true}),runs=[];
 for(const [label,w,h,compact] of [['landscape',1180,820,false],['portrait',820,1180,true],['phone',390,844,true]]){
  const c=await b.newContext({viewport:{width:w,height:h},colorScheme:'light'});
  if(!process.env.LIVE)await c.route('**/*',r=>{
   const u=new URL(r.request().url()),f=FILES[u.pathname];
   return f&&u.host==='192.168.8.50:8243'?r.fulfill({status:200,body:fs.readFileSync(path.join(__dirname,f)),contentType:f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':'text/html'}):r.continue();
  });
  const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(BASE+'/estate/#/read/library',{waitUntil:'domcontentloaded'});
  await ready(p,'library');await p.waitForTimeout(240);
  const initial=await p.evaluate(()=>{
   const track=document.querySelector('.reader-scroll-region'),pages=[...document.querySelectorAll('.reader-collection-page')];
   return {n:pages.length,units:pages.map(x=>x.dataset.collection),ids:pages.map(x=>({
     id:x.dataset.collection,
     txt:[...x.querySelectorAll('.reader-shelf-contents-entry')].map(b=>b.dataset.workId),
     imgs:[...x.querySelectorAll('.reader-gallery-item')].map(b=>b.dataset.workId),
     widths:[...x.querySelectorAll('.reader-collection-pair > .reader-shelf-panel')].map(a=>a.getBoundingClientRect().width),
     presentations:[...x.querySelectorAll('.reader-shelf-panel')].map(a=>({name:a.dataset.presentation,hidden:a.hidden}))})),
     width:track.clientWidth,max:track.scrollWidth,footer:document.querySelector('.frame-controls').getBoundingClientRect().bottom,
     compact:matchMedia('(max-width:900px)').matches,
     nextDisabled:document.querySelector('#next-page').disabled};
  });
  assert.equal(initial.n,2);assert.deepEqual(initial.units,['essays','first-readings']);assert.ok(initial.max>initial.width);
  assert.deepEqual(initial.ids.map(x=>x.txt.length),[7,32]);assert.deepEqual(initial.ids.map(x=>x.imgs.length),[7,30]);
  assert.ok(initial.ids[1].imgs.every(id=>initial.ids[1].txt.includes(id)));
  assert.equal(initial.compact,compact);
  assert.ok(Math.abs(initial.footer-h)<15);
  assert.equal(initial.nextDisabled,false);
  if(compact){
   assert.deepEqual(initial.ids[0].presentations.map(x=>x.hidden),[false,true]);
   await p.locator('.reader-collection-page[data-collection=essays] .reader-presentation-button[data-presentation=images]').click();
   await p.waitForTimeout(50);
   const on=await p.locator('.reader-collection-page[data-collection=essays]').evaluate(e=>[e.dataset.presentation,[...e.querySelectorAll('.reader-shelf-panel')].map(x=>x.hidden)]);
   assert.deepEqual(on,['images',[true,false]]);
  } else {
   assert.deepEqual(initial.ids[0].presentations.map(x=>x.hidden),[false,false]);
  }
  // One explicit collection step advances the pair; not a half-page.
  await p.locator('#next-page').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport').dataset.collection==='first-readings');
  await p.waitForTimeout(390);
  const target=await p.evaluate(()=>{
    const track=document.querySelector('.reader-scroll-region'),book=document.querySelector('.reader-collection-page[data-collection=first-readings]');
    return {index:document.querySelector('#page-viewport').dataset.collection,left:book.getBoundingClientRect().left-track.getBoundingClientRect().left,
       nextDisabled:document.querySelector('#next-page').disabled};
  });
  assert.ok(Math.abs(target.left)<15,JSON.stringify(target));assert.equal(target.nextDisabled,true);
  const first=p.locator('.reader-collection-page[data-collection=first-readings]');
  const textItems=first.locator('.reader-shelf-contents-entry');
  const imageItems=first.locator('.reader-gallery-item');
  assert.equal(await textItems.count(),32);assert.equal(await imageItems.count(),30);
  if(compact){
   await first.locator('.reader-presentation-button[data-presentation=images]').click();
  }
  // Focus on text and gallery must share selection without navigation.
  if(compact)await first.locator('.reader-presentation-button[data-presentation=contents]').click();
  const chosen=textItems.nth(7);
  const id=await chosen.getAttribute('data-work-id');
  await chosen.focus();await p.waitForTimeout(90);
  let marked=await first.locator('[aria-current=true]').evaluateAll(nodes=>nodes.map(n=>n.dataset.workId));
  assert.ok(marked.length>=2 && marked.every(x=>x===id),JSON.stringify(marked));
  assert.equal(await p.locator('#page-viewport').getAttribute('data-volume'),'library');
  // Keyboard ArrowDown changes selected item but does not open it.
  await chosen.press('ArrowDown');
  await p.waitForTimeout(80);
  const id2=await textItems.nth(8).getAttribute('data-work-id');
  marked=await first.locator('[aria-current=true]').evaluateAll(nodes=>nodes.map(n=>n.dataset.workId));
  assert.deepEqual(marked,[id2,id2]); // one index, one gallery
  assert.equal(await p.locator('#page-viewport').getAttribute('data-volume'),'library');
  const list=first.locator('.reader-collection-scroll'),gallery=first.locator('.reader-gallery-scroll');
  // Position memory including compact presentation on return.
  await list.evaluate(e=>e.scrollTop=350);await gallery.evaluate(e=>e.scrollTop=475);
  await p.waitForTimeout(160);
  if(compact)await first.locator('.reader-presentation-button[data-presentation=images]').click();
  const expectedWork=await imageItems.nth(9).getAttribute('data-work-id');
  await p.evaluate(()=>document.addEventListener('click',event=>{
    if(event.target.closest('.reader-gallery-item'))window.__afterReaderAction=event.target.closest('.reader-gallery-scroll').scrollTop;
  },{once:true}));
  await imageItems.nth(9).evaluate(e=>e.addEventListener('click',()=>{
   window.__collectionAtClick={x:e.closest('.reader-scroll-region').scrollLeft,y:e.closest('.reader-gallery-scroll').scrollTop}
  },{capture:true,once:true}));
  await imageItems.nth(9).click();
  const pos=await p.evaluate(()=>({x:window.__collectionAtClick.x,y:window.__afterReaderAction}));
  await ready(p,expectedWork);
  const openedVol=await p.locator('#page-viewport').getAttribute('data-volume');
  assert.ok(openedVol.startsWith('solstice-reading-01--'),openedVol);
  assert.equal(await p.locator('#reader-parent').getAttribute('data-reader-target'),'library');
  await p.locator('#reader-parent').click();await ready(p,'library');await p.waitForTimeout(260);
  const restored=await p.evaluate(()=>{
    const c=document.querySelector('.reader-collection-page[data-collection=first-readings]');
    return {index:document.querySelector('#page-viewport').dataset.collection,
     x:document.querySelector('.reader-scroll-region').scrollLeft,
     y:c.querySelector('.reader-gallery-scroll').scrollTop,
     selection:[...c.querySelectorAll('[aria-current=true]')].map(e=>e.dataset.workId),
     presentation:c.dataset.presentation,
     footer:document.querySelector('.frame-controls').getBoundingClientRect().bottom};
  });
  assert.equal(restored.index,'first-readings');
  assert.ok(Math.abs(restored.x-pos.x)<22,JSON.stringify({restored,pos}));
  console.log('RESTORE',label,JSON.stringify({restored,pos}));
  assert.ok(Math.abs(restored.y-pos.y)<23,JSON.stringify({restored,pos}));
  assert.ok(restored.selection.length>=2&&restored.selection.every(x=>x===openedVol),JSON.stringify(restored));
  if(compact)assert.equal(restored.presentation,'images');
  assert.ok(Math.abs(restored.footer-h)<15);
  assert.deepEqual(errors,[]);
  await p.screenshot({path:path.join(__dirname,'one-collection-'+label+'.png')});
  runs.push({label,initial,target,opened:openedVol,restored,errors});console.log('PASS',label,JSON.stringify({units:initial.n,index:restored.index,selected:restored.selection.length,presentation:restored.presentation}));
  await c.close();
 }
 await b.close();
 fs.writeFileSync(path.join(__dirname,process.env.LIVE?'collection-identity-live.json':'collection-identity-preflight.json'),JSON.stringify({origin:BASE,intercepted:!process.env.LIVE,runs,failures:0},null,2)+'\n');
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
