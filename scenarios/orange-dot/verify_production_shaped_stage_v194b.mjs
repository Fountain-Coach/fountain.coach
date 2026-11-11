import {createRequire} from 'node:module';
import fs from 'node:fs';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const expected=['essays','first-readings','orange-dot'];
const baseline='https://fountain.coach/estate/';
const candidate=process.env.BOOKSHELF_BASE||'http://127.0.0.1:8835/estate/';
const b=await webkit.launch({headless:true});
let failures=[];
try {
 for(const vp of [{name:'ipad-portrait',width:820,height:1180},{name:'ipad-landscape',width:1180,height:820},{name:'phone',width:390,height:844}]){
  const p=await b.newPage({viewport:{width:vp.width,height:vp.height},isMobile:true,hasTouch:true,ignoreHTTPSErrors:true});
  const errors=[];
  p.on('pageerror',e=>errors.push(e.message));
  const res=await p.goto(candidate,{waitUntil:'domcontentloaded',timeout:50000});
  if(res.status()!==200)throw Error('Candidate Bookshelf HTTP '+res.status());
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:45000});
  const data=await p.evaluate(()=>{
    const html=document.documentElement;
    const galleries=JSON.parse(document.getElementById('reader-gallery-data').textContent);
    const templates=[...document.querySelectorAll('template[data-reader-volume]')].map(x=>x.dataset.readerVolume);
    const headings=[...document.querySelectorAll('h1,h2,h3')].filter(x=>x.getBoundingClientRect().width).map(x=>x.textContent.trim()).slice(0,12);
    const nav=[...document.querySelectorAll('option')].map(x=>x.value);
    return {
      headings,collections:Object.keys(galleries.collections),
      orange:templates.filter(k=>k.startsWith('orange-dot--')).length,
      works:templates.filter(k=>k==='works'||k==='scores'||k.startsWith('score--')).length,
      governance:templates.filter(k=>k==='governance'||k.startsWith('governance--')).length,
      governanceChapterReferences:(document.documentElement.outerHTML.match(/https:\/\/governance\.fountain\.coach\/chapters\//g)||[]).length,
      prohibitedOptions:nav.filter(k=>k==='governance'||k==='scores'||k==='works'||k.startsWith('score--')||k.startsWith('governance--')),
      layout:document.querySelector('#page-viewport')?.dataset.layout,
      overflow:html.scrollWidth>innerWidth+2,
    };
  });
  if(JSON.stringify(data.collections)!==JSON.stringify(expected))throw Error('Wrong collections '+JSON.stringify(data));
  if(data.orange!==23||data.governance||data.works||data.prohibitedOptions.length||data.overflow)throw Error('Invalid shelf '+JSON.stringify(data));
  if(data.governanceChapterReferences<10)throw Error('Semantic chapter references were removed');
  if(!data.headings.includes('Bookshelf'))throw Error('Staging does not open on Bookshelf');
  if(errors.length)throw Error('Page errors: '+errors.join(';'));
  await p.screenshot({path:'/tmp/orange-v194-'+vp.name+'.png'});
  console.log('PRODUCTION_SHAPED_STAGE_BOOKSHELF_PASS',vp.name,JSON.stringify(data));
  await p.close();
 }
}finally {await b.close();}
