// Private WLAN acceptance: real audio crosses a source-addressed MIDI2 boundary.
// Usage: PLAYWRIGHT_MODULE=/path/to/playwright node verify_narrated_page_turn.cjs
// The browser media element and actual accepted Vergil MP3 are required.
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{let failures=0;for(const [browserName,browserType,route,label,button,id] of [['Chrome',chromium,'teatro','Teatro','#teatro-vergil-read','teatro'],['WebKit',webkit,'solstice-reading-01--vergil','prologue','#vergil-prologue-read','prologue']]){
 const browser=await browserType.launch(browserName==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 const page=await browser.newPage({viewport:{width:1024,height:768},ignoreHTTPSErrors:true});
 const errs=[];page.on('pageerror',e=>errs.push(String(e)));const result={browser:browserName,route};
 try{
  await page.goto((process.env.WLAN_READER_ORIGIN||'https://192.168.8.50:8243')+'/estate/#/read/'+route,{waitUntil:'domcontentloaded'});
  const player='satzfunk-player[label*="'+label+'"]';
  await page.waitForFunction(s=>document.querySelector(s)?.narrationBinding&&document.querySelector('#page-viewport')?.dataset.layout==='ready',player,{timeout:30000});
  const pair=await page.evaluate(async name=>{
   const score=await(await fetch('/estate/media/first-readings/'+name+'-midi2-reading-score.private.json')).json();
   const bridge=window.FountainPressNarrationBridge;const map=new Map();
   for(let i=0;i<bridge.leaves.length;i++)for(const n of bridge.leaves[i].area.querySelectorAll('[data-source-block][data-source-from][data-source-to]')){
    const key=n.dataset.sourceBlock;if(!map.has(key))map.set(key,[]);map.get(key).push({i,start:+n.dataset.sourceFrom,end:+n.dataset.sourceTo})
   }
   const at=e=>{const p=map.get(e.blockID)?.find(r=>e.start>=r.start&&e.start<r.end);return p?bridge.spreadStart(p.i):null};
   const events=score.events;
   const candidates=[];
   for(let i=1;i<events.length;i++){
    const a=events[i-1],b=events[i],ap=at(a),bp=at(b);
    if(ap!==null&&bp!==null&&ap!==bp&&b.timeSeconds-a.timeSeconds<4&&b.timeSeconds-a.timeSeconds>0&&a.timeSeconds>4)candidates.push({a,b,ap,bp,gap:b.timeSeconds-a.timeSeconds});
   }
   return candidates.find(x=>x.gap>=.05)||candidates[0]||null;
  },id);
  if(!pair)throw Error('No natural page boundary between consecutive timed words');
  result.boundary={start:pair.a.timeSeconds,end:pair.b.timeSeconds,from:pair.ap,to:pair.bp,gap:pair.gap};
  await page.evaluate(([s,t])=>{const x=document.querySelector(s);x.seek(t)},[player,pair.a.timeSeconds+.01]);
  await page.waitForFunction(([s,t])=>Math.abs(document.querySelector(s).state.currentTime-t)<.08,[player,pair.a.timeSeconds+.01],{timeout:11000});

  await page.waitForFunction(n=>window.FountainPressNarrationBridge.current===n,pair.ap,{timeout:12000});
  result.initial=await page.evaluate(s=>({page:window.FountainPressNarrationBridge.current,time:document.querySelector(s).state.currentTime,paused:document.querySelector(s).state.paused}),player);
  await page.locator(button).click();
  await page.waitForFunction(([s,target])=>window.FountainPressNarrationBridge.current===target&&document.querySelector(s).state.currentTime>=0,[player,pair.bp],{timeout:17000});
  result.follow=await page.evaluate(s=>({page:window.FountainPressNarrationBridge.current,time:document.querySelector(s).state.currentTime,paused:document.querySelector(s).state.paused,mode:document.querySelector(s).narrationBinding.mode,marks:document.querySelectorAll('.linotype-audio-cursor-mark').length}),player);
  await page.evaluate(s=>document.querySelector(s).pause(),player);
  result.pass=result.initial.page===pair.ap&&result.follow.page===pair.bp&&result.follow.mode==='cursor'&&result.follow.marks>0&&!result.follow.paused&&result.follow.time>=pair.b.timeSeconds-.3&&errs.length===0;
 }catch(e){result.fail=String(e).slice(0,600);result.pass=false}
 result.errors=errs;console.log(JSON.stringify(result));if(!result.pass)failures++;await page.close();await browser.close();
}console.log('NATURAL_PAGE_TURNS_FAILURES',failures);if(failures)process.exitCode=1})().catch(e=>{console.error(e);process.exitCode=1});