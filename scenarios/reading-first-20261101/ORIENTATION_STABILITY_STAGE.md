# Orientation / resize stability — live iPadOS acceptance boundary

Date: 2026-11-01

## Observed defect on v97

The user's physical iPad reported flicker and inconsistent layout when switching landscape to portrait. A controlled, **unintercepted WebKit baseline** on the live v97 origin recorded 7 destructive Bookshelf viewport replacements across repeated orientation-width/height transitions, transient selection/collection loss, and temporary footer misalignment.

Source: `orientation-live.json` baseline is **v97 only**; it is not v98 acceptance.

## Narrow correction

Source-owned `reading-first-app.js` no longer reconstructs the Bookshelf when only viewport size changes. It retains one persistent collection DOM and its selected work, coalesces the burst of resize notifications, reprojects compact Contents/Images visibility and restores the active collection only after geometry settles. The resize path is throttled for paginated works to avoid repeated work-page recomposition during orientation. The reader height is owned by CSS `100dvh` instead of a JavaScript assignment of lagging `visualViewport.height`. No published text, source media, collection membership, page renderer, imagery or user-authored CSS token is modified.

## Acceptance

`test_orientation_stability.cjs` exercises transitions from 1180×820 to 820×1180 and intermediate sizes, and back, on WebKit with mobile/touch emulation, including the selected First Readings collection and work identity. The strict candidate passed **zero DOM replacements**, **zero readiness transitions**, **stable selected work**, and fixed footer alignment across all sampled geometries. Source candidates are intercepted for candidate-only checks; acceptance requires rerun without interception on the actual private stage.

Unmodified `test_collection_identity.cjs` passed 3 landscape/portrait/phone profiles and direct reading/selection/return. `test_dark_paper_plates.cjs` passed 2 light/dark profiles. `test_essay_abstracts.cjs` passed 21 essay profiles.

## Physical / iPadOS limits

A paired physical iPad Pro 11-inch is available through CoreDevice; direct orientation control was attempted and Apple explicitly returned `Device Orientation capability not supported` for this hardware. Prior physical XCTest installation was refused at the **three-app free developer profile limit**, and we did not remove existing Reframe/Teatro apps. A separate iPad Air iOS 26.5 simulator was booted for controlled native Safari rotation, but its first boot was excessively resource-intensive and could not complete a witnessed Safari page before being shut down. The existing Reframe simulator was not changed.

**Do not claim native iOS Safari gesture or physical iPad/VoiceOver acceptance.** A WebKit touch-mode/browser test is useful evidence for a bounded fix but cannot witness actual iOS orientation gestures, toolbar behavior or VoiceOver.

## Deployment boundary

Owner-controlled private HTTPS WLAN staging only, immutable v97 rollback retained, release v98 with exactly the updated reader JS/CSS and evidence, independent HTTPS and release SHA-256 readback. Production domains remain unchanged. Fountain Press PR #3 remains a separate conflicting Git source review; do not force merge.
