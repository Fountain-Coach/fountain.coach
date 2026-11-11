#!/usr/bin/env python3
"""Admit production-shaped Orange Dot Bookshelf on the canonical private WLAN stage.

Public fountain.coach is the inspected visual/Reader baseline. Preserve every
historical file of v193 except explicit SHA-256-pinned overlays, all Koken media
and all source repositories. No public deployment or rights admission.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
CURRENT=BASE/"current"
OLD="shared-shell-20261111-v193-orange-dot-portrait-spacing-b431528"
NEW="shared-shell-20261111-v194b-orange-dot-production-bookshelf-kino-007ca1c"
OVERLAY=BASE/"candidates/orange-dot-wlan-v194b-source"
MANIFEST=OVERLAY/"overlay-manifest.json"
GUARD=BASE/"candidates/serve_orange_dot_production_bookshelf_v194b.py"
SECURE=BASE/"candidates/serve_secure_orange_dot_production_bookshelf_v194b.py"
ADMISSION=BASE/"candidates/orange-dot-production-bookshelf-admission-v194b.json"
PREVIOUS_LOCK="ab24cd67a668153a6d8fbc3ba599090bda1e037327920053deb0607149b93de0"
PREVIOUS_GUARD="cc9ff3254f50404842097b389778d8e23d03e397e514260a248c4e79274c223c"
SOURCE_MANIFEST="7bfcd9dda35fcea84f6c8b2e6c30a6cffaff4b6623df65d907ca0f8e56830888"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    previous=BASE/"releases"/OLD
    release=BASE/"releases"/NEW
    assert CURRENT.is_symlink() and CURRENT.resolve()==previous, "Stage already changed"
    assert not release.exists() and not ADMISSION.exists() and not GUARD.exists() and not SECURE.exists()
    assert sha(previous/"source-lock.json")==PREVIOUS_LOCK
    assert sha(BASE/"candidates/serve_orange_dot_spacing_v193.py")==PREVIOUS_GUARD
    assert sha(MANIFEST)==SOURCE_MANIFEST
    meta=json.loads(MANIFEST.read_text())
    assert meta["sourceGitCommit"]=="007ca1c"
    assert meta["publicBaselineRelease"]=="fcis-essay-heading-20261110-8f58f29"
    assert meta["collections"]==["essays","first-readings","orange-dot"]
    assert meta["exclusions"]==["governance","works","scores"]
    assert meta["livePublicProductionChanged"] is False
    files=meta["files"]
    assert len(meta["stageOnlyReconciliation"]["alreadyPublicKinoEditionManifests"])==2
    assert len(files)==36
    for path,digest in files.items():
        obj=OVERLAY/path
        assert obj.is_file() and not obj.is_symlink()
        assert sha(obj)==digest
    html=(OVERLAY/"estate/index.html").read_text()
    for forbidden in ('data-reader-volume="governance"',
                      'data-reader-volume="scores"',
                      'data-reader-volume="score--between-gardens"',
                      'data-edition-membership="governance"'):
        assert forbidden not in html,forbidden
    assert html.count('data-reader-volume="orange-dot--')==23
    assert 'governance.fountain.coach/' in html, "Published references must survive"

    subprocess.run(["cp","-a","-l",str(previous),str(release)],check=True)
    changed={}
    identical=[]
    new=[]
    for rel,source_hash in sorted(files.items()):
        dest=release/rel
        if dest.exists() and sha(dest)==source_hash:
            identical.append(rel)
            continue
        if not dest.exists():new.append(rel)
        dest.parent.mkdir(parents=True,exist_ok=True)
        tmp=dest.with_name("."+dest.name+".orange-v194b-tmp")
        tmp.write_bytes((OVERLAY/rel).read_bytes())
        os.replace(tmp,dest)
        assert sha(dest)==source_hash
        changed[rel]=source_hash

    before=json.loads((previous/"source-lock.json").read_text())
    assert "orangeDotProductionShapeV194B" not in before
    record={
      "schema":"fountain.press.orange-dot.production-shaped-bookshelf.v194b",
      "status":"private-WLAN-proof-not-public",
      "sourceOwner":"Fountain-Coach/fountain.coach",
      "sourceGitCommit":meta["sourceGitCommit"],
      "productionPredecessor":meta["publicBaselineRelease"],
      "stagePredecessor":OLD,
      "stageRelease":NEW,
      "collections":["essays","first-readings","orange-dot"],
      "excludedBookShelves":["governance","works","scores"],
      "governanceReferencesPreserved":True,
      "governanceSourceUnchanged":True,
      "kokenSourceMediaUnchanged":True,
      "originalOrangeDotWorks":23,
      "originalOrangeDotImages":29,
      "productionMirrorHTMLSHA256":meta["publicCandidateHTMLSHA256"],
      "sourceManifestSHA256":SOURCE_MANIFEST,
      "stageOverlayIdenticalPaths":identical,
      "stageOverlayChangedOrNewFiles":changed,
      "publicReleaseAuthorized":False,
    }
    lock=dict(before)
    lock["orangeDotProductionShapeV194B"]=record
    tmp=release/".source-lock-orange-v194b-tmp"
    tmp.write_text(json.dumps(lock,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    os.replace(tmp,release/"source-lock.json")
    before_files={p.relative_to(previous).as_posix():p for p in previous.rglob("*") if p.is_file()}
    after_files={p.relative_to(release).as_posix():p for p in release.rglob("*") if p.is_file()}
    expected=set(before_files)|set(new)
    assert set(after_files)==expected,(len(after_files),len(expected))
    for rel,p in before_files.items():
        if rel=="source-lock.json" or rel in changed:continue
        assert not after_files[rel].is_symlink() and sha(p)==sha(after_files[rel]),rel
    receipt={
      "schema":"fountain.press.orange-dot-production-shape-stage-admission.v194b",
      "oldRelease":OLD,"newRelease":NEW,
      "oldLockSHA256":PREVIOUS_LOCK,
      "newLockSHA256":sha(release/"source-lock.json"),
      "inheritedGuardSHA256":PREVIOUS_GUARD,
      "sourceManifestSHA256":SOURCE_MANIFEST,
      "record":record,
      "changedFiles":changed,
      "identicalSourceFiles":identical,
      "preservedPreviousFiles":len(before_files)-1-len([x for x in changed if x in before_files]),
      "newFiles":new,
      "publicProductionAffected":False,
    }
    ADMISSION.write_text(json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    admission_sha=sha(ADMISSION)
    source='''#!/usr/bin/env python3
"""Source-locked private production-shaped Bookshelf; inherit exact v193 chain."""
import hashlib,json,sys
from pathlib import Path
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_orange_dot_spacing_v193 as previous
original=previous.original
server=previous.server
ADMISSION=BASE/"candidates/orange-dot-production-bookshelf-admission-v194b.json"
ADMISSION_SHA="__ADMISSION_SHA__"
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()
if digest(ADMISSION)!=ADMISSION_SHA:
    raise SystemExit("v194b admission altered")
A=json.loads(ADMISSION.read_text())
if digest(Path(previous.__file__))!=A["inheritedGuardSHA256"]:
    raise SystemExit("v193 inherited source guard altered")
class OrangeDotBookshelfV194BGate:
    def __init__(self,baseline,current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=A["newRelease"]:
            raise original.UnadmittedReaderRoute("Wrong Orange Dot staging release")
        self.prior=self.current.parent/A["oldRelease"]
        if digest(self.prior/"source-lock.json")!=A["oldLockSHA256"]:
            raise original.UnadmittedReaderRoute("Predecessor stage source-lock changed")
        if digest(self.current/"source-lock.json")!=A["newLockSHA256"]:
            raise original.UnadmittedReaderRoute("Production-shaped stage source-lock changed")
        self.inherited=previous.OrangeDotSpacingV193Gate(baseline,self.prior)
        oldlock=json.loads((self.prior/"source-lock.json").read_text())
        newlock=json.loads((self.current/"source-lock.json").read_text())
        if newlock.pop("orangeDotProductionShapeV194B",None)!=A["record"] or newlock!=oldlock:
            raise original.UnadmittedReaderRoute("Unexpected source-lock mutation")
        old={p.relative_to(self.prior).as_posix():p for p in self.prior.rglob("*") if p.is_file()}
        new={p.relative_to(self.current).as_posix():p for p in self.current.rglob("*") if p.is_file()}
        if set(new)!=set(old)|set(A["newFiles"]):
            raise original.UnadmittedReaderRoute("Unexpected stage inventory")
        for rel,p in old.items():
            if rel=="source-lock.json" or rel in A["changedFiles"]:continue
            if new[rel].is_symlink() or digest(p)!=digest(new[rel]):
                raise original.UnadmittedReaderRoute("Inherited stage changed "+rel)
        for rel,h in A["changedFiles"].items():
            if new[rel].is_symlink() or digest(new[rel])!=h:
                raise original.UnadmittedReaderRoute("Stage overlay changed "+rel)
        print("ORANGE_DOT_V194B_ADMITTED production Bookshelf; Essays, First Readings, Orange Dot; Governance and Works shelves excluded",flush=True)
    def check(self,raw_url):
        rel=original.normalized_request_path(raw_url)
        if rel in A["changedFiles"]:
            obj=self.current/rel
            if not obj.is_file() or obj.is_symlink() or digest(obj)!=A["changedFiles"][rel]:
                raise original.UnadmittedReaderRoute("Unadmitted production-shaped asset")
            return
        self.inherited.check(raw_url)
if __name__=="__main__":
    server.ReaderProvenanceGate=OrangeDotBookshelfV194BGate
    server.main()
'''
    GUARD.write_text(source.replace("__ADMISSION_SHA__",admission_sha))
    SECURE.write_text('''#!/usr/bin/env python3
import sys
from pathlib import Path
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_orange_dot_production_bookshelf_v194b as bookshelf
import serve_shared_shell_preview_https as secure
if __name__=="__main__":
    secure.ReaderProvenanceGate=bookshelf.OrangeDotBookshelfV194BGate
    secure.main()
''')
    print("ORANGE_V194B_CANDIDATE_READY",NEW,flush=True)
    print("DELTA",len(changed),"changed/new",len(new),"new",len(identical),"already-identical",flush=True)
    print("INHERITED_FILES_PRESERVED",receipt["preservedPreviousFiles"],flush=True)
    print("LOCK_SHA",receipt["newLockSHA256"],"ADMISSION_SHA",admission_sha,flush=True)
    print("NOT_ACTIVATED",flush=True)

if __name__=="__main__": main()
