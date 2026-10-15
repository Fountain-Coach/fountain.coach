#!/usr/bin/env python3
"""Source-attested, visual-only semantic fixture for Fountain Press Bookshelf.

Builds a separate non-production projection. The admitted source essays, all
production routes, publishing manifests, and original imagery remain unchanged.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "/fixtures/semantic-visual-bookshelf/"
OUT = SITE / BASE.lstrip("/")
PRESS = ROOT.parent.parent / "fountain-press/runtime"
EDITION = SITE / "essays/edition-manifest.json"
FIRST = SITE / "collections/first-readings/collection.json"
LOGO = "/assets/fountain-coach-logo-transparent.png"
BOOKSHELF_CSS = "/assets/linotype/bookshelf.css"
VISUAL_CSS = BASE + "visual.css"
READER_JS = BASE + "visual-reader.js"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned_asset(path: str, expected: str | None = None) -> str:
    assert path.startswith("/") and ".." not in Path(path).parts, path
    resolved = (SITE / path.lstrip("/")).resolve()
    assert resolved.is_relative_to(SITE.resolve()) and resolved.is_file(), path
    hash_value = digest(resolved)
    if expected:
        assert hash_value == expected, (path, "source artwork fingerprint mismatch")
    return hash_value


def bookshelf_renderer():
    assert (PRESS / "bookshelf.py").is_file(), PRESS
    spec = spec_from_file_location("fountain_press_bookshelf_fixture", PRESS / "bookshelf.py")
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.render_bookshelf


def injected_shelf(page: str) -> str:
    anchor = '<link rel="stylesheet" href="' + BOOKSHELF_CSS + '">'
    assert page.count(anchor) == 1
    page = page.replace(anchor, anchor + '\n<link rel="stylesheet" href="' + VISUAL_CSS + '">')
    assert page.count('class="book-app bookshelf-state') == 1
    return page.replace('class="book-app bookshelf-state', 'class="book-app bookshelf-state visual-fixture', 1)


def shelf_book(identity: str, title: str, edition: str, destination: str,
               art: str, revision: str) -> dict:
    owned_asset(art)
    assert destination.startswith(BASE)
    return dict(id=identity, title=title, author="Benedikt Eickhoff",
                edition=edition, reader=destination, cover_image=art,
                source_revision=revision, host="fountain", status="wlan-proof")


def visual_reader(collection: str, entry: dict) -> str:
    assert collection in ("essays", "first-readings")
    parent = BASE + "collections/" + collection + "/#work-" + entry["id"]
    images = entry["images"]
    assert images
    pages = []
    for position, item in enumerate(images, 1):
        image = escape(item["path"], quote=True)
        pages.append(
            '<section class="visual-page" id="plate-' + str(position) + '"' +
            ' data-asset-sha256="' + item["sha256"] + '"' +
            ' role="group" aria-label="Original illustration ' + str(position) +
            ' of ' + str(len(images)) + '"' +
            ("" if position == 1 else " hidden") + ">" +
            '<img src="' + image + '" alt="' + escape(item["alt"], quote=True) +
            '" loading="' + ("eager" if position == 1 else "lazy") +
            '" decoding="async"></section>')
    previous_icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7-7-7 7 7 7"/></svg>'
    next_icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>'
    close_icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; img-src 'self'; script-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
<title>{escape(entry["title"])} — Visual fixture</title>
<link rel="stylesheet" href="{VISUAL_CSS}">
<script type="module" src="{READER_JS}"></script>
</head>
<body class="visual-reader" data-work-id="{escape(entry["id"],quote=True)}"
 data-collection-id="{escape(collection,quote=True)}" data-page-count="{len(images)}"
 data-source-sha256="{entry["sourceSHA256"]}">
<main class="visual-reader-main" aria-label="Visual-only reading of {escape(entry["title"],quote=True)}">
<a class="visual-return" href="{parent}" aria-label="Return to {escape(collection)} collection">{close_icon}</a>
<div class="visual-book-frame" id="visual-book" aria-label="Original visual plates">
{''.join(pages)}
</div>
<nav class="visual-reader-controls" aria-label="Visual page navigation">
<button type="button" id="visual-previous" aria-label="Previous original illustration" disabled>{previous_icon}</button>
<div class="visual-track" role="progressbar" aria-label="Position in visual reading" aria-valuemin="1"
 aria-valuemax="{len(images)}" aria-valuenow="1"><span class="visual-progress-fill"></span></div>
<button type="button" id="visual-next" aria-label="Next original illustration">{next_icon}</button>
</nav>
<p class="visual-assistive" id="visual-status" aria-live="polite"></p>
</main>
</body>
</html>
'''


def main():
    edition = json.loads(EDITION.read_text())
    first = json.loads(FIRST.read_text())
    assert edition["schema"] == "fountain.press.linotype.essay-edition.v2"
    assert first["identity"] == "first-readings"
    assert [x["id"] for x in edition["essays"]] == edition["readingOrder"]
    assert first["workCount"] == 1
    assert first["works"][0]["workId"] in edition["readingOrder"]
    render = bookshelf_renderer()
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("visual.css", "visual-reader.js"):
        source = ROOT / "fixtures/semantic-visual-bookshelf" / name
        assert source.is_file(), source
        shutil.copyfile(source, OUT / name)

    manifest = dict(schema="fountain.press.semantic-visual-bookshelf.fixture.v1",
                    published=False, status="wlan-proof", sourceOwner="Fountain-Coach/fountain.coach",
                    runtimeOwner="Fountain-Coach/fountain-press",
                    scope="visual-only; metadata remains authoritative",
                    sourceManifests=dict(essaysSHA256=digest(EDITION), firstReadingsSHA256=digest(FIRST)),
                    collections=[], works=[])
    arts = {"essays": "/assets/estate-bookshelf/fountain-coach-edition.png",
            "first-readings": "/assets/estate-bookshelf/first-reading-ink.png"}
    collections = {
        "essays": [x["id"] for x in edition["essays"]],
        "first-readings": [first["works"][0]["workId"]]
    }
    by_id = {x["id"]: x for x in edition["essays"]}
    source_work_entries = {}
    for item in edition["essays"]:
        src = SITE / item["sourcePath"]
        assert digest(src) == item["sourceSHA256"], item["id"]
        pages = []
        for image in item["images"]:
            path = "/essays/" + item["id"] + "/" + image["path"]
            pages.append(dict(path=path, sha256=owned_asset(path, image["sha256"]),
                              alt="Original authored illustration from " + item["title"]))
        source_work_entries[item["id"]] = dict(id=item["id"], title=item["title"],
                                              sourceSHA256=item["sourceSHA256"],
                                              sourcePath=item["sourcePath"], images=pages)
    first_work = first["works"][0]
    assert first_work["sourceSHA256"] == source_work_entries[first_work["workId"]]["sourceSHA256"]
    assert first_work["coverArtworkSHA256"] == source_work_entries[first_work["workId"]]["images"][0]["sha256"]

    root_books = []
    for collection_id, work_ids in collections.items():
        collection_path = BASE + "collections/" + collection_id + "/"
        cover = arts[collection_id]
        cover_hash = owned_asset(cover)
        root_books.append(shelf_book(collection_id, collection_id, "Collection",
                                     collection_path, cover,
                                     (digest(EDITION) if collection_id == "essays" else digest(FIRST))))
        manifest["collections"].append(dict(id=collection_id, path=collection_path,
                                             cover=cover, coverSHA256=cover_hash, works=work_ids))
        books = []
        for work_id in work_ids:
            work = source_work_entries[work_id]
            reader = collection_path + "works/" + work_id + "/"
            books.append(shelf_book(work_id, work["title"], "Authored work",
                                    reader, work["images"][0]["path"], work["sourceSHA256"]))
            manifest["works"].append(dict(collection=collection_id, reader=reader, **work))
            destination = OUT / "collections" / collection_id / "works" / work_id
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "index.html").write_text(visual_reader(collection_id, work))
        page = render(title=collection_id, imprint=collection_id, books=books,
                      css_url=BOOKSHELF_CSS, logo_url=LOGO,
                      collection_title=collection_id, collection_parent=BASE,
                      collection_id=collection_id)
        where = OUT / "collections" / collection_id
        where.mkdir(parents=True, exist_ok=True)
        (where / "index.html").write_text(injected_shelf(page))

    root = render(title="Visual Bookshelf fixture", imprint="Fountain Coach",
                  books=root_books, css_url=BOOKSHELF_CSS, logo_url=LOGO)
    (OUT / "index.html").write_text(injected_shelf(root))
    (OUT / "fixture.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print("VISUAL_FIXTURE_BUILT", len(manifest["collections"]), "collections",
          len(manifest["works"]), "source-attested reader projections",
          sum(len(x["images"]) for x in manifest["works"]), "original-image encounters")
    print("ROOT_ROUTE", BASE, "PUBLISHED", manifest["published"])


if __name__ == "__main__":
    main()
