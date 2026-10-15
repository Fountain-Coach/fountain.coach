# Publisher-circle navigation — structural Bookshelf V3

This is a correction to structural Bookshelf V2, not a new publication.

**Semantic invariant:** The circular publisher position is the root/parent
landmark. On the root Bookshelf it is inert. In an admitted collection, the
same circle is the **only parent return action**. There is no separate top
arrow, toolbar, competing home link, back label or replacement logo.

The collection's semantic h1 remains available to assistive technologies,
but not rendered as a second visual navigation system. Circle activation
uses its existing grid position and shape. Hover, press and keyboard focus
produce restrained visible affordances only when the circle is interactive.
Keyboard Enter and pointer activation both navigate to the parent route.

We have not attached any content images, titles, Scores, text or iconography
to the circle or to an occupied cover. The exact same anonymous cover is
used for every admitted collection or work. The original three identical
blank reader leaves are untouched.

This tests containment/parent semantics **as behavior** rather than
manufacturing a visible content identifier. It cannot, alone, tell a human
which otherwise indistinguishable collection is Essays versus First Readings.

## Reusable renderer

Fountain Press `render_bookshelf` gains
`parent_navigation="publisher-circle"`, explicitly selected only in this
fixture. The original `parent_navigation="masthead"` mode remains the
default, keeping the published V38 and source-oriented Bookshelf unchanged.
The parent path comes from the admitted collection model.

## Definition of done

- The collection has exactly one circle parent link and no separate top arrow.
- The root circle is not a link, even for keyboard navigation.
- Circle parent activation works with pointer, focus and Enter.
- The same link works in both admitted collections.
- Same grid, spacing, shape, unmarked surfaces and blank reader.
- Source-hash provenance, deep links, and parent-specific return preserved.
- Existing V38 reading and essay content remain byte-for-byte unchanged.
- No public deployment. iPad Safari editorial perception remains open.

The browser witnesses in this directory cover iPad portrait, landscape and
phone portrait against WLAN staging. `release-receipt.json` records the
release and test gates.

## Live candidate evidence

The active Ubuntu WLAN release is `20261015-publisher-circle-navigation-v3`.
Its iPad/phone browser acceptance passed pointer and keyboard parent returns,
no external top arrow, inert root circle, and the V38 regressions.
`release-receipt.json` records the pinned two-repository release pair.
Human iPad Safari judgement is intentionally not marked accepted.
