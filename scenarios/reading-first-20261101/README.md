# Fountain Coach — reading-first Fountain Press candidate

This is the source-bound development projection for the **private WLAN staging** of the reading-first entrance, not an independently approved public edition.

## Authority and source

- Publication owner: `Fountain-Coach/fountain.coach`, parent revision `9e5d437081212cccd11df964400b4cffd9ad23e2`.
- Composition provenance: Fountain Press viewport compositor, reused without claiming ownership.
- AV owner: `Fountain-Coach/SatzfunkPlayer@ce83b11b0a3785f5b3248417c0b53bbe0c80e72e`; exact owner modules `satzfunk-media-element.mjs` and `player-media.mjs` are copied to a static release without editing their behavior.
- Authoritative original essay snapshots and the earlier About text are retained as reproducible projection inputs in this directory.
- Original Door recordings: the four 14-second audio renderings and the source/score digests in `door-source-evidence.json`. `door-player-rehearsal.json` is **private WLAN rehearsal only**, with `publicReleaseAuthorized=false` and explicit source SHA matches. It is not publication approval.

## What this candidate changes

- One Fountain Press page frame contains the opening matter, Bookshelf, First Readings and the admitted essays. These are not links to another reader shell.
- *The Door Is a Score* retains the written manuscript and adds the real SatzfunkPlayer as `figure[data-press-media="satzfunk-player.recorded-directions.v1"][data-keep-with-anchor="previous"]` immediately after its authored listening passage. It uses source-owned track selection and media transport—not a generic widget or a link to a demonstration.
- Original obsolete playback-button labels and the inert Csound status are not projected as editorial text. The actual four published recording bytes are staged under a same-origin `media/` prefix; the original source/rights evidence is retained.
- The original player enforces HTTPS or loopback. On `http://192.168.8.50:8200` the Press figure honestly declares recorded playback unavailable, rather than impersonating a secure origin. A temporary Mac loopback tunnel to the same canonical staging release enables genuine rehearsal.
- The original light raster illustration remains **unresolved in dark mode**. Transparency, inverted colors and CSS recoloring are not admitted dark artwork. An author-approved dark asset must preserve the same source identity.

## Tests and scope

The private stage release `shared-shell-20261101-v84-inline-satzfunk-qa` carries `estate/evidence/inline-satzfunk-folio-audit.json`: 78 WebKit/Chromium work-and-layout combinations and 542 folios passed measured geometry and source-text checks. On secure Mac loopback, all four original tracks were selected in WebKit and Chromium at landscape, portrait and phone sizes, with no detected visible-page overflow. Native iPad Safari, VoiceOver, audible interpretation, live Csound, iPad HTTPS transport, themed art and the other essays' complete audiovisual exhibits are **not accepted** by those tests.

The existing EstatePublisher production checks and public publisher approval are separate. This branch is not a public release.

## Composition

`node build_embedded_sources.cjs` then `python3 build_reading_first.py` builds the authoring-time direct-static `index.html` from the retained original HTML. The builder uses the installed headless Chrome/Puppeteer runtime at the authoring workstation. The resulting output is a static route, not a hydrated second site or a second publishing authority.
