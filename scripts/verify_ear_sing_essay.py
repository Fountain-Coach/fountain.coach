#!/usr/bin/env python3
"""Verify the original essay plate and source-bound, private audio references."""
from pathlib import Path
import hashlib, json, re, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
BASE=SITE/"essays/the-ear-that-learns"
HTML=(BASE/"index.html").read_text()
GALLERY=(SITE/"essays/index.html").read_text()
CSS=(SITE/"assets/site.css").read_text()
ART=BASE/"assets/listening-room.svg"
PNG=BASE/"assets/listening-room.png"
MODULE=BASE/"assets/essay-listening.mjs"
assert ET.parse(ART).getroot().attrib["viewBox"]=="0 0 1536 1024"
assert PNG.stat().st_size>30000
assert PNG.read_bytes()[:4].hex()=="89504e47"
assert "ear-sing-plate" not in CSS
assert ".essay-hero-illustration" in CSS and ".essay-timed-cues" in CSS
assert 'src="assets/listening-room.png"' in HTML
assert 'src="assets/essay-listening.mjs"' in HTML
assert GALLERY.count('data-essay-route="/essays/the-ear-that-learns/"')==1
assert 'src="/essays/the-ear-that-learns/assets/listening-room.png"' in GALLERY
assert "bindEssayListening" in MODULE.read_text()
assert "data-copy-citation" in HTML and "data-reader-note" in HTML
assert HTML.count('href="?take=')>=4
assert HTML.count('data-legal-role="company-status"')==1
m=re.search(r'<script type="application/json" id="ear-sing-audio-manifest">(.*?)</script>',HTML,re.S)
assert m
v=json.loads(m.group(1))
assert v["schema"]=="satzfunk.essay-listening.v1"
assert v["release"]=="wlan-research-only"
assert v["referenceHumanVoice"] is False
assert v["qualifiedSinging"] is False
assert v["earRecognizedLyrics"] is False
expected={
"plain":"f4826365089889eafef579f5e0b3cf6f77d7bf570fcc0fa6e1d5f85ef191cf24",
"articulated":"1d285c6b0a9dd2f7b7be58aac1509b5f55bcac5e3636c530cbec25f20db8f505",
"expressive":"b7390503bdcb4669235fc417e0d21f8008c578f59228ab7ee0817e3df3ff8d27"
}
assert [t["id"] for t in v["takes"]]==list(expected)
for t in v["takes"]:
 assert t["sha256"]==expected[t["id"]]
 assert t["sourceId"]==v["sourceId"]
 assert t["media"]=="media/sing-"+t["id"]+"-compare.m4a"
 assert t["durationSeconds"]==5.2 and t["sampleRate"]==48000
 assert [c["atSeconds"] for c in t["comments"]]==[0,1.15,2.15,3.35]
 assert not (BASE/t["media"]).exists(),"private audio must remain outside public Git"
print("EAR_SING_SOURCE_ACCEPTED",len(v["takes"]),"original audio references",
 "plate",hashlib.sha256(PNG.read_bytes()).hexdigest())
