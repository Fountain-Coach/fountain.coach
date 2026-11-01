# Fountain Press — essay abstracts and illustration order (1 November 2026)

## Editorial decision

The seven admitted Essays are now read **title → a distinct editorial abstract → source-owned illustration when suitable → unchanged essay prose**, all within the same measured Fountain Press reader. This is a layout and editorial paratext change for the private owner-WLAN stage. It does not re-author the original essay manuscripts or change their ownership, publication approval, First Readings, the Bookshelf organigram, or the SatzfunkPlayer.

Each new summary is authored and checked against the actual corresponding source in `essay-abstracts.json`, with `data-editorial-role="abstract"` and a stable separate `editorial.abstract.<slug>` semantic source address. The original manuscript files and their SHA-256 digests remain unchanged. The original body text stays source-bound and exact after repagination; for *Did the Machine Actually Read the Book?*, its duplicated original title paragraph is lifted into the identical opening heading under the original paragraph's semantic address, rather than being printed a second time. No words from that authenticated title are omitted.

Six essays retain the original source illustration as the hero **after the abstract**, fitted to its own full folio with the original aspect ratio and unchanged artwork. The original reader-test screenshot in *Did the Machine Actually Read the Book?* is retained later in the essay as historical documentation, not presented as promotional artwork. The share-art fallback is a genuine 1200×630 WebKit screenshot of the composed opening spread: `essay-share-did-the-machine-actually-read-the-book.png`. `essay-share-manifest.json` records the share-art choice, abstract, alt text and intended reader target for all seven essays. These stage assets are candidate sharing images; private WLAN does not make them accessible to public social crawlers.

## Composition contract and finite proof

- Source reading: `original-essays-continuing.html` and `integrated-manifest.json`. Source owner: `Fountain-Coach/fountain.coach`. Staged Press compositor: `press-viewport-engine.js`.
- Use one authenticated image at the source's first visual reference point. No new stock image, logo, social collage, dark-mode inversion or external viewer.
- Keep abstract and title on the same opening folio. The next folio may contain the original illustration, with readable narrative continuing afterward. Do not turn figure content into hypertext navigation or crop it for arbitrary social ratios.
- The 21 essay-opening scenarios in `essay-abstracts-preflight.json` prove abstract presence, correct semantic/visual order, full original manuscript body, six source-art hero fits, one print-preview exception, no cropping, and successful pagination across 1180×820, 820×1180 and 390×844 WebKit geometries. Navigation is checked independently with `test_fcis_navigation.cjs`.
- A staged static sharing manifest and preview **do not imply** working OpenGraph metadata from a `#/read/...` hash route; public link-preview release remains separate.

## FCIS governance and scope

Read existing canonical `linotype-estate-template` and `reader-navigation-and-score-composition.md`; apply Goal Fidelity and Non-Invention, direct-static source, and owner-WLAN staging. An illustration belongs to its narrative, not to competing digital chrome. Do not create a new Skill, renderer, publishing endpoint or external player as a prerequisite. The inherited stage baseline is the active v92 private HTTPS reader, copied into an immutable v93 candidate, with explicit pinned Git delta and v92 rollback. Stage and public effects remain separate.

## Acceptance status

Local source candidate is browser-tested. **Live stage readback is recorded separately only after activation.** No physical iPad Safari/VoiceOver or public social scraper claim is made here.

## Actual WLAN staging readback — v93

- **Active immutable private release:** `shared-shell-20261101-v93-essay-abstracts-before-art`, on the existing `MacMiniDocker` HTTPS origin `https://192.168.8.50:8243/estate/`, copied from verified previous v92 with no public production effect.
- **Source commit:** `Fountain-Coach/fountain.coach@f76f52b7f9c594831ce76b4409edadde0cbb796c`; v92 rollback retained. Changed route and assets have individually recorded SHA-256 values in `essay-abstract-release.json`.
- **Unintercepted WebKit on the live stage:** `essay-abstracts-live.json` documents 21 successful essay/viewport compositions. `fcis-navigation-live.json` documents three successful navigation profiles, including fixed footer, scroll-position restoration and unchanged First Reading Score.
- **HTTPS asset readback:** the reader entrance, Works alias and Pointer alias, sharing manifest and 1200×630 print-folio PNG all returned HTTP 200 with valid TLS certificate (curl verify result 0).
- **Limitations:** the live essay abstracts are editorial stage drafts; source manuscripts and images are unchanged. Public social crawlers cannot fetch private WLAN image URLs, and physical iPad Safari/VoiceOver are not yet independently witnessed. Public production remains unmodified.
