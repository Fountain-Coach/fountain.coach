#!/usr/bin/env python3
"""Read-only proof of the essay-focused Linotype edition's source fidelity."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
def sha(b):return hashlib.sha256(b).hexdigest()
class Text(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.parts=[];self.feed(s)
 def handle_data(self,x):self.parts.append(x)
 def val(self):return "".join(self.parts)
def parts(s):return [Text(x).val() for x in re.findall(r'<p\b[^>]*>.*?</p>',s,re.S)]
def main():
 edition=json.loads((SITE/"essays/edition-manifest.json").read_text())
 assert edition["sourceRepository"]=="Fountain-Coach/fountain.coach"
 assert len(edition["essays"])==3
 assert edition["originalFigures"]==5
 reader=(SITE/"index.html").read_text()
 assert 'class="book-flow"' in reader
 assert 'id="book-viewport"' in reader
 assert 'data-legal-role="company-status"' in reader
 assert 'data-estate-id="status"' not in reader
 assert reader.count('data-book-chapter=')==3
 assert reader.count('src="/essays/')==5
 assert reader.count('data-book-toc-target=')==4
 assert '<a href="https://fountain.coach/essays/' in reader
 for i,item in enumerate(edition["essays"],1):
  src=SITE/item["sourcePath"];raw=src.read_bytes()
  assert sha(raw)==item["sourceSHA256"]
  s=raw.decode()
  original_prose=re.search(r'<div class="essay-prose">(.*?)</div>',s,re.S).group(1)
  lead=re.search(r'<p class="lead">(.*?)</p>',s,re.S).group(1)
  canonical=[Text('<p>'+lead+'</p>').val()]+parts(original_prose)
  assert sha(json.dumps(canonical,ensure_ascii=False).encode())==item["paragraphsSHA256"]
  slug=item["id"]
  start=reader.index('<section class="book-chapter" id="work-'+slug+'"')
  end=reader.find('<section class="book-chapter" id="work-',start+10)
  if end==-1:end=reader.index('<section class="book-end"',start)
  section=reader[start:end]
  transformed=[p for chunk in re.findall(r'<article class="book-prose">(.*?)</article>',section,re.S) for p in parts(chunk)]
  assert canonical==transformed,(slug,"Manuscript paragraphs altered")
  assert section.count('src="/essays/'+slug+'/')==item["originalFigures"]
  for image in item["images"]:
   assert sha((src.parent/image["path"]).read_bytes())==image["sha256"]
  print("ESSAY_VERBATIM",i,slug,len(canonical),"paragraphs",item["originalFigures"],"plates")
 inventory={}
 for line in (ROOT/"publication-files.sha256").read_text().splitlines():
  hashvalue,space,path=line.partition("  ")
  assert space and path not in inventory
  inventory[path]=hashvalue
 now={str(x.relative_to(SITE)):sha(x.read_bytes()) for x in SITE.rglob("*") if x.is_file()}
 assert now==inventory, "Complete site source inventory differs"
 print("FOUNTAIN_ESSAY_READER_ACCEPTED",len(edition["essays"]),"full essays",edition["originalFigures"],"original plates",len(inventory),"source files")
if __name__=="__main__":main()
