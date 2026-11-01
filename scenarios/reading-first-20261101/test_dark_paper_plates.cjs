const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert').strict;
const base='https://192.168.8.50:8243';
const files={'/estate/':'index.html','/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css',
 '/estate/assets/linotype/reading-first-app.js':'reading-first-app.js','/estate/assets/linotype/reading-first-press-engine.js':'press-viewport-engine.js'};
(async()=>{
 const browser=await webkit.launch({headless:true}),report=[];
 for(const [profile,width,height] of [['landscape',1180,820],['phone',390,844]]){
  const ctx=await browser.newContext({viewport:{width,height},colorScheme:'light'});
  if(!process.env.LIVE)await ctx.route('**/*',r=>{
   const u=new URL(r.request().url()),file=files[u.pathname];
   if(file&&u.host==='192.168.8.50:8243')return r.fulfill({status:200,body:fs.readFileSync(path.join(__dirname,file)),contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html'});
   return r.continue();
  });
  const p=await ctx.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(base+'/estate/#/read/library',{waitUntil:'domcontentloaded'});
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
  const collect=()=>p.evaluate(()=>{
   const body=getComputedStyle(document.body),squares=[...document.querySelectorAll('.reader-gallery-square')];
   return {theme:document.documentElement.dataset.theme,background:body.backgroundColor,
     color:body.color,figs:squares.map(square=>{const img=square.querySelector('img');
      return {src:img.getAttribute('src'),paper:getComputedStyle(square).backgroundColor,
       fit:getComputedStyle(img).objectFit,filter:getComputedStyle(img).filter,alt:img.alt};}),
     footer:document.querySelector('.frame-controls').getBoundingClientRect().bottom,
     page:document.querySelector('#page-viewport').getAttribute('aria-label')};
  });
  const light=await collect();
  await p.locator('#reader-theme').click();
  await p.waitForFunction(()=>document.documentElement.dataset.theme==='dark');
  const dark=await collect();
  assert.equal(light.figs.length,37);assert.equal(dark.figs.length,37);
  assert.notEqual(light.background,dark.background);
  for(let i=0;i<37;i++){
   assert.equal(light.figs[i].src,dark.figs[i].src);
   assert.equal(dark.figs[i].paper,'rgb(245, 242, 233)');
   assert.equal(dark.figs[i].fit,'contain');
   assert.equal(dark.figs[i].filter,'none');
   assert.ok(dark.figs[i].alt);
  }
  assert.ok(Math.abs(dark.footer-height)<18);
  await p.screenshot({path:path.join(__dirname,'bookshelf-dark-plate-'+profile+'.png')});
  // Check source-art folio uses the same deliberate print plate.
  await p.goto(base+'/estate/#/read/essay--the-door-is-a-score',{waitUntil:'domcontentloaded'});
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
  const art=await p.evaluate(()=>{
   const img=document.querySelector('#page-viewport figure.frame-essay-hero img');
   return img?{paper:getComputedStyle(img).backgroundColor,filter:getComputedStyle(img).filter}:null;
  });
  if(art)assert.equal(art.paper,'rgb(245, 242, 233)');
  if(art)assert.equal(art.filter,'none');
  // Focus semantics for image entries (no unreadable hyperlink underline).
  await p.goto(base+'/estate/#/read/library',{waitUntil:'domcontentloaded'});
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
  const accessibility=await p.locator('.reader-gallery-item').first().evaluate(el=>({
   name:el.getAttribute('aria-label'),tag:el.tagName,tabIndex:el.tabIndex
  }));
  assert.equal(accessibility.tag,'BUTTON');assert.ok(accessibility.name.startsWith('Read '));
  assert.deepEqual(errors,[]);
  const entry={profile,illustrations:dark.figs.length,darkPlate:dark.figs[0].paper,sourceStable:light.figs[0].src===dark.figs[0].src,
    sourceFolioPlate:art,accessibility,errors};
  report.push(entry);console.log('PASS',JSON.stringify(entry));
  await ctx.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(__dirname,process.env.LIVE?'dark-paper-live.json':'dark-paper-preflight.json'),JSON.stringify({origin:base,intercepted:!process.env.LIVE,results:report,errors:0},null,2)+'\n');
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
