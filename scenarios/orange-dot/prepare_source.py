#!/usr/bin/env python3
"""Private author-source selection from the writer's own normalized Facebook export.
This never copies the full archive, nor approves public distribution.
"""
from pathlib import Path
from hashlib import sha256
import json,subprocess,shutil
ROOT=Path(__file__).resolve().parent
ARCHIVE=Path('/Volumes/DockerDisk/midi2-gpu-fabric/corpora/facebook-benedikteickhoff')
CORPUS=ARCHIVE/'normalized/posts-by-day.json'
FIRST=Path('/Users/benedikteickhoff/Developer/fountain-publishing/fountain.coach/scenarios/reading-first-20261101/solstice-first-reading-manifest.json')
SELECTION=[
(1364,'Solstice','opening'),(1361,'The Raft','ember'),
(1352,'Am Rand des Feldes','boundary'),(1346,'Die Butterbrotdose','carried warmth'),
(1332,'Hotel Paris / 1947','rest'),(1298,'Wardrobe + Casting Spec','state change'),
(1291,'Fog Stage / Observer Seat','vigilance'),(1229,'Burning Down the House','continuity'),
(1209,'First LO — R.','contact'),(1175,'The Vigilance Regulator','contact regulation'),
(1168,'I Keep Moving','living signal'),(1113,'Drift Notes','pilot light'),
(951,'On Natural Intermittency','intermittency'),(890,'Nothing Is Solved in This Way','nonintervention'),
(873,'Bee — Love, Grounding, Movement','unforced relation'),
(804,'A Score Before Production','score translation'),
(791,'N. — First Platform','embodied score'),(776,'N. — Drawing to Stay','warm attention'),
(696,'N. — Care and Capture','critical care'),
(597,'N. — The Orange Frame','doubt'),(534,'N. — Schnippel','color as impulse'),
(463,'Domestic Geometry My Ass','liberation of mark'),(410,'Bee — The Interval','open encounter'),
]
posts=[p for d in json.load(open(CORPUS))['days'] for p in d['posts']]
lookup={p['sourceIndex']:p for p in posts}
firstEntries=json.load(open(FIRST))['entries']
firstByDigest={e['textSha256'].removeprefix('sha256:'):e for e in firstEntries}
entries=[]
for index,title,theme in SELECTION:
 p=lookup[index];day=p['day'];raw=p['text'];textsha=sha256(raw.encode('utf-8')).hexdigest()
 slug=''.join(c.lower() if c.isascii() and c.isalnum() else '-' for c in title).strip('-');slug='-'.join(filter(None,slug.split('-')))
 identity='orange-dot--'+day+'-'+slug
 path=ROOT/'source-text'/f'{identity}.txt'
 path.write_text(raw,encoding='utf8')
 imgs=[]
 for i,rel in enumerate(p.get('imageURIs') or [],1):
  source=ARCHIVE/rel;assert source.is_file(),source
  sha=sha256(source.read_bytes()).hexdigest();name=f'{identity}-{i:02d}-{sha[:14]}{source.suffix.lower()}'
  dest=ROOT/'source-images'/name
  if not dest.exists():shutil.copy2(source,dest)
  assert sha256(dest.read_bytes()).hexdigest()==sha
  proc=subprocess.run(['sips','-g','pixelWidth','-g','pixelHeight',str(dest)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
  parts=[line.strip() for line in proc.stdout.splitlines()]
  width=int(next(x.split(':')[1] for x in parts if x.startswith('pixelWidth:')))
  height=int(next(x.split(':')[1] for x in parts if x.startswith('pixelHeight:')))
  imgs.append({'sourceImageFile':name,'sha256':sha,'width':width,'height':height,'ordinal':i})
 old=firstByDigest.get(textsha)
 entries.append({'id':identity,'date':day,'title':title,'theme':theme,'sourceIndex':index,
                 'sourceTextFile':'source-text/'+path.name,'textSha256':textsha,'textLength':len(raw),
                 'originalImageCount':len(imgs),'images':imgs,
                 'firstReadingsOverlap':{'title':old['title'],'href':old['href'],
                  'image':old['image']} if old else None})
assert len(entries)==23 and len({e['id'] for e in entries})==23
assert [e['sourceIndex'] for e in entries]==[x[0] for x in SELECTION]
assert [e['date'] for e in entries]==sorted(e['date'] for e in entries)
assert {e['sourceIndex'] for e in entries if e['firstReadingsOverlap']}=={1168,804}
review={'schema':'fountain.press.orange-dot.author-selection.v1','sourceAuthority':'Benedikt Eickhoff Facebook export, locally owned, September 2026',
'corpusStart':'2025-12-21','corpusEnd':'2026-09-19','totalArchivePostsInRange':690,
'editorialDecision':'23 source-authentic posts; no claim that unselected material is irrelevant; original entire source texts and all original associated images retained for each selected entry',
'editorialAxes':['orange signal','carried warmth','vigilance and self-regulation','intermittent contact','translation into Teatro Score','N. and Bee: the autonomous mark and interval'],
'preexistingFirstReadingsWorks':['Integration (2025-12-23): cited without text duplication','I Keep Moving (2026-01-23): deliberate reappearance','A Score Before Production (2026-05-01): deliberate reappearance'],
'rightsBoundary':'Private author-controlled WLAN stage only; no public release or automatic social distribution',
'entries':entries}
(ROOT/'selection.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('SOURCE_SELECTED',len(entries),'original_images',sum(len(e['images']) for e in entries),
      'deliberate_reprises',sum(bool(e['firstReadingsOverlap']) for e in entries))
