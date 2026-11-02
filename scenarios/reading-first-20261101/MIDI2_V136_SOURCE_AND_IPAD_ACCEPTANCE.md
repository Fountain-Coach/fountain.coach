# MIDI2 Vergil — Git/source reconciliation and bounded accessibility closure

**Date:** 2026-11-02. **Active:** private owner-WLAN
`shared-shell-20261102-v136-vergil-midi2-range-anchor`.
**Public publication:** not requested, not performed.

## Reproducible exact staged source (completed)

The v136 checked-in direct-static reader now matches the observed approved stage **byte-for-byte for the selected reader route and 38 dependency assets**, using `STAGED_V136_SOURCE_MAP.json` and read-only `verify_v136_source_map.py`.

- `index.html`: exactly `78d4113fec4a70fccb84dcef18231d892a63b3128d1cf0813a9f3aacfecd3a19`, as read from the active v136 release.
- `reading-first-app.js`: exactly `91bd9274ec80627b97fdcdc5c8da2f2dc74fcd9125a993517d3c3594d1e1248b`.
- All 27 static `assets/linotype/` files: 27 exact source paths and independent SHA-256 values; the 8 projection-only versions live under `stage-owned-assets/linotype/`, while matching assets retain their exact Fountain Press / Teatro / existing Git owner.
- All 11 `assets/satzfunk-player/` files, including the pinned bundled MIDI2 codec under `vendor/midi2/`, have exact source paths and SHA-256. The older installed stage `index.mjs` has two fewer public exports than the current SatzfunkPlayer owner; its byte-exact variant is retained as a derived projection, **not used to downgrade the owner**.
- The `book-csound-host.js` stage bundle is already byte-identical to the Teatro owner source and is not redundantly copied.
- Two private original MP3 and two private source-verified MIDI2 reading-score digests are retained in the manifest. **No private MP3, WAV, source transcripts, credential, or alignment JSON is committed to Git**.
- The previous static content and app are recoverable through Git history. Historical `build_reading_first.py` is an older editorial assembler, not an authority to overwrite the checked-in accepted v136 direct-static route.
- Existing unrelated worktree modifications and unpublished image/generated content were not staged, rewritten or committed.

Verification: `python3 scenarios/reading-first-20261101/verify_v136_source_map.py` passed **38/38 assets plus the index**. Comparison with a separately fetched exact immutable v136 stage snapshot also passed **39/39**. The active stage release and both WLAN HTTPS services remained unchanged. This is an exact **selected source/assets** reconstruction, not a claim of verified production-first lineage or full-estate archival equivalence.

## Automatic spoken pages and cursor

Previously accepted actual-version tests remain recorded in `VERGIL_MIDI2_V136_ACCEPTANCE.md`: two source-verified readings, real HTMLMediaElement time, physical page-recomposition coordinates, 8/8 WebKit/Chrome cursor + page tests and 2/2 natural, continuous audio-driven page transitions. No replacement clock, invented word boundary or separate audio engine. No public rights changed.

## New accessibility evidence — 2026-11-02

`verify_midi2_axe_v136.cjs` and `MIDI2_V136_AX_ACCEPTANCE.json` capture 8/8 tests from **Chrome and WebKit × desktop spread and 390px portrait × Teatro and Prologue**. Each test selected a real admitted word with Cursor mode, observed one visible cursor mark, verified labelled narrator and voice controls, and ran axe-core WCAG 2.0/2.1 A + AA checks.

- **0 violations and 0 page errors** in all eight cases.
- The automated `color-contrast` check returned `incomplete` for all eight cases: do not claim confirmed colour-contrast compliance without another visual or computed-colour witness.
- These are real desktop browser/engine tests, not physical-device VoiceOver/AX tree acceptance.

## Physical iPad — what was and was not witnessed

On the paired, real iPad Pro 11-inch (3rd generation), iPadOS 26.6.2, CoreDevice readback confirmed booted, developer mode enabled, unlocked, landscape orientation and active backlight. `devicectl device process launch --payload-url` successfully launched the system MobileSafari with the actual private Teatro URL. The device connection and Safari process launch are **PROVEN**.

**Not independently witnessed:** a physical screenshot showing that the particular URL rendered in Safari, physical touch/scrub gestures, narration through the selected physical audio output, page turns, or VoiceOver speech/semantics on that device. The installed CoreDevice command surface reports device display geometry and application launch, not remote Safari DOM/AX or touch automation; the Xcode `devices://` screen-viewing URL had no handler. The previously documented iPad XCTest runner installation is blocked by the three-app free-developer limit. We did **not** remove existing Reframe, Teatro or other apps to force an unrelated installation.

These are exact environment/evidence limitations, not assumptions that the UI fails. Do not elevate them to an invented new host service or test framework prerequisite. Physical acceptance remains **UNVERIFIED**, not passed, and can be completed only with supported non-invasive physical-screen/touch/VoiceOver evidence.

## Future work boundaries

Any public release requires a separate rights/publisher decision, actual production-baseline verification, and readback through existing EstatePublisher authority. Complete-programme BBC/EBU mastering certification is separate; MIDI2 event timing does not certify audio loudness or speech alignment at phoneme granularity.

## Skills learning candidate

One transferable, proved procedure exists: **pin a source/media text digest, admit word-times only from an actual recorded performance, project MIDI2 timed lyrics without interpolating gaps, and bind the browser media clock to measured Linotype source offsets**. Candidate destinations are existing `midi2-js-workflow` (codec projection checks), `teatro-scenario-composer` (Ear/acoustic witness boundary) and `linotype-estate-template` (page-position/reflow and private-stage provenance). Prefer narrowly editing a relevant canonical FCIS skill over creating duplicate runtime capability claims. Canonical skill authority is `Fountain-Coach/.github` under Chapter 160; no ChatGPT skill installation or public Skills API promotion was performed by this reconciliation.
