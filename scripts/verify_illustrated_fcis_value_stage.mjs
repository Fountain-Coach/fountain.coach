import {createRequire} from 'node:module';
import fs from 'node:fs';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const base=process.env.FCIS_ESSAY_STAGE||'http://192.168.8.50:8200';
const work='essay--the-value-of-what-we-can-prove';
const heroPath='/estate/read/'+work+'/assets/fcis-value-illustration.webp';
const socialPath='/estate/assets/social/essays/the-value-of-what-we-can-prove.jpg';
const outcomes=[];
function assert(x,m){if(!x)throw Error(m)}
const browser=await webkit.launch({headless:true});
try{
 for(const viewport of [
  {id:'ipad-portrait',width:820,height:1180},
  {id:'ipad-landscape',width:1180,height:820},
  {id:'phone',width:390,height:844}
 ]){
  const context=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},isMobile:true,hasTouch:true});
  const page=await context.newPage(),errors=[],failed=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('response',r=>{if(r.status()>=400&&r.url().startsWith(base))failed.push([r.status(),r.url()]);});
  const res=await page.goto(base+'/estate/read/essays/',{waitUntil:'domcontentloaded',timeout:45000});
  assert(res.status()===200,'Essays collection not served');
  await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume==='essays',{timeout:90000});
  const contents=await page.locator('#page-viewport .reader-contents-entry').allTextContents();
  assert(contents.length===8,'Essays list should show 8, got '+contents.length);
  assert(contents.some(t=>t.trim()==='The Value of What We Can Prove'),'New essay not in Contents');
  const sourceGallery=await page.evaluate(()=>JSON.parse(document.getElementById('reader-gallery-data').textContent).collections.essays);
  assert(sourceGallery.length===8&&sourceGallery[0].id===work,'Gallery order/quantity wrong');
  assert(sourceGallery[0].src===heroPath,'Gallery not using principal source artwork');
  const response=await page.goto(base+'/estate/read/'+work+'/',{waitUntil:'domcontentloaded',timeout:45000});
  assert(response.status()===200,'Essay missing at direct route');
  await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id,work,{timeout:90000});
  const meta=await page.evaluate(()=>{
   const template=document.querySelector('template[data-reader-volume="essay--the-value-of-what-we-can-prove"]');
   const image=template?.content.querySelector('figure[data-source-illustration-id="fcis-value.illustration.1"] img');
   const page=document.querySelector('#page-viewport');
   const blocks=template?.content.querySelectorAll('.book-prose > p[data-source-block]')||[];
   return {id:page.dataset.volume,pages:Number(page.dataset.pages),img:image?.getAttribute('src'),
    alt:image?.getAttribute('alt'),heroBlocks:template?.content.querySelectorAll('figure[data-source-illustration-id]').length,
    proseBlocks:blocks.length,sourceHeadings:template?.content.querySelectorAll('.frame-subheading').length,
    sourceProems:template?.content.querySelectorAll('[data-editorial-role="proem"]').length,
    robots:[...document.querySelectorAll('meta[name="robots"]')].map(x=>x.getAttribute('content')),
    ogImage:document.querySelector('meta[property="og:image"]')?.getAttribute('content'),
    bodyWidth:document.documentElement.scrollWidth,
    viewportWidth:innerWidth
   };
  });
  assert(meta.heroBlocks===1&&meta.proseBlocks===28&&meta.sourceHeadings===6&&meta.sourceProems===1,'Source semantics altered '+JSON.stringify(meta));
  assert(meta.img===heroPath&&meta.alt?.includes('Axonometric Teatro Score'),'Wrong source hero');
  assert(meta.pages>=2&&meta.bodyWidth<=meta.viewportWidth+2,'Reader layout broken');
  assert(meta.robots.length===1&&meta.robots[0]==='noindex,nofollow','Contradictory staging robots');
  assert(meta.ogImage==='https://fountain.coach'+socialPath,'Work social metadata missing');
  let seen=false,actualLeaves=0,lastState='',heroVisibleCount=0;
  for(let n=0;n<Math.max(4,meta.pages+3);n++){
    const state=await page.evaluate(path=>{
      const v=document.querySelector('#page-viewport');
      const images=[...v.querySelectorAll('img[src="'+path+'"]')].map(i=>({
        loaded:i.complete&&i.naturalWidth>0,
        src:i.getAttribute('src'),
        rect:(()=>{const r=i.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};})()
      }));
      return {position:document.querySelector('#page-count')?.textContent||'', images};
    },heroPath);
    if(state.images.length){
      seen=true;heroVisibleCount+=state.images.length;
      assert(state.images.every(i=>i.loaded),'Source artwork not loaded on measured leaf');
      assert(state.images.every(i=>i.rect.width>80&&i.rect.height>50),'Source artwork missing real folio geometry');
      await page.screenshot({path:'/tmp/fcis-illustrated-'+viewport.id+'-hero.png'});
    }
    const next=page.locator('#next-page');
    if(!(await next.isEnabled()))break;
    if(state.position===lastState&&n>0)break;
    lastState=state.position;
    await next.click();
    await page.waitForTimeout(160);
    actualLeaves++;
  }
  assert(seen,'Principal image did not appear in any composed folio');
  assert(!failed.some(([code,url])=>url.includes('fcis-value-illustration.webp')),'Hero failed to fetch');
  const entry={viewport:viewport.id,pages:meta.pages,contents:contents.length,gallery:sourceGallery.length,
     illustratedLeaves:heroVisibleCount,paginationTurns:actualLeaves,errors,failed};
  outcomes.push(entry);console.log('ILLUSTRATED_ESSAY_WEBKIT_PASS',JSON.stringify(entry));
  await context.close();
 }
 const context=await browser.newContext();
 const manifestRes=await context.request.get(base+'/estate/read/'+work+'/edition-manifest.json');
 assert(manifestRes.status()===200,'Source manifest route failed');
 const manifest=await manifestRes.json();
 assert(manifest.figures?.length===1&&manifest.originalImages===1,'Manifest not source-bound to approved art');
 assert(manifest.publicReleaseAuthorized===false&&manifest.stagingOnly===true,'False production rights');
 const heroRes=await context.request.get(base+heroPath);
 const socialRes=await context.request.get(base+socialPath);
 assert(heroRes.status()===200&&socialRes.status()===200,'Artwork HTTP failed');
 const {createHash}=await import('node:crypto');
 function sha(b){return createHash('sha256').update(b).digest('hex')}
 assert(sha(await heroRes.body())===manifest.figures[0].originalSHA256,'Hero SHA mismatch');
 assert(sha(await socialRes.body())===manifest.figures[0].socialSHA256,'Social source SHA mismatch');
 const catalogRes=await context.request.get(base+'/estate/books/catalog.json');
 const catalog=await catalogRes.json();
 const essays=catalog.books.find(b=>b.id==='essays');
 assert(essays.firstIllustratedChapterID===work&&essays.firstChapterOriginalImageSHA256===manifest.figures[0].originalSHA256,'Book cover source drift');
 await context.close();
 console.log('ILLUSTRATED_ESSAY_STAGE_ACCEPTED',JSON.stringify({sourceSHA256:manifest.sourceSHA256,figures:manifest.figures.length,outcomes}));
}catch(err){console.error('ILLUSTRATED_ESSAY_STAGE_FAILED',err.stack||err);process.exitCode=1}
finally{await browser.close()}
