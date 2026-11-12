#!/usr/bin/env python3
"""Compose one public Fountain Press essay release from a verified production predecessor.

No publishing side-effects. The production predecessor's 483 files are the
complete source of every inherited public route. The staged author-approved
source/illustration and existing Press compositor supply only a bounded delta.
"""
from pathlib import Path
import json, hashlib, re, shutil, argparse

WORK_ID="essay--the-value-of-what-we-can-prove"
TITLE="The Value of What We Can Prove"
SOURCE_SHA="113781a540e606ae3de6436bb72b126d92fa1dcf5cfb565d72f26bedc1e731b5"
HERO_SHA="b043511473e6bca1e05b3c09d8dc1c92997b8bcbacb8506525ca0a4c0f02ebdb"
SOCIAL_SHA="82ccaf0e6d050c046d44a0684f420e36d4dd71f8655faa5c42925152e93b40f3"
SOURCE_REV="ba6a6531d82934a52a6ac63e6f39cc477992b803"
PARENT="fountain-press-orange-dot-root-20261111-fe71ba5"
RELEASE="fountain-press-fcis-value-20261112-ba6a653"
BASE_ROOT_SHA="b8f2e495d7ba2e0b7ad0ca04321c7d5afb6a25633fdeb5dbccd90b8321d0b508"
ESSAY_REL=f"estate/read/{WORK_ID}/index.html"
IMAGE_REL=f"estate/read/{WORK_ID}/assets/fcis-value-illustration.webp"
SOCIAL_REL="estate/assets/social/essays/the-value-of-what-we-can-prove.jpg"
SOCIAL_BOOK_REL="estate/assets/social/books/essays-first-chapter.jpg"
APP_SHA="233205de4f9ce94289086bb23e31b0df45009818438bc0eff03a4e2688299c68"

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def inventory(root):
    return {p.relative_to(root).as_posix():sha(p.read_bytes())
            for p in root.rglob("*") if p.is_file()}
def public_robots(path):
    s=path.read_text()
    # The private review had two incompatible robots statements; public has one.
    s=re.sub(r'<meta name="robots" content="[^"]*"\s*/?>\s*','',s)
    if s.count("</head>")!=1:raise RuntimeError("No unique HTML head")
    s=s.replace("</head>",'<meta name="robots" content="index,follow"/>\n</head>',1)
    path.write_text(s)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--predecessor",type=Path,required=True)
    parser.add_argument("--working",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    previous,working,output=args.predecessor,args.working,args.output
    if output.exists():raise RuntimeError("No overwrite of production candidate")
    if sha((previous/"estate/index.html").read_bytes())!=BASE_ROOT_SHA:raise RuntimeError("Production index changed")
    if (previous/"index.html").read_bytes()!=(previous/"estate/index.html").read_bytes():raise RuntimeError("Prior root mismatch")
    if len(inventory(previous))!=483:raise RuntimeError("Production predecessor inventory changed")
    if sha((working/IMAGE_REL).read_bytes())!=HERO_SHA or sha((working/SOCIAL_REL).read_bytes())!=SOCIAL_SHA:
        raise RuntimeError("Staged image/social source changed")
    manuscript=json.loads((working/f"estate/read/{WORK_ID}/edition-manifest.json").read_text())
    if manuscript.get("sourceSHA256")!=SOURCE_SHA or manuscript.get("sourceRevision")!=SOURCE_REV:
        raise RuntimeError("Author source revision changed")
    if len(manuscript["sourceBlocks"])!=28 or len(manuscript["sections"])!=6:
        raise RuntimeError("Authored prose inventory changed")
    if manuscript["originalImages"]!=1 or manuscript["figures"][0]["originalSHA256"]!=HERO_SHA:
        raise RuntimeError("Approved figure provenance changed")
    if len(inventory(working))-len(inventory(previous))>15:
        raise RuntimeError("Unexpected inherited route additions")
    shutil.copytree(working,output,copy_function=shutil.copy2)
    # The unillustrated v196 source-app was an intermediate stage compilation,
    # never referenced by the final illustrated Reader. Do not publish it.
    intermediate=output/"estate/assets/linotype/reading-first-app.f6973e96f9e16c30d814016b04d5febdf3c042f938a5740d5955d1128fbc458d.js"
    if not intermediate.is_file():raise RuntimeError("Missing expected intermediate source app")
    for page in output.rglob("*.html"):
        if "reading-first-app.f6973e96" in page.read_text(errors="ignore"):
            raise RuntimeError("Intermediate Reader still referenced by "+str(page))
    intermediate.unlink()
    # The actual public origin has two identical reading entrances.
    shutil.copy2(output/"estate/index.html",output/"index.html")
    for path in (ESSAY_REL,"estate/read/essays/index.html"):
        public_robots(output/path)
    # Publication status belongs to this individually authorized essay, not all
    # older source works or private rehearsal/test media.
    manifest_path=output/f"estate/read/{WORK_ID}/edition-manifest.json"
    manuscript.update({
        "stagingOnly":False,"publicReleaseAuthorized":True,
        "publicationState":"published","releaseID":RELEASE,
        "publicURL":f"https://fountain.coach/estate/read/{WORK_ID}/",
        "productionPredecessor":PARENT,
        "publicationDecision":"Author-approved public Fountain Press release, 2026-11-12",
        "sourceRevision":SOURCE_REV,
    })
    manuscript["figures"][0]["rights"]="Author-approved public illustration and source-derived social preview, 2026-11-12"
    manifest_path.write_text(json.dumps(manuscript,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    book_path=output/"estate/books/catalog.json"
    book=json.loads(book_path.read_text())
    if book["schema"]!="fountain.press.book-direct-links.v1" or len(book["books"])!=3:
        raise RuntimeError("Bookshelf contract changed")
    essays=next(v for v in book["books"] if v["id"]=="essays")
    if essays["firstIllustratedChapterID"]!=WORK_ID or essays["firstChapterOriginalImageSHA256"]!=HERO_SHA or essays["socialImageSHA256"]!=SOCIAL_SHA:
        raise RuntimeError("Essays social-source identity drift")
    if book.get("publicReleaseAuthorized") is not True or book.get("status")!="public-production":
        raise RuntimeError("Predecessor public Bookshelf status not preserved")
    book["latestAdmittedEssay"]={
        "workID":WORK_ID,"sourceRevision":SOURCE_REV,
        "sourceSHA256":SOURCE_SHA,"heroSHA256":HERO_SHA,
        "publicURL":f"https://fountain.coach/estate/read/{WORK_ID}/",
        "socialURL":f"https://fountain.coach/{SOCIAL_REL}",
        "socialSHA256":SOCIAL_SHA,
        "releaseID":RELEASE,
        "authorApproved":True,"publicationDate":"2026-11-12"
    }
    book["publicPredecessor"]=PARENT
    book["currentReleaseID"]=RELEASE
    book_path.write_text(json.dumps(book,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    # A fresh release summary supersedes the historical heading-release manifest
    # while preserving its SHA-bound identity as an archived predecessor.
    release_manifest_path=output/"release-manifest.json"
    old_summary_sha=sha((previous/"release-manifest.json").read_bytes())
    release={
      "schemaVersion":1,"schema":"fountain.press.source-bound-static-release.v198",
      "host":"fountain.coach","releaseID":RELEASE,"releaseMode":"EstatePublisher-SSH-static-immutable",
      "previousReleaseID":PARENT,"publicationState":"public-release-authorized",
      "sourceRepo":"Fountain-Coach/fountain.coach","sourceRevision":SOURCE_REV,
      "sourceSHA256":SOURCE_SHA,
      "stageRelease":"shared-shell-20261112-v197-fcis-value-illustrated-ba6a653",
      "stageSourceLockSHA256":"e35eb681ef23feeacd8bfa05c391dd0c7ee94156baf0b331af6b0e0950f54398",
      "approvedWork":WORK_ID,"workRoute":"/estate/read/"+WORK_ID+"/",
      "collectionRoute":"/estate/read/essays/",
      "heroOriginalSHA256":HERO_SHA,"socialDerivativeSHA256":SOCIAL_SHA,
      "preservedPreviousReleaseManifestSHA256":old_summary_sha,
      "publicationDecision":"Author publicly instructed publication of the accepted illustrated essay, 2026-11-12",
      "publicationExclusions":["private rehearsal recordings","unreleased staging-only pages","source locks","secrets"],
      "machineRoutes":["/estate/books/catalog.json",f"/estate/read/{WORK_ID}/edition-manifest.json"],
    }
    release_manifest_path.write_text(json.dumps(release,indent=2,ensure_ascii=False)+"\n")
    # Source-byte invariant: images and manuscript are identical to the WLAN stage.
    if sha((output/IMAGE_REL).read_bytes())!=HERO_SHA or sha((output/SOCIAL_REL).read_bytes())!=SOCIAL_SHA:
        raise RuntimeError("Final image-source bytes changed")
    final_inv=inventory(output);old_inv=inventory(previous)
    added={p:h for p,h in final_inv.items() if p not in old_inv}
    modified={p:h for p,h in final_inv.items() if p in old_inv and h!=old_inv[p]}
    removed=sorted(set(old_inv)-set(final_inv))
    if removed:raise RuntimeError("Unintended production file deletion "+str(removed))
    expected_added={
      ESSAY_REL,f"estate/read/{WORK_ID}/edition-manifest.json",IMAGE_REL,SOCIAL_REL,
      f"estate/assets/linotype/reading-first-app.{APP_SHA}.js"
    }
    expected_modified={
      "index.html","estate/index.html","estate/read/essays/index.html",
      "estate/books/catalog.json","estate/books/essays/index.html",
      "estate/books/first-readings/index.html","estate/books/orange-dot/index.html",
      SOCIAL_BOOK_REL,"release-manifest.json"
    }
    if set(added)!=expected_added or set(modified)!=expected_modified:
        raise RuntimeError("Unexpected release delta: added="+str(sorted(added))+" modified="+str(sorted(modified)))
    preserved=len(old_inv)-len(modified)
    if preserved!=474:raise RuntimeError("Unexpected published predecessor preservation")
    if (output/"index.html").read_bytes()!=(output/"estate/index.html").read_bytes():
        raise RuntimeError("Root and estate are not exactly the same publication")
    receipt={"releaseID":RELEASE,"previousReleaseID":PARENT,
         "sourceRevision":SOURCE_REV,"sourceSHA256":SOURCE_SHA,
         "inheritedProductionFiles":len(old_inv),"preservedProductionFiles":preserved,
         "added":added,"modified":modified,"removed":removed,
         "heroSourceSHA256":HERO_SHA,"socialSHA256":SOCIAL_SHA,
         "publicReleaseCandidate":True,"delivered":False}
    (output.parent/"fcis-value-prod-composition-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("PRODUCTION_ESSAY_CANDIDATE",RELEASE,
          "preserved",preserved,"modified",len(modified),"added",len(added),"removed",len(removed))
    print("NEW",list(added))
    print("MODIFIED",list(modified))
    print("PUBLIC_DELIVERY_NOT_YET_ATTEMPTED")
if __name__=="__main__":main()
