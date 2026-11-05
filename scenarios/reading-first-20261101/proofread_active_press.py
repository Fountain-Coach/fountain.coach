#!/usr/bin/env python3
"""Source-addressed whole-publication QA ledger. No automatic author prose edits."""
from __future__ import annotations
import json,re,hashlib,collections,urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=json.loads((ROOT/"fountain-press-all-publications-source-audit.json").read_text())
MANIFEST=json.loads((ROOT/"editorial-archive-decision.json").read_text())
routes=set((ROOT/"stage-v151-route-inventory.txt").read_text().splitlines())
works=SOURCE["works"]
gallery=json.loads(re.search(r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',
                         (ROOT/"stage-v151-before-archive.html").read_text(),re.S).group(1))
FIRST={x["id"]:x for x in gallery["collections"]["first-readings"]}
ACTIVE=["essay--what-makes-a-page-modern",
        "essay--reframe-and-the-business-value-of-the-estate",
        "essay--teatro-an-unfinished-composition",
        "essay--the-ear-that-learns","essay--the-door-is-a-score"]
FIRST_IDS=list(FIRST)
INDEX={w["id"]:w for w in works}
assert len(ACTIVE)==5 and len(FIRST_IDS)==30 and len(INDEX)==49
DECISION=set(["essay--to-read-is-not-to-remember"])
IMPLEMENTATION=set(["essay--the-composable-book","essay--semantic-compilation-the-archive-is-not-the-edition"])
def sha(s:str):return hashlib.sha256(s.encode()).hexdigest()
def words(s):return re.findall(r"[\w\u00C0-\u024F]+(?:[’'-][\w\u00C0-\u024F]+)*",s,re.UNICODE)
def normalize(s):return re.sub(r"\s+"," ",s).strip()
def audit(work):
    id=work["id"]
    role=("current-essay" if id in ACTIVE else
          "current-first-reading" if id in FIRST_IDS else
          "archive" if id in DECISION else
          "historical-implementation" if id in IMPLEMENTATION else
          "other-reader-surface")
    text=work["text"]
    para=work["paragraphs"]
    blocks=work["sourceBlocks"]
    issues=[]
    def mark(category,severity,message):
        issues.append({"area":category,"severity":severity,"finding":message})
    if id in ACTIVE+FIRST_IDS and para<2:
        mark("source","needs-review","Active work appears to have fewer than two source paragraphs")
    if id in ACTIVE+FIRST_IDS and len(work["proems"])!=1:
        mark("editorial","needs-review",f"Expected one source-separated editorial proem, saw {len(work['proems'])}")
    if id in ACTIVE+FIRST_IDS and len(text.strip())<300:
        mark("source","needs-review","Active source prose unusually short")
    if not blocks and role in ("current-essay","current-first-reading"):
        mark("identity","needs-review","No source-block identity in authored work")
    repeats=[v for v,n in collections.Counter(blocks).items() if n>1]
    if repeats:
        mark("identity","verify","Repeated source-block IDs within the same authored template: "+", ".join(repeats[:6]))
    for i in range(1,len(re.split(r"\n\n+",text))):
        pass
    paragraphs=[normalize(x) for x in re.split(r"\n\n+",text) if normalize(x)]
    consecutive=[i+1 for i in range(1,len(paragraphs)) if paragraphs[i]==paragraphs[i-1] and len(paragraphs[i])>55]
    if consecutive:
        mark("copy","needs-review","Adjacent identical authored paragraphs at index "+str(consecutive[:8]))
    if '\ufffd' in text:
        mark("copy","needs-fix","Replacement characters found in authored source")
    if re.search(r"\b[A-Za-z] {2,}[A-Za-z]\b",text):
        mark("copy","verify","Double spacing inside a word/sentence (may be intentional in poetry)")
    if re.search(r"\b(\w+)\s+\1\b",text,re.I):
        duplicates=sorted(set(m.group(0) for m in re.finditer(r"\b(\w+)\s+\1\b",text,re.I)))
        mark("copy","verify","Repeated adjacent word(s): "+", ".join(duplicates[:8]))
    if '\t' in text:mark("copy","verify","Tab characters in manuscript source")
    if re.search(r'\b(?:will soon|coming soon|currently testing|planned release|the next version)\b',text,re.I):
        mark("present tense","verify","Future product or test wording; check against author-evidenced present capability")
    missingAlt=[f.get("src") for f in work["imageInfo"] if f.get("src") and not f.get("alt")]
    if missingAlt:
        mark("accessibility","needs-review","Source images missing alternative text: "+", ".join(missingAlt[:4]))
    malformed=[f.get("src") for f in work["imageInfo"] if f.get("src") and (not f.get("width") or not f.get("height"))]
    if malformed:
        mark("layout","needs-review","Illustrations missing declared dimensions: "+", ".join(malformed[:5]))
    broken=[]
    for f in work["imageInfo"]:
        src=f.get("src")
        if src:
            url=urllib.parse.urlparse(src)
            if url.path.startswith("/estate/") and not (url.path.lstrip("/") in routes):
                broken.append(url.path)
    for link in work["links"]:
        url=urllib.parse.urlparse(link["href"] or "")
        if url.path.startswith("/estate/"):
            rel=url.path.lstrip("/")
            if rel not in routes and rel.rstrip("/")+"/index.html" not in routes:
                broken.append(url.path)
    if broken:
        mark("links/assets","needs-review","Missing referenced stage source route(s): "+", ".join(sorted(set(broken))[:7]))
    if id in FIRST_IDS:
        gal=FIRST[id]
        if not gal.get("src"):mark("illustration","needs-review","Gallery carries no source illustration")
        if work["figures"]==0:
            mark("illustration","editorial-review","Gallery artwork exists, but no source-bound image appears in the work's Reader body")
    if id=="essay--what-makes-a-page-modern":
        if len(work["imageInfo"])!=12:
            mark("illustration","needs-review","v151 reference figure identity changed")
        typeFig=[f for f in work["imageInfo"] if not f.get("src")]
        if len(typeFig)==2:
            mark("illustration","passed","Two source-bound, live typographic specimens have no img/alt by design")
    if id in DECISION:
        mark("publication-state","archived","Writer archived on 2026-11-05; keep source/direct route while excluding from current list")
    if id in IMPLEMENTATION:
        mark("publication-state","historical","Previous author decision excludes implementation story from current literary collection")
    if role=="current-essay":
        mark("content-review","not-verified","Factual claims, artistic decisions and full prose line edits require source-grounded editorial review")
    elif role=="current-first-reading":
        mark("content-review","not-verified","Full literary German/English proofreading and editorial voice require review beyond deterministic text scan")
    return {
      "id":id,"title":work["title"],"status":role,"sourceSHA256":sha(text),
      "sourceParagraphs":para,"wordCount":len(words(text)),"sourceAddressCount":len(blocks),
      "figures":work["figures"],"proems":len(work["proems"]),"abstracts":len(work["abstracts"]),
      "sourceImagesMissingAlt":len(missingAlt),"externalCitations":sum(
         urllib.parse.urlparse(x["href"] or "").scheme in ("https","http") for x in work["links"]),
      "findings":issues
    }
results=[audit(w) for w in works]
metrics={
 "templates":len(works),
 "currentEssays":sum(x["status"]=="current-essay" for x in results),
 "currentFirstReadings":sum(x["status"]=="current-first-reading" for x in results),
 "currentWords":sum(x["wordCount"] for x in results if x["status"] in ("current-essay","current-first-reading")),
 "firstReadingsWithNoEmbeddedImage":sum(x["status"]=="current-first-reading" and x["figures"]==0 for x in results),
 "sourceReferenceIssues":sum(any(f["severity"]=="needs-review" for f in x["findings"]) for x in results),
 "archiveCount":sum(x["status"]=="archive" for x in results),
 "archivedWork":MANIFEST["workID"],
}
obj={"schema":"fountain.press.per-publication-proofreading-ledger.v1",
     "authority":"v151 live stage source HTML, reviewed as exact static source snapshot",
     "method":"Whole inventory source/link/markup/spelling-pattern pass; no literary revision inferred",
     "limitations":"Lexical anomalies, factual/rights claims and source-to-gallery attribution still require independent editorial evidence",
     "metrics":metrics,"works":results}
(ROOT/"fountain-press-proofreading-ledger.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
lines=["# Fountain Press — source-led publication proofreading ledger",
"5 November 2026 · private staging v151 source, current edition after writer archive decision",
"",
"**Classification:** technical/source-bound pass and issue register, not a claim that every sentence received author approval.",
f"**Inventory:** {metrics['templates']} source-bearing Reader templates, including {metrics['currentEssays']} current essays, {metrics['currentFirstReadings']} current First Reading works and {metrics['archiveCount']} writer-archived essay. {metrics['currentWords']} words in current works (machine word tokenization).",
"",
"## Current essays",
""]
for category,title in [("current-essay","Current essays"),("current-first-reading","First Readings"),("archive","Archived work"),("historical-implementation","Historical implementation stories"),("other-reader-surface","Navigation, notes and other source projections")]:
    if category!="current-essay":lines+=["","## "+title,""]
    for x in results:
        if x["status"]!=category:continue
        severity=[f for f in x["findings"] if f["severity"] in ("needs-review","needs-fix","editorial-review")]
        special='; '.join(f['area']+': '+f['finding'] for f in severity[:3]) or 'No deterministic source/layout defects flagged'
        lines.append("- **"+(x["title"] or x["id"])+"** (`"+x["id"]+"`) — "+
           str(x["wordCount"])+" words, "+str(x["sourceParagraphs"])+" paragraphs, "+
           str(x["figures"])+" embedded figures; "+special+".")
lines+=["","## Material findings (do not silently rewrite source)","",
"- Historical *Did the Machine Actually Read the Book?* is withdrawn from current membership, with original source and standalone URL retained and the archived state marked in its Reader.",
"- Some First Reading works have gallery images but no source-bound figure in their actual work text. This is an editorial illustration-admission question, **not** permission to invent/insert an image into every text without inspecting original sources and rights.",
"- The mechanical scan cannot truthfully certify exact historical facts, current capability claims, translation, audio transcription or artistic spelling in mixed-language first-person work. These remain unresolved until reviewed against source/evidence; no prose was changed.",
"- Visual/WebKit/AX and audio evidence must be measured per released candidate; a source inventory is not that witness.",
"","## Reproduction",
"Source: `scenarios/reading-first-20261101/fountain-press-all-publications-source-audit.json`. Script: `proofread_active_press.py`. Machine-readable per-title ledger: `fountain-press-proofreading-ledger.json`.",""]
(ROOT/"fountain-press-proofreading-ledger.md").write_text("\n".join(lines))
print(json.dumps(metrics,ensure_ascii=False,indent=2))
for x in results:
    sev=[f for f in x["findings"] if f["severity"] in ("needs-review","needs-fix","editorial-review")]
    if sev:
        print("REVIEW",x["id"],":","; ".join(f["area"]+" "+f["finding"][:145] for f in sev[:3]))
