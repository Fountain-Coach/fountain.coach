#!/usr/bin/env python3
"""Inherit the accepted v217/v216/v215 gate and add only two Kino originals.

Never bypass any previous source-lock requirements, alter source HTML/Reader,
or turn private review staging into public publication.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path('/home/benedikt/estate-shell-acceptance-staging')
sys.path.insert(0,str(ROOT/'candidates'))
import serve_v217_private as previous

original,server=previous.original,previous.server
RELEASE='shared-shell-20261116-v218-kino-plates-restored'
PREDECESSOR='shared-shell-20261116-v217-proof-of-the-page-heading-proof'
ADMISSION=ROOT/'candidates/press-kino-v218-admission.json'
# Verify the exact active v217 lock SHA before admitting original public images.
OLD_LOCK_SHA='570f3a17e57211fdbce4f2fc22f015a1143190fc492886f662744c48f04d765e'
ORIGINALS={
 'estate/instruments/kino/plates/v156.png':'f2e0dc22c01a626b184983a7d8abf94d44dddfa3c0143b834706d7ca3e258d00',
 'estate/instruments/kino/plates/v158.png':'6e4ee6d8571062f9fca405b718eb1e5c561716a8f08a3d16b9cea3f89d3b9484',
}


def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

class KinoV218Gate:
    def __init__(self, baseline, current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=RELEASE:
            raise original.UnadmittedReaderRoute('REFUSED non-v218 stage release')
        self.prior=self.current.parent/PREDECESSOR
        if not self.prior.is_dir():
            raise original.UnadmittedReaderRoute('Canonical v217 predecessor absent')
        self.inherited=previous.ProofPressV217Gate(baseline,self.prior)
        a=json.loads(ADMISSION.read_text('utf8'))
        if a.get('guardSHA256')!=sha(Path(__file__)):
            raise original.UnadmittedReaderRoute('Kino v218 guard executable SHA drift')
        if (a.get('schema')!='fountain.press.private-kino-v218-stage-admission.v1' or
            a.get('status')!='PREPARED_NOT_ACTIVATED' or
            a.get('releaseID')!=RELEASE or a.get('predecessorReleaseID')!=PREDECESSOR or
            a.get('publicationLane')!='private-owner-WLAN-editorial-review' or
            a.get('stageOnly') is not True or a.get('publicReleaseAuthorized') is not False or
            a.get('productionModified') is not False or
            a.get('predecessorSourceLockSHA256')!=OLD_LOCK_SHA or
            a.get('predecessorSourceLockSHA256')!=sha(self.prior/'source-lock.json') or
            a.get('existingCatalogueWorkCounts')!={'essays':11,'first-readings':32,'orange-dot':23} or
            a.get('addedPaths')!=sorted(ORIGINALS) or
            a.get('changedPaths')!=['source-lock.json'] or
            a.get('changedFilesSHA256')!={**ORIGINALS,'source-lock.json':a['changedFilesSHA256'].get('source-lock.json')}):
            raise original.UnadmittedReaderRoute('Kino v218 private admission mismatch')
        for rel in ORIGINALS:
            if a['originalPublicSourceURLs'].get(rel)!='https://fountain.coach/'+rel:
                raise original.UnadmittedReaderRoute('Original public publication provenance lost')
        prior_paths={p.relative_to(self.prior).as_posix() for p in self.prior.rglob('*') if p.is_file()}
        current_paths={p.relative_to(self.current).as_posix() for p in self.current.rglob('*') if p.is_file()}
        if prior_paths-current_paths or current_paths-prior_paths!=set(ORIGINALS):
            raise original.UnadmittedReaderRoute('Unadmitted v218 changed release file inventory')
        diffs={rel for rel in prior_paths&current_paths if (self.current/rel).is_symlink() or sha(self.current/rel)!=sha(self.prior/rel)}
        if diffs!={'source-lock.json'}:
            raise original.UnadmittedReaderRoute('Other source/Reader byte changed under v218')
        for rel,want in a['changedFilesSHA256'].items():
            p=self.current/rel
            if p.is_symlink() or not p.is_file() or sha(p)!=want:
                raise original.UnadmittedReaderRoute('Unreviewed original Kino plate/source-lock byte '+rel)
        lock=json.loads((self.current/'source-lock.json').read_text())
        tag=lock.get('pressProofV218KinoAssetAdmission',{})
        if (tag.get('schema')!='fountain.press.kino-public-original-plates-private-reconciliation.v1' or
            tag.get('releaseID')!=RELEASE or tag.get('predecessorReleaseID')!=PREDECESSOR or
            tag.get('sourceOwnerCommit')!=a.get('sourceOwnerCommit') or
            tag.get('sourceImageSHA256')!=ORIGINALS or
            tag.get('admittedAddedPaths')!=sorted(ORIGINALS) or
            tag.get('stageOnly') is not True or tag.get('publicReleaseAuthorized') is not False or
            tag.get('originalsRetained') is not True or tag.get('productionModified') is not False):
            raise original.UnadmittedReaderRoute('Kino original source-lock admission mismatch')
        print('PRESS_KINO_V218_ADMITTED two SHA-pinned public original Kino plates; all v217 texts/Reader retained',flush=True)
        self.changed=dict(a['changedFilesSHA256'])

    def check(self,raw_url):
        rel=original.normalized_request_path(raw_url)
        current=self.current/rel
        if rel in self.changed:
            if current.is_symlink() or not current.is_file() or sha(current)!=self.changed[rel]:
                raise original.UnadmittedReaderRoute('Kino v218 altered private route '+rel)
            return
        self.inherited.check(raw_url)
        prior=self.prior/rel
        if current.is_symlink() or not current.is_file() or not prior.is_file() or sha(current)!=sha(prior):
            raise original.UnadmittedReaderRoute('Kino v218 could not reuse original route '+rel)

server.ReaderProvenanceGate=KinoV218Gate
if __name__=='__main__':server.main()
