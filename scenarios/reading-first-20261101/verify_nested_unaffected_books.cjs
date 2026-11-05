#!/usr/bin/env node
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium,webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const origin='https://192.168.8.50:8243',root=__dirname;
const assets=[
 ['**/estate/','stage-v149-semantic-type.html','text/html'],
 ['**/estate/assets/linotype/reading-first-press-engine.js','reading-first-press-engine.js','text/javascript'],
 ['**/estate/assets/linotype/reading-first-press-frame.css','reading-first-press-frame.css','text/css']
];
const volumes=['first-readings','essays','teatro','essay--to-read-is-not-to-remember'];
const results=[];
(async()=>{
 for(const [label,driver] of [['chromium',chromium],['webkit',webkit]]){
  const browser=await driver.launch(label==='chromium'?
    {headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
  try{
   const ctx=await browser.newContext({viewport:{width:820,height:1120},ignoreHTTPSErrors:true});
   for(const [pattern,file,mime] of assets)
     await ctx.route(pattern,route=>route.fulfill({status:200,contentType:mime,body:fs.readFileSync(path.join(root,file))}));
   for(const volume of volumes){
    const page=await ctx.newPage(),errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error' && m.text().includes('Fountain Press reader failure'))errors.push(m.text())});
    try{
      await page.goto(origin+'/estate/#/read/'+volume,{waitUntil:'domcontentloaded',timeout:16000});
      await page.waitForFunction(id=>{
        const v=document.querySelector('#page-viewport');
        return v?.dataset.volume===id && v?.dataset.layout==='ready';
      },volume,{timeout:20000});
      const state=await page.evaluate(()=>{
        const v=document.querySelector('#page-viewport');
        return {pages:Number(v.dataset.pages),overflow:document.documentElement.scrollWidth-innerWidth,
          semanticSpecimens:v.querySelectorAll('figure[data-typographic-specimen]').length};
      });
      assert.ok(state.pages>=0 && state.pages<150,JSON.stringify({volume,state}));
      assert.ok(state.overflow<=3,JSON.stringify({volume,state}));
      assert.equal(state.semanticSpecimens,0,'Unrelated book inherited specimen styling');
      assert.deepEqual(errors,[]);
      results.push({label,volume,...state});
      console.log('UNAFFECTED_PASS',label,volume,'pages',state.pages);
    }finally{await page.close()}
   }
   await ctx.close();
  }finally{await browser.close()}
 }
 fs.writeFileSync(path.join(root,'stage-v149-unaffected-books.json'),JSON.stringify({results},null,2)+'\n');
})().catch(e=>{console.error(e);process.exitCode=1});
