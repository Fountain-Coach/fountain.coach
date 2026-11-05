#!/usr/bin/env node
const fs=require('node:fs');
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const source=fs.readFileSync(__dirname+'/reading-first-press-engine.js');
(async()=>{const browser=await webkit.launch({headless:true});
for(const [w,h]of[[1440,900],[1200,860],[1280,720],[820,1120],[390,844],[1920,1080]]){
const context=await browser.newContext({viewport:{width:w,height:h},ignoreHTTPSErrors:true}),page=await context.newPage(),errors=[];
await context.route('**/estate/assets/linotype/reading-first-press-engine.js',r=>r.fulfill({status:200,body:source,contentType:'text/javascript'}));
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(m.type()==='error'&&m.text().includes('Fountain Press reader failure'))errors.push(m.text())});
await page.goto('https://192.168.8.50:8243/estate/#/read/essay--what-makes-a-page-modern',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000});
const count=+await page.locator('#page-viewport').getAttribute('data-pages');
console.log('PROFILE',w,h,'folios',count);
for(let n=1;n<=Math.min(count,12);n++){
 const state=await page.evaluate(()=>[...document.querySelectorAll('#page-viewport .linotype-sheet')].map(s=>{
 const a=s.querySelector('.linotype-area'),ar=a.getBoundingClientRect(),nodes=[...a.children].filter(n=>n.offsetHeight>0&&!n.hidden),last=nodes.at(-1);
 return {folio:s.querySelector('.linotype-folio')?.textContent.slice(-4),fill:last?Math.round((last.getBoundingClientRect().bottom-ar.top)/ar.height*100):0,
   first:nodes[0]?.textContent.slice(0,48),last:last?.textContent.slice(-85),
   n:nodes.length,figureIDs:nodes.filter(x=>x.tagName==='FIGURE').map(x=>({id:x.dataset.sourceBlock,w:x.querySelector('img')?.getBoundingClientRect().width,h:x.querySelector('img')?.getBoundingClientRect().height}))};
 }));
 if(n>=3&&n<=8)console.log('SPREAD',n,JSON.stringify(state));
 if(n===4||n===5)await page.screenshot({path:'/tmp/candidate-semantic-spread-'+w+'x'+h+'-s'+n+'.png'});
 if(n<count)await page.locator('#next-page').click();
}
console.log('ERRORS',JSON.stringify(errors));await context.close()
}
await browser.close()
})().catch(e=>{console.error(e);process.exitCode=1});
