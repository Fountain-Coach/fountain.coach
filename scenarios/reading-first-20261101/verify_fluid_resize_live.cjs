#!/usr/bin/env node
// Actual active v150 Reader: recompose at runtime on viewport-size changes,
// retaining an addressable passage rather than scaling a snapshot.
const assert=require('node:assert/strict');
const {webkit,chromium}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
(async()=>{
 for(const [name,driver]of[['webkit',webkit],['chromium',chromium]]){
  const browser=await driver.launch(name==='chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
  const ctx=await browser.newContext({viewport:{width:820,height:1120},ignoreHTTPSErrors:true});
  const page=await ctx.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error'&&m.text().includes('Fountain Press reader failure'))errors.push(m.text());});
  try{
   await page.goto('https://192.168.8.50:8243/estate/#/read/essay--what-makes-a-page-modern',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.pages==='17'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000});
   await page.locator('#next-page').click(); // manuscript's demonstration on leaf 2
   const measure=()=>page.evaluate(()=>{
     const v=document.querySelector('#page-viewport'),sheet=v.querySelector('.linotype-sheet'),area=sheet.querySelector('.linotype-area');
     return {count:+v.dataset.pages,width:sheet.getBoundingClientRect().width,measure:area.getBoundingClientRect().width,
       sourceIDs:[...v.querySelectorAll('[data-source-block]')].map(x=>x.dataset.sourceBlock).filter(Boolean),
       text:v.innerText.slice(0,300)};
   });
   const first=await measure();
   assert.equal(first.measure,670);
   assert.ok(first.sourceIDs.some(x=>x.includes('what-makes-a-page-modern')),'source address not visible before resize');
   await page.setViewportSize({width:1024,height:1366});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.pages==='13' &&
      Math.abs(document.querySelector('#page-viewport .linotype-area')?.getBoundingClientRect().width-844)<2,{timeout:25000});
   const enlarged=await measure();
   assert.equal(enlarged.measure,844);
   assert.ok(enlarged.sourceIDs.some(x=>x.includes('what-makes-a-page-modern')),'source identity lost after resize');
   await page.setViewportSize({width:820,height:1120});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.pages==='17' &&
      Math.abs(document.querySelector('#page-viewport .linotype-area')?.getBoundingClientRect().width-670)<2,{timeout:25000});
   const returned=await measure();
   assert.equal(returned.measure,670);
   assert.ok(returned.sourceIDs.some(x=>x.includes('what-makes-a-page-modern')));
   assert.deepEqual(errors,[]);
   console.log('ACTUAL_LIVE_REFLOW_PASS',name,JSON.stringify({first:{width:first.width,measure:first.measure,count:first.count},enlarged:{width:enlarged.width,measure:enlarged.measure,count:enlarged.count},returned:{width:returned.width,measure:returned.measure,count:returned.count},sourceAddressSurvived:true}));
  }finally{await ctx.close();await browser.close()}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
