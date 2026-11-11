# Orange Dot — Fountain Press production-based review, 11 November 2026

## Decision

**Author-WLAN staging accepted.** The Orange Dot figure-spacing correction is active as the immutable Fountain Press stage release `shared-shell-20261111-v193-orange-dot-portrait-spacing-b431528` at `https://192.168.8.50:8243/estate/#/read/orange-dot`. Both canonical preview services are active, the v192b rollback is retained, and source-lock admission verified exactly one shared Reader compositor change. In the troubled *The Vigilance Regulator*, the second figure is now positioned after its source paragraph with 15.3 px before, 18 px after; the portrait chapter is four measured leaves, formerly five.

**Production-based candidate verified but NOT PUBLICLY PUBLISHED.** The actual public `fountain.coach` static root remains `fcis-essay-heading-20261110-8f58f29`. The current production Reader is earlier than author-WLAN staging. Replacing the entire staged site in public would overwrite unrelated published material; this operation intentionally did not.

## Production predecessor and source

Read-only SSH observed the current public root `/srv/fountain-static-publications/fountain.coach/current` with the exact release above. Public `/estate/index.html` SHA-256 `005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49`; public versioned Reader application SHA-256 `1b574fe1d24004a7c4d25ecc5df31cb098ac0784f4a87158ac5208d7cda06dd7`; public compositor SHA-256 `e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a`.

The source owner repository is `Fountain-Coach/fountain.coach`, Orange Dot author source revision `b431528`, with the original selection and source file SHA-256 assertions. Twenty-three complete original texts and twenty-nine original accompanying images survive; three exact images reuse existing First Readings originals and twenty-six are separate retained files. *Integration* is referenced but not duplicated, and the two intentional First Readings reprises stay verbatim.

The public-base composition scripts are `scenarios/orange-dot/compose_public_orange_sources.py` and `build_public_press_candidate.py`. Their pinned original public and authored source snapshots are held in `DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/baseline/`. The project-owned scripts recreate only a bounded source-addressed Orange Dot addition. The assembled private production review candidate is `DockerDisk/ArchiveOps/orange-dot-public-preflight-20261111/mirror/`, not a public URL.

## Exact public delta and independent tests

- The source-generated public candidate has precisely **475 files**, compared with **445** live public files: `estate/index.html` is replaced by the source-addressed Orange Dot graft, and **30** new paths are added (26 original images, two versioned Reader JS sources, Orange Dot edition manifest and its collection route). The other 444 public files remain exactly SHA-256-equivalent. Public Essays and First Readings source galleries are unchanged.
- Candidate HTML SHA-256: `7db826d5aa32da727213ce2d53dc1e1a35efe5ee820c987ae6066e2dd1500f3b`. Versioned Reader app SHA-256 `d2c2020390a35d7def6409abf50171e1998a0f1baa4bf8da3cbaf50bc3aa1a81`; corrected compositor SHA-256 `837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a`.
- Source fidelity verification: 23/23 full texts and 29/29 source image digests, intentional First Readings overlap policy, unchanged 32 original First Reading templates and 160 Governance source templates on the private stage.
- Live staging: iPad portrait (820×1180), landscape (1180×820), phone (390×844): 23/23 Orange Dot entries, 29/29 original images, first/last/previous navigation, genuine folio turn and no Reader exceptions. Neighbor regression across Essays, Scores, First Readings, Orange Dot and Governance: 15/15 representative work openings.
- Production-based *local mirror*, not the public host: WebKit 3/3 responsive viewport tests, three Bookshelf collections in exact sequence `essays,first-readings,orange-dot`, original Essays/First Readings identities preserved, Orange Dot illustration correction measured. All six supplementary Orange Dot source figures were audited in portrait, facing-spread landscape and phone views; image/caption counts preserved and adjacent figure/text spacing consistent.
- Editorial note: some final folios have short source-tail paragraphs. These are not image gaps, but should be visually proofread on a physical iPad. Physical iPad Safari/VoiceOver acceptance has not yet occurred.

## Writer's release exclusion: the former Works book

The writer decided on 11 November 2026 to omit the **entire former Works book** from this Orange Dot release. The four source titles are *Between Gardens* (`score--between-gardens`), *Ballern Gehen* (`score--ballern-gehen`), *A Midsummer Night’s Dream* (`score--midsummer-nights-dream`) and *Above the Line* (`essay--above-the-line`). The Works-derived Scores collection is not included either. Their original sources and unpublished staging evidence are retained, not deleted. The actual public predecessor already lacked all four, so no live public content is being taken down.

`scenarios/orange-dot/release-exclusions.json` and `build_public_press_candidate.py` enforce absence from templates, galleries, source-owner records and the public candidate media inventory. The candidate/mirror test and three-viewport WebKit Reader acceptance passed after the release-scope change, preserving 23 Orange Dot texts/29 images and the existing Essays and First Readings. The canonical owner-WLAN v193 stage still contains inherited former Works volumes; **it is not this proposed public production candidate**.

## Public release gates — unfulfilled

1. `selection.json` explicitly says **“Private author-controlled WLAN stage only; no public release or automatic social distribution.”** The 29-image rights matrix in `docs/acceptance/orange-dot-public-rights-matrix-20261111.json` therefore marks the public redistribution/third-party subject clearance as unverified, not approved. Neither archive possession nor a past Facebook post proves permission for each public reissue. The user intends a future Press publication, but the source rights gate must be independently brought into agreement with that intention before delivery.
2. Physical iPad/Safari/VoiceOver and final editorial visual approval remain to be recorded. No automatic claims of iPad acceptance are made from Playwright screenshots.
3. Production delivery must use the native EstatePublisher release/receipt capability against the **named `fountain.coach` root** with current predecessor, exact 475-file SHA inventory, independently authorized content, public HTTPS witness set and retained rollback. A read-only native `inspect` already succeeded and reported `fcis-essay-heading-20261110-8f58f29`. No `deliver`, Caddy changes, DNS changes, public symlink update or production media modifications occurred in this task.

## Next editorial phase

Only after Orange Dot is properly admitted beside First Readings should *Revisiting the Head Boxers Medicine Show* be developed as a new source-backed Reading. It must link or cite individual Orange Dot and First Readings paragraphs semantically, preserve each of the 20 historical film captions and media identity, distinguish retrospective tinnitus listening narrative from medical claims, and obtain its own separate source/rights/publication review. The staged Medicine Show stays unpublished.
