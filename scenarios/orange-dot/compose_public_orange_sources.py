#!/usr/bin/env python3
"""Deterministically graft only Orange Dot's authored sources onto actual public Press.

Current public Bookshelf/Reader remains the predecessor; never copy private
staging's entire site. Output is a local private publication-review candidate.
"""
import hashlib,html,json,re,shutil
from pathlib import Path
ROOT=Path("/Users/benedikteickhoff/Developer/.orange-dot-reader-20261110/scenarios/orange-dot")
BASE=Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111")
PUBLIC=Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/baseline/public-20261111-index.html")
STAGED_ORANGE=Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/baseline/orange-dot-v185-composed.html")
OUT=BASE/"estate/index.html"
PUBLIC_SHA="005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49"
SOURCE_SHA="0d9d16093a300c787e703dc53658dba8616ce8b2204378781be0b4babc715b8b"
def sha(b):return hashlib.sha256(b).hexdigest()
def replace_once(s,a,b):
    assert s.count(a)==1,(a[:75],s.count(a))
    return s.replace(a,b,1)
def gallery(s):
    pattern=r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)'
    m=re.search(pattern,s,re.S)
    assert m
    return m,json.loads(m.group(2))
def main():
    assert sha(PUBLIC.read_bytes())==PUBLIC_SHA
    assert sha(STAGED_ORANGE.read_bytes())==SOURCE_SHA
    selected=json.loads((ROOT/"selection.json").read_text())
    assert selected["rightsBoundary"].startswith("Private author-controlled WLAN stage only")
    entries=selected["entries"]
    assert len(entries)==23 and sum(len(x["images"]) for x in entries)==29
    for entry in entries:
        assert sha((ROOT/entry["sourceTextFile"]).read_bytes())==entry["textSha256"]
        for im in entry["images"]:
            assert sha((ROOT/"source-images"/im["sourceImageFile"]).read_bytes())==im["sha256"]
    original=PUBLIC.read_text()
    authored=STAGED_ORANGE.read_text()
    pattern=r'<template data-reader-volume="orange-dot(?:--[^"]+)?"[^>]*>.*?</template>'
    templates=re.findall(pattern,authored,re.S)
    assert len(templates)==24 and sum('data-edition-membership="orange-dot"' in x for x in templates)==23
    for entry in entries:
        matching=[t for t in templates if 'data-reader-volume="'+entry["id"]+'"' in t]
        assert len(matching)==1 and 'data-source-sha256="'+entry["textSha256"]+'"' in matching[0]
    s=replace_once(original,
      '<script type="application/json" id="reader-gallery-data">',
      '\n'.join(templates)+'\n<script type="application/json" id="reader-gallery-data">')
    m,newsource=gallery(s)
    _,stage_gallery=gallery(authored)
    for section in ("essays","first-readings"):
        assert newsource["collections"][section]==gallery(original)[1]["collections"][section]
    assert "orange-dot" not in newsource["collections"]
    newsource["collections"]["orange-dot"]=stage_gallery["collections"]["orange-dot"]
    newsource["source"]["orangeDot"]={
        "owner":"Benedikt Eickhoff",
        "sourceRevision":"b431528",
        "sourceKind":"selected-original-Facebook-posts",
        "stageOnly":True,"publicReleaseAuthorized":False,
    }
    s=s[:m.start(2)]+json.dumps(newsource,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+s[m.end(2):]
    cover_old='<figcaption>Reading 01 — First Reading</figcaption></figure></div></article>'
    cover_new='<figcaption>Reading 01 — First Reading</figcaption></figure>'+(
      '<figure class="frame-book-cover"><a href="#/read/orange-dot" data-reader-target="orange-dot" '
      'aria-label="Open Orange Dot inside this reader"><span class="frame-cover-mark" aria-hidden="true">●</span>'
      '<span class="frame-cover-name">Orange Dot</span></a>'
      '<figcaption>Solstice · original post sequence</figcaption></figure>'
      '</div></article>')
    s=replace_once(s,cover_old,cover_new)
    assert s.count('data-edition-membership="orange-dot"')==23
    assert s.count('data-reader-volume=')==original.count('data-reader-volume=')+24
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(s,encoding="utf-8")
    new_assets=[]
    stage_manifest=json.loads(Path("/Volumes/DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/baseline/orange-dot-v185-edition.json").read_text())
    reused=0
    for e in stage_manifest["entries"]:
        for im in e["images"]:
            if im["storage"]=="existing-original-first-readings-asset":
                reused+=1
                continue
            assert im["storage"]=="original-export-image"
            name=Path(im["readerPath"]).name
            matching=next(a for a in entries if a["id"]==e["id"])
            origin=ROOT/"source-images"/name
            assert origin.is_file()
            b=origin.read_bytes()
            assert sha(b)==im["sha256"]
            out=BASE/im["readerPath"].lstrip("/")
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_bytes(b)
            new_assets.append(out)
    assert reused==3 and len(new_assets)==26
    print("PUBLIC_SOURCE_GRAFT_PREPARED",len(templates),"templates",len(new_assets),"new assets",reused,"source originals reused")
    print("INHERITED_PUBLIC_ORIGINAL",sha(PUBLIC.read_bytes()),"DERIVED_PUBLIC_READER",sha(OUT.read_bytes()))
    print("AUTHOR_SOURCE",selected["sourceAuthority"] if "sourceAuthority" in selected else "Benedikt Eickhoff", "RELEASE_AUTHORIZED",False)
if __name__=="__main__":main()
