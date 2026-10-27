// Browser acceptance of exact local candidate bytes; no public-serving claim.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const site=path.join(root,'site');
const browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH||undefined,args:['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required']});
const context=await browser.newContext();
const mimes={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.png':'image/png','.svg':'image/svg+xml','.wav':'audio/wav','.ogg':'audio/ogg','.mp3':'audio/mpeg','.json':'application/json'};
await context.route('https://fountain.coach/**',async route=>{
 const u=new URL(route.request().url());let pathname=decodeURIComponent(u.pathname);if(pathname.endsWith('/'))pathname+='index.html';
 const p=path.resolve(site,'.'+pathname);if(!p.startsWith(site+path.sep)||!fs.existsSync(p)){await route.fulfill({status:404,body:'Missing local candidate asset'});return;}
 await route.fulfill({status:200,contentType:mimes[path.extname(p)]||'application/octet-stream',body:fs.readFileSync(p)});
});
const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
const report={browser:await browser.version(),origin:'intercepted-local-candidate-not-public-readback',layouts:[],media:[],live:{}};
await page.goto('https://fountain.coach/essays/the-door-is-a-score/');
for(const [width,height] of [[1280,900],[1024,768],[820,1180],[390,844]]){
 await page.setViewportSize({width,height});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,'horizontal overflow');
 report.layouts.push({width,height,noOverflow:true});
}
for(const id of ['present','beyond','memory','withheld']){
 await page.locator(`[data-direction=${id}]`).click();
 await page.locator('audio').evaluate(a=>a.play());
 await page.waitForFunction(()=>document.querySelector('audio').currentTime>.15);
 const media=await page.locator('audio').evaluate(a=>({time:a.currentTime,duration:a.duration,source:a.currentSrc,paused:a.paused}));
 assert.ok(Math.abs(media.duration-14)<.1);assert.equal(media.paused,false);report.media.push({id,...media});
 await page.locator('audio').evaluate(a=>{a.pause();a.currentTime=4.3;});
}
await page.locator('[data-direction=present]').click();await page.locator('[data-perform]').click();
await page.waitForFunction(()=>document.querySelector('[data-door-study]').studyState.running,{timeout:45000});
await page.waitForFunction(()=>!document.querySelector('[data-recall]').disabled,{timeout:15000});
await page.locator('[data-recall]').click();
await page.waitForFunction(()=>document.querySelector('[data-door-study]').studyState.recalls===1);
report.live.beforeStop=await page.locator('[data-door-study]').evaluate(e=>e.studyState);
assert.equal(report.live.beforeStop.engineVersion,7000);assert.ok(report.live.beforeStop.maxRms>0.0001,'actual Csound output was silent');
await page.locator('[data-stop]').click();
await page.waitForFunction(()=>document.querySelector('[data-door-study]').studyState.contextState==='closed');
report.live.afterStop=await page.locator('[data-door-study]').evaluate(e=>e.studyState);
assert.equal(report.live.afterStop.running,false);
await page.locator('[data-direction=withheld]').click();await page.locator('[data-perform]').click();
await page.waitForFunction(()=>document.querySelector('[data-door-study]').studyState.running);
await page.waitForTimeout(5000);assert.equal(await page.locator('[data-recall]').isDisabled(),true);
await page.locator('[data-stop]').click();await page.waitForFunction(()=>document.querySelector('[data-door-study]').studyState.contextState==='closed');
for(const scheme of ['light','dark']){
 await page.emulateMedia({colorScheme:scheme});
 if(process.env.DOOR_QA_DIR){fs.mkdirSync(process.env.DOOR_QA_DIR,{recursive:true});await page.screenshot({path:path.join(process.env.DOOR_QA_DIR,`phone-${scheme}.png`),fullPage:true});}
}
report.errors=errors;assert.deepEqual(errors,[]);
await browser.close();console.log(JSON.stringify(report,null,2));
