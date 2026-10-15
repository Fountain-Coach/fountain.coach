#!/usr/bin/env python3
"""Verify the conceptual, name-free Bookshelf grammar."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"site/fixtures/semantic-visual-bookshelf"
BASE="/fixtures/semantic-visual-bookshelf/"
def digest(key):
    return hashlib.sha256(("structural-bookshelf:anonymous:"+key).encode()).hexdigest()
def check():
    g=json.loads((OUT/"fixture.json").read_text())
    assert g["schema"]=="fountain.press.spatial-bookshelf.fixture.v4"
    assert g["published"] is False
    assert g["source"].startswith("anonymous structural experiment")
    assert g["displayPolicy"]==dict(visibleImages=0,visibleText=0,sourceContent=False,
                                    coloredBy="containing-space-position",leafCount=3)
    assert [x["id"] for x in g["objects"]]==["o-01","o-02","o-03"]
    assert {x["id"]:x["token"] for x in g["objects"]}=={x:digest(x) for x in ("o-01","o-02","o-03")}
    assert [(x["id"],x["position"],x["members"]) for x in g["spaces"]]==[
        ("s-01",0,["o-01","o-02","o-03"]),
        ("s-02",1,["o-02"])]
    assert len(g["encounters"])==4
    root=(OUT/"index.html").read_text()
    assert root.count('class="shelf-space-item"')==2
    assert root.count('class="shelf-space"')==2
    assert root.count('class="shelf-book"')==0
    assert root.count('class="shelf-space-member"')==4
    assert root.count('class="shelf-space-vacancy"')==4
    assert root.count('class="bookshelf-empty"')==0
    assert 'data-space-ordinal="0"' in root and 'data-space-ordinal="1"' in root
    assert 'class="publisher-circle-return"' not in root
    assert root.count('class="bookshelf-brand fc-identity-circle"')==1
    for space in g["spaces"]:
        path=OUT/"spaces"/space["id"]/"index.html"
        html=path.read_text()
        assert 'data-space-position="'+str(space["position"])+'"' in html
        assert 'data-collection-id="'+space["id"]+'"' in html
        assert html.count('class="shelf-book"')==len(space["members"])
        assert html.count('class="bookshelf-empty"')==20
        assert 'class="publisher-circle-return" href="'+BASE+'"' in html
        assert 'bookshelf-collection-masthead"><a' not in html
        assert html.count('class="shelf-space-item"')==0
        for item in space["members"]:
            assert 'data-book-id="'+item+'"' in html
    for encounter in g["encounters"]:
        key=encounter["object"]
        space=encounter["space"]
        assert encounter["token"]==digest(key)
        assert encounter["parent"]==BASE+"spaces/"+space+"/"
        assert encounter["route"]==encounter["parent"]+"objects/"+key+"/"
        html=(ROOT/"site"/encounter["route"].lstrip("/")/"index.html").read_text()
        assert 'data-object-id="'+key+'"' in html
        assert 'data-space-id="'+space+'"' in html
        assert 'data-space-position="'+str(encounter["position"])+'"' in html
        assert 'data-object-token="'+digest(key)+'"' in html
        assert html.count('class="visual-page"')==3
        assert 'href="'+encounter["parent"]+'#work-'+key+'"' in html
        assert 'class="reader-context"' in html
        assert 'class="reader-parent-circle visual-return"' in html
        assert html.count('<li class="reader-member')==len(next(x for x in g["spaces"] if x["id"]==space)["members"])
        assert html.count('class="reader-member is-current"')==1
        assert 'class="reader-paper-assembly"' in html
        assert 'class="reader-focus"' in html
        assert 'data-transition="rest"' in html
        assert 'aria-label="Return to containing space"' in html
        assert '<a class="visual-return"' not in html
    assert sorted([x["space"] for x in g["encounters"] if x["object"]=="o-02"])==["s-01","s-02"]
    for file in OUT.rglob("index.html"):
        html=file.read_text().lower()
        for prohibited in ("<img","essays","teatro","score","first readings","work-cover"):
            assert prohibited not in html,(file,prohibited)
    assert not (OUT/"collections").exists()
    css=(OUT/"visual.css").read_text()
    assert "--scope-zero:#357f7d" in css and "--scope-one:#b66e48" in css
    assert ".structural-spaces-state .shelf-spaces" in css
    assert ".reader-context" in css and ".reader-members" in css
    assert ".reader-paper-assembly" in css
    assert ".visual-reader .visual-book-frame" in css
    assert "aspect-ratio:1 / 1.414" in css
    assert 'data-transition="settling"' in css
    assert '.visual-reader[data-space-position="0"]' in css
    reader_js=(OUT/"visual-reader.js").read_text()
    assert "DRAG_THRESHOLD=.34" in reader_js
    assert 'frame.dataset.transition="drag"' in reader_js
    assert 'history.pushState' in reader_js
    assert 'matchMedia("(prefers-reduced-motion: reduce)")' in reader_js
    print("SPATIAL_BOOKSHELF_PASS 2 containing fields 3 anonymous books 4 memberships; color follows scope, no names or artwork")
if __name__=="__main__":check()
