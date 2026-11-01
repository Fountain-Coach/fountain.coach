# Fountain Press — One collection, two coordinated projections (2026-11-01)

## Accepted design and source boundary

The writer accepted an Apple-informed correction to the existing reader: **a collection, not each of its views, is the horizontal navigation unit**. There are exactly two admitted collection identities, Essays and First Readings. Each derives textual contents and illustrations from the same existing source-authored sequence, without new publication membership, a UIKit runtime or a new collection engine.

On a wide spread, the complete vertically scrolling contents faces a vertically scrolling square-image gallery. On compact/portrait screens, the same collection keeps its identity and provides two properly labelled views, Contents and Images, shown one at a time. Both use the same `data-work-id`, source title, semantic selection, activation and breadcrumb. Focusing an item selects it without navigating; activating it opens its work. Selection is reflected in both views and survives return. One collection step moves the complete pair, not half a spread. Bottom reader controls and horizontal keyboard motion represent collections; vertical movements remain inside the respective scroll regions. A source item with no artwork remains text-only and never receives an invented image.

The book reader remains direct-static and source-bound. Original Essays, Solstice Reading 01 (including its two preludes and 30 illustrated works with 41 original illustrations), Teatro Score full-folio fits, SatzfunkPlayer and the v96 publication/reader frame remain unchanged. The implementation changes only `reading-first-app.js` and `reading-first-shell.css`. The manifest and page body remain unchanged. Style is restrained typographic emphasis, not an App Store card theme.

## Canonical FCIS procedure

Source: `Fountain-Coach/.github/.codex/skills/linotype-estate-template/`, updated within its existing `reader-navigation-and-score-composition.md` reference. Source commit and digest are recorded in source Git/PR. 64 organization skill tests and four canonical digest checks must pass before promotion. Provider Skill installations are not silently upgraded.

## Candidate and acceptance

- `test_collection_identity.cjs` executes native Mac WebKit against the real trusted stage origin with the exact two modified candidate files intercepted in preflight. Tests landscape 1180x820, portrait 820x1180 and phone 390x844.
- Proves **2** horizontal collection units; list counts **7 / 32** and galleries **7 / 30**; facing split or accessible compact choice; one shared selection state; keyboard select-without-activate; selection/return after opening a thumbnail; compact pane and independent vertical/collection positions; fixed reader footer; no browser page error.
- `collection-identity-preflight.json` is candidate proof, *not* live stage acceptance. Re-run with `LIVE=1` after activation; keep screenshots only as visual witnesses.
- Native physical iPad gestures, native VoiceOver, complete regulatory accessibility, authored dark image variants and public production remain separately unverified. Do not infer them from Mac WebKit or modify installed iPad apps.

## Staging delivery

Private owner WLAN only: preserve immutable `shared-shell-20261101-v96-contents-facing-gallery` as rollback; activate new v97 candidate by copying that release, replacing exactly two source-owned assets, recalculating SHA-256 and atomically switching the existing release symlink. HTTPS and live test readback required. No DNS, production publisher or new daemon.
