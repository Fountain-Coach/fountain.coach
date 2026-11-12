#!/usr/bin/env python3
"""Activate illustrated FCIS value essay v197 on existing WLAN services; rollback on failure."""
from pathlib import Path
import hashlib,json,os,subprocess,time,urllib.request
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
OLD="shared-shell-20261112-v196-fcis-value-essay-3b6fbd5"
NEW="shared-shell-20261112-v197-fcis-value-illustrated-ba6a653"
ADMISSION_SHA="2ec554159bd62c8384e9a36611d9125afdfb9999728883344d5e0dde6a024e47"
SERVICES=["fountain-shell-acceptance-preview.service","fountain-shell-acceptance-preview-https.service"]
PREFIX=Path("/home/benedikt/.config/systemd/user")
HTTP_CONF=PREFIX/"fountain-shell-acceptance-preview.service.d/zzzzzzzzzzzzz-fcis-illustrated-v197.conf"
HTTPS_CONF=PREFIX/"fountain-shell-acceptance-preview-https.service.d/zzzzzzzzzzzzz-fcis-illustrated-v197.conf"
URI="http://192.168.8.50:8200"
STAGED=BASE/"candidates"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def run(*cmd):
 return subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
def fetch(path):
 with urllib.request.urlopen(URI+path,timeout=5) as r:
  return r.status,r.read()
def main():
 current=BASE/"current"
 old=BASE/"releases"/OLD;new=BASE/"releases"/NEW
 admission=STAGED/"fcis-value-essay-admission-v197.json"
 if current.resolve()!=old or not current.is_symlink():raise RuntimeError("Expected active v196 stage has changed")
 if sha(admission)!=ADMISSION_SHA:raise RuntimeError("v197 source admission changed")
 a=json.loads(admission.read_text())
 if a["oldRelease"]!=OLD or a["newRelease"]!=NEW or sha(new/"source-lock.json")!=a["newLockSHA256"]:
  raise RuntimeError("Unexpected source-locked staged revision")
 for rel,digest in a["changedFiles"].items():
  if sha(new/rel)!=digest:raise RuntimeError("Candidate changed "+rel)
 if HTTP_CONF.exists() or HTTPS_CONF.exists():raise RuntimeError("v197 overrides already exist")
 if any(run("systemctl","--user","is-active",s).strip()!="active" for s in SERVICES):
  raise RuntimeError("Existing preview server inactive")
 status,html=fetch("/estate/")
 if status!=200 or hashlib.sha256(html).hexdigest()!=sha(old/"estate/index.html"):
  raise RuntimeError("Active predecessor HTTP mismatch")
 common="--root "+str(current)+" --bind 192.168.8.50"
 http="[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(STAGED/"serve_fcis_value_essay_v197.py")+" "+common+" --port 8200\n"
 https="[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(STAGED/"serve_secure_fcis_value_essay_v197.py")+" "+common+" --port 8243 --cert /etc/teatro-first-readings-staging/fullchain.pem --key /etc/teatro-first-readings-staging/leaf.key\n"
 try:
  for p,data in ((HTTP_CONF,http),(HTTPS_CONF,https)):
   p.parent.mkdir(parents=True,exist_ok=True)
   tmp=p.with_name("."+p.name+".tmp")
   tmp.write_text(data);os.replace(tmp,p)
  tmp=current.with_name("current-v197-atomic")
  tmp.symlink_to(new);os.replace(tmp,current)
  run("systemctl","--user","daemon-reload")
  run("systemctl","--user","restart",*SERVICES)
  essay="/estate/read/essay--the-value-of-what-we-can-prove/"
  collection="/estate/read/essays/"
  hero=essay+"assets/fcis-value-illustration.webp"
  social="/estate/assets/social/essays/the-value-of-what-we-can-prove.jpg"
  for i in range(95):
   try:
    status,html=fetch(essay)
    if status==200 and b'fcis-value.illustration.1' in html:
     c,cc=fetch(collection)
     h,original=fetch(hero)
     sc,card=fetch(social)
     if c!=200 or b'fcis-value.illustration.1' not in cc:
      raise RuntimeError("Gallery or Contents missing illustrated essay")
     if h!=200 or sc!=200:raise RuntimeError("Image routes not served")
     expected=a["record"]
     if hashlib.sha256(original).hexdigest()!=expected["sourceImageSHA256"]:
      raise RuntimeError("Hero image digest not preserved")
     if hashlib.sha256(card).hexdigest()!=expected["socialImageSHA256"]:
      raise RuntimeError("Social derivative digest not preserved")
     print("FCIS_V197_STAGE_ACTIVE",current.resolve(),flush=True)
     print("ESSAY_URL",URI+essay,status,"sha",hashlib.sha256(html).hexdigest(),flush=True)
     print("COLLECTION_URL",URI+collection,c,flush=True)
     print("HERO_URL",URI+hero,h,flush=True)
     print("SOCIAL_URL",URI+social,sc,flush=True)
     print("SOURCE_LOCK",sha(current/"source-lock.json"),"PUBLIC_UNCHANGED",flush=True)
     return
   except Exception:
    if i>=94:raise
    time.sleep(2)
  raise RuntimeError("Stage timed out")
 except BaseException as err:
  print("FCIS_V197_RESTORING_V196",type(err).__name__,str(err),flush=True)
  undo=current.with_name("current-v196-rollback")
  undo.symlink_to(old);os.replace(undo,current)
  for p in (HTTP_CONF,HTTPS_CONF):
   if p.exists():p.unlink()
  run("systemctl","--user","daemon-reload")
  run("systemctl","--user","restart",*SERVICES)
  print("FCIS_V196_RESTORED",current.resolve(),flush=True)
  raise
if __name__=="__main__":main()
