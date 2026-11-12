import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const base=process.env.FCIS_PUBLIC_CANDIDATE||'http://127.0.0.1:8862';
const id='essay--the-value-of-what-we-can-prove',title='The Value of What We Can Prove';
const hero='/estate/read/'+id+'/assets/fcis-value-illustration.webp';
const social='/estate/assets/social/essays/the-value-of-what-we-can-prove.jpg';
const heroSHA='b043511473e6bca1e05b3c09d8dc1c92997b8bcbacb8506525ca0a4c0f02ebdb';
const socialSHA='82ccaf0e6d050c046d44a0684f420e36d4dd71f8655faa5c42925152e93b40f3';
const sourceSHA='113781a540e606ae3de6436bb72b126d92fa1dcf5cfb565d72f26bedc1e731b5';
const browser=await webkit.launch({headless:true});
const assert=(v,m)=>{if(!v)throw Error(m)};
const sha=b=>createHash('sha256').update(b).digest('hex');
try{
 const ctx=await browser.newContext();
 const api=ctx.request;
 for(const path of ['/', '/estate/','/estate/read/essays/','/estate/books/essays/','/estate/books/first-readings/','/estate/books/orange-dot/','/estate/read/'+id+'/','/estate/books/catalog.json',hero,social]){
   const r=await api.get(base+path);
   assert(r.status()===200,'New public route broken '+path+': '+r.status());
 }
 const [a,b]=await Promise.all([api.get(base+'/'),api.get(base+'/estate/')]);
 assert(sha(await a.body())===sha(await b.body()),'Public root and estate not identical');
 const img=await api.get(base+hero),share=await api.get(base+social);
 assert(sha(await img.body())===heroSHA,'Hero source digest mismatch');
 assert(sha(await share.body())===socialSHA,'Social derivative digest mismatch');
 const catalog=await (await api.get(base+'/estate/books/catalog.json')).json();
 const first=catalog.books.find(x=>x.id==='essays');
 assert(first.firstIllustratedChapterID===id,'Book first chapter does not identify new essay');
 assert(first.firstChapterOriginalImageSHA256===heroSHA&&first.socialImageSHA256===socialSHA,'Book share provenance mismatch');
 assert(catalog.publicReleaseAuthorized===true&&catalog.status==='public-production','Book catalogue publication state');
 const manifest=await (await api.get(base+'/estate/read/'+id+'/edition-manifest.json')).json();
 assert(manifest.sourceSHA256===sourceSHA&&manifest.publicReleaseAuthorized===true&&manifest.stagingOnly===false,'Essay manuscript public state');
 assert(manifest.originalImages===1&&manifest.sourceBlocks.length===28,'Essay manuscript structure mismatch');
 await ctx.close();
 const results=[];
 for(const viewport of [{name:'ipad-portrait',width:820,height:1180},{name:'ipad-landscape',width:1180,height:820},{name:'phone',width:390,height:844}]){
   const c=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},hasTouch:true,isMobile:true});
   const page=await c.newPage();
   const failures=[],errors=[];
   page.on('response',r=>{if(r.status()>=400&&r.url().startsWith(base))failures.push([r.status(),r.url()]);});
   page.on('pageerror',e=>errors.push(String(e)));
   const root=await page.goto(base+'/',{waitUntil:'domcontentloaded',timeout:45000});
   assert(root.status()===200,'Root unavailable');
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:45000});
   const links=await page.locator('.reader-book-direct-link').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')));
   assert(links.length===3&&links.includes('/estate/books/essays/'),'Bookshelf direct links changed '+JSON.stringify(links));
   const collection=await page.goto(base+'/estate/read/essays/',{waitUntil:'domcontentloaded',timeout:45000});
   assert(collection.status()===200,'Essays collection unavailable');
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='essays',{timeout:45000});
   const names=await page.locator('#page-viewport .reader-contents-entry').allTextContents();
   assert(names.length===8&&names[0].includes(title),'Essay contents not integrated '+JSON.stringify(names));
   const order=await page.evaluate(()=>JSON.parse(document.getElementById('reader-gallery-data').textContent).collections.essays.map(x=>x.id));
   assert(order.length===8&&order[0]===id,'Gallery first illustration not same work');
   const essay=await page.goto(base+'/estate/read/'+id+'/',{waitUntil:'domcontentloaded',timeout:45000});
   assert(essay.status()===200,'Essay direct unavailable');
   await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id,id,{timeout:45000});
   const measured=await page.evaluate(()=>{
     const v=document.getElementById('page-viewport');
     const tpl=document.querySelector('template[data-reader-volume="essay--the-value-of-what-we-can-prove"]');
     return {
        volume:v.dataset.volume,pages:Number(v.dataset.pages),
        sourceBlocks:tpl?.content.querySelectorAll('.book-prose p[data-source-block]').length,
        hero:tpl?.content.querySelector('figure[data-source-illustration-id="fcis-value.illustration.1"] img')?.getAttribute('src'),
        ogImage:document.querySelector('meta[property="og:image"]')?.content,
        canonical:document.querySelector('link[rel=canonical]')?.href,
        robots:[...document.querySelectorAll('meta[name=robots]')].map(n=>n.content),
        overflow:document.documentElement.scrollWidth-innerWidth
     };
   });
   assert(measured.sourceBlocks===28&&measured.hero===hero,'Source blocks/figure missing');
   assert(measured.ogImage==='https://fountain.coach'+social,'Static social semantics not bound');
   assert(measured.canonical==='https://fountain.coach/estate/read/'+id+'/','Canonical work route incorrect');
   assert(measured.robots.length===1&&measured.robots[0]==='index,follow','Not public indexing metadata');
   assert(measured.overflow<=2&&measured.pages>=2,'Reader measurement broken');
   let visible=false;
   for(let i=0;i<measured.pages+2;i++){
     const images=await page.locator('#page-viewport img[src="'+hero+'"]').count();
     if(images){visible=true;assert(await page.locator('#page-viewport img[src="'+hero+'"]').first().evaluate(el=>el.complete&&el.naturalWidth>0),'Hero not visually loaded');break;}
     const next=page.locator('#next-page');if(!(await next.isEnabled()))break;await next.click();await page.waitForTimeout(75);
   }
   assert(visible,'Hero only in hidden template, not mounted folio');
   assert(!failures.some(x=>x[1].includes('fcis-value')),'FCIS image/media route failure '+JSON.stringify(failures));
   const entry={viewport:viewport.name,pages:measured.pages,essayEntries:names.length,heroMounted:visible,rootLinks:links.length,unrelatedPageErrors:errors.length};
   results.push(entry);console.log('PUBLIC_CANDIDATE_WEBKIT_PASS',JSON.stringify(entry));
   await c.close();
 }
 const neighbor=await browser.newContext();
 for(const [path,volume] of [['/estate/books/first-readings/','first-readings'],['/estate/books/orange-dot/','orange-dot']]){
   const p=await neighbor.newPage();await p.goto(base+path,{waitUntil:'domcontentloaded'});
   await p.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id,volume,{timeout:45000});
   const count=await p.locator('#page-viewport .reader-contents-entry').count();
   assert(count===(volume==='orange-dot'?23:32),'Adjacent book inventory drift: '+volume+' '+count);
   await p.close();
 }
 for(const path of ['/estate/read/essay--client-centered/','/estate/read/essay--a-sound-must-earn-its-place/']){
   const r=await neighbor.request.get(base+path);assert(r.status()===200,'Historic direct essay broke '+path);
 }
 await neighbor.close();
 console.log('PUBLIC_CANDIDATE_FULL_ACCEPTED',JSON.stringify({publicRoutes:true,sourceSHA,heroSHA,socialSHA,viewports:results}));
}catch(err){console.error('PUBLIC_CANDIDATE_FAILED',err.stack||err);process.exitCode=1}
finally{await browser.close()}
