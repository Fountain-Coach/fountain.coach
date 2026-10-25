#!/usr/bin/env python3
"""Test the source-owned essay route, source evidence, PDF, and original collection."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,subprocess
root=Path(__file__).resolve().parents[1]
site=root/"site"
slug="to-read-is-not-to-remember"
page=site/"essays"/slug
h=(page/"index.html").read_text()
collection=(site/"essays/index.html").read_text()
intro=(page/"editorial-introduction.md").read_text()
render=subprocess.run(["pandoc","--from=markdown+smart","--to=html5","--wrap=none"],input=intro,text=True,capture_output=True,check=True).stdout
assert render in h,"Published editorial must be exact source Markdown projection"
assert collection.count('data-essay-route="/essays/'+slug+'/"')==1
assert collection.count('class="essay-gallery-card"')==5
assert collection.count('data-essay-route="/essays/the-ear-that-learns/"')==1
assert h.count('<object class="pdf-frame"')==1
assert h.count('href="to-read-is-not-to-remember.pdf"')==3
assert '<meta property="og:image:alt"' in h and 'application/ld+json' in h
assert 'not evidence that a model understood a book' in h
assert 'essays/to-read-is-not-to-remember/' in h
assert h.count('data-legal-role="company-status"')==1
p=page/"to-read-is-not-to-remember.pdf"
assert p.read_bytes().startswith(b"%PDF-") and p.stat().st_size>200000
orig=site/"essays"/slug/"source.md"
assert orig.read_text().startswith("---\ntitle:")
img=page/"assets/bookshelf-ipad-landscape-test.png"
qa=root/"docs/qa/first-readings-v38/ipad-landscape-estate.png"
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(img)==sha(qa)
entries={}
for line in (root/"publication-files.sha256").read_text().splitlines():
    digest,_,name=line.partition("  ");assert name not in entries;entries[name]=digest
actual={str(x.relative_to(site)):sha(x) for x in site.rglob("*") if x.is_file()}
assert entries==actual, "Publication file hashes do not match owning source"
manifest=json.loads((root/"edition.json").read_text())
assert manifest["fileCount"]==len(actual)
assert manifest["indexPages"]==len(list(site.rglob("index.html")))
assert manifest["sourceSha256Inventory"]==hashlib.sha256((root/"publication-files.sha256").read_bytes()).hexdigest()
print("READING_CONTINUITY_ESSAY_ACCEPTED",slug,"pdf_sha256",sha(p),"qa_image_sha256",sha(img),"site_files",len(actual))
