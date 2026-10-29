#!/usr/bin/env python3
"""Compile a complete static source-owned reader-first entrance and retain
the previous author-led editorial home as an explicitly alternate scenario."""
from pathlib import Path
from bs4 import BeautifulSoup
import copy
root=Path(__file__).resolve().parents[1]
site=root/"site"
original=site/"index.html"
reader=site/"scenarios/reader-first/index.html"
alternative=site/"scenarios/author-led/index.html"
if not alternative.exists():
    alternative.parent.mkdir(parents=True,exist_ok=True)
    alternative.write_bytes(original.read_bytes())
existing=BeautifulSoup(alternative.read_text(),"html.parser")
soup=BeautifulSoup(reader.read_text(),"html.parser")
# Re-running the source build is idempotent: replace the prior borrowed
# Publication Core, never nest two headers/footers.
for prior in list(soup.select("header.site-header,footer.footer,meta[name='fountain:publication-role']")):
    prior.decompose()
header=existing.select_one("header.site-header")
footer=existing.select_one("footer.footer")
assert header and footer
# The editor-approved Fountain Coach Publication Core is source-owned.
soup.body.insert(1,copy.deepcopy(header))
soup.body.append(copy.deepcopy(footer))
meta=soup.new_tag("meta")
meta["name"]="fountain:publication-role"
meta["content"]="writer-approved reader-first living Essays edition"
soup.head.append(meta)
if not soup.head.select_one('link[rel="icon"]'):
    soup.head.append(soup.new_tag("link",attrs={"rel":"icon","href":"/assets/fountain-coach-logo-transparent.png"}))
# This source is a candidate; its canonical already identifies the parent.
soup.select_one('meta[name="robots"]')["content"]="noindex,nofollow"
# Link original fully authored works explicitly rather than substituting
# the book's flattened media exhibits for their own published routes.
assert len(soup.select('.book-chapter[data-book-chapter]'))==7
assert soup.body["data-edition-entry-anchor"]=="work-the-door-is-a-score"
result=str(soup).rstrip()+"\n"
original.write_text(result)
reader.write_text(result)
print("SOURCE_READER_FIRST_ENTRY",original,len(result),"alternate",alternative)
