const {chromium,webkit}=require(require('path').join(require('os').homedir(),'Developer','fcis.fountain.coach','node_modules','playwright'));
(async()=>{let fails=0;for(const [browserName,engine,route,label,button,file] of [['Chrome',chromium,'teatro','Teatro','#teatro-vergil-read','teatro'],['WebKit',webkit,'solstice-reading-01--vergil','prologue','#vergil-prologue-read','prologue']]){
 const b=await engine.launch(browserName==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});const p=await b.newPage({viewport:{width:1024,height:768},ignoreHTTPSErrors:true});const errors=[];p.on('pageerror',e=>errors.push(String(e)));const r={browser:browserName,route};
 try{await p.goto('https://192.168.8.50:8243/estate/#/read/'+route);const sel='satzfunk-player[label*="'+label+'"]';await p.waitForFunction(s=>document.querySelector(s)?.narrationBinding&&document.querySelector('#page-viewport')?.dataset.layout==='ready',sel,{timeout:26000});const score=await p.evaluate(async f=>await(await fetch('/estate/media/first-readings/'+f+'-midi2-reading-score.private.json')).json(),file);const word=score.events[Math.floor(score.events.length*.51)];
 await p.locator(button).click();await p.waitForFunction(s=>document.querySelector(s)?.state.paused===false,sel,{timeout:17000});
 await p.evaluate(([s,t])=>{const x=document.querySelector(s);x.pause();x.seek(t);window.seekWitness=[];x.addEventListener('satzfunkplayer:seek',e=>window.seekWitness.push(e.detail.currentTime));},[sel,word.timeSeconds+.02]);
 await p.waitForFunction(()=>document.querySelectorAll('.linotype-audio-cursor-mark').length>0,{timeout:15000});
 const marker=await p.locator('.linotype-audio-cursor-mark').first().boundingBox();r.marker=marker;
 await p.mouse.click(marker.x+marker.width/2,marker.y-5);
 r.click=await p.evaluate(s=>({seeks:window.seekWitness,mode:document.querySelector(s).narrationBinding.mode,current:document.querySelector(s).state.currentTime}),sel);
 const clickPassed=r.click.seeks.length>=1;



 await p.evaluate(([s,t])=>{const x=document.querySelector(s);x.seek(t)},[sel,word.timeSeconds+.02]);
 await p.setViewportSize({width:390,height:844});await p.waitForFunction(()=>window.innerWidth===390&&window.FountainPressNarrationBridge?.css?.spread===false&&document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('.linotype-audio-cursor-mark'),null,{timeout:18000});
 r.reflow=await p.evaluate(s=>({page:document.querySelector('#page-count')?.value,volume:document.querySelector('#page-viewport').dataset.volume,mark:document.querySelectorAll('.linotype-audio-cursor-mark').length,current:document.querySelector(s).narrationBinding.current?.blockID,visible:[...document.querySelectorAll('#page-viewport [data-source-block]')].some(n=>n.dataset.sourceBlock===document.querySelector(s).narrationBinding.current?.blockID)}),sel);
 r.pass=clickPassed&&r.reflow.visible&&r.reflow.mark>0&&errors.length===0;
 await p.evaluate(s=>document.querySelector(s)?.pause(),sel);
 }catch(e){r.fail=String(e).slice(0,420);r.pass=false}r.errors=errors;console.log(JSON.stringify(r));if(!r.pass)fails++;await b.close();
 }console.log('FAILURES',fails);if(fails)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});