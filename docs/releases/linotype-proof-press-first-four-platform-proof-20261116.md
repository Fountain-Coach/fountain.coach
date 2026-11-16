# Proof Press — first actual four-platform folio witness

**16 November 2026.** This is a *scoped* real Reader proof of the previously published *What Makes a Page Modern?*, **not** proof of the entire Fountain Press estate and **not** editorial quality acceptance. The source is the existing canonical private WLAN v216 Linotype Reader, `shared-shell-20261116-v216-catalogue-bookshelf`, whose prior stage v215 remains retained. It did not publish, modify or recompose anything.

The read-only `scenarios/press-books/proof-press/run.mjs` enumerated the work's **actual composed sheets** and captured one lossless PNG, source-addressed geometry and SHA-256 per physical folio. The independent canonical FCIS `linotype-proof-press/scripts/audit_proof.py` checked inventory and source fragment continuity.

| WebKit profile | Rendered folios visited | Errors | Editorial-review candidate |
| --- | ---: | ---: | --- |
| iPad-size portrait, 820×1180 | 16/16 | 0 | Folio 7: heading at page foot |
| iPad-size landscape, 1180×820 | 28/28 | 0 | None from this rule |
| Desktop, 1440×900 | 23/23 | 0 | None from this rule |
| Phone, 390×844 | 35/35 | 0 | Folios 4 and 34: heading at page foot |
| **Total** | **102/102** | **0** | **Three review locations** |

**Source continuity:** 472 source-character ranges verified continuously across the four compositions, 20 single un-ranged textual source nodes verified by matching source text length, and 48 figure/source identities remained without character-offset coverage. Those 48 require appropriate figure/artwork/ink and editorial verification; the tool does **not** label them character-perfect. No source-gap, overflow, missing screenshot, page or blocking geometry finding was reported in the audited model work.

**Evidence retained privately:** the author's proof volume contains 102 page PNGs, append-only `pages.jsonl`, machine `run.json`, independent `audit.json` and an HTML contact sheet. Public Git contains only the following non-sensitive content digests so that proof can be independently located and reconciled without exposing private source captures:

- `run.json` SHA-256: `850d2d51babbdbc7a4c7bda0376a12c008722c26c7cb4512e9ba273684ae3ff6`
- `audit.json` SHA-256: `d985bac3d14a03e6f3f0e5b4308e494277918eafd6a09f5957b973b82c2a019d`
- `pages.jsonl` SHA-256: `f17ab432b527e0eea1f42d70cab91b2d8cccbc49774f6955f8f5acfb1e690ae1`

**Interpretation:** the three headings are precisely measured candidates for traditional page-setting correction, not an automatic license to insert generic padding or rewrite the authored text. Their adjacent prose, original figure placement, source interval and line breaks require real editorial review. A rule that merely increases page occupancy would contradict the essay's account of whitespace.

**Next bounded action:** inspect the three implicated *current* leaves with the author, correct necessary compositor break decisions while retaining source and illustration identity, re-run the exact affected work × platform matrix, then run the complete 65-work × supported-platform proof as a separate acceptance operation. The latter cannot be declared complete by this model specimen or by synthetic 1,001-page tests. Physical iPad Safari/VoiceOver, font/ink perception and secure HTTPS listening remain independently unverified. No public release authorization follows from this record.
