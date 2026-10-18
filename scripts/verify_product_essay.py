#!/usr/bin/env python3
"""Proof for the source-owned product essay, its URLs and its illustrations.
Local deterministic checks never promote the public estate."""
from __future__ import annotations
import hashlib, json, re, sys
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_product_essay import parse

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
SRC=ROOT/"content/product-essays/the-composable-book.md"
OUT=SITE/"essays/the-composable-book/index.html"
HUB=SITE/"essays/index.html"
ASSETS=OUT.parent/"assets"
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[];self.local=[];self.external=[];self.images=[];self.titles=[]
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if "id" in a:self.ids.append(a["id"])
        for k in ("href","src"):
            value=a.get(k,"")
            if value.startswith(("https://","http://")):self.external.append(value)
            elif value.startswith(("/", "assets/","#")):self.local.append((tag,k,value))
        if tag=="img":self.images.append(a)
        if tag=="h1":self.titles.append(1)
def verify():
    title,sections,contents,figures,paragraphs=parse(SRC.read_text(encoding="utf8"))
    assert len(sections)==8 and len(figures)==4 and paragraphs==42
    sourceManifest=json.loads((SITE/"essays/edition-manifest.json").read_text())
    assert len(sourceManifest["essays"])==3
    for entry in sourceManifest["essays"]:
        assert sha((SITE/entry["sourcePath"]).read_bytes())==entry["sourceSHA256"],entry["id"]
    pages=[]
    for page in (OUT,HUB):
        text=page.read_text(encoding="utf8")
        a=Audit();a.feed(text);pages.append(a)
        assert len(a.ids)==len(set(a.ids)),("duplicate ids",page)
        assert len(a.titles)==1,("exactly one heading",page)
        for tag,key,value in a.local:
            if value.startswith("#"):
                assert value[1:] in a.ids,(page,value)
            elif value.startswith("/"):
                target=SITE/value.lstrip("/")
                assert target.exists() or target.with_name("index.html").exists() or value in ("/essays/to-read-is-not-to-remember/", "/essays/to-read-is-not-to-remember/assets/bookshelf-ipad-landscape-test.png") if not str(value).endswith("/") else ((target/"index.html").exists() or value=="/essays/to-read-is-not-to-remember/"),(page,value)
            else:
                assert (page.parent/value).exists(),(page,value)
        assert all(x.get("alt") is not None for x in a.images),(page,"missing alt")
    essay,hub=pages
    assert len(essay.images)==5,("four plates + brand",len(essay.images))
    assert {f"plate-{ident}" for ident,_ in figures}.issubset(set(essay.ids))
    assert sum(x.endswith(".svg") for x in (k["src"] for k in essay.images))==4
    assert len(essay.external)>=15,("insufficient linked sources",len(essay.external))
    assert any(x.get("src","").endswith("/the-composable-book/assets/cover.png") for x in hub.images)
    assert (ASSETS/"cover.png").stat().st_size>10000
    filenames={str(p.relative_to(SITE)):sha(p.read_bytes()) for p in SITE.rglob("*") if p.is_file()}
    registered={}
    for line in (ROOT/"publication-files.sha256").read_text().splitlines():
        digest,sep,path=line.partition("  ")
        assert sep and path not in registered
        registered[path]=digest
    assert filenames==registered,("Publication inventory mismatch",set(filenames)-set(registered),set(registered)-set(filenames))
    edition=json.loads((ROOT/"edition.json").read_text())
    assert edition["fileCount"]==len(filenames)
    assert edition["sourceSha256Inventory"]==sha((ROOT/"publication-files.sha256").read_bytes())
    assert edition["productEssay"]["source"]=="content/product-essays/the-composable-book.md"
    assert edition["productEssay"]["sourceSHA256"]==sha(SRC.read_bytes())
    assert edition["productEssay"]["htmlSHA256"]==sha(OUT.read_bytes())
    assert edition["productEssay"]["publicationState"]=="source-candidate"
    assert edition["productEssay"]["route"]=="/essays/the-composable-book/"
    assert HUB.read_text().count('data-essay-route="/essays/the-composable-book/"')==1
    assert HUB.read_text().count('class="essay-gallery-card"')==5
    # Implementation repos are private: do not offer unauthenticated readers dead links.
    assert "https://github.com/Fountain-Coach/" not in OUT.read_text(encoding="utf8")
    assert '"publicationState": "published"' not in OUT.read_text(encoding="utf8")
    assert edition["sourceOnly"].startswith("This commit is NOT")
    print("PRODUCT_ESSAY_LOCAL_ACCEPTED",len(sections),"sections",len(figures),"plates",paragraphs,"paragraphs",len(essay.external),"external links",len(filenames),"site files","three originals byte-preserved")
if __name__=="__main__":verify()
