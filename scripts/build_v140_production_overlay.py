#!/usr/bin/env python3
"""Preserve current public v19 exactly except the explicitly approved reader delta.
Writes a local immutable release candidate, never contacts production.
"""
from pathlib import Path
import hashlib, json, shutil, subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"build/production-v19-readonly"
READER=ROOT/"build/public-full-v140"
OUT=ROOT/"build/public-release-v140-overlay"
SOURCE="611c3e34c9dfffc932d86d957edf49bda46927ec"
PREVIOUS="estate-20261027-v19-door-score-accepted-shell-824404f"
RELEASE="estate-20261103-v20-vergil-reader-611c3e3"
EXPECTED_ROOT="9814fc24e3018c36f310f0bc8da3ccaa3251e0100404be3da0b7dad8e7c02309"
def digest(file):return hashlib.sha256(file.read_bytes()).hexdigest()

assert subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()==SOURCE
if OUT.exists():raise SystemExit("Refusing to overwrite immutable local release "+str(OUT))
if digest(BASE/"index.html")!=EXPECTED_ROOT:raise SystemExit("Production v19 original root digest does not match public witness")
if len([p for p in BASE.rglob("*") if p.is_file()])!=66:raise SystemExit("Current v19 file inventory changed")
reader_manifest=json.loads((READER/"public-v140-inventory.json").read_text())
if reader_manifest["source"]["commit"]!=SOURCE:raise SystemExit("Reader source SHA changed")
for item in reader_manifest["files"]:
    path=READER/item["path"]
    if digest(path)!=item["sha256"]:raise SystemExit("Reader asset changed "+item["path"])
# Baseline owned by the exact current deployed release, not by an older Git snapshot.
shutil.copytree(BASE,OUT)
preserved=set(str(p.relative_to(BASE)) for p in BASE.rglob("*") if p.is_file())
modified=set();added=set()
for source in sorted(READER.rglob("*")):
    if not source.is_file():continue
    rel=str(source.relative_to(READER))
    if rel=="public-v140-inventory.json":continue
    if rel.startswith(("evidence/","scenarios/","media/vergil-private-auditions/")):raise SystemExit("Private path in candidate")
    target=OUT/rel
    if target.is_file():
        if rel!="index.html" and digest(target)!=digest(source):
            raise SystemExit("Unexpected overwrite of live public asset "+rel)
        if digest(target)!=digest(source):modified.add(rel)
    else:added.add(rel)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
if modified!={"index.html"}:raise SystemExit("Unexpected modified live files "+repr(modified))
if len(added)<120:raise SystemExit("New public reader assets missing")
# Preserve all public v19 file bytes except manifest and the explicitly amended homepage.
for rel in preserved-{"index.html","release-manifest.json"}:
    if digest(BASE/rel)!=digest(OUT/rel):raise SystemExit("Baseline was altered "+rel)
manifest={
 "schemaVersion":1,
 "host":"fountain.coach",
 "releaseID":RELEASE,
 "previousReleaseID":PREVIOUS,
 "sourceRepo":"Fountain-Coach/fountain.coach",
 "sourceRevision":SOURCE,
 "publicationState":"author-approved-source-verified-v140-reader",
 "authorDecision":"2026-11-03: publish complete v140 Linotype staging reader and final two Vergil readings",
 "stageRelease":"shared-shell-20261103-v140-same-folio-return",
 "releaseMode":"existing-EstatePublisher-SSH-static-immutable",
 "publicURL":"https://fountain.coach/",
 "contentScope":"v140 complete literary reader, final Vergil recordings, MIDI2 reading-score events, Csound and Door sounds",
 "publicationExclusions":["unreleased audition and review recordings","stage-only evidence","private rehearsal grants","secrets","unreleased WAV masters"],
 "recordings":reader_manifest["recordings"],
 "preservedPublicReleaseFiles":len(preserved)-2,
 "addedPaths":len(added),
 "modifiedPaths":sorted(modified),
 "assetManifest":"native-EstatePublisher-prepare-manifest",
}
(OUT/"release-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
allfiles=sorted(p for p in OUT.rglob("*") if p.is_file())
report={
 "schema":"fountain.coach.v140.production-baseline-overlay.v1",
 "predecessor":PREVIOUS, "releaseID":RELEASE, "sourceCommit":SOURCE,
 "baselineRootSHA256":EXPECTED_ROOT,
 "preservedPaths":sorted(preserved-{"index.html","release-manifest.json"}),
 "modifiedPaths":sorted(modified|{"release-manifest.json"}),
 "addedPaths":sorted(added),
 "files":[{"path":str(p.relative_to(OUT)),"bytes":p.stat().st_size,"sha256":digest(p)} for p in allfiles],
}
(ROOT/"build/v140-production-overlay-witness.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print("RELEASE_READY",RELEASE,"FILES",len(allfiles),"PRESERVED",len(report["preservedPaths"]),"ADDED",len(added),"MODIFIED",sorted(report["modifiedPaths"]))
print("BYTES",sum(p.stat().st_size for p in allfiles),"SOURCE",SOURCE)
