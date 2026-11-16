# Proof Press — the existing Fountain Press compositor, fully inspected

**Domain/source owner:** `Fountain-Coach/fountain.coach`. Agent procedure and independent auditor: canonical `Fountain-Coach/.github/.codex/skills/linotype-proof-press`. This folder adds **no renderer**. Its `run.mjs` is a read-only browser witness of the existing `linotype-sheet` pages and authored source-block identity.

## Full edition run

Use the authorized host with the already-installed Playwright dependency. Set a fresh **private** proof directory on a volume with enough space for potentially thousands of screenshots; never put private manuscript screenshots into public Git.

`PLAYWRIGHT_MODULE=<absolute-existing-playwright> node scenarios/press-books/proof-press/run.mjs --origin http://192.168.8.50:8200 --release <independently-verified-current-release-id> --out /<private-proof-volume>/proof-<new-unique-run-id>`

Default = **all admitted published works × 4 specified platform geometries** and **every actual rendered physical folio**. The browser loads original fonts/media from the actual origin, waits for the existing Reader's `data-layout=ready`, captures each `.linotype-sheet` page to an individual PNG and writes one JSONL geometry/source record per folio. `--work`, `--platform`, `--limit` and a single engine are diagnostic subsets only; even a complete 16/16 work is not a 65-work estate proof. `--browser chromium` requires an actually installed Chromium executable; never claim it if absent. For secure cross-platform proof record the browser/font/OS/device versions, and separately verify physical iPad Safari/VoiceOver rather than pretending emulation is native.

## Independent audit

Run the canonical `linotype-proof-press/scripts/audit_proof.py <private-proof-dir> --require-complete --write`. It verifies exact published work × viewport × folio coverage, unchanged screenshots, source-block presence, measured source-character coverage using original template lengths and contiguous compositor intervals where available, and unexpected title/figure/clipping findings. For un-ranged or split figures it reports identity-only proof rather than falsely claiming character-perfect coverage. It creates machine `audit.json` and a local private `index.html` contact sheet. A **machine-inventory complete** state always remains `EDITORIAL_REVIEW_REQUIRED` until the source-owning editor examines every raised exception and accepts the actual typography. No average fill percentage is a quality score.

Do not confuse observed v216 metadata's `publicationSnapshotSourceReleaseID` (the *predecessor* v215) with v216's **active** release; supply an independently read active release identity explicitly via `--release`. Future browser run comparisons need all source, browser, font, OS and geometry identities.

## Reproduced first proof (not a universal closure)

On 16 November 2026 the active owner-WLAN v216 Reader composed *What Makes a Page Modern?* as **16 leaves** in WebKit's 820×1180 iPad portrait-sized viewport. All 16 were observed and captured, with original source block identifiers, zero JS errors and no blocking geometry. One heading near the end of a leaf was marked as an editorial review candidate. Its scoped audit correctly reports `INCOMPLETE` for the estate-wide matrix (one work and one platform), **not** print-quality acceptance. Private screenshots and full ledger remain on the owner's working volume, not a public repo.

The accompanying essay's 1,000-leaf plate is a **diagram**. It is not a screenshot of a thousand pages actually proofed; the scanner's ability to enumerate every page does not waive the obligation to execute the complete run on each admitted book and platform before release.
