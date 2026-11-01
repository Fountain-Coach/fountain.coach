const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'solstice-source-inventory.json'),'utf8'));
const ids=manifest.inventory.filter(x=>x.kind==='work').map(x=>x.id);
(async()=>{
 const browser=await webkit.launch({headless:true});
 const records=[];
 for(const [profile,width,height] of [['landscape',1180,820],['phone',390,844]]){
  const page=await browser.newPage({viewport:{width,height}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('https://192.168.8.50:8243/estate/#/read/solstice-reading-01',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
  for(const id of ids){
   await page.getByLabel('Choose publication').selectOption(id);
   await page.waitForFunction(name=>document.querySelector('#page-viewport')?.dataset.volume===name&&document.querySelector('#page-viewport')?.dataset.layout==='ready',id,{timeout:14000});
   const result=await page.evaluate(async()=>{
    const expected=new Map([...document.querySelectorAll('#source-flow [data-source-block]')].map(n=>[n.dataset.sourceBlock,n.textContent]));
    const read=new Map(),faults=[],seen=new Set(),imgs=new Set();
    let folios=0,step=0;
    while(step++<80){
     const page=document.querySelector('#page-count').textContent;
     if(seen.has(page)){faults.push('cycle '+page);break;}seen.add(page);
     const vp=document.querySelector('#page-viewport');
     for(const area of vp.querySelectorAll('.linotype-area')){
      folios++;
      for(const image of area.querySelectorAll('img')){
       try{if(!image.complete||!image.naturalWidth)await image.decode();}catch(e){faults.push('decode '+image.src)}
       imgs.add(image.getAttribute('src'));
       if(!image.naturalWidth)faults.push('image absent '+image.getAttribute('src'));
      }
      const rect=area.getBoundingClientRect();
      if(area.scrollHeight>area.clientHeight+2)faults.push('overflow scroll '+page);
      for(const el of area.querySelectorAll('p,figure,img,figcaption,h2')){
       const r=el.getBoundingClientRect();
       if(r.bottom>rect.bottom+1.4||r.right>rect.right+1.4)faults.push('clip '+page+' '+el.tagName);
      }
      for(const el of area.querySelectorAll('[data-source-block]')){
       read.set(el.dataset.sourceBlock,(read.get(el.dataset.sourceBlock)||'')+el.textContent);
      }
     }
     if(document.getElementById('next-page').disabled)break;
     document.getElementById('next-page').click();
    }
    for(const [id,txt] of expected)if(read.get(id)!==txt)faults.push('text '+id);
    return {folios,images:imgs.size,sourceBlocks:expected.size,faults};
   });
   const original=manifest.inventory.find(x=>x.id===id);
   if(result.images!==original.images)result.faults.push('original image count '+result.images+' / '+original.images);
   if(errors.length)result.faults.push(...errors.splice(0));
   records.push({profile,id,...result});
   if(result.faults.length)console.log('FAIL',profile,id,result.faults.slice(0,8));
  }
  console.log('PROFILE',profile,'checked',ids.length,'works');
  await page.close();
 }
 await browser.close();
 const summary={sourceEdition:'Fountain-Coach/solstice.fountain.coach first-reading',profileRuns:records.length,folios:records.reduce((n,r)=>n+r.folios,0),artworks:records.reduce((n,r)=>n+r.images,0),failures:records.filter(x=>x.faults.length),records};
 fs.writeFileSync(path.join(__dirname,'solstice-corpus-audit.json'),JSON.stringify(summary,null,2)+'\n');
 console.log('TOTAL',JSON.stringify({profileRuns:summary.profileRuns,folios:summary.folios,artworks:summary.artworks,fails:summary.failures.length}));
 if(summary.failures.length)process.exitCode=2;
})().catch(e=>{console.error(e.stack);process.exitCode=1});
