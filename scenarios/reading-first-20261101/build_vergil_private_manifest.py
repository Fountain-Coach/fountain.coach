#!/usr/bin/env python3
"""Source-bound British Vergil candidate metadata from independently verified Satzfunk WAV."""
from pathlib import Path
from hashlib import sha256
import json
import os
satzfunk=Path(os.environ.get("SATZFUNK_ROOT",str(Path.home()/"Developer"/"Satzfunk")))
root=satzfunk/"drafts"/"voice-editions"/"on-continuity-fb57e1726c81-cedar"
source=satzfunk/"drafts"/"vergil-on-continuity-v109"/"text.txt"
source_digest="fb57e1726c816497beed41a12504a276a7eeed8b9e1359e35ed07426c56f4b4c"
audio_digest="73e20acd6d063b420c33beb6eb8176a5069eba0949a233412a090c9783757168"
text=source.read_text(encoding="utf8")
audio=(root/"reading.wav").read_bytes()
compressed=(root/"reading.mp3").read_bytes()
derivative_digest="36c1f88c05e896fc1c2f509a898d2858dab1352fdff49d6b3f9f63660a241e40"
assert sha256(compressed).hexdigest()==derivative_digest
receipt=json.loads((root/"render-receipt.json").read_text())
assert sha256(text.encode()).hexdigest()==source_digest
assert sha256(audio).hexdigest()==audio_digest
assert receipt["sourceSHA256"]==source_digest and receipt["audioSHA256"]==audio_digest
assert receipt["status"]=="rendered-private-unreviewed"
assert receipt["frames"]==3666000 and receipt["sampleRate"]==24000
assert receipt["durationSeconds"]==152.75
edition=dict(
 schema="satzfunk.spoken-edition.v1",
 id="british-vergil-on-continuity-fb57e1726c81",
 title="On Continuity",status="private-candidate",
 sourceChapter="continuity",narrator="Vergil",embodiment="British Vergil",
 sourceSHA256=source_digest,text=text,
 publicReleaseAuthorized=False,privateRehearsalAuthorized=True,
 voice=dict(provider="OpenAI",model="gpt-4o-mini-tts",name="cedar",
            disclosure="AI-generated voice, not the author's recording; British Vergil candidate"),
 recording=dict(media="/estate/media/vergil-on-continuity/cedar.mp3",
                sha256=derivative_digest,sampleRate=24000,frames=3666000,
                duration=152.75,bytes=len(compressed),sourceMasterWAVSHA256=audio_digest,
                listeningDerivative="LAME VBR MP3, private stage",estimatedFileDurationSeconds=152.808))
out=Path(__file__).resolve().parent/"british-vergil-edition.private.json"
out.write_text(json.dumps(edition,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print("PRIVATE_CANDIDATE",out,"text_sha",source_digest,"wav_master_sha",audio_digest,"mp3_sha",derivative_digest,"bytes",len(compressed))
