#!/usr/bin/env python3
"""Source-bound, fail-closed receipt -> staging admission for v219."""
import argparse,hashlib,json
from pathlib import Path
SOURCE='fountain.press.private-v219-subtitle-candidate.v1'
TARGET='fountain.press.private-v219-subtitle-stage-admission.v1'
def make(candidate,guard):
 if (candidate.get('schema')!=SOURCE or candidate.get('status')!='PREPARED_NOT_ACTIVATED' or
     candidate.get('stageOnly') is not True or candidate.get('publicReleaseAuthorized') is not False or
     candidate.get('productionModified') is not False or candidate.get('addedPaths')!=[] or
     set(candidate.get('changedPaths',[]))!=set(candidate.get('changedFilesSHA256',{})) or
     candidate.get('noOtherWorksAltered') is not True or
     candidate.get('readerEngineUnchanged') is not True):
    raise ValueError('REFUSED private subtitle candidate admission')
 return {**candidate,'schema':TARGET,'guardSHA256':hashlib.sha256(guard).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--guard',type=Path,default=Path(__file__).parent/'serve_subtitle_v219.py');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise SystemExit('REFUSED overwriting immutable source admission')
 data=make(json.loads(a.receipt.read_text()),a.guard.read_bytes());a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('PREPARED_V219_PRIVATE_ADMISSION',data['releaseID'],len(data['changedPaths']),data['guardSHA256'])
