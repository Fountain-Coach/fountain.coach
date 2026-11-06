#!/usr/bin/env python3
"""Project two writer-selected source illustrations into v165's original Reader.

Only this essay's one source template changes. No new Reader, audio player,
re-pagination engine, public publication, added prose, or invented building fact.
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
SOURCE_V2=HERE/"a-sound-must-earn-its-place-v2.md"
SOURCE_V3=HERE/"a-sound-must-earn-its-place-v3.md"
IMAGES=HERE/"assets/illustration-source.json"
BASE_INDEX_SHA="5a2a8c084d806c515890e276be445fe34c21ca0243948d8cc088bcc70e65ab97"
BASE_APP_SHA="46876ca7b54c5f26df2372f1ec037871e61f6773a406ff41ec32a634337b7831"
VOLUME="essay--a-sound-must-earn-its-place"
OUT_DIR="estate/essays/a-sound-must-earn-its-place/media"
MARKERS=("[KINO-ILLUSTRATION:architectural-plate]","[KINO-ILLUSTRATION:night-photograph]")
SOURCE_OWNER="Fountain-Coach/fountain.coach"
def sha(data): return hashlib.sha256(data).hexdigest()

def old_builder():
    spec=importlib.util.spec_from_file_location("sound_essay_v2",HERE/"build_stage_proof_v2.py")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def validate_sources():
    v2=SOURCE_V2.read_text()
    v3=SOURCE_V3.read_text()
    for marker in MARKERS:
        if v3.count(marker)!=1:
            raise ValueError("Figure marker missing or duplicated: "+marker)
    # Exact prose, punctuation, audio comparison and 15 text source blocks preserved.
    recovered=v3
    for marker in MARKERS:
        recovered=recovered.replace("\n\n"+marker+"\n\n","\n\n",1)
    if recovered!=v2:
        raise ValueError("Unreviewed editorial prose changes")
    if not (v3.index(MARKERS[0])<v3.index(MARKERS[1])<
            v3.index("[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]")):
        raise ValueError("Wrong source visual order")
    manifest=json.loads(IMAGES.read_text())
    if manifest.get("schema")!="fountain.press.essay-authored-illustrations.v1" or manifest.get("publicRightsGranted") is not False:
        raise ValueError("Source rights not scoped to private editorial review")
    expected=["architectural-plate","night-photograph"]
    if [i.get("id") for i in manifest["figures"]]!=expected:
        raise ValueError("Wrong or reordered figure ownership")
    for i in manifest["figures"]:
        f=HERE/"assets"/i["filename"]
        if not f.is_file() or sha(f.read_bytes())!=i["sha256"]:
            raise ValueError("Source illustration changed: "+str(f))
        if not (100 < i["width"] < 4000 and 100 < i["height"] < 4000 and
                re.fullmatch(r"[a-f0-9]{64}",i["originSha256"])):
            raise ValueError("Image dimensions/provenance missing")
    return v2,v3,manifest

def figure(i):
    kind=i["id"]
    portrait=(kind=="night-photograph")
    width="min(73%,370px)" if portrait else "100%"
    tag=(
      '<figure class="linotype-inline-illustration frame-reading-figure" '
      'data-source-block="'+html.escape(i["sourceAddress"],quote=True)+'" '
      'data-source-illustration-id="'+kind+'" '
      'data-inline-after-paragraph="'+("7" if portrait else "2")+'" '
      'data-press-illustration-role="'+html.escape(i["role"])+'" '
      'data-press-media="source-photo-and-architectural-interpretation" '
      'style="box-sizing:border-box;display:block;'
      'width:'+width+';max-width:100%;padding:0;'
      'margin:.55em auto .6em;break-inside:avoid;">'
      '<img src="/'+OUT_DIR+'/'+html.escape(i["filename"],quote=True)+'" '
      'width="'+str(i["width"])+'" height="'+str(i["height"])+'" '
      'alt="'+html.escape(i["alt"],quote=True)+'" '
      'loading="eager" decoding="async" '
      'style="display:block;width:100%;height:auto;max-width:100%;'
      'aspect-ratio:'+str(i["width"])+'/'+str(i["height"])+';object-fit:contain;">'
      '<figcaption style="padding:.25em 0 0;'
      'font-size:.74em;line-height:1.28;text-align:left;">'+
       html.escape(i["caption"])+
      '</figcaption></figure>'
    )
    return tag

def template_v3(v2,v3,figures):
    prior,paragraphs=old_builder().essay_template(v2)
    if paragraphs!=15 or prior.count("<satzfunk-player compact")!=2:
        raise ValueError("Original reader source not the accepted v165 proof")
    out=prior
    prior_sha=sha(v2.encode())
    new_sha=sha(v3.encode())
    if out.count('data-source-sha256="'+prior_sha+'"')!=1:
        raise ValueError("Wrong source address or content")
    out=out.replace('data-source-sha256="'+prior_sha+'"',
                    'data-source-sha256="'+new_sha+'"',1)
    for anchor,i in (("2",figures[0]),("7",figures[1])):
        pat=r'(<p data-source-block="a-sound-must-earn-its-place\.p'+anchor+r'"[^>]*>.*?</p>)'
        if len(re.findall(pat,out,re.S))!=1:
            raise ValueError("Missing exact prose anchor "+anchor)
        out=re.sub(pat,lambda m:m.group(1)+figure(i),out,count=1,flags=re.S)
    if out.count("<figure")!=3:
        raise ValueError("Unexpected figure count")
    for i in figures:
        if out.count('data-source-illustration-id="'+i["id"]+'"')!=1:
            raise ValueError("Source image missing")
    return prior,out

def build(index_path,app_path,output):
    idx=Path(index_path).read_bytes()
    app=Path(app_path).read_bytes()
    if sha(idx)!=BASE_INDEX_SHA or sha(app)!=BASE_APP_SHA:
        raise ValueError("Unrecognized immutable v165 stage baseline")
    v2,v3,manifest=validate_sources()
    prev,next_template=template_v3(v2,v3,manifest["figures"])
    text=idx.decode()
    if text.count(prev)!=1:raise ValueError("Previous exact source template absent")
    updated=text.replace(prev,next_template,1)
    if updated.replace(next_template,prev,1)!=text:
        raise ValueError("Any other Reader/volume changed")
    out=Path(output)
    (out/"estate").mkdir(parents=True,exist_ok=True)
    target=out/OUT_DIR;target.mkdir(parents=True,exist_ok=True)
    (out/"estate/index.html").write_bytes(updated.encode())
    for i in manifest["figures"]:
        shutil.copy2(HERE/"assets"/i["filename"],target/i["filename"])
    shutil.copy2(IMAGES,target/"illustration-source.json")
    imgs=manifest["figures"]
    receipt={
      "schema":"fountain.press.kino-essay-illustrations-stage-candidate.v1",
      "state":"private-stage-candidate-not-public",
      "work":VOLUME,"sourceOwner":SOURCE_OWNER,
      "v2SourceSHA256":sha(v2.encode()),
      "v3SourceSHA256":sha(v3.encode()),
      "parentIndexSHA256":BASE_INDEX_SHA,"parentAppSHA256":BASE_APP_SHA,
      "candidateIndexSHA256":sha(updated.encode()),
      "candidateAppUnchanged":True,
      "essayBodyTextUnchanged":True,
      "csoundSatzfunkTracksUnchanged":True,
      "otherReaderVolumesUnchanged":True,
      "figureCount":2,
      "architecturalPlateInline":True,
      "socialLeadIllustrationID":"night-photograph",
      "socialLeadOriginalPhoto":True,
      "nightPhotographSourceSupplied":True,
      "architecturePlateMeasured":False,
      "publicRightsGranted":False,
      "images":[{"id":i["id"],"sourceSHA256":i["originSha256"],
                 "webSHA256":i["sha256"],"file":OUT_DIR+"/"+i["filename"]}
                for i in imgs]
    }
    receipt_path=out/"estate/evidence/press-essay-kino-illustrations-v166.json"
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("KIN0_ESSAY_IMAGES_SOURCE_CANDIDATE",json.dumps(receipt,indent=2))
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for k in ("parent-index","parent-app","out"):
        parser.add_argument("--"+k,required=True)
    a=parser.parse_args()
    build(a.parent_index,a.parent_app,a.out)
