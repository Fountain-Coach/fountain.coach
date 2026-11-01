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


## Accepted private-WLAN staging result

- **Activated release:** `shared-shell-20261101-v94-square-collection-galleries`, with immutable v93 retained for rollback. The existing HTTPS service is active at `https://192.168.8.50:8243/estate/#/read/library`; staging aliases `/works/` and `/pointer/` retain the same reader bytes (the latter redirects to Works). The source projection belongs to `Fountain-Coach/fountain.coach@09e27e8d8c32021dc83cb21ae3a2b2ce7f5b6362`.
- **Unintercepted live browser:** three Mac WebKit profiles (landscape, portrait, phone), zero exceptions, four alternating surfaces, seven and thirty source-ordered gallery items, 1:1 square cells and `object-fit: contain`, fixed footer, thumbnail-to-work navigation and preserved shelf/gallery scroll positions. Witness: `bookshelf-gallery-live.json` in source and the active stage's `/estate/evidence/`.
- **Regression:** twenty-one essay opening layouts passed unchanged; one HTTPS SatzfunkPlayer regression passed with all four source recordings and two-second seek; original First Reading full-size Scores remain on their authored work pages. All thirty-seven source image URLs returned 200 on trusted private staging HTTPS.
- **Provenance:** route/asset SHA-256 readback in `bookshelf-gallery-release.json`, originally pinned source release bytes unchanged, and public production left unmodified. Trust/HTTPS readback yielded HTTP 200, certificate result 0.
- **Not accepted:** physical iPad Safari gesture/VoiceOver, authored dark image renditions, public production or social crawler access. This is accepted **live private staging**, not public publication.
