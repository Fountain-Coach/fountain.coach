"""Adversarial source-owned acceptance for mandatory Press publication closure.

Synthetic fixtures: no network, stage mutation, browser or public release.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from publication_closure import verify


def sha(data):
    return hashlib.sha256(data).hexdigest()


def make_release(root):
    def put(rel, value):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value if isinstance(value, bytes) else value.encode())

    app = b"const reader='existing Linotype';"
    engine = b"const press='existing page compositor';"
    appurl = "/estate/assets/linotype/reading-first-app." + sha(app) + ".js"
    engineurl = "/estate/assets/linotype/reading-first-press-engine." + sha(engine) + ".js"
    put(appurl.lstrip("/"), app)
    put(engineurl.lstrip("/"), engine)
    image = b"source-owned social image"
    image_path = "/estate/assets/social/books/essays-first.jpg"
    put(image_path.lstrip("/"), image)

    work = "essay--one"
    edition = "fountain.press.publication-snapshot.v1"
    gallery = {"schema": "fountain.press.bookshelf-gallery.v1", "collections": {"essays": [{"id": work}]}}
    snapshot = {
        "schema": edition,
        "publicationLane": "private-owner-WLAN-editorial-review",
        "books": [{
            "id": "essays", "stageOnly": True,
            "publicReleaseAuthorized": False,
            "orderedWorkIDs": [work], "illustratedWorkIDs": [work],
            "unlistedSourceWorks": []
        }]
    }
    gallery_html = '<script type="application/json" id="reader-gallery-data">' + json.dumps(gallery) + "</script>"
    snapshot_html = '<script type="application/json" id="reader-publication-data">' + json.dumps(snapshot) + "</script>"
    chapter = '<template data-reader-volume="essay--one"><h2>Original essay</h2></template>'
    scripts = '<script src="' + appurl + '"></script><script src="' + engineurl + '"></script>'
    main = "<html><head></head><body>" + chapter + gallery_html + snapshot_html + scripts + "</body></html>"
    canonical = "https://fountain.coach/estate/books/essays/"
    ld = {"@type": "Book", "hasPart": [{"identifier": work}]}
    head = ('<head><link rel="canonical" href="' + canonical +
            '"><meta property="og:image" content="' + canonical + 'share.jpg">' +
            '<meta name="twitter:image" content="' + canonical + 'share.jpg">' +
            '<script type="application/ld+json">' + json.dumps(ld) + '</script></head>')
    direct = main.replace("<head></head>", head).replace("<body>", '<body data-initial-volume="essays">')
    catalog = {
        "books": [{"id": "essays", "orderedWorkIDs": [work],
                   "illustratedWorkIDs": [work],
                   "firstIllustratedChapterID": work,
                   "publicReleaseAuthorized": False, "stageOnly": True,
                   "canonicalURL": canonical,
                   "directURLPath": "/estate/books/essays/",
                   "socialImagePath": image_path,
                   "socialImageSHA256": sha(image)}],
        "stagedCollectionOrder": ["essays"],
        "publicationSnapshotSchema": edition,
        "stageOnly": True, "publicReleaseAuthorized": False
    }
    put("estate/index.html", main)
    put("estate/read/library/index.html", main)
    put("estate/books/essays/index.html", direct)
    put("estate/essays/index.html", direct)
    put("estate/books/catalog.json", json.dumps(catalog))
    return main, direct, catalog


class MandatoryPublicationClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.main, self.direct, self.catalog = make_release(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_source_bound_private_essay_and_all_entrances_pass(self):
        result = verify(self.root, lane="staging", expected_work="essay--one")
        self.assertEqual(result["status"], "PUBLICATION_CLOSURE_PASSED_BYTES_ONLY")
        self.assertEqual(result["books"][0]["works"], 1)

    def test_stale_legacy_essay_index_fails_even_with_direct_work(self):
        (self.root / "estate/essays/index.html").write_text("<title>Old essays</title>")
        with self.assertRaisesRegex(ValueError, "STALE_ESSAYS_ENTRANCE"):
            verify(self.root, expected_work="essay--one")

    def test_unadmitted_essay_refused(self):
        with self.assertRaisesRegex(ValueError, "missing from admitted Essays"):
            verify(self.root, expected_work="essay--unpublished")

    def test_old_library_reader_refused(self):
        (self.root / "estate/read/library/index.html").write_text("<title>Old Reader</title>")
        with self.assertRaisesRegex(ValueError, "Legacy library entrance"):
            verify(self.root)

    def test_catalogue_work_drift_refused(self):
        self.catalog["books"][0]["orderedWorkIDs"].append("essay--not-source")
        (self.root / "estate/books/catalog.json").write_text(json.dumps(self.catalog))
        with self.assertRaisesRegex(ValueError, "work order"):
            verify(self.root)

    def test_public_authorization_in_private_stage_refused(self):
        self.catalog["publicReleaseAuthorized"] = True
        (self.root / "estate/books/catalog.json").write_text(json.dumps(self.catalog))
        with self.assertRaisesRegex(ValueError, "incorrectly claims public"):
            verify(self.root)

    def test_direct_book_metadata_and_reader_must_match(self):
        (self.root / "estate/books/essays/index.html").write_text(
            self.direct.replace('"hasPart": [{"identifier": "essay--one"}]', '"hasPart": []'))
        with self.assertRaisesRegex(ValueError, "JSON-LD membership"):
            verify(self.root)

    def test_social_derivative_must_match_source_digest(self):
        (self.root / "estate/assets/social/books/essays-first.jpg").write_bytes(b"other")
        with self.assertRaisesRegex(ValueError, "social derivative"):
            verify(self.root)

    def test_overlay_only_replaces_legacy_index_and_keeps_predecessor_immutable(self):
        with tempfile.TemporaryDirectory() as dest:
            overlay = Path(dest)
            path = overlay / "estate/essays/index.html"
            path.parent.mkdir(parents=True)
            path.write_text(self.direct)
            (self.root / "estate/essays/index.html").write_text("obsolete")
            accepted = verify(overlay, predecessor=self.root, expected_work="essay--one")
            self.assertEqual(accepted["books"][0]["id"], "essays")
            self.assertEqual((self.root / "estate/essays/index.html").read_text(), "obsolete")


if __name__ == "__main__":
    unittest.main()
