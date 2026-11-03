const path=require('path'),fs=require('fs');
const {chromium,webkit}=require(path.join(require('os').homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
(async()=>{
let failures=0,checks=0;
for(const [name,engine] of [['Chrome',chromium],['WebKit',webkit]]){
 const args=name==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true};
 const browser=await engine.launch(args);
 for(const viewport of [{width:1024,height:768},{width:768,height:1024},{width:390,height:844}]){
  for(const side of viewport.width>viewport.height?['left','right']:['left']){
   const page=await browser.newPage({viewport});
   const errors=[],missing=[],privateRequests=[];
   page.on('pageerror',e=>errors.push(String(e)));
   page.on('response',r=>{if(r.status()>=400)missing.push(r.status()+' '+r.url());});
   page.on('request',r=>{if(/(media\/edition\.json|private|\.mp3|\.wav|vergil-hearing)/i.test(r.url()))privateRequests.push(r.url());});
   const id={name,viewport:viewport.width+'x'+viewport.height,side};
   try{
    await page.goto('http://127.0.0.1:4193/#/read/teatro',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready' && document.querySelector('#page-viewport')?.dataset.volume==='teatro',{timeout:24000});
    await page.locator('#next-page').click();
    await page.waitForTimeout(200);
    const initial=(await page.locator('#page-count').textContent()).trim();
    const infos=page.locator('#page-viewport .linotype-folio button[data-reader-info]');
    const idx=side==='right'?1:0;
    if((await infos.count())<=idx)throw Error('Missing folio i');
    const rect=await infos.nth(idx).boundingBox();
    const c={x:rect.x+rect.width/2,y:rect.y+rect.height/2};
    await page.mouse.click(c.x,c.y);
    await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:24000});
    const returns=page.locator('#page-viewport button[data-reader-return]');
    if((await returns.count())<=idx)throw Error('Missing same-position return logo');
    const ret=await returns.nth(idx).boundingBox();
    const delta=Math.hypot(ret.x+ret.width/2-c.x,ret.y+ret.height/2-c.y);
    await page.mouse.click(c.x,c.y);
    await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='teatro'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:24000});
    const after=(await page.locator('#page-count').textContent()).trim();
    const bridge=await page.evaluate(()=>typeof window.FountainPressNarrationBridge);
    const pub=await page.evaluate(()=>document.querySelectorAll('satzfunk-player').length);
    id.initial=initial;id.after=after;id.delta=Math.round(delta*100)/100;id.bridge=bridge;id.player=pub;
    id.pass=initial===after && delta<=3 && bridge==='undefined' && pub===0 && !errors.length && !missing.length && !privateRequests.length;
   }catch(e){id.error=String(e);id.pass=false}
   id.pageErrors=errors;id.missing=missing.slice(0,5);id.privateRequests=privateRequests.slice(0,5);
   checks++;if(!id.pass)failures++;console.log(JSON.stringify(id));
   await page.close();
  }
 }
 await browser.close();
}
console.log('PUBLIC_V140_BROWSER',checks-failures,'/',checks);
process.exitCode=failures?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
