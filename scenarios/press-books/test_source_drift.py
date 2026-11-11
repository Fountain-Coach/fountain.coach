#!/usr/bin/env python3
"""Two source-drift regression checks for the Fountain Press direct-book compiler.

No production mutation. Copy-on-write fake input on a disposable filesystem.
The unchanged production-derived source is the independently admitted positive.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SCRIPT=Path(__file__).with_name("compose_direct_books.py")

def fail_if_not_refused(result,word):
    if result.returncode==0 or word not in (result.stdout+result.stderr):
        raise AssertionError("Publisher did not reject corruption: "+repr(word)+" stderr "+result.stderr[:500])
    print("EXPECTED_REFUSAL",word)
def run(source,output):
    return subprocess.run([sys.executable,str(SCRIPT),"--source",str(source),"--output",str(output)],
                          text=True,capture_output=True,check=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--scratch",type=Path,required=True)
    args=p.parse_args()
    assert (args.source/"estate/index.html").is_file()
    args.scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fountain-book-drift-",dir=args.scratch) as root:
        tmp=Path(root)
        source=tmp/"source"
        shutil.copytree(args.source,source,copy_function=os.link)
        # Source contents drift: original SHA pin must refuse before generating.
        index=source/"estate/index.html"
        before=index.read_bytes()
        next_=index.with_name("index.html.changed")
        next_.write_bytes(before+b"\n<!-- unauthorized book contents drift -->\n")
        os.replace(next_,index)
        r=run(source,tmp/"invalid-root")
        fail_if_not_refused(r,"Source drift")
    with tempfile.TemporaryDirectory(prefix="fountain-book-image-",dir=args.scratch) as root:
        tmp=Path(root)
        source=tmp/"source"
        shutil.copytree(args.source,source,copy_function=os.link)
        image=source/"estate/read/essay--client-centered/assets/images/client-centered-positions.svg"
        assert image.is_file()
        tmp_img=image.with_name("client-centered-positions.svg.modified")
        tmp_img.write_bytes(image.read_bytes()+b"\n<!-- tampered figure -->")
        os.replace(tmp_img,image)
        r=run(source,tmp/"invalid-first-image")
        fail_if_not_refused(r,"First chapter source-image SHA conflict essays")
    print("DIRECT_BOOK_DRIFT_TESTS_PASSED 2 refusals; no original files changed")

if __name__=="__main__":main()
