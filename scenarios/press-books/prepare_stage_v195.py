#!/usr/bin/env python3
"""Admit three stable Fountain Press book URLs + source-art social derivatives.

Source-bound to production-derived v194b on canonical owner WLAN. Immutable
v195 staged successor; v194b rollback remains untouched. No public delivery,
new authority, rights admission or rewriting any original manuscript/media.
"""
import hashlib,json,os,subprocess
from pathlib import Path
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
OLD="shared-shell-20261111-v194b-orange-dot-production-bookshelf-kino-007ca1c"
NEW="shared-shell-20261111-v195-direct-books-social-5227c32"
PREV_LOCK="3e815168392fb990c4749a33ba01befea5ea4e2e3777253f52a5c4c5761acb4a"
PREV_GUARD="3edb10bb6d5cc67f9f8e40aadfa80eff891f0045fe437df85ec20b07b6c87402"
BUILD_RECEIPT="06dd20b00ceee50d17f42b2f066d534c3a4a5ec1ce674fb98ae2cb3402eb0cb5"
SOURCE=BASE/"candidates/orange-dot-direct-books-v195b-source"
ADMISSION=BASE/"candidates/orange-dot-direct-books-admission-v195.json"
GUARD=BASE/"candidates/serve_orange_dot_direct_books_v195.py"
SECURE=BASE/"candidates/serve_secure_orange_dot_direct_books_v195.py"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for v in iter(lambda:f.read(1048576),b""):h.update(v)
    return h.hexdigest()

def main():
    current=BASE/"current"
    old=BASE/"releases"/OLD
    new=BASE/"releases"/NEW
    assert current.is_symlink() and current.resolve()==old,"Canonical staging release has changed"
    assert not new.exists() and not ADMISSION.exists() and not GUARD.exists() and not SECURE.exists()
    assert sha(old/"source-lock.json")==PREV_LOCK
    assert sha(BASE/"candidates/serve_orange_dot_production_bookshelf_v194b.py")==PREV_GUARD
    assert sha(SOURCE/"source-direct-book-build-receipt.json")==BUILD_RECEIPT
    receipt=json.loads((SOURCE/"source-direct-book-build-receipt.json").read_text())
    assert receipt["sourceRootHTMLSHA256"]=="7db826d5aa32da727213ce2d53dc1e1a35efe5ee820c987ae6066e2dd1500f3b"
    assert sha(old/"estate/index.html")==receipt["sourceRootHTMLSHA256"]
    assert sha(old/"estate/assets/linotype/reading-first-app.d2c2020390a35d7def6409abf50171e1998a0f1baa4bf8da3cbaf50bc3aa1a81.js")==receipt["sourceReaderAppSHA256"]
    assert sha(old/"estate/assets/linotype/reading-first-shell.css")==receipt["sourceReaderCSSSHA256"]
    paths=receipt["stagedFiles"]
    assert len(paths)==10
    for rel,h in paths.items():
        assert (SOURCE/rel).is_file() and not (SOURCE/rel).is_symlink() and sha(SOURCE/rel)==h,rel
    catalog=json.loads((SOURCE/"estate/books/catalog.json").read_text())
    assert catalog["schema"]=="fountain.press.book-direct-links.v1"
    assert [b["id"] for b in catalog["books"]]==["essays","first-readings","orange-dot"]
    assert all(b["stageOnly"] and b["publicReleaseAuthorized"] is False for b in catalog["books"])
    assert all(b["socialImageDimensions"]==[1200,630] for b in catalog["books"])
    for b in catalog["books"]:
        assert sha(old/b["firstChapterOriginalImagePath"].lstrip("/"))==b["firstChapterOriginalImageSHA256"]
    assert all(x not in (SOURCE/"estate/index.html").read_text() for x in
               ('data-reader-volume="governance"','data-reader-volume="scores"','data-reader-volume="score--between-gardens"'))
    subprocess.run(["cp","-a","-l",str(old),str(new)],check=True)
    changed={}
    added=[]
    for rel,h in sorted(paths.items()):
        target=new/rel
        if not target.exists():added.append(rel)
        target.parent.mkdir(parents=True,exist_ok=True)
        tmp=target.with_name("."+target.name+".v195-tmp")
        tmp.write_bytes((SOURCE/rel).read_bytes())
        os.replace(tmp,target)
        assert sha(target)==h
        changed[rel]=h
    oldlock=json.loads((old/"source-lock.json").read_text())
    assert "fountainBookDirectLinksV195" not in oldlock
    record={
      "schema":"fountain.press.book-direct-links-stage.v195",
      "sourceOwner":"Fountain-Coach/fountain.coach",
      "sourceGitRevision":"5227c32",
      "sourceBuildReceiptSHA256":BUILD_RECEIPT,
      "bookCatalogSHA256":sha(SOURCE/"estate/books/catalog.json"),
      "oldRelease":OLD,"newRelease":NEW,
      "bookIDs":["essays","first-readings","orange-dot"],
      "bookRoutes":["/estate/books/essays/","/estate/books/first-readings/","/estate/books/orange-dot/"],
      "firstIllustrationPolicy":"first-admitted-illustrated-chapter-source-sha",
      "originalWorksUnmodified":True,"governanceIndependent":True,
      "publicRightsGranted":False,"publicDeployment":False,
      "newOrUpdatedFiles":dict(sorted(changed.items())),
    }
    newlock=dict(oldlock)
    newlock["fountainBookDirectLinksV195"]=record
    tmp=new/".source-lock-v195-tmp"
    tmp.write_text(json.dumps(newlock,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    os.replace(tmp,new/"source-lock.json")
    previous_files={p.relative_to(old).as_posix():p for p in old.rglob("*") if p.is_file()}
    new_files={p.relative_to(new).as_posix():p for p in new.rglob("*") if p.is_file()}
    assert set(new_files)==set(previous_files)|set(added)
    for rel,p in previous_files.items():
        if rel in changed or rel=="source-lock.json":continue
        assert not new_files[rel].is_symlink() and sha(p)==sha(new_files[rel]),rel
    admission={
      "schema":"fountain.press.book-direct-links-admission.v195",
      "oldRelease":OLD,"newRelease":NEW,
      "oldLockSHA256":PREV_LOCK,"newLockSHA256":sha(new/"source-lock.json"),
      "inheritedGuardSHA256":PREV_GUARD,
      "record":record,"changedFiles":changed,"newFiles":added,
      "preservedSourceFileCount":len(previous_files)-1-len(set(changed)&set(previous_files)),
      "publicProductionAffected":False,
      "physicalIPadAccepted":False
    }
    ADMISSION.write_text(json.dumps(admission,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    adm_sha=sha(ADMISSION)
    guard='''#!/usr/bin/env python3
"""v195 inherits exact prior private staging source guard; permits book derivatives."""
from pathlib import Path
import hashlib,json,sys
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_orange_dot_production_bookshelf_v194b as prev
original=prev.original
server=prev.server
ADMISSION=BASE/"candidates/orange-dot-direct-books-admission-v195.json"
ADM_SHA="__ADM_SHA__"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for v in iter(lambda:f.read(1048576),b""):h.update(v)
    return h.hexdigest()
if sha(ADMISSION)!=ADM_SHA:raise SystemExit("Book link admission changed")
A=json.loads(ADMISSION.read_text())
if sha(Path(prev.__file__))!=A["inheritedGuardSHA256"]:raise SystemExit("v194b source guard changed")
class BookDirectLinksV195Gate:
    def __init__(self,baseline,current):
        self.current=Path(current).resolve(strict=True)
        if self.current.name!=A["newRelease"]:
            raise original.UnadmittedReaderRoute("Unexpected direct book release")
        self.prior=self.current.parent/A["oldRelease"]
        if sha(self.prior/"source-lock.json")!=A["oldLockSHA256"]:
            raise original.UnadmittedReaderRoute("Previous book source-lock changed")
        if sha(self.current/"source-lock.json")!=A["newLockSHA256"]:
            raise original.UnadmittedReaderRoute("New book source-lock changed")
        self.inherited=prev.OrangeDotBookshelfV194BGate(baseline,self.prior)
        old=json.loads((self.prior/"source-lock.json").read_text())
        new=json.loads((self.current/"source-lock.json").read_text())
        if new.pop("fountainBookDirectLinksV195",None)!=A["record"] or old!=new:
            raise original.UnadmittedReaderRoute("Unexpected book source-lock delta")
        oldfiles={p.relative_to(self.prior).as_posix():p for p in self.prior.rglob("*") if p.is_file()}
        newfiles={p.relative_to(self.current).as_posix():p for p in self.current.rglob("*") if p.is_file()}
        if set(newfiles)!=set(oldfiles)|set(A["newFiles"]):
            raise original.UnadmittedReaderRoute("Unadmitted book file inventory")
        for rel,p in oldfiles.items():
            if rel in A["changedFiles"] or rel=="source-lock.json":continue
            if newfiles[rel].is_symlink() or sha(p)!=sha(newfiles[rel]):
                raise original.UnadmittedReaderRoute("Inherited private material altered "+rel)
        for rel,h in A["changedFiles"].items():
            if newfiles[rel].is_symlink() or sha(newfiles[rel])!=h:
                raise original.UnadmittedReaderRoute("Book social asset altered "+rel)
        print("BOOK_DIRECT_LINKS_V195_ADMITTED 3 books 3 original-figure social assets 10 files no public deployment",flush=True)
    def check(self,raw_url):
        rel=original.normalized_request_path(raw_url)
        if rel in A["changedFiles"]:
            p=self.current/rel
            if not p.is_file() or p.is_symlink() or sha(p)!=A["changedFiles"][rel]:
                raise original.UnadmittedReaderRoute("Book direct route or social image tampered")
            return
        self.inherited.check(raw_url)
if __name__=="__main__":
    server.ReaderProvenanceGate=BookDirectLinksV195Gate
    server.main()
'''
    GUARD.write_text(guard.replace("__ADM_SHA__",adm_sha))
    SECURE.write_text('''#!/usr/bin/env python3
from pathlib import Path
import sys
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_orange_dot_direct_books_v195 as books
import serve_shared_shell_preview_https as secure
if __name__=="__main__":
    secure.ReaderProvenanceGate=books.BookDirectLinksV195Gate
    secure.main()
''')
    print("BOOKS_V195_CANDIDATE_READY",NEW,"changed",len(changed),"added",len(added),
          "preserved",admission["preservedSourceFileCount"],flush=True)
    print("LOCK",admission["newLockSHA256"],"ADMISSION",adm_sha,flush=True)
    print("NOT_ACTIVATED",flush=True)

if __name__=="__main__":main()
