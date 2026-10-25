# The Ear That Learns — first illustration as public social preview

**Verified public correction · 25 October 2026.**

## Observed publishing defect

The author showed a Facebook composer displaying the generic Fountain Coach hand/logo instead of the first illustration of `https://fountain.coach/essays/the-ear-that-learns/`. Before this correction, public HTML contained an article title, description and `og:url`, but **no `og:image` or `twitter:image`** and `twitter:card` was `summary`. The generic logo was therefore a fallback social-card candidate. Governance publication pages already demonstrate the applicable Open Graph and Twitter card pattern. This is a **metadata/publishing defect**, not a commission to create new artwork.

## Source-owned correction

- Source: `Fountain-Coach/fountain.coach@124c9fabc310dcf35a8c23bd5018efb3126c4394`.
- The article's first actual illustration remains `assets/listening-room.png`; the exact same image is `og:image`, `og:image:secure_url` and `twitter:image`.
- Absolute public HTTPS preview: `https://fountain.coach/essays/the-ear-that-learns/assets/listening-room.png`.
- Original image identity SHA-256: `d07e55ebed5b0e9100a86191099b686c8c1802770b292c358d86208911dd269e`, `image/png`, 1536 × 1024 pixels. No new or alternate art; the illustration visible in the essay is byte-identical to the social image.
- `og:image:alt` and `twitter:image:alt` match the first illustration's own alt text. `twitter:card` is `summary_large_image`.
- `scripts/verify_ear_sing_essay.py` now binds the first `article` illustration to the social preview, not to the first image in the site shell. The general publication rule is documented in `docs/decisions/2026-10-25-illustrated-essay-social-preview.md`. The full source check passed before publication.

## Production-first bounded immutable release

The existing exact host was `fountain.coach`. The independently observed active predecessor was `estate-20261025-v15-ear-sing-61f264d`. Its **33 files** and affected public HTML and PNG SHA digests were checked before the mutation.

The new release `estate-20261025-v16-ear-sing-social-124c9fa` retained 31 files byte-identically and modified only:

1. `essays/the-ear-that-learns/index.html` — OG/Twitter head metadata only, SHA-256 `c7d6f85a2562e56dffa4b5319a9df218a22154a41c6022a7510dc3d22a097a11`.
2. `release-manifest.json` — the new immutable release identity and complete inventory.

The rest of the essay after `</head>` is **byte-identical**, including prose, chapter navigation, illustration, semantic player and audio. All previous essays, other public pages and assets remain untouched. No Caddy configuration, DNS, additional domain, staging, or production media asset change was required.

Existing exact-host `EstatePublisherSSHDelivery` accepted `prepare` and `preflight`, activated the immutable release, returned **`activated=true`, `state=active`** and checked seven independent HTTPS witness files, including the article and unchanged social image. The previous production release is retained for rollback.

## Independent social-crawler HTTPS witness

A fresh `facebookexternalhit/1.1` user-agent GET of the actual public essay returned the published HTML SHA-256 above, with `og:image` and `twitter:image` both naming the original first illustration, accurate alt, type and dimensions. A separate public GET of the image under the same crawler user agent returned **HTTP 200**, `image/png`, the exact original SHA-256 and 1536 × 1024 dimensions. No `noindex` restriction was present. The body after `</head>` matched the v15 baseline.

**Platform distinction:** This proves what the public site serves to a Facebook-style crawler. It does **not** prove that Facebook has invalidated its previously cached preview for this URL or that the author's already-open composer has refreshed. No logged-in Facebook Sharing Debugger rescrape or app-session screenshot was obtained; do not misrepresent the existing Facebook cache as the new web publication.

## Original records

- [Typed release receipt](2026-10-25-ear-sing-social-v16-public-receipt.json)
- [Exact publisher manifest](2026-10-25-ear-sing-social-v16-public-manifest.json)
- [Full previous-to-current delta](2026-10-25-ear-sing-social-v16-production-delta.json)
- [General source publishing rule](../decisions/2026-10-25-illustrated-essay-social-preview.md)
