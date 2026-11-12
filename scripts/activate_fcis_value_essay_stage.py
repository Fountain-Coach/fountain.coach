#!/usr/bin/env python3
"""Activate one preaccepted, immutable FCIS-value essay stage with rollback.

No public release, no new service, no removal of predecessor files.
"""
from pathlib import Path
import hashlib,json,os,subprocess,time,urllib.request
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
OLD="shared-shell-20261111-v195-direct-books-social-5227c32"
NEW="shared-shell-20261112-v196-fcis-value-essay-3b6fbd5"
EXPECTED_ADMISSION="683571b3b3138aa11cbcf81f084a465f0870f43afe5f21be60560fd672de173d"
SERVICES=["fountain-shell-acceptance-preview.service","fountain-shell-acceptance-preview-https.service"]
PREFIX=Path("/home/benedikt/.config/systemd/user")
HTTP_CONF=PREFIX/("fountain-shell-acceptance-preview.service.d/zzzzzzzzzzzz-fcis-value-v196.conf")
HTTPS_CONF=PREFIX/("fountain-shell-acceptance-preview-https.service.d/zzzzzzzzzzzz-fcis-value-v196.conf")
URI="http://192.168.8.50:8200"
CANDIDATES=BASE/"candidates"

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def run(*args):
 return subprocess.run(args,check=True,text=True,capture_output=True).stdout

def http_fetch(url):
 with urllib.request.urlopen(url,timeout=4) as f:
  return f.status,f.read()

def main():
 current=BASE/"current"
 old=BASE/"releases"/OLD
 new=BASE/"releases"/NEW
 if not current.is_symlink() or current.resolve()!=old:
  raise RuntimeError("Active predecessor changed: refusing switch")
 if sha(CANDIDATES/"fcis-value-essay-admission-v196.json")!=EXPECTED_ADMISSION:
  raise RuntimeError("Admission source changed")
 a=json.loads((CANDIDATES/"fcis-value-essay-admission-v196.json").read_text())
 if a["oldRelease"]!=OLD or a["newRelease"]!=NEW or sha(new/"source-lock.json")!=a["newLockSHA256"]:
  raise RuntimeError("Candidate source-lock changed")
 for rel,digest in a["changedFiles"].items():
  if sha(new/rel)!=digest:raise RuntimeError("Changed candidate asset drift: "+rel)
 if HTTP_CONF.exists() or HTTPS_CONF.exists():
  raise RuntimeError("Conflicting v196 service override")
 if any(run("systemctl","--user","is-active",service).strip()!="active" for service in SERVICES):
  raise RuntimeError("Expected existing stage services not running")
 before_status, before_content=http_fetch(URI+"/estate/")
 if before_status!=200 or hashlib.sha256(before_content).hexdigest()!=sha(old/"estate/index.html"):
  raise RuntimeError("Public WLAN staging predecessor not exact")
 common="--root "+str(current)+" --bind 192.168.8.50"
 http="[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(CANDIDATES/"serve_fcis_value_essay_v196.py")+" "+common+" --port 8200\n"
 https="[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(CANDIDATES/"serve_secure_fcis_value_essay_v196.py")+" "+common+" --port 8243 --cert /etc/teatro-first-readings-staging/fullchain.pem --key /etc/teatro-first-readings-staging/leaf.key\n"
 try:
  for p,contents in [(HTTP_CONF,http),(HTTPS_CONF,https)]:
   p.parent.mkdir(parents=True,exist_ok=True)
   tmp=p.with_name("."+p.name+".tmp")
   tmp.write_text(contents)
   os.replace(tmp,p)
  symlink=current.with_name("current-v196-atomic")
  symlink.symlink_to(new)
  os.replace(symlink,current)
  run("systemctl","--user","daemon-reload")
  run("systemctl","--user","restart",*SERVICES)
  target=URI+"/estate/read/essay--the-value-of-what-we-can-prove/"
  collect=URI+"/estate/read/essays/"
  for i in range(80):
   try:
    result, html=http_fetch(target)
    if result==200 and b"fcis-value.possession.heading" in html:
     code,other=http_fetch(collect)
     if code!=200 or b'The Value of What We Can Prove' not in other:
      raise RuntimeError("Staged Essays collection incorrect")
     lock=sha(current/"source-lock.json")
     print("V196_STAGE_ACTIVE",current.resolve())
     print("ESSAY_HTTP",target,result,"sha256",hashlib.sha256(html).hexdigest())
     print("ESSAYS_HTTP",collect,code,"sha256",hashlib.sha256(other).hexdigest())
     print("LOCK_SHA",lock)
     print("PRIVATE_ONLY_PUBLIC_UNCHANGED")
     return
   except Exception as err:
    if i>=79:raise
    time.sleep(2)
  raise RuntimeError("Stage readback timed out")
 except Exception as err:
  print("V196_STAGE_FAILED_ROLLING_BACK",type(err).__name__,str(err),flush=True)
  backup=current.with_name("current-v195-rollback")
  backup.symlink_to(old)
  os.replace(backup,current)
  for p in (HTTP_CONF,HTTPS_CONF):
   if p.exists():p.unlink()
  run("systemctl","--user","daemon-reload")
  run("systemctl","--user","restart",*SERVICES)
  print("RESTORED_V195",current.resolve(),flush=True)
  raise

if __name__=="__main__":main()
