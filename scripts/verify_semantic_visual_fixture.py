#!/usr/bin/env python3
"""Verify reproducible, provenance-bound visual Bookshelf fixture."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "/fixtures/semantic-visual-bookshelf/"
OUT = SITE / BASE.lstrip("/")
WORK = "teatro-an-unfinished-composition"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    assert (OUT / "index.html").is_file(), "build fixture before verification"
    manifest = json.loads((OUT / "fixture.json").read_text())
    assert manifest["schema"] == "fountain.press.semantic-visual-bookshelf.fixture.v1"
    assert manifest["published"] is False and manifest["status"] == "wlan-proof"
    assert manifest["sourceManifests"]["essaysSHA256"] == sha(SITE / "essays/edition-manifest.json")
    assert manifest["sourceManifests"]["firstReadingsSHA256"] == sha(SITE / "collections/first-readings/collection.json")
    assert [x["id"] for x in manifest["collections"]] == ["essays", "first-readings"]
    assert [len(x["works"]) for x in manifest["collections"]] == [3, 1]
    assert len(manifest["works"]) == 4
    edition = json.loads((SITE / "essays/edition-manifest.json").read_text())
    assert [x["id"] for x in edition["essays"]] == manifest["collections"][0]["works"]
    first = json.loads((SITE / "collections/first-readings/collection.json").read_text())
    assert manifest["collections"][1]["works"] == [first["works"][0]["workId"]]
    for collection in manifest["collections"]:
        assert sha(SITE / collection["cover"].lstrip("/")) == collection["coverSHA256"]
        shelf = (SITE / collection["path"].lstrip("/") / "index.html").read_text()
        assert 'data-collection-id="' + collection["id"] + '"' in shelf
        assert 'class="bookshelf-collection-masthead"' in shelf
        assert shelf.count('class="shelf-book"') == len(collection["works"])
        assert shelf.count('class="bookshelf-empty" aria-hidden="true"') == 20
        assert "shelf-cover-name" not in shelf
        assert "<script" not in shelf and "<p>" not in shelf
    root = (OUT / "index.html").read_text()
    assert root.count('class="shelf-book"') == 2
    assert root.count('class="bookshelf-empty" aria-hidden="true"') == 20
    assert 'data-linotype-state="bookshelf"' in root
    assert "shelf-cover-name" not in root
    assert "data-preview-host=" in root
    for work in manifest["works"]:
        source = SITE / work["sourcePath"]
        assert sha(source) == work["sourceSHA256"]
        content = (SITE / work["reader"].lstrip("/") / "index.html").read_text()
        assert f'data-work-id="{work["id"]}"' in content
        assert f'data-collection-id="{work["collection"]}"' in content
        assert f'data-source-sha256="{work["sourceSHA256"]}"' in content
        assert content.count('class="visual-page"') == len(work["images"])
        assert 'class="visual-return"' in content
        assert 'id="visual-next"' in content and 'id="visual-previous"' in content
        assert '<article' not in content and '<h1' not in content
        assert 'essay-prose' not in content and 'linotype-sheet' not in content
        assert 'href="' + BASE + 'collections/' + work["collection"] + '/#work-' + work["id"] + '"' in content
        for image in work["images"]:
            assert sha(SITE / image["path"].lstrip("/")) == image["sha256"]
            assert 'data-asset-sha256="' + image["sha256"] + '"' in content
            assert 'src="' + image["path"] + '"' in content
    paths = {x["reader"] for x in manifest["works"]}
    assert len(paths) == 4, "Two editorial memberships may share the original artwork, not the reader session"
    style = (OUT / "visual.css").read_text()
    assert '.visual-fixture .shelf-cover-name{display:none}' in style
    assert '.visual-book-frame[data-invalid="true"]' in style
    reader_js = (OUT / "visual-reader.js").read_text()
    assert "history.pushState" in reader_js and "popstate" in reader_js
    assert "pointerup" in reader_js and "ArrowRight" in reader_js
    print("SEMANTIC_VISUAL_FIXTURE_PASS", len(manifest["collections"]),
          "collections", len(manifest["works"]), "reader projections",
          sum(len(w["images"]) for w in manifest["works"]), "original artwork encounters")


if __name__ == "__main__":
    check()
