# Fountain Press — catalogue-driven frontend implementation, 16 November 2026

**State:** Source-built, deterministic, tested in WebKit; **not** admitted to canonical WLAN staging or public production. Writer-approved scope is the existing Fountain Press HTML/CSS/JavaScript/reader template, not a new CMS, database, rendering service or release authority. Owning decision: `scenarios/press-books/BOOKSHELF-TEMPLATE-MAINTENANCE.md` (merged from source commit `54ac999`).

## The actual defect and source predecessor

The already-published root and `/estate/` have all **three** published books; `/estate/read/library/` still serves a **different two-book old Reader**. The current machine catalogue contains 10 ordered Essays but no `orderedWorkIDs` for First Readings/Orange Dot. In the old app, `collectionOrder`, active/archive exclusion lists, adjacent work sequences, and gallery-count constants are separate, manually maintained JavaScript. This is an actual frontend source-projection defect, not a new storage prerequisite.

Pinned exact production readback `fountain-press-collection-parity-20261116-9c145b5`:

| Source | SHA-256 |
| --- | --- |
| `/` and `/estate/` | `1da8cc4eab4b4baab460dfe754fba262b1633b96d7b1739cd8c3473fcb7a234e` |
| `reading-first-app` | `50bb76f72f280b8381f9f5f7b3ab5d2f79b1f3ab3217503bfee46a1004fbf452` |
| Reader CSS | `1a94f0d4e0d529e76f32b0454e0dab88866bf0a4c341742ceff6972fb38a2119` |
| Public catalogue | `f91503ae5b3511301d41534eb7f56e5be9e8605661bd6a3c3ed1f6ff482562ee` |

The `published-frontend-predecessor.json` declares all nine exact preimage file hashes, three source-authored subtitles/roles and proem requirements. The compiler refuses source drift rather than trying to infer new admission. Original published text and media are never rewritten.

## Source-owned correction

`scenarios/press-books/published_frontend.py` composes **nine changed static paths only**: `/`, `/estate/`, `/estate/read/library/`, the three current direct books, the machine catalogue, a new content-addressed original Reader module, and one existing Reader stylesheet. Its `reader-publication-state.js.inc` reads a single embedded, versioned publication snapshot. Every visible book, ordered contents entry, gallery item, previous/next collection, selection control and 01/03 position is derived from that snapshot. Missing First Readings/Orange Dot `orderedWorkIDs` migrate once from their original complete top-level source template order, verified against the exact original galleries; subsequent versions use the generated catalogue order. Source-retained archived and historical Essays retain original deep-reading identity but are not listed as active. Unreleased/private source in an intended public artifact is refused, not silently hidden while its full HTML remains downloadable.

**Visual navigation:** narrow typographic running navigation in the actual collection heading names the prior/next *published* book, with a tabular folio position. It is not a phone carousel or the rejected independent side-tab/proxy. It leaves the existing full-width contents-versus-gallery spread, landscape/portrait modes, vertical scrollports and footer intact. A physical iPad/author design acceptance is still necessary before public promotion.

## Local acceptance and limits

- `python3 scenarios/press-books/test_published_frontend.py -q`: **9/9 pass**, including negative cases for missing book, reordered gallery, archival promotion, hidden private source, malformed nested templates, editorial proem loss and digest drift.
- `published_frontend.py --input <exact-source-root> --output <fresh-candidate> --receipt <fresh-json>` on real downloaded public predecessor: **three books / 10, 32, 23 complete contents / 10, 30, 23 original gallery entries**.
- Two independently compiled candidates: **all nine output digests and complete candidate receipt match byte-for-byte**.
- `verify_published_frontend.py --root <candidate> --receipt <receipt>`: complete static route/catalogue/social identity, top-level source, exact new Reader, root/estate/legacy byte parity pass (**9/9 emitted files**). Two negative tamper cases rejected even after recomputing file checksums: obsolete `/estate/read/library/` and missing public Essay membership.
- Real WebKit, with only the nine candidate resource paths overridden and all other assets loaded from the real public site: **desktop 1180×820, tablet portrait 820×1180, phone 390×844 passed**. Each browser run opened root, traversed all three collections horizontally and back with visible named navigation, verified complete contents and gallery counts, checked old library route and all three direct book routes, footer, responsive content presentation and JavaScript exceptions. Expected book scrollLeft values were 2068, 1420 and 662 respectively. This is a source-candidate browser witness, not public production.
- An optional Chromium test was **not run** because that Playwright Chromium executable is not installed on this Mac; it was not downloaded. The host filesystem returned `ENOSPC` when the full three-viewport WebKit report was written **after all three tests printed PASS**; no full JSON report is claimed. Existing tool terminal output holds those actual browser results. The separate offline receipt and source/negative test results are available.

**Staging safety:** The named canonical WLAN current symlink was independently read as `shared-shell-20261116-v215-better-ear-reader-ready`. Its static root differs from current public source in more than metadata: it also has divergent private source template placement and private editorial publication catalogue status (`publicReleaseAuthorized: false`, `stageOnly: true`). Do **not** replace the v215 source/metadata wholesale with this production-derived public candidate or silently convert private stage membership into public admission. Reconcile the intended exact source/rights lineage and the real active predecessor in the **existing EstatePublisher WLAN lane**, preserving unrelated private stage media and rollback. Native terminal staging receipt, HTTPS iPad Safari, VoiceOver and separately authorized public publication are **not established** by this implementation.

**Next action:** admit the reviewed compiler/source via protected Git, reconcile the production-derived candidate against the current author-WLAN stage under the native EstatePublisher procedure, verify actual HTTPS/Reader/source-lock and physical iPad behavior; only after that can a separate public release be requested and independently verified. No alternate local preview server or user-facing copy link is offered as canonical staging.
