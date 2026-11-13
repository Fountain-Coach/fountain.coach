const fs=require('fs'),path=require('path');
const {chromium,webkit}=require(process.env.HOME+'/Developer/fcis.fountain.coach/node_modules/playwright');
const root=path.join(process.env.HOME,'Developer/fountain-essay-20261113/build/if-only-v202/overlay/estate');
const src='https://192.168.8.50:8243';
const route='/estate/read/essay--if-only/';
const targets=[
 {name:'iPad portrait',width:820,height:1180},
 {name:'iPad landscape',width:1180,height:820},
 {name:'Phone portrait',width:390,height:844}
];
(async()=>{
 let failure=[];
 for(const [engine,type] of [['Chromium',chromium],['WebKit',webkit]]){
  const b=await type.launch(engine==='Chromium'?{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--ignore-certificate-errors']}:{headless:true});
  for(const vp of targets){
   const p=await b.newPage({viewport:{width:vp.width,height:vp.height},ignoreHTTPSErrors:true});
   const errors=[];
   p.on('pageerror',e=>errors.push(e.message));
   p.on('console',m=>{if(m.type()==='error'&&m.text().includes('Fountain Press reader failure'))errors.push(m.text())});
   const html=fs.readFileSync(path.join(root,'read/essay--if-only/index.html'),'utf8');
   const art=fs.readFileSync(path.join(root,'read/essay--if-only/assets/hero-simultanbuehne.webp'));
   await p.route(src+route,r=>r.fulfill({status:200,contentType:'text/html; charset=utf-8',body:html}));
   await p.route(src+route+'assets/hero-simultanbuehne.webp',r=>r.fulfill({status:200,contentType:'image/webp',body:art}));
   const res=await p.goto(src+route,{waitUntil:'domcontentloaded',timeout:28000});
   await p.waitForTimeout(2500);
   const state=await p.evaluate(()=>{
    const page=document.querySelector('#page-viewport');
    const t=document.querySelector('template[data-reader-volume="essay--if-only"]');
    const figure=t?.content.querySelector('[data-source-illustration-id="if-only.hero"]');
    const editorial=t?.content.querySelector('.frame-editorial-proem[data-editorial-role="proem"]');
    const title=t?.content.querySelector('.book-chapter-heading h2');
    const subtitle=t?.content.querySelector('.book-prose > p.frame-lead');
    const imgs=[...page.querySelectorAll('img')];
    return {status:document.querySelector('#reader-status')?.textContent,layout:page?.dataset.layout,
      folio:document.querySelector('#page-count')?.textContent,
      imageCount:imgs.length,missingImages:imgs.filter(i=>!i.complete||i.naturalWidth===0).length,
      editorial:!!editorial,editorialLabel:editorial?.querySelector('.frame-editorial-kicker')?.textContent,
      title:title?.textContent,subtitle:subtitle?.textContent,figure:!!figure,
      sourceParagraphs:t?.content.querySelectorAll('p[data-source-block^="if-only."]').length,
      sidewaysOverflow:document.documentElement.scrollWidth>innerWidth
    };
   });
   const count=Number((state.folio||'').split('/')[1]||0);
   const ok=res.status()===200&&state.layout==='ready'&&state.editorialLabel==='From the editor'&&
     state.subtitle==='The Contexter and the Simultaneous Stage'&&state.figure&&state.title==='If Only'&&
     state.sourceParagraphs>=48&&count>=4&&!state.sidewaysOverflow&&errors.length===0;
   console.log('COMPOSE',JSON.stringify({engine,viewport:vp.name,ok,http:res.status(),...state,errors:errors.slice(0,2)}));
   if(!ok)failure.push(engine+':'+vp.name);
   if(engine==='Chromium'&&vp.name==='iPad portrait'){
     const outfile=path.join(process.env.HOME,'Developer/fountain-essay-20261113/build/if-only-v202/if-only-ipad-inert.png');
     await p.screenshot({path:outfile,fullPage:true});
   }
   await p.close();
  }
  await b.close();
 }
 console.log('CANDIDATE_BROWSER_TEST',JSON.stringify({checks:6,failed:failure}));
 if(failure.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=2});
