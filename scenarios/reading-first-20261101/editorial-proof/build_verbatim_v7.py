#!/usr/bin/env python3
"""Restore both original rejected Kino synthesizers as citations in real Fountain Press.

The existing reader only paginates authentic source plates and text. On activation
the complete vintage source app runs in a bounded in-Press performance sheet.
No iframe enters the measured Linotype template; no new Reader is created.
"""
from pathlib import Path
import argparse, hashlib, json, html, re, shutil
ROOT=Path(__file__).resolve().parent
MANUSCRIPT=ROOT/'a-sound-must-earn-its-place-v7.md'
TEATRO=Path('/Users/benedikteickhoff/Developer/teatro-kino-interlude-20261105/site/interludes/kino/press-citation')
BRIDGE=Path('/Users/benedikteickhoff/Developer/.estate-press-sound-proof-20261106/staging/press-kino-verbatim-bridge.js')
PARENT='75fb9c8c160d6526447b3818225d44ab33acd0caa0fd8e676352ca539ce939d4'
VOLUME=r'<template data-reader-volume="essay--a-sound-must-earn-its-place"[^>]*>.*?</template>'
EXPECTED={
 'v156':{'html':'12b4613db0472293887c7a9a6f1c7e066151ef406c1632a03c3a5b37dcd360f6',
         'plate':'f2e0dc22c01a626b184983a7d8abf94d44dddfa3c0143b834706d7ca3e258d00'},
 'v158':{'html':'293cbec0524809e432d1494c91f2c88b1457c4f44680068417408e557041a3bf',
         'plate':'6e4ee6d8571062f9fca405b718eb1e5c561716a8f08a3d16b9cea3f89d3b9484'}
}
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inline(text):
 value=html.escape(text,quote=True)
 value=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',value)
 return re.sub(r'\*(.+?)\*',r'<em>\1</em>',value)
def original_citation(kind,title,caption):
 source='/teatro/interludes/kino/press-citation/plates/'+kind+'.png'
 return (
 '<figure class="frame-press-original-kino-source" data-press-original-kino="'+kind+'" '
 'data-source-block="a-sound-must-earn-its-place.original-'+kind+'" '
 'data-keep-with-anchor="previous" style="width:100%;max-width:100%;box-sizing:border-box;margin:.45em 0;padding:.15em 0;">'
 '<img src="'+source+'" width="1720" height="1040" alt="'+html.escape(title,quote=True)+
 '; original Teatro Kino façade and live instrument controls" '
 'style="display:block;max-width:100%;width:100%;height:auto;object-fit:contain;border:1px solid #596b5a" />'
 '<figcaption>'+html.escape(caption)+'</figcaption>'
 '<button type="button" data-press-verbatim="'+kind+'" '
 'aria-label="Perform complete original '+html.escape(title,quote=True)+' within Fountain Press" '
 'style="display:block;width:100%;min-height:44px;margin:.25em 0 0;'
 'border:1px solid #607769;border-radius:3px;background:transparent;color:inherit;'
 'font:inherit;font-size:.88em;text-align:center;cursor:pointer;">'
 'Perform original source · Play / Stop / Controls</button></figure>')
def build(parent,out):
 parent=Path(parent)
 if digest(parent)!=PARENT:raise ValueError('Wrong current original Press folio')
 source=MANUSCRIPT.read_text()
 for name in ('[KINO-VERBATIM-CITATIONS:groove-and-room]','[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]'):
  if source.count(name)!=1:raise ValueError('Expected source anchor: '+name)
 original=parent.read_text()
 old=re.findall(VOLUME,original,re.S)
 if len(old)!=1:raise ValueError('Wrong Reader book identity')
 new=old[0]
 history=source.split('[KINO-HISTORICAL-COMPARISON:groove-memory]',1)[1].split('[KINO-VERBATIM-CITATIONS:groove-and-room]',1)[0].strip()
 later=source.split('[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]',1)[1].strip().split('\n\n',1)[0]
 if '\n\n' in history or not later:raise ValueError('Invalid authored paragraphs')
 for which,paragraph in (('history',history),('controlled',later)):
  pat=r'<p data-source-block="a-sound-must-earn-its-place.live-'+which+r'-description">.*?</p>'
  new,count=re.subn(pat,lambda m:'<p data-source-block="a-sound-must-earn-its-place.live-'+which+'-description">'+inline(paragraph)+'</p>',new,count=1,flags=re.S)
  if count!=1:raise ValueError('Missing existing authored paragraph '+which)
 fig_pat=r'<figure class="frame-press-live-instrument"[^>]*>.*?</figure>'
 figures=re.findall(fig_pat,new,re.S)
 if len(figures)!=2 or 'data-press-live-csound="history"' not in figures[0] or 'data-press-live-csound="controlled"' not in figures[1]:
  raise ValueError('Unexpected generic iframe source to replace')
 first=original_citation('v156','Kino After Dark — original groove synthesizer','Groove instrument, Teatro source f3f7d39 (AAC-compatible 35fd6a4).')
 second=original_citation('v158','Kino After Dark — original cinematic room','Cinematic room, Teatro source e2f5dd2.')
 new=new.replace(figures[0],first+second,1).replace(figures[1],'',1)
 new,count=re.subn(r'data-source-sha256="[a-f0-9]{64}"','data-source-sha256="'+digest(MANUSCRIPT)+'"',new,count=1)
 if count!=1:raise ValueError('No edition source SHA')
 if (new.count('<iframe')!=0 or new.count('data-press-verbatim=')!=2 or
     new.count('<satzfunk-player compact')!=4 or new.count('data-source-illustration-id=')!=2):
  raise ValueError('Lost existing audio/images or retained iframe in reader')
 revised=original.replace(old[0],new,1)
 assert revised.replace(new,old[0],1)==original
 script='<script type="module" src="/estate/assets/instruments/kino-verbatim-bridge.js"></script>'
 if revised.count('</body>')!=1:raise ValueError('Unexpected root HTML')
 revised=revised.replace('</body>',script+'</body>',1)
 if revised.count(script)!=1:raise ValueError('Bridge injected more than once')
 out=Path(out)
 index=out/'estate/index.html';index.parent.mkdir(parents=True,exist_ok=True);index.write_text(revised)
 runtime=out/'estate/assets/instruments/kino-verbatim-bridge.js'
 runtime.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BRIDGE,runtime)
 source_root=out/'teatro/interludes/kino/press-citation'
 shutil.copytree(TEATRO,source_root,dirs_exist_ok=True)
 manifest=json.loads((source_root/'manifest.json').read_text())
 if manifest.get('publicReleaseAuthorized') is not False:raise ValueError('Public rights not granted')
 for kind in ('v156','v158'):
  if digest(source_root/kind/'index.html')!=EXPECTED[kind]['html'] or digest(source_root/'plates'/f'{kind}.png')!=EXPECTED[kind]['plate']:
   raise ValueError('Verbatim source and author-made plates changed '+kind)
 added={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=index}
 receipt={
  'schema':'fountain.press.kino-original-source-citations.v171',
  'sourceOwner':'Fountain-Coach/fountain.coach','teatroOwner':'Fountain-Coach/teatro.fountain.coach',
  'manuscriptSHA256':digest(MANUSCRIPT),'parentIndexSHA256':PARENT,
  'indexSHA256':digest(index),'liveOriginalSourceIDs':['v156','v158'],
  'originalRuntimeUnmodified':True,'reconstructionsRetiredAsLiveClaims':True,
  'recordedComparisonTracksPreserved':['kino-history-groove','kino-history-memory','a-literal','b-directed'],
  'existingFiguresPreserved':['architectural-plate','night-photograph'],
  'existingLinotypeJSUnchanged':True,'iframesInLinotype':0,
  'originalSources':manifest['editions'],'privateWLANOnly':True,'publicReleaseAuthorized':False,
  'changed':{'estate/index.html':digest(index)},'added':added}
 path=out/'estate/evidence/press-kino-verbatim-v171.json'
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(receipt,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'sourceSHA256':receipt['manuscriptSHA256'],'indexSHA256':receipt['indexSHA256'],
   'bridgeSHA256':digest(runtime),'addedFiles':len(added),'receiptSHA256':digest(path),'existingPlayers':4,
   'readerIframes':0,'originalSourceIDs':['v156','v158']},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--parent',required=True);ap.add_argument('--out',required=True)
 a=ap.parse_args();build(a.parent,a.out)
