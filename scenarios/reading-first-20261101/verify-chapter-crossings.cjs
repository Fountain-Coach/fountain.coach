const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await webkit.launch({headless:true});
 for(const [label,width,height] of [['spread',1180,820],['phone',390,844]]){
  const p=await b.newPage({viewport:{width,height}});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto('https://192.168.8.50:8243/estate/#/read/essay--reframe-and-the-business-value-of-the-estate',{waitUntil:'domcontentloaded'});
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
  const first='essay--reframe-and-the-business-value-of-the-estate';
  const second='essay--teatro-an-unfinished-composition';
  let turns=0;
  while(turns++<50){
   const current=await p.locator('#page-viewport').getAttribute('data-volume');
   if(current===second)break;
   await p.locator('#next-page').click();
   await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
  }
  assert.equal(await p.locator('#page-viewport').getAttribute('data-volume'),second,'next chapter');
  console.log('BEFORE PREV',await p.evaluate(()=>({volume:document.querySelector('#page-viewport').dataset.volume,count:document.querySelector('#page-count').textContent,disabled:document.querySelector('#previous-page').disabled})));
  await p.locator('#previous-page').click();
  await p.waitForTimeout(750);
  console.log('AFTER PREV',await p.evaluate(()=>({volume:document.querySelector('#page-viewport').dataset.volume,count:document.querySelector('#page-count').textContent,disabled:document.querySelector('#previous-page').disabled})));
  await p.waitForFunction(name=>document.querySelector('#page-viewport')?.dataset.volume===name&&document.querySelector('#page-viewport')?.dataset.layout==='ready',first);
  const count=await p.locator('#page-count').textContent();
  assert.ok(!/^1(–2)?\s*\//.test(count),'previous chapter returns at its end');
  await p.getByLabel('Choose publication').selectOption('solstice-reading-01--vergil');
  await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='solstice-reading-01--vergil'&&document.querySelector('#page-viewport')?.dataset.layout==='ready');
  let count2=0;
  while(count2++<40){
   if(await p.locator('#page-viewport').getAttribute('data-volume')==='solstice-reading-01--preface')break;
   await p.locator('#next-page').click();
   await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready');
  }
  assert.equal(await p.locator('#page-viewport').getAttribute('data-volume'),'solstice-reading-01--preface','solstice sequence');
  assert.equal(errors.length,0);
  console.log('PASS',label,'essay turns',turns,'return',count,'solstice turns',count2);
  await p.close();
 }
 await b.close();
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
