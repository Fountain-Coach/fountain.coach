const path=require('path'),os=require('os'),fs=require('fs');
const {chromium,webkit}=require(path.join(os.homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
const ORIGIN=process.env.TEST_ORIGIN||'http://127.0.0.1:4292';
const targets=[
 'library','essays','teatro','essay--the-door-is-a-score','solstice-reading-01--vergil',
 'solstice-reading-01--preface','solstice-reading-01--2025-12-22-anweisung-an-den-schmerz',
 'essay--teatro-an-unfinished-composition','publication-notes'
];
if(process.env.READER_LEDGER){
 const works=JSON.parse(fs.readFileSync(process.env.READER_LEDGER)).works.filter(x=>x.status==='current-essay'||x.status==='current-first-reading');
 if(works.length!==35)throw Error('Wrong current-publication ledger');
 for(const id of [...works.map(x=>x.id),'essay--to-read-is-not-to-remember'])if(!targets.includes(id))targets.push(id);
}
if(process.env.TEST_TARGETS)targets.splice(0,targets.length,...process.env.TEST_TARGETS.split(','));
const candidate=process.env.CANDIDATE_ROOT&&path.resolve(process.env.CANDIDATE_ROOT);
async function fixture(page){
 if(!candidate)return;
 await page.route(new URL(ORIGIN).origin+'/**',async route=>{
  const u=new URL(route.request().url()),relative=decodeURIComponent(u.pathname).replace(/^\//,'');
  let file=path.resolve(candidate,relative||'index.html');
  if(!file.startsWith(candidate+path.sep))return route.fulfill({status:403,body:'outside candidate'});
  if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
  if(!fs.existsSync(file))return route.fulfill({status:404,body:'unlisted candidate file'});
  const mime={'.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json','.svg':'image/svg+xml','.mp3':'audio/mpeg','.jpg':'image/jpeg','.png':'image/png'}[path.extname(file)]||'application/octet-stream';
  return route.fulfill({status:200,contentType:mime,body:fs.readFileSync(file)});
 });
}
(async()=>{
 if(process.env.TEST_CACHE_ISOLATION){
  const results=[],browser=await webkit.launch({headless:true});
  const stale=fs.readFileSync(path.join(__dirname,'../build/public-release-v141-social/estate/assets/linotype/reading-first-app.js'));
  for(const landscape of [false,true])for(const target of ['/', '/estate/read/essays/', '/estate/read/essay--what-makes-a-page-modern/']){
   const page=await browser.newPage({viewport:landscape?{width:1180,height:820}:{width:820,height:1180},isMobile:true,hasTouch:true,
    userAgent:'Mozilla/5.0 (iPad; CPU OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/480.0.0.0.1;FBDV/iPad13,4;FBSN/iPadOS;FBSV/17.6;FBID/tablet;FBLC/en_US;IABMV/1]'});
   await fixture(page);
   let staleHits=0;const errors=[],requests=[];
   await page.route(new URL(ORIGIN).origin+'/estate/assets/linotype/reading-first-app.js',route=>{
    staleHits++;return route.fulfill({status:200,contentType:'text/javascript',body:stale});
   });
   await page.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Denied','SecurityError')}}));
   page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
   const result={target,landscape,evidence:candidate?'candidate-fixture':'actual-public-HTTPS',device:'emulated iPad WebKit with Facebook UA; not physical Facebook'};
   try{
    const response=await page.goto(ORIGIN+target+'?fbclid=cache-isolation-regression',{waitUntil:'load'});
    if(response.status()!==200)throw Error('HTTP '+response.status());
    if(process.env.TEST_EXPECT_BLANK){
     await page.waitForFunction(()=>document.querySelector('#page-viewport')&& !document.querySelector('#page-viewport').textContent.trim());
     if(staleHits!==1||!errors.includes('Editorial collection inventory changed'))throw Error('Expected stale-script startup failure was not reproduced');
     result.reproducedBlank=true;
    }else{
     await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:28000});
     if(staleHits)throw Error('Reader still requests collision-prone old app URL');
     if(!requests.some(u=>/reading-first-app\.[a-f0-9]{64}\.js$/.test(u)))throw Error('Content-addressed app was not requested');
     if(errors.length)throw Error(errors.join('; '));
     const text=await page.locator('#page-viewport').innerText();if(text.trim().length<30)throw Error('Blank composed viewport');
     result.volume=await page.locator('#page-viewport').getAttribute('data-volume');
     await page.reload({waitUntil:'load'});
     await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
     result.reload=true;
     if(target==='/'&&!landscape&&process.env.SCREENSHOT_PATH)await page.screenshot({path:process.env.SCREENSHOT_PATH});
    }
    result.pass=true;
   }catch(e){result.error=String(e);result.pass=false}
   result.staleHits=staleHits;result.errors=errors;results.push(result);console.log(JSON.stringify(result));await page.close();
  }
  await browser.close();
  const report={evidence:candidate?'candidate-fixture':'actual-public-HTTPS',passed:results.filter(r=>r.pass).length,total:results.length,results};
  if(process.env.REPORT_PATH)fs.writeFileSync(process.env.REPORT_PATH,JSON.stringify(report,null,2)+'\n');
  process.exitCode=report.passed===report.total?0:1;return;
 }
 const all=[],failures=[];
 for(const [browserName,engine] of [['Chrome',chromium],['WebKit',webkit]]){
  const launch=browserName==='Chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true};
  const browser=await engine.launch(launch);
  for(const id of targets){
   const page=await browser.newPage({viewport:{width:900,height:1200}});
   await fixture(page);
   const errors=[],missing=[];
   page.on('pageerror',e=>errors.push(e.message));
   page.on('response',r=>{if(r.status()>=400)missing.push(r.status()+' '+r.url())});
   const url=ORIGIN+'/estate/read/'+id+'/';
   const expected=['solstice','solstice-reading-01'].includes(id)?'first-readings':id;
   const result={browser:browserName,id,url};
   try{
    const response=await page.goto(url,{waitUntil:'load'});
    if(response.status()!==200)throw Error('direct page HTTP '+response.status());
    await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id &&
          document.querySelector('#page-viewport')?.dataset.layout==='ready',expected,{timeout:28000});
    const meta=await page.locator('meta[property="og:image"]').getAttribute('content');
    if(!meta?.endsWith('/'+id+'.jpg'))throw Error('wrong social image '+meta);
    const title=await page.title();
    const ogtitle=await page.locator('meta[property="og:title"]').getAttribute('content');
    if(!title.includes(ogtitle.replace(/^The /,'')))throw Error('runtime title does not match work '+title+' vs '+ogtitle);
    await page.waitForLoadState('networkidle',{timeout:20000});
    await page.reload({waitUntil:'load'});
    await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id &&
          document.querySelector('#page-viewport')?.dataset.layout==='ready',expected,{timeout:28000});
    if(page.url().split('?')[0]!==url)throw Error('reload unexpectedly changed stable work URL '+page.url());
    await page.waitForLoadState('networkidle',{timeout:20000});
    result.direct=true;result.reload=true;result.meta=meta;
   }catch(e){result.error=String(e)}
   result.errors=errors;result.missing=missing.slice(0,3);
   result.pass=!result.error&&errors.length===0&&missing.length===0;
   if(!result.pass)failures.push(result);
   all.push(result);console.log(JSON.stringify(result));
   await page.close();
  }
  const page=await browser.newPage({viewport:{width:1024,height:768}});
  await fixture(page);
  const r={browser:browserName,kind:'navigation-and-legacy'};
  try{
   await page.goto(ORIGIN+'/estate/#/read/teatro',{waitUntil:'load'});
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
 if(process.env.READER_LEDGER){
  const browser=await webkit.launch({headless:true});
  const page=await browser.newPage({viewport:{width:820,height:1120}});await fixture(page);
  const r={kind:'v152-current-membership-and-archive',evidence:candidate?'candidate-fixture':'actual-public-HTTPS'};
  try{
   await page.goto(ORIGIN+'/estate/read/essays/',{waitUntil:'load'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
   const state=await page.evaluate(()=>({
    essays:JSON.parse(document.querySelector('#reader-gallery-data').textContent).collections.essays.map(n=>n.id),
    archivedSelectable:!!document.querySelector('#reader-section option[value="essay--to-read-is-not-to-remember"]'),
    modernPresent:!!document.querySelector('template[data-reader-volume="essay--what-makes-a-page-modern"]'),
    archivedNote:document.querySelector('template[data-reader-volume="essay--to-read-is-not-to-remember"]').content.textContent.includes('Archived')
   }));
   const unique=[...new Set(state.essays.filter(id=>id.startsWith('essay--')))];
   if(unique.length!==5||unique.includes('essay--to-read-is-not-to-remember')||state.archivedSelectable||!state.modernPresent||!state.archivedNote)throw Error(JSON.stringify(state));
   r.pass=true;r.currentEssays=unique.length;r.archiveRetained=true;
  }catch(e){r.error=String(e);r.pass=false;failures.push(r)}
  all.push(r);console.log(JSON.stringify(r));await browser.close();
 }
 if(process.env.REPORT_PATH)fs.writeFileSync(process.env.REPORT_PATH,JSON.stringify({evidence:candidate?'candidate-fixture':'actual-public-HTTPS',passed:all.length-failures.length,total:all.length,results:all},null,2)+'\n');
 console.log('PRESS_SOCIAL_BROWSER',candidate?'CANDIDATE_FIXTURE':'LIVE',all.length-failures.length,'/',all.length);
 process.exitCode=failures.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
