import fs from 'node:fs';
import crypto from 'node:crypto';
const root=process.env.ESTATE_BASE_URL||'http://192.168.8.249:8180';
const chrome='http://127.0.0.1:9237';
const output=process.env.JOURNEY_CAPTURE_DIR||'/tmp/first-readings';
const work='teatro-an-unfinished-composition';
const art='/essays/'+work+'/assets/teatro-score-memory-vector-human-condition.svg';
fs.mkdirSync(output,{recursive:true});
const admitted=await(await fetch(root+'/collections/first-readings/collection.json')).json();
const bytes=Buffer.from(await(await fetch(root+art)).arrayBuffer());
if(admitted.works.length!==1||admitted.works[0].coverArtworkSHA256!==crypto.createHash('sha256').update(bytes).digest('hex'))throw Error('Unadmitted artwork');
const nap=n=>new Promise(r=>setTimeout(r,n));
async function proof(label,width,height){
 const tab=await(await fetch(chrome+'/json/new?about:blank',{method:'PUT'})).json();
 const ws=new WebSocket(tab.webSocketDebuggerUrl);
 await new Promise(r=>ws.addEventListener('open',r,{once:true}));
 const pending=new Map();let counter=0;
 ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id)}});
 const cmd=(method,params={})=>new Promise(r=>{let id=++counter;pending.set(id,r);ws.send(JSON.stringify({id,method,params}))});
 const ev=async expression=>{const r=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));return r.result.result.value};
 const wait=async expression=>{for(let i=0;i<70;i++){if(await ev(expression))return;await nap(150)}throw Error('timeout '+expression)};
 const click=async selector=>{let rect=await ev('document.querySelector('+JSON.stringify(selector)+')?.getBoundingClientRect().toJSON()');if(!rect||rect.width<12||rect.height<12)throw Error('Not visible '+selector);const x=rect.x+rect.width/2,y=rect.y+rect.height/2;await cmd('Input.dispatchMouseEvent',{type:'mousePressed',x,y,button:'left',clickCount:1});await cmd('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button:'left',clickCount:1})};
 const shot=async stage=>{const r=await cmd('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(output+'/'+label+'-'+stage+'.png',Buffer.from(r.result.data,'base64'))};
 try{
 await cmd('Page.enable');await cmd('Runtime.enable');await cmd('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
 await cmd('Page.navigate',{url:root+'/'});
 await wait('document.querySelectorAll(".shelf-book").length===2');
 const estate=await ev('({links:document.querySelectorAll(".shelf-book").length,empty:document.querySelectorAll(".bookshelf-empty").length,label:document.querySelector("[data-book-id=first-reading] a")?.getAttribute("aria-label"),teatro:!!document.querySelector("[data-book-id=teatro]"),coverName:document.querySelector("[data-book-id=first-reading] .shelf-cover-name")?.textContent})');
 if(estate.empty!==20||estate.teatro||estate.coverName!=='First Readings'||!estate.label?.includes('First Readings'))throw Error('Estate category confusion '+JSON.stringify(estate));
 await shot('estate');await click('[data-book-id=first-reading] a.shelf-book');
 await wait('location.pathname==="/collections/first-readings/" && document.body?.dataset.collectionId==="first-readings" && !!document.getElementById("work-teatro-an-unfinished-composition")');
 await wait('document.querySelector("[data-book-id=teatro-an-unfinished-composition] img")?.naturalWidth>0');
 const collection=await ev('({title:document.querySelector(".bookshelf-collection-masthead h1")?.textContent,work:document.querySelector("[data-book-id=teatro-an-unfinished-composition] img")?.getAttribute("src"),artLoaded:document.querySelector("[data-book-id=teatro-an-unfinished-composition] img")?.naturalWidth>0,imageWidth:document.querySelector("[data-book-id=teatro-an-unfinished-composition] img")?.getBoundingClientRect().width,imageOpacity:getComputedStyle(document.querySelector("[data-book-id=teatro-an-unfinished-composition] img")).opacity,parent:document.querySelector(".bookshelf-collection-masthead a")?.getAttribute("href"),slot:!!document.getElementById("work-teatro-an-unfinished-composition"),coverName:document.querySelector("[data-book-id=teatro-an-unfinished-composition] .shelf-cover-name")?.textContent})');
 if(!collection.artLoaded||collection.title!=='First Readings'||collection.coverName!=='An Unfinished Composition'||collection.work!==art||!collection.slot||collection.parent!=='/')throw Error('Collection identity failure '+JSON.stringify(collection));
 await shot('collection');await click('[data-book-id=teatro-an-unfinished-composition] a.shelf-book');
 await wait('location.pathname.includes("/editions/essays/teatro-an-unfinished-composition/")&&document.body?.dataset.bookReady==="true"');
 const cover=await ev('(()=>{let leaf=document.querySelector(".linotype-stage .linotype-sheet");let img=leaf?.querySelector(".work-cover-art");return {page:leaf?.dataset.sourceId,title:leaf?.querySelector("h1")?.textContent,image:img?getComputedStyle(img).backgroundImage:null,visible:!!img?.getClientRects().length,back:document.querySelector("a.book-back")?.getAttribute("href"),heading:document.querySelector(".work-reading-identity")?.textContent,folio:leaf?.querySelector(".linotype-folio")?.textContent,overflow:document.documentElement.scrollWidth>innerWidth+1}})()');
 if(cover.page!=='book-cover'||!cover.visible||!cover.image.includes(art)||!cover.title.includes('An Unfinished Composition')||!cover.heading?.includes('AN UNFINISHED COMPOSITION')||!cover.folio?.includes('FIRST READINGS')||cover.back!=='/collections/first-readings/'||cover.overflow||await ev('!!document.querySelector("#book-type-button")'))throw Error('Unrecognizable opening '+JSON.stringify(cover));
 await shot('work-cover');
 if(width<600){
  await cmd('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  await cmd('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
 }else await click('#book-next');
 await nap(240);
 const reading=await ev('(()=>{const page=document.querySelector(".linotype-stage .linotype-sheet");const legal=document.querySelector(".book-legal")?.getBoundingClientRect();const progress=document.querySelector(".book-progress")?.getBoundingClientRect();const prev=document.querySelector("#book-prev")?.getBoundingClientRect();const next=document.querySelector("#book-next")?.getBoundingClientRect();const overlap=(a,b)=>a&&b&&a.left<b.right&&b.left<a.right&&a.top<b.bottom&&b.top<a.bottom;return {source:page?.dataset.sourceId,back:document.querySelector("a.book-back")?.getAttribute("href"),ordinal:page?.querySelector(".book-ordinal")?.textContent,running:page?.querySelector(".linotype-running")?.textContent,folio:page?.querySelector(".linotype-folio")?.textContent,appearanceButton:!!document.querySelector("#book-type-button"),legalOverlap:!!(overlap(legal,progress)||overlap(legal,prev)||overlap(legal,next)),phoneLayout:document.body.dataset.deviceNavigation==="phone",footerHidden:getComputedStyle(document.querySelector(".book-pagination")).display==="none",legalLinks:document.querySelectorAll(".book-legal a").length,atlasVisible:!!document.querySelector("#book-page-atlas")?.getBoundingClientRect().height,legalVisible:!!(legal&&legal.width>50&&legal.top>=0&&legal.bottom<=innerHeight+1),legalRect:legal?.toJSON(),innerHeight,footerRect:document.querySelector(".book-pagination")?.getBoundingClientRect().toJSON(),viewportOverflow:document.documentElement.scrollWidth>innerWidth+1}})()');
 if(reading.source==='book-cover'||reading.back!=='/collections/first-readings/'||!reading.ordinal?.includes('FIRST READINGS')||reading.ordinal.includes('01 / 03')||reading.running?.includes('ESSAYS')||!reading.folio?.includes('FIRST READINGS')||reading.appearanceButton||reading.legalOverlap||reading.legalLinks!==3||(!reading.phoneLayout&&!reading.legalVisible)||(reading.phoneLayout&&(!reading.footerHidden||!reading.atlasVisible))||reading.viewportOverflow)throw Error('Reading identity or footer layout failure '+JSON.stringify(reading));
 await shot('reading');await click('a.book-back');await wait('location.pathname==="/collections/first-readings/" && document.body?.dataset.collectionId==="first-readings" && !!document.getElementById("work-teatro-an-unfinished-composition")');
 await ev('history.back()');await wait('location.pathname.includes("/editions/essays/teatro-an-unfinished-composition/")');
 console.log('FIRST_READINGS_JOURNEY_PASS',label,JSON.stringify({estate,collection,cover,reading,history:true}));
 }finally{ws.close();await fetch(chrome+'/json/close/'+tab.id).catch(()=>{})}
}
for(const v of [['ipad-portrait',820,1180],['ipad-landscape',1180,820],['phone-portrait',390,844]])await proof(...v);
