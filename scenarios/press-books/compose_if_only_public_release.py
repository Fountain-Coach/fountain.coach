#!/usr/bin/env python3
"""Promote accepted If Only composition over the ACTUAL current public Fountain Press.

All 488 existing public files are copied unchanged first. The only authorized
changes are the book/Reader's shared essay template and gallery, the Esssays
source-hero/social identity, new direct essay, exact first-image assets, and
the catalog/manifest. Reader JS/CSS and other works are retained byte-for-byte.

Inputs: complete exact production predecessor, the author-accepted v202 private
stage direct edition and its source manifest, exact merged Git source owner.
Outputs: complete immutable public publication directory + narrow change receipt.
No SSH, Caddy, authorization, native delivery, or public mutation.
"""
import argparse
from pathlib import Path
import hashlib,html,json,re,shutil,subprocess

REPO=Path(__file__).resolve().parents[2]
OWNER="Fountain-Coach/fountain.coach"
VOLUME="essay--if-only"
SOURCE=REPO/"site/essays/if-only/if-only.md"
HERO=SOURCE.parent/"hero-simultanbuehne.webp"
SOCIAL=SOURCE.parent/"if-only-social.jpg"
PREVIOUS="fountain-press-fcis-value-20261112-ba6a653"
BASE_SHA="f4fded2432f586f7ebd99afd41d33842d84e2872c90430030307042a543609a0"
STAGE_SOURCE_SHA="396afcb457cdd930b208f94c520012abeaa6103498dd8001c8dd12ccd0fcc8a6"
STAGE_HERO_SHA="e03e5cf7ed8851fadd4c08488cdebd86cf98f177d9d28cb4ed9730ce69f8fa70"
STAGE_SOCIAL_SHA="f41b9bbec06e2de89c1369fa965fc382a867d331637903c3c18bde039254c583"
STAGE_ORIGINAL_SHA="f2ec1d79c05f16466c39b0e45c1f7a32cc0332b49c1664dbfadeb4b2c487c481"
PUBLIC_ORIGIN="https://fountain.coach"
HERO_PATH="/estate/read/essay--if-only/assets/hero-simultanbuehne.webp"
ESSAY_SOCIAL="/estate/assets/social/essays/if-only-social.jpg"
BOOK_SOCIAL="/estate/assets/social/books/essays-first-chapter.jpg"
BOOK_ROUTES=[
 "index.html", "estate/index.html", "estate/books/essays/index.html",
 "estate/books/first-readings/index.html","estate/books/orange-dot/index.html",
 "estate/read/essays/index.html",
]
DIRECT="estate/read/essay--if-only/index.html"
GALLERY_MARK=re.compile(r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)',re.S)
TEMPLATE=re.compile(r'<template data-reader-volume="essay--if-only">.*?</template>',re.S)
ALT="A sparse axonometric simultaneous stage: an empty central frame, a small terracotta mark on a left plinth, and a tablet on the floor to the right."

def sha(data):return hashlib.sha256(data).hexdigest()
def digest(path):return sha(path.read_bytes())
def insist(ok,msg):
 if not ok:raise RuntimeError(msg)
def source_git():
 return subprocess.check_output(["git","-C",str(REPO),"rev-parse","HEAD"],text=True).strip()
def normalized(s):
 # A common semantic text comparison: the accepted Reader uses <em>/<code>
 # for original Markdown emphasis/backticks, not verbatim delimiter glyphs.
 plain=html.unescape(re.sub(r'<[^>]+>','',s))
 plain=re.sub(r'(?<!\w)[*`]([^*`]+)[*`]',r'\1',plain)
 return re.sub(r'\s+',' ',plain).strip()
def get_gallery(page):
 m=GALLERY_MARK.search(page)
 insist(bool(m),"Missing protected native Bookshelf gallery")
 return m,json.loads(m.group(2))
def capture_stage(staged):
 html_text=(staged/"estate/read/essay--if-only/index.html").read_text()
 m=TEMPLATE.search(html_text)
 insist(bool(m) and len(TEMPLATE.findall(html_text))==1,"Accepted stage lost If Only template")
 manifest=json.loads((staged/"estate/read/essay--if-only/edition-manifest.json").read_text())
 insist(manifest["sourceSHA256"]==STAGE_SOURCE_SHA and manifest["heroSourceSHA256"]==STAGE_HERO_SHA
  and manifest["shareImageSHA256"]==STAGE_SOCIAL_SHA
  and manifest["figures"][0]["originalPNG_SHA256"]==STAGE_ORIGINAL_SHA,"Stage source identities drifted")
 insist(manifest["publicationState"].startswith("private"),"Accepted input is not private-stage edition")
 template=m.group()
 insist(template.count('data-source-illustration-id="if-only.hero"')==1,"Missing approved first Solstice score")
 insist('frame-editorial-proem' in template and 'From the editor' in template,"Accepted editor style missing")
 paragraphs=re.findall(r'<p[^>]*data-source-block="if-only\.(?:intro\.p\d+|s\d+\.p\d+)"[^>]*>(.*?)</p>',template,re.S)
 blocks=[b for b in manifest["blocks"] if b["kind"]=="paragraph"]
 insist(len(paragraphs)==len(blocks)>=40,"Source paragraphs missing from accepted Reader")
 for rendered,source in zip(paragraphs,blocks):
  insist(normalized(rendered)==normalized(html.escape(source["text"])),
   "Authored paragraph mismatch: "+source["id"])
 insist("192.168.8.50" not in template,"Private URL in rendered source template")
 return template,manifest
def integrate_html(old,template):
 # Other complete signed Reader volumes remain identical; only add one.
 insist(old.count('<template data-reader-volume="essay--if-only">')==0,
  "If Only already in production; refusing duplicate")
 mark='<template data-reader-volume="essay--'
 idx=old.find(mark)
 insist(idx>0,"No existing Reader essay templates")
 amended=old[:idx]+template+old[idx:]
 match,g=get_gallery(amended)
 originals=list(g["collections"]["essays"])
 insist(len(originals)==8 and originals[0]["id"]=="essay--the-value-of-what-we-can-prove","Unexpected public gallery predecessor")
 g["collections"]["essays"].insert(0,dict(id=VOLUME,src=HERO_PATH,alt=ALT,
  sourceKind="author-selected Solstice Teatro Score",sourceSHA256=STAGE_HERO_SHA))
 val=match.group(1)+json.dumps(g,ensure_ascii=False,separators=(",",":"))+match.group(3)
 amended=amended[:match.start()]+val+amended[match.end():]
 insist(amended.count('<template data-reader-volume="essay--if-only">')==1,"Duplicate template after composition")
 insist(amended.count("192.168.8.50")==0,"Stage-only address carried into public Reader")
 return amended
def head_meta(body,revision,kind):
 head,rest=body.split("</head>",1)
 if kind=="direct":
  head=re.sub(r'<title>[^<]*</title>',"<title>If Only — Benedikt Eickhoff — Fountain Press</title>",head,count=1)
  head=re.sub(r'<meta property="og:[^>]*>',"",head)
  head=re.sub(r'<meta name="twitter:[^>]*>',"",head)
  head=re.sub(r'<link rel="canonical"[^>]*>',"",head)
  head=re.sub(r'<meta name="description"[^>]*>',"",head)
  head=re.sub(r'<meta name="robots"[^>]*>',"",head)
  desc="A terminal can call the tools we once wrapped. If only that meant the work was done. The Contexter and Fountain Coach's simultaneous stages."
  social=PUBLIC_ORIGIN+ESSAY_SOCIAL
  tags=f'''<link rel="canonical" href="{PUBLIC_ORIGIN}/estate/read/essay--if-only/"/>
  <meta name="description" content="{html.escape(desc,quote=True)}"/>
  <meta name="robots" content="index,follow"/>
  <meta property="og:type" content="article"/>
  <meta property="og:title" content="If Only — Benedikt Eickhoff"/>
  <meta property="og:description" content="{html.escape(desc,quote=True)}"/>
  <meta property="og:url" content="{PUBLIC_ORIGIN}/estate/read/essay--if-only/"/>
  <meta property="og:image" content="{social}"/>
  <meta property="og:image:width" content="1200"/>
  <meta property="og:image:height" content="630"/>
  <meta property="og:image:alt" content="{html.escape(ALT,quote=True)}"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="If Only"/>
  <meta name="twitter:image" content="{social}"/>
  <meta name="fountain:hero-source-sha256" content="{STAGE_HERO_SHA}"/>
  <meta name="fountain:social-sha256" content="{STAGE_SOCIAL_SHA}"/>
  <meta name="fountain:publication-state" content="public-production"/>'''
  head=head.replace("</title>","</title>\n"+tags,1)
  rest=rest.replace('data-initial-volume="essays"','data-initial-volume="'+VOLUME+'"',1)
  rest=rest.replace('data-initial-volume="library"','data-initial-volume="'+VOLUME+'"',1)
 elif kind=="essays":
  # The existing Bookshelf social URL is retained; only its first-source image,
  # description and provenance change.
  head=re.sub(r'(<meta property="og:image:alt" content=")[^"]*(")',
   lambda m:m.group(1)+html.escape(ALT,quote=True)+m.group(2),head,count=1)
  head=re.sub(r'(<meta name="fountain:hero-source-sha256" content=")[0-9a-f]{64}(")',
   lambda m:m.group(1)+STAGE_HERO_SHA+m.group(2),head,count=1)
  head=re.sub(r'(<meta name="fountain:social-sha256" content=")[0-9a-f]{64}(")',
   lambda m:m.group(1)+STAGE_SOCIAL_SHA+m.group(2),head,count=1)
  # Book identity and canonical remain unchanged. Source revision only in
  # machine catalogue and release manifest, not by stealth in source prose.
 return head+"</head>"+rest
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--production-predecessor",type=Path,required=True)
 ap.add_argument("--accepted-stage",type=Path,required=True)
 ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--revision",required=True)
 a=ap.parse_args()
 revision=source_git()
 insist(a.revision==revision and len(revision)==40,"Source revision not the checked-out Git commit")
 predecessor=a.production_predecessor.resolve()
 insist(digest(predecessor/"index.html")==BASE_SHA and
        digest(predecessor/"estate/index.html")==BASE_SHA,"Actual predecessor has changed")
 insist(digest(SOURCE)==STAGE_SOURCE_SHA and digest(HERO)==STAGE_HERO_SHA
        and digest(SOCIAL)==STAGE_SOCIAL_SHA,"Source or accepted hero/social image drifted")
 template,manifest=capture_stage(a.accepted_stage)
 if a.output.exists():shutil.rmtree(a.output)
 shutil.copytree(predecessor,a.output,symlinks=False)
 result=a.output
 previous={p.relative_to(predecessor).as_posix():digest(p)
  for p in predecessor.rglob("*") if p.is_file()}
 changed=[]
 def put(path,contents):
  p=result/path
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_bytes(contents if isinstance(contents,bytes) else contents.encode("utf-8"))
  changed.append(dict(path=path,beforeSha256=previous.get(path),afterSha256=digest(p)))
 for path in BOOK_ROUTES:
  original=(predecessor/path).read_text()
  htmltext=integrate_html(original,template)
  if path=="estate/books/essays/index.html":
   htmltext=head_meta(htmltext,revision,"essays")
  put(path,htmltext)
 # Maintain exact same original book entrance at / and /estate/. Composed
 # independently from identical predecessors, so the resulting bytes coincide.
 insist((result/"index.html").read_bytes()==(result/"estate/index.html").read_bytes(),
        "Root and Fountain Press estate Reader entrance drifted")
 direct_base=(predecessor/"estate/read/essays/index.html").read_text()
 direct=head_meta(integrate_html(direct_base,template),revision,"direct")
 put("estate/read/essay--if-only/index.html",direct)
 put(HERO_PATH.lstrip("/"),HERO.read_bytes())
 put(ESSAY_SOCIAL.lstrip("/"),SOCIAL.read_bytes())
 put(BOOK_SOCIAL.lstrip("/"),SOCIAL.read_bytes())
 cat=json.loads((predecessor/"estate/books/catalog.json").read_text())
 book=next(x for x in cat["books"] if x["id"]=="essays")
 insist(book["firstIllustratedChapterID"]=="essay--the-value-of-what-we-can-prove",
        "Public predecessor book identity changed")
 book.update(firstIllustratedChapterID=VOLUME,firstChapterOriginalImagePath=HERO_PATH,
  firstChapterOriginalImageSHA256=STAGE_HERO_SHA,
  firstChapterImageAlt=ALT,sourceIllustrationDeclaredSHA256=STAGE_HERO_SHA,
  sourceIllustrationProvenance="author-selected first Solstice Teatro Score",
  socialImageSHA256=STAGE_SOCIAL_SHA,sourceRevision=revision,
  rightsProvenance="Author-approved artwork and essay, 13 November 2026",
  publicReleaseAuthorized=True,stageOnly=False,publicationState="public-production")
 cat["currentEssaysFirstChapter"]=dict(id=VOLUME,sourceRevision=revision,
  manuscriptSha256=STAGE_SOURCE_SHA,heroSha256=STAGE_HERO_SHA)
 # Do not preserve an unrelated private candidate from the predecessor.
 cat.pop("privateEssayCandidate",None)
 put("estate/books/catalog.json",json.dumps(cat,ensure_ascii=False,indent=2)+"\n")
 public_manifest=dict(manifest)
 public_manifest.update(sourceRevision=revision,stageURL=PUBLIC_ORIGIN+"/estate/read/essay--if-only/",
  publicationState="public-production",productionAuthorized=True,
  sourceOwner=OWNER,sourceSHA256=STAGE_SOURCE_SHA,
  publicReleasePredecessor=PREVIOUS,sourceFigureSHA256=STAGE_HERO_SHA,
  publicationAuthorization="author's explicit production approval following physical iPad stage acceptance")
 public_manifest["figures"][0]["stagingURL"]=HERO_PATH
 public_manifest["shareURL"]=PUBLIC_ORIGIN+ESSAY_SOCIAL
 public_manifest["predecessor"]["stageRelease"]="shared-shell-20261113-v202-if-only-solstice-b4c091f"
 put("estate/read/essay--if-only/edition-manifest.json",json.dumps(public_manifest,ensure_ascii=False,indent=2)+"\n")
 # No private stage evidence or machine-only permissions are made public.
 current={p.relative_to(result).as_posix():digest(p) for p in result.rglob("*") if p.is_file()}
 actual={p for p in current if previous.get(p)!=current[p]}
 declared={x["path"] for x in changed}
 insist(actual==declared,"Output changed files outside declared scope")
 for name,checksum in previous.items():
  if name not in declared:insist(current.get(name)==checksum,"Unrelated public file drift "+name)
 insist(len(current)>=len(previous),"Whole estate was truncated")
 insist(digest(result/HERO_PATH.lstrip("/"))==STAGE_HERO_SHA,"Hero SHA mismatch")
 insist(digest(result/BOOK_SOCIAL.lstrip("/"))==digest(result/ESSAY_SOCIAL.lstrip("/"))==STAGE_SOCIAL_SHA,
        "Essay/Bookshelf social parity mismatch")
 if (result/"estate/index.html").read_bytes()!=(result/"index.html").read_bytes():
  raise RuntimeError("Production homepage identity drift")
 output_report=a.output.parent/"if-only-public-composition.json"
 output_report.write_text(json.dumps({
  "schema":"fountain.press.if-only.publication-composition.v1",
  "sourceOwner":OWNER,"sourceRevision":revision,
  "predecessorRelease":PREVIOUS,"predecessorRootSha256":BASE_SHA,
  "manuscriptSHA256":STAGE_SOURCE_SHA,"heroSha256":STAGE_HERO_SHA,
  "firstSolsticeOriginalPNG_SHA256":STAGE_ORIGINAL_SHA,
  "socialSha256":STAGE_SOCIAL_SHA,"publicProductionAuthorized":True,
  "readerEngineCSSJavaScriptUnchanged":True,"originalPredecessorFileCount":len(previous),
  "finalFileCount":len(current),"changedFiles":changed},ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"result":"candidate-built-no-publish","revision":revision,
  "predecessorFiles":len(previous),"newFileCount":len(current),"changedFiles":len(changed),
  "rootParity":True},indent=2))

if __name__=="__main__":main()
