#!/usr/bin/env python3
"""Offline, fail-closed parity verification for the new Fountain Press frontend.

Checks compiled candidate bytes and metadata; does not assert staging/production
or replace actual WebKit/iPad acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from published_frontend import APP_PATTERN,parse_gallery,source_templates,digest
from publication_closure import verify as verify_publication_closure

SNAPSHOT=re.compile(r'<script type="application/json" id="reader-publication-data">(.*?)</script>',re.S)

def verify(root:Path, receipt:dict, predecessor:Path|None=None):
    expected=receipt['changedFilesSHA256']
    if receipt['status']!='development-candidate-not-published':
        raise ValueError('Not an unreleased source candidate')
    for name,sha in expected.items():
        path=root/name
        if not path.is_file() or digest(path.read_bytes())!=sha:
            raise ValueError('Candidate missing/modified source-bound file: '+name)
    root_page=(root/'index.html').read_text()
    for name in ('estate/index.html','estate/read/library/index.html'):
        if root_page!=(root/name).read_text():
            raise ValueError('Legacy/root Bookshelf publication mismatch: '+name)
    result=SNAPSHOT.findall(root_page)
    if len(result)!=1:raise ValueError('Missing or duplicate publication snapshot')
    snap=json.loads(result[0]);books=snap['books'];ids=[book['id'] for book in books]
    if snap['schema']!='fountain.press.publication-snapshot.v1' or not books or len(set(ids))!=len(ids):
        raise ValueError('Invalid frontend publication snapshot')
    catalog=json.loads((root/'estate/books/catalog.json').read_text())
    if catalog.get('publishedCollectionOrder')!=ids or catalog.get('publicationSnapshotSchema')!=snap['schema']:
        raise ValueError('Machine catalogue does not match published Bookshelf order')
    app=APP_PATTERN.findall(root_page)
    if len(app)!=1:raise ValueError('Source page must use one versioned Reader')
    apppath=root/app[0].lstrip('/')
    if not apppath.is_file() or digest(apppath.read_bytes())!=app[0].rsplit('.',2)[-2]:
        raise ValueError('Content-addressed Reader integrity failed')
    if 'reader-shelf-leaf-navigation' not in apppath.read_text():
        raise ValueError('Missing published frontend leaf navigation')
    galleries=parse_gallery(root_page)
    names,_=source_templates(root_page)
    live_work_ids=set()
    for book in books:
        source=next((b for b in catalog['books'] if b['id']==book['id']),None)
        if not source or source['orderedWorkIDs']!=book['orderedWorkIDs'] or source['illustratedWorkIDs']!=book['illustratedWorkIDs']:
            raise ValueError('Catalogue work/illustration order diverges: '+book['id'])
        if book['publicationState']!='public-production' or book['publicReleaseAuthorized'] is not True or book['stageOnly'] is not False:
            raise ValueError('Non-public book in public frontend')
        works=book['orderedWorkIDs'];gallery=book['illustratedWorkIDs']
        if len(set(works))!=len(works) or len(set(gallery))!=len(gallery) or not set(works)<=set(names):
            raise ValueError('Invalid work source identities: '+book['id'])
        if set(works)&live_work_ids:raise ValueError('Work appears in multiple books')
        live_work_ids.update(works)
        if [x['id'] for x in galleries[book['id']]]!=gallery:
            raise ValueError('Gallery source does not match published work: '+book['id'])
        if any(w not in works for w in gallery):raise ValueError('Illustration outside content')
        direct=(root/f"estate/books/{book['id']}/index.html").read_text()
        if SNAPSHOT.findall(direct)!=result or APP_PATTERN.findall(direct)!=app:
            raise ValueError('Direct-book frontend source drift: '+book['id'])
        if 'data-initial-volume="'+book['id']+'"' not in direct or book['canonicalURL'] not in direct:
            raise ValueError('Direct-book route/canonical identity drift: '+book['id'])
        for historical in book.get('unlistedSourceWorks',[]):
            if historical['id'] in live_work_ids or historical['id'] not in names or historical['status'] not in ('historical-public','archived-public'):
                raise ValueError('Historical source wrongly promoted or lost: '+historical['id'])
    if set(galleries)!=set(ids):raise ValueError('Source galleries differ from published books')
    if catalog.get('currentReleaseID')!=snap['publicPredecessorReleaseID'] or receipt['sourceReleaseID']!=snap['publicPredecessorReleaseID']:
        raise ValueError('Published predecessor identity is not retained')
    closure=verify_publication_closure(root, predecessor=predecessor, lane='public')
    return {'state':'CANDIDATE_VERIFIED_NOT_DEPLOYED','books':[(b['id'],len(b['orderedWorkIDs']),len(b['illustratedWorkIDs'])) for b in books],
            'rootEstateLegacyByteIdentical':True,'sourceReleaseID':receipt['sourceReleaseID'],
            'candidateReaderModule':app[0],'checkedFiles':len(expected),
            'mandatoryPublicationClosure':closure['status']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--receipt',required=True,type=Path)
    p.add_argument('--predecessor',required=True,type=Path,help='exact admitted source root for the immutable overlay')
    a=p.parse_args()
    print(json.dumps(verify(a.root,json.loads(a.receipt.read_text()),a.predecessor),indent=2))
