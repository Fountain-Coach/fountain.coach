#!/usr/bin/env python3
"""Independent digest/semantic guard for an immutable private-stage overlay.

This validates an unactivated candidate, never the live release or a public host.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from published_frontend import APP_PATTERN,GALLERY_PATTERN,digest,parse_gallery,source_templates
from published_frontend_stage import META,LD
from publication_closure import verify as verify_publication_closure

SNAP=re.compile(r'<script type="application/json" id="reader-publication-data">(.*?)</script>',re.S)

def verify(predecessor:Path,candidate:Path,receipt:dict,admission:dict):
    if receipt['status']!='PREPARED_NOT_ACTIVATED' or receipt['publicationLane']!='private-owner-WLAN-editorial-review' or receipt['productionModified'] is not False:
        raise ValueError('Candidate claims unauthorized public/activated publication')
    if receipt['predecessorReleaseID']!=admission['releaseID'] or receipt['releaseID']!=admission['nextReleaseID']:
        raise ValueError('Private stage release identity mismatch')
    if set(receipt['changedFilesSHA256']) != set(receipt['changedPaths'])|set(receipt['addedPaths']) or set(receipt['changedPaths'])&set(receipt['addedPaths']):
        raise ValueError('Invalid complete stage delta inventory')
    for path,expected in admission['sourceDigestSHA256'].items():
        if digest((predecessor/path).read_bytes())!=expected or receipt['predecessorSHA256'][path]!=expected:
            raise ValueError('Drifted private predecessor source '+path)
    for path,expected in receipt['changedFilesSHA256'].items():
        data=(candidate/path).read_bytes()
        if digest(data)!=expected:raise ValueError('Drifted candidate byte source '+path)
    if len(list(candidate.rglob('*'))) < len(receipt['changedFilesSHA256']):
        raise ValueError('Incomplete file overlay')
    if any((predecessor/p).exists() for p in receipt['addedPaths']):
        raise ValueError('A route classified new already existed in active predecessor')
    if any(not (predecessor/p).is_file() for p in receipt['changedPaths']):
        raise ValueError('Changed path not owned by predecessor')
    stage=(candidate/'estate/index.html').read_text()
    snaplist=SNAP.findall(stage)
    if len(snaplist)!=1:raise ValueError('No single admitted staging frontend snapshot')
    snap=json.loads(snaplist[0]);catalog=json.loads((candidate/'estate/books/catalog.json').read_text())
    ids=[b['id'] for b in snap['books']]
    if snap['publicationLane']!='private-owner-WLAN-editorial-review' or ids!=admission['expectedBookIDs'] or catalog['stagedCollectionOrder']!=ids:
        raise ValueError('Stage Bookshelf order/publication lane drift')
    if catalog['status']!=admission['expectedCatalogueStatus'] or catalog['publicReleaseAuthorized'] is not False:
        raise ValueError('Private catalogue publication authority corrupted')
    if catalog.get('currentReleaseID') is not None:
        raise ValueError('Invented public production release in private staging')
    original=(predecessor/'estate/index.html').read_text()
    stage_names,stage_sources=source_templates(stage);old_names,old_sources=source_templates(original)
    if stage_names!=old_names or stage_sources!=old_sources:
        raise ValueError('Changed authorial source templates while adapting frontend')
    galleries=parse_gallery(stage)
    app=APP_PATTERN.findall(stage)
    if len(app)!=1 or digest((candidate/app[0].lstrip('/')).read_bytes())!=app[0].split('.')[-2]:
        raise ValueError('Unbound hashed Reader module')
    js=(candidate/app[0].lstrip('/')).read_text()
    if 'reader-shelf-leaf-navigation' not in js or 'publication.publicationLane' not in js:
        raise ValueError('Private staging Reader cannot render complete collection model')
    if '<meta name="robots" content="noindex,nofollow"/>' not in stage.split('</head>')[0]:
        raise ValueError('Private stage root is indexable')
    linked=set()
    for book in snap['books']:
        id=book['id'];published=next(b for b in catalog['books'] if b['id']==id)
        if (book['publicationState']!='private-owner-WLAN-editorial-review' or
            book['originalPublicationState']!=published.get('publicationState') or
            book['publicReleaseAuthorized'] is not False or book['stageOnly'] is not True):
            raise ValueError('Private staging book promoted to public: '+id)
        if book['stagePreviewAuthorized'] is not True or published['publicReleaseAuthorized'] is not False or published['stageOnly'] is not True:
            raise ValueError('Book state/original admission drift: '+id)
        if published['orderedWorkIDs']!=book['orderedWorkIDs'] or published['illustratedWorkIDs']!=book['illustratedWorkIDs']:
            raise ValueError('Stage machine catalogue differs from rendered book contents: '+id)
        if any(w not in stage_sources for w in book['orderedWorkIDs']) or len(set(book['orderedWorkIDs']))!=len(book['orderedWorkIDs']):
            raise ValueError('Missing duplicate or unadmitted stage work: '+id)
        if linked.intersection(book['orderedWorkIDs']):raise ValueError('Work in two staged books')
        linked.update(book['orderedWorkIDs'])
        gallery=[item['id'] for item in galleries[id]]
        if gallery!=book['illustratedWorkIDs'] or published['firstIllustratedChapterID']!=gallery[0]:
            raise ValueError('Stage illustrated source drift: '+id)
        new=(candidate/f'estate/books/{id}/index.html').read_text()
        if SNAP.findall(new)!=snaplist or APP_PATTERN.findall(new)!=app or parse_gallery(new)!=galleries:
            raise ValueError('Stale stage direct-book shell: '+id)
        if 'data-initial-volume="'+id+'"' not in new or '<meta name="robots" content="noindex,nofollow"/>' not in new.split('</head>')[0]:
            raise ValueError('Direct book volume/private robots drift: '+id)
        original_book=(predecessor/f'estate/books/{id}/index.html').read_text()
        for source_field in ('<title>','<link rel="canonical"'):
            if source_field not in new or source_field not in original_book:
                raise ValueError('Source book head missing '+id)
        old_gallery=source_templates(original_book)[1]
        if any(stage_sources[x]!=value for x,value in old_gallery.items()):
            raise ValueError('Source-original direct book manuscript changed: '+id)
        old_meta=original_book.split('</head>',1)[0]
        for key in ('og:image','twitter:image'):
            pattern=r'<meta (?:name|property)="'+key+r'" content="([^"]+)"'
            m=re.search(pattern,old_meta)
            if m and m[0] not in new.split('</head>',1)[0]:
                raise ValueError('Original source-owned social metadata lost '+id+' '+key)
        ld=LD.findall(new.split('</head>',1)[0])
        if len(ld)!=1 or [p['identifier'] for p in json.loads(ld[0])['hasPart']]!=book['orderedWorkIDs']:
            raise ValueError('Stale stage direct-book JSON-LD contents: '+id)
    if (candidate/admission['missingLegacyRoute']).read_bytes()!=(candidate/'estate/index.html').read_bytes():
        raise ValueError('Legacy library Bookshelf route still differs from current stage')
    stage_lock=json.loads((candidate/'source-lock.json').read_text())
    old_lock=json.loads((predecessor/'source-lock.json').read_text())
    admission_key='pressBookshelfCmsV216Admission'
    marker=stage_lock.pop(admission_key,None)
    if stage_lock!=old_lock or not marker or marker['productionModified'] is not False or marker['privateStageOnly'] is not True:
        raise ValueError('Inherited stage source-lock authority mutated')
    if marker['sourceLockPredecessorSHA256']!=admission['sourceDigestSHA256']['source-lock.json'] or marker['candidateReleaseID']!=receipt['releaseID']:
        raise ValueError('Private stage source-lock release identity drift')
    # Publication closure is compulsory, not an optional post-hoc essay test.
    # All existing entrances must show the same catalogue before activation.
    closure=verify_publication_closure(candidate, predecessor=predecessor, lane='staging')
    return {'status':'SOURCE_BOUND_STAGE_CANDIDATE_ACCEPTED_NOT_ACTIVATED',
            'source':receipt['predecessorReleaseID'],'candidate':receipt['releaseID'],
            'books':[(b['id'],len(b['orderedWorkIDs']),len(b['illustratedWorkIDs'])) for b in snap['books']],
            'delta':{'changed':len(receipt['changedPaths']),'added':len(receipt['addedPaths'])},
            'privateRightsPreserved':True,'originalAuthoredTemplatesPreserved':len(stage_names),
            'mandatoryPublicationClosure':closure['status']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--predecessor',type=Path,default=Path(__file__).parent/'wlan-stage-v215-predecessor.json')
    a=p.parse_args()
    print(json.dumps(verify(a.source,a.candidate,json.loads(a.receipt.read_text()),json.loads(a.predecessor.read_text())),indent=2))
