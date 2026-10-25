# Illustrated essays: the first illustration is the social preview

**Publication rule · 25 October 2026.** The first authored image in an article is the social preview of its canonical URL. Do not generate a replacement, draw a separate social cover, or let the generic Fountain Coach logo become the preview because metadata is missing.

Every illustrated essay's complete static HTML should expose an absolute HTTPS `og:image` pointing to the same published asset shown by its **first image within `article`** (not the publisher-logo image in the shell). Publish matching `og:image:alt` and correct original dimensions and image MIME type. `twitter:image` must point to that same asset; use `twitter:card=summary_large_image`. Use the actual essay title, canonical URL and description. Governance's chapter pages, including [Chapter 158](https://governance.fountain.coach/chapters/158-publishing-is-not-a-distributed-transaction/), provide existing examples.

For *The Ear That Learns*, the first article illustration is `assets/listening-room.png`. The shared preview is `https://fountain.coach/essays/the-ear-that-learns/assets/listening-room.png`, exactly that original 1536 × 1024 image (SHA-256 `d07e55ebed5b0e9100a86191099b686c8c1802770b292c358d86208911dd269e`). The `scripts/verify_ear_sing_essay.py` source check binds the first illustration, alt, dimensions and both preview URLs together so a later change cannot silently fall back to the logo.

Verify the image and social HTML metadata over public HTTPS with a social-crawler user agent after the exact-host release. Social platform caches may retain older cards until the URL is re-scraped. That caching is separate from the site's published metadata and does not authorize a different image.
