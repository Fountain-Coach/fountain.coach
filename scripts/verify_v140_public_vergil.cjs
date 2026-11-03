const path=require('path'),fs=require('fs');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||path.join(require('os').homedir(),'Developer','fcis.fountain.coach','node_modules','playwright'));
(async()=>{
 const out=[];let fails=0;
 for(const [browserName,engine,route,playerLabel,buttonID,scoreName] of [
  ['Chrome',chromium,'teatro','Teatro','#teatro-vergil-read','teatro'],
  ['Chrome',chromium,'solstice-reading-01--vergil','prologue','#vergil-prologue-read','prologue'],
  ['WebKit',webkit,'teatro','Teatro','#teatro-vergil-read','teatro'],
  ['WebKit',webkit,'solstice-reading-01--vergil','prologue','#vergil-prologue-read','prologue']
 ]){
  if(process.env.CASE && process.env.CASE !== browserName+':'+route) continue;
  const browser=await engine.launch(browserName==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
  const page=await browser.newPage({viewport:{width:1024,height:768},ignoreHTTPSErrors:true});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  let r={browser:browserName,route};
  const sel='satzfunk-player[label*="'+playerLabel+'"]';
  try{
   await page.goto((process.env.WLAN_READER_ORIGIN||'https://192.168.8.50:8243')+'/estate/#/read/'+route,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(s=>document.querySelector(s)?.narrationBinding&&document.querySelector('#page-viewport')?.dataset.layout==='ready',sel,{timeout:32000});
   const button=page.locator(buttonID);
   r.start=await page.evaluate(([s,b])=>{
    const player=document.querySelector(s),button=document.querySelector(b);
    const main=document.querySelector('#page-viewport');
    return {button:button.textContent,mode:player.narrationBinding.mode,hidden:button.hidden,
      aria:button.getAttribute('aria-label'),sound:player.audioSettings.mode,
      patches:document.querySelectorAll('.voice-mastering-leaf,.voice-patch-surface').length,
      soundSelectors:document.querySelectorAll('.satzfunk-voice-settings,.satzfunk-narration-mode').length,
      finalTemplatePatches:document.querySelectorAll('template[data-reader-volume] .voice-mastering-leaf').length,
      pages:main.dataset.pages,layout:main.dataset.mode,csound:player.audioSettings.engine||null,
      font:getComputedStyle(button).fontFamily,fontSize:getComputedStyle(button).fontSize,
      hit:{w:button.getBoundingClientRect().width,h:button.getBoundingClientRect().height}
     };
   },[sel,buttonID]);
   if(r.start.button!=='▶'||r.start.mode!=='cursor'||r.start.hidden||r.start.sound!=='studio'||
      r.start.patches!==0||r.start.soundSelectors!==0||r.start.finalTemplatePatches!==0||
      r.start.hit.w<43||r.start.hit.h<43)throw Error('Default reader UI failed: '+JSON.stringify(r.start));
   await button.click();
   await page.waitForFunction(s=>document.querySelector(s)?.audioSettings?.ear?.windows>15,sel,{timeout:28000});
   await page.waitForFunction(b=>document.querySelector(b)?.textContent==='❚❚',buttonID,{timeout:16000});
   r.playing=await page.evaluate(([s,b])=>{
    const p=document.querySelector(s);
    return {symbol:document.querySelector(b).textContent,aria:document.querySelector(b).getAttribute('aria-label'),
      paused:p.state.paused,engine:p.audioSettings.engine,mode:p.audioSettings.mode,
      earWindows:p.audioSettings.ear?.windows,rms:p.audioSettings.ear?.rms};
   },[sel,buttonID]);
   if(r.playing.paused||r.playing.symbol!=='❚❚'||!r.playing.earWindows||!(r.playing.rms>0))throw Error('Csound/playback failure');
   await button.click();
   await page.waitForFunction(([s,b])=>document.querySelector(s)?.state.paused===true&&document.querySelector(b).textContent==='▶',[sel,buttonID],{timeout:12000});
   const target=await page.evaluate(async name=>{
     const data=await(await fetch('/estate/media/first-readings/'+name+'-midi2-reading-score.json')).json();
     const p=window.FountainPressNarrationBridge;
     for(const e of data.events){
      if(e.timeSeconds<50)continue;
      const match=p.leaves.find(x=>[...x.area.querySelectorAll('[data-source-block][data-source-from][data-source-to]')].some(n=>
        n.dataset.sourceBlock===e.blockID && Number(n.dataset.sourceFrom)<=e.start && Number(n.dataset.sourceTo)>e.start));
      if(match)return {block:e.blockID,start:e.start,t:(e.timeSeconds+e.endSeconds)/2};
     }
     throw Error('No source-addressed target');
   },scoreName);
   await page.evaluate(([s,t])=>document.querySelector(s).seek(t),[sel,target.t]);
   await page.waitForFunction(()=>document.querySelectorAll('.linotype-audio-cursor-mark').length>0,{timeout:16000});
   r.cursor=await page.evaluate(([s,t])=>({position:document.querySelector(s).state.currentTime,
     page:window.FountainPressNarrationBridge.current,
     marks:document.querySelectorAll('.linotype-audio-cursor-mark').length,
     mode:document.querySelector(s).narrationBinding.mode}),[sel,target.t]);
   if(!r.cursor.marks||r.cursor.mode!=='cursor')throw Error('Fixed cursor unavailable');
   // Keep the accepted reading selected and test responsive re-composition.
   await page.setViewportSize({width:390,height:844});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&
     window.FountainPressNarrationBridge?.css?.spread===false,{timeout:25000});
   await page.waitForFunction(()=>document.querySelectorAll('.linotype-audio-cursor-mark').length>0,{timeout:14000});
   r.portrait=await page.evaluate(([s,b])=>({
      display:document.querySelector('#page-viewport').dataset.mode,
      mode:document.querySelector(s).narrationBinding.mode,
      marks:document.querySelectorAll('.linotype-audio-cursor-mark').length,
      button:document.querySelector(b).textContent,
      voiceOptions:document.querySelectorAll('.satzfunk-voice-settings,.satzfunk-narration-mode').length,
      patchLeaves:document.querySelectorAll('.voice-mastering-leaf').length
   }),[sel,buttonID]);
   r.errors=errors;r.pass=r.portrait.marks>0&&r.portrait.display==='single'&&r.portrait.button==='▶'&&
      r.portrait.voiceOptions===0&&r.portrait.patchLeaves===0&&errors.length===0;
  }catch(e){r.failure=String(e).slice(0,450);r.errors=errors;r.pass=false}
  console.log(JSON.stringify(r));out.push(r);if(!r.pass)fails++;
  await page.close();await browser.close();
 }
 if(process.env.OUTPUT)fs.writeFileSync(process.env.OUTPUT,JSON.stringify({schema:'fountain.press.vergil.public-v140',tests:out,failures:fails},null,2));
 console.log(JSON.stringify({cases:out.length,passed:out.length-fails,failed:fails}));
 if(fails)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});