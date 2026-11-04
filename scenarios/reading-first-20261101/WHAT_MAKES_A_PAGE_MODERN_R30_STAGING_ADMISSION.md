# R30 — What Makes a Page Modern? / Original Reader source admission

Scope: insert an approved essay into the accepted production-derived v140 Fountain Press Reader. No second reader, no extra compositor, no public release, no fake audio or physical MIDI transport.

Chapters read: 07 — plan the bounded owner change; 08 — independently verify the actual Reader; 29 — measured geometry is not meaning; 42 — reuse existing source and Reader; 50 — source position/identity must survive reflow. Organization FCIS and Fountain-Coach/estate/AGENTS.md apply.

Forbidden: stand-alone app shell; copying the older book.js renderer; silent changes to existing Reader runtime, audio, stage-only deltas or manuscript paragraphs; treating successful pagination as Store admission or production rights.

Conflicts: public HTTPS Reader main differs from accepted v140 WLAN staging; preserve three documented stage-only JS differences. V140 source at 81317b77b1e28d6e8b8e15d99c83f321e2e180aa is byte-identical to accepted staging estate/index.html (SHA-256 69e656346b219be35c030e437100e72338f54d3a70abecbe6030971773cb1c01). The comparison applies to the affected Reader and its deployed dependencies, not a new production route.

Excluded: PDF export, optical proof scanning, Store E01 admission, native iPad AX, paid providers, public release. Stage only by existing authenticated SSH and immutable symlink with preflight and rollback.

## Original manuscript

The authoritative source is the 13-page illustrated A4 PDF What Makes a Page Modern? — Four Settings, One Text. SHA-256: 2baaab0012e825b49f04e7a760b64efa52c95dc09deab7117de790f6c6e14bad.

All 27 main prose paragraphs have been checked against the original PDF and match the source text in the publication source branch. Six bilingual working principles are likewise preserved. The three repeated typographic specimens contain one identical 444-character passage (SHA-256 655e4477fdc0eeec16813e7573990c5cfd83e010f343b074d46ea36460a54724). Each occurrence has a distinct source block for compositor integrity but shares one canonical semantic unit ID. See site/essays/what-makes-a-page-modern/source-receipt.json for the per-paragraph digest record.

The 13 source-owned SVG diagrams are adapted editorial plates, not claimed to be byte-identical PDF images. The editorial proem and distribution colophon are clearly separate authored additions. No Read Aloud or actual MIDI2 performance is invented.

## Concrete delta

Reuse the SAME existing Reader and frame:
- Add one data-reader-volume template inside existing scenarios/reading-first-20261101/index.html; keep every existing volume unchanged.
- Adjust the existing reading-first-app.js collection membership check from five to six Essays; do not change engine, shell, CSS, media or transport.
- Add the new gallery entry in existing source data and the source-owned SVG illustrations.
- Stage candidate shall be v140 exact predecessor plus these declared files only, preserving stage-only Reader/audio differences.
- Reader provenance guard must be updated by a source-owned, exact SHA-approved admission for this single candidate. Never disable it.

## Evidence and status

Actual existing v140 Reader, via Playwright interception of source changes without changing staging:
Chrome 1200x860, 820x1120, 390x844: PASS.
WebKit 1200x860, 820x1120, 390x844: PASS.
The Reader itself verified source-block and text preservation; measured 22/13/21 leaves, 0 page errors, 0 viewport overflow; 6 gallery Essays; original Teatro book still opens; parent navigation returns to Essays. This is browser source evidence, not physical iPad or FountainStore acceptance.

Staging not yet active at time of this source record. Final SSH receipt must establish production scope, exact Git SHA, v140 predecessor, candidate routes/assets and guarded HTTP readback. No public deployment.

## Golden single-page reference — writer's editorial direction, 4 November 2026

For this essay and all subsequent Fountain Press layouts, **iPad portrait is the golden visual reference for one complete Linotype leaf**, not a mathematical golden-ratio rectangle. Its *Satzspiegel*, margins (*Stege*), leading (*Durchschuss*), line measure/fall, principal and secondary illustrations, unoccupied space, discreet folio closure and touch navigation establish the editorial quality bar. **One page is the unit of composition; landscape is a two-page relationship**, not two compressed website columns. Desktop and phone adapt the same source identity without assuming the portrait page has fixed pixels or the same folio count. An A4 Druckfahne is a separately composed printer's proof with intentional blank correction space.

The actual staging v142 edition has passed Chrome and WebKit at desktop, tablet portrait-sized and narrow-phone viewports (six live WLAN browser checks, 22 / 13 / 21 leaves with preserved source integrity, no horizontal overflow, correct Essays return and six-work gallery). This **does not yet establish physical iPad Safari golden-page acceptance**, which remains a distinct required witness for editorial layout admission. Any following layout changes should compare against the actual iPad portrait reference first. Binding source: Fountain Press `README.md` and `AGENTS.md`, golden-page reference of 4 November 2026. No new reader or publication route is authorized by this note.

## Editorial correction — 4 November 2026 · balanced figure measure

The writer identified a left-hand alignment break at the actual portrait Reader and inconsistent internal padding in the rectangular illustrations. The accepted v142 WebKit portrait measurement showed the body column at x=98 CSS px, opening figure/image at x=103 and its independently centred caption at x≈220.7; this was a real, observable defect.

**Adopted in this essay's owning source, without a new reader:**
1. The rendered image, illustration figure and caption share the **same left edge** as the actual measured paragraph's Satzspiegel; measured tolerance ≤1.3 CSS px. The compositor's existing safety width (up to 10 px less than the text measure) is preserved, not overwritten by styling a false full-bleed width.
2. Secondary vector diagrams follow the text flow with one measured figure interval (0.72em before, 0.88em after), and left-anchored captions. Figure placement and page breaks stay under the existing Press compositor, not a new author-defined pagination service.
3. Each unframed source-owned diagram has its own ink-based viewBox and a **36 SVG-unit optical inset on all four sides**. For *Satzspiegel* and *returned sheet*, the outer visible rule is aligned with the measured Satzspiegel itself (only 1 SVG unit stroke allowance), while its inner content retains balanced semantic padding; it must not embed another running header, page footer, external pseudo-sheet frame or centred caption. The *question/Satzspiegel* and *Joyce/returned sheet* rectangular diagrams have explicitly balanced internal boundaries and inset labels (approximately 60–74 SVG units within their semantic rectangle). Open margins remain genuinely open where they are the meaning of the diagram.
4. Original source prose, bilingual vocabulary, specimen source unit IDs and the authoritative PDF digest are unchanged. The SVGs are explicitly **adapted editorial plates**, not a claim to reproduce the PDF image bytes.

**Actual Reader regression:** the original v140 Press compositor measured these corrections on a local source overlay at WebKit and Chrome 820×1120, 1200×860, 390×844: 6/6 passes, all 12 rendered figures and captions aligned to their own page text area within ≤1.3 CSS px, no horizontal overflow; source integrity preserved. Page counts may legitimately change through reflow. Physical iPad portrait Safari remains the editorial golden witness and is not yet claimed independently accepted by this browser test.

**Staging promotion:** create only a new digest-bound immutable WLAN release using the current accepted v142 as predecessor. Break hard links through atomic replacement before changing any candidate file. Retain v142 and its previously pinned guard admission for rollback. Publish no standalone essay Reader and do not change shared engine/CSS or public production.
