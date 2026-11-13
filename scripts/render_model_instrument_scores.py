#!/usr/bin/env python3
"""Four paragraph-addressed contemporary Teatro Scores for The Model Is Not the Instrument.
Paper, measured stage geometry, independent instruments and one restrained vermilion cue.
These SVG source assets are editorial art, not software architecture documentation.
"""
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "site/essays/the-model-is-not-the-instrument/assets"
BASE.mkdir(parents=True, exist_ok=True)

def svg(content):
    header = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 980" role="img">
<title>Fountain Press Teatro Score</title>
<rect width="1500" height="980" fill="#f7f6f0"/>
<g stroke="#555a54" stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round">
<path d="M149 627 736 297 1369 646 775 956Z" fill="#e9e8e1" fill-opacity=".32"/>
<path d="M149 627V405L736 84V297" fill="none" stroke="#b6b7ae" stroke-width="1.5"/>
<path d="M736 84 1369 430V646" fill="none" stroke="#b6b7ae" stroke-width="1.5"/>
<g stroke="#afb0a9" stroke-width="1" opacity=".42">
<path d="M248 681 834 350M347 734 933 404M446 787 1032 459M545 840 1131 515M644 892 1230 568"/>
<path d="M237 578 862 923M335 521 960 871M432 464 1058 819M530 409 1158 766M629 354 1256 712"/>
</g>
"""
    return header + content + "</g></svg>\n"

def screen(x,y,w=280,h=252):
    # Tilted screen and understated foot, a distinct native resource
    return f"""<path d="M{x} {y} l{w} -39 v{h} l-{w} 39Z" fill="#f6f5ef"/>
<path d="M{x+19} {y+19} l{w-38} -31 v{h-52} l-{w-38} 31Z" fill="#e3e4dc"/>
<path d="M{x+51} {y+68} l{w-112} -23 M{x+51} {y+92} l{w-119} -23 M{x+51} {y+116} l{w-135} -21 M{x+51} {y+140} l{w-104} -17" stroke="#9b9e96" stroke-width="1.9"/>
<path d="M{x+112} {y+h-16}v44 l-42 23 h136 l-45 -23 v-44" fill="#d8d9d1"/>"""

def host(x,y):
    return f"""<path d="M{x} {y} l186 -106 194 103 -186 109Z" fill="#f5f4ee"/>
<path d="M{x} {y} l194 106 v188 l-194 -106Z" fill="#d8dad3"/>
<path d="M{x+194} {y+106} l186 -109 v188 l-186 109Z" fill="#e3e4dc"/>
<g stroke="#92958d" stroke-width="2.3"><path d="M{x+41} {y+77}v105 M{x+57} {y+85}v105 M{x+73} {y+94}v105 M{x+89} {y+103}v105"/></g>
<circle cx="{x+310}" cy="{y+164}" r="9" fill="#bb503d" stroke="none"/>
<circle cx="{x+337}" cy="{y+148}" r="6" fill="#e7e8e1"/>"""

def tablet(x,y):
    return f"""<path d="M{x} {y} l271 -101 125 76 -266 101Z" fill="#e7e8e0" stroke-width="6"/>
<path d="M{x+23} {y-2} l248 -90 99 60 -247 92Z" fill="#faf9f5" stroke="#92968e" stroke-width="1.3"/>
<path d="M{x+74} {y+3} l63 -24 52 31 -64 24Z" fill="#e2e4dd" stroke="#abb0a6"/>
<path d="M{x+193} {y-38} l75 -27 M{x+187} {y-21} l104 -39 M{x+178} {y-4} l105 -40 M{x+74} {y+38} l69 -26" stroke="#8e9188" stroke-width="1.4"/>"""

hero = svg(
    '<g opacity=".96">'+screen(240,423,258,250)+'</g>'
    +'<path d="M424 781 523 720 624 776 523 835Z" fill="#faf9f3"/>'
    +'<path d="M447 773 521 732 M445 788 545 732 M478 792 570 739" stroke="#a4a69e" stroke-width="1.4"/>'
    +host(635,442)
    +tablet(1120,660)
    +'<path d="M511 591 C573 569 584 541 632 539 M1016 642 C1060 651 1094 660 1117 660" stroke="#737a73" stroke-width="2.5" stroke-dasharray="2 13" fill="none"/>'
    +'<path d="M830 237l54 -31 54 31v59l-54 32-54-32Z" fill="#f9f7f1" stroke="#777c76"/>'
    +'<path d="M843 275c17-19 28-19 41-2 11-14 24-18 40-3" fill="none" stroke="#92958e" stroke-width="2.5"/>'
    +'<path d="M884 329v96" stroke="#92958e" stroke-width="2" stroke-dasharray="2 12"/>'
    +'<path d="M870 425l14 15 14-15-14-16Z" fill="#bd523f" stroke="none"/>'
)
absence = svg(
    '<path d="M270 520l290 -152 142 87 -290 166Z" fill="#f8f7f1"/>'
    +'<path d="M270 520v204l142 87V621Z" fill="#d8d9d1"/>'
    +'<path d="M412 621v190l290-165V455Z" fill="#ecece5"/>'
    +'<path d="M347 581l191 -101 M347 601l210-112 M347 621l175-97" stroke="#a1a29b" stroke-width="1.8"/>'
    +'<path d="M730 446l226-121 180 100-229 126Z" fill="#faf9f5"/>'
    +'<path d="M730 446v225l177 101V551Z" fill="#e8e9e2"/>'
    +'<path d="M907 551v221l229-126V425Z" fill="#f6f4ee"/>'
    +'<path d="M980 532l92-50 M980 564l92-50 M980 595l92-50" stroke="#c0c1bb"/>'
    +'<text x="972" y="670" font-family="Georgia,serif" font-size="73" fill="#8c8d85" stroke="none" transform="skewY(-27)">404</text>'
    +'<path d="M678 608 Q719 574 756 605" stroke="#ba4c39" fill="none" stroke-width="3" stroke-dasharray="3 12"/>'
    +'<path d="M713 609l18 3-7 17" fill="none" stroke="#ba4c39" stroke-width="3"/>'
    +'<path d="M990 780l76-44" stroke="#bd523f" stroke-width="6"/>'
)
score = svg(
    '<path d="M307 345l254-128 197 111-257 140Z" fill="#f8f8f3"/>'
    +'<path d="M307 345v278l194 115V468Z" fill="#e1e1d9"/>'
    +'<path d="M501 468v270l257-144V328Z" fill="#f5f5ef"/>'
    +'<g stroke="#949a93" stroke-width="1.6"><path d="M354 426l117 69 M354 439l117 69 M354 452l117 69 M354 465l117 69 M354 478l117 69"/><path d="M520 503l175-98 M520 517l175-98 M520 531l175-98 M520 545l175-98 M520 559l175-98"/></g>'
    +'<path d="M577 466c13-21 31-24 31 1v57 M649 431c13-21 31-24 31 1v57" fill="none" stroke="#565b54" stroke-width="3"/>'
    +host(806,424)
    +'<path d="M1208 555q42-58 0-116M1236 570q69-93 0-185M1271 589q99-132 0-264" stroke="#ba4c39" stroke-width="3.4" fill="none"/>'
    +'<path d="M753 560l58 13" stroke="#727872" stroke-width="2.4" stroke-dasharray="2 12"/>'
)
workshop = svg(
    screen(210,441,250,229)+host(631,400)+tablet(1110,616)
    +'<path d="M1036 722l92-52 69 36-88 56Z" fill="#dfe2dc"/>'
    +'<path d="M1052 720l71-39 49 24-69 41Z" fill="#faf9f3" stroke="#9b9c95" stroke-width="1.3"/>'
    +'<path d="M1133 737l106-59 65 42-102 58Z" fill="#f3f1e9"/>'
    +'<path d="M1149 730l80-45 M1140 747l80-45" stroke="#9c9d95" stroke-width="1.2"/>'
    +'<path d="M484 602l145-58M1006 594l105 50 M820 796l287-87" stroke="#747a74" stroke-width="2" stroke-dasharray="2 13"/>'
    +'<path d="M803 808l17-12 17 12-17 13Z" fill="#bd513e" stroke="none"/>'
    +'<path d="M462 778l110-66 104 57-110 65Z" fill="#faf9f4"/>'
    +'<path d="M483 779l100-57 M508 793l100-57 M533 807l100-57" stroke="#a2a49d" stroke-width="1.2"/>'
)
items=[('01-the-instrument-and-its-place.svg',hero),('02-the-claim-and-the-browser.svg',absence),('03-a-score-becomes-sound.svg',score),('04-three-machines-one-work.svg',workshop)]
for name,raw in items:
    path=BASE/name
    path.write_text(raw,encoding='utf-8')
    assert raw.startswith('<svg') and '</svg>' in raw
    print(path.name,len(raw))
