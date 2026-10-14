const chrome="http://127.0.0.1:9237";
const base=process.env.ESSAY_BASE_URL||"http://127.0.0.1:8199/editions/essays/";
const pause=n=>new Promise(r=>setTimeout(r,n));
async function run(label,width,height){
 const target=await(await fetch(chrome+"/json/new?about:blank",{method:"PUT"})).json();
 const ws=new WebSocket(target.webSocketDebuggerUrl);
 await new Promise((ok,no)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",no,{once:true})});
 let nextId=0;const pending=new Map();const errors=[];
 ws.addEventListener("message",ev=>{
  const m=JSON.parse(ev.data);
  if(m.method==="Runtime.exceptionThrown")errors.push(m.params.exceptionDetails?.exception?.description||"runtime exception");
  if(m.method==="Runtime.consoleAPICalled"&&m.params.type==="error")errors.push(m.params.args.map(x=>x.value||x.description||"").join(" "));
  if(pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id)}
 });
 const cmd=(method,params={})=>new Promise(done=>{const id=++nextId;pending.set(id,done);ws.send(JSON.stringify({id,method,params}))});
 const evaluate=async(expression)=>{
  const r=await cmd("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
  if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));
  return r.result.result.value;
 };
 try{
  await cmd("Runtime.enable");await cmd("Page.enable");
  await cmd("Emulation.setDeviceMetricsOverride",{width,height,deviceScaleFactor:1,mobile:width<600});
  await cmd("Page.navigate",{url:base});
  let state="waiting";
  for(let i=0;i<60;i++){await pause(200);state=await evaluate("document.body?.dataset.bookReady||'waiting'");if(state==="true"||state==="fallback")break}
  if(state!=="true")throw Error("fallback "+state+" : "+await evaluate("document.body?.dataset.bookError||''")+" : "+errors.join(" "));
  const capture="(() => {const root=document.getElementById('book-viewport');const x=root.getBoundingClientRect();const sheet=document.querySelector('.linotype-stage .linotype-sheet')?.getBoundingClientRect();return {pages:+document.body.dataset.bookPageCount,mode:document.body.dataset.bookMode,chapters:document.querySelectorAll('#book-flow [data-book-chapter]').length,images:document.querySelectorAll('#book-flow img').length,overX:document.documentElement.scrollWidth>innerWidth+1,overY:document.documentElement.scrollHeight>innerHeight+1,folio:document.getElementById('book-page-count').textContent,location:document.getElementById('book-location').textContent,viewport:[x.x,x.y,x.width,x.height],paper:sheet&&[sheet.x,sheet.y,sheet.width,sheet.height]}})()";
  const a=await evaluate(capture);
  console.log("COMPOSED",label,JSON.stringify(a));
  if(a.pages<9||a.pages>300||a.chapters!==3||a.images!==5||a.overX||a.overY)throw Error("unexpected geometry/content");
  await evaluate("document.getElementById('book-next').click()");await pause(180);
  const b=await evaluate(capture);
  if(b.folio===a.folio)throw Error("page next did not turn");
  await evaluate("document.getElementById('book-toc-button').click()");
  if(!(await evaluate("document.getElementById('book-contents').open")))throw Error("contents did not open");
  await evaluate("document.querySelector('[data-book-toc-target=\"semantic-compilation-the-archive-is-not-the-edition\"]').click()");
  const c=await evaluate(capture);
  if(!c.location.includes("Semantic Compilation"))throw Error("chapter selection failed "+JSON.stringify(c));
  if(errors.length)throw Error(errors.join("; "));
  console.log("PASSED",label,a.mode,a.pages,"sheets");
 } finally {
  ws.close();
  await fetch(chrome+"/json/close/"+target.id).catch(()=>{});
 }
}
for(const [label,w,h] of [["iPad landscape",1180,820],["iPad portrait",820,1180],["desktop",1366,900],["phone portrait",390,844],["phone landscape",844,390]]){
 try{await run(label,w,h)}catch(e){console.error("FAIL",label,String(e));process.exitCode=1}
}
