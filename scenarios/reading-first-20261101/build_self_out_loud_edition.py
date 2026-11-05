#!/usr/bin/env python3
"""Compose one revised essay in the existing, source-bound Fountain Press Reader.

Input: exact already-accepted v146 WLAN release HTML and the author-approved
combined manuscript in fountain.coach. Output: changed Reader content only.
No new reader, engine, stylesheet, server, audio, MIDI event or public route.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

BASE_SHA = "11cd731753769f5feacd2f91dc2ba1fc8c0e914d5d107b00f9c98ad58eff3c2c"
VOLUME = "essay--what-makes-a-page-modern"
PREFIX = "what-makes-a-page-modern"
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "site/essays/what-makes-a-page-modern/combined-essay.md"
FIGURES = (
    "classical", "modern", "machine", "joyce", "proof", "reader",
    "address", "cursor", "midi", "return", "conditions"
)
TEMPLATE_RX = re.compile(
    r'(<template data-reader-volume="' + VOLUME + r'">)(.*?)(</template>)', re.S
)
ARTICLE_RX = re.compile(r'<article class="book-prose">.*?</article>', re.S)
FIGURE_RX = re.compile(
    r'<figure [^>]*data-source-block="' + PREFIX +
    r'\.plate\.([^"]+)"[^>]*>.*?</figure>', re.S
)
PROEM_RX = re.compile(
    r'(<aside class="frame-editorial-proem"[^>]*>)(.*?)(</aside>)', re.S
)

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def slugify(s: str) -> str:
    s = s.lower().replace("'", "")
    s = re.sub(r'[^a-z0-9]+', "-", s).strip("-")
    if not s:
        raise ValueError("Missing heading source identity")
    return s

def framed_specimen(raw: str, kind: str) -> str:
    """Make the two type-settings identifiable as stage-within-stage plates.

    The SVG art remains byte-for-byte unchanged; a measured, bordered inset
    and its accessible label belong to THIS essay's source projection only.
    The specimen text appears exactly once in each plate, not in body prose.
    """
    number, name = {"classical": ("I", "classical measure"),
                    "modern": ("II", "modernist measure")}[kind]
    prefix = '<figure class="frame-reading-figure"'
    if raw.count(prefix) != 1 or raw.count("<img ") != 1:
        raise ValueError("Unexpected existing author-owned figure structure")
    # The frame is part of the source-owned nested typographic specimen, NOT
    # a new page, reader component or cross-book stylesheet.
    raw = raw.replace(prefix, prefix + (
        ' data-typographic-specimen="' + kind + '"'
        ' style="box-sizing:border-box;max-width:100%;background:#fbfaf6;'
        'border:1px solid #b0a99d;padding:1rem 1rem .85rem;'
        'margin-block:1.15rem 1.35rem;break-inside:avoid;"'
    ), 1)
    label = (
        '<div role="note" aria-label="Typography experiment, specimen ' + number + 
        ', ' + name + '" style="box-sizing:border-box;display:flex;flex-wrap:wrap;'
        'justify-content:space-between;align-items:baseline;gap:.25rem .9rem;'
        'width:100%;border-bottom:1px solid #b0a99d;padding-bottom:.6rem;margin-bottom:.8rem;'
        'font:600 .65rem/1.35 system-ui,sans-serif;letter-spacing:.11em;'
        'text-transform:uppercase;color:#5e584d;">'
        '<span>ONE PASSAGE / TWO SETTINGS</span>'
        '<span>SPECIMEN ' + number + ' · ' + name.upper() + '</span>'
        '</div>'
    )
    raw = raw.replace("<img ", label + "<img ", 1)
    return raw


def compose(source: str, figures: dict[str, str]) -> tuple[str, dict]:
    lines = source.splitlines()
    if lines[0].strip() != "# What Makes a Page Modern?":
        raise ValueError("Unexpected authored title")
    if lines[1].strip() != "The printed, spoken and addressable page — and Self Out Loud":
        raise ValueError("Unexpected subtitle")
    pieces: list[str] = []
    heading = None
    counts: dict[str, int] = {}
    paragraph_position = 0  # same narrative paragraph numbering as the existing compositor
    authored_anchors: list[dict] = []
    used_figures: list[str] = []
    i = 2
    headings: list[str] = []
    paragraphs = []
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            key = slugify(heading)
            if key in headings:
                raise ValueError("Duplicate heading: " + key)
            headings.append(key)
            pieces.append(
                '<p class="frame-subheading" data-source-block="' +
                PREFIX + '.' + key + '.heading" data-source-from="0" ' +
                'data-source-to="' + str(len(heading)) + '">' +
                html.escape(heading) + "</p>"
            )
            paragraph_position += 1
            continue
        if heading is None:
            raise ValueError("Text not attached to any heading")
        if line.startswith("[[plate:") and line.endswith("]]"):
            key = line[len("[[plate:"):-2]
            if key not in figures or key in used_figures:
                raise ValueError("Unknown or repeated source plate: " + key)
            used_figures.append(key)
            if paragraph_position < 1:
                raise ValueError("A source plate has no preceding narrative position")
            plate = framed_specimen(figures[key],key) if key in ("classical","modern") else figures[key]
            # Existing Reader accepts a precise author-specified prose anchor.
            # Without this, its fallback spreads all figures by equal intervals,
            # destroying each specimen's relationship with its explanation.
            plate = plate.replace("<figure ", '<figure data-inline-after-paragraph="' +
                str(paragraph_position) + '" ', 1)
            authored_anchors.append({"figure":key,"afterParagraph":paragraph_position})
            pieces.append(plate)
            continue
        is_specimen = line.startswith("> ")
        if is_specimen:
            line = line[2:]
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(("## ","[[plate:")):
            line += " " + lines[i].strip()
            i += 1
        sec = slugify(heading)
        counts[sec] = counts.get(sec, 0) + 1
        block = PREFIX + "." + sec + ".p" + str(counts[sec])
        attrs = (' class="frame-lead"' if is_specimen else '')
        if is_specimen:
            attrs += ' data-source-unit-id="' + PREFIX + '.specimen"'
        pieces.append(
            "<p" + attrs + ' data-source-block="' + block +
            '" data-source-from="0" data-source-to="' + str(len(line)) + '">' +
            html.escape(line, quote=False) + "</p>"
        )
        paragraphs.append((block,line))
        paragraph_position += 1
    if set(used_figures) != set(FIGURES):
        raise ValueError("Missing original illustrations: " + repr(set(FIGURES)-set(used_figures)))
    if len(headings) < 13 or len(paragraphs) < 50:
        raise ValueError("Incomplete revised essay")
    if "self-out-loud" not in headings:
        raise ValueError("Self Out Loud section missing")
    if not any("The writer is the first actor" in p for _,p in paragraphs):
        raise ValueError("Missing writer-as-actor argument")
    if not any("Only the writer authorizes" in p for _,p in paragraphs):
        raise ValueError("Six-condition closure is missing")
    article = '<article class="book-prose">' + ''.join(pieces) + '</article>'
    return article, {"headingSlugs":headings,"paragraphs":len(paragraphs),
                     "sourceAnchoredPlates":authored_anchors,
                     "originalInlinePlates":used_figures,
                     "sourceBlocks":len(paragraphs)+len(headings)+len(used_figures)}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True, help="exact v146 existing Reader HTML")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    raw = args.base.read_bytes()
    if digest(raw) != BASE_SHA:
        raise ValueError("Refuse to edit an unknown Reader baseline: " + digest(raw))
    document = raw.decode("utf-8")
    templates = list(TEMPLATE_RX.finditer(document))
    if len(templates) != 1:
        raise ValueError("Original Reader volume missing or duplicated")
    match = templates[0]
    body = match.group(2)
    articles = list(ARTICLE_RX.finditer(body))
    if len(articles) != 2:
        raise ValueError("Unexpected editorial article structure")
    figures = {m.group(1):m.group(0) for m in FIGURE_RX.finditer(articles[0].group())}
    if set(figures) != set(FIGURES):
        raise ValueError("Existing author-owned semantic diagrams changed")
    manuscript = SOURCE.read_bytes()
    edited_article, info = compose(manuscript.decode("utf-8"), figures)
    edited = body[:articles[0].start()] + edited_article + body[articles[0].end():]
    replacement_proem = (
      '<span class="frame-editorial-kicker">From the editor</span>'
      '<p>The same passage passes through classical setting, modern typography, '
      'the returned proof and an addressable page. Self Out Loud lets the writer’s '
      'own voice enter the argument: not as a finished performance, but as an '
      'instrument through which the writing may continue.</p>'
    )
    edited, n = PROEM_RX.subn(
       lambda m:m.group(1)+replacement_proem+m.group(3), edited, count=1)
    if n != 1:
        raise ValueError("Original editorial preface not found")
    articles = list(ARTICLE_RX.finditer(edited))
    new_colophon = (
        '<article class="book-prose">'
        '<p class="frame-subheading" data-source-block="editorial.colophon.'+PREFIX+'">About this setting</p>'
        '<p data-source-block="editorial.colophon.'+PREFIX+'.p1">This revised essay joins the original '
        'illustrated typographic inquiry with Self Out Loud. The classical, modernist and printer’s-proof '
        'settings retain their own composition; the page remains a measured and addressable field.</p>'
        '<p data-source-block="editorial.colophon.'+PREFIX+'.p2">Existing synthetic readings illustrate '
        'source-linked listening. The writer-operated live voice cursor, pronunciation assistance and '
        'other Self Out Loud possibilities remain an invitation to develop the instrument, not a claim '
        'that this edition already performs them.</p></article>'
    )
    edited = edited[:articles[1].start()] + new_colophon + edited[articles[1].end():]
    source_sha = digest(manuscript)
    edited = re.sub(
       r'data-source-work-sha256="[a-f0-9]{64}"',
       'data-source-work-sha256="' + source_sha + '"', edited, count=1)
    new_template = match.group(1) + edited + match.group(3)
    new_document = document[:match.start()] + new_template + document[match.end():]
    # Exactly one source volume changes. No outside script, shell or reader mutation.
    if new_document.replace(new_template, "[SOURCE]", 1) != document.replace(match.group(), "[SOURCE]", 1):
        raise ValueError("Non-essay Reader bytes changed")
    if len(re.findall(r'data-source-block="' + PREFIX + r'\.plate\.', new_template)) != 12:
        raise ValueError("Expected eleven inline plates and existing hero illustration")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(new_document.encode("utf-8"))
    receipt = {
        "schema": "fountain.press.modern-page-self-out-loud-edition.v1",
        "readerVolume": VOLUME,
        "readerEngineChanged": False,
        "changedSourceOnly": True,
        "previousReaderRootSHA256": BASE_SHA,
        "revisedReaderRootSHA256": digest(args.out.read_bytes()),
        "revisedManuscriptSHA256": source_sha,
        "earlierDruckfahnePDFSHA256": "2baaab0012e825b49f04e7a760b64efa52c95dc09deab7117de790f6c6e14bad",
        "renderedFigureCount": 12,
        "originalIllustrationsUnchanged": True,
        "authorApprovedRevision": True,
        "liveVoiceCursorApproved": False,
        "publicPublished": False,
        **info
    }
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
