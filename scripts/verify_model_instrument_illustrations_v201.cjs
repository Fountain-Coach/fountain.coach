const fs=require('fs'),path=require('path');
const {chromium,webkit}=require(process.env.HOME+'/Developer/fcis.fountain.coach/node_modules/playwright');
const root=path.join(process.env.HOME,'Developer/fountain-essay-20261113');
const overlay=path.join(root,'build/model-illustrations-v201/overlay');
const base='https://192.168.8.50:8243';
const essay='/estate/read/essay--the-model-is-not-the-instrument/';
const svgPrefix=essay+'assets/';
const assets=[
 '01-the-instrument-and-its-place.svg',
 '02-the-claim-and-the-browser.svg',
 '03-a-score-becomes-sound.svg',
 '04-three-machines-one-work.svg',
];
const out=path.join(root,'build/model-illustrations-v201/qa');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 let failures=[];
 for(const [engine,type] of [['Chromium',chromium],['WebKit',webkit]]){
  const browser=await type.launch(engine==='Chromium'
   ?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--ignore-certificate-errors']}
   :{headless:true});
  for(const v of [{name:'ipad-portrait',width:820,height:1180},{name:'ipad-landscape',width:1180,height:820},{name:'phone',width:390,height:844}]){
   const page=await browser.newPage({viewport:{width:v.width,height:v.height},ignoreHTTPSErrors:true});
   const consoleErrors=[];
   page.on('pageerror',e=>consoleErrors.push(e.message));
   page.on('console',m=>{
    if(m.type()==='error'&&m.text().includes('Fountain Press reader failure'))consoleErrors.push(m.text());
   });
   const html=fs.readFileSync(path.join(overlay,'estate/read/essay--the-model-is-not-the-instrument/index.html'),'utf8');
   await page.route(base+essay,r=>r.fulfill({status:200,contentType:'text/html; charset=utf-8',body:html}));
   await page.route(base+svgPrefix+'*.svg',r=>{
    const name=path.basename(new URL(r.request().url()).pathname);
    if(!assets.includes(name))return r.continue();
    const body=fs.readFileSync(path.join(overlay,'estate/read/essay--the-model-is-not-the-instrument/assets',name));
    return r.fulfill({status:200,body,contentType:'image/svg+xml'});
   });
   const res=await page.goto(base+essay,{waitUntil:'domcontentloaded',timeout:28000});
   await page.waitForTimeout(800);
   const state=await page.evaluate(()=>{
    const t=document.querySelector('template[data-reader-volume="essay--the-model-is-not-the-instrument"]');
    const figures=[...t.content.querySelectorAll('[data-source-illustration-id]')];
    const address=t.content.querySelector('[data-source-illustration-id="model-instrument.workshop"]');
    const preceding=address?.previousElementSibling;
    const text=t.content.querySelector('.book-prose')?.textContent;
    return {
     layout:document.querySelector('#page-viewport')?.dataset.layout,
     folio:document.querySelector('#page-count')?.textContent,
     figureCount:figures.length,
     commercialAfter:preceding?.dataset.sourceBlock,
     editorialCount:t.content.querySelectorAll('.frame-editorial-proem').length,
     textBytes:text?.length,
     sourceAnchors:figures.map(f=>f.dataset.sourceIllustrationId),
     width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
    };
   });
   const seen=new Set, broken=[];
   for(let n=0;n<25;n++){
    const imgs=await page.evaluate(()=>{
      return [...document.querySelectorAll('#page-viewport img')].map(img=>({
       url:new URL(img.src).pathname,
       width:img.getBoundingClientRect().width,
       broken:!img.complete||(img.complete&&img.naturalWidth===0)
      })).filter(x=>x.width>2);
    });
    for(const img of imgs){
     if(assets.some(x=>img.url.endsWith(x)))seen.add(path.basename(img.url));
     if(img.broken)broken.push(img.url);
    }
    if(n===0&&engine==='Chromium'&&v.name==='ipad-portrait')
      await page.screenshot({path:path.join(out,'first-leaf-ipad-portrait.png')});
    const next=page.locator('#next-page');
    if(!await next.count()||await next.isDisabled())break;
    await next.click();await page.waitForTimeout(80);
   }
   const ok=res.status()===200&&state.layout==='ready'&&state.figureCount===4&&state.commercialAfter==='model-instrument.s3.p3'
       &&state.editorialCount===1&&state.scrollWidth<=state.width+2&&seen.size===4&&broken.length===0&&consoleErrors.length===0;
   console.log(JSON.stringify({engine,viewport:v.name,http:res.status(),ok,...state,visibleFigures:[...seen],broken:broken.slice(0,2),errors:consoleErrors.slice(0,2)}));
   if(!ok)failures.push(engine+':'+v.name);
   await page.close();
  }
  await browser.close();
 }
 const dir=path.join(overlay,'estate');
 const work=fs.readFileSync(path.join(dir,'read/essay--the-model-is-not-the-instrument/index.html'),'utf8');
 const book=fs.readFileSync(path.join(dir,'books/essays/index.html'),'utf8');
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'read/essay--the-model-is-not-the-instrument/edition-manifest.json')));
 const catalog=JSON.parse(fs.readFileSync(path.join(dir,'books/catalog.json')));
 const social=fs.readFileSync(path.join(dir,'assets/social/essays/the-model-is-not-the-instrument-social.jpg'));
 const card=fs.readFileSync(path.join(dir,'assets/social/books/essays-first-chapter.jpg'));
 const shared=Buffer.compare(social,card)===0;
 const adequate=work.includes('property="og:image"')&&book.includes('property="og:image"')
   &&shared&&manifest.shareImageSHA256===catalog.books.find(b=>b.id==='essays').socialImageSHA256
   &&manifest.figures[3].after==='model-instrument.s3.p3';
 console.log('SOCIAL_PARITY',JSON.stringify({ok:adequate,shared,socialBytes:social.length,heroSHA:manifest.heroSourceSHA256}));
 if(!adequate)failures.push('social');
 console.log('FINAL',JSON.stringify({checks:7,failures}));
 if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(2)});
