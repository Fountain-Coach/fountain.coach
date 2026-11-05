#!/usr/bin/env node
// Candidate on actual v148 private Reader origin, only three source-owned
// assets substituted. No second compositor, no alternative app or publication.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {chromium,webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const root=__dirname,base='https://192.168.8.50:8243';
const source=fs.readFileSync(path.join(root,'stage-v149-before.html'));
const unscaled=fs.readFileSync(path.join(root,'reading-first-press-engine.js'),'utf8');
const probe='const font=parseFloat(getComputedStyle(this.viewport).fontSize)||18;';
assert.ok(unscaled.includes(probe),'Cannot locate measured page-font input');
const script=Buffer.from(unscaled.replace(probe,'const font=34; // stress-only enlarged page-font input'));
const style=Buffer.concat([fs.readFileSync(path.join(root,'reading-first-press-frame.css')),Buffer.from('\n#page-viewport{font-size:34px!important}\n')]);
const canonical=fs.readFileSync(path.join(root,'../../site/essays/what-makes-a-page-modern/specimen-source.txt'),'utf8').trimEnd();
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(sha(source),'8ca2c693f4ae275f16331f3989790016a7f0ba3d0a2c2dc34d58e3a4f432478f');
const volume='essay--what-makes-a-page-modern';
const profiles=[[390,844],[820,1120]];
const results=[];
async function inspect(browser,label,w,h) {
 const ctx=await browser.newContext({viewport:{width:w,height:h},ignoreHTTPSErrors:true});
 const errors=[],warnings=[];
 await ctx.route('**/estate/',route=>route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:source}));
 await ctx.route('**/estate/assets/linotype/reading-first-press-engine.js',route=>route.fulfill({status:200,contentType:'text/javascript',body:script}));
 await ctx.route('**/estate/assets/linotype/reading-first-press-frame.css',route=>route.fulfill({status:200,contentType:'text/css',body:style}));
 const page=await ctx.newPage();
 page.on('pageerror',e=>errors.push('JS '+e.message));
 page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')console.log('BROWSER_CONSOLE',label,w,h,m.type(),m.text().slice(0,600));});
 page.on('requestfailed',q=>{const m=q.failure()?.errorText||'';if(q.url().includes('/estate/media/first-readings/')&&(m.includes('ERR_ABORTED')||m.includes('ERR_TOO_MANY_RETRIES')||m.toLowerCase()==='cancelled')){warnings.push(m);return;}errors.push('REQ '+q.url()+' '+m);});
 page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url());});
 try{
   await page.goto(base+'/estate/#/read/'+volume,{waitUntil:'domcontentloaded',timeout:16000});
   try{
     await page.waitForFunction(id=>{
        const v=document.querySelector('#page-viewport');return v?.dataset.volume===id&&v?.dataset.layout==='ready';
     },volume,{timeout:12000});
   }catch(error){
     console.log('NOT_READY',label,w,h,JSON.stringify(await page.evaluate(()=>({
       url:location.href,title:document.title,
       v:document.querySelector('#page-viewport')?.dataset,
       stage:document.querySelector('.linotype-stage')?.dataset,
       body:document.body?.innerText?.slice(0,650),
       scriptSrc:[...document.scripts].map(x=>x.src).slice(-9),
       figures:document.querySelectorAll('figure[data-typographic-specimen]').length
     }))),JSON.stringify(errors));
     throw error;
   }
   const total=Number(await page.locator('#page-viewport').getAttribute('data-pages'));
   assert.ok(total>=10&&total<=150,total);
   const chapters=[],segments=[],allFigures=new Set(),stat=[];
   for(let i=1;i<=total;i++){
     const state=await page.evaluate(()=>{
       const v=document.querySelector('#page-viewport'),area=v.querySelector('.linotype-area');
       const st=v.querySelector('.linotype-sheet');
       const r=a=>a.getBoundingClientRect().toJSON();
       const frames=[...v.querySelectorAll('figure[data-typographic-specimen]')];
       const figures=[...v.querySelectorAll('figure[data-source-block^="what-makes-a-page-modern.plate."]')].map(x=>x.dataset.sourceBlock);
       const layout=frames.map(f=>{
         const p=f.querySelector('.linotype-specimen-text');
         const setting=f.querySelector('.linotype-specimen-setting');
         const ra=r(f),rp=r(p),rs=r(setting);
         const ar=r(f.closest('.linotype-area'));
         return {
           kind:f.dataset.typographicSpecimen,
           from:Number(p?.dataset.sourceFrom),to:Number(p?.dataset.sourceTo),
           unit:p?.dataset.sourceUnitId,setting:p?.dataset.sourceSetting,text:p?.textContent,
           frame:ra,area:ar,paragraph:rp,settingRect:rs,
           imageCount:f.querySelectorAll('img,svg,canvas').length,
           explicitSize:!!(f.style.width||f.style.height),
           imageSourceAttr:!!f.querySelector('[width],[height]'),
           widthOverflow:f.scrollWidth-f.clientWidth,
           sourceOverflow:f.scrollHeight-f.clientHeight,
           font:Number.parseFloat(getComputedStyle(p).fontSize),
           areaFont:Number.parseFloat(getComputedStyle(f.closest('.linotype-area')).fontSize),
           lineHeight:getComputedStyle(p).lineHeight,
           textAlign:getComputedStyle(p).textAlign
         };
       });
       return {text:v.innerText,figures,layout,
        overflow:document.documentElement.scrollWidth-window.innerWidth,
        areaRect:area?r(area):null,stageRect:st?r(st):null};
     });
     assert.ok(state.overflow<=3,label+' '+w+'x'+h+' leaf '+i+' horizontal overflow '+state.overflow);
     for(const f of state.layout){
       assert.ok(f.frame.left>=f.area.left-1.5 && f.frame.right<=f.area.right+1.5,'frame outside parent text measure '+JSON.stringify({i,kind:f.kind,frame:f.frame,area:f.area}));
       assert.ok(f.paragraph.left>=f.frame.left+1.5&&f.paragraph.right<=f.frame.right-1.5,'inner text outside frame '+JSON.stringify({i,f}));
       assert.ok(f.frame.bottom<=f.area.bottom+1.5,'nested setting clipped below actual leaf '+JSON.stringify({i,f}));
       assert.equal(f.imageCount,0,'type must not be rendered as an image');
       assert.equal(f.explicitSize,false,'no author-fixed width or height on nested type');
       assert.ok(Math.abs(f.font-f.areaFont)<1.5,'type did not inherit actual folio font '+JSON.stringify({i,f}));
       assert.ok(f.widthOverflow<=1.5&&f.sourceOverflow<=1.5,'nested type overflow');
       assert.ok(f.to>f.from,'empty specimen fragment');
       segments.push({...f,leaf:i});
     }
     for(const f of state.figures)allFigures.add(f);
     chapters.push(state.text);
     stat.push({leaf:i,...state,layout:state.layout.map(x=>({kind:x.kind,from:x.from,to:x.to,frame:x.frame,area:x.area,font:x.font}))});
     if(i<total){
       const before=state.text;
       await page.locator('#next-page').click();
       await page.waitForFunction(before=>document.querySelector('#page-viewport')?.innerText!==before,before,{timeout:8000});
     }
   }
   assert.equal(allFigures.size,12,'every original figure identity must be reached');
   for(const kind of ['classical','modern']){
     const rows=segments.filter(x=>x.kind===kind).sort((a,b)=>a.from-b.from);
     assert.ok(rows.length>=1,'missing '+kind);
     assert.equal(rows[0].from,0);
     for(let j=1;j<rows.length;j++)assert.equal(rows[j].from,rows[j-1].to,'fragment gap '+kind);
     assert.equal(rows.at(-1).to,canonical.length,'lost source characters '+kind);
     assert.equal(rows.map(x=>x.text).join(''),canonical,'mutated specimen text '+kind);
   }
   // At 34px a legitimate paragraph can be split between folios and a page
   // header inserted between its two halves. Test source recovery from
   // addressed fragments and the Press integrity check, not a substring of
   // concatenated visible page text (which would yield a false negative).
   assert.ok(segments.length>=2);
   assert.equal(segments.filter(s=>s.kind==='classical').map(s=>s.text).join(''),canonical);
   assert.equal(segments.filter(s=>s.kind==='modern').map(s=>s.text).join(''),canonical);
   assert.deepEqual(errors,[],'stage regressions '+JSON.stringify(errors));
   console.log('FLUID_STRESS_PASS',label,w,h,'leaves',total,'specimenParts',segments.length,
     'figureIDs',allFigures.size,'font',segments[0]?.font,
     'sourceSHA',sha(Buffer.from(canonical,'utf8')));
   results.push({browser:label,width:w,height:h,leaves:total,
     specimenParts:segments.map(x=>({kind:x.kind,from:x.from,to:x.to,leaf:x.leaf,font:x.font})),
     figures:allFigures.size,errors,warnings});
   const dest='/tmp/nested-specimen-'+label+'-'+w+'x'+h+'-last.png';
   await page.screenshot({path:dest});
   return stat;
 }catch(e){
   console.error('PROFILE_FAILURE',label,w,h,e);
   console.log('PAGE_ERRORS',errors);
   throw e;
 }finally{await ctx.close();}
}
(async()=>{
 for(const [label,klass]of [['chromium',chromium],['webkit',webkit]]){
   const b=await klass.launch(label==='chromium'?
     {headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
   try{for(const [w,h]of profiles)await inspect(b,label,w,h);}
   finally{await b.close();}
 }
 fs.writeFileSync(path.join(root,'fluid-nested-STRESS-proof.json'),JSON.stringify({schema:'fountain.press.native-nested-specimen.v1',results},null,2)+'\n');
 console.log('VERIFIED',results.length,'source-preserving paginated profiles');
})().catch(e=>{console.error(e);process.exitCode=1});
