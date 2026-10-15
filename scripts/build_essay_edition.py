#!/usr/bin/env python3
"""Source-bound Fountain Coach essays projected through the accepted Linotype book."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import hashlib,json,re,subprocess,argparse

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
ESSAYS=SITE/"essays"
ORDER=["teatro-an-unfinished-composition","semantic-compilation-the-archive-is-not-the-edition","reframe-and-the-business-value-of-the-estate"]
LABELS=["THE CONDITION","THE EDITION","THE ESTATE"]
RUNTIME=["book.css","book-boot.js","reading-layout-policy.js","linotype-engine.js","mobile-page-navigation.js","mobile-page-navigation.css","book.js"]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def grab(pattern,raw,required=True):
 m=re.search(pattern,raw,re.S)
 if required and not m:raise ValueError("Missing published essay structure: "+pattern)
 return m
class Text(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.parts=[];self.feed(s)
 def handle_data(self,s):self.parts.append(s)
 def get(self):return "".join(self.parts)
def text(s):return Text(s).get()
def main(owner):
 template=(owner/"editions/first-reading/index.html").read_text()
 assets=owner/"assets"
 entries=[];chapters=[]
 for n,(slug,label) in enumerate(zip(ORDER,LABELS),1):
  src=SITE/"essays"/slug/"index.html"; raw=src.read_bytes(); s=raw.decode()
  article=grab(r'<article class="essay-article">(.*?)</article>',s).group(1)
  head=grab(r'<header class="essay-header">(.*?)</header>',article).group(1)
  prose=grab(r'<div class="essay-prose">(.*?)</div>',article).group(1)
  title=grab(r'<h1>(.*?)</h1>',head).group(1)
  lead=grab(r'<p class="lead">(.*?)</p>',head).group(1)
  hero=grab(r'<figure\b[^>]*>.*?</figure>',head).group()
  body_figures=re.findall(r'<figure\b[^>]*>.*?</figure>',prose,re.S)
  assert len(re.findall(r'<p\b[^>]*>',prose))>=20,(slug,"incomplete prose")
  images=[]
  def relocate(match):
   image=match.group(1)
   if not image.startswith("assets/") or ".." in Path(image).parts:raise ValueError("Unauthorized image path "+image)
   p=src.parent/image
   if not p.is_file():raise ValueError("Missing original image "+str(p))
   images.append(dict(path=image,sha256=sha(p.read_bytes())))
   return 'src="/essays/'+slug+'/'+image+'"'
  def fig(f):return re.sub(r'src="([^"]+)"',relocate,f)
  uid="work-"+slug
  label_html=escape(label)
  start='<section class="book-chapter" id="'+uid+'" data-book-chapter="'+slug+'" data-chapter-number="'+str(n)+'"><header class="book-chapter-heading"><p class="book-ordinal">'+label_html+'<span>'+f"{n:02d} / 03"+'</span></p><h2>'+title+'</h2><p class="book-chapter-meta">ESSAY · BENEDIKT EICKHOFF</p></header><div class="book-opener-art">'+fig(hero)+'</div></section>'
  fragments=re.split(r'<figure\b[^>]*>.*?</figure>',prose,flags=re.S)
  parts=[start]
  boundary=grab(r'<aside class="essay-boundary"[^>]*>.*?</aside>',article,False)
  for i,fragment in enumerate(fragments):
   if i==0:fragment='<p class="essay-lead">'+lead+'</p>'+fragment
   note=''
   if i==len(fragments)-1:
    note=(boundary.group() if boundary else "")+'<p class="book-source-note">COMPLETE ORIGINAL ESSAY · <a href="https://fountain.coach/essays/'+slug+'/" aria-label="Open original essay">PUBLISHED SOURCE ↗</a></p>'
   parts.append('<section class="book-chapter-text"><article class="book-prose">'+fragment+'</article>'+note+'</section>')
   if i<len(body_figures):
    parts.append('<section class="book-art-leaf" aria-label="Original essay illustration">'+fig(body_figures[i])+'</section>')
  paragraphs=[text('<p>'+lead+'</p>')]+[text(x) for x in re.findall(r'<p\b[^>]*>.*?</p>',prose,re.S)]
  headings=[text(x) for x in re.findall(r'<h2\b[^>]*>.*?</h2>',prose,re.S)]
  entries.append(dict(id=slug,title=text(title),sourcePath=f"essays/{slug}/index.html",sourceSHA256=sha(raw),
   publishedSource="https://fountain.coach/essays/"+slug+"/",originalParagraphs=len(paragraphs),
   paragraphsSHA256=sha(json.dumps(paragraphs,ensure_ascii=False).encode()),sectionHeadings=headings,
   originalFigures=len(images),images=images))
  assert len(images)==len(body_figures)+1
  chapters.append("\n".join(parts))
 pre=template[:template.index('<div id="book-flow"')]
 post=template[template.index('  <aside id="book-page-atlas"'):]
 cover='''<section class="book-cover" id="book-cover"><div class="book-cover-top"><span>FOUNTAIN COACH</span><span>THE ESSAY EDITION</span></div><div class="book-cover-center"><span class="cover-mark" aria-hidden="true">✳</span><p class="book-imprint">WRITING · PERFORMANCE · PUBLISHING</p><h1>Essays<span>.</span></h1><p class="book-cover-subtitle">Fountain Coach</p></div><p class="book-cover-foot">THREE COMPLETE ESSAYS · FIVE ORIGINAL PLATES<br>BENEDIKT EICKHOFF<br><a data-estate-id="first-reading" href="https://works.benedikt-eickhoff.de/solstice/editions/first-reading/">First Reading →</a> · <a data-estate-id="teatro" href="https://teatro.fountain.coach/">Teatro →</a></p></section>'''
 ending='''<section class="book-end" id="book-end"><span class="cover-mark" aria-hidden="true">✳</span><p>END OF ESSAYS</p><h2>The writing continues.</h2><a href="/essays/">Original publications →</a></section>'''
 html=pre+'<div id="book-flow" class="book-flow">\n'+cover+'\n'+'\n'.join(chapters)+'\n'+ending+'\n</div>\n</div>\n</div>\n'+post
 toc='<nav aria-label="Chapters"><ol class="book-toc-list"><li><a href="#book-cover" data-book-toc-target="cover"><span class="toc-number">·</span><span class="toc-title">Cover</span></a></li>'
 for n,e in enumerate(entries,1):
  toc+='<li><a href="#work-'+e["id"]+'" data-book-toc-target="'+e["id"]+'"><span class="toc-number">'+f"{n:02d}"+'</span><span class="toc-title">'+escape(e["title"])+'</span><span class="toc-voice">'+escape(LABELS[n-1])+'</span></a></li>'
 toc+='</ol></nav>'
 html,replace=re.subn(r'<nav aria-label="Chapters"><ol class="book-toc-list">.*?</ol></nav>',lambda _:toc,html,flags=re.S)
 assert replace==1
 html=html.replace('First Reading — Solstice','Fountain Coach — Essays').replace('Solstice First Reading — an illustrated, thirty-work literary edition presented as a paginated reading experience.','Three complete essays by Benedikt Eickhoff, in the measured Linotype reader.')
 html=html.replace('id="book-pages" class="book-main" aria-label="First Reading, a literary edition"','id="book-pages" class="book-main" aria-label="Fountain Coach essay edition"')
 html=html.replace('href="../../assets/','href="/assets/linotype/').replace('src="../../assets/','src="/assets/linotype/')
 html=html.replace('href="../../" aria-label="Leave First Reading and return to Solstice"','href="/essays/" aria-label="Original Fountain Coach essay source"')
 html=html.replace('<span>Solstice</span></a>','<span>Source Essays</span></a>').replace('<span>FIRST READING</span></div>','<span>FOUNTAIN COACH · ESSAYS</span></div>')
 html=html.replace('<a href="proof/" class="book-proof-link" aria-label="Open the accepted Fountain Press page proof">Druckfahne ↗</a>','')
 # Fixed authorial typography: never project the inherited appearance control.
 appearance_button='<button type="button" id="book-type-button" aria-label="Reading appearance" aria-haspopup="dialog">Aa</button>'
 assert html.count(appearance_button)==1
 html=html.replace('    '+appearance_button+'\n','')
 html=html.replace('<small>SOLSTICE · FIRST READING</small>','<small>FOUNTAIN COACH · ESSAYS</small>').replace('id="book-location" aria-live="off">First Reading','id="book-location" aria-live="off">Essays')
 html=html.replace('All source images are shown in full.','All five original plates are shown in full.')
 html=html.replace('<link rel="canonical" href="https://works.benedikt-eickhoff.de/solstice/editions/first-reading/">','<link rel="canonical" href="https://fountain.coach/">')
 html=html.replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,nofollow">')
 legal='<nav class="book-legal" aria-label="Legal and company information"><a data-legal-role="company-status" href="https://status.fountain.coach/">Company status &amp; transparency</a> · <a href="https://governance.fountain.coach/legal/">Legal notices</a> · <a href="https://governance.fountain.coach/privacy/">Privacy</a></nav>'
 html=html.replace('<div class="book-progress"><span id="book-location"',legal+'<div class="book-progress"><span id="book-location"')
 html=html.replace('<link rel="stylesheet" href="/assets/linotype/book.css">','<link rel="stylesheet" href="/assets/linotype/book.css">\n<link rel="stylesheet" href="/assets/linotype/essays.css">')
 runtime=SITE/"assets/linotype";runtime.mkdir(exist_ok=True)
 stamps=[]
 for file in RUNTIME:
  data=(assets/file).read_bytes();modified=data
  if file=="linotype-engine.js":
   modified=modified.replace(b'if(this.pages<30)',b'if(this.pages<7)')
   # An essay can contain text, then a full-page original plate, then more
   # prose. The original engine checked each text section against *all* leaves
   # of the chapter, so grouped sections must be compared as one manuscript.
   old=b"""    for(const original of this.source.querySelectorAll(".book-chapter-text")){
      const node=original.previousElementSibling;
      let opener=node;
      while(opener&&!opener.classList.contains("book-chapter"))opener=opener.previousElementSibling;
      const id=opener?.id;
      if(!id)throw Error("Unbound manuscript passage");
      const expected=[...original.querySelectorAll(".book-prose p")].map(x=>x.textContent).join("");
      const received=this.leaves.filter(x=>x.type==="text"&&x.sourceId===id)
        .flatMap(x=>[...x.area.querySelectorAll("p:not(.book-source-note)")])
        .map(x=>x.textContent).join("");
      if(expected!==received)throw Error("Source text lost in pagination: "+id);
    }"""
   new=b"""    const expectedBySource=new Map();
    for(const original of this.source.querySelectorAll(".book-chapter-text")){
      let opener=original.previousElementSibling;
      while(opener&&!opener.classList.contains("book-chapter"))opener=opener.previousElementSibling;
      const id=opener?.id;
      if(!id)throw Error("Unbound manuscript passage");
      const expected=[...original.querySelectorAll(".book-prose p")].map(x=>x.textContent).join("");
      expectedBySource.set(id,(expectedBySource.get(id)||"")+expected);
    }
    for(const [id,expected] of expectedBySource){
      const received=this.leaves.filter(x=>x.type==="text"&&x.sourceId===id)
        .flatMap(x=>[...x.area.querySelectorAll("p:not(.book-source-note)")])
        .map(x=>x.textContent).join("");
      if(expected!==received)throw Error("Source text lost in pagination: "+id);
    }"""
   if old not in modified:raise ValueError("Upstream Linotype text-fidelity block changed")
   modified=modified.replace(old,new)
   modified=modified.replace(b'SOLSTICE \\xc2\\xb7 FIRST READING',b'FOUNTAIN COACH \\xc2\\xb7 ESSAYS')
   modified=modified.replace(b'FIRST READING',b'ESSAYS')
   old_folio="'<span>SOLSTICE · ESSAYS</span><span>'".encode()
   new_folio="'<span>'+(document.body.dataset.editionId==='essays-teatro-an-unfinished-composition'?'FIRST READINGS · AN UNFINISHED COMPOSITION':'FOUNTAIN COACH · ESSAYS')+'</span><span>'".encode()
   assert modified.count(old_folio)==1
   modified=modified.replace(old_folio,new_folio)
   old_running='const sheet=this.leaf(type,id,id==="book-vergil"?"VERGIL · PROLOGUE":"ESSAYS");'.encode()
   new_running='const sheet=this.leaf(type,id,id==="book-vergil"?"VERGIL · PROLOGUE":(document.body.dataset.editionId==="essays-teatro-an-unfinished-composition"?"FIRST READINGS":"ESSAYS"));'.encode()
   assert modified.count(old_running)==1
   modified=modified.replace(old_running,new_running)
   # Plate/opener and continuation leaves also need the admitted edition
   # identity; replacing only the first sheet leaves an "ESSAYS" header.
   old_default='leaf(type,sectionId,chapterLabel="ESSAYS"){'.encode()
   new_default='leaf(type,sectionId,chapterLabel=(document.body.dataset.editionId==="essays-teatro-an-unfinished-composition"?"FIRST READINGS":"ESSAYS")){'.encode()
   assert modified.count(old_default)==1
   modified=modified.replace(old_default,new_default)
   old_continuation='page=this.leaf(type,id,isVergil?"VERGIL · PROLOGUE":"ESSAYS");'.encode()
   new_continuation='page=this.leaf(type,id,isVergil?"VERGIL · PROLOGUE":(document.body.dataset.editionId==="essays-teatro-an-unfinished-composition"?"FIRST READINGS":"ESSAYS"));'.encode()
   assert modified.count(old_continuation)==1
   modified=modified.replace(old_continuation,new_continuation)
  elif file=="book.js":
   modified=modified.replace(b'solstice.first-reading.linotype.v2',b'fountain.essays.linotype.v1')
   modified=modified.replace(b'First Reading',b'Essays')
  (runtime/file).write_bytes(modified)
  stamps.append(dict(file=file,upstreamSHA256=sha(data),projectedSHA256=sha(modified)))
 (runtime/"essays.css").write_text('''.book-cover h1{font-size:clamp(4rem,9vw,6.1rem)}
.book-prose h2{font:400 1.25em/1.24 Georgia,serif;margin:1em 0 .6em}
.book-prose .essay-lead{font-style:italic}
.book-prose .source-line{font-size:.75em}
.book-chapter-text .essay-boundary{border-top:1px solid var(--book-rule);font:12px/1.5 Georgia,serif;padding:1em 0}
.book-pagination{grid-template-columns:minmax(70px,1fr) minmax(0,400px) minmax(70px,1fr);grid-template-rows:minmax(30px,1fr) auto;row-gap:2px}
.book-legal{grid-column:1/-1;grid-row:2;justify-self:center;align-self:center;max-width:100%;text-align:center;font:9px/1.35 ui-monospace,Menlo,monospace;color:var(--book-muted)}
.book-legal a{text-decoration:none;border-bottom:1px solid var(--book-rule)}
.book-progress{grid-column:2;grid-row:1}#book-prev{grid-column:1;grid-row:1}#book-next{grid-column:3;grid-row:1}
body.book-app.reader-ready .book-pagination{height:90px;min-height:90px}
body.book-app.reader-ready .book-main{height:calc(100svh - 152px)}
body.book-app.reader-ready .book-viewport{height:calc(100svh - 160px)}
@media(max-width:680px){.book-pagination{grid-template-columns:55px minmax(0,1fr) 55px;gap:2px 5px}
.book-progress{grid-column:2;grid-row:1}.book-legal{grid-column:1/-1;grid-row:2;font-size:8px;line-height:1.35}
#book-next{grid-column:3;grid-row:1}
body.book-app.reader-ready .book-pagination{height:94px;min-height:94px}
body.book-app.reader-ready .book-main{height:calc(100svh - 148px)}
body.book-app.reader-ready .book-viewport{height:calc(100svh - 156px)}}
''')
 (SITE/"index.html").write_text(html)
 version=dict(schema="fountain.press.linotype.essay-edition.v1",title="Fountain Coach — Essays",
  sourceRepository="Fountain-Coach/fountain.coach",sourceRoot="site/essays/",
  upstreamLinotypeRepository="Fountain-Coach/solstice.fountain.coach",
  upstreamRevision=subprocess.check_output(["git","-C",str(owner.parent),"rev-parse","HEAD"],text=True).strip(),
  runtime=stamps,essays=entries,readingOrder=ORDER,
  originalFigures=sum(e["originalFigures"] for e in entries),
  originalParagraphs=sum(e["originalParagraphs"] for e in entries),
  status="source-candidate-not-publicly-deployed",reader="measured-first-reading-linotype-engine")
 assert version["originalFigures"]==5
 (ESSAYS/"edition-manifest.json").write_text(json.dumps(version,indent=2,ensure_ascii=False)+"\n")
 print("ESSAYS_LINOTYPE_COMPOSED",len(entries),"essays",version["originalParagraphs"],"paragraphs",version["originalFigures"],"figures",version["upstreamRevision"])

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--linotype-source",type=Path,required=True);args=p.parse_args()
 main(args.linotype_source.resolve())
