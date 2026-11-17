#!/usr/bin/env python3
"""Fail-closed Fountain Press publication closure over one immutable composition.

This is the existing Press publication preflight, not a publisher or a second
Reader. It checks a full release or a small immutable overlay plus its source
predecessor. No writes, activation, network or public authorization occur.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from published_frontend import APP_PATTERN, parse_gallery, source_templates

SNAPSHOT = re.compile(
    r'<script type="application/json" id="reader-publication-data">(.*?)</script>', re.S)
JSON_LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
PRESS_ENGINE = re.compile(
    r'/estate/assets/linotype/reading-first-press-engine\.[a-f0-9]{64}\.js')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(root: Path, *, predecessor: Path | None = None,
           lane: str = "staging", expected_work: str | None = None) -> dict:
    """Require one Bookshelf, one catalogue and a current Essays entrance.

    The root may be an immutable overlay; only absent files resolve to its
    predecessor. An obsolete Essays entrance is refused even when an essay's
    direct route returns HTTP 200. This is pre-activation and readback proof.
    """
    if lane not in ("staging", "public"):
        raise ValueError("Unsupported publication lane")
    root = Path(root).resolve(strict=True)
    predecessor = Path(predecessor).resolve(strict=True) if predecessor else None

    def read(relative: str) -> bytes:
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Invalid publication path")
        for base in (root, predecessor):
            if base is None:
                continue
            path = base / rel
            if path.is_file():
                if path.is_symlink() or not path.resolve().is_relative_to(base):
                    raise ValueError("Symlink/escape refused: " + relative)
                return path.read_bytes()
        raise ValueError("Required publication path missing: " + relative)

    def json_script(html: str, pattern: re.Pattern, label: str) -> dict:
        matches = pattern.findall(html)
        if len(matches) != 1:
            raise ValueError("Expected one " + label)
        return json.loads(matches[0])

    main_raw = read("estate/index.html")
    main = main_raw.decode("utf8")
    snap = json_script(main, SNAPSHOT, "publication snapshot")
    if snap.get("schema") != "fountain.press.publication-snapshot.v1":
        raise ValueError("Unexpected publication snapshot schema")
    catalog = json.loads(read("estate/books/catalog.json"))
    books = snap.get("books", [])
    ids = [book["id"] for book in books]
    if not books or len(set(ids)) != len(ids):
        raise ValueError("Missing/duplicate published collections")
    ordered = catalog.get("stagedCollectionOrder" if lane == "staging"
                          else "publishedCollectionOrder")
    if ordered != ids or [b["id"] for b in catalog.get("books", [])] != ids:
        raise ValueError("Publication catalogue/book order drift")
    if catalog.get("publicationSnapshotSchema") != snap["schema"]:
        raise ValueError("Publication catalogue/snapshot schema drift")
    if lane == "staging":
        if catalog.get("stageOnly") is not True or catalog.get("publicReleaseAuthorized") is not False:
            raise ValueError("Private staging authority incorrectly claims public release")
        if snap.get("publicationLane") != "private-owner-WLAN-editorial-review":
            raise ValueError("Private staging Reader has wrong publication lane")
    elif catalog.get("publicReleaseAuthorized") is not True or catalog.get("stageOnly") is not False:
        raise ValueError("Public release must have separately admitted publication authority")

    if read("estate/read/library/index.html") != main_raw:
        raise ValueError("Legacy library entrance is an obsolete Reader")
    if lane == "public" and read("index.html") != main_raw:
        raise ValueError("Public root and estate entrance have different Bookshelves")
    app_paths = APP_PATTERN.findall(main)
    if len(app_paths) != 1:
        raise ValueError("Missing/duplicate content-addressed Reader app")
    app = app_paths[0]
    if sha256(read(app.lstrip("/"))) != app.rsplit(".", 2)[-2]:
        raise ValueError("Reader app source hash mismatch")
    engines = PRESS_ENGINE.findall(main)
    if len(engines) != 1 or sha256(read(engines[0].lstrip("/"))) != engines[0].rsplit(".", 2)[-2]:
        raise ValueError("Press engine hash mismatch")
    gallery = parse_gallery(main)
    if list(gallery) != ids:
        raise ValueError("Illustrated gallery/book order drift")
    _, source = source_templates(main)
    active = set()
    for book in books:
        bid = book["id"]
        original = next((b for b in catalog["books"] if b["id"] == bid), None)
        if original is None:
            raise ValueError("Missing book from catalogue: " + bid)
        works = book.get("orderedWorkIDs", [])
        art_ids = book.get("illustratedWorkIDs", [])
        if (not works or len(set(works)) != len(works)
                or not set(works).issubset(source) or active.intersection(works)):
            raise ValueError("Missing/duplicate/overlapping source work in " + bid)
        active.update(works)
        if original.get("orderedWorkIDs") != works or original.get("illustratedWorkIDs") != art_ids:
            raise ValueError("Catalogue work order/gallery drift: " + bid)
        if [g["id"] for g in gallery[bid]] != art_ids:
            raise ValueError("Reader gallery and book contents disagree: " + bid)
        if original.get("firstIllustratedChapterID") != art_ids[0]:
            raise ValueError("First illustrated chapter differs: " + bid)
        if lane == "staging" and (not book.get("stageOnly")
                                  or book.get("publicReleaseAuthorized") is not False
                                  or original.get("publicReleaseAuthorized") is not False):
            raise ValueError("Private staged book has unsafe publication status: " + bid)
        if lane == "public" and (book.get("stageOnly") is not False
                                  or book.get("publicReleaseAuthorized") is not True
                                  or original.get("publicReleaseAuthorized") is not True):
            raise ValueError("Private/unadmitted book found in public edition: " + bid)
        for historical in book.get("unlistedSourceWorks", []):
            if (historical["id"] in works or historical["id"] not in source
                    or historical["status"] not in ("archived-public", "historical-public")):
                raise ValueError("Archived/historical source membership drift")
        direct_raw = read("estate/books/" + bid + "/index.html")
        direct = direct_raw.decode("utf8")
        if (SNAPSHOT.findall(direct) != SNAPSHOT.findall(main)
                or parse_gallery(direct) != gallery
                or APP_PATTERN.findall(direct) != [app]
                or PRESS_ENGINE.findall(direct) != engines):
            raise ValueError("Direct book contains obsolete Reader: " + bid)
        if 'data-initial-volume="' + bid + '"' not in direct:
            raise ValueError("Direct book has wrong initial volume: " + bid)
        head = direct.split("</head>", 1)[0]
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', head)
        if (not canonical or urlparse(canonical[1]).path != original.get("directURLPath")
                or (lane == "public" and canonical[1] != original.get("canonicalURL"))):
            raise ValueError("Direct book canonical route mismatch: " + bid)
        book_ld = json_script(direct.split("</head>", 1)[0], JSON_LD, "book JSON-LD")
        if [item["identifier"] for item in book_ld.get("hasPart", [])] != works:
            raise ValueError("Stale direct-book JSON-LD membership: " + bid)
        for key in ("og:image", "twitter:image"):
            if key not in direct.split("</head>", 1)[0]:
                raise ValueError("Direct book social image metadata missing: " + bid)
        social = original.get("socialImagePath")
        if social and sha256(read(social.lstrip("/"))) != original["socialImageSHA256"]:
            raise ValueError("Stale book social derivative: " + bid)

    # Project this supported entrance from the current Essays book. Historical
    # individual work URLs are still present and do not become active members.
    essays_raw = read("estate/books/essays/index.html")
    if read("estate/essays/index.html") != essays_raw:
        raise ValueError("STALE_ESSAYS_ENTRANCE: not the current CMS-like Essays Reader")
    if expected_work is not None and expected_work not in next(
            b["orderedWorkIDs"] for b in books if b["id"] == "essays"):
        raise ValueError("New essay missing from admitted Essays collection: " + expected_work)
    return {
        "status": "PUBLICATION_CLOSURE_PASSED_BYTES_ONLY",
        "lane": lane,
        "books": [{"id": b["id"], "works": len(b["orderedWorkIDs"]),
                   "illustrations": len(b["illustratedWorkIDs"])} for b in books],
        "catalogueSHA256": sha256(read("estate/books/catalog.json")),
        "readerApp": app,
        "pressEngine": engines[0],
        "essaysEntranceSHA256": sha256(essays_raw),
        "expectedWork": expected_work,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--predecessor", type=Path)
    parser.add_argument("--lane", choices=("staging", "public"), default="staging")
    parser.add_argument("--expected-work")
    args = parser.parse_args()
    try:
        result = verify(args.root, predecessor=args.predecessor,
                        lane=args.lane, expected_work=args.expected_work)
    except (ValueError, KeyError, IndexError, TypeError, OSError) as error:
        parser.exit(2, "PUBLICATION_CLOSURE_REFUSED: " + str(error) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
