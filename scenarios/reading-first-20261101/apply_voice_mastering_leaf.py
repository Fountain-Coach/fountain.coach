#!/usr/bin/env python3
"""Append one source-separate Linotype mastering score leaf to each Vergil reading."""
from pathlib import Path
import re
import sys
root=Path(__file__).resolve().parent
source=Path(sys.argv[1]) if len(sys.argv)>1 else root/"index.html"
html=source.read_text()
svg='''<svg class="voice-score-plate" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" role="img" aria-label="Axonometric acoustic score: Vergil source, five Csound mastering stations, Ear observation and browser output.">
<g fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" opacity=".72">
<path d="M38 80 L120 48 L184 78 L103 111 Z M103 111 V156 L184 122 V78 M38 80 V124 L103 156" />
<path d="M188 159 L267 127 L336 156 L258 189 Z M258 189 V228 L336 196 V156 M188 159 V198 L258 228"/>
<path d="M363 81 L449 46 L514 78 L427 113 Z M427 113 V155 L514 121 V78 M363 81 V120 L427 155"/>
<path d="M530 158 L607 126 L682 158 L605 192 Z M605 192 V232 L682 198 V158 M530 158 V198 L605 232"/>
<path d="M184 107 L216 129 M336 165 L392 131 M514 108 L556 138" stroke-dasharray="3 8"/>
<path d="M45 187 C80 173 99 201 122 183 S166 173 181 185" stroke-width="1"/>
<path d="M364 221 C405 206 416 233 449 214 S494 212 523 219" stroke-width="1"/>
</g>
<g fill="currentColor" font-family="ui-monospace,monospace" font-size="17" letter-spacing="1.2">
<text x="78" y="89">01</text><text x="229" y="165">02</text><text x="402" y="85">03</text><text x="567" y="167">04</text>
<text x="18" y="28" font-size="12">SOURCE</text><text x="186" y="116" font-size="12">TONE</text>
<text x="372" y="28" font-size="12">DYNAMICS</text><text x="548" y="113" font-size="12">EAR / OUT</text>
<text x="16" y="266" font-size="12">VOICE · RUMBLE · PRESENCE · SIBILANCE · LEVEL · SAFETY · WITNESS</text>
</g>
<path d="M21 279 H697" stroke="currentColor" stroke-width=".7" opacity=".45"/>
<circle cx="605" cy="211" r="8" fill="#b98265" opacity=".85"/>
</svg>'''
leaf='''<section class="book-end voice-mastering-leaf" id="voice-mastering-{id}" data-voice-mastering-profile="satzfunk.voice.mastering.01">
<p class="voice-score-kicker">Satzfunk · A listening score</p>
<h2>The voice has a room</h2>
'''+svg+'''
<p class="voice-score-commentary">Vergil's recorded voice passes through rumble, tonal, sibilance and dynamics control. Ear listens before the browser sends the sound onward.</p>
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
