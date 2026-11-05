#!/usr/bin/env node
// Exercise the formerly-broken branch: the first specimen cannot entirely
// fit after the intro, but a meaningful measured fragment CAN share the leaf.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {webkit,chromium}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const source=fs.readFileSync(path.join(__dirname,'../../site/essays/what-makes-a-page-modern/specimen-source.txt'),'utf8').trimEnd();
(async()=>{
 for(const [name,driver]of[['webkit',webkit],['chromium',chromium]]){
  const b=await driver.launch(name==='chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
  const context=await b.newContext({viewport:{width:390,height:690},ignoreHTTPSErrors:true});
  for(const [asset,mime]of[['reading-first-press-engine.js','text/javascript'],['reading-first-press-frame.css','text/css']]){
    await context.route('**/estate/assets/linotype/'+asset,route=>route.fulfill({status:200,body:fs.readFileSync(path.join(__dirname,asset)),contentType:mime}));
  }
  const page=await context.newPage(),parts=[];
  try{
   await page.goto('https://192.168.8.50:8243/estate/#/read/essay--what-makes-a-page-modern');
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000});
   const total=Number(await page.locator('#page-viewport').getAttribute('data-pages'));
   assert.ok(total>10);
   for(let i=1;i<=total;i++){
    const found=await page.evaluate(()=>{
      const a=document.querySelector('#page-viewport .linotype-area');
      return [...a.querySelectorAll('figure[data-typographic-specimen="classical"]')].map(f=>{
       const p=f.querySelector('.linotype-specimen-text');
       const a=f.closest('.linotype-area'),r=f.getBoundingClientRect();
       return {from:Number(p.dataset.sourceFrom),to:Number(p.dataset.sourceTo),
         text:p.textContent,previous:f.previousElementSibling?.tagName,
         areaBottom:a.getBoundingClientRect().bottom,frameBottom:r.bottom};
      });
    });
    for(const f of found){
      parts.push({...f,leaf:i});
      if(parts.length<=2)await page.screenshot({path:'/tmp/fluid-REAL-CONTINUATION-'+name+'-'+i+'.png'});
    }
    if(parts.length&&parts.at(-1).to===source.length)break;
    if(i<total)await page.locator('#next-page').click();
   }
   assert.ok(parts.length>=2,'expected genuine continuation');
   assert.equal(parts[0].from,0);
   assert.equal(parts[0].previous,'P','first prefix should share the folio with its prose');
   for(let n=1;n<parts.length;n++)assert.equal(parts[n].from,parts[n-1].to,'lost paragraph address');
   assert.equal(parts.at(-1).to,source.length);
   assert.equal(parts.map(x=>x.text).join(''),source);
   for(const f of parts)assert.ok(f.frameBottom<=f.areaBottom+1.5,'clipped fragment');
   console.log('FLUID_CONTINUATION_PASS',name,'pages',total,JSON.stringify(parts.map(({leaf,from,to,previous})=>({leaf,from,to,previous}))));
  }finally{await context.close();await b.close()}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
