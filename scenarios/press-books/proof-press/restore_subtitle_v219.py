#!/usr/bin/env python3
"""Restore the omitted *authored* subtitle, without altering manuscript, images or Reader identity.

Exact immutable v218 -> v219 private Fountain Press successor. This is a
two bounded proof corrections on the established Linotype compositor.
"""
from pathlib import Path
import argparse,hashlib,html,json,re,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent))
from compose_v217_private import authored_template,WORK,PROOF_SOURCE
from published_frontend import source_templates
from keep_media_headings_v219 import patch as patch_engine, PRIOR as ENGINE_PRIOR
PREV='shared-shell-20261116-v218-kino-plates-restored'
RELEASE='shared-shell-20261116-v219-complete-authored-subtitle'
PREV_LOCK='b2dc3d053117fbc6a7d71813cb9f3f6b96ffbdd957bfc7b3dbabff229d5dadb8'
ROUTES=['estate/index.html','estate/read/library/index.html','estate/books/essays/index.html','estate/books/first-readings/index.html','estate/books/orange-dot/index.html','estate/read/essay--the-proof-of-the-page/index.html']
MANIFEST='estate/read/essay--the-proof-of-the-page/edition-manifest.json'
ENGINE_OLD='estate/assets/linotype/reading-first-press-engine.'+ENGINE_PRIOR+'.js'
SUBTITLE='On composition, judgment, and the thousand-page book'
def sha(data):return hashlib.sha256(data).hexdigest()
def read(base,name):
 p=(base/name).resolve();parent=base.resolve(strict=True)
 if not p.is_relative_to(parent) or not p.is_file():raise ValueError('REFUSED predecessor outside tree or missing '+name)
 return p.read_bytes()
def patch_source(original,template):
 old_names,old=source_templates(original)
 if WORK not in old:raise ValueError('Original work missing')
 src=old[WORK]
 add=(f'<div class="frame-source" data-source-block="the-proof-of-the-page.subtitle" '
      f'data-source-from="0" data-source-to="{len(SUBTITLE)}">{html.escape(SUBTITLE)}</div>')
 if 'the-proof-of-the-page.subtitle' in original or src.count('</h2>')!=1:raise ValueError('Subtitle already set or source drift')
 expected=src.replace('</h2>','</h2>'+add,1)
 if template!=f'<template data-reader-volume="{WORK}">'+expected+'</template>':
    raise ValueError('REFUSED old book had other changes than the one omitted authored line')
 start=f'<template data-reader-volume="{WORK}">'+src+'</template>'
 if original.count(start)!=1:raise ValueError('Original template not unique')
 updated=original.replace(start,template,1)
 new_names,changed=source_templates(updated)
 if new_names!=old_names or any(old[x]!=changed[x] for x in old_names if x!=WORK):
  raise ValueError('REFUSED other works modified by subtitle repair')
 return updated

def compose(previous,output,receipt,source_commit):
 if output.exists() or receipt.exists():raise ValueError('REFUSED artifact overwrite')
 if not re.fullmatch(r'[a-f0-9]{40}',source_commit):raise ValueError('REFUSED unpinned source commit')
 rawlock=read(previous,'source-lock.json')
 if sha(rawlock)!=PREV_LOCK:raise ValueError('REFUSED active v218 original lock drift')
 lock=json.loads(rawlock)
 if lock.get('pressProofV218KinoAssetAdmission',{}).get('releaseID')!=PREV:raise ValueError('REFUSED missing v218 ancestry')
 template,figures,counts=authored_template()
 assert len(figures)==6 and counts['paragraphs']==15
 changed={};modified={};added=[]
 output.mkdir(parents=True)
 def emit(rel,new):
  p=output/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(new)
  changed[rel]=sha(new);modified[rel]=sha(read(previous,rel))
 new_engine=patch_engine(read(previous,ENGINE_OLD))
 engine_sha=sha(new_engine)
 engine_new='estate/assets/linotype/reading-first-press-engine.'+engine_sha+'.js'
 engine_path=output/engine_new
 engine_path.parent.mkdir(parents=True,exist_ok=True);engine_path.write_bytes(new_engine)
 changed[engine_new]=engine_sha;added.append(engine_new)
 for rel in ROUTES:
  original=read(previous,rel).decode('utf8')
  updated=patch_source(original,template)
  if updated.count('/'+ENGINE_OLD)!=1:raise ValueError('REFUSED original Reader asset route drift')
  updated=updated.replace('/'+ENGINE_OLD,'/'+engine_new,1)
  if rel.endswith('essay--the-proof-of-the-page/index.html'):
   original_desc='<meta name="description" content="A source-authored, six-plate essay about traditional page proofing and the thousand-page book."/>'
   changed_desc=f'<meta name="description" content="{html.escape(SUBTITLE)}"/>'
   if updated.count(original_desc)!=1:raise ValueError('Source direct metadata drift')
   updated=updated.replace(original_desc,changed_desc,1)
   marker='<meta property="og:title" content="The Proof of the Page"/>'
   if updated.count(marker)!=1:raise ValueError('Original OG title missing')
   updated=updated.replace(marker,marker+f'<meta property="og:description" content="{html.escape(SUBTITLE)}"/>',1)
  emit(rel,updated.encode())
 manifest=json.loads(read(previous,MANIFEST))
 if manifest['sourceSHA256']!=PROOF_SOURCE or manifest['workID']!=WORK or manifest['publicReleaseAuthorized'] is not False:
  raise ValueError('REFUSED original stage manifest source or publication role')
 if 'sourceSubtitle' in manifest:raise ValueError('Subtitle already declared')
 manifest['sourceSubtitle']=SUBTITLE
 manifest['sourceSubtitleSHA256']=sha(SUBTITLE.encode())
 manifest['sourceSubtitleAddress']='the-proof-of-the-page.subtitle@0'
 emit(MANIFEST,(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode())
 lock['pressProofV219SubtitleAdmission']={'schema':'fountain.press.private-v219-authored-subtitle.v1',
  'releaseID':RELEASE,'predecessorReleaseID':PREV,'sourceOwnerCommit':source_commit,
  'originalManuscriptSHA256':PROOF_SOURCE,'originalSubtitleSHA256':sha(SUBTITLE.encode()),
  'sourceAddress':'the-proof-of-the-page.subtitle@0','stageOnly':True,'publicReleaseAuthorized':False,
  'productionModified':False,'addedPaths':sorted(added),
  'oldReaderEngineSHA256':ENGINE_PRIOR,'newReaderEngineSHA256':engine_sha,
  'changedWithoutLockSHA256':sha((json.dumps(changed,sort_keys=True,indent=2)+'\n').encode())}
 output.joinpath('source-lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n')
 changed['source-lock.json']=sha((output/'source-lock.json').read_bytes())
 modified['source-lock.json']=PREV_LOCK
 report={'schema':'fountain.press.private-v219-subtitle-candidate.v1','status':'PREPARED_NOT_ACTIVATED',
   'releaseID':RELEASE,'predecessorReleaseID':PREV,'publicationLane':'private-owner-WLAN-editorial-review',
   'sourceOwnerCommit':source_commit,'sourceSHA256':PROOF_SOURCE,'originalSubtitleSHA256':sha(SUBTITLE.encode()),
   'stageOnly':True,'publicReleaseAuthorized':False,'productionModified':False,
   'previousSourceLockSHA256':PREV_LOCK,'changedFilesSHA256':changed,'previousSHA256':modified,
   'addedPaths':sorted(added),'changedPaths':sorted(modified),'expectedBooks':{'essays':11,'first-readings':32,'orange-dot':23},
   'noOtherWorksAltered':True,'originalFiguresUnchanged':True,'readerEngineUnchanged':False,
   'readerEngineSourceSHA256':ENGINE_PRIOR,'readerEngineSHA256':engine_sha}
 receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--predecessor',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--source-commit',required=True);a=p.parse_args()
 r=compose(a.predecessor,a.output,a.receipt,a.source_commit);print('V219_PINNED_SUBTITLE_PRIVATE_CANDIDATE',r['releaseID'],len(r['changedFilesSHA256']),r['sourceSHA256'])
