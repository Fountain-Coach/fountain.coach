#!/usr/bin/env python3
"""Source-bound v216 -> v217 *private* Fountain Press delta, with no deployment.

Operates on an exact read-only copy of the active WLAN predecessor. Reuses its
Linotype Reader, Bookshelf, catalogue and direct-book shells. Public admission
is explicitly false. The editor's draft and six original drawings are unchanged.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import html
import json
import re
import shutil
import subprocess
import argparse
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent))
from heading_keep_v217 import patch as patch_engine,PRIOR as ENGINE_PRIOR
from published_frontend import source_templates

SOURCE=REPO/'site/essays/the-proof-of-the-page'
WORK='essay--the-proof-of-the-page'
RELEASE='shared-shell-20261116-v217-proof-of-the-page-heading-proof'
PREDECESSOR='shared-shell-20261116-v216-catalogue-bookshelf'
LANE='private-owner-WLAN-editorial-review'
HERO='assets/01-source-and-folio.svg'
OLD_ENGINE='estate/assets/linotype/reading-first-press-engine.'+ENGINE_PRIOR+'.js'
ENGINE_PATTERN=re.compile(r'/estate/assets/linotype/reading-first-press-engine\.[a-f0-9]{64}\.js')
GALLERY=re.compile(r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)',re.S)
SNAPSHOT=re.compile(r'(<script type="application/json" id="reader-publication-data">)(.*?)(</script>)',re.S)
TEMPLATE=re.compile(r'<template\s+data-reader-volume="([^"]+)"[^>]*>.*?</template>',re.S)
COMMIT_SHA=re.compile(r'^[a-f0-9]{40}$')
PREVIOUS_PIN='b8afc2666f8d2d4df8f083d7ad2193bd6039d4efa02a2b042eab999f32b21ec9'
PROOF_SOURCE='3778b007423c2b94a9e3da26b9a4c3f1dd7ff04e7ed53747cff43cb7ebc13647'


def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def raw(root:Path,name:str)->bytes:
    base=root.resolve(strict=True);p=(base/name).resolve()
    if not p.is_relative_to(base) or not p.is_file():raise ValueError('REFUSED missing or outside predecessor '+name)
    return p.read_bytes()
def one(txt,old,new):
    if txt.count(old)!=1:raise ValueError('REFUSED ambiguous source substitution '+str(old)[:64])
    return txt.replace(old,new,1)
def inlinemd(s:str)->str:
    # Preserve complete words and punctuation, interpret only the source's
    # declared emphasis/backticks, not a fabricated Markdown renderer.
    result=html.escape(s,quote=False)
    result=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',result)
    result=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>',result)
    result=re.sub(r'`([^`]+)`',r'<code>\1</code>',result)
    if '*' in re.sub(r'<[^>]+>','',result):
        raise ValueError('Unsupported editorial Markdown inline syntax '+s[:90])
    return result

def plain(s:str)->str:return html.unescape(re.sub(r'<[^>]+>','',s))
def authored_template():
    statement=json.loads((SOURCE/'source-receipt.json').read_text())
    original=(SOURCE/'combined-essay.md').read_bytes()
    if sha(original)!=PROOF_SOURCE or statement['manuscriptSHA256']!=PROOF_SOURCE or statement['workID']!=WORK or statement['publicationState']!='source-editorial-draft-not-published' or statement['releaseAuthorization'] is not False:
        raise ValueError('REFUSED draft source or public-rights drift')
    for name,digest in statement['illustrations'].items():
        if sha((SOURCE/name).read_bytes())!=digest:raise ValueError('REFUSED original plate SHA drift '+name)
    lines=original.decode().splitlines()
    if lines[:2]!=['# The Proof of the Page','On composition, judgment, and the thousand-page book']:
        raise ValueError('REFUSED essay title/subtitle drift')
    result=[];counts={'paragraphs':0,'subheadings':0,'figures':0};figure_records=[];para_number=0;i=2
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line or line=='---':continue
        if line.startswith('## '):
            contents=line[3:];ident=f'the-proof-of-the-page.section-{counts["subheadings"]+1}.heading'
            result.append(f'<p class="frame-subheading" data-source-block="{ident}" data-source-from="0" data-source-to="{len(contents)}">{inlinemd(contents)}</p>')
            counts['subheadings']+=1;para_number+=1;continue
        if line.startswith('!['):
            match=re.fullmatch(r'!\[([^\]]+)\]\((assets/[^)]+\.svg)\)',line)
            if not match:raise ValueError('REFUSED ungrounded source image '+line[:120])
            alt,image=match.groups()
            if i>=len(lines) or not lines[i].startswith('*Plate '):raise ValueError('REFUSED figure caption absent')
            caption=lines[i];i+=1
            expected=statement['illustrations'].get(image)
            if not expected:raise ValueError('REFUSED unadmitted plate '+image)
            size='700' if '05-thousand' in image else '640'
            source_id=f'the-proof-of-the-page.plate-{counts["figures"]+1:02d}'
            path=f'/estate/read/{WORK}/{image}'
            result.append(f'<figure class="frame-reading-figure" data-source-block="{source_id}" data-source-plate-sha256="{expected}" data-inline-after-paragraph="{para_number}"><img loading="eager" decoding="sync" src="{path}" alt="{html.escape(alt,quote=True)}" width="1100" height="{size}"/><figcaption>{inlinemd(caption)}</figcaption></figure>')
            counts['figures']+=1
            figure_records.append({'id':source_id,'sourcePath':image,'readerPath':path,'sha256':expected,'alt':alt,'caption':plain(inlinemd(caption)),'afterParagraph':para_number})
            continue
        if line.startswith('#') or line.startswith('!'):
            raise ValueError('REFUSED unexpected Markdown structure '+line)
        paragraph=[line]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','![','---')):
            paragraph.append(lines[i].strip());i+=1
        merged=' '.join(paragraph)
        rendered=inlinemd(merged)
        size=len(plain(rendered))
        if size<1:raise ValueError('Empty original paragraph')
        ident=f'the-proof-of-the-page.p{counts["paragraphs"]+1:02d}'
        result.append(f'<p data-source-block="{ident}" data-source-from="0" data-source-to="{size}">{rendered}</p>')
        counts['paragraphs']+=1;para_number+=1
    if counts!={'paragraphs':15,'subheadings':7,'figures':6}:
        raise ValueError('REFUSED actual manuscript content inventory '+str(counts))
    preface='The printer’s proof becomes a method for examining every addressed page. Six source-owned plates distinguish intentional white space, a stranded heading, the image’s place in prose, and the evidence needed before a thousand-page edition can be accepted.'
    chapter=f'<section class="book-chapter" id="work-the-proof-of-the-page"><div class="book-chapter-heading"><h2 data-source-block="the-proof-of-the-page.title">The Proof of the Page</h2></div></section>'
    proem=f'<aside class="frame-editorial-proem" data-editorial-role="proem" data-source-block="editorial.proem.the-proof-of-the-page" role="note" aria-label="Editorial preface"><span class="frame-editorial-kicker">From the editor</span><p>{html.escape(preface)}</p></aside>'
    template=f'<template data-reader-volume="{WORK}"><div class="book-flow" data-min-leaves="1" data-source-work-sha256="{PROOF_SOURCE}">{chapter}<section class="book-chapter-text">{proem}<article class="book-prose">'+''.join(result)+'</article></section></div></template>'
    return template,figure_records,counts


def compile_delta(source:Path,out:Path,receipt:Path,source_commit:str):
    if out.exists() or receipt.exists():raise ValueError('REFUSED candidate/receipt already exists')
    if not COMMIT_SHA.fullmatch(source_commit):raise ValueError('REFUSED unpinned source Git revision')
    base_lock=raw(source,'source-lock.json')
    if sha(base_lock)!=PREVIOUS_PIN:raise ValueError('REFUSED predecessor v216 lock drift')
    admission=json.loads((REPO/'scenarios/press-books/wlan-stage-v216-admission.json').read_text())
    for key,want in admission['changedFilesSHA256'].items():
        p=source/key
        if p.is_file() and sha(p.read_bytes())!=want:
            raise ValueError('REFUSED changed v216 predecessor source '+key)
    stage=raw(source,'estate/index.html').decode('utf8')
    original,original_map=source_templates(stage)
    if WORK in original_map or len(original)<70:
        raise ValueError('REFUSED previous estate source identities drift')
    template,figures,counts=authored_template()
    gallery_match=GALLERY.search(stage);snap_match=SNAPSHOT.search(stage)
    if not gallery_match or not snap_match:raise ValueError('Missing original authored catalogue or gallery')
    gallery=json.loads(gallery_match[2]);snap=json.loads(snap_match[2]);catalog=json.loads(raw(source,'estate/books/catalog.json'))
    if snap['publicationLane']!=LANE or catalog['status']!=LANE or catalog['publicReleaseAuthorized'] is not False:
        raise ValueError('REFUSED private edition role mismatch')
    essay=next(b for b in snap['books'] if b['id']=='essays');essays=next(b for b in catalog['books'] if b['id']=='essays')
    if len(essay['orderedWorkIDs'])!=10 or len(gallery['collections']['essays'])!=10 or len(essays['illustratedWorkIDs'])!=10:
        raise ValueError('REFUSED predecessor Essays membership drift')
    if len(snap['books'])!=3 or len(catalog['books'])!=3:
        raise ValueError('REFUSED unexpected book inventory')
    for b in snap['books']:
        if b['stageOnly'] is not True or b['publicReleaseAuthorized'] is not False:
            raise ValueError('REFUSED public admission in private stage')
    old_engine=raw(source,OLD_ENGINE)
    new_engine=patch_engine(old_engine)
    engine_digest=sha(new_engine)
    new_engine_path='estate/assets/linotype/reading-first-press-engine.'+engine_digest+'.js'
    old_engine_uri='/'+OLD_ENGINE;new_engine_uri='/'+new_engine_path
    # Preserve complete existing source/reader; append only the source-owned work.
    last_essay=re.search(r'<template data-reader-volume="essay--a-sound-must-earn-its-place"[^>]*>.*?</template>',stage,re.S)
    if not last_essay:raise ValueError('Last previous essay identity not found')
    insert_after=last_essay[0]
    first=figures[0]
    item={'id':WORK,'src':first['readerPath'],'alt':first['alt'],'sourceKind':'source-owned-explanatory-proof-plate','sourceSHA256':first['sha256'],'stageOnly':True,'publicReleaseAuthorized':False}
    gallery['collections']['essays'].append(item)
    gallery['source']['proofPressCompanion']={'owner':'Fountain-Coach/fountain.coach','sourceRevision':source_commit,'sourceSHA256':PROOF_SOURCE,'stageOnly':True,'publicReleaseAuthorized':False}
    essay['orderedWorkIDs'].append(WORK);essay['illustratedWorkIDs'].append(WORK)
    essays['orderedWorkIDs'].append(WORK);essays['illustratedWorkIDs'].append(WORK)
    snap['requiredEditorialProemWorkIDs'].append(WORK)
    snap['sourceGitRevision']=source_commit
    snap['sourcePredecessorReleaseID']=PREDECESSOR
    snap['sourceAddedWork']={'id':WORK,'sourceSHA256':PROOF_SOURCE,'sourceOwnerCommit':source_commit,'stageOnly':True,'publicReleaseAuthorized':False}
    catalog['sourceGitRevision']=source_commit
    catalog['publicationSnapshotSourceReleaseID']=RELEASE
    catalog['privateProofPressEssay']={'id':WORK,'sourceOwner':'Fountain-Coach/fountain.coach','sourceCommit':source_commit,'sourceSHA256':PROOF_SOURCE,'stageOnly':True,'publicReleaseAuthorized':False,'figureSHA256s':{f['id']:f['sha256'] for f in figures}}
    essays['stagePreviewSourceReleaseID']=RELEASE
    catalog['stageOnly']=True;catalog['publicReleaseAuthorized']=False
    for book in catalog['books']:
        if book.get('publicReleaseAuthorized') is not False or book.get('stageOnly') is not True:
            raise ValueError('REFUSED promotion through staging')
    new_gallery=json.dumps(gallery,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    new_snap=json.dumps(snap,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    old_gallery=gallery_match[2];old_snap=snap_match[2]
    changes={};added=[];predecessor={}
    out.mkdir(parents=True)
    def emit(name,data,created=False):
        if name in changes:raise ValueError('Duplicate changed route '+name)
        p=out/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data);changes[name]=sha(data)
        if created:added.append(name)
        else:predecessor[name]=sha(raw(source,name))
    def transform_html(old:str):
        if old.count(insert_after)!=1:raise ValueError('Missing source insertion point in direct shell')
        edited=one(old,insert_after,insert_after+template)
        edited=one(edited,old_gallery,new_gallery)
        edited=one(edited,old_snap,new_snap)
        if edited.count(old_engine_uri)!=1:raise ValueError('Engine asset reference not unique')
        edited=one(edited,old_engine_uri,new_engine_uri)
        original_ids,original_templates=source_templates(old)
        new_ids,new_templates=source_templates(edited)
        if any(original_templates[k]!=new_templates.get(k) for k in original_ids):
            raise ValueError('REFUSED existing 78 source templates mutated')
        if set(new_ids)-set(original_ids)!={WORK}:raise ValueError('Incorrect added work identity')
        return edited
    shell_routes=['estate/index.html','estate/read/library/index.html',
                  'estate/books/essays/index.html','estate/books/first-readings/index.html',
                  'estate/books/orange-dot/index.html']
    for name in shell_routes:
        old=raw(source,name).decode('utf8');new=transform_html(old)
        if name=='estate/books/essays/index.html':
            # The source-authored direct book structured data must reflect its
            # exact 11 active essays. Other books retain their original metadata.
            m=re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)',new,re.S)
            if not m:raise ValueError('Missing source-owned essays Book JSON-LD')
            info=json.loads(m[2]);parts=info.get('hasPart')
            if not isinstance(parts,list) or len(parts)!=10:raise ValueError('Old Essays structured membership drift')
            parts.append({'@type':'CreativeWork','identifier':WORK,'url':'https://fountain.coach/estate/read/'+WORK+'/'})
            new=one(new,m[0],m[1]+json.dumps(info,ensure_ascii=False,separators=(',',':'))+m[3])
        emit(name,new.encode())
    emit('estate/books/catalog.json',(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n').encode())
    emit(new_engine_path,new_engine,True)
    for fig in figures:
        path='estate/read/'+WORK+'/'+fig['sourcePath']
        emit(path,(SOURCE/fig['sourcePath']).read_bytes(),True)
    # A stage-only static direct entrance with genuine crawler metadata and an
    # aspect-preserving derivative of plate 01, not a generated replacement.
    social_path='estate/read/'+WORK+'/assets/proof-of-the-page-social.jpg'
    first_path=SOURCE/HERO
    art=subprocess.check_output(['rsvg-convert','--width','1200',str(first_path)])
    generated=subprocess.run(['magick','png:-','-resize','1200x630','-gravity','center','-background','#f7f4ec','-extent','1200x630','-quality','90','jpeg:-'],input=art,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
    emit(social_path,generated,True)
    direct=transform_html(raw(source,'estate/index.html').decode())
    direct=one(direct,'data-initial-volume="library"','data-initial-volume="'+WORK+'"')
    # Override only the head of this exact work while preserving shared Reader.
    head,tail=direct.split('</head>',1)
    title_match=re.search(r'<title>.*?</title>',head,re.S)
    if not title_match:raise ValueError('Missing native book title')
    head=one(head,title_match[0],'<title>The Proof of the Page — Fountain Press private proof</title>')
    if '<meta name="robots" content="noindex,nofollow"/>' not in head:
        raise ValueError('Private original review robots unavailable')
    # This direct stage route has *one* metadata identity. Delete only the
    # inherited generic Bookshelf crawler tags and replace them with declared
    # source-derived article tags. Never expose an indexable private draft.
    for tag in re.findall(r'<meta\b[^>]*>',head,re.I):
        if 'property="og:' in tag or 'name="twitter:' in tag or 'name="description"' in tag:
            head=one(head,tag,'')
    for old_ld in re.findall(r'<script type="application/ld\+json">.*?</script>',head,re.S):
        head=one(head,old_ld,'')
    canonical=re.search(r'<link\s+rel="canonical"[^>]*>',head,re.I)
    if not canonical:raise ValueError('Missing direct canonical source identity')
    head=one(head,canonical[0],'<link rel="canonical" href="https://fountain.coach/estate/read/'+WORK+'/"/>')
    metadata=[
      '<meta name="description" content="A source-authored, six-plate essay about traditional page proofing and the thousand-page book."/>',
      '<meta property="og:title" content="The Proof of the Page"/>',
      '<meta property="og:type" content="article"/>',
      '<meta property="og:url" content="https://fountain.coach/estate/read/'+WORK+'/"/>',
      '<meta property="og:image" content="/estate/read/'+WORK+'/assets/proof-of-the-page-social.jpg"/>',
      '<meta property="og:image:width" content="1200"/>',
      '<meta property="og:image:height" content="630"/>',
      '<meta property="og:image:alt" content="Source and folio: the same addressed passage composed in three different measures."/>',
      '<meta name="twitter:card" content="summary_large_image"/>',
      '<meta name="twitter:title" content="The Proof of the Page"/>',
      '<meta name="twitter:image" content="/estate/read/'+WORK+'/assets/proof-of-the-page-social.jpg"/>',
    ]
    head=one(head,'</title>','</title>\n'+'\n'.join(metadata))
    head+='<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@type':'Article','identifier':WORK,'headline':'The Proof of the Page','isPartOf':{'@type':'Book','name':'Essays'},'image':'/estate/read/'+WORK+'/assets/proof-of-the-page-social.jpg','creativeWorkStatus':'private editorial review','isAccessibleForFree':False},ensure_ascii=False,separators=(',',':'))+'</script>'
    emit('estate/read/'+WORK+'/index.html',(head+'</head>'+tail).encode(),True)
    manifest={'schema':'fountain.press.source-bound-illustrated-private-preview.v1','releaseID':RELEASE,'predecessorReleaseID':PREDECESSOR,'sourceOwner':'Fountain-Coach/fountain.coach','sourceCommit':source_commit,'sourceSHA256':PROOF_SOURCE,'workID':WORK,'title':'The Proof of the Page','publicationLane':LANE,'stageOnly':True,'publicReleaseAuthorized':False,'figures':figures,'socialImagePath':'/'+social_path,'socialImageSHA256':sha(generated),'socialImageDimensions':[1200,630],'sourceParagraphCounts':counts,'headingKeepEngineSHA256':engine_digest}
    emit('estate/read/'+WORK+'/edition-manifest.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode(),True)
    # The lock itself records a stable digest of all OTHER changed bytes to
    # prevent a self-reference. Admission separately pins the full lock bytes.
    lock=json.loads(base_lock)
    lock['pressProofV217Admission']={'schema':'fountain.press.private-proof-v217.v1','releaseID':RELEASE,'predecessorReleaseID':PREDECESSOR,'sourceOwnerCommit':source_commit,'originalManuscriptSHA256':PROOF_SOURCE,'privateStageOnly':True,'publicReleaseAuthorized':False,'changedWithoutLockSHA256':sha((json.dumps(changes,sort_keys=True,indent=2)+'\n').encode()),'addedPaths':sorted(added),'engineSourceSHA256':engine_digest,'manifestSHA256':changes['estate/read/'+WORK+'/edition-manifest.json']}
    emit('source-lock.json',(json.dumps(lock,ensure_ascii=False,indent=2)+'\n').encode())
    report={'schema':'fountain.press.private-immutable-v217-candidate.v1','status':'PREPARED_NOT_ACTIVATED','releaseID':RELEASE,'predecessorReleaseID':PREDECESSOR,'sourceOwnerCommit':source_commit,'sourceSHA256':PROOF_SOURCE,'publicationLane':LANE,'stageOnly':True,'publicReleaseAuthorized':False,'productionModified':False,'predecessorSourceLockSHA256':PREVIOUS_PIN,'predecessorSHA256':predecessor,'changedFilesSHA256':changes,'addedPaths':sorted(added),'changedPaths':sorted(set(changes)-set(added)),'editorialReviewRequired':True,'expectedBooks':{'essays':11,'first-readings':32,'orange-dot':23},'expectedIllustrations':{'essays':11,'first-readings':30,'orange-dot':23},'sourceWork':WORK,'originalFigures':[{'id':f['id'],'sha256':f['sha256'],'sourcePath':f['sourcePath']} for f in figures]}
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--predecessor',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--receipt',required=True,type=Path);p.add_argument('--source-commit',required=True)
    a=p.parse_args();r=compile_delta(a.predecessor,a.output,a.receipt,a.source_commit)
    print(json.dumps({'status':r['status'],'releaseID':r['releaseID'],'changed':len(r['changedPaths']),'added':len(r['addedPaths']),'books':r['expectedBooks'],'SHA':r['changedFilesSHA256']['source-lock.json']},indent=2))
