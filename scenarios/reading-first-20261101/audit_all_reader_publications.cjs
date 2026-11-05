#!/usr/bin/env node
// Editorial inventory/proofreading inputs from the actual source-bound v151
// static publication; no inferred live web claims.
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const root=__dirname,source=fs.readFileSync(root+'/stage-v151-before-archive.html','utf8');
(async()=>{
 const browser=await webkit.launch({headless:true});
 const ctx=await browser.newContext({viewport:{width:1440,height:900},ignoreHTTPSErrors:true});
 const page=await ctx.newPage();
 await page.goto('https://192.168.8.50:8243/estate/',{waitUntil:'domcontentloaded'});
 const inventory=await page.evaluate(()=>{
  const texts=[];
  for(const t of document.querySelectorAll('template[data-reader-volume]')){
   const id=t.dataset.readerVolume,root=t.content;
   const inner=root.querySelector('.book-flow');
   const chapters=[...root.querySelectorAll('.book-chapter')];
   const paras=[...root.querySelectorAll('article.book-prose > p')];
   const figures=[...root.querySelectorAll('article.book-prose figure,section.book-art-leaf figure')];
   const links=[...root.querySelectorAll('article.book-prose a[href]')].map(x=>({text:x.textContent.trim().slice(0,90),href:x.getAttribute('href')}));
   const proems=[...root.querySelectorAll('[data-editorial-role=proem]')].map(x=>x.textContent.trim());
   const abstracts=[...root.querySelectorAll('[data-editorial-role=abstract]')].map(x=>x.textContent.trim());
   const text=paras.map(x=>x.textContent.trim()).filter(Boolean).join('\n\n');
   texts.push({id,title:chapters[0]?.querySelector('h2')?.textContent.trim(),paragraphs:paras.length,chars:text.length,
      words:text.split(/\s+/).length,figures:figures.length,
      imageInfo:figures.map(f=>({src:f.querySelector('img')?.src,width:+f.querySelector('img')?.getAttribute('width'),height:+f.querySelector('img')?.getAttribute('height'),alt:f.querySelector('img')?.getAttribute('alt')??null,caption:f.querySelector('figcaption')?.textContent.trim()||''})),
      sourceBlocks:[...root.querySelectorAll('[data-source-block]')].map(x=>x.dataset.sourceBlock),
      proems,abstracts,links,text});
  }
  return texts;
 });
 fs.writeFileSync(root+'/fountain-press-all-publications-source-audit.json',
    JSON.stringify({schema:'fountain.press.all-publications-source-audit.v1',sourceRootSHA256:crypto.createHash('sha256').update(source).digest('hex'),works:inventory},null,2)+'\n');
 const summary=inventory.map(({id,title,paragraphs,chars,words,figures,proems,abstracts,links,imageInfo})=>({id,title,paragraphs,chars,words,figures,proems:proems.length,abstracts:abstracts.length,links:links.length,imageWithoutAlt:imageInfo.filter(x=>!x.alt).length}));
 console.log('VOLUMES',inventory.length,'TOTAL_WORDS',summary.reduce((s,x)=>s+x.words,0));
 summary.forEach(x=>console.log(JSON.stringify(x)));
 await ctx.close();await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
