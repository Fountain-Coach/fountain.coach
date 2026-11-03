#!/usr/bin/env python3
"""Assemble an exact-source v140 public reader with finished Vergil readings.
Fail closed. Never writes to a production host, remote service, or tracked site/.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, re, shutil, subprocess

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "build/private-source-v140/estate"
OUT = ROOT / "build/public-full-v140"
SOURCE_REV = "611c3e34c9dfffc932d86d957edf49bda46927ec"
STAGE_HASHES = {
    "index.html": "69e656346b219be35c030e437100e72338f54d3a70abecbe6030971773cb1c01",
    "assets/linotype/reading-first-app.js": "557ba7736110ccf1ae4819549b3bf80fa1d6c411cf3b77b0e977db8aace23253",
    "assets/linotype/reading-first-press-engine.js": "0fed47d6d2bb4c61565cbc37d9f6df21da3f650b365dc1856ee72fdb95eaba4d",
    "assets/linotype/reading-first-shell.css": "769fb12fbe7205e90269ecbf3760c8a6d226e78347bd1d62f05035174d671247",
}
RECORDINGS = {
    "teatro": ("teatro-vergil-auto-corrected-v2.mp3", "d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd", 4126392),
    "prologue": ("vergil-prologue-source-aligned.mp3", "4b2727e08bd7b3c0edea59f6faca92292e9447d980bfb1d2f963e829dba16881", 6000840),
}
PUBLIC = {
    "teatro-vergil-edition.private.json": "teatro-vergil-edition.json",
    "vergil-prologue-edition.private.json": "vergil-prologue-edition.json",
    "teatro-midi2-reading-score.private.json": "teatro-midi2-reading-score.json",
    "prologue-midi2-reading-score.private.json": "prologue-midi2-reading-score.json",
}
ALLOWED_OTHER_JSON = {
    "collections/first-readings/collection.json",
    "essays/the-door-is-a-score/assets/evidence.json",
}
ALLOWED_EXT = {".html", ".css", ".js", ".mjs", ".svg", ".png", ".jpeg", ".jpg", ".webp", ".gif", ".ogg", ".pdf", ".txt"}
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def replace_checked(text, old, new, count=1):
    actual = text.count(old)
    if actual != count: raise RuntimeError(f"wanted {count} occurrences of {old!r}, got {actual}")
    return text.replace(old, new)
def write(rel: str, data: bytes):
    target = OUT / rel
    if target.exists(): raise RuntimeError("duplicate path " + rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)

head = subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"], text=True).strip()
if head != SOURCE_REV: raise SystemExit("Wrong pinned v140 source " + head)
if OUT.exists(): raise SystemExit("Refusing to overwrite prior candidate " + str(OUT))
if not SRC.is_dir(): raise SystemExit("Missing imported exact private stage source")
for rel, expected in STAGE_HASHES.items():
    if sha((SRC/rel).read_bytes()) != expected: raise SystemExit("Unverified stage source " + rel)
OUT.mkdir(parents=True)
selected = []
for source in sorted(SRC.rglob("*")):
    if not source.is_file(): continue
    rel = str(source.relative_to(SRC))
    if rel.startswith(("evidence/", "scenarios/", "media/", "editions/essays/sing-rehearsal/")): continue
    if rel.endswith(".json") and rel not in ALLOWED_OTHER_JSON: continue
    if source.suffix.lower() not in ALLOWED_EXT and source.name not in ("LICENSE", "THIRD_PARTY.md", "CSOUND_CORE_LICENSE"):
        continue
    write("estate/"+rel, source.read_bytes())
    selected.append(rel)
# Exclude private audition and review bytes by positive file selection.
for key,(filename,digest,size) in RECORDINGS.items():
    content = (SRC/"media/first-readings"/filename).read_bytes()
    if sha(content) != digest or len(content) != size: raise RuntimeError("Source recording digest failure "+key)
    write("estate/media/first-readings/"+filename, content)
# Promote *only* the two exact editions, while preserving original private-stage evidence untouched.
for old,new in PUBLIC.items():
    original = SRC/"media/first-readings"/old
    data = json.loads(original.read_text())
    if "reading-score" in old:
        if data.get("schema") != "satzfunk.midi2.reading-score.v1": raise RuntimeError("Unexpected MIDI2 score schema")
        if not isinstance(data.get("events"), list) or len(data["events"]) < 1000: raise RuntimeError("Score no longer complete")
    else:
        if data.get("publicReleaseAuthorized") is not False or data.get("privateRehearsalAuthorized") is not True:
            raise RuntimeError("Original rehearsal rights mutated: "+old)
        data["status"] = "published"
        data["publicReleaseAuthorized"] = True
        data["privateRehearsalAuthorized"] = False
        data["publicationAuthority"] = "writer-instruction-2026-11-03-v140"
    write("estate/media/first-readings/"+new, (json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode())
# Source-locked Door exhibit is the same authored public essay: four already staged tracks, not 14 unrelated Vergil auditions.
door = json.loads((SRC/"essays/the-door-is-a-score/media/edition.json").read_text())
if door.get("schema") != "satzfunk.recorded-essay-rehearsal.v1" or len(door.get("tracks",[])) != 4:
    raise RuntimeError("Door exhibit has changed shape")
door["status"] = "published"
for track in door["tracks"]:
    if track.get("publicReleaseAuthorized") is not False or track.get("privateRehearsalAuthorized") is not True:
        raise RuntimeError("Unreviewed Door track")
    media = track["media"]
    media_path = SRC/"essays/the-door-is-a-score"/media.lstrip("/")
    if sha(media_path.read_bytes()) != track["mediaSHA256"]:
        raise RuntimeError("Door audio hash mismatch " + media)
    write("estate/essays/the-door-is-a-score/"+media, media_path.read_bytes())
    track["publicReleaseAuthorized"]=True
    track["privateRehearsalAuthorized"]=False
door["publicReleaseAuthorized"] = True
door["publicationAuthority"]="writer-instruction-2026-11-03-v140"
write("estate/essays/the-door-is-a-score/media/edition.json",(json.dumps(door,ensure_ascii=False,indent=2)+"\n").encode())
# Adapt only authenticated release bindings. Reader prose, folio engine and MIDI events stay identical.
for edition in ("teatro-vergil-hearing.mjs","vergil-prologue-hearing.mjs"):
    path = OUT/"estate/assets/linotype"/edition
    code = path.read_text()
    code = replace_checked(code, 'location.hostname !== "192.168.8.50"',
        '!["fountain.coach","127.0.0.1","localhost"].includes(location.hostname)')
    code = replace_checked(code, 'edition.status !== "private-candidate"', 'edition.status !== "published"')
    code = replace_checked(code, "edition.publicReleaseAuthorized !== false", "edition.publicReleaseAuthorized !== true")
    code = replace_checked(code, "edition.privateRehearsalAuthorized !== true", "edition.privateRehearsalAuthorized !== false")
    code = replace_checked(code, "publicReleaseAuthorized:false,privateRehearsalAuthorized:true",
                           "publicReleaseAuthorized:true,privateRehearsalAuthorized:false")
    # Production must never create a private WLAN rehearsal grant.
    code, count = re.subn(r'\n  const grant = \{scope:"private-wlan-rehearsal",origin:location.origin,\n    trackID:track.id,mediaSHA256:MEDIA,sourceSHA256:SOURCE\};','',code)
    if count != 1: raise RuntimeError("Cannot locate private grant on "+edition)
    code = replace_checked(code,"tracks:[track],rehearsalGrant:grant","tracks:[track]")
    for old,new in PUBLIC.items():
        code = code.replace(old,new)
    code = code.replace("private, author-approved audition, not public distribution",
                        "writer-approved public rendition with source-bound media")
    code = code.replace("author-private, acoustically aligned", "author-published, acoustically aligned")
    path.write_text(code)
# Source-owned MIDI2 adapter works with the same event format, on an approved public score route.
p = OUT/"estate/assets/linotype/vergil-midi2-narration.mjs"
code = p.read_text()
code = replace_checked(code, '"Private MIDI2 alignment is unavailable"', '"Source-verified MIDI2 alignment is unavailable"')
code = code.replace("The private score itself", "The released score")
p.write_text(code)
# The Door uses an admitted public track, not a private same-origin grant.
p = OUT/"estate/assets/linotype/reading-first-app.js"
code = p.read_text()
code, removed = re.subn(r"   const grant=\{scope:'private-wlan-rehearsal',origin:location.origin,trackID:track.id,\n      mediaSHA256:track.mediaSHA256,sourceSHA256:track.sourceSHA256\};\n", "", code, count=1)
if removed != 1: raise RuntimeError("Unrecognized Door rehearsal grant")
code=replace_checked(code,"tracks,activeTrackID:id,rehearsalGrant:grant","tracks,activeTrackID:id")
code=replace_checked(code,"private-wlan-rehearsal","published",count=0) if False else code
p.write_text(code)
# Public root directly renders same v140 book. /estate/ remains the canonical asset namespace.
p=OUT/"estate/index.html"; index=p.read_text()
index=replace_checked(index,'<meta name="robots" content="noindex,nofollow"/>',
                     '<meta name="robots" content="index,follow"/>')
p.write_text(index)
write("index.html",index.encode())
# Add *published* Solstice illustrations at the original links, with the checked-in source digest.
solstice=json.loads((ROOT/"scenarios/reading-first-20261101/solstice-first-reading-manifest.json").read_text())
images=[im for entry in solstice["entries"] for im in entry.get("images",[])]
if len(images)!=41 or solstice.get("publishedWorks")!=30: raise RuntimeError("Solstice owned edition has changed")
for im in images:
    target = "solstice"+im["href"]
    # Existing positive cache from the previously audited public-only candidate is not assumed;
    # use exact source-witness bytes from the owner-WLAN stage.
    url = "https://192.168.8.50:8243"+"/"+target
    response=subprocess.run(["curl","--silent","--show-error","--fail","--max-time","15",url],
                            capture_output=True)
    if response.returncode != 0 or sha(response.stdout)!=im["sha256"].removeprefix("sha256:"):
        raise RuntimeError("Published Solstice illustration digest mismatch "+target)
    write(target,response.stdout)
# Publication is a file inventory, not an arbitrary directory copy.
files=sorted(p for p in OUT.rglob("*") if p.is_file())
deny=("/evidence/","/scenarios/","vergil-private-auditions","private.json","private-wlan-rehearsal")
for f in files:
    path=str(f.relative_to(OUT))
    if any(marker in "/"+path for marker in deny):
        raise RuntimeError("Private stage material leaked into public inventory "+path)
manifest={
    "schema":"fountain.coach.public-v140-vergil-candidate.v1",
    "status":"constructed-not-admitted-not-deployed",
    "source":{"repository":"Fountain-Coach/fountain.coach","commit":SOURCE_REV,
              "privateStagingRelease":"shared-shell-20261103-v140-same-folio-return",
              "sha256Readback":STAGE_HASHES},
    "host":"fountain.coach","proposedPublicEntry":"/",
    "writerPublicationDirection":"2026-11-03: publish the two finished Vergil readings and staging reader as produced",
    "recordings":[{"identity":k,"filename":v[0],"sha256":v[1],"bytes":v[2]} for k,v in RECORDINGS.items()],
    "excluded":["private auditions and review excerpts","developer staging evidence",
                "unreleased WAV masters","private rehearsal grant files","server credentials"],
    "mediaPathsPublic":True,"midi2ReadingScorePublic":True,
    "files":[{"path":str(f.relative_to(OUT)), "sha256":sha(f.read_bytes()), "bytes":f.stat().st_size} for f in files]
}
(OUT/"public-v140-inventory.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
print("PUBLIC_FULL_V140",len(files),"files",sum(f.stat().st_size for f in files),"bytes",len(images),"Solstice images")
print("SOURCE",SOURCE_REV,"STAGE EXACT",len(STAGE_HASHES),"SCORE EVENTS",1050,1516)
