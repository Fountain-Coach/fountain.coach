#!/usr/bin/env python3
"""Build exact-source illustrated Fountain Press essay overlay against v197 owner-WLAN baseline.

No new Reader, paginator, shell, server or publishing authority. This script only
composes files off-host. Stage activation remains EstatePublisher's responsibility.
"""
from __future__ import annotations
import hashlib, html, json, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "the-model-is-not-the-instrument"
VOLUME = "essay--" + SLUG
TITLE = "The Model Is Not the Instrument"
WORK = ROOT / "site/essays" / SLUG
SOURCE = WORK / (SLUG + ".md")
ART = WORK / "assets"
FIX = ROOT / "fixtures/stage-current"
OUT = ROOT / "build/model-instrument-stage/overlay"
STAGE_ORIGIN = "https://192.168.8.50:8243"
STAGE_ROUTE = "/estate/read/" + VOLUME + "/"
SOCIAL = "the-model-is-not-the-instrument-social.jpg"
FIGURES = [
 dict(id="model-instrument.hero", path="01-the-instrument-and-its-place.svg",
      role="hero", after="model-instrument.title",
      alt="Teatro Score: a separate manuscript source, executable Ubuntu instrument, AI request and composed reading surface."),
 dict(id="model-instrument.claim", path="02-the-claim-and-the-browser.svg",
      role="inline", after="model-instrument.intro.p2",
      alt="Teatro Score: a declared publication faces an empty address with a visible 404, marking the distance between claim and observed result."),
 dict(id="model-instrument.score", path="03-a-score-becomes-sound.svg",
      role="inline", after="model-instrument.s1.p2",
      alt="Teatro Score: written musical relations pass through an independent sound engine before becoming audible."),
 dict(id="model-instrument.workshop", path="04-three-machines-one-work.svg",
      role="inline", after="model-instrument.s2.p2",
      alt="Teatro Score: a writer's Mac, persistent Ubuntu host, reading tablet and selected mobile image contribute distinct resources."),
]
BASE_HASHES = {
 "estate-index.html": "f7cedae9efaba21f9d6798fac91932e704e02963f153ab1854f9902d4ee443ae",
 "books-essays.html": "262d6fbf0263ebd923c693cc2f05b8586d1b129756510740e223d615d6893952",
 "read-essays.html": "ba10952f9ebdaf863626738f27fcd8af9df3e5a5d91c00c14ca85ffd5cf2ed7f",
 "reader-app-live.js": "233205de4f9ce94289086bb23e31b0df45009818438bc0eff03a4e2688299c68",
}
APP_NAME = "reading-first-app.233205de4f9ce94289086bb23e31b0df45009818438bc0eff03a4e2688299c68.js"
STAGE_APP = "reading-first-app.model-instrument-review-20261113.js"

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def file_sha(path):return sha(path.read_bytes())
def require(condition,message):
 if not condition:raise RuntimeError(message)
def inline(text):
 parts=html.escape(text).split("*")
 return "".join("<em>"+part+"</em>" if i%2 else part for i,part in enumerate(parts))
def write(rel, data):
 p=OUT/rel
 p.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,bytes):p.write_bytes(data)
 else:p.write_text(data,encoding="utf-8")
 return p

def source_blocks():
 raw=SOURCE.read_text("utf-8")
 assert raw.startswith("# "+TITLE+"\n\n*")
 chunks=raw.strip().split("\n\n## ")
 intro=chunks[0].split("\n\n")
 lead=intro[1].strip("*")
 sections=[]
 allparas=[("intro",None,intro[2:])]
 for i,chunk in enumerate(chunks[1:],1):
  heading,body=chunk.split("\n\n",1)
  ps=body.strip().split("\n\n")
  sections.append((f"s{i}",heading,ps))
  allparas.append((f"s{i}",heading,ps))
 return raw,lead,sections,allparas

def new_template(lead,groups):
 figures={f["after"]:f for f in FIGURES[1:]}
 blocks=[]
 ordered=[]
 para_index=0
 def p(addr,text,klass="",extra=""):
  nonlocal para_index
  para_index+=1
  attr=(' class="'+klass+'"') if klass else ''
  ordered.append(f'<p{attr} data-source-block="{addr}" data-source-from="0" data-source-to="{len(text)}" {extra}>{inline(text)}</p>')
  blocks.append(dict(id=addr,kind="heading" if klass=="frame-subheading" else "paragraph",text=text))
  if addr in figures:
   f=figures[addr]
   figid=f["id"];path=f["path"]
   ordered.append(f'<figure class="frame-reading-figure" data-source-block="{figid}" data-source-illustration-id="{figid}" data-source-plate-sha256="{file_sha(ART/path)}" data-inline-after-paragraph="{para_index}" data-editorial-role="inline"><img loading="lazy" decoding="async" src="{STAGE_ROUTE}assets/{path}" width="1500" height="980" alt="{html.escape(f["alt"],quote=True)}"/></figure>')
 p("model-instrument.lead",lead,"frame-lead", 'data-editorial-role="proem"')
 for section_id,head,paras in groups:
  if head is not None:p(f"model-instrument.{section_id}.heading",head,"frame-subheading")
  for n,paragraph in enumerate(paras,1):
   require("\n" not in paragraph,"Unexpected hard break in manuscript")
   p(f"model-instrument.{section_id}.p{n}",paragraph)
 require(all(f["after"] in {b["id"] for b in blocks} for f in FIGURES[1:]),"Figure anchor missing")
 f=FIGURES[0]
 hero=f'<section class="book-art-leaf"><figure class="frame-reading-figure frame-essay-hero" data-source-block="{f["id"]}" data-source-illustration-id="{f["id"]}" data-source-plate-sha256="{file_sha(ART/f["path"])}" data-editorial-role="hero"><img loading="eager" decoding="sync" src="{STAGE_ROUTE}assets/{f["path"]}" width="1500" height="980" alt="{html.escape(f["alt"],quote=True)}"/></figure></section>'
 title=f'<section class="book-chapter" id="work-{SLUG}"><div class="book-chapter-heading"><h2 data-source-block="model-instrument.title">{TITLE}</h2></div></section>'
 body='<section class="book-chapter-text"><article class="book-prose">'+''.join(ordered)+'</article></section>'
 template=f'<template data-reader-volume="{VOLUME}"><div class="book-flow" data-min-leaves="1">{title}{hero}{body}</div></template>'
 return template,blocks

def update_gallery(source):
 match=re.search(r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',source,re.S)
 require(bool(match),"Original publication gallery not found")
 gallery=json.loads(match.group(1))
 original=gallery["collections"]["essays"]
 require(len(original)==8 and original[0]["id"]=="essay--the-value-of-what-we-can-prove","Unexpected stage gallery predecessor")
 f=FIGURES[0]
 original.insert(0,dict(id=VOLUME,src=STAGE_ROUTE+"assets/"+f["path"],alt=f["alt"],sourceKind="source-authored-Teatro-Score",sourceSHA256=file_sha(ART/f["path"])))
 replacement='<script type="application/json" id="reader-gallery-data">'+json.dumps(gallery,ensure_ascii=False,separators=(",",":"))+'</script>'
 return source[:match.start()]+replacement+source[match.end():]

def insert_essay(source,template):
 anchor='<script type="application/json" id="reader-gallery-data">'
 require(source.count(anchor)==1 and VOLUME not in source,"Unexpected original essay/template state")
 text=source.replace(anchor," "+template+"\n"+anchor,1)
 text=update_gallery(text)
 require(text.count('data-reader-volume="'+VOLUME+'"')==1,"Missing newly authored template")
 require('data-initial-volume="library"' in text or 'data-initial-volume="essays"' in text,"Reader initial volume unknown")
 require(APP_NAME in text,"Pinned actual Reader script identity absent")
 return text.replace(APP_NAME,STAGE_APP)

def direct_meta(source,lead,hero_sha,share_sha):
 source=source.replace('data-initial-volume="library"',f'data-initial-volume="{VOLUME}"',1)
 source=source.replace('data-initial-volume="essays"',f'data-initial-volume="{VOLUME}"',1)
 head,body=source.split('</head>',1)
 head=re.sub(r'<title>[^<]*</title>',f'<title>{TITLE} — Fountain Press (private review)</title>',head,count=1)
 head=re.sub(r'<meta property="og:[^>]*>',"",head)
 head=re.sub(r'<meta name="twitter:[^>]*>',"",head)
 head=re.sub(r'<link rel="canonical"[^>]*>',"",head)
 head=re.sub(r'<meta name="description"[^>]*>',"",head)
 head=head.replace('<meta name="robots" content="index,follow"/>','<meta name="robots" content="noindex,nofollow"/>')
 desc="A language model may describe an action. The instrument must actually perform it."
 tags=f"""<meta name="description" content="{html.escape(desc,quote=True)}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{TITLE}"/>
<meta property="og:description" content="{html.escape(desc,quote=True)}"/>
<meta property="og:url" content="{STAGE_ORIGIN}{STAGE_ROUTE}"/>
<meta property="og:image" content="{STAGE_ORIGIN}/estate/assets/social/essays/{SOCIAL}"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:image:alt" content="{html.escape(FIGURES[0]['alt'],quote=True)}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{TITLE}"/>
<meta name="twitter:image" content="{STAGE_ORIGIN}/estate/assets/social/essays/{SOCIAL}"/>
<meta name="fountain:publication-state" content="private-owner-WLAN-editorial-review"/>
<meta name="fountain:hero-source-sha256" content="{hero_sha}"/>
<meta name="fountain:social-sha256" content="{share_sha}"/>"""
 head=head.replace('</title>',"</title>\n"+tags,1)
 return head+'</head>'+body

def books_metadata(source,hero_sha,share_sha):
 head,body=source.split('</head>',1)
 head=head.replace('<meta name="robots" content="index,follow"/>','<meta name="robots" content="noindex,nofollow"/>')
 head=re.sub(r'(<meta property="og:image:alt" content=")[^"]+("[^>]*>)',lambda m:m.group(1)+html.escape(FIGURES[0]["alt"],quote=True)+m.group(2),head,count=1)
 head=head.replace('</head>','')
 # In a private stage the initial, no-JS book share metadata must refer to
 # the very same new source-derived hero bytes served on this stage, never
 # to the still-public predecessor book image.
 head=head.replace("https://fountain.coach/estate/assets/social/books/essays-first-chapter.jpg",STAGE_ORIGIN+"/estate/assets/social/books/essays-first-chapter.jpg")
 head=head.replace("https://fountain.coach/estate/books/essays/",STAGE_ORIGIN+"/estate/books/essays/")
 head=head.replace('</title>',f'</title><meta name="fountain:publication-state" content="private-owner-WLAN-editorial-review"/><meta name="fountain:hero-source-sha256" content="{hero_sha}"/><meta name="fountain:social-sha256" content="{share_sha}"/>',1)
 return head+'</head>'+body

def build():
 for k,h in BASE_HASHES.items():require(file_sha(FIX/k)==h,f"Accepted v197 predecessor drift: {k}")
 raw,lead,sections,groups=source_blocks()
 template,blocks=new_template(lead,groups)
 source_sha=sha(raw.encode())
 release_rev=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
 hero_sha=file_sha(ART/FIGURES[0]["path"])
 share=ART/SOCIAL
 require(share.exists(),"Hero-social raster derivative missing")
 share_sha=file_sha(share)
 require(len(release_rev)==40,"Unpinned author source")
 if OUT.exists():shutil.rmtree(OUT)
 # The one live runtime is reused; stage-local app only adjusts strict counters.
 app=(FIX/"reader-app-live.js").read_text("utf-8")
 require("if(essaySequence.length!==7||" in app and "galleries.essays.length!==8||" in app,"Unknown live Reader inventory")
 app=app.replace("if(essaySequence.length!==7||","if(essaySequence.length!==8||",1).replace("galleries.essays.length!==8||","galleries.essays.length!==9||",1)
 write("estate/assets/linotype/"+STAGE_APP,app)
 routes={
  "estate/index.html":"estate-index.html",
  "estate/read/essays/index.html":"read-essays.html",
  "estate/books/essays/index.html":"books-essays.html",
  f"estate/read/{VOLUME}/index.html":"estate-index.html"
 }
 for dest,src in routes.items():
  base=(FIX/src).read_text("utf-8")
  updated=insert_essay(base,template)
  if dest==f"estate/read/{VOLUME}/index.html":updated=direct_meta(updated,lead,hero_sha,share_sha)
  if dest=="estate/books/essays/index.html":updated=books_metadata(updated,hero_sha,share_sha)
  write(dest,updated)
 for f in FIGURES:
  write(f"estate/read/{VOLUME}/assets/{f['path']}",(ART/f["path"]).read_bytes())
 write(f"estate/assets/social/essays/{SOCIAL}",share.read_bytes())
 write("estate/assets/social/books/essays-first-chapter.jpg",share.read_bytes())
 catalog=json.loads((FIX/"books-catalog.json").read_text("utf-8"))
 e=next(b for b in catalog["books"] if b["id"]=="essays")
 require(e["firstIllustratedChapterID"]=="essay--the-value-of-what-we-can-prove","Book source order unexpectedly changed")
 e.update(firstIllustratedChapterID=VOLUME,firstChapterOriginalImagePath=STAGE_ROUTE+"assets/"+FIGURES[0]["path"],firstChapterOriginalImageSHA256=hero_sha,sourceIllustrationDeclaredSHA256=hero_sha,firstChapterImageAlt=FIGURES[0]["alt"],sourceIllustrationProvenance="source-authored-Teatro-Score",
          socialImageSHA256=share_sha,sourceRevision=release_rev,stageOnly=True,publicationState="private-owner-WLAN-editorial-review",publicReleaseAuthorized=False,
          rightsProvenance="Writer-approved illustrated staging review, not public promotion")
 catalog["stageOnly"]=True
 catalog["status"]="private-owner-WLAN-editorial-review"
 catalog["publicReleaseAuthorized"]=False
 catalog["privateEssayCandidate"]=dict(id=VOLUME,sourceSHA256=source_sha,heroSHA256=hero_sha,shareSHA256=share_sha,sourceRevision=release_rev)
 write("estate/books/catalog.json",json.dumps(catalog,ensure_ascii=False,indent=2)+"\n")
 figure_rows=[dict(**f,sha256=file_sha(ART/f["path"]),stagingURL=STAGE_ROUTE+"assets/"+f["path"]) for f in FIGURES]
 manifest=dict(schema="fountain.press.source-bound-illustrated-essay.v1",title=TITLE,sourceOwner="Fountain-Coach/fountain.coach",sourcePath=str(SOURCE.relative_to(ROOT)),sourceRevision=release_rev,sourceSHA256=source_sha,
               stageURL=STAGE_ORIGIN+STAGE_ROUTE,publicationState="private-owner-WLAN-editorial-review",productionAuthorized=False,proem=lead,
               sections=[dict(id=s,title=h,paragraphCount=len(p)) for s,h,p in sections],
               blocks=blocks,figures=figure_rows,heroFigureID=FIGURES[0]["id"],heroSourceSHA256=hero_sha,shareURL=STAGE_ORIGIN+"/estate/assets/social/essays/"+SOCIAL,
               shareImageSHA256=share_sha,shareImageDimensions=[1200,630],
               predecessor=dict(stageRelease="shared-shell-20261112-v197-fcis-value-illustrated-ba6a653",sourceHashes=BASE_HASHES),
               renderer="existing measured Linotype Reader; original Press engine unchanged",stagingAdapter="strict essay/gallery inventory extended to new author-approved essay only")
 write(f"estate/read/{VOLUME}/edition-manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
 digest_map={str(p.relative_to(OUT)):file_sha(p) for p in sorted(OUT.rglob("*")) if p.is_file()}
 write("estate/evidence/the-model-is-not-the-instrument-stage-inventory.json",json.dumps(dict(sourceSHA256=source_sha,sourceRevision=release_rev,files=digest_map,stageOnly=True),indent=2)+"\n")
 # Static source and asset assertions. Browser and live Publisher verification are separate.
 require(all((OUT/("estate/read/"+VOLUME+"/assets/"+f["path"])).exists() for f in FIGURES),"Figure inventory incomplete")
 require(OUT.joinpath("estate/assets/social/essays/"+SOCIAL).read_bytes()==OUT.joinpath("estate/assets/social/books/essays-first-chapter.jpg").read_bytes(),"Book/share art mismatch")
 for k in routes:
  t=(OUT/k).read_text()
  require(t.count(f'data-reader-volume="{VOLUME}"')==1 and t.count(FIGURES[0]["id"])>=1,f"Source template mismatch: {k}")
 require((OUT/f"estate/read/{VOLUME}/index.html").read_text().count('property="og:image"')==1,"Crawler OG metadata absent")
 print(json.dumps(dict(status="candidate-built",sourceRevision=release_rev,sourceSHA256=source_sha,paragraphCount=sum(len(p) for _,_,p in groups),figures=len(FIGURES),files=len(digest_map),shareImageSHA256=share_sha,stage=STAGE_ORIGIN+STAGE_ROUTE),indent=2))
if __name__=="__main__":build()
