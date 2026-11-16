#!/usr/bin/env python3
"""Recompose admitted direct books from the current public Reader; no delivery effects."""
import argparse, hashlib, json, re, shutil
from pathlib import Path
from compose_direct_books import update_meta, make_social
SLUG='essay--a-better-ear-for-fountain-coach'
BASE='https://fountain.coach'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def gallery(s): return json.loads(re.search(r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',s,re.S)[1])['collections']
def verify(root,release):
 root=Path(root); s=(root/'index.html').read_text(); g=gallery(s); c=json.loads((root/'estate/books/catalog.json').read_text()); e=json.loads((root/f'estate/read/{SLUG}/edition-manifest.json').read_text())
 assert s==(root/'estate/index.html').read_text(), 'root parity'
 assert c['currentReleaseID']==release and c['latestAdmittedEssay']['workID']==SLUG, 'stale catalogue release/latest'
 assert c['currentEssaysFirstChapter']['id']==g['essays'][0]['id']==SLUG, 'first chapter drift'
 app=re.search(r'/estate/assets/linotype/reading-first-app\.[a-f0-9]+\.js',s)[0]
 for b in c['books']:
  page=(root/f"estate/books/{b['id']}/index.html").read_text()
  assert gallery(page)==g and app in page, 'stale direct book shell'
  assert b['firstIllustratedChapterID']==g[b['id']][0]['id'], 'book first art drift'
  assert sha(root/b['socialImagePath'].lstrip('/'))==b['socialImageSHA256'], 'social SHA drift'
  assert b['socialImageURL'] in page and b['firstChapterImageAlt'] in page, 'book social metadata drift'
  assert f'data-initial-volume="{b["id"]}"' in page
 assert e['hero']['sha256']==sha(root/f'estate/read/{SLUG}'/e['hero']['file'])
 assert e['publicSocialImage']['sha256']==sha(root/e['publicSocialImage']['url'].removeprefix(BASE+'/'))
 return {'releaseID':release,'collections':len(c['books']),'essayOrder':[x['id'] for x in g['essays']],'sharedReader':app,'checks':'passed'}
def compose(src,out,revision,release):
 src=Path(src); out=Path(out)
 assert not out.exists(), 'immutable output already exists'
 old=json.loads((src/'release-manifest.json').read_text())
 assert old['releaseID']=='fountain-press-better-ear-20261116-0175fc1-r2'
 shutil.copytree(src,out)
 s=(out/'estate/index.html').read_text(); g=gallery(s)
 c=json.loads((out/'estate/books/catalog.json').read_text()); e=json.loads((out/f'estate/read/{SLUG}/edition-manifest.json').read_text())
 first=g['essays'][0]; assert first['id']==SLUG
 art=out/first['src'].lstrip('/'); assert sha(art)==e['hero']['sha256']
 social=f'estate/assets/social/books/essays-better-ear-{revision[:8]}.jpg'
 social_sha=make_social(art,out/social)
 head,body=s.split('</head>',1)
 changed=[]
 for b in c['books']:
  col=b['id']; p=out/f'estate/books/{col}/index.html'; oldpage=p.read_text(); oldhead=oldpage.split('</head>',1)[0]
  # Preserve each book's authored identity and social policy; refresh the shared Reader head/assets and body.
  page=head+'</head>'+body
  oldmeta=re.findall(r'<(?:meta\b[^>]*(?:property="og:|name="twitter:|name="description"|name="robots")[^>]*|link rel="canonical"[^>]*)/?>',oldhead)
  page=re.sub(r'<meta\b[^>]*(?:property="og:|name="twitter:|name="description"|name="robots")[^>]*>\s*','',page)
  page=re.sub(r'<link rel="canonical"[^>]*>\s*','',page)
  page=re.sub(r'<script type="application/ld\+json">.*?</script>\s*','',page,flags=re.S)
  title=re.search(r'<title>.*?</title>',oldhead,re.S)[0]
  page=re.sub(r'<title>.*?</title>',lambda _:title,page,count=1,flags=re.S)
  ld=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',oldhead,re.S)[1])
  page=page.replace('</head>','\n'.join(oldmeta)+'\n</head>',1)
  if col=='essays':
   url=BASE+'/'+social
   for k,v in [('og:image',url),('og:image:secure_url',url),('og:image:alt',first['alt'])]: page=update_meta(page,'property',k,v)
   page=update_meta(page,'name','twitter:image',url)
   ld['image'].update(url=url,caption=first['alt'])
   ld['hasPart']=[{'@type':'CreativeWork','identifier':x['id'],'url':BASE+'/estate/read/'+x['id']+'/'} for x in g['essays']]
   b.update(firstIllustratedChapterID=SLUG,firstChapterOriginalImagePath=first['src'],firstChapterOriginalImageSHA256=sha(art),firstChapterImageAlt=first['alt'],socialImagePath='/'+social,socialImageURL=url,socialImageSHA256=social_sha,sourceIllustrationDeclaredSHA256=sha(art),sourceIllustrationProvenance='author-approved Better Ear hero',rightsProvenance='Author-approved essay and artwork, 16 November 2026',sourceRevision=e['sourceRevision'],orderedWorkIDs=[x['id'] for x in g['essays']])
  b['compositionRevision']=revision; b['releaseID']=release
  page=page.replace('</head>','<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False,separators=(',',':'))+'</script>\n</head>',1)
  page=page.replace('data-initial-volume="library"',f'data-initial-volume="{col}"',1)
  p.write_text(page); changed.append(str(p.relative_to(out)))
 c.update(currentReleaseID=release,sourceGitRevision=revision,publicPredecessor=old['releaseID'],publicationAuthority='Author-directed publication correction, 16 November 2026',latestAdmittedEssay={'workID':SLUG,'publicURL':e['publicRoute'],'publicationDate':e['approvedDate'],'releaseID':release,'sourceRevision':e['sourceRevision'],'sourceSHA256':e['sourceSHA256'],'heroSHA256':e['hero']['sha256'],'socialURL':e['publicSocialImage']['url'],'socialSHA256':e['publicSocialImage']['sha256'],'authorApproved':True},currentEssaysFirstChapter={'id':SLUG,'sourceRevision':e['sourceRevision'],'manuscriptSha256':e['sourceSHA256'],'heroSha256':e['hero']['sha256']})
 (out/'estate/books/catalog.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n'); changed+=['estate/books/catalog.json',social,'release-manifest.json']
 old.update(releaseID=release,previousReleaseID=old['releaseID'],sourceRevision=revision,modifiedPaths=changed,collectionParityCorrection=True)
 (out/'release-manifest.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(verify(out,release),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--output'); p.add_argument('--revision'); p.add_argument('--release',required=True); a=p.parse_args()
 if a.output: compose(a.source,a.output,a.revision,a.release)
 else: print(json.dumps(verify(a.source,a.release),indent=2))
