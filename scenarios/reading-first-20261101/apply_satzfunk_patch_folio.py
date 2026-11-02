#!/usr/bin/env python3
"""Replace the abstract final-leaf illustration with the source-owned patcher host.

Only the two explicitly admitted Vergil end leaves are transformed.
The audio media, narration, and all other Linotype source remain byte-exact.
"""
from pathlib import Path
import re
import sys
target=Path(sys.argv[1])
text=target.read_text()
old_svg=r'<svg class="voice-score-plate".*?</svg>'
replacement='<div class="voice-patch-surface" data-patch-model="satzfunk.voice.mastering.01" role="group" aria-label="SatzfunkPlayer Csound voice patch. Select module ports to reconnect processing.">The voice processing patch is available when the reader loads.</div>'
old_comment="Vergil's recorded voice passes through rumble, tonal, sibilance and dynamics control. Ear listens before the browser sends the sound onward."
new_comment="These are the actual Csound modules. Select a processor to inspect it, or connect its ports to change the voice path. Safety and Ear remain in circuit."
changes=[
 ('svg',lambda s:re.sub(old_svg,replacement,s,flags=re.S),len(re.findall(old_svg,text,flags=re.S))),
 ('kicker',lambda s:s.replace("Satzfunk · A listening score","Satzfunk · A patch you can hear"),text.count("Satzfunk · A listening score")),
 ('comment',lambda s:s.replace(old_comment,new_comment),text.count(old_comment))
]
if text.count('class="voice-patch-surface"')==2:
 print('PATCH_FOLIOS_ALREADY_CURRENT')
 sys.exit(0)
assert all(c==2 for _,_,c in changes),changes
out=text
for _,fn,_ in changes:out=fn(out)
assert out.count('class="voice-patch-surface"')==2
for vol in ('teatro','solstice-reading-01--vergil'):
 pat=r'<template data-reader-volume="'+re.escape(vol)+r'">(.*?)</template>'
 a=re.search(pat,text,re.S).group(1);b=re.search(pat,out,re.S).group(1)
 assert len(a)>1000 and len(b)>1000
 # Preserve all authoritative source blocks verbatim.
 sources=lambda v:re.findall(r'<(?:p|h2)[^>]*data-source-block="[^"]+"[^>]*>.*?</(?:p|h2)>',v,re.S)
 assert sources(a)==sources(b),vol
target.write_text(out)
print('SOURCE_PRESERVED_PATCH_FOLIOS',target,len(out)-len(text))
