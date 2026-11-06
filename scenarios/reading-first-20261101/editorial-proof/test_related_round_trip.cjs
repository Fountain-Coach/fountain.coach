// Verify real published related-reading navigation returns to the exact,
// source-addressed editorial proof on the *active* owner-WLAN HTTPS Reader.
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const origin='https://192.168.8.50:8243/estate/';
const volume='essay--a-sound-must-earn-its-place';
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--no-sandbox','--ignore-certificate-errors']});
 try{
  const page=await browser.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewport({width:768,height:1024});
  await page.goto(origin+'#/read/'+volume,{waitUntil:'domcontentloaded',timeout:20000});
  await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id && document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000},volume);
  const semanticBefore=await page.evaluate(()=>({
    volume:document.getElementById('page-viewport').dataset.volume,
    anchor:location.hash,
    first:document.querySelector('#source-flow [data-source-block^="a-sound"]')?.dataset.sourceBlock
  }));
  await page.evaluate(()=>document.querySelector('[data-reader-info]')?.click());
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='publication-notes'&&document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:25000});
  const link=await page.evaluate(()=>document.querySelector('#source-flow [data-reader-related-public]')?.href);
  if(link!=='https://fountain.coach/essays/the-ear-that-learns/')throw Error('Unexpected related public reading '+link);
  await Promise.all([
    page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),
    page.evaluate(()=>document.querySelector('#source-flow [data-reader-related-public]').click())
  ]);
  await new Promise(resolve=>setTimeout(resolve,1000));
  if(!page.url().startsWith('https://fountain.coach/essays/the-ear-that-learns/'))throw Error('Related reading did not open: '+page.url());
  await page.goBack({waitUntil:'domcontentloaded',timeout:20000});
  await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.volume===id&&
    document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000},volume);
  const after=await page.evaluate(()=>({
    url:location.href,
    volume:document.getElementById('page-viewport')?.dataset.volume,
    paragraph:document.querySelector('#source-flow [data-source-block^="a-sound"]')?.dataset.sourceBlock
  }));
  if(!after.url.includes('?at=')||!after.paragraph||errors.length)throw Error('Round-trip source address not preserved '+JSON.stringify({after,errors}));
  console.log('PRESS_RELATION_ROUND_TRIP_PASS',JSON.stringify({before:semanticBefore,link,after}));
 } finally {await browser.close();}
})().catch(e=>{console.error(e.stack||String(e));process.exit(1)});
