#!/usr/bin/env python3
"""A real Csound A/B audition in the ALREADY INSTALLED SatzfunkPlayer/Reader.

Only the essay source template and its existing Reader controller are updated.
The four unrelated Door recordings, other works and player implementation stay.
"""
import argparse
import hashlib
import html
import importlib.util
import json
import re
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
TEATRO=Path("/Users/benedikteickhoff/Developer/teatro-kino-interlude-20261105")
ORIGINAL=HERE/"a-sound-must-earn-its-place.md"
REVISED=HERE/"a-sound-must-earn-its-place-v2.md"
OLD_SCRIPT=HERE/"build_stage_proof.py"
ORIGINAL_SHA="53b5f7369f68548f211571bdaf5fa4d92bbc85b3fed30aedf8839eaf8e293b7c"
BASE_INDEX_SHA="4c9298785fa505f8971429be9cf42b10682acc950b534194415193c87472e757"
BASE_APP_SHA="9fc914956045523522a1a4557721bb22a20fe995cb82f2f8c85c053f1f929f09"
VOLUME="essay--a-sound-must-earn-its-place"
MOUNT="estate/media/kino/sound-craft"
MARKER="[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]"

def sha(data):return hashlib.sha256(data).hexdigest()
def replace_once(s,old,new):
    if s.count(old)!=1:raise ValueError("Unrecognized exact reader source anchor "+old[:75])
    return s.replace(old,new,1)
def inline(text):
    x=html.escape(text,quote=True)
    x=re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",x)
    return re.sub(r"\*(.+?)\*",r"<em>\1</em>",x)
def original_template():
    if sha(ORIGINAL.read_bytes())!=ORIGINAL_SHA:raise ValueError("Original source changed")
    spec=importlib.util.spec_from_file_location("original_sound_proof",OLD_SCRIPT)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.make_template(ORIGINAL.read_text())[0]
def media_source():
    manifest=json.loads((TEATRO/"scripts/kino-interlude/sound-craft-contrast/manifest.json").read_text())
    if (manifest["schema"]!="fountain.teatro.sound-craft-comparison.v1"
        or manifest.get("noOutsideRecordings") is not True
        or len(manifest["files"])!=2
        or [x["id"] for x in manifest["files"]]!=["a-literal","b-directed"]
        or not re.fullmatch(r"[0-9a-f]{64}",manifest["sourceScoreSHA256"])):
        raise ValueError("Unrecognized original Csound score pair")
    for e in manifest["files"]:
        for filekey,digestkey in (("csoundPatch","csoundSHA256"),
                                  ("previewMedia","previewMediaSHA256")):
            data=(TEATRO/e[filekey]).read_bytes()
            if sha(data)!=e[digestkey]:raise ValueError("Source Csound/M4A changed")
        if e["renderFacts"]["durationSeconds"]!=16:
            raise ValueError("Csound pair not same duration")
    if abs(manifest["files"][0]["renderFacts"]["rmsLinear"]-
           manifest["files"][1]["renderFacts"]["rmsLinear"])>.003:
        raise ValueError("Level unmatched")
    return manifest
def essay_template(markdown):
    blocks=[p.strip() for p in markdown.split("\n\n") if p.strip()]
    if (blocks[0]!="# A Sound Must Earn Its Place"
        or not blocks[1].startswith("*On acoustic craft")
        or not blocks[2].startswith("**Status:** Revised editorial proof")
        or blocks.count(MARKER)!=1):
        raise ValueError("Unrecognized edited proof")
    nodes=[];n=0
    for text in [blocks[1]]+blocks[3:]:
        if text==MARKER:
            nodes.append(
                '<figure class="frame-press-av frame-sound-craft-ab" '
                'data-press-media="satzfunk-csound-kino-a-b" '
                'data-keep-with-anchor="previous" '
                'data-source-block="a-sound-must-earn-its-place.audio-ab" '
                'style="max-width:100%;box-sizing:border-box;'
                'padding:0.45em 0.25em;display:grid;gap:0.35em;">'
                '<div class="frame-sound-craft-take">'
                '<p data-source-block="a-sound-must-earn-its-place.audio-a" '
                'style="font-size:.82em;margin:0 0 .18em;">A — literal Csound pass</p>'
                '<satzfunk-player compact data-sound-track-id="a-literal" '
                'label="A — literal Csound pass" '
                'style="display:block;width:100%;min-height:44px;"></satzfunk-player></div>'
                '<div class="frame-sound-craft-take">'
                '<p data-source-block="a-sound-must-earn-its-place.audio-b" '
                'style="font-size:.82em;margin:0 0 .18em;">B — directed Csound pass</p>'
                '<satzfunk-player compact data-sound-track-id="b-directed" '
                'label="B — directed Csound pass" '
                'style="display:block;width:100%;min-height:44px;"></satzfunk-player></div>'
                '<p class="press-av-status" role="status" '
                'style="font-size:.75em;min-height:0;margin:0;"></p>'
                '<figcaption>One original score · two real Csound patches · '
                '16 seconds each · same measured overall level · editorial audition, not a master.</figcaption>'
                '</figure>'
            )
            continue
        if text.startswith("## "):raise ValueError("New headings would over-edit the reading")
        n+=1
        plain=text.replace("**","").replace("*","")
        nodes.append(
          f'<p data-source-block="a-sound-must-earn-its-place.p{n}" '
          f'data-source-from="0" data-source-to="{len(plain)}">{inline(text)}</p>'
        )
    return (
        f'<template data-reader-volume="{VOLUME}" data-editorial-state="proof-revision" '
        f'data-source-sha256="{sha(markdown.encode())}">'
        '<div class="book-flow" data-min-leaves="1">'
        '<section class="book-chapter" id="work-a-sound-must-earn-its-place">'
        '<div class="book-chapter-heading">'
        '<h2 data-source-block="a-sound-must-earn-its-place.title">'
        'A Sound Must Earn Its Place</h2></div></section>'
        '<section class="book-chapter-text"><article class="book-prose">'
        '<p class="frame-edition-imprint" data-source-block="editorial.proof.status">'
        'Editorial proof · Csound listening comparison · Unpublished</p>'
        + "".join(nodes) + '</article></section></div></template>'
    ),n
def stage_edition(manifest):
    tracks=[]
    for e in manifest["files"]:
        tracks.append({
          "id":e["id"],
          "title":e["title"],
          "media":"/media/kino/sound-craft/"+e["id"]+".m4a",
          "mediaSHA256":e["previewMediaSHA256"],
          "sourceSHA256":manifest["sourceScoreSHA256"],
          "csoundPatchSHA256":e["csoundSHA256"],
          "duration":16.0,
          "publicReleaseAuthorized":False,
          "privateRehearsalAuthorized":True,
        })
    return {
      "schema":"satzfunk.recorded-essay-rehearsal.v1",
      "sourceOwner":"Fountain-Coach/teatro.fountain.coach",
      "playerOwner":"Fountain-Coach/SatzfunkPlayer",
      "scoreSHA256":manifest["sourceScoreSHA256"],
      "status":"WLAN-private-csound-editorial-audition-not-public",
      "mediaBasePrefix":"/estate/",
      "tracks":tracks
    }
def proof_controller(app):
    # Exact re-use of existing SatzfunkMediaElement, the original Reader
    # transport and private-rehearsal-grant contract.
    promise="""const soundCraftPromise=fetch('/estate/media/kino/sound-craft/edition.json',{cache:'no-store'})
 .then(r=>{if(!r.ok)throw Error('Csound sound-craft edition unavailable');return r.json()})
 .then(m=>{
  if(m.schema!=='satzfunk.recorded-essay-rehearsal.v1'||m.tracks?.length!==2||
     !/^[a-f0-9]{64}$/.test(m.scoreSHA256)||
     m.tracks.some(t=>t.sourceSHA256!==m.scoreSHA256||
       t.publicReleaseAuthorized!==false||t.privateRehearsalAuthorized!==true||
       t.duration!==16))
   throw Error('Unauthenticated Csound score comparison');
  return m;
 });
"""
    app=replace_once(app,"const proofVolume='essay--a-sound-must-earn-its-place';",
                     "const proofVolume='essay--a-sound-must-earn-its-place';\n"+promise)
    amendment="""function syncSatzfunkPlayer(){
 if(volume===proofVolume){
   const players=[...viewport.querySelectorAll('satzfunk-player[data-sound-track-id]')];
   if(!players.length)return;
   for(const p of players){
     if(p.dataset.bound)continue;
     p.dataset.bound='pending';
     const status=p.closest('.frame-press-av')?.querySelector('.press-av-status');
     if(!securePlayerOrigin){
       p.hidden=true;p.dataset.bound='insecure';
       if(status)status.textContent='Listening requires the existing HTTPS rehearsal origin.';
       continue;
     }
     soundCraftPromise.then(edition=>{
       if(!p.isConnected||!viewport.contains(p))return;
       const track=edition.tracks.find(x=>x.id===p.dataset.soundTrackId);
       if(!track)throw Error('Unrecognized Csound patch source identity');
       const choose=()=>p.setEdition({origin:location.origin,
         mediaBasePrefix:edition.mediaBasePrefix,tracks:[track],
         activeTrackID:track.id,rehearsalGrant:{
          scope:'private-wlan-rehearsal',origin:location.origin,
          trackID:track.id,mediaSHA256:track.mediaSHA256,
          sourceSHA256:track.sourceSHA256
         }});
       p.addEventListener('satzfunkplayer:refused',event=>{
         if(event.detail.reason==='unreleased')
           queueMicrotask(()=>{if(p.isConnected&&viewport.contains(p))choose()});
       });
       p.addEventListener('satzfunkplayer:transport',event=>{
         if(event.detail.state!=='playing')return;
         for(const other of viewport.querySelectorAll('satzfunk-player[data-sound-track-id]')){
           if(other!==p&&other.state?.state==='ready'&&!other.state.paused)other.pause();
         }
       });
       const admitted=choose();
       p.dataset.bound=admitted.state;
       if(status)status.textContent='';
     }).catch(err=>{
       p.dataset.bound='error';
       if(status)status.textContent='Csound recording unavailable for source-bound playback.';
       console.error('Csound SatzfunkPlayer binding',err);
     });
   }
   return;
 }
"""
    return replace_once(app,"function syncSatzfunkPlayer(){",amendment)
def build(index_path,app_path,out_dir):
    base_index=Path(index_path).read_bytes()
    base_app=Path(app_path).read_bytes()
    if sha(base_index)!=BASE_INDEX_SHA or sha(base_app)!=BASE_APP_SHA:
        raise ValueError("Original accepted reader stage lineage changed")
    old=original_template()
    original=base_index.decode()
    newraw=REVISED.read_bytes()
    new,n=essay_template(newraw.decode())
    index=replace_once(original,old,new)
    app=proof_controller(base_app.decode())
    manifest=media_source()
    edition=stage_edition(manifest)
    dest=Path(out_dir)
    (dest/"estate/assets/linotype").mkdir(parents=True,exist_ok=True)
    (dest/MOUNT).mkdir(parents=True,exist_ok=True)
    (dest/"estate/index.html").write_bytes(index.encode())
    (dest/"estate/assets/linotype/reading-first-app.js").write_bytes(app.encode())
    for e in manifest["files"]:
        for name,ext in (("csoundPatch",".csd"),("previewMedia",".m4a")):
            shutil.copy2(TEATRO/e[name],dest/MOUNT/(e["id"]+ext))
    (dest/MOUNT/"edition.json").write_text(json.dumps(edition,indent=2,ensure_ascii=False)+"\n")
    (dest/MOUNT/"source-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    files={p.relative_to(dest).as_posix():sha(p.read_bytes())
           for p in (dest/"estate").rglob("*") if p.is_file()}
    receipt={
      "schema":"fountain.press.editorial-proof.csound-satzfunk.v1",
      "status":"private-stage-candidate-needs-browser-acceptance",
      "editionVolume":VOLUME,
      "editorialSourceSHA256":sha(newraw),
      "originalSourceSHA256":ORIGINAL_SHA,
      "sourceScoreSHA256":manifest["sourceScoreSHA256"],
      "actualCsoundPatches":2,
      "sourceOwnedBy":"Fountain-Coach/teatro.fountain.coach",
      "player":"existing SatzfunkMediaElement from Fountain-Coach/SatzfunkPlayer",
      "newPlayerOrReader":False,
      "synthesis":"Native Csound source CSD rendered 48kHz stereo offline",
      "nativeScenarioAdmission":False,
      "publicRelease":False,
      "privateRehearsal":True,
      "otherVolumesUnmodified":True,
      "sourceBlocks":n,
      "expectedPreviousRelease":"shared-shell-20261106-v164-governance-social-b7b1dee",
      "previousIndexSHA256":BASE_INDEX_SHA,
      "previousAppSHA256":BASE_APP_SHA,
      "outputIndexSHA256":sha(index.encode()),
      "outputAppSHA256":sha(app.encode()),
      "changedFiles":files
    }
    (dest/"editorial-csound-satzfunk-receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    return receipt
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for key in ("baseline-index","baseline-app","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.baseline_index,a.baseline_app,a.output),indent=2,ensure_ascii=False))
