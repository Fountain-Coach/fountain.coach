# Private staging baseline (not redistributed)

The stage builder compares the source-owned essay against the exact retained Fountain Press v197 Reader. Five reference files (`estate-index.html`, `read-essays.html`, `books-essays.html`, `books-catalog.json`, and `reader-app-live.js`) must be materialized by an authorized maintainer from the **retained immutable owner-WLAN v197 release**, never copied into this public Git repository. Their exact expected SHA-256 values are pinned in `scripts/build_model_instrument_press_stage.py`.

No stage-owned Reader corpus, private author material, or derived live service payload is distributed as a fixture here. The build fails closed if any supplied predecessor file differs. The shared Fountain Press engine remains unchanged.
