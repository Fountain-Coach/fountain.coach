#!/usr/bin/env python3
"""Prepare, do not activate, Orange Dot graft into the EXISTING public Press baseline.

Source-only candidate: preserves public Essays and First Readings, admits all
23 selected source works/29 original images, and fixes illustration geometry.
The current rights-boundary remains private pending separate publisher review.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

OWNER=Path("/Users/benedikteickhoff/Developer/.orange-dot-reader-20261110")
SRC=OWNER/"scenarios/orange-dot"
BASE=Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111")
ORIG_HTML=Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/baseline/public-20261111-index.html")
ORIG_JS=Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/baseline/public-20261111-app.js")
CORRECTED_ENGINE=Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/baseline/reader-patch-v193.js")
HTML=BASE/"estate/index.html"
JS=BASE/"estate/assets/linotype/reading-first-app.js"
ENGINE=BASE/"estate/assets/linotype/reading-first-press-engine.js"
EXPECTED={
    str(ORIG_HTML):"005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49",
    str(ORIG_JS):"1b574fe1d24004a7c4d25ecc5df31cb098ac0784f4a87158ac5208d7cda06dd7",
    str(CORRECTED_ENGINE):"837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a",
}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def replace_once(s,a,b,reason):
    count=s.count(a)
    if count!=1:
        raise ValueError(f"{reason}: expected one anchor, got {count}: {a[:90]}")
    return s.replace(a,b,1)
def main():
    for p,h in EXPECTED.items():
        assert sha(Path(p))==h, ("public predecessor drift",p)
    assert HTML.is_file()
    original=ORIG_HTML.read_text()
    merged=HTML.read_text()
    selection=json.loads((SRC/"selection.json").read_text())
    assert selection["rightsBoundary"].startswith("Private author-controlled WLAN stage only")
    entries=selection["entries"]
    assert len(entries)==23 and sum(len(e["images"]) for e in entries)==29
    assert original.count('data-reader-volume=')==51
    assert merged.count('data-reader-volume=')==75
    assert merged.count('data-edition-membership="orange-dot"')==23
    assert merged.find('data-reader-volume="orange-dot"')>0
    source_gallery=json.loads(re.search(
        r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',
        original,re.S).group(1))
    merged_gallery=json.loads(re.search(
        r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',
        merged,re.S).group(1))
    for col in ("essays","first-readings"):
        assert merged_gallery["collections"][col]==source_gallery["collections"][col]
    assert len(merged_gallery["collections"]["orange-dot"])==23
    for e in entries:
        assert e["textSha256"]==sha(SRC/e["sourceTextFile"])
        for image in e["images"]:
            assert image["sha256"]==sha(SRC/"source-images"/image["sourceImageFile"])
    text=ORIG_JS.read_text()
    patches=[
      ("['first-readings','First Readings']",
       "['first-readings','First Readings'],['orange-dot','Orange Dot']", "collection label"),
      ("if(key.startsWith('essay--')||key.startsWith('solstice-reading-01--')){",
       "if(key.startsWith('essay--')||key.startsWith('solstice-reading-01--')||key.startsWith('orange-dot--')){",
       "volume recognition"),
      ("option.textContent=key.startsWith('essay--')?'Essays · '+label:'First Reading · '+label;",
       "option.textContent=key.startsWith('essay--')?'Essays · '+label:key.startsWith('orange-dot--')?'Orange Dot · '+label:'First Reading · '+label;",
       "volume selector"),
      ("const solsticeSequence=[...templates.keys()].filter(x=>x.startsWith('solstice-reading-01--'));",
       "const solsticeSequence=[...templates.keys()].filter(x=>x.startsWith('solstice-reading-01--'));\nconst orangeSequence=[...templates.keys()].filter(x=>x.startsWith('orange-dot--'));\nif(orangeSequence.length!==23)throw Error('Orange Dot source inventory changed');",
       "new original entry sequence"),
      ("const contents={essays:[...essaySequence,kinoPublicVolume],'first-readings':solsticeSequence};",
       "const contents={essays:[...essaySequence,kinoPublicVolume],'first-readings':solsticeSequence,'orange-dot':orangeSequence};",
       "third collection contents"),
      ("throw Error('Gallery no longer matches admitted source ordering');",
       "throw Error('Gallery no longer matches admitted source ordering');\nif(galleries['orange-dot']?.length!==orangeSequence.length || galleries['orange-dot'].some((e,i)=>e.id!==orangeSequence[i]))throw Error('Orange Dot gallery/source drift');",
       "new image and full-entry parity"),
      ("const isContents=name=>name==='essays'||name==='first-readings';",
       "const isContents=name=>name==='essays'||name==='first-readings'||name==='orange-dot';",
       "contents navigation"),
      ("if(solsticeSequence.includes(name))return 'first-readings';",
       "if(solsticeSequence.includes(name))return 'first-readings';\n if(orangeSequence.includes(name))return 'orange-dot';",
       "source owner collection"),
      ("const sequence=[contents.essays,solsticeSequence].find(s=>s.includes(name));",
       "const sequence=[contents.essays,solsticeSequence,orangeSequence].find(s=>s.includes(name));",
       "adjacent work"),
      ("(sequence===contents.essays?'essays':'first-readings')",
       "(sequence===contents.essays?'essays':sequence===orangeSequence?'orange-dot':'first-readings')",
       "work boundary return"),
      ("const surfaceOffsets={shelf:0,essays:0,'first-readings':0};",
       "const surfaceOffsets={shelf:0,essays:0,'first-readings':0,'orange-dot':0};",
       "surface offsets"),
      ("const galleryOffsets={essays:0,'first-readings':0};",
       "const galleryOffsets={essays:0,'first-readings':0,'orange-dot':0};",
       "gallery offsets"),
      ("const shelfContentsOffsets={essays:0,'first-readings':0};",
       "const shelfContentsOffsets={essays:0,'first-readings':0,'orange-dot':0};",
       "list offsets"),
      ("const collectionOrder=['essays','first-readings'];",
       "const collectionOrder=['essays','first-readings','orange-dot'];",
       "three horizontal books"),
      ("const selectedWork={essays:null,'first-readings':null};",
       "const selectedWork={essays:null,'first-readings':null,'orange-dot':null};",
       "one selection"),
      ("const compactPresentation={essays:'contents','first-readings':'contents'};",
       "const compactPresentation={essays:'contents','first-readings':'contents','orange-dot':'contents'};",
       "compact state"),
      ("if(pathname.includes('/collections/first-readings/'))return 'first-readings';",
       "if(pathname.includes('/collections/first-readings/'))return 'first-readings';\n if(pathname.includes('/collections/orange-dot/'))return 'orange-dot';",
       "direct route"),
      ("subtitle.textContent='Reading 01 · First Reading';",
       "subtitle.textContent=id==='orange-dot'?'Solstice · original post sequence':'Reading 01 · First Reading';",
       "editorial identity"),
    ]
    for a,b,reason in patches:
        text=replace_once(text,a,b,reason)
    JS.parent.mkdir(parents=True,exist_ok=True)
    new_js_sha=hashlib.sha256(text.encode()).hexdigest()
    new_js=JS.with_name("reading-first-app."+new_js_sha+".js")
    new_js.write_text(text)
    new_engine_sha=sha(CORRECTED_ENGINE)
    new_engine=ENGINE.with_name("reading-first-press-engine."+new_engine_sha+".js")
    new_engine.write_bytes(CORRECTED_ENGINE.read_bytes())
    # Public HTML invokes source-digest versions, not stale unversioned aliases.
    html_source=HTML.read_text()
    html_source=replace_once(html_source,
      "/estate/assets/linotype/reading-first-app.1b574fe1d24004a7c4d25ecc5df31cb098ac0784f4a87158ac5208d7cda06dd7.js",
      "/estate/assets/linotype/reading-first-app."+new_js_sha+".js", "live app selection")
    html_source=replace_once(html_source,
      "/estate/assets/linotype/reading-first-press-engine.e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a.js",
      "/estate/assets/linotype/reading-first-press-engine."+new_engine_sha+".js", "live compositor selection")
    HTML.write_text(html_source)
    print("PRODUCTION_EXECUTED_READER_ASSETS",new_js.name,new_engine.name)
    # Only this disposable candidate's former unversioned outputs may be cleaned.
    for old in (JS,ENGINE):
      if old.is_file(): old.unlink()
    # Static collection files remain source-bound to the same selected images
    # and remain explicitly UNAUTHORIZED for public release until rights review.
    stage_manifest=json.loads(Path(
      "/tmp/orange-dot-stage-delta-20261110/estate/collections/orange-dot/edition.json"
    ).read_text())
    stage_manifest["sourceGitRevision"]="b431528"
    stage_manifest["stageOnly"]=True
    stage_manifest["publicReleaseAuthorized"]=False
    stage_manifest["rightsBoundary"]=selection["rightsBoundary"]
    stage_manifest["preparation"]="PUBLIC-PREDECESSOR-BASED-PREFLIGHT-NOT-PUBLIC-PRODUCTION"
    path=BASE/"estate/collections/orange-dot/edition.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(stage_manifest,ensure_ascii=False,indent=2)+"\n")
    redirect=BASE/"estate/collections/orange-dot/index.html"
    redirect.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url=/estate/#/read/orange-dot"><title>Orange Dot · Fountain Press</title></head><body><p><a href="/estate/#/read/orange-dot">Read Orange Dot in Fountain Press</a></p></body></html>')
    changed={}
    for path in (BASE/"estate").rglob("*"):
        if not path.is_file():continue
        rel=path.relative_to(BASE).as_posix()
        changed[rel]=sha(path)
    assert len(changed)==31,(len(changed),sorted(changed))
    expected_paths={"estate/index.html","estate/assets/linotype/"+new_js.name,
        "estate/assets/linotype/"+new_engine.name,
        "estate/collections/orange-dot/edition.json","estate/collections/orange-dot/index.html"}
    assert expected_paths<=set(changed)
    assert len([n for n in changed if n.startswith("estate/assets/orange-dot/")])==26
    report={
        "schema":"fountain.press.orange-dot.public-predecessor-candidate.v1",
        "scope":"CANDIDATE ONLY, PUBLIC RIGHTS NOT ADMITTED",
        "publicBaseline":{"estateHTMLSHA256":EXPECTED[str(ORIG_HTML)],
                          "readerAppSHA256":EXPECTED[str(ORIG_JS)],
                          "readerEngineSHA256":"e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a"},
        "sourceRevision":"b431528","sourceOwner":"Fountain-Coach/fountain.coach",
        "selectedWorks":23,"originalImages":29,"newImageAssets":26,
        "existingFirstReadingImageReuse":3,
        "previousCollectionsPreserved":["essays","first-readings"],
        "newCollectionOrder":["essays","first-readings","orange-dot"],
        "rightsBoundary":selection["rightsBoundary"],
        "publicReleaseAuthorized":False,
        "candidatePathsSHA256":changed,
        "productionDeploy":False,
    }
    (BASE/"production-preflight-receipt.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("PUBLIC_BASE_CANDIDATE_PREPARED",len(changed),"changed/new files, original source materials and current public baseline")
    print("REVIEW_BOUNDARY",selection["rightsBoundary"])
    print("NEVER_DEPLOYED",BASE)
if __name__=="__main__":main()
