#!/usr/bin/env python3
"""Deterministically convert one exact stage candidate receipt to guard admission.

Never mistake the source-candidate *receipt* schema for the runtime gate's
*admission* schema. No remote effects or activation are implemented here.
"""
import argparse,hashlib,json
from pathlib import Path

EXPECTED_RECEIPT='fountain.press.cms.stage-candidate-receipt.v1'
ADMISSION='fountain.press.cms.private-wlan-stage-admission.v1'

def make(receipt:dict,guard:bytes)->dict:
    if receipt.get('schema')!=EXPECTED_RECEIPT or receipt.get('status')!='PREPARED_NOT_ACTIVATED' or receipt.get('productionModified') is not False:
        raise ValueError('REFUSED invalid source-only private-stage receipt')
    if (receipt.get('publicationLane')!='private-owner-WLAN-editorial-review' or
        set(receipt['changedFilesSHA256'])!=set(receipt['addedPaths'])|set(receipt['changedPaths'])):
        raise ValueError('REFUSED release boundary/delta mismatch')
    # Override schema LAST: a source receipt cannot overwrite the admission type.
    return {**receipt,'schema':ADMISSION,'guardSHA256':hashlib.sha256(guard).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--guard',type=Path,default=Path(__file__).parent/'serve_press_cms_v216.py')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    data=make(json.loads(a.receipt.read_text()),a.guard.read_bytes())
    a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('SOURCE_BOUND_PRIVATE_ADMISSION',data['schema'],data['releaseID'],len(data['changedFilesSHA256']))
