# Vergil — Csound mastering and Linotype listening score
Private staging acceptance · 2 November 2026

## Authored outcome

Both existing private Vergil readings now use the versioned `satzfunk.voice.mastering.01` Csound profile by default in SatzfunkPlayer (Studio). The Original mode is a real PCM bypass. A final separate Linotype end leaf, *The voice has a room*, presents an axonometric acoustic score and an Ear observation with concise editorial commentary. The score does not change, append to, or silently re-record the authoritative narrated text.

## Source authority and pinning

- Csound engine: original Teatro `BookCsoundHost` and its source-bound Ear observation; no second runtime.
- Player source: `Fountain-Coach/SatzfunkPlayer`, branch `codex/fcis-public-readaloud-20261031`, commit `9b7a45564dc4d127be5f90b151648b6148bf4690`; `src/voice-mastering.mjs` SHA-256 `c62b925cd1d422cdbbfce4048abf4b10d08e5bce84c86f71c5c4c871f27da89b`.
- Linotype source: `Fountain-Coach/fountain.coach`, branch `codex/teatro-vergil-new-reader-20261101`; end leaf `b8558f1`, source-anchoring `9aa555e`, concise WebKit folio commentary `7b57142`, subsequent reader end-reflow/flex-fit `9a4b3c5`.
- The staging HTML already contains other admitted stage-only work newer than parts of the local source tree. Promotion here preserved that content; **do not overwrite it wholesale from an older local HTML or reader file**.

## Active private release and preservation

- Verified active immutable release: `shared-shell-20261102-v132-vergil-mastering-concise`, owner WLAN Ubuntu staging service.
- HTTPS: `https://192.168.8.50:8243/estate/` (private, secure browser AudioWorklet origin).
- Predecessor: `shared-shell-20261102-v131-vergil-mastering-final-leaf` retained for rollback.
- Change v131→v132: exactly `estate/index.html`, replacing two overly long end-leaf editorial paragraphs without touching authored narration, audio or runtime.
- HTTPS readback index SHA-256: `4cee16864ac5eae44039e71a9609235c39bb4fa7ac36c969427c4dc3e07327fe`.
- HTTPS readback of mastering module: `c62b925cd1d422cdbbfce4048abf4b10d08e5bce84c86f71c5c4c871f27da89b`.
- Private Teatro MP3 remains `d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd`; private Prologue MP3 remains `4b2727e08bd7b3c0edea59f6faca92292e9447d980bfb1d2f963e829dba16881`. Rights flags remain private candidate, not public release.

## Mastering chain

`PCM source → dcblock2 → 75 Hz high-pass → related tone bands → high-frequency speech compression → main speech levelling → 2x makeup → bounded sample limiter → Teatro host gain → browser-selected output`.

Ear listens **before** the Teatro host's final gain and reports 1024-sample windows (RMS, sample peak, silence/clip state, timing) with a source identity. The browser and operating system retain device routing. The listening preference is an optional Audio disclosure rather than a permanent mixer.

## Independent witnessed acceptance

- SatzfunkPlayer: `npm test`, **126/126 tests passed**; live local Chrome/WebKit AudioWorklet compiles, processes and returns nonzero Ear output.
- Live v132 HTTPS: **8/8 passed**, both Prologue and Teatro at 1024×768 and 390×844, Chrome and WebKit. The final source-separate score is the last page, fits the measured leaf without clipping, and updates with actual Ear RMS and sample-peak observations while audio advances.
- Live v132 HTTPS: **4/4 passed** for Chrome/WebKit × both readings, Studio → Original bypass → Studio, with no page errors and no forged Ear observations during bypass.
- The mobile WebKit issue was resolved with shorter *editorial* copy; the earlier measurements identified paragraph-height overrun. The engine's clipping refusal remained intact.
- No public deployment was performed.

## Unproven boundary

**Not broadcast certified.** The application states BBC/EBU delivery **aim** of -23 LUFS integrated / max -1 dBTP. Neither Ear's live RMS nor the sample limiter verifies BS.1770 whole-programme LUFS, true peak after host gain, a 48 kHz PCM export or perceptual mastering across the entire recordings. Independent whole-programme analysis and physical iPad/Safari listening acceptance remain distinct tasks. Do not present this stage as final broadcast delivery.
