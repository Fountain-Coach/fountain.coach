#!/usr/bin/env python3
"""Withdraw one source-owned archival essay from active galleries, never delete it.

The page retains an accessible, separate archive reference to the exact
existing static essay route. Source edition and WLAN projection are different
inputs, and the original source files remain byte-for-byte unchanged.
"""
from pathlib import Path
import argparse,hashlib,json,re
SOURCE_SLUG="to-read-is-not-to-remember"
TITLE="Did the Machine Actually Read the Book?"
def sha(raw):return hashlib.sha256(raw).hexdigest()
def transform(blob:bytes,expected:str,locale:str):
    if sha(blob)!=expected:raise ValueError("Original gallery revision mismatch")
    s=blob.decode("utf8")
    route=("/estate" if locale=="stage" else "")+"/essays/"+SOURCE_SLUG+"/"
    pattern=re.compile(r'<article\b[^>]*\bclass="essay-gallery-card"[^>]*\bdata-essay-route="'+re.escape(route)+r'"[^>]*>.*?</article>',re.S)
    found=list(pattern.finditer(s))
    if len(found)!=1:raise ValueError("Archival card must be in active gallery exactly once: "+str(len(found)))
    element=found[0].group(0)
    if TITLE not in element:raise ValueError("Wrong archived essay found")
    s=s[:found[0].start()]+s[found[0].end():]
    start=s.find('data-essay-gallery')
    if start<0:raise ValueError("Authored gallery missing")
    end=s.find('</section>',start)
    if end<0:raise ValueError("Gallery section not closed")
    if s.count('aria-label="Archived essays"'):raise ValueError("Already archived")
    note=(' <aside class="essay-boundary" aria-label="Archived essays">'
          '<strong>Archived work.</strong> <a href="'+route+
          '">'+TITLE+'</a> — retained as a historical essay, removed from '
          'the current publishing list on 5 November 2026.</aside>\n')
    s=s[:end+len('</section>')]+note+s[end+len('</section>'):]
    assert s.count('data-essay-route="'+route+'"')==0
    assert s.count('href="'+route+'"')==1
    assert s.count(TITLE)==1
    result=s.encode("utf8")
    return result,{"schema":"fountain.press.archived-gallery-projection.v1",
        "inputSHA256":expected,"outputSHA256":sha(result),
        "title":TITLE,"originalRoute":route,"archivalCardRemoved":True,
        "archiveReferenceRetained":True,"sourceProseChanged":False,
        "page":"legacy Essays gallery","stageOnly":locale=="stage"}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--locale",choices=["source","stage"],required=True)
    ap.add_argument("--expect-sha",required=True)
    ap.add_argument("--report",type=Path)
    arg=ap.parse_args()
    if arg.input.resolve()==arg.output.resolve():raise ValueError("Output must be distinct")
    content,receipt=transform(arg.input.read_bytes(),arg.expect_sha,arg.locale)
    if arg.output.exists():raise ValueError("Refuse overwriting prior projected gallery")
    arg.output.write_bytes(content)
    if arg.report:arg.report.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
