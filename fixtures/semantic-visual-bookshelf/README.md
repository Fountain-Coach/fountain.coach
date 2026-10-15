# Spatial Bookshelf V4 — contained meaning without borrowed names

**Experimental, unpublished, not yet human-approved on iPad Safari.**

## Semantics

A space is not a book. It is a containing region with membership and a
destination. Books are distinct objects: only books have rounded-square
occupied cells. Empty places remain non-interactive.

A color belongs to the **currently containing region**, not a title,
genre, document, author, source artwork, Score, or permanent identity.
Color is assigned only by structural sibling position. A book visited
through one region inherits that region's color; the same book opened
through another region carries that different context color while
preserving the identical opaque object token.

The publisher position is a circular structural landmark. At root it
is inert. Inside a region the same circle is the sole reactive way to
return to the containing Bookshelf; no separate arrow is emitted.

### What the fixture contains

- Two anonymous containing regions with distinct colors and physical bounds.
- Three distinct anonymous books; one book is present in both regions.
- Four membership encounters, each with a reversible containing route.
- Every book has three identical blank test leaves, unrelated to source.
- Zero image tags, zero Score-derived cover/identity, zero authored prose,
  no source publication names, and no source file dependency.
- Opaque identifiers (e.g. `s-01` and `o-02`) are transport keys only.
  They contain no editorial meaning and are not shown on the screen.

This is intentionally a **grammar test**. Passing routes and color propagation
does not prove readers know what a particular anonymous book means.

## Spatial grammar and behavior

Root: circular publisher landmark + colored, wide containing fields showing
miniature membership silhouettes. The fields are not book-sized rectangles.
Each area has an assigned hue and depicts only occupancy. Activating a field
enters that space.

Inside: that hue tints the spatial region, circular parent control, and
small markings on its member book cells. Empty places are not books.
Opening a book enters a neutral blank reader and retains the containing
region's hue as a structural edge and progress mark.

The same anonymous object is encountered through both spaces; the object's
token is constant while the parent destination and hue change. Browser
Back, pointer swipes, keyboard navigation, invalid-address refusal, and
return to the containing space remain operational.

## Tests

`npm run fixture:build` regenerates the static projection.
`npm run fixture:check` checks anonymous structure, memberships, provenance
tokens, no source asset strings, no image/text pollution, and color rules.
`npm run fixture:browser` checks the full interaction across iPad portrait,
iPad landscape, and phone portrait.

Reusable renderer: Fountain Press `render_bookshelf(spaces=...)` draws
actual containing regions instead of smuggling space links into the list of
books. Original publication mode and V38 source content are unchanged.

## Editorial question

Does the visible containment structure itself carry enough meaning?
Color now conveys belonging/relationship, **not what the objects are**.
Recognizability of a specific work is expressly *not* claimed. The user can
assess whether the structure is legible on a physical iPad.

Preview route: `/fixtures/semantic-visual-bookshelf/` (WLAN, noindex).
