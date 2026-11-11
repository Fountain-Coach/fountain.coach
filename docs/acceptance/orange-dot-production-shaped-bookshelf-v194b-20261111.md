# Orange Dot — production-shaped Fountain Press staging v194b

**Observed 11 November 2026.** Private canonical owner-WLAN proof; no public publication or rights admission.

## Actual production predecessor inspected

Live production `https://fountain.coach/estate/` was read and rendered in WebKit at iPad portrait (820×1180) and landscape (1180×820). The live public Bookshelf currently contains **Essays and First Readings**, without Governance or Works shelves; it opens in a compact paginated Bookshelf layout. Public active release remains `fcis-essay-heading-20261110-8f58f29`; public `estate/index.html` SHA-256 `005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49`.

Canonical private staging v193 was also inspected and rendered. It still opened the historical On Continuity volume with old Scores/Governance book entries, rather than the desired public Bookshelf composition. This explains the writer's objection: removing Governance only from the future public candidate was not enough.

The production-derived Orange Dot candidate, built reproducibly from the public predecessor, displayed **Essays, First Readings, Orange Dot**, retaining exactly 23 original Orange Dot writings and 29 original images. The entire former Works/Scores book and the Governance shelf are excluded. Original essay chapter links to the independent `https://governance.fountain.coach/` publication remain in source; the independent published Governance domain is not modified.

## Canonical WLAN stage acceptance

**Source release decision:** `scenarios/orange-dot/release-exclusions.json`, Git commit `007ca1c`. The production-derived publication composition's HTML digest is `7db826d5aa32da727213ce2d53dc1e1a35efe5ee820c987ae6066e2dd1500f3b`. This is the same exact HTML on the active staged Reader.

**Active stage:** `shared-shell-20261111-v194b-orange-dot-production-bookshelf-kino-007ca1c`; canonical HTTP `http://192.168.8.50:8200/estate/`; canonical owner-WLAN HTTPS `https://192.168.8.50:8243/estate/`. Source-lock SHA-256 `3e815168392fb990c4749a33ba01befea5ea4e2e3777253f52a5c4c5761acb4a`; v194b admission SHA-256 `320f04a5a0a0cf36e6a643d6c7bdca090a03b73fe76657f54590ab0427243299`.

**Predecessor:** immutable v193 `shared-shell-20261111-v193-orange-dot-portrait-spacing-b431528` retained as rollback. That release and the source archives still contain older unpublished volumes, but these are not part of the new Bookshelf.

**Declared stage-only reconciliation:** earlier private staging marked two already-public Kino sound manifests `publicReleaseAuthorized=false`, causing the production Reader to reject their admission. Their original recorded source/media hashes matched the publicly published manifests; exactly the two public manifest projections were copied for the WLAN proof, without altering the media or bypassing Reader validation. The first candidate v194 was never activated; corrected v194b is the accepted release.

**Source and custody:** `scenarios/orange-dot/prepare_production_shaped_stage_v194b.py` builds the immutable derived release from the source-pinned candidate input retained on DockerDisk and the observed v193 predecessor. Nine files were changed/added; twenty-seven candidate assets were already byte-identical in staging; 1,934 unrelated inherited files were preserved. `activate_production_shaped_stage_v194b.py` switches the two existing stage services with automatic rollback on failed HTTP/HTTPS readback. No public host, DNS, public symlink or original archive was mutated.

## Independent readback and browser evidence

- Live HTTP **and** HTTPS HTML 200 and exact SHA-256; production-matched versioned app and compositor JS assets also match their SHA-256.
- Source manifest and Reader gallery: exactly `essays, first-readings, orange-dot`; Orange Dot 23/23 original texts, 29/29 original images, first/last/previous navigation and measured secondary figure spacing pass iPad portrait, iPad landscape and phone.
- Zero Governance, Works or Scores templates, selector options or collections; 18 raw HTML governance-chapter link occurrences remain as scholarly references rather than an erroneously integrated shelf.
- Two public Kino edition manifests have matching source/media identities and public authorization flags; no duplicate audio engine or weakened Reader gate was introduced.
- Original Koken videos were not changed; independent HTTP/HTTPS byte-range tests returned 206 and original `ftyp` signatures for sampled films.
- Public production independently re-checked unchanged at `fcis-essay-heading-20261110-8f58f29`, SHA `005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49`.
- No physical iPad Safari or VoiceOver session is claimed; Mac WebKit's iPad viewport/gesture proof is distinct.

## Outstanding release boundary

Orange Dot's source selection still says private owner-WLAN only. Public dissemination of 23 writings and 29 images requires an explicit source-owned rights/editorial release decision. The native EstatePublisher public production manifest/preflight is prepared separately but has not been delivered; this staging change does not grant production authority.

*Revisiting the Head Boxers Medicine Show* remains a separate private editorial undertaking until its paragraph-addressed interlinks to Orange Dot and First Readings are established.
