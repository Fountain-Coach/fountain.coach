#!/usr/bin/env python3
"""Compose If Only in the existing Fountain Press Reader, stage-only."""
from pathlib import Path
import hashlib,html,json,re,shutil,subprocess

R=Path(__file__).resolve().parents[1]
SRC=R/"site/essays/if-only/if-only.md"
ART=SRC.parent/"hero-simultanbuehne.webp"
SOC=SRC.parent/"if-only-social.jpg"
BASE=R/"build/if-only-v202/baseline"
OUT=R/"build/if-only-v202/overlay"
HOST="https://192.168.8.50:8243"
OLD="essay--the-model-is-not-the-instrument"
ID="essay--if-only"
PATH="/estate/read/"+ID+"/"
FIG=PATH+"assets/hero-simultanbuehne.webp"
ALT="A sparse axonometric simultaneous stage: an empty central frame, a small terracotta mark on a left plinth, and a tablet on the floor to the right."
PREDECESSOR="shared-shell-20261113-v201-teatro-semantic-5ea3380"
LOCK="7fa67597090b6a3e0b46b49df79dd35eac5f34e3116cbaf1ba126ec22133c856"
PNG_ORIGINAL="f2ec1d79c05f16466c39b0e45c1f7a32cc0332b49c1664dbfadeb4b2c487c481"
ROUTES=["estate/index.html","estate/books/essays/index.html","estate/read/essays/index.html"]
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(p.read_bytes())
def req(test,msg):
 if not test:raise RuntimeError(msg)
def write(rel,data):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(data if isinstance(data,bytes) else data.encode("utf-8"))
 return p
def inline(s):
 mark=chr(96)
 parts=re.split(r"(\*[^*]+\*|"+re.escape(mark)+r"[^"+re.escape(mark)+r"]+"+re.escape(mark)+")",s)
 return "".join(
   "<em>"+html.escape(t[1:-1])+"</em>" if t.startswith("*") and t.endswith("*") else
   "<code>"+html.escape(t[1:-1])+"</code>" if t.startswith(mark) and t.endswith(mark) else html.escape(t)
   for t in parts)
def source():
 raw=SRC.read_text();chunks=raw.strip().split("\n\n")
 req(chunks[0]=="# If Only" and all(c.startswith("*") and c.endswith("*") for c in chunks[1:3]),"Source structure changed")
 subtitle,proem=chunks[1][1:-1],chunks[2][1:-1]
 blocks=[];sections=[];sid="intro";n=0
 for text in chunks[3:]:
  req("\n" not in text,"Unadmitted hard line break")
  if text.startswith("## "):
   sid="s"+str(len(sections)+1);n=0
   sections.append(dict(id=sid,title=text[3:],paragraphCount=0))
   blocks.append(dict(id=f"if-only.{sid}.heading",kind="heading",text=text[3:]))
  else:
   n+=1
   blocks.append(dict(id=f"if-only.{sid}.p{n}",kind="paragraph",text=text))
   if sid!="intro":sections[-1]["paragraphCount"]+=1
 return raw,subtitle,proem,blocks,sections
def template(subtitle,proem,blocks):
 h=sha(ART)
 heading='<section class="book-chapter" id="work-if-only"><div class="book-chapter-heading"><h2 data-source-block="if-only.title">If Only</h2></div></section>'
 subtitle_para=f'<p class="frame-lead" data-source-block="if-only.subtitle" data-source-from="0" data-source-to="{len(subtitle)}">{html.escape(subtitle)}</p>'
 hero=f'<section class="book-art-leaf"><figure class="frame-reading-figure frame-essay-hero" data-source-block="if-only.hero" data-source-illustration-id="if-only.hero" data-source-plate-sha256="{h}" data-editorial-role="hero"><img loading="eager" decoding="sync" src="{FIG}" width="640" height="480" alt="{html.escape(ALT,quote=True)}"/></figure></section>'
 pref='<aside class="frame-editorial-proem" data-editorial-role="proem" data-source-block="if-only.editorial" data-source-from="0" data-source-to="'+str(len(proem))+'" role="note" aria-label="Editorial preface"><span class="frame-editorial-kicker">From the editor</span><p>'+inline(proem)+'</p></aside>'
 body="".join(f'<p{" class="+chr(34)+"frame-subheading"+chr(34) if b["kind"]=="heading" else ""} data-source-block="{b["id"]}" data-source-from="0" data-source-to="{len(b["text"])}">{inline(b["text"])}</p>' for b in blocks)
 return f'<template data-reader-volume="{ID}"><div class="book-flow" data-min-leaves="1">'+heading+hero+'<section class="book-chapter-text">'+pref+'<article class="book-prose">'+subtitle_para+body+'</article></section></div></template>'
def replace(t,edition):
 needle=re.compile(r'<template data-reader-volume="'+OLD+r'">.*?</template>',re.S)
 req(len(needle.findall(t))==1,"Old essay template identity not unique")
 t=needle.sub(lambda _:edition,t)
 marker=re.search(r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',t,re.S)
 req(bool(marker),"No source-owned gallery")
 gallery=json.loads(marker[1]);essays=gallery["collections"]["essays"]
 req(len(essays)==9 and essays[0]["id"]==OLD,"Source-owned gallery no longer matched v201")
 essays[0]=dict(id=ID,src=FIG,alt=ALT,sourceKind="source-authored-Teatro-Score",sourceSHA256=sha(ART))
 data='<script type="application/json" id="reader-gallery-data">'+json.dumps(gallery,ensure_ascii=False,separators=(",",":"))+'</script>'
 t=t[:marker.start()]+data+t[marker.end():]
 req(t.count('data-reader-volume="'+ID+'"')==1 and OLD not in re.findall(r'data-reader-volume="([^"]+)"',t),"Reader source sequence drift")
 return t
def direct(t,social,source):
 for old in ['data-initial-volume="library"','data-initial-volume="essays"','data-initial-volume="'+OLD+'"']:
  t=t.replace(old,'data-initial-volume="'+ID+'"',1)
 head,body=t.split("</head>",1)
 head=re.sub(r'<title>[^<]*</title>','<title>If Only — Benedikt Eickhoff — Fountain Press (private staging)</title>',head,count=1)
 head=re.sub(r'<meta property="og:[^>]*>',"",head)
 head=re.sub(r'<meta name="twitter:[^>]*>',"",head)
 head=re.sub(r'<link rel="canonical"[^>]*>',"",head)
 head=re.sub(r'<meta name="description"[^>]*>',"",head)
 desc="The tools were already there. If only that meant the work was done. A first-person history of Fountain Coach's instruments and simultaneous stages."
 meta=f'''<meta name="robots" content="noindex,nofollow"/>
<meta name="description" content="{html.escape(desc,quote=True)}"/>
<link rel="canonical" href="{HOST}{PATH}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="If Only — Benedikt Eickhoff"/>
<meta property="og:description" content="{html.escape(desc,quote=True)}"/>
<meta property="og:url" content="{HOST}{PATH}"/>
<meta property="og:image" content="{HOST}/estate/assets/social/essays/if-only-social.jpg"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:image:alt" content="{html.escape(ALT,quote=True)}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="If Only"/>
<meta name="twitter:image" content="{HOST}/estate/assets/social/essays/if-only-social.jpg"/>
<meta name="fountain:publication-state" content="private-owner-WLAN-staging"/>
<meta name="fountain:hero-source-sha256" content="{source}"/>
<meta name="fountain:social-sha256" content="{social}"/>'''
 head=head.replace("</title>","</title>\n"+meta,1)
 return head+"</head>"+body
def bookmeta(t,social,source):
 head,body=t.split("</head>",1)
 req("essays-first-chapter.jpg" in head,"Book social source changed")
 head=re.sub(r'(<meta property="og:image:alt" content=")[^"]+(")',lambda m:m[1]+html.escape(ALT,quote=True)+m[2],head,count=1)
 head=re.sub(r'(<meta name="fountain:hero-source-sha256" content=")[0-9a-f]{64}(")',lambda m:m[1]+source+m[2],head,count=1)
 head=re.sub(r'(<meta name="fountain:social-sha256" content=")[0-9a-f]{64}(")',lambda m:m[1]+social+m[2],head,count=1)
 return head+"</head>"+body
def main():
 req(sha(BASE/"source-lock.json")==LOCK,"Immutable predecessor drift")
 req(sha(ART)=="e03e5cf7ed8851fadd4c08488cdebd86cf98f177d9d28cb4ed9730ce69f8fa70","Artist-selected hero changed")
 rev=subprocess.check_output(["git","-C",str(R),"rev-parse","HEAD"],text=True).strip()
 raw,subtitle,proem,blocks,sections=source();edition=template(subtitle,proem,blocks)
 if OUT.exists():shutil.rmtree(OUT)
 changes=[]
 def stage(rel,data):
  target=write(rel,data);p=BASE/rel
  changes.append(dict(path=rel,beforeSHA256=sha(p) if p.is_file() else None,afterSHA256=sha(target)))
 artsha,socialsha=sha(ART),sha(SOC)
 for rel in ROUTES:
  old=(BASE/rel).read_text()
  new=replace(old,edition)
  if rel=="estate/books/essays/index.html":new=bookmeta(new,socialsha,artsha)
  stage(rel,new)
 olddirect=(BASE/("estate/read/"+OLD+"/index.html")).read_text()
 stage("estate/read/"+ID+"/index.html",direct(replace(olddirect,edition),socialsha,artsha))
 stage("estate/read/"+ID+"/assets/hero-simultanbuehne.webp",ART.read_bytes())
 stage("estate/assets/social/essays/if-only-social.jpg",SOC.read_bytes())
 stage("estate/assets/social/books/essays-first-chapter.jpg",SOC.read_bytes())
 cat=json.loads((BASE/"estate/books/catalog.json").read_text())
 essays=next(b for b in cat["books"] if b["id"]=="essays")
 req(essays["firstIllustratedChapterID"]==OLD,"Books catalogue predecessor is not v201")
 essays.update(firstIllustratedChapterID=ID,firstChapterOriginalImagePath=FIG,firstChapterOriginalImageSHA256=artsha,
  sourceIllustrationDeclaredSHA256=artsha,firstChapterImageAlt=ALT,
  sourceIllustrationProvenance="author-selected Solstice Teatro Score, private staging derivative",
  socialImageSHA256=socialsha,sourceRevision=rev,stageOnly=True,publicReleaseAuthorized=False)
 cat["privateEssayCandidate"]=dict(id=ID,sourceSHA256=digest(raw.encode()),heroSHA256=artsha,shareSHA256=socialsha,sourceRevision=rev)
 stage("estate/books/catalog.json",json.dumps(cat,ensure_ascii=False,indent=2)+"\n")
 manifest=dict(schema="fountain.press.source-bound-illustrated-essay.v1",title="If Only",sourceOwner="Fountain-Coach/fountain.coach",
  sourcePath=str(SRC.relative_to(R)),sourceRevision=rev,sourceSHA256=digest(raw.encode()),stageURL=HOST+PATH,
  publicationState="private-owner-WLAN-editorial-review",productionAuthorized=False,
  sections=sections,blocks=[dict(id="if-only.title",kind="title",text="If Only"),dict(id="if-only.subtitle",kind="subtitle",text=subtitle),dict(id="if-only.editorial",kind="editorial-proem",text=proem)]+blocks,
  figures=[dict(id="if-only.hero",path="hero-simultanbuehne.webp",role="hero",after="if-only.title",alt=ALT,
   sha256=artsha,stagingURL=FIG,originalPNG_SHA256=PNG_ORIGINAL,originalDimensions=[1448,1086],
   stageDerivativeDimensions=[640,480],sourceKind="author-selected Solstice Teatro Score")],
  heroFigureID="if-only.hero",heroSourceSHA256=artsha,shareURL=HOST+"/estate/assets/social/essays/if-only-social.jpg",
  shareImageSHA256=socialsha,shareImageDimensions=[1200,630],proem=proem,
  predecessor=dict(stageRelease=PREDECESSOR,sourceLockSHA256=LOCK),
  oldDraftRetainedAt="/estate/read/"+OLD+"/",
  renderer="existing Fountain Press measured Linotype Reader; shared engine unchanged")
 stage("estate/read/"+ID+"/edition-manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
 evidence=dict(schema="fountain.press.if-only-stage.v202",stageOnly=True,productionAuthorized=False,
  sourceRevision=rev,sourceSHA256=manifest["sourceSHA256"],firstSolsticePNG_SHA256=PNG_ORIGINAL,
  heroSHA256=artsha,shareSHA256=socialsha,stageHeroIsOptimizedDerivative=True,
  predecessorRelease=PREDECESSOR,predecessorLockSHA256=LOCK,
  galleryReplaces=OLD,archivalDirectRouteRetained=True,otherManuscriptsUnchanged=True,
  sharedReaderEngineUnchanged=True,changedFiles=changes)
 write("estate/evidence/if-only-v202.json",json.dumps(evidence,ensure_ascii=False,indent=2)+"\n")
 req((OUT/"estate/assets/social/books/essays-first-chapter.jpg").read_bytes()==SOC.read_bytes(),"Social parity")
 print(json.dumps({"status":"inert-v202-composed","sourceRevision":rev,
  "sourceSHA256":manifest["sourceSHA256"],"paragraphs":len(blocks),
  "changes":len(changes)+1,"stageRoute":HOST+PATH},indent=2))
if __name__=="__main__":main()
