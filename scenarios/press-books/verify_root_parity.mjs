import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const base=process.env.PRESS_PARITY_URL||'http://127.0.0.1:8845';
function assert(x,msg){if(!x)throw Error(msg);}
const browser=await webkit.launch({headless:true});
try{
 for(const v of [
  {name:'ipad-portrait',width:820,height:1180},
  {name:'ipad-landscape',width:1180,height:820},
  {name:'phone',width:390,height:844},
 ]){
  const context=await browser.newContext({viewport:{width:v.width,height:v.height},isMobile:true,hasTouch:true});
  const snapshots=[];
  for(const route of ['/','/estate/']){
   const page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   const response=await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:45000});
   assert(response.status()===200,'No root page '+base+route);
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='library',{timeout:30000});
   const state=await page.evaluate(()=>({
    books:[...document.querySelectorAll('.reader-collection-page')].map(p=>({
     id:p.dataset.collection,
     chapters:p.querySelectorAll('.reader-collection-scroll [data-work-id]').length,
     images:p.querySelectorAll('.reader-gallery-scroll [data-work-id]').length,
     bookDirect:p.querySelector('.reader-book-direct-link')?.getAttribute('href')
    })),
    title:document.title,
    ogImage:document.querySelector('meta[property="og:image"]')?.getAttribute('content'),
    render:document.querySelector('#page-viewport')?.dataset.layout,
    body:document.body.dataset.initialVolume
   }));
   const expected=[
    {id:'essays',chapters:7,images:7,bookDirect:'/estate/books/essays/'},
    {id:'first-readings',chapters:32,images:30,bookDirect:'/estate/books/first-readings/'},
    {id:'orange-dot',chapters:23,images:23,bookDirect:'/estate/books/orange-dot/'}
   ];
   assert(JSON.stringify(state.books)===JSON.stringify(expected),'Source Bookshelf mismatch '+route+' '+JSON.stringify(state.books));
   assert(state.body==='library','Wrong opening book '+route);
   assert(!errors.length,'Root page errors '+route+' '+errors.join(';'));
   const open=await page.locator('.reader-collection-page[data-collection="orange-dot"] .reader-contents-entry').first();
   await open.click();
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='orange-dot--2025-12-21-solstice'&&Number(document.querySelector('#page-viewport')?.dataset.pages)>0,{timeout:30000});
   const paged=await page.evaluate(()=>({volume:document.querySelector('#page-viewport').dataset.volume,pages:Number(document.querySelector('#page-viewport').dataset.pages),width:document.documentElement.scrollWidth}));
   assert(paged.width<=v.width+3,'Root page horizontal overflow '+route);
   assert(!errors.length,'Root chapter JS exception '+route+' '+errors.join(';'));
   snapshots.push({route,state,paged});
   await page.close();
  }
  assert(JSON.stringify(snapshots[0].state)===JSON.stringify(snapshots[1].state),'Root and estate differ '+v.name);
  console.log('FOUNTAIN_PRESS_ROOT_PARITY_PASS',v.name,snapshots.map(x=>[x.route,x.paged.volume,x.paged.pages]));
  await context.close();
 }
 console.log('PUBLIC_ROOT_PARITY_ACCEPTED 2 exact routes, 3 viewports, 23+29 Orange Dot and existing Bookshelf intact');
}catch(e){console.error('ROOT_PARITY_FAILED',e.stack||e);process.exitCode=1}
finally{await browser.close();}
