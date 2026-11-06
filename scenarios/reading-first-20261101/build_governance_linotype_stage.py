#!/usr/bin/env python3
"""Integrate the full canonical Governance book into the accepted Linotype Reader.

Only the existing reader's source templates and navigation are extended.
The measured compositor, Essays, First Readings, private media and published
Governance site are never rewritten.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def once(haystack, needle, replacement):
    count=haystack.count(needle)
    if count!=1:
        raise ValueError("Reader source structure drifted: "+needle[:90]+" count "+str(count))
    return haystack.replace(needle,replacement,1)


STYLE = """
<style id="governance-press-source-style">
/* Source-faithful Governance block conventions on existing measured Linotype leaves. */
.linotype-stage .gov-source-block.gov-subheading {font-weight:650;letter-spacing:.005em;break-after:avoid;}
.linotype-stage .gov-source-block.gov-code {font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.74em;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.45;}
.linotype-stage .gov-source-block.gov-list-item {padding-left:1em;position:relative;}
.linotype-stage .gov-source-block.gov-list-item::before {content:"\\2022";position:absolute;left:.2em;color:inherit;}
.linotype-stage .gov-source-block.gov-blockquote {border-left:1px solid currentColor;padding-left:1em;font-style:italic;}
.linotype-stage .gov-source-block.gov-table-row {border-bottom:1px solid currentColor;display:flex;flex-wrap:wrap;gap:.6em;font-size:.87em;padding:.45em 0;}
.linotype-stage .gov-source-block.gov-table-row .gov-table-cell {flex:1 1 24%;min-width:0;overflow-wrap:anywhere;}
.linotype-stage .gov-source-block.gov-table-head {font-weight:650;}
.linotype-stage .gov-source-rule {opacity:.28;margin:.8em 0;}
.linotype-stage figure.gov-reading-figure {display:flex;flex-direction:column;align-items:flex-start;justify-content:center;max-width:100%;max-height:20rem;margin:.5em 0;min-width:0;}
.linotype-stage figure.gov-reading-figure img {width:auto;max-width:100%;height:auto;max-height:17rem;object-fit:contain;object-position:left center;}
.linotype-stage figure.gov-reading-figure svg {width:100%;height:auto;max-height:17rem;}
.linotype-stage figure.gov-reading-figure figcaption {font-size:.72em;text-align:left;line-height:1.3;}
.reader-gallery-cover-lettering {display:grid;place-items:center;width:100%;height:100%;font-size:clamp(.74rem,1.5vw,1.13rem);letter-spacing:.06em;font-weight:650;text-align:center;padding:.25em;overflow-wrap:anywhere;}
</style>
"""


def build(source_index, source_app, template_file, manifest_file, output):
    index=Path(source_index).read_text()
    app=Path(source_app).read_text()
    templates=Path(template_file).read_text()
    gov=json.loads(Path(manifest_file).read_text())
    chapters=gov["chapters"]
    if gov["schema"]!="fountain.press.governance.edition.v1" or gov["chapterCount"]!=160:
        raise ValueError("Not the complete canonical Governance edition")
    if len(set(x["volumeId"] for x in chapters))!=160:
        raise ValueError("Duplicate Governance volume")
    for ch in chapters:
        marker='data-reader-volume="'+ch["volumeId"]+'"'
        if templates.count(marker)!=1 or ('data-source-sha256="'+ch["sourceSha256"]+'"') not in templates:
            raise ValueError("Chapter source manifest mismatch: "+ch["slug"])
    if 'data-reader-volume="governance--' in index:
        raise ValueError("Governance already installed in Reader; reconcile rather than duplicate")
    governance_contents_template=(
        '<template data-reader-volume="governance" data-source-owner="Fountain-Coach/governance.fountain.coach">'
        '<div class="book-flow" data-min-leaves="1"><section class="book-chapter" id="work-governance">'
        '<div class="book-chapter-heading"><h2>Governance</h2></div></section>'
        '<section class="book-chapter-text"><article class="book-prose">'
        '<p>Complete canonical published Governance edition · 160 source-authentic chapters</p>'
        '</article></section></div></template>')
    index=once(index,'<template data-reader-volume="publication-notes">',
               governance_contents_template+'\n'+templates+'\n<template data-reader-volume="publication-notes">')
    matcher=re.compile(r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)',re.S)
    match=matcher.search(index)
    if not match:
        raise ValueError("Original gallery schema missing")
    gallery=json.loads(match.group(2))
    if gallery.get("schema")!="fountain.press.bookshelf-gallery.v1" or set(gallery["collections"])!={"essays","first-readings"}:
        raise ValueError("Not the accepted two-collection Bookshelf")
    gallery["collections"]["governance"]=[{"id":chapters[0]["volumeId"],
        "src":None,"alt":"Governance — complete source-owned published edition",
        "sourceKind":"canonical-governance-book-identity"}]
    gallery["source"]["governance"]=gov["sourceOwner"]+"@"+gov["sourceRevision"]
    index=index[:match.start()]+match.group(1)+json.dumps(gallery,ensure_ascii=False,separators=(",",":"))+match.group(3)+index[match.end():]
    manifest_copy=json.dumps(gov,ensure_ascii=False,separators=(",",":"))
    index=once(index,'</head>',STYLE+'\n</head>')
    index=once(index,'<script type="application/json" id="reader-gallery-data">',
       '<script type="application/json" id="governance-edition-manifest">'+manifest_copy+'</script>\n<script type="application/json" id="reader-gallery-data">')
    app=once(app,"const proofVolume='essay--a-sound-must-earn-its-place';",
        """const proofVolume='essay--a-sound-must-earn-its-place';
const governanceEdition=JSON.parse(document.getElementById('governance-edition-manifest')?.textContent||'null');
if(governanceEdition?.schema!=='fountain.press.governance.edition.v1'||
 governanceEdition.chapterCount!==160||
 governanceEdition.chapters?.length!==160)
 throw Error('Incomplete canonical Governance edition');
const governanceSequence=governanceEdition.chapters.map(ch=>{
 const t=templates.get(ch.volumeId);
 if(!t||t.dataset.sourceSha256!==ch.sourceSha256 ||
    t.dataset.governanceStatus!==ch.status)
  throw Error('Governance source/status drift: '+ch.slug);
 return ch.volumeId;
});
if(new Set(governanceSequence).size!==160)throw Error('Repeated Governance chapter identity');""")
    app=once(app,"['publication-notes','Publication Notes'],",
        "['governance','Governance'],['publication-notes','Publication Notes'],")
    app=once(app,"if(key.startsWith('essay--')||key.startsWith('solstice-reading-01--')){",
        "if(key.startsWith('essay--')||key.startsWith('solstice-reading-01--')||key.startsWith('governance--')){")
    app=once(app,"labels.set(key,label);\n  const option=document.createElement('option');",
        "labels.set(key,label);\n  if(key.startsWith('governance--'))continue; // all chapter navigation stays inside one book\n  const option=document.createElement('option');")
    app=once(app,"// Authored editorial membership: implementation histories",
        """// One edition identity in publication control, not 160 duplicate covers.
const governanceOption=document.createElement('option');
governanceOption.value='governance';governanceOption.textContent='Governance · Published Book';
section.append(governanceOption);
// Authored editorial membership: implementation histories""")
    app=once(app,"const contents={essays:[...essaySequence,proofVolume],'first-readings':solsticeSequence};",
        "const contents={essays:[...essaySequence,proofVolume],'first-readings':solsticeSequence,governance:governanceSequence};")
    app=once(app,"galleries['first-readings'].some((e,i)=>e.id!==solsticeSequence[i+2]))",
        "galleries['first-readings'].some((e,i)=>e.id!==solsticeSequence[i+2]) ||\n galleries.governance?.length!==1||galleries.governance[0].id!==governanceSequence[0])")
    app=once(app,"const isContents=name=>name==='essays'||name==='first-readings';",
        "const isContents=name=>name==='essays'||name==='first-readings'||name==='governance';")
    app=once(app,"if(solsticeSequence.includes(name))return 'first-readings';",
        "if(solsticeSequence.includes(name))return 'first-readings';\n if(governanceSequence.includes(name))return 'governance';")
    app=once(app,"const sequence=[essaySequence,solsticeSequence].find(s=>s.includes(name));",
        "const sequence=[essaySequence,solsticeSequence,governanceSequence].find(s=>s.includes(name));")
    app=once(app,"(sequence===essaySequence?'essays':'first-readings')",
        "(sequence===essaySequence?'essays':sequence===governanceSequence?'governance':'first-readings')")
    app=once(app,"const surfaceOffsets={shelf:0,essays:0,'first-readings':0};",
        "const surfaceOffsets={shelf:0,essays:0,'first-readings':0,governance:0};")
    app=once(app,"const galleryOffsets={essays:0,'first-readings':0};",
        "const galleryOffsets={essays:0,'first-readings':0,governance:0};")
    app=once(app,"const shelfContentsOffsets={essays:0,'first-readings':0};",
        "const shelfContentsOffsets={essays:0,'first-readings':0,governance:0};")
    app=once(app,"const collectionOrder=['essays','first-readings'];",
        "const collectionOrder=['essays','first-readings','governance'];")
    app=once(app,"const selectedWork={essays:null,'first-readings':null};",
        "const selectedWork={essays:null,'first-readings':null,governance:null};")
    app=once(app,"const compactPresentation={essays:'contents','first-readings':'contents'};",
        "const compactPresentation={essays:'contents','first-readings':'contents',governance:'contents'};")
    app=once(app,"subtitle.textContent=id==='essays'?'Six essays · chronological':'Reading 01 · First Reading';",
        "subtitle.textContent=id==='essays'?'Five essays · chronological':id==='governance'?'Complete published edition · 160 chapters':'Reading 01 · First Reading';")
    app=once(app,"galleryTitle.textContent='Illustrations';",
        "galleryTitle.textContent=id==='governance'?'Book cover':'Illustrations';")
    app=once(app,"const image=document.createElement('img');image.src=item.src;\n    image.alt=item.alt||labels.get(item.id);\n    image.loading=id==='essays'?'eager':'lazy';image.decoding='async';\n    square.append(image);",
        """if(item.src){
     const image=document.createElement('img');image.src=item.src;
     image.alt=item.alt||labels.get(item.id);
     image.loading=id==='essays'?'eager':'lazy';image.decoding='async';
     square.append(image);
    }else if(id==='governance'&&item.id===governanceSequence[0]){
     const lettering=document.createElement('span');
     lettering.className='reader-gallery-cover-lettering';
     lettering.textContent='GOVERNANCE';
     square.append(lettering);
    }else throw Error('Unidentified source-owned book cover');""")
    # Reuse the original same-position i/addendum, only provide chapter-true
    # provenance from the canonical manifest; no separate panel.
    app=once(app,"if(name==='publication-notes'&&addendumReturnVolume===proofVolume){",
        """if(name==='publication-notes'&&governanceSequence.includes(addendumReturnVolume)){
 const ch=governanceEdition.chapters.find(x=>x.volumeId===addendumReturnVolume);
 const prose=source.querySelector('.book-prose');
 if(!ch||!prose)throw Error('Unknown Governance source for addendum');
 const p=document.createElement('p');p.dataset.sourceBlock='gov.addendum.provenance';
 p.textContent='Governance · '+ch.title+' · '+(ch.status==='current'?'Current':'Reference')+
  ' · source revision '+governanceEdition.sourceRevision+
  ' · source SHA-256 '+ch.sourceSha256;
 prose.append(p);
}
if(name==='publication-notes'&&addendumReturnVolume===proofVolume){""")
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    (out/"index.html").write_text(index)
    (out/"reading-first-app.js").write_text(app)
    rec={"schema":"fountain.press.complete-governance-wlan-stage.v1",
         "sourceOwner":gov["sourceOwner"],"sourceRevision":gov["sourceRevision"],
         "chapterCount":gov["chapterCount"],"statuses":gov["chapterStatuses"],
         "governanceManifestSHA256":digest(Path(manifest_file).read_bytes()),
         "chapterTemplateSHA256":digest(Path(template_file).read_bytes()),
         "baseIndexSHA256":digest(Path(source_index).read_bytes()),
         "baseAppSHA256":digest(Path(source_app).read_bytes()),
         "indexSHA256":digest(index.encode()),"appSHA256":digest(app.encode()),
         "editionStatus":"source-faithful-private-stage-projection",
         "publicProductionChanged":False,"governanceSourceChanged":False,
         "previousReaderPreserved":True}
    (out/"governance-projection-receipt.json").write_text(json.dumps(rec,indent=2)+"\n")
    print(json.dumps(rec,indent=2))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for name in ("base-index","base-app","templates","manifest","output"):
        ap.add_argument("--"+name,required=True)
    x=ap.parse_args()
    build(x.base_index,x.base_app,x.templates,x.manifest,x.output)
