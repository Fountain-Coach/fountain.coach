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
 assert catalogue.count('class="shelf-item"')==2
 assert catalogue.count('class="shelf-cover"')==2
 assert catalogue.count('class="bookshelf-empty" aria-hidden="true"')==20
 assert catalogue.count('class="bookshelf-brand fc-identity-circle"')==1
 assert '@import url("./identity-circle.css")' in (SITE/'assets/linotype/bookshelf.css').read_text()
 assert (SITE/'assets/linotype/identity-circle.css').read_bytes()==(ROOT.parent.parent/'fountain-press/runtime/identity-circle.css').read_bytes()
 assert catalogue.count('class="shelf-book"')==2
 assert 'data-preview-host="teatro"' not in catalogue
 assert '<h1' not in catalogue and 'id="book-viewport"' not in catalogue
 assert 'class="instrument-slot"' not in catalogue
 assert 'class="bookshelf-wordmark"' not in catalogue
 assert 'class="shelf-miniature"' not in catalogue
 # Original books remain the same; supporting editorial navigation is not a cover.
 assert catalogue.count('class="bookshelf-pathways"') == 1
 for path in ('/essays/', '/essays/the-ear-that-learns/', 'https://instruments.fountain.coach/'):
  assert 'href="' + path + '"' in catalogue
 assert (SITE/'assets/essay-pathways.css').is_file()
 article=(SITE/'essays/the-ear-that-learns/index.html').read_text()
 assert '<h1>The Ear That Learns</h1>' in article
 assert 'href="https://instruments.fountain.coach/#ear"' in article
 assert 'href="https://instruments.fountain.coach/#sing"' in article
 assert article.count('<h2>') >= 5
 gallery=(SITE/'essays/index.html').read_text()
 assert gallery.count('data-essay-route="/essays/the-ear-that-learns/"') == 1
 assert gallery.count('href="/essays/the-ear-that-learns/"') >= 2
 assert 'class="shelf-item-caption"' not in catalogue
 front={x['id']:x for x in json.loads((ROOT.parent/'estate/manifest.json').read_text())['frontDoors']}
 expected=[front['fountain-coach']['entryEditionUrl'],
           front['first-reading']['collectionUrl'],
           ]
 for href in expected:
  assert 'href="'+href+'"' in catalogue,href
 css=(SITE/'assets/linotype/bookshelf.css').read_bytes()
 assert css==(ROOT.parent.parent/'fountain-press/runtime/bookshelf.css').read_bytes()
 assert b'background:transparent;box-shadow:none;' in css
 collection=(SITE/'collections/first-readings/index.html').read_text()
 identity=json.loads((SITE/'collections/first-readings/collection.json').read_text())
 assert identity['schema']=='fountain.press.collection.v1'
 assert identity['identity']=='first-readings' and identity['workCount']==1
 assert identity['works'][0]['workId']=='teatro-an-unfinished-composition'
 assert collection.count('class="shelf-book"')==1 and collection.count('class="shelf-cover"')==1
 assert collection.count('class="bookshelf-empty" aria-hidden="true"')==20
 assert '<h1>First Readings</h1>' in collection
 assert 'href="/" aria-label="Return to Fountain Coach bookshelf"' in collection
 assert 'href="https://fountain.coach/editions/essays/teatro-an-unfinished-composition/"' in collection
 assert 'data-book-id="teatro-an-unfinished-composition"' in collection
 assert identity['works'][0]['coverArtworkSHA256']==sha((SITE/identity['works'][0]['coverArtwork'].lstrip('/')).read_bytes())
 work=(SITE/'editions/essays/teatro-an-unfinished-composition/index.html').read_text()
 assert 'class="book-cover work-identity-cover"' in work
 assert work.count('src="'+identity['works'][0]['coverArtwork']+'"')==1
 assert identity['works'][0]['coverArtwork'] in (SITE/'assets/linotype/essays.css').read_text()
 assert 'href="/collections/first-readings/#work-teatro-an-unfinished-composition"' in work
 assert 'aria-label="Return to First Readings collection"' in work
 assert 'data-edition-entry-anchor="book-cover"' in work
 assert 'body.dataset.editionEntryAnchor||prefs.anchor' in (SITE/'assets/linotype/book.js').read_text()
 assert '(hash||body.dataset.editionEntryAnchor)?0:' in (SITE/'assets/linotype/book.js').read_text()
 assert identity['singularFirstReadingPreserved'] == front['first-reading']['entryEditionUrl']
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
 assert 'id="book-type-button"' not in main
 css=(SITE/'assets/linotype/essays.css').read_text()
 assert '.book-legal{grid-column:1/-1;grid-row:2;' in css
 assert 'body.book-app.reader-ready .book-pagination{height:90px;' in css
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
  if slug=='teatro-an-unfinished-composition':
   assert '<p class="book-ordinal">FIRST READINGS<span>THE CONDITION</span></p>' in sub
   assert '<p class="book-ordinal">THE CONDITION<span>01 / 03</span></p>' not in sub
   assert '<p>FIRST READINGS</p><h2>End of reading.</h2>' in sub
   assert 'href="/collections/first-readings/#work-teatro-an-unfinished-composition"' in sub
  else:
   assert 'href="/editions/essays/"' in sub
  assert 'id="book-type-button"' not in sub
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
