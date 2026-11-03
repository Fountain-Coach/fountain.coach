const path=require('path'),os=require('os');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
const axe=require.resolve('axe-core/axe.min.js',{paths:[path.join(os.homedir(),'Developer/fcis.fountain.coach')]});
(async()=>{let fails=0;for(const [name,engine] of [['Chrome',chromium],['WebKit',webkit]]){
 const b=await engine.launch(name==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 for(const viewport of [{width:1024,height:768},{width:390,height:844}]){
  const p=await b.newPage({viewport,ignoreHTTPSErrors:true});
  const errors=[];p.on('pageerror',e=>errors.push(String(e)));
  const result={browser:name,viewport:viewport.width+'x'+viewport.height};
  try{
    await p.goto((process.env.STAGING_ORIGIN||'https://192.168.8.50:8243')+'/estate/#/read/publication-notes',{waitUntil:'domcontentloaded'});
    await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes' && document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
    await p.addScriptTag({path:axe});
    const scan=await p.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
    result.violations=scan.violations.map(v=>v.id);
    result.incomplete=scan.incomplete.map(v=>v.id);
    result.heading=await p.locator('#page-viewport .linotype-area h2').first().textContent();
    result.linkLabel=await p.locator('#page-viewport a[href="https://status.fountain.coach/"]').first().textContent();
    result.pass=result.violations.length===0&&result.heading==='Publication Notes'&&result.linkLabel.includes('Legal')&&errors.length===0;
  }catch(e){result.failure=String(e).slice(0,340);result.pass=false}
  result.errors=errors;console.log(JSON.stringify(result));if(!result.pass)fails++;await p.close();
 }await b.close();
}console.log('V138_ADDENDUM_AX',4-fails,'/ 4');if(fails)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});