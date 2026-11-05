#!/usr/bin/env python3
"""Project the writer's 2026-11-05 archival decision into the EXISTING Reader.

The authored essay and its old direct static route remain unchanged. Modify
only the collection imprint, gallery membership, and source-distinct status
inside the original preserved book template. Do not create another Reader.
"""
from __future__ import annotations
import argparse,hashlib,html,json,re
from pathlib import Path

WORK="essay--to-read-is-not-to-remember"
SLUG="to-read-is-not-to-remember"
TITLE="Did the Machine Actually Read the Book?"
STATUS_TEXT=("Archived on 5 November 2026. This historical essay remains available "
             "at its original address but is no longer part of the current Essays edition.")
ARCHIVE_PREAMBLE=(
    '<span class="frame-editorial-kicker">From the editor · Archived work</span>'
    '<p class="frame-editorial-archive" data-editorial-role="archive-status" '
    'data-source-block="editorial.archive.to-read-is-not-to-remember" '
    'aria-label="Archival publication status"><strong>Archived on 5 November 2026.</strong> '
    'This historical essay remains available at its original address, '
    'but is no longer part of the current Essays edition.</p>'
)
GALLERY=re.compile(r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)',re.S)
TEMPLATE=re.compile(r'(<template data-reader-volume="'+WORK+r'")>(.*?)</template>',re.S)
def digest(data: bytes) -> str:return hashlib.sha256(data).hexdigest()
def render(source: bytes,source_digest: str|None=None)->tuple[bytes,dict]:
    if source_digest is not None and digest(source)!=source_digest:
        raise ValueError("Original stage/source digest changed, refusing archive projection")
    s=source.decode("utf-8")
    if s.count('Six essays · chronological edition')!=1:
        raise ValueError("Expected original six-essay edition imprint missing")
    match=GALLERY.search(s)
    if not match:raise ValueError("Original coordinated gallery manifest missing")
    gallery=json.loads(match.group(2))
    if gallery.get("schema")!="fountain.press.bookshelf-gallery.v1":
        raise ValueError("Unknown gallery source contract")
    prior=gallery["collections"]["essays"]
    if len(prior)!=6 or [x.get("id") for x in prior].count(WORK)!=1:
        raise ValueError("Wrong original six-essay gallery membership")
    archive_item=next(x for x in prior if x["id"]==WORK)
    gallery["collections"]["essays"]=[x for x in prior if x["id"]!=WORK]
    archive_note=json.dumps(gallery,ensure_ascii=False,separators=(',',':'))
    s=s[:match.start()]+match.group(1)+archive_note+match.group(3)+s[match.end():]
    s=s.replace("Six essays · chronological edition","Five essays · current edition",1)
    match=TEMPLATE.search(s)
    if not match or len(TEMPLATE.findall(s))!=1:
        raise ValueError("Archive source-bearing Reader volume must occur once")
    body=match.group(2)
    if TITLE not in body or 'data-editorial-role="proem"' not in body:
        raise ValueError("Archived essay's original title and proem must exist")
    if 'data-editorial-role="archive-status"' in body:
        raise ValueError("Already archived: input cannot be projected twice")
    kicker='<span class="frame-editorial-kicker">From the editor</span>'
    if body.count(kicker)!=1:
        raise ValueError("Expected one editorial proem kicker on archived work")
    body=body.replace(kicker,ARCHIVE_PREAMBLE,1)
    template=match.group(1)+' data-editorial-state="archived">'+body+'</template>'
    s=s[:match.start()]+template+s[match.end():]
    out=s.encode("utf-8")
    assert len(gallery["collections"]["essays"])==5
    assert s.count('data-reader-volume="'+WORK+'"')==1
    report={
      "schema":"fountain.press.editorial-archive-decision.v1",
      "workID":WORK,"title":TITLE,"status":"archived",
      "archivedAt":"2026-11-05",
      "preservedOriginalRoute":"/estate/essays/"+SLUG+"/",
      "preservedReaderRoute":"#/read/"+WORK,
      "originalSourceHTMLSHA256":digest(source),
      "archivedReaderHTMLSHA256":digest(out),
      "currentEssays":[x["id"] for x in gallery["collections"]["essays"]],
      "removedFromCurrentGallery":archive_item["id"],
      "preservedOriginalFigurePaths":True,
      "preservedWriterProse":True,
      "editorialStatusSourceBlock":"editorial.archive."+SLUG,
      "productionStatus":"unchanged"
    }
    return out,report

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--input",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--report",type=Path)
    a.add_argument("--expect-sha")
    opts=a.parse_args()
    rendered,report=render(opts.input.read_bytes(),opts.expect_sha)
    if opts.input.resolve()==opts.output.resolve():
        raise ValueError("Write to a distinct output to preserve source comparison")
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_bytes(rendered)
    if opts.report:
        opts.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
