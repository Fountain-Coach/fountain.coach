#!/usr/bin/env python3
"""Deterministic source-to-HTML projection of the Composable Book product essay.
Only the Markdown source and source-controlled SVG plates define its content.
No model, network, environment, publishing side-effect or runtime build.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/product-essays/the-composable-book.md"
OUT = ROOT / "site/essays/the-composable-book/index.html"
COLLECTION = ROOT / "site/essays/index.html"
BASE = "https://fountain.coach/essays/the-composable-book/"
TITLE = "The Composable Book"
DESC = ("A book that can become what its writer imagines. Reframe, Composer, "
        "the DOM, and governed semantic languages across platforms.")

def inline(raw: str) -> str:
    text = html.escape(raw, quote=True)
    def link(match: re.Match[str]) -> str:
        caption, url = match.group(1), html.unescape(match.group(2))
        if not (url.startswith("https://") or url.startswith("#") or url.startswith("/")):
            raise ValueError(f"Untrusted link target: {url}")
        return f'<a href="{html.escape(url, quote=True)}">{caption}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', link, text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    return text

def parse(md: str):
    blocks = [part.strip() for part in re.split(r'\n\s*\n', md.replace('# The Composable Book\n*', '# The Composable Book\n\n*', 1)) if part.strip()]
    if not blocks or blocks[0] != "# The Composable Book":
        raise ValueError("Unknown product essay source title")
    if not blocks[1].startswith("*"):
        raise ValueError("Expected editorial subtitle")
    subtitle = re.sub(r'^\*|\*$', '', blocks[1])
    sections: list[tuple[str, str]] = []
    paragraphs = 0
    figures = []
    rendered = []
    for part in blocks[2:]:
        if part.startswith("## "):
            match = re.fullmatch(r"## (.+?) \{#([a-z-]+)\}", part)
            if not match:
                raise ValueError(f"Unaddressed section: {part}")
            label, ident = match.groups()
            sections.append((label, ident))
            rendered.append(f'<h2 id="{ident}">{inline(label)}</h2>')
        elif part.startswith(":::figure "):
            match = re.fullmatch(r":::figure ([a-z0-9-]+\.svg) \| (.+?) \| ([a-z]+)", part)
            if not match:
                raise ValueError(f"Invalid figure contract: {part}")
            asset, caption, ident = match.groups()
            if not (OUT.parent / "assets" / asset).exists():
                raise FileNotFoundError(asset)
            figures.append((ident, asset))
            rendered.append(
                f'<figure class="editorial-plate" id="plate-{ident}">'
                f'<a href="assets/{asset}" title="Open full vector illustration" aria-label="Open full vector illustration: {html.escape(caption, quote=True)}">'
                f'<img src="assets/{asset}" alt="{html.escape(caption, quote=True)}" loading="lazy" width="1400" height="820"></a>'
                f'<figcaption><span>FIG. {len(figures):02d}</span>{inline(caption)}</figcaption>'
                f'</figure>'
            )
        elif part.startswith(":::aside "):
            rendered.append(f'<aside class="essay-claim" aria-label="Editorial claim boundary">{inline(part[9:])}</aside>')
        elif part.startswith("#"):
            raise ValueError(f"Unsupported heading: {part}")
        else:
            paragraphs += 1
            rendered.append(f'<p>{inline(" ".join(part.splitlines()))}</p>')
    if len(sections) != 8 or len(figures) != 4 or paragraphs < 27:
        raise ValueError(f"Incomplete essay: {len(sections)} sections, {len(figures)} figures, {paragraphs} paragraphs")
    if len(set(i for _, i in sections)) != len(sections):
        raise ValueError("Duplicate section address")
    return subtitle, sections, rendered, figures, paragraphs

def build():
    subtitle, sections, content, figures, paragraphs = parse(SOURCE.read_text(encoding="utf-8"))
    navigation = "\n".join(
        f'<a href="#{ident}">{html.escape(label)}</a>' for label, ident in sections
    )
    reading = [
        ("Reframe — Product", "https://fountain.coach/",
         "Reframe public estate; Mac implementation source is collaborator-only"),
        ("Chapter 58 — Open-turn mediation", "https://governance.fountain.coach/chapters/58-open-turn-mediation-protocol/",
         "Public governance behind the draft R27 collaboration scenario"),
        ("Chapter 83 — Conversational authoring", "https://governance.fountain.coach/chapters/83-conversational-scenario-authoring/",
         "How writer and model design executable scenarios"),
        ("Chapter 108 — Portable runtime", "https://governance.fountain.coach/chapters/108-reframe-is-a-swift-native-cross-platform-runtime/",
         "Platform-neutral semantics and execution"),
        ("Chapter 124 — Timed WebKit", "https://governance.fountain.coach/chapters/124-midi2-timed-webkit-transitions/",
         "DOM as governed visual surface"),
        ("Semantic Compilation essay", "/essays/semantic-compilation-the-archive-is-not-the-edition/",
         "An edition is authored, not harvested"),
        ("Reframe and Business Value", "/essays/reframe-and-the-business-value-of-the-estate/",
         "Why independent publishing needs operational identity"),
        ("Teatro essay", "/essays/teatro-an-unfinished-composition/",
         "An unfinished composition")
    ]
    references = "\n".join(
        f'<li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a><span>{html.escape(detail)}</span></li>'
        for label, url, detail in reading
    )
    metadata = json.dumps({
        "@context": "https://schema.org", "@type": "Article", "headline": TITLE,
        "description": DESC, "mainEntityOfPage": BASE,
        "datePublished": "2026-10-18",
        "author": {"@type": "Organization", "name": "Fountain Coach"},
        "publisher": {"@type": "Organization", "name": "Fountain Coach", "url": "https://fountain.coach/"},
        "image": BASE + "assets/cover.png"
    }, ensure_ascii=False).replace("<", "\\u003c")
    document = f"""<!doctype html>
<html lang="en" data-publication-state="source-candidate">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light"><meta name="robots" content="index,follow">
<meta name="description" content="{html.escape(DESC, quote=True)}">
<title>{TITLE} — Fountain Coach</title>
<link rel="canonical" href="{BASE}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Fountain Coach">
<meta property="og:title" content="{TITLE}"><meta property="og:description" content="{html.escape(DESC, quote=True)}">
<meta property="og:url" content="{BASE}"><meta property="og:image" content="{BASE}assets/cover.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{metadata}</script>
<link rel="stylesheet" href="assets/essay.css">
</head>
<body>
<a class="skip" href="#essay">Skip to essay</a>
<header class="book-header"><a class="identity" href="/" aria-label="Fountain Coach editions"><img src="/assets/fountain-coach-logo-transparent.png" alt="" width="30" height="30"><span>FOUNTAIN COACH</span></a><nav aria-label="Publication navigation"><a href="https://works.benedikt-eickhoff.de/solstice/editions/first-reading/">First Reading</a><a href="/essays/">Essays</a><a href="/essays/">Collection</a></nav></header>
<main id="essay">
  <div class="essay-cover">
    <p class="overline">PRODUCT ESSAY <span>·</span> OCTOBER 2026</p>
    <h1>{TITLE}</h1>
    <p class="deck">{inline(subtitle)}</p>
    <p class="edition-meta">REFRAME / COMPOSER / SEMANTIC LANGUAGES / THE DOM</p>
  </div>
  <div class="essay-body-grid">
    <aside class="contents" aria-label="In this essay"><p>IN THIS ESSAY</p><nav>{navigation}</nav><a class="contents-end" href="#references">Sources and connections ↗</a></aside>
    <article class="essay-article" aria-label="The Composable Book essay">
      {"".join(content)}
      <section class="references" id="references" aria-labelledby="references-title"><p class="overline">CONTINUE READING</p><h2 id="references-title">A connected argument</h2><p>These routes separate the conceptual proposal from the existing implementations, independent essays, and governing contracts.</p><ul>{references}</ul></section>
    </article>
  </div>
</main>
<footer class="book-footer">
  <div><a href="/">Fountain Coach</a> <span>·</span> <a href="https://works.benedikt-eickhoff.de/solstice/editions/first-reading/">First Reading</a> <span>·</span> <a href="/essays/">Original essays</a> <span>·</span> <a href="https://governance.fountain.coach/">Governance</a></div>
  <p>Fountain Coach · Product essay · An authored interpretation, not an executable governance instrument.</p>
</footer>
</body></html>
"""
    # Derive the domain-wide estate frame from the published source-owned
    # collection, not an independently invented page masthead. Keep the
    # editorial body as the book's own restrained typographic projection.
    shell = COLLECTION.read_text(encoding="utf-8")
    shared_header = re.search(r'<header class="site-header" role="banner">.*?</header>', shell, re.S)
    shared_footer = re.search(r'<footer id="footer".*?</footer>', shell, re.S)
    if not shared_header or not shared_footer:
        raise ValueError("Fountain Coach estate shell unavailable")
    document, n = re.subn(r'<header class="book-header">.*?</header>',
                          lambda _: shared_header.group(), document, count=1, flags=re.S)
    if n != 1:
        raise ValueError("Composer essay header projection drift")
    document, n = re.subn(r'<footer class="book-footer">.*?</footer>',
                          lambda _: shared_footer.group(), document, count=1, flags=re.S)
    if n != 1:
        raise ValueError("Composer essay footer projection drift")
    document = document.replace('<body>', '<body class="composable-book">', 1)
    document = document.replace('data-publication-state="source-candidate"',
                                'data-publication-state="published"', 1)
    document = document.replace('<a class="skip" href="#essay">Skip to essay</a>',
                                '<a class="skip-link" href="#essay">Skip to essay</a>', 1)
    document = document.replace('<main id="essay">',
        '<main id="essay" class="composable-publication">'
        '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'
        '<li><a class="breadcrumb-root" href="/">'
        '<img src="/assets/fountain-coach-logo-transparent.png" alt="Fountain Coach logo">'
        '<span>Fountain Coach</span></a></li>'
        '<li><a href="/essays/">Essays</a></li>'
        '<li aria-current="page">The Composable Book</li></ol></nav>', 1)
    document = document.replace('<link rel="stylesheet" href="assets/essay.css">',
        '<link rel="icon" type="image/png" href="/assets/fountain-coach-logo-transparent.png">'
        '<link rel="stylesheet" href="/assets/site.css">'
        '<link rel="stylesheet" href="/assets/estate-core.css">'
        '<script src="/assets/estate-core.js" defer></script>'
        '<link rel="stylesheet" href="assets/essay.css">', 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(document, encoding="utf-8")
    # The collection index is source-owned; add the new product essay card, without
    # modifying the three existing original essay cards or their source pages.
    collection=COLLECTION.read_text(encoding="utf8")
    gallery_end='</div><nav class="essay-pagination"'
    if collection.count(gallery_end)!=1:
        raise ValueError("Essay collection gallery shape drift")
    marker='data-essay-route="/essays/the-composable-book/"'
    new_card=(
      '<article class="essay-gallery-card" '+marker+'>'
      '<a class="essay-gallery-image" href="/essays/the-composable-book/">'
      '<img src="/essays/the-composable-book/assets/cover.png" width="1200" height="630" '
      'alt="The Composable Book: continuous cream folio, source reading and Composer in dialogue"></a>'
      '<div class="essay-gallery-copy"><div class="eyebrow">PRODUCT ESSAY · REFRAME</div>'
      '<h3><a href="/essays/the-composable-book/">The Composable Book</a></h3>'
      '<p>A book that can become what its writer imagines: Composer, semantic languages and DOM-backed forms.</p>'
      '</div></article>'
    )
    if marker not in collection:
        original_gallery_open='<div class="essay-gallery" data-essay-gallery data-page-size="6" aria-label="Essay illustration gallery">'
        if collection.count(original_gallery_open)!=1:
            raise ValueError("Essay gallery opening shape drift")
        collection=collection.replace(original_gallery_open,original_gallery_open+new_card,1)
        collection=collection.replace('Page 1 of 1','Page 1 of 1')
        COLLECTION.write_text(collection,encoding="utf8")
    elif collection.count(marker)!=1:
        raise ValueError("Duplicated Composable Book collection card")
    print(f"PRODUCT_ESSAY_RENDERED sections={len(sections)} figures={len(figures)} paragraphs={paragraphs} bytes={OUT.stat().st_size}")
if __name__ == "__main__":
    build()
