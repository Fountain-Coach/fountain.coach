#!/usr/bin/env python3
"""Retain a versioned Linotype end leaf through audio-control resize/reflow."""
from pathlib import Path
import sys
for raw in sys.argv[1:]:
    path=Path(raw)
    s=path.read_text()
    helper="""function semanticAnchor(page){
 if(viewport.querySelector('.voice-mastering-leaf') &&
    source.querySelector('.book-end.voice-mastering-leaf'))
  return {block:'voice-mastering.'+volume,offset:0};
 return engine?.anchorAt(page)||null;
}
"""
    old="""function remember(page){
 if(!engine)return;
 const anchor=engine.anchorAt(page);
"""
    new=helper+"""function remember(page){
 if(!engine)return;
 const anchor=semanticAnchor(page);
"""
    assert s.count(old)==1,(raw,"remember",s.count(old))
    s=s.replace(old,new,1)
    old="""  else if(anchor){try{target=candidate.pageForAnchor(anchor)}catch{target=0;}}"""
    new="""  else if(anchor?.block==='voice-mastering.'+volume &&
          source.querySelector('.book-end.voice-mastering-leaf'))target=candidate.pages-1;
  else if(anchor){try{target=candidate.pageForAnchor(anchor)}catch{target=0;}}"""
    if old in s:
        assert s.count(old)==1
        s=s.replace(old,new,1)
    else:
        old="""  else if(anchor){try{target=e.pageForAnchor(anchor)}catch{positions.delete(volume);}}"""
        new="""  else if(anchor?.block==='voice-mastering.'+volume &&
          source.querySelector('.book-end.voice-mastering-leaf'))target=e.pages-1;
  else if(anchor){try{target=e.pageForAnchor(anchor)}catch{positions.delete(volume);}}"""
        assert s.count(old)==1,(raw,"compose",s.count(old))
        s=s.replace(old,new,1)
    old="""  const address=engine.anchorAt(engine.current);"""
    if old in s:
        assert s.count(old)==1
        s=s.replace(old,"  const address=semanticAnchor(engine.current);",1)
    path.write_text(s)
    print("END_ANCHOR_PATCHED",path,len(s))
