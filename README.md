# fountain.coach - owning Git source

GitHub source authority for fountain.coach and its site/ publishing tree.
Role: Public Fountain Coach identity; one of three front-door editorial identities

Status: verified-live-publication-baseline

The former midi2-gpu-fabric/estate/sites/fountain.coach is a downstream integration copy, not an independent editor. Git source is not a public deployment. Source review, a pinned commit, a scoped immutable static release, retained rollback and independent live HTTPS readback are required. Under Chapter 158, secure SSH can carry approved static release bytes without a distributed application runtime.

The editorial estate has only three public fronts: Fountain Coach, First Reading and Teatro. Other domains remain supporting, legal, reference or archival surfaces. No GitHub CI, unscoped host deployment, or credentials stored in Git.

## Static essay publication — one command (Chapter 158)

The Git-owned essay publisher has one narrow, verified source contract and one release operation. It is currently admitted only for `/essays/the-composable-book/` and the corresponding `/essays/` card, not for unrelated site paths or other domains.

```sh
npm run essays:check      # 11 synthetic release/rollback/idempotence tests + source fidelity
npm run essays:prepare    # read-only comparison against live Caddy and gallery
npm run essays:publish    # fixed-host SSH release, atomic activation, public SHA-256 witnesses
```

Source must be clean and committed before `essays:publish`. The exact host, release roots and scope are fixed; a changed Caddy configuration, missing predecessor, changed gallery content or missing deployment identity fails closed. The previous immutable release remains available for rollback. The script reports `PUBLISHED_HTTPS_VERIFIED` only after exact-byte HTTPS checks for all changed files and preservation of five existing public sibling routes. See `docs/product/one-command-static-essay-publication-20261018.md`. This implementation uses the Chapter 158 static-release exception; it does not depend on a remote FountainStore/FCIS session. A Git push is never publication.

## Product writing — The Composable Book (published 18 October 2026)

The separate new product essay, **The Composable Book — A book that can become what its writer imagines**, is source-owned at `content/product-essays/the-composable-book.md`. Its deterministic HTML, product writing index, editable SVG editorial plates and Open Graph illustration are under `site/essays/` (`/essays/` and `/essays/the-composable-book/`). It is independent of the three original, byte-attested essays; no fourth source essay has been inserted into the Linotype edition.

```sh
npm run product:build
npm run product:check
# with a local static site server and headless Chrome CDP, as documented in docs/product/
npm run product:browser
npm run check
```

The product essay links outward to publicly readable governance chapters, the original essay source URLs, First Reading, Teatro, MDN, React and Vite. Private implementation source identities and exact commits are kept in `docs/product/composable-book-essay-publication-20261018.md` rather than dead links on the public page. Its claims explicitly distinguish native Mac evidence from proposed Linux GUI, iPad parity, general DSL authoring and DOM composition capabilities.

**Published and independently verified:** [The Composable Book](https://fountain.coach/essays/the-composable-book/) entered the live `/essays/` collection under immutable Caddy release `static-composable-44fc5d4e8c4bc6` from source commit `b2d8c28`. All eight changed paths and five existing sibling routes passed exact-byte HTTPS readback. The accepted terminal receipt is in `docs/product/receipts/composable-book-production-20261018.json`. Static SSH delivery is permitted by Chapter 158; it does not use the application's remote Store synchronization. The source-candidate metadata in `edition.json` describes the source artifact before deployment; the separate terminal receipt establishes public status.

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

## Edition-thumbnail grid

The estate entrance at `/` mirrors `/editions/`. Inspired by the real
Instruments catalogue grid, it now displays just the original hand/spring
mark and the three source-authorized edition images. There are no empty
icon placeholders or secondary title blocks. The previous detailed
editions catalogue remains at `/editions/catalogue/`; the three complete
original essays and their standalone Linotype readers remain unchanged.
The owning repository builds and verifies the grid, while LAN-only URL
substitution occurs in the Estate registry staging pipeline.

### Domain integration of The Composable Book (18 October)

The release additionally projects Fountain Coach's shared estate rail, breadcrumbs and legal footer onto the article, and inserts a source-pinned link into the *already published homepage*. The existing planned Bookshelf in `site/index.html` is **not** published or replaced by this targeted deployment. Its separate UX acceptance remains independent. The public homepage feature is derived by `scripts/project_home_essay.py` from its exact-byte archived predecessor and is accepted only if every other byte is unchanged. A publication receipt must attest both homepage and essay digests.

### Reader continuity: Back/Forward scroll restoration (18 October)

The shared public estate script formerly forced `history.scrollRestoration='manual'` and scrolled to page top on `pageshow`, losing a reader's place after following a link. The corrected `site/assets/estate-core.js` **defers to native browser history restoration** and leaves all other estate rail/scroll effects byte-identical. The immutable static publisher admits this one additional scoped asset with its predecessor digest and strict unchanged-remainder check. For browser regression tests, serve the live-home projection with `site/essays/` and `site/assets/` on one local origin and run `SCROLL_TEST_ORIGIN=http://127.0.0.1:8219 npm run essays:history`; the command checks `/`, `/essays/`, and the full Composable Book, following a real link and returning via browser Back. Repeat with `SCROLL_TEST_WIDTH=820 SCROLL_TEST_HEIGHT=1180` (iPad) and `390/844` (phone). See `docs/product/browser-history-restoration-20261018.md` for bounds and SHA provenance.

### macOS Safari legacy history entries

Safari on macOS can retain the former `manual` scroll restoration setting in an *already open* document even after its original script has been replaced, whereas iPad Safari and fresh desktop sessions behave correctly. The estate script now explicitly recovers the browser's native `auto` mode without moving the reader. The Safari-native regression test is `npm run essays:safari` (requires the macOS `safaridriver` endpoint); it covers a preexisting manual history entry and three link/Back journeys. See `docs/product/browser-history-restoration-20261018.md`.
