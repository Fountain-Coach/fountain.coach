"""Source-lock the exact v109 On Continuity text; no speech synthesis."""
import hashlib,html,re,sys
from pathlib import Path
source=Path(sys.argv[1]).read_bytes()
match=re.findall(r'<template data-reader-volume="continuity">(.*?)</template>',source.decode(),re.S)
assert len(match)==1
names=['continuity.title']+[f'continuity.p{i}' for i in range(1,10)]
texts=[]
for name in names:
    parts=re.findall(r'<(?:h2|p)[^>]*data-source-block="'+re.escape(name)+r'"[^>]*>(.*?)</(?:h2|p)>',match[0],re.S)
    assert len(parts)==1,name
    texts.append(html.unescape(re.sub(r'<[^>]+>','',parts[0])).strip())
text='\n\n'.join(texts)
assert text.startswith('On Continuity\n\n') and len(text)<4096
existing=Path(sys.argv[2]).read_text()
assert text==existing,'source drift'
print('SOURCE-LOCKED',len(texts),'blocks',len(text),'characters',hashlib.sha256(text.encode()).hexdigest())
