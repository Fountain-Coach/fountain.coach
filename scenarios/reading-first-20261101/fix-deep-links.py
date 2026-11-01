from pathlib import Path
import sys,hashlib,json
root=Path(sys.argv[1]).resolve(strict=True)
home=(root/'estate/index.html').read_text()
mark='<body data-edition-id="fountain-coach-opening-matter-20261101">'
assert home.count(mark)==1
changed={}
for target,volume,canonical in [
 ('estate/collections/first-readings/index.html','first-readings','https://fountain.coach/collections/first-readings/'),
 ('estate/bookshelf/index.html','library','https://fountain.coach/bookshelf/')]:
 text=home.replace(mark,mark[:-1]+' data-initial-volume="'+volume+'">')
 text=text.replace('<link rel="canonical" href="https://fountain.coach/"/>','<link rel="canonical" href="'+canonical+'"/>',1)
 assert 'data-initial-volume="'+volume+'"' in text
 dst=root/target
 dst.write_text(text)
 changed[target]=hashlib.sha256(dst.read_bytes()).hexdigest()
assert not 'data-initial-volume' in home
old=root/'folio-proof-receipt.json'
r=json.loads(old.read_text())
r['release']=root.name
r['predecessor']='shared-shell-20261101-v77-folio-verified'
r['deepLinkProofRequired']=['first-readings','library']
r['sha256'].update(changed)
old.write_text(json.dumps(r,indent=2))
print(json.dumps({'release':root.name,'modified':changed},indent=2))
