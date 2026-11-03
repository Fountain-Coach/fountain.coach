const path=require('path'),os=require('os');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
(async()=>{let fail=0;for(const [name,engine] of [['Chrome',chromium],['WebKit',webkit]]){
 const b=await engine.launch(name==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 const p=await b.newPage({viewport:{width:1024,height:768},ignoreHTTPSErrors:true});const errors=[];p.on('pageerror',e=>errors.push(String(e)));
 const r={browser:name};try{
  await p.goto((process.env.STAGING_ORIGIN||'https://192.168.8.50:8243')+'/estate/#/read/teatro',{waitUntil:'domcontentloaded'});
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='teatro',{timeout:27000});
  await p.locator('#next-page').click();
  r.before=await p.locator('#page-count').textContent();
  await p.locator('#page-viewport button[data-reader-info]:visible').first().click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000});
  await p.locator('#page-viewport [data-reader-return]:visible').first().click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='teatro'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000});
  r.after=await p.locator('#page-count').textContent();
  r.duplicatedPublisher=await p.evaluate(()=>document.querySelectorAll('p[data-source-block="continuity.publisher"]').length+
   (document.querySelector('template[data-reader-volume="continuity"]')?.content.querySelectorAll('p[data-source-block="continuity.publisher"]').length||0));
  r.pass=r.before!=='1–2 / 10'&&r.before===r.after&&r.duplicatedPublisher===0&&errors.length===0;
 }catch(e){r.failure=String(e).slice(0,400);r.pass=false}
 r.errors=errors;console.log(JSON.stringify(r));if(!r.pass)fail++;await b.close();
}console.log('NONFIRST_FOLIO_RETURN',2-fail,'/ 2');if(fail)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});