const path=require('path'),os=require('os');
const {chromium,webkit}=require(path.join(os.homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
const ORIGIN=process.env.TEST_ORIGIN||'http://127.0.0.1:4292';
const targets=[
 'library','essays','teatro','essay--the-door-is-a-score','solstice-reading-01--vergil',
 'solstice-reading-01--preface','solstice-reading-01--2025-12-22-anweisung-an-den-schmerz',
 'essay--teatro-an-unfinished-composition','publication-notes'
];
(async()=>{
 const all=[],failures=[];
 for(const [browserName,engine] of [['Chrome',chromium],['WebKit',webkit]]){
  const launch=browserName==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true};
  const browser=await engine.launch(launch);
  for(const id of targets){
   const page=await browser.newPage({viewport:{width:900,height:1200}});
   const errors=[],missing=[];
   page.on('pageerror',e=>errors.push(e.message));
   page.on('response',r=>{if(r.status()>=400)missing.push(r.status()+' '+r.url())});
   const url=ORIGIN+'/estate/read/'+id+'/';
   const expected=['solstice','solstice-reading-01'].includes(id)?'first-readings':id;
   const result={browser:browserName,id,url};
   try{
    const response=await page.goto(url,{waitUntil:'domcontentloaded'});
    if(response.status()!==200)throw Error('direct page HTTP '+response.status());
    await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id &&
          document.querySelector('#page-viewport')?.dataset.layout==='ready',expected,{timeout:28000});
    const meta=await page.locator('meta[property="og:image"]').getAttribute('content');
    if(!meta?.endsWith('/'+id+'.jpg'))throw Error('wrong social image '+meta);
    const title=await page.title();
    const ogtitle=await page.locator('meta[property="og:title"]').getAttribute('content');
    if(!title.includes(ogtitle.replace(/^The /,'')))throw Error('runtime title does not match work '+title+' vs '+ogtitle);
    await page.reload({waitUntil:'domcontentloaded'});
    await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id &&
          document.querySelector('#page-viewport')?.dataset.layout==='ready',expected,{timeout:28000});
    if(page.url().split('?')[0]!==url)throw Error('reload unexpectedly changed stable work URL '+page.url());
    result.direct=true;result.reload=true;result.meta=meta;
   }catch(e){result.error=String(e)}
   result.errors=errors;result.missing=missing.slice(0,3);
   result.pass=!result.error&&errors.length===0&&missing.length===0;
   if(!result.pass)failures.push(result);
   all.push(result);console.log(JSON.stringify(result));
   await page.close();
  }
  const page=await browser.newPage({viewport:{width:1024,height:768}});
  const r={browser:browserName,kind:'navigation-and-legacy'};
  try{
   await page.goto(ORIGIN+'/estate/#/read/teatro',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'
      && document.querySelector('#page-viewport')?.dataset.volume==='teatro',{timeout:28000});
   r.legacyHash=true;
   if(!new URL(page.url()).pathname.endsWith('/estate/read/teatro/'))throw Error('Legacy bookmark did not normalize on opening: '+page.url());
   await page.locator('#reader-section').selectOption('solstice-reading-01--vergil');
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice-reading-01--vergil'&&
      document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:28000});
   r.canonical=page.url();
   if(!new URL(page.url()).pathname.endsWith('/estate/read/solstice-reading-01--vergil/'))throw Error('work URL did not acquire stable pathname');
   await page.reload();
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice-reading-01--vergil'&&
      document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:28000});
   r.reload=true;
  }catch(e){r.error=String(e)}
  r.pass=!r.error;if(!r.pass)failures.push(r);
  all.push(r);console.log(JSON.stringify(r));await page.close();
  await browser.close();
 }
 console.log('PRESS_SOCIAL_BROWSER',all.length-failures.length,'/',all.length);
 process.exitCode=failures.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
