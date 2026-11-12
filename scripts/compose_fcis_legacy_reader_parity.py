#!/usr/bin/env python3
"""Reconcile legacy Fountain Press direct Reader entrances to the current book source.

The current work's manuscript, images, social cards and main Reader are byte-identical
to the already published v198 release. This is strictly a source-template/gallery/
content-addressed runtime projection for older static entrance documents.
"""
from pathlib import Path
import argparse,re,hashlib,shutil,json,html

SOURCE_ID="essay--the-value-of-what-we-can-prove"
RELEASE="fountain-press-fcis-value-nav-20261112-v199"
OLD_RELEASE="fountain-press-fcis-value-20261112-ba6a653"
APP_OLD="1b574fe1d24004a7c4d25ecc5df31cb098ac0784f4a87158ac5208d7cda06dd7"
ENGINE_OLD="e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a"
APP_NEW="233205de4f9ce94289086bb23e31b0df45009818438bc0eff03a4e2688299c68"
ENGINE_NEW="837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a"
def sha(b):return hashlib.sha256(b).hexdigest()
TEMPLATE_PATTERN=r'<template data-reader-volume="([^"]+)"[^>]*>.*?</template>'
def templates(s):
    return list(re.finditer(TEMPLATE_PATTERN,s,re.S))
def gallery(s):
    p=r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)'
    x=list(re.finditer(p,s,re.S))
    if len(x)!=1:raise RuntimeError("Reader gallery seam missing")
    return x[0]
def names(s):
    return [m.group(1) for m in templates(s)]
def update(entry,root):
    oldmatches=templates(entry);newmatches=templates(root)
    if len(oldmatches)!=51 or len(newmatches)!=76:
        raise RuntimeError("Unexpected old/new Reader identities")
    old_names=names(entry);new_names=names(root)
    if len(set(old_names))!=len(old_names) or len(set(new_names))!=len(new_names):
        raise RuntimeError("Duplicate source volume identities")
    if not set(old_names).issubset(set(new_names)):
        missing=sorted(set(old_names)-set(new_names))
        raise RuntimeError("New source would delete legacy source volumes "+str(missing))
    # Keep every inherited exact source template, changing only the inventory.
    old_records={m.group(1):m.group(0) for m in oldmatches}
    new_records={m.group(1):m.group(0) for m in newmatches}
    changed=[k for k in old_records if old_records[k]!=new_records[k]]
    # These two collection projections were explicitly revised by the new
    # essay; every authored work template must remain exact-byte identical.
    if set(changed)-{"library","essays"}:
        raise RuntimeError("Legacy authored template drift "+str(changed))
    all_templates="\n".join(m.group(0) for m in newmatches)+"\n"
    first=oldmatches[0].start()
    s=entry[:first]+all_templates+re.sub(TEMPLATE_PATTERN,"",entry[first:],flags=re.S)
    g=gallery(s);newg=gallery(root)
    olddata=json.loads(g.group(2));newdata=json.loads(newg.group(2))
    for key,v in olddata["collections"].items():
        old_items={i["id"]:i for i in v}
        new_items={i["id"]:i for i in newdata["collections"].get(key,[])}
        for item in old_items:
            if item not in new_items or old_items[item]!=new_items[item]:
                raise RuntimeError("Old gallery source item lost or altered "+item)
    s=s[:g.start(2)]+newg.group(2)+s[g.end(2):]
    for old,new,label in [
      (f"reading-first-app.{APP_OLD}.js",f"reading-first-app.{APP_NEW}.js","Reader app"),
      (f"reading-first-press-engine.{ENGINE_OLD}.js",f"reading-first-press-engine.{ENGINE_NEW}.js","Press engine")
    ]:
        if s.count(old)!=1:raise RuntimeError("Unexpected "+label+" reference")
        s=s.replace(old,new)
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--predecessor",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    old,out=args.predecessor,args.output
    if out.exists():raise RuntimeError("Never overwrite candidate")
    source=(old/"estate/index.html").read_text()
    if len(names(source))!=76 or source.count(SOURCE_ID)<3:
        raise RuntimeError("Current public source/essay identity not established")
    # Only source-owned book aliases and essay direct entries are in scope.
    candidates=[*sorted((old/"estate/read").glob("essay--*/index.html"))]
    for q in ["estate/bookshelf/index.html","estate/read/library/index.html","estate/editions/index.html","estate/collections/first-readings/index.html"]:
        path=old/q
        if path.exists():candidates.append(path)
    # The older archive-only sources not in the current 76-template Reader are retained.
    excluded=[]
    selected=[]
    for path in candidates:
        contents=path.read_text()
        if '<template data-reader-volume="library">' not in contents:continue
        if len(names(contents))!=51:continue
        if not set(names(contents)).issubset(set(names(source))):
            excluded.append(path.relative_to(old).as_posix())
            continue
        selected.append(path.relative_to(old).as_posix())
    if "estate/read/essay--client-centered/index.html" not in selected:
        raise RuntimeError("Known semantic bug route not in scope")
    shutil.copytree(old,out,copy_function=shutil.copy2)
    for relative in selected:
        path=out/relative
        original=path.read_text()
        rewritten=update(original,source)
        if original==rewritten:raise RuntimeError("No semantic source change "+relative)
        path.write_text(rewritten)
    # Reconciliation does not change the essay edition, only legacy entrances.
    prior=json.loads((old/"release-manifest.json").read_text())
    if prior.get("releaseID")!=OLD_RELEASE:
        raise RuntimeError("Public release predecessor metadata changed")
    release=dict(prior)
    release.update({
        "previousReleaseID":OLD_RELEASE,"releaseID":RELEASE,
        "publicationState":"published-reader-legacy-source-parity-corrected",
        "navigationCorrection":{
            "scope":"Older direct essay and Bookshelf Reader entrances only",
            "sourceVolumeInventory":76,"currentEssays":8,
            "sourceAndMediaUnchanged":True,"modifiedReaderEntrances":selected,
            "publicPredecessor":OLD_RELEASE,
            "authorDecision":"Complete semantic production integration, 2026-11-12"
        }
    })
    (out/"release-manifest.json").write_text(json.dumps(release,indent=2,ensure_ascii=False)+"\n")
    before={p.relative_to(old).as_posix():sha(p.read_bytes()) for p in old.rglob("*") if p.is_file()}
    after={p.relative_to(out).as_posix():sha(p.read_bytes()) for p in out.rglob("*") if p.is_file()}
    if set(before)!=set(after):raise RuntimeError("Published route inventory changed")
    changed={key:after[key] for key in sorted(after) if after[key]!=before[key]}
    if set(changed)!=set(selected)|{"release-manifest.json"}:raise RuntimeError("Unexpected changed paths")
    (out.parent/"fcis-value-legacy-reader-parity.json").write_text(json.dumps({
        "schema":"fountain.press.legacy-entry-source-parity.v1",
        "predecessor":OLD_RELEASE,"newRelease":RELEASE,"modifiedPaths":changed,
        "excludedLegacyArchivePaths":excluded,"unchangedProductionFiles":len(before)-len(changed),
        "sourceAndOriginalMediaUnchanged":True,"newSourceTemplateCount":76,
        "essaysContentsCount":8,"publicDelivery":False
    },indent=2)+"\n")
    print("LEGACY_READER_PARITY_CANDIDATE",len(changed),"updated",len(excluded),"excluded",len(before)-len(changed),"preserved")
    print("UPDATED",list(changed))
    print("EXCLUDED",excluded)
if __name__=="__main__":main()
