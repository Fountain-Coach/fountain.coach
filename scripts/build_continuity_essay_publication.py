#!/usr/bin/env python3
"""Build the complete source-owned Reading Continuity essay page without changing established essays."""
from pathlib import Path
import re, html, json, hashlib, subprocess

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
ARCHIVE=SITE/"essays"
DEST=ARCHIVE/"to-read-is-not-to-remember"
CANON="https://fountain.coach/essays/to-read-is-not-to-remember/"
SRC=ARCHIVE/"index.html"
intro=(DEST/"editorial-introduction.md").read_text()
pd=subprocess.run(["pandoc","--from=markdown+smart","--to=html5","--wrap=none"],input=intro,text=True,capture_output=True,check=True)
intro_html=pd.stdout
assert "<h1" in intro_html and "It must become an accountable reader." in intro_html

existing=SRC.read_text()
header=re.search(r'<header class="site-header".*?</header>',existing,re.S).group(0)
footer=re.search(r'<footer id="footer".*?</footer>',existing,re.S).group(0)
path="/essays/to-read-is-not-to-remember/"
img=path+"assets/bookshelf-ipad-landscape-test.png"
pdf=path+"to-read-is-not-to-remember.pdf"

page=f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="fountain:publication-role" content="essay, editorial introduction and primary PDF">
<title>Did the Machine Actually Read the Book? · Fountain Coach</title>
<meta name="description" content="On artificial intelligence, reading continuity, semantic drift and the limits of model memory. An editorial introduction to To Read Is Not to Remember.">
<link rel="canonical" href="{CANON}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Fountain Coach">
<meta property="og:title" content="Did the Machine Actually Read the Book?">
<meta property="og:description" content="On AI, memory, Reading Continuity and the evidence of understanding.">
<meta property="og:url" content="{CANON}">
<meta property="og:image" content="https://fountain.coach{img}">
<meta property="og:image:alt" content="Real Fountain Coach Bookshelf iPad landscape visual test, showing two editions and empty publication slots">
<meta property="article:published_time" content="2026-10-17">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"ScholarlyArticle","headline":"To Read Is Not to Remember","alternativeHeadline":"Did the Machine Actually Read the Book?","mainEntityOfPage":CANON,"datePublished":"2026-10-17","publisher":{"@type":"Organization","name":"Fountain Coach","url":"https://fountain.coach/"},"image":"https://fountain.coach"+img,"encodingFormat":"application/pdf","url":"https://fountain.coach"+pdf},ensure_ascii=False)}</script>
<link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/estate-core.css">
<script src="/assets/estate-core.js" defer></script>
<style>
.reading-essay .essay-prose{{max-width:69ch;margin-inline:auto}}
.reading-essay .essay-prose p{{font-size:clamp(1.06rem,1.9vw,1.22rem);line-height:1.78;margin:0 0 1.28em;}}
.reading-essay .essay-prose h1{{font-weight:400;font-size:clamp(1.7rem,4vw,2.5rem);line-height:1.22;margin:0 0 .35em}}
.reading-essay .essay-prose h1 + p{{font-style:italic;opacity:.8;margin-bottom:2em}}
.reading-essay .essay-hero{{max-width:1050px;margin:2.8rem auto 3.2rem}}
.reading-essay .essay-hero img{{width:100%;height:auto;display:block;object-fit:contain}}
.reading-essay .essay-hero figcaption{{max-width:75ch;font-size:.84rem;line-height:1.52;margin:1rem auto;color:inherit;opacity:.72}}
.reading-essay .paper-intro{{max-width:69ch;margin:2.5rem auto 1.2rem}}
.reading-essay .paper-intro h2{{font-size:clamp(1.5rem,3vw,2rem);font-weight:400;line-height:1.35}}
.reading-essay .paper-intro p{{line-height:1.68}}
.reading-essay .pdf-actions{{display:flex;gap:1.3rem;flex-wrap:wrap;margin:1.2em 0 1.6em}}
.reading-essay .pdf-actions a{{text-decoration:underline;text-underline-offset:.2em}}
.reading-essay .pdf-frame{{width:100%;height:min(90vh,1000px);min-height:520px;border:1px solid currentColor;background:#f8f6f0;}}
.reading-essay .pdf-wrap{{max-width:1060px;margin:0 auto 4rem}}
@media(max-width:670px){{.reading-essay .pdf-frame{{height:68vh;min-height:380px}}.reading-essay .essay-prose p{{line-height:1.66}}}}
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{header}
<main id="main" class="layout essay-page reading-essay">
<nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a class="breadcrumb-root" href="/"><img src="/assets/fountain-coach-logo-transparent.png" alt=""><span>Fountain Coach</span></a></li><li><a href="/essays/">Essays</a></li><li aria-current="page">Reading Continuity</li></ol></nav>
<article class="essay-article">
<header class="essay-header"><div class="eyebrow">Essay · Reading Continuity · 17 October 2026</div></header>
<div class="essay-prose">
{intro_html}
</div>
<figure class="essay-figure essay-hero">
<img src="assets/bookshelf-ipad-landscape-test.png" width="1180" height="820" alt="Actual iPad landscape visual-test capture of the Fountain Coach Bookshelf with its publisher mark, two book covers and empty publication slots." loading="lazy">
<figcaption>Fountain Coach Bookshelf, iPad landscape visual test (<a href="https://github.com/Fountain-Coach/fountain.coach/tree/main/docs/qa/first-readings-v38">first-readings-v38</a>). This records a tested interface projection; it is not evidence that a model understood a book.</figcaption>
</figure>
<section class="paper-intro" aria-labelledby="full-paper">
<div class="eyebrow">Full-length scholarly essay · PDF</div>
<h2 id="full-paper">To Read Is Not to Remember</h2>
<p><em>Interpretation, Discontinuity, and the Making of a Durable Reader.</em> The full essay reconstructs Reframe's technical and intellectual development, examining reading continuity, compiled knowledge, two forms of drift calculus, the actual <em>Ulysses</em> experiments, and the limits of what present implementations prove. Includes documentary genesis and scientific references.</p>
<nav class="pdf-actions" aria-label="Full essay PDF options">
<a href="to-read-is-not-to-remember.pdf" type="application/pdf" target="_blank" rel="noopener">Open the complete essay (PDF)</a>
<a href="to-read-is-not-to-remember.pdf" download="To Read Is Not to Remember.pdf">Download PDF</a>
</nav>
</section>
<div class="pdf-wrap">
<object class="pdf-frame" data="to-read-is-not-to-remember.pdf#view=FitH" type="application/pdf" aria-label="Read To Read Is Not to Remember, the complete scholarly essay">
<p>The embedded PDF is not supported in this browser. <a href="to-read-is-not-to-remember.pdf">Open the complete essay as a PDF.</a></p>
</object>
</div>
<aside class="essay-boundary" aria-label="Publication boundary"><strong>Editorial inquiry, not governance authority.</strong> The essay distinguishes proposed capabilities from tested evidence; technical acceptance and normative governance remain separately recorded.</aside>
</article>
</main>
{footer}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''
assert page.count('<object class="pdf-frame"')==1
(DEST/"index.html").write_text(page)
assert (DEST/"to-read-is-not-to-remember.pdf").read_bytes().startswith(b"%PDF-")
assert hashlib.sha256((DEST/"assets/bookshelf-ipad-landscape-test.png").read_bytes()).hexdigest()==hashlib.sha256((ROOT/"docs/qa/first-readings-v38/ipad-landscape-estate.png").read_bytes()).hexdigest()
gallery='''<article class="essay-gallery-card" data-essay-route="/essays/to-read-is-not-to-remember/"><a class="essay-gallery-image" href="/essays/to-read-is-not-to-remember/"><img src="/essays/to-read-is-not-to-remember/assets/bookshelf-ipad-landscape-test.png" width="1180" height="820" alt="The Fountain Coach Bookshelf in an iPad landscape implementation test"></a><div class="essay-gallery-copy"><div class="eyebrow">04 · ESSAY</div><h3><a href="/essays/to-read-is-not-to-remember/">Did the Machine Actually Read the Book?</a></h3><p>Reading Continuity, Drift Calculus and an accountable history of interpretation. Includes the complete illustrated scholarly PDF.</p></div></article>'''
anchor='</div><nav class="essay-pagination"'
assert existing.count(anchor)==1
if 'data-essay-route="/essays/to-read-is-not-to-remember/"' not in existing:
    SRC.write_text(existing.replace(anchor,gallery+anchor))
else:
    assert existing.count('data-essay-route="/essays/to-read-is-not-to-remember/"')==1
print("BUILT", DEST, "pdf", (DEST/"to-read-is-not-to-remember.pdf").stat().st_size,"bytes")
