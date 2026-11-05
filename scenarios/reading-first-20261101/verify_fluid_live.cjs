#!/usr/bin/env node
// Independent actual v150 HTTPS Reader check. NO route substitution.
// Verify exact served Press assets and the measured, source-bound reading flow.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium,webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const r=__dirname,base='https://192.168.8.50:8243';
const source=fs.readFileSync(path.join(r,'../../site/essays/what-makes-a-page-modern/specimen-source.txt'),'utf8').trimEnd();
const scriptSHA='52f30f9fd36f3f1ccb24bd833b14f91289d270df394f8418a77cc672ee7c5342';
const cssSHA='8e175ccbdfdd71e506979772059c72fcfb85de8d3daa366a34544ccc7d4502e6';
const rootSHA='8ca2c693f4ae275f16331f3989790016a7f0ba3d0a2c2dc34d58e3a4f432478f';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const profiles=[[390,844],[600,950],[740,1050],[820,1120],[900,1280],[1024,1366],[1200,1500],[1200,860],[1440,900]];
const result=[];
const ready=id=>document.querySelector('#page-viewport')?.dataset.volume===id && document.querySelector('#page-viewport')?.dataset.layout==='ready';
(async()=>{
 for(const [browserName,driver] of [['webkit',webkit],['chromium',chromium]]){
  const browser=await driver.launch(browserName==='webkit'?{headless:true}:{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try{
   for(const [width,height] of profiles){
    const context=await browser.newContext({viewport:{width,height},ignoreHTTPSErrors:true});
    const errors=[];
    // Actual served candidate; no local HTML, JS or CSS is substituted.
    const expected=[
      ['/estate/', '8ca2c693f4ae275f16331f3989790016a7f0ba3d0a2c2dc34d58e3a4f432478f'],
      ['/estate/assets/linotype/reading-first-press-engine.js','52f30f9fd36f3f1ccb24bd833b14f91289d270df394f8418a77cc672ee7c5342'],
      ['/estate/assets/linotype/reading-first-press-frame.css','8e175ccbdfdd71e506979772059c72fcfb85de8d3daa366a34544ccc7d4502e6']
    ];
    for(const [uri,want]of expected){
      const response=await context.request.get(base+uri,{timeout:12000});
      assert.equal(response.status(),200,uri);
      const digest=crypto.createHash('sha256').update(await response.body()).digest('hex');
      assert.equal(digest,want,'Live stage digest mismatch '+uri);
    }
    const page=await context.newPage();
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',msg=>{if(msg.type()==='error'&&msg.text().includes('Fountain Press reader failure'))errors.push(msg.text())});
    try{
     await page.goto(base+'/estate/#/read/essay--what-makes-a-page-modern',{waitUntil:'domcontentloaded',timeout:16000});
     await page.waitForFunction(ready,'essay--what-makes-a-page-modern',{timeout:20000});
     const count=Number(await page.locator('#page-viewport').getAttribute('data-pages'));
     assert.ok(count>=8&&count<=150,'leaf count '+count);
     const segments=[],firsts={},figures=new Set(),pages=[];
     for(let i=0;i<count;i++){
      const p=await page.evaluate(()=>{
       const v=document.querySelector('#page-viewport'),a=[...v.querySelectorAll('.linotype-sheet')];
       const rect=el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
       const sheets=a.map(s=>({sheet:rect(s),area:rect(s.querySelector('.linotype-area')),
         font:getComputedStyle(s.querySelector('.linotype-area')).fontSize,
         elements:[...s.querySelector('.linotype-area').children].map((el,i)=>({
           index:i,tag:el.tagName,type:el.className,figure:el.getAttribute('data-typographic-specimen'),
           text:el.innerText?.slice(0,110),rect:rect(el)
         }))}));
       return {
        viewport:rect(v),
        mode:v.dataset.mode,
        overflow:document.documentElement.scrollWidth-window.innerWidth,
        sheets,
        figureIDs:[...v.querySelectorAll('figure[data-source-block^="what-makes-a-page-modern.plate."]')].map(x=>x.dataset.sourceBlock),
        parts:[...v.querySelectorAll('figure[data-typographic-specimen]')].map(f=>{
          const container=f.closest('.linotype-area'),s=f.querySelector('.linotype-specimen-setting'),p=f.querySelector('.linotype-specimen-text');
          return{kind:f.dataset.typographicSpecimen,from:+p.dataset.sourceFrom,to:+p.dataset.sourceTo,
             text:p.textContent,frame:rect(f),area:rect(container),paragraph:rect(p),setting:rect(s),
             inset:getComputedStyle(f).paddingInlineStart,
             font:getComputedStyle(p).fontSize,
             imageCount:f.querySelectorAll('img,svg,canvas').length,
             previous: f.previousElementSibling?{
               tag:f.previousElementSibling.tagName,text:f.previousElementSibling.textContent?.slice(0,100),
               rect:rect(f.previousElementSibling)}:null
          };
        })
       };
      });
      assert.ok(p.overflow<=3,JSON.stringify({browserName,width,height,i,overflow:p.overflow}));
      for(const f of p.parts){
       assert.ok(f.area.width>0&&f.frame.width>0);
       assert.ok(Math.abs(f.frame.width-f.area.width)<2,JSON.stringify(f));
       assert.ok(f.paragraph.x>f.frame.x+4&&f.paragraph.right<f.frame.right-4,'lost inner type inset '+JSON.stringify(f));
       assert.ok(f.frame.bottom<=f.area.bottom+2,'nested type clipped '+JSON.stringify({i,f}));
       assert.equal(f.imageCount,0);
       segments.push({...f,leaf:i+1});
       if(!firsts[f.kind]){firsts[f.kind]={...f,leaf:i+1,context:p.sheets};await page.screenshot({path:'/tmp/fluid-LIVE-'+browserName+'-'+width+'-'+height+'-'+f.kind+'.png'});}
      }
      for(const id of p.figureIDs)figures.add(id);
      pages.push({leaf:i+1,...p});
      if(i<count-1){
       const before=await page.locator('#page-viewport').innerText();
       await page.locator('#next-page').click();
       await page.waitForFunction(before=>document.querySelector('#page-viewport')?.innerText!==before,before,{timeout:8000});
      }
     }
     for(const kind of ['classical','modern']){
      const part=segments.filter(p=>p.kind===kind).sort((a,b)=>a.from-b.from);
      assert.ok(part.length,'missing '+kind);
      assert.equal(part[0].from,0);
      for(let n=1;n<part.length;n++)assert.equal(part[n].from,part[n-1].to);
      assert.equal(part.at(-1).to,source.length);
      assert.equal(part.map(p=>p.text).join(''),source);
     }
     assert.equal(figures.size,12);
     assert.deepEqual(errors,[]);
     const first=firsts.classical;
     const entry={browserName,width,height,pages:count,mode:pages[0].mode,
      outerWidth:firsts.classical.context[0]?.sheet.width,
      measure:firsts.classical.area.width,innerWidth:firsts.classical.paragraph.width,
      typeInset:firsts.classical.paragraph.x-firsts.classical.frame.x,
      classicalLeaf:firsts.classical.leaf,modernLeaf:firsts.modern.leaf,
      classicalPrevious:first.previous,fragments:segments.length,errors};
     console.log('FLUID_LIVE_PASS',JSON.stringify(entry));
     result.push(entry);
    }catch(e){
     console.error('FLUID_FAILURE',browserName,width,height,e.message);console.error('ERRORS',errors);
     throw e;
    }finally{await context.close()}
   }
  }finally{await browser.close()}
 }
 for(const browserName of ['webkit','chromium']){
   const list=result.filter(x=>x.browserName===browserName&&x.mode==='single').sort((a,b)=>a.width-b.width);
   for(let i=1;i<list.length;i++){
     assert.ok(list[i].measure>list[i-1].measure+10,JSON.stringify({browserName,prior:list[i-1],next:list[i]}));
     assert.ok(list[i].innerWidth>list[i-1].innerWidth+5);
   }
 }
 const file=path.join(r,'fluid-nested-LIVE-proof.json');
 fs.writeFileSync(file,JSON.stringify({schema:'fountain.press.fluid-nested-v1',profiles:result},null,2)+'\n');
 console.log('VERIFIED',result.length,'source-bound ACTUAL-LIVE v150 Reader profiles',file);
})().catch(e=>{console.error(e);process.exitCode=1});
