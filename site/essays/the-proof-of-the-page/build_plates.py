#!/usr/bin/env python3
"""Six original, deterministic source-owned editorial plates; no production effects.

All plates are explanatory schematics, never fabricated screenshots of a bug.
"""
from pathlib import Path
import html
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent/'assets'
PAPER='#f7f4ec';WHITE='#fffdf8';INK='#27302f';MUTED='#686e68';RULE='#b9b7ae';RUST='#a75d43';PALE='#dedbd1'

def esc(text):return html.escape(str(text),quote=True)
def txt(x,y,text,size=18,fill=INK,anchor='start',weight='normal',family='Georgia,serif'):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(text)}</text>'
def rect(x,y,w,h,fill='none',stroke=RULE,sw=1.3,r=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def line(x1,y1,x2,y2,color=RULE,sw=1):return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="{sw}" fill="none"/>'
def paragraph(x,y,lines=7,width=170,step=17,ink=INK,variation=0):
    parts=[]
    for i in range(lines):
        ratio=(.62 if i==lines-1 else (0.80 if (i+variation)%5==4 else 1.0))
        parts.append(line(x,y+step*i,x+width*ratio,y+step*i,ink,1.8))
    return ''.join(parts)
def sheet(x,y,w,h,label=None,fill=WHITE):
    out=[rect(x,y,w,h,fill,INK,1.15)]
    if label:out.append(txt(x+13,y+23,label,13,MUTED))
    return ''.join(out)
def base(title,desc,body,h=640):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{h}" viewBox="0 0 1100 {h}" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>{esc(desc)}</desc>{rect(0,0,1100,h,PAPER,'none',0)}{line(64,70,1036,70,INK,1.15)}{txt(65,49,title,29,INK)}{body}{line(64,h-58,1036,h-58,INK,1)}{txt(66,h-29,'FOUNTAIN PRESS / THE PROOF OF THE PAGE',12,MUTED)}{txt(1035,h-29,'EXPLANATORY PLATE · NOT A LIVE SCREENSHOT',12,MUTED,anchor='end')}</svg>'''

# 01: stable source addresses, reflowed folios.
b=[]
b.append(txt(64,111,'One addressed passage',17,MUTED))
for i,label in enumerate(['S.1.01','S.1.02','S.1.03','S.1.04','S.1.05']):
    x=65+i*195;b.extend([rect(x,125,168,66,WHITE,INK,1),txt(x+13,150,label,14,RUST),line(x+13,168,x+151,168,INK,1.5)])
b.extend([line(530,191,530,227,RUST,2),txt(550,218,'same source; different physical measure',15,MUTED)])
for x,y,w,h,label in [(90,257,240,290,'A4 PROOF'),(410,257,220,290,'PORTRAIT'),(705,296,300,202,'LANDSCAPE SPREAD')]:
    b.append(sheet(x,y,w,h,label))
    if label=='LANDSCAPE SPREAD':
        b.append(line(x+w/2,y+30,x+w/2,y+h-16,RULE,1.8));b.append(paragraph(x+18,y+70,5,113,17));b.append(paragraph(x+167,y+70,5,112,17))
    else:b.append(paragraph(x+23,y+69,9,w-46,20))
    b.append(txt(x+w/2,y+h+26,'FOLIO '+('001' if label=='A4 PROOF' else '1 / 2' if label=='LANDSCAPE SPREAD' else '01'),13,MUTED,anchor='middle'))
(OUT/'01-source-and-folio.svg').parent.mkdir(parents=True,exist_ok=True)
(OUT/'01-source-and-folio.svg').write_text(base('Source and folio','The same source block identities are composed into three different sets of page geometries.',''.join(b)))

# 02: actual v177 -> v178 structural failure, labeled explicitly diagram.
b=[]
b.extend([txt(86,111,'v177 · mistaken art-leaf break',17,RUST),txt(614,111,'v178 · corrected in-flow figure',17,INK)])
for x in (95,619):b.append(sheet(x,134,385,369))
b.append(txt(112,170,'004',13,MUTED));b.append(paragraph(117,201,1,338,19));b.append(txt(119,256,'The last sentence',16,INK));b.append(txt(119,276,'was isolated here.',16,INK));b.append(line(117,299,455,299,RUST,1.5))
b.append(txt(112,457,'Unexplained blank space',15,RUST))
b.append(txt(635,170,'003',13,MUTED));b.append(paragraph(639,202,4,328,20));b.append(rect(639,297,185,107,'#e7e7dc',RULE,1));b.append(txt(733,351,'FIGURE',15,MUTED,anchor='middle'));b.append(paragraph(639,430,2,329,20))
b.append(txt(95,543,'A verified source-structure defect',16,MUTED));b.append(txt(619,543,'Source unchanged; flow restored',16,MUTED))
(OUT/'02-abandoned-sentence.svg').write_text(base('The abandoned sentence','Schematic comparison of the Client-Centered private v177 isolated sentence and the accepted v178 in-flow correction.',''.join(b)))

# 03: correct and incorrect white with same area.
b=[]
b.extend([txt(105,117,'A deliberate terminal leaf',17,INK),txt(607,117,'A misplaced break before prose',17,RUST)])
for x in (116,621):b.append(sheet(x,139,343,371))
b.append(paragraph(136,181,4,304,20));b.append(txt(136,294,'Chapter ends here.',17,INK))
b.append(paragraph(640,181,4,300,20));b.append(txt(640,294,'A paragraph continues...',17,INK));b.append(txt(638,469,'Next source block displaced',14,RUST))
b.extend([line(481,322,598,322,MUTED,1),txt(540,306,'≈ SAME',13,MUTED,anchor='middle'),txt(540,337,'OPEN AREA',13,MUTED,anchor='middle')])
b.append(txt(115,548,'Space belongs to the chapter ending.',15,MUTED));b.append(txt(620,548,'Space is an artifact of pagination.',15,MUTED))
(OUT/'03-white-space.svg').write_text(base('The right to remain empty','Two schematic sheets have comparable open space, but only one is deliberate.',''.join(b)))

# 04: figure position relative to authored prose.
b=[]
b.extend([txt(92,110,'False independent art leaf',17,RUST),txt(610,110,'Source-anchored illustration',17,INK)])
for x in (99,608):b.append(sheet(x,136,378,390))
b.append(paragraph(120,187,3,329,20));b.append(line(120,273,449,273,RUST,2))
b.append(txt(120,302,'END OF PROSE STREAM',13,RUST))
b.append(rect(121,333,327,134,'#e0ddd2',RULE,1));b.append(txt(286,405,'FIGURE ON NEW LEAF',14,MUTED,anchor='middle'))
b.append(paragraph(630,176,4,328,19));b.append(rect(630,283,274,112,'#e0ddd2',RULE,1));b.append(txt(767,345,'SOURCE FIGURE',15,INK,anchor='middle'))
b.append(txt(630,421,'Caption remains with figure',13,MUTED));b.append(paragraph(630,445,3,328,18))
b.append(txt(101,561,'False page boundary',15,RUST));b.append(txt(609,561,'Continuation remains possible',15,MUTED))
(OUT/'04-image-and-passage.svg').write_text(base('The image and its passage','A secondary figure cannot replace the source relationship between preceding and following prose.',''.join(b)))

# 05: precisely 1,000 schematized folios.
b=[];b.append(txt(67,109,'1,000 numbered folios · 1,000 evidence addresses · no sampling',17,INK))
columns,rows=40,25;stepx,stepy=24,16.6;x0,y0=68,139
review={31,176,299,431,678,799,885,971}
for index in range(1,1001):
    row=(index-1)//columns;col=(index-1)%columns;x=x0+stepx*col;y=y0+stepy*row
    fill=RUST if index in review else WHITE
    stroke=RUST if index in review else RULE
    b.append(rect(round(x,1),round(y,1),16,12,fill,stroke,.55))
b.append(txt(70,589,'01',14,MUTED));b.append(txt(1015,589,'1000',14,MUTED,anchor='end'))
b.append(txt(67,622,'Rust marks indicate review candidates, not automatic failures.',14,MUTED))
(OUT/'05-thousand-leaf-proof.svg').write_text(base('The thousand-leaf proof','A schematic contact sheet with exactly 1,000 folio cells and a small set of review candidates, not a live scan.', ''.join(b),h=700))

# 06: accountable proof cycle, not a software workflow screen.
b=[]
names=[('SOURCE','admitted writing'),('SETTING','measured composition'),('EVIDENCE','all composed folios'),('DECISION','writer or editor')]
for i,(name,sub) in enumerate(names):
    x=63+i*260
    b.append(rect(x,171,227,239,WHITE,INK,1.2))
    b.append(txt(x+18,210,name,18,INK));b.append(line(x+18,224,x+207,224,RUST,1))
    b.append(txt(x+18,252,sub,15,MUTED))
    if i==0:b.append(paragraph(x+19,286,5,183,21))
    if i==1:b.append(sheet(x+45,281,137,104));b.append(paragraph(x+62,307,3,101,18))
    if i==2:
        for n in range(12):b.append(rect(x+18+n%4*45,291+n//4*33,28,23,WHITE,RULE,.65))
        b.append(rect(x+18+2*45,291+1*33,28,23,RUST,RUST,.8))
    if i==3:b.append(txt(x+20,296,'OBSERVE',14,INK));b.append(txt(x+20,328,'APPROVE',14,INK));b.append(txt(x+20,360,'REVISE',14,RUST))
    if i<3:b.append(line(x+230,289,x+258,289,RUST,1.5))
b.append(line(966,444,130,444,MUTED,1.1));b.append(line(130,444,130,411,MUTED,1.1));b.append(txt(548,474,'Only an authorized revision returns to the source.',16,MUTED,anchor='middle'))
(OUT/'06-the-returned-proof.svg').write_text(base('The proof returns','Source, setting, evidence and editorial decision are distinct; observations do not automatically rewrite the work.',''.join(b)))

for svg in sorted(OUT.glob('*.svg')):
    ET.parse(svg)
    print(svg.name,svg.stat().st_size)
