const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=__dirname,base='https://192.168.8.50:8243',abstracts=JSON.parse(fs.readFileSync(path.join(root,'essay-abstracts.json'),'utf8')).items;
const overrides={
 '/estate/':'index.html',
 '/estate/assets/linotype/reading-first-app.js':'reading-first-app.js',
 '/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css',
 '/estate/assets/linotype/reading-first-press-engine.js':'press-viewport-engine.js'
};
async function run(){
 const browser=await webkit.launch({headless:true});const results=[],screens=[];
 for(const [profile,width,height] of [['landscape',1180,820],['portrait',820,1180],['phone',390,844]]){
  const ctx=await browser.newContext({viewport:{width,height}});
  if(!process.env.LIVE)await ctx.route('**/*',r=>{
   const u=new URL(r.request().url()),file=overrides[u.pathname];
   return file&&u.host==='192.168.8.50:8243'?r.fulfill({status:200,body:fs.readFileSync(path.join(root,file)),contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html'}):r.continue();
  });
  const pg=await ctx.newPage(),errors=[];pg.on('pageerror',e=>errors.push(e.message));pg.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  for(const [slug,entry] of Object.entries(abstracts)){
   const vol='essay--'+slug;
   await pg.goto(base+'/estate/#/read/'+vol,{waitUntil:'domcontentloaded'});
   try{await pg.waitForFunction(v=>document.querySelector('#page-viewport')?.dataset.volume===v&&document.querySelector('#page-viewport')?.dataset.layout==='ready',vol,{timeout:14000})}catch(e){const state=await pg.evaluate(()=>({status:document.querySelector('#reader-status')?.textContent,layout:document.querySelector('#page-viewport')?.dataset.layout}));throw Error(profile+' '+slug+' failed '+JSON.stringify({state,errors}))}
   let state=await pg.evaluate(()=>{
    const v=document.querySelector('#page-viewport'),s=document.querySelector('#source-flow');
    const summary=s.querySelector('[data-editorial-role="abstract"]');
    const visibleSummary=v.querySelector('.frame-essay-abstract');
    const heroSrc=s.querySelector('.frame-essay-hero img')?.getAttribute('src');
    const story=s.querySelector('.book-prose');
    const all=[...s.querySelectorAll('figure img')];
    return {layout:v.dataset.layout,pages:v.dataset.pages,summary:summary?.textContent,summaryVisible:visibleSummary?.textContent,
    heroSrc,figs:all.map(i=>({src:i.getAttribute('src'),width:i.getAttribute('width'),height:i.getAttribute('height')})),
    storyCharacters:story?.textContent.length,firstParagraph:story?.querySelector('p')?.textContent.slice(0,90),
    sourceFigureIndex:heroSrc?[...s.children].findIndex(x=>x.classList.contains('book-art-leaf')):-1,
    sourceStoryIndex:[...s.children].findIndex(x=>x.classList.contains('book-chapter-text'))};
   });
   assert.equal(state.summary,entry.summary);
   assert.equal(state.summaryVisible,entry.summary,profile+' abstract should appear on initial page '+slug);
   assert.ok(state.storyCharacters>650,slug+' manuscript missing');
   assert.equal(!!state.heroSrc,entry.share==='source-image');
   assert.equal(errors.length,0,profile+' '+slug+' '+errors.join('; '));
   if(entry.share==='source-image'){
    assert.ok(state.sourceFigureIndex>0 && state.sourceStoryIndex>state.sourceFigureIndex,'hero must follow abstract before prose');
    if(!await pg.locator('#page-viewport .frame-essay-hero').count()){
     await pg.locator('#next-page').click();
     await pg.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
    }
    const image=await pg.evaluate(()=>{
     const fig=document.querySelector('#page-viewport figure.frame-essay-hero');
     const img=fig?.querySelector('img');const i=img?.getBoundingClientRect();const a=fig?.closest('.linotype-area')?.getBoundingClientRect();
     return {found:!!fig,width:i?.width,height:i?.height,source:[img?.naturalWidth,img?.naturalHeight],
       fit:fig?.dataset.essayHeroFit,within:i&&a?i.left>=a.left-2&&i.right<=a.right+2&&i.bottom<=a.bottom+2:false};
    });
    assert.equal(image.fit,'balanced',slug+' hero fit');
    assert.ok(image.within&&image.width>115&&image.height>100,slug+' hero clipping or thumbnail '+JSON.stringify(image));
    state.image=image;
   }else{
    assert.equal(state.figs.length,1,'archival screenshot evidence retained in manuscript');
   }
   results.push({profile,slug,...state});
   if(profile==='landscape'){
    await pg.screenshot({path:path.join(root,'essay-opening-'+slug+'.png')});
    screens.push(slug);
   }
   console.log('PASS',profile,slug,state.pages,entry.share);
  }
  await ctx.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(root,process.env.LIVE?'essay-abstracts-live.json':'essay-abstracts-preflight.json'),JSON.stringify({origin:base,sourceInterception:!process.env.LIVE,results,errors:0},null,2)+'\n');
}
run().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
