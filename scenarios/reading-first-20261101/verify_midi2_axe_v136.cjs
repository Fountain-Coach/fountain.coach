const path=require('path'),fs=require('fs');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||path.join(process.env.HOME,'Developer/fcis.fountain.coach/node_modules/playwright'));
const axe=require.resolve('axe-core/axe.min.js',{paths:[path.join(process.env.HOME,'Developer/fcis.fountain.coach')]});
(async()=>{
let errors=0;const results=[];
for(const [engineName,engine] of [['Chrome',chromium],['WebKit',webkit]]){
 const browser=await engine.launch(engineName==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 for(const viewport of [{width:1024,height:768},{width:390,height:844}])
 for(const [route,playerName] of [['teatro','Teatro'],['solstice-reading-01--vergil','prologue']]){
  const page=await browser.newPage({viewport,ignoreHTTPSErrors:true});const pageErrors=[];page.on('pageerror',e=>pageErrors.push(String(e)));
  const record={browser:engineName,viewport:viewport.width+'x'+viewport.height,route};try{
   await page.goto((process.env.STAGING_ORIGIN||'https://192.168.8.50:8243')+'/estate/#/read/'+route,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(name=>document.querySelector('satzfunk-player[label*="'+name+'"]')?.narrationBinding&&document.querySelector('#page-viewport')?.dataset.layout==='ready',playerName,{timeout:32000});
   await page.evaluate(async name=>{const player=document.querySelector('satzfunk-player[label*="'+name+'"]');const key=name==='Teatro'?'teatro':'prologue';const score=await (await fetch('/estate/media/first-readings/'+key+'-midi2-reading-score.private.json')).json();player.narrationBinding.setMode('cursor');const entry=score.events.find(e=>e.timeSeconds>5);if(entry)player.seek((entry.timeSeconds+entry.endSeconds)/2)},playerName);
   await page.waitForTimeout(180);
   await page.addScriptTag({path:axe});
   const r=await page.evaluate(async()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']},resultTypes:['violations','incomplete']}));
   record.violations=r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(x=>x.target.join(' ')).slice(0,3)}));
   record.incomplete=r.incomplete.map(v=>v.id);
   record.pageErrors=pageErrors;
   record.control=await page.evaluate(name=>{const p=document.querySelector('satzfunk-player[label*="'+name+'"]');return {mode:p.narrationBinding?.mode,cursor:document.querySelectorAll('.linotype-audio-cursor-mark').length,selects:[...document.querySelectorAll('select')].map(x=>x.getAttribute('aria-label')).filter(Boolean)}},playerName);
   record.pass=record.violations.length===0&&pageErrors.length===0;
  }catch(e){record.failure=String(e).slice(0,360);record.pass=false}
  if(!record.pass)errors++;
  results.push(record);console.log(JSON.stringify(record));await page.close();
 }await browser.close();
}
console.log(JSON.stringify({total:results.length,failures:errors,scan:'axe-core WCAG 2 A/AA and 2.1 A/AA',physicalDevice:false}));
if(process.env.REPORT_FILE)fs.writeFileSync(process.env.REPORT_FILE,JSON.stringify({schema:'fountain.press.midi2.ax.acceptance.v1',physicalDevice:false,results},null,2)+'\n');
if(errors)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});