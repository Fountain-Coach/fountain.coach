import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');

const base=process.env.DIRECT_BOOKS_BASE||'http://127.0.0.1:8841';
const local=process.env.DIRECT_BOOKS_LOCAL||'/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/book-links-stage-v195-preview';
const manifest=JSON.parse(fs.readFileSync(path.join(local,'estate/books/catalog.json'),'utf8'));
const cols=['essays','first-readings','orange-dot'];
function assert(x,msg){if(!x)throw Error(msg)}
assert(manifest.schema==='fountain.press.book-direct-links.v1','catalog schema');
assert(JSON.stringify(manifest.books.map(b=>b.id))===JSON.stringify(cols),'ordered collections');
const browser=await webkit.launch({headless:true});
try{
 for(const vp of [
  {label:'ipad-portrait',width:820,height:1180},
  {label:'ipad-landscape',width:1180,height:820},
  {label:'phone',width:390,height:844}
 ]){
  const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height},isMobile:true,hasTouch:true});
  const landing=await ctx.newPage();
  const opening=await landing.goto(base+'/estate/',{waitUntil:'domcontentloaded',timeout:45000});
  assert(opening.status()===200,'Bookshelf root unavailable');
  await landing.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:30000});
  const rootLinks=await landing.locator('.reader-book-direct-link').evaluateAll(nodes=>nodes.map(n=>({href:n.getAttribute('href'),name:n.textContent.trim(),accessible:n.getAttribute('aria-label')})));
  assert(JSON.stringify(rootLinks.map(l=>l.href))===JSON.stringify(cols.map(id=>'/estate/books/'+id+'/')),'Bookshelf direct links absent '+JSON.stringify(rootLinks));
  await landing.close();
  // Separate book pages avoid aborting optional module imports in the previous document
  // during same-tab navigation. Every page independently observes uncaught errors.
  for(const book of manifest.books){
   const page=await ctx.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   const url=base+book.directURLPath;
   const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
   assert(response.status()===200,'book route HTTP '+url);
   await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume===id,book.id,{timeout:30000});
   const result=await page.evaluate(()=>{
    const meta=(name,attr='property')=>document.querySelector('meta['+attr+'="'+name+'"]')?.getAttribute('content');
    const sem=JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent);
    const collection=document.querySelector('#page-viewport')?.dataset.volume;
    const readerLink=[...document.querySelectorAll('.reader-book-direct-link')].length;
    return {title:document.title,collection,pages:document.querySelector('#page-viewport').dataset.pages,
      canonical:document.querySelector('link[rel=canonical]')?.href,
      ogTitle:meta('og:title'),ogImage:meta('og:image'),ogURL:meta('og:url'),ogAlt:meta('og:image:alt'),
      twitterImage:meta('twitter:image','name'), ogWidth:meta('og:image:width'),
      ld:sem,links:readerLink,scroll:document.documentElement.scrollWidth,width:innerWidth,
      body:document.body.dataset.initialVolume
    };
   });
   assert(result.collection===book.id&&result.body===book.id,'wrong Reader volume '+JSON.stringify(result));
   assert(result.canonical===book.canonicalURL&&result.ogURL===book.canonicalURL,'non-canonical direct path');
   assert(result.ld['@type']==='Book'&&result.ld.hasPart.identifier===book.firstIllustratedChapterID,'inaccurate first-chapter semantics');
   assert(result.ogImage===book.socialImageURL&&result.twitterImage===book.socialImageURL,'image mismatch');
   assert(result.ogAlt===book.firstChapterImageAlt,'wrong OG alt text');
   assert(result.ogWidth==='1200','social dimensions');
   assert(result.scroll<=result.width+2,'horizontal overflow');
   const entryCount=await page.locator('#page-viewport .reader-contents-entry').count();
   const expected=book.id==='essays'?7:book.id==='first-readings'?32:23;
   assert(entryCount===expected,'book contents incomplete '+book.id+' '+entryCount);
   await page.locator('#page-viewport .reader-contents-entry').first().click();
   await page.waitForFunction(id=>document.querySelector('#page-viewport')?.dataset.layout==='ready'&&document.querySelector('#page-viewport')?.dataset.volume!==id&&Number(document.querySelector('#page-viewport')?.dataset.pages)>0,book.id,{timeout:30000});
   const resp=await ctx.request.get(base+book.socialImagePath);
   assert(resp.status()===200,'missing social JPEG');
   const bytes=await resp.body();
   const {createHash}=await import('node:crypto');
   assert(createHash('sha256').update(bytes).digest('hex')===book.socialImageSHA256,'social SHA mismatch');
   if(vp.label==='ipad-portrait'){
    await page.screenshot({path:'/Volumes/DockerDisk/ArchiveOps/direct-book-'+book.id+'-portrait.png'});
   }
   assert(!errors.length,'uncaught Reader exception '+book.id+' '+JSON.stringify(errors));
   console.log('BOOK_DIRECT_LINK_PASS',vp.label,book.id,'chapterRead',true,'OG',book.firstIllustratedChapterID,'href',book.directURLPath);
   await page.close();
  }
  await ctx.close();
 }
 const catalogRes=await browser.newContext();
 const http=await catalogRes.request.get(base+'/estate/books/catalog.json');
 assert(http.status()===200,'machine book catalog unavailable');
 const parsed=await http.json();
 assert(JSON.stringify(parsed.books.map(x=>x.id))===JSON.stringify(cols),'machine order mismatch');
 for(const x of parsed.books){
  assert(x.stageOnly===true&&x.publicReleaseAuthorized===false,'false public assertion');
  assert(x.firstChapterOriginalImageSHA256.length===64&&x.socialImageSHA256.length===64,'missing source provenance');
 }
 await catalogRes.close();
 console.log('ALL_DIRECT_BOOKS_ACCEPTED','3 books, 3 responsive viewports, 3 static OG cards, machine catalog parity, Reader intact');
}catch(e){console.error('DIRECT_BOOKS_FAILED',e.stack||e);process.exitCode=1}
finally{await browser.close()}
