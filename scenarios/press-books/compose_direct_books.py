#!/usr/bin/env python3
"""Fountain Press source-bound direct-book and social card composer.

Run on the EXACT production-derived, stage-accepted Bookshelf root. Do not
edit original manuscripts, images or Reader templates. Generate three semantic
book URLs with one existing Linotype Reader, and one source-art social card
per book. The first admitted *illustrated* chapter in collection order is
the cover source (unillustrated proems are not invented as paintings).
No public deployment or rights approval is implied.
"""
import argparse
from html import escape
import hashlib
import json
import re
from pathlib import Path
import subprocess

POLICY_PATH=Path(__file__).with_name("book-policy.json")
POLICY=json.loads(POLICY_PATH.read_text(encoding="utf-8"))
assert POLICY["schema"]=="fountain.press.book-social-policy.v1"
assert POLICY["publicationStage"]=="owner-WLAN-staging-private"
BOOKS=POLICY["books"]
COLLECTIONS=tuple(b["id"] for b in BOOKS)
assert len(COLLECTIONS)==len(set(COLLECTIONS)) and all(re.fullmatch(r"[a-z][a-z0-9-]*",id) for id in COLLECTIONS)
TITLES={b["id"]:b["title"] for b in BOOKS}
DESCRIPTIONS={b["id"]:b["description"] for b in BOOKS}
SOURCE={
    "owner":POLICY["sourceOwner"],
    "revision":POLICY["sourceGitRevision"],
    "publicPredecessor":POLICY["publicPredecessor"],
    "privateStagingPredecessor":POLICY["privateStagingPredecessor"],
}
ROOT_SHA=POLICY["sourceIndexSHA256"]
APP_SHA=POLICY["sourceReaderAppSHA256"]
CSS_SHA=POLICY["sourceCSSSHA256"]
APP=POLICY["sourceReaderAppPath"]
CSS=POLICY["sourceCSSPath"]
assert len(ROOT_SHA)==len(APP_SHA)==len(CSS_SHA)==64

def digest(data):
    return hashlib.sha256(data).hexdigest()
def read_sha(root,path,expected):
    actual=(root/path).read_bytes()
    if digest(actual)!=expected:
        raise RuntimeError("Source drift "+str(path))
    return actual
def replace_once(source,old,new,name):
    if source.count(old)!=1:
        raise RuntimeError("Unadmitted template change "+name+": "+str(source.count(old)))
    return source.replace(old,new,1)
def escape_attr(s):
    return escape(s,quote=True)
def media_digest(path):
    return digest(path.read_bytes())
def make_social(original,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([
        "magick","-density","180",str(original),
        "-auto-orient","-background","#f5f2e9","-alpha","remove",
        "-alpha","off","-resize","1160x580",
        "-gravity","center","-extent","1200x630",
        "-sampling-factor","4:4:4","-quality","92",
        "-strip",str(dest)
    ],check=True,capture_output=True,text=True)
    dimensions=subprocess.run(["magick","identify","-format","%w %h %m",str(dest)],check=True,capture_output=True,text=True).stdout
    if dimensions!="1200 630 JPEG":
        raise RuntimeError("Invalid source-art derivative "+dimensions)
    return media_digest(dest)
def update_meta(page,kind,key,value):
    name="property" if kind=="property" else "name"
    pattern=r'<meta '+name+r'="'+re.escape(key)+r'" content="[^"]*"/?>'
    replacement='<meta '+name+'="'+escape_attr(key)+'" content="'+escape_attr(value)+'"/>'
    matches=re.findall(pattern,page)
    if len(matches)!=1:
        raise RuntimeError("Metadata identity missing or duplicate "+key)
    return re.sub(pattern,lambda _:replacement,page,count=1)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path,help="Exact staged production-derived full static root")
    p.add_argument("--output",required=True,type=Path,help="Only newly/changed files to overlay onto source")
    a=p.parse_args()
    src=a.source
    dest=a.output
    if dest.exists():
        raise RuntimeError("Refuse overwriting existing output "+str(dest))
    original=read_sha(src,"estate/index.html",ROOT_SHA).decode()
    app=read_sha(src,APP,APP_SHA).decode()
    css=read_sha(src,CSS,CSS_SHA).decode()
    galleries_match=re.search(r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',original,re.S)
    if not galleries_match:
        raise RuntimeError("Source Bookshelf gallery absent")
    gallery=json.loads(galleries_match.group(1))
    if list(gallery["collections"])!=list(COLLECTIONS):
        raise RuntimeError("Unexpected source Bookshelf collections")
    for book in BOOKS:
        col=book["id"]
        if len(gallery["collections"][col])!=book["illustratedEntryCount"]:
            raise RuntimeError("Unadmitted source gallery changed "+col)
        prefix=book.get("chapterVolumePrefix")
        if prefix and original.count('data-reader-volume="'+prefix)!=book["chapterCount"]:
            raise RuntimeError("Incomplete authored chapter source "+col)

    # The normal existing Reader publishes these links in the Bookshelf header.
    # Neither source prose, gallery buttons nor page compositor is forked.
    marker="   header.append(name);"
    new=("""   header.append(name);
   // An absolute, crawler-addressable book route; Reader remains the same.
   const direct=document.createElement('a');
   direct.className='reader-book-direct-link';
   direct.href='/estate/books/'+id+'/';
   direct.textContent='Direct book link';
   direct.setAttribute('aria-label','Direct link to '+labels.get(id)+' book');
   header.append(direct);""")
    app=replace_once(app,marker,new,"Bookshelf direct links")
    new_app_hash=digest(app.encode())
    new_app_path="estate/assets/linotype/reading-first-app."+new_app_hash+".js"
    style=css+"""
/* Fountain Press direct-book identity: typographic link, no duplicate Reader. */
.reader-collection-heading .reader-book-direct-link{
 display:inline-block;margin:.15rem 0 0;
 color:var(--muted);font:normal .79rem/1.3 system-ui,-apple-system,sans-serif;
 text-decoration:underline;text-underline-offset:.16em;
}
.reader-collection-heading .reader-book-direct-link:focus-visible{
 outline:2px solid currentColor;outline-offset:3px;
}
"""
    root=original.replace("/estate/assets/linotype/reading-first-app."+APP_SHA+".js",
                          "/estate/assets/linotype/reading-first-app."+new_app_hash+".js")
    root=replace_once(root,'</head>','<link rel="alternate" type="application/json" title="Fountain Press Books" href="/estate/books/catalog.json"/>\n</head>',"Bookshelf discovery")
    root=root.replace('reading-first-shell.css','reading-first-shell.css')
    # Existing CSS name is retained; staged overlay changes precisely that file.
    # Renderer and original image/contents metadata remain identical.
    appended={}
    def emit(path,data):
        if path in appended:
            raise RuntimeError("Duplicate output "+path)
        output=dest/path
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(data)
        appended[path]=digest(data)
    emit("estate/index.html",root.encode())
    emit(new_app_path,app.encode())
    emit(CSS,style.encode())
    books=[]
    for col in COLLECTIONS:
        all_illustrated=gallery["collections"][col]
        if not all_illustrated:
            raise RuntimeError("First folio fallback is not yet implemented: "+col)
        first=all_illustrated[0]
        first_id=first["id"]
        image_path=first["src"].lstrip("/")
        image_source=src/image_path
        if not image_source.is_file():
            raise RuntimeError("First illustrated chapter image unavailable "+image_path)
        source_hash=media_digest(image_source)
        stated=first.get("sourceSHA256")
        if stated and source_hash!=stated:
            raise RuntimeError("First chapter source-image SHA conflict "+col)
        image_dest=dest/("estate/assets/social/books/"+col+"-first-chapter.jpg")
        social_hash=make_social(image_source,image_dest)
        image_rel="/"+image_dest.relative_to(dest).as_posix()
        appended[image_dest.relative_to(dest).as_posix()]=social_hash
        url="https://fountain.coach/estate/books/"+col+"/"
        social_url="https://fountain.coach"+image_rel
        name=TITLES[col]
        description=DESCRIPTIONS[col]
        image_alt=first["alt"]
        page=root
        for property_,value in (
          ("og:type","book"),
          ("og:site_name","Fountain Press"),
          ("og:title",name+" — Fountain Press"),
          ("og:description",description),
          ("og:url",url),
          ("og:image",social_url),
          ("og:image:secure_url",social_url),
          ("og:image:type","image/jpeg"),
          ("og:image:width","1200"),
          ("og:image:height","630"),
          ("og:image:alt",image_alt),
        ):
            page=update_meta(page,"property",property_,value)
        for t,v in (
          ("twitter:card","summary_large_image"),
          ("twitter:title",name+" — Fountain Press"),
          ("twitter:description",description),
          ("twitter:image",social_url),
        ):
            page=update_meta(page,"name",t,v)
        title_tag='<title>'+escape(name)+' — Fountain Press</title>'
        page=re.sub(r'<title>.*?</title>',lambda _:title_tag,page,count=1,flags=re.S)
        page=replace_once(page,'data-initial-volume="library"',
                          'data-initial-volume="'+col+'"',"direct book Reader admission")
        semantics={
          "@context":"https://schema.org",
          "@type":"Book",
          "@id":url+"#book",
          "name":name,
          "url":url,
          "description":description,
          "author":{"@type":"Person","name":"Benedikt Eickhoff"},
          "publisher":{"@type":"Organization","name":"Fountain Press","url":"https://fountain.coach/"},
          "image":{"@type":"ImageObject","url":social_url,"width":1200,"height":630,"caption":image_alt},
          "hasPart":{"@type":"CreativeWork","identifier":first_id,
                     "url":"https://fountain.coach/estate/read/"+first_id+"/"},
          "isAccessibleForFree":True,
        }
        ld='<script type="application/ld+json">'+json.dumps(semantics,ensure_ascii=False,separators=(',',':'))+'</script>'
        page=replace_once(page,
            '<link rel="canonical" href="https://fountain.coach/"/>',
            '<link rel="canonical" href="'+escape_attr(url)+'"/>',
            'replace root canonical with direct book identity')
        page=replace_once(page,'</head>',
            ld+'\n</head>',
            'direct book machine semantics')
        # The first documented chapter-image identity is never replaced by
        # a generic Press banner or an unrelated hero.
        emit("estate/books/"+col+"/index.html",page.encode())
        books.append({
            "id":col,"title":name,"canonicalURL":url,
            "directURLPath":"/estate/books/"+col+"/",
            "description":description,
            "firstIllustratedChapterID":first_id,
            "firstChapterOriginalImagePath":"/"+image_path,
            "firstChapterOriginalImageSHA256":source_hash,
            "firstChapterImageAlt":image_alt,
            "socialImageURL":social_url,
            "socialImagePath":image_rel,
            "socialImageSHA256":social_hash,
            "socialImageDimensions":[1200,630],
            "sourceIllustrationProvenance":first.get("sourceKind"),
            "sourceIllustrationDeclaredSHA256":stated or None,
            "sourceRevision":SOURCE["revision"],
            "stageOnly":True,
            "publicReleaseAuthorized":False
        })
    record={
      "schema":"fountain.press.book-direct-links.v1",
      "status":"owner-WLAN-staging-private",
      "sourceOwner":SOURCE["owner"],
      "sourceGitRevision":SOURCE["revision"],
      "publicPredecessor":SOURCE["publicPredecessor"],
      "stagingPredecessor":SOURCE["privateStagingPredecessor"],
      "linkPolicy":"stable path, never hash-fragment as canonical social URL",
      "visualPolicy":"first admitted illustrated chapter in original collection order",
      "fallbackPolicy":"unillustrated collection requires rendered first Linotype folio; absent here",
      "publicationAuthority":"EstatePublisher - separate rights approval",
      "books":books,
    }
    emit("estate/books/catalog.json",(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode())
    (dest/"source-direct-book-build-receipt.json").write_text(json.dumps({
        "schema":"fountain.press.book-social-stage-build-receipt.v1",
        "sourceRootHTMLSHA256":ROOT_SHA,
        "sourceReaderAppSHA256":APP_SHA,
        "sourceReaderCSSSHA256":CSS_SHA,
        "newReaderAppSHA256":new_app_hash,
        "sourceOwner":SOURCE["owner"],
        "sourceGitRevision":SOURCE["revision"],
        "stagedFiles":dict(sorted(appended.items())),
        "bookCount":len(books),
        "productionAffected":False,
    },indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("BOOK_DIRECT_LINKS_COMPOSED",len(books),"books",len(appended),"staged paths")
    print("NEW_READER_APP",new_app_hash)
    for b in books:
        print("BOOK",b["id"],b["directURLPath"],b["firstIllustratedChapterID"],
              "sourceSHA",b["firstChapterOriginalImageSHA256"],"imageSHA",b["socialImageSHA256"])
    print("NOT_DEPLOYED",dest)
if __name__=="__main__":main()
