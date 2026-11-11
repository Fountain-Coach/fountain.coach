#!/usr/bin/env python3
"""Independent canonical owner-WLAN acceptance of production-derived Orange Dot.
Read-only HTTP/HTTPS, publication identities, one-page source parity and original
audiovisual film byte ranges. No public deployment is performed.
"""
import hashlib,json,ssl,urllib.request,urllib.error
from pathlib import Path

BASES=("http://192.168.8.50:8200","https://192.168.8.50:8243")
EXPECTED_INDEX="7db826d5aa32da727213ce2d53dc1e1a35efe5ee820c987ae6066e2dd1500f3b"
EXPECTED_APP="d2c2020390a35d7def6409abf50171e1998a0f1baa4bf8da3cbaf50bc3aa1a81"
EXPECTED_ENGINE="837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a"
APP="/estate/assets/linotype/reading-first-app."+EXPECTED_APP+".js"
ENGINE="/estate/assets/linotype/reading-first-press-engine."+EXPECTED_ENGINE+".js"
def fetch(base,path,byte_range=None):
    hdr={"Cache-Control":"no-store"}
    if byte_range:hdr["Range"]=byte_range
    request=urllib.request.Request(base+path,headers=hdr)
    ctx=ssl._create_unverified_context() if base.startswith("https:") else None
    try:
        with urllib.request.urlopen(request,context=ctx,timeout=12) as response:
            return response.status,response.read(),dict(response.headers)
    except urllib.error.HTTPError as e:
        return e.code,e.read(),dict(e.headers)
def sha(blob):return hashlib.sha256(blob).hexdigest()
for base in BASES:
    code,page,_=fetch(base,"/estate/")
    assert code==200 and sha(page)==EXPECTED_INDEX,(base,code,sha(page))
    for path,expected in ((APP,EXPECTED_APP),(ENGINE,EXPECTED_ENGINE)):
        status,data,_=fetch(base,path)
        assert status==200 and sha(data)==expected,(path,status)
    assert b'data-reader-volume="orange-dot"' in page
    assert page.count(b'data-reader-volume="orange-dot--')==23
    for token in (b'data-reader-volume="governance"',b'data-reader-volume="scores"',
                  b'data-reader-volume="score--between-gardens"',
                  b'data-edition-membership="governance"'):
        assert token not in page,(base,token)
    assert page.count(b'https://governance.fountain.coach/chapters/')>=10
    s,b,_=fetch(base,"/estate/collections/orange-dot/edition.json")
    assert s==200
    edition=json.loads(b)
    assert edition.get("publicReleaseAuthorized") is False
    for leaf in ("history","sound-craft"):
        s,body,_=fetch(base,"/estate/media/kino/"+leaf+"/edition.json")
        assert s==200
        m=json.loads(body)
        assert len(m["tracks"])==2 and all(t["publicReleaseAuthorized"] is True for t in m["tracks"])
    for path in ("/estate/assets/orange-dot/orange-dot--2026-01-22-the-vigilance-regulator-02-b5da722ce9f6c7.jpg",):
        s,body,_=fetch(base,path)
        assert s==200 and len(body)>10000
    for movie in ("64","44"):
        s,data,head=fetch(base,"/pointer/assets/historical-media/koken-head-boxers/"+movie+".mp4","bytes=0-31")
        assert s==206 and len(data)==32 and data[4:8]==b"ftyp", (base,movie,s)
    for src in ("/source-lock.json","/estate/collections/works/edition.json"):
        s,_,_=fetch(base,src)
        assert s in (403,404),(src,s)
    print("PASS",base,"production-matched Bookshelf; Orange Dot 23; no Governance/Works/Scores shelf; independent original film range")
print("PASS_ORANGE_DOT_V194B_CANONICAL_WLAN_READBACK")
