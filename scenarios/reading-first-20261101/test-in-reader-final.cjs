const {webkit,chromium}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const base='http://192.168.8.50:8200';
(async()=>{
let failures=[];
for(const [browserName,browserType,launchArgs] of [['WebKit',webkit,{}],['Chromium',chromium,{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}]]){
 const browser=await browserType.launch({headless:true,...launchArgs});
 for(const [size,w,h] of [['landscape',1180,820],['portrait',820,1180],['phone',390,844]]){
  const page=await browser.newPage({viewport:{width:w,height:h}});
  const errors=[];page.on('pageerror',e=>errors.push('Page: '+e.message));page.on('console',m=>{if(m.type()==='error')errors.push('Console: '+m.text())});
  async function ready(expected){
   try{await page.waitForFunction(vol=>{let e=document.querySelector('#page-viewport');return e?.dataset.layout==='ready'&&e?.dataset.volume===vol},expected,{timeout:14000});}
   catch(e){errors.push('Not ready: '+expected+' '+await page.locator('#page-viewport').getAttribute('data-layout'));}
   return await page.evaluate(()=>({v:document.getElementById('page-viewport').dataset.volume,pages:document.getElementById('page-count').textContent,overflow:document.documentElement.scrollWidth>innerWidth||document.documentElement.scrollHeight>innerHeight}));
  }
  await page.goto(base+'/estate/collections/first-readings/',{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>window.__readerWitness='same-document');
  const first=await ready('first-readings');
  await page.screenshot({path:__dirname+'/preview-first-readings-'+browserName.toLowerCase()+'-'+size+'.png'});
  await page.locator('.page-viewport [data-reader-target="teatro"]').click();
  const teatro=await ready('teatro');
  const text=await page.evaluate(()=>document.querySelector('.frame-source-flow')?.innerText||''); // source hidden by CSS, contains full work
  const correctText=text.includes('The human condition is not a completed story')&&text.includes('Where does the human remain?');
  const plate=await page.locator('.page-viewport img[src*="teatro-score-memory-vector"]').count();
  await page.goBack();const back=await ready('first-readings');
  await page.getByRole('button',{name:'Open the Bookshelf inside the reader'}).click();
  const library=await ready('library');
  await page.screenshot({path:__dirname+'/preview-bookshelf-'+browserName.toLowerCase()+'-'+size+'.png'});
  await page.locator('.page-viewport [data-reader-target="essays"]').click();
  const essays=await ready('essays');
  const target=await page.locator('.page-viewport [data-reader-target^="essay--"]').first().getAttribute('data-reader-target');
  await page.locator('.page-viewport [data-reader-target^="essay--"]').first().click();
  const essay=await ready(target);
  const witness=await page.evaluate(()=>window.__readerWitness);
  const result={first,teatro,correctText,plate,back,library,essays,essay,witness,errors};
  if(errors.length||!witness||plate===0||!correctText||[first,teatro,back,library,essays,essay].some(x=>x.overflow))failures.push([browserName,size,result]);
  console.log(browserName,size,JSON.stringify(result));
  await page.close();
 }
 await browser.close();
}
console.log('FAILURES',failures.length);if(failures.length)process.exitCode=2;
})().catch(e=>{console.error(e.stack);process.exitCode=1});
