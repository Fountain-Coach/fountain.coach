#!/usr/bin/env python3
"""Append one source-separate Linotype mastering score leaf to each Vergil reading."""
from pathlib import Path
import re
import sys
root=Path(__file__).resolve().parent
source=Path(sys.argv[1]) if len(sys.argv)>1 else root/"index.html"
html=source.read_text()
patcher='<div class="voice-patch-surface" data-patch-model="satzfunk.voice.mastering.01" role="group" aria-label="SatzfunkPlayer Csound voice patch. Select module ports to reconnect processing.">The voice processing patch is available when the reader loads.</div>'

leaf='''<section class="book-end voice-mastering-leaf" id="voice-mastering-{id}" data-voice-mastering-profile="satzfunk.voice.mastering.01">
<p class="voice-score-kicker">Satzfunk · A patch you can hear</p>
<h2>The voice has a room</h2>
'''+patcher+'''
<p class="voice-score-commentary">These are the actual Csound modules. Select a processor to inspect it, or connect its ports to change the voice path. Safety and Ear remain in circuit.</p>
<output class="voice-score-live" aria-label="Ear observation during playback" aria-live="off">Ear listens when the reading plays.</output>
<p class="voice-score-standard">BBC/EBU aim: −23 LUFS · −1 dBTP. Certification requires a full-programme measurement.</p>
</section>'''
for volume in ("teatro","solstice-reading-01--vergil"):
 pattern=r'(<template data-reader-volume="'+re.escape(volume)+r'">)(.*?)(</template>)'
 m=re.search(pattern,html,re.S)
 if not m: raise SystemExit("Missing volume "+volume)
 inner=m.group(2)
 if 'voice-mastering-leaf' in inner: raise SystemExit("Score already exists "+volume)
 trailer='</article></section></div>'
 if not inner.endswith(trailer): raise SystemExit("Unrecognized source template ending "+volume+":"+inner[-70:])
 # Append a distinct final end page; never add text to the immutable narrated prose.
 insert=leaf.replace('{id}',volume)
 inner=inner[:-len('</div>')]+insert+'</div>'
 html=html[:m.start(2)]+inner+html[m.end(2):]
source.write_text(html)
print("LINOTYPE_END_LEAVES",[(v,html.count('id="voice-mastering-'+v+'"')) for v in ("teatro","solstice-reading-01--vergil")])
