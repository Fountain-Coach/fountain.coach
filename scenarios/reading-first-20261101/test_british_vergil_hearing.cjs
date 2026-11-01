const path=require('path');
const os=require('os');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE || path.join(os.homedir(),'Developer','fcis.fountain.coach','node_modules','playwright'));
const fs=require('fs');
const base=__dirname;
const media=path.join(process.env.SATZFUNK_ROOT||path.join(os.homedir(),'Developer','Satzfunk'),'drafts','voice-editions','on-continuity-fb57e1726c81-cedar','reading.mp3');
const live=process.argv.includes('--live');
const url='https://192.168.8.50:8243/estate/#/read/continuity';
(async()=>{
  const manifest=fs.readFileSync(base+'/british-vergil-edition.private.json');
  const wav=fs.readFileSync(media);
  const failures=[];
  for(const [name,engine] of [['Chromium',chromium],['WebKit',webkit]]){
    const browser=await engine.launch(name==="Chromium"?{headless:true,executablePath:"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}:{headless:true});
    for(const [size,width,height] of [['landscape',1180,820],['portrait',820,1180],['phone',390,844]]){
      const page=await browser.newPage({viewport:{width,height},ignoreHTTPSErrors:true});
      const errors=[];
      page.on('pageerror',error=>errors.push(error.message));
      page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text())});
      try {
        if(!live)await page.route('**/estate/media/vergil-on-continuity/**',route=>{
          const isAudio=route.request().url().endsWith('/cedar.mp3');
          return route.fulfill({status:200,contentType:isAudio?'audio/mpeg':'application/json',
            headers:{'Access-Control-Allow-Origin':'*','Accept-Ranges':'bytes'},
            body:isAudio?wav:manifest});
        });
        await page.goto(url,{waitUntil:'domcontentloaded',timeout:18000});
        await page.waitForFunction(()=>document.getElementById('page-viewport')?.dataset.layout==='ready',{timeout:12000});
        if(!live)await page.addScriptTag({path:base+'/british-vergil-hearing.mjs'});
        await page.waitForSelector('.reader-hearing-button:not([hidden])',{timeout:20000});
        const label=await page.locator('.reader-hearing-button').getAttribute('aria-label');
        if(!label.includes('AI-generated British Vergil'))throw Error('Missing voice disclosure');
        await page.locator('.reader-hearing-button').click();
        await page.waitForFunction(()=>{const p=document.querySelector('satzfunk-player');return p?.state?.paused===false},{timeout:15000});
        await page.waitForTimeout(1200);
        const heard=await page.evaluate(()=>{const p=document.querySelector('satzfunk-player');return {state:p?.state,
         range:document.querySelector('.reader-hearing-rail input')?.value,
         page:document.getElementById('page-count').textContent,
         overflow:document.documentElement.scrollHeight>innerHeight||document.documentElement.scrollWidth>innerWidth}});
        if(heard.state.currentTime<=0||heard.overflow)throw Error('Not playing or layout overflow: '+JSON.stringify(heard));
        await page.locator('.reader-hearing-button').click();
        await page.waitForFunction(()=>document.querySelector('satzfunk-player')?.state?.paused===true);
        const result={name,size,live,label,heard,errors};
        console.log('VERGIL_TEST',JSON.stringify(result));
        if(errors.length)failures.push(result);
      } catch(error) {
        failures.push({name,size,live,error:error.message,errors});
        console.error('VERGIL_FAILURE',name,size,error.message,JSON.stringify(errors));
      }
      await page.close();
    }
    await browser.close();
  }
  console.log('VERGIL_FAILURES',failures.length);
  if(failures.length)process.exitCode=1;
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
