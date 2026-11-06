#!/usr/bin/env python3
"""Project complete Kino story (two source-reconstructed historic auditions + verified Csound A/B) into existing Press Reader v167."""
import argparse, hashlib, html, json, re, shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'a-sound-must-earn-its-place-v4.md'
HISTORY=Path('/Users/benedikteickhoff/Developer/teatro-kino-interlude-20261105/site/interludes/kino/assets/editorial-history')
IMAGE_MANIFEST=HERE/'assets/illustration-source.json'
BASE_INDEX='33812b6e908e2f9ca26c9f09e7da7a5074bf20b5ccf43d19df41514b5cc30360'
BASE_APP='46876ca7b54c5f26df2372f1ec037871e61f6773a406ff41ec32a634337b7831'
VOLUME='essay--a-sound-must-earn-its-place'
PAT=r'<template data-reader-volume="essay--a-sound-must-earn-its-place"[^>]*>.*?</template>'
def sha(x):return hashlib.sha256(x).hexdigest()
def digest(p):return sha(Path(p).read_bytes())
def inline(s):
    v=html.escape(s,quote=True)
    v=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',v)
    return re.sub(r'\*(.+?)\*',r'<em>\1</em>',v)
def audio(name,prefix,labels,descriptions):
    return '<figure class="frame-press-av frame-sound-craft-ab" data-press-media="'+name+'" data-source-block="a-sound-must-earn-its-place.'+prefix+'" data-keep-with-anchor="previous" style="max-width:100%;box-sizing:border-box;padding:.45em .25em;display:grid;gap:.35em;">'+''.join('<div class="frame-sound-craft-take"><p data-source-block="a-sound-must-earn-its-place.'+prefix+'.'+str(i)+'" style="font-size:.82em;margin:0 0 .18em;">'+html.escape(label)+'</p><satzfunk-player compact data-sound-track-id="'+nameid+'" label="'+html.escape(label)+'" style="display:block;width:100%;min-height:44px;"></satzfunk-player></div>' for i,(nameid,label) in enumerate(zip(labels,descriptions),1))+'<p class="press-av-status" role="status" style="font-size:.75em;min-height:0;margin:0;"></p><figcaption>'+('Two source-authentic editorial reconstructions, not recordings of original browser sessions.' if prefix=='history' else 'One original score · two native Csound patches · 16 seconds each · editorial audition, not approved masters.')+'</figcaption></figure>'
def project(old_idx,old_app):
    old_idx=Path(old_idx).read_bytes();old_app=Path(old_app).read_bytes()
    if sha(old_idx)!=BASE_INDEX or sha(old_app)!=BASE_APP:raise ValueError('Wrong v167 original Reader baseline')
    old=old_idx.decode();prior=re.findall(PAT,old,re.S)
    if len(prior)!=1:raise ValueError('Not exactly one original editorial template')
    previous=prior[0]
    figures={}
    for kind in ('architectural-plate','night-photograph'):
        mats=re.findall(r'<figure[^>]*data-source-illustration-id="'+kind+r'"[^>]*>.*?</figure>',previous,re.S)
        if len(mats)!=1:raise ValueError('Source-bound original figure missing '+kind)
        figures[kind]=mats[0]
    manuscript=SOURCE.read_text(); blocks=[x.strip() for x in manuscript.split('\n\n') if x.strip()]
    assert blocks[0]=='# A Sound Must Earn Its Place'
    assert blocks[1].startswith('*On Kino International') and blocks[2].startswith('**Status:**')
    markers={
      '[KINO-ILLUSTRATION:architectural-plate]':'architectural-plate',
      '[KINO-ILLUSTRATION:night-photograph]':'night-photograph',
      '[KINO-HISTORICAL-COMPARISON:groove-memory]':'historical',
      '[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]':'controlled'
    }
    for k in markers:
        if manuscript.count(k)!=1:raise ValueError('Missing or repeated source mark '+k)
    units=[];p=0;positions={}
    for block in [blocks[1]]+blocks[3:]:
        if block in markers:
            kind=markers[block];positions[kind]=p
            if kind in figures:
                figure=figures[kind]
                figure=re.sub(r'data-inline-after-paragraph="\d+"','data-inline-after-paragraph="'+str(p)+'"',figure,count=1)
                units.append(figure)
            elif kind=='historical':
                units.append(audio('kino-history-reconstruction','history',('kino-history-groove','kino-history-memory'),('I — Original bass and groove materials','II — Revised cinematic memory materials')))
            else:
                units.append(audio('satzfunk-csound-kino-a-b','audio-ab',('a-literal','b-directed'),('A — Literal Csound pass','B — Directed Csound pass')))
            continue
        p+=1
        if block.startswith('## '): raise ValueError('No editorial section inflation')
        plain=block.replace('**','').replace('*','')
        units.append('<p data-source-block="a-sound-must-earn-its-place.p'+str(p)+'" data-source-from="0" data-source-to="'+str(len(plain))+'">'+inline(block)+'</p>')
    if p<20 or positions['architectural-plate']>=positions['historical'] or positions['historical']>=positions['night-photograph'] or positions['night-photograph']>=positions['controlled']:raise ValueError('Source flow incorrect')
    tpl='<template data-reader-volume="'+VOLUME+'" data-editorial-state="proof-revision" data-source-sha256="'+sha(SOURCE.read_bytes())+'"><div class="book-flow" data-min-leaves="1"><section class="book-chapter" id="work-a-sound-must-earn-its-place"><div class="book-chapter-heading"><h2 data-source-block="a-sound-must-earn-its-place.title">A Sound Must Earn Its Place</h2></div></section><section class="book-chapter-text"><article class="book-prose"><p class="frame-edition-imprint" data-source-block="editorial.proof.status">Editorial proof · Four source-bound Csound auditions · Unpublished</p>'+''.join(units)+'</article></section></div></template>'
    idx=old.replace(previous,tpl,1)
    assert idx.replace(tpl,previous,1)==old and idx.count('data-reader-volume="'+VOLUME+'"')==1
    assert tpl.count('<satzfunk-player compact')==4 and tpl.count('data-source-illustration-id=')==2
    app=old_app.decode()
    old_cb='     soundCraftPromise.then(edition=>{'
    if app.count(old_cb)!=1:raise ValueError('Existing Satzfunk binding changed')
    app=app.replace(old_cb,"     (p.dataset.soundTrackId.startsWith('kino-history-')?soundHistoryPromise:soundCraftPromise).then(edition=>{",1)
    hook="const governanceEdition=JSON.parse(document.getElementById('governance-edition-manifest')?.textContent||'null');"
    if app.count(hook)!=1:raise ValueError('Existing app not recognized')
    history_promise='''const soundHistoryPromise=fetch('/estate/media/kino/history/edition.json',{cache:'no-store'})
 .then(r=>{if(!r.ok)throw Error('Kino history recordings unavailable');return r.json()})
 .then(m=>{
   if(m.schema!=='satzfunk.recorded-essay-rehearsal.v1'||m.tracks?.length!==2||
     m.tracks.some(t=>!/^kino-history-(groove|memory)$/.test(t.id)||
       !/^[a-f0-9]{64}$/.test(t.mediaSHA256)||
       !/^[a-f0-9]{64}$/.test(t.sourceSHA256)||t.duration!==16||
       t.publicReleaseAuthorized!==false||t.privateRehearsalAuthorized!==true))
     throw Error('Unverified Kino source reconstruction');
   return m;
 });
'''
    app=app.replace(hook,history_promise+hook,1)
    result={'index':idx.encode(),'app':app.encode(),'positions':positions,'paragraphs':p,'sourceSHA256':sha(SOURCE.read_bytes())}
    return result

def build(index,app,out):
    r=project(index,app);out=Path(out);(out/'estate/assets/linotype').mkdir(parents=True,exist_ok=True)
    (out/'estate/index.html').write_bytes(r['index'])
    (out/'estate/assets/linotype/reading-first-app.js').write_bytes(r['app'])
    src=json.loads((HISTORY/'sources.json').read_text())
    assert src['originalCapture'] is False and src['editorialAudioReconstructionOnly'] is True
    target=out/'estate/media/kino/history';target.mkdir(parents=True,exist_ok=True)
    shutil.copy2(HISTORY/'sources.json',target/'sources.json')
    tracks=[]
    for x in src['files']:
        name=x['id'];f=HISTORY/(name+'.m4a')
        assert digest(f)==x['mediaSHA256']
        shutil.copy2(f,target/f.name)
        tracks.append({'id':name,'title':name,'media':'/media/kino/history/'+f.name,'mediaSHA256':x['mediaSHA256'],'sourceSHA256':digest(HISTORY/'sources.json'),'duration':16,'publicReleaseAuthorized':False,'privateRehearsalAuthorized':True})
    edition={'schema':'satzfunk.recorded-essay-rehearsal.v1','sourceOwner':'Fountain-Coach/teatro.fountain.coach','playerOwner':'Fountain-Coach/SatzfunkPlayer','status':'private-WLAN-original-csound-stem-reconstructions','mediaBasePrefix':'/estate/','originalBrowserCaptures':False,'sourceStemsCsoundRendered':True,'tracks':tracks}
    (target/'edition.json').write_text(json.dumps(edition,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    manifest={'schema':'fountain.press.kino-complete-four-auditions.v1','sourceOwner':'Fountain-Coach/fountain.coach','sourceSHA256':r['sourceSHA256'],'sourceParagraphs':r['paragraphs'],'sourcePositions':r['positions'],'indexSHA256':sha(r['index']),'appSHA256':sha(r['app']),'historicRecordingCount':2,'controlledCsoundRecordingCount':2,'originalArtworkPreserved':True,'originalReaderRuntimePreserved':True,'privateWLANOnly':True,'publicRightsGranted':False,'historicalCaptureClaimed':False,'files':{x.relative_to(out).as_posix():digest(x) for x in out.rglob('*') if x.is_file()}}
    receipt=out/'estate/evidence/press-kino-complete-v168.json';receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'candidate':str(out),'editorialSHA':r['sourceSHA256'],'indices':r['positions'],'sourceParagraphs':r['paragraphs'],'indexSHA':manifest['indexSHA256'],'appSHA':manifest['appSHA256'],'files':manifest['files'],'receiptSHA':digest(receipt)},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('index','app','out'):p.add_argument('--'+n,required=True)
    a=p.parse_args();build(a.index,a.app,a.out)
