# Fountain Press: Hetzner staging candidate — 20 November 2026

## Writer outcome

Provide https://staging.fountain.coach/estate/ as a fast, separately controlled editorial staging hostname for the **existing** Fountain Press Bookshelf and Linotype Reader. Preserve production and stage the latest **proposed** essay, *Before We Can Work Together*, from its source-owned repository.

This is evidence of a **prepared local candidate**, not a staging deployment. The manuscript remains **status: proposed**; no production authorization is implied.

## Source and provenance

- Source owner: Fountain-Coach/fountain.coach.
- Exact authored source revision: 8114436dac6c45b28f78d199c5f9c80e73c4778e.
- Manuscript: site/essays/before-we-can-work-together/source.md.
- Manuscript SHA-256: c7457cd839e830e88793f7d61d9dfdd393a0c1334a22fe35150fba104511ea86.
- Three source-owned original SVG figures, retained byte-for-byte.
- Source-art-derived 1200x630 JPEG SHA-256: 64928d5424e82a51fd1c6e4cee67123d8fe44b950abde43da918842b7331fe65.
- Observed full public predecessor: fountain-press-v223b-navigation-css-20261118-ba364ad8 under the authorized /srv/fountain-static-publications/fountain.coach/current symlink on 65.109.14.71.
- Prepared private candidate ID: fountain-press-stage-20261120-8114436-r2.
- No remote site, DNS, Caddyfile or production release was altered.

## Reproduction and acceptance

Use scenarios/press-books/compose_proposed_essay_preview.py with the verified full predecessor, Git-authored manuscript/figures, pinned source SHA40, and new unique output/receipt paths. The compiler checks the public predecessor, preserves the original source-addressed Reader, projects the new proposed essay into Bookshelf, direct books and catalogue, retains original prose/art/media, and writes private noindex metadata. Before it emits its candidate receipt it checks all staging collection routes using the existing publication_closure.py with the exact predecessor and expected-work.

Baseline public closure PASS: 11 Essays, 32 First Readings, 23 Orange Dot.
Candidate r2 private staging closure PASS: 12 Essays, 32 First Readings, 23 Orange Dot.
Original Reader app and Press engine remain content-addressed and unchanged.
All three new SVGs compared byte-for-byte against Git.
Tests PASS: 9 closure tests, 10 frontend tests, 3 new source-compiler tests; wrong source revision refuses output.
Chrome real-browser localhost tests PASS for desktop 1440x900, simulated iPad portrait 820x1180 and phone 390x844: zero JavaScript exceptions, newly listed essay readable with Abstract and all three source figures, no horizontal overflow.
Candidate v1 failed the browser private-stage guard despite passing closure; v2 fixes the existing state semantics. Do not use v1.

Physical iPad Safari / VoiceOver, remote HTTPS readback, native EstatePublisher receipt and actual staging activation remain **UNVERIFIED**.

## Exact remaining blockers

**DNS now independently resolves**: after the earlier empty answer, all three Hetzner authoritative nameservers and the local resolver return staging.fountain.coach A = 65.109.14.71; a nonexistent probe name returns no A. No DNS write was performed by this session. Installed hcloud v1.70.1 is authenticated to context fountainai, whose zone list is empty: **PROJECT_SCOPE_UNVERIFIED** remains relevant only to future DNS management, not to the present existing A record. Do not create a duplicate zone or introduce credentials.

**CADDY/TLS STAGING ADMISSION MISSING**: existing server 65.109.14.71 has no staging.fountain.coach site in the live Caddyfile and no /srv/fountain-static-publications/staging.fountain.coach root. The HTTPS request fails at the TLS handshake with an internal error. A resolving DNS name is not a working staging site.

**PUBLISHER PREFLIGHT BINDING NOT ESTABLISHED**: the existing previously built EstatePublisher SSH transport provides inspect, prepare, preflight and deliver, but its exact-artifact mandatory Fountain Press publication-closure binding is not verified. A separate passing Python validator is insufficient. Do not activate via manual SSH/Caddy/symlink mutation or a parallel publisher.

When the native publisher's exact-artifact closure is genuinely bound, admit the dedicated staging Caddy hostname/root through its authorized route mechanism, use the authenticated EstatePublisher staging profile to issue immutable prepare/preflight/deliver/activation, retain rollback, then independently verify HTTPS metadata, routes, original Reader startup and representative media. A separate decision is required for production.
