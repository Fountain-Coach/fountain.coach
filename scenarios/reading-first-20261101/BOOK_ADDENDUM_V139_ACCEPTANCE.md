# Fountain Press book folio and publication addendum — private v139 acceptance

**Date:** 3 November 2026. **Scope:** source-owned Linotype reader / private owner-WLAN projection, plus the independently owned Fountain Press portrait-geometry correction. **No public release.**

## Author-requested edition design

- The publisher-logo control at the reader's upper left is now only the Fountain Coach mark. Its accessible name remains **Open Fountain Coach Bookshelf**. The visually oversized personal name was removed, not the author identity.
- The running head remains a discreet author credit on each normal reading folio. The repeated **Benedikt Eickhoff** imprint at the bottom of each page is replaced by a small circled **i**, a real keyboard-operable, accessible button.
- Selecting **i** opens the normal source-bound Press compositor on a separately paginated **Publication Notes** addendum, **not** a web footer panel, overlay, drawer or external application. Its contents name Fountain Coach as publisher, preserve contributor/source attribution, and link to the already identified [company, contact and legal information](https://status.fountain.coach/).
- The historic publisher/legal text at the close of *On Continuity* was removed from both its no-JS source and its reader template (two copies). The independently meaningful historical source note remains.
- The addendum returns to the exact previously composed reading position, including a non-first spread. It also has a direct internal route `/estate/#/read/publication-notes`, and does not create another bookshelf/reading-list entry.
- Original story text, source author blocks, image resources, private recordings, MIDI2 reading scores, narration cursor, player and default Csound processing were preserved.

## Source owners and immutable stage

- `Fountain-Coach/fountain.coach`: branch `codex/teatro-vergil-new-reader-20261101`; modified `scenarios/reading-first-20261101/index.html`, `reading-first-app.js`, `reading-first-press-engine.js`, and `reading-first-shell.css`. Only the reader shell, optional folio action and independently sourced metadata addendum are changed. The generic Press owner does not receive an unrequested global footer or second paginator.
- `Fountain-Coach/fountain-press`: branch `codex/linotype-sing-folio-20261029`; commit `710d785`, adjusts `runtime/book.css` iPad portrait height reserve and includes a local executable browser regression. The canonical source-verified Solstice edition still builds and verifies 30 works / 41 original images, with 21 Python and 3 Node tests passing.
- Active immutable private stage: `shared-shell-20261103-v139-clean-book-closure`. Predecessors `shared-shell-20261103-v138-publication-addendum` and `shared-shell-20261102-v137-vergil-simplified-reader` retained for rollback.
- The stage delta versus v137 contains only **four exact files**: `estate/index.html`, `assets/linotype/reading-first-app.js`, `reading-first-press-engine.js`, and `reading-first-shell.css`. No WAV, MP3, score sidecar or unrelated book asset changed. Both preview and HTTPS systemd user services are active.
- Independent HTTPS-vs-source SHA-256 check of all four changed assets: **4/4 passed**. Active index SHA-256 `a84e7fbaef789e5be4ff1dbcfe16030ce149442f759ebc49d0c346ce25cbe718`.

## Browser and editor acceptance

- **6/6**: Chrome and WebKit × 1024×768, 768×1024, and 390×844. Logo-only header; normal page has quiet running author and a real circled info action; selecting it shows the paginated Publication Notes; legal link exists, button disappears on the addendum; return restores the same folio; no page JavaScript errors.
- **2/2**: Chrome and WebKit returned precisely to a non-first Teatro facing spread (**3–4 / 10**) after opening and closing the addendum. The duplicated publisher paragraph was absent.
- **4/4**: Chrome and WebKit × 1024×768 and 390×844; axe-core WCAG 2.0/2.1 A/AA scan of actual addendum route reported zero rule violations or page errors. `color-contrast` remains **incomplete** under automation, not independently certified.
- **4/4**: Earlier v138 verification exercised both actual Vergil recordings in Chrome and WebKit, default Csound Studio AudioWorklet, Ear nonzero RMS, Play/Pause, fixed audio cursor and responsive reflow. The v139-only subsequent delta removed historical publisher text from `index.html` and did not alter the audio controller or media assets.
- **2/2**: The canonical Fountain Press iPad portrait overflow fix (separate owner) yielded exact 1024px document height at 768×1024, bottom footer at y=1023.34px, no overflow, single-page layout and actual Next-page interaction in Chrome and WebKit. The previous 8.34px regression was eliminated.

## Explicitly open

Physical iPad Safari touch, real VoiceOver/contrast and author visual acceptance have not been witnessed by these desktop browser runs. That does not invalidate source/browser acceptance but cannot be represented as native-device proof. Full EBU/BBC loudness certification remains independent and is not implied by preserving Csound Studio.

No production DNS/Caddy change, public delivery, iPad app installation, private recording publication, or new publishing service occurred.

## Reproduce

- `node scenarios/reading-first-20261101/verify_v139_book_addendum.cjs`
- `node scenarios/reading-first-20261101/verify_v139_return_later.cjs`
- `node scenarios/reading-first-20261101/verify_v139_addendum_ax.cjs`
- `node tests/verify_ipad_portrait_layout.cjs` in `fountain-press` after the pinned admitted Solstice local build

These are finite witness scripts, not a second rendering or publication authority.
