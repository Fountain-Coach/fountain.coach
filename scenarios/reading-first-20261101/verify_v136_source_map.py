#!/usr/bin/env python3
"""Verify exact local source bytes for the independently observed private v136 projection.

This is a read-only provenance check, not production-baseline or publisher
authority. It never reads private media bytes or performs deployment.
"""
from pathlib import Path
import hashlib
import json
import sys

def digest(file):
    h = hashlib.sha256()
    with file.open("rb") as stream:
        while chunk := stream.read(1048576):
            h.update(chunk)
    return h.hexdigest()

root = Path(__file__).resolve().parent
developer = Path.home() / "Developer"
data = json.loads((root / "STAGED_V136_SOURCE_MAP.json").read_text())
assert data["schema"] == "fountain.press.private-stage-source-map.v1"
assert data["stageRelease"] == "shared-shell-20261102-v136-vergil-midi2-range-anchor"
assert data["publicPublication"] is False
assert digest(root / "index.html") == data["indexSHA256"]
count = 0
for section in ("assets", "playerAssets"):
    for route, item in data[section].items():
        source = (developer / item["source"]).resolve()
        if not source.is_file() or not source.is_relative_to(developer.resolve()):
            raise RuntimeError("Missing or foreign source: " + route)
        if digest(source) != item["sha256"]:
            raise RuntimeError("Source digest differs: " + route)
        count += 1
print("SOURCE_MAP_VERIFIED", count, "ASSETS + 1 INDEX; STAGING NOT MODIFIED")
if len(sys.argv) > 1:
    stage = Path(sys.argv[1])
    if digest(stage / "index.html") != data["indexSHA256"]:
        raise RuntimeError("Stage index is different")
    for section in ("assets", "playerAssets"):
        for route, item in data[section].items():
            source = stage / route
            if not source.is_file() or digest(source) != item["sha256"]:
                raise RuntimeError("Stage asset mismatch: " + route)
    print("SELECTED_STAGE_BYTE_COMPARISON_PASSED", count + 1)
