#!/usr/bin/env python3
"""Publish The Composable Book to fountain.coach using one bounded Chapter 158 act.

No application runtime, FountainStore mirror, CI, or hand-edited Caddy needed.
An immutable release is prepared from the pinned Git owner, transferred through
authenticated SSH and activated by the fixed-host installer. HTTPS bytes are the
terminal witness, not a Git push or a process exit code.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
ACTIVATOR = REPO / "scripts/activate_static_essay.py"
ARTICLE = "essays/the-composable-book/index.html"
COLLECTION = "essays/index.html"
BASE = "https://fountain.coach"
HOST = "root@65.109.14.71"  # Pinned production IP, never user-supplied.
REMOTE_BASE = "/srv/fountain-static-publications/fountain.coach"
PUBLIC_SIBLINGS = (
    "/essays/to-read-is-not-to-remember/",
    "/essays/semantic-compilation-the-archive-is-not-the-edition/",
    "/essays/reframe-and-the-business-value-of-the-estate/",
    "/essays/teatro-an-unfinished-composition/",
)
SSH_OPTIONS = ("-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
               "-o", "ConnectTimeout=12")


class PublicationStopped(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(args: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=80)
    if completed.returncode:
        raise PublicationStopped(
            f"Command failed ({args[0]}, exit {completed.returncode}): "
            + (completed.stderr.strip() or completed.stdout.strip())[:450]
        )
    # Preserve raw bytes when reading Caddy: even its trailing newline belongs
    # to the reviewed predecessor digest.
    return completed.stdout


def https(path: str) -> bytes:
    req = Request(BASE + path, headers={"User-Agent": "FountainCoachEssayPublication/1.0",
                                       "Cache-Control": "no-cache"})
    with urlopen(req, timeout=15) as response:
        if response.status != 200:
            raise PublicationStopped(f"HTTP {response.status} for {path}")
        return response.read()


def preflight(*, require_clean: bool) -> dict:
    if require_clean and run(["git", "status", "--porcelain"], cwd=REPO):
        raise PublicationStopped("Source worktree is not committed; publish a pinned revision")
    revision = run(["git", "rev-parse", "HEAD"], cwd=REPO).strip()
    from build_product_essay import parse
    subtitle, sections, blocks, figures, paragraphs = parse(
        (REPO / "content/product-essays/the-composable-book.md").read_text()
    )
    if (len(sections), len(figures), paragraphs) != (8, 4, 42):
        raise PublicationStopped("Product essay proof does not match reviewed source")
    # Tests are local and deterministic. The product build should not mutate
    # committed bytes when rerun.
    run(["python3", "scripts/build_product_essay.py"], cwd=REPO)
    run(["python3", "scripts/verify_product_essay.py"], cwd=REPO)
    run(["python3", "scripts/verify_essay_edition.py"], cwd=REPO)
    if require_clean and run(["git", "status", "--porcelain"], cwd=REPO):
        raise PublicationStopped("Deterministic build changed committed source; re-review")
    return {"sourceRevision": revision}


def source_files() -> dict[str, bytes]:
    names = [COLLECTION] + sorted(
        str(p.relative_to(SITE))
        for p in (SITE / "essays/the-composable-book").rglob("*") if p.is_file()
    )
    records = {name: (SITE / name).read_bytes() for name in names}
    from project_home_essay import baseline, project_home
    # Never overwrite the separately owned future Bookshelf at site/index.html.
    records["index.html"] = project_home(baseline())
    # One admitted shared navigation asset; no other site routes or assets.
    records["assets/estate-core.js"] = (SITE / "assets/estate-core.js").read_bytes()
    if ARTICLE not in records or len(records) != 10:
        raise PublicationStopped("Expected exactly ten fixed-path publication files")
    return records


def check_collection(candidate: bytes, live: bytes) -> None:
    """The only intended difference is one new product-essay gallery card."""
    from html.parser import HTMLParser

    class Cards(HTMLParser):
        def __init__(self):
            super().__init__(); self.entries = []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "article" and "data-essay-route" in attrs:
                self.entries.append(attrs["data-essay-route"])

    before, after = Cards(), Cards()
    before.feed(live.decode("utf8"))
    after.feed(candidate.decode("utf8"))
    expected = "/essays/the-composable-book/"
    if candidate == live:
        return
    if (expected in before.entries or after.entries.count(expected) != 1 or
            len(after.entries) != len(before.entries) + 1 or
            [x for x in after.entries if x != expected] != before.entries):
        raise PublicationStopped("Gallery does not preserve live existing essay cards")
    # Only one new card may differ from the live collection; preserve all
    # surrounding HTML, gallery ordering, pagination and other editorial edits.
    card = re.compile(
        rb'<article class="essay-gallery-card" data-essay-route="/essays/the-composable-book/".*?</article>',
        re.DOTALL,
    )
    restored, removed = card.subn(b"", candidate)
    if removed != 1 or restored != live:
        raise PublicationStopped("Collection changed outside the single admitted new card")


def remote_read(command: str, *args: str) -> str:
    return run(["ssh", *SSH_OPTIONS, HOST, command, *args])


def remote_profile() -> tuple[str, bytes]:
    link = remote_read("readlink", REMOTE_BASE + "/current").strip()
    if not link.startswith("releases/"):
        raise PublicationStopped("Unexpected production current symlink")
    caddy = remote_read("cat", "/etc/caddy/Caddyfile").encode()
    if "@fountainNewEssay" not in caddy.decode():
        raise PublicationStopped("Named Fountain Coach Caddy matcher absent")
    return link, caddy


def package(revision: str, predecessor: str, caddy: bytes,
            current_collection: bytes, files: dict[str, bytes],
            current_home: bytes | None = None,
            current_asset: bytes | None = None) -> tuple[bytes, dict]:
    from project_home_essay import baseline, check_home
    check_collection(files[COLLECTION], current_collection)
    if current_home is None:
        current_home = baseline()
    if current_asset is None:
        current_asset = https("/assets/estate-core.js")
    if current_home != files["index.html"]:
        check_home(files["index.html"], current_home)
    manifest = {
        "schemaVersion": 1,
        "publicationState": "candidate",
        "host": "fountain.coach",
        "route": "/essays/the-composable-book/",
        "collection": "/essays/index.html",
        "sourceRevision": revision,
        "predecessor": predecessor,
        "predecessorCaddySHA256": sha(caddy),
        "predecessorCollectionSHA256": sha(current_collection),
        "predecessorHomeSHA256": sha(current_home),
        "predecessorEstateCoreSHA256": sha(current_asset),
        "files": [
            {"path": name, "bytes": len(data), "sha256": sha(data)}
            for name, data in sorted(files.items())
        ]
    }
    records = {
        "release-manifest.json": (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode(),
        **files
    }
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for name, value in sorted(records.items()):
            info = tarfile.TarInfo(name)
            info.size = len(value)
            info.mode = 0o644
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(value))
    return gzip.compress(raw.getvalue(), compresslevel=9, mtime=0), manifest


def witness(files: dict[str, bytes], *, previous_siblings: dict[str, str]) -> dict:
    observed = {}
    for name, value in files.items():
        actual = https("/" if name == "index.html" else "/" + name)
        if actual != value:
            raise PublicationStopped("Public byte mismatch: /" + name)
        observed["/" if name == "index.html" else "/" + name] = sha(actual)
    for route, previous_digest in previous_siblings.items():
        actual = https(route)
        if sha(actual) != previous_digest:
            raise PublicationStopped("Existing public sibling changed: " + route)
        observed[route] = sha(actual)
    return observed


def deploy(prepared: bytes, manifest: dict, *, files: dict[str, bytes],
           previous_siblings: dict[str, str], receipt_path: Path) -> dict:
    expected_sha = sha(prepared)
    short = expected_sha[:14]
    local_folder = Path(tempfile.mkdtemp(prefix="fountain-essay-"))
    archive = local_folder / ("estate-essay-" + short + ".tar.gz")
    archive.write_bytes(prepared)
    remote_archive = "/tmp/estate-essay-" + short + ".tar.gz"
    remote_installer = "/tmp/estate-essay-activator-" + sha(ACTIVATOR.read_bytes())[:14] + ".py"
    print("RELEASE_PREPARED", expected_sha, manifest["predecessor"], flush=True)
    # No generic shell or arbitrary remote path. SSH authenticates and checks the
    # host key; the remote fixed-target installer validates all archive inputs.
    run(["scp", *SSH_OPTIONS, str(archive), HOST + ":" + remote_archive])
    run(["scp", *SSH_OPTIONS, str(ACTIVATOR), HOST + ":" + remote_installer])
    print("RELEASE_TRANSFERRED", remote_archive, flush=True)
    text = remote_read("python3", remote_installer, "--archive", remote_archive,
                       "--sha256", expected_sha)
    try:
        receipt = json.loads(text.splitlines()[-1])
    except Exception as error:
        raise PublicationStopped("Activation receipt missing; inspect host state before retry") from error
    if (receipt.get("state") != "ACTIVATED_PENDING_PUBLIC_WITNESS" or
            receipt.get("archiveSHA256") != expected_sha or
            receipt.get("sourceRevision") != manifest["sourceRevision"]):
        raise PublicationStopped("Activation receipt did not match release")
    print("RELEASE_ACTIVATED", receipt["release"], flush=True)
    try:
        checks = witness(files, previous_siblings=previous_siblings)
    except BaseException as error:
        try:
            rollback_result = remote_read("python3", remote_installer,
                                          "--rollback", receipt["release"])
        except BaseException as rollback_error:
            raise PublicationStopped(
                f"HTTPS witness failed ({error}); automatic rollback also failed "
                f"({rollback_error}); inspect release immediately"
            ) from error
        raise PublicationStopped(
            f"HTTPS witness failed ({error}); remote rollback: {rollback_result[-250:]}"
        ) from error
    completed = {
        **receipt,
        "state": "PUBLISHED_HTTPS_VERIFIED",
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "httpsWitness": checks,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(completed, indent=2, sort_keys=True) + "\n")
    return completed


def already_published(files: dict[str, bytes], live_collection: bytes,
                      receipt_path: Path) -> dict | None:
    """Idempotent no-op for a site already serving exactly these reviewed bytes."""
    if live_collection != files[COLLECTION]:
        return None
    checked = {}
    for path, expected in files.items():
        actual = https("/" if path == "index.html" else "/" + path)
        if actual != expected:
            # A newly revised essay or its homepage entry is a legitimate
            # successor to the already published collection. Its exact
            # predecessor is checked by the immutable release preflight.
            if path in ("index.html", ARTICLE, "assets/estate-core.js"):
                return None
            raise PublicationStopped(
                "Existing published asset differs unexpectedly: /" + path
            )
        checked["/" if path == "index.html" else "/" + path] = sha(actual)
    known = {}
    if receipt_path.is_file():
        known = json.loads(receipt_path.read_text())
        for sibling in PUBLIC_SIBLINGS:
            original = known.get("httpsWitness", {}).get(sibling)
            if original and sha(https(sibling)) != original:
                raise PublicationStopped("Previously accepted sibling changed: " + sibling)
    return {
        "state": "ALREADY_PUBLISHED_HTTPS_VERIFIED",
        "host": "fountain.coach",
        "route": "/essays/the-composable-book/",
        "release": known.get("release", "not-read-from-public-HTML"),
        "publishedSourceRevision": known.get("sourceRevision", "read-back-not-declared"),
        "files": len(files),
        "verifiedSHA256": checked,
        "noHostMutation": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", help="Read-only host preflight and deterministic artifact")
    parser.add_argument("--receipt", type=Path,
                        default=Path("/tmp/fountain-coach-essay-publication-receipt.json"))
    args = parser.parse_args()
    identity = preflight(require_clean=not args.prepare_only)
    files = source_files()
    # The public predecessor is verified both in the HTTPS view and against the
    # production exact symlink and Caddy config before activation.
    live_collection = https("/essays/")
    live_home = https("/")
    live_asset = https("/assets/estate-core.js")
    receipt_for_idempotency = args.receipt
    if not receipt_for_idempotency.is_file():
        receipt_for_idempotency = REPO / "docs/product/receipts/composable-book-production-20261018.json"
    already = already_published(files, live_collection, receipt_for_idempotency)
    if already is not None:
        print(json.dumps(already, indent=2, sort_keys=True))
        return
    predecessor, caddy = remote_profile()
    prior = {route: sha(https(route)) for route in PUBLIC_SIBLINGS}
    artifact, manifest = package(identity["sourceRevision"], predecessor, caddy,
                                 live_collection, files, current_home=live_home,
                                 current_asset=live_asset)
    if args.prepare_only:
        print(json.dumps({
            "state": "PREPARED_NOT_PUBLISHED",
            "host": "fountain.coach",
            "revision": manifest["sourceRevision"],
            "predecessor": predecessor,
            "files": len(files),
            "archiveSha256": sha(artifact),
            "caddyPredecessorSha256": sha(caddy),
        }, indent=2))
        return
    print(json.dumps(deploy(artifact, manifest, files=files,
                            previous_siblings=prior, receipt_path=args.receipt),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (PublicationStopped, HTTPError, subprocess.TimeoutExpired, OSError) as error:
        print("PUBLICATION_STOPPED:", error, file=sys.stderr)
        sys.exit(1)
