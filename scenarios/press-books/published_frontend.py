#!/usr/bin/env python3
"""Source-locked CMS-like Linotype frontend projection; never deploys.

Reads exact current published files plus one admitted predecessor record, and
produces only changed static routes/modules. A catalogue is the published view;
templates remain authored text, and EstatePublisher alone performs releases.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
APP_PATTERN=re.compile(r'/estate/assets/linotype/reading-first-app\.[a-f0-9]{64}\.js')
GALLERY_PATTERN=re.compile(r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)',re.S)
TEMPLATE_PATTERN=re.compile(r'<template\s+data-reader-volume="([^"]+)"[^>]*>(.*?)</template>',re.S)
JS_OLD_START='const labels=new Map('
JS_OLD_END='let addendumReturnVolume='
JS_OLD_HEADER='   book.append(header);'


def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def content_addressed_shell_path(css_bytes: bytes) -> str:
    """The navigation stylesheet's URL changes whenever its bytes change."""
    return 'estate/assets/linotype/reading-first-shell.' + digest(css_bytes) + '.css'

def project_shell_stylesheet(html: str, asset_path: str) -> str:
    """Fail closed rather than retaining stale unversioned CSS in a public book."""
    return replace_once(html,
        'href="/estate/assets/linotype/reading-first-shell.css"',
        'href="/' + asset_path + '"', 'source-bound navigation stylesheet')

def json_bytes(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')

def read_pinned(root:Path,path:str,admission:dict)->bytes:
    base=root.resolve(strict=True)
    candidate=(base/path).resolve()
    if not candidate.is_relative_to(base) or not candidate.is_file():
        raise ValueError('Input path outside source: '+path)
    data=candidate.read_bytes()
    expected=admission['sourceDigestSHA256'][path]
    if digest(data)!=expected:
        raise ValueError('REFUSED source SHA drift '+path+': expected '+expected+' saw '+digest(data))
    return data

class TemplateStructure(HTMLParser):
    def __init__(self,source:str):
        self.names=[];self.nesting=[];self.depth=0
        super().__init__(convert_charrefs=True);self.feed(source)
    def handle_starttag(self,tag,attrs):
        if tag!='template':return
        value=dict(attrs).get('data-reader-volume')
        if value is not None:
            self.names.append(value)
            if self.depth:self.nesting.append(value)
        self.depth+=1
    def handle_endtag(self,tag):
        if tag=='template':self.depth-=1

def source_templates(source:str)->tuple[list[str],dict[str,str]]:
    structure=TemplateStructure(source)
    matches=TEMPLATE_PATTERN.findall(source)
    names=[m[0] for m in matches]
    if structure.depth!=0 or structure.nesting or names!=structure.names or len(names)!=len(set(names)):
        raise ValueError('REFUSED source template nesting, duplicate identity or malformed HTML')
    return names,{key:markup for key,markup in matches}

def parse_gallery(source):
    matches=GALLERY_PATTERN.findall(source)
    if len(matches)!=1:raise ValueError('Exactly one authored gallery declaration required')
    data=json.loads(matches[0][1])
    if data.get('schema')!='fountain.press.bookshelf-gallery.v1':
        raise ValueError('Unexpected authored gallery schema')
    return data['collections']

def parse_source_exclusion_ids(app:str,name:str)->list[str]:
    match=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*new Set\(\[([^\]]*)\]\)',app,re.S)
    if not match:raise ValueError('Source editorial exclusion declaration missing: '+name)
    return re.findall(r"'([^']+)'",match[1])

def build_snapshot(page:str,app:str,catalog:dict,admission:dict):
    names,markup=source_templates(page)
    galleries=parse_gallery(page)
    source_books=catalog.get('books')
    if not isinstance(source_books,list) or not source_books:
        raise ValueError('No admitted source books')
    if len(source_books)!=len({b['id'] for b in source_books}) or set(galleries)!={b['id'] for b in source_books}:
        raise ValueError('Publication book/gallery identities disagree')
    if catalog.get('currentReleaseID')!=admission['publicReleaseID']:
        raise ValueError('REFUSED publication release/predecessor drift')
    archived=parse_source_exclusion_ids(app,'archivedEssays')
    histories=parse_source_exclusion_ids(app,'implementationStories')
    role_source={**{x:'historical-public' for x in histories},**{x:'archived-public' for x in archived}}
    if role_source!=admission['sourceUnlistedWorkRoles']:
        raise ValueError('REFUSED archived/historical work authorial classification drift')
    published=[];all_active=set();proem_ids=[];all_historical=set()
    for book in source_books:
        if book.get('publicReleaseAuthorized') is not True or book.get('stageOnly') is not False or book.get('publicationState')!='public-production':
            # This is a PUBLIC source build: hiding a private book's card is not
            # sufficient when its full source template still ships in HTML.
            raise ValueError('REFUSED private/unreleased book in public source: '+book['id'])
        identifier=book['id'];gallery=galleries[identifier];illustrated=[item['id'] for item in gallery]
        if len(set(illustrated))!=len(illustrated):raise ValueError('Duplicate gallery work: '+identifier)
        listed=book.get('orderedWorkIDs')
        if not listed:
            # Legacy source migration: infer the original chapter prefix once,
            # then publish the complete order into the machine catalogue.
            if not illustrated or '--' not in illustrated[0]:
                raise ValueError('Unordered unillustrated book needs explicit source admission: '+identifier)
            prefix=illustrated[0].split('--',1)[0]+'--'
            listed=[name for name in names if name.startswith(prefix)]
            if illustrated!=listed[len(listed)-len(illustrated):]:
                raise ValueError('Original book chapter order is not a verified gallery suffix: '+identifier)
        if len(listed)!=len(set(listed)) or not listed or not set(listed)<=set(markup):
            raise ValueError('Missing/duplicate authored source work: '+identifier)
        if set(listed)&all_active:raise ValueError('Duplicate active work across collections')
        all_active.update(listed)
        previous=-1
        for work in illustrated:
            if work not in listed or listed.index(work)<=previous:
                raise ValueError('Illustration order is not subsequence of contents: '+identifier)
            previous=listed.index(work)
        # Source-proven role classification, not an implicit active shelf entry.
        not_listed=[]
        if identifier=='essays':
            unlisted=[name for name in names if name.startswith('essay--') and name not in listed]
            if set(unlisted)!=set(role_source):raise ValueError('Unexpected omitted original essay')
            not_listed=[{'id':name,'status':role_source[name]} for name in unlisted]
            all_historical.update(unlisted)
        for work in listed:
            role='data-editorial-role="proem"'
            if role in markup[work]:
                proem_ids.append(work)
                if 'data-source-block' not in markup[work]:
                    raise ValueError('Original editorial proem lacks source address: '+work)
        presentation=admission.get('existingPresentation',{}).get(identifier,{})
        published.append({
            'id':identifier,'title':book['title'],'canonicalURL':book['canonicalURL'],
            'directURLPath':book['directURLPath'],'publicationState':book['publicationState'],
            'publicReleaseAuthorized':True,'stageOnly':False,'sourceRevision':book['sourceRevision'],
            'orderedWorkIDs':listed,'illustratedWorkIDs':illustrated,
            'unlistedSourceWorks':not_listed,
            **({'subtitle':presentation['subtitle']} if presentation.get('subtitle') else {}),
            **({'contentsCaption':presentation['contentsCaption']} if presentation.get('contentsCaption') else {}),
        })
    if not published:raise ValueError('No eligible publicly released collections')
    if len(all_active)!=sum(len(b['orderedWorkIDs']) for b in published):raise ValueError('Published membership duplicates')
    expected=admission['requiredEditorialProemCounts']
    for book in published:
        if book['id'] in expected:
            actual=sum(w in proem_ids for w in book['orderedWorkIDs'])
            if actual!=expected[book['id']]:raise ValueError('Editorial proem source drift: '+book['id'])
    if set(proem_ids)&all_historical:raise ValueError('Historical-only prose in current editorial proems')
    publication={
        'schema':'fountain.press.publication-snapshot.v1',
        'sourceOwner':catalog['sourceOwner'],'sourceGitRevision':catalog['sourceGitRevision'],
        'publicPredecessorReleaseID':catalog['currentReleaseID'],
        'books':published,'requiredEditorialProemWorkIDs':proem_ids,
    }
    return publication


def replace_once(text,old,new,label):
    if text.count(old)!=1:raise ValueError('REFUSED expected single source anchor '+label+': '+str(text.count(old)))
    return text.replace(old,new,1)

def add_bookshelf_vertical_cues(app: str) -> str:
    """Decorate the EXISTING two vertical scrollports, never make new pages.

    The visual cue is an accessible control that scrolls only its own region.
    Its state comes from measured overflow, not historical book counts.
    """
    if 'reader-shelf-scroll-cue' in app:
        raise ValueError('REFUSED duplicate Bookshelf continuation cue injection')
    anchor = "   vertical.append(tiles);gallery.append(vertical);pair.append(gallery);book.append(pair);scroll.append(book);"
    insertion = """   for(const [region,panel] of [[list,statement],[vertical,gallery]]){
    // iPad Safari hides overlay scrollbars. Show a typographic, functional
    // continuation cue only while this SAME authored collection has overflow.
    const cue=document.createElement('button');cue.type='button';
    cue.className='reader-shelf-scroll-cue';cue.dataset.more='false';cue.disabled=true;
    cue.setAttribute('aria-label','Scroll further down '+labels.get(id)+' '+panel.dataset.presentation);
    const caption=document.createElement('span');caption.textContent='More below';
    const mark=document.createElement('span');mark.className='reader-shelf-scroll-cue-mark';
    mark.setAttribute('aria-hidden','true');mark.textContent='↓';cue.append(caption,mark);
    cue.addEventListener('click',()=>{
     region.scrollBy({top:Math.max(80,region.clientHeight*.75),behavior:'smooth'});
    });
    const update=()=>{
     const more=region.clientHeight>0&&region.scrollHeight-region.scrollTop-region.clientHeight>5;
     cue.dataset.more=String(more);cue.disabled=!more;
     cue.setAttribute('aria-hidden',String(!more));
    };
    region.addEventListener('scroll',update,{passive:true});
    if(typeof ResizeObserver!=='undefined'){
     const observer=new ResizeObserver(update);observer.observe(region);
     if(region.firstElementChild)observer.observe(region.firstElementChild);
    }
    panel.append(cue);
    requestAnimationFrame(()=>requestAnimationFrame(update));
   }
"""
    return replace_once(app,anchor,anchor+"\n"+insertion,"two independent Bookshelf vertical continuation cues")


def add_latest_essay_link(app: str) -> str:
    """Expose the last source-admitted Essays work without changing book order.

    The latest placement is derived from the normalized collection snapshot,
    not an independently authored title or a duplicate work entry.
    """
    if 'reader-latest-essay-link' in app:
        raise ValueError('REFUSED duplicate latest-essay link injection')
    anchor = "   header.append(direct);\n   if(bookById.get(id).subtitle){"
    addition = """   header.append(direct);
   if(id==='essays' && contents[id]?.length){
    const newestID=contents[id][contents[id].length-1];
    if(!bookById.get(id).orderedWorkIDs.includes(newestID))
     throw new Error('Latest essay is not an admitted work');
    const link=document.createElement('a');link.className='reader-latest-essay-link';
    link.href='#/read/'+encodeURIComponent(newestID);
    link.dataset.readerTarget=newestID;
    link.setAttribute('aria-label','Read latest essay: '+labels.get(newestID));
    const prefix=document.createElement('span');prefix.className='reader-latest-essay-prefix';
    prefix.textContent='Latest essay';
    const title=document.createElement('span');title.textContent=labels.get(newestID);
    const mark=document.createElement('span');mark.setAttribute('aria-hidden','true');
    mark.textContent='→';
    link.append(prefix,title,mark);header.append(link);
   }
   if(bookById.get(id).subtitle){"""
    return replace_once(app, anchor, addition, 'latest Essays work pointer')


def compile_app(app:str)->str:
    source=(HERE/'reader-publication-state.js.inc').read_text()
    start=app.find(JS_OLD_START);end=app.find(JS_OLD_END,start)
    if start<0 or end<=start:raise ValueError('REFUSED Reader state source drift')
    if 'const collectionOrder=' not in app[start:end] or 'const galleries=' not in app[start:end]:
        raise ValueError('REFUSED Reader state source shape drift')
    app=app[:start]+source+'\n'+app[end:]
    app=replace_once(app,"let activeCollection='essays';",'let activeCollection=collectionOrder[0];','active collection')
    app=replace_once(app,"const selectedWork={essays:null,'first-readings':null,'orange-dot':null};",
        'const selectedWork=Object.fromEntries(collectionOrder.map(id=>[id,null]));','selected work identities')
    app=replace_once(app,"const compactPresentation={essays:'contents','first-readings':'contents','orange-dot':'contents'};",
        "const compactPresentation=Object.fromEntries(collectionOrder.map(id=>[id,'contents']));",'presentation identities')
    app=replace_once(app,"if(pathname.includes('/collections/first-readings/'))return 'first-readings';\n if(pathname.includes('/collections/orange-dot/'))return 'orange-dot';",
        "for(const book of books){if(pathname.includes('/collections/'+book.id+'/'))return book.id;}", 'legacy collection routes')
    app=replace_once(app,"   if(id!=='essays'){\n     const subtitle=document.createElement('p');\n     subtitle.textContent=id==='orange-dot'?'Solstice · original post sequence':'Reading 01 · First Reading';\n     header.append(subtitle);\n   }",
        "   if(bookById.get(id).subtitle){\n    const subtitle=document.createElement('p');\n    subtitle.textContent=bookById.get(id).subtitle;header.append(subtitle);\n   }",'source-owned subtitle')
    app=replace_once(app,"  if(volume==='first-readings'){\n   const caption=document.createElement('p');caption.className='reader-contents-reading';\n   caption.textContent='Reading 01 — First Reading';outer.append(caption);\n  }",
        "  if(bookById.get(volume)?.contentsCaption){\n   const caption=document.createElement('p');caption.className='reader-contents-reading';\n   caption.textContent=bookById.get(volume).contentsCaption;outer.append(caption);\n  }", 'contents caption')
    app=replace_once(app,"    image.loading=id==='essays'?'eager':'lazy';image.decoding='async';",
        "    image.loading=id===collectionOrder[0]?'eager':'lazy';image.decoding='async';",'lazy images')
    app=replace_once(app,JS_OLD_HEADER,'   header.append(makeLeafNavigation(id));\n'+JS_OLD_HEADER,'folio navigation')
    anchor='function renderSurface(){'
    navi='''function makeLeafNavigation(id){
 const n=collectionOrder.indexOf(id),nav=document.createElement('nav');
 nav.className='reader-shelf-leaf-navigation';nav.setAttribute('aria-label','Browse published collections');
 const previousID=collectionOrder[n-1],nextID=collectionOrder[n+1];
 const create=(target,isNext)=>{
  const button=document.createElement('button');button.type='button';
  button.className='reader-shelf-leaf-'+(isNext?'next':'previous');
  button.setAttribute('aria-label',(isNext?'Next':'Previous')+' published book: '+labels.get(target));
  const mark=document.createElement('span');mark.className='reader-shelf-leaf-mark';
  mark.setAttribute('aria-hidden','true');mark.textContent=isNext?'→':'←';
  const name=document.createElement('span');name.textContent=labels.get(target);
  if(isNext)button.append(name,mark);else button.append(mark,name);
  button.addEventListener('click',()=>shelfSnapTo(target,{smooth:true}));
  return button;
 };
 if(previousID)nav.append(create(previousID,false));
 const count=document.createElement('span');count.className='reader-shelf-leaf-position';
 count.textContent=String(n+1).padStart(2,'0')+' / '+String(collectionOrder.length).padStart(2,'0');
 count.setAttribute('aria-label','Collection '+(n+1)+' of '+collectionOrder.length);
 nav.append(count);
 if(nextID)nav.append(create(nextID,true));
 return nav;
}
'''
    app=replace_once(app,anchor,navi+anchor,'leaf navigation function')
    app=add_bookshelf_vertical_cues(app)
    app=add_latest_essay_link(app)
    return app

STYLE='''
/* Published Bookshelf: an editorial running navigation, derived from book order.
   The original collection spread, page measure and vertical scrollports remain. */
.reader-collection-heading{
 display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:start;
 column-gap:clamp(10px,2vw,25px);
}
.reader-collection-heading h2{grid-column:1;grid-row:1}
.reader-collection-heading .reader-book-direct-link{grid-column:1;grid-row:2;justify-self:start}
.reader-collection-heading > p{grid-column:1;grid-row:3}
.reader-shelf-leaf-navigation{
 grid-column:2;grid-row:1/span 3;display:flex;align-items:baseline;
 justify-content:flex-end;gap:clamp(8px,1.4vw,17px);min-height:27px;
 font:normal clamp(.72rem,1.1vw,.84rem)/1.5 "Iowan Old Style",Palatino,Georgia,serif;
 font-variant-numeric:tabular-nums;letter-spacing:.02em;color:var(--muted);
}
.reader-shelf-leaf-navigation button{
 appearance:none;border:0;border-bottom:1px solid var(--line);border-radius:0;
 background:none;color:var(--ink);font:inherit;cursor:pointer;display:inline-flex;
 align-items:baseline;gap:6px;padding:1px 1px 3px;white-space:nowrap;
}
.reader-shelf-leaf-navigation button:hover{border-color:var(--ink)}
.reader-shelf-leaf-navigation button:focus-visible{outline:2px solid var(--focus);outline-offset:3px}
.reader-shelf-leaf-mark{font-size:.91em;line-height:1;vertical-align:baseline}
.reader-shelf-leaf-position{white-space:nowrap;font-variant-numeric:tabular-nums}
@media(max-width:700px){
 .reader-collection-heading{grid-template-columns:minmax(0,1fr);row-gap:0}
 .reader-shelf-leaf-navigation{grid-column:1;grid-row:4;justify-content:space-between;
   width:100%;margin:4px 0 0;font-size:.74rem;min-height:25px}
 .reader-shelf-leaf-navigation button{max-width:43%;white-space:normal;text-align:start}
}
/* Safari overlay scrollbars disappear while resting. Keep a quietly printed,
   measured continuation action OUTSIDE each independently scrollable column. */
.reader-shelf-scroll-cue{
 display:inline-flex;align-items:baseline;justify-content:flex-end;gap:7px;
 align-self:flex-end;flex:0 0 22px;min-height:22px;max-height:22px;
 appearance:none;border:0;border-bottom:1px solid var(--line);
 padding:3px 2px 1px;margin:0;background:none;color:var(--muted);
 font:normal clamp(.72rem,1vw,.82rem)/1.3 "Iowan Old Style",Palatino,Georgia,serif;
 letter-spacing:.02em;cursor:pointer;
}
.reader-shelf-scroll-cue[data-more="false"]{visibility:hidden}
.reader-shelf-scroll-cue:hover{color:var(--ink);border-color:var(--ink)}
.reader-shelf-scroll-cue:focus-visible{outline:2px solid var(--focus);outline-offset:2px;color:var(--ink)}
.reader-shelf-scroll-cue-mark{font:normal 1em/1 "Iowan Old Style",Palatino,Georgia,serif}
/* Latest admitted essay: a compact editorial signpost, not a duplicate item.
   The Contents and Gallery remain unchanged and source-ordered. */
.reader-latest-essay-link{
 grid-column:1;grid-row:3;display:inline-flex;align-items:baseline;flex-wrap:wrap;
 gap:4px 9px;justify-self:start;text-decoration:none;color:var(--ink);
 font:normal clamp(.77rem,1.2vw,.93rem)/1.4 "Iowan Old Style",Palatino,Georgia,serif;
 margin:5px 0 2px;border-bottom:1px solid var(--line);padding-bottom:3px;
}
.reader-latest-essay-link:hover{border-bottom-color:var(--ink)}
.reader-latest-essay-link:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.reader-latest-essay-prefix{color:var(--muted)}
.reader-collection-heading:has(.reader-latest-essay-link)>p{grid-row:4}
@media print{.reader-shelf-leaf-navigation,.reader-shelf-scroll-cue{display:none!important}}
@media(forced-colors:active){.reader-shelf-leaf-navigation button,.reader-shelf-scroll-cue{border-color:CanvasText}}
'''

def build(src:Path,out:Path,admission:dict,receipt:Path):
    if out.exists():raise ValueError('REFUSED immutable candidate path already exists')
    inputs={path:read_pinned(src,path,admission) for path in admission['sourceDigestSHA256']}
    page=inputs['estate/index.html'].decode();app_path=next(path for path in inputs if APP_PATTERN.fullmatch('/'+path))
    app=inputs[app_path].decode();css=inputs['estate/assets/linotype/reading-first-shell.css'].decode()
    catalog=json.loads(inputs['estate/books/catalog.json'])
    if inputs['index.html']!=inputs['estate/index.html']:
        raise ValueError('Existing root and estate are not the same published edition')
    published_app_paths=APP_PATTERN.findall(page)
    if set(published_app_paths)!={'/'+app_path}:
        raise ValueError('REFUSED unexpected source Reader module')
    gallery=parse_gallery(page)
    for b in catalog['books']:
        book_path=f"estate/books/{b['id']}/index.html"
        book=inputs[book_path].decode()
        if set(APP_PATTERN.findall(book))!={'/'+app_path} or parse_gallery(book)!=gallery:
            raise ValueError('REFUSED stale source direct book shell: '+b['id'])
        if 'data-initial-volume="'+b['id']+'"' not in book:
            raise ValueError('REFUSED direct book identity mismatch: '+b['id'])
    snapshot=build_snapshot(page,app,catalog,admission)
    newapp=compile_app(app).encode()
    new_app='/estate/assets/linotype/reading-first-app.'+digest(newapp)+'.js'
    new_css=(css+STYLE).encode()
    new_css_path=content_addressed_shell_path(new_css)
    insertion='<script type="application/json" id="reader-publication-data">'+json.dumps(snapshot,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>'
    def project(html):
        html=replace_once(html,app_path,new_app.lstrip('/'),'Reader module')
        html=project_shell_stylesheet(html,new_css_path)
        return replace_once(html,GALLERY_PATTERN.search(html)[0],GALLERY_PATTERN.search(html)[0]+'\n'+insertion,'publication snapshot')
    out.mkdir(parents=True)
    files={}
    def emit(path,data):
        p=out/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);files[path]=digest(data)
    root=project(page)
    emit('index.html',root.encode())
    emit('estate/index.html',root.encode())
    # The supported legacy Bookshelf URL must not silently render an obsolete edition.
    emit('estate/read/library/index.html',root.encode())
    for b in catalog['books']:
        item=inputs[f"estate/books/{b['id']}/index.html"].decode()
        item=project(item)
        emit(f"estate/books/{b['id']}/index.html",item.encode())
    # The historical Essays index is a supported Bookshelf entrance, not a second
    # independently maintained collection. Reuse the exact composed Essays book.
    emit('estate/essays/index.html', (out/'estate/books/essays/index.html').read_bytes())
    for output_book in catalog['books']:
        published=next((b for b in snapshot['books'] if b['id']==output_book['id']),None)
        if published:
            output_book['orderedWorkIDs']=published['orderedWorkIDs']
            output_book['illustratedWorkIDs']=published['illustratedWorkIDs']
            output_book['unlistedSourceWorks']=published['unlistedSourceWorks']
    catalog['publishedCollectionOrder']=[book['id'] for book in snapshot['books']]
    catalog['publicationSnapshotSchema']=snapshot['schema']
    catalog['publicationSnapshotSourceReleaseID']=snapshot['publicPredecessorReleaseID']
    emit('estate/books/catalog.json',json_bytes(catalog))
    emit(new_app.lstrip('/'),newapp)
    emit(new_css_path,new_css)
    # Fail before writing an admission receipt if ANY current collection route,
    # catalogue, Reader, social projection or legacy entrance diverges.
    from publication_closure import verify as verify_publication_closure
    verify_publication_closure(out, predecessor=src, lane='public')
    result={'schema':'fountain.press.frontend-candidate-receipt.v1','status':'development-candidate-not-published',
        'sourceReleaseID':admission['publicReleaseID'],'snapshotBooks':[
          {'id':b['id'],'works':len(b['orderedWorkIDs']),'illustrations':len(b['illustratedWorkIDs'])} for b in snapshot['books']],
        'sourceSHA256':{k:digest(v) for k,v in inputs.items()},'snapshotSHA256':digest(json_bytes(snapshot)),
        'changedFilesSHA256':files}
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_bytes(json_bytes(result))
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--receipt',required=True,type=Path)
    p.add_argument('--predecessor',type=Path,default=HERE/'published-frontend-predecessor.json')
    args=p.parse_args()
    if args.receipt.exists():raise SystemExit('REFUSED receipt exists')
    admission=json.loads(args.predecessor.read_text())
    if admission.get('schema')!='fountain.press.frontend-predecessor.v1':raise SystemExit('Wrong admission schema')
    try: result=build(args.input,args.output,admission,args.receipt)
    except (ValueError,KeyError,IndexError,TypeError,FileNotFoundError) as exc:raise SystemExit(str(exc))
    print(json.dumps({'status':result['status'],'books':result['snapshotBooks'],'files':len(result['changedFilesSHA256'])},indent=2))

if __name__=='__main__':main()
