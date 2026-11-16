#!/usr/bin/env python3
"""Convert one immutable private candidate receipt to source-locked gate admission."""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE='fountain.press.private-immutable-v217-candidate.v1'
DEST='fountain.press.proof-v217.private-stage-admission.v1'

def make(receipt,guard):
    if receipt.get('schema')!=SOURCE or receipt.get('status')!='PREPARED_NOT_ACTIVATED' or receipt.get('stageOnly') is not True or receipt.get('publicReleaseAuthorized') is not False or receipt.get('productionModified') is not False:
        raise ValueError('REFUSED public or unadmitted v217 candidate')
    if set(receipt['changedFilesSHA256'])!=set(receipt['changedPaths'])|set(receipt['addedPaths']):
        raise ValueError('REFUSED changed/added inventory mismatch')
    return {**receipt,'schema':DEST,'guardSHA256':hashlib.sha256(guard).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--guard',type=Path,default=Path(__file__).parent/'serve_v217_private.py');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise SystemExit('REFUSED overwrite existing release admission')
    output=make(json.loads(a.receipt.read_text()),a.guard.read_bytes())
    a.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('PREPARED_PRIVATE_V217',output['releaseID'],len(output['changedFilesSHA256']),output['guardSHA256'])
