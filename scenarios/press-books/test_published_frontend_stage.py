"""Fail-closed source admission tests for the private existing WLAN Bookshelf.

These use synthetic inputs and do not touch the actual stage service.
"""
import copy
from pathlib import Path
import unittest
from test_published_frontend import fixture
from published_frontend_stage import snapshot_stage


def stage_fixture():
    html,app,catalog,_=fixture()
    app=app.replace('const implementationStories=new Set([]);',"const implementationStories=new Set([]);")
    catalog['status']='private-owner-WLAN-editorial-review'
    catalog['publicReleaseAuthorized']=False
    for book in catalog['books']:
        book['publicReleaseAuthorized']=False;book['stageOnly']=True
        book['publicationState']=None
        book.pop('orderedWorkIDs',None)
    admission={'lane':'private-owner-WLAN-editorial-review','releaseID':'wlan-v215',
            'expectedBookIDs':['essays','first-readings','orange-dot'],
            'expectedCatalogueStatus':'private-owner-WLAN-editorial-review',
            'unlistedSourceWorkRoles':{'essay--past':'archived-public'},
            'requiredEditorialProemCounts':{'essays':1,'first-readings':1},
            'existingPresentation':{'first-readings':{'subtitle':'Reading 01 · First Reading'}}}
    return html,app,catalog,admission

class StageCatalogueTests(unittest.TestCase):
    def test_gate_admission_schema_cannot_be_shadowed_by_receipt_schema(self):
        import json
        from make_stage_guard_admission import make,ADMISSION,EXPECTED_RECEIPT
        guard=(Path(__file__).parent/'serve_press_cms_v216.py').read_bytes()
        original={'schema':EXPECTED_RECEIPT,'status':'PREPARED_NOT_ACTIVATED',
                  'productionModified':False,'publicationLane':'private-owner-WLAN-editorial-review',
                  'changedFilesSHA256':{'a':'f'},'addedPaths':['a'],'changedPaths':[],
                  'releaseID':'example'}
        new=make(original,guard)
        self.assertEqual(new['schema'],ADMISSION)
        self.assertEqual(json.loads((Path(__file__).parent/'wlan-stage-v216-admission.json').read_text())['schema'],ADMISSION)
        with self.assertRaisesRegex(ValueError,'private-stage receipt'):
            make({**original,'status':'ACTIVE'},guard)

    def test_catalogue_stage_status_and_original_contents(self):
        out=snapshot_stage(*stage_fixture())
        self.assertEqual(out['publicationLane'],'private-owner-WLAN-editorial-review')
        self.assertEqual(out['sourcePredecessorReleaseID'],'wlan-v215')
        self.assertEqual([len(b['orderedWorkIDs']) for b in out['books']],[1,2,1])
        self.assertTrue(all(b['publicReleaseAuthorized'] is False and b['stageOnly'] is True and b['stagePreviewAuthorized'] is True for b in out['books']))
        self.assertEqual(out['books'][0]['unlistedSourceWorks'],[{'id':'essay--past','status':'archived-public'}])

    def test_public_flag_in_stage_source_refused(self):
        html,app,catalog,admission=stage_fixture()
        catalog['books'][0]['publicReleaseAuthorized']=True
        with self.assertRaisesRegex(ValueError,'private-stage admission'):
            snapshot_stage(html,app,catalog,admission)
        catalog['books'][0]['publicReleaseAuthorized']=False
        catalog['publicReleaseAuthorized']=True
        with self.assertRaisesRegex(ValueError,'public/private'):
            snapshot_stage(html,app,catalog,admission)

    def test_removed_book_is_refused_even_when_gallery_still_present(self):
        html,app,catalog,admission=stage_fixture()
        catalog['books'].pop()
        with self.assertRaisesRegex(ValueError,'staged book order'):
            snapshot_stage(html,app,catalog,admission)

    def test_unlisted_archived_essay_cannot_be_made_published(self):
        html,app,catalog,admission=stage_fixture()
        app=app.replace("['essay--past']","[]")
        with self.assertRaisesRegex(ValueError,'original archive role drift'):
            snapshot_stage(html,app,catalog,admission)

    def test_source_and_illustration_order_drift_refused(self):
        html,app,catalog,admission=stage_fixture()
        html=html.replace('"solstice-reading-01--chapter"','"unadmitted-source"')
        with self.assertRaises(ValueError):snapshot_stage(html,app,catalog,admission)

    def test_private_proem_source_required(self):
        html,app,catalog,admission=stage_fixture()
        html=html.replace(' data-editorial-role="proem"','')
        with self.assertRaisesRegex(ValueError,'Required stage proem drift'):
            snapshot_stage(html,app,catalog,admission)

if __name__=='__main__':unittest.main()
