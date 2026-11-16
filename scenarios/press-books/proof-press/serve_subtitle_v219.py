#!/usr/bin/env python3
"""Source-bound private v219 continuation of identical v218/v217 Press Reader."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path('/home/benedikt/estate-shell-acceptance-staging')
sys.path.insert(0,str(ROOT/'candidates'))
import serve_kino_v218 as previous
original,server=previous.original,previous.server
RELEASE='shared-shell-20261116-v219-complete-authored-subtitle'
PREV='shared-shell-20261116-v218-kino-plates-restored'
ADMISSION=ROOT/'candidates/press-subtitle-v219-admission.json'
LOCK='b2dc3d053117fbc6a7d71813cb9f3f6b96ffbdd957bfc7b3dbabff229d5dadb8'
SOURCE='3778b007423c2b94a9e3da26b9a4c3f1dd7ff04e7ed53747cff43cb7ebc13647'
SUBTITLE_SHA=''
def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

class SubtitleV219Gate:
    def __init__(self,baseline,current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=RELEASE:raise original.UnadmittedReaderRoute('REFUSED different v219 target')
        self.prior=self.current.parent/PREV
        if not self.prior.is_dir():raise original.UnadmittedReaderRoute('Missing canonical v218 predecessor')
        self.inherited=previous.KinoV218Gate(baseline,self.prior)
        a=json.loads(ADMISSION.read_text())
        if (a.get('schema')!='fountain.press.private-v219-subtitle-stage-admission.v1' or
            a.get('status')!='PREPARED_NOT_ACTIVATED' or a.get('guardSHA256')!=sha_file(Path(__file__)) or
            a.get('releaseID')!=RELEASE or a.get('predecessorReleaseID')!=PREV or
            a.get('sourceSHA256')!=SOURCE or a.get('publicationLane')!='private-owner-WLAN-editorial-review' or
            a.get('stageOnly') is not True or a.get('publicReleaseAuthorized') is not False or
            a.get('productionModified') is not False or a.get('noOtherWorksAltered') is not True or
            a.get('originalFiguresUnchanged') is not True or a.get('readerEngineUnchanged') is not True or
            a.get('previousSourceLockSHA256')!=LOCK or sha_file(self.prior/'source-lock.json')!=LOCK or
            a.get('expectedBooks')!={'essays':11,'first-readings':32,'orange-dot':23}):
            raise original.UnadmittedReaderRoute('Unadmitted source or stage v219 protection')
        self.changed=dict(a['changedFilesSHA256'])
        if a['changedPaths']!=sorted(self.changed) or a['addedPaths'] or set(self.changed)!=set(a['previousSHA256']):
            raise original.UnadmittedReaderRoute('Private v219 changed-file declarations drift')
        before={p.relative_to(self.prior).as_posix() for p in self.prior.rglob('*') if p.is_file()}
        after={p.relative_to(self.current).as_posix() for p in self.current.rglob('*') if p.is_file()}
        if before!=after:raise original.UnadmittedReaderRoute('Private v219 missing or unadmitted extra files')
        changed={p for p in before if sha_file(self.prior/p)!=sha_file(self.current/p) or (self.current/p).is_symlink()}
        if changed!=set(self.changed):raise original.UnadmittedReaderRoute('Private v219 mutated unadmitted route or media')
        for name,digest in self.changed.items():
            if (self.current/name).is_symlink() or sha_file(self.current/name)!=digest or sha_file(self.prior/name)!=a['previousSHA256'][name]:
                raise original.UnadmittedReaderRoute('Private v219 named source did not match SHA '+name)
        lock=json.loads((self.current/'source-lock.json').read_text())
        tag=lock.get('pressProofV219SubtitleAdmission',{})
        remaining={k:v for k,v in self.changed.items() if k!='source-lock.json'}
        desired=hashlib.sha256((json.dumps(remaining,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
        if (tag.get('schema')!='fountain.press.private-v219-authored-subtitle.v1' or
            tag.get('releaseID')!=RELEASE or tag.get('predecessorReleaseID')!=PREV or
            tag.get('sourceOwnerCommit')!=a['sourceOwnerCommit'] or
            tag.get('originalManuscriptSHA256')!=SOURCE or
            tag.get('originalSubtitleSHA256')!=a['originalSubtitleSHA256'] or
            tag.get('sourceAddress')!='the-proof-of-the-page.subtitle@0' or
            tag.get('stageOnly') is not True or tag.get('publicReleaseAuthorized') is not False or
            tag.get('productionModified') is not False or
            tag.get('changedWithoutLockSHA256')!=desired):
            raise original.UnadmittedReaderRoute('Private v219 source-locked subtitle not admitted')
        manifest=json.loads((self.current/'estate/read/essay--the-proof-of-the-page/edition-manifest.json').read_text())
        if (manifest.get('sourceSubtitleSHA256')!=a['originalSubtitleSHA256'] or
            manifest.get('sourceSubtitleAddress')!='the-proof-of-the-page.subtitle@0' or
            manifest['sourceSHA256']!=SOURCE or manifest['stageOnly'] is not True or
            manifest['publicReleaseAuthorized'] is not False):
            raise original.UnadmittedReaderRoute('Private v219 source manifest/draft role mismatch')
        print('PRESS_SUBTITLE_V219_ADMITTED exact author subtitle; all 66 original works/Reader preserved; private staging only',flush=True)
    def check(self,url):
        rel=original.normalized_request_path(url)
        if rel in self.changed:
            path=self.current/rel
            if path.is_symlink() or not path.is_file() or sha_file(path)!=self.changed[rel]:
                raise original.UnadmittedReaderRoute('Changed v219 page refused '+rel)
            return
        self.inherited.check(url)
        p=self.current/rel;q=self.prior/rel
        if p.is_symlink() or not p.is_file() or not q.is_file() or sha_file(p)!=sha_file(q):
            raise original.UnadmittedReaderRoute('Inherited v219 page not identical to accepted predecessor '+rel)
server.ReaderProvenanceGate=SubtitleV219Gate
if __name__=='__main__':server.main()
