#!/usr/bin/env python3
"""Local contract tests: no production host, no credentials, no network."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import activate_static_essay as remote
import publish_essays as local


class PublishingContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.root = self.folder / "fountain.coach"
        self.root.mkdir()
        (self.root / "releases").mkdir()
        self.predecessor = self.root / "releases/static-previous"
        for rel in ("essays/index.html",
                    "essays/to-read-is-not-to-remember/index.html",
                    "essays/semantic-compilation-the-archive-is-not-the-edition/index.html"):
            p = self.predecessor / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("unchanged "+rel)
        self.old_collection = (
            b'<article data-essay-route="/essays/to-read-is-not-to-remember/"></article>'
            b'<article data-essay-route="/essays/semantic-compilation-the-archive-is-not-the-edition/"></article>'
            b'<article data-essay-route="/essays/teatro-an-unfinished-composition/"></article>'
            b'<article data-essay-route="/essays/reframe-and-the-business-value-of-the-estate/"></article>'
        )
        (self.predecessor / "essays/index.html").write_bytes(self.old_collection)
        from project_home_essay import baseline
        (self.predecessor / "index.html").write_bytes(baseline())
        (self.root / "current").symlink_to("releases/static-previous")
        self.caddy = self.folder / "Caddyfile"
        self.caddy.write_text(
            "fountain.coach {\n @fountainNewEssay {\n  host fountain.coach\n"
            "  path / /essays/ /essays/to-read-is-not-to-remember/*\n }\n"
            " handle @fountainNewEssay {\n  root * /srv/fountain-static-publications/fountain.coach/current\n"
            "  file_server\n }\n}\n"
        )
        self.files = local.source_files()
        self.original_index = self.files[local.COLLECTION]
        # Generate a strict synthetic 4-card predecessor plus one accepted new card;
        # the local site is also checked separately in the real read-only preflight.
        import re
        local_card = re.search(
            rb'<article class="essay-gallery-card" data-essay-route="/essays/the-composable-book/".*?</article>',
            self.original_index, re.DOTALL,
        )
        self.assertIsNotNone(local_card)
        self.files[local.COLLECTION] = local_card.group() + self.old_collection
        self.archive, self.manifest = local.package(
            "deadbeef" * 5, "releases/static-previous",
            self.caddy.read_bytes(), self.old_collection, self.files,
        )
        self.path = self.folder / "archive.tar.gz"
        self.path.write_bytes(self.archive)
        self.reloads = []
        self.validations = []

    def do_activate(self, **overrides):
        return remote.activate(
            self.path, local.sha(self.archive), root=self.root, config=self.caddy,
            validate=lambda path: self.validations.append(path.read_text()),
            reload=lambda: self.reloads.append("reloaded"),
            **overrides
        )

    def test_idempotent_publish_verifies_live_bytes_without_host_mutation(self):
        from unittest.mock import patch
        mapping = {"/" if key == "index.html" else "/" + key: value for key, value in self.files.items()}
        with patch.object(local, "https", side_effect=lambda path: mapping[path]):
            result = local.already_published(
                self.files, self.files[local.COLLECTION], self.folder / "no-receipt.json"
            )
        self.assertEqual(result["state"], "ALREADY_PUBLISHED_HTTPS_VERIFIED")
        self.assertTrue(result["noHostMutation"])
        self.assertEqual(len(result["verifiedSHA256"]), 9)

    def test_idempotent_publish_refuses_public_byte_drift(self):
        from unittest.mock import patch
        mapping = {"/" if key == "index.html" else "/" + key: value for key, value in self.files.items()}
        asset = "/essays/the-composable-book/assets/01-book-spread.svg"
        mapping[asset] = b"modified"
        with patch.object(local, "https", side_effect=lambda path: mapping[path]):
            with self.assertRaisesRegex(local.PublicationStopped, "published asset differs"):
                local.already_published(
                    self.files, self.files[local.COLLECTION], self.folder / "no-receipt.json"
                )

    def test_revised_essay_is_not_mistaken_for_duplicate_publish(self):
        from unittest.mock import patch
        mapping = {"/" if key == "index.html" else "/" + key: value for key, value in self.files.items()}
        mapping["/"] = b"previous homepage"
        with patch.object(local, "https", side_effect=lambda path: mapping[path]):
            self.assertIsNone(local.already_published(
                self.files, self.files[local.COLLECTION], self.folder / "no-receipt.json"
            ))

    def test_identical_reproducible_artifact(self):
        data, manifest = local.package(
            "deadbeef" * 5, "releases/static-previous",
            self.caddy.read_bytes(), self.old_collection, self.files
        )
        self.assertEqual(self.archive, data)
        self.assertEqual(self.manifest, manifest)
        self.assertEqual(len(manifest["files"]), 9)

    def test_reject_changed_sibling_gallery(self):
        with self.assertRaises(local.PublicationStopped):
            local.check_collection(
                self.old_collection + b'<article data-essay-route="/essays/the-composable-book/"></article>',
                self.old_collection.replace(b"to-read-is-not-to-remember", b"new-overwritten")
            )
        # Unchanged, already published collection is accepted for a later article update.
        local.check_collection(self.old_collection, self.old_collection)

    def test_immutable_activation_and_rollback(self):
        receipt = self.do_activate()
        self.assertEqual(receipt["state"], "ACTIVATED_PENDING_PUBLIC_WITNESS")
        self.assertEqual(len(self.reloads), 1)
        self.assertEqual(len(self.validations), 2)
        current = (self.root / "current").resolve()
        self.assertEqual((current / "essays/to-read-is-not-to-remember/index.html").read_text(),
                         (self.predecessor / "essays/to-read-is-not-to-remember/index.html").read_text())
        self.assertEqual((current / "essays/index.html").read_bytes(), self.files[local.COLLECTION])
        self.assertEqual((current / "index.html").read_bytes(), self.files["index.html"])
        self.assertEqual((current / "essays/the-composable-book/index.html").read_bytes(),
                         self.files[local.ARTICLE])
        self.assertIn("/essays/the-composable-book/*", self.caddy.read_text())
        with self.assertRaises(remote.Refused):
            self.do_activate()
        result = remote.rollback(receipt["release"], root=self.root, config=self.caddy,
                                 reload=lambda: self.reloads.append("rolled back"))
        self.assertEqual(result["state"], "ROLLED_BACK")
        self.assertEqual(os.readlink(self.root / "current"), "releases/static-previous")
        self.assertNotIn("/essays/the-composable-book/*", self.caddy.read_text())
        self.assertEqual(len(self.reloads), 2)

    def test_refuse_unrelated_homepage_mutation(self):
        from project_home_essay import baseline, project_home, check_home
        original = baseline()
        candidate = project_home(original)
        check_home(candidate, original)
        with self.assertRaisesRegex(ValueError, "not exactly the admitted essay card"):
            check_home(candidate.replace(b"Fountain Coach", b"Other Company", 1), original)

    def test_refuse_tampered_archive_before_effect(self):
        with self.assertRaises(remote.Refused):
            remote.activate(self.path, "0"*64, root=self.root, config=self.caddy)
        self.assertEqual(os.readlink(self.root / "current"), "releases/static-previous")

    def test_refuse_stale_predecessor(self):
        (self.predecessor / "essays/index.html").write_text("outside editorial change")
        with self.assertRaisesRegex(remote.Refused, "live essays collection has changed"):
            self.do_activate()
        self.assertEqual(os.readlink(self.root / "current"), "releases/static-previous")

    def test_refuse_caddy_drift(self):
        self.caddy.write_text(self.caddy.read_text() + "# unrelated edit\n")
        with self.assertRaisesRegex(remote.Refused, "Caddyfile changed"):
            self.do_activate()
        self.assertEqual(os.readlink(self.root / "current"), "releases/static-previous")

    def test_rollback_on_caddy_reload_failure(self):
        count = []
        def reload():
            count.append(1)
            if len(count) == 1:
                raise RuntimeError("simulated Caddy failure")
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            remote.activate(self.path, local.sha(self.archive), root=self.root,
                            config=self.caddy, validate=lambda _: None, reload=reload)
        self.assertEqual(os.readlink(self.root / "current"), "releases/static-previous")
        self.assertNotIn("/essays/the-composable-book/*", self.caddy.read_text())
        self.assertEqual(len(count), 2)

    def test_changed_caddy_refuses_stale_rollback(self):
        receipt = self.do_activate()
        self.caddy.write_text(self.caddy.read_text() + "# another editor\n")
        with self.assertRaisesRegex(remote.Refused, "Caddy changed since activation"):
            remote.rollback(receipt["release"], root=self.root, config=self.caddy,
                            reload=lambda: None)
        self.assertEqual(os.readlink(self.root / "current"), "releases/"+receipt["release"])

    def test_read_archive_rejects_unrelated_route(self):
        import gzip, io, tarfile
        records = {}
        with tarfile.open(fileobj=io.BytesIO(self.archive), mode="r:gz") as z:
            for m in z:
                records[m.name] = z.extractfile(m).read()
        records["other-domain/index.html"] = b"not admitted"
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode="w") as t:
            for name, data in records.items():
                item = tarfile.TarInfo(name)
                item.size=len(data)
                t.addfile(item,io.BytesIO(data))
        altered=gzip.compress(raw.getvalue())
        path=self.folder/"invalid.tar.gz"
        path.write_bytes(altered)
        with self.assertRaises(remote.Refused):
            remote.read_archive(path, local.sha(altered))


if __name__ == "__main__":
    unittest.main(verbosity=2)
