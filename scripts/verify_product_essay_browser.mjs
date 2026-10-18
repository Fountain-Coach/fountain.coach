/* Local-only product essay acceptance: Chrome DevTools protocol, no npm deps.
   Start a Chrome session with remote debugging on port 9347 and serve site/
   at http://127.0.0.1:8207; no public publishing or network writes. */
import fs from "node:fs";
const host=process.env.CHROME_DEBUG_URL||"http://127.0.0.1:9347";
const origin=process.env.ESSAY_BASE_URL||"http://127.0.0.1:8207";
const proof=process.env.ESSAY_PROOF_DIR||"/tmp/composable-book-qa";
fs.mkdirSync(proof,{recursive:true});
const wait=ms=>new Promise(done=>setTimeout(done,ms));
async function inspect(name,width,height){
  const target=await(await fetch(host+"/json/new?about:blank",{method:"PUT"})).json();
  const ws=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((done,fail)=>{ws.addEventListener("open",done,{once:true});ws.addEventListener("error",fail,{once:true})});
  let seq=0;const pending=new Map();
  ws.addEventListener("message",event=>{
    const message=JSON.parse(event.data);
    if(pending.has(message.id)){pending.get(message.id)(message);pending.delete(message.id)}
  });
  const cmd=(method,params={})=>new Promise((resolve,reject)=>{
    const id=++seq;
    pending.set(id,response=>response.error?reject(new Error(JSON.stringify(response.error))):resolve(response));
    ws.send(JSON.stringify({id,method,params}));
  });
  const evalJS=async expression=>{
    const result=await cmd("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
    if(result.result.exceptionDetails)throw Error(JSON.stringify(result.result.exceptionDetails));
    return result.result.result.value;
  };
  try {
    await cmd("Runtime.enable");await cmd("Page.enable");
    await cmd("Emulation.setDeviceMetricsOverride",{width,height,deviceScaleFactor:1,mobile:width<550});
    await cmd("Page.navigate",{url:origin+"/product/the-composable-book/"});
    await wait(350);
    // Lazy illustrations below the fold must be explicitly decoded before fidelity assertions.
    await evalJS(`Promise.all([...document.querySelectorAll('.editorial-plate img')].map(async img => {img.loading='eager';try{await img.decode()}catch{};return img.naturalWidth}))`);
    const state=await evalJS(`(()=>{
      const figures=[...document.querySelectorAll(".editorial-plate img")];
      const ids=[...document.querySelectorAll("[id]")].map(el=>el.id);
      const anchors=[...document.querySelectorAll('a[href^="#"]')];
      const links=[...document.querySelectorAll("a[href]")];
      return {inner:innerWidth,doc:document.documentElement.scrollWidth,sections:document.querySelectorAll(".essay-article>h2").length,
        figures:figures.length,imagesLoaded:figures.every(x=>x.complete&&x.naturalWidth>0),heading:document.querySelectorAll('h1').length,
        localAnchorsValid:anchors.every(a=>document.getElementById(a.hash.slice(1))),
        missingImages:figures.filter(x=>!x.complete||!x.naturalWidth).map(x=>x.src),
        relLinks:links.filter(x=>x.getAttribute("href").startsWith("/")).map(x=>x.getAttribute("href")),
        idDuplicates:ids.length-new Set(ids).size,nav:document.querySelectorAll(".contents a").length,
        plateOverlapsContents:innerWidth>=1200 && document.querySelector('.editorial-plate').getBoundingClientRect().left<document.querySelector('.contents').getBoundingClientRect().right+8,
        lang:document.documentElement.lang,main:document.querySelectorAll("main").length};
    })()`);
    console.log("COMPOSABLE_BOOK_BROWSER",name,JSON.stringify(state));
    if(state.inner!==width||state.doc>width+1||state.sections!==8||state.figures!==4||!state.imagesLoaded||state.heading!==1||!state.localAnchorsValid||state.idDuplicates||state.plateOverlapsContents||state.nav!==9||state.lang!=="en"||state.main!==1)
      throw Error("Browser acceptance failed: "+name+" "+JSON.stringify(state));
    let shot=await cmd("Page.captureScreenshot",{format:"png",fromSurface:true,captureBeyondViewport:false});
    fs.writeFileSync(proof+"/"+name+".png",Buffer.from(shot.result.data,"base64"));
    if(name==="desktop") {
      await evalJS('document.querySelector("#plate-codex").scrollIntoView({block:"center"})');
      await wait(300);
      shot=await cmd("Page.captureScreenshot",{format:"png",fromSurface:true,captureBeyondViewport:false});
      fs.writeFileSync(proof+"/book-plate.png",Buffer.from(shot.result.data,"base64"));
    }
  } finally {
    ws.close();
    await fetch(host+"/json/close/"+target.id).catch(()=>{});
  }
}
for(const [name,w,h] of [["desktop",1440,980],["ipad-portrait",820,1180],["ipad-landscape",1180,820],["phone",390,844]]) await inspect(name,w,h);
console.log("COMPOSABLE_BOOK_BROWSER_ACCEPTED 4 viewports");
