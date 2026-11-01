const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const fs=require('fs'),path=require('path');
const axe=process.env.FOUNTAIN_AXE_SCRIPT || require.resolve('axe-core/axe.min.js',{paths:[path.join(process.env.HOME,'Developer/fcis.fountain.coach')]});
const samples=[['library','Bookshelf'],['essays','Essays contents'],['first-readings','First Readings contents'],
['essay--the-door-is-a-score','Illustrated essay'],['solstice-reading-01--2025-12-22-anweisung-an-den-schmerz','Teatro Score']];
(async()=>{
 const browser=await webkit.launch({headless:true});
 const findings=[];
 for(const [profile,width,height,theme] of [['landscape-light',1180,820,'light'],['landscape-dark',1180,820,'dark'],['phone-dark',390,844,'dark']]){
  const ctx=await browser.newContext({viewport:{width,height},colorScheme:theme});
  const page=await ctx.newPage();
  for(const [id,label] of samples){
   await page.goto('https://192.168.8.50:8243/estate/#/read/'+id,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:20000});
   await page.addScriptTag({path:axe});
   const result=await page.evaluate(async()=>axe.run(document,{
      runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']},
      resultTypes:['violations']
   }));
   const violations=result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length,
     examples:v.nodes.slice(0,2).map(n=>({target:n.target.join(' '),summary:n.failureSummary?.slice(0,140)}))}));
   findings.push({profile,id,label,violations,incomplete:result.incomplete?.length||0});
   console.log(profile,label,JSON.stringify(violations));
  }
  await ctx.close();
 }
 await browser.close();
 const severe=findings.filter(x=>x.violations.some(v=>['critical','serious'].includes(v.impact)));
 fs.writeFileSync(path.join(__dirname,'reader-axe-live-v95.json'),JSON.stringify({engine:'WebKit',scanner:'axe-core 4.13.0',physicaliPad:false,tests:findings,
     seriousOrCritical:severe.length},null,2)+'\n');
 console.log('SUMMARY',JSON.stringify({scans:findings.length,severe:severe.length}));
 if(severe.length)process.exitCode=2;
})().catch(e=>{console.error('FAIL',e.stack);process.exitCode=2});
