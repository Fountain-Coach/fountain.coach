# Vergil v137 — one transport, fixed synchronized cursor, invisible Csound mastering

**Task:** simplify the accepted v136 private Linotype reader without replacing its recordings, MIDI2 score, book composition or underlying SatzfunkPlayer mastering instrument.

## Intended reader behaviour

- Each source-verified Vergil reading has one standard-sized system-font transport button: ▶ while paused and ❚❚ while playing. Use Play/Pause accessible labels and a 44 × 44 CSS hit area.
- Follow + audio cursor is the *fixed* reader policy. There is no narrator mode selector. Exact timed word spans still drive folio following and permit source-addressed tap-to-seek; no invented word times.
- The Audio / Voice sound user-choice disclosure is not projected. Studio Csound is explicitly configured for each fresh private player. The pre-existing software Original bypass remains internally available as a fail-safe, but not as a reader dropdown.
- Remove exactly the two `voice-mastering-leaf` sections and their interactive Bidule-like patch UI from the end of the two narrative works. The story ends at its authored final paragraph.
- Keep the existing Csound default voice patch, Ear acoustic witness and HTML media destination routing. No new player, output selector, preprocessed recording or synthesizer.
- The default Csound voice patch targets EBU/BBC -23 LUFS integrated and -1 dBTP true peak; it is **not** certified to those measurements by the existing live output path. Sample-ceiling and short Ear RMS measurements are not an integrated LUFS/true-peak witness.
- Preserve immutable private WAV/MP3 and exact MIDI2 score bytes; do not public-publish.

## Source-owned delta

- `index.html`: delete the two source-separated patch endings only; preserve all 29 Teatro and 40 Prologue authoritative source blocks and digests.
- `vergil-midi2-narration.mjs`: fixed mode `cursor`, no select or label, retain verified score admission, source-based navigation and pointer scrub.
- `teatro-vergil-hearing.mjs`, `vergil-prologue-hearing.mjs`: remove patch mounting and options disclosure; retain admitted player's media/score identity, Csound Studio default, play/pause state and elapsed time.
- `reading-first-app.js`: remove deleted patch end-leaf restoration special case. Ordinary page anchors survive reflow.
- `teatro-vergil-hearing.css`, `vergil-prologue-hearing.css`: remove obsolete patch UI and control dropdown styling; use system transport glyphs.

## Finite acceptance

1. Browser admits both real source-locked private readings and both MIDI2 sidecars unchanged, with `mode=cursor`.
2. No audio settings / narrator selector or patch end leaf in DOM; final rendered page has no `voice-patch-surface`.
3. Play/Pause icons toggle with the actual HTMLMediaElement state; default Csound engine starts and Ear observes real PCM.
4. A real source-addressed timed passage moves the page and leaves a visible cursor, including after responsive reflow. Tap-to-seek remains available.
5. Chrome and WebKit at desktop and portrait widths; independent AX checks without console errors.
6. Immutable v137 private stage deployed as exact delta from active v136, preserving v136 rollback. No public publication.
7. Audible-quality judgement and integrated programme loudness certification remain separately unproven; a BBC *target* is not a certified file master.

**Ownership:** SatzfunkPlayer owns the unchanged default Csound chain; Fountain Press owns pagination and cursor; Fountain Coach direct-static source owns this reader presentation; EstatePublisher owner-WLAN delivery owns private staging. The prior `STAGED_V136_SOURCE_MAP.json` remains historical evidence, not a template to overwrite.
