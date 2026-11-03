const path=require('path'),os=require('os');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
(async()=>{
let failures=0;
for(const [name,engine] of [['Chrome',chromium],['WebKit',webkit]]){
 const browser=await engine.launch(name==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 for(const viewport of [{width:1024,height:768},{width:768,height:1024},{width:390,height:844}]){
  const page=await browser.newPage({viewport,ignoreHTTPSErrors:true});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const result={browser:name,viewport:viewport.width+'x'+viewport.height};
  try{
   await page.goto((process.env.STAGING_ORIGIN||'https://192.168.8.50:8243')+'/estate/#/read/teatro',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='teatro',{timeout:28000});
   result.before=await page.evaluate(()=>{
    const v=document.querySelector('#page-viewport');
    const sheet=v.querySelector('.linotype-sheet:not([hidden])');
    return {brandText:document.querySelector('.brand').textContent.trim(),brandLabel:document.querySelector('.brand').getAttribute('aria-label'),
       info:[...v.querySelectorAll('button[data-reader-info]')].length,
       imprint:v.querySelector('.linotype-folio')?.textContent?.trim(),
       head:v.querySelector('.linotype-running')?.textContent?.trim(),
       count:document.querySelector('#page-count').textContent,
       source:document.querySelector('template[data-reader-volume="teatro"]').content.querySelectorAll('[data-source-block^="teatro-an-unfinished-composition."]').length
    };
   });
   const info=page.locator('#page-viewport button[data-reader-info]:visible').first();
   await info.waitFor({state:'visible',timeout:13000});
   await info.click();
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:24000});
   result.notes=await page.evaluate(()=>({
     title:document.querySelector('#page-viewport .linotype-area h2')?.textContent,
     legal:!!document.querySelector('template[data-reader-volume="publication-notes"]')?.content.querySelector('a[href="https://status.fountain.coach/"]'),
     infoButtons:document.querySelectorAll('#page-viewport button[data-reader-info]').length,
     returnVisible:[...document.querySelectorAll('#page-viewport [data-reader-return]')].some(x=>x.getClientRects().length>0),
     pages:document.querySelector('#page-viewport').dataset.pages
   }));
   await page.locator('#page-viewport [data-reader-return]:visible').first().click();
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='teatro'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:24000});
   result.returned=await page.evaluate(()=>({
     count:document.querySelector('#page-count').textContent,
     info:[...document.querySelectorAll('#page-viewport button[data-reader-info]')].length,
     mode:document.querySelector('#page-viewport').dataset.mode,
     author:document.querySelector('#page-viewport .linotype-running')?.textContent
   }));
   result.pass=result.before.brandText===''&&result.before.brandLabel.includes('Bookshelf')&&
     result.before.info>0&&result.before.imprint.startsWith('i')&&
     result.before.head.includes('Benedikt')&&result.notes.legal&&
     result.notes.infoButtons===0&&result.notes.returnVisible&&result.returned.count===result.before.count&&result.returned.info>0&&errors.length===0;
  }catch(e){result.failure=String(e).slice(0,550);result.pass=false}
  result.errors=errors;
  console.log(JSON.stringify(result));
  if(!result.pass)failures++;
  await page.close();
 }await browser.close();
}
console.log('COLOPHON_ACCEPTANCE',6-failures,'/ 6', 'FAILURES',failures);
if(failures)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
