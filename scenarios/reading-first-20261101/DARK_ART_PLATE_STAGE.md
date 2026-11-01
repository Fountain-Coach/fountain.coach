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
