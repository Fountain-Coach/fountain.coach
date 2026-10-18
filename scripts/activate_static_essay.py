#!/usr/bin/env python3
"""Fixed-host immutable essay activation for Fountain Coach (FCIS 158).

Runs on the admitted Caddy origin. Paths, vhost and mutable routes are fixed in
source, not chosen by a remote user. It never executes source-content code.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import uuid

HOST = "fountain.coach"
SITE = Path("/srv/fountain-static-publications/fountain.coach")
CADDY = Path("/etc/caddy/Caddyfile")
ESSAY_BASE = "/essays/"
MAX_BYTES = 15_000_000


class Refused(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_archive(archive: Path, expected_sha: str):
    raw = archive.read_bytes()
    if len(raw) > MAX_BYTES or digest(raw) != expected_sha:
        raise Refused("archive size or SHA-256 differs from approved artifact")
    entries: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as bundle:
        for item in bundle.getmembers():
            path = Path(item.name)
            if (not item.isfile() or item.name in entries or path.is_absolute()
                    or ".." in path.parts or not item.name or item.size > MAX_BYTES):
                raise Refused("unsafe, duplicate or non-file release member")
            entries[item.name] = bundle.extractfile(item).read()
    if "release-manifest.json" not in entries:
        raise Refused("release manifest absent")
    m = json.loads(entries["release-manifest.json"])
    if (m.get("host") != HOST or m.get("schemaVersion") != 1
            or m.get("publicationState") != "candidate"
            or m.get("route") != "/essays/the-composable-book/"
            or m.get("collection") != "/essays/index.html"):
        raise Refused("unsupported host/route/publication identity")
    expected = {f["path"] for f in m.get("files", [])}
    if len(expected) != len(m.get("files", [])) or expected | {"release-manifest.json"} != set(entries):
        raise Refused("manifest/file inventory mismatch")
    for record in m["files"]:
        name = record["path"]
        if not (name == "essays/index.html" or name.startswith("essays/the-composable-book/")):
            raise Refused("release contains an unrelated route")
        data = entries[name]
        if len(data) != record["bytes"] or digest(data) != record["sha256"]:
            raise Refused("declared file digest mismatch: " + name)
    if "essays/the-composable-book/index.html" not in entries:
        raise Refused("article entry absent")
    if "essays/the-composable-book/assets/cover.png" not in entries:
        raise Refused("cover asset absent")
    index = entries["essays/index.html"].decode("utf-8")
    for slug in ("the-composable-book", "to-read-is-not-to-remember",
                 "semantic-compilation-the-archive-is-not-the-edition",
                 "teatro-an-unfinished-composition",
                 "reframe-and-the-business-value-of-the-estate"):
        if index.count(f'data-essay-route="/essays/{slug}/"') != 1:
            raise Refused("collection is missing or duplicates: " + slug)
    return m, entries


def proposed_config(caddy: str, route: str) -> str:
    # Only this existing matcher may be extended; untouched host blocks stay byte-identical.
    pattern = r"( @fountainNewEssay \{\s*host fountain\.coach\s*path )([^\n]+)(\n \})"
    matches = list(re.finditer(pattern, caddy))
    if len(matches) != 1:
        raise Refused("production Caddy matcher missing or ambiguous")
    match = matches[0]
    paths = [route[:-1], route, route + "*"]
    line = match.group(2)
    if all(path in line.split() for path in paths):
        return caddy
    if any(path in line.split() for path in paths):
        raise Refused("partial route matcher state")
    new_paths = line + " " + " ".join(paths)
    return caddy[:match.start(2)] + new_paths + caddy[match.end(2):]


def preflight(root: Path, config: Path, manifest: dict, entries: dict[str, bytes]):
    current = root / "current"
    if not current.is_symlink():
        raise Refused("current is not an immutable release symlink")
    link = os.readlink(current)
    if link != manifest["predecessor"] or not link.startswith("releases/"):
        raise Refused("active predecessor changed; rebuild against live state")
    prior = current.resolve(strict=True)
    if ((root / link).resolve(strict=True) != prior or
            not prior.is_relative_to((root / "releases").resolve(strict=True))):
        raise Refused("current symlink resolves outside release directory")
    old = (prior / "essays/index.html").read_bytes()
    if digest(old) != manifest["predecessorCollectionSHA256"]:
        raise Refused("live essays collection has changed; reconcile first")
    for rel in (
        "essays/to-read-is-not-to-remember/index.html",
        "essays/semantic-compilation-the-archive-is-not-the-edition/index.html",
    ):
        if not (prior / rel).is_file():
            raise Refused("required earlier essay missing from predecessor: " + rel)
    caddy = config.read_text()
    if digest(caddy.encode()) != manifest["predecessorCaddySHA256"]:
        raise Refused("Caddyfile changed; re-review before activation")
    new_config = proposed_config(caddy, manifest["route"])
    return prior, caddy, new_config


def activate(archive: Path, sha: str, *, root: Path = SITE,
             config: Path = CADDY, validate=None, reload=None):
    m, entries = read_archive(archive, sha)
    prior, before, after = preflight(root, config, m, entries)
    validate = validate or (lambda path: subprocess.run(
        ["caddy", "validate", "--config", str(path), "--adapter", "caddyfile"], check=True))
    reload = reload or (lambda: subprocess.run(["systemctl", "reload", "caddy"], check=True))
    ident = "static-composable-" + sha[:14]
    release = root / "releases" / ident
    if release.exists():
        raise Refused("release already exists; inspect existing receipt instead of replay")
    candidate = config.parent / (".caddy-composable-" + uuid.uuid4().hex)
    candidate.write_text(after)
    try:
        validate(candidate)
    finally:
        candidate.unlink(missing_ok=True)
    # Clone predecessor to conserve every unrelated file and earlier essay.
    shutil.copytree(prior, release, symlinks=True)
    for name, contents in entries.items():
        destination = release / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)
        destination.chmod(0o644)
    for record in m["files"]:
        if digest((release / record["path"]).read_bytes()) != record["sha256"]:
            raise Refused("staged release differs from reviewed artifact")
    for rel in ("essays/to-read-is-not-to-remember/index.html",
                "essays/semantic-compilation-the-archive-is-not-the-edition/index.html"):
        if digest((prior / rel).read_bytes()) != digest((release / rel).read_bytes()):
            raise Refused("sibling route changed")
    backup = config.parent / ("Caddyfile.before-composable-" + sha[:14])
    if backup.exists():
        raise Refused("config backup exists; do not overwrite predecessor evidence")
    backup.write_text(before)
    current = root / "current"
    newlink = root / (".pending-" + uuid.uuid4().hex)
    newlink.symlink_to("releases/" + ident)
    activated = False
    try:
        os.replace(newlink, current)
        activated = True
        newconfig = config.parent / (".candidate-" + uuid.uuid4().hex)
        newconfig.write_text(after)
        os.replace(newconfig, config)
        validate(config)
        if after != before:
            reload()
    except BaseException:
        if activated:
            restore = root / (".rollback-" + uuid.uuid4().hex)
            restore.symlink_to(m["predecessor"])
            os.replace(restore, current)
            config.write_text(before)
            reload()
        raise
    return {
        "state": "ACTIVATED_PENDING_PUBLIC_WITNESS",
        "host": HOST,
        "route": m["route"],
        "sourceRevision": m["sourceRevision"],
        "archiveSHA256": sha,
        "release": ident,
        "predecessor": m["predecessor"],
        "predecessorCaddySHA256": m["predecessorCaddySHA256"],
        "newCollectionSHA256": digest(entries["essays/index.html"]),
        "newEssaySHA256": digest(entries["essays/the-composable-book/index.html"]),
        "files": len(m["files"]),
        "caddyBackup": str(backup),
    }


def rollback(expected_release: str, *, root: Path = SITE,
             config: Path = CADDY, reload=None):
    if not re.fullmatch(r"static-composable-[0-9a-f]{14}", expected_release):
        raise Refused("invalid release identity")
    current = root / "current"
    if not current.is_symlink() or os.readlink(current) != "releases/" + expected_release:
        raise Refused("another release became current; refusing rollback")
    release = current.resolve(strict=True)
    m = json.loads((release / "release-manifest.json").read_text())
    prior = m["predecessor"]
    if not prior.startswith("releases/") or not (root / prior).is_dir():
        raise Refused("rollback predecessor unavailable")
    backup = config.parent / ("Caddyfile.before-composable-" + expected_release.removeprefix("static-composable-"))
    if not backup.exists():
        raise Refused("rollback Caddy predecessor unavailable")
    prior_bytes = backup.read_bytes()
    if digest(prior_bytes) != m["predecessorCaddySHA256"]:
        raise Refused("rollback Caddy predecessor digest mismatch")
    expected_config = proposed_config(prior_bytes.decode("utf-8"), m["route"])
    if config.read_text() != expected_config:
        raise Refused("Caddy changed since activation; refusing stale rollback")
    restore = root / (".rollback-" + uuid.uuid4().hex)
    restore.symlink_to(prior)
    os.replace(restore, current)
    config.write_bytes(prior_bytes)
    (reload or (lambda: subprocess.run(["systemctl", "reload", "caddy"], check=True)))()
    return {"state": "ROLLED_BACK", "previous": prior, "release": expected_release}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path)
    ap.add_argument("--sha256")
    ap.add_argument("--rollback", metavar="RELEASE_ID")
    args = ap.parse_args()
    if args.rollback:
        if args.archive or args.sha256:
            ap.error("rollback and publication arguments are mutually exclusive")
        result = rollback(args.rollback)
    else:
        if args.archive is None or args.sha256 is None:
            ap.error("--archive and --sha256 required for publication")
        result = activate(args.archive, args.sha256)
    print(json.dumps(result, sort_keys=True))
