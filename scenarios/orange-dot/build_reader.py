#!/usr/bin/env python3
"""Compose the curated original Facebook posts through the existing Fountain Press reader.

Input is source-locked local author Git + the exact immutable live stage v184
HTML/JS pair. Output is a deterministic stage-only delta, not a second Reader.
"""
from pathlib import Path
from hashlib import sha256
import html,json,re,subprocess,shutil

ROOT=Path(__file__).resolve().parent
BASE_HTML=Path('/tmp/orange-stage-index-v184.html')
BASE_JS=Path('/tmp/orange-first-app-v184.js')
OUT=Path('/tmp/orange-dot-stage-delta-20261110')
SRC=json.loads((ROOT/'selection.json').read_text())
FIRST=json.loads(Path('/Users/benedikteickhoff/Developer/fountain-publishing/fountain.coach/scenarios/reading-first-20261101/solstice-first-reading-manifest.json').read_text())
FIRST_IMAGES={a['sha256'].removeprefix('sha256:'):('/solstice'+a['href']) for entry in FIRST['entries'] for a in entry['images']}
entries=SRC['entries']
EDITORIAL_NOTES=json.loads((ROOT/'editorial-notes.json').read_text())
sourceRev=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
assert len(entries)==23
assert len({e['textSha256'] for e in entries})==23

def digest(b):return sha256(b).hexdigest()
def save(rel,data):
 path=OUT/rel
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_bytes(data if isinstance(data,bytes) else data.encode('utf-8'))
 return digest(path.read_bytes())
def esc(s):return html.escape(s,quote=True)
def replace_once(s,old,new,why):
 n=s.count(old)
 assert n==1,(why,n,old[:60])
 return s.replace(old,new)
def para_tags(raw,vol):
 parts=[part for part in re.split(r'\n{2,}',raw) if part.strip()]
 if not parts:parts=[raw]
 chunks=[]
 for n,part in enumerate(parts,1):
  # White-space adjustment belongs to the compositor, not a rewritten manuscript.
  val=part.strip()
  chunks.append(f'<p style="white-space:pre-line" data-source-block="{vol}.text.{n}" data-source-from="0" data-source-to="{len(val)}">{esc(val)}</p>')
 return ''.join(chunks)
def figure(e,im,first=False):
 role='opener' if first else 'plate'
 number=im['ordinal'];total=len(e['images'])
 caption=f'Original post image · {e["date"]}' if total==1 else f'Original post image · {number} of {total} · {e["date"]}'
 return (f'<figure class="frame-reading-figure teatro-score" data-teatro-score="source-owned" '
         f'data-source-block="{e["id"]}.{role}.image.{number}">'
         f'<img loading="eager" src="{esc(im["readerPath"])}" '
         f'alt="Original image {number} of {total} accompanying {esc(e["title"])}, {e["date"]}" '
         f'width="{im["width"]}" height="{im["height"]}"/>'
         f'<figcaption>{esc(caption)}</figcaption></figure>')
stage_entries=[]
templates=[]
assetPaths=[]
for e in entries:
 original=(ROOT/e['sourceTextFile']).read_bytes()
 assert digest(original)==e['textSha256'],e['id']
 raw=original.decode('utf-8')
 images=[]
 for im in e['images']:
  path=ROOT/'source-images'/im['sourceImageFile']
  b=path.read_bytes()
  assert digest(b)==im['sha256']
  if im['sha256'] in FIRST_IMAGES:
   readerPath=FIRST_IMAGES[im['sha256']]
   storage='existing-original-first-readings-asset'
  else:
   readerPath='/estate/assets/orange-dot/'+im['sourceImageFile']
   storage='original-export-image'
   assetPaths.append(readerPath.removeprefix('/'))
   save(readerPath.removeprefix('/'),b)
  images.append({**im,'readerPath':readerPath,'storage':storage})
 e={**e,'images':images}
 stage_entries.append({k:v for k,v in e.items() if k not in ['sourceTextFile','sourceIndex']})
 # The reader preserves every original authored paragraph and original source image.
 frame=EDITORIAL_NOTES[str(e['sourceIndex'])]
 intro=('<aside class="frame-editorial-proem" data-editorial-role="proem" '
        f'data-source-block="{e["id"]}.editorial" role="note" aria-label="Editorial context">'
        '<span class="frame-editorial-kicker">From the editor</span><p>'+esc(frame)+'</p></aside>') if frame else ''
 firstImage=figure(e,images[0],True) if images else ''
 restImages=''.join(figure(e,img) for img in images[1:])
 source=(f'<template data-reader-volume="{e["id"]}" data-source-owner="Benedikt Eickhoff" '
         f'data-source-sha256="{e["textSha256"]}" data-edition-membership="orange-dot">'
         f'<div class="book-flow" data-min-leaves="1">'
         f'<section class="book-chapter" id="work-{e["id"]}">'
         f'<div class="book-chapter-heading"><h2>{esc(e["title"])}</h2></div>'
         f'{firstImage}</section>'
         f'<section class="book-chapter-text">{intro}<article class="book-prose">'
         f'<p class="frame-edition-imprint" data-source-block="{e["id"]}.date">{e["date"]} · Original Facebook post</p>'
         f'{restImages}{para_tags(raw,e["id"])}'
         f'</article></section></div></template>')
 templates.append(source)
assert len(templates)==len(entries)
collectionIntro=(
 '<template data-reader-volume="orange-dot"><div class="book-flow" data-min-leaves="1">'
 '<section class="book-chapter" id="work-orange-dot"><div class="book-chapter-heading"><h2>Orange Dot</h2></div></section>'
 '<section class="book-chapter-text"><article class="book-prose">'
 '<p data-source-block="orange-dot.editorial.1">From Solstice, 21 December 2025, to September 2026: '
 'an authored selection of posts, complete original text and its accompanying original images. '
 'The orange mark begins as an ember and a bodily signal; its later encounters with care, '
 'distance, performance and the making of scores change how the mark can be read.</p>'
 '<p data-source-block="orange-dot.editorial.2">Two works already present in First Readings '
 'are intentionally revisited here, because their position in this sequence matters. '
 'Integration (23 December) remains in First Readings and is not republished a second time. '
 'The source words have not been rewritten.</p>'
 '</article></section></div></template>')
s=BASE_HTML.read_text()
s=replace_once(s,'<script type="application/json" id="reader-gallery-data">',
               collectionIntro+'\n'+'\n'.join(templates)+'\n<script type="application/json" id="reader-gallery-data">',
               'new source templates')
patt=r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)'
m=re.search(patt,s,re.S)
assert m
gallery=json.loads(m.group(2))
gallery['source']['orangeDot']={'owner':'Benedikt Eickhoff','sourceRevision':sourceRev,'sourceKind':'selected-original-Facebook-posts','stageOnly':True}
gallery['collections']['orange-dot']=[
 {'id':e['id'],'src':e['images'][0]['readerPath'],'alt':f'Original post image for {e["title"]}, {e["date"]}',
  'sourceKind':'source-owned-Facebook-original'} for e in stage_entries]
s=s[:m.start(2)]+json.dumps(gallery,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+s[m.end(2):]
# Keep a semantic edition place in the static source alongside the dynamic shelf.
old='<figcaption>Reading 01 — First Reading</figcaption></figure></div></article>'
new=('<figcaption>Reading 01 — First Reading</figcaption></figure>'
     '<figure class="frame-book-cover"><a href="#/read/orange-dot" data-reader-target="orange-dot" '
     'aria-label="Open Orange Dot inside this reader"><span class="frame-cover-mark" aria-hidden="true">●</span>'
     '<span class="frame-cover-name">Orange Dot</span></a>'
     '<figcaption>Solstice · original post sequence</figcaption></figure></div></article>')
s=replace_once(s,old,new,'semantic source shelf')
h_sha=save('estate/index.html',s)
j=BASE_JS.read_text()
patches=[
("['first-readings','First Readings']","['first-readings','First Readings'],['orange-dot','Orange Dot']",'labels'),
("key.startsWith('governance--')){","key.startsWith('governance--')||key.startsWith('orange-dot--')){",'recognized work identity'),
("key.startsWith('score--')?'Scores · '+label:'First Reading · '+label;",
 "key.startsWith('score--')?'Scores · '+label:key.startsWith('orange-dot--')?'Orange Dot · '+label:'First Reading · '+label;",'selector identity'),
("const solsticeSequence=[...templates.keys()].filter(x=>x.startsWith('solstice-reading-01--'));",
 "const solsticeSequence=[...templates.keys()].filter(x=>x.startsWith('solstice-reading-01--'));\nconst orangeSequence=[...templates.keys()].filter(x=>x.startsWith('orange-dot--'));\nif(orangeSequence.length!==23)throw Error('Orange Dot source inventory changed');",'exact collection size'),
("const contents={essays:[...essaySequence,proofVolume],scores:scoreSequence,'first-readings':solsticeSequence,governance:governanceSequence};",
 "const contents={essays:[...essaySequence,proofVolume],scores:scoreSequence,'first-readings':solsticeSequence,'orange-dot':orangeSequence,governance:governanceSequence};",'contents membership'),
("throw Error('Gallery no longer matches admitted source ordering');",
 "throw Error('Gallery no longer matches admitted source ordering');\nif(galleries['orange-dot']?.length!==orangeSequence.length ||\n galleries['orange-dot'].some((e,i)=>e.id!==orangeSequence[i]))\n throw Error('Orange Dot gallery/source drift');",'gallery parity'),
("const isContents=name=>name==='essays'||name==='scores'||name==='first-readings'||name==='governance';",
 "const isContents=name=>name==='essays'||name==='scores'||name==='first-readings'||name==='orange-dot'||name==='governance';",'collection surfaces'),
("if(solsticeSequence.includes(name))return 'first-readings';",
 "if(solsticeSequence.includes(name))return 'first-readings';\n if(orangeSequence.includes(name))return 'orange-dot';",'owning collection'),
("const sequence=[essaySequence,scoreSequence,solsticeSequence,governanceSequence].find(s=>s.includes(name));",
 "const sequence=[essaySequence,scoreSequence,solsticeSequence,orangeSequence,governanceSequence].find(s=>s.includes(name));",'adjacent work'),
("sequence===governanceSequence?'governance':'first-readings'",
 "sequence===governanceSequence?'governance':sequence===orangeSequence?'orange-dot':'first-readings'",'adjacent parent'),
("const surfaceOffsets={shelf:0,essays:0,scores:0,'first-readings':0,governance:0};",
 "const surfaceOffsets={shelf:0,essays:0,scores:0,'first-readings':0,'orange-dot':0,governance:0};",'scroll offset'),
("const galleryOffsets={essays:0,scores:0,'first-readings':0,governance:0};",
 "const galleryOffsets={essays:0,scores:0,'first-readings':0,'orange-dot':0,governance:0};",'gallery offset'),
("const shelfContentsOffsets={essays:0,scores:0,'first-readings':0,governance:0};",
 "const shelfContentsOffsets={essays:0,scores:0,'first-readings':0,'orange-dot':0,governance:0};",'contents scroll'),
("const collectionOrder=['essays','scores','first-readings','governance'];",
 "const collectionOrder=['essays','scores','first-readings','orange-dot','governance'];",'horizontal shelf'),
("const selectedWork={essays:null,scores:null,'first-readings':null,governance:null};",
 "const selectedWork={essays:null,scores:null,'first-readings':null,'orange-dot':null,governance:null};",'selected identity'),
("const compactPresentation={essays:'contents',scores:'contents','first-readings':'contents',governance:'contents'};",
 "const compactPresentation={essays:'contents',scores:'contents','first-readings':'contents','orange-dot':'contents',governance:'contents'};",'responsive presentation'),
("if(pathname.includes('/collections/first-readings/'))return 'first-readings';",
 "if(pathname.includes('/collections/first-readings/'))return 'first-readings';\n if(pathname.includes('/collections/orange-dot/'))return 'orange-dot';",'direct route'),
("id==='governance'?'Complete published edition · 160 chapters':'Reading 01 · First Reading';",
 "id==='governance'?'Complete published edition · 160 chapters':id==='orange-dot'?'Solstice · original post sequence':'Reading 01 · First Reading';",'bookshelf subtitle')
]
for old,new,why in patches:j=replace_once(j,old,new,why)
js_sha=save('estate/assets/linotype/reading-first-app.js',j)
stage_manifest={
 'schema':'fountain.press.orange-dot.stage-edition.v1',
 'editionID':'orange-dot','title':'Orange Dot','subtitle':'From Solstice · An Orange Signal',
 'stageOnly':True,'publicReleaseAuthorized':False,'compositor':'Fountain Press original Linotype',
 'sourceOwner':'Benedikt Eickhoff','sourceGitRevision':sourceRev,'sourceArchivePeriod':['2025-12-21','2026-09-19'],
 'entryCount':len(stage_entries),'sourceTextPolicy':'complete lexical original; paragraph layout only',
 'overlapPolicy':'Integration referenced only; I Keep Moving and A Score Before Production deliberately reappearing from First Readings',
 'sourceSelectionSHA256':digest((ROOT/'selection.json').read_bytes()),
 'entries':[{**{k:v for k,v in e.items() if k!='images'},'images':[
            {k:v for k,v in im.items() if k in ('readerPath','width','height','sha256','ordinal','storage')} for im in e['images']]}
           for e in stage_entries]
}
manifest_sha=save('estate/collections/orange-dot/edition.json',json.dumps(stage_manifest,ensure_ascii=False,indent=2)+'\n')
redirect=('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">'
 '<meta http-equiv="refresh" content="0;url=/estate/#/read/orange-dot"><title>Orange Dot · Fountain Press</title>'
 '</head><body><p><a href="/estate/#/read/orange-dot">Read Orange Dot in Fountain Press</a></p></body></html>')
redirect_sha=save('estate/collections/orange-dot/index.html',redirect)
# Source-first meaningful acceptance, without treating HTTP 200 as sufficient.
assert s.count('data-edition-membership="orange-dot"')==len(stage_entries)
assert j.count("const orangeSequence=")==1
assert len({p for e in stage_entries for p in [e['id']]})==23
changed={
 'estate/index.html':h_sha,
 'estate/assets/linotype/reading-first-app.js':js_sha,
 'estate/collections/orange-dot/index.html':redirect_sha,
 'estate/collections/orange-dot/edition.json':manifest_sha,
}
for rel in assetPaths:changed[rel]=digest((OUT/rel).read_bytes())
receipt={'schema':'fountain.press.orange-dot.verified-delta.v1',
 'predecessorRelease':'shared-shell-20261110-v184-playable-breach-b9d4c88',
 'predecessorIndexSHA256':digest(BASE_HTML.read_bytes()),
 'predecessorReaderJSSHA256':digest(BASE_JS.read_bytes()),
 'sourceRevision':sourceRev,'selectedCount':len(stage_entries),
 'originalImageCount':sum(len(e['images']) for e in stage_entries),
 'reusedFirstReadingsOriginalImageCount':29-len(assetPaths),
 'sourceTextSHA256':{e['id']:e['textSha256'] for e in stage_entries},
 'changedAndAddedFiles':changed,'stagingOnly':True,'publicReleaseAuthorized':False}
save('orange-dot-delta-receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print('ORANGE_DOT_PRESS_DELTA_CREATED',len(entries),'entries',len(assetPaths),'new original image files',
 len(changed),'stage paths','sourceRevision',sourceRev[:12],
 'index_sha',h_sha[:16],'app_sha',js_sha[:16])
