# fountain.coach Git ownership

## Current reader-first editorial decision — 29 October 2026

The parent homepage opens a continuous seven-chapter Linotype Essays book. The latest attested writing is chapter one in every reader-selected semantic order. Original essays and media remain separately owned at their published routes. The previous four-hero landing is preserved at /scenarios/author-led/, the article gallery at /essays/, and the original independent Press Bookshelf at /editions/. The writer-approved source is pinned at commit 5ec8c5490c8a1fe2b4a941185ecb3f415a7bdfdd. Staging v59 is an owner-WLAN preview, not a production publication. The October 28 decision below is historic.

## Approved editorial decision — 28 October 2026

The Fountain Coach parent identity is one author's independent software and publishing practice. The homepage makes that authorship visible and features four original essay illustrations; `/essays/` is the complete reading room next door. The independent Fountain Press Bookshelf stays at `/editions/`. Chapter 92's publisher/authority map and Chapter 127's direct-static Publication Core remain applicable.

Use the current `Fountain-Coach/estate/navigation/canonical-reel.v1.json` for the complete headmast/reel identity and the estate legal-footer requirements; the Status destination remains footer-only. All route changes preserve source ownership, rights and source text. Publicly live articles whose media are absent from this Git candidate must be retained from the verified production baseline when assembling an immutable staging candidate; never publish a stale Git tree over newer public work. Source, stage and production are separate authorities.

- GitHub owner: Fountain-Coach/fountain.coach.
- Canonical source: site/ and edition.json.
- Preserve rights, status and historical source content.
- Do not use the old Hetzner Git domain as source authority.
- A Git push never deploys content.
- Do not reverse-copy derived estate HTML over the canonical source.
- Publication needs typed exact-host EstatePublisher and independent public read-back.
- Three editorial fronts only: Fountain Coach, First Reading, Teatro.

## Essay edition authority

- Fountain Coach's primary `site/index.html` is the approved one-person editorial identity and four authentic essay heroes. `/essays/` is the complete seven-work illustrated reading room. Preserve all complete original Linotype essays, texts and plates at `/editions/essays/` and their source-owned routes.
- Editorial order: Teatro, Semantic Compilation, Reframe and Business Value.
  Do not invent new connective essays, claims, technical specifications,
  pseudo-governance or filler chapters to inflate the book.
- `scripts/build_essay_edition.py` is the deterministic source projector.
  `scripts/verify_essay_edition.py` verifies every original paragraph/asset,
  publication inventory and link. `scripts/verify_essay_browser.mjs`
  checks actual responsive book composition.
- Original essay pages are retained as source-specific URLs and legal/provenance
  references. The former future-facing portal lives in Git history; do not restore it as the front door.
- The runtime comes from the accepted First Reading source owner. Any
  adaptation must preserve prose, original images, source identities,
  measured book geometry, iPad spreads and phone reading.
- Status remains legal-footer material; First Reading and Teatro are the other
  two estate front doors. Git commit is not public publication.


## Editions hierarchy (independent of author-led root)

- `/` is a separately authored landing for the independent practice. `/editions/` remains the authentic Fountain Press editions catalogue, not a duplicate homepage.
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

## Edition grid at /editions/ (historic 15 October acceptance, retained)

- `/editions/` uses the genuine Fountain Press Bookshelf. The editorial homepage does not duplicate its grid or invent book identities.
- The four first-row cells are the authentic Fountain Coach mark and the
  three admitted books: Essays, First Reading, Teatro. All images are
  original source-owned assets. The remaining cells are visible, lightly dashed
  **empty slots**, modeled on the Instruments catalogue grid, with no links
  or invented publication identities. No iOS app-icon treatments, extra
  titles, invented publications, or separate action buttons.
- The prior detailed catalogue is preserved at `/editions/catalogue/`
  without losing nested essay edition routes and original manuscripts.
- `scripts/build_edition_hierarchy.py` owns the `/editions/` projection, never `site/index.html`. The editor-approved root and adjacent gallery are verified by `scripts/verify_author_landing.py`. The estate registry may rewrite canonical outbound edition links only in disposable WLAN staging; public promotion remains separate.

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
