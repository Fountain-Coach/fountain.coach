#!/usr/bin/env python3
"""Source-owned reading-first WLAN candidate; no production effect."""
from pathlib import Path
import re, html, json, hashlib
w=Path(__file__).resolve().parent
original=(w/'previous-about-source.html').read_text()
prose=re.search(r'<article class="book-prose">(.*?)</article>',original,re.S)
assert prose,'Previous author-approved About prose unavailable'
paragraphs=[html.unescape(re.sub(r'<[^>]*>','',p)) for p in re.findall(r'<p[^>]*>(.*?)</p>',prose.group(1),re.S)]
assert len(paragraphs)==9,(len(paragraphs),paragraphs)
assert paragraphs[0].startswith('Fountain Coach began with a question about continuity.')
assert paragraphs[-1]=='The invitation is simply to read.'
flow=''.join('<p class="'+('frame-lead' if i==0 else 'frame-prose')+'" data-source-block="continuity.p'+str(i+1)+'" data-source-from="0" data-source-to="'+str(len(p))+'">'+html.escape(p)+'</p>' for i,p in enumerate(paragraphs))
flow+='''<p class="frame-source" data-source-block="continuity.sources">Historical source: <a href="https://github.com/Fountain-Coach/fountain-manifesto/blob/main/index.html">Original Fountain Coach manifesto</a>.</p>
<p class="frame-source" data-source-block="continuity.publisher">Benedikt Eickhoff · Author. Fountain Coach · Publisher. <a href="https://status.fountain.coach/">Company and legal information</a>.</p>'''
page='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="color-scheme" content="light dark"/>
<meta name="robots" content="noindex,nofollow"/>
<meta name="fountain:publication-role" content="Fountain Coach opening matter, source-authored Fountain Press edition"/>
<meta name="description" content="Fountain Coach began with a question about continuity. Read the history from FountainAI to Reframe."/>
<link rel="canonical" href="https://fountain.coach/"/>
<title>Fountain Coach — On Continuity</title>
<link rel="icon" href="/estate/assets/fountain-coach-logo-transparent.png"/>
<link rel="preload" as="image" href="/estate/assets/estate-bookshelf/fountain-coach-edition.png"/>
<link rel="preload" as="image" href="/estate/assets/estate-bookshelf/first-reading-ink.png"/>
<link rel="stylesheet" href="/estate/assets/linotype/reading-first-press-frame.css"/>
<link rel="stylesheet" href="/estate/assets/linotype/reading-first-press-host.css"/>
<link rel="stylesheet" href="/estate/assets/linotype/reading-first-shell.css"/>
<script>document.documentElement.classList.add('js');</script>
<script defer src="/estate/assets/linotype/reading-first-press-engine.js"></script>
<script type="module" src="/estate/assets/linotype/reading-first-app.js"></script>
</head>
<body data-edition-id="fountain-coach-opening-matter-20261101">
<a class="skip" href="#page-viewport">Skip to reading pages</a>
<div class="reading-shell">
<header class="app-header">
 <button type="button" data-reader-target="continuity" class="brand" aria-label="Fountain Coach — first page"><img src="/estate/assets/fountain-coach-logo-transparent.png" alt="" width="32" height="32"/><strong>Fountain Coach</strong></button>
 <div class="header-actions"><button id="reader-parent" class="header-books" data-reader-target="first-readings" type="button" hidden>First Readings</button><button id="reader-library" class="header-books" data-reader-target="library" type="button" aria-label="Open the Bookshelf inside the reader">Books</button><button id="reader-theme" class="icon-only" type="button" aria-label="Use dark appearance" title="Change appearance">◐</button></div>
</header>
<main class="page-frame-reader" id="main">
 <div class="frame-source-flow" id="source-flow" data-min-leaves="1">
  <section class="book-chapter" id="work-on-continuity"><div class="book-chapter-heading"><h2 data-source-block="continuity.title" data-source-from="0" data-source-to="13">On Continuity</h2></div></section>
  <section class="book-chapter-text"><article class="book-prose">
'''+flow+'''
  </article></section>
 </div>
 <div class="page-viewport" id="page-viewport" role="region" aria-label="Fountain Coach — paginated On Continuity" tabindex="0"></div>
 <nav class="frame-controls" aria-label="Reading controls">
  <button class="page-arrow" type="button" id="previous-page" aria-label="Previous page" disabled>←</button>
  <div class="frame-location">
   <label for="reader-section">Reading</label>
   <select id="reader-section" aria-label="Choose publication">
    <option value="continuity" selected>On Continuity</option>
    <option value="library">The Bookshelf</option>
    <option value="essays">Essays — A Book Continually Written</option>
    <option value="first-readings">First Readings</option>
    <option value="teatro">Teatro — An Unfinished Composition</option>
   </select>
   <output class="frame-page-count" id="page-count" aria-live="off">Pages</output>
  </div>
  <button class="page-arrow" type="button" id="next-page" aria-label="Next page">→</button>
 </nav>
 <p class="sr-only" id="reader-status" role="status" aria-live="polite" aria-atomic="true"></p>
</main>
</div>
</body>
</html>
'''
assert (w/'integrated-volumes.html').exists(), 'Build the source-bound volumes first'
page=page.replace(' <div class="page-viewport"', (w/'integrated-volumes.html').read_text()+'\n <div class="page-viewport"',1)
(w/'index.html').write_text(page)
print('written manuscript blocks',len(paragraphs),'chars',sum(map(len,paragraphs)))
