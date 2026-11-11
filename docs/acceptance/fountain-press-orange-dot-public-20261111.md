# Fountain Press — Orange Dot public release and root parity

**Status:** independently accepted public production, 11 November 2026 (Berlin). **Host:** https://fountain.coach/ with the unchanged existing Hetzner/Caddy v2.10.2 static site. **Publisher authority:** existing EstatePublisherSSHDelivery authenticated release transport; no new SSH credentials, server helper, DNS service, Caddy config changes, or FountainStore dependency.

## Writer's scope and source authority

The author expressly requested public publication of the staged Orange Dot book and its *containing Fountain Press*. The author-owned source admission in `scenarios/press-books/orange-dot-public-admission-20261111.json` records the precise 23 complete selected writings and 29 original accompanying images from the historical private Facebook export, superseding the earlier private-only release restriction **for this public edition** without silently rewriting the archived decision. It does not assert separately proven third-party licenses or depicted-subject releases. This publication was directed by the author, not granted by private-staging readback.

Public Bookshelf order: **Essays (7), First Readings (32), Orange Dot (23)**. Governance remains independent at governance.fountain.coach; the entire former Works book, Scores and unfinished Medicine Show are excluded. All public predecessor material is preserved except declared source-authorized Reader/metadata changes. The original source-authentic Orange Dot writings, all 29 images and their original paragraph/image placement remain unchanged.

## First exact public release — complete book, direct URLs and first-chapter social images

- **Source Git admission:** [`d71968a730d2e0458a6f67e74370f21c79e34b2f`](https://github.com/Fountain-Coach/fountain.coach/pull/20), merged protected PR #20. Public composer: `scenarios/press-books/compose_orange_dot_public_release.py`.
- **Predecessor:** `fcis-essay-heading-20261110-8f58f29`; native EstatePublisher read-only `inspect` confirmed it before delivery. The static source was the independently accepted private v195 production-derived Press artifact.
- **Release:** `fountain-press-orange-dot-20261111-d71968a`; **483 complete site files**, source inventory SHA-256 `73589835922028b55f4f2a058b6db0e0328545766c919533fee0672b051b6ac4`. Native `prepare`, `preflight`, `deliver` succeeded. Native terminal receipt state `active`, `activated=true` and 7 exact public HTTPS file/image SHA witnesses, including all three direct-book routes, canonical catalogue, Orange Dot edition metadata and Solstice social card.
- **Preservation proof:** the original 445 public predecessor paths were retained. Only the existing `estate/index.html` and link CSS differed prior to the four declared public metadata/alias transformations; 38 files were added. No original source text/illustration/Reader chapter positions were changed.
- **Book URLs:** [Essays](https://fountain.coach/estate/books/essays/), [First Readings](https://fountain.coach/estate/books/first-readings/), [Orange Dot](https://fountain.coach/estate/books/orange-dot/). Each has a visible accessible Bookshelf link, its own crawler-readable Open Graph/Twitter metadata, Schema.org Book with first eligible illustrated chapter and 1200×630 source-image derivative. JSON catalogue: [`/estate/books/catalog.json`](https://fountain.coach/estate/books/catalog.json).

## Found and corrected main-domain entrance drift

An independent post-release production inspection proved that `https://fountain.coach/` still served the two-book predecessor (`index.html` SHA `005ca222f53735a313543809521c525e23552223406f31bf3e590ccde4a13a49`) while the accepted three-book `https://fountain.coach/estate/` had SHA `b8f2e495d7ba2e0b7ad0ca04321c7d5afb6a25633fdeb5dbccd90b8321d0b508`. This violated the author's original *containing Press* publication goal and the existing single Linotype Reader contract.

The bounded source correction `scenarios/press-books/align_public_press_root.py` was merged in [PR #21](https://github.com/Fountain-Coach/fountain.coach/pull/21) at Git SHA `fe71ba5be854495486874a014b18ef55bf8d688d`. It builds the next immutable complete 483-file artifact with **only the root `index.html` replaced by the exact, unchanged accepted `estate/index.html` bytes**. All 482 other files remain byte-identical to the first public Orange Dot release. This reuses the existing Reader rather than adding a new route service or redirect.

- **Current production release:** `fountain-press-orange-dot-root-20261111-fe71ba5`, activated through native EstatePublisher `inspect → prepare → preflight → deliver`.
- **Native terminal receipt:** `active`, `activated=true`; inventory SHA-256 `fb898e1a76b59304468e83bce78897210eb7d8cf98fb3a6063e1d26a1abb0bee`. Eight exact public HTTPS witnesses include `/index.html` and `/estate/index.html`, **both SHA-256 `b8f2e495d7ba2e0b7ad0ca04321c7d5afb6a25633fdeb5dbccd90b8321d0b508`**, plus all three book pages, catalogue, rights-admitted edition JSON, and first-chapter Orange Dot social image.
- **Rollback:** previous `fountain-press-orange-dot-20261111-d71968a` and original public `fcis-essay-heading-20261110-8f58f29` release directories still exist. No Caddyfile/DNS mutation was needed; Caddy validation passed independently.

## Independent public readback

1. **Complete corpus and source-original art:** `public-orange-dot-full-https-witness.json` checks **23/23 original selected full-text SHA identities** against author source files and public edition metadata, fetches and independently hashes **29/29 individual original image URLs via external HTTPS**, and compares those bytes to the source-owned image SHA. All passed, no missing/altered art. External public `estate/index.html` confirms the original 23 ordered Reader templates and absence of excluded Works titles.
2. **Static social/machine metadata:** `verify_http_semantics.py --base https://fountain.coach --public` passed all three canonical direct-book URL HTML responses, exactly one canonical link each, Open Graph/Twitter image URL, 1200×630 dimensions, source image checksum, raster derivative checksum, first illustrated chapter identity, Schema.org Book and public machine catalogue.
3. **Direct-book WebKit acceptance:** `verify_direct_books.mjs` passed all **three public book paths × three viewports** (iPad portrait, landscape, phone), accessible Bookshelf deep links, actual Linotype chapter opening/pagination, static metadata and no page exceptions.
4. **Both public entrances:** `verify_root_parity.mjs` passed **`/` and `/estate/` × all three viewports**, with identical collection contents, direct links and actual first Orange Dot chapter foliation. External public root and estate HTML are byte-identical; independently rechecked after final release.
5. **Neighbor/regression:** existing `verify_public_press_candidate.mjs` passed public iPad portrait, landscape and phone Bookshelf counts, existing Essays and First Readings neighbors, and measured Orange Dot figure spacing. Caddy active symlink and native `inspect` read back the final release identity.

The source-verified original media does **not** imply independent third-party copyright clearance. Physical hardware iPad/Safari/VoiceOver was not driven; Mac WebKit responsive acceptance is the witnessed behavior. External social platform caches are outside this on-site HTTPS proof.

## Terminal proof files

- [First Native EstatePublisher receipt](receipts/orange-dot-public-native-d71968a.json)
- [Final Native EstatePublisher root-parity receipt](receipts/orange-dot-public-root-native-fe71ba5.json)
- [23-text / 29-image public HTTPS source witness](receipts/orange-dot-public-full-https-20261111.json)

The existing canonical FCIS Linotype Estate Skill governs book-level source-image/social/URL regeneration; the root-parity regression is retained in the Fountain Press source repository. Git source merges and receipts are not interchangeable with the native activation and independently witnessed public HTTPS results above.
