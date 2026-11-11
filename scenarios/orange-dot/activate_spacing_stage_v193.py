#!/usr/bin/env python3
"""Atomic activation of already source-admitted Orange Dot v193 on owner WLAN.

Preserves current v192b predecessor for rollback and both canonical services.
This script is staging-only; it never publishes to public Fountain Press.
"""
from pathlib import Path
import hashlib,os,subprocess,time,urllib.request,ssl,sys

BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
OLD="shared-shell-20261111-v192b-satzfunk-listening-64f5263"
NEW="shared-shell-20261111-v193-orange-dot-portrait-spacing-b431528"
ENGINE="estate/assets/linotype/reading-first-press-engine.js"
NEW_ENGINE_SHA="837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a"
LOCK_SHA="ab24cd67a668153a6d8fbc3ba599090bda1e037327920053deb0607149b93de0"
ADMISSION_SHA="904251c6506c2944d15d85e6929de3866177097da1ac9e75e86d122cf4a4bbcb"
CURRENT=BASE/"current"
GUARD=BASE/"candidates/serve_orange_dot_spacing_v193.py"
SECURE=BASE/"candidates/serve_secure_orange_dot_spacing_v193.py"
ADMISSION=BASE/"candidates/orange-dot-figure-spacing-admission-v193.json"
HTTP="fountain-shell-acceptance-preview.service"
HTTPS="fountain-shell-acceptance-preview-https.service"
CONF=Path.home()/".config/systemd/user"
D1=CONF/(HTTP+".d")/"zzzzzzzzz-orange-dot-v193.conf"
D2=CONF/(HTTPS+".d")/"zzzzzzzzz-orange-dot-v193.conf"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for data in iter(lambda:f.read(1048576),b""):h.update(data)
    return h.hexdigest()
def cmd(*a):subprocess.run(a,check=True)
def switch(release):
    temp=BASE/".orange-dot-v193-symlink-next"
    temp.unlink(missing_ok=True)
    os.symlink(str(BASE/"releases"/release),temp)
    os.replace(temp,CURRENT)
    assert CURRENT.resolve().name==release
def read(url):
    ctx=ssl._create_unverified_context() if url.startswith("https://") else None
    try:
        req=urllib.request.Request(url,headers={"Cache-Control":"no-store"})
        with urllib.request.urlopen(req,timeout=5,context=ctx) as r:
            return r.status,r.read()
    except Exception:return 0,b""
def ready():
    for scheme,port in (("http",8200),("https",8243)):
        base=f"{scheme}://192.168.8.50:{port}"
        status,html=read(base+"/estate/")
        if status!=200 or b"orange-dot" not in html:return False
        status,engine=read(base+"/"+ENGINE)
        if status!=200 or hashlib.sha256(engine).hexdigest()!=NEW_ENGINE_SHA:return False
        status,asset=read(base+"/estate/assets/orange-dot/orange-dot--2026-01-22-the-vigilance-regulator-02-b5da722ce9f6c7.jpg")
        if status!=200 or len(asset)<10000:return False
    return True
def main():
    assert CURRENT.is_symlink() and CURRENT.resolve().name==OLD,"Active stage changed; refuse overlap"
    assert sha(BASE/"releases"/NEW/ENGINE)==NEW_ENGINE_SHA
    assert sha(BASE/"releases"/NEW/"source-lock.json")==LOCK_SHA
    assert sha(ADMISSION)==ADMISSION_SHA
    assert GUARD.is_file() and SECURE.is_file()
    assert not D1.exists() and not D2.exists(),"Existing v193 override: no duplicate activation"
    D1.parent.mkdir(parents=True,exist_ok=True)
    D2.parent.mkdir(parents=True,exist_ok=True)
    D1.write_text("[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(GUARD)+" --root "+str(CURRENT)+" --bind 192.168.8.50 --port 8200\n")
    D2.write_text("[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(SECURE)+" --root "+str(CURRENT)+" --bind 192.168.8.50 --port 8243 --cert /etc/teatro-first-readings-staging/fullchain.pem --key /etc/teatro-first-readings-staging/leaf.key\n")
    try:
        switch(NEW)
        print("SWITCHED",NEW,flush=True)
        cmd("systemctl","--user","daemon-reload")
        cmd("systemctl","--user","restart",HTTP,HTTPS)
        print("VALIDATING inherited guard on canonical HTTP + HTTPS",flush=True)
        start=time.monotonic()
        while time.monotonic()-start<480:
            if ready():
                print("ORANGE_DOT_V193_LIVE_ACCEPTED both canonical lanes, one Reader patch, v192b rollback",flush=True)
                return
            time.sleep(5)
        raise RuntimeError("Live reader engine and original image readback did not complete")
    except Exception:
        print("REVERTING v193 to v192b",file=sys.stderr,flush=True)
        switch(OLD)
        D1.unlink(missing_ok=True);D2.unlink(missing_ok=True)
        cmd("systemctl","--user","daemon-reload")
        cmd("systemctl","--user","restart",HTTP,HTTPS)
        raise
if __name__=="__main__":main()
