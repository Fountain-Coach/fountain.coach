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

BASE_SHA = "532dbdf6603fb1300a974418130c50cbc17636262d9dcf7c0a802c3aabfdd81c"
VOLUME = "essay--what-makes-a-page-modern"
PREFIX = "what-makes-a-page-modern"
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "site/essays/what-makes-a-page-modern/combined-essay.md"
SPECIMEN_SOURCE = ROOT / "site/essays/what-makes-a-page-modern/specimen-source.txt"
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

def semantic_specimen(raw: str, kind: str) -> str:
    """Compose real, addressable typography inside the parent Linotype measure.

    This replaces the old *image rendering* of the two historic source SVGs.
    The type is rebroken by the same Reader at every page width and font size.
    The source passage occurs once in specimen-source.txt and is projected
    into two deliberately different layouts without fixed image dimensions.
    """
    number, name = {"classical": ("I", "Classical measure"),
                    "modern": ("II", "Modernist measure")}[kind]
    if raw.count("<img ") != 1 or raw.count("<figcaption>") != 1:
        raise ValueError("Unexpected historical specimen illustration")
    historical_sha = re.search(r'data-source-plate-sha256="([a-f0-9]{64})"', raw)
    caption = re.search(r'<figcaption>(.*?)</figcaption>', raw, re.S)
    if not historical_sha or not caption:
        raise ValueError("Cannot identify original setting provenance")
    text = SPECIMEN_SOURCE.read_text(encoding="utf-8").rstrip("\n")
    if not text.startswith("A page is not a container") or len(text) < 350:
        raise ValueError("Unadmitted specimen source")
    digest_text = digest(SPECIMEN_SOURCE.read_bytes())
    source_id = PREFIX + ".specimen-source"
    # The original SVG remains an immutable historical asset, rather than
    # a second, fixed-size image masquerading as the live nested setting.
    return (
        '<figure class="frame-reading-figure linotype-typographic-specimen"'
        ' data-typographic-specimen="' + kind + '"'
        ' data-source-block="' + PREFIX + '.plate.' + kind + '"'
        ' data-historical-plate-sha256="' + historical_sha.group(1) + '"'
        ' data-specimen-source-sha256="' + digest_text + '">'
        '<header class="linotype-specimen-label" aria-label="Type specimen ' +
        number + ', ' + name.lower() + '">'
        '<span>ONE PASSAGE / TWO SETTINGS</span>'
        '<span>SPECIMEN ' + number + ' · ' + name.upper() + '</span>'
        '</header>'
        '<div class="linotype-specimen-setting">'
        '<h3 class="linotype-specimen-title">THE PAGE</h3>'
        '<p class="linotype-specimen-text" data-source-unit-id="' + source_id +
        '" data-source-setting="' + kind + '"'
        ' data-source-block="' + source_id + '.' + kind + '"'
        ' data-source-from="0" data-source-to="' + str(len(text)) + '">' +
        html.escape(text, quote=False) + '</p>'
        '</div>'
        '<figcaption>' + caption.group(1) + '</figcaption>'
        '</figure>'
    )


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
            plate = semantic_specimen(figures[key],key) if key in ("classical","modern") else figures[key]
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
    # The inherited essay-local figure reset used !important to flatten the
    # SVG illustrations against the page measure. That is correct for images,
    # but DESTROYS horizontal insets in an actual nested typographic setting.
    # Restrict that reset to the remaining true artwork, by one exact edit
    # inside the already-authorized essay-local stylesheet.
    style_rx = re.compile(r'<style id="modern-page-figure-measure">.*?</style>', re.S)
    old_styles = style_rx.findall(document)
    if len(old_styles) != 1:
        raise ValueError("Cannot reconcile existing essay-local padding rule")
    image_rule = 'figure[data-source-block^="' + PREFIX + '.plate."]'
    inline_rule = 'figure.linotype-inline-illustration[data-source-block^="' + PREFIX + '.plate."]'
    if old_styles[0].count(image_rule) != 4 or old_styles[0].count(inline_rule) != 1:
        raise ValueError("Unexpected essay-local image CSS")
    new_styles = old_styles[0].replace(
        image_rule, image_rule + ':not([data-typographic-specimen])').replace(
        inline_rule, inline_rule + ':not([data-typographic-specimen])')
    if new_document.count(old_styles[0]) != 1:
        raise ValueError("Missing original essay CSS in new Reader")
    new_document = new_document.replace(old_styles[0], new_styles, 1)
    # Exactly the source-bound essay and its image-only reset are allowed
    # to change here. The actual Press engine/CSS are separately pinned.
    before_outside = document.replace(match.group(), "[SOURCE]", 1).replace(
        old_styles[0], "[SPECIMEN-STYLES]", 1)
    after_outside = new_document.replace(new_template, "[SOURCE]", 1).replace(
        new_styles, "[SPECIMEN-STYLES]", 1)
    if before_outside != after_outside:
        raise ValueError("Unreviewed Reader shell or template mutation")
    if len(re.findall(r'data-source-block="' + PREFIX + r'\.plate\.', new_template)) != 12:
        raise ValueError("Expected eleven inline plates and existing hero illustration")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(new_document.encode("utf-8"))
    receipt = {
        "schema": "fountain.press.nested-type-measure.v1",
        "readerVolume": VOLUME,
        "readerEngineChanged": True,
        "changedSourceOnly": False,
        "nestedComposition": "measured-and-source-addressed",
        "specimenSourceSHA256": digest(SPECIMEN_SOURCE.read_bytes()),
        "reflowingTypeSpecimens": 2,
        "preservedActualImageFigures": 10,
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
