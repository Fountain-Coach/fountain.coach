#!/usr/bin/env python3
"""Author-admitted Fountain Press public artifact from exact accepted v195 stage.

No remote access or server mutation here. This *declared public transform* changes
only book/collection public-status metadata, Orange Dot's legacy alias and the
Bookshelf social description. Every published predecessor path is inventoried.
Original chapter texts, images, Reader, scripts and page positions are immutable.
EstatePublisherSSHDelivery alone packages and activates the result on Caddy.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parent
ADMISSION=ROOT/"orange-dot-public-admission-20261111.json"
SCHEMA="fountain.press.orange-dot.public-author-admission.v1"
OLD_META="Fountain Coach Bookshelf: original writing, Teatro Scores, essays and First Readings."
NEW_META="Fountain Press Bookshelf: Essays, First Readings and Orange Dot."
EXPECTED_SOURCE_FILES=483
PUBLIC_PRESERVED_MUTATIONS={
    "estate/index.html",
    "estate/assets/linotype/reading-first-shell.css",
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def file_sha(path):
    return sha(path.read_bytes())

def assert_one(text,old,new):
    if text.count(old)!=1:
        raise ValueError("Source drift; expected exactly one "+old[:120]+" (found "+str(text.count(old))+")")
    return text.replace(old,new,1)

def write_changed(root,rel,raw):
    dest=root/rel
    if not dest.is_file() or dest.is_symlink():
        raise ValueError("Missing expected source-owned artifact "+rel)
    tmp=dest.with_name("."+dest.name+".public-atomic")
    tmp.write_bytes(raw)
    os.replace(tmp,dest)
    return sha(raw)

def check_source(src,inventory,admission):
    assert admission["schema"]==SCHEMA
    assert admission["publicationIntent"]=="PUBLIC_AUTHOR_AUTHORIZED_FOR_THIS_SELECTED_EDITION"
    assert admission["publicationHost"]=="fountain.coach"
    assert admission["selectedWritings"]==23 and admission["originalAccompanyingImages"]==29
    assert admission["editorialScope"]["bookshelfOrder"]==["essays","first-readings","orange-dot"]
    assert admission["editorialScope"]["medicineShowUnpublished"] is True
    assert admission["composition"]["publicPredecessorFileInventorySHA256"]==file_sha(inventory)
    assert admission["composition"]["productionDerivedHTMLSHA256"]==file_sha(src/"estate/index.html")
    all_files={p.relative_to(src).as_posix():p for p in src.rglob("*") if p.is_file()}
    assert len(all_files)==EXPECTED_SOURCE_FILES,("Unexpected full site file count",len(all_files))
    expected={}
    for row in inventory.read_text().splitlines():
        digest,rel=row.split("  ./",1)
        if len(digest)!=64 or rel in expected:raise ValueError("Invalid public predecessor SHA inventory")
        expected[rel]=digest
    assert len(expected)==445
    assert set(expected).issubset(set(all_files))
    changes={p for p,h in expected.items() if file_sha(all_files[p])!=h}
    assert changes==PUBLIC_PRESERVED_MUTATIONS,("Predecessor delta no longer bounded",changes)
    assert len(set(all_files)-set(expected))==38
    edition=json.loads((src/"estate/collections/orange-dot/edition.json").read_text())
    assert edition["entryCount"]==23 and edition["stageOnly"] is True and edition["publicReleaseAuthorized"] is False
    assert edition["sourceSelectionSHA256"]==admission["sourceSelectionSHA256"]
    assert len(edition["entries"])==23
    count=0
    for entry in edition["entries"]:
        count+=len(entry["images"])
        for img in entry["images"]:
            relative=img["readerPath"].lstrip("/")
            f=src/relative
            if not f.is_file() or f.is_symlink() or file_sha(f)!=img["sha256"]:
                raise ValueError("Original image missing/altered "+entry["id"]+": "+relative)
        if not entry["id"].startswith("orange-dot--"):raise ValueError("Unrecognized authored chapter identity")
    assert count==29,("Original artworks incomplete",count)
    catalog=json.loads((src/"estate/books/catalog.json").read_text())
    assert catalog["schema"]=="fountain.press.book-direct-links.v1"
    assert catalog["status"]=="owner-WLAN-staging-private"
    assert len(catalog["books"])==3
    assert [b["id"] for b in catalog["books"]]==admission["editorialScope"]["bookshelfOrder"]
    for book in catalog["books"]:
        assert book["stageOnly"] is True and book["publicReleaseAuthorized"] is False
        assert book["socialImageDimensions"]==[1200,630]
        original=src/book["firstChapterOriginalImagePath"].lstrip("/")
        social=src/book["socialImagePath"].lstrip("/")
        assert file_sha(original)==book["firstChapterOriginalImageSHA256"]
        assert file_sha(social)==book["socialImageSHA256"]
    index=(src/"estate/index.html").read_text()
    assert index.count('data-reader-volume="orange-dot--')==23
    for forbidden in ['data-reader-volume="score--between-gardens"',
                      'data-reader-volume="score--ballern-gehen"',
                      'data-reader-volume="score--midsummer-nights-dream"',
                      'data-reader-volume="essay--above-the-line"']:
        assert forbidden not in index,("Excluded former Works escaped source",forbidden)
    assert index.count(OLD_META)==3
    assert index.count('rel="alternate" type="application/json" title="Fountain Press Books"')==1
    print("SOURCE_ADMITTED_FOR_PUBLIC_TRANSFORM 23 texts 29 images; 445 predecessor files 2 anticipated edits 38 stage additions",flush=True)
    return catalog,edition,all_files,expected

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True,help="full exact production-derived v195 local staging review root")
    ap.add_argument("--output",type=Path,required=True,help="new public immutable artifact directory")
    ap.add_argument("--public-inventory",type=Path,required=True,help="pinned 445-file production predecessor SHA inventory")
    ap.add_argument("--revision",required=True,help="exact 40-character merged Git source commit")
    ap.add_argument("--receipt",type=Path,required=True,help="new local build receipt outside public site")
    args=ap.parse_args()
    if not re.fullmatch("[0-9a-f]{40}",args.revision):
        raise ValueError("Merged source revision must be exact forty-character Git SHA")
    if args.output.exists() or args.receipt.exists():
        raise ValueError("Cannot replace an existing artifact or build receipt")
    if args.output.is_relative_to(args.source) or args.source.is_relative_to(args.output):
        raise ValueError("Cannot mutate source through output directory")
    admission=json.loads(ADMISSION.read_text())
    catalog,edition,source_files,prev=check_source(args.source,args.public_inventory,admission)
    shutil.copytree(args.source,args.output,copy_function=os.link)
    changed={}
    index=(args.output/"estate/index.html").read_text()
    index=index.replace(OLD_META,NEW_META)
    assert index.count(NEW_META)==3
    index=assert_one(index,'<meta property="og:site_name" content="Fountain Coach"/>',
                                '<meta property="og:site_name" content="Fountain Press"/>')
    index=assert_one(index,'<meta property="og:title" content="On Continuity"/>',
                                '<meta property="og:title" content="Benedikt Eickhoff — Fountain Press Bookshelf"/>')
    index=assert_one(index,'<meta name="twitter:title" content="On Continuity"/>',
                                '<meta name="twitter:title" content="Benedikt Eickhoff — Fountain Press Bookshelf"/>')
    index=assert_one(index,'<title>Benedikt Eickhoff — Bookshelf</title>',
                                '<title>Benedikt Eickhoff — Fountain Press Bookshelf</title>')
    changed["estate/index.html"]=write_changed(args.output,"estate/index.html",index.encode())
    rights_decision="Author-authorized public Fountain Press edition, 11 November 2026; original imagery/paragraph addresses retained; third-party clearance not independently attested"
    edition["schema"]="fountain.press.orange-dot.public-edition.v1"
    edition["stageOnly"]=False
    edition["publicReleaseAuthorized"]=True
    edition["rightsBoundary"]=rights_decision
    edition["publicAdmissionSHA256"]=file_sha(ADMISSION)
    edition["publicAdmissionGitRevision"]=args.revision
    edition["preparation"]="AUTHOR-APPROVED-PUBLIC-PRESS-EDITION-SOURCE-BOUND"
    changed["estate/collections/orange-dot/edition.json"]=write_changed(
        args.output,"estate/collections/orange-dot/edition.json",
        (json.dumps(edition,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode())
    legacy=(args.output/"estate/collections/orange-dot/index.html").read_text()
    assert legacy.count("/estate/#/read/orange-dot")==2
    legacy=legacy.replace("/estate/#/read/orange-dot","/estate/books/orange-dot/")
    changed["estate/collections/orange-dot/index.html"]=write_changed(
        args.output,"estate/collections/orange-dot/index.html",legacy.encode())
    catalog["status"]="public-production"
    catalog["publicationAuthority"]="Author's explicit public publication decision of 2026-11-11, delivered by EstatePublisher/Caddy"
    catalog["publicAdmissionSHA256"]=file_sha(ADMISSION)
    catalog["publicAdmissionGitRevision"]=args.revision
    catalog["publicReleaseAuthorized"]=True
    catalog["sourceGitRevision"]=args.revision
    for book in catalog["books"]:
        book["stageOnly"]=False
        book["publicReleaseAuthorized"]=True
        book["publicationState"]="public-production"
        if book["id"]=="orange-dot":
            book["publicAdmissionSHA256"]=file_sha(ADMISSION)
            book["rightsProvenance"]="Author's 2026-11-11 public publication instruction; original source image SHA retained"
        else:
            book["rightsProvenance"]="Unchanged already-public existing book materials"
    changed["estate/books/catalog.json"]=write_changed(
        args.output,"estate/books/catalog.json",
        (json.dumps(catalog,sort_keys=True,ensure_ascii=False,indent=2)+"\n").encode())
    # An untouched source image or copied book HTML is a value, not a missing publish.
    output_files={p.relative_to(args.output).as_posix():p for p in args.output.rglob("*") if p.is_file()}
    assert set(output_files)==set(source_files) and len(output_files)==483
    for rel,source in source_files.items():
        if rel not in changed and file_sha(source)!=file_sha(output_files[rel]):
            raise ValueError("Unauthorized public site change "+rel)
    assert set(changed)=={
        "estate/index.html","estate/books/catalog.json",
        "estate/collections/orange-dot/index.html",
        "estate/collections/orange-dot/edition.json",
    }
    for rel,digest in prev.items():
        if rel in PUBLIC_PRESERVED_MUTATIONS:continue
        assert file_sha(output_files[rel])==digest,("Published original changed",rel)
    assert all(file_sha(output_files[rel])==h for rel,h in changed.items())
    receipt={
        "schema":"fountain.press.orange-dot.public-composition-receipt.v1",
        "status":"PUBLIC_CANDIDATE_NOT_YET_DELIVERED",
        "publicHost":"fountain.coach",
        "sourceOwnerGitRevision":args.revision,
        "publicAdmissionSHA256":file_sha(ADMISSION),
        "stageRelease":"shared-shell-20261111-v195-direct-books-social-5227c32",
        "originalStageHTMLSHA256":admission["composition"]["productionDerivedHTMLSHA256"],
        "publicPredecessor":admission["composition"]["publicPredecessor"],
        "publicPredecessorInventorySHA256":admission["composition"]["publicPredecessorFileInventorySHA256"],
        "sourceFileCount":len(source_files),"candidateFileCount":len(output_files),
        "publishedPredecessorPathsRetained":len(prev),
        "publishedPredecessorUnchangedPaths":len(prev)-len(PUBLIC_PRESERVED_MUTATIONS),
        "stageInheritingAdditions":len(source_files)-len(prev),
        "authorizedPublicTransforms":changed,
        "bookOrder":[x["id"] for x in catalog["books"]],
        "orangeDotCompleteWorks":edition["entryCount"],
        "orangeDotOriginalImages":sum(len(e["images"]) for e in edition["entries"]),
        "publicReleased":False,
        "caddyEdited":False,
    }
    args.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("PUBLIC_RELEASE_CANDIDATE_CREATED",args.output,"483 files / 4 source-declared public transforms",flush=True)
    print("RELEASE_RECEIPT",args.receipt,flush=True)

if __name__=="__main__":
    main()
