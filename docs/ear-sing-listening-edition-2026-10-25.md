# The Ear That Learns — listening edition (source candidate)

**25 October 2026 · Fountain-Coach/fountain.coach.** This revises the new authored essay source only; its 25 October initial public-intent v1 prose, typographic art and private staging release remain available in Git/immutable rollback history. The changes do not modify the three separately composed Linotype book essays or Reframe Bookshelf membership.

## Editorial correction

The first draft made a tour through Italian opera, German declamation, Spanish zarzuela, tabla and Hindustani practice. The amended text starts from the actual Sing event at **2.15 seconds**, narrates the plain/articulated/expressive three-take contrast, follows Ear's precisely scoped spectral measurements, and derives the question of teaching and repetition from that concrete listening problem. The traditions now enter one continuous argument and remain different forms of musical learning; **none is falsely presented as an actual audio performance in this essay**.

The hero has been replaced with a 1536 × 1024 authored technical plate, **04 HEARING / REHEARSAL**: cream paper, thin isometric architectural lines, one vermilion listening mark, a score pedestal and a listening instrument. The source SVG and a high-resolution PNG derivative use the existing figure-series manufacturing and the image is reused at the Essays gallery entrance. No human singer, voice sample or recording is inferred from the picture.

## One musical score; three exact audio witnesses

Original score: [Sing `examples/sustained-melisma.json`](https://github.com/Fountain-Coach/sing/blob/main/examples/sustained-melisma.json). Source is a five-second original synthesized English-like `la mi na` prototype, **not real European opera, tabla, Hindustani vocal practice or a source-blindly qualified singer**. Four MIDI 2.0 notes span three phonetic syllables; the first vowel continues across two notes. Original full 48 kHz PCM SHA-256 digests and Ear's score-aligned spectral measurements are in [Sing's three-take evidence](https://github.com/Fountain-Coach/sing/blob/main/docs/evidence/three-take-comparison-2026-10-24.md) and [Ear's bounded selection](https://github.com/Fountain-Coach/sing/blob/main/docs/evidence/2026-10-24-ear-three-take-selection.md).

| Take | Original 48k PCM SHA-256 | Private preview AAC/M4A SHA-256 |
| --- | --- | --- |
| plain | `f4826365089889eafef579f5e0b3cf6f77d7bf570fcc0fa6e1d5f85ef191cf24` | `83b45c232a05abea5c3fe5fd25bee71630ce86e66eae78b9817cd60fd9ee8c21` |
| articulated | `1d285c6b0a9dd2f7b7be58aac1509b5f55bcac5e3636c530cbec25f20db8f505` | `c27fe2ee9bd757b4b1d82aeb3f1ea82f7ff24b1b03741cc77408ebc1638cc807` |
| expressive | `b7390503bdcb4669235fc417e0d21f8008c578f59228ab7ee0817e3df3ff8d27` | `acf902889e00a37bb832864ff826a612b468fb49900db8de02682cbefd6ab68f` |

The three preview `.m4a` files are separately encoded high-quality AAC-LC **derivatives**, not bit-identical PCM or original phonetic measurements. Mac `afinfo` confirms 48 kHz mono and 5.2 s. The existing canonical staging server forbids `.wav` and publicly unlisted `.mp4` in its source-locked WLAN preview. The WAVs stay in author-controlled development scratch space; neither WAV nor AAC bytes enter Git. Their staging-only M4A copies are SHA-256 verified before activation and by live independent HTTP readback, with no historical private Satzfunk media copied.

## Existing semantic player, direct sound comments

Software owner: [SatzfunkPlayer `1e621411dc412ab2482a9e6df9a6054145ddfa43`](https://github.com/Fountain-Coach/SatzfunkPlayer/commit/1e621411dc412ab2482a9e6df9a6054145ddfa43) with `src/essay-listening.mjs`, six new core tests and 102 passing overall tests. Exact source file SHA-256 `dacec22a5454bc5481fb40163ce387b55deb2c093af6e69e648f65fd2c03af4c` is checked into Fountain Coach as a **byte-identical, same-origin static projection** for the essay (not a fork or second player authority).

The player uses one native HTML audio element, selection of the three take identities, seek-to-comment observations at 0.00, 1.15, 2.15 and 3.35 seconds, and a reader comment that can be copied with exact sample identifier, original WAV checksum and source position. No comment persistence, upload, live AI inference, invented transcript, autoplay or automatic publication exists. On private WLAN HTTP, if Safari denies clipboard API, a selected text field provides manual copy. A direct link with `?take=articulated&t=2.15#listening-exhibit` selects the actual recorded moment without autoplay.

**Numerical evidence boundaries:** shipped Ear audio worklet only monitored activity; a separately scoped companion worklet measured score-aligned high-frequency energy share at /m/ and /n/ and selected articulated as acoustic development baseline. The Japanese PJS singer reference and its independent human annotation revisions are not cleared as this essay's audio source; Japanese phone recognition and singer qualification remain blocked.

## Publication scope

Source HTML, CSS, SVG, PNG, source-bound annotation manifest, player projection, tests and exact source inventories are in the Fountain Coach repository. The AAC bytes are private WLAN-stage evidence only, with a release plan and media digests; public HTTPS must remain unchanged absent separate editorial publication authorization. The previous staged v31 essay is the rollback predecessor for the listening-edition update.
