"""Offline positive and adversarial checks for the real Press CMS-like frontend.

No network, no publisher or test proxy. The full-size source predecessor is
separately checked through the source-pinned compiler and WebKit acceptance.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import published_frontend as pf


def fixture():
    work={
      'essay--current':'<h2>Current</h2><p data-editorial-role="proem" data-source-block="s1">Summary</p>',
      'essay--past':'<h2>Past</h2>',
      'solstice-reading-01--intro':'<h2>Preface</h2>',
      'solstice-reading-01--chapter':'<h2>Chapter</h2><p data-editorial-role="proem" data-source-block="s2">Summary</p>',
      'orange-dot--one':'<h2>Orange</h2>',
    }
    gallery={
      'essays':[{'id':'essay--current'}],
      'first-readings':[{'id':'solstice-reading-01--chapter'}],
      'orange-dot':[{'id':'orange-dot--one'}],
    }
    html='<html><body>'+''.join('<template data-reader-volume="'+k+'">'+v+'</template>' for k,v in work.items())+'<script type="application/json" id="reader-gallery-data">'+json.dumps({'schema':'fountain.press.bookshelf-gallery.v1','collections':gallery})+'</script></body></html>'
    app="const implementationStories=new Set([]);\nconst archivedEssays=new Set(['essay--past']);"
    books=[]
    for identifier in gallery:
        books.append({'id':identifier,'title':identifier,'canonicalURL':'https://fountain.coach/estate/books/'+identifier+'/',
            'directURLPath':'/estate/books/'+identifier+'/','publicationState':'public-production',
            'publicReleaseAuthorized':True,'stageOnly':False,'sourceRevision':'source'})
    books[0]['orderedWorkIDs']=['essay--current']
    catalog={'books':books,'sourceOwner':'Fountain-Coach/fountain.coach','sourceGitRevision':'abc','currentReleaseID':'signed-release'}
    admission={'publicReleaseID':'signed-release','sourceUnlistedWorkRoles':{'essay--past':'archived-public'},
               'existingPresentation':{'first-readings':{'subtitle':'Reading'}},
               'requiredEditorialProemCounts':{'essays':1,'first-readings':1}}
    return html,app,catalog,admission

class TestPublishedFrontend(unittest.TestCase):
    def test_three_active_books_and_archive_preserved(self):
        snapshot=pf.build_snapshot(*fixture())
        self.assertEqual([b['id'] for b in snapshot['books']],['essays','first-readings','orange-dot'])
        self.assertEqual([len(b['orderedWorkIDs']) for b in snapshot['books']],[1,2,1])
        self.assertEqual(snapshot['books'][0]['unlistedSourceWorks'],[{'id':'essay--past','status':'archived-public'}])
        self.assertEqual(snapshot['books'][1]['illustratedWorkIDs'],['solstice-reading-01--chapter'])
        self.assertEqual(len(snapshot['requiredEditorialProemWorkIDs']),2)

    def test_missing_published_book_is_refused(self):
        html,app,catalog,admission=fixture()
        catalog['books'].pop()
        with self.assertRaisesRegex(ValueError,'Publication book/gallery identities disagree'):
            pf.build_snapshot(html,app,catalog,admission)

    def test_archive_cannot_be_silently_promoted(self):
        html,app,catalog,admission=fixture()
        catalog['books'][0]['orderedWorkIDs'].append('essay--past')
        with self.assertRaisesRegex(ValueError,'Unexpected omitted original essay'):
            pf.build_snapshot(html,app,catalog,admission)

    def test_stale_or_out_of_order_gallery_is_refused(self):
        html,app,catalog,admission=fixture()
        catalog['books'][0]['orderedWorkIDs']=['essay--past','essay--current']
        with self.assertRaises(ValueError):pf.build_snapshot(html,app,catalog,admission)
        html=html.replace('"orange-dot--one"','"nonexistent-orange"')
        with self.assertRaises(ValueError):pf.build_snapshot(html,app,fixture()[2],admission)

    def test_private_book_cannot_appear_in_public_snapshot(self):
        html,app,catalog,admission=fixture()
        catalog['books'][2]['publicReleaseAuthorized']=False
        catalog['books'][2]['publicationState']='private-stage'
        with self.assertRaisesRegex(ValueError,'private/unreleased book in public source'):
            pf.build_snapshot(html,app,catalog,admission)

    def test_source_template_nesting_is_refused(self):
        html,app,catalog,admission=fixture()
        html=html.replace('<template data-reader-volume="orange-dot--one">',
             '<template data-reader-volume="library"><template data-reader-volume="orange-dot--one">').replace('</template></body>', '</template></template></body>')
        with self.assertRaisesRegex(ValueError,'source template nesting'):
            pf.build_snapshot(html,app,catalog,admission)

    def test_proem_loss_refused(self):
        html,app,catalog,admission=fixture()
        html=html.replace(' data-editorial-role="proem"','')
        with self.assertRaisesRegex(ValueError,'Editorial proem source drift'):
            pf.build_snapshot(html,app,catalog,admission)

    def test_sha_drift_and_untracked_paths_are_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'book.json').write_bytes(b'original')
            admission={'sourceDigestSHA256':{'book.json':hashlib.sha256(b'original').hexdigest()}}
            self.assertEqual(pf.read_pinned(root,'book.json',admission),b'original')
            (root/'book.json').write_bytes(b'mutated')
            with self.assertRaisesRegex(ValueError,'source SHA drift'):
                pf.read_pinned(root,'book.json',admission)
            with self.assertRaises(ValueError):pf.read_pinned(root,'../secret',admission)

    def test_public_reader_source_fragment_and_navigation_order_are_independent_of_fixed_book_ids(self):
        fragment=(Path(__file__).parent/'reader-publication-state.js.inc').read_text()
        for required in ('publication.books', 'collectionOrder=books.map','Object.fromEntries',
                         'book.orderedWorkIDs','book.illustratedWorkIDs','publicReleaseAuthorized','source order'):
            self.assertIn(required,fragment)
        for bad in ("const collectionOrder=['essays','first-readings'",'const essaySequence=', 'const orangeSequence='):
            self.assertNotIn(bad,fragment)
        compiled=Path(__file__).parent/'published_frontend.py'
        self.assertIn('reader-shelf-leaf-navigation',compiled.read_text())
        self.assertIn('data-reader-volume',compiled.read_text())
        self.assertIn('estate/read/library/index.html',compiled.read_text())

if __name__=='__main__':unittest.main()
