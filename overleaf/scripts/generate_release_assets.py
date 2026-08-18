#!/usr/bin/env python3
"""Generate Q-OPS figures, vector clip art, and the two main tables.

All quantitative marks are derived from the frozen CSV/JSON inputs.  The SVG
masters retain live text, stable IDs, text-shape ownership, and editable paths.
"""

from __future__ import annotations

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
SECONDARY = "#14877D"
ACCENT = "#D97745"
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
        self.parts.append(f'<text id="text-{self.text_counter}" x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{own}>{esc(value)}</text>')

    def multiline(self, x, y, lines, size=24, fill=INK, weight=400, anchor="start", leading=1.25, container=None, padding=10, free=False):
        if bool(container) == bool(free):
            raise ValueError("text must be exactly one of container-owned or free")
        self.text_counter += 1
        own = f' data-container="{esc(container)}" data-padding="{padding}"' if container else ' data-containment="free"'
        spans = ''.join(f'<tspan x="{x}" dy="{0 if i == 0 else size*leading}">{esc(line)}</tspan>' for i, line in enumerate(lines))
        self.parts.append(f'<text id="text-{self.text_counter}" x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{own}>{spans}</text>')

    def rotated_text(self, x, y, value, angle=-90, size=24, fill=INK, weight=400, anchor="middle", free=True):
        if not free:
            raise ValueError("rotated text is reserved for intentional free labels")
        self.text_counter += 1
        self.parts.append(f'<text id="text-{self.text_counter}" x="{x}" y="{y}" transform="rotate({angle} {x} {y})" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" data-containment="free">{esc(value)}</text>')

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
    svg.circle(cx-10*scale, cy-8*scale, 4*scale, fill=color, stroke=color, sw=1)
    svg.circle(cx+10*scale, cy-8*scale, 4*scale, fill=color, stroke=color, sw=1)
    svg.line(cx-10*scale, cy+10*scale, cx+10*scale, cy+10*scale, stroke=color, sw=3*scale)


def ledger(svg, x, y, w, h, color=SECONDARY):
    svg.rect(x, y, w, h, fill=WHITE, stroke=color, sw=4, rx=10)
    for i in range(3):
        yy = y + 30 + i*32
        svg.circle(x+25, yy, 6, fill=color, stroke=color, sw=1)
        svg.line(x+45, yy, x+w-20, yy, stroke=color, sw=4)


def clip_staffing():
    s=SVG(512,512,"Staffing mix","Human, AI, and collaborative work as a conceptual staffing micro-scene.",True)
    person(s,130,235,INK,1.25); chip(s,382,230,PRIMARY,1.25)
    s.circle(256,315,54,fill=WARM,stroke=SECONDARY,sw=5); person(s,238,320,SECONDARY,.62); chip(s,278,320,SECONDARY,.55)
    s.path('M 174 250 C 205 275 218 289 226 301',stroke=SECONDARY,sw=5); s.path('M 338 250 C 307 275 294 289 286 301',stroke=SECONDARY,sw=5)
    return s


def clip_classical():
    s=SVG(512,512,"Classical counterfactual","Two candidate ledgers compared through a lens.",True)
    ledger(s,70,120,150,220,PRIMARY); ledger(s,292,120,150,220,SECONDARY)
    s.circle(255,305,70,fill=WHITE,stroke=INK,sw=7); s.line(307,357,382,432,stroke=INK,sw=14)
    s.path('M 225 305 L 247 327 L 289 277',stroke=ACCENT,sw=8)
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
    s.circle(385,250,54,fill=WHITE,stroke=SECONDARY,sw=5)
    s.path('M 325 250 C 340 190 430 190 445 250 C 430 310 340 310 325 250',stroke=SECONDARY,sw=4)
    s.path('M 385 188 C 330 215 330 285 385 312 C 440 285 440 215 385 188',stroke=SECONDARY,sw=4)
    s.circle(385,250,8,fill=ACCENT,stroke=ACCENT,sw=1)
    return s


def clip_certificate():
    s=SVG(512,512,"Independent certificate","A magnifier checks constraint rows without implying external certification.",True)
    ledger(s,95,90,270,310,SECONDARY)
    s.circle(340,315,78,fill=WHITE,stroke=INK,sw=8); s.line(395,370,452,427,stroke=INK,sw=16)
    s.path('M 305 315 L 330 340 L 380 285',stroke=SECONDARY,sw=9)
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


CLIP_BUILDERS = {
    'staffing-mix': clip_staffing, 'classical-counterfactual': clip_classical,
    'evidence-gate': clip_gate, 'quantum-pilot': clip_quantum,
    'independent-certificate': clip_certificate, 'classical-fallback': clip_fallback,
    'outcome-ledger': clip_outcomes,
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
    s=SVG(1400,720,"Trustworthy application-level architecture","Classical-first staffing architecture with evidence gate, optional pilot, independent evaluation, and fallback.")
    s.text(50,48,"Trustworthy application-level architecture",size=32,weight=700,free=True)
    s.text(50,82,"Solid paths are implemented in the frozen audit; dashed actions are architectural extensions.",size=26,fill=MUTED,free=True)
    # connectors first, through dedicated horizontal and vertical gutters
    for x1,x2 in [(250,300),(550,600),(850,900),(1150,1200)]: s.line(x1,260,x2,260,arrow=True)
    s.line(725,390,725,470,arrow=True); s.line(1000,390,1000,470,arrow=True)
    s.path('M 1260 390 C 1260 610 500 610 500 390',stroke=ACCENT,sw=4,arrow=True)
    card(s,'problem',40,150,210,240,'Staffing',['service / cost','review cap.','joint shocks'],fill=COOL,accent=PRIMARY,asset='staffing-mix')
    card(s,'classical',300,150,250,240,'Classical first',['greedy + cluster','repair','feasible plan'],fill=SURFACE,accent=PRIMARY,asset='classical-counterfactual')
    card(s,'gate',600,150,250,240,'Evidence gate',['core / headroom','ambiguity / value'],fill=WARM,accent=ACCENT,asset='evidence-gate')
    card(s,'pilot',900,150,250,240,'Quantum pilot',['retained states','matched draws'],fill=COOL,accent=SECONDARY,asset='quantum-pilot')
    card(s,'certificate',1180,150,180,240,'Verify',['tests','accept/stop'],fill=SURFACE,accent=SECONDARY,asset='independent-certificate')
    card(s,'review',595,470,260,150,'Abstain / review',['conceptual','not evaluated'],fill=WHITE,stroke=ACCENT,accent=ACCENT,dashed=True)
    card(s,'outcome',875,470,250,150,'Outcome',['metrics'],fill=SURFACE,accent=SECONDARY,asset='outcome-ledger')
    card(s,'fallback',1160,470,200,150,'Fallback',['classical'],fill=WARM,accent=ACCENT,asset='classical-fallback')
    s.text(50,682,"Evidence boundary: quantum sampling can inform a candidate distribution; live labels, gates, certification, and fallback remain editable and classical.",size=26,fill=MUTED,free=True)
    s.save(FIGS/'fig1_architecture.svg')


def read_records():
    with (DATA/'locked_c12_records.csv').open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))


def fig2(records):
    s=SVG(1200,760,"Quantum Value Region","Observed frozen instances mapped by classical ambiguity and p=2 optimum probability.")
    s.text(55,50,"Observed Quantum Value Region",size=32,weight=700,free=True)
    s.text(55,82,"Frozen C1.2 observations; regions are gate interpretations, not application-level value estimates.",size=22,fill=MUTED,free=True)
    x0,y0,w,h=120,125,930,510
    xthr=x0+.08*w; ythr=y0+h-.18*h
    s.rect(x0,y0,w,h,fill=WHITE,stroke=DIVIDER,sw=2,rx=0,eid='plot')
    s.rect(x0,y0,xthr-x0,h,fill=SURFACE,stroke='none',sw=0,rx=0)
    s.rect(xthr,y0,w-(xthr-x0),ythr-y0,fill='#E8F6F1',stroke='none',sw=0,rx=0)
    s.rect(xthr,ythr,w-(xthr-x0),y0+h-ythr,fill=WARM,stroke='none',sw=0,rx=0)
    s.line(xthr,y0,xthr,y0+h,stroke=INK,sw=2,dash='8 6'); s.line(x0,ythr,x0+w,ythr,stroke=INK,sw=2,dash='8 6')
    for k in range(6):
        xx=x0+k*w/5; yy=y0+h-k*h/5
        s.line(xx,y0+h,xx,y0+h+8,stroke=INK,sw=2); s.text(xx,y0+h+34,f'{k/5:.1f}',size=22,anchor='middle',free=True)
        s.line(x0-8,yy,x0,yy,stroke=INK,sw=2); s.text(x0-15,yy+6,f'{k/5:.1f}',size=22,anchor='end',free=True)
    s.text(x0+w/2,700,"classical ambiguity",size=22,weight=700,anchor='middle',free=True)
    s.rotated_text(40,380,"p=2 optimum probability",size=22,weight=700)
    s.text(150,155,"Classical sufficient",size=22,weight=700,fill=MUTED,free=True)
    s.text(720,155,"Quantum-candidate region",size=22,weight=700,fill=SECONDARY,free=True)
    s.text(650,610,"Evidence insufficient",size=22,weight=700,fill=ACCENT,free=True)
    for r in records:
        x=x0+float(r['ambiguity'])*w; y=y0+h-float(r['qaoa_p2_optimal_probability'])*h
        adopted=r['adoption_gate'].lower()=='true'; strict=float(r['strict_feasible_states'])>0
        color=SECONDARY if adopted else (ACCENT if strict else MUTED)
        if strict: s.circle(x,y,7,fill=WHITE if not adopted else color,stroke=color,sw=3)
        else:
            s.line(x-7,y-7,x+7,y+7,stroke=color,sw=3); s.line(x-7,y+7,x+7,y-7,stroke=color,sw=3)
    # legend in protected band
    s.circle(1090,170,7,fill=SECONDARY,stroke=SECONDARY,sw=3); s.text(1110,176,"gate +",size=22,fill=SECONDARY,free=True)
    s.circle(1090,210,7,fill=WHITE,stroke=ACCENT,sw=3); s.text(1110,216,"gate −",size=22,fill=ACCENT,free=True)
    s.line(1083,243,1097,257,stroke=MUTED,sw=3); s.line(1083,257,1097,243,stroke=MUTED,sw=3); s.text(1110,256,"no core",size=22,fill=MUTED,free=True)
    s.text(120,738,"Guides: ambiguity .08; p2 mass .18. Full gate also uses strict core, ratio, and headroom.",size=22,fill=MUTED,free=True)
    s.save(FIGS/'fig2_quantum_value_region.svg')


def fig3():
    s=SVG(1400,690,"Evidence evolution","C1.0 to C1.2 development logic and controls.")
    s.text(50,50,"Evidence evolution: controls added because earlier signals were insufficient",size=31,weight=700,free=True)
    s.text(50,82,"C1.0--C1.1 are qualitative development evidence; only C1.2 carries frozen held-out results.",size=26,fill=MUTED,free=True)
    s.line(430,330,500,330,arrow=True); s.line(900,330,970,330,arrow=True)
    card(s,'c10',40,145,390,370,'C1.0  Classical ceiling',['Strong classical search','left too little headroom.','Control: compare against','credible alternatives.'],fill=SURFACE,accent=MUTED)
    card(s,'c11',500,145,400,370,'C1.1  Attractive proxy',['Concentration alone','did not establish a','feasible, ambiguous','value region.','Control: gate feasibility','and ambiguity.'],fill=WARM,accent=ACCENT)
    card(s,'c12',970,145,390,370,'C1.2  Frozen audit',['32 held-out instances','strict cores: 30/32','post-simulation gate: 9/32','shared evaluator + fallback','704 exact shared-field checks'],fill=COOL,accent=SECONDARY)
    s.text(50,585,"Scientific argument",size=28,weight=700,fill=INK,free=True)
    s.text(320,585,"Apparent value can vanish without feasibility, strong classical controls, and relevance.",size=26,fill=MUTED,free=True)
    s.text(50,640,"Remaining boundary",size=28,weight=700,fill=INK,free=True)
    s.text(350,640,"Routing, QPU/noise, end-to-end cost, and stakeholder outcomes remain open.",size=26,fill=MUTED,free=True)
    s.save(FIGS/'fig3_evidence_evolution.svg')


def wrappers():
    wrappers = {
        'fig1_architecture.tex': r'''\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{figs/fig1_architecture.pdf}
\caption{\textbf{Trustworthy application-level architecture.} Strong classical alternatives precede the recorded evidence gate; the quantum branch is optional; a shared classical evaluator and fallback bound operational acceptance. Dashed abstention/review is conceptual and was not evaluated. Clip art is semantic only; labels, arrows, gates, and evidence states are editable vector layers.}\label{fig:architecture}
\end{figure*}
''',
        'fig2_quantum_value_region.tex': r'''\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{figs/fig2_quantum_value_region.pdf}
\caption{\textbf{Observed Quantum Value Region.} Each frozen instance is plotted by classical ambiguity and $p=2$ optimum probability. Filled points pass the complete post-simulation gate; open points fail it; crosses lack a strict core. Shaded regions interpret two gate dimensions only and do not encode economic value or a prospective routing policy.}\label{fig:qvr}
\end{figure*}
''',
        'fig3_evidence_evolution.tex': r'''\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{figs/fig3_evidence_evolution.pdf}
\caption{\textbf{Evidence evolution rather than a decorative timeline.} C1.0 and C1.1 identify why strong classical controls, strict feasibility, ambiguity, matched comparison, certification, and fallback are necessary. Only the immutable C1.2 held-out evaluation supplies headline numbers.}\label{fig:evolution}
\end{figure*}
'''
    }
    for name,content in wrappers.items(): (FIGS/name).write_text(content,encoding='utf-8')


def tables(summary, rerun):
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
    tex = ['\\begin{table}[t]','\\caption{Benchmark and decision environment. All coefficients are frozen synthetic choices, not field-calibrated welfare weights.}\\label{tab:environment}','\\small\\setlength{\\tabcolsep}{3.5pt}','\\begin{tabularx}{\\columnwidth}{@{}p{.19\\columnwidth}YY@{}}','\\toprule','\\textbf{Family} & \\textbf{Benchmark encoding} & \\textbf{Interpretation} \\\\','\\midrule']
    tex += [f'{a} & {b} & {c} \\\\' for a,b,c in rows1]
    tex += ['\\bottomrule','\\end{tabularx}','\\end{table}']
    (TABS/'table1_decision_environment.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')

    ci=rerun['paired_ci']; rows2 = [
        ('Held-out matrix','32','--','Frozen; all cases retained'),
        ('Strict feasible core','30/32','--','Two least-violation fallbacks'),
        ('Cluster repair gain',f"{ci['alns_gain']['mean']:.3f}",f"[{ci['alns_gain']['lower']:.3f}, {ci['alns_gain']['upper']:.3f}]",'Paired instance bootstrap'),
        ('Uniform optimum mass',f"{summary['mean_uniform_optimal_probability']:.4f}",f"[{summary['confidence_intervals']['uniform_optimal_probability_ci95'][0]:.4f}, {summary['confidence_intervals']['uniform_optimal_probability_ci95'][1]:.4f}]",'All retained cores'),
        ('$p=2$ optimum mass',f"{summary['mean_qaoa_p2_optimal_probability']:.4f}",f"[{summary['confidence_intervals']['qaoa_p2_optimal_probability_ci95'][0]:.4f}, {summary['confidence_intervals']['qaoa_p2_optimal_probability_ci95'][1]:.4f}]",'Noiseless statevector'),
        ('$p=2$ minus uniform',f"{ci['qaoa_minus_uniform_optimal_probability']['mean']:.4f}",f"[{ci['qaoa_minus_uniform_optimal_probability']['lower']:.4f}, {ci['qaoa_minus_uniform_optimal_probability']['upper']:.4f}]",'Matched retained state set'),
        ('Evidence-gate positive','9/32 (28.13\\%)','[12.50\\%, 43.75\\%]','Post-simulation; not prospective'),
        ('Composite-feasible incumbent','27/32','--','Stricter than mode legality'),
        ('Disallowed-mode violations','0/32','--','Not total safety or feasibility'),
    ]
    with (DATA/'table2_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n'); w.writerow(['metric','estimate','ci95_or_denominator','scope']); w.writerows(rows2)
    tex = ['\\begin{table}[t]','\\caption{Frozen C1.2 benchmark results. Intervals are 95\\% paired bootstrap intervals where available; ``--'' means no interval was specified.}\\label{tab:results}','\\footnotesize\\setlength{\\tabcolsep}{3pt}','\\begin{tabularx}{\\columnwidth}{@{}Yp{.18\\columnwidth}p{.25\\columnwidth}Y@{}}','\\toprule','\\textbf{Metric} & \\textbf{Estimate} & \\textbf{95\\% CI / denominator} & \\textbf{Scope} \\\\','\\midrule']
    tex += [f'{a} & {b} & {c} & {d} \\\\' for a,b,c,d in rows2]
    tex += ['\\bottomrule','\\end{tabularx}','\\end{table}']
    (TABS/'table2_results.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')


def clip_package():
    CLIP_ASSETS.mkdir(parents=True,exist_ok=True)
    for name,builder in CLIP_BUILDERS.items(): builder().save(CLIP_ASSETS/f'{name}.svg')
    s=SVG(1600,900,"Q-OPS technical clip-art contact sheet","Seven original vector assets on a common grid.")
    s.text(60,58,"Q-OPS technical clip-art family",size=34,weight=700,free=True)
    s.text(60,92,"Original editable vectors; artwork contains no claims, labels, numbers, logos, or performance marks.",size=20,fill=MUTED,free=True)
    for i,name in enumerate(CLIP_BUILDERS):
        row,col=divmod(i,4); x=55+col*385; y=125+row*365
        s.rect(x,y,340,320,fill=SURFACE,stroke=DIVIDER,sw=2,rx=18,eid=f'cell-{i}')
        s.inline_svg_asset(CLIP_ASSETS/f'{name}.svg',x+65,y+25,210,210)
        s.text(x+170,y+276,name.replace('-',' '),size=20,weight=700,anchor='middle',container=f'cell-{i}',padding=12)
    s.save(CLIP/'contact-sheet.svg')
    usage = """# Q-OPS technical clip-art family\n\nSeven original, transparent, editable SVG assets share a front-view editorial-vector style, 2 px-equivalent dark-ink outline, restrained primary/secondary/status colors, rounded joins, and 12% clear space. PNG exports are convenience previews; SVG is authoritative.\n\nEvidence boundary: these conceptual illustrations identify actors, objects, processes, safeguards, and outputs. They do not encode measurements, effect sizes, causality, certification by an external body, implementation status, fairness, safety, or quantum advantage. Hide the art layer and the figures still communicate their scientific meaning through editable text, data marks, connectors, and evidence-state grammar.\n\nPlacement: staffing mix anchors Figure 1 input; classical counterfactual and evidence gate support the classical-first path; quantum pilot marks only the optional branch; independent certificate and fallback occupy the acceptance boundary; outcome ledger labels operational evaluation. Minimum recommended width is 25 mm or 180 px.\n"""
    (CLIP/'usage-note.md').write_text(usage,encoding='utf-8')
    prompts = """# Asset briefs and source method\n\nSource method: original native SVG geometry authored by the paper-generation script; no external image, logo, traced raster, stock asset, or protected style was used.\n\nStyle lock: editorial vector, front view, medium detail, dark ink #18324A, primary #315EFB, secondary #14877D, status accent #D97745, neutral #F5F7FB; rounded caps/joins; transparent background; no embedded text.\n\n- staffing-mix: human figure, unlabeled AI chip, and collaborative micro-scene converging; do not imply worker benefit or optimal allocation.\n- classical-counterfactual: two candidate ledgers compared through a lens; do not imply global optimality.\n- evidence-gate: feasibility/headroom/ambiguity marks entering a funnel; do not imply prospective validation of the frozen gate.\n- quantum-pilot: retained-state graph and distribution motif; do not imply QPU execution or hardware advantage.\n- independent-certificate: constraint ledger inspected by a magnifier; do not imply third-party certification or total safety.\n- classical-fallback: unsupported branch returns to a stable classical ledger; do not imply every fallback is composite-feasible.\n- outcome-ledger: service, cost, review, and resilience marks; do not imply measured welfare or field outcomes.\n"""
    (CLIP/'prompts-and-method.md').write_text(prompts,encoding='utf-8')


def main():
    FIGS.mkdir(exist_ok=True); TABS.mkdir(exist_ok=True)
    summary=json.loads((DATA/'locked_c12_summary.json').read_text())
    rerun=json.loads((DATA/'locked_rerun_summary.json').read_text())
    records=read_records()
    clip_package(); fig1(); fig2(records); fig3(); wrappers(); tables(summary,rerun)


if __name__ == '__main__': main()
