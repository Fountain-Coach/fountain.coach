#!/usr/bin/env node
/* Source-owned regression: the pictured negative specimen breaches only its internal frame. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {webkit,chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const svg=path.join(root,'site/essays/before-we-can-work-together/figures/03-measured-correction.svg');
const available={webkit,chromium};
const browsers=(process.env.FIGURE_BROWSERS||'webkit').split(',').map(k=>[k,available[k]]);
for (const [name,provider] of browsers) {
  if(!provider)throw Error('Unknown browser: '+name);
  const browser=await provider.launch({headless:true,...(name==='chromium'&&process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
  try {
    const page=await browser.newPage({viewport:{width:1024,height:768},deviceScaleFactor:2});
    await page.goto('file://'+svg,{waitUntil:'load'});
    await page.evaluate(()=>document.fonts.ready);
    const result=await page.evaluate(()=>{
      const svg=document.querySelector('svg');
      const rects=[...svg.querySelectorAll('rect')].map(r=>({x:+r.getAttribute('x'),right:+r.getAttribute('x')+(+r.getAttribute('width')),top:+r.getAttribute('y'),bottom:+r.getAttribute('y')+(+r.getAttribute('height'))}));
      const texts=[...svg.querySelectorAll('text')].map(t=>{const b=t.getBBox();return {text:t.textContent,x:b.x,right:b.x+b.width,top:b.y,bottom:b.y+b.height,originX:+t.getAttribute('x'),y:+t.getAttribute('y')}})
      return {viewBox:svg.getAttribute('viewBox'),rects,texts};
    });
    const [before,after]=result.rects;
    const failed=result.texts.find(t=>t.text==='container in which words happen to');
    const negative=result.texts.filter(t=>t.originX===57);
    const positive=result.texts.filter(t=>t.originX===552);
    if(!failed||negative.length!==3||positive.length!==3) throw Error(name+' semantic lineation');
    const overflow=failed.right-before.right;
    if(!(overflow>=0.25&&overflow<6))throw Error(name+' failed specimen overflow '+overflow);
    for(const t of [...negative,...positive]){
      const box=t.originX===57?before:after;
      if(!(t.x>box.x+5 && t.top>box.top+5 && t.bottom<box.bottom-5))throw Error(name+' text outside panel '+t.text);
      if(t.originX===552 && t.right>box.right-14)throw Error(name+' positive overfull '+t.text);
      if(t.originX===57 && t.right>before.right+6)throw Error(name+' negative too far '+t.text);
    }
    if(result.texts.some(t=>t.right>930||t.x<30||t.top<0||t.bottom>405)) throw Error(name+' outer plate overflow');
    const png=process.env.PROOF_DIR?path.join(process.env.PROOF_DIR,'figure-iii-'+name+'.png'):null;
    if(png){fs.mkdirSync(path.dirname(png),{recursive:true});await page.screenshot({path:png,animations:'disabled'});}
    console.log(JSON.stringify({browser:name,state:'PASS',negativeInkOverrun:overflow,negativeLines:negative.map(x=>x.text),positiveLines:positive.map(x=>x.text),png}));
  } finally {await browser.close();}
}
