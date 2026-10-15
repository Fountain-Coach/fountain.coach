#!/usr/bin/env python3
"""Verify the complete author-owned Fountain Coach Linotype edition hierarchy."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
def sha(x):return hashlib.sha256(x).hexdigest()
class Text(HTMLParser):
 def __init__(self,html):super().__init__(convert_charrefs=True);self.data=[];self.feed(html)
 def handle_data(self,s):self.data.append(s)
 def value(self):return "".join(self.data)
def paragraphs(s):return [Text(x).value() for x in re.findall(r'<p\b[^>]*>.*?</p>',s,re.S)]
def essay_passages(reader,slug):
 start=reader.index('<section class="book-chapter" id="work-'+slug+'"')
 end=reader.find('<section class="book-chapter" id="work-',start+10)
 if end<0:end=reader.index('<section class="book-end"',start)
 chapter=reader[start:end]
 return chapter,[p for part in re.findall(r'<article class="book-prose">(.*?)</article>',chapter,re.S) for p in paragraphs(part)]

def check():
 catalogue=(SITE/"index.html").read_text()
 editions=(SITE/"editions/index.html").read_text()
 assert catalogue==editions,"Root must exactly mirror edition catalogue"
 assert 'data-linotype-state="bookshelf"' in catalogue
 assert 'class="bookshelf-paper"' in catalogue
 assert catalogue.count('class="shelf-item"')==3
 assert catalogue.count('class="shelf-cover"')==3
 assert catalogue.count('class="bookshelf-empty" aria-hidden="true"')==20
 assert catalogue.count('class="bookshelf-brand"')==1
 assert catalogue.count('class="shelf-book"')==3
 assert '<h1' not in catalogue and 'id="book-viewport"' not in catalogue
 assert 'class="instrument-slot"' not in catalogue
 assert 'class="bookshelf-wordmark"' not in catalogue
 assert 'class="shelf-miniature"' not in catalogue
 assert 'class="shelf-item-caption"' not in catalogue
 front={x['id']:x for x in json.loads((ROOT.parent/'estate/manifest.json').read_text())['frontDoors']}
 expected=[front['fountain-coach']['entryEditionUrl'],
           front['first-reading']['entryEditionUrl'],
           front['teatro']['url'].rstrip('/')+front['teatro']['firstHearing']['readerPath']]
 for href in expected:
  assert 'href="'+href+'"' in catalogue,href
 css=(SITE/'assets/linotype/bookshelf.css').read_bytes()
 assert css==(ROOT.parent.parent/'fountain-press/runtime/bookshelf.css').read_bytes()
 assert b'background:transparent;box-shadow:none;' in css
 detailed=(SITE/"editions/catalogue/index.html").read_text()
 assert 'class="edition-list"' in detailed
 assert '<h1>Editions<span>.</span></h1>' in detailed
 assert 'data-legal-role="company-status"' in detailed
 assert 'data-estate-id="status"' not in detailed
 for asset in ('fountain-coach-edition.png','first-reading-ink.png',
    'teatro-score-memory-vector-human-condition.svg'):
  assert (SITE/'assets/estate-bookshelf'/asset).is_file()
 assert sha((SITE/'assets/fountain-coach-logo-transparent.png').read_bytes()) == '8c5fad1c3db56138d5959da75991dc8034a0be537ce46da6ffcc0d9655e7f729'
 version=json.loads((SITE/"essays/edition-manifest.json").read_text())
 assert version["schema"]=="fountain.press.linotype.essay-edition.v2"
 assert version["sourceRepository"]=="Fountain-Coach/fountain.coach"
 assert version["cataloguePath"]=="editions/"
 assert version["editionPath"]=="editions/essays/"
 assert len(version["essays"])==len(version["subEditions"])==3
 assert version["originalFigures"]==5
 assert version["originalParagraphs"]==77
 main=(SITE/"editions/essays/index.html").read_text()
 assert main.count('data-book-chapter=')==3
 assert main.count('src="/essays/')==5
 assert main.count('data-book-toc-target=')==4
 assert 'data-legal-role="company-status"' in main
 assert 'class="edition-rail"' in main
 assert 'data-estate-id="status"' not in main
 assert 'id="book-viewport"' in main
 assert 'href="/editions/"' in main
 assert 'fountain.coach/editions/essays/' in main
 assert (SITE/"assets/linotype/book.js").read_text().count('document.body.dataset.editionId')==1
 for number,entry in enumerate(version["essays"],1):
  slug=entry["id"]
  source=SITE/entry["sourcePath"]
  raw=source.read_bytes()
  assert sha(raw)==entry["sourceSHA256"],slug
  prose=re.search(r'<div class="essay-prose">(.*?)</div>',raw.decode(),re.S).group(1)
  lead=re.search(r'<p class="lead">(.*?)</p>',raw.decode(),re.S).group(1)
  expected=[Text('<p>'+lead+'</p>').value()]+paragraphs(prose)
  assert sha(json.dumps(expected,ensure_ascii=False).encode())==entry["paragraphsSHA256"],slug
  for layout in ["editions/essays/index.html",entry["editionPath"]+"index.html"]:
   html=(SITE/layout).read_text()
   chapter,found=essay_passages(html,slug)
   assert expected==found,(slug,layout,"Verbatim paragraph mismatch")
   assert chapter.count('src="/essays/'+slug+'/')==entry["originalFigures"]
   assert 'href="https://fountain.coach/essays/'+slug+'/"' in chapter
   assert html.count('data-legal-role="company-status"')==1
  sub=(SITE/entry["editionPath"]/"index.html").read_text()
  assert sub.count('data-book-chapter=')==1
  assert sub.count('data-book-toc-target=')==2
  assert sub.count('src="/essays/')==entry["originalFigures"]
  assert 'data-edition-id="essays-'+slug+'"' in sub
  assert 'href="/editions/essays/"' in sub
  assert slug in version["readingOrder"]
  assert 'data-estate-id="status"' not in sub
  assert '<link rel="canonical" href="https://fountain.coach/editions/essays/'+slug+'/"' in sub
  assert 'href="/editions/essays/'+slug+'/"' in detailed
  for figure in entry["images"]:
   assert sha((source.parent/figure["path"]).read_bytes())==figure["sha256"]
  print("SOURCE_VERBATIM",number,slug,len(expected),"paragraphs",entry["originalFigures"],"original figures","independent-book")
 files={str(p.relative_to(SITE)):sha(p.read_bytes()) for p in SITE.rglob("*") if p.is_file()}
 registered={}
 for line in (ROOT/"publication-files.sha256").read_text().splitlines():
  digest,sep,name=line.partition("  ")
  assert sep and name not in registered
  registered[name]=digest
 assert registered==files,"Git source file inventory differs"
 obj=json.loads((ROOT/"edition.json").read_text())
 assert obj["fileCount"]==len(files)
 assert sha((ROOT/"publication-files.sha256").read_bytes())==obj["sourceSha256Inventory"]
 print("EDITION_HIERARCHY_ACCEPTED",len(version["essays"]),"full sub-editions",len(files),"tracked site files",version["originalParagraphs"],"original paragraphs")

if __name__=="__main__":check()
