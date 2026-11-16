# Fountain Press v216: private WLAN CMS-style Bookshelf stage

**Source-bound candidate only until activated and independently read back.** This resumes the merged deterministic Fountain Press frontend source from `main@3b83455c2f08caae02ed63788e0b866bba734760`; it does not create another CMS, Reader, database, port, or public publication.

## Verified actual predecessor

- Canonical owner-WLAN host `MacMiniDocker`, original `fountain-shell-acceptance-preview.service` is **active in user-level systemd**, serving the registered `current` symlink at port 8200. A system-level `systemctl status` erroneously reports service absent; the relevant authority is `systemctl --user status`.
- Actual active immutable release: `shared-shell-20261116-v215-better-ear-reader-ready` (527 MB), terminal admission and exact predecessor in `candidates/better-ear-v215-*`. Its source-lock SHA-256 is `018c392afa8f91fa8c77bc7f452b25666820f29d209103d5c73f26fa01d5f638`.
- Source-preserved `estate/index.html` SHA-256 `2f4fd9ca80045594f373e425a03cb1df79965d320545c87d1ad2a2ab1fc4eeaf`; stage catalogue SHA `824b61b2f3927549089c964b3ae8fbb4962b5c36af87eef58667920fc5c6c0fa`. The stage app SHA `50bb76f72f280b8381f9f5f7b3ab5d2f79b1f3ab3217503bfee46a1004fbf452` is the actual v215 Reader, not a historical un-hashed script.
- The stage catalog has 3 explicitly `stageOnly: true`, `publicReleaseAuthorized: false` books; its root publication state is `private-owner-WLAN-editorial-review`, not public-production. First Readings and Orange Dot book entries have no individually set `publicationState` and are therefore normalized only *within the private stage snapshot*, while retaining their original nullable metadata.
- `estate/books/{essays,first-readings,orange-dot}/` are stale source shells; in each case the overlapping source work templates match the current stage byte-for-byte. Essays lacks Better Ear; First Readings/Orange Dot lack Better Ear and If Only. `estate/read/library/` does not exist and is blocked by the exact-v215 provenance gate.

## Source-owned same-frontend stage adapter

- `scenarios/press-books/wlan-stage-v215-predecessor.json` pins the 8 actual source file digests, all source-owned identities and the terminal predecessor, not invented development inputs.
- `published_frontend_stage.py` composes the same `reader-publication-state.js.inc`, `published_frontend.compile_app` and inherited Linotype stylesheet against the **actual stage's** complete manuscripts. It derives status-bearing private book/contents/gallery/adjacency, never flips a public-authorized flag, and refuses unknown source/rights or changed text while reconciling old direct books.
- All current source works remain in one complete authorial HTML. This stage has Essays 10, First Readings 32 and Orange Dot 23; original image entries 10/30/23. The 3 retained historical/archived Essays remain in the original templates and are not inserted into active contents.
- It writes an **immutable 9-path overlay**: changed stage `/estate/`, 3 existing direct books, source-bound catalogue, existing stylesheet and `source-lock.json`; new content-addressed Reader app and `/estate/read/library/index.html`. The catalog preserves the original private admission flags, credits and social images; private pages are `noindex,nofollow`. Historical social derivatives are retained rather than silently relabeled as a newly approved share asset.
- `serve_press_cms_v216.py` extends the current v215 gate, which must first verify the exact accepted v215 predecessor. It refuses unknown release identities, unreviewed source drift, unexpected new/deleted paths, modified unrelated files, altered guard source SHA and missing status-bound source-lock marker. It runs under the **same registered user systemd service**, not a secondary preview server. Stage admission lives in `wlan-stage-v216-admission.json`, with the exact candidate hashes and guard digest.

## Source candidate tests

- `python3 scenarios/press-books/test_published_frontend_stage.py -q` — 6/6; public mode tests `test_published_frontend.py` — 9/9.
- `verify_published_frontend_stage.py` — exact 9-file overlay with all 78 source templates byte-preserved, staged private status and source-lock preservation; passes. Second separate build produced **byte-identical 9-file output and receipt**.
- Negative cases: private state promoted to public refused, missing book/source proem refused, historical archive relisted refused, source SHA drift refused, non-canonical library page refused even with recalculated checksum, changed catalogue public permission refused even with recalculated checksum.
- Actual WebKit browser using the **real WLAN origin and all inherited stage assets**, overriding only the exact nine candidate resources, passed desktop 1180×820, iPad-sized portrait 820×1180 and phone 390×844. Three books, 10/32/23 contents, 10/30/23 art, visible source-derived previous/next controls, horizontal transitions and Back, old library route, all three direct book openings, compact contents/illustrations, readable footer and no new JS exceptions were checked. Detailed local JSON/screenshot proof resides outside Git with the private candidate; these are browser-source witnesses, **not** a terminal stage receipt, physical iPad Safari/VoiceOver, or HTTPS WebAudio release acceptance.

## Stage effect boundary

The current release is protected by a version-specific source-lock gate. A direct copy into its active root would be refused; replacing v215 with the public-production build would also wrongly change private source states and destroy stage-specific material. The release procedure must preserve v215 as a complete immutable rollback, admit the v216 file-inventory and source lock through the existing guarded owner-WLAN process, then restart the *same* user-level service under the new gate and verify its actual `current` symlink and rendered pages. Public production must not be touched.

**Not yet established by source tests:** exact native EstatePublisher release receipt for a live v216 stage activation, active on-WLAN HTTPS browser/physical iPad VoiceOver, and separate public authorization. Never call a candidate or Git merge a live stage release. A direct public site link remains an independently released predecessor.
