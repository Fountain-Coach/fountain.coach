#!/usr/bin/env python3
"""Project the source-owned seven-chapter Linotype reader onto the canonical
WLAN staging shell. This creates direct-static HTML, not a runtime renderer.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import argparse,copy,hashlib,json
p=argparse.ArgumentParser()
p.add_argument("--source",type=Path,required=True)
p.add_argument("--existing-stage-home",type=Path,required=True)
p.add_argument("--output",type=Path,required=True)
a=p.parse_args()
stage=BeautifulSoup(a.existing_stage_home.read_text(),"html.parser")
shell=stage.select_one("header.fc-estate-shell")
foot=stage.select_one("footer.fc-estate-shell")
assert shell and foot
source=BeautifulSoup(a.source.read_text(),"html.parser")
assert source.body and source.head
# Source has the shared direct-static Publication Core. WLAN candidates replace
# only that global chrome with the current v58 authenticated EstateShell, so
# there is never a duplicate masthead or legal footer in the browser.
for old in list(source.select("header.site-header,footer.footer")):
    old.decompose()
for old in list(source.select('meta[name="fountain:publication-role"]')):
    old.decompose()
assert source.body.get("data-edition-entry-anchor")=="work-the-door-is-a-score"
assert len(source.select(".book-chapter[data-book-chapter]"))==7
# Shared EstateShell and footer come from the installed canonical predecessor.
# The source owns the Press reader's article bodies, measured folio and toolbar.
source.body.insert(1,copy.deepcopy(shell))
source.body.append(copy.deepcopy(foot))
for path,tag in [("/assets/estate-shell.css","link"),("/assets/estate-shell-state.js","script")]:
    if tag=="link":
        el=source.new_tag(tag,rel="stylesheet",href=path)
    else:
        el=source.new_tag(tag,src=path)
        el["defer"]=""
    source.head.append(el)
meta=source.new_tag("meta")
meta["name"]="fountain:publication-role"
meta["content"]="author-led living Essays book, writer-approved private WLAN reader-first scenario"
source.head.append(meta)
source.body["data-estate-publication"]="living-essays"
# Route identities are separate. Shared estate destinations retain the
# current release's stage-origin contract, not source-owner derivation.
for tag in source.find_all(True):
    for key in ("href","src","poster"):
        val=tag.get(key)
        if not val or not val.startswith("/"):continue
        # Shared EstateShell assets live at the WLAN origin's /assets,
        # whereas the Fountain Coach site owns its /estate/assets projection.
        if val.startswith("/assets/estate-shell"):
            continue
        if val.startswith(("/assets/","/essays/","/editions/","/collections/","/scenarios/")):
            tag[key]="/estate"+val
        # Other owned published editions (Book, Works, Solstice, Teatro) are
        # already first-class siblings in the current private WLAN release.
# Source text needs to retain its anchored work identities.
anchors=[x.get("id") for x in source.select(".book-chapter")]
assert len(anchors)==len(set(anchors))==7
assert source.select_one('[data-estate-id="works"]')
assert source.select_one('[data-estate-id="satzfunk"]')
assert source.select_one('footer.fc-estate-shell')
for x in source.select("meta[name='robots']"):x["content"]="noindex,nofollow"
# The preview edition is NOT an independently published new source work.
source.head.append(source.new_tag("meta",attrs={"name":"fountain:stage-source","content":"private author-controlled seven-work edition; no production grant"}))
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(str(source)+"\n")
print(json.dumps({"readerFirstStageHTML":str(a.output),
    "bytes":a.output.stat().st_size,
    "sha256":hashlib.sha256(a.output.read_bytes()).hexdigest(),
    "chapters":len(anchors),
    "entry":source.body.get("data-edition-entry-anchor"),
    "shell":"retained v58 shared masthead/reel/footer"}))
