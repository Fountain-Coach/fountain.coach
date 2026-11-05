#!/usr/bin/env node
// Verify a candidate revised source inside the EXACT existing owner-WLAN Reader.
// This uses Playwright route fulfilment for /estate/ only; no alternate Reader,
// compositor, media module, publishing server or staging activation.
const fs=require('node:fs');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {chromium,webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const path=require('node:path');
const root=__dirname;
const essay='essay--what-makes-a-page-modern';
const source=fs.readFileSync(path.join(root,'stage-v147-combined.html'));
const receipt=JSON.parse(fs.readFileSync(path.join(root,'stage-v147-combined-receipt.json')));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(sha(source),receipt.revisedReaderRootSHA256);
const base='https://192.168.8.50:8243';
const expectedPlateCount=receipt.renderedFigureCount;
const results=[];
async function run(type,label){
  const browser=await type.launch(label==='chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{headless:true});
  try{
    for(const [w,h] of [[820,1120],[1200,860],[390,844]]){
      const ctx=await browser.newContext({viewport:{width:w,height:h},ignoreHTTPSErrors:true,colorScheme:'light'});
      const errors=[]; const mediaWarnings=[];
      await ctx.route('**/estate/',async route=>{
        if(route.request().url().startsWith(base+'/estate/')){
          await route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:source});
        } else await route.continue();
      });
      const page=await ctx.newPage();
      page.on('pageerror',e=>errors.push('js '+e.message));
      page.on('requestfailed',q=>{ const why=q.failure()?.errorText||''; if(q.url().includes('/estate/media/first-readings/') && (why.includes('ERR_ABORTED')||why.includes('ERR_TOO_MANY_RETRIES'))) {mediaWarnings.push(why); return;} errors.push('fail '+q.url()+' '+why); });
      page.on('response',res=>{if(res.status()>=400)errors.push('http '+res.status()+' '+res.url());});
      try{
        await page.goto(base+'/estate/#/read/'+essay,{waitUntil:'domcontentloaded',timeout:15000});
        try{
          await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id
            &&document.querySelector('#page-viewport')?.dataset.layout==='ready',essay,{timeout:12000});
        }catch(error){
          console.log('PAGE_DIAGNOSTIC',label,w,h,JSON.stringify(await page.evaluate(()=>({
            address:location.href,title:document.title,body:document.body?.innerText?.slice(0,350),
            viewport:document.querySelector('#page-viewport')?.dataset,
            template:!!document.querySelector('template[data-reader-volume="essay--what-makes-a-page-modern"]'),
            scripts:[...document.querySelectorAll('script[src]')].map(x=>x.src).slice(-12)
          }))),JSON.stringify(errors));
          throw error;
        }
        const state=await page.evaluate(id=>{
          const tpl=document.querySelector('template[data-reader-volume="'+id+'"]');
          const viewport=document.querySelector('#page-viewport');
          const figures=[...tpl.content.querySelectorAll('figure[data-source-block^="what-makes-a-page-modern.plate."]')];
          const visibleFigures=[...viewport.querySelectorAll('figure[data-source-block^="what-makes-a-page-modern.plate."]')];
          const imageFigures=visibleFigures.map(f=>f.querySelector('img')).filter(Boolean);
          const headings=[...tpl.content.querySelectorAll('p.frame-subheading')].map(x=>x.textContent.trim());
          const blocks=[...tpl.content.querySelectorAll('[data-source-block]')];
          const nonempty=blocks.filter(b=>b.textContent.trim());
          return {
            volume:viewport.dataset.volume,layout:viewport.dataset.layout,
            pages:Number(viewport.dataset.pages),images:figures.length,
            visibleImages:imageFigures.length,
            readyImages:imageFigures.filter(x=>x.complete && x.naturalWidth>0).length,
            headings,sourceBlocks:blocks.length,nonemptyBlocks:nonempty.length,
            bookParent:document.querySelector('#reader-parent')?.getAttribute('data-reader-target'),
            widthOverflow:document.documentElement.scrollWidth-window.innerWidth,
            revision:tpl.content.querySelector('[data-source-work-sha256]')?.getAttribute('data-source-work-sha256')??tpl.content.querySelector('[data-source-work-sha256]')?.dataset.sourceWorkSha256,
            hero:!!tpl.content.querySelector('figure[data-source-block="what-makes-a-page-modern.plate.question"]')
          };
        },essay);
        assert.equal(state.volume,essay);
        assert.equal(state.layout,'ready');
        assert.equal(state.images,expectedPlateCount,state.images+' vs '+expectedPlateCount);
        assert.equal(state.readyImages,state.visibleImages);
        console.log('COMPOSED',label,w,h,'pages',state.pages,'figures',state.images,'visible',state.visibleImages,'ready',state.readyImages);
        assert.ok(state.pages>=15,JSON.stringify(state));
        assert.ok(state.widthOverflow<=3,JSON.stringify(state));
        assert.ok(state.headings.includes('Self Out Loud'),JSON.stringify(state.headings));
        assert.ok(state.headings.includes('The writer is the first actor'),JSON.stringify(state.headings));
        assert.ok(state.headings.includes('Conditions of composition'));
        assert.equal(state.bookParent,'essays',JSON.stringify(state));
        assert.equal(errors.length,0,errors.join('\n'));
        const save=path.join('/tmp','self-out-loud-'+label+'-'+w+'x'+h+'.png');
        await page.screenshot({path:save,fullPage:false});
        // The existing book gallery, Teatro, source-linked routes remain unchanged.
        await page.goto(base+'/estate/#/read/library',{waitUntil:'domcontentloaded'});
        await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='library'
          && document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
        const gallery=await page.locator('.reader-gallery-scroll[data-collection="essays"] .reader-gallery-item').count();
        assert.equal(gallery,6);
        await page.goto(base+'/estate/#/read/teatro',{waitUntil:'domcontentloaded'});
        await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='teatro'
          && document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
        console.log('PASS',label,w,h,'pages',state.pages,'headings',state.headings.length,
          'figures',state.images,'blocks',state.sourceBlocks,'gallery',gallery,'screenshot',save);
        results.push({label,width:w,height:h,...state,gallery,errors,mediaWarnings});
      }finally{
        await ctx.close();
      }
    }
  }finally{await browser.close();}
}
(async()=>{
  await run(chromium,'chromium');
  await run(webkit,'webkit');
  fs.writeFileSync(path.join(root,'stage-v147-browser-acceptance.json'),
    JSON.stringify({schema:'fountain.press.self-out-loud-browser-proof.v1',results},null,2)+'\n');
})().catch(err=>{console.error(err);process.exitCode=1;});
