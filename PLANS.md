# Editorial release plan — 28 October 2026

## New reader-first landing scenario — 29 October 2026

Writer's decision: the primary Fountain Coach entrance should open directly into a **continuing Linotype Essays book**. Each published essay is one addressable chapter; the latest **verified writing date**, not merely publication timestamp, is always the first chapter and the first visible measured folio, even in alternative reader-chosen semantic pathways. The existing *author-led four-hero gallery* remains available as a separate comparison scenario at `/scenarios/author-led/`. The original published Essays index, full individual reading routes, complete Press Bookshelf and Solstice/Teatro editions retain their own source authority.

Governance 07/08/92/127, FCIS source/non-invention rules and the current Linotype/Publication Core agreement were read. The seven original stage-v58 essay HTML files are pinned individually by SHA in `editorial/living-essays-reader-source.json`. The current latest documented written date is *The Door Is a Score* on 27 Oct 2026; some older essays have only a publication date or no date, which is **not** invented as a writing date. Their existing published collection order is a disclosed editorial fallback. Admissions of new essays require metadata reconciliation; regenerated source should determine the new latest from verified written dates. Reading pathways: Continuing / Listening / Books and memory / Reframe and estate.

`scripts/build_living_essays_reader.py` composes the original seven authored article DOMs and artwork without writing new prose; Press's measured Linotype engine performs the pagination and verifies source text preservation. Original playback controls, complete scholarly PDF and site-specific interactions stay on their original published article URLs; the book links to them rather than displaying non-functional substitutes. `scripts/project_reader_first_source.py` supplies the approved source-owned masthead, reel and footer. `scripts/project_reader_first_stage.py` is a stage-only host path projection. The original three-essay Press/Bookshelf generator has been amended so building an edition can no longer overwrite the parent homepage.

Source `npm run check` passed for the new root: 111 tracked site files, 26 index pages, seven essays, three complete Press subeditions, the signed reading-continuity PDF and source-owned listening assets. Local actual Chrome/Press browser tests passed six cases (390x844, 820x1180 and 1280x800; all four semantic orders and Contents). **Source compilation and local acceptance are not a staging activation**; the candidate is staged separately from v58 and requires immutable inventory, live HTTP evidence and rollback.


## Route-specific Linotype repair — 28 October 2026

The Composable Book article was incorrectly unstyled because its page-local `assets/essay.css` was absent from v56/v57. The public owner HTTPS served the original CSS with HTTP 200 (7,393 bytes, SHA-256 `05b3915…`) and the stage route returned 404 with MIME refusal. The original file has now been source-recovered and staged as v58 on `192.168.8.50:8200` without altering the article HTML. Chrome checks exercised mobile (390), iPad-like (820) and desktop (1280) sizes including real image decoding and table-of-contents anchors. V57 remains the rollback release; production is unchanged. The estate companion branch owns the typed v58 receipt and live route-specific CSS regression check.

## Successful owner-WLAN staging — 28 October 2026

The stage previously marked not accepted below is now active as v57, `shared-shell-20261028-v57-author-led-aa38389`, assembled from the checked Git source and the verified v56 predecessor. Full remote SHA inventory 1,138 files, 509 independently served routes PASS, 30 live Chrome viewport checks PASS. v56 is retained for rollback; the public HTTPS estate remains unchanged. Complete route report and receipt are in the private Mac-mini staging receipt root and described in the estate source branch.

## Observed goal and finite acceptance

Author approved **Fountain Coach as an independent one-person software and publishing practice**. Present a few real essays through their original hero illustrations at `/`; make `/essays/` the complete reading room next door; preserve the genuine Fountain Press Bookshelf at `/editions/`. Carry this semantic distinction consistently through the entire registered estate. Stage one immutable candidate on the already registered owner-WLAN Ubuntu staging machine, document every owned route, and independently check accessible masthead, full canonical nine-entry reel and footer on all routes. **No public production promotion is requested.**

## Governance reading record

- **Chapters read:** 07 (Goal Fidelity and phase-sized work, use existing apparatus); 08 (evidence is source-, build- and runtime-bound); 92 (parent identity, domain-owned authority and shared semantics); 127 (checked-in direct-static Publication Core, no hydrated shell), plus estate operating rules and organization FCIS Goal Fidelity.
- **Forbidden here:** invented new publisher/CI, silently mutating public production, copying derived staging HTML back over canonical Git, deleting source media, treating generated book pages or old screenshots as site authority, making a solo practice into a staffed institution.
- **Conflicts:** October 14 root-equals-Bookshelf notes conflict with the explicit 28 October author decision and with public portal semantics. This editorial change resolves the root's role and retains Bookshelf at `/editions/`; update its generator/tests without falsifying historic work identity. Current public and staged essays are newer than several source-tree article files.
- **Excluded:** publishing to public HTTPS, DNS/TLS surgery, content rewrites of independent Governance/MIDI2/Satzfunk Works, private Reframe Bookshelf admission and unauthorised media migration.

## Phase 1 — source-bound editorial composition

The independent root displays four authentic essay heroes, declares authorship/role, maintains shared publication-shell links and social metadata. The /essays/ index contains the seven previously public works and original source-owned hero references. No new essay text is invented. Book builder never overwrites `site/index.html`; `/editions/` retains the Fountain Press grid. Maintain deterministic SHA inventory.

## Phase 2 — estate source inventory and chrome contract

The Estate owner maintains a snapshot of every Git-tracked HTML source route, source owners and delegated literary paths, plus explicit public-only discovered routes. The test `scripts/audit-editorial-shell.py` gives per-route findings. The canonical reel now uses Works because the actual current stage already serves /works/; Status stays a legal footer link.

## Phase 3 — current production-first stage candidate

A candidate MUST start from the independently observed relevant public production bytes/immutable inventory, preserve original public-only essay HTML/media, add exactly this pinned editorial source delta, and preserve accepted stage-only content from v56. Never blindly stage all of latest Git main. Confirm current stage `current` predecessor and actual running service, use established EstatePublisher SSH/rsync/sha256/atomic activation, independently reread every selected path and asset. Keep old release available for rollback. Native production-first enforcement remains separately evidenced.

## Acceptance and current state

- **PROVEN (static source comparison):** root vs Essays reel/order/URLs match; four feature essays, seven collection items; identical legal footer link graph; two separate page identities; Bookshelf retained.
- **PROVEN (executed on the connected owner Mac):** `npm run check` passes at exact Git source SHA `aa38389ba2ef9070d91a36c169e74902ed3b096b`. It covers nine-entry root/Essays reel and equal footer, four featured and seven catalogue essays, the original 77 manuscript paragraphs, five figures, the complete 106-file SHA inventory, the reading-continuity PDF and the Ear/Sing source verification. A stale five-essay assertion was repaired to seven before the passing run.
- **PROVEN (local test composition):** a disposable private preview was generated from a read-only copy of the actual stage v56 root plus the exact Git editorial delta and authentic assets. It has seven independent edition/collection index routes; complete stage v56 was also copied read-only to the connected Mac. This is development/preview evidence only, not a WLAN staging publication.
- **OBSERVED:** canonical private staging on `192.168.8.50:8200` still serves `shared-shell-20261028-v56-modell-wirklichkeit-e3753d7`, not this branch. SSH **read** and source tests execute successfully. Explicit SSH/rsync **write** attempts to the canonical WLAN stage `incoming/` directory are rejected by OpenAI tool safety checks before running; no host filesystem denial was observed.
- **NOT ACCEPTED:** full 509-file live stage shell parity, browser/device acceptance, native staging activation, exact new stage release digest and typed publisher receipt. `npm run book:browser` and the complete estate route audit have not yet been completed.
