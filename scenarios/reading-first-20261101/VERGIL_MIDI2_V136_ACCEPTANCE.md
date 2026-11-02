# Vergil MIDI 2.0 Narrated Reading — Private v136 Acceptance

Date: 2026-11-02
Scope: Both existing private First Readings on the owner-controlled WLAN. No public release.
Stage URL: https://192.168.8.50:8243/estate/
Active immutable candidate: shared-shell-20261102-v136-vergil-midi2-range-anchor
Previous immutable release: shared-shell-20261102-v135-vergil-midi2-follow-cursor

## Milestone results
M0: governance, source owners, exact failure boundaries and milestone plan recorded.
M1: SatzfunkPlayer source/media SHA-256 bound reading score, verified timed word spans, real MIDI2 Flex Lyric UMP, MIDI2 Clip File export. Nonmatching source and unsupported events are rejected.
M2: MIDI reading events follow the existing HTML media currentTime; no second transport. Play/pause/seek/dispose and mismatched source refusal tested. SatzfunkPlayer full suite: 133/133 passed.
M3: Fountain Press source spans resolve to exact measured Linotype leaves. Manual, Follow, Cursor modes and user-initiated reverse seek implemented. Three source-controller tests pass. Chrome and WebKit proved contiguous source offsets across four measured fragments.
M4: Two accepted private Vergil WAVs aligned by already-installed local Apple SpeechTranscriber; real word candidates independently compared with canonical text. Teatro: 1050/1090 tokens (96.33%) produced MIDI events. Prologue: 1516/1581 tokens (95.89%). Unmatched, uncertain and overlong Flex tokens are omitted, not interpolated; human word-timing review is NOT claimed.
M5: Private staging v136 browser acceptance complete, subject to the explicit physical iPad and source-reconstruction qualifications below.

## Actual runtime acceptance
Eight of eight exercised cases passed for Teatro and Vergil Prologue, in Chrome and WebKit at 1024x768 desktop spread and 390x844 single-page dimensions:
- Full source/media/score admission and the real MP3 in the media element.
- Seek from the opening to a timed spoken word; active folio changes to the appropriate source paragraph.
- At a known admitted word, Cursor mode draws a visible underline at the typeset text.
- Manual mode removes the cursor and holds the last followed page during later audio seeks.
- Returning to Cursor mode restores the source-aligned position and reverse seeking.
- No JavaScript page errors.

Additional direct browser proofs:
- Chrome Teatro and WebKit Prologue: clicking the actual rendered word underline issued a real SatzfunkPlayer seek to a source-verified timestamp (247.02s and 387.66s respectively).
- Repeating the same click in Manual mode did NOT initiate seeking.
- Browser reflow from 1024x768 spread to 390x844 single page preserved the narration block, page location and visible cursor.
- Chrome/WebKit actual recording playback confirmed after the stage server fix; recorded tests closed their browser sessions afterward.

## Missing HTTP byte-range support was fixed at the owning WLAN HTTPS stage boundary
Observed failure: SimpleHTTPRequestHandler returned 200 with the full MP3 to a Range request. HTMLMediaElement exposed seekable [0,0] even after buffering, and seeking failed.
Correction: source-owned serve_shared_shell_preview_https.py now admits range handling for exactly two approved First Readings, in addition to existing Door essay MP3s. Independently verified:
- HEAD: Accept-Ranges: bytes.
- GET with Range bytes=200000-200127: 206 Partial Content, Content-Range and 128 received bytes, for both readings.
- Local HTTP regression test exercises HEAD, 206, malformed/out-of-range 416, and an unrelated MP3 which retains ordinary response behavior.
- No Caddy/public service or DNS changes. This HTTPS stage service script is operational infrastructure outside immutable content release; its SHA-256 is 08bdb55c7073108af0ad1b15287c91e2f9dac54862ffc051bfa2976c1f483e78.

## v136 lineage and source identity
Staged v136 is a byte-preserving copy of v135 except for assets/linotype/reading-first-app.js. That JS received four in-memory anchor bookkeeping lines, so audio-driven page turns survive responsive recomposition without writing a manual bookmark. Actual staged JS SHA-256: 91bd9274ec80627b97fdcdc5c8da2f2dc74fcd9125a993517d3c3594d1e1248b. Independently fetched HTTPS bytes match.
The previous v135 release remains in releases/ for rollback. Both stage services are active and active source-lock says WLAN-PREVIEW-NOT-PUBLIC with authorPublished=false.

Exact private audio media were not altered:
- Teatro MP3 SHA-256: d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd
- Prologue MP3 SHA-256: 4b2727e08bd7b3c0edea59f6faca92292e9447d980bfb1d2f963e829dba16881
- Teatro private MIDI2 score SHA-256: 1a04fd7b6835c183b4cd1f01146c1769e0974466393d398e4043691931efebb8
- Prologue private MIDI2 score SHA-256: f96d3f09c24e81cdd72590536bd28bb4ccd64ec2cf358d24a8d4c0a09178794d

Owner code revisions:
- Fountain-Coach/SatzfunkPlayer d50140ddc8bb0ec12aec26499ac55c1c7d907a91
- Fountain-Coach/fountain-press 9393405ec72d9640705605fb1273184dc87c2a14
- Fountain-Coach/fountain.coach 7fed09493613a9826dce5c9b971287a1a85248a2 (plus this acceptance report)

## Limits and next promotion gates
- The in-service staging reader app is derived from the accepted v135 stage asset; the whole staged JS is not yet identical byte-for-byte with the current fountain.coach Git branch reader-app source because the earlier staged editorial baseline has independent revisions. This four-line delta is committed and stage-preserved, but fully reproducible Git-to-stage reconstruction still requires reconciliation before any public promotion.
- Source accuracy checks are exact lexical comparison with machine-generated timed words, NOT human-verified phoneme boundaries. Gaps intentionally produce no cursor.
- Physical iPad Safari listening, gestures and accessibility acceptance have not been witnessed. Browser WebKit simulation does not prove a physical device.
- MIDI2 Flex Lyric/Clip is a software projection here; physical MIDI2 output and hardware MIDI-CI are not claimed.
- BBC/EBU integrated loudness and true-peak certification remain a separate mastering gate.
- No public release was performed or authorized.
