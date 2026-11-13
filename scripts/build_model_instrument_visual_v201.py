#!/usr/bin/env python3
"""Compose a source-verified visual-only v201 Fountain Press private stage overlay.

Input: the exact immutable v200 production-derived owner-WLAN predecessor.
Output: only changed source-bound essay templates, unchanged manuscript,
four replacement Teatro plates and hero-derived essay/book social raster.
No new Reader, new publishing authority or public production change.
"""
from pathlib import Path
import hashlib,importlib.util,json,html,re,subprocess,shutil,sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"build/model-illustrations-v201/baseline"
OUT=ROOT/"build/model-illustrations-v201/overlay"
SOURCE=ROOT/"site/essays/the-model-is-not-the-instrument/the-model-is-not-the-instrument.md"
ART=SOURCE.parent/"assets"
BUILD=ROOT/"scripts/build_model_instrument_press_stage.py"
EXPECTED_V200="37a8fcc215e89aa7eb59f92703361273ed47db9dbab768ce67ed9da2448eed01"
STAGE="shared-shell-20261113-v200-estate-editorial-da150ad"
VOLUME="essay--the-model-is-not-the-instrument"
ROUTES=[
 "estate/index.html",
 "estate/books/essays/index.html",
 "estate/read/essays/index.html",
 f"estate/read/{VOLUME}/index.html"
]
ASSET_DIR=f"estate/read/{VOLUME}/assets"
SOCIAL_PATH="estate/assets/social/essays/the-model-is-not-the-instrument-social.jpg"
BOOK_SOCIAL_PATH="estate/assets/social/books/essays-first-chapter.jpg"

def sha(b:bytes):return hashlib.sha256(b).hexdigest()
def file_sha(p):return sha(p.read_bytes())
def require(check,reason):
 if not check:raise RuntimeError(reason)
def write(rel,raw):
 p=OUT/rel
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(raw if isinstance(raw,bytes) else raw.encode("utf-8"))
 return p
def gitrevision():
 return subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
def load_builder():
 spec=importlib.util.spec_from_file_location("fountain_press_essay_builder",BUILD)
 mod=importlib.util.module_from_spec(spec)
 sys.modules[spec.name]=mod
 spec.loader.exec_module(mod)
 return mod
def make():
 require(file_sha(BASE/"source-lock.json")==EXPECTED_V200,"v200 predecessor no longer exact")
 mod=load_builder()
 manuscript,lead,sections,groups=mod.source_blocks()
 base_manifest=json.loads((BASE/f"estate/read/{VOLUME}/edition-manifest.json").read_text())
 require(sha(manuscript.encode())==base_manifest["sourceSHA256"],"Authored manuscript changed")
 new_template,blocks=mod.new_template(lead,groups)
 require(blocks==base_manifest["blocks"],"Authored essay source addresses or content changed")
 old_by_id={f["id"]:f for f in base_manifest["figures"]}
 require(set(old_by_id)=={f["id"] for f in mod.FIGURES},"Unapproved figure identity change")
 expected_positions={
 "model-instrument.hero":"model-instrument.title",
 "model-instrument.claim":"model-instrument.intro.p2",
 "model-instrument.score":"model-instrument.s1.p2",
 "model-instrument.workshop":"model-instrument.s3.p3"
 }
 assert {f["id"]:f["after"] for f in mod.FIGURES}==expected_positions
 require(new_template.count('data-source-illustration-id=')==4,"Exactly four source-addressed figures required")
 assert new_template.index('data-source-block="model-instrument.s3.p3"') < new_template.index('data-source-illustration-id="model-instrument.workshop"')
 assert new_template.index('data-source-illustration-id="model-instrument.workshop"') < new_template.index('data-source-block="model-instrument.s3.p4"')
 social=ART/mod.SOCIAL
 require(social.is_file(),"Hero-derived social image missing")
 with social.open("rb") as stream:
  require(stream.read(3)==b"\xff\xd8\xff","Expected a valid social JPEG")
 before_sha={f["id"]:f["sha256"] for f in base_manifest["figures"]}
 after_sha={f["id"]:file_sha(ART/f["path"]) for f in mod.FIGURES}
 require(all(before_sha[k]!=after_sha[k] for k in before_sha),"Source figure must actually change")
 new_social_sha=file_sha(social)
 require(new_social_sha!=base_manifest["shareImageSHA256"],"Social image not regenerated")
 new_rev=gitrevision()
 require(len(new_rev)==40,"Need exact Git owner")
 if OUT.exists():shutil.rmtree(OUT)
 changes=[]
 def record(rel,raw):
  b=raw if isinstance(raw,bytes) else raw.encode("utf-8")
  prev=BASE/rel
  old_sha=file_sha(prev) if prev.exists() else None
  target=write(rel,b)
  changes.append(dict(path=rel,oldSHA256=old_sha,newSHA256=file_sha(target)))
 def rewrite_figure_meta(text):
  for f in mod.FIGURES:
   old=old_by_id[f["id"]]
   text=text.replace(old["sha256"],after_sha[f["id"]])
   text=text.replace(html.escape(old["alt"],quote=True),html.escape(f["alt"],quote=True))
   text=text.replace(old["alt"],f["alt"])
  text=text.replace(base_manifest["shareImageSHA256"],new_social_sha)
  return text
 for rel in ROUTES:
  before=(BASE/rel).read_text()
  needle=re.compile(r'<template data-reader-volume="'+re.escape(VOLUME)+r'">.*?</template>',re.S)
  require(len(needle.findall(before))==1,"Exactly one original essay template needed: "+rel)
  after=needle.sub(lambda _:new_template,before)
  after=rewrite_figure_meta(after)
  require(after!=before,"Route did not change")
  require(after.count('data-reader-volume="'+VOLUME+'"')==1,"Original Reader changed")
  require('data-source-illustration-id="model-instrument.workshop"' in after,"Commercial figure missing")
  for f in mod.FIGURES:
   require(f["alt"] in after or html.escape(f["alt"],quote=True) in after,"Missing visual description in "+rel)
  for old in before_sha.values():
   require(old not in after,"Stale source-art digest still in "+rel)
  record(rel,after)
 # Exact source-owned rendered figure assets. The historic v200 files stay
 # preserved only in the retained predecessor release and its evidence.
 for f in mod.FIGURES:
  record(ASSET_DIR+"/"+f["path"],(ART/f["path"]).read_bytes())
 record(SOCIAL_PATH,social.read_bytes())
 record(BOOK_SOCIAL_PATH,social.read_bytes())
 # The same new hero SHA must be used by both edition + Bookshelf metadata.
 edition=dict(base_manifest)
 edition["sourceRevision"]=new_rev
 edition["figures"]=[
  dict(old_by_id[f["id"]],role=f["role"],after=f["after"],alt=f["alt"],sha256=after_sha[f["id"]])
  for f in mod.FIGURES
 ]
 edition["heroSourceSHA256"]=after_sha[mod.FIGURES[0]["id"]]
 edition["shareImageSHA256"]=new_social_sha
 edition["illustrationRevision"]={
  "sourceOwner":"Fountain-Coach/fountain.coach",
  "sourceRevision":new_rev,
  "semanticProof":"Request/execution/readback; claim/404; score/sound; licensed instrument on customer compute",
  "manuscriptSourceSHA256":base_manifest["sourceSHA256"],
  "commercialFigureMovedAfter":"model-instrument.s3.p3",
  "oldVisualSourceShas":before_sha,
  "newVisualSourceShas":after_sha,
  "stageOnly":True
 }
 record(f"estate/read/{VOLUME}/edition-manifest.json",json.dumps(edition,ensure_ascii=False,indent=2)+"\n")
 catalog=json.loads((BASE/"estate/books/catalog.json").read_text())
 book=next(x for x in catalog["books"] if x["id"]=="essays")
 require(book["firstIllustratedChapterID"]==VOLUME,"Unexpected Essays ordering")
 book.update(firstChapterOriginalImageSHA256=edition["heroSourceSHA256"],
             sourceIllustrationDeclaredSHA256=edition["heroSourceSHA256"],
             socialImageSHA256=new_social_sha,sourceRevision=new_rev,
             firstChapterImageAlt=mod.FIGURES[0]["alt"])
 catalog["privateEssayCandidate"].update(heroSHA256=edition["heroSourceSHA256"],
   shareSHA256=new_social_sha,sourceRevision=new_rev)
 record("estate/books/catalog.json",json.dumps(catalog,ensure_ascii=False,indent=2)+"\n")
 # New evidence, no editing the independently accepted historical v198/v200 receipts.
 inventory={
  "schema":"fountain.press.semantic-illustration.v201",
  "sourceOwner":"Fountain-Coach/fountain.coach",
  "sourceRevision":new_rev,
  "manuscriptSHA256":base_manifest["sourceSHA256"],
  "stageOnly":True,
  "productionAuthorized":False,
  "baselineRelease":STAGE,
  "baselineLockSHA256":EXPECTED_V200,
  "figureCount":4,
  "figurePositions":expected_positions,
  "formerFigureSHA256":before_sha,
  "figureSHA256":after_sha,
  "heroFigureID":"model-instrument.hero",
  "heroSHA256":edition["heroSourceSHA256"],
  "socialImageSHA256":new_social_sha,
  "socialImageDimensions":[1200,630],
  "bookSocialEqualsEssaySocial":True,
  "sourceTextChanged":False,
  "existingReaderEngineChanged":False,
  "changes":changes
 }
 ev="estate/evidence/model-instrument-illustrations-v201.json"
 write(ev,json.dumps(inventory,ensure_ascii=False,indent=2)+"\n")
 require((OUT/SOCIAL_PATH).read_bytes()==(OUT/BOOK_SOCIAL_PATH).read_bytes(),"Hero/share identity broken")
 print(json.dumps(dict(result="v201-source-visual-overlay-built",sourceRevision=new_rev,
   figures=4,changedFiles=len(changes)+1,sourceTextChanged=False,
   imageMoves={"model-instrument.workshop":expected_positions["model-instrument.workshop"]},
   heroSHA256=inventory["heroSHA256"],socialSHA256=new_social_sha,
   evidenceSHA256=file_sha(OUT/ev),baselineLockSHA256=EXPECTED_V200),indent=2))
if __name__=="__main__":make()
