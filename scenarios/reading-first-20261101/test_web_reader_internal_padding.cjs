const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {webkit,chromium}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const root=path.resolve(__dirname,'../../site/essays/what-makes-a-page-modern/assets');
const svg=path.join(root,'reader.svg');
const content=fs.readFileSync(svg,'utf8');
const expected='A page is not a container in which words happen to rest.';
const sourceRoot=__dirname;
const main=fs.readFileSync(path.join(sourceRoot,'index.html'),'utf8');
const origin='http://192.168.8.50:8200';
async function check(engine,label){
 const browser=await engine.launch(label==='chrome'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
 try{
  const page=await browser.newPage({viewport:{width:820,height:1120}});
  await page.goto('file://'+svg,{waitUntil:'load'});
  const result=await page.evaluate(()=>{
    const all=[...document.querySelectorAll('text')];
    const panels=[...document.querySelectorAll('rect')];
    const rect=p=>{const b=p.getBBox();return {left:b.x,right:b.x+b.width,top:b.y,bottom:b.y+b.height}};
    return {
      panels:panels.map(rect),
      text:all.map(t=>({content:t.textContent,x:Number(t.getAttribute('x')),y:Number(t.getAttribute('y')),...rect(t)}))
    };
  });
  assert.equal(result.panels.length,2);
  const [left,right]=result.panels;
  const headings=result.text.filter(t=>/SATZSPIEGEL|WEB READER/.test(t.content));
  const l=result.text.filter(t=>t.x===156);
  const r=result.text.filter(t=>t.x===744&&!/WEB READER/.test(t.content));
  assert.equal(l.length,3);
  assert.equal(r.length,3);
  assert.equal(l.map(t=>t.content).join(' '),expected);
  assert.equal(r.map(t=>t.content).join(' '),expected);
  assert.equal(r.length,3);
  assert.equal(headings[1].x,744);
  for(const [rect,group] of [[left,result.text.filter(t=>t.x<300)],[right,result.text.filter(t=>t.x>=700)]]){
    for(const line of group){
      assert.ok(line.left>=rect.left+28,label+' glyph out of left frame '+JSON.stringify({line,rect}));
      assert.ok(line.right<=rect.right-30,label+' glyph crossed right frame '+JSON.stringify({line,rect}));
      assert.ok(line.top>=rect.top+8,label+' glyph above frame '+JSON.stringify({line,rect}));
      assert.ok(line.bottom<=rect.bottom-8,label+' glyph below frame '+JSON.stringify({line,rect}));
    }
  }
  // The longest right line's visual inset is balanced with its 34-unit left inset.
  const rightInset=Math.min(...r.map(t=>right.right-t.right));
  const leftInset=r[0].left-right.left;
  assert.ok(Math.abs(rightInset-leftInset)<=16,label+' excessive inside asymmetry '+JSON.stringify({leftInset,rightInset}));
  console.log('SVG_INTERNAL_FRAME_PASS',label,{leftInset,rightInset,lines:r.map(t=>t.content)});
  await page.close();
  const ctx=await browser.newContext({viewport:{width:820,height:1120}});
  await ctx.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.host==='192.168.8.50:8200'&&url.pathname==='/estate/')
      return route.fulfill({status:200,contentType:'text/html',body:main});
    if(url.pathname==='/estate/essays/what-makes-a-page-modern/assets/reader.svg')
      return route.fulfill({status:200,contentType:'image/svg+xml',body:content});
    try{const res=await route.fetch();return await route.fulfill({response:res})}
    catch(e){if(/Target closed|disposed/i.test(String(e)))return;throw e;}
  });
  const reader=await ctx.newPage();
  const errors=[];
  reader.on('pageerror',e=>errors.push(e.message));
  await reader.goto(origin+'/estate/#/read/essay--what-makes-a-page-modern',{waitUntil:'domcontentloaded'});
  await reader.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
  let found=null,pages=Number(await reader.locator('#page-viewport').getAttribute('data-pages'));
  for(let i=0;i<pages;i++){
    const onPage=await reader.evaluate(()=>{
      const figure=document.querySelector('.linotype-sheet figure[data-source-block="what-makes-a-page-modern.plate.reader"]');
      const image=figure?.querySelector('img');
      if(!image)return null;
      const p=image.getBoundingClientRect();
      const a=figure.closest('.linotype-area').getBoundingClientRect();
      return {natural:image.complete&&image.naturalWidth>0,figLeft:p.left,paragraphLeft:a.left,width:p.width,available:a.width};
    });
    if(onPage){
      assert.ok(onPage.natural,label+' reader.svg not rendered');
      assert.ok(Math.abs(onPage.figLeft-onPage.paragraphLeft)<1.3,label+' reader.svg not type-area aligned');
      assert.ok(onPage.width<=onPage.available+1);
      found={folio:i+1,...onPage};
      if(process.env.CAPTURE_READER_PREVIEW==='1'){
        await reader.screenshot({path:'/Users/benedikteickhoff/Developer/.modern-page-existing-reader-QA/webreader-v144-'+label+'.png'});
      }
      break;
    }
    if(i<pages-1)await reader.locator('#next-page').click();
  }
  assert.ok(found,label+' reader.svg not found in full composed essay');
  assert.deepEqual(errors,[]);
  console.log('REAL_READER_FLOW_PASS',label,{pages,...found});
  await ctx.unrouteAll({behavior:'ignoreErrors'});
  await ctx.close();
 }finally{await browser.close();}
}
(async()=>{await check(webkit,'webkit');await check(chromium,'chrome')})().catch(e=>{console.error(e);process.exitCode=1;});
