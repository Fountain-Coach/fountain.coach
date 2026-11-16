#!/usr/bin/env python3
"""One source-locked extension of the *existing* Press typesetter keep-with-next.

No new renderer, no manuscript edit, no CSS padding and no source reflow
outside the normal measured compositor. A new hashed engine keeps v216 intact.
"""
import hashlib
from pathlib import Path

PRIOR='837c57731e872c8525a671a6f588e0112f92a11445cb8c640e90653231a5686a'
OLD='if(this.pageFrame&&this.css.spread&&\n           element.matches(".frame-subheading")&&elements[i+1]?.tagName==="P"){'
NEW='if(this.pageFrame&&\n           element.matches(".frame-subheading")&&elements[i+1]?.tagName==="P"){'

def patch(data:bytes)->bytes:
    if hashlib.sha256(data).hexdigest()!=PRIOR:
        raise ValueError('REFUSED old Reader engine drift')
    s=data.decode('utf8')
    if s.count(OLD)!=1:raise ValueError('REFUSED heading break contract not unique')
    s=s.replace(OLD,NEW,1)
    assert s.count(NEW)==1
    return s.encode('utf8')

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--input',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
    if args.output.exists():raise SystemExit('REFUSED overwrite existing engine')
    raw=patch(args.input.read_bytes());args.output.write_bytes(raw)
    print(hashlib.sha256(raw).hexdigest())
