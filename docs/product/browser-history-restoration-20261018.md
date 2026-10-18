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

## Terminal live HTTPS acceptance (18 October)

Deployment from owning source commit `60126ef9b57ee2b86feec41438f075b9579ad8b1` completed through the unchanged immutable static publishing command. Production release: `static-composable-966fda4b634744` (predecessor `static-composable-90e7bbe2da6fd7`). Source-controlled terminal receipt: `docs/product/receipts/browser-history-restoration-production-20261018.json`. State: **PUBLISHED_HTTPS_VERIFIED**. The new shared asset is SHA-256 `1de0df086a4f0205f4fad5b5c7a0a212874d70042956f80968d84272f2e07950`; exact public HTTPS comparison confirms all other included pages, images and essay content retained their previous bytes, plus sibling routes remained unchanged.

Public Chrome CDP link → navigation → browser Back tests passed across **three independent route origins** (`/`, `/essays/`, `/essays/the-composable-book/`) at **desktop (1050×740), iPad portrait (820×1180) and narrow phone (390×844)**: 9/9 returned to exact original scroll position (delta 0px), with native `history.scrollRestoration='auto'` before and after history traversal. QA temporarily disables cache in the CDP browser so prior test sessions cannot reuse outdated static scripts. A fresh Chrome browser profile also passed independently. A tab containing an older cached document may need one refresh to load the deployed script; that is not a reason to re-enable manual history handling.

## macOS Safari retained-session repair — 18 October 2026

The previous production release removed a forced `scrollRestoration='manual'` assignment and a forced top-of-page `pageshow` scroll. Native Chrome (9/9) and fresh Safari WebDriver sessions initially passed; iPad Safari was user-confirmed working. **The user's existing macOS Safari article tab still reported `history.scrollRestoration='manual'`** and retained its scroll position at 4,998px. A browser-history entry can preserve its earlier manual setting even though the current site's JavaScript no longer assigns it. This is not a content issue and does not require new URL state or an invented scroll position store.

The corrected common estate asset now explicitly **sets `history.scrollRestoration='auto'` if it is not already auto**, without changing the current scroll position or forcing a `pageshow` scroll. This restores the browser's own behavior in legacy macOS Safari history sessions and keeps iPad/native Chrome behavior unchanged. The user's already-open Safari article was also repaired directly using Safari's JavaScript Apple Event; its mode changed manual→auto while `scrollY` remained precisely 4,998. This immediate tab repair is not the permanent fix; the source-owned asset is.

Source proof: production predecessor `content/deployment-baselines/estate-core-native-before-macos-repair-20261018.js` SHA-256 `1de0df086a4f0205f4fad5b5c7a0a212874d70042956f80968d84272f2e07950`. Proposed repaired asset `site/assets/estate-core.js` SHA-256 `020f32d995828892cd86e38edf190b02fadbfe34e2dad00cacfc6a5b8e8feec9`. The immutable deployment guard requires exact predecessor SHA, exactly one explicit auto restoration assignment, no manual-setting assignment, and an identical remainder of the shared estate script; all unrelated routes and JavaScript effects remain unchanged.

Real **macOS Safari 26.5** regression testing is at `scripts/verify_safari_scroll_browser.py`: start native `safaridriver --port 9349`, then run `SCROLL_TEST_ORIGIN=http://127.0.0.1:8219 npm run essays:safari`. The test deliberately creates a `manual` legacy history entry, reloads the edited site and verifies `auto`; it then follows actual links and returns with native WebDriver Back from the essay collection, long article across the `governance.fountain.coach` host, and homepage. The initial local result was **four cases accepted, all scroll deltas 0px**. Run the same against public HTTPS for production acceptance. The test uses an isolated Safari automation session and does not change Safari's user preferences.
