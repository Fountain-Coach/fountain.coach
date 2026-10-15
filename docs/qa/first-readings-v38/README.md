# First Readings — publication identity and real reader journey (V38)

**Date:** 15 October 2026
**Source owner:** Fountain-Coach/fountain.coach
**Fountain Press reusable Bookshelf:** revision ec924588 (unchanged)
**Source implementation:** e6e1bcf and 81ad80e, pushed to main
**WLAN candidate:** 20261015-first-readings-identity-v38 on 192.168.8.249:8180
**Status:** Browser E2E / screenshot candidate, not native iPad Safari author approval or production publication.

## User journey witnessed

Fountain Coach Bookshelf -> First Readings collection -> *Teatro — An Unfinished Composition* cover -> source-authentic essay -> return to parent, including Back history.

One admitted authored work, original SVG cover-artwork projection, 22 original paragraphs, unchanged source and plate. The singular Solstice First Reading remains independent. No manufactured First Hearings publication and no Teatro-as-publication substitution.

## Corrected failures

1. The standalone work no longer shows the 3-essay omnibus `01 / 03` marker. Its chapter label identifies FIRST READINGS and retains the authored theme THE CONDITION.
2. Running titles in all generated leaves (including image/plate and continuation leaves) now say FIRST READINGS. Previously the second page still said ESSAYS while its folio said FIRST READINGS.
3. The inherited Aa appearance button is removed from generated readers, preserving the pinned authorial typography.
4. Legal links occupy a dedicated second row of the iPad/desktop pagination footer instead of overlapping page progress. On phones, the existing page-atlas presentation intentionally hides the traditional pager; that behavior remains unchanged.
5. The original cover SVG appears larger in the work's opening. The collection-cover image itself remains source-authentic and uncropped.
6. Browser screenshot capture now explicitly waits for decoded source artwork. Earlier screenshots made the collection cover appear blank solely because the lazy image had not loaded at capture time.

## Proof

- `npm run book:build`: pass, deterministic source projection.
- `npm run check`: pass, all 77 original authorial paragraphs and five figures; three independent books.
- `npm run book:browser`: pass, desktop, iPad, and phone composition plus bookshelf/edition routes.
- `ESTATE_BASE_URL=http://192.168.8.249:8180 node scripts/verify_first_readings_journey.mjs`: pass for iPad portrait (820x1180), iPad landscape (1180x820), and phone portrait (390x844). This verifies original artwork loads, navigability, title and image continuity, browser Back, reading state, running headers, folios, absent Aa, absence of footer collision, and no horizontal overflow.

The adjacent PNGs are actual Chrome browser captures from those journeys. They are evidence to inspect, not automated proof of authorial visual acceptance or native Safari rendering.

## Publication boundary

Only the disposable, source-pinned WLAN release is active at port 8180. This work did not deploy or mutate the public fountain.coach estate. Native iPad Safari proofreading and publisher approval remain separately required before public promotion.
