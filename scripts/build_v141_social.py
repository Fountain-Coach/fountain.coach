#!/usr/bin/env python3
"""Project pinned v140 public Fountain Press into crawlable v141 social routes.

"assemble" builds the exact public-release overlay and all principal-art OG JPEGs.
"finalize" verifies every first-folio screenshot and writes immutable inventory.
No stage or production effect; no new renderer or unauthorized content.
"""
from __future__ import annotations
from html.parser import HTMLParser
from html import escape as html_escape
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "build/production-v20-readonly"
OUT = ROOT / "build/public-release-v141-social"
LIST = ROOT / "build/v141-social-first-folio-fallbacks.json"
WITNESS = ROOT / "build/v141-social-release-witness.json"
PARENT = "estate-20261103-v20-vergil-reader-611c3e3"
BASE_SOURCE = "5f9b3eafc4248baf0bdb4432b53efa1c5e9caf9c"
SOURCE = os.environ.get("FOUNTAIN_V141_SOURCE_SHA", BASE_SOURCE)
if not re.fullmatch(r"[0-9a-f]{40}", SOURCE):raise ValueError("Expected source commit SHA40")
RELEASE = "estate-20261103-v21-social-principal-" + SOURCE[:7]
ROOT_SHA = "c6de70bf24b6e2e2321fdfbd215e568c36e518b3e093c65f6921d02ad03164bc"
def digest(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def fail(s): raise RuntimeError(s)
def checked(s, old, new, n=1):
    if s.count(old)!=n: fail(f"Expected {n} occurrence(s) {old!r}, found {s.count(old)}")
    return s.replace(old,new)
class PressVolumes(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = None
        self.h2 = False
        self.volumes = {}
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="template" and "data-reader-volume" in a:
            self.active=a["data-reader-volume"]
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]+",self.active):fail("Unadmitted volume id")
            if self.active in self.volumes:fail("Duplicated authored volume")
            self.volumes[self.active]={"title":"","figure":None,"figureAlt":None,"figureCount":0}
        if self.active and tag=="h2" and not self.volumes[self.active]["title"]:self.h2=True
        if self.active and tag=="figure":self.volumes[self.active]["figureCount"]+=1
        if self.active and tag=="img" and self.volumes[self.active]["figure"] is None:
            self.volumes[self.active]["figure"]=a.get("src")
            self.volumes[self.active]["figureAlt"]=a.get("alt") or ""
    def handle_endtag(self,tag):
        if tag=="h2":self.h2=False
        if tag=="template":self.active=None;self.h2=False
    def handle_data(self,data):
        if self.active and self.h2:self.volumes[self.active]["title"]+=data

def main_assemble():
    if OUT.exists():fail("Refusing to overwrite existing v141 local artifact")
    if not BASE.is_dir() or digest((BASE/"index.html").read_bytes())!=ROOT_SHA: fail("Exact published v20 baseline not verified")
    current=json.loads((BASE/"release-manifest.json").read_text())
    if current["releaseID"]!=PARENT:fail("Unexpected predecessor identity")
    base_files=[p for p in BASE.rglob("*") if p.is_file()]
    if len(base_files)!=219:fail("Source baseline file count changed")
    html=(BASE/"estate/index.html").read_text()
    if html!=(BASE/"index.html").read_text():fail("Root and book HTML diverged")
    original_app=(BASE/"estate/assets/linotype/reading-first-app.js").read_text()
    for f,expected in [
        ("estate/media/first-readings/teatro-vergil-auto-corrected-v2.mp3","d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd"),
        ("estate/media/first-readings/vergil-prologue-source-aligned.mp3","4b2727e08bd7b3c0edea59f6faca92292e9447d980bfb1d2f963e829dba16881")]:
        if digest((BASE/f).read_bytes())!=expected:fail("Original Vergil audio changed "+f)
    doc=PressVolumes();doc.feed(html)
    if len(doc.volumes)<40 or "solstice-reading-01--vergil" not in doc.volumes or "library" not in doc.volumes:
        fail("Unexpected reader volume inventory: "+str(len(doc.volumes)))
    # Keep an exact copy of the active public release, including historic routes.
    shutil.copytree(BASE,OUT)
    app=original_app
    old=' const pathname=location.pathname,match=location.hash.match(/^#\\/read\\/([\\w-]+)/);'
    new=""" const pathname=location.pathname,match=location.hash.match(/^#\\/read\\/([\\w-]+)/);
 const direct=pathname.match(/^\\/estate\\/read\\/([\\w-]+)\\/?$/);
 if(direct&&labels.has(direct[1]))return entryVolume(direct[1]);"""
    app=checked(app,old,new)
    app=checked(app,
      " const raw=new URLSearchParams(location.hash.split('?')[1]||'').get('at');",
      " const raw=new URLSearchParams(location.search).get('at')||new URLSearchParams(location.hash.split('?')[1]||'').get('at');")
    # Preserve exact per-passage position but put the *work identity* in the pathname.
    app=checked(app,"'/estate/#/read/'+v+'?at='+encodeURIComponent(anchor.block+'@'+anchor.offset)",
                    "'/estate/read/'+v+'/?at='+encodeURIComponent(anchor.block+'@'+anchor.offset)")
    app=checked(app,"'/estate/#/read/'+name","'/estate/read/'+name+'/'")
    # The previous public reader used hash-only work URLs. Normalize those
    # bookmarks on first load so a Share action copies the actual work URL.
    app=checked(app,
      "const anchored=addressFromUrl();if(anchored)positions.set(initial,anchored);\nschedule();",
      "const anchored=addressFromUrl();if(anchored)positions.set(initial,anchored);\n"
      "if(location.hash.startsWith('#/read/')){\n"
      " const offset=anchored?'?at='+encodeURIComponent(anchored.block+'@'+anchored.offset):'';\n"
      " history.replaceState({volume:initial},'', '/estate/read/'+initial+'/'+offset);\n"
      " lastHistoryLocation=location.href;\n"
      "}\nschedule();")
    (OUT/"estate/assets/linotype/reading-first-app.js").write_text(app)
    fallback=[]
    image_records=[]
    for volume,meta in doc.volumes.items():
        title=meta["title"].strip() or ("Fountain Coach Bookshelf" if volume=="library" else volume)
        if volume=="continuity":title="On Continuity"
        if volume=="publication-notes":title="Publication Notes"
        if len(title)>170:fail("Unbounded heading for "+volume)
        src=meta["figure"]
        visual=OUT/"estate/assets/social/v141"/(volume+".jpg")
        visual.parent.mkdir(parents=True,exist_ok=True)
        chosen="first-composed-folio"
        if src:
            if not src.startswith(("/estate/","/solstice/")):fail("Unadmitted first figure source "+str(src))
            source=BASE/src.lstrip("/")
            if not source.is_file():fail("Authored illustration unavailable "+src)
            if source.suffix.lower()==".svg":
                png=ROOT/"build"/(volume+"-svg-source.png")
                r=subprocess.run(["rsvg-convert","--keep-aspect-ratio","-w","1200","-h","630","-o",str(png),str(source)],capture_output=True,text=True)
                if r.returncode:fail("Could not render original SVG "+src+" "+r.stderr[:150])
                inputfile=png
            else: inputfile=source
            command=["magick",str(inputfile),"-auto-orient","-resize","1200x630",
                     "-background","#efeee9","-gravity","center","-extent","1200x630",
                     "-alpha","remove","-alpha","off","-strip","-quality","88",str(visual)]
            r=subprocess.run(command,capture_output=True,text=True)
            if r.returncode:fail("Could not render source principal image "+src+": "+r.stderr[:150])
            chosen="first-authored-illustration"
        else:
            fallback.append({"id":volume,"title":title,"page":"/estate/read/"+volume+"/","image":"/estate/assets/social/v141/"+volume+".jpg"})
        image_records.append({"id":volume,"title":title,"source":src,"sourceSHA256":digest((BASE/src.lstrip("/")).read_bytes()) if src else None,
                              "image":"/estate/assets/social/v141/"+volume+".jpg","selection":chosen})
    def og_headers(id, title,canonical,image,description):
        def tag(prop,value):return f'<meta property="{prop}" content="{html_escape(value,quote=True)}"/>'
        img="https://fountain.coach"+image
        result=[tag("og:type","article" if (id.startswith("essay--") or id.startswith("solstice-reading-01--") or id=="teatro") else "website"),
                tag("og:site_name","Fountain Coach"),
                tag("og:title",title),
                tag("og:description",description),
                tag("og:url",canonical),
                tag("og:image",img),
                tag("og:image:secure_url",img),
                tag("og:image:type","image/jpeg"),
                tag("og:image:width","1200"),
                tag("og:image:height","630"),
                tag("og:image:alt",f"Principal illustration of {title}" if doc.volumes[id]["figure"] else f"First composed Fountain Press page of {title}"),
                '<meta name="twitter:card" content="summary_large_image"/>',
                f'<meta name="twitter:title" content="{html_escape(title,quote=True)}"/>',
                f'<meta name="twitter:description" content="{html_escape(description,quote=True)}"/>',
                f'<meta name="twitter:image" content="{html_escape(img,quote=True)}"/>']
        return "\n".join(result)+"\n"
    def compose(id,canonical,description):
        title=next(v["title"] for v in image_records if v["id"]==id)
        image=next(v["image"] for v in image_records if v["id"]==id)
        text=html
        if canonical!='https://fountain.coach/':
            text=checked(text,'<title>Benedikt Eickhoff — Bookshelf</title>',
                         '<title>'+html_escape(title,quote=True)+' — Fountain Press</title>')
        text=checked(text,'<link rel="canonical" href="https://fountain.coach/"/>',
                     '<link rel="canonical" href="'+html_escape(canonical,quote=True)+'"/>')
        text=checked(text,'<meta name="description" content="Essays in chronological sequence and Solstice (WT), a collection of numbered readings."/>',
                     '<meta name="description" content="'+html_escape(description,quote=True)+'"/>')
        text=checked(text,"</head>",og_headers(id,title,canonical,image,description)+"</head>")
        text=checked(text,'<body data-edition-id="benedikt-eickhoff-bookshelf-20261101">',
                     '<body data-edition-id="benedikt-eickhoff-bookshelf-20261101" data-initial-volume="'+id+'">')
        return text
    for row in image_records:
        v=row["id"]
        canonical="https://fountain.coach/estate/read/"+v+"/"
        description="Read "+row["title"]+" in the source-bound Fountain Press Linotype edition."
        entry=OUT/"estate/read"/v/"index.html"
        entry.parent.mkdir(parents=True,exist_ok=True)
        entry.write_text(compose(v,canonical,description))
    # Site front doors share the same Bookshelf; they get the first authentic published folio.
    for rel in ["index.html","estate/index.html"]:
        (OUT/rel).write_text(compose("continuity","https://fountain.coach/","Fountain Coach Bookshelf: original writing, Teatro Scores, essays and First Readings."))
    # Keep existing editorial metadata and all legacy route bytes exactly unchanged.
    manifest=current.copy()
    manifest["releaseID"]=RELEASE
    manifest["previousReleaseID"]=PARENT
    manifest["sourceRevision"]=SOURCE
    manifest["publicationState"]="author-approved-principal-illustration-social-preview"
    manifest["contentScope"]="v140 verified public reader plus source-work-specific Open Graph social previews"
    manifest["socialPolicy"]="first authored illustration, else first measured published Linotype page"
    (OUT/"release-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    LIST.write_text(json.dumps({"schema":"fountain.press.folio-social-fallback.v1","items":fallback},indent=2,ensure_ascii=False)+"\n")
    (ROOT/"build/v141-social-source-inventory.json").write_text(json.dumps({"parent":PARENT,"release":RELEASE,"volumes":image_records},indent=2,ensure_ascii=False)+"\n")
    print("ASSEMBLED",len(image_records),"routes,",sum(1 for v in image_records if v["selection"]=="first-authored-illustration"),"source illustrations",len(fallback),"first-folio screenshot fallbacks")
def main_finalize():
    if not OUT.is_dir() or not LIST.is_file():fail("v141 candidate not assembled")
    items=json.loads(LIST.read_text())["items"]
    records=json.loads((ROOT/"build/v141-social-source-inventory.json").read_text())["volumes"]
    if len(items)+sum(r["selection"]=="first-authored-illustration" for r in records)!=len(records):fail("Image admission count mismatch")
    for row in records:
        f=OUT/row["image"].lstrip("/")
        if not f.is_file():fail("Missing required social principal "+row["image"])
        result=subprocess.run(["magick","identify","-format","%wx%h %m",str(f)],capture_output=True,text=True)
        if result.returncode or result.stdout.strip()!="1200x630 JPEG":fail("Invalid social JPEG "+str(f)+": "+result.stdout.strip())
        if f.stat().st_size<3000:fail("Empty social art "+str(f))
        row["imageSHA256"]=digest(f.read_bytes())
        html=(OUT/"estate/read"/row["id"]/"index.html").read_text()
        if ('content="https://fountain.coach'+row["image"]+'"') not in html:
            fail("Wrong per-edition OG image for "+row["id"])
        if ('data-initial-volume="'+row["id"]+'"') not in html:fail("wrong rendered route identity")
    old={str(p.relative_to(BASE)):digest(p.read_bytes()) for p in BASE.rglob("*") if p.is_file()}
    new={str(p.relative_to(OUT)):digest(p.read_bytes()) for p in OUT.rglob("*") if p.is_file()}
    replaced={r for r in old if old[r]!=new.get(r)}
    authorized={"index.html","estate/index.html","estate/assets/linotype/reading-first-app.js","release-manifest.json"}
    if replaced!=authorized:fail("Existing public files changed beyond OG/reader route: "+str(replaced))
    added=set(new)-set(old)
    if len(added)!=2*len(records):fail("Expected one static route and one social JPEG per volume")
    m={"schema":"fountain.press.social-publication-proof.v1","parent":PARENT,"release":RELEASE,"sourceCommit":SOURCE,
       "rootSourceSHA256":ROOT_SHA,"volumeCount":len(records),"firstFigureCount":len(records)-len(items),"firstFolioCount":len(items),
       "modified":sorted(replaced),"added":sorted(added),"volumeEvidence":records,
       "files":[{"path":k,"sha256":v,"bytes":(OUT/k).stat().st_size} for k,v in sorted(new.items())]}
    WITNESS.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n")
    print("FINAL_CANDIDATE",RELEASE,"files",len(new),"preserved",len(old)-len(replaced),"new",len(added),"fallbacks",len(items))
def main_refresh_v152():
    """Refresh the executed public overlay from exact, prebuilt v152 source.

    Local packaging only. Keep the public grants, final audio and direct-route
    adapter; transfer only through the existing native publisher afterward.
    """
    source_repo=Path(os.environ["FOUNTAIN_V152_SOURCE_REPO"]).resolve()
    stage=ROOT/"build/private-source-v152"
    source="1609cb909ae2f89b4b28223fe70c482638d6b854"
    parent="estate-20261103-v21-social-principal-fb47bd0"
    release="estate-20261105-v22-reader-v152-1609cb9"
    baseline=ROOT/"build/public-release-v141-social"
    out=ROOT/"build/public-release-v152"
    if out.exists():fail("Refusing to overwrite immutable v152 candidate")
    old_manifest=json.loads((ROOT/"releases/v141-native-published-static-release.json").read_text())
    if old_manifest["releaseID"]!=parent:fail("Wrong public predecessor")
    old={row["path"].lstrip("/"):row["sha256"] for row in old_manifest["files"]}
    actual={str(p.relative_to(baseline)):digest(p.read_bytes()) for p in baseline.rglob("*") if p.is_file()}
    if old!=actual:fail("Local published predecessor bytes differ from native manifest")
    def git_bytes(path,revision=source):
        return subprocess.check_output(["git","-C",str(source_repo),"show",revision+":"+path])
    prefix="scenarios/reading-first-20261101/"
    locked={
        "index.html":"77f90b8db05a42700f727b4558f7e91a6406e2ae6bf25d59d953fa5ddae7b3d9",
        "reading-first-app.js":"9fa017c008cebad8586a49a03741aae398a36a0fc61e935364f45b6e913b6345",
        "reading-first-press-engine.js":"e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a",
        "reading-first-press-frame.css":"8e175ccbdfdd71e506979772059c72fcfb85de8d3daa366a34544ccc7d4502e6",
    }
    stage_paths={name:("estate/index.html" if name=="index.html" else "estate/assets/linotype/"+name) for name in locked}
    admission=json.loads((stage/"source-lock.json").read_text())["machineReadingEditorialArchiveAdmission"]
    if admission["sourceCommit"]!=source or admission["release"]!="shared-shell-20261105-v152-editorial-archive-1609cb9":
        fail("Wrong staged source admission")
    inputs={name:(stage/stage_paths[name]).read_bytes() for name in locked}
    for name,data in inputs.items():
        if digest(data)!=locked[name]:fail("Unverified v152 source "+name)
        if name!="index.html" and data!=git_bytes(prefix+name):fail("Staged runtime differs from pinned Git source: "+name)
    html=inputs["index.html"].decode()
    if any(s in html for s in ("private-auditions/","192.168.","localhost:")):
        fail("Private origin or audition in authored Reader")
    doc=PressVolumes();doc.feed(html)
    prior_ids={p.parent.name for p in (baseline/"estate/read").glob("*/index.html")}
    modern="essay--what-makes-a-page-modern"
    if set(doc.volumes)-prior_ids!={modern} or prior_ids-set(doc.volumes):
        fail("Unexpected Reader source identity delta")
    shutil.copytree(baseline,out)
    # Apply only the source-owned archival app delta to the already-published
    # app. The public narrator grants and v141 pathname/history handling stay.
    app=(baseline/"estate/assets/linotype/reading-first-app.js").read_text()
    diff=subprocess.check_output(["git","-C",str(source_repo),"diff","--unified=3",
        "611c3e34c9dfffc932d86d957edf49bda46927ec",source,"--",prefix+"reading-first-app.js"],text=True)
    hunks=re.split(r"^@@[^\n]*\n",diff,flags=re.M)[1:]
    if not hunks:fail("Expected v152 archival app change")
    for hunk in hunks:
        lines=hunk.splitlines(keepends=True)
        before="".join(line[1:] for line in lines if line.startswith((" ","-")))
        after="".join(line[1:] for line in lines if line.startswith((" ","+")))
        app=checked(app,before,after)
    if 'const direct=pathname.match' not in app or 'archivedEssays' not in app:
        fail("Public paths or archival membership missing")
    for forbidden in ("private-wlan-rehearsal",".private.json","192.168."):
        if forbidden in app:fail("Private binding in public app: "+forbidden)
    (out/"estate/assets/linotype/reading-first-app.js").write_text(app)
    for name in ("reading-first-press-engine.js","reading-first-press-frame.css"):
        (out/"estate/assets/linotype"/name).write_bytes(inputs[name])
    # Original authored SVGs only; no private source manuscript or auditions.
    asset_prefix="site/essays/what-makes-a-page-modern/assets/"
    asset_paths=subprocess.check_output(["git","-C",str(source_repo),"ls-tree","-r","--name-only",source,"--",asset_prefix],text=True).splitlines()
    if len(asset_paths)!=13 or any(not p.endswith(".svg") for p in asset_paths):
        fail("Unexpected modern-page illustration inventory")
    for path in asset_paths:
        target=out/"estate/essays/what-makes-a-page-modern/assets"/Path(path).name
        target.parent.mkdir(parents=True,exist_ok=True)
        data=git_bytes(path)
        staged=(stage/"estate/essays/what-makes-a-page-modern/assets"/Path(path).name).read_bytes()
        if staged!=data:fail("Staged illustration differs from source: "+path)
        target.write_bytes(data)
    # Reuse the published per-work social headers, replacing only their Reader
    # body with the exact source. New work uses the same existing wrapper.
    body=html.split("</head>",1)[1]
    marker='<body data-edition-id="benedikt-eickhoff-bookshelf-20261101">'
    if body.count(marker)!=1:fail("Reader source body identity changed")
    for rel in ["index.html","estate/index.html"]+["estate/read/"+v+"/index.html" for v in sorted(prior_ids)]:
        original=(baseline/rel).read_text()
        found=re.search(r'data-initial-volume="([a-z0-9-]+)"',original)
        if not found:fail("Published initial volume missing: "+rel)
        head=original.split("</head>",1)[0]+"</head>"
        (out/rel).write_text(head+checked(body,marker,marker[:-1]+' data-initial-volume="'+found[1]+'">'))
    meta=doc.volumes[modern]
    src=meta["figure"]
    if not src or not src.startswith("/estate/essays/what-makes-a-page-modern/assets/"):
        fail("New work lacks a source-owned principal illustration")
    social=out/"estate/assets/social/v152"/(modern+".jpg")
    social.parent.mkdir(parents=True,exist_ok=True)
    intermediate=ROOT/"build/v152-modern-principal.png"
    subprocess.run(["rsvg-convert","--keep-aspect-ratio","-w","1200","-h","630","-o",str(intermediate),str(out/src.lstrip("/"))],check=True)
    subprocess.run(["magick",str(intermediate),"-resize","1200x630","-background","#efeee9","-gravity","center","-extent","1200x630","-alpha","remove","-alpha","off","-strip","-quality","88",str(social)],check=True)
    model="essay--the-ear-that-learns"
    head=(baseline/"estate/read"/model/"index.html").read_text().split("</head>",1)[0]+"</head>"
    head=head.replace(model,modern).replace("The Ear That Learns",meta["title"].strip())
    head=head.replace("/estate/assets/social/v141/"+modern+".jpg","/estate/assets/social/v152/"+modern+".jpg")
    target=out/"estate/read"/modern/"index.html";target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(head+checked(body,marker,marker[:-1]+' data-initial-volume="'+modern+'">'))
    # Reuse the v152 archival projection on each separately published gallery;
    # original direct essay URLs and all their files stay byte-identical.
    archive_module={"__name__":"pinned_archive_projection"}
    exec(compile(git_bytes(prefix+"archive_gallery_projection.py"),"pinned-archive-gallery.py","exec"),archive_module)
    gallery_proof=[]
    for rel,locale in (("essays/index.html","source"),("estate/essays/index.html","stage")):
        original=(baseline/rel).read_bytes()
        projected,receipt=archive_module["transform"](original,digest(original),locale)
        (out/rel).write_bytes(projected);gallery_proof.append({"path":rel,**receipt})
    share=out/"estate/assets/essay-share/manifest.json"
    share.write_bytes(git_bytes(prefix+"essay-share-manifest.json"))
    manifest=json.loads((baseline/"release-manifest.json").read_text())
    manifest.update(releaseID=release,previousReleaseID=parent,sourceRevision=source,
        stageRelease="shared-shell-20261105-v152-editorial-archive-1609cb9",
        publicationState="owner-authorized-v152-reader-and-archive",
        contentScope="v152 Reader, five current Essays, 30 First Readings; existing public media and historical routes retained",
        authorDecision="2026-11-05: publish accepted v152 staging to production; existing final-media grants retained",
        generatorSHA256=digest(Path(__file__).read_bytes()))
    (out/"release-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    new={str(p.relative_to(out)):digest(p.read_bytes()) for p in out.rglob("*") if p.is_file()}
    modified={p for p in old if old[p]!=new.get(p)}
    allowed={"index.html","estate/index.html","estate/assets/linotype/reading-first-app.js",
        "estate/assets/linotype/reading-first-press-engine.js","estate/assets/linotype/reading-first-press-frame.css",
        "essays/index.html","estate/essays/index.html","release-manifest.json"}
    allowed.update("estate/read/"+v+"/index.html" for v in prior_ids)
    if modified!=allowed or set(old)-set(new):fail("Unexpected changed or removed public file")
    added=set(new)-set(old)
    allowed_added={"estate/essays/what-makes-a-page-modern/assets/"+Path(p).name for p in asset_paths}
    allowed_added.update({"estate/read/"+modern+"/index.html","estate/assets/social/v152/"+modern+".jpg","estate/assets/essay-share/manifest.json"})
    if added!=allowed_added:fail("Unexpected added public asset")
    report={"schema":"fountain.press.v152.public-overlay.v1","release":release,"predecessor":parent,
        "sourceCommit":source,"sourceInputs":locked,
        "gitSourceHTMLSHA256":digest(git_bytes(prefix+"index.html")),
        "stagedProjectionHTMLSHA256":locked["index.html"],
        "generatorSHA256":manifest["generatorSHA256"],
        "currentEssays":5,"currentFirstReadings":30,"sourceVolumes":len(doc.volumes),
        "modified":sorted(modified),"added":sorted(added),"preservedFiles":len(old)-len(modified),
        "galleryProof":gallery_proof,"privateAuditionsIncluded":False,
        "files":[{"path":p,"sha256":h,"bytes":(out/p).stat().st_size} for p,h in sorted(new.items())]}
    (ROOT/"build/v152-production-overlay-witness.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("V152_CANDIDATE",release,"files",len(new),"bytes",sum((out/p).stat().st_size for p in new),"preserved",report["preservedFiles"])

def main_isolate_v152_cache():
    """Keep the accepted Reader bytes; bind each HTML to its exact runtime bytes.

    Embedded browsers can retain the former app at the unchanged asset URL.
    Mixing that v141 app with v152's five-essay HTML throws before composition.
    Content-addressed paths prevent that collision without changing the reader.
    """
    baseline=ROOT/"build/public-release-v152"
    out=ROOT/"build/public-release-v152-cache-isolated"
    prior=json.loads((ROOT/"releases/v152-native-static-release.json").read_text())
    parent="estate-20261105-v22-reader-v152-1609cb9"
    if prior["releaseID"]!=parent:fail("Wrong cache-repair predecessor")
    old={f["path"].lstrip("/"):f["sha256"] for f in prior["files"]}
    observed={str(p.relative_to(baseline)):digest(p.read_bytes()) for p in baseline.rglob("*") if p.is_file()}
    if observed!=old:fail("Published v152 baseline inventory mismatch")
    if out.exists():fail("Refusing to overwrite immutable cache-isolated candidate")
    revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    release="estate-20261105-v23-reader-cache-"+revision[:7]
    shutil.copytree(baseline,out)
    assets={}
    for name in ("reading-first-app.js","reading-first-press-engine.js","reading-first-press-frame.css"):
        relative="estate/assets/linotype/"+name
        file=Path(relative)
        fingerprint=str(file.with_name(file.stem+"."+old[relative]+file.suffix))
        (out/fingerprint).write_bytes((baseline/relative).read_bytes())
        assets[relative]=fingerprint
    html_paths=[]
    for relative in sorted(old):
        if not relative.endswith(".html"):continue
        html=(baseline/relative).read_text()
        if 'src="/estate/assets/linotype/reading-first-app.js"' not in html:continue
        for original,fingerprint in assets.items():
            html=checked(html,'"/'+original+'"','"/'+fingerprint+'"')
        (out/relative).write_text(html)
        html_paths.append(relative)
    if len(html_paths)!=51:fail("Unexpected Reader route inventory")
    manifest=json.loads((baseline/"release-manifest.json").read_text())
    manifest.update(releaseID=release,previousReleaseID=parent,sourceRevision=revision,
        publicationState="v152-reader-cache-isolated",
        generatorSHA256=digest(Path(__file__).read_bytes()),contentAddressedReaderAssets=assets)
    (out/"release-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    new={str(p.relative_to(out)):digest(p.read_bytes()) for p in out.rglob("*") if p.is_file()}
    modified={p for p in old if old[p]!=new.get(p)}
    if modified!=set(html_paths)|{"release-manifest.json"} or set(old)-set(new):fail("Unexpected cache repair changes")
    if set(new)-set(old)!=set(assets.values()):fail("Unexpected cache repair additions")
    report={"schema":"fountain.press.cache-isolation.v1","release":release,"predecessor":parent,
        "sourceCommit":revision,"assets":assets,"modified":sorted(modified),
        "added":sorted(set(new)-set(old)),"preservedFiles":len(old)-len(modified),
        "readerRuntimeBytesChanged":False,"files":[{"path":p,"sha256":h} for p,h in sorted(new.items())]}
    (ROOT/"build/v152-cache-isolation-witness.json").write_text(json.dumps(report,indent=2)+"\n")
    print("CACHE_ISOLATED_CANDIDATE",release,"files",len(new),"readerRoutes",len(html_paths),"preserved",report["preservedFiles"])

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("assemble","finalize","refresh-v152","isolate-v152-cache"):raise SystemExit("Usage: build_v141_social.py assemble|finalize|refresh-v152|isolate-v152-cache")
    if sys.argv[1]=="assemble":main_assemble()
    elif sys.argv[1]=="finalize":main_finalize()
    elif sys.argv[1]=="refresh-v152":main_refresh_v152()
    else:main_isolate_v152_cache()
