# fountain.coach Git ownership

- GitHub owner: Fountain-Coach/fountain.coach.
- Canonical source: site/ and edition.json.
- Preserve rights, status and historical source content.
- Do not use the old Hetzner Git domain as source authority.
- A Git push never deploys content.
- Do not reverse-copy derived estate HTML over the canonical source.
- Immutable static essays follow Governance Chapter 158: the author approves the exact Git-owned source; `npm run essays:publish` packages, validates, delivers through verified SSH, atomically activates on Caddy, preserves rollback and requires exact-byte public HTTPS readback. FountainStore mirroring, FCIS host enrollment and MIDI2 runtime are not prerequisites. Other operations retain their own authorities.
- Three editorial fronts only: Fountain Coach, First Reading, Teatro.

## Independent product essay — The Composable Book (18 October 2026)

- The **separate** product essay is sourced from `content/product-essays/the-composable-book.md`; `scripts/build_product_essay.py` deterministically projects `/essays/` and `/essays/the-composable-book/` with four source-controlled SVG plates and a social card; the existing `/essays/` collection index gains one source-owned gallery card while the three original essay pages remain byte-identical.
- It is **not** a fourth original essay of the established three-work Linotype edition. Do not add it to `site/essays/edition-manifest.json`, alter the three existing source essay pages, or change the edition table of contents to accommodate it.
- Keep links publicly reachable for anonymous readers: private Fountain Coach GitHub implementations belong in local provenance notes, not public hyperlink targets. Public governance chapters, First Reading, Teatro and essays are suitable editorial references when they are reachable.
- `npm run product:build`, `npm run product:check` and `npm run product:browser` verify source projection, inventory/provenance, and real desktop/iPad/phone layouts. The browser verifier requires a local Chrome DevTools endpoint and local static site server; see `docs/product/composable-book-essay-publication-20261018.md`.
- New site files require regenerating `publication-files.sha256`, `edition.json` file count and SHA inventory. Preserve the SHA-guarded 77 original paragraphs and five figures. No GitHub CI or unapproved runtime scripting.
- This essay is **published**, with terminal source-revision/HTTPS digest evidence in `docs/product/receipts/composable-book-production-20261018.json`. The `edition.json` source-candidate value is the historical authored artifact state, not the live publication state. Chapter 158 permits authenticated SSH as a bounded static-release transport, with immutable release, atomic activation, rollback and public readback; FountainStore/FCIS application runtime is not a prerequisite. A source push, candidate preview or static server alone is not a publication receipt.

## Essay edition authority

- Fountain Coach's primary site `site/index.html` is an essay-first
  Linotype reader. Retain **all three** complete authored essays and five
  original illustrations from `site/essays/`.
- Editorial order: Teatro, Semantic Compilation, Reframe and Business Value.
  Do not invent new connective essays, claims, technical specifications,
  pseudo-governance or filler chapters to inflate the book.
- `scripts/build_essay_edition.py` is the deterministic source projector.
  `scripts/verify_essay_edition.py` verifies every original paragraph/asset,
  publication inventory and link. `scripts/verify_essay_browser.mjs`
  checks actual responsive book composition.
- Original essay pages are retained as source-specific URLs and legal/provenance
  references. The former promotional homepage lives in Git history; don't
  restore it as the front door without separate author approval.
- The runtime comes from the accepted First Reading source owner. Any
  adaptation must preserve prose, original images, source identities,
  measured book geometry, iPad spreads and phone reading.
- Status remains legal-footer material; First Reading and Teatro are the other
  two estate front doors. Git commit is not public publication.


## Editions hierarchy (authoritative root)

- Do not put the essays book at `/`: both `/` and `/editions/` must show the
  same *editions catalogue*.
- Every editorial rail destination is an edition: Fountain Coach enters
  `/editions/essays/`; First Reading enters its accepted published edition;
  Teatro enters its independently owned performance edition.
- An edition can contain full, independently paginated sub-editions. The
  three original authored essays are currently the Essays sub-editions.
- `scripts/build_edition_hierarchy.py` is the top-level deterministic
  producer; it consumes the older source-bound book builder without
  changing the original published essays under `site/essays/`.
- Source-owned original essay bodies and illustrations remain SHA-protected. The `/essays/` *collection index* may grow by an exactly diffed, source-owned card under Chapter 158, preserving every previously published card. Any WLAN-only rail remapping belongs in Fountain-Coach/estate staging.
- Validate the catalogue and every nested reader with `npm run check` and
  `npm run book:browser` before source promotion.

## Edition grid root (15 October 2026)

- The estate landing `/` and `/editions/` share the genuine Fountain Press
  Bookshelf implementation, never an independent or duplicated shelf UI.
- The four first-row cells are the authentic Fountain Coach mark and the
  three admitted books: Essays, First Reading, Teatro. All images are
  original source-owned assets. The remaining cells are visible, lightly dashed
  **empty slots**, modeled on the Instruments catalogue grid, with no links
  or invented publication identities. No iOS app-icon treatments, extra
  titles, invented publications, or separate action buttons.
- The prior detailed catalogue is preserved at `/editions/catalogue/`
  without losing nested essay edition routes and original manuscripts.
- `scripts/build_edition_hierarchy.py` owns this deterministic projection.
  The estate registry may only rewrite the three canonical outbound book
  links in disposable WLAN staging; public promotion remains separately gated.

## Logo's circular identity

The authentic logo is displayed in the shared `fc-identity-circle` geometry
owned by Fountain Press, matching Teatro's Play/Stop button. The circle is
quiet and inert, not a new logo or navigation link. Include the Press-owned
`identity-circle.css` in deterministic site output; never independently
implement or override it in the Fountain Coach domain.

## Publisher thumbnail geometry

An admitted publication is represented by a clickable **rounded square**,
identical in dimensions and corner radius to its unoccupied neighboring grid
slot. The original (often portrait) cover art sits inside, source-faithful,
using `object-fit:contain`; it must not replace the square thumbnail boundary.
The circle is reserved for the publisher logo. These geometry rules are
implemented once in Fountain Press; this owner only publishes its copies.

## First Readings collection acceptance candidate — 15 October 2026

The pinned [Fountain Press publication identity contract](https://github.com/Fountain-Coach/fountain-press/blob/main/docs/publication-identity-and-cover-navigation.md) governs the first real shelf-to-work proof. The source owner publishes an editioned collection at `/collections/first-readings/`, which currently contains precisely one source-digest-admitted work: `teatro-an-unfinished-composition`. It is **not the Teatro authoring instrument** and not a fictitious hearing.

The Estate shelf renders only two populated publication slots: Essays and First Readings. The absent First Hearings has an actual empty slot, not a counterfeit cover. The original Solstice singular First Reading reader is preserved at its canonical URL, without changing its identity. Legacy Teatro tool and beta routes remain usable without being promoted as publications.

The source-owned Score artwork is explicitly admitted as the *visual cover artwork projection* of this first work, not as the work's identity or mandatory opening. The same artwork is present in the collection's rounded-square cover and visually on the Linotype opening cover. A reader can move to the full, unchanged 22-paragraph work, then back to the parent collection. Other essays retain the conventional Linotype reader. No narration or First Hearings edition has been published.

Browser acceptance requires `npm run book:browser` plus `node scripts/verify_first_readings_journey.mjs` on the served WLAN endpoints, screenshot comparison across iPad portrait/landscape and phone, source digests and keyboard/Back navigation. The work's native iPad Safari aesthetic acceptance is still a separate editorial decision.

## Browser history is reader continuity — 18 October

- Never set `history.scrollRestoration = 'manual'` or force `scrollTo(0,0)` during `pageshow` for the shared estate. The browser owns scroll restoration for Back/Forward and ordinary links; authored fragment targets work natively.
- Source `site/assets/estate-core.js` is the only admitted shared navigation file for the narrow scroll-fix release. Changes require a pinned predecessor SHA and byte-identical verification of every unrelated navigation behavior; see `docs/product/browser-history-restoration-20261018.md`.
- Browser acceptance must exercise real link navigation + browser Back with native `history.scrollRestoration === 'auto'` and compare the returned scroll positions for the homepage, essay collection and long article. `npm run essays:history` implements the regression witness.

## Live estate shell integration — 18 October

- The current public `/` homepage differs from the planned Bookshelf at `site/index.html`. They are separate revisions. Do not replace the live portal with the unadmitted bookshelf during an essay publication.
- `scripts/project_home_essay.py` owns the one featured essay card projected from a pinned live homepage predecessor; it does not change `site/index.html`. It refuses any unrelated source mutation.
- `scripts/build_product_essay.py` derives the shared estate navigation rail and legal footer from the already source-owned `site/essays/index.html`, with current breadcrumbs and full outbound estate links. Do not invent an independent product header or duplicate the website menu.
- The 18 October codex integration changed only live `/`, `/essays/the-composable-book/` and its assets. The subsequent Back/Forward correction adds only the source-owned shared `/assets/estate-core.js` to the immutable release scope. All page HTML, `essays/` and other existing source files remain byte-identical. Verify both the corrected JavaScript and unchanged page digests by public HTTPS readback.

## macOS Safari existing-tab recovery — 18 October

- Removing the old `manual` scroll-restoration assignment is not sufficient: a previously loaded WebKit history entry may retain that value. Set `history.scrollRestoration='auto'` explicitly **only if not already auto**, without `scrollTo`, and let the browser own Back/Forward.
- Before promoting that change, test with actual macOS Safari: simulate an inherited `manual` mode, reload the page, prove it becomes `auto`, then follow a cross-domain governance link and Back without losing scroll position. `npm run essays:safari` uses native Safari WebDriver for this contract.
- The immutable route-scoped publisher verifies SHA-pinned predecessor `estate-core-native-before-macos-repair-20261018.js` and byte-identical remainder of the common estate JavaScript. Do not widen its permitted asset or route scope.
