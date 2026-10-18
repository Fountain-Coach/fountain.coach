// Verify native browser Back preserves the linked reading position.
// Uses Chrome CDP directly, no installed test runner or production mutation.
import fs from 'node:fs';
const debug=process.env.CHROME_DEBUG_URL||'http://127.0.0.1:9347';
const base=process.env.SCROLL_TEST_ORIGIN||'https://fountain.coach';
const target=await(await fetch(debug+'/json/new?about:blank',{method:'PUT'})).json();
const ws=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((done,fail)=>{ws.addEventListener('open',done,{once:true});ws.addEventListener('error',fail,{once:true})});
let id=0;const pending=new Map();
ws.addEventListener('message',msg=>{
  const response=JSON.parse(msg.data);
  if(pending.has(response.id)){pending.get(response.id)(response);pending.delete(response.id)}
});
const cmd=(method,params={})=>new Promise((resolve,reject)=>{
  const key=++id;
  pending.set(key,r=>r.error?reject(new Error(JSON.stringify(r.error))):resolve(r.result));
  ws.send(JSON.stringify({id:key,method,params}));
});
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function evalJS(expression){
  const r=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));
  return r.result?.value;
}
async function until(pred,limit=10000){
  const start=Date.now();while(Date.now()-start<limit){try{const x=await evalJS(pred);if(x)return x}catch{}await wait(130)}
  throw Error('timeout '+pred);
}
async function caseOf(startPath,selector,desiredScroll){
  await cmd('Page.navigate',{url:base+startPath});
  await until('document.readyState==="complete"');
  await wait(300);
  const startInfo=await evalJS('({url:location.pathname, mode:history.scrollRestoration,max:document.documentElement.scrollHeight-innerHeight})');
  if(startInfo.max<desiredScroll+180)throw Error('Page too short for scroll test '+JSON.stringify(startInfo));
  const state=await evalJS(`(()=>{
    window.scrollTo(0,${desiredScroll});
    const link=document.querySelector(${JSON.stringify(selector)});
    if(!link)throw Error('link missing: '+${JSON.stringify(selector)});
    // Link must be actually visible before a genuine click.
    link.scrollIntoView({block:'center',behavior:'instant'});
    const from=window.scrollY;
    const href=link.href;
    link.click();
    return {from,href};
  })()`);
  await until(`location.href===${JSON.stringify(state.href)}`);
  await wait(350);
  await evalJS('history.back()');
  await until(`location.pathname===${JSON.stringify(startPath)}`);
  await wait(1000);
  const after=await evalJS('({y:scrollY,mode:history.scrollRestoration,href:location.href})');
  const tolerance=18;
  const pass=Math.abs(after.y-state.from)<=tolerance;
  console.log('BACK_SCROLL',JSON.stringify({route:startPath,scrollBefore:state.from,scrollAfter:after.y,delta:after.y-state.from,modeOnLoad:startInfo.mode,modeAfter:after.mode,pass}));
  if(startInfo.mode!=='auto'||after.mode!=='auto')throw Error('site disabled native scroll restoration '+startPath);
  if(!pass)throw Error('browser Back changed scroll position '+startPath);
}
try {
  await cmd('Page.enable');await cmd('Runtime.enable');
  const width=Number(process.env.SCROLL_TEST_WIDTH||1050);
  const height=Number(process.env.SCROLL_TEST_HEIGHT||740);
  await cmd('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  await caseOf('/essays/','.essay-gallery-card:last-of-type a[href]',950);
  await caseOf('/essays/the-composable-book/','.references a[href^="/essays/"]',1650);
  await caseOf('/','.estate-card.essay-entry a[href^="/essays/"]',1100);
  console.log('BACK_SCROLL_NATIVE_ACCEPTED 3 publication routes');
}finally{
  ws.close();await fetch(debug+'/json/close/'+target.id).catch(()=>{});
}
