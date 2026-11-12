import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const require=createRequire(import.meta.url);
const {webkit}=require('/Users/benedikteickhoff/Developer/fcis.fountain.coach/node_modules/playwright');
const base=process.env.FCIS_PARITY_BASE||'http://127.0.0.1:8863';
const local='/Users/benedikteickhoff/Developer/.fcis-value-essay-20261112/build/publication-v199';
const receipt=JSON.parse(fs.readFileSync(path.join(local,'fcis-value-legacy-reader-parity.json'),'utf8'));
const previous='/Users/benedikteickhoff/Developer/.fcis-value-essay-20261112/build/publication-v198/public-release-fcis-value-20261112';
const candidate=path.join(local,'public-release-fcis-value-nav');
const assert=(x,msg)=>{if(!x)throw Error(msg)};
const browser=await webkit.launch({headless:true});
try{
  const changes=Object.keys(receipt.modifiedPaths);
  assert(changes.length===14&&changes.includes("release-manifest.json"),"Expected thirteen entrances and one release manifest");
  const changed=changes.filter(x=>x.endsWith("/index.html"));
  assert(changed.length===13,"Expected exactly thirteen legacy Reader entrances");
  const staticOriginal=(s)=>[...s.matchAll(/<(?:meta|link)\s+[^>]*(?:og:|twitter:|rel="canonical")[^>]*>/g)].map(x=>x[0]).sort();
  for(const rel of changed){
    const old=fs.readFileSync(path.join(previous,rel),'utf8');
    const newer=fs.readFileSync(path.join(candidate,rel),'utf8');
    assert(JSON.stringify(staticOriginal(old))===JSON.stringify(staticOriginal(newer)),'Existing work share/canonical meta altered: '+rel);
    assert((newer.match(/<template data-reader-volume=/g)||[]).length===76,'Incomplete new Reader templates: '+rel);
    assert(newer.includes('reading-first-app.233205de4f9ce94289086bb23e31b0df45009818438bc0eff03a4e2688299c68.js'),'Missing unified Reader: '+rel);
    assert(!newer.includes('reading-first-app.1b574fe1d24004a7c4d25ecc5df31cb098ac0784f4a87158ac5208d7cda06dd7.js'),'Stale Reader: '+rel);
  }
  for(const viewport of [{name:'ipad-portrait',width:820,height:1180},{name:'ipad-landscape',width:1180,height:820},{name:'phone',width:390,height:844}]){
   const c=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},isMobile:true,hasTouch:true});
   let verified=0;
   for(const rel of changed){
    const page=await c.newPage(),errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    const url=base+'/'+rel.replace(/index\.html$/,'');
    const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
    assert(response.status()===200,'Entry route unavailable '+rel);
    await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.layout==='ready',{timeout:40000});
    const before=await page.evaluate(()=>({volume:document.getElementById('page-viewport')?.dataset.volume,pages:Number(document.getElementById('page-viewport')?.dataset.pages)}));
    if(rel.includes('/essay--'))assert(before.pages>=1,'No measured essay leaves '+rel);
    if(rel.includes('/essay--')){
      const parentCount=await page.locator('[data-reader-target="essays"]').count();
      if(parentCount){
        await page.locator('[data-reader-target="essays"]').first().click();
        await page.waitForFunction(()=>document.querySelector('#page-viewport')?.dataset.volume==='essays',{timeout:5000});
        const labels=await page.locator('#page-viewport .reader-contents-entry').allTextContents();
        assert(labels.length===8&&labels[0].includes('The Value of What We Can Prove'),'New essay missing after direct navigation '+rel);
      }else{
        assert(rel.includes('semantic-compilation')||rel.includes('composable-book'),'Active Essay lost its parent navigation '+rel);
      }
    }
    if(!rel.includes('/essay--')&&before.volume==='library'){
      const links=await page.locator('.reader-book-direct-link').count();
      assert(links===3,'Legacy Bookshelf direct-link count changed '+rel);
    }
    assert(!errors.length,'Reader runtime errors '+rel+JSON.stringify(errors));
    verified++;await page.close();
   }
   console.log('LEGACY_READER_PARITY_WEBKIT_PASS',viewport.name,verified,'routes, direct-source continuity, eight Essays');
   await c.close();
  }
  console.log('LEGACY_READER_SEMANTIC_NAV_ACCEPTED',changed.length,'routes and all three viewports');
}catch(e){console.error('LEGACY_READER_PARITY_FAILED',e.stack||e);process.exitCode=1}
finally{await browser.close()}
