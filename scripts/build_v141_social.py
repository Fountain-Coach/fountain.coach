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
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("assemble","finalize"):raise SystemExit("Usage: build_v141_social.py assemble|finalize")
    if sys.argv[1]=="assemble":main_assemble()
    else:main_finalize()
