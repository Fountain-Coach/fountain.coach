/* Live acceptance of the actual developing Bookshelf's Teatro volume.
 * Source-owned test: no mocked audio, no external media URLs, no paid calls.
 * Staging private HTTPS only; never a public estate acceptance claim. */
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||
  path.join(os.homedir(),'Developer','fcis.fountain.coach','node_modules','playwright'));
const BASE=process.env.FCIS_WLAN_STAGE_HTTPS||'https://192.168.8.50:8243';
const SRC_SHA='6aefe374f2109d6d432cc3952d4703d8795fbeaf728e62b0113543e6ff11e43c';
const AUDIO_SHA='d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd';
const failures=[];
async function test(engineName,engine,width,height){
 const browser=await engine.launch(engineName==='Chromium'
  ? {headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}
  : {headless:true});
 const page=await browser.newPage({viewport:{width,height},ignoreHTTPSErrors:true});
 page.setDefaultTimeout(12000);page.setDefaultNavigationTimeout(20000);
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 try{
  const response=await page.goto(BASE+'/estate/#/read/library',{waitUntil:'domcontentloaded',timeout:20000});
  assert.equal(response.status(),200);console.log('CHECK_ROOT',engineName,width);
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library',{timeout:18000});
  await page.waitForSelector('#teatro-vergil-read',{state:'attached',timeout:12000});
  assert.equal(await page.locator('#teatro-vergil-read').isHidden(),true);
  const text=await page.evaluate(()=>{
   const template=document.querySelector('template[data-reader-volume="teatro"]');
   const blocks=[...template.content.querySelectorAll('[data-source-block^="teatro-an-unfinished-composition."]')]
     .filter(e=>e.matches('h2,p')&&/^teatro-an-unfinished-composition\.(?:title|p\d+)$/.test(e.dataset.sourceBlock));
   return blocks.map(e=>e.textContent.trim()).join('\n\n');
  });
  assert.equal(crypto.createHash('sha256').update(text).digest('hex'),SRC_SHA);console.log('CHECK_SOURCE',engineName,width);
  const manifestResponse=await page.request.get(BASE+'/estate/media/first-readings/teatro-vergil-edition.private.json');
  assert.equal(manifestResponse.status(),200);
  const manifest=await manifestResponse.json();
  assert.equal(manifest.sourceSHA256,SRC_SHA);
  assert.equal(manifest.recording.sha256,AUDIO_SHA);
  assert.equal(manifest.publicReleaseAuthorized,false);
  assert.equal(manifest.privateRehearsalAuthorized,true);console.log('CHECK_MANIFEST',engineName,width);
  // Browser navigation is internal: same page-frame and no duplicate edition tab.
  await page.locator('#reader-section').selectOption('first-readings');
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='first-readings');
  assert.equal(await page.locator('#teatro-vergil-read').isHidden(),true);
  console.log('CHECK_FIRST_READINGS',engineName,width);
  await page.evaluate(()=>{const link=document.querySelector('[data-reader-target="teatro"]');if(!link)throw Error('No Teatro target in First Readings');link.click()});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='teatro');
  await page.waitForFunction(()=>document.querySelector('satzfunk-player[label*="Teatro"]')?.state?.state==='ready');
  const btn=page.locator('#teatro-vergil-read');
  assert.equal(await btn.isVisible(),true);
  assert.match(await btn.getAttribute('aria-label'),/AI-generated Vergil voice/);
  console.log('CHECK_TEATRO',engineName,width);
  await btn.click();
  await page.waitForFunction(()=>document.querySelector('satzfunk-player[label*="Teatro"]')?.state?.paused===false);
  await page.waitForTimeout(650);
  const during=await page.evaluate(()=>{
   const player=document.querySelector('satzfunk-player[label*="Teatro"]');
   return {time:player.state.currentTime,duration:player.state.duration,paused:player.state.paused,
     clock:document.querySelector('#teatro-vergil-clock').textContent,
     volume:document.querySelector('#page-viewport').dataset.volume,
     overflowX:document.documentElement.scrollWidth>innerWidth};
  });
  assert.ok(during.time>0 && during.time<during.duration);
  assert.ok(Math.abs(during.duration-498.97)<0.12,
    "Browser duration differs from decoded source by more than MP3 padding");
  assert.match(during.clock,/8:19$/);
  assert.equal(during.overflowX,false);
  await page.locator('#next-page').click();
  await page.waitForTimeout(460);
  const afterTurn=await page.evaluate(()=>{
   const player=document.querySelector('satzfunk-player[label*="Teatro"]');
   return {time:player.state.currentTime,paused:player.state.paused,
    volume:document.querySelector('#page-viewport').dataset.volume};
  });
  assert.equal(afterTurn.paused,false);
  assert.ok(afterTurn.time>during.time);
  await page.locator('#reader-library').click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library');
  const left=await page.evaluate(()=>({
   paused:document.querySelector('satzfunk-player[label*="Teatro"]').state.paused,
   hidden:document.querySelector('#teatro-vergil-read').hidden
  }));
  assert.equal(left.paused,true);
  assert.equal(left.hidden,true);
  assert.deepEqual(errors,[]);
  console.log('NEW_ESTATE_VERGIL_ACCEPTED',JSON.stringify({engineName,width,height,during,afterTurn,left}));
 }catch(e){
  const detail={engineName,width,height,error:e.message,errors};
  failures.push(detail);
  console.error('NEW_ESTATE_VERGIL_FAILED',JSON.stringify(detail));
 }finally{await page.close();await browser.close()}
}
(async()=>{
 for(const [engineName,engine] of [['Chromium',chromium],['WebKit',webkit]]){
  for(const [width,height] of [[1024,768],[390,844]])await test(engineName,engine,width,height);
 }
 console.log('NEW_ESTATE_VERGIL_FAILURES',failures.length);
 if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
