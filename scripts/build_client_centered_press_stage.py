#!/usr/bin/env python3
"""Source-authored Client-Centered, projected through the *published* Fountain Press Reader.

Baseline is the SHA-pinned 2026-11-10 production Fountain Press reading-first HTML,
press-engine and assets. No replacement compositor, typesetting CSS or app shell.
One edition template is added; the existing five-essay shelf stays unaltered.
This script never deploys or authorizes a public release.
"""
from pathlib import Path
import hashlib, html, json, re, shutil, subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"site/essays/client-centered"
MARKDOWN=SOURCE/"client-centered.md"
FIXTURE=ROOT/"fixtures/published-fountain-press"
BASE=FIXTURE/"production-reading-first-essay.html"
APP=FIXTURE/"reading-first-app.js"
ENGINE=FIXTURE/"reading-first-press-engine.js"
ASSETS=SOURCE/"assets"
OUT=ROOT/"build/client-centered-stage/estate/read/essay--client-centered"
PREFIX="/estate/read/essay--client-centered/"
BASELINE={
 "productionHtmlSHA256":"30af76515fb99cf9045f27e9240773cbff2e55d78d00cc52bdb9b7c24c020462",
 "appSHA256":"1a7b4f9e30f9448f5ac0bf1e773a9d8b91a69cedbb27c94e75564059b0fd8893",
 "engineSHA256":"e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a",
 "productionURL":"https://fountain.coach/estate/read/essay--the-ear-that-learns/",
 "observed":"2026-11-10",
}
FIGURES=[
 {"id":"client-centered.positions","file":"client-centered-positions.svg",
  "after":"client-centered.title","role":"hero",
  "alt":"Axonometric Teatro Score: two separate platforms across an open, translucent plane, with a small vermilion mark on the shared floor."},
 {"id":"client-centered.method","file":"client-centered-open-method.svg",
  "after":"client-centered.s2.p6","role":"inline",
  "alt":"Axonometric Teatro Score: a method made of incomplete spatial frames with an open vermilion route passing beyond the instrument."},
]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def filehash(p):return digest(p.read_bytes())
def assert_pinned():
    actual={"productionHtmlSHA256":filehash(BASE),"appSHA256":filehash(APP),"engineSHA256":filehash(ENGINE)}
    for key,value in actual.items():
        if value!=BASELINE[key]:raise RuntimeError("Published Fountain Press predecessor drift: "+key)
def parse_source():
    raw=MARKDOWN.read_text("utf-8")
    assert raw.startswith("# Client-Centered\n\n*On expertise, participation, and the freedom of another person*\n\n")
    parts=re.split(r"(?m)^## ([^\n]+)\n\n",raw)
    assert len(parts)==9
    headings=[parts[i] for i in (1,3,5,7)]
    assert headings==["Another Person's Purpose","The Method and the Situation",
                     "Intelligence in the Relationship","What Becomes Possible"]
    groups=[]
    for i,heading in enumerate(headings):
        block=parts[2+2*i].strip()
        paras=[p.strip().replace("\n"," ") for p in block.split("\n\n") if p.strip()]
        assert paras and all(not p.startswith("#") for p in paras)
        groups.append({"id":f"s{i+1}","heading":heading,"paragraphs":paras})
    assert all("\n" not in p for g in groups for p in g["paragraphs"])
    return raw,groups
def blocks(raw,groups):
    all_blocks=[]
    sections_html=[]
    for g in groups:
        i=g["id"]
        heading_id=f"client-centered.{i}.heading"
        all_blocks.append({"id":heading_id,"text":g["heading"],"kind":"heading"})
        sections_html.append(
            '<p class="frame-subheading" data-source-block="'+heading_id+
            '" data-source-from="0" data-source-to="'+str(len(g["heading"]))+'">'+
            html.escape(g["heading"])+'</p>')
        for index,p in enumerate(g["paragraphs"],1):
            addr=f"client-centered.{i}.p{index}"
            all_blocks.append({"id":addr,"text":p,"kind":"paragraph"})
            sections_html.append(
                '<p data-source-block="'+addr+'" data-source-from="0" data-source-to="'+
                str(len(p))+'">'+html.escape(p)+'</p>')
        if i=="s2":
            sections_html.append("__FIGURE_TWO__")
    return sections_html,all_blocks
def build():
    assert_pinned()
    raw,groups=parse_source()
    section_fragments,all_blocks=blocks(raw,groups)
    source_sha=digest(raw.encode())
    release_rev=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    figure_meta=[]
    for item in FIGURES:
        p=ASSETS/item["file"]
        b=p.read_bytes()
        if b"<svg" not in b[:200] or b"viewBox" not in b[:600]:raise ValueError("Not an authored SVG")
        figure_meta.append({**item,"sha256":digest(b),"bytes":len(b),
                            "stagingURL":PREFIX+"assets/images/"+item["file"]})
    if OUT.exists():shutil.rmtree(OUT)
    (OUT/"assets/images").mkdir(parents=True)
    shutil.copytree(ASSETS/"press",OUT/"assets/press")
    for item in FIGURES:shutil.copy2(ASSETS/item["file"],OUT/"assets/images"/item["file"])
    # Exactly the original production app, with ONE staging-only exclusion:
    # the review work is addressable but never added to the five accepted essays.
    published_app=APP.read_text("utf-8")
    old="const implementationStories=new Set([\n 'essay--semantic-compilation-the-archive-is-not-the-edition',"
    new="const implementationStories=new Set([\n 'essay--client-centered', // review-only, not a fifth/sixth published essay\n 'essay--semantic-compilation-the-archive-is-not-the-edition',"
    assert published_app.count(old)==1
    stage_app=published_app.replace(old,new,1)
    stage_app_path=OUT/"assets/press/reading-first-app.client-centered-review.js"
    stage_app_path.write_text(stage_app)
    # Use the current published 2026-11-10 Reader, with untouched page CSS,
    # real original press-engine and its existing complete shelf source.
    start='<section class="book-chapter" id="work-client-centered"><div class="book-chapter-heading"><h2 data-source-block="client-centered.title">Client-Centered</h2></div></section>'
    hero=FIGURES[0]
    hero_html=('<section class="book-art-leaf"><figure class="frame-reading-figure frame-essay-hero" '+
               'data-source-block="'+hero["id"]+'" data-source-plate-sha256="'+figure_meta[0]["sha256"]+'">'+
               '<img loading="eager" decoding="sync" src="'+figure_meta[0]["stagingURL"]+
               '" alt="'+html.escape(hero["alt"],quote=True)+
               '" width="1500" height="980"/></figure></section>')
    second=FIGURES[1]
    # Secondary art belongs at its authored source beat inside the existing
    # paragraph stream, not in a stand-alone plate that splits the chapter.
    # The original Press engine measures in-flow figures with nearby prose.
    figure_after = 1 + sum(1 + len(g["paragraphs"]) for g in groups[:2])
    second_html=('<figure class="frame-reading-figure" '+
                 'data-inline-after-paragraph="'+str(figure_after)+'" '+
                 'data-source-block="'+second["id"]+'" data-source-illustration-id="'+second["id"]+'" '+
                 'data-source-plate-sha256="'+figure_meta[1]["sha256"]+'">'+
                 '<img loading="lazy" decoding="async" src="'+figure_meta[1]["stagingURL"]+
                 '" alt="'+html.escape(second["alt"],quote=True)+
                 '" width="1500" height="980"/></figure>')
    intro='On expertise, participation, and the freedom of another person'
    # Keep source paragraphs intact. CSS controls lineation; no inserted <br>.
    ordered_source="".join(section_fragments).replace("__FIGURE_TWO__",second_html)
    text_flow=('<section class="book-chapter-text"><article class="book-prose">'+
           '<p class="frame-lead" data-source-block="client-centered.subtitle" data-source-from="0" data-source-to="'+str(len(intro))+'">'+
           html.escape(intro)+'</p>'+ordered_source+'</article></section>')
    template='<template data-reader-volume="essay--client-centered"><div class="book-flow" data-min-leaves="1">'+start+hero_html+text_flow+'</div></template>'
    html_out=BASE.read_text("utf-8")
    anchor=' <script type="application/json" id="reader-gallery-data">'
    assert html_out.count(anchor)==1
    html_out=html_out.replace(anchor,template+'\n'+anchor,1)
    html_out=html_out.replace('data-initial-volume="essay--the-ear-that-learns"',
                              'data-initial-volume="essay--client-centered"',1)
    # Retain the published Reader + CSS/JS. Only route-local links change
    # to pinned *copies* of the same published assets. No new layout/engine.
    head=html_out[:html_out.index("</head>")]
    links=list(dict.fromkeys(re.findall(r'(?:href|src)="(/estate/assets/linotype/[^"]+\.(?:js|css|mjs))"',head)))
    for link in links:
        target=PREFIX+"assets/press/"+Path(link).name
        if "reading-first-app." in link:
            target=PREFIX+"assets/press/reading-first-app.client-centered-review.js"
        html_out=html_out.replace('"'+link+'"','"'+target+'"')
    html_out=html_out.replace('<title>The Ear That Learns — Fountain Press</title>',
                              '<title>Client-Centered — Fountain Press (WLAN editorial review)</title>',1)
    html_out=html_out.replace('Read The Ear That Learns in the source-bound Fountain Press Linotype edition.',
                              'Client-Centered, a complete source-bound Fountain Press essay in private editorial review.')
    # No public canonical or OG claim for an unapproved edition.
    html_out=re.sub(r'<link rel="canonical" href="https://fountain.coach/estate/read/essay--the-ear-that-learns/"/>\s*','',html_out,count=1)
    # Never carry another essay's social image or title into this private review.
    html_out=re.sub(r'<meta property="og:(?:url|image[^"]*|title|description)"[^>]*>\s*','',html_out)
    html_out=re.sub(r'<meta name="twitter:(?:title|description|image|card)"[^>]*>\s*','',html_out)
    html_out=html_out.replace('<meta name="robots" content="index,follow"/>',
                              '<meta name="robots" content="noindex,nofollow"/>\n'+
                              '<meta name="fountain:publication-state" content="owner-WLAN-editorial-review"/>\n'+
                              '<meta name="fountain:manuscript-sha256" content="'+source_sha+'"/>\n'+
                              '<meta name="fountain:source-revision" content="'+release_rev+'"/>',1)
    (OUT/"index.html").write_text(html_out)
    manifest={
      "schema":"fountain.press.source-owned-essay-review.v1",
      "title":"Client-Centered","subtitle":intro,"sourceOwner":"Fountain-Coach/fountain.coach",
      "sourcePath":"site/essays/client-centered/client-centered.md","sourceRevision":release_rev,
      "sourceSHA256":source_sha,"publicationState":"private-owner-WLAN-review",
      "productionAuthorized":False,"targetPublicRoute":"https://fountain.coach/estate/read/essay--client-centered/",
      "stageRoute":PREFIX,"predecessorProduction":BASELINE,
      "currentPublishedEssaysUnchanged":True,
      "renderer":"original published reading-first-press-engine, byte-identical",
      "stagingAdapter":"one source-app exclusion keeps the current five-essay catalogue unchanged",
      "sections":[{"id":g["id"],"title":g["heading"],"paragraphCount":len(g["paragraphs"])} for g in groups],
      "paragraphCount":sum(len(g["paragraphs"]) for g in groups),
      "blocks":all_blocks,"figures":figure_meta,
      "figureSourceRole":"new standalone Teatro Score visual interpretations; source-owned illustration only",
    }
    (OUT/"edition-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    assets={}
    for path in OUT.rglob("*"):
        if path.is_file():
            assets[path.relative_to(OUT).as_posix()]=filehash(path)
    (ROOT/"build/client-centered-stage-inventory.json").write_text(json.dumps({
         "sourceRevision":release_rev,"manuscriptSHA256":source_sha,"files":assets,
         "stageOnly":True,"publicProductionModified":False},indent=2)+"\n")
    print(json.dumps({"releaseSourceRevision":release_rev,"paragraphs":manifest["paragraphCount"],
                      "headings":len(groups),"figures":len(FIGURES),
                      "productionEngineIdentical":True,"files":len(assets)},indent=2))
if __name__=="__main__":build()
