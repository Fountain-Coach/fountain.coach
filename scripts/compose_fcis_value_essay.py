#!/usr/bin/env python3
"""Compose one FCIS value essay into the existing Fountain Press Reader.

Creates only an overlay from the exact immutable v195 WLAN predecessor.
Never deploys, overwrites the predecessor, invents illustrations, or edits
original reader templates.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

VOL = "essay--the-value-of-what-we-can-prove"
TITLE = "The Value of What We Can Prove"
OLD_APP_SHA = "2b3ed3e08c2ff459b7371e790e10720c711e78842797ff92dc1f6518bebe4458"
ROOT_NAME = "estate/index.html"
APP_NAME = "estate/assets/linotype/reading-first-app." + OLD_APP_SHA + ".js"

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def one_replace(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise ValueError("Source composition seam changed: " + label + " (" + str(n) + ")")
    return s.replace(old, new, 1)

def plain(text):
    # The cover uses visual <br> breaks, not semantic word joins.
    text = re.sub(r"<br\\s*/?>", " ", text, flags=re.I)
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()

def source_blocks(source):
    title = re.search(r"<h1>(.*?)</h1>", source, re.S)
    if not title or plain(title.group(1)) != TITLE:
        raise ValueError("Unexpected manuscript title")
    sections = []
    for match in re.finditer(r'<section\s+id="([a-z-]+)"[^>]*>(.*?)</section>', source, re.S):
        section_id, body = match.groups()
        heading_match = re.search(r"<h2[^>]*>(.*?)</h2>", body, re.S)
        if not heading_match:
            raise ValueError("Missing authored heading " + section_id)
        ps = []
        for p in re.finditer(r"<p([^>]*)>(.*?)</p>", body, re.S):
            attributes, inner = p.groups()
            ps.append((inner.strip(), "proem" in attributes))
        sections.append((section_id, plain(heading_match.group(1)), ps))
    if len(sections) != 6:
        raise ValueError("Expected exactly six authored essay sections")
    if sum(bool(proem) for _, _, ps in sections for _, proem in ps) != 1:
        raise ValueError("Exactly one authored proem required")
    note = re.search(r'<aside class="source-note"[^>]*>(.*?)</aside>', source, re.S)
    if not note:
        raise ValueError("Missing source basis")
    note_text = plain(note.group(1))
    return sections, note_text

def source_span(content, block_id, cls=None, role=None):
    body = plain(content)
    if not body:
        raise ValueError("Empty source paragraph " + block_id)
    attrs = (' class="' + cls + '"' if cls else '')
    attrs += (' data-editorial-role="' + role + '"' if role else '')
    attrs += ' data-source-block="' + block_id + '"'
    attrs += ' data-source-from="0" data-source-to="' + str(len(body)) + '"'
    return '<p' + attrs + '>' + content + '</p>', {"block":block_id,"text":body,"length":len(body),"sha256":sha(body.encode())}

def make_volume(sections, note_text):
    parts = ['<div class="book-flow" data-min-leaves="1"><section class="book-chapter" id="work-the-value-of-what-we-can-prove"><div class="book-chapter-heading"><h2 data-source-block="fcis-value.title">' + TITLE + '</h2></div></section><section class="book-chapter-text"><article class="book-prose">']
    blocks = []
    for section_id, heading, paragraphs in sections:
        block = 'fcis-value.' + section_id + '.heading'
        h, record = source_span(html.escape(heading),block,cls='frame-subheading')
        parts.append(h);blocks.append(record)
        for i, (raw, proem) in enumerate(paragraphs,1):
            block = 'fcis-value.' + section_id + '.p' + str(i)
            p, record = source_span(raw,block,cls='frame-lead' if proem else None,role='proem' if proem else None)
            parts.append(p);blocks.append(record)
    p, record = source_span(html.escape(note_text),'fcis-value.source-note',cls='frame-reference-intro')
    parts.append(p);blocks.append(record)
    parts.append('</article></section></div>')
    return ''.join(parts), blocks

def replace_meta(s,name,content):
    pattern = r'<meta (?:property|name)="' + re.escape(name) + r'" content="[^"]*"\s*/?>'
    if re.search(pattern,s):
        return re.sub(pattern,lambda _: '<meta property="' + name + '" content="' + html.escape(content,quote=True) + '"/>',s,count=1)
    return s

def decorate_direct(root,volume,title,description):
    s = root
    s = one_replace(s,'data-initial-volume="library"','data-initial-volume="' + volume + '"','direct starting volume')
    s = re.sub(r'<title>[^<]*</title>',lambda _: '<title>' + html.escape(title) + ' — Fountain Press (WLAN review)</title>',s,count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*"\s*/?>','<link rel="canonical" href="https://fountain.coach/estate/read/' + volume + '/"/>',s,count=1)
    for k,v in [('og:title',title+' — Fountain Press'),('og:description',description),('og:url','https://fountain.coach/estate/read/'+volume+'/')]:
        s=replace_meta(s,k,v)
    # Original Bookshelf's artwork is not the source artwork of this text-only essay.
    s=re.sub(r'<meta (?:name|property)="(?:og:image(?::[^"]*)?|twitter:image(?::[^"]*)?)" content="[^"]*"\s*/?>','',s)
    s=one_replace(s,'</head>','<meta name="robots" content="noindex,nofollow"/>\n</head>','stage-only robots')
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--revision',required=True)
    args=ap.parse_args()
    if args.output.exists():raise RuntimeError("No overwrite of candidate overlay")
    b=args.baseline
    root_bytes=(b/ROOT_NAME).read_bytes()
    js_bytes=(b/APP_NAME).read_bytes()
    if sha(js_bytes)!=OLD_APP_SHA:raise ValueError("Existing Reader JS drift")
    original=root_bytes.decode()
    if original.count('<template data-reader-volume=')!=75:raise ValueError("Unexpected base Reader inventory")
    source_bytes=args.source.read_bytes()
    sections,note=source_blocks(source_bytes.decode())
    volume,blocks=make_volume(sections,note)
    root=one_replace(original,
        '<script type="application/json" id="reader-gallery-data">',
        '<template data-reader-volume="' + VOL + '">' + volume + '</template>\n<script type="application/json" id="reader-gallery-data">',
        'new essay volume')
    root=one_replace(root,'Five essays · current edition','Essays · current selection','obsolete count')
    js=js_bytes.decode()
    js=one_replace(js,'if(essaySequence.length!==6||solsticeSequence.length!==32)',
      'if(essaySequence.length!==7||solsticeSequence.length!==32)','current essay inventory')
    js=one_replace(js,
        'const galleryData=JSON.parse(document.getElementById(\'reader-gallery-data\')?.textContent||\'null\');',
        "const illustratedEssaySequence=essaySequence.filter(id=>id!=='" + VOL + "');\n" +
        "const galleryData=JSON.parse(document.getElementById('reader-gallery-data')?.textContent||'null');",
        'text-only essay has no source illustration')
    js=one_replace(js,'i<essaySequence.length?essaySequence[i]:kinoPublicVolume',
                  'i<illustratedEssaySequence.length?illustratedEssaySequence[i]:kinoPublicVolume','gallery/contents source parity')
    js_bytes=js.encode(); newsha=sha(js_bytes)
    new_app='estate/assets/linotype/reading-first-app.'+newsha+'.js'
    root=one_replace(root,APP_NAME.replace('estate/','/estate/'),
                 '/'+new_app,'Reader asset digest route')
    title = TITLE
    description='An evidence-bound essay on FCIS, canonical skills, intellectual property, commercial value and the possibility of a first paying customer.'
    direct=decorate_direct(root,VOL,title,description)
    # Existing reader supports /estate/read/essays as the collection, not another edition engine.
    collection=decorate_direct(root,'essays','Essays','Fountain Press Essays — source-addressed writing, including The Value of What We Can Prove.')
    published = {
      ROOT_NAME:root.encode(),new_app:js_bytes,
      'estate/read/'+VOL+'/index.html':direct.encode(),
      'estate/read/essays/index.html':collection.encode(),
    }
    manifest={
        'schema':'fountain.press.source-bound-essay-review.v1',
        'workID':VOL,'title':TITLE,'author':'Benedikt Eickhoff',
        'publisher':'Fountain Coach','date':'2026-11-12',
        'sourceOwner':'Fountain-Coach/fountain.coach','sourceRevision':args.revision,
        'sourcePath':'site/essays/the-value-of-what-we-can-prove/source.html',
        'sourceSHA256':sha(source_bytes),
        'readerArtifactPath':'/estate/read/'+VOL+'/',
        'collectionPath':'/estate/read/essays/',
        'publicReleaseAuthorized':False,
        'stagingOnly':True,
        'originalImages':0,
        'proemCount':1,
        'sections':[{'id':a,'heading':b,'paragraphCount':len(c)} for a,b,c in sections],
        'sourceBlocks':blocks,
    }
    published['estate/read/'+VOL+'/edition-manifest.json']=(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode()
    for rel,contents in published.items():
        dest=args.output/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(contents)
    digest_map={rel:sha(contents) for rel,contents in sorted(published.items())}
    (args.output/'build-receipt.json').write_text(json.dumps({
      'sourceSHA256':sha(source_bytes),'sourceGitRevision':args.revision,
      'baselineIndexSHA256':sha(root_bytes),'baselineAppSHA256':OLD_APP_SHA,
      'newAppSHA256':newsha,'changes':digest_map,
      'unchangedGallerySource':True,'newOriginalImages':0,
      'directEssayRoute':'/estate/read/'+VOL+'/',
      'collectionRoute':'/estate/read/essays/',
      'stagingOnly':True,'publicDelivery':False
    },indent=2)+'\n')
    print('COMPOSED',len(sections),'sections',len(blocks),'source blocks','files',len(published))
    print('NEW_APP_SHA',newsha)
    print('SOURCE_SHA',sha(source_bytes))
    print('OUTPUT',args.output)
if __name__=='__main__':main()
