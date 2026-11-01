# Collection Gallery Alternation — FCIS staging revision (1 November 2026)

## Source and authority

- **Authorizing design:** User-approved Collection Gallery Alternation, extending the accepted one-reader organigram. Canonical `Fountain-Coach/.github` Linotype skill amendment in [PR #27](https://github.com/Fountain-Coach/.github/pull/27), merge `d8041ba02e8436179679ddbc3363affca0026b00`. Full-tree skill digest `2c227b03c94dcebb54b6b9e53a7bcbf070da9a306dccf5a0292444911e584bc3` (62/62 tests pass).
- **Development owner:** `Fountain-Coach/fountain.coach`; this revision changes its existing `reading-first-app.js`, `reading-first-shell.css`, `build_reading_first.py`, and adds `build_bookshelf_gallery.cjs`, `bookshelf-gallery.json`, and focused browser tests. The direct-static HTML page embeds its source-attested gallery JSON; no new runtime, Kit or website route is introduced.
- **Original manuscript/illustration authority:** seven source-owned Essays with `essay-share-manifest.json` (six published illustrations, one actual typeset-page preview), and First Reading's thirty published works with their first original figure from `solstice-volumes.html` and `solstice-source-inventory.json`. The original edition contains forty-one source illustrations; it continues to present all of them inside the works. No original source image, paragraph or published edition is replaced.

## Composition

Bookshelf remains a horizontal page-frame movement, now alternating exactly four semantic surfaces:

1. Essays — typographic collection statement and action to enter complete contents.
2. Essays — vertically scrollable gallery with seven equal **square** image cells.
3. First Readings — typographic statement and action to its complete contents.
4. First Readings — vertically scrollable gallery with thirty square image cells.

Gallery images are source URLs rendered with **object-fit: contain**, not cropped, invented or stretched. Each square has a source-attested work identity, actual title, alt text, keyboard focus and a same-reader action. The gallery orders match the admitted source work order, not arbitrary visual sorting. Collection description surfaces and galleries alternate horizontally, while only gallery bodies scroll vertically. The fixed reader masthead and footer remain outside both scroll regions. Horizontal and per-gallery vertical positions are preserved across reading and return. The source-based prose pagination, Score-first full-folio sizing and embedded SatzfunkPlayer remain unchanged. No unknown future work or image is admitted.

## Acceptance boundary

The candidate browser test `test_bookshelf_gallery.cjs` inspects landscape spread (1180×820), portrait (820×1180), narrow phone (390×844) and asserts four-panel order; 7+30 distinct work IDs; 1:1 image boxes; proportional contain rendering; fixed bottom footer; nested scroll; source-derived naming; work navigation; horizontal and vertical position restoration. The trusted WLAN staging host independently serves all thirty-seven asset URLs (HTTP 200, TLS verified). The seven essay illustrations also passed a browser decode check in the candidate.

The screen is a direct-static Fountain Press projection. Do not treat a preflight interception screenshot as a *live deployed stage*. After immutable activation, rerun browser assertions **without intercepted files** and read back actual release byte digests against the host. Physical iPad Safari, VoiceOver, authored dark renditions, and public release remain outside this bounded staging acceptance. No production or DNS mutation is authorized.
