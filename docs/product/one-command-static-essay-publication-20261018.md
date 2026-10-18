# One-command essay publishing — Chapter 158

**Owner:** `Fountain-Coach/fountain.coach`. **Host:** `fountain.coach` only. **Current admitted scope:** `/essays/the-composable-book/` plus its one collection card. This is deliberately the first narrowly proven instance of a future generic publication contract, not authority over other hostnames or all essays.

## Author's workflow

Edit the source essay, inspect the generated page, and commit the approved source revision on the owning Git branch.

```sh
npm run product:build
npm run essays:check
npm run essays:prepare
npm run essays:publish
```

- `essays:check` runs the immutable-source and 9 local deployment contract tests.
- `essays:prepare` inspects the live collection, verifies its preserved card sequence, determines the active release and Caddy SHA, and computes a reproducible release package **without any host mutation**. It can run with a dirty Git tree for inspection.
- `essays:publish` requires a **clean committed Git tree**, rebuilds and verifies the essay, checks the exact live collection and Caddy predecessor, packages eight reviewed files, transfers one archive plus the fixed-host activation module, activates a cloned immutable predecessor atomically, and independently reads back **every changed route and every changed asset** by exact SHA-256. It also confirms five existing public sibling routes remain byte-identical.
- Missing SSH identity, changed index, changed Caddy, incorrect source digest, changed sibling, missing remote prerequisites, invalid public bytes, or a failed activation must stop with a named failure. The previous release is preserved. On failed public verification, the command attempts rollback; an ambiguous rollback must be reported rather than blindly retried.
- The host address and deployment root are source-fixed, and SSH host-key checking is strict. The fixed installer refuses unrelated routes. This does **not** yet provide a least-privilege deployment identity: the existing recovery account is `root@65.109.14.71`; replacing it with a restricted forced-command identity remains an explicit hardening task.
- The successful receipt is written to `/tmp/fountain-coach-essay-publication-receipt.json` on the initiating Mac. The source is not marked published until a matching public HTTPS witness exists.

This avoids unrelated FountainStore replication, FCIS host bootstrap, MIDI 2.0 runtime and CI requirements for a simple static article. It does not generalize to mutable Store publishing or privileged host/identity management.

## Deterministic local negative and positive checks

```sh
python3 -m unittest discover -s scripts -p test_essays_publication.py -v
```

The harness uses a disposable simulated Caddy release tree. It checks reproducible tarball bytes, preservation of collection siblings, strict route inventory, inactive-source tampering, Caddy drift, predecessor drift, atomic activation, a reload failure with rollback, stale rollback refusal, and duplicate-operation refusal. None of these local tests implies a live deployment.

## Distinguishing source, activation and publication

The only success predicate is `PUBLISHED_HTTPS_VERIFIED`, with source revision, artifact digest, remote release identity, predecessor, collection digest, exact public asset hashes and unmodified sibling digests. `PREPARED_NOT_PUBLISHED` means the command has read-only preflight evidence. `ACTIVATED_PENDING_PUBLIC_WITNESS` means the remote effect finished but it has **not** yet been accepted as published.

Existing production `/essays/` includes **To Read Is Not to Remember** as well as the three original essays. The owner source preserved this live predecessor and adds a fifth card. Do not derive this release from the earlier four-card source snapshot.

## Operational limits

The command initially covers only this essay: it is not yet a generic `--slug` or cross-domain publisher. Future work can generalize the release schema after a terminal, witnessed deployment. Do not widen it by adding arbitrary SSH arguments, target paths, or hostnames. Do not add GitHub CI. Do not return to an unneeded model-defined publication intent catalog.

The remote operator must have a previously approved SSH deployment identity and Caddy release rights. If the remote transport is blocked by the tool environment, preserve the prepared candidate and report the block. Never silently replace an authenticated transport with an unverified backchannel.
