#!/usr/bin/env python3
"""Admit a private WLAN stage projection through the SAME Linotype frontend.

Creates a small, source-bound delta over the actual stage v215 predecessor.
No environment delivery, service mutation or production publication occurs here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from published_frontend import (
    APP_PATTERN, GALLERY_PATTERN, STYLE, compile_app, digest,
    json_bytes, parse_gallery, parse_source_exclusion_ids,
    read_pinned, replace_once, source_templates,
)

HERE=Path(__file__).resolve().parent
META=re.compile(r'<meta\b[^>]*>',re.I)
LD=re.compile(r'<script type="application/ld\+json">(.*?)</script>',re.S)
TITLE=re.compile(r'<title>.*?</title>',re.S)
CANONICAL=re.compile(r'<link\s+rel="canonical"[^>]*>',re.I)


def snapshot_stage(page:str,app:str,catalog:dict,admission:dict):
    names,source=source_templates(page)
    gallery=parse_gallery(page)
    expected=admission['expectedBookIDs']
    if [book['id'] for book in catalog['books']]!=expected or list(gallery)!=expected:
        raise ValueError('REFUSED staged book order disagrees with admitted source')
    if catalog.get('status')!=admission['expectedCatalogueStatus'] or catalog.get('publicReleaseAuthorized') is True:
        raise ValueError('REFUSED public/private stage catalogue boundary drift')
    original_roles={**dict.fromkeys(parse_source_exclusion_ids(app,'implementationStories'),'historical-public'),
                    **dict.fromkeys(parse_source_exclusion_ids(app,'archivedEssays'),'archived-public')}
    if original_roles!=admission['unlistedSourceWorkRoles']:
        raise ValueError('REFUSED stage original archive role drift')
    books=[];proem_ids=[];used=set()
    for book in catalog['books']:
        id=book['id'];illustrated=[item['id'] for item in gallery[id]]
        if book.get('stageOnly') is not True or book.get('publicReleaseAuthorized') is not False:
            raise ValueError('REFUSED no private-stage admission for '+id)
        if not illustrated or len(illustrated)!=len(set(illustrated)):
            raise ValueError('Empty/duplicate staged gallery '+id)
        if id=='essays':
            listed=illustrated[:]
            historical=[name for name in names if name.startswith('essay--') and name not in listed]
            if set(historical)!=set(original_roles):
                raise ValueError('REFUSED unstated essay exclusion or published work loss')
        else:
            prefix=illustrated[0].split('--',1)[0]+'--'
            listed=[name for name in names if name.startswith(prefix)]
            historical=[]
            if illustrated!=listed[len(listed)-len(illustrated):]:
                raise ValueError('REFUSED original staged source/illustration order drift: '+id)
        if len(listed)!=len(set(listed)) or any(w not in source or w in used for w in listed):
            raise ValueError('Duplicate or missing private-stage authored work: '+id)
        used.update(listed)
        previous=-1
        for work in illustrated:
            if work not in listed or listed.index(work)<=previous:
                raise ValueError('Staged illustration outside ordered contents: '+id)
            previous=listed.index(work)
        for work in listed:
            if 'data-editorial-role="proem"' in source[work]:
                if 'data-source-block' not in source[work]:
                    raise ValueError('Source proem address missing: '+work)
                proem_ids.append(work)
        count=sum(w in proem_ids for w in listed)
        if id in admission['requiredEditorialProemCounts'] and count!=admission['requiredEditorialProemCounts'][id]:
            raise ValueError('Required stage proem drift '+id+': '+str(count))
        authored=admission['existingPresentation'].get(id,{})
        books.append({'id':id,'title':book['title'],'canonicalURL':book['canonicalURL'],
                      'directURLPath':book['directURLPath'],
                      'publicationState':admission['lane'],
                      'originalPublicationState':book.get('publicationState'),
                      'publicReleaseAuthorized':False,'stageOnly':True,'stagePreviewAuthorized':True,
                      'sourceRevision':book['sourceRevision'],
                      'orderedWorkIDs':listed,'illustratedWorkIDs':illustrated,
                      'unlistedSourceWorks':[{'id':w,'status':original_roles[w]} for w in historical],
                      **({'subtitle':authored['subtitle']} if authored.get('subtitle') else {}),
                      **({'contentsCaption':authored['contentsCaption']} if authored.get('contentsCaption') else {})})
    return {'schema':'fountain.press.publication-snapshot.v1',
            'publicationLane':admission['lane'],
            'sourceOwner':catalog['sourceOwner'],
            'sourceGitRevision':catalog['sourceGitRevision'],
            'sourcePredecessorReleaseID':admission['releaseID'],
            'books':books,'requiredEditorialProemWorkIDs':proem_ids}


def preserve_book_meta(compiled_root:str,original:str,book:dict,gallery:list):
    """Recompose a stale direct route from the actual latest authored stage.

    Preserve the book's direct identity, social image, rights and original art.
    Require the new root to retain every previous source template unchanged.
    """
    start=compiled_root.split('</head>',1)[0]
    previous=original.split('</head>',1)[0]
    old_names,old_templates=source_templates(original)
    new_names,new_templates=source_templates(compiled_root)
    if set(old_names)-set(new_names):
        raise ValueError('REFUSED former direct book has source missing from current Reader')
    if any(old_templates[key]!=new_templates[key] for key in old_names):
        raise ValueError('REFUSED original authored work changed during direct book reconciliation')
    expected_missing=set(book['expectedMissing'])
    if set(new_names)-set(old_names)!=expected_missing:
        raise ValueError('REFUSED undeclared direct book source/template delta')
    # Preserve exact original per-book meta, not the root's generic book SEO.
    old_title=TITLE.search(previous)
    old_canonical=CANONICAL.search(previous)
    if not old_title or not old_canonical:
        raise ValueError('Direct book identity head is missing')
    start=TITLE.sub(lambda _:old_title[0],start,count=1)
    start=CANONICAL.sub(lambda _:old_canonical[0],start,count=1)
    def role(tag):
        if 'property="og:' in tag:return 'og'
        if 'name="twitter:' in tag:return 'twitter'
        if 'name="description"' in tag:return 'description'
        if 'name="robots"' in tag:return 'robots'
        return None
    before=[t for t in META.findall(previous) if role(t)]
    if not any(role(t)=='og' for t in before):
        raise ValueError('Direct-book social image metadata missing')
    start=META.sub(lambda m:'' if role(m[0]) else m[0],start)
    old_ld=LD.findall(previous)
    if len(old_ld)!=1:raise ValueError('Direct-book original JSON-LD unavailable')
    data=json.loads(old_ld[0]);data['hasPart']=[{
        '@type':'CreativeWork','identifier':id,'url':'https://fountain.coach/estate/read/'+id+'/'
        } for id in book['orderedWorkIDs']]
    start=LD.sub('',start)
    # The stage remains private even where old source metadata was index,follow.
    before=[tag for tag in before if role(tag)!='robots']
    before.append('<meta name="robots" content="noindex,nofollow"/>')
    head=start+'\n'+'\n'.join(before)+'\n'+'<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
    page=head+'</head>'+compiled_root.split('</head>',1)[1]
    return replace_once(page,'data-initial-volume="library"',
                        'data-initial-volume="'+book['id']+'"','direct-book volume')


def compile_stage(root:Path,out:Path,admission:dict,receipt:Path):
    if out.exists() or receipt.exists():raise ValueError('REFUSED immutable candidate/receipt already exists')
    input_files={p:read_pinned(root,p,admission) for p in admission['sourceDigestSHA256']}
    page=input_files['estate/index.html'].decode()
    catalog=json.loads(input_files['estate/books/catalog.json'])
    lock=json.loads(input_files['source-lock.json'])
    app_path=next(p for p in input_files if APP_PATTERN.fullmatch('/'+p))
    if set(APP_PATTERN.findall(page))!={'/'+app_path}:
        raise ValueError('REFUSED unexpected active-stage Reader module')
    app=input_files[app_path].decode()
    snap=snapshot_stage(page,app,catalog,admission)
    script=compile_app(app).encode('utf8')
    new_app='estate/assets/linotype/reading-first-app.'+digest(script)+'.js'
    source_gallery=parse_gallery(page)
    inserted='<script type="application/json" id="reader-publication-data">'+json.dumps(snap,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>'
    def project(html):
        html=replace_once(html,app_path,new_app,'Reader module path')
        old=GALLERY_PATTERN.search(html)
        if not old:raise ValueError('Missing original gallery data')
        return replace_once(html,old[0],old[0]+'\n'+inserted,'publication snapshot')
    current_root=project(page)
    # All stage routes are a private review, no indexable public content.
    current_root=replace_once(current_root,'<meta name="robots" content="index,follow"/>',
                '<meta name="robots" content="noindex,nofollow"/>','private preview robots')
    changes={};added=[]
    def emit(path,data,created=False):
        file=out/path;file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(data);changes[path]=digest(data)
        if created:added.append(path)
    out.mkdir(parents=True,exist_ok=False)
    emit('estate/index.html',current_root.encode())
    for book in snap['books']:
        id=book['id'];original=input_files[f'estate/books/{id}/index.html'].decode()
        book['expectedMissing']=admission['expectedDirectMissingSourceWorks'][id]
        updated=preserve_book_meta(current_root,original,book,source_gallery[id]);del book['expectedMissing']
        emit(f'estate/books/{id}/index.html',updated.encode())
    emit(admission['missingLegacyRoute'],current_root.encode(),created=True)
    # Do not retain an obsolete independent Essays listing on the current stage.
    # The canonical direct Essays book already has the correct Reader and schema.
    emit('estate/essays/index.html',(out/'estate/books/essays/index.html').read_bytes())
    for b in catalog['books']:
        found=next(item for item in snap['books'] if item['id']==b['id'])
        b['orderedWorkIDs']=found['orderedWorkIDs']
        b['illustratedWorkIDs']=found['illustratedWorkIDs']
        b['unlistedSourceWorks']=found['unlistedSourceWorks']
        first=source_gallery[b['id']][0]
        b['firstIllustratedChapterID']=first['id']
        b['firstChapterOriginalImagePath']=first['src']
        if first.get('sourceSHA256'):b['firstChapterOriginalImageSHA256']=first['sourceSHA256']
        b['firstChapterImageAlt']=first['alt']
        b['stagePreviewSourceReleaseID']=admission['releaseID']
        # Original social derivative remains historical when the source hero changed;
        # production publication must separately recompose that derivative.
        b['socialPreviewSourceMatchesCurrentHero']=\
          b.get('firstChapterOriginalImagePath')==b.get('socialImageSourcePath',b['firstChapterOriginalImagePath']) and \
          b.get('firstChapterOriginalImageSHA256')==b.get('sourceIllustrationDeclaredSHA256')
    catalog['stagedCollectionOrder']=[b['id'] for b in snap['books']]
    catalog['publicationSnapshotSchema']=snap['schema']
    catalog['publicationSnapshotSourceReleaseID']=admission['releaseID']
    if catalog.get('publicReleaseAuthorized') is not False or any(b['publicReleaseAuthorized'] is not False or b['stageOnly'] is not True for b in catalog['books']):
        raise ValueError('Stage catalogue public status mutation refused')
    emit('estate/books/catalog.json',json_bytes(catalog))
    emit(new_app,script,created=True)
    css=input_files['estate/assets/linotype/reading-first-shell.css'].decode()
    emit('estate/assets/linotype/reading-first-shell.css',(css+STYLE).encode())
    lock['pressBookshelfCmsV216Admission']={
        'schema':'fountain.press.cms.private-stage-admission.v1',
        'sourceOwner':admission['sourceOwner'],
        'sourceOwnerCommit':'3b83455c2f08caae02ed63788e0b866bba734760',
        'predecessorReleaseID':admission['releaseID'],
        'candidateReleaseID':admission['nextReleaseID'],
        'productionModified':False,
        'privateStageOnly':True,
        'sourceLockPredecessorSHA256':admission['sourceDigestSHA256']['source-lock.json'],
        'frontendSnapshotSHA256':digest(json_bytes(snap)),
        'books':[{'id':b['id'],'works':len(b['orderedWorkIDs']),'art':len(b['illustratedWorkIDs'])} for b in snap['books']],
        'modifiedStageRoutes':sorted(p for p in changes if p not in added),
        'addedStageRoutes':sorted(added),
    }
    emit('source-lock.json',json_bytes(lock))
    # The existing composer must execute closure before any publishable receipt.
    from publication_closure import verify as verify_publication_closure
    verify_publication_closure(out, predecessor=root, lane='staging')
    # Only the current v215 source can be the predecessor of a new v216 gate.
    result={'schema':'fountain.press.cms.stage-candidate-receipt.v1',
            'status':'PREPARED_NOT_ACTIVATED',
            'publicationLane':admission['lane'],
            'releaseID':admission['nextReleaseID'],
            'predecessorReleaseID':admission['releaseID'],
            'productionModified':False,
            'sourceOwnerCommit':'3b83455c2f08caae02ed63788e0b866bba734760',
            'predecessorSHA256':{p:digest(raw) for p,raw in input_files.items()},
            'snapshotSHA256':digest(json_bytes(snap)),
            'privateBookOrder':catalog['stagedCollectionOrder'],
            'bookWorkCounts':{b['id']:len(b['orderedWorkIDs']) for b in snap['books']},
            'bookIllustrationCounts':{b['id']:len(b['illustratedWorkIDs']) for b in snap['books']},
            'changedFilesSHA256':changes,'addedPaths':sorted(added),
            'changedPaths':sorted(set(changes)-set(added))}
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_bytes(json_bytes(result))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--receipt',required=True,type=Path)
    p.add_argument('--predecessor',type=Path,default=HERE/'wlan-stage-v215-predecessor.json')
    a=p.parse_args();admission=json.loads(a.predecessor.read_text())
    if admission.get('schema')!='fountain.press.stage-frontend-predecessor.v1':raise SystemExit('Wrong private WLAN source schema')
    try:result=compile_stage(a.input,a.output,admission,a.receipt)
    except (ValueError,KeyError,IndexError,TypeError,FileNotFoundError) as err:raise SystemExit(str(err))
    print(json.dumps({k:result[k] for k in ('status','releaseID','bookWorkCounts','bookIllustrationCounts','addedPaths','changedPaths')},indent=2))
