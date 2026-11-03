# Linotype folio toggle — private v140 acceptance

**3 November 2026.** Source owner: `Fountain-Coach/fountain.coach`, branch `codex/teatro-vergil-new-reader-20261101`. Public release: **not performed**.

## Requested interaction

- On every reading folio, the discreet **circled i** opens the source-bound *Publication Notes* addendum.
- At the **identical bottom-left folio position**, the i is replaced by the **existing Fountain Coach logo**, with the accessible action **Return to previous reading position**.
- In facing-page mode the return logo is also present on an otherwise blank facing right leaf at the exact original right-hand folio coordinate. A finger that touched an i on either page touches the logo at the **same physical position**.
- On return, the previous authored reading and folio position are restored and the icon becomes i again. The redundant in-prose text link "Return to the reading" is removed.
- The logo is image-backed by the already owned `/estate/assets/fountain-coach-logo-transparent.png`. No new logo, second book engine, popup, drawer or website footer is introduced.
- The unchanged source text, publisher and legal link, private recordings, source/MIDI2 identities, Csound processing, narrative cursor, and book pagination remain in place.

## Independent private staging acceptance

Active immutable owner-WLAN stage: `shared-shell-20261103-v140-same-folio-return`, predecessor `shared-shell-20261103-v139-clean-book-closure` retained. Exact stage diff: **4 modified files, no other changes**.

1. `verify_v140_same_finger.cjs`: **8/8 passed**; Chrome and WebKit × left/right landscape folios and 768×1024 / 390×844 portrait, clicking the *same pointer coordinate* in both directions. Button-centre x/y difference reading → addendum = **0 CSS px**; returning addendum → reading = **0 CSS px**. The actual original folio numbers persisted: landscape `3–4 / 10`, portrait `2 / 5` or `2 / 11`. Zero page errors, no in-prose return link, and real source-owned logo returned.
2. `verify_v139_addendum_ax.cjs`: **4/4 passed**, Chrome/WebKit × spread and narrow portrait, zero detected WCAG 2.0/2.1 A/AA violations; automated colour contrast remains **incomplete**, not independently proven.
3. `verify_v137_simplified.cjs`: **4/4 passed**, both real Vergil reading routes on Chrome and WebKit: Csound Studio AudioWorklet and Ear signal witness, Play/Pause, audio cursor and responsive reflow.
4. Independent HTTPS SHA-256 readback **4/4** exact source file matches:
   - `estate/index.html`: `69e656346b219be35c030e437100e72338f54d3a70abecbe6030971773cb1c01`
   - `estate/assets/linotype/reading-first-app.js`: `557ba7736110ccf1ae4819549b3bf80fa1d6c411cf3b77b0e977db8aace23253`
   - `estate/assets/linotype/reading-first-press-engine.js`: `0fed47d6d2bb4c61565cbc37d9f6df21da3f650b365dc1856ee72fdb95eaba4d`
   - `estate/assets/linotype/reading-first-shell.css`: `769fb12fbe7205e90269ecbf3760c8a6d226e78347bd1d62f05035174d671247`

No public production, DNS/Caddy, publication approval, iPad app or private media bytes were changed. Physical Safari touch and VoiceOver remain separately unverified; browser touch-coordinate acceptance must not be conflated with native iPad proof.

To reproduce: `node scenarios/reading-first-20261101/verify_v140_same_finger.cjs` from the owner checkout with network access to the private owner-WLAN staging service.
