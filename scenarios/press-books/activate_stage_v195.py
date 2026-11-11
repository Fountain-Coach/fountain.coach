#!/usr/bin/env python3
"""Activate already-admitted v195 book sharing on canonical owner-WLAN staging.
V194b remains rollback. A stale admission or failed live readback restores it.
No public SSH/Caddy change and no public rights claim.
"""
import hashlib,os,ssl,subprocess,sys,time,urllib.error,urllib.request
from pathlib import Path
BASE=Path("/home/benedikt/estate-shell-acceptance-staging")
CURRENT=BASE/"current"
OLD="shared-shell-20261111-v194b-orange-dot-production-bookshelf-kino-007ca1c"
NEW="shared-shell-20261111-v195-direct-books-social-5227c32"
ADMISSION=BASE/"candidates/orange-dot-direct-books-admission-v195.json"
ADMISSION_SHA="63a9331e7fde3c028ea9f48598cad7669edf63a9ae70fd75ea3e76518fae46f1"
LOCK_SHA="71eae0d19d032617ba80ee4d9ef749d62fa04c8c1b32ec129a03cef2306152e5"
GUARD=BASE/"candidates/serve_orange_dot_direct_books_v195.py"
SECURE=BASE/"candidates/serve_secure_orange_dot_direct_books_v195.py"
HTTP="fountain-shell-acceptance-preview.service"
HTTPS="fountain-shell-acceptance-preview-https.service"
CONF=Path.home()/".config/systemd/user"
D1=CONF/(HTTP+".d")/"zzzzzzzzzzz-book-direct-links-v195.conf"
D2=CONF/(HTTPS+".d")/"zzzzzzzzzzz-book-direct-links-v195.conf"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()
def call(*args):subprocess.run(args,check=True)
def switch(release):
    temp=BASE/".direct-books-v195-symlink-next"
    temp.unlink(missing_ok=True)
    os.symlink(str(BASE/"releases"/release),temp)
    os.replace(temp,CURRENT)
    assert CURRENT.resolve().name==release
def get(host,route):
    ctx=ssl._create_unverified_context() if host.startswith("https://") else None
    try:
        request=urllib.request.Request(host+route,headers={"Cache-Control":"no-store"})
        with urllib.request.urlopen(request,context=ctx,timeout=6) as response:
            return response.status,response.read()
    except (OSError,TimeoutError,urllib.error.URLError):
        return 0,b""
def ready():
    for scheme,port in (("http",8200),("https",8243)):
        base=f"{scheme}://192.168.8.50:{port}"
        for col in ("essays","first-readings","orange-dot"):
            status,body=get(base,"/estate/books/"+col+"/")
            if status!=200:return False
            if f'data-initial-volume="{col}"'.encode() not in body:return False
            if f'og:url" content="https://fountain.coach/estate/books/{col}/"'.encode() not in body:return False
        code,body=get(base,"/estate/books/catalog.json")
        if code!=200 or b'"schema": "fountain.press.book-direct-links.v1"' not in body:return False
        code,body=get(base,"/estate/")
        if code!=200 or b'reading-first-app.2b3ed3e08c2ff459b7371e790e10720c711e78842797ff92dc1f6518bebe4458.js' not in body:return False
        for col in ("essays","first-readings","orange-dot"):
            code,data=get(base,"/estate/assets/social/books/"+col+"-first-chapter.jpg")
            if code!=200 or len(data)<10000:return False
    return True

def main():
    assert CURRENT.is_symlink() and CURRENT.resolve().name==OLD,"Active stage changed; refuse overlapping deployment"
    assert sha(ADMISSION)==ADMISSION_SHA
    assert sha(BASE/"releases"/NEW/"source-lock.json")==LOCK_SHA
    assert GUARD.is_file() and SECURE.is_file()
    assert not D1.exists() and not D2.exists(),"Existing v195 override"
    D1.parent.mkdir(parents=True,exist_ok=True)
    D2.parent.mkdir(parents=True,exist_ok=True)
    D1.write_text("[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(GUARD)+" --root "+str(CURRENT)+" --bind 192.168.8.50 --port 8200\n")
    D2.write_text("[Service]\nExecStart=\nExecStart=/usr/bin/python3 "+str(SECURE)+" --root "+str(CURRENT)+" --bind 192.168.8.50 --port 8243 --cert /etc/teatro-first-readings-staging/fullchain.pem --key /etc/teatro-first-readings-staging/leaf.key\n")
    try:
        switch(NEW)
        print("ACTIVATED_CANDIDATE",NEW,flush=True)
        call("systemctl","--user","daemon-reload")
        call("systemctl","--user","restart",HTTP,HTTPS)
        start=time.monotonic()
        while time.monotonic()-start<600:
            if ready():
                print("FountainPress_BOOK_LINKS_V195_CANONICAL_HTTP_HTTPS_OK",flush=True)
                print("ROLLBACK_RETAINED",OLD,flush=True)
                return
            time.sleep(4)
        raise RuntimeError("Live Direct Books stage did not complete readback")
    except Exception:
        print("ROLLBACK_TO",OLD,file=sys.stderr,flush=True)
        switch(OLD)
        D1.unlink(missing_ok=True);D2.unlink(missing_ok=True)
        call("systemctl","--user","daemon-reload")
        call("systemctl","--user","restart",HTTP,HTTPS)
        raise

if __name__=="__main__":main()
