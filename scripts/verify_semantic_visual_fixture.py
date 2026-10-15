#!/usr/bin/env python3
"""Contract test: meaning must survive total removal of artwork and prose."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
BASE="/fixtures/semantic-visual-bookshelf/"
OUT=SITE/BASE.lstrip("/")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check():
    m=json.loads((OUT/"fixture.json").read_text())
    assert m["schema"]=="fountain.press.semantic-structural-ablation.v2"
    assert m["published"] is False
    assert m["displayPolicy"]==dict(
        visibleImages=0,visibleText=0,coverTitles=0,sourceImageDependence=False,
        leafCount=3,leafCountIndependentOfSource=True)
    assert m["sourceManifests"]==dict(
        essaysSHA256=sha(SITE/"essays/edition-manifest.json"),
        firstReadingsSHA256=sha(SITE/"collections/first-readings/collection.json"))
    assert [c["id"] for c in m["collections"]]==["essays","first-readings"]
    assert [len(c["works"]) for c in m["collections"]]==[3,1]
    assert len(m["encounters"])==4
    source=json.loads((SITE/"essays/edition-manifest.json").read_text())
    work_by_id={w["id"]:w for w in source["essays"]}
    assert len(work_by_id)==3
    assert [e["workId"] for e in m["encounters"] if e["collection"]=="essays"]==source["readingOrder"]
    first=json.loads((SITE/"collections/first-readings/collection.json").read_text())
    assert [e["workId"] for e in m["encounters"] if e["collection"]=="first-readings"]==[first["works"][0]["workId"]]
    for e in m["encounters"]:
        work=work_by_id[e["workId"]]
        assert e["sourceSHA256"]==work["sourceSHA256"]==sha(SITE/work["sourcePath"])
        assert e["testLeaves"]==3
        assert e["parent"]==BASE+"collections/"+e["collection"]+"/"
        page=(SITE/e["route"].lstrip("/")/"index.html").read_text()
        assert 'data-work-id="'+e["workId"]+'"' in page
        assert 'data-source-sha256="'+e["sourceSHA256"]+'"' in page
        assert 'data-collection-id="'+e["collection"]+'"' in page
        assert page.count('class="visual-page"')==3
        assert 'href="'+e["parent"]+'#work-'+e["workId"]+'"' in page
        assert 'id="visual-next"' in page and 'id="visual-previous"' in page
        assert 'data-page-count="3"' in page
        assert not any(t in page for t in ('<img','<article','data-asset-sha256','<h1','essay-prose'))
    for c in m["collections"]:
        html=(SITE/c["path"].lstrip("/")/"index.html").read_text()
        assert 'data-collection-id="'+c["id"]+'"' in html
        assert html.count('class="shelf-book"')==len(c["works"])
        assert html.count('class="shelf-cover shelf-cover-unmarked"')==len(c["works"])
        assert html.count('class="bookshelf-empty" aria-hidden="true"')==20
        assert 'href="'+BASE+'"' in html
    root=(OUT/"index.html").read_text()
    assert root.count('class="shelf-book"')==2
    assert root.count('class="shelf-cover shelf-cover-unmarked"')==2
    assert root.count('class="bookshelf-empty" aria-hidden="true"')==20
    for p in OUT.rglob("index.html"):
        page=p.read_text()
        assert '<img' not in page and 'shelf-cover-name' not in page
        assert 'data-asset-sha256' not in page
        assert 'src="/essays' not in page and 'alt="Original' not in page
        assert '<p>First' not in page and '<h2>' not in page
    assert not any(k in m for k in ("images","arts","coverArtwork","covers"))
    css=(OUT/"visual.css").read_text()
    assert ".shelf-cover-unmarked" in css and ".visual-page" in css
    js=(OUT/"visual-reader.js").read_text()
    assert "history.pushState" in js and "popstate" in js and "pointerup" in js
    assert len({e["route"] for e in m["encounters"]})==4
    duplicated=[e for e in m["encounters"] if e["workId"]=="teatro-an-unfinished-composition"]
    assert len(duplicated)==2 and duplicated[0]["sourceSHA256"]==duplicated[1]["sourceSHA256"]
    assert duplicated[0]["parent"]!=duplicated[1]["parent"]
    print("STRUCTURAL_BOOKSHELF_ABLATION_PASS: zero source images, zero visible prose, identical 3-page neutral reader, 2 collections, 4 context-bound encounters")

if __name__=="__main__":
    check()
