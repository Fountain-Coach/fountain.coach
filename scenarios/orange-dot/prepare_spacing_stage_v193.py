#!/usr/bin/env python3
"""Source-pinned one-asset Orange Dot Reader repair on canonical Fountain Press WLAN.

Requires live predecessor v192b, an accepted source-owning Git revision,
and byte-matched current Linotype engine. Builds an immutable release and
a strict descendant of the existing provenance guard. DOES NOT ACTIVATE.
"""
import hashlib,json,os,subprocess,sys
from pathlib import Path

BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
OLD="shared-shell-20261111-v192b-satzfunk-listening-64f5263"
NEW="shared-shell-20261111-v193-orange-dot-portrait-spacing-b431528"
OLD_LOCK="981851877b7be9c020412a66ac328d3e825ac9e46a892a9bc1fcea07027a9518"
OLD_JS="e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a"
NEW_JS="837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a"
OLD_GUARD="25a992c59a10618d8549a8dc02178f3a70d0f17ebb52d1e2bf63bb63e7d15834"
OWNER="Fountain-Coach/fountain.coach"
SOURCE_COMMIT="b431528"
REL="estate/assets/linotype/reading-first-press-engine.js"
PATCH=BASE/"candidates/orange-dot-reader-v193-corrected.js"
GUARD=BASE/"candidates/serve_orange_dot_spacing_v193.py"
SECURE=BASE/"candidates/serve_secure_orange_dot_spacing_v193.py"
ADMISSION=BASE/"candidates/orange-dot-figure-spacing-admission-v193.json"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()

def main():
    prev=BASE/"releases"/OLD
    new=BASE/"releases"/NEW
    current=BASE/"current"
    assert current.is_symlink() and current.resolve()==prev,"Another stage has become current"
    assert not new.exists() and not GUARD.exists() and not SECURE.exists() and not ADMISSION.exists(),"Do not overwrite prior candidate"
    assert sha(prev/"source-lock.json")==OLD_LOCK
    assert sha(prev/REL)==OLD_JS and sha(PATCH)==NEW_JS
    assert sha(BASE/"candidates/serve_satzfunk_listening_v192b.py")==OLD_GUARD
    expected=(prev/REL).read_text()
    altered=PATCH.read_text()
    line='if(this.pageFrame&&(this.css.spread||sourceId.startsWith("work-orange-dot--"))&&leaf.area.childElementCount){'
    original='if(this.pageFrame&&this.css.spread&&leaf.area.childElementCount){'
    assert expected.count(original)==1
    assert altered==expected.replace(original,line,1)
    subprocess.run(["cp","-a","-l",str(prev),str(new)],check=True)
    dest=new/REL
    staging=dest.with_name(dest.name+".v193-tmp")
    staging.write_bytes(PATCH.read_bytes())
    os.replace(staging,dest)
    assert sha(dest)==NEW_JS
    before=json.loads((prev/"source-lock.json").read_text())
    assert "orangeDotFigureSpacingV193" not in before
    record={
        "schema":"fountain.press.orange-dot.portrait-secondary-illustration.v193",
        "sourceOwner":OWNER,"sourceGitRevision":SOURCE_COMMIT,
        "previousRelease":OLD,"currentRelease":NEW,
        "selectedSourceTexts":23,"originalSourceImages":29,
        "sourceImageBytesUnchanged":True,
        "sourceManuscriptBytesUnchanged":True,
        "changedPath":REL,"sourceSHA256":OLD_JS,"candidateSHA256":NEW_JS,
        "behaviour":"measured portrait secondary-figure fit only for work-orange-dot--*",
        "firstReadingsUnmodified":True,
        "publicReleaseAuthorized":False,
        "stageLane":"owner-WLAN private editorial proof"
    }
    after=dict(before)
    after["orangeDotFigureSpacingV193"]=record
    lock=new/"source-lock.json"
    tmp=new/".source-lock-v193-tmp"
    tmp.write_text(json.dumps(after,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    os.replace(tmp,lock)
    prevFiles={p.relative_to(prev).as_posix():p for p in prev.rglob("*") if p.is_file()}
    newFiles={p.relative_to(new).as_posix():p for p in new.rglob("*") if p.is_file()}
    assert set(prevFiles)==set(newFiles)
    for rel,p in prevFiles.items():
        if rel in (REL,"source-lock.json"):continue
        if newFiles[rel].is_symlink() or sha(newFiles[rel])!=sha(p):
            raise SystemExit("Unadmitted stage change: "+rel)
    receipt={
        "schema":"fountain.press.orange-dot.spacing-admission.v193",
        "oldRelease":OLD,"newRelease":NEW,
        "oldLockSHA256":OLD_LOCK,"newLockSHA256":sha(lock),
        "inheritedGuardSHA256":OLD_GUARD,
        "oldEngineSHA256":OLD_JS,"newEngineSHA256":NEW_JS,
        "changedPath":REL,"preservedFileCount":len(prevFiles)-2,
        "record":record,"sourceCommit":SOURCE_COMMIT,
        "rightsScope":"original sources private; public release separate",
        "physicalIPadAccepted":False,
        "publicProductionAffected":False
    }
    ADMISSION.write_text(json.dumps(receipt,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    admissionSHA=sha(ADMISSION)
    guard='''#!/usr/bin/env python3
"""Admit exactly one source-owned Orange Dot portrait pagination correction."""
import hashlib,json,sys
from pathlib import Path
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_satzfunk_listening_v192b as previous
original=previous.original
server=previous.server
ADMISSION=BASE/"candidates/orange-dot-figure-spacing-admission-v193.json"
ADMISSION_SHA="__ADMISSION_SHA__"
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
if digest(ADMISSION)!=ADMISSION_SHA:
    raise SystemExit("Orange Dot v193 admission was altered")
A=json.loads(ADMISSION.read_text())
if digest(Path(previous.__file__))!=A["inheritedGuardSHA256"]:
    raise SystemExit("Orange Dot inherited reader guard altered")
class OrangeDotSpacingV193Gate:
    def __init__(self,baseline,current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=A["newRelease"]:
            raise original.UnadmittedReaderRoute("Unexpected Orange Dot stage")
        self.prior=self.current.parent/A["oldRelease"]
        if digest(self.prior/"source-lock.json")!=A["oldLockSHA256"]:
            raise original.UnadmittedReaderRoute("Predecessor source-lock changed")
        if digest(self.current/"source-lock.json")!=A["newLockSHA256"]:
            raise original.UnadmittedReaderRoute("Orange Dot source-lock changed")
        self.inherited=previous.SatzfunkListeningV192Gate(baseline,self.prior)
        before=json.loads((self.prior/"source-lock.json").read_text())
        after=json.loads((self.current/"source-lock.json").read_text())
        if after.pop("orangeDotFigureSpacingV193",None)!=A["record"] or after!=before:
            raise original.UnadmittedReaderRoute("Unexpected Orange Dot source-lock delta")
        old={p.relative_to(self.prior).as_posix():p for p in self.prior.rglob("*") if p.is_file()}
        new={p.relative_to(self.current).as_posix():p for p in self.current.rglob("*") if p.is_file()}
        if set(old)!=set(new):
            raise original.UnadmittedReaderRoute("Unexpected stage inventory delta")
        for rel,p in old.items():
            if rel in ("source-lock.json",A["changedPath"]):continue
            if new[rel].is_symlink() or digest(p)!=digest(new[rel]):
                raise original.UnadmittedReaderRoute("Unadmitted inherited change "+rel)
        if digest(new[A["changedPath"]])!=A["newEngineSHA256"]:
            raise original.UnadmittedReaderRoute("Unadmitted Orange Dot compositor")
        print("ORANGE_DOT_V193_ADMITTED 23 source texts, 29 original images, prior stage intact",flush=True)
    def check(self,raw_url):
        rel=original.normalized_request_path(raw_url)
        if rel==A["changedPath"]:
            if digest(self.current/rel)!=A["newEngineSHA256"]:
                raise original.UnadmittedReaderRoute("Reader compositor tampered")
            return
        self.inherited.check(raw_url)
if __name__=="__main__":
    server.ReaderProvenanceGate=OrangeDotSpacingV193Gate
    server.main()
'''
    GUARD.write_text(guard.replace("__ADMISSION_SHA__",admissionSHA))
    SECURE.write_text('''#!/usr/bin/env python3
import sys
from pathlib import Path
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_orange_dot_spacing_v193 as orange
import serve_shared_shell_preview_https as secure
if __name__=="__main__":
    secure.ReaderProvenanceGate=orange.OrangeDotSpacingV193Gate
    secure.main()
''')
    print("PREPARED",NEW,flush=True)
    print("PINNED_OWNER_COMMIT",SOURCE_COMMIT,flush=True)
    print("DELTA",REL,OLD_JS,NEW_JS,flush=True)
    print("PREVIOUS_FILES_PRESERVED",receipt["preservedFileCount"],flush=True)
    print("ADMISSION_SHA",admissionSHA,"LOCK_SHA",receipt["newLockSHA256"],flush=True)
    print("CANDIDATE_NOT_ACTIVATED",flush=True)
if __name__=="__main__":main()
