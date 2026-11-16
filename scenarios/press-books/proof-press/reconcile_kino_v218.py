#!/usr/bin/env python3
"""Prepare exact two-plate Kino restoration to the same immutable Press stage.

v217's fully source-locked Reader already references v156/v158 but lacked
both files. Restore the byte-identical original **public** plates. No prose,
image edit, new renderer, public release, or service mutation occurs here.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

PREDECESSOR='shared-shell-20261116-v217-proof-of-the-page-heading-proof'
RELEASE='shared-shell-20261116-v218-kino-plates-restored'
PUBLIC_ORIGIN='https://fountain.coach'
PREVIOUS_SHA='570f3a17e57211fdbce4f2fc22f015a1143190fc492886f662744c48f04d765e'
ORIGINALS={
 'estate/instruments/kino/plates/v156.png':'f2e0dc22c01a626b184983a7d8abf94d44dddfa3c0143b834706d7ca3e258d00',
 'estate/instruments/kino/plates/v158.png':'6e4ee6d8571062f9fca405b718eb1e5c561716a8f08a3d16b9cea3f89d3b9484',
}

def sha(data):return hashlib.sha256(data).hexdigest()

def verify_original_png(rel:str,data:bytes):
    if rel not in ORIGINALS or data[:8]!=b'\x89PNG\r\n\x1a\n' or sha(data)!=ORIGINALS[rel]:
        raise ValueError('REFUSED non-original public Kino image bytes: '+rel)
    return sha(data)

def build(source:Path,old_lock:Path,out:Path,receipt:Path,owner_commit:str):
    if out.exists() or receipt.exists():raise ValueError('REFUSED immutable candidate overwrite')
    if not re.fullmatch(r'[a-f0-9]{40}',owner_commit):raise ValueError('REFUSED unpinned source commit')
    old_raw=old_lock.read_bytes()
    if sha(old_raw)!=PREVIOUS_SHA:raise ValueError('REFUSED active v217 predecessor/source-lock drift')
    lock=json.loads(old_raw)
    if lock.get('pressProofV217Admission',{}).get('releaseID')!=PREDECESSOR:
        raise ValueError('REFUSED missing exact v217 release ancestry')
    if lock['pressProofV217Admission'].get('privateStageOnly') is not True:
        raise ValueError('REFUSED previous staging rights drift')
    changes={};added=[]
    out.mkdir(parents=True)
    for rel,expected in ORIGINALS.items():
        base=(source/Path(rel).name).read_bytes()
        verify_original_png(rel,base)
        dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(base)
        changes[rel]=expected;added.append(rel)
    lock['pressProofV218KinoAssetAdmission']={
        'schema':'fountain.press.kino-public-original-plates-private-reconciliation.v1',
        'releaseID':RELEASE,'predecessorReleaseID':PREDECESSOR,'sourceOwner':'Fountain-Coach/fountain.coach',
        'sourceOwnerCommit':owner_commit,'sourceOrigin':PUBLIC_ORIGIN,
        'sourceImageSHA256':ORIGINALS,'admittedAddedPaths':sorted(added),
        'originalsRetained':True,'stageOnly':True,'publicReleaseAuthorized':False,'productionModified':False,
        'reason':'Exact two missing original public assets prevent full inherited Kino essay composition in v217',
    }
    path='source-lock.json';lockbytes=(json.dumps(lock,ensure_ascii=False,indent=2)+'\n').encode()
    (out/path).write_bytes(lockbytes);changes[path]=sha(lockbytes)
    record={'schema':'fountain.press.private-kino-v218-candidate.v1','status':'PREPARED_NOT_ACTIVATED',
      'releaseID':RELEASE,'predecessorReleaseID':PREDECESSOR,
      'sourceOwnerCommit':owner_commit,'publicationLane':'private-owner-WLAN-editorial-review',
      'stageOnly':True,'publicReleaseAuthorized':False,'productionModified':False,
      'predecessorSourceLockSHA256':PREVIOUS_SHA,'changedFilesSHA256':changes,
      'addedPaths':sorted(added),'changedPaths':['source-lock.json'],
      'originalPublicSourceURLs':{rel:PUBLIC_ORIGIN+'/'+rel for rel in ORIGINALS},
      'existingCatalogueWorkCounts':{'essays':11,'first-readings':32,'orange-dot':23},
      'plannedLiveProof':'full 66-work by four-viewport no-interception Proof Press on active v218',
    }
    receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    return record

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--predecessor-lock',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--source-commit',required=True);a=p.parse_args()
 j=build(a.source,a.predecessor_lock,a.output,a.receipt,a.source_commit)
 print('SOURCE_BOUND_KINO_V218_PREPARED',j['releaseID'],j['addedPaths'])
