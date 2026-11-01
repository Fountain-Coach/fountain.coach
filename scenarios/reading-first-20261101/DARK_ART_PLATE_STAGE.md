# Dark illustration plates — staged source contract (1 November 2026)

**Scope:** Correct an observed dark-mode presentation defect in the existing Fountain Press Bookshelf and illustrated essays/First Readings on the private staging host. Do not change author-owned art, text, collection membership, public production or the FCIS Skill.

## Observed problem and bounded correction

The live v94 reader's dark theme sets the page background to `rgb(17, 21, 16)`. Before correction, the square-thumbnail background was **transparent**; some SVG ink and transparent artwork had no guaranteed light ground, so the readability of the actual art depended on its embedded pixels. The writer has explicitly rejected treating transparency or automatic inversion as dark-mode responsiveness.

Use the existing **source-owned print plate**, with a stable paper value `--art-paper: #f5f2e9`. Give every square thumbnail this backing. Full-folio Teatro Scores, essay hero art and source-integrated figures get the same background behind unmodified pixels. **No CSS inversion of illustrations** and no claimed authored dark variant. The illustrated book remains legible in dark mode because it carries its intended paper field; it is not a newly reinterpreted image.

## Evidence and limits

`test_dark_paper_plates.cjs` exercises the actual private HTTPS origin using both 1180×820 landscape and 390×844 phone layouts. It first compares candidate CSS/JS to the existing staging origin, then must run again with `LIVE=1` after activation. For all 37 gallery thumbnails it compares work/source image URL across themes, enforces source-preserving `object-fit: contain`, checks the opaque paper plate and no image filter, confirms accessible item labels, unchanged fixed footer, and checks an essay source-art folio where visible.

This correction is a **dark-mode-safe presentation of unchanged light art**, not delivery of individually authored dark-image renditions. Author-approved true dark variants, physical iPad Safari gestures, VoiceOver reading order, EU compliance and public production remain unverified. Do not assert them on browser screenshot evidence alone.

**Existing FCIS rule:** the page is the frame; preserve image source identity and accessible labels, do not automatically invert/crop transparent artwork, keep media source bound. This is a small editorial CSS/layout correction, not a second renderer or source modification.

**Staging operation:** copy the active immutable v94 private WLAN release to a new v95, replace only the checked-in stylesheet, retain rollback, update an explicit source/asset digest receipt, atomically move `current`, and verify live HTTPS bytes and browser behavior. Source Git and public publication authority remain separate. Native iPad launch evidence, if obtained, is not a VoiceOver witness.


## Live v95 and physical-device boundary — 1 November 2026

- **Active immutable WLAN release:** `shared-shell-20261101-v95-dark-art-paper`, unchanged v94 retained as rollback; HTTPS trust returned 200/TLS verify 0. The source-only CSS revision is `Fountain-Coach/fountain.coach@ce31d16dfed0885434e2bd302a7bafb283963c33`.
- **Independent live browser:** `dark-paper-live.json` verifies 2 light/dark WebKit viewport profiles with all 37 original gallery image URLs unchanged, contained with no filter and warm opaque backing; the existing `test_bookshelf_gallery.cjs` again passed 3 landscape/portrait/phone profiles with same-reader image navigation, preserved offsets and fixed footer.
- **Accessibility:** `reader-axe-live-v95.json` records 15 un-intercepted live WebKit / axe-core 4.13.0 WCAG A/AA scans (Bookshelf, Essays contents, First Readings contents, illustrated essay, Teatro Score across 1180x820 light+dark and 390x844 dark), with **zero reported violations**. This proves only the tested browser checks, not complete EU accessibility or native VoiceOver.
- **Physical iPad:** A paired, unlocked, developer-mode 11-inch iPad Pro running iPadOS 26.6.2 was confirmed. Apple CoreDevice successfully launched MobileSafari with the exact stage URL. A disposable, signed XCTest UI-test app was compiled outside source repositories but iPadOS **refused its installation** because the device has reached the free developer-profile limit of three installed apps. No existing Reframe or Teatro test installation was deleted or replaced. No native screenshot, gesture transcript or VoiceOver read order was observed. `physical-ipad-acceptance.json` is the exact bounded record.
- **Open source PR:** Fountain Press PR #3 contains the staging composition but currently conflicts with `main` in public publication artifacts (`edition.json`, `publication-files.sha256`, and two essay HTML files). Do not silently resolve those authoritative public changes, or claim public production published. Source review remains open and public sites unchanged.
