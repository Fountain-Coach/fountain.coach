# Client-Centered — Fountain Press index and shell reconciliation

## Observed failure, not a new index

On 10 November 2026 the writer reported that the newly published
Client-Centered essay was not properly integrated: direct reading worked,
but the publishing shell did not recognize it across index-like entrances.
Inspection of the **actual current production release**
fcis-client-centered-20261110-4a89ae5 at fountain.coach confirmed:

- The new direct work and /estate/ embedded **seven** current essays.
- The root site, /estate/read/library/, /estate/read/essays/ and many older
  direct Reader routes still embedded only **five or six** current essays.
- /estate/bookshelf/ and /estate/collections/first-readings/ carried
  seven gallery records but omitted authored Reader source templates.
- Historical /essays/, /estate/essays/ and editions indexes omitted the
  newly admitted public essay or directed readers to a historical book.
- Two older indexes requested /assets/estate-shell.css, which returned 404
  instead of the already available, versioned production stylesheet.
- A historical Essays cover still described its new public destination
  as a WLAN candidate.

The original promotion checked its direct Reader URL, not complete index
parity. The actual HTML inventory exposed three conflicting publication
shells.

## Bounded existing-source correction

**Owner:** Fountain-Coach/fountain.coach; existing production-projector
scripts/build_client_centered_press_production.py; source manuscript
site/essays/client-centered/client-centered.md at
4a89ae5c2d822a0f594c382748277e2b818d82e4 and SHA-256
03e4497f6deabe173958bd632b721ac7f23ae95e3bbe0043a1204ad5039de78a.

- Reuse the **original Fountain Press Reader**, its existing 51 source
  templates, seven current essay source addresses, 30 First Readings,
  current gallery and versioned Press app across 55 existing Reader
  entrances. Preserve every direct route's canonical, social metadata,
  authored words and initial reading identity. Root entries open Bookshelf.
- Give the two older essay galleries an authentic link and approved
  source Score for Client-Centered. The previous editions catalogue gains
  a pointer to the current Reader. The older compiled continuing book and
  its three-essay sub-edition remain untouched historical publications.
- Correct the historical Essays cover to point to the current seven-essay
  Reader and mark that destination as public, without modifying the
  separate First Readings cover or historical source texts.
- Reuse an already-published, content-addressed stylesheet rather than
  introducing a second CSS asset or any new reader/publishing service.
- Preserve the exact source-owned edition manifest, both original Teatro
  Score SVGs, the public share raster and the old compositor SHA.
- The release-diff contract is **55 Reader HTML entrances, four historic
  index HTML entrances, and one release manifest**: 60 files modified,
  no added or deleted files, 384 predecessor files byte-identical.

## Offline browser E2E, before author-approved public update

The bounded candidate is derived from the observed public predecessor,
not from an arbitrarily older source or unrelated private staging.

- Five focused static tests passed, including full 55/55 Reader-template
  and gallery parity, per-route metadata, archive/source preservation,
  declared file diff and the existing 30 First Readings.
- 35/35 Chromium browser visits passed across landscape, portrait and
  phone widths; no fatal Reader JavaScript or missing current essay.
- Seven interactive click journeys passed: Essays cover -> Client-Centered,
  page turn, return with the Reader logo, old essay gallery links, and
  historical catalogue entrances.
- Exhaustive 55/55 Chromium Reader entrance check passed.
- The two previously broken stylesheet URLs were corrected with actual
  existing production assets.

Candidate browser proof did **not** imply public deployment,
physical iPad Safari or VoiceOver. The separately authorized EstatePublisher
public effect and its independent live HTTPS/browser proof are recorded
below, without promoting desktop Chromium to native-device acceptance.

The source-owning fountain.coach Git repository has no existing PLANS.md;
this record continues the existing Client-Centered publication acceptance
documentation. No new app, alternative renderer, DNS service, password
or Store transaction was introduced.


## Production terminal closeout — independently read back

**ACTIVE:** fcis-client-centered-shell-20261110-1e26f73 on
https://fountain.coach/, installed by the existing native
EstatePublisherSSHDelivery with immutable release inventory, authenticated
SSH/rsync, atomic symlink activation, independent HTTPS byte verification
and retained rollback.

- Canonical source projector merge:
  Fountain-Coach/fountain.coach@1e26f73b6de9a17f9c2a78dd417bc8111e38eebb
  (source PR #14, exact merged code).
- Work manuscript unchanged at original SHA-256
  03e4497f6deabe173958bd632b721ac7f23ae95e3bbe0043a1204ad5039de78a.
- Publisher full source-inventory SHA-256:
  3670e033eb3d7a8721067fddc306cafbefd8d85b7f9c3d7d53d1a845eebb630e.
- Native typed result: state=active, activated=true;
  **14/14** public HTTPS path+SHA-256 witnesses, including root,
  Bookshelf, both collection indexes, existing and new essays,
  original new-essay semantic manifest/social raster, old index surfaces,
  and a retained existing neighboring Reader route.
- Preserved predecessor (rollback): fcis-client-centered-20261110-4a89ae5.
- [Typed public release receipt](../releases/2026-11-10-client-centered-shell-public-receipt.json)
  is verbatim native publisher output, not inferred from HTTP 200.
- [Live 55-route Reader browser acceptance](2026-11-10-client-centered-shell-live-all-reader-routes.json):
  **55/55** true public HTTPS routes with current seven-essay catalogue,
  51 complete source templates, 30 original First Readings and no
  fatal runtime errors in the observed set.
- [Live seven-journey navigation acceptance](2026-11-10-client-centered-shell-live-navigation-journeys.json):
  **7/7** public HTTPS end-to-end flows: root Bookshelf to Client-Centered,
  next page, logo to Bookshelf, current Essays index, mobile Bookshelf,
  both historic essay galleries and two older edition index pointers.

**Authority boundaries:** No new native physical iPad Safari/VoiceOver proof
and no FountainStore membership/effect claim. Earlier independent
historical book editions preserve their original text and status; this
release updates the current Reader/index membership, not their archived
manuscripts. The original author-provided source and source-bound artwork
remain byte-identical under the recorded SHA manifests. The candidate's
landscape/portrait/phone browser matrix and the live public click journeys
are distinct forms of evidence, not one test counted twice.
