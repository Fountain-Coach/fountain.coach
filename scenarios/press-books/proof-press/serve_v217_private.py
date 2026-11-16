#!/usr/bin/env python3
"""Exact v217 immutable private WLAN release guard inheriting v216 authority.

This is not a second server or publication lane: it supplies one additional
source-bound boundary to the existing registered user-systemd preview service.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path('/home/benedikt/estate-shell-acceptance-staging')
sys.path.insert(0,str(ROOT/'candidates'))
import serve_press_cms_v216 as previous

original,server=previous.original,previous.server
RELEASE='shared-shell-20261116-v217-proof-of-the-page-heading-proof'
PREDECESSOR='shared-shell-20261116-v216-catalogue-bookshelf'
ADMISSION=ROOT/'candidates/press-proof-v217-admission.json'
SOURCE='3778b007423c2b94a9e3da26b9a4c3f1dd7ff04e7ed53747cff43cb7ebc13647'


def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


class ProofPressV217Gate:
    def __init__(self, baseline, current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=RELEASE:
            raise original.UnadmittedReaderRoute('REFUSED non-v217 release identity')
        self.prior=self.current.parent/PREDECESSOR
        if not self.prior.is_dir():raise original.UnadmittedReaderRoute('Missing canonical v216 predecessor')
        self.inherited=previous.PressCmsV216Gate(baseline,self.prior)
        self.admission=json.loads(ADMISSION.read_text('utf8'))
        a=self.admission
        if a.get('guardSHA256')!=sha(Path(__file__)):
            raise original.UnadmittedReaderRoute('Unadmitted v217 executable guard source')
        if (a.get('schema')!='fountain.press.proof-v217.private-stage-admission.v1' or
            a.get('status')!='PREPARED_NOT_ACTIVATED' or
            a.get('releaseID')!=RELEASE or a.get('predecessorReleaseID')!=PREDECESSOR or
            a.get('sourceSHA256')!=SOURCE or
            a.get('publicationLane')!='private-owner-WLAN-editorial-review' or
            a.get('stageOnly') is not True or a.get('publicReleaseAuthorized') is not False or
            a.get('productionModified') is not False or
            a.get('expectedBooks')!={'essays':11,'first-readings':32,'orange-dot':23} or
            a.get('expectedIllustrations')!={'essays':11,'first-readings':30,'orange-dot':23} or
            a.get('predecessorSourceLockSHA256')!=sha(self.prior/'source-lock.json')):
            raise original.UnadmittedReaderRoute('Private v217 source admission or book membership drift')
        self.changed=dict(a['changedFilesSHA256'])
        self.added=set(a['addedPaths'])
        self.modified=set(a['changedPaths'])
        if self.added&self.modified or set(self.changed)!=self.added|self.modified or 'source-lock.json' not in self.modified:
            raise original.UnadmittedReaderRoute('Invalid source-authorized v217 delta')
        prior_paths={p.relative_to(self.prior).as_posix() for p in self.prior.rglob('*') if p.is_file()}
        current_paths={p.relative_to(self.current).as_posix() for p in self.current.rglob('*') if p.is_file()}
        if prior_paths-current_paths or current_paths-prior_paths!=self.added or not self.modified<=prior_paths:
            raise original.UnadmittedReaderRoute('Missing original private works or undeclared additions')
        changed={rel for rel in prior_paths&current_paths if sha(self.prior/rel)!=sha(self.current/rel) or (self.current/rel).is_symlink()}
        if changed!=self.modified:
            raise original.UnadmittedReaderRoute('Undeclared mutation of a protected v216 publication file')
        for rel,want in self.changed.items():
            target=self.current/rel
            if target.is_symlink() or not target.is_file() or sha(target)!=want:
                raise original.UnadmittedReaderRoute('Refused modified v217 source bytes: '+rel)
        lock=json.loads((self.current/'source-lock.json').read_text('utf8'))
        tag=lock.get('pressProofV217Admission',{})
        without={k:v for k,v in self.changed.items() if k!='source-lock.json'}
        expected=hashlib.sha256((json.dumps(without,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
        if (tag.get('schema')!='fountain.press.private-proof-v217.v1' or
            tag.get('releaseID')!=RELEASE or tag.get('predecessorReleaseID')!=PREDECESSOR or
            tag.get('sourceOwnerCommit')!=a['sourceOwnerCommit'] or
            tag.get('originalManuscriptSHA256')!=SOURCE or
            tag.get('privateStageOnly') is not True or tag.get('publicReleaseAuthorized') is not False or
            tag.get('changedWithoutLockSHA256')!=expected or
            tag.get('addedPaths')!=sorted(self.added) or
            tag.get('manifestSHA256')!=self.changed['estate/read/essay--the-proof-of-the-page/edition-manifest.json']):
            raise original.UnadmittedReaderRoute('Private v217 admitted lock did not match changed files')
        manifest=json.loads((self.current/'estate/read/essay--the-proof-of-the-page/edition-manifest.json').read_text())
        if (manifest['sourceSHA256']!=SOURCE or manifest['sourceCommit']!=a['sourceOwnerCommit'] or
            manifest['publicReleaseAuthorized'] is not False or manifest['stageOnly'] is not True or
            len(manifest['figures'])!=6):
            raise original.UnadmittedReaderRoute('Source/illustration manifest not admitted')
        print('PRESS_PROOF_V217_ADMITTED original v216 Reader, 66 complete active works, six source-owned plates, private only',flush=True)

    def check(self,url):
        rel=original.normalized_request_path(url)
        target=self.current/rel
        if rel in self.changed:
            if target.is_symlink() or not target.is_file() or sha(target)!=self.changed[rel]:
                raise original.UnadmittedReaderRoute('Unadmitted v217 changed route '+rel)
            return
        self.inherited.check(url)
        prior=self.prior/rel
        if target.is_symlink() or not target.is_file() or not prior.is_file() or sha(target)!=sha(prior):
            raise original.UnadmittedReaderRoute('Unreviewed v217 inherited original route '+rel)

server.ReaderProvenanceGate=ProofPressV217Gate

if __name__=='__main__':
    server.main()
