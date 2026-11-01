const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert').strict;
const inv=JSON.parse(fs.readFileSync(path.join(__dirname,'solstice-source-inventory.json'),'utf8')).inventory;
const works=inv.filter(x=>x.kind==='work');
const assets={'/estate/':'index.html','/estate/assets/linotype/reading-first-app.js':'reading-first-app.js',
 '/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css',
 '/estate/assets/linotype/reading-first-press-engine.js':'press-viewport-engine.js'};
const profiles=[['landscape',1180,820],['portrait',820,1180],['phone',390,844]];
(async()=>{
const browser=await webkit.launch({headless:true});
const results=[],faults=[];
for(const [name,width,height] of profiles){
 const ctx=await browser.newContext({viewport:{width,height}});
 if(!process.env.LIVE)await ctx.route('**/*',route=>{
  const u=new URL(route.request().url()),file=assets[u.pathname];
  return file&&u.host==='192.168.8.50:8243'?route.fulfill({status:200,body:fs.readFileSync(path.join(__dirname,file)),contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html'}):route.continue();
 });
 const p=await ctx.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await p.goto('https://192.168.8.50:8243/estate/#/read/first-readings',{waitUntil:'domcontentloaded'});
 await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000});
 for(const [i,entry] of works.entries()){
  await p.locator('#reader-section').selectOption(entry.id);
  let ok=true;
  try{await p.waitForFunction(id=>document.querySelector('#page-viewport').dataset.volume===id&&document.querySelector('#page-viewport').dataset.layout==='ready',entry.id,{timeout:10000})}
  catch(err){ok=false}
  const observed=await p.evaluate(()=>{
    const v=document.querySelector('#page-viewport'),src=document.querySelector('#source-flow');
    const original=[...src.querySelectorAll('figure.teatro-score img')].map(i=>({w:+i.getAttribute('width'),h:+i.getAttribute('height'),url:i.getAttribute('src')}));
    const scores=[...v.querySelectorAll('figure.teatro-score img')].map(i=>({w:+i.getAttribute('width'),h:+i.getAttribute('height'),url:i.getAttribute('src'),loaded:i.naturalWidth>0}));
    const visible=[...v.querySelectorAll('figure.teatro-score img')].map(i=>{
       const r=i.getBoundingClientRect(),a=i.closest('.linotype-area').getBoundingClientRect();
       return {w:r.width,h:r.height,within:r.right<=a.right+2&&r.bottom<=a.bottom+2&&r.left>=a.left-2,visible:r.width>0&&r.height>0};
    }).filter(x=>x.visible);
    return{layout:v.dataset.layout,volume:v.dataset.volume,sourceImages:original,renderImages:scores,visible,pages:+v.dataset.pages||0,sourceText:src.querySelector('.book-prose')?.textContent?.length||0};
  });
  const bad=[];
  if(!ok||observed.layout!=='ready')bad.push('composition failed');
  // The active reader mounts only the currently displayed one/two folios;
  // the paginator has already verified the full source-block image inventory.
  if(observed.sourceImages.length!==entry.images||observed.renderImages.length>entry.images)bad.push('image inventory mismatch '+observed.sourceImages.length+'/'+observed.renderImages.length+'/'+entry.images);
  if(observed.renderImages.some(img=>!img.loaded))bad.push('image decode');
  if(observed.visible.some(x=>!x.within))bad.push('score cropped');
  if(observed.visible.some(x=>x.w<100||x.h<100))bad.push('thumbnail');
  if(errors.length)bad.push('pageerror '+errors.splice(0).slice(0,2).join('; '));
  if(bad.length)faults.push({profile:name,id:entry.id,bad,observed});
  results.push({profile:name,id:entry.id,images:observed.renderImages.length,pages:observed.pages,visible:observed.visible,ok:bad.length===0});
  if(i%6===5||bad.length)console.log('PROGRESS',name,i+1,'of',works.length,'faults',faults.length,bad.join(' '));
  if(bad.length)break;
 }
 await ctx.close();
 if(faults.length)break;
}
await browser.close();
const receipt={sourceEdition:'Fountain-Coach/solstice.fountain.coach Reading 01',profiles:profiles.map(p=>p[0]),workLayouts:results.length,totalImagePlacements:results.reduce((n,r)=>n+r.images,0),failures:faults,results};
fs.writeFileSync(path.join(__dirname,process.env.LIVE?'fcis-score-corpus-live.json':'fcis-score-corpus-preflight.json'),JSON.stringify(receipt,null,2)+'\n');
console.log('SUMMARY',JSON.stringify({workLayouts:results.length,imagePlacements:receipt.totalImagePlacements,failures:faults.length}));
if(faults.length)process.exitCode=2;
})().catch(e=>{console.error('FAILED',e.stack);process.exitCode=2});
