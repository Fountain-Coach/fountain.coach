# Satzfunk voice patcher — v134 private stage acceptance

**Date:** 2 November 2026. **Scope:** the final Linotype leaf of both private Vergil readings. Not a public release or an EBU R128 broadcast-master certificate.

## Outcome

The former four-cube axonometric graphic has been replaced by a true, source-bound patching surface inside the existing paginated Linotype reader. It resembles a compact Bidule-style audio network, with nine identifiable modules, input/output jacks, dynamically rendered signal cables, a selectable processor inspector, parameter control and a real Ear measurement. This is interactive DOM, not a pre-rendered image and not a replacement media player.

The source-owned signal graph is `satzfunk.voice.mastering.01`, exposed by SatzfunkPlayer. Its default route is:

`Vergil PCM → Rumble (75 Hz) → Presence → De-ess → Level → Makeup → Safety → Ear → Browser output`.

Connecting the output port of one supported module to another input **changes the validated graph and recompiles the executable Csound instrument**. A disconnected processor remains in the palette for reinsertion. The bounded voice profile permits one acyclic PCM path; feedback, unknown ports and arbitrary Csound injection are refused. Safety, Ear and system output are mandatory and cannot be removed. Parameter ranges are source-defined. The original media and the browser-selected physical output remain unchanged. Studio is default; Original continues to be a true bypass.

On a live update, the replacement Csound instrument retires the predecessor at initialization with the native `turnoff2_i` opcode after successful compilation. Its return should not be mistaken for an `inputMessage` status. The existing Teatro host and Ear tap are reused; no second audio engine or unadmitted CsoundTeatroScenario was invented.

## Sources and build evidence

- Player: `Fountain-Coach/SatzfunkPlayer`, branch `codex/fcis-public-readaloud-20261031`, commit `acfc1c38212f169e15dc453298f9729802028935`; owner files `voice-patch.mjs`, `voice-patch-view.mjs`, `voice-mix.mjs`, `satzfunk-media-element.mjs`.
- Linotype owner: `Fountain-Coach/fountain.coach`, branch `codex/teatro-vergil-new-reader-20261101`, commit `0da6826c5feb1bc923265ab232811d10bb2fb4bc`; earlier folio projection `7f10702`.
- SatzfunkPlayer full suite: **129 tests passed, 0 failed**, including topology and unsafe-routing refusals.
- Local Chrome/WebKit live AudioWorklet tests witnessed changing Rumble cutoff to 105 Hz and reconnecting source to De-ess, with continued audio and Ear observations. No simulated DSP was used.
- Both reader controllers now bind the patch host only when their own source volume is active. A prior defect allowed the inactive reading controller to mount another player's patch view. The active-reading guard was verified using a real WebKit Prologue rewire.

## Live private WLAN staging

- Active immutable release: `shared-shell-20261102-v134-vergil-patch-reading-bind`.
- Previous release, retained for rollback: `shared-shell-20261102-v133-vergil-bidule-patcher`.
- Private HTTPS entrance: `https://192.168.8.50:8243/estate/`.
- The v133 candidate changed only the two source-generated patch modules, the Player integration modules, two source-bound reader integrations, the shared audio CSS and the exact two final-leaf projections, from active v132. The v134 corrective delta changes only the two reading-controller files. No WAV, MP3, manifest, narration source block or release authorization changed.
- Teatro private MP3 SHA-256: `d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd`.
- Prologue private MP3 SHA-256: `4b2727e08bd7b3c0edea59f6faca92292e9447d980bfb1d2f963e829dba16881`.

## Browser acceptance

**8/8 passed:** Chrome and WebKit, desktop 1024×768 and phone 390×844, for both Vergil readings. Each test reached the source-separated final folio, observed all nine nodes and eight default cables, no clipping or page overflow, started the original Csound AudioWorklet and witnessed real nonzero Ear RMS while playback advanced. No JavaScript page errors.

**Real WebKit rewire passed:** Prologue Source output connected directly to Safety input; the *Prologue player-owned graph* changed to `[source, ceiling, ear, output]`. Media advanced, Original bypass removed Studio Ear observation, and returning to Studio preserved the edited graph. No page errors.

The aesthetic is deliberately Linotype (paper, ink, small modules and restrained copper cables), while the graph and DSP behavior are SatzfunkPlayer-owned. Modules are accessible by named buttons and keyboard as well as pointer/click-to-connect. The source audio editor has **not** become a general-purpose arbitrarily branching Bidule replacement; it is the fully executable, bounded *voice mastering patch*.

## Unproven boundaries

- Ear witnesses short RMS/sample-peak windows before the Teatro host output gain. It does not measure integrated LUFS or intersample true peak. BBC/EBU -23 LUFS and -1 dBTP are delivery aims; no full-programme broadcast master has yet been independently certified.
- Physical iPad/Safari listening acceptance, drag-cable gestures on physical touch hardware, and producer's aesthetic approval are not yet witnessed.
- No public distribution authorization or production publication occurred.
