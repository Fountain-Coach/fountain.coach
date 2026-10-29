#!/usr/bin/env python3
"""Compose a source-pinned, reader-first Fountain Coach Linotype landing.

Source is the verified seven-work PUBLIC essay collection projected into an
immutable WLAN baseline.  Content is copied; no prose is generated or revised.
Writing dates are never inferred.  Outputs are direct-static HTML and a
chapter-source receipt, not a second publishing authority.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, re
from pathlib import Path
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlsplit

p=argparse.ArgumentParser()
p.add_argument("--published-stage-root",type=Path,required=True)
p.add_argument("--inventory",type=Path,required=True)
p.add_argument("--output",type=Path,required=True)
p.add_argument("--receipt",type=Path,required=True)
a=p.parse_args()
here=Path(__file__).resolve().parents[1]
site=here/"site"
plan=json.loads((here/"editorial/living-essays-2026-10-29.json").read_text())
root=a.published_stage_root
inventory=json.loads(a.inventory.read_text())
exact={f["path"]:f["sha256"] for f in inventory["files"]}
if inventory["release"]!="shared-shell-20261028-v58-composable-css-05b3915":
    raise SystemExit("Unexpected published/staged baseline; reconcile before compiling")
hash_bytes=lambda v:hashlib.sha256(v).hexdigest()
index=root/"essays/index.html"
sindex=BeautifulSoup(index.read_text(),"html.parser")
routes=[x["data-essay-route"] for x in sindex.select("[data-essay-route]")]
ids=[urlsplit(x).path.rstrip("/").split("/")[-1] for x in routes]
works=plan["works"]
catalogue={w["id"]:w for w in works}
for card in sindex.select("[data-essay-route]"):
    slug=urlsplit(card["data-essay-route"]).path.rstrip("/").split("/")[-1]
    h3=card.select_one("h3")
    assert h3,("published work has no authored title",slug)
    catalogue[slug]["title"]=h3.get_text(" ",strip=True)
assert len(ids)==len(set(ids))==len(works)==7,ids
assert set(ids)==set(catalogue),("Missing published work",set(ids)^set(catalogue))
by_date=sorted((w for w in works if w.get("written")),key=lambda w:w["written"],reverse=True)
latest=by_date[0]["id"]
assert latest==plan["latest"] and by_date[0]["written"]==plan["verifiedWrittenAt"]
ordered=[latest]+[w for w in ids if w!=latest]
# The source list can grow only when a dated, explicitly recorded admission
# appears in the editorial plan.  Historic undated works retain a disclosed
# original-gallery fallback rather than a fabricated chronology.
fallback=[x for x in plan["works"] if x["id"]!=latest]
order=[latest]+[x["id"] for x in fallback]
assert set(order)==set(ids)

soup=BeautifulSoup((site/"editions/essays/index.html").read_text(),"html.parser")
flow=soup.select_one("#book-flow")
assert flow is not None
flow.clear()
body=soup.body
body["data-edition-id"]="essays-continuing-20261029"
body["data-edition-entry-anchor"]="work-"+latest
body["data-latest-written"]=latest
body["data-reading-scenario"]="one-continuing-book"
body["data-publication-state"]="source-bound-stage-candidate"
for meta in list(soup.select('meta[http-equiv="Content-Security-Policy"]')):meta.decompose()
description=soup.select_one('meta[name="description"]')
description["content"]="Seven published Fountain Coach essays, composed as one continuing reader-first book. Choose semantic chapter sequences; the newest dated writing always opens."
soup.select_one("title").string="Essays — A Book Continually Written · Fountain Coach"
canonical=soup.select_one('link[rel="canonical"]');canonical["href"]="https://fountain.coach/"
soup.select_one("meta[name='robots']")["content"]="noindex,nofollow"
for script in soup.select("head script[src]"):
    if script.get("src")=="/assets/linotype/book.js":
        tag=soup.new_tag("script",src="/assets/linotype/living-essays.js")
        tag["defer"]=""
        script.insert_before(tag)
css=soup.new_tag("link",rel="stylesheet",href="/assets/linotype/living-essays.css")
soup.head.append(css)
# This source-owned static scenario has the same shared CSS/JS as the estate.
for path in ("/assets/site.css","/assets/estate-core.css"):
    sheet=soup.new_tag("link",rel="stylesheet",href=path)
    soup.head.append(sheet)
soup.head.append(soup.new_tag("script",src="/assets/estate-core.js",defer=""))
header=soup.select_one("header.book-toolbar")
back=header.select_one("a.book-back")
back["href"]="/essays/"
back["aria-label"]="The complete Essays publication collection"
back.select_one("span:last-child").string="Essays"
rail=header.select_one("nav.edition-rail")
rail.replace_with(BeautifulSoup('<h1 class="book-identity" aria-label="Essays, a book continually written"><span>ESSAYS</span><span class="living-title-long" aria-hidden="true"> · ONE CONTINUING BOOK</span></h1>',"html.parser"))
tools=header.select_one(".book-tools")
selector=BeautifulSoup('<label class="living-path-label" for="living-reading-path">Read by <select id="living-reading-path" name="path" aria-label="Choose a semantic chapter sequence"><option value="recent">Latest first</option><option value="sound">Listening</option><option value="reading">Books &amp; memory</option><option value="systems">Reframe &amp; estate</option></select></label>',"html.parser")
tools.insert(0,selector)

rec=[]
for n,slug in enumerate(order,1):
    work=catalogue[slug]
    file=root/"essays"/slug/"index.html"
    rel="estate/essays/"+slug+"/index.html"
    data=file.read_bytes()
    assert hash_bytes(data)==exact[rel],("source revision changed",rel)
    source=BeautifulSoup(data,"html.parser")
    original=source.select_one("main article.essay-article")
    assert original and len(original.get_text(strip=True))>200,slug
    original_art=next((fig.select_one("img") for fig in original.select("figure") if fig.select_one("img")),None)
    assert original_art is not None,("Published essay has no source-owned opening artwork",slug)
    opener=soup.new_tag("div");opener["class"]="book-opener-art"
    figure=soup.new_tag("figure");figure["class"]="book-hero-figure"
    art=soup.new_tag("img")
    src=original_art.get("src")
    if src.startswith("assets/"):src="/essays/"+slug+"/"+src
    if src.startswith("/estate/"):src=src[len("/estate"):]
    art["src"]=src
    art["alt"]=original_art.get("alt") or ("Original published artwork for "+slug)
    art["width"]=original_art.get("width") or "1200"
    art["height"]=original_art.get("height") or "630"
    art["loading"]="eager"
    figure.append(art)
    opener.append(figure)
    chapter=soup.new_tag("section",id="work-"+slug)
    chapter["class"]="book-chapter"
    chapter["data-book-chapter"]=slug
    chapter["data-chapter-number"]=str(n)
    chapter["data-semantic-roles"]=" ".join(work["tags"])
    chapter["data-fallback-order"]=str(n)
    if work.get("written"):chapter["data-written-at"]=work["written"]
    heading=soup.new_tag("header");heading["class"]="book-chapter-heading"
    ordinal=soup.new_tag("p");ordinal["class"]="book-ordinal"
    ordinal.string=("CURRENT WRITING" if slug==latest else "ESSAY · ORIGINAL PUBLICATION")
    cnt=soup.new_tag("span");cnt.string=f"{n:02d} / {len(order):02d}";ordinal.append(cnt)
    heading.append(ordinal)
    h2=soup.new_tag("h2");h2.string=slug.replace("-", " ").title() if not work.get("title") else work["title"]
    heading.append(h2)
    meta=soup.new_tag("p");meta["class"]="book-chapter-meta"
    meta.string=("WRITTEN "+work["written"] if work.get("written") else "WRITING DATE NOT ATTESTED · PUBLISHED ESSAY")
    heading.append(meta)
    chapter.append(heading)
    chapter.append(opener)
    flow.append(chapter)
    content=soup.new_tag("section");content["class"]="book-chapter-text"
    content["data-chapter-content"]=slug
    prose=soup.new_tag("article");prose["class"]="book-prose"
    # Copy every source article block; the original author-facing title is
    # already the chapter heading, but its lead and original cover image remain.
    for node in original.find_all(recursive=False):
        if node.name=="header" and "essay-header" in node.get("class",[]):
            for x in node.find_all(recursive=False):
                if x.name in ("h1","h2","div") and not x.select("img"):continue
                if x.name not in ("p","figure","img"):continue
                prose.append(copy.deepcopy(x))
            continue
        # Press pagination splits direct paragraphs. Original editorial
        # prose containers are structural, not indivisible manuscript blocks.
        # Lift their children into the chapter's original sequential flow.
        if node.name in ("div","section") and any(
          cls in node.get("class",[]) for cls in
          ("essay-prose","door-study","essay-listening-panel","paper-intro","pdf-wrap")):
            for child in node.find_all(recursive=False):
                if getattr(child,"name",None):
                    prose.append(copy.deepcopy(child))
        else:
            prose.append(copy.deepcopy(node))
    for elem in prose.find_all(True):
        if elem.has_attr("id"):elem["id"]=slug+"--"+elem["id"]
        for attr in ("src","href","poster"):
            path=elem.get(attr)
            if not path:continue
            if path.startswith("assets/"):
                elem[attr]="/essays/"+slug+"/"+path
            elif path.startswith("/estate/"):
                elem[attr]=path[len("/estate"):]
            elif path.startswith("#") and len(path)>1:
                elem[attr]="#"+slug+"--"+path[1:]
        if elem.name=="figure":elem["class"]=list(dict.fromkeys(elem.get("class",[])+["reading-original-figure"]))
        if elem.name=="img":elem["loading"]="lazy"
    # Live custom listening controls are owned by the original essay pages;
    # inside a composed book do not expose no-op buttons as working exhibits.
    interactive=bool(prose.select("button,audio:not([src]),iframe,embed,object"))
    for elem in list(prose.select("button")):
        anchor=soup.new_tag("a",href="/essays/"+slug+"/#"+(elem.get("id") or ""))
        anchor["class"]="book-original-exhibit-link"
        anchor.string=elem.get_text(" ",strip=True) or "Original interactive exhibit"
        elem.replace_with(anchor)
    for elem in list(prose.select("embed,iframe,object")):
        elem.decompose()
    # A native browser audio control does not fit a measured portrait leaf.
    # The complete interactive listening original is linked in the next note;
    # never fake a working player inside a static manuscript projection.
    for audio in list(prose.select("audio")):
        audio.decompose()
    if interactive:
        note=soup.new_tag("p");note["class"]="book-original-exhibit-note"
        link=soup.new_tag("a",href="/essays/"+slug+"/")
        link.string="Open the original published work for its complete interactive listening or PDF exhibits"
        note.append(link);prose.append(note)
    # Some prose references are full scholarly PDFs, not full HTML. Provide
    # an explicit original-work link; never relabel an abstract as full text.
    origin=soup.new_tag("p");origin["class"]="book-source-note"
    origin.string="ORIGINAL PUBLISHED WORK · "
    l=soup.new_tag("a",href="/essays/"+slug+"/");l.string="READ AT SOURCE ↗"
    origin.append(l)
    # Preserve published literary content while composing original interactive
    # exhibit controls as links back to their functional published owner route.
    # Press page measurement accepts standalone text/plate blocks, not long
    # nested lists, dynamic sound controls or indivisible application widgets.
    # Do not rewrite a source paragraph or its inline marks: lift each in order.
    def linearize(node):
        kind=node.name
        if kind in ("script","style","audio","video","canvas","button","input",
                    "select","textarea","noscript","iframe","embed","object"):
            return []
        if kind=="figure" and node.select_one("img"):
            return [copy.deepcopy(node)]
        if kind in ("p","h1","h2","h3","h4"):
            text=copy.deepcopy(node)
            if kind=="h1":text.name="h2"
            return [text]
        if kind=="li":
            out=soup.new_tag("p")
            out["class"]="book-listed-note"
            for child in node.contents:
                if getattr(child,"name",None) in ("ol","ul"):
                    continue
                out.append(copy.deepcopy(child))
            nested=[]
            for x in node.find_all(["ol","ul"],recursive=False):
                nested.extend(linearize(x))
            return [out]+nested if out.get_text(" ",strip=True) else nested
        if kind=="summary":
            h=soup.new_tag("h3");h.string=node.get_text(" ",strip=True)
            return [h]
        result=[]
        for child in node.find_all(recursive=False):
            result.extend(linearize(child))
        if not result and node.get_text(" ",strip=True):
            para=soup.new_tag("p")
            para["class"]="book-inline-original"
            para.string=node.get_text(" ",strip=True)
            return [para]
        return result
    current=list(prose.find_all(recursive=False))
    prose.clear()
    for block in current:
        for flat in linearize(block):
            prose.append(flat)
    # Linotype's native image compositor measures plates separately from
    # prose. Split original chapter content at every original <figure> while
    # preserving the original paragraph/art order and authorial captions.
    # Never reduce a plate to a clipped image inside an indivisible text leaf.
    blocks=list(prose.find_all(recursive=False))
    content.clear()
    segment=soup.new_tag("article");segment["class"]="book-prose"
    def flush_segment():
        if not segment.find(True):
            return
        part=soup.new_tag("section");part["class"]="book-chapter-text"
        part["data-chapter-content"]=slug
        part.append(segment)
        flow.append(part)
    for block in blocks:
        if block.name=="figure" and block.select_one("img"):
            flush_segment()
            plate=soup.new_tag("section");plate["class"]="book-art-leaf"
            plate.append(block)
            flow.append(plate)
            segment=soup.new_tag("article");segment["class"]="book-prose"
        else:
            segment.append(block)
    flush_segment()
    # The engine measures source notes outside .book-prose; including them
    # in the manuscript would make its text-conservation witness compare
    # a source note against its intentionally excluded running footnote.
    last_text=next(x for x in reversed(list(flow.children))
        if "book-chapter-text" in x.get("class",[]) and x.has_attr("data-chapter-content"))
    assert last_text.get("data-chapter-content")==slug
    last_text.append(origin)
    rec.append({"id":slug,"source":rel,"sourceSHA256":exact[rel],
                "textSHA256":hash_bytes(original.get_text(" ",strip=True).encode()),
                "written":work.get("written"),"images":len(original.select("img")),
                "originalCharacters":len(original.get_text(" ",strip=True))})
end=soup.new_tag("section",id="book-end");end["class"]="book-end"
h2=soup.new_tag("h2");h2.string="To be continued."
end.append(h2)
par=soup.new_tag("p");par.string="This book continues as new essays are written. Each published work retains its own address, images and original edition."
end.append(par)
link=soup.new_tag("a",href="/essays/");link.string="Browse the complete publication collection"
end.append(link)
flow.append(end)

toc=soup.select_one("#book-contents nav .book-toc-list")
assert toc is not None
toc.clear()
for n,slug in enumerate(order,1):
    li=soup.new_tag("li")
    a1=soup.new_tag("a",href="#work-"+slug)
    a1["data-book-toc-target"]=slug
    number=soup.new_tag("span");number["class"]="toc-number";number.string=f"{n:02d}"
    title=soup.new_tag("span");title["class"]="toc-title";title.string=catalogue[slug]["title"] if "title" in catalogue[slug] else slug.replace("-"," ").title()
    label=soup.new_tag("span");label["class"]="toc-voice";label.string=("/".join(catalogue[slug]["tags"][:2])).upper()
    for z in (number,title,label):a1.append(z)
    li.append(a1);toc.append(li)
contents=soup.select_one("#book-contents")
other=soup.new_tag("section");other["class"]="living-other-works"
other["aria-label"]="Other published books and works"
label=soup.new_tag("h3");label.string="Other published readings"
other.append(label)
nav=soup.new_tag("nav")
nav["aria-label"]="Published works beyond the Essays book"
for name,route in [
    ("Solstice · First Reading","/solstice/editions/first-reading/"),
    ("Teatro · First Hearing","/teatro/editions/first-hearing/"),
    ("Book of Reframe","/book/"),
    ("Fountain Press editions","/editions/"),
    ("Author's Works","/works/"),
    ("Full Essays collection","/essays/"),
    ("Earlier author-led entrance","/scenarios/author-led/")]:
    link=soup.new_tag("a",href=route)
    link.string=name
    nav.append(link)
other.append(nav);contents.append(other)
for x in soup.select("#book-appearance p"):
    x.string="Swipe or use arrow keys to turn measured pages. Chapters are source-stable; their order can change. Original published exhibits remain at their own links."
soup.select_one("main")["aria-label"]="Essays — one continuing book, newest authored chapter first"
skip=soup.select_one("a.book-skip");skip["href"]="#book-pages"
output=a.output
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(str(soup)+"\n")
receipt={"schema":"fountain.coach.reader-first-source-plan.v1",
  "baseRelease":inventory["release"],"sourceOwner":"Fountain-Coach/fountain.coach",
  "latest":latest,"latestWrittenAt":catalogue[latest].get("written"),
  "allPublishedEssayCount":len(rec),"sourceWorks":rec,
  "chapterOrder":order,"semanticPathways":["recent","sound","reading","systems"],
  "bookHTMLSHA256":hash_bytes(output.read_bytes()),
  "stageActivated":False,"publicReleased":False}
a.receipt.parent.mkdir(parents=True,exist_ok=True)
a.receipt.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="sourceWorks"},indent=2))
