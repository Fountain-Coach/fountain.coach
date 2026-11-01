const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path');
const w=__dirname;
const abstracts=JSON.parse(fs.readFileSync(path.join(w,'essay-abstracts.json'),'utf8')).items;
const files={'/estate/':'index.html','/estate/assets/linotype/reading-first-app.js':'reading-first-app.js','/estate/assets/linotype/reading-first-shell.css':'reading-first-shell.css','/estate/assets/linotype/reading-first-press-engine.js':'press-viewport-engine.js'};
(async()=>{
 const browser=await webkit.launch({headless:true}),ctx=await browser.newContext({viewport:{width:1200,height:630},deviceScaleFactor:1});
 await ctx.route('**/*',r=>{const url=new URL(r.request().url()),f=files[url.pathname];if(f&&url.host==='192.168.8.50:8243')return r.fulfill({status:200,body:fs.readFileSync(path.join(w,f)),contentType:f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':'text/html'});return r.continue()});
 const p=await ctx.newPage();
 await p.goto('https://192.168.8.50:8243/estate/#/read/essay--to-read-is-not-to-remember',{waitUntil:'domcontentloaded'});
 await p.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:17000});
 const preview=path.join(w,'essay-share-did-the-machine-actually-read-the-book.png');
 await p.screenshot({path:preview});
 await p.close();await ctx.close();await browser.close();
 const manifest={schema:'fountain.press.essay-share-art.v1',status:'private-WLAN-candidate',note:'One human-readable composition; unchanged source image where suitable; otherwise an actual page screenshot. No claim of public social crawler access.',essays:{}};
 for(const [slug,x] of Object.entries(abstracts)){
  const html=fs.readFileSync(path.join(w,'integrated-volumes.html'),'utf8');
  const id='data-reader-volume="essay--'+slug+'"';
  const start=html.indexOf(id),end=html.indexOf('</template>',start);
  if(start<0||end<0)throw Error('Missing manuscript '+slug);
  const chunk=html.slice(start,end);
  const match=chunk.match(/<figure class="[^"]*frame-essay-hero[^"]*"[^>]*><img[^>]*src="([^"]+)"[^>]*alt="([^"]+)"/);
  if(x.share==='source-image'&&!match)throw Error('Missing shareable source art '+slug);
  const art=x.share==='source-image'?{type:'original-source-image',path:match[1],alt:match[2]}:{type:'actual-typeset-page-preview',path:'/estate/assets/essay-share/did-the-machine-actually-read-the-book.png',alt:'Typeset opening spread of Did the Machine Actually Read the Book? showing its title, argument and original essay typography'};
  manifest.essays[slug]={reader:'#/read/essay--'+slug,abstract:x.summary,art};
 }
 fs.writeFileSync(path.join(w,'essay-share-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 const stat=fs.statSync(preview);console.log('SHARE_PREVIEW',stat.size,'bytes',JSON.stringify({width:1200,height:630,essays:Object.keys(manifest.essays).length,printPages:Object.values(manifest.essays).filter(v=>v.art.type==='actual-typeset-page-preview').length}));
})().catch(e=>{console.error(e.stack);process.exitCode=2});
