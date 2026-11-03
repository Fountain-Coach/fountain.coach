/* Exact Linotype first-page screenshots for works without authored illustration.
 * Uses the accepted v140 browser composition; no generated substitute art.
 */
const fs=require('fs'),path=require('path'),os=require('os'),cp=require('child_process');
const {webkit}=require(path.join(os.homedir(),'Developer/fcis.fountain.coach/node_modules/playwright'));
const ROOT=path.resolve(__dirname,'..');
const config=JSON.parse(fs.readFileSync(path.join(ROOT,'build/v141-social-first-folio-fallbacks.json'),'utf8'));
(async()=>{
 const browser=await webkit.launch({headless:true});
 const receipts=[];
 try {
 for(const item of config.items) {
  const page=await browser.newPage({viewport:{width:900,height:1200},deviceScaleFactor:2,hasTouch:false});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:4291/estate/#/read/'+item.id,{waitUntil:'domcontentloaded'});
  const effectiveId=['solstice','solstice-reading-01'].includes(item.id)?'first-readings':item.id;
  await page.waitForFunction(id=> {
   const v=document.getElementById('page-viewport');
   return v?.dataset.layout==='ready' && v?.dataset.volume===id;
  },effectiveId,{timeout:25000});
  await page.evaluate(()=>document.fonts.ready);
  const sheets=page.locator('#page-viewport .linotype-sheet');
  const target=(await sheets.count())>0?sheets.first():page.locator('#page-viewport');
  const rect=await target.boundingBox();
  if(!rect || rect.width<450 || rect.height<600)throw Error('Invalid first composed page '+item.id+' '+JSON.stringify(rect));
  const text=(await target.innerText()).trim();
  if(!text || text.length<24)throw Error('Empty first folio for '+item.id);
  if(errors.length)throw Error('Reader failed before first page '+item.id+': '+errors.join(','));
  const tmp=path.join(ROOT,'build','v141-first-folio-'+item.id+'.png');
  await target.screenshot({path:tmp,type:'png'});
  const outfile=path.join(ROOT,'build/public-release-v141-social',item.image.slice(1));
  cp.execFileSync('magick',[tmp,'-resize','1200x610','-background','#efeee9',
    '-gravity','center','-extent','1200x630','-strip','-quality','90',outfile]);
  const dim=cp.execFileSync('magick',['identify','-format','%wx%h %m',outfile],{encoding:'utf8'});
  if(dim!=='1200x630 JPEG')throw Error('Unexpected first folio JPG '+item.id+' '+dim);
  receipts.push({id:item.id,title:item.title,source:'accepted-v140-first-measured-Linotype-sheet',
    sheetWidthPx:Math.round(rect.width),sheetHeightPx:Math.round(rect.height),
    textBeginning:text.slice(0,170),output:item.image,
    screenshotFirstSheet:true,byteSize:fs.statSync(outfile).size});
  console.log('FIRST_FOLIO',item.id,dim,rect.width,rect.height,JSON.stringify(text.slice(0,85)));
  await page.close();
 }
 } finally {await browser.close()}
 fs.writeFileSync(path.join(ROOT,'build/v141-first-folio-browser-proof.json'),JSON.stringify({
  schema:'fountain.press.first-folio-screenshot-proof.v1',method:'Playwright WebKit actual first sheet',
  readerSource:'fountain.coach v140 source SHA 5f9b3eafc4248baf0bdb4432b53efa1c5e9caf9c',
  total:receipts.length,screenshots:receipts
 },null,2)+'\n');
 console.log('FIRST_FOLIO_ACCEPTED',receipts.length);
})().catch(e=>{console.error(e);process.exitCode=1});
