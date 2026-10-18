# Browser Back must retain reading position

18 October 2026 · Fountain Coach static publication compatibility correction.

## Observed defect

A reader follows an ordinary link from `fountain.coach`, `/essays/` or a long essay, then returns with browser Back. The return is expected to preserve the reading position that made the link available. Instead, the shared `site/assets/estate-core.js` source explicitly chose `history.scrollRestoration = 'manual'` and called `scrollTo({top:0})` on initial rendering and `pageshow`. That imposes a fresh-entry rule on history traversal and makes the browser abandon its own history semantics (notably on WebKit/Safari). The rule is not justified by Linotype and does not belong to authoring semantics.

## Correction

Remove only the first forced-top block. Do **not** introduce sessionStorage scroll coordinates, per-route timers, onpopstate hacks, DOM reflow observers or special behavior for different link targets. The browser owns restoration with `history.scrollRestoration === 'auto'` by default, including Back/Forward. Fresh navigation and authored hash targets keep native behavior. Shared estate navigation, link hydration, Info scroll, themes and footer behavior remain byte-identical after the former block.

- Pinned old asset: `content/deployment-baselines/estate-core-scroll-before-20261018.js`, SHA-256 `d3c54081b69c0a3b62483100015dabc2bf69467d2903742909019b88a77cd869`.
- Corrected source: `site/assets/estate-core.js`, SHA-256 `1de0df086a4f0205f4fad5b5c7a0a212874d70042956f80968d84272f2e07950`.
- Path admission in `scripts/activate_static_essay.py` is deliberately limited to this one additional shared file. The remote installer verifies the predecessor SHA and byte-identical remainder of the asset. No other JavaScript mutation is accepted.
- The new immutable release copies all existing routes and assets, including the already published homepage and essay, and changes only `assets/estate-core.js`.

## Reproducible UI verification

A Chrome CDP test, `scripts/verify_scroll_history_browser.mjs`, opens three static publication routes. It scrolls to an internal link, follows the link, invokes browser Back, and compares scroll Y (within 18 pixels). It also asserts that the page uses native `history.scrollRestoration === 'auto'` both before departure and after return.

For a local preview, serve the source-controlled essay and assets from a single origin with the **deployed homepage projection**, not the separate unadmitted Bookshelf candidate in `site/index.html`. Example: make an ephemeral directory with `index.html` projected by `scripts/project_home_essay.py`, and symlinks to `site/assets` and `site/essays`. Serve it on port 8219 and start Chrome's debugging endpoint on port 9347. Then:

```sh
SCROLL_TEST_ORIGIN=http://127.0.0.1:8219 npm run essays:history
```

Witnessed before publication: all three tests returned to their previous scroll positions, with the browser reporting `auto`, rather than the original `manual`. The same three-route test must run against public HTTPS after deployment with `npm run essays:history`.

Static release and rollback test suite: `npm run essays:check` (16/16 tests). Original three essay bodies: unchanged byte-for-byte. This change does not alter unrelated subdomains or the not-yet-published Bookshelf projection.

## Publication acceptance

Required outcome: public `/assets/estate-core.js` digest matches the corrected source; prior homepage, essay collection, and article content SHA-256 remain unchanged. Navigate and Back in the actual browser. Store the terminal release receipt, including all public SHA witnesses. This corrects site navigation behavior, not content or rendering authority.

Local extended acceptance: Chrome at 1050×740, iPad-sized 820×1180 and phone-sized 390×844 each passed all three Back navigation cases (9/9), with scroll deltas of 0 pixels and native `history.scrollRestoration='auto'` before and after traversal. Safari's actual back/forward behavior remains separately observable on the user's iPad; the application no longer prevents it with a manual override.
