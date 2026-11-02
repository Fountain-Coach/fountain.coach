#!/usr/bin/env python3
"""Retain the visible mastering leaf while Linotype measures a replacement frame."""
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text()
if 'candidate.compose();' in s and 'preparation.remove()' in s:
 old='''  candidate.compose();
  let target=0;'''
 new='''  const preserveMasteringEnd=viewport.dataset.volume===volume&&
    !!viewport.querySelector('.voice-mastering-leaf');
  candidate.compose();
  let target=0;'''
 old2="else if(anchor?.endLeaf==='satzfunk.voice.mastering.01'){target=candidate.pages-1;}"
 new2="else if(preserveMasteringEnd||anchor?.endLeaf==='satzfunk.voice.mastering.01'){target=candidate.pages-1;}"
else:
 old='''  const focused=viewport.contains(document.activeElement);
  engine?.dispose();engine=null;viewport.replaceChildren();'''
 new='''  const focused=viewport.contains(document.activeElement);
  const preserveMasteringEnd=viewport.dataset.volume===volume&&
    !!viewport.querySelector('.voice-mastering-leaf');
  engine?.dispose();engine=null;viewport.replaceChildren();'''
 old2="else if(anchor?.endLeaf==='satzfunk.voice.mastering.01'){target=e.pages-1;}"
 new2="else if(preserveMasteringEnd||anchor?.endLeaf==='satzfunk.voice.mastering.01'){target=e.pages-1;}"
for a,b in [(old,new),(old2,new2)]:
 assert s.count(a)==1,(p.name,a[:46],s.count(a))
 s=s.replace(a,b)
p.write_text(s);print("PRESERVED_VISIBLE_END",p)
