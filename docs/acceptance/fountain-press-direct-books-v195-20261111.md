# Direct book links and first-chapter social preview — acceptance

**Date:** 11 November 2026. **Source owner:** Fountain-Coach/fountain.coach. **Audience:** Writer, Fountain Press publisher and future source-bound FCIS Skills. **Status:** Private canonical WLAN **v195 stage accepted**; public deployment **not performed**; physical iPad native/VoiceOver **not driven**.

## Scope and production-first source

The writer requested directly shareable **books** (not just chapters) whose first eligible illustrated chapter supplies the book-level social image, and repeatable semantic/FCIS maintenance. The actual production Fountain Press `https://fountain.coach/estate/` was independently inspected on the source Mac and rendered on iPad viewport, and its current public release pinned at `fcis-essay-heading-20261110-8f58f29`, index SHA-256 `005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49`. It contains Essays and First Readings. The production-derived, private Orange Dot Bookshelf `v194b` adds Orange Dot without Governance/Works/Scores shelves, and is the only source for this derivative. The base staging HTML SHA is `7db826d5aa32da727213ce2d53dc1e1a35efe5ee820c987ae6066e2dd1500f3b`, app SHA `d2c2020390a35d7def6409abf50171e1998a0f1baa4bf8da3cbaf50bc3aa1a81`, CSS SHA `769fb12fbe7205e90269ecbf3760c8a6d226e78347bd1d62f05035174d671247`.

## Implemented

The existing Bookshelf now has one small accessible “Direct book link” beneath each book heading. The existing Reader is reused: opening a direct path starts in that book's complete contents, and selecting a chapter opens a paginated Linotype work. No scrolling alternative was introduced.

Three path routes and corresponding static crawler metadata have been admitted privately: `/estate/books/essays/`, `/estate/books/first-readings/` and `/estate/books/orange-dot/`. Every initial HTML response has one canonical HTTPS URL (no duplicate `rel=canonical`), book-specific OpenGraph image/title/url/alt/1200×630, Twitter image/card and Schema.org Book JSON-LD with first eligible illustrated chapter identity. This is source-bound metadata, not post-load JS.

The first eligible illustrated chapter determines the picture:
- Essays — `essay--client-centered`, source SVG SHA `e5a8fc282d138efa561e332a306f8f4be3b1a5e36a840ecb6386daa223b8bbc3`, derivative JPEG SHA `74876fb17e31ed6dbec786e6163ae9be06817e8997b95f9c0be65bc891a47b65`.
- First Readings — `solstice-reading-01--2025-12-22-anweisung-an-den-schmerz`, source image SHA `b0e6cf8252aca0da83a9b0bfbdbb3f57b88c826e8b85ac5a89f43b23bad98876`, derivative SHA `3358d3a3fbc67c8648f57a85bdf9102a3822b4d9d1315689cfd9ddd369cadad1`.
- Orange Dot — `orange-dot--2025-12-21-solstice`, source image SHA `6e5f8aec639a96ed025cfc4e6e6626197fa41e026626f114a92001375adaa33d`, derivative SHA `040adeafa8c7bee1b0075cfbe297388580c6e8897b9bf08712e8ef3bd5c58115`.

Original chapter images and paragraph source positions remain unchanged. Share image background/contain is deterministic. Source paths, figure SHA, derivative SHA, first chapter IDs, canonical URLs and private publication status are recorded together in `/estate/books/catalog.json`.

## Source and release evidence

The checked-in `scenarios/press-books/book-policy.json` has a source-authority SHA, ordered collection identity, original figure review status and expected count. `compose_direct_books.py` regenerates the complete 10-file new/changed overlay deterministically from that source. It was rerun after conversion to policy-derived inputs and all **11 physical output files**, including the local build receipt, matched the accepted v195b source overlay **byte-for-byte**. Two deliberate negative fixtures refused a modified source index and a tampered first illustration source, without modifying original files.

Canonical owner-WLAN active release: `shared-shell-20261111-v195-direct-books-social-5227c32`. Source-lock SHA `71eae0d19d032617ba80ee4d9ef749d62fa04c8c1b32ec129a03cef2306152e5`; admission SHA `63a9331e7fde3c028ea9f48598cad7669edf63a9ae70fd75ea3e76518fae46f1`. Ten changed files, eight new, 1,941 unaffected older stage files preserved. v194b predecessor remains intact as rollback. The inherited admission guard printed `BOOK_DIRECT_LINKS_V195_ADMITTED`, and both original HTTP and HTTPS staging services passed activated exact-route/source/image readback.

Independent no-JavaScript HTTP **and** HTTPS verification passed all three routes, original figure source bytes, OG/Twitter/JSON-LD identity, original and derived SHA, existing Governance chapter references and no Governance/Works/Scores shelf. Mac WebKit checked **3 books × 3 viewport sizes** (820×1180 portrait, 1180×820 landscape, 390×844 phone) on the **live canonical stage**; every book route opened the correct book contents, clicking the first item opened a true paginated chapter, all social image SHAs and machine catalogue fields matched, and there were no Reader page exceptions. Earlier same-tab navigation momentarily aborted optional modules; the final test opens each book independently, matching real shared link behavior and avoiding browser test-induced resource cancellation. Local preview produced the same accepted result. The three landscape social images and typography link placement were visually reviewed.

## FCIS maintenance status and publication boundary

The canonical existing `linotype-estate-template` Skill in `Fountain-Coach/.github` now includes the [direct-book publication procedure](https://github.com/Fountain-Coach/.github/pull/71). Canonical/derived files were committed separately, the existing FCIS marketplace projection advanced to v0.1.13 **on a review branch**, source-digest parity passed, and all **138 Skill regression tests passed**. PR #71 is not yet evidence of merged GitHub main, installed provider plugin synchronization or future autonomous background monitoring. The Skill instructs source-triggered regeneration and verification during future publisher work, not scheduled work in the absence of a publisher invocation.

Production remains at `fcis-essay-heading-20261110-8f58f29` and has NOT acquired these routes. The public book canonical URLs are future identifiers, not publicly available webpages yet. Source Orange Dot rights status still specifically says owner-WLAN private/author-controlled; no public media upload, Facebook sharing, DNS or public EstatePublisher `deliver` occurred. The separate Governance and Works books remain excluded; unrelated historical sources and the 20 Koken film originals are preserved.

Physical iPad Safari/VoiceOver acceptance and independent public delivery after explicit rights/editorial admission remain outstanding. The initial book-level social derivation workflow is implemented, but adding a new source book or changing membership still requires a new source-owned policy, composite Reader membership and verified immutable release through the FCIS Skill procedure.
