"""Private restoration of exact published original Kino plates only."""
from pathlib import Path
import hashlib
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from reconcile_kino_v218 import ORIGINALS,PREVIOUS_SHA,PREDECESSOR,RELEASE,verify_original_png,build
from make_kino_v218_admission import DEST,make

class KinoV218ProofTests(unittest.TestCase):
    def test_source_is_exact_two_original_public_pngs(self):
        self.assertEqual(len(ORIGINALS),2)
        self.assertEqual(PREVIOUS_SHA,'570f3a17e57211fdbce4f2fc22f015a1143190fc492886f662744c48f04d765e')
        self.assertEqual(PREDECESSOR,'shared-shell-20261116-v217-proof-of-the-page-heading-proof')
        self.assertTrue(RELEASE.startswith('shared-shell-20261116-v218-'))
        with self.assertRaisesRegex(ValueError,'non-original'):
            verify_original_png('estate/instruments/kino/plates/v156.png',b'PNG screenshot replacement')
        with self.assertRaisesRegex(ValueError,'non-original'):
            verify_original_png('estate/instruments/kino/plates/unknown.png',b'')

    def test_candidate_only_private_stage_and_separate_admission_schema(self):
        doc={'schema':'fountain.press.private-kino-v218-candidate.v1','status':'PREPARED_NOT_ACTIVATED',
            'stageOnly':True,'publicReleaseAuthorized':False,'productionModified':False,
            'addedPaths':sorted(ORIGINALS),'changedPaths':['source-lock.json'],
            'changedFilesSHA256':{**ORIGINALS,'source-lock.json':'0'*64},
            'releaseID':RELEASE,'predecessorReleaseID':PREDECESSOR}
        result=make(doc,b'guard-stub')
        self.assertEqual(result['schema'],DEST)
        self.assertEqual(result['guardSHA256'],hashlib.sha256(b'guard-stub').hexdigest())
        for bad in ({'status':'ACTIVE'}, {'publicReleaseAuthorized':True},
                    {'productionModified':True}, {'addedPaths':[]}, {'schema':'not-candidate'}):
            with self.assertRaisesRegex(ValueError,'invalid private'):
                make({**doc,**bad},b'guard-stub')

    def test_guard_inherits_every_prior_release_and_forbids_unlisted_mutations(self):
        script=(HERE/'serve_kino_v218.py').read_text()
        for text in ('self.inherited=previous.ProofPressV217Gate',
                     'if diffs!={\'source-lock.json\'}:',
                     'self.inherited.check(raw_url)',
                     'prior_paths-current_paths',
                     'current_paths-prior_paths!=set(ORIGINALS)',
                     'originalPublicSourceURLs',
                     "tag.get('publicReleaseAuthorized') is not False",
                     'KinoV218Gate'):
            self.assertIn(text,script)
        self.assertNotIn('allow_all',script.lower())

    def test_reproducible_true_source_when_available_not_required_ci(self):
        path=Path('/Volumes/DockerDisk/proof-press-v217-work/kino-public-originals')
        if not path.exists():self.skipTest('Live private fixture not available in CI')
        for rel,want in ORIGINALS.items():
            raw=(path/Path(rel).name).read_bytes()
            self.assertEqual(verify_original_png(rel,raw),want)

if __name__=='__main__':unittest.main()
