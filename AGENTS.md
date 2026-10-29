# fountain.coach Git ownership

## One public Reader publication source for two domains (29 October 2026)

The **intended** common Reframe Reader/Bookshelf publication source is this repository's checked-in `site/` and exact source/release inventory. The author directs **both `fountain.coach` and `benedikt-eickhoff.de` to point to this same source-built site**, rather than maintaining separate company and personal websites. Author/About and Fountain Coach publisher identity must coexist inside the *same* publication. Original manuscripts, Governance normative source and governed instruments keep their own source owners; the former personal-domain repo is retained as historical/original-source custody, not an independent future Reader editing tree. A common source can be deployed as identical immutable artifacts or via a safe canonical redirect, subject to separately authorized routing, deep links, TLS, canonical/social metadata, browser origins and unaffected domain MX/email. **No routing or production change is claimed by this AGENTS update.** Owner product authority: Reframe ADR-008; public publication projection: `Fountain-Coach/estate/docs/decisions/2026-10-29-one-reader-two-domains.md`.

## Reframe public Reader naming — author correction, 29 October 2026

The intended public `fountain.coach/` entrance is the free Reframe **Reader / Bookshelf**, not a separate “Estate”, “Editorial”, or renamed “Works” category. **Remove the terms “Estate” and “Editorial” as public navigation destinations or site branding** in a new or edited Reader source projection, including accessible names, document title/description, breadcrumbs and social metadata. Preserve quotations inside the actual authored source texts, original source/rights attribution and all old deep routes. “Editorial” remains legitimate for internal editorial acts, not the visitor's destination. The publisher is Fountain Coach; `benedikt-eickhoff.de` identifies the human author. Historical local paths, `EstatePublisher`, source ownership/authority and the staging runtime stay unchanged until separately reviewed migration and actual deployment proof. This decision is recorded in Reframe ADR-007 and R27 and the downstream `Fountain-Coach/estate` publication decision; it does not itself change live bytes.

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
