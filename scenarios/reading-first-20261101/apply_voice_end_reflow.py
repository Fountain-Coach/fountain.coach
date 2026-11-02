#!/usr/bin/env python3
"""Preserve a source-identified mastering end leaf across responsive re-pagination."""
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text()
old='''function remember(page){
 if(!engine)return;
 const anchor=engine.anchorAt(page);'''
new='''function remember(page){
 if(!engine)return;
 // A technical end leaf has no narrated prose anchor. Keep its stable
 // source identity when the header changes width and Linotype reflows.
 const visible=engine.leaves.slice(page,page+(engine.css.spread?2:1));
 if(visible.some(leaf=>leaf.type==='end'&&
   leaf.area.querySelector('.voice-mastering-leaf[data-voice-mastering-profile="satzfunk.voice.mastering.01"]'))){
  positions.set(volume,{endLeaf:'satzfunk.voice.mastering.01'});
  pendingPosition=null;
  clearTimeout(positionTimer);positionTimer=0;
  return;
 }
 const anchor=engine.anchorAt(page);'''
assert s.count(old)==1,('remember',s.count(old))
s=s.replace(old,new)
old='''  if(openAtEnd===volume){target=e.pages-1;openAtEnd=null;}
  else if(anchor){try{target=e.pageForAnchor(anchor)}catch{positions.delete(volume);}}'''
new='''  if(openAtEnd===volume){target=e.pages-1;openAtEnd=null;}
  else if(anchor?.endLeaf==='satzfunk.voice.mastering.01'){target=e.pages-1;}
  else if(anchor){try{target=e.pageForAnchor(anchor)}catch{positions.delete(volume);}}'''
assert s.count(old)==1,('reflow',s.count(old))
s=s.replace(old,new)
p.write_text(s)
print('MASTERING_END_REFLOW_GUARD',p)
