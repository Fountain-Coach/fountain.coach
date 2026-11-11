#!/usr/bin/env python3
"""Activate one source-admitted production-shaped Orange Dot on canonical owner WLAN.
No public estate mutation. Roll back atomically to v193 on readback failure.
"""
import hashlib
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
CURRENT=BASE/"current"
OLD="shared-shell-20261111-v193-orange-dot-portrait-spacing-b431528"
NEW="shared-shell-20261111-v194b-orange-dot-production-bookshelf-kino-007ca1c"
GUARD=BASE/"candidates/serve_orange_dot_production_bookshelf_v194b.py"
SECURE=BASE/"candidates/serve_secure_orange_dot_production_bookshelf_v194b.py"
ADMISSION=BASE/"candidates/orange-dot-production-bookshelf-admission-v194b.json"
LOCK_SHA="3e815168392fb990c4749a33ba01befea5ea4e2e3777253f52a5c4c5761acb4a"
ADMISSION_SHA="320f04a5a0a0cf36e6a643d6c7bdca090a03b73fe76657f54590ab0427243299"
HTML_SHA="7db826d5aa32da727213ce2d53dc1e1a35efe5ee820c987ae6066e2dd1500f3b"
APP="estate/assets/linotype/reading-first-app.d2c2020390a35d7def6409abf50171e1998a0f1baa4bf8da3cbaf50bc3aa1a81.js"
ENGINE="estate/assets/linotype/reading-first-press-engine.837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a.js"
HTTP="fountain-shell-acceptance-preview.service"
HTTPS="fountain-shell-acceptance-preview-https.service"
CONF=Path.home()/".config/systemd/user"
D1=CONF/(HTTP+".d")/"zzzzzzzzzz-orange-production-bookshelf-v194b.conf"
D2=CONF/(HTTPS+".d")/"zzzzzzzzzz-orange-production-bookshelf-v194b.conf"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def call(*args):
    subprocess.run(args,check=True)

def switch(name):
    tmp=BASE/".orange-production-bookshelf-v194b-switch"
    tmp.unlink(missing_ok=True)
    os.symlink(str(BASE/"releases"/name),tmp)
    os.replace(tmp,CURRENT)
    assert CURRENT.resolve().name==name

def fetch(url):
    ctx=ssl._create_unverified_context() if url.startswith("https://") else None
    try:
        request=urllib.request.Request(url,headers={"Cache-Control":"no-store"})
        with urllib.request.urlopen(request,timeout=5,context=ctx) as response:
            return response.status,response.read()
    except (urllib.error.URLError,TimeoutError,OSError):
        return 0,b""

def ready():
    for scheme,port in (("http",8200),("https",8243)):
        base=f"{scheme}://192.168.8.50:{port}"
        status,index=fetch(base+"/estate/")
        if status!=200 or hashlib.sha256(index).hexdigest()!=HTML_SHA:
            return False
        for asset in (APP,ENGINE):
            status,data=fetch(base+"/"+asset)
            if status!=200 or sha(BASE/"releases"/NEW/asset)!=hashlib.sha256(data).hexdigest():
                return False
        for edition in ("history","sound-craft"):
            status,data=fetch(base+"/estate/media/kino/"+edition+"/edition.json")
            if status!=200 or b'"publicReleaseAuthorized": true' not in data:
                return False
    return True

def main():
    assert CURRENT.is_symlink() and CURRENT.resolve().name==OLD,"Active stage changed; do not overwrite"
    assert sha(BASE/"releases"/NEW/"source-lock.json")==LOCK_SHA
    assert sha(ADMISSION)==ADMISSION_SHA
    assert sha(BASE/"releases"/NEW/"estate/index.html")==HTML_SHA
    assert GUARD.is_file() and SECURE.is_file()
    assert not D1.exists() and not D2.exists(),"Existing override; do not duplicate"
    D1.parent.mkdir(parents=True,exist_ok=True)
    D2.parent.mkdir(parents=True,exist_ok=True)
    D1.write_text("[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(GUARD)+" --root "+str(CURRENT)+" --bind 192.168.8.50 --port 8200\n")
    D2.write_text("[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(SECURE)+" --root "+str(CURRENT)+" --bind 192.168.8.50 --port 8243 --cert /etc/teatro-first-readings-staging/fullchain.pem --key /etc/teatro-first-readings-staging/leaf.key\n")
    try:
        switch(NEW)
        print("SWITCHED",NEW,flush=True)
        call("systemctl","--user","daemon-reload")
        call("systemctl","--user","restart",HTTP,HTTPS)
        start=time.monotonic()
        while time.monotonic()-start<540:
            if ready():
                print("CANONICAL_BOOKSHELF_V194B_READBACK_OK HTTP HTTPS",flush=True)
                print("RETAINED_ROLLBACK",OLD,flush=True)
                return
            time.sleep(5)
        raise RuntimeError("Canonical production-shaped Bookshelf did not pass readback")
    except Exception:
        print("ROLLBACK_TO",OLD,file=sys.stderr,flush=True)
        switch(OLD)
        D1.unlink(missing_ok=True)
        D2.unlink(missing_ok=True)
        call("systemctl","--user","daemon-reload")
        call("systemctl","--user","restart",HTTP,HTTPS)
        raise

if __name__=="__main__":
    main()
