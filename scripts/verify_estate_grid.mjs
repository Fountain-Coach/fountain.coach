/* Read-only browser proof of the source-owned estate grid. */
const chrome='http://127.0.0.1:9237';
const base=process.env.ESTATE_BASE_URL||'http://127.0.0.1:8199';
const wait=ms=>new Promise(done=>setTimeout(done,ms));
async function test(label,width,height,cols){
 const target=await(await fetch(chrome+'/json/new?about:blank',{method:'PUT'})).json();
 const ws=new WebSocket(target.webSocketDebuggerUrl);
 await new Promise((done,fail)=>{ws.addEventListener('open',done,{once:true});ws.addEventListener('error',fail,{once:true})});
 let seq=0;const pending=new Map();
 ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id)}});
 const cmd=(method,params={})=>new Promise(done=>{const id=++seq;pending.set(id,done);ws.send(JSON.stringify({id,method,params}))});
 const evalJS=async expression=>{const m=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(m.result.exceptionDetails)throw Error(JSON.stringify(m.result.exceptionDetails));return m.result.result.value};
 try{
  await cmd('Runtime.enable');await cmd('Page.enable');await cmd('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  await cmd('Page.navigate',{url:base+'/'});await wait(400);
  const state=await evalJS(`(()=>{const g=document.querySelector('.shelf-grid');const img=[...document.querySelectorAll('.shelf-entry img')];const a=[...document.querySelectorAll('.shelf-entry a')];return {grid:!!g,columns:g?getComputedStyle(g).gridTemplateColumns.split(' ').length:0,covers:img.length,loaded:img.every(x=>x.complete&&x.naturalWidth>0),links:a.map(x=>x.getAttribute('href')),logo:document.querySelectorAll('.shelf-brand img').length,overflow:document.documentElement.scrollWidth>innerWidth+1,field:getComputedStyle(document.body).backgroundColor,mark:getComputedStyle(document.querySelector('.shelf-brand img')).width,placeholder:!!document.querySelector('.instrument-slot'),oldContents:!!document.querySelector('.edition-list')}})()`);
  console.log('ESTATE_GRID',label,JSON.stringify(state));
  if(!state.grid||state.columns!==cols||state.covers!==3||!state.loaded||state.logo!==1||state.overflow||state.placeholder||state.oldContents)throw Error('Grid regression: '+label);
  if(state.links[0]!=='/editions/essays/'||!state.links[1].includes('solstice/editions/first-reading/')||state.links[2]!=='https://teatro.fountain.coach/')throw Error('Incorrect authorized edition destinations');
 }finally{ws.close();await fetch(chrome+'/json/close/'+target.id).catch(()=>{})}
}
for(const [name,w,h,c] of [['desktop',1366,768,4],['iPad landscape',1180,820,4],['iPad portrait',820,1180,4],['phone portrait',390,844,2],['phone landscape',844,390,4]])await test(name,w,h,c);
