#!/usr/bin/env node
/** Exhaustive source-addressed, actual-folio proof for the existing Linotype Reader.
 * Development/owner-WLAN observation ONLY. No edition writes, new renderer, or release.
 * Proofs EVERY composed leaf for each admitted work/platform; no sampling by default.
 */
import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const require=createRequire(import.meta.url);
const {webkit,chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const configs={
 'ipad-portrait':{width:820,height:1180,dpr:2},
 'ipad-landscape':{width:1180,height:820,dpr:2},
 'desktop':{width:1440,height:900,dpr:1},
 'phone':{width:390,height:844,dpr:3},
};
function args(){const a={origin:'http://192.168.8.50:8200',out:'',browser:'webkit',work:'',platform:'',limit:0,release:''};
 for(let i=2;i<process.argv.length;i++){
  const arg=process.argv[i];if(!arg.startsWith('--'))throw Error('Unknown argument: '+arg);
  const k=arg.slice(2);if(!(k in a))throw Error('Unknown option: '+arg);
  if(i+1>=process.argv.length)throw Error('Missing value '+arg);
  a[k]=process.argv[++i];
 }
 if(!a.out)throw Error('--out required. Save private screenshots outside public Git.');
 a.limit=Number(a.limit);
 if(!Number.isSafeInteger(a.limit)||a.limit<0)throw Error('--limit requires nonnegative integer');
 a.platforms=a.platform?a.platform.split(','):Object.keys(configs);
 for(const k of a.platforms)if(!(k in configs))throw Error('Unknown platform '+k);
 a.works=a.work?a.work.split(','):null;
 if(!['webkit','chromium'].includes(a.browser))throw Error('Unsupported browser '+a.browser);
 a.origin=new URL(a.origin).origin;
 return a;
}
function clean(s){return s.replace(/[^a-zA-Z0-9-]/g,'-').slice(0,130)}
function invariant(ok,msg){if(!ok)throw Error(msg)}
const input=args();const root=path.resolve(input.out);
invariant(!fs.existsSync(root),'Refuse to overwrite an existing proof run: '+root);
fs.mkdirSync(root,{recursive:true});
const log=fs.createWriteStream(path.join(root,'pages.jsonl'),{flags:'wx'});
const run={schema:'fountain.press.proof-run.v1',state:'IN_PROGRESS',origin:input.origin,
   startedAtUTC:new Date().toISOString(),browser:input.browser,platforms:input.platforms,
   requestedWorks:input.works,limit:input.limit,edition:{},expectedWorks:[],
   expectedFolios:{},visitedFolios:0,observedIssues:{blocking:0,review:0},
   machineProof:'IN_PROGRESS',editorialProof:'NOT_REVIEWED'};
fs.writeFileSync(path.join(root,'run.json'),JSON.stringify(run,null,2)+'\n',{flag:'wx'});
const browser=await (input.browser==='webkit'?webkit:chromium).launch({headless:true});
try{
 const reader=await browser.newPage({viewport:{width:820,height:1180}});
 const response=await reader.goto(input.origin+'/estate/books/catalog.json',{waitUntil:'domcontentloaded',timeout:30000});
 invariant(response.status()===200,'No admitted Bookshelf catalogue at '+input.origin);
 const catalog=JSON.parse(await response.body());
 invariant(Array.isArray(catalog.books),'Missing source-admitted book inventory');
 const admitted=catalog.books.filter(b=>b.stageOnly===true?b.publicReleaseAuthorized===false:b.publicReleaseAuthorized===true);
 const works=admitted.flatMap(b=>(b.orderedWorkIDs||[]).map(id=>({id,book:b.id})));
 invariant(works.length>0 && new Set(works.map(x=>x.id)).size===works.length,'Invalid unique publication membership');
 invariant(!input.works||input.works.every(id=>works.some(w=>w.id===id)),'Unadmitted requested work');
 const selected=works.filter(w=>!input.works||input.works.includes(w.id));
 invariant(selected.length>0,'No selected works');
 run.edition={status:catalog.status||catalog.publicationState||'unspecified',sourceGitRevision:catalog.sourceGitRevision,
  sourceOwner:catalog.sourceOwner,sourceReleaseID:input.release||catalog.currentReleaseID||'UNVERIFIED',sourcePredecessorReleaseID:catalog.publicationSnapshotSourceReleaseID||null,
  catalogueSHA256:sha(await response.body()),admittedWorkCount:works.length};
 run.expectedWorks=selected;
 await reader.close();
 const spec=browser.version();run.browserVersion=spec;
 const frame=(work,plat)=>path.join(root,'folios',plat,clean(work));
 for(const plat of input.platforms){
  run.expectedFolios[plat]={};const dims=configs[plat];
  const context=await browser.newContext({viewport:{width:dims.width,height:dims.height},deviceScaleFactor:dims.dpr,reducedMotion:'reduce'});
  try{
   for(const work of selected){
    const page=await context.newPage(),pageErrors=[];
    page.on('pageerror',e=>pageErrors.push(e.message));
    const url=input.origin+'/estate/#/read/'+encodeURIComponent(work.id);
    const resp=await page.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
    invariant(resp.status()===200,'Reader HTTP error '+resp.status());
    await page.waitForFunction(id=>{const v=document.querySelector('#page-viewport');return v?.dataset.layout==='ready'&&v.dataset.volume===id},work.id,{timeout:45000});
    await page.evaluate(()=>document.fonts.ready);
    const initial=await page.evaluate(()=>({total:Number(document.querySelector('#page-viewport').dataset.pages),
     sourceSha:document.querySelector(`template[data-reader-volume="${document.querySelector('#page-viewport').dataset.volume}"]`)?.content.querySelector('[data-source-work-sha256]')?.getAttribute('data-source-work-sha256')||null,
     sourceBlocks:[...document.querySelector(`template[data-reader-volume="${document.querySelector('#page-viewport').dataset.volume}"]`)?.content.querySelectorAll('[data-source-block]')||[]].map(e=>e.dataset.sourceBlock),
     sourceRanges:[...document.querySelector(`template[data-reader-volume="${document.querySelector('#page-viewport').dataset.volume}"]`)?.content.querySelectorAll('[data-source-block][data-source-from][data-source-to]')||[]].map(e=>({id:e.dataset.sourceBlock,from:Number(e.dataset.sourceFrom),to:Number(e.dataset.sourceTo)}))}));
    invariant(Number.isSafeInteger(initial.total)&&initial.total>0,'Uninitialized folio count '+work.id);
    run.expectedFolios[plat][work.id]={count:initial.total,sourceSha:initial.sourceSha,sourceBlocks:initial.sourceBlocks,sourceRanges:initial.sourceRanges};
    const seen=new Set();let turn=0;
    while(seen.size<initial.total){
      const state=await page.evaluate(()=>{
        const v=document.querySelector('#page-viewport'),sheets=[...v.querySelectorAll('.linotype-sheet')];
        function rect(el){if(!el)return null;const b=el.getBoundingClientRect();return{x:b.x,y:b.y,width:b.width,height:b.height,top:b.top,right:b.right,bottom:b.bottom,left:b.left}}
        return{total:Number(v.dataset.pages),mode:v.dataset.mode,volume:v.dataset.volume,
          sheets:sheets.map(s=>{
            const area=s.querySelector('.linotype-area'),ar=rect(area),sr=rect(s),figures=[...s.querySelectorAll('figure')];
            const fragments=[...area.querySelectorAll('[data-source-block]')].map(el=>({id:el.dataset.sourceBlock,
              from:el.hasAttribute('data-source-from')?Number(el.dataset.sourceFrom):null,
              to:el.hasAttribute('data-source-to')?Number(el.dataset.sourceTo):null,
              tag:el.tagName.toLowerCase(),className:typeof el.className==='string'?el.className:'',
              rect:rect(el),textLength:el.textContent.trim().length,
              lines:(()=>{if(el.tagName==='FIGURE')return null;const range=document.createRange();range.selectNodeContents(el);const lines=[...range.getClientRects()].filter(b=>b.width>3&&b.height>3);return lines.length})()}));
            const used=fragments.filter(f=>f.rect?.height>0).reduce((mx,f)=>Math.max(mx,f.rect.bottom),ar?.top||0);
            return{folio:Number((s.getAttribute('aria-label')||'').match(/^Page (\d+)$/)?.[1]),
              frame:sr,area:ar,sourceID:s.dataset.sourceId||null,kind:s.className,
              apparentBottomGap:ar?Math.max(0,ar.bottom-used):null,
              fragments,images:[...s.querySelectorAll('img')].map(img=>({src:img.getAttribute('src'),complete:img.complete,
                naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,rect:rect(img)})),
              figures:figures.map(f=>({sourceID:f.dataset.sourceBlock||null,rect:rect(f),
                caption:rect(f.querySelector('figcaption'))})),
              paragraphs:[...s.querySelectorAll('.linotype-area p')].map(p=>({id:p.dataset.sourceBlock||null,rect:rect(p),text:p.textContent.trim(),
                isHeading:p.classList.contains('frame-subheading')})),
              folioText:s.querySelector('.linotype-folio')?.textContent.trim()||null};
          })};
      });
      invariant(state.volume===work.id&&state.total===initial.total,'Reader source/version drift during proof '+work.id);
      invariant(state.sheets.length>0&&state.sheets.length<=2,'Page is not a single leaf or eligible spread');
      let newFolios=0;
      for(const s of state.sheets){
        invariant(Number.isInteger(s.folio)&&s.folio>0&&s.folio<=initial.total,'Unknown folio in '+work.id);
        if(seen.has(s.folio))continue;
        const blocking=[],review=[];seen.add(s.folio);newFolios++;
        if(!s.area||!s.frame||s.area.width<=0||s.area.height<=0)blocking.push('unmeasurable-type-area');
        if(s.area&&(s.area.left<s.frame.left-2||s.area.right>s.frame.right+2||s.area.top<s.frame.top-2||s.area.bottom>s.frame.bottom+2))blocking.push('type-area-outside-paper');
        for(const img of s.images)if(!img.complete||!img.naturalWidth||!img.naturalHeight)blocking.push('unloaded-image:'+img.src);
        for(const f of s.fragments)if(f.rect&&s.area&&(f.rect.left<s.area.left-3||f.rect.right>s.area.right+3||f.rect.top<s.area.top-3||f.rect.bottom>s.area.bottom+3))blocking.push('source-fragment-outside-measure:'+f.id);
        for(const fig of s.figures){if(fig.caption&&fig.rect&&(fig.caption.left<fig.rect.left-2||fig.caption.right>fig.rect.right+2||fig.caption.bottom>fig.rect.bottom+2))blocking.push('caption-outside-figure:'+fig.sourceID)}
        const para=s.paragraphs.filter(p=>p.rect&&p.rect.height>0);
        if(para.length&&para[para.length-1].isHeading)review.push('heading-at-page-foot-check-next-leaf');
        if(s.apparentBottomGap!=null&&s.area&&s.apparentBottomGap/s.area.height>0.55&&s.kind.includes('linotype-text'))review.push('unusually-open-leaf-needs-editorial-judgment');
        for(const f of s.fragments)if(f.from!=null&&f.to!=null&&f.from>0&&f.lines===1&&f.textLength>9)review.push('single-line-continuation:'+f.id);
        const sheet=page.locator('.linotype-sheet[aria-label="Page '+s.folio+'"]');
        const outdir=frame(work.id,plat);fs.mkdirSync(outdir,{recursive:true});
        const rel=path.join('folios',plat,clean(work.id),'folio-'+String(s.folio).padStart(5,'0')+'.png');
        await sheet.screenshot({path:path.join(root,rel),animations:'disabled',timeout:30000});
        const shot=fs.readFileSync(path.join(root,rel));
        const row={schema:'fountain.press.folio-proof.v1',book:work.book,work:work.id,platform:plat,browser:input.browser,
          folio:s.folio,total:initial.total,sourceSHA256:initial.sourceSha,createdAtUTC:new Date().toISOString(),
          frame:s.frame,area:s.area,folioText:s.folioText,kind:s.kind,sourceFragments:s.fragments,
          figures:s.figures,images:s.images,bottomGap:s.apparentBottomGap,
          screenshot:rel.split(path.sep).join('/'),screenshotSHA256:sha(shot),blocking,review};
        await new Promise((resolve,reject)=>log.write(JSON.stringify(row)+'\n',err=>err?reject(err):resolve()));
        run.visitedFolios++;run.observedIssues.blocking+=blocking.length;run.observedIssues.review+=review.length;
      }
      if(seen.size===initial.total)break;
      if(input.limit&&seen.size>=input.limit)break;
      invariant(turn++<=initial.total+5,'Page-navigation did not terminate at admitted count '+work.id);
      const previous=state.sheets.map(s=>s.folio).join(',');
      await page.getByRole('button',{name:'Next page'}).click();
      await page.waitForFunction(pr=>{let v=document.querySelector('#page-viewport');return[...v.querySelectorAll('.linotype-sheet')].map(s=>Number((s.getAttribute('aria-label')||'').match(/^Page (\d+)$/)?.[1])).join(',')!==pr},previous,{timeout:15000});
      invariant(newFolios>0,'Repeated page turn without new physical folio: '+work.id);
    }
    run.expectedFolios[plat][work.id].captured=seen.size;
    run.expectedFolios[plat][work.id].pageErrors=pageErrors;
    if(seen.size!==initial.total)run.expectedFolios[plat][work.id].partial=true;
    if(pageErrors.length)run.observedIssues.blocking+=pageErrors.length;
    console.log('PROOF',plat,work.id,seen.size+'/'+initial.total,'errors',pageErrors.length);
    fs.writeFileSync(path.join(root,'run.json'),JSON.stringify(run,null,2)+'\n');
    await page.close();
   }
  }finally{await context.close()}
 }
 const complete=!input.limit&&selected.length===works.length&&run.platforms.length===Object.keys(configs).length&&
   Object.values(run.expectedFolios).every(a=>Object.values(a).every(x=>x.count===x.captured&&!x.pageErrors.length));
 run.state=complete?'MACHINE_INVENTORY_COMPLETE':'SCOPED_OR_PARTIAL_PROOF';
 run.machineProof=run.observedIssues.blocking?'BLOCKING_FINDINGS':complete?'INVENTORY_COMPLETE_REVIEW_REQUIRED':'PARTIAL';
 run.finishedAtUTC=new Date().toISOString();
} catch(e){run.state='FAILED';run.machineProof='FAILED';run.failure=String(e.stack||e);run.finishedAtUTC=new Date().toISOString();process.exitCode=2;console.error(run.failure)}
finally{await browser.close();await new Promise(resolve=>log.end(resolve));fs.writeFileSync(path.join(root,'run.json'),JSON.stringify(run,null,2)+'\n');
 console.log('PROOF_RECORD',path.join(root,'run.json'),run.state,'folios',run.visitedFolios)}
