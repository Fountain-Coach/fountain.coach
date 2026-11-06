#!/usr/bin/env python3
"""Project a verbatim editorial proof into the CURRENT existing Linotype Reader.

No second reader, Store admission, public release, or changed published collection.
The base HTML/JS MUST be copied from the live canonical stage predecessor.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

SOURCE_SHA = "53b5f7369f68548f211571bdaf5fa4d92bbc85b3fed30aedf8839eaf8e293b7c"
VOLUME = "essay--a-sound-must-earn-its-place"
NAME = "A Sound Must Earn Its Place"
RELATED = (
    ("The Ear That Learns", "https://fountain.coach/essays/the-ear-that-learns/"),
    ("The Door Is a Score", "https://fountain.coach/essays/the-door-is-a-score/"),
)

def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError("Existing-reader identity drift: expected one " + old[:75])
    return source.replace(old, new, 1)

def inline(source):
    # Format only the explicitly present emphasis; never let editorial text inject HTML.
    text = html.escape(source, quote=True)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)

def content_blocks(markdown):
    blocks = [x.strip() for x in markdown.split("\n\n") if x.strip()]
    if blocks[0] != "# " + NAME or not blocks[1].startswith("*On acoustic craftsmanship"):
        raise ValueError("Unexpected original manuscript heading")
    if not blocks[2].startswith("**Status:** Complete editorial draft"):
        raise ValueError("Original draft status changed")
    return [blocks[1]] + blocks[3:]

def make_template(markdown):
    paragraphs = []
    for n, block in enumerate(content_blocks(markdown), 1):
        if block.startswith("## "):
            body = block[3:]
            class_name = ' class="frame-subheading"'
        else:
            body = block
            class_name = ""
        # Range is an address in the projected visible text, never a physical page.
        plain = body.replace("**", "").replace("*", "")
        paragraphs.append(
            f'<p{class_name} data-source-block="a-sound-must-earn-its-place.p{n}" '
            f'data-source-from="0" data-source-to="{len(plain)}">{inline(body)}</p>'
        )
    flow = (
        f'<template data-reader-volume="{VOLUME}" data-editorial-state="proof" data-source-sha256="{SOURCE_SHA}">'
        '<div class="book-flow" data-min-leaves="1">'
        '<section class="book-chapter" id="work-a-sound-must-earn-its-place">'
        f'<div class="book-chapter-heading"><h2 data-source-block="a-sound-must-earn-its-place.title">{NAME}</h2></div></section>'
        '<section class="book-chapter-text"><article class="book-prose">'
        '<p class="frame-edition-imprint" data-source-block="editorial.proof.status">Editorial proof · Unpublished draft</p>'
        + "".join(paragraphs) + '</article></section></div></template>'
    )
    return flow, len(paragraphs)

def relation_template():
    parts = [
        '<template id="press-proof-related"><section class="frame-press-proof-relations" '
        'role="group" aria-label="Editorial reading relations">',
        '<p class="frame-subheading" data-source-block="proof-relations.heading">Reading relations · editorial proof</p>',
        '<p data-source-block="proof-relations.explanation">These relationships are under editorial review. '
        'The essay and its proposed standard are not public releases.</p>',
    ]
    for n, (title, href) in enumerate(RELATED, 1):
        parts.append(
            f'<p data-source-block="proof-relations.related.{n}">Related published reading: '
            f'<a data-reader-related-public="true" href="{html.escape(href, quote=True)}">'
            f'{html.escape(title)}</a>.</p>'
        )
    parts += [
        '<p data-source-block="proof-relations.standard">Proposed standard: '
        'Audio Production and Artistic Acceptance · draft, not an adopted Governance chapter.</p>',
        '<p data-source-block="proof-relations.kino">Kino After Dark · private sound study; '
        'no public audio or staging link.</p>',
        '</section></template>'
    ]
    return "".join(parts)

def build(markdown_path, baseline_index, baseline_app, output):
    raw = Path(markdown_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("Source drift: briefing essay SHA-256 mismatch")
    essay = raw.decode("utf-8")
    index = Path(baseline_index).read_text(encoding="utf-8")
    app = Path(baseline_app).read_text(encoding="utf-8")
    if 'data-reader-volume="essay--a-sound-must-earn-its-place"' in index:
        raise ValueError("Stage predecessor already has this draft: reconcile, do not duplicate")
    if "shared-shell" not in index and 'data-reader-volume="publication-notes"' not in index:
        raise ValueError("Not the existing Reader baseline")
    template, count = make_template(essay)
    index = replace_once(index, '<template data-reader-volume="publication-notes">', template + "\n" +
        relation_template() + "\n" + '<template data-reader-volume="publication-notes">')
    app = replace_once(app, "const labels=new Map([", "const proofVolume='" + VOLUME + "';\nconst labels=new Map([")
    app = replace_once(app, "option.textContent=key.startsWith('essay--')?'Essays · '+label:'First Reading · '+label;",
        "option.textContent=key===proofVolume?'Editorial proof · '+label:key.startsWith('essay--')?'Essays · '+label:'First Reading · '+label;")
    app = replace_once(app, ".filter(x=>x.startsWith('essay--')&&!implementationStories.has(x)&&!archivedEssays.has(x)).reverse();",
        ".filter(x=>x.startsWith('essay--')&&!implementationStories.has(x)&&!archivedEssays.has(x)&&x!==proofVolume).reverse();")
    app = replace_once(app, "const contents={essays:essaySequence,'first-readings':solsticeSequence};",
        "const contents={essays:[...essaySequence,proofVolume],'first-readings':solsticeSequence};")
    app = replace_once(app, "if(essaySequence.includes(name)||archivedEssays.has(name)||name==='teatro'",
        "if(essaySequence.includes(name)||archivedEssays.has(name)||name===proofVolume||name==='teatro'")
    app = replace_once(app, "source.dataset.minLeaves='1';",
        "if(name==='publication-notes'&&addendumReturnVolume===proofVolume){\n"
        " const approvedPreview=document.getElementById('press-proof-related');\n"
        " if(approvedPreview)source.querySelector('.book-prose')?.append(approvedPreview.content.cloneNode(true));\n"
        "}\nsource.dataset.minLeaves='1';")
    app = replace_once(app, " const info=e.target.closest('[data-reader-info]');",
        " const related=e.target.closest('[data-reader-related-public]');\n"
        " if(related){\n"
        "  const address=positions.get(addendumReturnVolume);\n"
        "  if(!address||addendumReturnVolume!==proofVolume){\n"
        "   e.preventDefault();status.textContent='Original source position unavailable; relation not opened.';return;\n"
        "  }\n"
        "  history.replaceState({volume:addendumReturnVolume},'',\n"
        "   '/estate/#/read/'+addendumReturnVolume+'?at='+encodeURIComponent(address.block+'@'+address.offset));\n"
        "  lastHistoryLocation=location.href;return;\n"
        " }\n const info=e.target.closest('[data-reader-info]');")
    Path(output).mkdir(parents=True, exist_ok=True)
    (Path(output)/"index.html").write_text(index, encoding="utf-8")
    (Path(output)/"reading-first-app.js").write_text(app, encoding="utf-8")
    receipt = {
        "schema": "fountain.press.editorial-proof.v1",
        "sourceSHA256": SOURCE_SHA, "volume": VOLUME, "paragraphsAndHeadings": count,
        "sourceStatus": "verbatim-draft", "stagingOnly": True,
        "baseIndexSHA256": hashlib.sha256(Path(baseline_index).read_bytes()).hexdigest(),
        "baseAppSHA256": hashlib.sha256(Path(baseline_app).read_bytes()).hexdigest(),
        "outputIndexSHA256": hashlib.sha256(index.encode()).hexdigest(),
        "outputAppSHA256": hashlib.sha256(app.encode()).hexdigest(),
        "otherReaderVolumesModified": False,
        "linkedTargets": [url for _, url in RELATED],
        "privateKinoLinks": 0,
        "governanceChapterAdmitted": False,
    }
    (Path(output)/"editorial-proof-receipt.json").write_text(json.dumps(receipt, indent=2)+"\n")
    return receipt

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    for name in ("source", "baseline-index", "baseline-app", "output"):
        p.add_argument("--"+name, required=True)
    args=p.parse_args()
    print(json.dumps(build(args.source, args.baseline_index, args.baseline_app,args.output),indent=2))
