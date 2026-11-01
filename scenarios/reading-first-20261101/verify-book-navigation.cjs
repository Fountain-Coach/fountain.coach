const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await webkit.launch({headless:true});
 const records=[];
 for(const [profile,width,height] of [['landscape',1180,820],['phone',390,844]]){
  const p=await browser.newPage({viewport:{width,height}});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto('https://192.168.8.50:8243/estate/',{waitUntil:'domcontentloaded'});
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  const initial=await p.evaluate(()=>{
   const area=document.querySelector('#page-viewport');
   const a=area.querySelector('.frame-book-cover a');
   return {volume:area.dataset.volume,anchors:area.querySelectorAll('a').length,linkDecoration:getComputedStyle(a).textDecorationLine,
     bookTitles:[...area.querySelectorAll('.frame-cover-name')].map(x=>x.textContent),heading:area.querySelector('h2')?.textContent};
  });
  assert.deepEqual(initial.bookTitles,['Essays','Solstice (WT)']);
  assert.equal(initial.linkDecoration,'none');
  await p.locator('#page-viewport [data-reader-target="essays"]').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='essays',{timeout:15000});
  assert.equal(await p.locator('#source-flow .frame-toc-item').count(),0);
  const title=await p.locator('#source-flow h2').textContent();assert.equal(title,'Essays');
  await p.locator('#next-page').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='essay--reframe-and-the-business-value-of-the-estate'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  const first=await p.locator('#source-flow h2').textContent();
  // Turn back across the chapter boundary, without a browser navigation.
  await p.locator('#previous-page').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='essays'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  await p.locator('.brand').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  await p.locator('#page-viewport [data-reader-target="solstice"]').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  assert.equal(await p.locator('#source-flow .frame-toc-item').count(),0);
  await p.locator('#next-page').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice-reading-01'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  await p.locator('#next-page').click();
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice-reading-01--vergil'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  // Use the accessible jump control without painting a link directory.
  await p.getByLabel('Choose publication').selectOption('solstice-reading-01--2025-12-22-anweisung-an-den-schmerz');
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice-reading-01--2025-12-22-anweisung-an-den-schmerz'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  const work=await p.evaluate(()=>{
   const a=document.querySelector('#page-viewport');
   const title=document.querySelector('#source-flow h2')?.textContent,im=a.querySelector('img');
   const clips=[...a.querySelectorAll('.linotype-area')].some(x=>x.scrollHeight>x.clientHeight+2);
   return {title,illustration:im?.naturalWidth||0,clipped:clips,underlineCount:[...a.querySelectorAll('a')].filter(x=>getComputedStyle(x).textDecorationLine.includes('underline')).length};
  });
  console.log('WORK',profile,JSON.stringify(work));
  assert.ok(work.title?.includes('Anweisung an den Schmerz'));
  assert.ok(work.illustration>0);
  assert.equal(work.underlineCount,0);
  assert.equal(work.clipped,false);
  assert.deepEqual(errors,[]);
  await p.screenshot({path:__dirname+'/book-nav-first-work-'+profile+'.png'});
  records.push({profile,initial,first,work,errors});
  console.log('PASS',JSON.stringify(records.at(-1)));
  await p.close();
 }
 await browser.close();
 require('fs').writeFileSync(__dirname+'/book-navigation-evidence.json',JSON.stringify({runs:records,failures:0},null,2)+'\n');
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
