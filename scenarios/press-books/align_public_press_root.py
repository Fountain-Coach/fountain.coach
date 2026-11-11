#!/usr/bin/env python3
"""Make / and /estate/ the SAME source-authentic published Fountain Press book.

This follows the writer's one-Press-shell rule and the actual public root
regression: root index still served an old two-book Reader after Orange Dot
was independently and successfully published at /estate/. There is one
bounded change: root index is the EXACT same accepted /estate/index.html.
No new UI, redirect, CSS, JS, content, image or private media.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

EXPECTED_ROOT_SHA="005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49"
EXPECTED_PRESS_SHA="b8f2e495d7ba2e0b7ad0ca04321c7d5afb6a25633fdeb5dbccd90b8321d0b508"
EXPECTED_PREVIOUS_RELEASE="fountain-press-orange-dot-20261111-d71968a"
EXPECTED_SOURCE_REVISION="d71968a730d2e0458a6f67e74370f21c79e34b2f"
EXPECTED_MANIFEST_SHA="73589835922028b55f4f2a058b6db0e0328545766c919533fee0672b051b6ac4"
def sha(b):return hashlib.sha256(b).hexdigest()
def assert_site(root):
    files={f.relative_to(root).as_posix():f for f in root.rglob("*") if f.is_file()}
    assert len(files)==483,("Expected full 483-file public site",len(files))
    old=files["index.html"].read_bytes()
    adopted=files["estate/index.html"].read_bytes()
    assert sha(old)==EXPECTED_ROOT_SHA,"Existing public root changed"
    assert sha(adopted)==EXPECTED_PRESS_SHA,"Accepted public Press Bookshelf changed"
    assert b'data-reader-volume="orange-dot--' not in old
    assert adopted.count(b'data-reader-volume="orange-dot--')==23
    assert adopted.count(b'data-reader-volume="solstice-reading-01--')==32
    assert adopted.count(b'data-reader-volume="essay--')==10
    assert b'reading-first-app.2b3ed3e08c2ff459b7371e790e10720c711e78842797ff92dc1f6518bebe4458.js' in adopted
    assert b'Fountain Press Bookshelf: Essays, First Readings and Orange Dot.' in adopted
    assert b'<link rel="canonical" href="https://fountain.coach/"/>' in adopted
    assert b'data-initial-volume="library"' in adopted
    for forbidden in [b'data-reader-volume="score--between-gardens"',b'data-reader-volume="score--ballern-gehen"',b'data-reader-volume="score--midsummer-nights-dream"',b'data-reader-volume="essay--above-the-line"']:
        assert forbidden not in adopted
    catalog=json.loads((root/"estate/books/catalog.json").read_text())
    assert catalog["status"]=="public-production" and catalog["publicReleaseAuthorized"] is True
    assert [a["id"] for a in catalog["books"]]==["essays","first-readings","orange-dot"]
    edition=json.loads((root/"estate/collections/orange-dot/edition.json").read_text())
    assert edition["publicReleaseAuthorized"] is True and edition["stageOnly"] is False
    assert edition["entryCount"]==23 and sum(len(e["images"]) for e in edition["entries"])==29
    return files,adopted

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--native-previous-receipt",type=Path,required=True)
    p.add_argument("--revision",required=True)
    p.add_argument("--receipt",type=Path,required=True)
    a=p.parse_args()
    assert re.fullmatch("[0-9a-f]{40}",a.revision)
    assert not a.output.exists() and not a.receipt.exists()
    native=json.loads(a.native_previous_receipt.read_text())
    assert native["activated"] is True and native["state"]=="active"
    assert native["releaseID"]==EXPECTED_PREVIOUS_RELEASE
    assert native["sourceRevision"]==EXPECTED_SOURCE_REVISION
    assert native["sourceInventorySHA256"]==EXPECTED_MANIFEST_SHA
    assert any(f["path"]=="/estate/index.html" and f["sha256"]==EXPECTED_PRESS_SHA for f in native["verifiedPublicFiles"])
    original,adopted=assert_site(a.source)
    shutil.copytree(a.source,a.output,copy_function=os.link)
    previous=a.output/"index.html"
    tmp=previous.with_name(".index.html.root-alignment")
    tmp.write_bytes(adopted)
    os.replace(tmp,previous)
    copied,accepted=assert_released_site(a.output)
    for name,path in original.items():
        if name=="index.html":continue
        assert sha(path.read_bytes())==sha(copied[name].read_bytes()),"Unrequested public site change: "+name
    record={
      "schema":"fountain.press.public-root-alignment-receipt.v1",
      "status":"SOURCE_CANDIDATE_NOT_DELIVERED",
      "sourceRevision":a.revision,
      "previousPublicRelease":EXPECTED_PREVIOUS_RELEASE,
      "previousEstateHTMLSHA256":EXPECTED_PRESS_SHA,
      "previousPublicRootSHA256":EXPECTED_ROOT_SHA,
      "newRootSHA256":sha(adopted),
      "sameExactBookCompositionForBothRoutes":True,
      "changedPublicFiles":{"index.html":sha(adopted)},
      "sourceFileCount":len(original),
      "retainedUnchangedFileCount":len(original)-1,
      "orangeDotEntries":23,
      "orangeDotOriginalImages":29,
      "newServerOrDNSChanges":False,
      "rollBackReleaseRetained":True,
    }
    a.receipt.write_text(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("PRESS_ROOT_ALIGNED_TO_CANONICAL_BOOK",a.output,"files",len(copied),"changed=1")
    print("ROOT_SHA256",sha(adopted),"ORANGE_DOT",23,"images",29)

def assert_released_site(root):
    files={f.relative_to(root).as_posix():f for f in root.rglob("*") if f.is_file()}
    assert len(files)==483
    data=(root/"index.html").read_bytes()
    assert sha(data)==EXPECTED_PRESS_SHA
    assert data==(root/"estate/index.html").read_bytes()
    return files,data

if __name__=="__main__":main()
