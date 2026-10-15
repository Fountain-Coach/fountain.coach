# Spatial Bookshelf V4 — browser and publication boundary

This supersedes V3's **semantic model**, in which anonymous book-shaped
tiles incorrectly stood in for containing spaces. V3 and earlier proofs
remain in Git history, not in the generated fixture.

- Containing regions are wide spatial fields. They are not books.
- Rounded squares represent individual books only.
- Color encodes a containing relationship at root, inside its area,
  and while reading one of its members.
- The same anonymous book has a stable token through two differently
  colored containing spaces; the return route changes with membership.
- No source-derived titles, art, author meaning, Score, content identity
  or external publication schema in this fixture.
- Publisher circle remains inert at root and reactive for parent return.
- Original V38 reading, real publication routes and source inventory
  remain unchanged; public publication is not in scope.

Proof: `scripts/verify_semantic_visual_fixture.py`,
`scripts/verify_semantic_visual_browser.mjs`, 10 shared renderer tests,
and untouched V38 publication browser regression.
PNG witnesses are captured from the browser at three form factors.
This proves mechanics, not perception or author approval.

Actual Safari iPad evaluation remains pending.
