#!/usr/bin/env python3
"""One-line, source-pinned fix for Orange Dot secondary-image pagination.

The adopted Linotype compositor remains the sole Reader for every collection.
The original opener artwork and all manuscript/figure source blocks are
unchanged; only portrait secondary-plate fitting is enabled for Orange Dot.
"""
import argparse
import hashlib
from pathlib import Path

BASELINE_SHA="e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a"
BEFORE='if(this.pageFrame&&this.css.spread&&leaf.area.childElementCount){'
AFTER='if(this.pageFrame&&(this.css.spread||sourceId.startsWith("work-orange-dot--"))&&leaf.area.childElementCount){'

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True,help="Exact active stage compositor bytes")
    p.add_argument("--output",type=Path,required=True,help="Candidate immutable corrected compositor")
    args=p.parse_args()
    b=args.baseline.read_bytes()
    if sha(b)!=BASELINE_SHA:
        raise SystemExit("Refusing non-pinned reader baseline")
    source=b.decode("utf-8")
    if source.count(BEFORE)!=1 or AFTER in source:
        raise SystemExit("Reader geometry rule no longer matches accepted source")
    output=source.replace(BEFORE,AFTER,1)
    assert len(output)>50000 and output.count(AFTER)==1
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(output,encoding="utf-8")
    print("ORANGE_DOT_PORTRAIT_FIGURE_PATCH",args.output)
    print("SOURCE_SHA256",sha(b))
    print("OUTPUT_SHA256",sha(args.output.read_bytes()))
    print("ADMITTED_CHANGE",BEFORE,"=>",AFTER)
if __name__=="__main__":
    main()
