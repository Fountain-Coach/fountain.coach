#!/usr/bin/env python3
"""Exact-v215-continuation gate for the existing WLAN Press Bookshelf service.

This extends the SAME source-locked gate and user service. No alternate server,
publisher, host or route authority is created. Activating it is a separate
EstatePublisher-governed immutable release operation.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path('/home/benedikt/estate-shell-acceptance-staging')
sys.path.insert(0,str(ROOT/'candidates'))
import serve_better_ear_v215 as previous

original,server=previous.original,previous.server
ADMISSION=ROOT/'candidates/press-cms-v216-admission.json'
PREDECESSOR='shared-shell-20261116-v215-better-ear-reader-ready'
RELEASE='shared-shell-20261116-v216-catalogue-bookshelf'


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as data:
        for chunk in iter(lambda:data.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


class PressCmsV216Gate:
    def __init__(self, baseline, current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=RELEASE:
            raise original.UnadmittedReaderRoute('Refused non-v216 active stage')
        self.prior=self.current.parent/PREDECESSOR
        if not self.prior.is_dir():
            raise original.UnadmittedReaderRoute('Missing admitted v215 stage predecessor')
        self.inherited=previous.BetterEarV215Gate(baseline,self.prior)
        self.admission=json.loads(ADMISSION.read_text('utf8'))
        a=self.admission
        if a.get('guardSHA256')!=sha(Path(__file__)):
            raise original.UnadmittedReaderRoute('Unreviewed v216 provenance guard source')
        if (a.get('schema')!='fountain.press.cms.private-wlan-stage-admission.v1' or
            a.get('status')!='PREPARED_NOT_ACTIVATED' or
            a.get('releaseID')!=RELEASE or a.get('predecessorReleaseID')!=PREDECESSOR or
            a.get('productionModified') is not False or
            a.get('publicationLane')!='private-owner-WLAN-editorial-review' or
            a.get('bookWorkCounts')!={'essays':10,'first-readings':32,'orange-dot':23} or
            a.get('bookIllustrationCounts')!={'essays':10,'first-readings':30,'orange-dot':23}):
            raise original.UnadmittedReaderRoute('Private v216 stage admission mismatch')
        self.changed=dict(a['changedFilesSHA256'])
        self.added=set(a['addedPaths'])
        self.modified=set(a['changedPaths'])
        if set(self.changed)!=self.added|self.modified or self.added&self.modified:
            raise original.UnadmittedReaderRoute('Invalid v216 file delta roles')
        if a['predecessorSHA256'].get('source-lock.json')!=sha(self.prior/'source-lock.json'):
            raise original.UnadmittedReaderRoute('Predecessor v215 source lock drift')
        prior_paths={p.relative_to(self.prior).as_posix() for p in self.prior.rglob('*') if p.is_file()}
        current_paths={p.relative_to(self.current).as_posix() for p in self.current.rglob('*') if p.is_file()}
        if prior_paths-current_paths or current_paths-prior_paths!=self.added or not self.modified<=prior_paths:
            raise original.UnadmittedReaderRoute('Undeclared additions/removals in v216')
        different=set()
        for rel in prior_paths&current_paths:
            current_path=self.current/rel
            if current_path.is_symlink() or sha(current_path)!=sha(self.prior/rel):different.add(rel)
        if different!=self.modified:
            raise original.UnadmittedReaderRoute('Undeclared v216 edit or missing accepted edit')
        for rel,expected in self.changed.items():
            current_path=self.current/rel
            if current_path.is_symlink() or not current_path.is_file() or sha(current_path)!=expected:
                raise original.UnadmittedReaderRoute('Source-bound v216 file drift: '+rel)
        lock=json.loads((self.current/'source-lock.json').read_text('utf8'))
        mark=lock.get('pressBookshelfCmsV216Admission',{})
        if (mark.get('candidateReleaseID')!=RELEASE or
            mark.get('predecessorReleaseID')!=PREDECESSOR or
            mark.get('privateStageOnly') is not True or
            mark.get('productionModified') is not False or
            mark.get('frontendSnapshotSHA256')!=a['snapshotSHA256']):
            raise original.UnadmittedReaderRoute('Private v216 canonical source-lock admission mismatch')
        print('PRESS_CMS_V216_ADMITTED 3 complete Bookshelf collections; source-authored v215 predecessor retained',flush=True)

    def check(self,raw_url):
        rel=original.normalized_request_path(raw_url)
        current=self.current/rel
        if rel in self.changed:
            if current.is_symlink() or not current.is_file() or sha(current)!=self.changed[rel]:
                raise original.UnadmittedReaderRoute('Unadmitted changed v216 route: '+rel)
            return
        self.inherited.check(raw_url)
        prior=self.prior/rel
        if current.is_symlink() or not current.is_file() or not prior.is_file() or sha(current)!=sha(prior):
            raise original.UnadmittedReaderRoute('Modified unrelated original v215 route: '+rel)

server.ReaderProvenanceGate=PressCmsV216Gate

if __name__=='__main__':
    server.main()
