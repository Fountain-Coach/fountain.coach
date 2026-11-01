/* Live acceptance of the actual developing Bookshelf's Vergil prologue volume.
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
const SRC_SHA='63eba43a777b39f9bb27ab8b54fcb7cb04f5ad61633a8f50e0e6aa44e56b3971';

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
  await page.waitForSelector('#vergil-prologue-read',{state:'attached',timeout:12000});
  assert.equal(await page.locator('#vergil-prologue-read').isHidden(),true);
  const text=await page.evaluate(()=>{
   const template=document.querySelector('template[data-reader-volume="solstice-reading-01--vergil"]');
   const blocks=[...template.content.querySelectorAll('[data-source-block^="solstice-reading-01--vergil.text."]')]
     .filter(e=>e.matches('h2,p')&&/^solstice-reading-01--vergil\.text\.\d+$/.test(e.dataset.sourceBlock));
   return blocks.map(e=>e.textContent.trim()).join('\n\n');
  });
  assert.equal(crypto.createHash('sha256').update(text).digest('hex'),SRC_SHA);console.log('CHECK_SOURCE',engineName,width);
  const manifestResponse=await page.request.get(BASE+'/estate/media/first-readings/vergil-prologue-edition.private.json');
  assert.equal(manifestResponse.status(),200);
  const manifest=await manifestResponse.json();
  assert.equal(manifest.sourceSHA256,SRC_SHA);
  assert.match(manifest.recording.sha256,/^[a-f0-9]{64}$/);
  assert.equal(manifest.independentTranscriptsAligned,true);
  assert.equal(manifest.publicReleaseAuthorized,false);
  assert.equal(manifest.privateRehearsalAuthorized,true);console.log('CHECK_MANIFEST',engineName,width);
  // Browser navigation is internal: same page-frame and no duplicate edition tab.
  await page.locator('#reader-section').selectOption('first-readings');
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='first-readings');
  assert.equal(await page.locator('#vergil-prologue-read').isHidden(),true);
  console.log('CHECK_FIRST_READINGS',engineName,width);
  await page.evaluate(()=>{location.hash='#/read/solstice-reading-01--vergil'});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice-reading-01--vergil');
  await page.waitForFunction(()=>document.querySelector('satzfunk-player[label*="prologue"]')?.state?.state==='ready');
  const btn=page.locator('#vergil-prologue-read');
  assert.equal(await btn.isVisible(),true);
  assert.match(await btn.getAttribute('aria-label'),/AI-generated Vergil voice/);
  console.log('CHECK_PROLOGUE',engineName,width);
  await btn.click();
  await page.waitForFunction(()=>document.querySelector('satzfunk-player[label*="prologue"]')?.state?.paused===false);
  await page.waitForTimeout(650);
  const during=await page.evaluate(()=>{
   const player=document.querySelector('satzfunk-player[label*="prologue"]');
   return {time:player.state.currentTime,duration:player.state.duration,paused:player.state.paused,
     clock:document.querySelector('#vergil-prologue-clock').textContent,
     volume:document.querySelector('#page-viewport').dataset.volume,
     overflowX:document.documentElement.scrollWidth>innerWidth};
  });
  assert.ok(during.time>0 && during.time<during.duration);
  assert.ok(Math.abs(during.duration-manifest.recording.duration)<0.16,
    "Browser duration differs from decoded source by more than MP3 padding");
  assert.ok(during.clock.includes(':'));
  assert.equal(during.overflowX,false);
  await page.locator('#next-page').click();
  await page.waitForTimeout(460);
  const afterTurn=await page.evaluate(()=>{
   const player=document.querySelector('satzfunk-player[label*="prologue"]');
   return {time:player.state.currentTime,paused:player.state.paused,
    volume:document.querySelector('#page-viewport').dataset.volume};
  });
  assert.equal(afterTurn.paused,false);
  assert.ok(afterTurn.time>during.time);
  await page.locator('#reader-library').click();
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library');
  const left=await page.evaluate(()=>({
   paused:document.querySelector('satzfunk-player[label*="prologue"]').state.paused,
   hidden:document.querySelector('#vergil-prologue-read').hidden
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
