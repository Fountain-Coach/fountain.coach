# Structural Bookshelf Ablation V2 — no content markers

**Status:** Experimental, unpublished, identity-perception unverified.

## Correction to V1

V1 was not a semantic test. It treated Score images and original artwork as
recognition cues, then declared success when the artwork and navigation worked.
That conflated authorship content with publication identity. V1 is rejected
as a semantic demonstration; its evidence remains only as audit history.

V2 removes all rendered source artwork and logos, visible text, headings,
cover-name captions, badges, bespoke colors, scores and content-dependent
layout. Occupied cells are visually identical. Empty cells are equally
generic but remain inert. The circular publisher-position cell is unmarked.

Every source-admitted work opens a geometrically identical three-leaf blank
reader, irrespective of how many paragraphs or images the original contains.
Leaves do not claim to represent the original work. They are identical test
surfaces for back/forward/parent/hierarchy/page operations. Reader navigation
icons are controls, not identity signals.

## What remains

The Fountain Press renderer constructs the grid itself (not a new frontend).
The *hidden* semantic model retains identity, parent collection, stable work
source SHA-256, admitted destination, ordered membership, and returning to
the source parent. Work membership is legitimately shared between Essays
and First Readings; the two contexts do not overwrite one another. Accessible
labels remain so this test doesn't gratuitously break assistive use.

In particular there are **zero img tags in the fixture**. The builder never
receives cover images, Score references, alt text of plates, image counts or
artistically interpreted material. Its only display rule is a uniform neutral
cover and three content-independent blank pages.

## Experimental question

With the identity signals removed, can the Bookshelf *itself* communicate
publication, collection, work, containment and reading? Is it possible to
navigate it as a publication architecture rather than a gallery?

This is **not answered by a passing browser test**. The software can prove
that two structurally identical tiles lead to different canonical collections,
but it cannot prove users can recognize which collection is which. That
perceptual distinction is the actual evaluation.

## Reproduce

`npm run fixture:build` builds this *separate* source-owned fixture and
reconstructs the publisher's source inventory.

`npm run fixture:check` verifies work identities, source fingerprints,
parent relations and absence of any visible content assets.

`npm run fixture:browser` verifies iPad/phone navigation, Back, pages, touch
and keyboard, unknown address refusal, zero cover content and hidden
collection labels.

Route: `/fixtures/semantic-visual-bookshelf/`

This route is a disposable WLAN preview, never a published edition. Source
essays, original artwork, existing V38 routes and public estate remain intact.
Native iPad Safari visual review and semantic interpretation are pending.
