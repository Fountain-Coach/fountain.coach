#!/usr/bin/env node
/* Test anonymous space, membership, inherited color, and navigation. */
import fs from "node:fs";
import path from "node:path";
const BASE=process.env.VISUAL_FIXTURE_BASE||"http://127.0.0.1:8199";
const ROUTE="/fixtures/semantic-visual-bookshelf/";
const CDP=process.env.CHROME_CDP||"http://127.0.0.1:9237";
const OUTPUT=process.env.VISUAL_FIXTURE_CAPTURE||"/tmp/spatial-bookshelf";
fs.mkdirSync(OUTPUT,{recursive:true});
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const book=id=>'[data-book-id="'+id+'"] a.shelf-book';
const space=id=>'[data-space-id="'+id+'"] a.shelf-space';
async function scenario(label,width,height){
 const tab=await (await fetch(CDP+"/json/new?about:blank",{method:"PUT"})).json();
 const ws=new WebSocket(tab.webSocketDebuggerUrl);
 await new Promise(r=>ws.addEventListener("open",r,{once:true}));
 let seq=0;
 const pending=new Map();
 ws.addEventListener("message",e=>{
  const response=JSON.parse(e.data);
  if(pending.has(response.id)){
   pending.get(response.id)(response);pending.delete(response.id);
  }
 });
 const cmd=(method,params={})=>new Promise(r=>{
  const id=++seq;pending.set(id,r);
  ws.send(JSON.stringify({id,method,params}));
 });
 const ev=async expression=>{
  const x=await cmd("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
  if(x.result.exceptionDetails)throw Error(JSON.stringify(x.result.exceptionDetails));
  return x.result.result.value;
 };
 const wait=async condition=>{
  for(let n=0;n<90;n++){if(await ev(condition))return;await delay(150)}
  throw Error("Wait timed out: "+condition);
 };
 const nav=async route=>{
  await cmd("Page.navigate",{url:BASE+route});
  await wait("location.pathname==="+JSON.stringify(route.split("#")[0])+" && document.readyState==='complete'");
 };
 const hit=sel=>"(()=>{const r=document.querySelector("+JSON.stringify(sel)+")?.getBoundingClientRect();return !!r&&r.width>15&&r.height>15})()";
 const click=async sel=>{
  await wait(hit(sel));
  await ev("document.querySelector("+JSON.stringify(sel)+").scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})");
  await wait(hit(sel));
  const r=await ev("document.querySelector("+JSON.stringify(sel)+").getBoundingClientRect().toJSON()");
  const x=r.x+r.width/2,y=r.y+r.height/2;
  await cmd("Input.dispatchMouseEvent",{type:"mousePressed",x,y,button:"left",clickCount:1});
  await cmd("Input.dispatchMouseEvent",{type:"mouseReleased",x,y,button:"left",clickCount:1});
 };
 const key=async name=>{
  const k=name==="Enter"?13:name==="ArrowRight"?39:name==="ArrowLeft"?37:27;
  await cmd("Input.dispatchKeyEvent",{type:"keyDown",key:name,code:name,windowsVirtualKeyCode:k});
  await cmd("Input.dispatchKeyEvent",{type:"keyUp",key:name,code:name,windowsVirtualKeyCode:k});
 };
 const shot=async name=>{
  const r=await cmd("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
  fs.writeFileSync(path.join(OUTPUT,label+"-"+name+".png"),Buffer.from(r.result.data,"base64"));
 };
 try{
  await cmd("Page.enable");await cmd("Runtime.enable");
  await cmd("Emulation.setDeviceMetricsOverride",{width,height,deviceScaleFactor:1,mobile:width<600});
  await nav(ROUTE);
  await wait(hit(space("s-01")));await wait(hit(space("s-02")));
  await wait('getComputedStyle(document.querySelector("[data-space-id=s-01] .shelf-space")).borderLeftWidth==="7px"');
  const root=await ev('(()=>{const a=[...document.querySelectorAll(".shelf-space")];return {spaces:a.length,books:document.querySelectorAll(".shelf-book").length,images:document.querySelectorAll("img").length,rootBack:!!document.querySelector(".publisher-circle-return"),members:a.map(x=>x.querySelectorAll(".shelf-space-member").length),colors:a.map(x=>getComputedStyle(x).borderLeftColor),ratios:a.map(x=>+(x.getBoundingClientRect().width/x.getBoundingClientRect().height).toFixed(2)),overflow:document.documentElement.scrollWidth>innerWidth+1}})()');
  if(root.spaces!==2||root.books||root.images||root.rootBack||
     root.members.join(",")!=="3,1"||root.colors[0]===root.colors[1]||
     root.ratios.some(x=>x<=1)||root.overflow)throw Error("Containing fields invalid "+JSON.stringify(root));
  await shot("containing-fields");
  await click(space("s-01"));
  await wait('document.body?.dataset.spacePosition==="0" && document.body?.dataset.collectionId==="s-01"');
  await wait(hit(book("o-02")));
  const one=await ev('({books:document.querySelectorAll(".shelf-book").length,empties:document.querySelectorAll(".bookshelf-empty").length,color:getComputedStyle(document.querySelector(".bookshelf-paper")).borderLeftColor,parent:document.querySelector(".publisher-circle-return")?.getAttribute("href"),extraArrow:!!document.querySelector(".bookshelf-collection-masthead a"),overflow:document.documentElement.scrollWidth>innerWidth+1})');
  if(one.books!==3||one.empties!==20||one.color!==root.colors[0]||one.parent!==ROUTE||one.extraArrow||one.overflow)throw Error("Scope 0 invalid "+JSON.stringify(one));
  await shot("inside-space-0");
  await click(book("o-02"));
  await wait('document.body?.dataset.objectId==="o-02" && document.body?.dataset.spaceId==="s-01"');
  await wait('getComputedStyle(document.querySelector(".visual-page")).borderLeftWidth==="7px"');
  await wait('document.querySelector("#visual-book")?.dataset.invalid==="false"');
  const readerOne=await ev('({token:document.body.dataset.objectToken,color:getComputedStyle(document.querySelector(".visual-page")).borderLeftColor,parent:document.querySelector(".visual-return").getAttribute("href"),leaves:document.querySelectorAll(".visual-page").length,images:document.querySelectorAll("img").length})');
  if(readerOne.color!==root.colors[0]||readerOne.leaves!==3||readerOne.images||!readerOne.parent.endsWith("/spaces/s-01/#work-o-02"))throw Error("Reader failed membership "+JSON.stringify(readerOne));
  await shot("blank-reader-0");
  await key("ArrowRight");
  await wait('location.hash==="#plate-2" && !document.querySelector("#plate-2").hidden');
  await shot("second-blank-leaf");
  await ev("history.back()");
  await wait('location.hash==="" && !document.querySelector("#plate-1").hidden');
  const box=await ev('document.querySelector("#visual-book").getBoundingClientRect().toJSON()');
  const x=box.x+box.width*.75,y=box.y+box.height*.5;
  await cmd("Input.dispatchMouseEvent",{type:"mousePressed",x,y,button:"left",clickCount:1});
  await cmd("Input.dispatchMouseEvent",{type:"mouseMoved",x:x-105,y,button:"left"});
  await cmd("Input.dispatchMouseEvent",{type:"mouseReleased",x:x-135,y,button:"left",clickCount:1});
  await wait('location.hash==="#plate-2"');
  await nav(ROUTE+"spaces/s-01/objects/o-02/#plate-99");
  await wait('document.querySelector("#visual-book")?.dataset.invalid==="true"');
  if(await ev('document.querySelectorAll(".visual-page:not([hidden])").length'))throw Error("Unknown leaf admitted");
  await nav(ROUTE+"spaces/s-01/objects/o-02/#plate-3");
  await wait('!document.querySelector("#plate-3").hidden');
  await key("Escape");
  await wait('document.body?.dataset.collectionId==="s-01" && location.hash==="#work-o-02"');
  await click(".publisher-circle-return");
  await wait('location.pathname==='+JSON.stringify(ROUTE)+' && !document.body.dataset.collectionId');
  await click(space("s-02"));
  await wait('document.body?.dataset.spacePosition==="1" && document.body?.dataset.collectionId==="s-02"');
  await wait(hit(book("o-02")));
  const two=await ev('({books:document.querySelectorAll(".shelf-book").length,color:getComputedStyle(document.querySelector(".bookshelf-paper")).borderLeftColor})');
  if(two.books!==1||two.color!==root.colors[1])throw Error("Scope 1 invalid "+JSON.stringify(two));
  await shot("inside-space-1");
  await click(book("o-02"));
  await wait('document.body?.dataset.objectId==="o-02" && document.body?.dataset.spaceId==="s-02"');
  await wait('getComputedStyle(document.querySelector(".visual-page")).borderLeftWidth==="7px"');
  await wait('document.querySelector("#visual-book")?.dataset.invalid==="false"');
  const readerTwo=await ev('({token:document.body.dataset.objectToken,color:getComputedStyle(document.querySelector(".visual-page")).borderLeftColor,parent:document.querySelector(".visual-return").getAttribute("href")})');
  if(readerOne.token!==readerTwo.token||readerTwo.color!==root.colors[1]||
     !readerTwo.parent.endsWith("/spaces/s-02/#work-o-02"))throw Error("Shared object identity/context invalid "+JSON.stringify(readerTwo));
  await shot("blank-reader-1");
  await click(".visual-return");
  await wait('document.body?.dataset.collectionId==="s-02" && location.hash==="#work-o-02"');
  await ev('document.querySelector(".publisher-circle-return").focus()');
  await key("Enter");
  await wait('location.pathname==='+JSON.stringify(ROUTE)+' && !document.body.dataset.collectionId');
  if(await ev('!!document.querySelector(".publisher-circle-return")'))throw Error("Root circle must be inert");
  console.log("SPATIAL_BOOKSHELF_BROWSER_PASS",label,JSON.stringify({root,one,two,readerOne,readerTwo,history:true,pointer:true,keyboard:true}));
 }finally{
  ws.close();
  await fetch(CDP+"/json/close/"+tab.id).catch(()=>{});
 }
}
for(const shape of [["ipad-portrait",820,1180],["ipad-landscape",1180,820],["phone-portrait",390,844]])await scenario(...shape);
