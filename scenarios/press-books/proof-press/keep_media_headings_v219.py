#!/usr/bin/env python3
"""Keep source headings with a following paragraph-and-media atomic group.

Only this narrow branch of the same source-pinned Linotype compositor changes;
no rewritten text, new paginator, media player or CSS fill rule.
"""
from pathlib import Path
import hashlib
PRIOR='7e00076b93d69e374d609aa6e3d1760a1b028cb2b796ea25be13a3241170312c'
OLD='''          const opening=elements[i+1],text=normalized(opening);
          const characters=Math.min(text.length,Math.max(90,
            Math.ceil(sheet.area.clientWidth/(this.css.font*.55)*1.8)));
          if(characters>0){
            const heading=immutable(element),first=fragmentFor(opening,0,characters);
            const fitsTogether=()=>{
              sheet.area.append(heading,first);
              const fit=this.fits(sheet.area);
              first.remove();heading.remove();
              return fit;
            };'''
NEW='''          const opening=elements[i+1],text=normalized(opening);
          const characters=Math.min(text.length,Math.max(90,
            Math.ceil(sheet.area.clientWidth/(this.css.font*.55)*1.8)));
          if(characters>0){
            // Short prose inseparable from source-authored media is an atomic
            // measured group. Keep its preceding heading with the actual
            // paragraph and figure, not merely a fragment of the paragraph.
            const attached=elements[i+2];
            const keepMedia=opening.textContent.length<=360 &&
              attached?.matches('figure[data-press-media][data-keep-with-anchor="previous"]');
            const heading=immutable(element);
            const first=keepMedia?immutable(opening):fragmentFor(opening,0,characters);
            const media=keepMedia?immutable(attached):null;
            const fitsTogether=()=>{
              sheet.area.append(heading,first);
              if(media)sheet.area.append(media);
              const fit=this.fits(sheet.area);
              media?.remove();first.remove();heading.remove();
              return fit;
            };'''

def patch(data:bytes)->bytes:
 if hashlib.sha256(data).hexdigest()!=PRIOR:raise ValueError('REFUSED compositor predecessor SHA drift')
 text=data.decode('utf8')
 if text.count(OLD)!=1:raise ValueError('REFUSED media heading source guard uniqueness drift')
 result=text.replace(OLD,NEW,1).encode('utf8')
 if hashlib.sha256(result).hexdigest()=='':raise ValueError('Unreachable')
 return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise SystemExit('REFUSED existing engine overwrite')
 result=patch(a.input.read_bytes());a.output.write_bytes(result)
 print(hashlib.sha256(result).hexdigest())
