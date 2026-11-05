#!/usr/bin/env node
// Bounded acceptance: same actual Fountain Press reader/HTML and source,
// with only the candidate compositor JS substituted during nonactive preview.
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium,webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const base='https://192.168.8.50:8243',path='/estate/#/read/essay--what-makes-a-page-modern';
const script=fs.readFileSync('/Users/benedikteickhoff/Developer/.linotype-fluid-nested-20261105/scenarios/reading-first-20261101/reading-first-press-engine.js');
const sha=value=>crypto.createHash('sha256').update(value).digest('hex');
assert.equal(sha(script),'52f30f9fd36f3f1ccb24bd833b14f91289d270df394f8418a77cc672ee7c5342',
  'Wrong baseline Reader source used for the mobile preservation comparison');
const profiles=[[390,844],[820,1120],[1194,834],[1200,860],[1280,720],[1440,900],[1920,1080]];
const results=[];
const collapsed=a=>a.filter((x,i)=>i===0||a[i-1]!==x);
async function read(browser,w,h,candidate){
 const ctx=await browser.newContext({viewport:{width:w,height:h},ignoreHTTPSErrors:true});
 if(!candidate)await ctx.route('**/estate/assets/linotype/reading-first-press-engine.js',
    route=>route.fulfill({status:200,contentType:'text/javascript',body:script}));
 else{
    // For the actual-v151 branch, no route interception. Check served bytes.
    const resp=await ctx.request.get(base+'/estate/assets/linotype/reading-first-press-engine.js');
    assert.equal(resp.status(),200);
    assert.equal(sha(await resp.body()),
     'e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a',
     'HTTPS v151 Press engine bytes do not match admitted candidate');
 }
 const p=await ctx.newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));
 p.on('console',m=>{if(m.type()==='error'&&m.text().includes('Fountain Press reader failure'))errors.push(m.text())});
 try{
  await p.goto(base+path,{waitUntil:'domcontentloaded',timeout:18000});
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='essay--what-makes-a-page-modern',{timeout:24000});
  const total=Number(await p.locator('#page-viewport').getAttribute('data-pages'));
  assert.ok(total>=8&&total<=85,'unexpected folio count '+total);
  const collection=[],figures=new Set(),leaves=[],headingOrphans=[];
  const logical=total;
  const turnCount=(await p.locator('#page-viewport .linotype-sheet').count())===2?Math.ceil(total/2):total;
  for(let i=1;i<=turnCount;i++){
   const snapshot=await p.evaluate(()=>{
     const v=document.querySelector('#page-viewport');
     return [...v.querySelectorAll('.linotype-sheet')].map(s=>{
       const a=s.querySelector('.linotype-area'),r=a.getBoundingClientRect();
       const kids=[...a.children].filter(x=>x.offsetHeight>0&&!x.hidden);
       const last=kids.at(-1);
       return {folio:s.querySelector('.linotype-folio')?.textContent,
         html:a.innerHTML,
         fills:last?(last.getBoundingClientRect().bottom-r.top)/r.height:0,
         ids:kids.map(x=>x.dataset.sourceBlock).filter(Boolean),
         figs:[...a.querySelectorAll('figure[data-source-block]')].map(x=>({id:x.dataset.sourceBlock,imageWidth:x.querySelector('img')?.getBoundingClientRect().width||null,hasImg:!!x.querySelector('img')})),
         lastHeading:last?.classList.contains('frame-subheading')||false,
         overflow:document.documentElement.scrollWidth-window.innerWidth};
     });
   });
   for(const s of snapshot){
     assert.ok(s.overflow<=3,JSON.stringify({w,h,i,overflow:s.overflow}));
     if(s.lastHeading)headingOrphans.push({folio:s.folio,turn:i});
     for(const f of s.figs)figures.add(f.id);
     collection.push(...s.ids);
     leaves.push({turn:i,...s});
   }
   if(i<turnCount){
      const before=await p.locator('#page-viewport').innerText();
      await p.locator('#next-page').click();
      await p.waitForFunction(previous=>document.querySelector('#page-viewport')?.innerText!==previous,before,{timeout:8000});
   }
  }
  assert.deepEqual(errors,[],'reader error '+JSON.stringify({w,h,errors}));
  assert.equal(figures.size,12,'12 original author illustrations remain accessible');
  return {w,h,candidate,total,ids:collapsed(collection),orphans:headingOrphans,leaves,errors,
    mode:leaves[0].folio&&leaves[0].turn===1?leaves.length/turnCount===2?'spread':'single':'unknown'};
 }finally{await ctx.close()}
}
(async()=>{
 for(const [browserName,driver]of[['webkit',webkit],['chromium',chromium]]){
  const browser=await driver.launch(browserName==='chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
  try{
   for(const [w,h]of profiles){
    const before=await read(browser,w,h,false),after=await read(browser,w,h,true);
    // Non-negotiable: no dropped/reordered writer-source blocks or images.
    assert.deepEqual(after.ids,before.ids,'source block sequence changed: '+w+'x'+h);
    if(w<=820&&h>=w){
       assert.equal(after.total,before.total,'compact view folio count changed');
       assert.deepEqual(after.leaves.map(x=>x.html),before.leaves.map(x=>x.html),
         'compact iPhone/iPad composition changed: '+w+'x'+h);
    }
    if(w===1440&&h===900){
      // The photo's problem: before the deferred proof illustration, one
      // facing leaf was ~41% filled and the next had been placed elsewhere.
      const target=after.leaves.find(x=>x.folio?.includes('008'));
      assert.ok(target,'missing photographed recto');
      assert.ok(target.fills>.8,'photographed underfilled recto was not repaired');
      assert.ok(target.figs.some(f=>f.id?.endsWith('.plate.proof')),
        'authored proof did not enter the same visible spread');
      assert.equal(after.orphans.length,0,'a subheading is orphaned at a page foot');
    }
    results.push({browserName,w,h,oldLeaves:before.total,newLeaves:after.total,
      oldOrphans:before.orphans.length,newOrphans:after.orphans.length,
      imageIdentitiesPreserved:true,sourceOrderPreserved:true,
      compactMarkupIdentical:w<=820&&h>=w});
    console.log('SPREAD_LIVE_ACCEPTED',JSON.stringify(results.at(-1)));
   }
  }finally{await browser.close()}
 }
 const file=__dirname+'/semantic-spread-LIVE-proof.json';
 fs.writeFileSync(file,JSON.stringify({schema:'fountain.press.semantic-spread-balance.v1',sourceEngineSHA256:'e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a',results},null,2)+'\n');
 console.log('VERIFIED',results.length,'profiles',file);
})().catch(e=>{console.error('FAILED',e);process.exitCode=1});
