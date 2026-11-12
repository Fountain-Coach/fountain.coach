#!/usr/bin/env python3
"""Prepare source-locked v196 from the verified v195 WLAN predecessor; never activate."""
from pathlib import Path
import hashlib,json,os,subprocess

BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
OLD="shared-shell-20261111-v195-direct-books-social-5227c32"
NEW="shared-shell-20261112-v196-fcis-value-essay-3b6fbd5"
EXPECTED_LOCK="71eae0d19d032617ba80ee4d9ef749d62fa04c8c1b32ec129a03cef2306152e5"
EXPECTED_GUARD="81eb6dca7b58b620f8567be36a73f0f72f50a27942b75b4054b9601551082274"
REV="3b6fbd537a3e9abaea54411f45ef9d21f1b48b12"
OVERLAY=BASE/"candidates/fcis-value-essay-v196-overlay"
ADMISSION=BASE/"candidates/fcis-value-essay-admission-v196.json"
GUARD=BASE/"candidates/serve_fcis_value_essay_v196.py"
SECURE=BASE/"candidates/serve_secure_fcis_value_essay_v196.py"
PRIOR_GUARD=BASE/"candidates/serve_orange_dot_direct_books_v195.py"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1048576),b""):
            h.update(part)
    return h.hexdigest()

def main():
    current=BASE/"current"
    old=BASE/"releases"/OLD
    new=BASE/"releases"/NEW
    if not current.is_symlink() or current.resolve()!=old:
        raise RuntimeError("Concurrent stage predecessor changed")
    if not old.is_dir() or new.exists() or any(p.exists() for p in (ADMISSION,GUARD,SECURE)):
        raise RuntimeError("Preflight refuses missing predecessor or existing v196 artifact")
    if sha(old/"source-lock.json")!=EXPECTED_LOCK or sha(PRIOR_GUARD)!=EXPECTED_GUARD:
        raise RuntimeError("Actual v195 stage lock or guard drift")
    receipt=json.loads((OVERLAY/"build-receipt.json").read_text())
    if receipt["sourceGitRevision"]!=REV or receipt["stagingOnly"] is not True or receipt["publicDelivery"] is not False:
        raise RuntimeError("Unexpected author source or authorization")
    original=BASE/"candidates/fcis-value-essay-v196-input/source.html"
    if sha(original)!=receipt["sourceSHA256"]:
        raise RuntimeError("Original manuscript changed")
    changed=receipt["changes"]
    if len(changed)!=5 or "estate/index.html" not in changed:
        raise RuntimeError("Unexpected source overlay")
    for rel,digest in changed.items():
        p=OVERLAY/rel
        if not p.is_file() or p.is_symlink() or sha(p)!=digest:
            raise RuntimeError("Source overlay digest drift: "+rel)
    if sha(old/"estate/index.html")!=receipt["baselineIndexSHA256"]:
        raise RuntimeError("v195 HTML baseline changed")
    inherited={p.relative_to(old).as_posix():p for p in old.rglob("*") if p.is_file()}
    newfiles=set(changed)-set(inherited)
    if len(newfiles)!=4 or set(inherited)&set(changed)!={"estate/index.html"}:
        raise RuntimeError("Source overlay does not match declared delta")
    subprocess.run(["cp","-a","-l",str(old),str(new)],check=True)
    for rel,digest in sorted(changed.items()):
        target=new/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        tmp=target.with_name("."+target.name+".v196-tmp")
        tmp.write_bytes((OVERLAY/rel).read_bytes())
        os.replace(tmp,target)
        if sha(target)!=digest:
            raise RuntimeError("Candidate copied wrong source: "+rel)
    previous=json.loads((old/"source-lock.json").read_text())
    if "fcisValueEssayV196Admission" in previous:
        raise RuntimeError("Duplicate admission")
    record={
        "schema":"fountain.press.source-bound-essay-stage.v196",
        "sourceOwner":"Fountain-Coach/fountain.coach",
        "sourceRevision":REV,
        "sourcePath":"site/essays/the-value-of-what-we-can-prove/source.html",
        "sourceSHA256":receipt["sourceSHA256"],
        "sourceBuildReceiptSHA256":sha(OVERLAY/"build-receipt.json"),
        "oldRelease":OLD,"newRelease":NEW,
        "essayID":"essay--the-value-of-what-we-can-prove",
        "canonicalCollection":"/estate/read/essays/",
        "candidateDirectRoute":"/estate/read/essay--the-value-of-what-we-can-prove/",
        "newOrUpdatedFiles":dict(sorted(changed.items())),
        "stageOnly":True,"publicReleaseAuthorized":False,
        "existingPressReader":True,"originalIllustrationsAdded":0,
    }
    updated=dict(previous)
    updated["fcisValueEssayV196Admission"]=record
    tmp=new/".source-lock-v196-tmp"
    tmp.write_text(json.dumps(updated,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    os.replace(tmp,new/"source-lock.json")
    final={p.relative_to(new).as_posix():p for p in new.rglob("*") if p.is_file()}
    if set(final)!=set(inherited)|newfiles:
        raise RuntimeError("Unexpected staged file inventory")
    for rel,p in inherited.items():
        if rel in changed or rel=="source-lock.json":
            continue
        if final[rel].is_symlink() or sha(p)!=sha(final[rel]):
            raise RuntimeError("Unrelated inherited file changed: "+rel)
    for rel,digest in changed.items():
        if final[rel].is_symlink() or sha(final[rel])!=digest:
            raise RuntimeError("Changed file is not admitted: "+rel)
    admission={
       "schema":"fountain.press.source-bound-essay-admission.v196",
       "oldRelease":OLD,"newRelease":NEW,
       "oldLockSHA256":EXPECTED_LOCK,
       "newLockSHA256":sha(new/"source-lock.json"),
       "inheritedGuardSHA256":EXPECTED_GUARD,
       "sourceSHA256":receipt["sourceSHA256"],
       "record":record,
       "changedFiles":dict(sorted(changed.items())),
       "newFiles":sorted(newfiles),
       "preservedSourceFileCount":len(inherited)-1-len(set(changed)&set(inherited)),
       "publicProductionAffected":False,
       "physicalIPadAccepted":False,
    }
    ADMISSION.write_text(json.dumps(admission,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    admission_sha=sha(ADMISSION)
    guard='''#!/usr/bin/env python3
"""v196 source-locked FCIS essay: exact v195 inheritance, no public delivery."""
from pathlib import Path
import hashlib,json,sys
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_orange_dot_direct_books_v195 as prev
original=prev.original
server=prev.server
ADMISSION=BASE/"candidates/fcis-value-essay-admission-v196.json"
ADMISSION_SHA="__ADM_SHA__"
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()
if sha(ADMISSION)!=ADMISSION_SHA:raise SystemExit("FCIS essay admission modified")
A=json.loads(ADMISSION.read_text())
if sha(Path(prev.__file__))!=A["inheritedGuardSHA256"]:
    raise SystemExit("v195 inherited server guard changed")
class FCISValueEssayV196Gate:
    def __init__(self,baseline,current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=A["newRelease"]:
            raise original.UnadmittedReaderRoute("Unexpected FCIS essay release")
        self.prior=self.current.parent/A["oldRelease"]
        if sha(self.prior/"source-lock.json")!=A["oldLockSHA256"]:
            raise original.UnadmittedReaderRoute("Essay predecessor lock changed")
        if sha(self.current/"source-lock.json")!=A["newLockSHA256"]:
            raise original.UnadmittedReaderRoute("Essay stage lock changed")
        self.inherited=prev.BookDirectLinksV195Gate(baseline,self.prior)
        earlier=json.loads((self.prior/"source-lock.json").read_text())
        new=json.loads((self.current/"source-lock.json").read_text())
        if new.pop("fcisValueEssayV196Admission",None)!=A["record"] or earlier!=new:
            raise original.UnadmittedReaderRoute("Unexpected essay source-lock change")
        old={p.relative_to(self.prior).as_posix():p for p in self.prior.rglob("*") if p.is_file()}
        newfiles={p.relative_to(self.current).as_posix():p for p in self.current.rglob("*") if p.is_file()}
        if set(newfiles)!=set(old)|set(A["newFiles"]):
            raise original.UnadmittedReaderRoute("Unadmitted essay route inventory")
        for rel,p in old.items():
            if rel=="source-lock.json" or rel in A["changedFiles"]:continue
            if newfiles[rel].is_symlink() or sha(p)!=sha(newfiles[rel]):
                raise original.UnadmittedReaderRoute("Inherited stage bytes changed "+rel)
        for rel,digest in A["changedFiles"].items():
            if newfiles[rel].is_symlink() or sha(newfiles[rel])!=digest:
                raise original.UnadmittedReaderRoute("Essay stage bytes changed "+rel)
        print("FCIS_VALUE_ESSAY_V196_ADMITTED exact source, v195 retained, staging only",flush=True)
    def check(self,raw_url):
        rel=original.normalized_request_path(raw_url)
        if rel in A["changedFiles"]:
            p=self.current/rel
            if not p.is_file() or p.is_symlink() or sha(p)!=A["changedFiles"][rel]:
                raise original.UnadmittedReaderRoute("Unadmitted FCIS essay asset")
            return
        self.inherited.check(raw_url)
if __name__=="__main__":
    server.ReaderProvenanceGate=FCISValueEssayV196Gate
    server.main()
'''
    GUARD.write_text(guard.replace("__ADM_SHA__",admission_sha))
    secure='''#!/usr/bin/env python3
from pathlib import Path
import sys
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_fcis_value_essay_v196 as essay
import serve_shared_shell_preview_https as secure
if __name__=="__main__":
    secure.ReaderProvenanceGate=essay.FCISValueEssayV196Gate
    secure.main()
'''
    # The v195 HTTPS wrapper uses imported "secure" from an earlier module.
    # Reuse its own exposed module at runtime rather than start another server.
    SECURE.write_text(secure)
    print("V196_CANDIDATE_READY",NEW,"changed",len(changed),"added",len(newfiles),"preserved",admission["preservedSourceFileCount"])
    print("SOURCE_SHA",admission["sourceSHA256"])
    print("LOCK_SHA",admission["newLockSHA256"],"ADMISSION_SHA",admission_sha)
    print("NOT_ACTIVATED_NOT_PUBLIC")
if __name__=="__main__":main()
