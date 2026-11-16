"""Exact authored subtitle restoration, against immutable v218 private source."""
import hashlib,json,re,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent))
from restore_subtitle_v219 import SUBTITLE,PREV,RELEASE,PREV_LOCK,ROUTES,MANIFEST,WORK,patch_source
from compose_v217_private import authored_template
from make_subtitle_v219_admission import make,TARGET
from published_frontend import source_templates
ROOT=Path('/Volumes/DockerDisk/proof-press-v217-work')
class SubtitleSourceV219(unittest.TestCase):
 def test_title_and_subtitle_authorially_addressed(self):
  s,figures,counts=authored_template()
  self.assertIn('data-source-block="the-proof-of-the-page.title"',s)
  self.assertIn('data-source-block="the-proof-of-the-page.subtitle"',s)
  self.assertIn(SUBTITLE,s)
  self.assertEqual(s.count(SUBTITLE),1)
  self.assertEqual((len(figures),counts['paragraphs'],counts['subheadings']),(6,15,7))
 def test_exact_v218_to_v219_delta(self):
  base=ROOT/'v218-projected-input';delta=ROOT/'v219-trial2'
  if not delta.exists():self.skipTest('Live staging fixture unavailable in CI')
  r=json.loads((ROOT/'v219-trial2-receipt.json').read_text())
  self.assertEqual(r['releaseID'],RELEASE);self.assertEqual(r['predecessorReleaseID'],PREV)
  self.assertTrue(r['stageOnly']);self.assertFalse(r['publicReleaseAuthorized']);self.assertFalse(r['productionModified']);self.assertEqual(r['previousSourceLockSHA256'],PREV_LOCK)
  self.assertEqual(len(r['changedFilesSHA256']),8);self.assertEqual(r['addedPaths'],[])
  for name,want in r['changedFilesSHA256'].items():
   self.assertEqual(hashlib.sha256((delta/name).read_bytes()).hexdigest(),want)
  for route in ROUTES:
   before=(base/route).read_text();after=(delta/route).read_text()
   oldnames,old=source_templates(before);newnames,new=source_templates(after)
   self.assertEqual(oldnames,newnames)
   for key in old:
    if key==WORK:self.assertEqual(new[key].count(SUBTITLE),1)
    else:self.assertEqual(old[key],new[key],key)
   self.assertEqual(after.count('data-source-block="the-proof-of-the-page.subtitle"'),1)
  manifest=json.loads((delta/MANIFEST).read_text())
  self.assertEqual(manifest['sourceSubtitle'],SUBTITLE)
  self.assertEqual(manifest['sourceSubtitleSHA256'],hashlib.sha256(SUBTITLE.encode()).hexdigest())
  self.assertEqual(manifest['sourceSubtitleAddress'],'the-proof-of-the-page.subtitle@0')
  self.assertEqual(len(manifest['figures']),6)
  head=(delta/ROUTES[-1]).read_text().split('</head>',1)[0]
  self.assertEqual(head.count('name="description" content="'+SUBTITLE+'"'),1)
  self.assertEqual(head.count('property="og:description" content="'+SUBTITLE+'"'),1)
  self.assertEqual(head.count('name="robots" content="noindex,nofollow"'),1)
 def test_repeated_insert_rejected(self):
  s,_fig,_count=authored_template()
  with self.assertRaisesRegex(ValueError,'already set'):
   patch_source(s,s)
 def test_public_and_invalid_admissions_refused(self):
  r={'schema':'fountain.press.private-v219-subtitle-candidate.v1','status':'PREPARED_NOT_ACTIVATED','stageOnly':True,'publicReleaseAuthorized':False,'productionModified':False,'noOtherWorksAltered':True,'readerEngineUnchanged':True,'addedPaths':[],'changedPaths':['source-lock.json'],'changedFilesSHA256':{'source-lock.json':'0'*64}}
  self.assertEqual(make(r,b'test')['schema'],TARGET)
  for bad in [{'publicReleaseAuthorized':True},{'stageOnly':False},{'productionModified':True},{'addedPaths':['newasset']},{'noOtherWorksAltered':False},{'readerEngineUnchanged':False}]:
   with self.assertRaisesRegex(ValueError,'REFUSED'):
    make({**r,**bad},b'test')
if __name__=='__main__':unittest.main()
