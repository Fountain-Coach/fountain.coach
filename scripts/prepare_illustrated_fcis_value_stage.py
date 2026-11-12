#!/usr/bin/env python3
"""Prepare immutable v197 illustrated FCIS essay staging against verified v196."""
from pathlib import Path
import hashlib,json,os,subprocess

BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
OLD="shared-shell-20261112-v196-fcis-value-essay-3b6fbd5"
NEW="shared-shell-20261112-v197-fcis-value-illustrated-ba6a653"
OLD_LOCK="c8378f30a47dcc36ffa43c5a2703f2f81c99837aa38ffabf5e1b61f51bd86060"
PREV_GUARD_SHA="180788158985132144b453d00215c8890f09171b4365f58283a929acd9274baf"
REV="ba6a6531d82934a52a6ac63e6f39cc477992b803"
OVERLAY=BASE/"candidates/fcis-value-essay-v197-overlay"
ADMISSION=BASE/"candidates/fcis-value-essay-admission-v197.json"
GUARD=BASE/"candidates/serve_fcis_value_essay_v197.py"
SECURE=BASE/"candidates/serve_secure_fcis_value_essay_v197.py"
PRIOR_GUARD=BASE/"candidates/serve_fcis_value_essay_v196.py"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for part in iter(lambda:f.read(1048576),b""):h.update(part)
 return h.hexdigest()
def main():
 old=BASE/"releases"/OLD;new=BASE/"releases"/NEW;current=BASE/"current"
 if not current.is_symlink() or current.resolve()!=old:raise RuntimeError("Staging predecessor changed")
 if not old.is_dir() or new.exists() or any(p.exists() for p in (ADMISSION,GUARD,SECURE)):
  raise RuntimeError("Refuse existing candidate/admission")
 if sha(old/"source-lock.json")!=OLD_LOCK or sha(PRIOR_GUARD)!=PREV_GUARD_SHA:
  raise RuntimeError("v196 source/guard drift")
 receipt=json.loads((OVERLAY/"build-receipt.json").read_text())
 if receipt["sourceRevision"]!=REV or not receipt["stagingOnly"] or receipt["publicReleaseAuthorized"]:
  raise RuntimeError("Unexpected manuscript rights or source revision")
 source=BASE/"candidates/fcis-value-essay-v197-input/source.html"
 hero=BASE/"candidates/fcis-value-essay-v197-input/hero.webp"
 social=BASE/"candidates/fcis-value-essay-v197-input/social.jpg"
 if sha(source)!=receipt["sourceSHA256"] or sha(hero)!=receipt["heroSourceSHA256"] or sha(social)!=receipt["socialDerivativeSHA256"]:
  raise RuntimeError("Authored media/source bytes changed")
 changed=receipt["changedFiles"]
 if len(changed)!=12:raise RuntimeError("Unexpected edited path inventory")
 for rel,digest in changed.items():
  p=OVERLAY/rel
  if not p.is_file() or p.is_symlink() or sha(p)!=digest:raise RuntimeError("Overlay drift: "+rel)
 oldfiles={p.relative_to(old).as_posix():p for p in old.rglob("*") if p.is_file()}
 newfiles=set(changed)-set(oldfiles)
 if len(newfiles)!=3 or "estate/index.html" not in changed or "estate/books/catalog.json" not in changed:
  raise RuntimeError("Unexpected additions for source image/catalog")
 subprocess.run(["cp","-a","-l",str(old),str(new)],check=True)
 for rel,digest in sorted(changed.items()):
  dest=new/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  temp=dest.with_name("."+dest.name+".v197-tmp")
  temp.write_bytes((OVERLAY/rel).read_bytes())
  os.replace(temp,dest)
  if sha(dest)!=digest:raise RuntimeError("Changed file SHA mismatch")
 earlier=json.loads((old/"source-lock.json").read_text())
 if "fcisValueEssayIllustrationV197" in earlier:raise RuntimeError("Duplicate admission")
 record={
   "schema":"fountain.press.illustrated-essay-stage.v197",
   "sourceOwner":"Fountain-Coach/fountain.coach",
   "sourceRevision":REV,"sourceSHA256":receipt["sourceSHA256"],
   "sourceImageSHA256":receipt["heroSourceSHA256"],
   "socialImageSHA256":receipt["socialDerivativeSHA256"],
   "workId":"essay--the-value-of-what-we-can-prove",
   "oldRelease":OLD,"newRelease":NEW,
   "originalManuscriptTextUnchanged":True,
   "oldGalleryAndOtherCollectionAssetsPreserved":True,
   "shareImage":"same-source-art-1200x630",
   "changedFiles":dict(sorted(changed.items())),
   "publicReleaseAuthorized":False,"stagingOnly":True,
 }
 updated=dict(earlier);updated["fcisValueEssayIllustrationV197"]=record
 tmp=new/".source-lock-v197-tmp"
 tmp.write_text(json.dumps(updated,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 os.replace(tmp,new/"source-lock.json")
 final={p.relative_to(new).as_posix():p for p in new.rglob("*") if p.is_file()}
 if set(final)!=set(oldfiles)|newfiles:raise RuntimeError("Stage file inventory changed")
 for rel,p in oldfiles.items():
  if rel in changed or rel=="source-lock.json":continue
  if final[rel].is_symlink() or sha(p)!=sha(final[rel]):raise RuntimeError("Unrelated inherited file changed "+rel)
 for rel,digest in changed.items():
  if final[rel].is_symlink() or sha(final[rel])!=digest:raise RuntimeError("Unadmitted file changed "+rel)
 admission={
  "schema":"fountain.press.illustrated-essay-admission.v197",
  "oldRelease":OLD,"newRelease":NEW,
  "oldLockSHA256":OLD_LOCK,"newLockSHA256":sha(new/"source-lock.json"),
  "inheritedGuardSHA256":PREV_GUARD_SHA,"sourceRevision":REV,
  "record":record,"changedFiles":dict(sorted(changed.items())),
  "newFiles":sorted(newfiles),
  "preservedSourceFileCount":len(oldfiles)-1-len(set(changed)&set(oldfiles)),
  "publicProductionAffected":False,"physicalIPadAccepted":False
 }
 ADMISSION.write_text(json.dumps(admission,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 adm_sha=sha(ADMISSION)
 guard='''#!/usr/bin/env python3
"""v197 illustration guard inherits exact previous private staging provenance."""
from pathlib import Path
import hashlib,json,sys
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_fcis_value_essay_v196 as previous
original=previous.original
server=previous.server
ADMISSION=BASE/"candidates/fcis-value-essay-admission-v197.json"
EXPECTED="__ADM_SHA__"
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
if sha(ADMISSION)!=EXPECTED:raise SystemExit("Illustration admission changed")
A=json.loads(ADMISSION.read_text())
if sha(Path(previous.__file__))!=A["inheritedGuardSHA256"]:
 raise SystemExit("Previous v196 guard changed")
class IllustratedValueEssayV197Gate:
 def __init__(self,baseline,current):
  self.current=Path(current).resolve(strict=True)
  if self.current.name!=A["newRelease"]:
   raise original.UnadmittedReaderRoute("Wrong illustrated essay release")
  self.prior=self.current.parent/A["oldRelease"]
  if sha(self.prior/"source-lock.json")!=A["oldLockSHA256"] or sha(self.current/"source-lock.json")!=A["newLockSHA256"]:
   raise original.UnadmittedReaderRoute("Source-lock drift")
  self.inherited=previous.FCISValueEssayV196Gate(baseline,self.prior)
  old=json.loads((self.prior/"source-lock.json").read_text())
  updated=json.loads((self.current/"source-lock.json").read_text())
  if updated.pop("fcisValueEssayIllustrationV197",None)!=A["record"] or updated!=old:
   raise original.UnadmittedReaderRoute("Unexpected book source-lock")
  before={p.relative_to(self.prior).as_posix():p for p in self.prior.rglob("*") if p.is_file()}
  now={p.relative_to(self.current).as_posix():p for p in self.current.rglob("*") if p.is_file()}
  if set(now)!=set(before)|set(A["newFiles"]):
   raise original.UnadmittedReaderRoute("Unexpected stage files")
  for rel,p in before.items():
   if rel in A["changedFiles"] or rel=="source-lock.json":continue
   if now[rel].is_symlink() or sha(p)!=sha(now[rel]):
    raise original.UnadmittedReaderRoute("Inherited file changed "+rel)
  for rel,digest in A["changedFiles"].items():
   if now[rel].is_symlink() or sha(now[rel])!=digest:
    raise original.UnadmittedReaderRoute("Illustrated source file drift "+rel)
  print("FCIS_ESSAY_V197_ADMITTED hero and source-derived social; staged only",flush=True)
 def check(self,raw_url):
  rel=original.normalized_request_path(raw_url)
  if rel in A["changedFiles"]:
   p=self.current/rel
   if p.is_symlink() or not p.is_file() or sha(p)!=A["changedFiles"][rel]:
    raise original.UnadmittedReaderRoute("Unadmitted image/essay route")
   return
  self.inherited.check(raw_url)
if __name__=="__main__":
 server.ReaderProvenanceGate=IllustratedValueEssayV197Gate
 server.main()
'''
 GUARD.write_text(guard.replace("__ADM_SHA__",adm_sha))
 SECURE.write_text('''#!/usr/bin/env python3
from pathlib import Path
import sys
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
sys.path.insert(0,str(BASE/"candidates"))
import serve_fcis_value_essay_v197 as essay
import serve_shared_shell_preview_https as secure
if __name__=="__main__":
 secure.ReaderProvenanceGate=essay.IllustratedValueEssayV197Gate
 secure.main()
''')
 print("ILLUSTRATED_V197_CANDIDATE_READY",NEW,"changed",len(changed),"added",len(newfiles),"preserved",admission["preservedSourceFileCount"])
 print("LOCK",admission["newLockSHA256"],"ADMISSION",adm_sha,"NOT_ACTIVE_NOT_PUBLIC")
if __name__=="__main__":main()
