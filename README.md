# fountain.coach - owning Git source

## Current private WLAN staging projection — 28 October 2026

The writer-approved root and Essays reading room are now active on the owner WLAN at [Fountain Coach staging](http://192.168.8.50:8200/estate/); v57 has passed all 509 stage HTML route readbacks and 30 Chrome viewport checks. The staging provenance and route report are governed by the companion Fountain-Coach/estate branch. **This is not a public HTTPS promotion.** The editorial Git source and its original Linotype editions remain authoritative for their content.

## Adopted author-led entrance — 28 October 2026

**The root website presents one independent author and developer, not a staffed institution.** Its four essay-hero illustrations are authentic source-owned artwork. /essays/ is the complete seven-work reading room, and /editions/ retains the authentic Fountain Press Bookshelf. The older edition-first sections below record historical proposals and are not current root authority.

Canonical nine-entry reel: Estate, Book, Governance, MIDI2, Instruments, Teatro, Satzfunk, Works, Solstice. Status is footer-only. The two currently published essays The Door Is a Score and The Composable Book lack complete HTML/media in this older Git snapshot; the verified public baseline and admitted WLAN v56 assets were preserved in the independently accepted v57 staging projection. This branch remains a draft for review; public HTTPS remains unchanged.


GitHub source authority for fountain.coach and its site/ publishing tree.
Role: Public Fountain Coach identity; one of three front-door editorial identities

Status: author-led Git source staged on owner WLAN as v57; not publicly released (28 October 2026)

The former midi2-gpu-fabric/estate/sites/fountain.coach is a downstream integration copy, not an independent editor. Git source is not a public deployment. Source review, a pinned derived checkout, separate EstatePublisher authorization, release receipt and live HTTPS read-back are required.

The editorial estate has only three public fronts: Fountain Coach, First Reading and Teatro. Other domains remain supporting, legal, reference or archival surfaces. No GitHub CI, raw host deployment or secrets.

## Historical: essay-first Linotype proposal (retained as a complete edition)

The original site entrance has been replaced **in Git source**, not yet
on production HTTPS, with a full Linotype book of the existing essays.
The content is not newly generated prose.

Editorial order:
1. **Teatro — An Unfinished Composition** (the human condition)
2. **Semantic Compilation — The Archive Is Not the Edition** (the form)
3. **Reframe and the Business Value of the Estate** (the economic proposition)

All 77 authorial paragraphs including the three leads, five original figures,
section headings, captions, emphasis and claim boundaries remain source-linked
to the original complete published `site/essays/*/index.html` pages. The old
site homepage remains available in the Git baseline history; it is no longer
the editorial entry point. Other site pages and essay source URLs are still
present for source references, links, and provenance.

The reader itself reuses the original measured First Reading Linotype engine:
`site/assets/linotype/` records its upstream source and per-file hashes in
`site/essays/edition-manifest.json`. Necessary reader-local adaptations are
a smaller valid book page count, an edition-specific folio, and an aggregation
of source-fidelity checks across essay text separated by full-page plates.
The measured paper, iPad portrait/spread, phone atlas, paging and contents
remain the established engine. No model has rewritten the essays.

To reproduce locally (with the independent First Reading source checkout
alongside this repository):

```sh
npm run book:build
npm run check
npm run book:browser
```

Browser verification expects Chrome DevTools on 127.0.0.1:9237 and the
repository's `site/` served over HTTP at localhost:8199. It checks five
desktop/iPad/phone viewport cases, chapter navigation, measured page creation
and non-overflow. The original essay source itself does not move.

**The current source is an unpublished candidate.** The public domain
continues to serve the previous homepage until a separately authorized,
source-pinned EstatePublisher publication and public HTTPS read-back.


## Historical: editions-as-root proposal, superseded by the writer

Historical candidate: fountain.coach/ was proposed as a duplicate of /editions/. The **28 October author decision supersedes this**: / is the author-led editorial homepage, /essays/ the neighboring reading room, /editions/ the independent catalogue. The catalogue owns the editorial navigation only; the Fountain
Coach rail enters its **/editions/essays/** volume, and the other two
fronts point into the independently owned First Reading and Teatro editions.
An edition may contain one or more **sub-editions** without ceasing to be an
edition itself. This is a hierarchical publication model, not a tree of dummy
marketing pages.

- `/editions/` — catalogue and hierarchy, not the domain root
- `/editions/essays/` — complete Linotype collection, three essays, five plates
- `/editions/essays/teatro-an-unfinished-composition/` — independent full essay
- `/editions/essays/semantic-compilation-the-archive-is-not-the-edition/` — independent full essay
- `/editions/essays/reframe-and-the-business-value-of-the-estate/` — independent full essay

The original source texts at `/essays/…` are preserved byte-for-byte;
sub-editions are complete **source-linked editions**, not snippets or
anchors masquerading as books. Every sub-edition gets its own cover, contents,
measured page composition, URL, folio and device-local reading state. The
book renderer is still the measured First Reading Linotype engine.

`npm run book:build` composes the source hierarchy deterministically from
published essays and the pinned First Reading runtime. `npm run check`
compares every complete source paragraph and original image and ensures the
source-file inventory is exact. `npm run book:browser` verifies both the
collection and all three independently composed sub-editions in simulated
iPad and phone viewports.

The old `/essays/` collection is retained as an **original source archive**;
it is no longer the front door. The Company Status link stays with mandatory
legal footer references. Publication of the new hierarchy is **staging-only**
until independently governed production promotion.

## Edition-thumbnail grid

Historical design: the estate entrance at / mirrored /editions/. The approved 28 October editorial homepage does not mirror it. Inspired by the real
Instruments catalogue grid, it now displays just the original hand/spring
mark and the three source-authorized edition images. There are no empty
icon placeholders or secondary title blocks. The previous detailed
editions catalogue remains at `/editions/catalogue/`; the three complete
original essays and their standalone Linotype readers remain unchanged.
The owning repository builds and verifies the grid, while LAN-only URL
substitution occurs in the Estate registry staging pipeline.
