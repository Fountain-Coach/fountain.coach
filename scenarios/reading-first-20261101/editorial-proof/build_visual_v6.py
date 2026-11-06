#!/usr/bin/env python3
"""Retain the Teatro architectural synth surface within the canonical Press folio."""
from pathlib import Path
import argparse,hashlib,re,html,json,shutil
HERE=Path(__file__).resolve().parent
SRC=HERE/'a-sound-must-earn-its-place-v6.md'
TEATRO=Path('/Users/benedikteickhoff/Developer/teatro-kino-interlude-20261105/site/interludes/kino/live-csound')
ARCH_SHA='789ef2af5131529e1f1ed43ff70ae7dce3ea715e91107304fe00632cf4a3677d'
PREV_SHA='9f951ffc2d8cb81653058a2b745233c8cd267b115dff06bb5796731a33ee9577'
PAT=r'<template data-reader-volume="essay--a-sound-must-earn-its-place"[^>]*>.*?</template>'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(p):return sha(Path(p).read_bytes())
def inline(s):
 s=html.escape(s,quote=True)
 s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
 return re.sub(r'\*(.+?)\*',r'<em>\1</em>',s)
def build(parent,out):
 original=Path(parent).read_bytes()
 if sha(original)!=PREV_SHA:raise ValueError('Not admitted v169 predecessor')
 original=original.decode()
 match=re.findall(PAT,original,re.S)
 if len(match)!=1:raise ValueError('Unexpected essay identity')
 old=match[0]
 new=old
 manuscript=SRC.read_text()
 anchors=[('history','[KINO-HISTORICAL-COMPARISON:groove-memory]','[KINO-LIVE-SYNTHS:history]'),
          ('controlled','[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]','[KINO-LIVE-SYNTHS:controlled]')]
 for kind,start,end in anchors:
  prose=manuscript.split(start,1)[1].split(end,1)[0].strip()
  if not prose or '\n\n' in prose:raise ValueError('Expected one paragraph per live score')
  pattern=r'<p data-source-block="a-sound-must-earn-its-place.live-'+kind+r'-description">.*?</p>'
  new,count=re.subn(pattern,lambda _: '<p data-source-block="a-sound-must-earn-its-place.live-'+kind+'-description">'+inline(prose)+'</p>',new,count=1,flags=re.S)
  if count!=1:raise ValueError('Missing live score description '+kind)
 new,count=re.subn(r'data-source-sha256="[a-f0-9]{64}"','data-source-sha256="'+digest(SRC)+'"',new,count=1)
 if count!=1:raise ValueError('Missing source SHA')
 new,count=re.subn('height:270px','height:clamp(315px,47vw,390px)',new)
 if count!=2:raise ValueError('Two existing Teatro frames required')
 new,count=re.subn('Actual Teatro Csound AudioWorklet source · Start / Stop · 16-second audition','Kino After Dark · original Teatro architectural score; the sixteen windows follow live Csound output.',new)
 if count!=2:raise ValueError('Expected two source captions')
 new,count=re.subn(r'(<figure class="frame-press-live-instrument")',r'\1 data-original-kino-svg-sha256="'+ARCH_SHA+'"',new)
 if count!=2:raise ValueError('Unexpected live score figure count')
 assert new.count('<satzfunk-player compact')==4 and new.count('<iframe ') ==2 and new.count('data-source-illustration-id=')==2
 updated=original.replace(old,new,1)
 assert updated.replace(new,old,1)==original
 out=Path(out);(out/'estate').mkdir(parents=True,exist_ok=True)
 (out/'estate/index.html').write_text(updated)
 for name in ('index.html','live.mjs'):
  target=out/'teatro/interludes/kino/live-csound'/name
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(TEATRO/name,target)
 if ARCH_SHA not in (out/'teatro/interludes/kino/live-csound/index.html').read_text():raise ValueError('Original Kino score source changed')
 receipt={'schema':'fountain.press.kino-architectural-live-score.v170',
  'sourceOwner':'Fountain-Coach/fountain.coach','teatroOwner':'Fountain-Coach/teatro.fountain.coach',
  'manuscriptSHA256':digest(SRC),'sourceKinoSVGsha256':ARCH_SHA,
  'readerIndexSHA256':sha(updated.encode()),
  'preservedRecordedAuditions':4,'preservedLiveCsoundInstruments':4,
  'existingReaderUnchanged':True,'existingArtworkPreserved':True,
  'privateWLANOnly':True,'publicReleaseAuthorized':False,
  'changed':{k:digest(p) for k,p in {
    'estate/index.html':out/'estate/index.html',
    'teatro/interludes/kino/live-csound/index.html':out/'teatro/interludes/kino/live-csound/index.html',
    'teatro/interludes/kino/live-csound/live.mjs':out/'teatro/interludes/kino/live-csound/live.mjs'}.items()}}
 dest=out/'estate/evidence/press-kino-architecture-v170.json'
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 print(json.dumps({'changed':receipt['changed'],'manuscript':receipt['manuscriptSHA256'],'receiptSHA256':digest(dest)},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--parent',required=True)
 p.add_argument('--out',required=True)
 a=p.parse_args();build(a.parent,a.out)
