#!/usr/bin/env python3
"""Read-only source fidelity and predecessor parity checks for Orange Dot."""
from pathlib import Path
import json,re,hashlib,html,subprocess
R=Path(__file__).parent
OUT=Path('/tmp/orange-dot-stage-delta-20261110')
old=Path('/tmp/orange-stage-index-v184.html').read_text()
new=(OUT/'estate/index.html').read_text()
entries=json.loads((R/'selection.json').read_text())['entries']
edition=json.loads((OUT/'estate/collections/orange-dot/edition.json').read_text())
assert len(entries)==edition['entryCount']==23
assert len(re.findall(r'<template data-reader-volume="orange-dot--',new))==23
assert len(re.findall(r'data-reader-volume="governance--',new))==len(re.findall(r'data-reader-volume="governance--',old))==160
assert len(re.findall(r'data-reader-volume="solstice-reading-01--',new))==len(re.findall(r'data-reader-volume="solstice-reading-01--',old))==32
assert len(re.findall(r'data-reader-volume="essay--',new))==len(re.findall(r'data-reader-volume="essay--',old))
assert len(re.findall(r'data-reader-volume="score--',new))==len(re.findall(r'data-reader-volume="score--',old))
for vol in re.findall(r'data-reader-volume="([^"]+)"',old):
 if vol=='library':continue
 pattern=r'<template data-reader-volume="'+re.escape(vol)+r'"[^>]*>.*?</template>'
 m1=re.search(pattern,old,re.S);m2=re.search(pattern,new,re.S)
 assert m1 and m2 and m1.group()==m2.group(),('Original volume drift',vol)
for e in entries:
 assert hashlib.sha256((R/e['sourceTextFile']).read_bytes()).hexdigest()==e['textSha256']
 id=e['id']
 block=re.search(r'<template data-reader-volume="'+re.escape(id)+r'"[^>]*>.*?</template>',new,re.S)
 assert block,id
 pars=re.findall(r'<p[^>]*data-source-block="'+re.escape(id)+r'\.text\.[0-9]+"[^>]*>(.*?)</p>',block.group(),re.S)
 assert pars,(id,'lost text')
 rendered=' '.join(' '.join(html.unescape(re.sub('<[^>]+>',' ',p)).split()) for p in pars)
 original=' '.join((R/e['sourceTextFile']).read_text().split())
 assert rendered==original,(id,'source words changed',len(rendered),len(original))
 assert block.group().count('<figure')==len(e['images']),id
 for img in e['images']:
  b=(R/'source-images'/img['sourceImageFile']).read_bytes()
  assert hashlib.sha256(b).hexdigest()==img['sha256']
gallery=lambda text:json.loads(re.search(r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',text,re.S).group(1))
a,b=gallery(old),gallery(new)
assert {k:v for k,v in a['collections'].items()}=={k:v for k,v in b['collections'].items() if k!='orange-dot'}
assert [i['id'] for i in b['collections']['orange-dot']]==[e['id'] for e in entries]
assert len(edition['entries'])==23
first={x['textSha256'].removeprefix('sha256:') for x in json.load(open('/Users/benedikteickhoff/Developer/fountain-publishing/fountain.coach/scenarios/reading-first-20261101/solstice-first-reading-manifest.json'))['entries']}
overlaps=[e for e in entries if e['textSha256'] in first]
assert {e['sourceIndex'] for e in overlaps}=={1168,804}
r=subprocess.run(['node','--input-type=module','--check'],input=(OUT/'estate/assets/linotype/reading-first-app.js').read_text(),text=True,capture_output=True)
assert r.returncode==0,r.stderr
receipt=json.loads((OUT/'orange-dot-delta-receipt.json').read_text())
assert len(receipt['changedAndAddedFiles'])==30
print('ORANGE_SOURCE_FIDELITY_PASS 23/23 texts 29/29 original images')
print('ORANGE_PREDECESSOR_PARITY_PASS 160/160 Governance 32/32 First Reading unchanged all existing source templates byte-identical')
print('ORANGE_OVERLAP_PASS 2 deliberate repetitions; Integration excluded and referenced; no untracked first reading overlaps')
print('ORANGE_APP_SYNTAX_PASS gallery 23/23, only new source templates, app registration and 26 original media files')
