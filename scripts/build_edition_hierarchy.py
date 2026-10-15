#!/usr/bin/env python3
"""Build the edition catalogue, the essay edition and its three sub-editions.

Only published, author-owned text from site/essays is admitted. The old
First Reading typesetter is consumed as a pinned dependency by the existing
source builder. No network, generated prose, deployment or Git mutation.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
BOOK=SITE/"editions/essays"
ED=SITE/"editions"
ORIGINAL=SITE/"essays/edition-manifest.json"
MAIN=SITE/"index.html"
FIRST="https://works.benedikt-eickhoff.de/solstice/editions/first-reading/"
TEATRO="https://teatro.fountain.coach/"
FOUNTAIN="https://fountain.coach/editions/essays/"
LABELS=["THE CONDITION","THE EDITION","THE ESTATE"]
NAV='<nav class="edition-rail" aria-label="Estate editions"><a data-estate-id="estate" href="/editions/essays/" aria-current="page" title="Fountain Coach essays">Fountain Coach</a><a data-estate-id="first-reading" href="'+FIRST+'" title="First Reading">First Reading</a><a data-estate-id="teatro" href="'+TEATRO+'" title="Teatro">Teatro</a></nav>'

def sha(data):return hashlib.sha256(data).hexdigest()
def anchor(label,url,extra=""):
 return '<a '+extra+' href="'+escape(url,quote=True)+'">'+escape(label)+'</a>'
def format_reader(source,canonical,title,edition_id,back_url,back_label,selected=None):
 result=source
 result=result.replace('href="/essays/" aria-label="Original Fountain Coach essay source"',
                       'href="'+back_url+'" aria-label="Back to '+escape(back_label,quote=True)+'"')
 result=result.replace('<span>Source Essays</span></a>','<span>'+escape(back_label)+'</span></a>')
 result=result.replace('href="/essays/">Original publications →','href="'+back_url+'">Back to '+escape(back_label)+' →')
 result=result.replace('<div class="book-identity"><span class="book-symbol" aria-hidden="true">✳</span><span>FOUNTAIN COACH · ESSAYS</span></div>',
                       NAV)
 assert 'class="edition-rail"' in result
 result=result.replace('<body class="book-app">','<body class="book-app" data-edition-id="'+edition_id+'">')
 result=result.replace('<link rel="canonical" href="https://fountain.coach/">',
                       '<link rel="canonical" href="'+canonical+'">')
 result=result.replace('<title>Fountain Coach — Essays</title>', '<title>'+escape(title)+'</title>')
 if selected:
  # This sub-edition is a *complete independent book*, not a link into
  # the master reader or an extracted quote.
  cover_start=result.index('<div id="book-flow" class="book-flow">')+len('<div id="book-flow" class="book-flow">')
  cover_end=result.index('  <aside id="book-page-atlas"')
  # Four closing containers are identical to the admitted First Reading.
  chunks=selected["chapter"]
  if selected["id"]=="teatro-an-unfinished-composition":
   # The standalone First Readings work must not inherit omnibus numbering.
   old_ordinal='<p class="book-ordinal">THE CONDITION<span>01 / 03</span></p>'
   assert chunks.count(old_ordinal)==1
   chunks=chunks.replace(old_ordinal,'<p class="book-ordinal">FIRST READINGS<span>THE CONDITION</span></p>',1)
  subcover='<section class="book-cover" id="book-cover" aria-label="'+escape(selected["title"],quote=True)+'"><div class="book-cover-top"><span>FOUNTAIN COACH</span><span>ESSAYS · SUB-EDITION '+str(selected["number"]).zfill(2)+'</span></div><div class="book-cover-center"><span class="cover-mark" aria-hidden="true">✳</span><p class="book-imprint">'+escape(selected["label"])+'</p><h1 class="subedition-title">'+escape(selected["title"])+'</h1><p class="book-cover-subtitle">Benedikt Eickhoff</p></div><p class="book-cover-foot">COMPLETE ORIGINAL ESSAY · '+str(selected["figureCount"])+' ORIGINAL PLATE'+('S' if selected["figureCount"]!=1 else '')+'<br><a href="/editions/essays/">All essays →</a></p></section>'
  if selected["id"]=="teatro-an-unfinished-composition":
   # Cover art is a source-attested editorial projection. The work is the
   # publication; the Teatro instrument and its Score are not the book ID.
   art='/essays/teatro-an-unfinished-composition/assets/teatro-score-memory-vector-human-condition.svg'
   subcover=subcover.replace('class="book-cover"','class="book-cover work-identity-cover"',1)
   subcover=subcover.replace('<span class="cover-mark" aria-hidden="true">✳</span>',
        '<span class="cover-mark work-cover-art" aria-hidden="true"></span>',1)
   subcover=subcover.replace('ESSAYS · SUB-EDITION 01','FIRST READINGS',1)
   subcover=subcover.replace('<p class="book-imprint">THE CONDITION</p>',
        '<p class="book-imprint">FIRST READINGS · AUTHORED WORK</p>',1)
   subcover=subcover.replace('<a href="/editions/essays/">All essays →</a>',
        '<a href="/collections/first-readings/#work-teatro-an-unfinished-composition" aria-label="Return to First Readings collection">← FIRST READINGS</a>',1)
  end='<section class="book-end" id="book-end"><span class="cover-mark" aria-hidden="true">✳</span><p>FOUNTAIN COACH · ESSAYS</p><h2>End of essay.</h2><a href="/editions/essays/">All three essays →</a></section>'
  if selected["id"]=="teatro-an-unfinished-composition":
   end='<section class="book-end" id="book-end"><p>FIRST READINGS</p><h2>End of reading.</h2><a href="/collections/first-readings/#work-teatro-an-unfinished-composition">Return to the collection →</a></section>'
  content=subcover+'\n'+chunks+'\n'+end+'\n'
  result=result[:cover_start]+content+'</div>\n</div>\n</div>\n'+result[cover_end:]
  if selected['id']=='teatro-an-unfinished-composition':
   result=result.replace('data-edition-id="essays-teatro-an-unfinished-composition"',
      'data-edition-id="essays-teatro-an-unfinished-composition" data-edition-entry-anchor="book-cover"',1)
   assert result.count('id="book-flow"')==1
   result=result.replace(NAV,'<div class="work-reading-identity" aria-label="Current publication">FIRST READINGS · AN UNFINISHED COMPOSITION</div>',1)
   assert 'class="edition-rail"' not in result
  toc='<nav aria-label="Chapters"><ol class="book-toc-list"><li><a data-book-toc-target="cover" href="#book-cover"><span class="toc-number">·</span><span class="toc-title">Cover</span></a></li><li><a data-book-toc-target="'+selected["id"]+'" href="#work-'+selected["id"]+'"><span class="toc-number">'+str(selected["number"]).zfill(2)+'</span><span class="toc-title">'+escape(selected["title"])+'</span></a></li></ol></nav>'
  result,n=re.subn(r'<nav aria-label="Chapters"><ol class="book-toc-list">.*?</ol></nav>',lambda _:toc,result,flags=re.S)
  assert n==1
  result=result.replace('<span>FOUNTAIN COACH · ESSAYS</span></div>','<span>FOUNTAIN COACH · '+escape(selected["label"])+'</span></div>')
 else:
  # The full omnibus remains its own book with chapter-level addresses.
  result=result.replace('<a data-estate-id="first-reading" href="'+FIRST+'">First Reading →</a> · <a data-estate-id="teatro" href="'+TEATRO+'">Teatro →</a>',
                        '<a href="/editions/">Editions catalogue →</a>')
 assert result.count('id="book-viewport"')==1
 return result

def build_catalogue(manifest):
 cards=[]
 essay_cover="/essays/teatro-an-unfinished-composition/assets/teatro-score-memory-vector-human-condition.svg"
 nested=''.join('<li><a href="/editions/essays/'+a["id"]+'/"><span>'+str(i).zfill(2)+'</span><span>'+escape(a["title"])+'</span><span aria-hidden="true">↗</span></a></li>'
                for i,a in enumerate(manifest["essays"],1))
 cards.append('''<article class="edition-item edition-primary" data-edition-id="essays">
  <div class="edition-meta"><span>01 / FOUNTAIN COACH</span><span>EDITED ESSAYS</span></div>
  <div class="edition-content"><figure class="edition-cover"><a href="/editions/essays/" aria-label="Read the Fountain Coach essay edition"><img src="'''+essay_cover+'''" alt="Original Teatro Score: Human Condition"></a></figure>
  <div class="edition-copy"><small>WRITING · PERFORMANCE · PUBLISHING</small><h2>Essays<span>.</span></h2>
  <p>Three complete essays. Their original words and five illustrations, typeset as one reading and available as three separate editions.</p>
  <p><a class="edition-open" href="/editions/essays/">Read the edition <span aria-hidden="true">→</span></a></p>
  <div class="edition-sublist"><h3>Inside this edition</h3><ol>'''+nested+'''</ol></div></div></div></article>''')
 cards.append('''<article class="edition-item" data-edition-id="first-reading"><div class="edition-meta"><span>02 / FIRST READING</span><span>AN AUTHORED EDITION</span></div>
  <div class="edition-content"><div class="edition-bookmark"><span class="edition-mark" aria-hidden="true">✳</span><span>SOLSTICE</span></div><div class="edition-copy">
  <small>LINOTYPE · LITERATURE</small><h2>First Reading<span>.</span></h2>
  <p>Thirty complete literary works and their original images. The separately authored Solstice reading edition.</p>
  <p><a class="edition-open" data-estate-id="first-reading" href="'''+FIRST+'''">Open First Reading <span aria-hidden="true">→</span></a></p></div></div></article>''')
 cards.append('''<article class="edition-item" data-edition-id="teatro"><div class="edition-meta"><span>03 / TEATRO</span><span>PERFORMANCE EDITION</span></div>
  <div class="edition-content"><div class="edition-bookmark edition-theatre"><span class="edition-mark" aria-hidden="true">◇</span><span>TEATRO</span></div><div class="edition-copy">
  <small>STAGE · SOUND · SCORE</small><h2>Teatro<span>.</span></h2>
  <p>The performance and listening domain. Its live score surface is a different medium from a finished literary manuscript.</p>
  <p><a class="edition-open" data-estate-id="teatro" href="'''+TEATRO+'''">Enter Teatro <span aria-hidden="true">→</span></a></p></div></div></article>''')
 navigation='<nav class="estate-nav edition-global-nav" aria-label="Estate editions"><a data-estate-id="estate" href="/editions/essays/">Fountain Coach</a><a data-estate-id="first-reading" href="'+FIRST+'">First Reading</a><a data-estate-id="teatro" href="'+TEATRO+'">Teatro</a></nav>'
 return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="robots" content="noindex,nofollow">
 <meta name="description" content="Fountain Coach editions: published essays, First Reading, and Teatro.">
 <meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
 <link rel="canonical" href="https://fountain.coach/editions/"><link rel="stylesheet" href="/assets/editions.css"><title>Editions — Fountain Coach</title></head>
 <body class="editions-catalogue"><header class="catalogue-header"><div class="catalogue-eyebrow"><a href="/editions/">FOUNTAIN COACH</a><span>PUBLICATIONS / EDITIONS</span></div>'''+navigation+'''</header>
 <main id="editions" class="catalogue-main"><section class="catalogue-intro"><p>FOUNTAIN COACH · THE ESTATE</p><h1>Editions<span>.</span></h1>
 <div class="catalogue-intro-line"><p>Writing in editions. Each edition has its own address; an edition may contain further editions.</p><span>THREE FRONT DOORS</span></div></section>
 <section class="edition-list" aria-label="Current editions">'''+''.join(cards)+'''</section></main>
 <footer class="catalogue-footer"><p>FOUNTAIN COACH · BENEDIKT EICKHOFF · BERLIN</p><nav aria-label="References and legal notices">
 <a href="/essays/">Original essay sources</a> · <a href="https://governance.fountain.coach/">Governance</a> ·
 <a href="https://midi2.fountain.coach/">MIDI2</a> · <a href="https://status.fountain.coach/" data-legal-role="company-status">Company status &amp; transparency</a> ·
 <a href="https://governance.fountain.coach/legal/">Legal notices</a> · <a href="https://governance.fountain.coach/privacy/">Privacy</a></nav></footer></body></html>
 '''

def build_first_readings_collection(version):
    """An identifiable collection of admitted works, not a Teatro instrument."""
    import shutil
    press=ROOT.parent.parent/'fountain-press/runtime'
    sys.path.insert(0,str(press))
    from bookshelf import render_bookshelf
    asset='/essays/teatro-an-unfinished-composition/assets/teatro-score-memory-vector-human-condition.svg'
    image=SITE/asset.lstrip('/')
    entry=next(x for x in version['essays'] if x['id']=='teatro-an-unfinished-composition')
    assert hashlib.sha256(image.read_bytes()).hexdigest()==entry['images'][0]['sha256']
    assert len([x for x in version['essays'] if x['id']=='teatro-an-unfinished-composition'])==1
    destination='https://fountain.coach/'+entry['editionPath']
    collection=SITE/'collections/first-readings';collection.mkdir(parents=True,exist_ok=True)
    collection_book=dict(id=entry['id'],title=entry['title'],author='Benedikt Eickhoff',
       edition='First Readings — source-authenticated work',reader=destination,cover_image=asset,
       source_revision=entry['sourceSHA256'],
       host='fountain',status='wlan-proof',cover_title='An Unfinished Composition')
    rendered=render_bookshelf(title='First Readings',imprint='First Readings',
       books=[collection_book],css_url='/assets/linotype/bookshelf.css',
       logo_url='/assets/fountain-coach-logo-transparent.png',
       collection_title='First Readings',collection_parent='/')
    (collection/'index.html').write_text(rendered)
    manifest=dict(schema='fountain.press.collection.v1',identity='first-readings',
       title='First Readings',publisher='Fountain-Coach/fountain.coach',
       canonical='https://fountain.coach/collections/first-readings/',
       sourceStatus='WLAN editorial candidate',coverAsset='/assets/estate-bookshelf/first-reading-ink.png',
       workCount=1,works=[dict(workId=entry['id'],title=entry['title'],editionPath=entry['editionPath'],
        coverArtwork=asset,coverArtworkSHA256=entry['images'][0]['sha256'],
        sourceSHA256=entry['sourceSHA256'],sourceParagraphs=entry['originalParagraphs'])],
       singularFirstReadingPreserved='https://works.benedikt-eickhoff.de/solstice/editions/first-reading/',
       hearingStatus='no First Hearings publication admitted')
    (collection/'collection.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    return manifest

def build_estate_grid():
    """Project the estate manifest through Fountain Press, not a second UI.

    Edition routes live in the Git-owned estate registry. The three cover
    images are locally admitted, source-owned assets, not generated art.
    """
    import shutil
    from urllib.parse import urljoin

    estate = json.loads((ROOT.parent / "estate/manifest.json").read_text())
    fronts = sorted(estate["frontDoors"], key=lambda item: item["rank"])
    assert [item["id"] for item in fronts] == ["fountain-coach", "first-reading", "teatro"]
    press = ROOT.parent.parent / "fountain-press/runtime"
    assert (press / "bookshelf.py").is_file() and (press / "bookshelf.css").is_file()
    sys.path.insert(0, str(press))
    from bookshelf import render_bookshelf

    css = SITE / "assets/linotype/bookshelf.css"
    css.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(press / "bookshelf.css", css)
    shutil.copyfile(press / "identity-circle.css", css.parent / "identity-circle.css")
    assert "background:transparent;box-shadow:none;" in css.read_text()
    artworks = {
        "fountain-coach": "fountain-coach-edition.png",
        "first-reading": "first-reading-ink.png",
        "teatro": "teatro-score-memory-vector-human-condition.svg",
    }
    identities = {
        "fountain-coach": ("Fountain Coach", "FOUNTAIN COACH · ESSAYS", "fountain", "wlan-proof"),
        "first-reading": ("First Readings", "FIRST READINGS · COLLECTION", "fountain", "wlan-proof"),
        "teatro": ("Teatro — First Hearing", "TEATRO · FIRST HEARING", "teatro", "wlan-proof"),
    }
    # Teatro belongs to the tool estate, not a bookshelf publication.
    visible=[f for f in fronts if f['id'] in estate['publishingShelves']['topLevelCollectionIds']]
    assert [f['id'] for f in visible]==['fountain-coach','first-reading']
    assert not next(f for f in fronts if f['id']=='teatro')['publishingShelfVisible']
    books = []
    for front in visible:
        identity = front["id"]
        title, edition, host, status = identities[identity]
        if identity == "teatro":
            # The edition opens its book, not another bookshelf at Teatro /.
            reader = urljoin(front["url"], front["firstHearing"]["readerPath"].lstrip("/"))
        elif identity == "first-reading":
            reader = front["collectionUrl"]
            assert front["collectionSourceRepo"]=="Fountain-Coach/fountain.coach"
        else:
            reader = front["entryEditionUrl"]
        art = "/assets/estate-bookshelf/" + artworks[identity]
        assert (SITE / art.lstrip("/")).is_file(), art
        # A cover binds to its actual publication/collection content, not a
        # changing Git HEAD or a machine-dependent staging build revision.
        admitted=(SITE/'collections/first-readings/collection.json' if identity=='first-reading'
                  else SITE/'essays/edition-manifest.json')
        revision=sha(admitted.read_bytes())
        books.append(dict(id=identity, title=title, author="Benedikt Eickhoff",
                          edition=edition, reader=reader, cover_image=art,
                          cover_title=('First Readings' if identity=='first-reading' else 'Essays'),
                          source_revision=revision, host=host, status=status))
    return render_bookshelf(title="Fountain Coach", imprint="Fountain Coach",
                            books=books, css_url="/assets/linotype/bookshelf.css",
                            logo_url="/assets/fountain-coach-logo-transparent.png")

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--linotype-source",type=Path,required=True)
 args=parser.parse_args()
 builder=ROOT/"scripts/build_essay_edition.py"
 subprocess.run([sys.executable,str(builder),"--linotype-source",str(args.linotype_source)],check=True)
 book=MAIN.read_text()
 version=json.loads(ORIGINAL.read_text())
 # The first step creates the edition at site/index.html. Move into its
 # actual versioned path before writing the editions catalogue.
 BOOK.mkdir(parents=True,exist_ok=True)
 full=format_reader(book,"https://fountain.coach/editions/essays/",
                    "Fountain Coach — Essays","essays","/editions/","Editions")
 (BOOK/"index.html").write_text(full)
 units=re.findall(r'(<section class="book-chapter" id="work-[\s\S]*?)(?=<section class="book-chapter" id="work-|<section class="book-end")',full)
 assert len(units)==3,len(units)
 for i,entry in enumerate(version["essays"]):
  leaf=dict(id=entry["id"],title=entry["title"],label=LABELS[i],
            number=i+1,figureCount=entry["originalFigures"],chapter=units[i])
  target=BOOK/entry["id"]
  target.mkdir(exist_ok=True)
  parent='/collections/first-readings/' if entry['id']=='teatro-an-unfinished-composition' else '/editions/essays/'
  parent_label='First Readings' if entry['id']=='teatro-an-unfinished-composition' else 'Essays'
  stand=format_reader(book,"https://fountain.coach/editions/essays/"+entry["id"]+"/",
                    "Fountain Coach — "+entry["title"],
                    "essays-"+entry["id"],parent,parent_label,selected=leaf)
  (target/"index.html").write_text(stand)
  entry["editionPath"]="editions/essays/"+entry["id"]+"/"
  entry["parentEdition"]="editions/essays/"
 # Update reader JS storage by edition address, so locations in three
 # sub-editions never collide with the master reader.
 p=SITE/"assets/linotype/book.js";js=p.read_text()
 old='const STORAGE="fountain.essays.linotype.v1";'
 new='const STORAGE="fountain.essays.linotype.v1."+(document.body.dataset.editionId||"essays");'
 assert old in js
 js=js.replace(old,new)
 old_entry='const requested=hash&&document.getElementById(hash)?hash:prefs.anchor||"book-cover";'
 new_entry='const requested=hash&&document.getElementById(hash)?hash:(body.dataset.editionEntryAnchor||prefs.anchor||"book-cover");'
 assert js.count(old_entry)==1
 js=js.replace(old_entry,new_entry)
 old_offset='compose({anchor:requested,offset:hash?0:Number(prefs.pageWithin)||0});'
 new_offset='compose({anchor:requested,offset:(hash||body.dataset.editionEntryAnchor)?0:Number(prefs.pageWithin)||0});'
 assert js.count(old_offset)==1
 js=js.replace(old_offset,new_offset)
 p.write_text(js)
 runtime=next(x for x in version["runtime"] if x["file"]=="book.js")
 runtime["projectedSHA256"]=sha(p.read_bytes())
 style=SITE/"assets/linotype/essays.css"
 with style.open("a") as out:
  out.write("""
.edition-rail{display:flex;align-items:center;justify-content:center;gap:clamp(5px,1.2vw,16px);font:600 10px/1.5 ui-monospace,Menlo,monospace;white-space:nowrap}
.edition-rail a{text-decoration:none;color:var(--book-muted);border-bottom:1px solid transparent}
.edition-rail a[aria-current="page"]{color:var(--book-ink);border-color:var(--book-ink)}
.book-cover h1.subedition-title{font-size:clamp(29px,calc(var(--sheet-w)*.073),47px);line-height:1.09;overflow-wrap:anywhere}
.work-identity-cover .book-cover-center{padding:clamp(8px,1.8vh,18px) 0}
.work-identity-cover .work-cover-art{display:block;width:min(100%,370px);height:clamp(100px,20vh,185px);margin:0 auto;background:transparent url('/essays/teatro-an-unfinished-composition/assets/teatro-score-memory-vector-human-condition.svg') center/contain no-repeat}
.work-identity-cover .subedition-title{font-size:clamp(26px,calc(var(--sheet-w)*.074),44px)!important;line-height:1.09;text-wrap:balance}
.work-identity-cover .book-cover-foot a{color:inherit;text-decoration:none;border-bottom:1px solid var(--book-rule)}
.work-reading-identity{justify-self:center;align-self:center;white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis;font:600 clamp(8px,1.1vw,11px)/1.4 ui-monospace,Menlo,monospace;letter-spacing:.06em}
@media(max-width:800px){.edition-rail{gap:6px;font-size:9px}.edition-rail a{max-width:9ch;overflow:hidden;text-overflow:ellipsis}}
@media(max-width:500px){.edition-rail a{max-width:5ch}.edition-rail{font-size:8px}}
""")
 # Source essay HTML is immutable; stage-only link projection changes the rail.
 # Preserve the previous detailed editions catalogue at its own route.
 catalogue=build_catalogue(version).replace('href="/editions/"','href="/editions/catalogue/"').rstrip()+"\n"
 detailed=ED/"catalogue"
 detailed.mkdir(parents=True,exist_ok=True)
 (detailed/"index.html").write_text(catalogue)
 collections=build_first_readings_collection(version)
 index=build_estate_grid()
 (ED/"index.html").write_text(index)
 MAIN.write_text(index)
 (SITE/"assets/editions.css").write_text("""*{box-sizing:border-box}
:root{color-scheme:light;background:#eeeae0;color:#26231d;font-family:"Iowan Old Style",Charter,Georgia,serif}
body{margin:0}a{color:inherit}a:focus-visible{outline:2px solid #aa6c37;outline-offset:4px}
.catalogue-header{max-width:1250px;margin:auto;padding:24px clamp(20px,5vw,70px) 16px}
.catalogue-eyebrow{display:flex;justify-content:space-between;gap:15px;font:600 11px/1.5 ui-monospace,Menlo,monospace;letter-spacing:.13em;border-bottom:1px solid #b6ada0;padding-bottom:12px}
.catalogue-eyebrow a{text-decoration:none}.catalogue-eyebrow span{color:#716c61}
.edition-global-nav{display:flex;gap:clamp(16px,4vw,50px);padding:22px 0 9px;font:500 12px ui-monospace,Menlo,monospace;flex-wrap:wrap}
.edition-global-nav a{border-bottom:1px solid transparent;text-decoration:none}
.edition-global-nav a:hover{border-color:#26231d}
.catalogue-main{max-width:1250px;margin:auto;padding:0 clamp(20px,5vw,70px)}
.catalogue-intro{border-top:1px solid #b6ada0;margin-top:13px;padding:35px 0 32px}
.catalogue-intro>p{font:600 10px ui-monospace,Menlo,monospace;letter-spacing:.19em}
.catalogue-intro h1{font-size:clamp(72px,12vw,150px);font-weight:400;line-height:.98;letter-spacing:-.065em;margin:24px 0 23px}
.catalogue-intro h1 span,.edition-copy h2 span{color:#986e4a}
.catalogue-intro-line{display:flex;align-items:end;justify-content:space-between;gap:20px}
.catalogue-intro-line p{font-size:clamp(18px,2.2vw,27px);max-width:42ch;margin:0;line-height:1.35}
.catalogue-intro-line span,.edition-meta,.edition-copy small,.edition-sublist h3{font:600 10px/1.5 ui-monospace,Menlo,monospace;letter-spacing:.09em;color:#736e63}
.catalogue-intro-line span{white-space:nowrap}
.edition-list{border-top:1px solid #b6ada0}
.edition-item{padding:28px 0 34px;border-bottom:1px solid #b6ada0}
.edition-meta{display:flex;align-items:center;justify-content:space-between;gap:20px}
.edition-content{display:grid;grid-template-columns:minmax(170px,29%) minmax(0,1fr);gap:clamp(22px,5vw,70px);padding-top:23px}
.edition-cover,.edition-bookmark{margin:0;aspect-ratio:1/1.25;min-height:180px;background:#f7f3ea;border:1px solid #d8d1c5;box-shadow:0 3px 14px #26231d14}
.edition-cover a,.edition-cover img{display:block;width:100%;height:100%}.edition-cover img{object-fit:contain;padding:12px}
.edition-bookmark{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:35px;font:600 12px ui-monospace,Menlo,monospace;letter-spacing:.2em}
.edition-mark{font-size:clamp(55px,10vw,140px);font-weight:400;color:#976e4e}
.edition-theatre{background:#e0d8c9}.edition-theatre .edition-mark{color:#26231d}
.edition-copy h2{font-size:clamp(37px,6vw,83px);letter-spacing:-.05em;line-height:1;margin:13px 0 18px;font-weight:400}
.edition-copy p{max-width:56ch;font-size:clamp(17px,1.9vw,23px);line-height:1.42}
.edition-open{display:inline-flex;gap:16px;font:600 12px ui-monospace,Menlo,monospace;letter-spacing:.035em;text-decoration:none;border-bottom:1px solid #26231d;padding:8px 0}
.edition-open:hover,.edition-sublist a:hover{color:#976e4e}
.edition-sublist{margin-top:24px;max-width:700px}.edition-sublist h3{margin:0 0 7px}
.edition-sublist ol{list-style:none;padding:0;margin:0}
.edition-sublist li a{display:grid;grid-template-columns:30px 1fr 18px;gap:13px;padding:9px 0;border-bottom:1px solid #d8d0c3;text-decoration:none;font-size:clamp(14px,1.4vw,18px)}
.edition-sublist li a span:first-child{font:600 10px ui-monospace,Menlo,monospace;color:#716c61}
.catalogue-footer{max-width:1250px;padding:26px clamp(20px,5vw,70px) 60px;margin:auto;font:11px/1.9 ui-monospace,Menlo,monospace;color:#716c61}
.catalogue-footer nav a{text-decoration:none;border-bottom:1px solid #b6ada0}
@media(max-width:640px){.catalogue-intro-line span{display:none}.edition-content{grid-template-columns:1fr}
.edition-cover,.edition-bookmark{max-width:270px;min-height:0}
.edition-item{padding:20px 0}.catalogue-intro{padding:23px 0}.catalogue-header{padding-top:17px}
.edition-copy h2{margin-top:7px}.edition-rail a{max-width:5ch}}
""")
 version.update({
  "schema":"fountain.press.linotype.essay-edition.v2",
  "editionPath":"editions/essays/",
  "cataloguePath":"editions/",
  "rootLanding":"editions/",
  "legacyDetailedCatalogue":"editions/catalogue/",
  "subEditions":[{"id":a["id"],"path":a["editionPath"],"parent":"editions/essays/"} for a in version["essays"]],
  "editionHierarchy":["editions/","editions/essays/"]+[x["editionPath"] for x in version["essays"]],
  "publicationRule":"A rail points to its edition; nested editions are independent complete Linotype readers."
 })
 ORIGINAL.write_text(json.dumps(version,indent=2,ensure_ascii=False)+"\n")
 items=sorted(x for x in SITE.rglob("*") if x.is_file())
 inventory=''.join(sha(x.read_bytes())+'  '+x.relative_to(SITE).as_posix()+'\n' for x in items)
 (ROOT/"publication-files.sha256").write_text(inventory)
 edition=ROOT/"edition.json"
 obj=json.loads(edition.read_text())
 obj.update(fileCount=len(items),indexPages=sum(x.name=="index.html" for x in items),
  sourceSha256Inventory=sha(inventory.encode()),
  publicationState="source-candidate-editions-hierarchy-not-publicly-deployed",
  editorialEdition="editions/essays/",editionCatalogue="editions/",
  nestedEditionCount=3,firstReadingsCollection="collections/first-readings/",
  firstReadingsWorkCount=collections["workCount"])
 edition.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
 print("EDITIONS_HIERARCHY_COMPILED",len(version["subEditions"]),"nested editions",
       version["originalParagraphs"],"original paragraphs",version["originalFigures"],"figures")
 for p in [MAIN,ED/"index.html",BOOK/"index.html",*[BOOK/a["id"]/"index.html" for a in version["essays"]]]:
  print("ROUTE",p.relative_to(SITE),p.stat().st_size)

if __name__=="__main__":main()
