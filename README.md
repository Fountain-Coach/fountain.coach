# fountain.coach - owning Git source

GitHub source authority for fountain.coach and its site/ publishing tree.
Role: Public Fountain Coach identity; one of three front-door editorial identities

Status: verified-live-publication-baseline

The former midi2-gpu-fabric/estate/sites/fountain.coach is a downstream integration copy, not an independent editor. Git source is not a public deployment. Source review, a pinned derived checkout, separate EstatePublisher authorization, release receipt and live HTTPS read-back are required.

The editorial estate has only three public fronts: Fountain Coach, First Reading and Teatro. Other domains remain supporting, legal, reference or archival surfaces. No GitHub CI, raw host deployment or secrets.

## Essays as the public edition (Linotype candidate)

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


## Editions are the public entrance (source edition candidate)

**fountain.coach/** lands in the **Editions catalogue**, byte-identical to
**/editions/**. The catalogue owns the editorial navigation only; the Fountain
Coach rail enters its **/editions/essays/** volume, and the other two
fronts point into the independently owned First Reading and Teatro editions.
An edition may contain one or more **sub-editions** without ceasing to be an
edition itself. This is a hierarchical publication model, not a tree of dummy
marketing pages.

- `/editions/` — catalogue and hierarchy, also the domain root
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
