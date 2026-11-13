#!/usr/bin/env python3
"""Source-pinned Fountain Press estate-wide editorial projection.

Compose ten selected private-WLAN estate entry routes off the staging host,
using the reusable Fountain Press instrument. Unrelated routes and all author
content stay unchanged. The result is a digest-indexed, inert overlay, NOT a
publisher or a production release.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

EXPECTED_PRESS_REV = "1c8e1b7ab872905218dc2cd2ae469f80ff17a00c"
EXPECTED_STAGE = "shared-shell-20261113-v199-editorial-preface-bf60bff"
EXPECTED_PREDECESSOR_LOCK = "34e6b039d360505391b92de458f9f30de9a135f58ec8190342f98425c911f863"
RELATIVE_ROUTES = (
    "estate/index.html",
    "estate/books/orange-dot/index.html",
    "estate/books/essays/index.html",
    "estate/books/first-readings/index.html",
    "estate/read/essay--client-centered/index.html",
    "estate/read/essay--the-value-of-what-we-can-prove/index.html",
    "estate/read/essay--the-model-is-not-the-instrument/index.html",
    "estate/read/essays/index.html",
    "estate/bookshelf/index.html",
    "estate/collections/first-readings/index.html",
)
EXPECTED_LEGACY_IDS = (
    "essay--the-composable-book",
    "essay--semantic-compilation-the-archive-is-not-the-edition",
)
OLD_BOOKSHELF_EXTRA_IDS = (
    "essay--the-door-is-a-score",
    "essay--the-ear-that-learns",
    "essay--to-read-is-not-to-remember",
    "essay--teatro-an-unfinished-composition",
    "essay--reframe-and-the-business-value-of-the-estate",
)
OLDER_ENTRY_ROUTES = {
    "estate/bookshelf/index.html",
    "estate/collections/first-readings/index.html",
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_git_revision(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()

def require(condition: bool, text: str):
    if not condition:
        raise RuntimeError(text)

def load_instrument(root: Path):
    require(read_git_revision(root) == EXPECTED_PRESS_REV,
            "Fountain Press instrument checkout is not the approved source revision")
    path = root / "Scripts" / "editorial_proem.py"
    require(path.is_file(), "Missing publisher-owned instrument")
    spec = importlib.util.spec_from_file_location("press_editorial_v1", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod, sha(path.read_bytes())

def prose_blocks(raw: str):
    # Every original paragraph and figure remains unchanged byte-for-byte.
    return re.findall(r'<article class="book-prose">(.*?)</article>',raw,re.DOTALL)

def image_addresses(raw: str):
    return re.findall(r'<(?:figure|img)\b[^>]*(?:data-source-block|src)="[^"]+"[^>]*>',raw)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--press",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    impl,impl_hash=load_instrument(a.press)
    require(sha((a.baseline/"source-lock.json").read_bytes())==EXPECTED_PREDECESSOR_LOCK,
            "Active source-lock predecessor is not the retained v199 source")
    output=a.output
    output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for route in RELATIVE_ROUTES:
        src=a.baseline/route
        require(src.is_file(), "Missing accepted baseline: "+route)
        before=src.read_text("utf-8")
        transformed,changes=impl.normalize_html(before)
        expected_ids=set(EXPECTED_LEGACY_IDS)
        if route in OLDER_ENTRY_ROUTES:
            expected_ids.update(OLD_BOOKSHELF_EXTRA_IDS)
        require(len(changes)==len(expected_ids), "Unexpected count of authored legacy abstracts on "+route)
        require({c.volume for c in changes}==expected_ids,
                "Unexpected editorial identity on "+route)
        require(prose_blocks(before)==prose_blocks(transformed), "Authorial prose changed on "+route)
        require(image_addresses(before)==image_addresses(transformed), "Image/score source changed on "+route)
        require("frame-essay-abstract" not in transformed,"Editorial abstract remains on "+route)
        require(impl.audit_html(before)["volumes"]==impl.audit_html(transformed)["volumes"],
                "Edition volume identity changed on "+route)
        again,more=impl.normalize_html(transformed)
        require(again==transformed and not more, "Projection not idempotent on "+route)
        require(before!=transformed,"Projection unexpectedly had no effect on "+route)
        target=output/route
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(transformed,encoding="utf-8")
        before_inventory=impl.audit_html(before)
        after_inventory=impl.audit_html(transformed)
        require(before_inventory["legacy_editorial_abstracts"]==len(expected_ids)
                and after_inventory["legacy_editorial_abstracts"]==0
                and after_inventory["editorial_proems"]==before_inventory["editorial_proems"]+len(expected_ids),
                "Editorial inventory cannot be reconciled on "+route)
        rows.append(dict(path=route,beforeSha256=sha(before.encode()),afterSha256=sha(transformed.encode()),
                         changes=[c.__dict__ for c in changes],beforeInventory=before_inventory,
                         afterInventory=after_inventory))
    require(len(rows)==10,"Route inventory changed")
    manifest={
        "schema":"fountain.press.editorial-estate-stage.v1",
        "stageOnly":True,
        "publicPromotionAuthorized":False,
        "predecessorRelease":EXPECTED_STAGE,
        "predecessorSourceLockSha256":EXPECTED_PREDECESSOR_LOCK,
        "compositionOwner":"Fountain-Coach/fountain.coach",
        "compositionOwnerRevision":read_git_revision(Path(__file__).resolve().parents[1]),
        "pressInstrumentOwner":"Fountain-Coach/fountain-press",
        "pressInstrumentRevision":EXPECTED_PRESS_REV,
        "pressInstrumentSourceSha256":impl_hash,
        "compositor":"existing Fountain Press measured Linotype engine unchanged",
        "editorialPolicy":"only source-declared editorial abstracts become separate editorial proems",
        "sourcePreservation":"authorial paragraphs and all figure/image identities unchanged",
        "routeCount":len(rows),
        "changedEditorialVolumeIds":list(EXPECTED_LEGACY_IDS)+list(OLD_BOOKSHELF_EXTRA_IDS),
        "routes":rows
    }
    evidence=output/"estate/evidence/editorial-proem-estate-v200.json"
    evidence.parent.mkdir(parents=True,exist_ok=True)
    evidence.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "result":"inert-estate-projection-built",
        "manifestSha256":sha(evidence.read_bytes()),
        "routes":len(rows),
        "changedBlockOccurrences":sum(len(x["changes"]) for x in rows),
        "editedManuscripts":0,
        "sourcePolicy":"no generated editor prose",
        "pressInstrumentRevision":EXPECTED_PRESS_REV,
        "exampleVolumeCount":rows[0]["afterInventory"],
    },indent=2))

if __name__=="__main__":
    main()
