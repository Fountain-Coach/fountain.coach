const fs=require('node:fs');const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
(async()=>{
 const browser=await webkit.launch({headless:true});
 for(const [w,h] of [[820,1120],[390,844]]){
  const context=await browser.newContext({viewport:{width:w,height:h},ignoreHTTPSErrors:true});
  const html=fs.readFileSync(__dirname+'/stage-v148-specimen.html');
  await context.route('**/estate/',route=>route.fulfill({status:200,body:html,contentType:'text/html'}));
  const page=await context.newPage();
  await page.goto('https://192.168.8.50:8243/estate/#/read/essay--what-makes-a-page-modern',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:15000});
  const pages=Number(await page.locator('#page-viewport').getAttribute('data-pages'));
  let found=[];
  for(let i=1;i<=pages;i++){
   const state=await page.evaluate(()=>{
     const v=document.querySelector('#page-viewport');
     return {head:v.innerText.slice(0,170),
        specimens:[...v.querySelectorAll('figure[data-typographic-specimen]')].map(x=>({name:x.dataset.typographicSpecimen,rect:x.getBoundingClientRect().toJSON(),text:x.textContent.slice(0,180),labels:[...x.querySelectorAll('[role=note]')].map(y=>y.innerText),figY:x.getBoundingClientRect().y,captionY:x.querySelector('figcaption')?.getBoundingClientRect().y}))};
   });
   if(state.specimens.length){
     const p='/tmp/stage-on-stage-PREVIEW-'+w+'-leaf-'+i+'.png';
     await page.screenshot({path:p});
     console.log('SPECIMEN',w,i,JSON.stringify(state),p);found.push(i);
   }
   if(i<pages)await page.locator('#next-page').click();
  }
  if(found.length!==2)throw Error('Expected two distinct specimen leaves: '+JSON.stringify(found));
  await context.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});