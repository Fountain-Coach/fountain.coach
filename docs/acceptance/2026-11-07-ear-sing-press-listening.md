# The Ear That Learns — Fountain Press listening restoration

Scope: Restore the author-approved public Ear/Sing synthetic listening exhibit inside the existing paginated Fountain Press reader. Do not reinstate the obsolete site shell or publish private vocal recordings.

## Source and manifestation

- Editorial source: publicly published Ear/Sing essay (25 October 2026), release public-original-synthetic-v1, original source identity sing.synthetic.sustained-la-mi-na.v1.
- The three public derivatives are already under /essays/the-ear-that-learns/media/ in plain, articulated, and expressive AAC versions.
- SHA-256 of all three existing public derivatives was compared with the author-approved essay manifest before embedding.
- Original prose and rehearsal illustration stay unchanged in Fountain Press. Only flattened exhibit blocks p6..p20 become an active page-native player/annotation figure. No second reader or edition.
- A compact source-time annotation with optional writing disclosure keeps the exhibit within the measured iPad page.

## Release and checks

- Start from the already active Hetzner Caddy static release, not a stale development copy, and run restore_ear_listening.py with the pinned original public essay manifest.
- Deliver through the established EstatePublisher SSH static release to Caddy immutable release tree, atomically activate current symlink, preserve rollback. No Caddyfile edit, new host, runtime build or private media.
- Minimal source correction: allow existing absolute same-root Caddy symlinks in publisher preflight and predecessor checks.
- WebKit checked at 768x1024 and 1024x768: Press reader READY, Ear exhibit visible and within folio. Switching among original takes verified.
- Require terminal typed production receipt plus independent public HTTPS digests.
