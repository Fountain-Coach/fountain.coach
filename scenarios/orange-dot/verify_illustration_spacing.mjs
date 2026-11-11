import fs from "node:fs";
import path from "node:path";
import {createRequire} from "node:module";
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const dir=path.dirname(new URL(import.meta.url).pathname);
const selection=JSON.parse(fs.readFileSync(path.join(dir,'selection.json'),'utf8'));
const names=selection.entries;
const base=process.env.ORANGE_BASE||'https://192.168.8.50:8243';
const patched=process.env.ORANGE_ENGINE||'';
const browser=await webkit.launch({headless:true});
let issues=[],results=[];
try {
 for(const vp of [{name:'ipad-portrait',width:820,height:1180},{name:'ipad-landscape',width:1180,height:820},{name:'phone',width:390,height:844}]){
  const page=await browser.newPage({viewport:{width:vp.width,height:vp.height},isMobile:vp.name!=='ipad-landscape',hasTouch:true,ignoreHTTPSErrors:true});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  let intercepted=0;
  if(patched)await page.route('**/reading-first-press-engine.js',route=>{
    intercepted++;return route.fulfill({status:200,contentType:'text/javascript',body:fs.readFileSync(patched)});
  });
  const target=names.find(e=>e.title==='The Vigilance Regulator');
  const url=base+'/estate/#/read/'+target.id;
  const res=await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
  if(res.status()!==200)throw Error('Page HTTP '+res.status());
  await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id,target.id,{timeout:45000});
  const initialCount=Number(await page.locator('#page-viewport').getAttribute('data-pages'));
  if(vp.name==='ipad-portrait'){
    if(initialCount!==4)throw Error('Vigilance expected 4 portrait leaves, got '+initialCount);
    await page.locator('#next-page').click();
    await page.locator('#next-page').click();
    const f=await page.evaluate(()=>{
      const area=document.querySelector('#page-viewport .linotype-area');
      const fig=area.querySelector('figure.linotype-inline-illustration');
      const preceding=fig?.previousElementSibling;
      const following=fig?.nextElementSibling;
      const c=fig?.getBoundingClientRect(),a=area.getBoundingClientRect();
      return {present:!!fig,preceding:preceding?.tagName,following:following?.tagName,
        top:c?.top,bottom:c?.bottom,spaceBefore:c&&preceding?c.top-preceding.getBoundingClientRect().bottom:null,
        spaceAfter:c&&following?following.getBoundingClientRect().top-c.bottom:null,
        remaining:a.bottom-(following?.getBoundingClientRect().bottom||c?.bottom||a.top)};
    });
    if(!f.present||f.preceding!=='P'||f.following!=='P'||f.spaceBefore>26||f.spaceAfter>26)
      throw Error('Measured figure placement '+JSON.stringify(f));
    results.push({viewport:vp.name,vigilanceLeaves:initialCount,measuredFigure:f});
  } else results.push({viewport:vp.name,vigilanceLeaves:initialCount});
  let n=0,imgs=0;
  for(const e of names){
    await page.evaluate(id=>{
      const x=document.querySelector('#reader-section');
      x.value=id;x.dispatchEvent(new Event('change',{bubbles:true}));
    },e.id);
    await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id&&Number(document.querySelector('#page-viewport')?.dataset.pages)>0,e.id,{timeout:45000});
    await page.waitForFunction(()=>[...document.querySelectorAll('#source-flow img')].every(im=>im.complete&&im.naturalWidth>0),null,{timeout:20000});
    const info=await page.evaluate(id=>{
      const a=document.querySelector('#source-flow'),v=document.querySelector('#page-viewport');
      const blocks=[...a.querySelectorAll('p[data-source-block^="'+id+'.text."]')];
      const images=[...a.querySelectorAll('img')];
      return {n:blocks.length,images:images.length,
        loaded:images.every(x=>x.complete&&x.naturalWidth>0),
        pageCount:Number(v.dataset.pages),
        outerWidth:document.documentElement.scrollWidth,innerWidth:innerWidth};
    },e.id);
    if(info.n<1||info.images!==e.images.length||!info.loaded||info.outerWidth>info.innerWidth+3)
      throw Error('Folio regression '+vp.name+' '+e.title+' '+JSON.stringify(info));
    n++;imgs+=info.images;
  }
  if(errors.length)throw Error('Browser JS '+JSON.stringify(errors));
  if(patched&&intercepted!==1)throw Error('Unexpected patched engine interception '+intercepted);
  results.at(-1).works=n;results.at(-1).images=imgs;results.at(-1).errors=errors.length;
  console.log('ORANGE_SPACING_ACCEPTED',JSON.stringify(results.at(-1)));
  await page.close();
 }
 console.log('ORANGE_SPACING_ALL_PASSED',JSON.stringify(results));
}catch(e){issues.push(e.stack||String(e)); console.error('ORANGE_SPACING_FAILED',issues.join('\n'));process.exitCode=1}
finally{await browser.close()}
