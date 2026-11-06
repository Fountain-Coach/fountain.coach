#!/usr/bin/env python3
"""v176: the existing Kino figure is the Essays thumbnail and social preview."""
from pathlib import Path
import hashlib, json, re, html, shutil
src=Path("/Volumes/DockerDisk/.fountain-kino-static-v175/site")
dst=Path("/Volumes/DockerDisk/.fountain-kino-static-v176/site")
work="essay--a-sound-must-earn-its-place"
img_path="estate/essays/a-sound-must-earn-its-place/media/kino-international-architectural-plate-20261106.jpg"
img="/"+img_path
image_url="https://fountain.coach/"+img_path
url=f"https://fountain.coach/estate/read/{work}/"
image_sha="9bfa71540c6b54a4ac83696fbc0506e31ae58e47c681634d9b93dc4386d31a1c"
prev_sha="ceefb395af8e200a244c5e63fa4cbe0599b5939950d0d6334857af859b9ef69a"
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def change(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)
def setmeta(s,kind,key,value):
    pattern=rf'<meta {kind}="{re.escape(key)}" content="[^"]*"/>'
    assert len(re.findall(pattern,s))==1,(kind,key)
    return re.sub(pattern,lambda m:f'<meta {kind}="{key}" content="{html.escape(value,quote=True)}"/>',s,count=1)
assert not dst.exists()
assert digest(src/"release.json")==prev_sha
assert digest(src/img_path)==image_sha
shutil.copytree(src,dst)
estate=dst/"estate"
root=estate/"index.html"
page=root.read_text()
match=re.search(r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)',page,re.S)
assert match
gallery=json.loads(match.group(2))
entries=gallery["collections"]["essays"]
assert len(entries)==5 and all(x["id"]!=work for x in entries)
alt="Architectural illustration of Kino International, Berlin, showing its horizontal facade, projecting glass foyer, lettering and entrance"
entries.append({"id":work,"src":img,"alt":alt,"sourceKind":"author-approved-architectural-interpretation","sourceSHA256":image_sha})
gallery["source"]["kinoEssay"]="A Sound Must Earn Its Place / architectural-plate figure.1"
page=page[:match.start(2)]+json.dumps(gallery,ensure_ascii=False,separators=(",",":"))+page[match.end(2):]
assert page.count(img)==2
appfile=estate/"assets/linotype/reading-first-app.js"
app=appfile.read_text()
app=change(app,"if(galleries.essays.length!==5||galleries['first-readings'].length!==30 ||",
    "if(galleries.essays.length!==6||galleries['first-readings'].length!==30 ||")
app=change(app,"galleries.essays.some((e,i)=>e.id!==essaySequence[i]) ||",
    "galleries.essays.some((e,i)=>e.id!==(i<essaySequence.length?essaySequence[i]:kinoPublicVolume)) ||")
app=change(app,"const sequence=[essaySequence,solsticeSequence].find(s=>s.includes(name));",
    "const sequence=[contents.essays,solsticeSequence].find(s=>s.includes(name));")
app=change(app,"sequence===essaySequence?'essays':'first-readings'",
    "sequence===contents.essays?'essays':'first-readings'")
apphash=hashlib.sha256(app.encode()).hexdigest()
newapp=f"reading-first-app.{apphash}.js"
assert not (appfile.parent/newapp).exists()
(appfile.parent/newapp).write_text(app)
appfile.write_text(app)
oldapp=re.findall(r'reading-first-app\.([a-f0-9]{64})\.js',page)
assert len(oldapp)==1
page=change(page,f"reading-first-app.{oldapp[0]}.js",newapp)
# First figure is principal illustration. The writer's photograph is supporting.
page=change(page,'data-press-illustration-role="inline" data-press-media="source-photo-and-architectural-interpretation"',
            'data-press-illustration-role="social-lead" data-press-media="source-photo-and-architectural-interpretation"')
page=change(page,'data-press-illustration-role="social-lead" data-press-media="source-photo-and-architectural-interpretation" style="box-sizing:border-box;display:block;width:min(73%,370px)',
            'data-press-illustration-role="inline-support" data-press-media="source-photo-and-architectural-interpretation" style="box-sizing:border-box;display:block;width:min(73%,370px)')
root.write_text(page)
for part in ["library","essays"]:
    (estate/"read"/part/"index.html").write_text(page)
# The Facebook crawler reads the head of this EXACT clean permalink,
# not the JS-selected volume or the Bookshelf homepage.
social=page
description="Kino International, two original unsuccessful live Csound synthesizers, four audio comparisons, and the gap between visual and acoustic conviction."
title="A Sound Must Earn Its Place"
social=change(social,"<title>Benedikt Eickhoff — Bookshelf</title>",f"<title>{title} — Benedikt Eickhoff | Fountain Press</title>")
social=change(social,'<link rel="canonical" href="https://fountain.coach/"/>',f'<link rel="canonical" href="{url}"/>')
social=setmeta(social,"name","description",description)
for k,v in {"og:type":"article","og:site_name":"Fountain Press","og:title":title,"og:description":description,
    "og:url":url,"og:image":image_url,"og:image:secure_url":image_url,"og:image:type":"image/jpeg",
    "og:image:width":"1200","og:image:height":"800","og:image:alt":alt}.items():
    social=setmeta(social,"property",k,v)
for k,v in {"twitter:card":"summary_large_image","twitter:title":title,
    "twitter:description":description,"twitter:image":image_url}.items():
    social=setmeta(social,"name",k,v)
social=change(social,"</head>",f'<meta name="twitter:image:alt" content="{html.escape(alt,quote=True)}"/>\n</head>')
direct=estate/"read"/work/"index.html"
assert direct.exists()
direct.write_text(social)
# Reconcile the actual illustrated source record with the owner's already
# admitted production rights without regenerating or altering either JPEG.
figsource=estate/"essays/a-sound-must-earn-its-place/media/illustration-source.json"
rights=json.loads((estate/"evidence/kino-owner-public-rights.json").read_text())
assert rights["specificSample"]["publicDerivativeUseAuthorizedByOwner"] is True
m=json.loads(figsource.read_text())
assert m["stagingOnly"] is True and m["publicRightsGranted"] is False
assert [f["id"] for f in m["figures"]]==["architectural-plate","night-photograph"]
m["stagingOnly"]=False
m["publicRightsGranted"]=True
m["ownerPublicRightsEvidence"]="/estate/evidence/kino-owner-public-rights.json"
m["figures"][0]["role"]="social-lead-and-navigation-image"
m["figures"][1]["role"]="inline-supporting-photograph"
m["canonicalSocialImage"]=image_url
m["galleryCoverImage"]=img
figsource.write_text(json.dumps(m,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
assert digest(dst/img_path)==image_sha
assert digest(dst/"index.html")==digest(src/"index.html")
assert root.read_text().count("data-reader-volume=")==50
assert social.count("data-reader-volume=")==50
assert f'property="og:image" content="{image_url}"' in social
assert 'property="og:title" content="On Continuity"' in page
assert 'property="og:title" content="A Sound Must Earn Its Place"' in social
assert len(gallery["collections"]["essays"])==6
# Rebuild the immutable inventory for the existing signed Caddy publisher.
d=json.loads((dst/"release.json").read_text())
assert d["publicPublicationAuthorized"] is True
assert d["existingSharedCaddySHA256"]=="08f10f0201c35458bcaf1cc3d1a9749d679ddde27a33c5e4a7d4c738a003a748"
assert d["publicReleaseCopy"]=="estate/release.json"
oldfiles=d["files"]
files={p.relative_to(dst).as_posix():digest(p) for p in sorted(dst.rglob("*"))
       if p.is_file() and p.relative_to(dst).as_posix() not in ("release.json","estate/release.json")}
d["files"]=files
d["publicationRepair"]="kino-original-architectural-social-and-navigation-v176"
d["previousReleaseDigest"]="sha256:"+prev_sha
d["canonicalSocialUrl"]=url
d["canonicalSocialImage"]=image_url
d["canonicalGalleryImage"]=img
d["canonicalGallerySourceSHA256"]=image_sha
d["canonicalGalleryWorkID"]=work
d["newReaderAppSHA256"]=apphash
d["publicIndexSHA256"]=digest(root)
d["socialPermalinkIndexSHA256"]=digest(direct)
release=json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2).encode()+b"\n"
(dst/"release.json").write_bytes(release)
(estate/"release.json").write_bytes(release)
release_sha=hashlib.sha256(release).hexdigest()
(dst.parent/"release-sha256.txt").write_text("sha256:"+release_sha+"\n")
(dst.parent/"projection-manifest.json").write_text(json.dumps({
    "schemaVersion":1,"projections":[{"host":"fountain.coach","root":str(dst),"templateContract":"template-contract.json"}]
},sort_keys=True,indent=2)+"\n")
for rel,hashval in files.items():assert digest(dst/rel)==hashval,rel
changes=[rel for rel in files if rel not in oldfiles or files[rel]!=oldfiles[rel]]
assert all(x.startswith("estate/") for x in changes)
assert len(files)>=434
print(json.dumps({"state":"READY","releaseDigest":"sha256:"+release_sha,"work":work,
    "social":url,"socialImage":image_url,"galleryImages":len(entries),
    "imageSHA256":image_sha,"readerSHA256":apphash,"files":len(files),
    "changedFiles":changes},indent=2))
