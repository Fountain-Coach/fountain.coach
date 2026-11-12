#!/usr/bin/env python3
"""Source-bound v197 illustrated FCIS value essay overlay on the existing v196 Reader."""
from __future__ import annotations
from pathlib import Path
from html import escape
import argparse, hashlib, json, re

ID="essay--the-value-of-what-we-can-prove"
TITLE="The Value of What We Can Prove"
HERO_REL=f"estate/read/{ID}/assets/fcis-value-illustration.webp"
HERO_URL="/"+HERO_REL
SOCIAL_REL=f"estate/assets/social/essays/the-value-of-what-we-can-prove.jpg"
SOCIAL_URL="https://fountain.coach/"+SOCIAL_REL
BOOK_SOCIAL_REL="estate/assets/social/books/essays-first-chapter.jpg"
BOOK_SOCIAL_URL="https://fountain.coach/"+BOOK_SOCIAL_REL
ALT=("Axonometric Teatro Score showing a source repository, authorization gate, "
     "modular instruments and verification record leading to an orange proof mark.")
CAPTION="Source, authorization, instruments, record and proof."
APP_OLD="f6973e96f9e16c30d814016b04d5febdf3c042f938a5740d5955d1128fbc458d"
APP_V195="2b3ed3e08c2ff459b7371e790e10720c711e78842797ff92dc1f6518bebe4458"
ESSAY_MANIFEST=f"estate/read/{ID}/edition-manifest.json"
GALLERY_PATTERN=r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)'
VOLUME_PATTERN=r'<template data-reader-volume="'+ID+r'">.*?</template>'
SOURCE_ROLE='author-approved-Teatro-Score-illustration'
def sha(b):return hashlib.sha256(b).hexdigest()
def once(s,old,new,label):
    if s.count(old)!=1: raise RuntimeError(f"Source seam {label} count {s.count(old)}")
    return s.replace(old,new,1)
def patch_app(b):
    s=b.decode()
    s=once(s,"const illustratedEssaySequence=essaySequence.filter(id=>id!=='"+ID+"');",
            "const illustratedEssaySequence=essaySequence;","illustrated membership")
    s=once(s,"galleries.essays.length!==7","galleries.essays.length!==8","gallery count")
    return s.encode()
def figure(hero_sha):
    return ('<section class="book-art-leaf"><figure class="frame-reading-figure frame-essay-hero" '
            f'data-source-block="fcis-value.illustration.1" data-source-illustration-id="fcis-value.illustration.1" '
            f'data-source-plate-sha256="{hero_sha}" data-editorial-role="hero">'
            f'<img loading="eager" decoding="sync" src="{HERO_URL}" '
            f'alt="{escape(ALT,quote=True)}" width="1200" height="900"/>'
            f'<figcaption>{escape(CAPTION)}</figcaption></figure></section>')
def patch_volume(s, baseline_v196, hero_sha):
    m=re.search(VOLUME_PATTERN,baseline_v196,re.S)
    if not m:raise RuntimeError("New essay base template missing")
    existing=m.group(0)
    needle='<section class="book-chapter-text">'
    if existing.count(needle)!=1 or 'fcis-value.illustration.1' in existing:
        raise RuntimeError("Unexpected new essay template shape")
    illustrated=once(existing,needle,figure(hero_sha)+needle,"art before first text")
    if re.search(VOLUME_PATTERN,s,re.S):
        new,n=re.subn(VOLUME_PATTERN,lambda _:illustrated,s,count=1,flags=re.S)
        if n!=1:raise RuntimeError("Work template replacement failed")
        return new
    key='<script type="application/json" id="reader-gallery-data">'
    return once(s,key,illustrated+"\n"+key,"single source template insertion")
def patch_gallery(s,hero_sha):
    m=re.search(GALLERY_PATTERN,s,re.S)
    if not m:raise RuntimeError("Gallery JSON missing")
    gallery=json.loads(m.group(2))
    entries=gallery["collections"]["essays"]
    if len(entries)!=7 or entries[0]["id"]!="essay--client-centered" or any(a["id"]==ID for a in entries):
        raise RuntimeError("Source-owned prior gallery differs")
    item={"id":ID,"src":HERO_URL,"alt":ALT,"sourceKind":SOURCE_ROLE,"sourceSHA256":hero_sha}
    gallery["collections"]["essays"]=[item,*entries]
    encoded=json.dumps(gallery,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    return s[:m.start(2)]+encoded+s[m.end(2):]
def meta(s,kind,name,value):
    attr='property' if kind=="og" else "name"
    pattern=r'<meta '+attr+r'="'+re.escape(name)+r'" content="[^"]*"\s*/?>'
    replacement=f'<meta {attr}="{name}" content="{escape(value,quote=True)}"/>'
    if re.search(pattern,s):
        return re.sub(pattern,lambda _:replacement,s,count=1)
    return once(s,"</head>",replacement+"\n</head>","new metadata "+name)
def update_staged_robots(s):
    # No contradictory index/follow and noindex metadata.
    s=s.replace('<meta name="robots" content="index,follow"/>','')
    s=re.sub(r'<meta name="robots" content="noindex,nofollow"\s*/?>','',s)
    return once(s,'</head>','<meta name="robots" content="noindex,nofollow"/>\n</head>','stage robots')
def app_reference(s,new_app):
    pat=r"/estate/assets/linotype/reading-first-app\.[a-f0-9]{64}\.js"
    urls=list(set(re.findall(pat,s)))
    if len(urls)!=1 or urls[0].split(".")[1] not in (APP_OLD,APP_V195):
        raise RuntimeError("Unexpected Reader app identity "+str(urls))
    return s.replace(urls[0],"/"+new_app)
def patch_html(s,v196,hero_sha,new_app):
    s=patch_volume(s,v196,hero_sha)
    s=patch_gallery(s,hero_sha)
    s=app_reference(s,new_app)
    s=s.replace("Five essays · current edition","Essays · current selection")
    return s
def patch_essay(s,hero_sha,new_app):
    s=patch_html(s,reference,hero_sha,new_app)
    for k,v in [
        ("og:image",SOCIAL_URL),("og:image:secure_url",SOCIAL_URL),
        ("og:image:type","image/jpeg"),("og:image:width","1200"),
        ("og:image:height","630"),("og:image:alt",ALT)
    ]:s=meta(s,"og",k,v)
    s=meta(s,"twitter","twitter:card","summary_large_image")
    s=meta(s,"twitter","twitter:title",TITLE+" — Fountain Press")
    s=meta(s,"twitter","twitter:image",SOCIAL_URL)
    return update_staged_robots(s)
def patch_book(s,hero_sha,new_app):
    s=patch_html(s,reference,hero_sha,new_app)
    s=meta(s,"og","og:image:alt",ALT)
    script=re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)',s,re.S)
    if not script:raise RuntimeError("Book JSON-LD missing")
    data=json.loads(script.group(2))
    if data.get("@type")!="Book" or data.get("hasPart",{}).get("identifier")!="essay--client-centered":
        raise RuntimeError("Previous book source-hero selection differs")
    data["hasPart"]["identifier"]=ID
    data["hasPart"]["url"]="https://fountain.coach/estate/read/"+ID+"/"
    image=data.get("image")
    if not isinstance(image,dict):raise RuntimeError("Book image schema unexpected")
    image["caption"]=ALT
    v=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    return s[:script.start(2)]+v+s[script.end(2):]
def main():
    global reference
    p=argparse.ArgumentParser()
    for arg in ("baseline","output","source","hero","social"):p.add_argument("--"+arg,type=Path,required=True)
    p.add_argument("--revision",required=True)
    args=p.parse_args()
    if args.output.exists():raise RuntimeError("Output exists; immutable candidate only")
    baseline=args.baseline
    reference=(baseline/"estate/index.html").read_text()
    if reference.count('<template data-reader-volume=')!=76:raise RuntimeError("Unexpected v196 template count")
    image=args.hero.read_bytes();social=args.social.read_bytes();hero_sha=sha(image)
    if hero_sha!="b043511473e6bca1e05b3c09d8dc1c92997b8bcbacb8506525ca0a4c0f02ebdb":
        raise RuntimeError("Approved hero source digest drift")
    if sha(social)!="82ccaf0e6d050c046d44a0684f420e36d4dd71f8655faa5c42925152e93b40f3":
        raise RuntimeError("Share image derivative digest drift")
    s=args.source.read_text()
    if 'data-source-illustration-id="fcis-value.illustration.1"' not in s or 'assets/fcis-value-illustration.webp' not in s:
        raise RuntimeError("Author source did not admit the figure")
    if 'data-author-approved="2026-11-12"' not in s:
        raise RuntimeError("Author editorial image intent not bound")
    app_rel="estate/assets/linotype/reading-first-app."+APP_OLD+".js"
    b=(baseline/app_rel).read_bytes()
    if sha(b)!=APP_OLD:raise RuntimeError("Inherited Reader changed")
    app=patch_app(b);newhash=sha(app)
    new_app="estate/assets/linotype/reading-first-app."+newhash+".js"
    rendered={}
    rendered[new_app]=app
    for key in ("estate/index.html","estate/read/essays/index.html",
                "estate/books/first-readings/index.html","estate/books/orange-dot/index.html"):
        rendered[key]=patch_html((baseline/key).read_text(),reference,hero_sha,new_app).encode()
    direct=f"estate/read/{ID}/index.html"
    rendered[direct]=patch_essay((baseline/direct).read_text(),hero_sha,new_app).encode()
    rendered["estate/books/essays/index.html"]=patch_book((baseline/"estate/books/essays/index.html").read_text(),hero_sha,new_app).encode()
    rendered[HERO_REL]=image
    rendered[SOCIAL_REL]=social
    rendered[BOOK_SOCIAL_REL]=social
    manifest=json.loads((baseline/ESSAY_MANIFEST).read_text())
    if manifest.get("originalImages")!=0 or manifest.get("sourceBlocks") is None:
        raise RuntimeError("Previous essay source manifest drift")
    manifest["sourceRevision"]=args.revision
    manifest["sourceSHA256"]=sha(args.source.read_bytes())
    manifest["originalImages"]=1
    manifest["figures"]=[{
        "id":"fcis-value.illustration.1","sourceBlock":"fcis-value.illustration.1",
        "editorialRole":"hero","originalPath":HERO_URL,"originalSHA256":hero_sha,
        "socialPath":"/"+SOCIAL_REL,"socialSHA256":sha(social),
        "intrinsicDimensions":[1200,900],"socialDimensions":[1200,630],
        "alt":ALT,"caption":CAPTION,
        "credit":"Fountain Coach — author-selected AI-assisted Teatro Score",
        "rights":"author-approved for private staging; public release separately authorized"
    }]
    rendered[ESSAY_MANIFEST]=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    cat_path="estate/books/catalog.json"
    cat=json.loads((baseline/cat_path).read_text())
    books=cat["books"]
    essay=next(x for x in books if x["id"]=="essays")
    if essay["firstIllustratedChapterID"]!="essay--client-centered":
        raise RuntimeError("Book source-first illustrated chapter has changed")
    essay.update({
      "firstIllustratedChapterID":ID,
      "firstChapterOriginalImagePath":HERO_URL,
      "firstChapterOriginalImageSHA256":hero_sha,
      "firstChapterImageAlt":ALT,
      "sourceIllustrationDeclaredSHA256":hero_sha,
      "sourceIllustrationProvenance":SOURCE_ROLE,
      "sourceRevision":args.revision[:7],
      "socialImageSHA256":sha(social)
    })
    rendered[cat_path]=(json.dumps(cat,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    for rel,content in sorted(rendered.items()):
        target=args.output/rel;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(content)
    receipt={
      "schema":"fountain.press.illustrated-essay-overlay.v197",
      "workId":ID,"sourceOwner":"Fountain-Coach/fountain.coach",
      "sourceRevision":args.revision,"sourceSHA256":manifest["sourceSHA256"],
      "baselineRelease":baseline.name,
      "baselineLockSHA256":sha((baseline/"source-lock.json").read_bytes()),
      "heroSourceSHA256":hero_sha,"socialDerivativeSHA256":sha(social),
      "originalWorkSourceParagraphsPreserved":True,
      "originalImageCount":1,"stagingOnly":True,"publicReleaseAuthorized":False,
      "changedFiles":{k:sha(v) for k,v in sorted(rendered.items())},
      "newAppSHA256":newhash,
      "sourceGalleryLength":8,"firstIllustratedEssay":ID
    }
    (args.output/"build-receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("ILLUSTRATED_ESSAY_V197_COMPOSED",len(rendered),"files; hero",hero_sha,"social",sha(social))
    print("NEW_APP",newhash,"SOURCE",receipt["sourceSHA256"],"STAGING_ONLY")
if __name__=="__main__":main()
