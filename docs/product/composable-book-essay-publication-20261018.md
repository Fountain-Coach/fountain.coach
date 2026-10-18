# The Composable Book — product essay source and publication gate

18 October 2026 · **Published** after the source-candidate phase. The original candidate notes below are historical evidence; the authoritative terminal receipt is `docs/product/receipts/composable-book-production-20261018.json` and the live route is `https://fountain.coach/essays/the-composable-book/`. Source commit `b2d8c28`, immutable release `static-composable-44fc5d4e8c4bc6`; exact SHA-256 public witnesses cover all eight changed files plus five existing sibling routes. A subsequent read-only run returned `ALREADY_PUBLISHED_HTTPS_VERIFIED` with no host mutation. This Chapter 158 static release used verified SSH transport and preserved the 17 October predecessor.

## Source authority and authorship

- Git owner: `Fountain-Coach/fountain.coach`, branch `feature/composable-book-product-essay`. Source text: `content/product-essays/the-composable-book.md`; deterministic generator: `scripts/build_product_essay.py`; final HTML route: `site/essays/the-composable-book/index.html`, gallery: `site/essays/index.html`. The four SVG plates are directly source-owned, text-addressable and have descriptive labels; `assets/cover.png` is their derived public preview card.
- **Product essay**, not fourth entry in the earlier three independently authored Essays/Linotype sub-editions. No `site/essays/<original-three-slugs>/*`, existing source-authored paragraph or five original figure files were changed.
- The essay distinguishes **verified** Mac R26/R28 book-spread functionality and stage/portal code from **unverified** cross-platform parity, arbitrary runtime-authored DSL support and Composer-driven DOM component creation.
- The public essay uses public governance chapters rather than private source-code URLs because those GitHub paths returned anonymous HTTP 404 in our audit. Implementation provenance remains here, not falsely available public links:
  - Native R28 `midi2-gpu-fabric` commit `7219b08`, branch `feature/reframe-codex-native-facing-spread`.
  - R27 mediation `0ba30e3` and cross-DSL scenario refactor `7cf8788`, pinned DSL decision `e59190b`.
  - Teatro Stage Web on `midi2-gpu-fabric` branch `codex/teatro-r12-moving-puppet-fallback-20261014`, `apps/teatro-stage-web` (React 18 / Vite 5 / Csound 7 beta / Three).
  - Domain Reasoning Portal from private `Fountain-Coach/domain-reasoning`, `portal/` (React 19 / Vite 7 / structured DOM document).
- Public, independently reachable commentary sources are Chapters 58, 83, 93, 108, 115, 122, 124, 151 at `https://governance.fountain.coach/chapters/...`; the original source essays; First Reading; Teatro; MDN; react.dev; vite.dev.

## Editorial projection and independently witnessed local QA

The Markdown source is parsed by a deterministic stdlib Python script. Four original technical SVG plates explain (1) the continuous codex, (2) open intention → typed relation → composed DOM/audio projection, (3) one book across Mac, iPad, Linux GUI and headless, and (4) FountainStore semantic revision separate from DOM projection. The site is editorially measured in cream/ink/monospaced captions and restrained Georgia typography, not a promotional card layout.

Required clean rebuild:

```sh
npm run product:build
npm run product:check
npm run check
```

For real responsive browser acceptance on the Mac:

```sh
python3 -m http.server 8207 --bind 127.0.0.1 --directory site
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --remote-debugging-port=9347 --user-data-dir=/tmp/composable-book-devtools-profile about:blank
npm run product:browser
```

Set `ESSAY_BASE_URL`, `CHROME_DEBUG_URL`, or `ESSAY_PROOF_DIR` to override defaults. These processes are local test harnesses, **not** an admitted publisher. Witnesses reside on the Mac at `/tmp/composable-book-qa/{desktop,ipad-portrait,ipad-landscape,phone,book-plate}.png` and were visually inspected. Explicit DevTools device-metric overrides proved zero horizontal overflow at 1440×980, 820×1180, 1180×820, and 390×844. Every in-page anchor resolves; 8 independent section identities, all four SVG illustrations, one semantic heading, and SVG decode passed. The desktop plate stays clear of the contents rail. A static-source check confirms the new essay is 42 content paragraphs and the original three-essay edition retains **77 untouched authorial paragraphs and five original plates**. `publication-files.sha256` and `edition.json` capture all site files and their digests.

Public link audit (anonymous `curl -L`): normal governance chapters, MDN, React, Vite, Teatro, First Reading, `fountain.coach/` and the original essays returned HTTP 200. Private GitHub source URLs returned 404 and were omitted from HTML in favor of public governance and this local provenance record. Candidate route `https://fountain.coach/essays/the-composable-book/` returns **404** until separately published; similarly the source-owner `/editions/` proposal was not assumed publicly live and is not linked from the product essay.

## Required separate publication transaction

The real native `EstatePublisher` is available at `/Volumes/DockerDisk/Development/solstice-caddy-20261012/apps/estate-publisher/.build/arm64-apple-macosx/debug/EstatePublisher`. Its `--help` enumerates `--preflight`, `--prepare-publication`, `--publish`, and Golden Key session operations. **The CLI is not an authorization**. Chapter [134 — EstatePublisher Is the Publication Authority](https://governance.fountain.coach/chapters/134-estatepublisher-publication-authority/) requires:

1. Reviewed, pinned Git source and complete native direct-static route projection for **exact host** `fountain.coach` and **path prefix** `/product/` only; the three existing editorial fronts and historical essay sources are excluded.
2. Contract-coherent local preflight, explicit FountainStore admission and inspected semantic diff; no unreviewed direct Caddy/SSH/rsync publication.
3. Source-revision-bound, expiring scoped approval through SecretStore and Golden Key session.
4. Native `estate.publication.sync` terminal receipt, authenticated remote FountainStore selected-path manifest and bytes readback, and independent public HTTPS digest/canonical/asset verification.
5. Only after (4): update publication state to `published`, record exact published revision/receipt and public link; until then source remains `source-candidate`.

If any requirement is missing, record **BLOCKED — publication proof incomplete**. Do not use `FountainStoreEstatePublisher` as a workaround; it only updates a local publication manifest. No alternate upload or raw host mutation.

## Claim boundary

This product essay is a completed **locally checked editorial candidate**. It does not claim the Linux graphical client, iPad Composer, user-authored arbitrary DSL execution or DOM-authoring instrument is implemented. It also does not claim that this essay was published to the public domain. A reviewer should evaluate typography and argument independently of test status before authorizing production publication.

## Chapter 158 static-publication reconciliation (18 October)

The user explicitly requested direct SSH publication to the existing Hetzner Caddy origin. Governance Chapter 158 supersedes Chapter 146's transport prohibition *for immutable static releases only*: vetted source, exact host/route scope, verified SSH host identity, immutable successor under `/srv/fountain-static-publications/fountain.coach/releases/`, atomic `current` symlink, Caddy validation/reload if needed, rollback, independent public SHA-256 witnesses. The earlier instructions above describe the Store-to-Store route and are not required dependencies for this static route. The existing production route was observed with a verified `root@65.109.14.71` SSH connection; this is a historical recovery identity and does not yet satisfy Chapter 158's least-privilege follow-up hardening.

The production `/essays/` index had a newer published `To Read Is Not to Remember` entry, absent from the 14 October owner snapshot. We imported that exact deployed index digest `13fdce014422b18ef5f98ae18070f437dfd90b1bef8a8b159e6569413e322aad` *only for the collection index*, preserving all four established public cards, before adding one new product card. The prior route content remains in the predecessor release. The new release must preserve the previous Caddy matcher's `/essays/to-read-is-not-to-remember/*` routes and the previous release in full. Only `/essays/index.html`, `/essays/the-composable-book/`, and its own assets are intended to change.

## Terminal estate integration receipt — 18 October 2026

The first `static-composable-44fc5d4e8c4bc6` release made the article publicly reachable but failed editorial integration: the essay used a standalone masthead and footer, and the actual live Fountain Coach homepage had no direct article entry. This was corrected in owning source commit `5270f04f96fdadfb6d70baf326a709b3dee724fd`.

The immutable successor `static-composable-90e7bbe2da6fd7` is **PUBLISHED_HTTPS_VERIFIED**. Its independent readback returned public HTTP 200 with exact bytes for `/` (SHA-256 `deee2ab39eac56511989f624911e3274db1aba657c197ce235f82a3353b13ca9`), `/essays/` (unchanged `30bf86c2c53e299cf60fe76410fd2fbd2c3257a08e10769c6fa2ef51ba6bfcbb`), and `/essays/the-composable-book/` (`e69e87294edb6f2faf7b86279af8c7951e75c7a458c79d540a3faa689f8eec54`). The four SVG plates, cover image and CSS retained their accepted source digests. The same exact-byte receipt proves the older essays unchanged. The article now derives its domain header, estate icon rail, breadcrumbs and legal footer from the current source-owned essay collection, not a custom shell. The *published homepage* includes a direct `The Composable Book` entry within its existing publication-card geometry.

**Important independent future work:** The intentionally separate `site/index.html` is a future Bookshelf candidate, not the deployed home portal. It was neither overwritten nor silently promoted by the targeted integration. The release-only homepage projection is deterministic and built from its source-pinned live predecessor, preserving its entire prior body outside the single article entry. Source index pages and all original authorial essays remain governed by their existing boundaries. The new publication/rollback acceptance suite passed 13/13 local tests. A repeat `npm run essays:prepare` returned `ALREADY_PUBLISHED_HTTPS_VERIFIED` with `noHostMutation=true`.

The authoritative terminal release receipt is `docs/product/receipts/composable-book-estate-integration-20261018.json`; the earlier `composable-book-production-20261018.json` remains the preserved first-release receipt. Public presentation is verified, but this does not certify the future Bookshelf source or cross-platform GUI support.
