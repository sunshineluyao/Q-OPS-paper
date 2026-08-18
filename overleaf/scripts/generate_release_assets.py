#!/usr/bin/env python3
"""Generate Q-OPS figures, vector clip art, and the two main tables.

All quantitative marks are derived from the frozen CSV/JSON inputs.  The SVG
masters retain live text, stable IDs, text-shape ownership, and editable paths.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "figs"
CLIP = ROOT / "assets" / "clip-art-set"
CLIP_ASSETS = CLIP / "assets"
TABS = ROOT / "tabs"
DATA = ROOT / "data"

INK = "#18324A"
PRIMARY = "#315EFB"
SECONDARY = "#0F766E"
ACCENT = "#A94F21"
BOUNDARY = "#8B4050"
SURFACE = "#F5F7FB"
COOL = "#EAF0FF"
WARM = "#FFF3EC"
DIVIDER = "#CBD5E1"
WHITE = "#FFFFFF"
MUTED = "#536273"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


class SVG:
    def __init__(self, width: int, height: int, title: str, desc: str, transparent: bool = False):
        self.width, self.height = width, height
        self.text_counter = 0
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(title)}</title>', f'<desc id="desc">{esc(desc)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#536273"/></marker></defs>',
        ]
        if not transparent:
            self.parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="{WHITE}"/>')

    def rect(self, x, y, w, h, fill=WHITE, stroke=DIVIDER, sw=2, rx=14, eid=None, dash=None):
        attrs = f'x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
        if eid: attrs += f' id="{esc(eid)}"'
        if dash: attrs += f' stroke-dasharray="{dash}"'
        self.parts.append(f'<rect {attrs}/>')

    def circle(self, cx, cy, r, fill=WHITE, stroke=DIVIDER, sw=2, eid=None):
        tag = f' id="{esc(eid)}"' if eid else ""
        self.parts.append(f'<circle{tag} cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def line(self, x1, y1, x2, y2, stroke=MUTED, sw=3, arrow=False, dash=None):
        extra = ' marker-end="url(#arrow)"' if arrow else ""
        if dash: extra += f' stroke-dasharray="{dash}"'
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{extra}/>')

    def path(self, d, fill="none", stroke=MUTED, sw=3, arrow=False, dash=None):
        extra = ' marker-end="url(#arrow)"' if arrow else ""
        if dash: extra += f' stroke-dasharray="{dash}"'
        self.parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    def text(self, x, y, value, size=24, fill=INK, weight=400, anchor="start", container=None, padding=10, free=False):
        if bool(container) == bool(free):
            raise ValueError("text must be exactly one of container-owned or free")
        self.text_counter += 1
        own = f' data-container="{esc(container)}" data-padding="{padding}"' if container else ' data-containment="free"'
        self.parts.append(f'<text id="text-{self.text_counter}" x="{x}" y="{y}" font-family="Nimbus Sans,TeX Gyre Heros,Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{own}>{esc(value)}</text>')

    def multiline(self, x, y, lines, size=24, fill=INK, weight=400, anchor="start", leading=1.25, container=None, padding=10, free=False):
        if bool(container) == bool(free):
            raise ValueError("text must be exactly one of container-owned or free")
        self.text_counter += 1
        own = f' data-container="{esc(container)}" data-padding="{padding}"' if container else ' data-containment="free"'
        spans = ''.join(f'<tspan x="{x}" dy="{0 if i == 0 else size*leading}">{esc(line)}</tspan>' for i, line in enumerate(lines))
        self.parts.append(f'<text id="text-{self.text_counter}" x="{x}" y="{y}" font-family="Nimbus Sans,TeX Gyre Heros,Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{own}>{spans}</text>')

    def rotated_text(self, x, y, value, angle=-90, size=24, fill=INK, weight=400, anchor="middle", free=True):
        if not free:
            raise ValueError("rotated text is reserved for intentional free labels")
        self.text_counter += 1
        self.parts.append(f'<text id="text-{self.text_counter}" x="{x}" y="{y}" transform="rotate({angle} {x} {y})" font-family="Nimbus Sans,TeX Gyre Heros,Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" data-containment="free">{esc(value)}</text>')

    def inline_svg_asset(self, path: Path, x, y, width, height):
        """Inline a 512-unit clip-art SVG so PDF export stays vector-native."""
        raw = path.read_text(encoding="utf-8")
        body = raw.split(">", 1)[1].rsplit("</svg>", 1)[0]
        body = re.sub(r"<(?:title|desc)\b[^>]*>.*?</(?:title|desc)>", "", body, flags=re.S)
        body = re.sub(r"<defs\b[^>]*>.*?</defs>", "", body, flags=re.S)
        sx, sy = width / 512.0, height / 512.0
        self.parts.append(f'<g transform="translate({x} {y}) scale({sx} {sy})">{body}</g>')

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(self.parts + ['</svg>']) + '\n', encoding='utf-8')


def person(svg, cx, cy, color=INK, scale=1.0):
    svg.circle(cx, cy-24*scale, 11*scale, fill=WHITE, stroke=color, sw=4*scale)
    svg.path(f'M {cx-24*scale} {cy+28*scale} Q {cx} {cy-8*scale} {cx+24*scale} {cy+28*scale}', stroke=color, sw=4*scale)


def chip(svg, cx, cy, color=PRIMARY, scale=1.0):
    svg.rect(cx-28*scale, cy-28*scale, 56*scale, 56*scale, fill=COOL, stroke=color, sw=4*scale, rx=8*scale)
    for off in (-18, 0, 18):
        svg.line(cx-38*scale, cy+off*scale, cx-28*scale, cy+off*scale, stroke=color, sw=3*scale)
        svg.line(cx+28*scale, cy+off*scale, cx+38*scale, cy+off*scale, stroke=color, sw=3*scale)
    svg.line(cx-12*scale, cy-10*scale, cx+12*scale, cy-10*scale, stroke=color, sw=3*scale)
    svg.line(cx-12*scale, cy+8*scale, cx+12*scale, cy+8*scale, stroke=color, sw=3*scale)


def ledger(svg, x, y, w, h, color=SECONDARY):
    svg.rect(x, y, w, h, fill=WHITE, stroke=color, sw=4, rx=10)
    for i in range(3):
        yy = y + 30 + i*32
        svg.circle(x+25, yy, 6, fill=color, stroke=color, sw=1)
        svg.line(x+45, yy, x+w-20, yy, stroke=color, sw=4)


def clip_staffing():
    s=SVG(512,512,"Staffing mix","A person, neutral compute module, and task board form a conceptual allocation micro-scene.",True)
    person(s,120,240,INK,1.2); chip(s,390,235,PRIMARY,1.2)
    s.rect(205,105,105,190,fill=WHITE,stroke=SECONDARY,sw=5,rx=10)
    for yy in (145,190,235):
        s.circle(230,yy,7,fill=SECONDARY,stroke=SECONDARY,sw=1)
        s.line(250,yy,290,yy,stroke=SECONDARY,sw=5)
    s.path('M 165 250 C 195 250 205 235 205 220',stroke=SECONDARY,sw=5)
    s.path('M 345 245 C 320 245 310 230 310 215',stroke=SECONDARY,sw=5)
    return s


def clip_classical():
    s=SVG(512,512,"Classical counterfactual","Two candidate ledgers compared through a lens.",True)
    ledger(s,70,120,150,220,PRIMARY); ledger(s,292,120,150,220,SECONDARY)
    s.circle(255,305,70,fill=WHITE,stroke=INK,sw=7); s.line(307,357,382,432,stroke=INK,sw=14)
    s.line(215,284,294,284,stroke=ACCENT,sw=6)
    s.line(215,316,278,316,stroke=ACCENT,sw=6)
    return s


def clip_gate():
    s=SVG(512,512,"Evidence gate","Feasibility, headroom, and ambiguity marks entering a selective funnel.",True)
    for x,c in [(115,SECONDARY),(256,PRIMARY),(397,ACCENT)]: s.circle(x,105,34,fill=WHITE,stroke=c,sw=6)
    s.path('M 75 165 L 437 165 L 320 330 L 320 402 L 192 402 L 192 330 Z',fill=COOL,stroke=INK,sw=6)
    s.line(115,140,180,220,stroke=SECONDARY,sw=5); s.line(256,140,256,250,stroke=PRIMARY,sw=5); s.line(397,140,332,220,stroke=ACCENT,sw=5)
    return s


def clip_quantum():
    s=SVG(512,512,"Quantum pilot","A retained-state grid linked to a compact quantum distribution motif.",True)
    for i in range(4):
        for j in range(4):
            c=PRIMARY if (i+j)%3==0 else DIVIDER
            s.circle(95+i*62,150+j*62,12,fill=WHITE,stroke=c,sw=4)
            if i<3: s.line(107+i*62,150+j*62,145+i*62,150+j*62,stroke=DIVIDER,sw=3)
            if j<3: s.line(95+i*62,162+j*62,95+i*62,200+j*62,stroke=DIVIDER,sw=3)
    for yy in (190,250,310):
        s.line(330,yy,452,yy,stroke=SECONDARY,sw=5)
    for x in (360,420):
        s.circle(x,190,13,fill=WHITE,stroke=SECONDARY,sw=4)
        s.circle(x,310,13,fill=WHITE,stroke=SECONDARY,sw=4)
    s.rect(376,228,28,44,fill=WARM,stroke=ACCENT,sw=4,rx=5)
    return s


def clip_certificate():
    s=SVG(512,512,"Feasibility inspector","A magnifier checks constraint rows without implying external certification.",True)
    ledger(s,95,90,270,310,SECONDARY)
    s.circle(340,315,78,fill=WHITE,stroke=INK,sw=8); s.line(395,370,452,427,stroke=INK,sw=16)
    s.line(300,290,378,290,stroke=SECONDARY,sw=7)
    s.line(300,325,360,325,stroke=SECONDARY,sw=7)
    return s


def clip_fallback():
    s=SVG(512,512,"Classical fallback","An unsupported branch returns to a stable classical solution stack.",True)
    ledger(s,70,245,170,170,PRIMARY); chip(s,380,160,SECONDARY,1.05)
    s.path('M 240 330 C 330 330 330 265 330 220 C 330 180 330 150 342 150',stroke=ACCENT,sw=7)
    s.path('M 376 215 C 365 290 315 380 240 380',stroke=PRIMARY,sw=7)
    return s


def clip_outcomes():
    s=SVG(512,512,"Outcome ledger","Editable conceptual ledger for service, cost, review, and resilience outputs.",True)
    ledger(s,96,70,320,370,SECONDARY)
    # Four distinct marks: service pulse, cost bars, review eye, resilience bridge.
    s.path('M 135 150 L 175 150 L 190 125 L 210 178 L 225 150 L 285 150',stroke=PRIMARY,sw=7)
    for i,h in enumerate((38,62,82)): s.rect(145+i*42,235-h,22,h,fill=PRIMARY,stroke=PRIMARY,sw=1,rx=3)
    s.path('M 140 294 Q 200 245 260 294 Q 200 343 140 294 Z',stroke=ACCENT,sw=6); s.circle(200,294,16,fill=WHITE,stroke=ACCENT,sw=5)
    s.path('M 140 390 Q 200 330 260 390',stroke=SECONDARY,sw=8); s.line(140,390,260,390,stroke=SECONDARY,sw=8)
    return s


def clip_difficulty_vector():
    s=SVG(512,512,"Difficulty vector instrument","Six measurement rails feed an unlabelled decision plane.",True)
    for i in range(6):
        yy=105+i*50
        s.line(70,yy,250,yy,stroke=DIVIDER,sw=6)
        s.circle(105+i*22,yy,10,fill=WHITE,stroke=PRIMARY if i<3 else SECONDARY,sw=5)
    s.path('M 275 110 L 440 180 L 400 390 L 245 315 Z',fill=COOL,stroke=INK,sw=6)
    s.line(250,145,315,200,stroke=PRIMARY,sw=5,arrow=True)
    s.line(250,305,300,300,stroke=SECONDARY,sw=5,arrow=True)
    return s


CLIP_BUILDERS = {
    'staffing-mix': clip_staffing, 'classical-counterfactual': clip_classical,
    'evidence-gate': clip_gate, 'quantum-pilot': clip_quantum,
    'independent-certificate': clip_certificate, 'classical-fallback': clip_fallback,
    'outcome-ledger': clip_outcomes, 'difficulty-vector-instrument': clip_difficulty_vector,
}


def card(s, eid, x, y, w, h, title, lines, fill=SURFACE, stroke=DIVIDER, accent=PRIMARY, dashed=False, asset=None):
    s.rect(x,y,w,h,fill=fill,stroke=stroke,sw=2,rx=18,eid=eid,dash='10 7' if dashed else None)
    s.rect(x+14,y+16,6,h-32,fill=accent,stroke=accent,sw=0,rx=3)
    s.text(x+34,y+50,title,size=28,weight=700,container=eid,padding=14)
    s.multiline(x+34,y+94,lines,size=26,fill=MUTED,container=eid,padding=14)
    if asset:
        s.parts.append('<g opacity="0.88">')
        s.inline_svg_asset(CLIP_ASSETS/f'{asset}.svg',x+w-82,y+h-82,62,62)
        s.parts.append('</g>')


def fig1():
    s=SVG(1200,610,"Trustworthy application-level architecture","A dominant classical route with a future invocation gate, optional statevector pilot, retrospective evidence gate, shared verification, and fallback.")
    s.text(35,45,"Trustworthy application architecture",size=36,weight=700,free=True)
    s.text(35,80,"Solid = frozen operation or audit; dashed = future pre-execution action.",size=27,fill=MUTED,free=True)

    # Connectors occupy dedicated gutters and are drawn before nodes.
    s.line(220,425,250,425,stroke=PRIMARY,sw=5,arrow=True)
    s.line(510,425,720,425,stroke=PRIMARY,sw=5,arrow=True)
    s.line(960,425,995,425,stroke=PRIMARY,sw=5,arrow=True)
    s.path('M 380 320 L 380 250',stroke=ACCENT,sw=4,arrow=True,dash='10 7')
    s.line(500,170,555,170,stroke=ACCENT,sw=4,arrow=True,dash='10 7')
    s.line(780,170,835,170,stroke=SECONDARY,sw=5,arrow=True)
    s.path('M 950 240 L 950 280 L 840 280 L 840 320',stroke=SECONDARY,sw=5,arrow=True)
    s.path('M 1080 240 L 1080 300 L 1085 300 L 1085 320',stroke=ACCENT,sw=4,arrow=True)

    # Main classical lane.
    for eid,x,w,asset,title,desc,fill,accent in [
        ('problem',30,190,'staffing-mix','Task instance','service / cost',COOL,PRIMARY),
        ('classical',250,260,'classical-counterfactual','Classical portfolio','incumbent + evidence',SURFACE,PRIMARY),
        ('verify',720,240,'independent-certificate','Shared evaluator','legality + feasibility',SURFACE,SECONDARY),
        ('fallback',995,175,'classical-fallback','Final plan','fallback',WARM,ACCENT),
    ]:
        s.rect(x,320,w,210,fill=fill,stroke=accent,sw=3,rx=18,eid=eid)
        aw=min(128,w-40); s.inline_svg_asset(CLIP_ASSETS/f'{asset}.svg',x+(w-aw)/2,334,aw,aw)
        s.text(x+w/2,478,title,size=27,weight=700,anchor='middle',container=eid,padding=7)
        s.text(x+w/2,505,desc,size=25,fill=MUTED,anchor='middle',container=eid,padding=7)

    # Optional side lane: prospective routing is distinct from the recorded post-simulation gate.
    s.rect(275,100,225,140,fill=WHITE,stroke=ACCENT,sw=3,rx=18,eid='future-gate',dash='10 7')
    s.inline_svg_asset(CLIP_ASSETS/'evidence-gate.svg',285,128,70,70)
    s.text(426,158,"Future gate",size=25,weight=700,anchor='middle',container='future-gate',padding=7)
    s.text(427,210,"not tested",size=25,fill=ACCENT,anchor='middle',container='future-gate',padding=7)

    s.rect(555,100,225,140,fill=COOL,stroke=SECONDARY,sw=3,rx=18,eid='pilot')
    s.inline_svg_asset(CLIP_ASSETS/'quantum-pilot.svg',570,120,100,100)
    s.multiline(718,145,['Optional','pilot'],size=25,weight=700,anchor='middle',container='pilot',padding=7)
    s.text(710,218,"distribution",size=25,fill=MUTED,anchor='middle',container='pilot',padding=7)

    s.rect(835,100,335,140,fill='#E8F6F1',stroke=SECONDARY,sw=3,rx=18,eid='recorded-gate')
    s.inline_svg_asset(CLIP_ASSETS/'outcome-ledger.svg',850,120,100,100)
    s.multiline(1060,143,['Recorded gate','after simulation'],size=26,weight=700,anchor='middle',container='recorded-gate',padding=7)
    s.text(1050,218,"9/32 gate-positive",size=25,fill=SECONDARY,anchor='middle',container='recorded-gate',padding=7)

    s.rect(515,385,190,44,fill=WHITE,stroke=DIVIDER,sw=1,rx=8,eid='label-classical')
    s.text(610,414,"classical route",size=25,weight=700,anchor='middle',container='label-classical',padding=5)
    s.text(35,579,"Boundary: the pilot never replaces the classical incumbent; verification remains classical.",size=26,fill=MUTED,free=True)
    s.save(FIGS/'fig1_architecture.svg')


def read_records():
    with (DATA/'locked_c12_records.csv').open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))


def fig2(records):
    gate_count=sum(r['adoption_gate'].lower()=='true' for r in records)
    s=SVG(1200,620,"Observed evidence margins and conceptual Quantum Value Region","Frozen gate diagnostics occupy the left panel; the unmeasured economic value region is separated on the right.")
    s.text(35,45,"Observed gate evidence versus the economic Quantum Value Region",size=34,weight=700,free=True)
    s.text(35,80,"All marks come from frozen C1.2; the economic region contains no observed points.",size=26,fill=MUTED,free=True)

    # Panel A: exact frozen margins for the two plotted gate dimensions.
    px,py,pw,ph=105,150,660,345
    xmin,xmax,ymin,ymax=-.10,.95,-.20,.40
    xmap=lambda v: px+(v-xmin)/(xmax-xmin)*pw
    ymap=lambda v: py+ph-(v-ymin)/(ymax-ymin)*ph
    xzero,yzero=xmap(0),ymap(0)
    s.rect(35,105,760,460,fill=WHITE,stroke=DIVIDER,sw=2,rx=16,eid='observed-panel')
    s.text(60,142,"A  Frozen post-simulation gate margins",size=29,weight=700,container='observed-panel',padding=8)
    s.rect(xzero,py,px+pw-xzero,yzero-py,fill='#E8F6F1',stroke='none',sw=0,rx=0)
    s.rect(px,py,pw,ph,fill='none',stroke=INK,sw=2,rx=0,eid='plot')
    s.line(xzero,py,xzero,py+ph,stroke=INK,sw=2,dash='8 6')
    s.line(px,yzero,px+pw,yzero,stroke=INK,sw=2,dash='8 6')
    for val in (-.08,0,.25,.50,.75,.92):
        xx=xmap(val); s.line(xx,py+ph,xx,py+ph+7,stroke=INK,sw=2)
        s.text(xx,py+ph+31,f'{val:.2f}'.rstrip('0').rstrip('.'),size=25,anchor='middle',free=True)
    for val in (-.18,0,.10,.20,.30,.40):
        yy=ymap(val); s.line(px-7,yy,px,yy,stroke=INK,sw=2)
        s.text(px-12,yy+7,f'{val:.2f}'.rstrip('0').rstrip('.'),size=25,anchor='end',free=True)
    s.text(px+pw/2,558,"ambiguity margin: a - 0.08",size=26,weight=700,anchor='middle',free=True)
    s.rotated_text(52,325,"concentration margin",size=26,weight=700)
    s.text(xzero+18,py+32,"positive two-margin region",size=25,weight=700,fill=SECONDARY,free=True)

    grouped={}
    for r in records:
        xv=float(r['ambiguity'])-.08
        yv=float(r['qaoa_p2_optimal_probability'])-max(.18,1.4*float(r['uniform_optimal_probability']))
        adopted=r['adoption_gate'].lower()=='true'; strict=float(r['strict_feasible_states'])>0
        grouped.setdefault((round(xv,12),round(yv,12),adopted,strict),0)
        grouped[(round(xv,12),round(yv,12),adopted,strict)]+=1
    for (xv,yv,adopted,strict),count in grouped.items():
        x,y=xmap(xv),ymap(yv); color=SECONDARY if adopted else (ACCENT if strict else MUTED)
        if strict: s.circle(x,y,8,fill=color if adopted else WHITE,stroke=color,sw=3)
        else:
            s.line(x-8,y-8,x+8,y+8,stroke=color,sw=3); s.line(x-8,y+8,x+8,y-8,stroke=color,sw=3)
        if count>1: s.text(x+12,y-10,f'x{count}',size=25,fill=color,weight=700,free=True)

    # Panel B: conceptual economic region, explicitly unestimated.
    s.rect(820,105,350,460,fill=SURFACE,stroke=BOUNDARY,sw=3,rx=16,eid='economic-panel',dash='10 7')
    s.text(850,142,"B  Economic QVR",size=29,weight=700,container='economic-panel',padding=8)
    s.inline_svg_asset(CLIP_ASSETS/'difficulty-vector-instrument.svg',920,155,150,150)
    s.multiline(997,335,['E[value gain | z] >','quantum + validation +','delay + risk + review cost'],size=27,weight=700,anchor='middle',container='economic-panel',padding=10)
    s.text(997,438,"not estimated here",size=28,weight=700,fill=BOUNDARY,anchor='middle',container='economic-panel',padding=14)
    s.multiline(997,470,['Missing: QPU noise + runtime,','engineering + review,','stakeholder outcomes'],size=25,fill=MUTED,anchor='middle',container='economic-panel',padding=6)

    s.circle(55,595,8,fill=SECONDARY,stroke=SECONDARY,sw=3); s.text(75,602,"complete gate +",size=25,fill=SECONDARY,free=True)
    s.circle(270,595,8,fill=WHITE,stroke=ACCENT,sw=3); s.text(290,602,"gate -",size=25,fill=ACCENT,free=True)
    s.line(425,587,441,603,stroke=MUTED,sw=3); s.line(425,603,441,587,stroke=MUTED,sw=3); s.text(450,602,"no strict core",size=25,fill=MUTED,free=True)
    s.text(815,602,f"{gate_count}/{len(records)} complete-gate pass",size=25,weight=700,fill=SECONDARY,free=True)
    s.save(FIGS/'fig2_quantum_value_region.svg')


def fig3(records, reproduction):
    strict_count=sum(float(r['strict_feasible_states'])>0 for r in records)
    gate_count=sum(r['adoption_gate'].lower()=='true' for r in records)
    shared_count=int(reproduction['shared_value_comparisons'])
    s=SVG(1200,600,"Evidence evolution","Three development stages explain which scientific controls were added and why the frozen evidence remains bounded.")
    s.text(35,45,"Evidence evolution: each control answers an earlier failure",size=35,weight=700,free=True)
    s.text(35,80,"C1.0--C1.1 are development evidence; only C1.2 carries frozen held-out results.",size=26,fill=MUTED,free=True)
    s.line(380,305,420,305,stroke=MUTED,sw=4,arrow=True)
    s.line(780,305,820,305,stroke=MUTED,sw=4,arrow=True)
    stages=[
        ('c10',30,'C1.0  Classical ceiling','classical-counterfactual',['Strong search removed','useful headroom.','Add credible alternatives.'],SURFACE,MUTED),
        ('c11',420,'C1.1  Attractive proxy','quantum-pilot',['Concentration appeared;','feasibility + ambiguity','were not established.'],WARM,ACCENT),
        ('c12',820,'C1.2  Frozen audit','evidence-gate',[f'{len(records)} held out; {strict_count}/{len(records)} strict',f'{gate_count}/{len(records)} retrospective gate',f'{shared_count} exact shared fields'],COOL,SECONDARY),
    ]
    for eid,x,title,asset,lines,fill,accent in stages:
        s.rect(x,120,350,350,fill=fill,stroke=accent,sw=3,rx=18,eid=eid)
        s.text(x+175,160,title,size=29,weight=700,anchor='middle',container=eid,padding=15)
        s.inline_svg_asset(CLIP_ASSETS/f'{asset}.svg',x+105,178,140,140)
        s.multiline(x+175,360,lines,size=27,fill=MUTED,weight=700,anchor='middle',container=eid,padding=10)
    s.rect(30,485,1140,95,fill=WHITE,stroke=BOUNDARY,sw=3,rx=12,eid='ceiling',dash='10 7')
    s.text(600,520,"Evidence ceiling: conditional noiseless statevector evidence on retained cores",size=26,weight=700,fill=BOUNDARY,anchor='middle',container='ceiling',padding=8)
    s.text(600,555,"No QPU, wall-clock, scale, application, security, fairness, or welfare claim",size=25,fill=MUTED,anchor='middle',container='ceiling',padding=8)
    s.save(FIGS/'fig3_evidence_evolution.svg')


def wrappers():
    wrappers = {
        'fig1_architecture.tex': r'''\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{figs/fig1_architecture.pdf}
\caption{\textbf{Trustworthy application-level architecture.} The dominant solid lane produces and verifies a classical incumbent. A dashed future pre-execution gate may invoke an optional pilot; the separate frozen gate is computed only after simulation. Gate-positive candidates would return to the same classical evaluator, while unsupported use retains the incumbent. Clip art is semantic only; labels, arrows, and evidence states remain editable.}\label{fig:architecture}
\end{figure*}
''',
        'fig2_quantum_value_region.tex': r'''\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{figs/fig2_quantum_value_region.pdf}
\caption{\textbf{Observed gate diagnostics and the unmeasured economic Quantum Value Region (QVR).} Panel A plots every frozen instance at its ambiguity margin $a-.08$ and concentration margin $p_2^\star-\max(.18,1.4p_U^\star)$. Filled points pass the complete post-simulation gate; open points fail another condition; crosses lack a strict core. Panel B separates the conceptual economic QVR, for which QPU, cost, runtime, risk, review, and stakeholder outcomes were not measured.}\label{fig:qvr}
\end{figure*}
''',
        'fig3_evidence_evolution.tex': r'''\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{figs/fig3_evidence_evolution.pdf}
\caption{\textbf{Evidence evolution as a control argument.} C1.0 shows why credible classical alternatives are necessary; C1.1 shows why concentration alone is insufficient; C1.2 freezes strict feasibility, ambiguity/headroom, matched draws, a recorded gate, shared verification, and fallback. Only the immutable C1.2 held-out evaluation supplies headline numbers.}\label{fig:evolution}
\end{figure*}
'''
    }
    for name,content in wrappers.items(): (FIGS/name).write_text(content,encoding='utf-8')


def tables(summary, rerun, records):
    n=len(records)
    strict_count=sum(float(r['strict_feasible_states'])>0 for r in records)
    gate_count=sum(r['adoption_gate'].lower()=='true' for r in records)
    feasible_count=sum(r['alns_feasible'].lower()=='true' for r in records)
    violation_count=sum(int(r['alns_hard_violations']) for r in records)
    rows1 = [
        ('Decision','Human-only, AI-only, or human--AI collaboration','Accountability and automation choice'),
        ('Reliability','24 correlated disruption scenarios; empirical chance constraints','Customer continuity under shocks'),
        ('Oversight','Finite review capacity; collaboration uses partial review','Reviewer workload and escalation'),
        ('Workflow','Cluster complementarity, concentration, and mode friction','Organizational coordination'),
        ('Objective','Expected service value minus cost, overflow, and penalties','Transparent trade-offs, not welfare'),
        ('Acceptance','Composite feasibility, shared evaluator, classical fallback','Auditable operational boundary'),
    ]
    with (DATA/'table1_decision_environment.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n'); w.writerow(['family','benchmark_encoding','stakeholder_interpretation']); w.writerows(rows1)
    tex = ['\\begin{table}[t]','\\caption{Benchmark and decision environment. All coefficients are frozen synthetic choices, not field-calibrated welfare weights.}\\label{tab:environment}','\\small\\renewcommand{\\arraystretch}{1.12}\\setlength{\\tabcolsep}{3.2pt}','\\begin{tabularx}{\\columnwidth}{@{}p{.18\\columnwidth}YY@{}}','\\toprule','\\textbf{Decision layer} & \\textbf{Benchmark encoding} & \\textbf{Trust question} \\\\','\\midrule','\\multicolumn{3}{@{}l}{\\textcolor{qnavy}{\\textbf{Decision environment}}} \\\\']
    for i,(a,b,c) in enumerate(rows1):
        if i==4: tex += ['\\addlinespace[2pt]','\\multicolumn{3}{@{}l}{\\textcolor{qnavy}{\\textbf{Acceptance and evidence}}} \\\\']
        tex += [f'\\textbf{{{a}}} & {b} & {c} \\\\']
    tex += ['\\bottomrule','\\end{tabularx}','\\end{table}']
    (TABS/'table1_decision_environment.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')

    ci=rerun['paired_ci']
    ratio=summary['mean_qaoa_p2_optimal_probability']/summary['mean_uniform_optimal_probability']
    p1_gt_p2=sum(float(r['qaoa_p1_optimal_probability'])>float(r['qaoa_p2_optimal_probability']) for r in records)
    rows2 = [
        ('Held-out matrix',str(n),'Frozen; all cases retained'),
        ('Strict feasible core',f'{strict_count}/{n}',f'{n-strict_count} least-violation fallbacks'),
        ('Cluster-repair gain',f"{ci['alns_gain']['mean']:.3f} [{ci['alns_gain']['lower']:.3f}, {ci['alns_gain']['upper']:.3f}]",'Paired instance bootstrap'),
        ('Uniform optimum mass',f"{summary['mean_uniform_optimal_probability']:.4f} [{summary['confidence_intervals']['uniform_optimal_probability_ci95'][0]:.4f}, {summary['confidence_intervals']['uniform_optimal_probability_ci95'][1]:.4f}]",'Marginal instance bootstrap; exact distribution'),
        ('$p=2$ optimum mass',f"{summary['mean_qaoa_p2_optimal_probability']:.4f} [{summary['confidence_intervals']['qaoa_p2_optimal_probability_ci95'][0]:.4f}, {summary['confidence_intervals']['qaoa_p2_optimal_probability_ci95'][1]:.4f}]",'Marginal instance bootstrap; statevector'),
        ('Ratio of exact means',f'{ratio:.3f}$\\times$','All 32 retained-core comparisons; no CI'),
        ('$p=2$ minus uniform',f"{ci['qaoa_minus_uniform_optimal_probability']['mean']:.4f} [{ci['qaoa_minus_uniform_optimal_probability']['lower']:.4f}, {ci['qaoa_minus_uniform_optimal_probability']['upper']:.4f}]",'Paired instance bootstrap'),
        ('Recorded gate positive',f"{gate_count}/{n} ({100*gate_count/n + 1e-12:.2f}\\%) [{100*summary['confidence_intervals']['adoption_gate_rate_ci95'][0]:.2f}\\%, {100*summary['confidence_intervals']['adoption_gate_rate_ci95'][1]:.2f}\\%]",'Post-simulation; not prospective'),
        ('$p=1>p=2$',f'{p1_gt_p2}/{n}','Unequal parameter-search budgets; descriptive'),
        ('Composite-feasible incumbent',f'{feasible_count}/{n}','Stricter than mode legality'),
        ('Disallowed-mode violations',f'{violation_count}/{n}','Not total safety or feasibility'),
    ]
    with (DATA/'table2_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n'); w.writerow(['metric','estimate_with_ci_if_applicable','scope']); w.writerows(rows2)
    tex = ['\\begin{table}[t]','\\caption{Frozen C1.2 benchmark results. Brackets are 95\\% intervals only in rows that display them; the scope column distinguishes marginal and paired bootstrap summaries.}\\label{tab:results}','\\small\\renewcommand{\\arraystretch}{1.08}\\setlength{\\tabcolsep}{3pt}','\\begin{tabularx}{\\columnwidth}{@{}p{.29\\columnwidth}p{.31\\columnwidth}Y@{}}','\\toprule','\\textbf{Quantity} & \\textbf{Estimate [95\\% CI]} & \\textbf{Evidence boundary} \\\\','\\midrule']
    tex += [f'{a} & {b} & {c} \\\\' for a,b,c in rows2]
    tex += ['\\bottomrule','\\end{tabularx}','\\end{table}']
    (TABS/'table2_results.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')


def clip_package():
    CLIP_ASSETS.mkdir(parents=True,exist_ok=True)
    for name,builder in CLIP_BUILDERS.items(): builder().save(CLIP_ASSETS/f'{name}.svg')
    s=SVG(1600,900,"Q-OPS technical clip-art contact sheet","Eight original vector assets on a common grid.")
    s.text(60,58,"Q-OPS technical clip-art family",size=34,weight=700,free=True)
    s.text(60,92,"Original editable vectors; artwork contains no claims, labels, numbers, logos, or performance marks.",size=20,fill=MUTED,free=True)
    for i,name in enumerate(CLIP_BUILDERS):
        row,col=divmod(i,4); x=55+col*385; y=125+row*365
        s.rect(x,y,340,320,fill=SURFACE,stroke=DIVIDER,sw=2,rx=18,eid=f'cell-{i}')
        s.inline_svg_asset(CLIP_ASSETS/f'{name}.svg',x+65,y+25,210,210)
        s.text(x+170,y+276,name.replace('-',' '),size=20,weight=700,anchor='middle',container=f'cell-{i}',padding=12)
    s.save(CLIP/'contact-sheet.svg')
    usage = """# Q-OPS technical clip-art family\n\nEight original, transparent, editable SVG assets share a front-view editorial-vector style, dark-ink outline, restrained named-role colors, rounded joins, and 12% clear space. PNG exports are convenience previews; SVG is authoritative. The build creates and validates this family before any manuscript diagram is composed.\n\nEvidence boundary: these conceptual illustrations identify actors, objects, processes, safeguards, and outputs. They do not encode measurements, effect sizes, causality, external certification, implementation status, fairness, safety, or quantum advantage. Hide the art layer and the figures still communicate their scientific meaning through editable text, data marks, connectors, and evidence-state grammar.\n\nPlacement: staffing mix anchors Figure 1 input; classical counterfactual supports the default route; the evidence gate and quantum pilot mark distinct prospective and retrospective processes; the feasibility inspector and fallback occupy the acceptance boundary; the outcome ledger labels reporting; the difficulty-vector instrument appears only in the conceptual economic QVR. Target 18--25 mm for semantically active scenes; do not shrink below 12 mm.\n"""
    (CLIP/'usage-note.md').write_text(usage,encoding='utf-8')
    prompts = """# Asset briefs and source method\n\nSource method: original native SVG geometry authored by the paper-generation script; no external image, logo, traced raster, stock asset, or protected style was used.\n\nStyle lock: editorial vector, front view, medium detail, dark ink #18324A, primary #315EFB, secondary #0F766E, caution #A94F21, boundary #8B4050, neutral #F5F7FB; rounded caps/joins; transparent background; no embedded text.\n\n- staffing-mix: person, neutral compute module, and task board; do not imply worker benefit or optimal allocation.\n- classical-counterfactual: two candidate ledgers compared through a lens; do not imply global optimality or approval.\n- evidence-gate: feasibility/headroom/ambiguity marks entering a funnel; diagram labels distinguish future invocation from frozen retrospective evidence.\n- quantum-pilot: retained-state graph and circuit rails; do not imply QPU execution or hardware advantage.\n- independent-certificate: legacy filename for a feasibility-inspector scene; magnifier over constraint rows; no certification/checkmark semantics.\n- classical-fallback: unsupported branch returns to a stable classical ledger; do not imply every fallback is composite-feasible.\n- outcome-ledger: service, cost, review, and resilience marks; do not imply measured welfare or field outcomes.\n- difficulty-vector-instrument: six measurement rails feed a projection plane; do not imply a trained router or measured economic value.\n"""
    (CLIP/'prompts-and-method.md').write_text(prompts,encoding='utf-8')


def verify_clip_package():
    manifest_path=CLIP/'clip-art-manifest.json'
    if not manifest_path.exists():
        raise SystemExit('clip-art manifest missing: run the clip-art build stage and finalize PNG/checksum validation first')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    expected=set(CLIP_BUILDERS)
    present={asset['id'] for asset in manifest['assets']}
    if present != expected:
        raise SystemExit(f'clip-art manifest IDs differ: expected {sorted(expected)}, found {sorted(present)}')
    for asset in manifest['assets']:
        path=CLIP/asset['file']
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != asset['checksum_sha256']:
            raise SystemExit(f'clip-art checksum mismatch before diagram composition: {asset["id"]}')


def manuscript_assets():
    verify_clip_package()
    FIGS.mkdir(exist_ok=True); TABS.mkdir(exist_ok=True)
    summary=json.loads((DATA/'locked_c12_summary.json').read_text())
    rerun=json.loads((DATA/'locked_rerun_summary.json').read_text())
    reproduction=json.loads((DATA/'shared_field_reproduction.json').read_text())
    records=read_records()
    fig1(); fig2(records); fig3(records,reproduction); wrappers(); tables(summary,rerun,records)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=('clip-art','manuscript'),required=True)
    args=parser.parse_args()
    if args.stage=='clip-art':
        clip_package()
    else:
        manuscript_assets()


if __name__ == '__main__': main()
