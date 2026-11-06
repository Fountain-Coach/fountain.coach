#!/usr/bin/env python3
"""Add source-owned live Teatro Csound instruments to the existing v168 Linotype essay."""
from pathlib import Path
import argparse, hashlib, html, json, re, shutil
HERE=Path(__file__).resolve().parent
ROOT=Path('/Users/benedikteickhoff/Developer/teatro-kino-interlude-20261105/site/interludes/kino/live-csound')
SOURCE=HERE/'a-sound-must-earn-its-place-v5.md'
PARENT_SHA='98fd4f38587db9202bc0ad84cc9ebc2888fefdfbc30b14169b7dd79eac9e3c86'
PAT=r'<template data-reader-volume="essay--a-sound-must-earn-its-place"[^>]*>.*?</template>'
def sha(b):return hashlib.sha256(b).hexdigest()
def filehash(p):return sha(Path(p).read_bytes())
def inline(s):
 s=html.escape(s,quote=True)
 s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
 return re.sub(r'\*(.+?)\*',r'<em>\1</em>',s)
def live_frame(pair):
 assert pair in ('history','controlled')
 return ('<figure class="frame-press-live-instrument" data-source-block="a-sound-must-earn-its-place.live-'+pair+'" data-press-live-csound="'+pair+'" data-keep-with-anchor="previous" style="max-width:100%;box-sizing:border-box;padding:.4em 0;">'
 +'<iframe loading="lazy" title="Kino International: two live '+pair+' Csound synthesizers" src="/teatro/interludes/kino/live-csound/?pair='+pair+'" allow="autoplay" sandbox="allow-scripts allow-same-origin" style="display:block;width:100%;height:270px;border:1px solid #aaa89b;box-sizing:border-box"></iframe>'
 +'<figcaption>Actual Teatro Csound AudioWorklet source · Start / Stop · 16-second audition</figcaption></figure>')
def build(parent,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 raw=Path(parent).read_bytes()
 if sha(raw)!=PARENT_SHA:raise ValueError('Unexpected Linotype v168 parent release')
 original=raw.decode()
 old=re.findall(PAT,original,re.S)
 if len(old)!=1:raise ValueError('Existing Reader identity missing')
 template=old[0]
 manuscript=SOURCE.read_text()
 for pair,first,second,existing in [
  ('history','[KINO-HISTORICAL-COMPARISON:groove-memory]','[KINO-LIVE-SYNTHS:history]','kino-history-reconstruction'),
  ('controlled','[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]','[KINO-LIVE-SYNTHS:controlled]','satzfunk-csound-kino-a-b')
 ]:
  if manuscript.count(first)!=1 or manuscript.count(second)!=1:raise ValueError('Invalid manuscript anchor')
  prose=manuscript.split(first,1)[1].split(second,1)[0].strip()
  if not prose or '\n\n' in prose:raise ValueError('Expected one authored description')
  paragraph='<p data-source-block="a-sound-must-earn-its-place.live-'+pair+'-description">'+inline(prose)+'</p>'
  matches=re.findall(r'<figure[^>]*data-press-media="'+existing+r'"[^>]*>.*?</figure>',template,re.S)
  if len(matches)!=1:raise ValueError('Missing authentic recordings '+pair)
  template=template.replace(matches[0],matches[0]+paragraph+live_frame(pair),1)
 source_sha=filehash(SOURCE)
 template=re.sub(r'data-source-sha256="[a-f0-9]{64}"','data-source-sha256="'+source_sha+'"',template,count=1)
 template=template.replace('Four source-bound Csound auditions · Unpublished','Four recordings · Four live Csound instruments · Unpublished',1)
 if template.count('<satzfunk-player compact')!=4 or template.count('<iframe ')!=2 or template.count('data-source-illustration-id=')!=2:raise ValueError('Lost an image, player or live instrument')
 updated=original.replace(old[0],template,1)
 if updated.replace(template,old[0],1)!=original:raise ValueError('Reader body outside essay changed')
 target=out/'estate/index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(updated)
 dest=out/'teatro/interludes/kino/live-csound';dest.mkdir(parents=True,exist_ok=True)
 allowed=('index.html','live.mjs','literal.json','directed.json','history-groove.json','history-memory.json')
 for name in allowed:shutil.copy2(ROOT/name,dest/name)
 # Reuse Teatro's actual Csound AudioWorklet engine; this server predecessor
 # has not yet admitted that asset under the Teatro prefix.
 owner_host=ROOT.parents[2]/'assets/book-csound-host.js'
 host_target=out/'teatro/assets/book-csound-host.js'
 host_target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(owner_host,host_target)
 manifest={'schema':'fountain.press.kino-live-csound-stage.v169',
  'sourceOwner':'Fountain-Coach/fountain.coach',
  'teatroOwner':'Fountain-Coach/teatro.fountain.coach',
  'manuscriptSHA256':source_sha,
  'readerIndexSHA256':sha(updated.encode()),
  'readerAppSHA256':'4c238138d2ba7bd1860509bd0441ce8975be569a528110b87f33ae9a8f5bc9bf',
  'liveSynthIDs':['history-groove','history-memory','literal','directed'],
  'recordedComparisonCount':4,'liveSourceCount':4,'existingImagesPreserved':True,
  'originalBrowserCapturesClaimed':False,'privateWLANOnly':True,'publicReleaseAuthorized':False}
 manifest['changed']={'estate/index.html':filehash(target)}
 manifest['added']={p.relative_to(out).as_posix():filehash(p) for p in sorted(dest.iterdir())}
 manifest['added']['teatro/assets/book-csound-host.js']=filehash(host_target)
 receipt=out/'estate/evidence/press-kino-live-v169.json'
 receipt.parent.mkdir(parents=True,exist_ok=True)
 receipt.write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--parent',required=True)
 parser.add_argument('--out',required=True)
 args=parser.parse_args()
 build(args.parent,args.out)
