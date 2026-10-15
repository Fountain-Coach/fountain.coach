# Semantic Visual Bookshelf — source-attested fixture

This is a **WLAN-only, visual-only semantic publication fixture**, not a new
production edition or a substitute for the authored essays.

The experiment takes a narrow, defensible learning from the prior REA
investigation: an application-level operation for opening a collection can be
distinct from navigation inside that collection. REA's static Obsidian analysis
did **not** recover verified internal note-link behavior. This implementation
does not copy Obsidian code or assume its runtime semantics.

## Ontology and editorial acceptance

- **Publisher logo:** a non-publication mark in the Bookshelf grid.
- **Collection:** a source-admitted publication container with its own stable
  identity and cover, independently addressable, never a generic page.
- **Work:** an authored source identified by source SHA-256 and work ID.
- **Encounter:** a work bound to one collection parent. The same source work
  may be encountered in Essays and First Readings without identity confusion.
- **Cover:** an original admitted image; not a title, URL alias, Score identity,
  or arbitrary placeholder.
- **Visual plate:** an original admitted image with source SHA-256, an ordinal
  within its work's current image sequence, and a stable `#plate-N` address.
- **Empty slot:** purely visual, no identity, no link or phantom publication.

The view displays **no page prose, work labels, chapter text or numbered
navigation**. Original images (including any lettering intrinsic to the artwork)
remain unmodified and uncropped. Human-readable identities stay in accessible
labels and the source-verified `fixture.json`, never in a second navigation table.

## Scenario

Estate Bookshelf -> Essays or First Readings collection -> original source
cover -> image-only work encounter -> return to exact parent cover.

The Essays shelf contains exactly three existing authorship-admitted essays.
The First Readings shelf contains only the already admitted *Teatro — An
Unfinished Composition* work. It is not evidence of a First Hearings edition;
Teatro remains an instrument, not an invented book.

The single work belongs to both the Essays source catalogue and the First
Readings collection. Two parent-specific encounter URLs share the same original
work digest. Browser Back, physical navigation icons, keyboard arrows,
pointer swipes and deep links preserve that collection context. An unknown
source page address has an explicit invalid state, never a silent fall-through.

## Implementation authority and commands

Reusable rendering belongs to Fountain Press `runtime/bookshelf.py`. This
fixture uses its real grid and 20 inert empty slots, plus the new explicit
`collection_id` parameter; there is no second bookshelf renderer.

The source owner is `Fountain-Coach/fountain.coach`. The deterministic
fixture builder verifies the original essay SHA-256 and every image digest
before generating any projection at:

`/fixtures/semantic-visual-bookshelf/`

- `npm run fixture:build` — source build, fixture projection, source inventory.
- `npm run fixture:check` — verbatim source and semantic fixture contract.
- `npm run fixture:browser` — Chrome journey proof with source imagery loaded.
- `fixture.json` — machine-readable collection/work/encounter/provenance graph.

No source essay text, original source image, established published route,
production DNS or release authority is modified by this experiment.
No GitHub Actions/CI is introduced.

Native iPad Safari visual approval and production publishing are **not**
claimed. The browser captures are evidence candidates, not author approval.
