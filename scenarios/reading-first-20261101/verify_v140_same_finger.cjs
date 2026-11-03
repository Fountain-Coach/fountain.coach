const path=require('path'),os=require('os');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
(async()=>{let fails=0;for(const [name,engine] of [['Chrome',chromium],['WebKit',webkit]]){
const b=await engine.launch(name==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
for(const viewport of [{width:1024,height:768},{width:768,height:1024},{width:390,height:844}]){
for(const side of viewport.width>viewport.height?['left','right']:['left']){
const p=await b.newPage({viewport,ignoreHTTPSErrors:true});const errs=[];p.on('pageerror',e=>errs.push(String(e)));
const out={browser:name,viewport:viewport.width+'x'+viewport.height,side};
try{
await p.goto((process.env.STAGING_ORIGIN||'https://192.168.8.50:8243')+'/estate/#/read/teatro',{waitUntil:'domcontentloaded'});
await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='teatro',{timeout:32000});
await p.locator('#next-page').click();
await p.waitForTimeout(160);
out.before=await p.locator('#page-count').textContent();
const infos=p.locator('#page-viewport .linotype-folio button[data-reader-info]');
const index=side==='right'?1:0;
if((await infos.count())<=index)throw Error('Missing corresponding info folio '+side);
const loc=infos.nth(index);
const r=await loc.boundingBox();
if(!r)throw Error('Info icon not visible');
const center={x:r.x+r.width/2,y:r.y+r.height/2};
await p.mouse.click(center.x,center.y);
await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:28000});
const links=p.locator('#page-viewport button[data-reader-return]');
out.addendum={count:await links.count(),inText:await p.locator('#page-viewport .linotype-area [data-reader-return]').count(),bodyWords:await p.locator('#page-viewport .linotype-area').first().innerText()};
if((await links.count())<=index)throw Error('Return control missing at original folio index: '+side);
const l=links.nth(index);const rr=await l.boundingBox();if(!rr)throw Error('Logo not visible');
const destination={x:rr.x+rr.width/2,y:rr.y+rr.height/2};
out.delta={x:destination.x-center.x,y:destination.y-center.y};
out.returnAria=await l.getAttribute('aria-label');
out.logo=await l.locator('img').getAttribute('src');
await p.mouse.click(center.x,center.y);
await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='teatro'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:28000});
out.after=await p.locator('#page-count').textContent();
const returned=p.locator('#page-viewport .linotype-folio button[data-reader-info]').nth(index);
const back=await returned.boundingBox();
out.cycleDelta={x:back.x+back.width/2-center.x,y:back.y+back.height/2-center.y};
out.pass=out.before===out.after&&out.before!=='1–2 / 10'&&
Math.abs(out.delta.x)<3&&Math.abs(out.delta.y)<3&&
Math.abs(out.cycleDelta.x)<3&&Math.abs(out.cycleDelta.y)<3&&
out.returnAria?.includes('previous reading position')&&out.logo?.includes('fountain-coach-logo')&&
out.addendum.inText===0&&errs.length===0;
}catch(e){out.error=String(e).slice(0,450);out.pass=false}
out.pageErrors=errs;console.log(JSON.stringify(out));if(!out.pass)fails++;await p.close();
} } await b.close();
} console.log('FOLIO_SAME_FINGER',8-fails,'/ 8', 'FAILS',fails);if(fails)process.exitCode=1;})().catch(e=>{console.error(e);process.exitCode=1});