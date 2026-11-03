#!/usr/bin/env python3
"""Verify the actual Facebook crawler contract of all static Press share routes."""
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from pathlib import Path
import json,sys,os
ROOT=Path(__file__).resolve().parents[1]
PREFIX=os.environ.get("TEST_ORIGIN","http://127.0.0.1:4292")
V=json.loads((ROOT/"build/v141-social-source-inventory.json").read_text())["volumes"]
class Meta(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.canonical=None;self.title=""
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=="meta" and d.get("property"):self.meta[d["property"]]=d.get("content")
  if t=="link" and d.get("rel")=="canonical":self.canonical=d.get("href")
def read(url):
 r=Request(url,headers={"User-Agent":"facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)","Accept":"text/html,application/xhtml+xml,image/avif,image/webp,image/*"})
 return urlopen(r,timeout=8)
used_images=set()
for row in V:
 vol=row["id"];route="/estate/read/"+vol+"/"
 with read(PREFIX+route) as response:
  assert response.status==200,(vol,response.status)
  assert response.info().get_content_type()=="text/html"
  html=response.read().decode("utf8")
 m=Meta();m.feed(html)
 expected="https://fountain.coach"+route
 img="https://fountain.coach"+row["image"]
 assert m.canonical==expected,(vol,"canonical",m.canonical)
 assert m.meta["og:url"]==expected,(vol,"OG URL")
 assert m.meta["og:title"]==row["title"],(vol,"OG TITLE")
 assert m.meta["og:image"]==img,(vol,"OG IMAGE")
 assert m.meta["og:image:width"]=="1200"
 assert m.meta["og:image:height"]=="630"
 assert m.meta["og:image:type"]=="image/jpeg"
 assert m.meta["og:image:alt"]
 assert row["image"] not in used_images
 used_images.add(row["image"])
 assert 'data-initial-volume="'+vol+'"' in html
 with read(PREFIX+row["image"]) as image:
  assert image.status==200
  assert image.info().get_content_type()=="image/jpeg",(vol,image.info())
  raw=image.read()
  assert raw[:3]==bytes.fromhex("ffd8ff"),(vol,"not JPEG")
  assert len(raw)>3000,(vol,"empty JPG")
# The root share must likewise be a real, publicly crawlable first-folio image.
with read(PREFIX+"/") as response:
 m=Meta();m.feed(response.read().decode("utf8"))
 assert m.meta["og:image"]=="https://fountain.coach/estate/assets/social/v141/continuity.jpg"
 assert m.meta["og:url"]=="https://fountain.coach/"
assert len(V)==48
print("FACEBOOK_CRAWL_ACCEPTANCE",len(V)+1,"/",len(V)+1,
      "origin",PREFIX,"unique work images",len(used_images),
      "original principal",sum(r["selection"]=="first-authored-illustration" for r in V),
      "authentic printed page",sum(r["selection"]=="first-composed-folio" for r in V))
