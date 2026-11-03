# v140 reader — controlled public publication decision

Date: 3 November 2026. **Status: PUBLICATION BLOCKED; no production mutation.**

## Source and ownership

Canonical writer/publisher owner: `Fountain-Coach/fountain.coach`, source commit `611c3e34c9dfffc932d86d957edf49bda46927ec`. Private accepted stage: `shared-shell-20261103-v140-same-folio-return` on the owner WLAN, with predecessor v139 retained. The reusable compositor remains owned by Fountain Press. No writer source, Solstice work, original score, or private recording is modified.

## What was actually constructed and tested

The isolated release branch `codex/v140-public-boundary-20261103` contains a deterministic builder, a Chrome/WebKit browser test, a typed EstatePublisher intent and plan, and this evidence. Its ignored output is `build/public-v140-text-only/`. Its candidate manifest marks `publicReleaseAuthorized=false`, `audioPlaybackIncluded=false` and `midiReadingDataIncluded=false`, so it is **not** a release receipt.

- Excludes the private Vergil hearing modules, narration bridge, the private Door performance, private media manifests/grants, MP3/WAV and MIDI listening data. The explanatory manuscript remains, and the withheld audio exhibit is identified honestly as private.
- Includes the full staged written edition and the 15 referenced source illustrations, plus all **41** already published Solstice Reading 01 images, verified byte-for-byte against `solstice-first-reading-manifest.json`. Includes the three source-licensed notices referenced by the Door essay.
- Candidate manifest: **65 allow-listed files, 15,585,249 bytes**, plus manifest. Its paths and SHA-256 digests are recorded.
- Browser acceptance: **8/8** Chrome/WebKit across landscape left/right and 768×1024 and 390×844 portrait. Returning from the book addendum at the same pointer position has **0 px displacement** in every test, restores the original folio, produces no console errors or missing HTTP assets, and requests no private audio or MIDI data. The optional narrator bridge is absent from this text-only edition.
- EstatePublisher CLI built successfully; `--inspect --strict` reports registration conformance PASS and native authority verifier PASS. Typed exact-host resolver returned `state=available`, `operation=estate.static-release.promote`. This only identifies the route; it is **not** permission or execution readiness.

## Exact production blockers

1. **Admitted artifact / authorization:** The 65-file candidate is a locally constructed, unsigned, unadmitted bundle, not an immutable artifact produced from a local FountainStore admission with a kit-owned authorization. Required proof is visible in `deployment-plan.json`; no typed production release request or terminal receipt exists.
2. **Production baseline divergence:** Live HTTPS `fountain.coach/` SHA-256 is `9814fc24e3018c36f310f0bc8da3ccaa3251e0100404be3da0b7dad8e7c02309`; checked-in `site/index.html` is `c33a6606a595b7401619e311de8c5ec3c2f8b80239515db923b343444ed73290`. Live `/for-agents/` is `120fa7d4471a5d1dc521e30a9e86ad1aaf2391d7a2145866e237f082caa49901`; checked-in `site/for-agents/index.html` is `9d4c6a3ff864f3c8fcdc994ebb9def6bfce167f8b3a8ffbb6be1cabddf013254`. Therefore the candidate must not replace the public root until its current active state, legacy routes and rollback artifact have been admitted and preserved. The old `publication-files.sha256` validates 96 old source files, **not** the current live server.
3. **Public scope:** The private Vergil and Door sound-study manifests explicitly deny public release. This candidate excludes them instead of overriding rights. The public text-only edition still needs explicit publication admission with reviewed scope; browser success cannot supply that.
4. **Effect evidence:** No atomic activation, typed production receipt, public HTTPS SHA readback of the candidate, or rollback proof has occurred. The private WLAN stage was not touched.

## Resume precisely

First reconcile the public live baseline through the current EstatePublisher production observer and preserve all established public routes. Next admit the text-only candidate and exact source/asset manifests to local FountainStore, acquire native kit-owned release authority and immutable artifact identity. Re-run browser/AX and rights/route checks on the admitted artifact. Then resolve and execute **only** `estate.static-release.promote` through EstatePublisher; require correlated terminal receipt, independent public HTTPS digest and previous release pointer. Never use direct SSH copying, push-as-deploy, staging symlink promotion, or compiler work on the production host. The private original v140 remains available on the WLAN.
