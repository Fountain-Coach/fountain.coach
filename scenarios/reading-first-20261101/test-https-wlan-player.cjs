const {webkit,chromium}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base='https://192.168.8.50:8243';
const target=base+'/estate/#/read/essay--the-door-is-a-score';
(async()=>{
const observations=[];
for(const [name,type,launch] of [['WebKit',webkit,{}],['Chromium',chromium,{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}]].filter(v=>!process.env.ENGINE||v[0]===process.env.ENGINE)){
 const browser=await type.launch({headless:true,...launch});
 for(const [profile,width,height] of [['landscape',1180,820],['portrait',820,1180],['phone',390,844]].filter(v=>!process.env.PROFILE||v[0]===process.env.PROFILE)){
  const page=await browser.newPage({viewport:{width,height}});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error')errors.push('Console: '+m.text())});
  const response=await page.goto(target,{waitUntil:'commit',timeout:15000});
  assert.equal(response.status(),200,name+' '+profile+' route');
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:17000});
  assert.equal(await page.evaluate(()=>location.protocol),'https:');
  assert.equal(await page.evaluate(()=>isSecureContext),true,'secure browser context');
  let found=false;
  for(let i=0;i<38;i++){
   if(await page.locator('#page-viewport .linotype-area satzfunk-player').count()){found=true;break}
   if(!await page.locator('#next-page').isEnabled())break;
   await page.locator('#next-page').click();
  }
  assert.ok(found,name+' '+profile+' player in printed folio');
  await page.waitForFunction(()=>{const p=document.querySelector('#page-viewport satzfunk-player');return p?.state.state==='ready'&&p.state.duration>13.9},null,{timeout:12000});
  const inspect=()=>page.evaluate(()=>{
    const player=document.querySelector('#page-viewport satzfunk-player');
    const audio=player.shadowRoot?.querySelector('audio');
    const pageAreas=[...document.querySelectorAll('#page-viewport .linotype-area')];
    const clip=pageAreas.flatMap(a=>{const r=a.getBoundingClientRect();return [...a.querySelectorAll('p,figure,img')].filter(n=>n.getBoundingClientRect().bottom>r.bottom+1.25).map(n=>({tag:n.tagName,delta:n.getBoundingClientRect().bottom-r.bottom}))});
    return {secure:isSecureContext,source:audio?.src,loaded:player.state.state,track:player.state.trackID,duration:player.state.duration,time:player.state.currentTime,selected:[...player.shadowRoot.querySelectorAll('option')].map(n=>n.value),visible:!player.hidden,mode:document.querySelector('#page-viewport').dataset.mode,pages:document.querySelector('#page-count').textContent,clip,scroll:pageAreas.map(a=>a.scrollHeight-a.clientHeight)};
  });
  let state=await inspect();
  assert.equal(state.secure,true);
  assert.deepEqual(state.selected,['present','beyond','memory','withheld']);
  assert.ok(state.visible);
  assert.ok(state.source.startsWith(base+'/estate/essays/the-door-is-a-score/media/'));
  assert.ok(state.duration>=13.9&&state.duration<14.2,'media duration');
  assert.equal(state.clip.length,0,'clipped nodes');
  assert.ok(state.scroll.every(n=>n<=2),'page overflow');
  const select=page.locator('#page-viewport satzfunk-player').locator('select');
  await select.selectOption('memory');
  await page.waitForFunction(()=>{const p=document.querySelector('#page-viewport satzfunk-player');return p?.state.trackID==='memory'&&p?.state.duration>13.9},null,{timeout:10000});
  await page.locator('#page-viewport satzfunk-player').evaluate(el=>el.seek(2));
  state=await inspect();
  assert.equal(state.track,'memory');
  assert.ok(state.source.endsWith('/memory.mp3'));
  assert.ok(Math.abs(state.time-2)<0.25,'time seek');
  assert.equal(errors.length,0,'browser errors: '+errors.join('; '));
  await page.screenshot({path:'/Users/benedikteickhoff/Developer/fountain-publishing/fountain.coach/scenarios/reading-first-20261101/https-stage-'+name+'-'+profile+'.png'});
  observations.push({engine:name,profile,https:state.secure,player:state.loaded,trackCount:state.selected.length,seek:state.time,page:state.pages,clip:state.clip.length,scroll:state.scroll,source:state.source,errors});
  console.log('PASS',name,profile,JSON.stringify(observations.at(-1)));
  await page.close();
 }
 await browser.close();
}
fs.writeFileSync('/Users/benedikteickhoff/Developer/fountain-publishing/fountain.coach/scenarios/reading-first-20261101/https-player-wlan-evidence'+(process.env.ENGINE?'-'+process.env.ENGINE+'-'+(process.env.PROFILE||'all'):'')+'.json',JSON.stringify({origin:base,release:'shared-shell-20261101-v84-inline-satzfunk-qa',results:observations,failures:0},null,2)+'\n');
console.log('ALL PASSED',observations.length);
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
