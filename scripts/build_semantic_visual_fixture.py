#!/usr/bin/env python3
"""Content-free spatial Bookshelf proof: no editorial source names or imagery."""
from pathlib import Path
from html import escape
from importlib.util import module_from_spec, spec_from_file_location
import hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
BASE="/fixtures/semantic-visual-bookshelf/"
OUT=SITE/BASE.lstrip("/")
PRESS=ROOT.parent.parent/"fountain-press/runtime"
SHELF_CSS="/assets/linotype/bookshelf.css"
STYLE=BASE+"visual.css"
SCRIPT=BASE+"visual-reader.js"
LEAF_COUNT=3
# Anonymous structure only: IDs are opaque identifiers, not classifications
# or semantic interpretations borrowed from source documents.
SPACES=(("s-01",("o-01","o-02","o-03")),("s-02",("o-02",)))
OBJECTS=("o-01","o-02","o-03")

def token(value):
    return hashlib.sha256(("structural-bookshelf:anonymous:"+value).encode()).hexdigest()

def renderer():
    spec=spec_from_file_location("structural_bookshelf_renderer",PRESS/"bookshelf.py")
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.render_bookshelf

def marked_document(page,position=None):
    needle='<link rel="stylesheet" href="'+SHELF_CSS+'">'
    assert page.count(needle)==1
    page=page.replace(needle,needle+'\n<link rel="stylesheet" href="'+STYLE+'">')
    page=page.replace('class="book-app bookshelf-state','class="book-app bookshelf-state neutral-ablation',1)
    if position is not None:
        needle='data-linotype-state="bookshelf"'
        assert page.count(needle)==1
        page=page.replace(needle,needle+f' data-space-position="{position}"')
    assert "<img" not in page and "shelf-cover-name" not in page
    return page

def book_slot(key,space):
    path=BASE+"spaces/"+space+"/objects/"+key+"/"
    return dict(id=key,title=key,author="anonymous",edition="Object",
                reader=path,source_revision=token(key),host="fountain",status="wlan-proof")

def blank_book(space,position,key,members):
    parent=BASE+"spaces/"+space+"/#work-"+key
    leaves=''.join('<section class="visual-page" id="plate-'+str(n)+
                   '" role="group" aria-label="Blank test leaf '+str(n)+' of '+str(LEAF_COUNT)+'"'+
                   ('' if n==1 else ' hidden')+'></section>' for n in range(1,LEAF_COUNT+1))
    # The small publisher circle and membership row are the original
    # containing space, carried directly into the reading experience.
    membership=''.join(
        '<li class="reader-member'+(' is-current' if peer==key else '')+'">'+
        ('<span class="reader-member-mark" aria-current="true" aria-label="Current book"></span>'
         if peer==key else
         '<a class="reader-member-mark" href="'+BASE+'spaces/'+space+'/objects/'+peer+'/" aria-label="Open neighboring book"></a>')+
        '</li>' for peer in members)
    prev='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7-7-7 7 7 7"/></svg>'
    next_='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>'
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
<title>Blank structural reading</title>
<link rel="stylesheet" href="{STYLE}"><script type="module" src="{SCRIPT}"></script>
</head><body class="visual-reader neutral-ablation" data-object-id="{escape(key)}"
 data-space-id="{escape(space)}" data-space-position="{position}" data-page-count="{LEAF_COUNT}"
 data-object-token="{token(key)}">
<main class="visual-reader-main" aria-label="Anonymous blank reading">
<aside class="reader-context" aria-label="Containing space and book position">
<a class="reader-parent-circle visual-return" href="{parent}" aria-label="Return to containing space"></a>
<nav class="reader-members" aria-label="Books in the containing space"><ol>{membership}</ol></nav>
</aside>
<section class="reader-focus" aria-label="Open book">
<div class="reader-paper-assembly">
<div class="visual-book-frame" id="visual-book" aria-label="Content-free reading leaves" data-transition="rest">{leaves}</div>
</div>
<nav class="visual-reader-controls" aria-label="Page navigation">
<button type="button" id="visual-previous" aria-label="Previous blank leaf" disabled>{prev}</button>
<div class="visual-track" role="progressbar" aria-label="Position in test sequence"
 aria-valuemin="1" aria-valuemax="{LEAF_COUNT}" aria-valuenow="1"><span class="visual-progress-fill"></span></div>
<button type="button" id="visual-next" aria-label="Next blank leaf">{next_}</button>
</nav><p class="visual-assistive" id="visual-status" aria-live="polite"></p>
</section>
</main></body></html>'''

def main():
    render=renderer()
    # Generated fixture releases are immutable; remove only the previous
    # generated fixture subtree so no obsolete editorial-named URL survives.
    assert OUT == SITE / "fixtures/semantic-visual-bookshelf"
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True,exist_ok=True)
    for file in ("visual.css","visual-reader.js"):
        shutil.copyfile(ROOT/"fixtures/semantic-visual-bookshelf"/file,OUT/file)
    graph=dict(schema="fountain.press.spatial-bookshelf.fixture.v4",
               source="anonymous structural experiment; no editorial collection or work names",
               published=False,
               displayPolicy=dict(visibleImages=0,visibleText=0,sourceContent=False,
                                  coloredBy="containing-space-position",leafCount=LEAF_COUNT),
               objects=[dict(id=key,token=token(key)) for key in OBJECTS],
               spaces=[],encounters=[])
    root_spaces=[]
    for position,(space,members) in enumerate(SPACES):
        path=BASE+"spaces/"+space+"/"
        root_spaces.append(dict(id=space,reader=path,members=list(members)))
        graph["spaces"].append(dict(id=space,position=position,parent=BASE,
                                    route=path,members=list(members)))
        entries=[]
        for key in members:
            entry=book_slot(key,space)
            entries.append(entry)
            target=OUT/"spaces"/space/"objects"/key
            target.mkdir(parents=True,exist_ok=True)
            (target/"index.html").write_text(blank_book(space,position,key,members))
            graph["encounters"].append(dict(space=space,position=position,object=key,
                                             route=entry["reader"],parent=path,
                                             token=token(key),testLeaves=LEAF_COUNT))
        html=render(title="Anonymous containing space",imprint="Publisher",books=entries,
                    css_url=SHELF_CSS,logo_url=None,logo_mode="unmarked",
                    cover_mode="unmarked",collection_title="Space",
                    collection_parent=BASE,collection_id=space,
                    parent_navigation="publisher-circle")
        where=OUT/"spaces"/space
        where.mkdir(parents=True,exist_ok=True)
        (where/"index.html").write_text(marked_document(html,position=position))
    root=render(title="Structural Bookshelf",imprint="Publisher",
                books=[],spaces=root_spaces,css_url=SHELF_CSS,logo_url=None,
                logo_mode="unmarked",cover_mode="unmarked",
                parent_navigation="publisher-circle")
    (OUT/"index.html").write_text(marked_document(root))
    (OUT/"fixture.json").write_text(json.dumps(graph,indent=2)+"\n")
    for file in OUT.rglob("index.html"):
        page=file.read_text()
        assert "<img" not in page and "data-asset-sha256" not in page
        assert "score" not in page.lower() and "essays" not in page.lower()
    print("SPATIAL_BOOKSHELF_BUILT",len(root_spaces),"spaces",
          len(graph["objects"]),"unique objects",len(graph["encounters"]),
          "membership encounters, zero source content")

if __name__=="__main__":
    main()
