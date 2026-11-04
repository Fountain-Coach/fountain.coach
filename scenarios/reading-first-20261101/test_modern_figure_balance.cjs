const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {webkit,chromium}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const root=__dirname,assetRoot=path.resolve(root,'../../site/essays/what-makes-a-page-modern/assets');
const ORIGIN='http://192.168.8.50:8200';
const base='estate/essays/what-makes-a-page-modern/assets/';
const volume='essay--what-makes-a-page-modern';
async function verify(browserType,name){
 const browser=await browserType.launch(name==='chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 try{
  for(const [width,height] of [[820,1120],[1200,860],[390,844]]){
   const ctx=await browser.newContext({viewport:{width,height}});
   await ctx.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.host==='192.168.8.50:8200'){
     const files={
      '/estate/':path.join(root,'index.html'),
      '/estate/assets/linotype/reading-first-app.js':path.join(root,'reading-first-app.js'),
     };
     let file=files[url.pathname];
     if(url.pathname.startsWith('/'+base))file=path.join(assetRoot,path.basename(url.pathname));
     if(file)return route.fulfill({status:200,body:fs.readFileSync(file),contentType:file.endsWith('.svg')?'image/svg+xml':file.endsWith('.js')?'text/javascript':'text/html'});
    }
    try{const res=await route.fetch();return await route.fulfill({response:res});}
    catch(error){if(/Request context disposed|Target closed/i.test(String(error)))return;throw error;}
   });
   const page=await ctx.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(ORIGIN+'/estate/#/read/'+volume,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(v=>document.querySelector('#page-viewport')?.dataset.volume===v&&document.querySelector('#page-viewport')?.dataset.layout==='ready',volume,{timeout:25000});
   const number=Number(await page.locator('#page-viewport').getAttribute('data-pages'));
   const found=new Set();
   for(let i=0;i<number;i++){
    const metrics=await page.evaluate(()=>{
     const areas=[...document.querySelectorAll('.linotype-sheet .linotype-area')];
     return areas.flatMap(area=>{
       const x=area.getBoundingClientRect().left;
       return [...area.querySelectorAll('figure[data-source-block^="what-makes-a-page-modern.plate."]')].map(f=>{
         const fig=f.getBoundingClientRect();
         const img=f.querySelector('img').getBoundingClientRect();
         const cap=f.querySelector('figcaption').getBoundingClientRect();
         return {id:f.dataset.sourceBlock,x0:x,xFig:fig.left,xImg:img.left,xCap:cap.left,
           usable:area.clientWidth,figWidth:fig.width,
           captionWidth:cap.width,imgWidth:img.width}
       });
     });
    });
    for(const m of metrics||[]){
      for(const key of ['xFig','xImg','xCap']) assert.ok(Math.abs(m[key]-m.x0)<=1.3,name+' '+width+' '+m.id+' '+key+' '+JSON.stringify(m));
      assert.ok(m.captionWidth<=m.usable+1);
      assert.ok(m.imgWidth<=m.usable+1);
      found.add(m.id);
    }
    if(i<number-1)await page.locator('#next-page').click();
   }
   assert.equal(found.size,12,name+' '+width+' only '+found.size+'/12 illustrations '+[...found].join(','));
   assert.deepEqual(errors,[]);
   console.log('PASSED',name,width,height,number,'folios / 12 aligned illustrations / margins and captions');
   await ctx.unrouteAll({behavior:'ignoreErrors'});await ctx.close();
  }
 }finally{await browser.close()}
}
(async()=>{
 await verify(webkit,'webkit');
 await verify(chromium,'chrome');
})().catch(e=>{console.error(e);process.exitCode=1})
