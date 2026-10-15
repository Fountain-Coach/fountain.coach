#!/usr/bin/env python3
"""Strict semantic ablation: neither Score nor image participates in identity."""
from pathlib import Path
from html import escape
from importlib.util import module_from_spec, spec_from_file_location
import hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
BASE="/fixtures/semantic-visual-bookshelf/"
OUT=SITE/BASE.lstrip("/")
PRESS=ROOT.parent.parent/"fountain-press/runtime"
EDITION=SITE/"essays/edition-manifest.json"
FIRST=SITE/"collections/first-readings/collection.json"
SHELF_CSS="/assets/linotype/bookshelf.css"
STYLE=BASE+"visual.css"
SCRIPT=BASE+"visual-reader.js"
LEAF_COUNT=3  # a constant test instrument, NEVER derived from sources

def sha(file:Path)->str:
    return hashlib.sha256(file.read_bytes()).hexdigest()

def renderer():
    spec=spec_from_file_location("semantic_ablation_bookshelf",PRESS/"bookshelf.py")
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.render_bookshelf

def wrap(page:str)->str:
    needle='<link rel="stylesheet" href="'+SHELF_CSS+'">'
    assert page.count(needle)==1
    page=page.replace(needle,needle+'\n<link rel="stylesheet" href="'+STYLE+'">')
    page=page.replace('class="book-app bookshelf-state','class="book-app bookshelf-state neutral-ablation',1)
    assert '<img' not in page and 'shelf-cover-name' not in page
    return page

def slot(identity,title,edition,target,revision):
    assert target.startswith(BASE) and len(revision)==64
    # A naked semantic object: identity, authority, parent, destination. No cover.
    return dict(id=identity,title=title,author="Benedikt Eickhoff",edition=edition,
                reader=target,source_revision=revision,host="fountain",status="wlan-proof")

def reader(collection,work):
    target=BASE+"collections/"+collection+"/#work-"+work["id"]
    leaves=''.join('<section class="visual-page" id="plate-'+str(n)+
                   '" role="group" aria-label="Blank test leaf '+str(n)+' of '+str(LEAF_COUNT)+'"'+
                   ('' if n==1 else ' hidden')+'></section>' for n in range(1,LEAF_COUNT+1))
    back='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>'
    prev='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7-7-7 7 7 7"/></svg>'
    next_='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>'
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
<title>{escape(work["title"])} — structural fixture</title>
<link rel="stylesheet" href="{STYLE}"><script type="module" src="{SCRIPT}"></script>
</head>
<body class="visual-reader neutral-ablation" data-work-id="{escape(work["id"],quote=True)}"
 data-collection-id="{escape(collection,quote=True)}" data-page-count="{LEAF_COUNT}"
 data-source-sha256="{work["sourceSHA256"]}">
<main class="visual-reader-main" aria-label="Content-free navigation for {escape(work["title"],quote=True)}">
<a class="visual-return" href="{target}" aria-label="Return to parent collection">{back}</a>
<div class="visual-book-frame" id="visual-book" aria-label="Three content-free structural test leaves">{leaves}</div>
<nav class="visual-reader-controls" aria-label="Page navigation">
<button type="button" id="visual-previous" aria-label="Previous blank leaf" disabled>{prev}</button>
<div class="visual-track" role="progressbar" aria-label="Position in test sequence"
 aria-valuemin="1" aria-valuemax="{LEAF_COUNT}" aria-valuenow="1"><span class="visual-progress-fill"></span></div>
<button type="button" id="visual-next" aria-label="Next blank leaf">{next_}</button>
</nav><p class="visual-assistive" id="visual-status" aria-live="polite"></p>
</main></body></html>'''

def main():
    edition=json.loads(EDITION.read_text())
    first=json.loads(FIRST.read_text())
    assert edition["schema"]=="fountain.press.linotype.essay-edition.v2"
    assert first["identity"]=="first-readings" and first["workCount"]==1
    assert [w["id"] for w in edition["essays"]]==edition["readingOrder"]
    source={w["id"]:w for w in edition["essays"]}
    for work in source.values():
        assert sha(SITE/work["sourcePath"])==work["sourceSHA256"]
    only=first["works"][0]
    assert only["workId"] in source
    assert only["sourceSHA256"]==source[only["workId"]]["sourceSHA256"]
    collection_members={
        "essays":list(edition["readingOrder"]),
        "first-readings":[only["workId"]]
    }
    OUT.mkdir(parents=True,exist_ok=True)
    for file in ("visual.css","visual-reader.js"):
        shutil.copyfile(ROOT/"fixtures/semantic-visual-bookshelf"/file,OUT/file)
    manifest=dict(schema="fountain.press.semantic-structural-ablation.v2",
                  published=False,release="wlan-proof",sourceOwner="Fountain-Coach/fountain.coach",
                  rendererOwner="Fountain-Coach/fountain-press",
                  hypothesis="Can the bookshelf encode hierarchy and reversible reading without content markers?",
                  displayPolicy=dict(visibleImages=0,visibleText=0,coverTitles=0,sourceImageDependence=False,
                                     leafCount=LEAF_COUNT,leafCountIndependentOfSource=True),
                  sourceManifests=dict(essaysSHA256=sha(EDITION),firstReadingsSHA256=sha(FIRST)),
                  collections=[],encounters=[])
    render=renderer()
    parents=[]
    for collection_id,ids in collection_members.items():
        parent=BASE+"collections/"+collection_id+"/"
        revision=sha(EDITION if collection_id=="essays" else FIRST)
        parents.append(slot(collection_id,collection_id,"Collection",parent,revision))
        manifest["collections"].append(dict(id=collection_id,parent=BASE,path=parent,works=ids))
        entries=[]
        for identity in ids:
            work=source[identity]
            path=parent+"works/"+identity+"/"
            entries.append(slot(identity,work["title"],"Work",path,work["sourceSHA256"]))
            manifest["encounters"].append(dict(collection=collection_id,workId=identity,
                   parent=parent,route=path,sourceSHA256=work["sourceSHA256"],
                   testLeaves=LEAF_COUNT))
            destination=OUT/"collections"/collection_id/"works"/identity
            destination.mkdir(parents=True,exist_ok=True)
            (destination/"index.html").write_text(reader(collection_id,work))
        html=render(title="Structural collection",imprint="Fountain Coach",books=entries,
                    css_url=SHELF_CSS,logo_url=None,logo_mode="unmarked",
                    cover_mode="unmarked",collection_title=collection_id,
                    collection_parent=BASE,collection_id=collection_id,
                    parent_navigation="publisher-circle")
        dest=OUT/"collections"/collection_id
        dest.mkdir(parents=True,exist_ok=True)
        (dest/"index.html").write_text(wrap(html))
    root=render(title="Structural Bookshelf",imprint="Fountain Coach",books=parents,
                css_url=SHELF_CSS,logo_url=None,logo_mode="unmarked",cover_mode="unmarked",
                parent_navigation="publisher-circle")
    (OUT/"index.html").write_text(wrap(root))
    (OUT/"fixture.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    for file in OUT.rglob("index.html"):
        raw=file.read_text()
        assert '<img' not in raw and 'data-asset-sha256' not in raw
        assert '<article' not in raw and 'cover_title' not in raw
    print("STRUCTURAL_ABLATION_BUILT",len(manifest["collections"]),"collections",
          len(manifest["encounters"]),"encounters",LEAF_COUNT,"identical blank leaves per work",
          "visible images ZERO")

if __name__=="__main__":
    main()
