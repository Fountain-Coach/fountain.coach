const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium,webkit}=require(process.env.HOME+'/Developer/fcis.fountain.coach/node_modules/playwright');
const sourceRoot=path.join(process.env.HOME,'Developer/if-only-public-source-20261113/build/if-only-public/candidate');
const base=process.env.IF_ONLY_TEST_ORIGIN||'http://127.0.0.1:8731';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const shaFile=path=>sha(fs.readFileSync(path));
const EXPECTED={
  hero:'e03e5cf7ed8851fadd4c08488cdebd86cf98f177d9d28cb4ed9730ce69f8fa70',
  social:'f41b9bbec06e2de89c1369fa965fc382a867d331637903c3c18bde039254c583',
  manuscript:'396afcb457cdd930b208f94c520012abeaa6103498dd8001c8dd12ccd0fcc8a6'
};
(async()=>{
 let failures=[];let cases=0;
 const file=p=>path.join(sourceRoot,p);
 if(shaFile(file('index.html'))!==shaFile(file('estate/index.html')))failures.push('root byte parity');
 const catalog=JSON.parse(fs.readFileSync(file('estate/books/catalog.json')));
 const essay=catalog.books.find(x=>x.id==='essays');
 if(!essay||essay.firstIllustratedChapterID!=='essay--if-only'||essay.firstChapterOriginalImageSHA256!==EXPECTED.hero
    ||essay.socialImageSHA256!==EXPECTED.social||essay.publicReleaseAuthorized!==true)failures.push('catalog');
 const manifest=JSON.parse(fs.readFileSync(file('estate/read/essay--if-only/edition-manifest.json')));
 if(manifest.sourceSHA256!==EXPECTED.manuscript||manifest.figures.length!==1||manifest.publicationState!=='public-production')failures.push('manifest');
 for(const [rel,expected] of [
  ['estate/read/essay--if-only/assets/hero-simultanbuehne.webp',EXPECTED.hero],
  ['estate/assets/social/essays/if-only-social.jpg',EXPECTED.social],
  ['estate/assets/social/books/essays-first-chapter.jpg',EXPECTED.social]]) if(shaFile(file(rel))!==expected)failures.push('asset digest '+rel);
 for(const [engine,type] of [['Chromium',chromium],['WebKit',webkit]]){
  const browser=await type.launch(engine==='Chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--ignore-certificate-errors']}:{headless:true});
  for(const viewport of [{name:'iPad portrait',width:820,height:1180},{name:'iPad landscape',width:1180,height:820},{name:'Phone',width:390,height:844}]){
   const page=await browser.newPage({viewport:{width:viewport.width,height:viewport.height},ignoreHTTPSErrors:true});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   page.on('console',m=>{if(m.type()==='error'&&m.text().includes('Fountain Press reader failure'))errors.push(m.text())});
   const url=base+'/estate/read/essay--if-only/';
   const res=await page.goto(url,{waitUntil:'domcontentloaded',timeout:28000});await page.waitForTimeout(900);
   const state=await page.evaluate(()=>{
    const page=document.querySelector('#page-viewport');
    const t=document.querySelector('template[data-reader-volume="essay--if-only"]');
    const hero=page?.querySelector('img');
    const editorial=t?.content.querySelector('.frame-editorial-proem');
    const initial=page?.dataset.layout;
    return {
      layout:initial,folio:document.querySelector('#page-count')?.textContent,
      title:t?.content.querySelector('.book-chapter-heading h2')?.textContent,
      heroSrc:hero?.getAttribute('src'),heroWidth:hero?.naturalWidth||0,
      editorial:editorial?.querySelector('.frame-editorial-kicker')?.textContent,
      authorSubtitle:t?.content.querySelector('.frame-lead')?.textContent,
      sourceParagraphs:t?.content.querySelectorAll('p[data-source-block^="if-only."]').length,
      overflows:document.documentElement.scrollWidth>window.innerWidth,
      links:[...document.querySelectorAll('link[rel=canonical]')].map(n=>n.href),
      images:[...t.content.querySelectorAll('img')].length
    };
   }).catch(e=>({exception:String(e)}));
   const ok=res.status()===200&&state.layout==='ready'&&state.title==='If Only'&&state.heroWidth>0&&
    state.editorial==='From the editor'&&state.authorSubtitle==='The Contexter and the Simultaneous Stage'&&
    state.sourceParagraphs>=48&&state.images===1&&!state.overflows&&errors.length===0;
   console.log('READER',JSON.stringify({engine,viewport:viewport.name,ok,http:res.status(),...state,errors:errors.slice(0,2)}));cases++;if(!ok)failures.push(engine+':'+viewport.name+' essay');
   if(engine==='Chromium'&&viewport.name==='iPad portrait'){
    const loc=path.join(sourceRoot,'..','if-only-public-page.png');
    await page.screenshot({path:loc,fullPage:true});
   }
   await page.goto(base+'/estate/books/essays/',{waitUntil:'domcontentloaded',timeout:25000});await page.waitForTimeout(800);
   const book=await page.evaluate(()=>{
    const gallery=JSON.parse(document.querySelector('#reader-gallery-data')?.textContent||'{}');
    const t=[...document.querySelectorAll('template[data-reader-volume]')];
    return {first:gallery?.collections?.essays?.[0]?.id,templates:t.length,
      containsNew:t.some(x=>x.dataset.readerVolume==='essay--if-only'),
      title:document.title,layout:document.querySelector('#page-viewport')?.dataset.layout,
      og:document.querySelector('meta[property="og:image"]')?.content,
      oldFcis:t.some(x=>x.dataset.readerVolume==='essay--the-value-of-what-we-can-prove'),
      otherFcis:t.some(x=>x.dataset.readerVolume==='essay--a-sound-must-earn-its-place'),
    }
   });
   const bok=book.first==='essay--if-only'&&book.containsNew&&book.oldFcis&&book.otherFcis&&book.templates>=45;
   console.log('ESSAYS_BOOK',JSON.stringify({engine,viewport:viewport.name,ok:bok,...book}));
   cases++;if(!bok)failures.push(engine+':'+viewport.name+' book');
   await page.close();
  }
  await browser.close();
 }
 const staticHtml=fs.readFileSync(file('estate/read/essay--if-only/index.html'),'utf8');
 const canonical='https://fountain.coach/estate/read/essay--if-only/';
 if(!staticHtml.includes('href="'+canonical+'"')||staticHtml.includes('192.168.8.50')||!staticHtml.includes('og:image:height'))failures.push('SEO public direct metadata');
 const existing=fs.readFileSync(file('estate/books/first-readings/index.html'),'utf8');
 if(!existing.includes('essay--if-only')||!existing.includes('data-reader-volume="orange-dot--'))failures.push('neighbor shell inclusion');
 console.log('FINAL',JSON.stringify({cases,failures,rootSha:shaFile(file('index.html'))}));
 if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=2});
