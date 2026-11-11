import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');

const root=process.env.ORANGE_PUBLIC_CANDIDATE_URL||'http://127.0.0.1:8840';
const browser=await webkit.launch({headless:true});
const results=[];
try{
 for(const view of [
  {name:'ipad-portrait',width:820,height:1180},
  {name:'ipad-landscape',width:1180,height:820},
  {name:'phone',width:390,height:844},
 ]){
  const context=await browser.newContext({viewport:view,hasTouch:true,isMobile:true});
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/estate/#/read/library',{waitUntil:'domcontentloaded',timeout:35000});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='library',{timeout:20000});
  const shelf=await page.evaluate(()=>[...document.querySelectorAll('.reader-collection-page')].map(p=>({
   id:p.dataset.collection,
   entries:p.querySelectorAll('.reader-collection-scroll [data-work-id]').length,
   images:p.querySelectorAll('.reader-gallery-scroll [data-work-id]').length
  })));
  const expected=[
    {id:'essays',entries:7,images:7},
    {id:'first-readings',entries:32,images:30},
    {id:'orange-dot',entries:23,images:23},
  ];
  if(JSON.stringify(shelf)!==JSON.stringify(expected))
    throw Error(view.name+' public-first bookshelf mismatch '+JSON.stringify(shelf));
  const original=[
    'essay--client-centered',
    'solstice-reading-01--2026-01-23-i-keep-moving',
    'orange-dot--2026-01-22-the-vigilance-regulator'
  ];
  let opened=[];
  for(const id of original){
    await page.evaluate(id=>{
      const selector=document.getElementById('reader-section');
      if(![...selector.options].some(o=>o.value===id)) throw Error('Missing Reader work '+id);
      selector.value=id;
      selector.dispatchEvent(new Event('change',{bubbles:true}));
    },id);
    await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id&&document.querySelector('#page-viewport')?.dataset.layout==='ready'&&Number(document.querySelector('#page-viewport')?.dataset.pages)>0,id,{timeout:30000});
    const composed=await page.evaluate(()=>({
      pages:Number(document.querySelector('#page-viewport').dataset.pages),
      heading:document.querySelector('#source-flow h2')?.textContent,
      images:document.querySelectorAll('#source-flow img').length,
      overflow:document.documentElement.scrollWidth-innerWidth
    }));
    if(!(composed.pages>=1)||composed.overflow>3||!composed.heading)throw Error(view.name+' broke preserved work '+id+' '+JSON.stringify(composed));
    if(id.includes('vigilance-regulator') && view.name==='ipad-portrait' && composed.pages!==4)
      throw Error('Orange Dot portrait figure was not compacted '+JSON.stringify(composed));
    opened.push([id,composed]);
  }
  if(errors.length)throw Error(view.name+' JS errors '+errors.join(';'));
  results.push({viewport:view.name,collections:shelf,opened,errors});
  console.log('PASS PUBLIC-BASELINE REVIEW CANDIDATE',view.name,JSON.stringify(shelf));
  await context.close();
 }
 console.log('PASS_PUBLIC_BASELINE_ORANGE_DOT_READER_PREFLIGHT',results.length,'responsive viewports, both published neighbor collections intact and Orange Dot measured');
}catch(e){
 console.error('FAILED PUBLIC-BASELINE CANDIDATE',e.stack||e);
 process.exitCode=1;
}finally{await browser.close()}
