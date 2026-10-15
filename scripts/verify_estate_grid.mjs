/* Verify the shared Fountain Press Bookshelf in a real browser. */
import fs from 'node:fs';
const chrome='http://127.0.0.1:9237';
const base=process.env.ESTATE_BASE_URL||'http://127.0.0.1:8199';
const manifest=JSON.parse(fs.readFileSync(new URL('../../estate/manifest.json',import.meta.url),'utf8'));
const fronts=[...manifest.frontDoors].sort((a,b)=>a.rank-b.rank);
const expected=[fronts[0].entryEditionUrl,fronts[1].entryEditionUrl,new URL(fronts[2].firstHearing.readerPath,fronts[2].url).href];
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
  await cmd('Runtime.enable');await cmd('Page.enable');
  await cmd('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  await cmd('Page.navigate',{url:base+'/'});await wait(550);
  await cmd('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
  await cmd('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
  const state=await evalJS(`(()=>{const paper=document.querySelector('.bookshelf-paper');const covers=[...document.querySelectorAll('.shelf-cover img')];const anchors=[...document.querySelectorAll('.shelf-book')];const g=getComputedStyle(paper);const b=getComputedStyle(document.body);const parent=getComputedStyle(document.querySelector('.bookshelf-main'));const logo=document.querySelectorAll('.bookshelf-brand img');anchors[0]?.focus();const focus=getComputedStyle(anchors[0]);return {grid:!!paper,columns:g.gridTemplateColumns.split(' ').length,covers:covers.length,loaded:covers.every(x=>x.complete&&x.naturalWidth>0),links:anchors.map(a=>a.getAttribute('href')),names:anchors.map(a=>a.getAttribute('aria-label')),logo:logo.length,logoLoaded:[...logo].every(x=>x.complete&&x.naturalWidth>0),overflow:document.documentElement.scrollWidth>innerWidth+1,colors:[getComputedStyle(document.documentElement).backgroundColor,b.backgroundColor,parent.backgroundColor,g.backgroundColor],shadow:g.boxShadow,borders:[...document.querySelectorAll('.shelf-cover')].map(x=>getComputedStyle(x).borderTopWidth),focus:focus.outlineStyle,secondary:document.querySelectorAll('h1,h2,footer,.bookshelf-wordmark,.shelf-item-caption,.shelf-miniature,.shelf-cover-title,.bookshelf-pagination').length,topLinks:document.querySelectorAll('main a').length,emptySlots:document.querySelectorAll('.bookshelf-empty[aria-hidden="true"]').length,emptyBorder:getComputedStyle(document.querySelector('.bookshelf-empty')).borderTopStyle,emptyLinks:document.querySelectorAll('.bookshelf-empty a').length}})()`);
  console.log('PRESS_BOOKSHELF',label,JSON.stringify(state));
  if(!state.grid||state.columns!==cols||state.covers!==3||!state.loaded||state.logo!==1||!state.logoLoaded||state.overflow||state.secondary||state.topLinks!==3||state.emptySlots!==20||state.emptyBorder!=='dashed'||state.emptyLinks!==0)throw Error('Bookshelf geometry regression: '+label);
  if(JSON.stringify(state.links)!==JSON.stringify(expected)||state.names.some(x=>!x?.startsWith('Open ')))throw Error('Source-authorized editions or accessibility mismatch');
  if(state.colors[0]!==state.colors[1]||state.colors[3]!=='rgba(0, 0, 0, 0)'||state.shadow!=='none')throw Error('Inset paper or mismatched background at '+label);
  if(state.borders.some(x=>x==='0px')||state.focus==='none')throw Error('Unframed cover or inaccessible focus at '+label);
 }finally{ws.close();await fetch(chrome+'/json/close/'+target.id).catch(()=>{})}
}
for(const [name,w,h,c] of [['desktop',1366,768,6],['iPad landscape',1180,820,4],['iPad portrait',820,1180,4],['phone portrait',390,844,2],['phone landscape',844,390,4]])await test(name,w,h,c);
