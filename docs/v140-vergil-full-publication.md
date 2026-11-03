# v140 — full Vergil reading publication

## Writer's approved scope, 3 November 2026

The writer explicitly instructed publication of the complete accepted stage **as produced**, including original-design Vergil voice in *Teatro — An Unfinished Composition* and *Vergil — Prologue*, the two source-aligned MIDI2 reading scores, Csound Studio / AudioWorklet playback, the original page composition, i↔logo same-position folio return, and the author-published Solstice image collection. This replaces the earlier incorrect decision to produce a text-only edition (draft PR #8). It does not admit unpublished review/audition takes, private voice-master WAV files, staging evidence, or host secrets.

Source owner `Fountain-Coach/fountain.coach` SHA `611c3e34c9dfffc932d86d957edf49bda46927ec`. Active and preserved private stage: `shared-shell-20261103-v140-same-folio-return`. Exact four live stage HTML/JS/CSS digests verified against committed acceptance.

- *Teatro* final 498.97 seconds, MP3 SHA-256 `d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd`; 1,050 source-timed MIDI events.
- *Vergil — Prologue* final 725.91 seconds, MP3 SHA-256 `4b2727e08bd7b3c0edea59f6faca92292e9447d980bfb1d2f963e829dba16881`; 1,516 source-timed MIDI events.
- Four final Door sound-study performances are separately admitted from their exact source digest, with third-party sound attribution preserved. Auditions and review fragments remain excluded.
- All 41 images in the already published Solstice Reading 01 are independently checked against the canonical source edition digest inventory. The book's original authored text and illustrations are preserved.

## Release artifact and tests

`scripts/build_v140_public_vergil.py` composes a public, source-verified projection from the immutable WLAN source into ignored `build/public-full-v140/`. It rewrites **only** the private-WLAN grant/hostname and publication rights metadata, leaving narration bytes, scoring and page composition intact. `scripts/build_v140_production_overlay.py` preserves the observed public v19 release from an independent read-only exact-host source, and adds the approved reader into ignored `build/public-release-v140-overlay/`.

Exact predecessor `estate-20261027-v19-door-score-accepted-shell-824404f`, independent public root hash `9814fc24e3018c36f310f0bc8da3ccaa3251e0100404be3da0b7dad8e7c02309`. Candidate `estate-20261103-v20-vergil-reader-611c3e3`: **219 files**, **64 existing public files preserved byte-for-byte**, 153 new files, index and release-manifest updated. Native EstatePublisherSSHDelivery prepare/preflight: PASS, 219 file hash inventory and nine independent release witness paths. Candidate manifest committed under `releases/` contains file paths, digests and rights declaration, no private binaries.

Tests on local HTTPS with the actual stage's MP3 byte-range support (206): **4/4** Chrome/WebKit two Vergil readings: Play/Pause, real Csound AudioWorklet/Ear activity, MIDI2 seek/source cursor, portrait reflow; **8/8** same-finger folio/addendum WebKit/Chrome tests: 0 px position delta and original reading position returned.

## Real production route dependency

Observed live `/estate/*` and `/solstice/assets/edition/*` fall through Caddy to Store (401), while `/` is static (200). The previously installed source-owning `Fountain-Coach/EstatePublisher` SSH client owns a new bounded route-admission operation on source branch `codex/v140-public-reader-route`: append those **two** prefixes to the existing exact-host `@fountainNewEssay` matcher and nothing else. Native route CLI and XCTest pass **20/20**; its plan binds the original Caddy SHA, proposed SHA and v19 predecessor. This Caddy change is a demonstrated prerequisite: merely delivering the reader files would leave audio, JS and MIDI unreachable.

The two native production operations must be verified separately: (1) route admission with Caddy validation, rollback and original release retained, then (2) `EstatePublisherSSHDelivery deliver` with 219-file immutable manifest, independent HTTPS SHA read-back and predecessor retained for rollback. Only a terminal public receipt and public browser/HTTPS observations establish that publication happened.

**State at preparation:** authorized and source-verified candidate, not yet a live public release. Do not claim production success from this document alone.
