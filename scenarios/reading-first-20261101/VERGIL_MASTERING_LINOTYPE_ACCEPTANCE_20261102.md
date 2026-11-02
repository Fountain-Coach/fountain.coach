# Vergil — Csound Voice Mastering and Linotype End-Folio Acceptance

**Date:** 2026-11-02. **Scope:** Author-controlled WLAN rehearsal only. No public media release.

## Selected source and actual accepted stage

- Mastering owner: `Fountain-Coach/SatzfunkPlayer`, branch `codex/fcis-public-readaloud-20261031`, commit `9b7a45564dc4d127be5f90b151648b6148bf4690`.
- Reader owner: `Fountain-Coach/fountain.coach`, branch `codex/teatro-vergil-new-reader-20261101`, source commits `b8558f1`, `9aa555e`, `7b57142`, `9a4b3c5e4386ad1c7c6919060a51ea8d72bcb8a3`.
- Last accepted active owner-WLAN stage: `shared-shell-20261102-v132-vergil-mastering-concise`; previously verified at `shared-shell-20261102-v131-vergil-mastering-final-leaf`. The v132 immutable delta changes only `estate/index.html` (two end-folio editorial commentary sections), not any narrated source or signal-processing media.
- Retained rollback: `shared-shell-20261102-v124-vergil-ear-voice` and v131.
- Private HTTPS entrance `https://192.168.8.50:8243/estate/`; reader volumes `#/read/teatro` and `#/read/solstice-reading-01--vergil`.
- Independent HTTPS SHA-256 readback at v132: `index.html` `4cee16864ac5eae44039e71a9609235c39bb4fa7ac36c969427c4dc3e07327fe`; `voice-mastering.mjs` `c62b925cd1d422cdbbfce4048abf4b10d08e5bce84c86f71c5c4c871f27da89b`; `voice-mix.mjs` `8ca1edd51db37734930ed06b7588642f0bcec12bfac98d6162690f57c122bd9e`; `teatro-vergil-hearing.css` `dcd94023c173ace65f38431739804e9ef7576ca9db19662840b45e5d181b21ee`.
- Source-preservation check: removing the two `book-end voice-mastering-leaf` sections from v131 and v132 yields identical HTML, so no narrated prose, collection entry or other publication content was changed. Both private audio MP3s remain byte-identical to their prior releases; rights and private-candidate manifests are unchanged.

## Processing and Linotype projection

SatzfunkPlayer's default `Studio` mode compiles real Csound instr 20 on source-bound browser PCM: DC/rumble removal (75 Hz high-pass), tonal shaping, upper-band sibilance levelling, gentle speech dynamics, +6 dB makeup, sample ceiling, and routed stereo to the browser-selected destination; Original remains a genuine bypass. The original Teatro Ear AudioWorklet witnesses Csound before its host's final output gain, reporting sample-window RMS and peak; there is no second player.

Both readings conclude with a measured source-separate Linotype end leaf titled **The voice has a room**, showing a restrained axonometric acoustic score (SOURCE → TONE → DYNAMICS → EAR/OUT), commentary on voice presentation, live Ear witness when playing, and a clearly marked broadcast *aim*, not a compliance claim. Responsive reflow retains the actual end-leaf identity, not a fragile physical page number. The original Vergil recording identity and editorial text remain untouched.

## Acceptance

- SatzfunkPlayer `npm test`: **126/126 passed**.
- Native browser real @csound/browser Web AudioWorklet: signal compiled, ran, produced nonzero Ear measurements; Original bypass worked in Chrome and WebKit.
- Final end-folio stage drive: **8/8 passed, 0 failed** for both readings × Chrome and WebKit × 1024×768 landscape and 390×844 portrait. Each pass reached the actual last folio, found one visible score and accessible SVG, recorded no clipped/overflowing sheet pixels, started real reading, observed nonzero Csound Ear RMS/peak and live page commentary, with zero dropped Ear windows and no page errors. End leaf survives phone-width reflow.
- A temporary WebKit diagnostic release v130 helped identify a 6.8 px top-bound kicker overflow; v132 uses the normal immutable Linotype engine, not the diagnostic instrumented engine.
- This QA does not establish physical iPad speaker hearing, artistic approval, actual live device loudness, or complete-programme EBU R128 / BBC compliance. Ear is **not** an integrated LUFS or oversampled true-peak meter. The targets are **−23 LUFS integrated** and **≤−1 dBTP** with a 48 kHz final delivery master and independent measurement. Resampling the original 24 kHz source does not restore bandwidth. No public promotion was authorized or made.
