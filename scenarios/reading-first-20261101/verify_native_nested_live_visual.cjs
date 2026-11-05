#!/usr/bin/env node
// Browser observes actual deployed WLAN release. No route fulfilment.
const assert=require('node:assert/strict');
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
(async()=>{
 const browser=await webkit.launch({headless:true});
 try{
  const ctx=await browser.newContext({viewport:{width:820,height:1120},ignoreHTTPSErrors:true});
  const page=await ctx.newPage();
  await page.goto('https://192.168.8.50:8243/estate/#/read/essay--what-makes-a-page-modern');
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:18000});
  const figures=[];
  const count=Number(await page.locator('#page-viewport').getAttribute('data-pages'));
  for(let leaf=1;leaf<=count;leaf++){
    const items=await page.evaluate(()=>[...document.querySelectorAll('#page-viewport figure[data-typographic-specimen]')].map(f=>{
      const r=f.getBoundingClientRect(),a=f.closest('.linotype-area').getBoundingClientRect();
      const p=f.querySelector('.linotype-specimen-text'),c=getComputedStyle(f);
      return {kind:f.dataset.typographicSpecimen,from:p.dataset.sourceFrom,to:p.dataset.sourceTo,
        padding:c.padding,left:r.left,right:r.right,parentLeft:a.left,parentRight:a.right,
        actualImages:f.querySelectorAll('img,svg,canvas').length};
    }));
    for(const item of items){
      assert.ok(item.left>=item.parentLeft-1.5&&item.right<=item.parentRight+1.5);
      assert.equal(item.actualImages,0);
      assert.ok(parseFloat(item.padding)>0);
      const filename='/tmp/press-native-nested-live-'+item.kind+'-'+leaf+'.png';
      await page.screenshot({path:filename});
      console.log('LIVE_VISUAL',filename,JSON.stringify(item));
      figures.push(item.kind);
    }
    if(leaf<count)await page.locator('#next-page').click();
  }
  assert.deepEqual(figures,['classical','modern']);
  console.log('NESTED_VISUAL_WITNESS_OK',count,'leaves, exactly 2 source-composed inner settings');
  await ctx.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
