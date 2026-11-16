#!/usr/bin/env python3
"""Convert exact source-locked v218 private candidate to guarded admission.

Never shadow the admission schema with the candidate-receipt schema.
"""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE='fountain.press.private-kino-v218-candidate.v1'
DEST='fountain.press.private-kino-v218-stage-admission.v1'

def make(record,guard):
 if (record.get('schema')!=SOURCE or record.get('status')!='PREPARED_NOT_ACTIVATED' or
     record.get('stageOnly') is not True or record.get('publicReleaseAuthorized') is not False or
     record.get('productionModified') is not False or
     set(record.get('addedPaths',[]))|set(record.get('changedPaths',[]))!=set(record.get('changedFilesSHA256',{}))):
    raise ValueError('REFUSED invalid private Kino candidate')
 return {**record,'schema':DEST,'guardSHA256':hashlib.sha256(guard).hexdigest()}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--guard',type=Path,default=Path(__file__).parent/'serve_kino_v218.py');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise SystemExit('REFUSED overwrite admission')
 record=make(json.loads(a.receipt.read_text()),a.guard.read_bytes())
 a.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print('ADMISSION',record['releaseID'],record['guardSHA256'])
