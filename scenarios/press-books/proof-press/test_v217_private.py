"""Source-based private v217 stage / typography regression, no publication effect."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent))
from compose_v217_private import authored_template,patch_engine,OLD_ENGINE,PREVIOUS_PIN,PROOF_SOURCE,WORK
from make_v217_admission import make,DEST

BASE=Path('/Volumes/DockerDisk/proof-press-v217-work/input')
CANDIDATE=Path('/Volumes/DockerDisk/proof-press-v217-work/candidate-02')
RECEIPT=Path('/Volumes/DockerDisk/proof-press-v217-work/candidate-receipt-02.json')

def sha(raw):return hashlib.sha256(raw).hexdigest()

class PrivateProofPressV217SourceTests(unittest.TestCase):
    def test_authorial_source_and_six_plate_geometry_present(self):
        template,plates,count=authored_template()
        self.assertEqual(count,{'paragraphs':15,'subheadings':7,'figures':6})
        self.assertEqual(len(plates),6)
        self.assertEqual(len(set(p['id'] for p in plates)),6)
        self.assertEqual(template.count('data-source-block="the-proof-of-the-page.plate-'),6)
        self.assertEqual(template.count('<figcaption>'),6)
        self.assertEqual(template.count('data-source-from="0"'),22)
        self.assertIn('data-source-work-sha256="'+PROOF_SOURCE+'"',template)
        self.assertIn('data-editorial-role="proem"',template)
        self.assertNotIn('public-production',template)
        for plate in plates:
            self.assertEqual(sha((ROOT/'site/essays/the-proof-of-the-page'/plate['sourcePath']).read_bytes()),plate['sha256'])
            self.assertTrue(plate['afterParagraph']>=1)

    def test_exact_engine_change_restores_measured_heading_keep_for_single_pages(self):
        source=(BASE/OLD_ENGINE).read_bytes()
        changed=patch_engine(source)
        self.assertNotEqual(sha(source),sha(changed))
        old=source.decode();new=changed.decode()
        self.assertEqual(new.count('if(this.pageFrame&&\n           element.matches(".frame-subheading")'),1)
        self.assertEqual(old.count('if(this.pageFrame&&this.css.spread&&\n           element.matches(".frame-subheading")'),1)
        self.assertEqual(len(new),len(old)-len('this.css.spread&&'))
        self.assertEqual(new.replace('if(this.pageFrame&&\n           element.matches(".frame-subheading")','if(this.pageFrame&&this.css.spread&&\n           element.matches(".frame-subheading")'),old)
        with self.assertRaisesRegex(ValueError,'drift'):
            patch_engine(source+b'changed')

    def test_stage_unchanged_previous_works_and_correct_all_book_projections(self):
        from published_frontend import source_templates
        report=json.loads(RECEIPT.read_text())
        self.assertEqual(report['status'],'PREPARED_NOT_ACTIVATED')
        self.assertTrue(report['stageOnly']);self.assertFalse(report['publicReleaseAuthorized']);self.assertFalse(report['productionModified'])
        self.assertEqual(report['expectedBooks'],{'essays':11,'first-readings':32,'orange-dot':23})
        self.assertEqual(report['expectedIllustrations'],{'essays':11,'first-readings':30,'orange-dot':23})
        self.assertEqual(report['predecessorSourceLockSHA256'],PREVIOUS_PIN)
        self.assertEqual(set(report['changedFilesSHA256']),set(report['addedPaths'])|set(report['changedPaths']))
        for rel,digest in report['changedFilesSHA256'].items():self.assertEqual(sha((CANDIDATE/rel).read_bytes()),digest)
        for rel in ['estate/index.html','estate/read/library/index.html','estate/books/essays/index.html',
                    'estate/books/first-readings/index.html','estate/books/orange-dot/index.html']:
            before=(BASE/rel).read_text();after=(CANDIDATE/rel).read_text()
            oldnames,oldblocks=source_templates(before);newnames,newblocks=source_templates(after)
            self.assertEqual(set(newnames)-set(oldnames),{WORK})
            self.assertEqual(newnames.index(WORK),oldnames.index('essay--a-sound-must-earn-its-place')+1)
            for id in oldnames:self.assertEqual(oldblocks[id],newblocks[id],id)
            self.assertEqual(after.count('data-reader-volume="'+WORK+'"'),1)
            self.assertIn('source-owned-explanatory-proof-plate',after)
        direct=(CANDIDATE/'estate/read'/WORK/'index.html').read_text()
        head=direct.split('</head>',1)[0]
        for val in ['og:image','og:url','og:title','og:type']:
            self.assertEqual(len(re.findall('property="'+val+'"',head)),1)
        self.assertEqual(head.count('name="robots" content="noindex,nofollow"'),1)
        self.assertEqual(head.count('<script type="application/ld+json">'),1)
        self.assertIn('data-initial-volume="'+WORK+'"',direct)
        books=json.loads((CANDIDATE/'estate/books/catalog.json').read_text())['books']
        essays=next(b for b in books if b['id']=='essays')
        self.assertEqual(essays['orderedWorkIDs'][-1],WORK)
        self.assertEqual(essays['illustratedWorkIDs'][-1],WORK)
        self.assertTrue(all(x['stageOnly'] and not x['publicReleaseAuthorized'] for x in books))
        manifest=json.loads((CANDIDATE/'estate/read'/WORK/'edition-manifest.json').read_text())
        self.assertEqual(manifest['sourceSHA256'],PROOF_SOURCE)
        self.assertEqual(len(manifest['figures']),6)
        self.assertEqual(manifest['socialImageDimensions'],[1200,630])

    def test_gate_admission_schema_cannot_be_shadowed_by_candidate_receipt(self):
        receipt=json.loads(RECEIPT.read_text())
        guard=(HERE/'serve_v217_private.py').read_bytes()
        admitted=make(receipt,guard)
        self.assertEqual(admitted['schema'],DEST)
        self.assertEqual(admitted['guardSHA256'],sha(guard))
        with self.assertRaisesRegex(ValueError,'unadmitted'):
            make({**receipt,'publicReleaseAuthorized':True},guard)
        with self.assertRaisesRegex(ValueError,'inventory'):
            make({**receipt,'addedPaths':[]},guard)

if __name__=='__main__':unittest.main()
