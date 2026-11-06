"""Exact source, existing Reader and authentic Csound/SatzfunkPlayer A/B proof."""
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest

HERE=pathlib.Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("sound_craft",HERE/"build_stage_proof_v2.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
BASE=pathlib.Path("/tmp/press-governance-163/stage")
sha=lambda b:hashlib.sha256(b).hexdigest()

class SoundCraftProof(unittest.TestCase):
    def test_original_reader_and_exact_editorial_replacement(self):
        old=M.original_template()
        new,n=M.essay_template(M.REVISED.read_text())
        self.assertEqual(n,15)
        with tempfile.TemporaryDirectory() as folder:
            r=M.build(BASE/"index.html",BASE/"reading-first-app.js",folder)
            out=pathlib.Path(folder)
            previous=(BASE/"index.html").read_text()
            after=(out/"estate/index.html").read_text()
            self.assertEqual(after.replace(new,old,1),previous)
            self.assertIn("soundCraftPromise", (out/"estate/assets/linotype/reading-first-app.js").read_text())
            self.assertIn("soundEditionPromise", (out/"estate/assets/linotype/reading-first-app.js").read_text())
            self.assertEqual(sha((BASE/"reading-first-app.js").read_bytes()),r["previousAppSHA256"])
            self.assertTrue(r["noOtherBookModified"] if "noOtherBookModified" in r else r["otherVolumesUnmodified"])
            self.assertFalse(r["newPlayerOrReader"])
            self.assertFalse(r["publicRelease"])

    def test_two_real_csound_patches_in_existing_player(self):
        new,n=M.essay_template(M.REVISED.read_text())
        self.assertEqual(new.count("<satzfunk-player compact"),2)
        self.assertEqual(new.count('data-press-media="satzfunk-csound-kino-a-b"'),1)
        self.assertIn('data-keep-with-anchor="previous"',new)
        self.assertNotIn("sing-plain-compare",new)
        self.assertNotIn("sing-expressive-compare",new)
        self.assertEqual(M.REVISED.read_text().count("## "),0)
        self.assertTrue(M.REVISED.read_text().strip().endswith(
           "It is ready when the work can answer for it.**"))
        media=M.media_source()
        self.assertEqual(len(media["files"]),2)
        self.assertAlmostEqual(media["files"][0]["renderFacts"]["rmsLinear"],
                               media["files"][1]["renderFacts"]["rmsLinear"],delta=0.003)
        edition=M.stage_edition(media)
        self.assertEqual(edition["schema"],"satzfunk.recorded-essay-rehearsal.v1")
        self.assertEqual(edition["scoreSHA256"],media["sourceScoreSHA256"])
        self.assertEqual(len(edition["tracks"]),2)
        self.assertTrue(all(t["privateRehearsalAuthorized"] and
                            not t["publicReleaseAuthorized"] and
                            t["sourceSHA256"]==edition["scoreSHA256"] for t in edition["tracks"]))

    def test_bytes_and_source_custody(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt=M.build(BASE/"index.html",BASE/"reading-first-app.js",folder)
            out=pathlib.Path(folder)
            self.assertEqual(len(receipt["changedFiles"]),8)
            for name,digest in receipt["changedFiles"].items():
                self.assertEqual(sha((out/name).read_bytes()),digest,name)
            self.assertEqual(len(list((out/M.MOUNT).glob("*.csd"))),2)
            self.assertEqual(len(list((out/M.MOUNT).glob("*.m4a"))),2)
            self.assertFalse((out/"estate/assets/satzfunk").exists(),"A duplicate Player must never be bundled")
            self.assertFalse(receipt["nativeScenarioAdmission"])
            self.assertIn("SatzfunkMediaElement",receipt["player"])
            self.assertEqual(receipt["expectedPreviousRelease"],
                             "shared-shell-20261106-v164-governance-social-b7b1dee")

    def test_guard_refuses_stale_reader(self):
        with tempfile.TemporaryDirectory() as folder:
            idx=pathlib.Path(folder)/"index.html"
            idx.write_bytes((BASE/"index.html").read_bytes()+b" ")
            with self.assertRaises(ValueError):
                M.build(idx,BASE/"reading-first-app.js",pathlib.Path(folder)/"output")

if __name__=="__main__":unittest.main()
