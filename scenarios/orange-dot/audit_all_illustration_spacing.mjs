import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const root='/Users/benedikteickhoff/Developer/.orange-dot-reader-20261110/scenarios/orange-dot';
const selection=JSON.parse(fs.readFileSync(root+'/selection.json','utf8'));
const multi=selection.entries.filter(x=>x.images.length>1);
const base=process.env.ORANGE_PUBLIC_CANDIDATE_URL||'http://127.0.0.1:8840';
const engine=process.env.ORANGE_OLD_ENGINE||null;
const b=await webkit.launch({headless:true});
const results=[];
try{
for(const vp of [{name:'portrait',width:820,height:1180},{name:'landscape',width:1180,height:820},{name:'phone',width:390,height:844}]){
  const p=await b.newPage({viewport:{width:vp.width,height:vp.height},isMobile:vp.name!=='landscape',hasTouch:true});
  let injected=0;const errors=[];
  p.on('pageerror',e=>errors.push(e.message));
  if(engine)await p.route('**/reading-first-press-engine.*.js',r=>{injected++;return r.fulfill({status:200,contentType:'text/javascript',body:fs.readFileSync(engine)})});
  for(const work of multi){
    await p.goto(base+'/estate/#/read/'+work.id,{waitUntil:'domcontentloaded',timeout:45000});
    await p.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id,work.id,{timeout:45000});
    const n=Number(await p.locator('#page-viewport').getAttribute('data-pages'));
    let figures=[],gaps=[],pagesSeen=new Set();
    for(let turn=0;turn<n+1;turn++){
      if(await p.locator('#page-viewport').getAttribute('data-volume')!==work.id)break;
      const shown=await p.locator('#page-count').innerText();
      if(pagesSeen.has(shown))break;
      pagesSeen.add(shown);
      const infos=await p.evaluate(()=>[...document.querySelectorAll('#page-viewport .linotype-sheet')].map(sheet=>{
        const area=sheet.querySelector('.linotype-area');
        if(!area)return {images:[],gap:null};
        const rect=area.getBoundingClientRect(),nodes=[...area.children];
        const images=nodes.filter(x=>x.matches('figure.linotype-inline-illustration')).map(x=>{
          const j=nodes.indexOf(x),r=x.getBoundingClientRect(),prev=nodes[j-1],next=nodes[j+1];
          const b=x.querySelector('img')?.getBoundingClientRect();
          return {image:x.getAttribute('data-source-block'),top:r.top,bottom:r.bottom,height:r.height,
             width:b?.width,imageHeight:b?.height,caption:!!x.querySelector('figcaption'),
             gapBefore:prev?r.top-prev.getBoundingClientRect().bottom:null,
             gapAfter:next?next.getBoundingClientRect().top-r.bottom:null,
             previous:prev?.tagName,following:next?.tagName};
        });
        const last=nodes.at(-1);
        return {images,gap:last?rect.bottom-last.getBoundingClientRect().bottom:rect.height,
          hasProse:nodes.some(e=>e.tagName==='P'),leafHeight:rect.height,page:sheet.getAttribute('aria-label')};
      }));
      for(const info of infos){
        for(const x of info.images){if(!figures.some(f=>f.image===x.image))figures.push({...x,page:info.page});}
        if(info.gap>180&&info.hasProse)gaps.push({page:info.page,gap:Math.round(info.gap),imagePage:info.images.length>0});
      }
      if(await p.locator('#next-page').isDisabled())break;
      await p.locator('#next-page').click();await p.waitForTimeout(80);
    }
    if(figures.length!==work.images.length-1)throw Error('Lost inline image '+vp.name+' '+work.title+' got '+figures.length+' on '+n+' leaves '+JSON.stringify({figures,gaps}));
    if(figures.some(x=>x.gapBefore>60||x.gapAfter>60||!x.caption))throw Error('Measured image gap/caption '+JSON.stringify({work:work.title,figures}));
    results.push({viewport:vp.name,work:work.title,pages:n,figures:figures.map(x=>({page:x.page,top:Math.round(x.top),height:Math.round(x.height),gapBefore:Math.round(x.gapBefore??-1),gapAfter:Math.round(x.gapAfter??-1)})),largeTextLeafGaps:gaps});
  }
  if(errors.length)throw Error('Runtime errors '+vp.name+JSON.stringify(errors));
  await p.close();
}
console.log('ORANGE_MULTI_IMAGE_LAYOUT_AUDIT_PASS',JSON.stringify(results,null,2));
}catch(e){console.error('ORANGE_MULTI_IMAGE_LAYOUT_AUDIT_FAILED',e.stack||e);process.exitCode=1}
finally{await b.close()}
