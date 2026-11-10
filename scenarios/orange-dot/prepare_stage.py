#!/usr/bin/env python3
"""Produce exact source admission for the current canonical owner-WLAN stage.

Does not touch a server; activation remains an explicit, separately guarded
EstatePublisher/owner-WLAN operation with immutable predecessor.
"""
from pathlib import Path
from hashlib import sha256
import json,pprint
R=Path(__file__).parent
OUT=Path('/tmp/orange-dot-stage-delta-20261110')
SOURCE=json.loads((R/'selection.json').read_text())
EDITION=json.loads((OUT/'estate/collections/orange-dot/edition.json').read_text())
DELTA=json.loads((OUT/'orange-dot-delta-receipt.json').read_text())
OLD='shared-shell-20261110-v184-playable-breach-b9d4c88'
NEW='shared-shell-20261110-v185-orange-dot-3ff1083'
prevLockPath=Path('/tmp/orange-stage-source-lock-v184.json')
prevLock=prevLockPath.read_bytes()
sha=lambda data:sha256(data).hexdigest()
old=json.loads(prevLock)
assert sha(prevLock)=='e4e28828f75a9aec226654daf537892ab3163979927abd18957767adfd4217a3'
assert EDITION['sourceGitRevision']=='3ff108330921f4befc5418b910860fbe6fb55428'
assert len(EDITION['entries'])==23 and len(DELTA['changedAndAddedFiles'])==30
record={
 'schema':'fountain.press.orange-dot.owner-wlan.v185',
 'release':NEW,'predecessor':OLD,'predecessorSourceLockSHA256':sha(prevLock),
 'sourceOwner':'Benedikt Eickhoff',
 'sourceGitRevision':EDITION['sourceGitRevision'],
 'sourceArchiveRange':['2025-12-21','2026-09-19'],
 'sourceSelectionSHA256':EDITION['sourceSelectionSHA256'],
 'sourceEntries':23,'originalPostImages':29,
 'sourceTextSHA256':DELTA['sourceTextSHA256'],
 'reusedOriginalFirstReadingsImages':3,
 'sourceTextsComplete':True,'originalImagesComplete':True,
 'otherReaderVolumesPreserved':True,'existingCompositorReused':True,
 'firstReadingsReuseExplained':True,'publishedProductionAffected':False,
 'publicReleaseAuthorized':False,'physicalIPadSafariAccepted':False,
 'changedAndAddedFiles':DELTA['changedAndAddedFiles'],
}
assert 'orangeDotV185Admission' not in old
new={**old,'orangeDotV185Admission':record}
lockbytes=(json.dumps(new,ensure_ascii=False,indent=2)+'\n').encode()
(OUT/'source-lock.json').write_bytes(lockbytes)
admission={
 'schema':'fountain.press.orange-dot.exact-stage-admission.v185',
 'old':OLD,'new':NEW,'oldLockSHA256':sha(prevLock),'newLockSHA256':sha(lockbytes),
 'oldGuardSHA256':sha(Path('/tmp/orange-stage-http-v184.py').read_bytes()),
 'existingHTTPSHostSHA256':'9a82515373dcac72283ea3f88ae520fac8400516b42b862f4e4d90d426560e92',
 'record':record,'files':DELTA['changedAndAddedFiles'],
 'oldIndexSHA256':DELTA['predecessorIndexSHA256'],
 'oldReaderAppSHA256':DELTA['predecessorReaderJSSHA256'],
}
control=Path('/tmp/orange-dot-guard-v185')
control.mkdir(exist_ok=True)
admissionBytes=(json.dumps(admission,ensure_ascii=False,indent=2)+'\n').encode()
(control/'orange-dot-admission-v185.json').write_bytes(admissionBytes)
admissionHash=sha(admissionBytes)
guard='''#!/usr/bin/env python3
"""Reviewed Orange Dot v185 extension to the existing Fountain Press guard."""
import hashlib,json,sys
from pathlib import Path
STAGE=Path('/home/benedikt/estate-shell-acceptance-staging')
CANDIDATES=STAGE/'candidates'
sys.path.insert(0,str(CANDIDATES))
import serve_breach_rehearsal_v184 as previous
original=previous.original
server=previous.server
ADMISSION_PATH=CANDIDATES/'orange-dot-admission-v185.json'
ADMISSION_SHA256=__HASH__
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
if sha(ADMISSION_PATH)!=ADMISSION_SHA256:
    raise SystemExit('Orange Dot source admission file drift')
A=json.loads(ADMISSION_PATH.read_text())
if sha(Path(previous.__file__))!=A['oldGuardSHA256']:
    raise SystemExit('Inherited v184 guard drift')
class OrangeDotV185Gate:
    def __init__(self,baseline,current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=A['new']:
            raise original.UnadmittedReaderRoute('Wrong Orange Dot stage release')
        self.previous=self.current.parent/A['old']
        if sha(self.previous/'source-lock.json')!=A['oldLockSHA256'] or sha(self.current/'source-lock.json')!=A['newLockSHA256']:
            raise original.UnadmittedReaderRoute('Orange Dot source-lock lineage drift')
        self.inherited=previous.BreachRehearsalV184Gate(baseline,self.previous)
        before=json.loads((self.previous/'source-lock.json').read_text())
        after=json.loads((self.current/'source-lock.json').read_text())
        changed=after.pop('orangeDotV185Admission',None)
        if before!=after or changed!=A['record']:
            raise original.UnadmittedReaderRoute('Orange Dot editorial/source admission drift')
        def inventory(base):
            return {p.relative_to(base).as_posix():p for p in base.rglob('*') if p.is_file()}
        oldfiles,newfiles=inventory(self.previous),inventory(self.current)
        fileHashes=A['files']
        added=set(fileHashes)-set(oldfiles)
        if set(newfiles)!=set(oldfiles)|added:
            raise original.UnadmittedReaderRoute('Unreviewed file additions/deletions')
        if set(fileHashes)&set(oldfiles)!={'estate/index.html','estate/assets/linotype/reading-first-app.js'}:
            raise original.UnadmittedReaderRoute('Unreviewed baseline replacement')
        if sha(self.previous/'estate/index.html')!=A['oldIndexSHA256'] or sha(self.previous/'estate/assets/linotype/reading-first-app.js')!=A['oldReaderAppSHA256']:
            raise original.UnadmittedReaderRoute('Changed source-owning v184 predecessor')
        for rel,p in oldfiles.items():
            if rel in fileHashes or rel=='source-lock.json':continue
            if newfiles[rel].is_symlink() or sha(p)!=sha(newfiles[rel]):
                raise original.UnadmittedReaderRoute('Unrelated established stage changed: '+rel)
        for rel,digest in fileHashes.items():
            if newfiles[rel].is_symlink() or sha(newfiles[rel])!=digest:
                raise original.UnadmittedReaderRoute('Orange Dot digest drift: '+rel)
        print('ORANGE_DOT_V185_ADMITTED posts=23 originalImages=29 sourceLock='+A['newLockSHA256'][:16],flush=True)
    def check(self,raw_url):
        path=original.normalized_request_path(raw_url)
        if path in A['files']:
            file=self.current/path
            if file.is_symlink() or not file.is_file() or sha(file)!=A['files'][path]:
                raise original.UnadmittedReaderRoute('Unadmitted Orange Dot reader asset')
            return
        if path.startswith('estate/assets/orange-dot/') or path.startswith('estate/collections/orange-dot/'):
            raise original.UnadmittedReaderRoute('Unreviewed Orange Dot route')
        self.inherited.check(raw_url)
if __name__=='__main__':
    server.ReaderProvenanceGate=OrangeDotV185Gate
    server.main()
'''.replace('__HASH__',repr(admissionHash))
(control/'serve_orange_dot_v185.py').write_text(guard)
secure='''#!/usr/bin/env python3
"""Original Fountain Press HTTPS host, exact Orange Dot admission only."""
import sys
from pathlib import Path
STAGE=Path('/home/benedikt/estate-shell-acceptance-staging')
sys.path.insert(0,str(STAGE))
sys.path.insert(0,str(STAGE/'candidates'))
import serve_orange_dot_v185 as orange
import serve_shared_shell_preview_https as secure
if orange.sha(Path(secure.__file__))!=orange.A['existingHTTPSHostSHA256']:
    raise SystemExit('Existing TLS reader changed')
if __name__=='__main__':
    secure.ReaderProvenanceGate=orange.OrangeDotV185Gate
    secure.main()
'''
(control/'serve_secure_orange_dot_v185.py').write_text(secure)
print('ORANGE_STAGE_ADMISSION_READY',NEW,'lockSHA',sha(lockbytes),
 'admissionSHA',admissionHash,'added/changed',len(admission['files']))
