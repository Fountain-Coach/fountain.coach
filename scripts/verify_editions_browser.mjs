const chrome="http://127.0.0.1:9237";
const base=process.env.EDITION_BASE_URL||"http://127.0.0.1:8199";
const pause=n=>new Promise(ok=>setTimeout(ok,n));
const works=[
 ["teatro-an-unfinished-composition",1],
 ["semantic-compilation-the-archive-is-not-the-edition",1],
 ["reframe-and-the-business-value-of-the-estate",3]
];
async function caseStudy(label,width,height,slug,plates){
 const target=await(await fetch(chrome+"/json/new?about:blank",{method:"PUT"})).json();
 const ws=new WebSocket(target.webSocketDebuggerUrl);
 await new Promise((ok,no)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",no,{once:true})});
 let sequence=0;const pending=new Map(), errors=[];
 ws.addEventListener("message",ev=>{
  const m=JSON.parse(ev.data);
  if(m.method==="Runtime.exceptionThrown")errors.push(m.params.exceptionDetails?.exception?.description||"exception");
  if(pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id)}
 });
 const command=(method,params={})=>new Promise(ok=>{const id=++sequence;pending.set(id,ok);ws.send(JSON.stringify({id,method,params}))});
 const evaluate=async(expression)=>{
  const r=await command("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
  if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));
  return r.result.result.value;
 };
 try {
  await command("Runtime.enable");await command("Page.enable");
  await command("Network.setCacheDisabled",{cacheDisabled:true});
  await command("Emulation.setDeviceMetricsOverride",{width,height,deviceScaleFactor:1,mobile:width<600});
  await command("Page.navigate",{url:base+"/editions/essays/"+slug+"/"});
  let status="waiting";
  for(let i=0;i<60;i++){
   await pause(225);
   status=await evaluate("document.body?.dataset.bookReady||'waiting'");
   if(status==="true"||status==="fallback")break;
  }
  if(status!=="true")throw Error("fallback: "+await evaluate("document.body?.dataset.bookError||''")+" exceptions "+errors.join(" "));
  const state=async()=>await evaluate("(() => {const v=document.getElementById('book-viewport');const s=document.querySelector('.linotype-stage .linotype-sheet');return {chapters:document.querySelectorAll('[data-book-chapter]').length,images:document.querySelectorAll('#book-flow img').length,pages:Number(document.body.dataset.bookPageCount),mode:document.body.dataset.bookMode,edition:document.body.dataset.editionId,folio:document.getElementById('book-page-count').textContent,overX:document.documentElement.scrollWidth>innerWidth+1,overY:document.documentElement.scrollHeight>innerHeight+1,paper:s?.getBoundingClientRect().toJSON(),area:v?.getBoundingClientRect().toJSON()}})()");
  const a=await state();
  console.log("COMPOSED",label,slug,JSON.stringify(a));
  if(a.chapters!==1||a.images!==plates||a.pages<7||a.pages>300||a.overX||a.overY||!a.edition)throw Error("invalid source/layout");
  await evaluate("(document.getElementById('book-next').disabled?document.getElementById('book-prev'):document.getElementById('book-next')).click()");
  await pause(140);
  const b=await state();
  if(b.folio===a.folio)throw Error("page turn did not advance");
  await evaluate("document.getElementById('book-toc-button').click()");
  if(!await evaluate("document.getElementById('book-contents').open"))throw Error("contents failed");
  if(errors.length)throw Error(errors.join("; "));
  console.log("PASSED",label,slug,a.pages,"pages");
 } finally {
  ws.close();
  await fetch(chrome+"/json/close/"+target.id).catch(()=>{});
 }
}
for(const path of ["/","/editions/","/editions/essays/",...works.map(w=>"/editions/essays/"+w[0]+"/")]){
 const r=await fetch(base+path);
 if(r.status!==200)throw Error("Missing edition route "+path+" "+r.status);
 if(path==="/"){const html=await r.text();if(!html.includes('class="shelf-grid"')||html.includes('id="book-viewport"'))throw Error("Root is not estate thumbnail grid");}
}
for(const [label,w,h] of [["iPad landscape",1180,820],["iPad portrait",820,1180],["phone portrait",390,844]]){
 for(const [slug,plates] of works){
  try {await caseStudy(label,w,h,slug,plates)}
  catch(e){console.error("FAIL",label,slug,String(e));process.exitCode=1}
 }
}
