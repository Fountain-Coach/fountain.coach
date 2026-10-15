# fountain.coach Git ownership

- GitHub owner: Fountain-Coach/fountain.coach.
- Canonical source: site/ and edition.json.
- Preserve rights, status and historical source content.
- Do not use the old Hetzner Git domain as source authority.
- A Git push never deploys content.
- Do not reverse-copy derived estate HTML over the canonical source.
- Publication needs typed exact-host EstatePublisher and independent public read-back.
- Three editorial fronts only: Fountain Coach, First Reading, Teatro.

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
- Source-owner HTML at `/essays/` is immutable for source SHA checks.
  Any WLAN-only rail remapping belongs in Fountain-Coach/estate staging.
- Validate the catalogue and every nested reader with `npm run check` and
  `npm run book:browser` before source promotion.

## Edition grid root (15 October 2026)

- The estate landing `/` and `/editions/` share the genuine Fountain Press
  Bookshelf implementation, never an independent or duplicated shelf UI.
- The four first-row cells are the authentic Fountain Coach mark and the
  three admitted books: Essays, First Reading, Teatro. All images are
  original source-owned assets. No iOS app-icon treatments, empty slots,
  extra titles, invented publications or separate action buttons.
- The prior detailed catalogue is preserved at `/editions/catalogue/`
  without losing nested essay edition routes and original manuscripts.
- `scripts/build_edition_hierarchy.py` owns this deterministic projection.
  The estate registry may only rewrite the three canonical outbound book
  links in disposable WLAN staging; public promotion remains separately gated.
