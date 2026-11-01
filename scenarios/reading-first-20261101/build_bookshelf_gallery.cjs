const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('/opt/homebrew/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer');
const W=__dirname;
(async()=>{
const manifest=JSON.parse(fs.readFileSync(path.join(W,'essay-share-manifest.json'),'utf8'));
const first=JSON.parse(fs.readFileSync(path.join(W,'solstice-source-inventory.json'),'utf8'));
if(first.publishedWorks!==30||first.images!==41)throw Error('First Reading source changed');
const browser=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--no-sandbox']});
const page=await browser.newPage();
const parsed=await page.evaluate(({essays,solstice})=>{
 const a=new DOMParser().parseFromString(essays,'text/html');
 const b=new DOMParser().parseFromString(solstice,'text/html');
 const essayIds=[...a.querySelectorAll('template[data-reader-volume^="essay--"]')].map(x=>x.getAttribute('data-reader-volume')).reverse();
 const works=[...b.querySelectorAll('template[data-reader-volume^="solstice-reading-01--"]')]
    .filter(t=>/\d{4}-\d{2}-\d{2}/.test(t.getAttribute('data-reader-volume')));
 return {essayIds,works:works.map(t=>({id:t.getAttribute('data-reader-volume'),
   title:t.content.querySelector('h2')?.textContent.trim(),
   first:t.content.querySelector('figure.teatro-score img')?.getAttribute('src'),
   alt:t.content.querySelector('figure.teatro-score img')?.getAttribute('alt')||''
 }))};
},{essays:fs.readFileSync(path.join(W,'integrated-volumes.html'),'utf8'),solstice:fs.readFileSync(path.join(W,'solstice-volumes.html'),'utf8')});
await browser.close();
const essays=parsed.essayIds.map(id=>{
 const slug=id.slice('essay--'.length),entry=manifest.essays[slug];
 if(!entry?.art?.path||!entry.abstract)throw Error('Missing admitted essay art '+slug);
 const title=slug==='to-read-is-not-to-remember'?'Did the Machine Actually Read the Book?':
   undefined;
 return {id,src:entry.art.path,alt:entry.art.alt,sourceKind:entry.art.type};
});
if(essays.length!==7)throw Error('Essay gallery inventory');
const works=parsed.works.map(w=>{
 const item=first.inventory.find(x=>x.id===w.id);
 if(!item||item.kind!=='work'||!item.images||!w.first||w.title!==item.title)throw Error('Missing original reading art '+w.id);
 if(!w.first.startsWith('/solstice/assets/edition/'))throw Error('Not source-owned art '+w.first);
 return {id:w.id,src:w.first,alt:w.alt||item.title,sourceKind:'published-Teatro-Score'};
});
if(works.length!==30||new Set([...essays,...works].map(x=>x.id)).size!==37)throw Error('Duplicate/missing gallery subjects');
const data={schema:'fountain.press.bookshelf-gallery.v1',source:{essays:'original-essays-continuing.html / essay-share-manifest.json',
 firstReadings:'published solstice-first-reading-source.html / solstice-source-inventory.json'},
 order:'published manuscript order',collections:{essays, 'first-readings':works}};
fs.writeFileSync(path.join(W,'bookshelf-gallery.json'),JSON.stringify(data,null,2)+'\n');
console.log('SOURCE_BOUND_GALLERY',essays.length,works.length,'WORKS');
})().catch(e=>{console.error(e.stack);process.exitCode=1});
