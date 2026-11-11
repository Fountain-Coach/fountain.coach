import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const browser=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--ignore-certificate-errors','--no-sandbox']});
const checks=[];
try{
 for(const [name,w,h] of [['portrait',820,1180],['landscape',1180,820],['phone',390,844]]){
  const page=await browser.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.setViewport({width:w,height:h,isMobile:name!=='landscape',hasTouch:true});
  await page.goto('https://192.168.8.50:8243/estate/#/read/library',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000});
  const actual=await page.evaluate(()=>{
   return [...document.querySelectorAll('.reader-collection-page')].map(p=>({
    id:p.dataset.collection,contents:p.querySelectorAll('.reader-collection-scroll [data-work-id]').length,
    images:p.querySelectorAll('.reader-gallery-scroll [data-work-id]').length
   }));
  });
  const expected=[['essays',7,6],['scores',3,3],['first-readings',32,30],['orange-dot',23,23],['governance',160,1]];
  for(let i=0;i<expected.length;i++){
   let [id,contents,images]=expected[i];
   if(actual[i]?.id!==id||actual[i]?.contents!==contents||actual[i]?.images!==images)
    throw Error('Collection regression '+name+': '+JSON.stringify(actual));
  }
  // Active v192b predecessor: Essays and Scores expanded since the original v185 fixture.
  // Test three independently published neighbors and the new collection route.
  for(const id of ['essay--what-makes-a-page-modern','score--between-gardens','solstice-reading-01--2026-01-23-i-keep-moving','orange-dot--2026-09-17-bee-the-interval','governance--00-abstract']){
   console.log('CHECKING',name,id); if(id.startsWith('governance--'))await page.goto('https://192.168.8.50:8243/estate/#/read/'+id,{waitUntil:'domcontentloaded'}); else await page.evaluate(id=>{let s=document.querySelector('#reader-section');s.value=id;s.dispatchEvent(new Event('change',{bubbles:true}));},id);
   try{await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id&&document.querySelector('#page-viewport')?.dataset.layout==='ready'&&Number(document.querySelector('#page-viewport')?.dataset.pages)>0,{timeout:30000},id);}catch(err){console.log('STATE',await page.evaluate(()=>({volume:document.querySelector('#page-viewport')?.dataset.volume,layout:document.querySelector('#page-viewport')?.dataset.layout,pages:document.querySelector('#page-viewport')?.dataset.pages,errors:document.querySelector('#reader-status')?.textContent,menu:document.querySelector('#reader-section')?.value})));throw err;}
   const title=await page.evaluate(()=>document.querySelector('#source-flow h2')?.textContent.trim());
   if(!title)throw Error('Missing preserved reader '+id);
   checks.push([name,id,title]);
  }
  // The new collection direct URL must resolve, not merely an entry in a list.
  await page.goto('https://192.168.8.50:8243/estate/#/read/orange-dot',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='orange-dot'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
  if(errors.length)throw Error('Runtime errors '+JSON.stringify(errors));
  await page.close();
 }
 console.log('ORANGE_DOT_V185_NEIGHBOR_REGRESSION_PASS',checks.length,'works',checks.map(x=>x[1]).join(','));
}catch(e){console.error('ORANGE_DOT_V185_NEIGHBOR_REGRESSION_FAILED',e.stack||String(e));process.exitCode=1}finally{await browser.close();}
