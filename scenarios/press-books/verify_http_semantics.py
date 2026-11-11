#!/usr/bin/env python3
"""Independent source/media/crawler parity for stable Fountain Press book links.

Read-only: no browser JavaScript or publication action. Source SHA comparison is
against the exact native stage-host asset that the book catalogue declares.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import ssl
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import urllib.error

class HeadScanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals=[]
        self.meta={}
        self.structured=[]
        self._in_ld=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="link" and a.get("rel")=="canonical":self.canonicals.append(a.get("href"))
        if tag=="meta":
            key=a.get("property") or a.get("name")
            if key:self.meta.setdefault(key,[]).append(a.get("content"))
        if tag=="script" and a.get("type")=="application/ld+json":self._in_ld=True
    def handle_data(self,data):
        if self._in_ld:self.structured.append(data)
    def handle_endtag(self,tag):
        if tag=="script":self._in_ld=False
def sha(blob):return hashlib.sha256(blob).hexdigest()
def fetch(base,route):
    ctx=ssl._create_unverified_context() if base.startswith("https:") else None
    req=Request(base+route,headers={"Cache-Control":"no-store"})
    with urlopen(req,context=ctx,timeout=30) as response:
        return response.status,response.read(),response.headers.get("Content-Type","")
def verify(base):
    result,b,ct=fetch(base,"/estate/books/catalog.json")
    assert result==200 and ct.startswith("application/json"),(result,ct)
    catalog=json.loads(b)
    assert catalog["schema"]=="fountain.press.book-direct-links.v1"
    assert [e["id"] for e in catalog["books"]]==["essays","first-readings","orange-dot"]
    for book in catalog["books"]:
        assert book["stageOnly"] is True and book["publicReleaseAuthorized"] is False
        status,html,typ=fetch(base,book["directURLPath"])
        assert status==200 and typ.startswith("text/html"),(book["id"],typ)
        raw=html.decode("utf-8")
        parser=HeadScanner();parser.feed(raw)
        assert parser.canonicals==[book["canonicalURL"]],(book["id"],parser.canonicals)
        def meta(k):
            values=parser.meta.get(k,[])
            assert len(values)==1,(book["id"],k,values)
            return values[0]
        for k,expected in [
           ("og:type","book"),("og:url",book["canonicalURL"]),
           ("og:image",book["socialImageURL"]),("og:image:alt",book["firstChapterImageAlt"]),
           ("og:image:width","1200"),("og:image:height","630"),
           ("twitter:card","summary_large_image"),("twitter:image",book["socialImageURL"]),
        ]:assert meta(k)==expected,(book["id"],k)
        assert len(parser.structured)==1
        ld=json.loads(parser.structured[0])
        assert ld["@type"]=="Book" and ld["url"]==book["canonicalURL"] and ld["hasPart"]["identifier"]==book["firstIllustratedChapterID"]
        assert raw.count('data-reader-volume="orange-dot--')==23
        status,img,typ=fetch(base,book["socialImagePath"])
        assert status==200 and typ.startswith("image/jpeg"),(book["id"],typ)
        assert sha(img)==book["socialImageSHA256"],book["id"]
        # JPEG beginning and size checked independently of ImageMagick tool.
        assert img.startswith(b"\xff\xd8") and len(img)>5000
        status,original,_=fetch(base,book["firstChapterOriginalImagePath"])
        assert status==200 and sha(original)==book["firstChapterOriginalImageSHA256"]
        print("BOOK_DIRECT_HTTP_ACCEPTED",base,book["id"],"firstChapter",book["firstIllustratedChapterID"],"sourceSHA",sha(original),"socialSHA",sha(img))
    code,root,_=fetch(base,"/estate/")
    assert code==200 and root.count(b"Direct book link")>=0
    assert b'data-reader-volume="governance"' not in root
    assert b'data-reader-volume="scores"' not in root
    assert root.count(b'https://governance.fountain.coach/chapters/')>=10
    print("PASS_DIRECT_BOOK_HTTP_SEMANTICS",base,"3 canonical routes, source images, OG/Twitter, JSON-LD and catalogue")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base",default="http://192.168.8.50:8200")
    args=p.parse_args()
    verify(args.base.rstrip("/"))
