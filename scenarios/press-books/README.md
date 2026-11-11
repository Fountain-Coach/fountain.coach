# Fountain Press direct book publishing

This directory contains the **source-bound book URL and social-card composer** for the existing Linotype Reader. It extends a production-derived Bookshelf. It does not create a second Reader, remove source chapters, override rights, or publish an unapproved book.

## Required inputs

The current Git-owned `book-policy.json` defines each book's stable ID, title, description, existing collection order, rights review state, exact source HTML/JS/CSS SHA-256, current source-owner revision, and already accepted public/private predecessors. The compiler reads the actual `reader-gallery-data` source in `estate/index.html` to locate each book's **first admitted illustrated chapter**. No static hero illustration list is maintained separately; an illustrated first chapter can change only through the admitted source's order and the corresponding policy/source SHA update. An unillustrated proem does not trigger an invented cover.

Input `--source` must be an already-composed, complete Fountain Press static root for the chosen version, such as the production-derived Orange Dot candidate in the acceptance record. Output `--output` must not exist; it becomes a small **overlay of only added/changed files** and a reproducible build receipt. Source files are immutable and original chapter art stays at its authored paragraph/source position.

The output contains:
- `estate/books/<book-id>/index.html`, the existing Reader opened on that book's complete contents, with static per-book canonical link, OpenGraph and Twitter metadata, and a Schema.org `Book` JSON-LD object.
- `estate/assets/social/books/<book-id>-first-chapter.jpg`, 1200 × 630 JPEG derived with aspect-safe **contain** from the first admitted illustrated chapter's actual original artwork.
- `estate/books/catalog.json`, the read-only machine-visible matching record of book canonical URLs, first illustrated chapter identity, source figure SHA-256, preview image SHA-256, alt and declared staging/private state.
- Source-corrected Bookshelf HTML, an immutable digest-named Reader app containing a small accessible “Direct book link” under each collection header, and the existing Reader stylesheet with minimal link styling.

The **base source worktree and acceptance prototype** at 11 November 2026 is `Fountain-Coach/fountain.coach` commit `5227c32`. The composer is policy-driven and was independently run against this production-derived root to reproduce **all ten v195 staged files byte-for-byte**, including its three source-art social image SHAs and machine catalog. A later Book or art/source version must update the source policy to the actual new Git/content digests and be admitted as a new immutable release.

## Development execution and tests

From the source repository:

```sh
python3 scenarios/press-books/compose_direct_books.py --source /path/to/exact/accepted/Press-root --output /new/overlay/directory
python3 scenarios/press-books/test_source_drift.py --source /path/to/exact/accepted/Press-root --scratch /path/to/scratch-volume
python3 scenarios/press-books/verify_http_semantics.py --base http://192.168.8.50:8200
python3 scenarios/press-books/verify_http_semantics.py --base https://192.168.8.50:8243
DIRECT_BOOKS_BASE=http://192.168.8.50:8200 DIRECT_BOOKS_LOCAL=/path/to/full/merged/preview node scenarios/press-books/verify_direct_books.mjs
```

The negative tests **must refuse** both unauthorized source-index drift and an altered first chapter image. The browser check must open every book URL and its actual Reader chapter on iPad portrait, iPad landscape and phone, verify Bookshelf direct links and original HTML metadata, and prove social asset digests and catalogue parity. HTTP/HTTPS tests do not require JavaScript. `TMPDIR` should point at an ample scratch volume when testing on the current Mac; it does not modify user files.

## Stage and publication

The accepted **private** release is `shared-shell-20261111-v195-direct-books-social-5227c32`, with v194b rollback. The source-locked stage admit script `prepare_stage_v195.py` and atomic activation/rollback script `activate_stage_v195.py` are **historic version-pinned examples**, not generic future version builders; use the currently admitted EstatePublisher workflow on subsequent revisions. Do not deploy by copying these scripts over a changed predecessor or deleting source-locked publication files.

The private live paths are `http://192.168.8.50:8200/estate/books/essays/`, `/first-readings/`, and `/orange-dot/`. The **canonical public** URLs are `https://fountain.coach/estate/books/<id>/`, but they are **not published yet**. Source `Orange Dot` rights remain a private/author-controlled gate, so neither the public URLs nor preview images may be promoted without an independently approved source-owner release.

A Skill can select and execute this checked-in compiler/verification on a publishing change, but does not itself run a background watcher. The canonical FCIS Linotype procedural source change is tracked separately in `Fountain-Coach/.github` pull request #71 and remains subject to protected merge and provider marketplace synchronization.
