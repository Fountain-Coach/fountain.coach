#!/usr/bin/env python3
"""Source-authoritative Teatro Scores for The Model Is Not the Instrument.

Semantic tests are part of this source: four nonrepeating visual arguments,
source-anchored role, and one disciplined 1500 x 980 coordinate system.
No humans, ambiguous AI boxes, invented execution or second publishing Reader.
"""
from pathlib import Path
import html

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"site/essays/the-model-is-not-the-instrument/assets"
OUT.mkdir(parents=True,exist_ok=True)

PAPER="#f8f7f2"; INK="#3e4441"; INK2="#7d857e"; HAIR="#bfc4bd"; WHITE="#fdfcf8"
FACE="#e2e5de"; FADE="#eeeee8"; ACC="#b9533d"; LIGHT="#d7dcd4"

def text(x,y,value,size=23,color=INK,weight="400",anchor="middle",spaced=1.3,family="Arial,Helvetica,sans-serif"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}" font-family="{family}" letter-spacing="{spaced}" stroke="none">'
            f'{html.escape(value)}</text>')
def line(x1,y1,x2,y2,color=INK2,width=2,dash=None):
    a=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{a}/>'
def path(d,fill="none",stroke=INK,width=3,dash=None):
    a=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{a}/>'
def rect(x,y,w,h,fill=WHITE,stroke=INK,width=2,r=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
def circle(x,y,r,fill=ACC,stroke="none",width=1):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
def arrow(x1,y1,x2,y2,colour=ACC,width=6):
    # horizontal or diagonal arrow with clear termination, not a bidirectional line
    import math
    dx=x2-x1;dy=y2-y1;length=math.hypot(dx,dy);ux=dx/length;uy=dy/length
    head=13
    left=(x2-ux*head-uy*8,y2-uy*head+ux*8)
    right=(x2-ux*head+uy*8,y2-uy*head-ux*8)
    return path(f"M{x1},{y1} L{x2-ux*head/2},{y2-uy*head/2}",stroke=colour,width=width)+path(
        f"M{left[0]},{left[1]} L{x2},{y2} L{right[0]},{right[1]}",stroke=colour,width=width)
def common(content,desc):
    # The isometric rule adds a shared optical coordinate field, not a decoration
    grid=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 980" role="img">',
          '<title>Fountain Press Teatro Score</title>',
          f'<desc>{html.escape(desc)}</desc>',rect(0,0,1500,980,PAPER,"none",0,0),
          '<g fill="none" stroke="#b9bdb5" stroke-width="1.4" opacity=".62">',
          path('M115,682 L725,348 L1384,700 L774,944 Z',stroke=HAIR,width=2),
          path('M115,682 L115,463 L725,135 L725,348 M725,135 L1384,486 L1384,700',stroke=HAIR,width=1.8)]
    for n in range(1,8):
        # parallel floor rulings, deliberately low contrast
        x1=115+(610*n)/8;y1=682-(334*n)/8
        x2=774+(610*n)/8;y2=944-(244*n)/8
        grid.append(line(int(x1),int(y1),int(x2),int(y2),HAIR,1))
    for n in range(1,8):
        x1=115+(659*n)/8;y1=682+(262*n)/8
        x2=725+(659*n)/8;y2=348+(352*n)/8
        grid.append(line(int(x1),int(y1),int(x2),int(y2),HAIR,1))
    grid.append('</g>')
    grid.append(content)
    grid.append('</svg>\n')
    return "".join(grid)

def book(x,y,scale=1):
    # A visibly *open readable book* with matching pages
    s=scale
    return f'<g transform="translate({x} {y}) scale({s})">'+(
      path("M0 86 Q92 40 185 79 L185 238 Q93 202 0 245 Z",WHITE,INK,4)+
      path("M185 79 Q290 42 380 82 L380 245 Q280 204 185 238 Z",WHITE,INK,4)+
      path("M185 79 L185 238",stroke=INK,width=3)+
      path("M29 111 L143 92 M28 132 L143 113 M28 153 L139 136 M225 111 L350 96 M225 132 L350 117 M225 153 L344 140 M225 174 L339 160",stroke=INK2,width=2)+
      rect(42,175,101,42,LIGHT,INK2,1,2)+
      path("M57 205 l23 -19 18 12 24 -15",stroke=INK2,width=2)
    )+'</g>'

# I. An execution with a verifiable outcome. A speech balloon does not
# turn into a book: only the admitted publishing instrument emits one.
hero=(
 text(280,224,"REQUEST",25,INK,"600")+text(747,224,"EXECUTION",25,INK,"600")+text(1218,224,"READBACK",25,INK,"600")
 +rect(142,312,282,245,WHITE,INK,4,21)
 +text(283,365,"AI",26,INK2,"600")
 +path("M183 409 H385 M183 437 H351 M183 466 H372",stroke=INK2,width=3)
 +text(283,524,"Prepare the edition",20,INK,anchor="middle",spaced=0)
 +path("M275 557 l-30 28 48 -12",WHITE,INK,4)
 +arrow(447,443,572,443)
 # machine has a visible paper inlet and separate book outlet
 +path("M635 342 l142 -74 155 82 -142 78Z",WHITE,INK,4)
 +path("M635 342 l155 86 v283 l-155 -89Z",FACE,INK,4)
 +path("M790 428 l142 -78 v272 l-142 89Z",FADE,INK,4)
 +path("M678 444 l72 39 M678 471 l72 39 M678 498 l72 39",stroke=INK2,width=3)
 +rect(670,580,90,19,WHITE,INK2,2,2)
 +circle(852,591,11,ACC)
 +path("M930 506 l67 -35 46 26 -68 37Z",WHITE,INK,3)
 +arrow(981,460,1072,460)
 +book(1100,320,.72)
 +path("M1175 675 l38 38 61 -83",stroke=ACC,width=10)
 +text(750,760,"A tool performs the operation.",22,INK,spaced=.15)
 +text(1210,760,"A page can be opened.",22,INK,spaced=.15)
 +circle(746,249,6,ACC)
)
(OUT/"01-the-instrument-and-its-place.svg").write_text(common(hero,
 "Three distinct events: the AI receives a publishing request, a governed publishing instrument executes, and the resulting illustrated book is opened and verified."))

# II. An actual contradiction: a claim at left, empty browser at right.
claim=(
 text(373,216,"CLAIM",26,INK,"600")
 +text(1121,216,"OBSERVATION",26,INK,"600")
 +rect(188,333,380,385,WHITE,INK,4,15)
 +rect(188,333,380,61,FACE,INK,2,15)
 +text(378,376,"AI REPORT",22,INK2,"600")
 +text(378,492,"Published.",44,INK,"400",spaced=0)
 +path("M300 553 l42 42 80 -93",stroke=ACC,width=9)
 +rect(896,330,415,388,WHITE,INK,4,15)
 +rect(896,330,415,62,FACE,INK,2,15)
 +circle(926,362,8,INK2)+circle(955,362,8,INK2)+circle(984,362,8,INK2)
 +text(1100,368,"/book/",23,INK,spaced=0)
 +text(1103,527,"404",90,INK,"400",spaced=0)
 +text(1103,582,"NOT FOUND",23,INK2,"600")
 # broken signal, stop: exactly why observation contradicts report
 +line(582,523,692,523,INK2,3,"4 12")
 +line(815,523,887,523,INK2,3,"4 12")
 +path("M694 505 l36 32 32 -32 32 32",stroke=ACC,width=5)
 +text(742,624,"No verified result",20,INK,spaced=0)
)
(OUT/"02-the-claim-and-the-browser.svg").write_text(common(claim,
 "The AI report states Published with a check, but direct observation in a browser returns HTTP 404 Not Found. The connection between the claim and the result is broken."))

# III. Three genuinely different states: notation -> synthesizer -> waveform.
score=(
 text(291,220,"SCORE",25,INK,"600")
 +text(739,220,"INSTRUMENT",25,INK,"600")
 +text(1188,220,"SOUND",25,INK,"600")
 +path("M186 334 l226 -109 141 87 -226 115Z",WHITE,INK,4)
 +path("M186 334 V683 L327 770 V427Z",FACE,INK,4)
 +path("M327 427 l226 -115 v347 L327 770Z",WHITE,INK,4)
 +path("M347 501 l178 -91 M347 521 l178 -91 M347 541 l178 -91 M347 561 l178 -91 M347 581 l178 -91",stroke=INK2,width=2.5)
 +circle(393,536,9,INK)+path("M402 531 v-55",stroke=INK,width=3)
 +circle(465,499,9,INK)+path("M474 494 v-55",stroke=INK,width=3)
 +arrow(568,497,636,497)
 +path("M675 380 l111 -60 148 81 -111 65Z",WHITE,INK,4)
 +path("M675 380 l148 86 v241 l-148 -83Z",FACE,INK,4)
 +path("M823 466 l111 -65 v226 l-111 80Z",FADE,INK,4)
 +path("M709 498 l91 53 M709 531 l91 53",stroke=INK2,width=2.5)
 +circle(857,523,14,WHITE,INK2,3)+circle(899,501,13,WHITE,INK2,3)+circle(884,592,10,ACC)
 +arrow(947,503,1032,503)
 +path("M1050 503 C1080 384 1116 384 1146 503 S1212 622 1242 503 S1310 383 1340 503",stroke=ACC,width=6)
 +path("M1050 556 C1080 464 1116 464 1146 556 S1212 648 1242 556 S1310 464 1340 556",stroke=ACC,width=3)
 +text(292,835,"Notation is not sound.",19,INK,spaced=.2)
 +text(1178,835,"The result can be heard.",19,INK,spaced=.2)
)
(OUT/"03-a-score-becomes-sound.svg").write_text(common(score,
 "An authored musical score is distinct from the performing software instrument, which must execute to produce sound waves. Clearly marked score, instrument and sound stages."))

# IV. Commercial proposition, not another workshop network drawing:
# three legally/economically distinct layers; paid entitlement points ONLY to
# instrument, the invocation path is separate from compute.
commercial=(
 text(300,230,"AI SERVICE",25,INK,"600")
 +text(752,230,"PAID INSTRUMENT",25,ACC,"600")
 +text(1202,230,"YOUR COMPUTER",25,INK,"600")
 # independent assistant
 +path("M195 410 Q195 361 245 356 Q262 307 319 327 Q354 328 368 370 Q437 371 444 417 Q448 462 403 470 L245 470 Q191 464 195 410Z",WHITE,INK,4)
 +circle(285,416,10,INK2)+circle(322,392,10,INK2)+circle(361,424,10,INK2)
 +path("M285 416 L322 392 L361 424 L285 416",stroke=INK2,width=3)
 +text(318,543,"Chosen independently",19,INK2,spaced=.1)
 # only the middle receives an entitlement
 +path("M630 386 l131 -74 142 79 -129 75Z",WHITE,ACC,5)
 +path("M630 386 l144 80 v221 l-144 -81Z",FACE,ACC,5)
 +path("M774 466 l129 -75 v221 l-129 75Z",FADE,ACC,5)
 +path("M675 472 l59 35 M675 500 l59 34 M675 528 l59 34",stroke=INK2,width=3)
 +circle(849,536,12,ACC)
 +path("M716 289 l32 -20 31 20 -31 20Z",ACC,ACC,1)
 +line(748,310,748,356,ACC,3)
 +text(753,761,"LICENSE / ACCESS",24,ACC,"600")
 # machine + tablet remain at customer
 +rect(1090,335,210,273,FACE,INK,4,8)
 +rect(1112,357,165,159,WHITE,INK2,2,2)
 +path("M1135 391 H1250 M1135 419 H1243 M1135 447 H1252",stroke=INK2,width=2.5)
 +rect(1149,625,214,24,FADE,INK,3,5)
 +path("M1115 612 l-27 22 h274 l-29 -22",WHITE,INK,3)
 +path("M1058 677 l95 -53 77 42 -95 56Z",WHITE,INK2,2)
 +rect(1080,696,90,50,WHITE,INK2,2,4)
 +path("M1095 711 H1153 M1095 725 H1139",stroke=INK2,width=2)
 +text(1197,786,"Execution is local",19,INK2,spaced=.1)
 # interactive pathways: AI invokes tool; tool runs *on* user compute
 +arrow(456,456,615,456,INK2,4)
 +arrow(909,457,1074,457,INK2,4)
 +text(535,417,"INVOKE",16,INK2,spaced=.8)
 +text(995,417,"RUN",16,INK2,spaced=.8)
 # separator under purchase, deliberately exclusive to the middle
 +path("M651 798 h203",stroke=ACC,width=4)
 +text(750,851,"Buy the instrument. Keep the machine.",22,INK,spaced=0)
)
(OUT/"04-three-machines-one-work.svg").write_text(common(commercial,
 "Three distinct commercial relationships: use an independently chosen AI provider, purchase access to Fountain Coach's governed instrument, and execute it on your own computer or Ubuntu host. Only the middle instrument is the sold product."))

for file in sorted(OUT.glob("0[1-4]-*.svg")):
 raw=file.read_text()
 assert raw.count("<svg")==raw.count("</svg>")==1
 assert raw.count("viewBox")==1
 assert raw.count('<desc>')==1
 print(file.name,len(raw))
