# First Readings — recognition milestone V36

**Technical browser candidate, not author visual acceptance or native iPad Safari evidence.**

The chosen work, *Teatro — An Unfinished Composition*, is a source-digest-verified 22-paragraph essay by Benedikt Eickhoff. Its original authored SVG artwork (sha256 `226e3440690dd8cbeb331c4f3f62ee002fa0bc0e6007fcdf8431f1f578d115e2`) is used as cover artwork in the collection and as a non-duplicating CSS background illustration on the opening leaf, while the sole original in-body plate remains intact. The title is a source-backed publication label, not a new invented cover image. Teatro itself remains a tool rather than a book.

## Visual evidence

- [Side-by-side iPad journey](journey-ipad.png) — estate → collection → selected work cover.
- [Estate](ipad-estate.png), [First Readings collection](ipad-collection.png), [work's cover](ipad-work-cover.png), [reading page](ipad-reading.png).
- [iPad landscape work cover](ipad-landscape-work-cover.png) and [phone portrait collection](phone-collection.png).

Each is an automated Chromium CDP capture against actual WLAN addresses using iPad or phone viewport geometry, not actual iPad Safari.

## Executable acceptance

`node scripts/verify_first_readings_journey.mjs` visits the WLAN estate root and clicks the real First Readings publication cover, clicks the sole admitted work cover, validates identity/artwork/title/source, verifies the Linotype opening cover and first page turn, returns to the exact parent, and exercises browser Back. It checks iPad portrait/landscape and phone portrait, in addition to source integrity and a separate full Linotype browser regression. `npm run check` attests that all three original essay bodies (77 paragraphs, five plates) remain unchanged.

Only two top-level publication tiles are filled. First Hearings is currently an empty publishing possibility, not a counterfeit edition; the old Teatro authoring/First Hearing beta routes and singular Solstice First Reading are preserved, but not represented by a newly issued publication cover. The collection currently has one admitted work. **A human editorial review still decides whether the cover identities are perceptually strong enough at actual iPad distance.**
