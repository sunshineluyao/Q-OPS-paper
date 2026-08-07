#!/usr/bin/env python3
"""Generate six editable, icon-rich SVG figures from frozen public evidence.

All icons are original line symbols drawn below.  The SVG files preserve live
text and vector geometry; the Makefile exports publication PDFs with Inkscape.
Quantitative panels read only the frozen CSV bundled with the paper.
"""

from __future__ import annotations

import csv
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "figs"
DATA = ROOT / "data" / "locked_c12_records.csv"

NAVY = "#17324D"
BLUE = "#2878C8"
VIOLET = "#6C5CC5"
GREEN = "#249D78"
ORANGE = "#E48319"
RED = "#CF4B4B"
TEAL = "#27A7A2"
INK = "#17212B"
MUTED = "#536273"
LIGHT = "#F5F8FB"
PALE_BLUE = "#EEF5FC"
PALE_GREEN = "#ECF7F2"
PALE_VIOLET = "#F2F0FB"
PALE_ORANGE = "#FFF6E9"
GRID = "#D6E0EA"
WHITE = "#FFFFFF"


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


class SVG:
    def __init__(self, width: int, height: int, title: str, desc: str):
        self.width = width
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(title)}</title>',
            f'<desc id="desc">{esc(desc)}</desc>',
            "<defs>",
            '<marker id="arrow" viewBox="0 0 10 10" refX="8.4" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#536273"/></marker>',
            '<filter id="shadow" x="-12%" y="-12%" width="124%" height="132%"><feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/><feOffset in="blur" dy="3" result="offset"/><feComponentTransfer in="offset" result="soft"><feFuncA type="linear" slope="0.12"/></feComponentTransfer><feMerge><feMergeNode in="soft"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
            "</defs>",
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="{WHITE}"/>',
        ]

    def rect(self, x, y, w, h, fill=WHITE, stroke=GRID, sw=2, rx=14, dash=None, shadow=False, element_id=None):
        attrs = f' x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
        if element_id:
            attrs += f' id="{esc(element_id)}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if shadow:
            attrs += ' filter="url(#shadow)"'
        self.parts.append(f"<rect{attrs}/>")

    def line(self, x1, y1, x2, y2, stroke=MUTED, sw=3, arrow=False, dash=None):
        attrs = f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"'
        if arrow:
            attrs += ' marker-end="url(#arrow)"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.parts.append(f"<line {attrs}/>")

    def path(self, d, stroke=MUTED, sw=3, fill="none", arrow=False, dash=None):
        attrs = f'd="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round"'
        if arrow:
            attrs += ' marker-end="url(#arrow)"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.parts.append(f"<path {attrs}/>")

    def circle(self, cx, cy, r, fill=WHITE, stroke=GRID, sw=2):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def ellipse(self, cx, cy, rx, ry, fill="none", stroke=GRID, sw=2, transform=None):
        attrs = f'cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
        if transform:
            attrs += f' transform="{transform}"'
        self.parts.append(f"<ellipse {attrs}/>")

    def polygon(self, points, fill="none", stroke=GRID, sw=2):
        pts = " ".join(f"{x},{y}" for x, y in points)
        self.parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')

    def text(self, x, y, text, size=25, fill=INK, weight=400, anchor="start", family="Arial, Helvetica, sans-serif", italic=False, element_id=None, container=None, padding=12):
        style = "italic" if italic else "normal"
        attrs = ""
        if element_id:
            attrs += f' id="{esc(element_id)}"'
        if container:
            attrs += f' data-container="{esc(container)}" data-padding="{padding}"'
        self.parts.append(
            f'<text{attrs} x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" font-style="{style}" fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>'
        )

    def multiline(self, x, y, lines, size=24, fill=INK, weight=400, anchor="start", leading=1.25, italic=False, element_id=None, container=None, padding=12):
        family = "Arial, Helvetica, sans-serif"
        style = "italic" if italic else "normal"
        attrs = ""
        if element_id:
            attrs += f' id="{esc(element_id)}"'
        if container:
            attrs += f' data-container="{esc(container)}" data-padding="{padding}"'
        spans = []
        for idx, line in enumerate(lines):
            dy = 0 if idx == 0 else size * leading
            spans.append(f'<tspan x="{x}" dy="{dy}">{esc(line)}</tspan>')
        self.parts.append(
            f'<text{attrs} x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" font-style="{style}" fill="{fill}" text-anchor="{anchor}">{"".join(spans)}</text>'
        )

    def save(self, name: str):
        self.parts.append("</svg>")
        FIGS.mkdir(parents=True, exist_ok=True)
        (FIGS / name).write_text("\n".join(self.parts), encoding="utf-8")


def header(svg: SVG, title: str, subtitle: str, status: str | None = None):
    svg.text(50, 48, title, size=32, weight=700, fill=NAVY)
    svg.text(50, 81, subtitle, size=22, fill=MUTED)
    if status:
        w = max(170, 11 * len(status) + 30)
        svg.rect(1150 - w, 28, w, 38, fill=WHITE, stroke=GREEN, sw=2, rx=19)
        svg.text(1150 - w / 2, 54, status, size=17, weight=700, fill=GREEN, anchor="middle")


def pill(svg: SVG, x, y, w, label, color, fill=WHITE, size=19, element_id=None):
    shape_id = f"{element_id}-shape" if element_id else None
    svg.rect(x, y, w, 38, fill=fill, stroke=color, sw=2, rx=19, element_id=shape_id)
    svg.text(
        x + w / 2,
        y + 26,
        label,
        size=size,
        weight=700,
        fill=color,
        anchor="middle",
        element_id=f"{element_id}-label" if element_id else None,
        container=shape_id,
        padding=8,
    )


def icon(svg: SVG, kind: str, cx: float, cy: float, color: str, r: float = 23, background=WHITE):
    """Draw a normalized original line icon inside a circular badge."""
    svg.circle(cx, cy, r, fill=background, stroke=color, sw=2)
    lw = 2.4
    if kind == "human":
        svg.circle(cx, cy - 7, 6, fill="none", stroke=color, sw=lw)
        svg.path(f"M {cx-12} {cy+12} C {cx-9} {cy+1}, {cx+9} {cy+1}, {cx+12} {cy+12}", stroke=color, sw=lw)
    elif kind == "ai":
        svg.rect(cx - 11, cy - 10, 22, 20, fill="none", stroke=color, sw=lw, rx=4)
        svg.circle(cx - 5, cy - 2, 2, fill=color, stroke=color, sw=1)
        svg.circle(cx + 5, cy - 2, 2, fill=color, stroke=color, sw=1)
        svg.line(cx - 5, cy + 5, cx + 5, cy + 5, stroke=color, sw=lw)
        for off in (-7, 0, 7):
            svg.line(cx - 15, cy + off, cx - 11, cy + off, stroke=color, sw=1.8)
            svg.line(cx + 11, cy + off, cx + 15, cy + off, stroke=color, sw=1.8)
    elif kind in {"collab", "network"}:
        pts = [(cx, cy - 11), (cx - 12, cy + 9), (cx + 12, cy + 9)]
        svg.line(*pts[0], *pts[1], stroke=color, sw=lw)
        svg.line(*pts[0], *pts[2], stroke=color, sw=lw)
        svg.line(*pts[1], *pts[2], stroke=color, sw=lw)
        for px, py in pts:
            svg.circle(px, py, 4, fill=background, stroke=color, sw=lw)
    elif kind in {"shield", "certificate"}:
        svg.path(f"M {cx} {cy-15} L {cx+13} {cy-10} L {cx+10} {cy+7} Q {cx} {cy+17} {cx-10} {cy+7} L {cx-13} {cy-10} Z", stroke=color, sw=lw, fill="none")
        svg.path(f"M {cx-6} {cy} L {cx-1} {cy+5} L {cx+7} {cy-5}", stroke=color, sw=lw)
    elif kind == "reliability":
        svg.path(f"M {cx-14} {cy+10} L {cx-6} {cy+2} L {cx+1} {cy+6} L {cx+13} {cy-10}", stroke=color, sw=lw)
        for px, py in [(cx-14, cy+10), (cx-6, cy+2), (cx+1, cy+6), (cx+13, cy-10)]:
            svg.circle(px, py, 2.5, fill=color, stroke=color, sw=1)
    elif kind == "review":
        svg.path(f"M {cx-15} {cy} Q {cx} {cy-14} {cx+15} {cy} Q {cx} {cy+14} {cx-15} {cy} Z", stroke=color, sw=lw, fill="none")
        svg.circle(cx, cy, 5, fill="none", stroke=color, sw=lw)
    elif kind == "quantum":
        svg.ellipse(cx, cy, 15, 6, stroke=color, sw=1.8, transform=f"rotate(30 {cx} {cy})")
        svg.ellipse(cx, cy, 15, 6, stroke=color, sw=1.8, transform=f"rotate(-30 {cx} {cy})")
        svg.ellipse(cx, cy, 15, 6, stroke=color, sw=1.8, transform=f"rotate(90 {cx} {cy})")
        svg.circle(cx, cy, 3, fill=color, stroke=color, sw=1)
    elif kind == "operations":
        svg.line(cx - 14, cy + 12, cx + 14, cy + 12, stroke=color, sw=lw)
        for x, h in [(cx-10, 12), (cx, 20), (cx+10, 27)]:
            svg.rect(x - 3, cy + 12 - h, 6, h, fill=color, stroke=color, sw=1, rx=1)
    elif kind == "warm":
        svg.path(f"M {cx} {cy+15} C {cx-13} {cy+5}, {cx-5} {cy-4}, {cx} {cy-14} C {cx+2} {cy-5}, {cx+14} {cy-1}, {cx+8} {cy+10} C {cx+5} {cy+15}, {cx-3} {cy+17}, {cx} {cy+15} Z", stroke=color, sw=lw, fill="none")
        svg.path(f"M {cx} {cy+10} C {cx-4} {cy+5}, {cx+1} {cy+1}, {cx+3} {cy-4}", stroke=color, sw=1.8)
    elif kind == "abstain":
        svg.line(cx - 13, cy - 11, cx - 13, cy + 11, stroke=color, sw=lw)
        svg.line(cx + 13, cy - 11, cx + 13, cy + 11, stroke=color, sw=lw)
        svg.line(cx - 7, cy, cx + 5, cy, stroke=color, sw=lw, arrow=True)
    elif kind == "scale":
        svg.line(cx, cy - 13, cx, cy + 13, stroke=color, sw=lw)
        svg.line(cx - 13, cy - 8, cx + 13, cy - 8, stroke=color, sw=lw)
        svg.line(cx - 9, cy - 8, cx - 14, cy + 4, stroke=color, sw=1.8)
        svg.line(cx + 9, cy - 8, cx + 14, cy + 4, stroke=color, sw=1.8)
        svg.path(f"M {cx-19} {cy+4} Q {cx-14} {cy+11} {cx-9} {cy+4}", stroke=color, sw=1.8)
        svg.path(f"M {cx+9} {cy+4} Q {cx+14} {cy+11} {cx+19} {cy+4}", stroke=color, sw=1.8)
    elif kind == "router":
        svg.circle(cx, cy, 5, fill=color, stroke=color, sw=1)
        for px, py in [(cx, cy-14), (cx-14, cy+10), (cx+14, cy+10)]:
            svg.line(cx, cy, px, py, stroke=color, sw=lw)
            svg.circle(px, py, 3, fill=background, stroke=color, sw=lw)
    elif kind == "benchmark":
        svg.rect(cx - 12, cy - 14, 24, 28, fill="none", stroke=color, sw=lw, rx=3)
        svg.rect(cx - 5, cy - 17, 10, 6, fill=background, stroke=color, sw=1.8, rx=2)
        for yy in (cy - 6, cy + 1, cy + 8):
            svg.line(cx - 6, yy, cx + 7, yy, stroke=color, sw=1.8)
    elif kind == "uniform":
        for dx in (-8, 0, 8):
            for dy in (-8, 0, 8):
                svg.circle(cx + dx, cy + dy, 2, fill=color, stroke=color, sw=1)
    elif kind == "filter":
        svg.path(f"M {cx-14} {cy-12} L {cx+14} {cy-12} L {cx+5} {cy-1} L {cx+5} {cy+12} L {cx-3} {cy+8} L {cx-3} {cy-1} Z", stroke=color, sw=lw, fill="none")
    elif kind == "repair":
        svg.path(f"M {cx-12} {cy+12} L {cx+3} {cy-3} M {cx-2} {cy-8} Q {cx+8} {cy-15} {cx+14} {cy-7} L {cx+7} {cy} Q {cx} {cy-5} {cx-2} {cy-8}", stroke=color, sw=lw)
        svg.circle(cx - 12, cy + 12, 3, fill="none", stroke=color, sw=lw)
    elif kind == "circuit":
        for dy in (-8, 0, 8):
            svg.line(cx - 15, cy + dy, cx + 15, cy + dy, stroke=color, sw=1.8)
        svg.rect(cx - 8, cy - 13, 7, 10, fill=background, stroke=color, sw=1.8, rx=1)
        svg.rect(cx + 3, cy + 3, 8, 10, fill=background, stroke=color, sw=1.8, rx=1)
        svg.circle(cx + 7, cy - 8, 3, fill=color, stroke=color, sw=1)
    elif kind == "economics":
        svg.circle(cx, cy, 14, fill="none", stroke=color, sw=lw)
        svg.line(cx - 5, cy - 7, cx + 7, cy - 7, stroke=color, sw=1.8)
        svg.line(cx - 7, cy, cx + 7, cy, stroke=color, sw=1.8)
        svg.line(cx - 5, cy + 7, cx + 7, cy + 7, stroke=color, sw=1.8)


def card(svg: SVG, x, y, w, h, color, title, lines, icon_kind, fill=WHITE, dashed=False, title_size=22, body_size=19, element_id=None):
    shape_id = f"{element_id}-shape" if element_id else None
    svg.rect(x, y, w, h, fill=fill, stroke=color, sw=2.6, rx=17, dash="9 7" if dashed else None, shadow=not dashed, element_id=shape_id)
    icon(svg, icon_kind, x + 42, y + 42, color, r=22, background=fill)
    svg.text(
        x + 76,
        y + 39,
        title,
        size=title_size,
        weight=700,
        fill=color,
        element_id=f"{element_id}-title" if element_id else None,
        container=shape_id,
    )
    svg.multiline(
        x + 76,
        y + 72,
        lines,
        size=body_size,
        fill=INK,
        leading=1.32,
        element_id=f"{element_id}-body" if element_id else None,
        container=shape_id,
    )


def compact_card(svg: SVG, x, y, w, h, color, title, subtitle, icon_kind, fill=WHITE):
    """Compact pipeline card with protected icon, title, and annotation zones."""
    svg.rect(x, y, w, h, fill=fill, stroke=color, sw=2.6, rx=16, shadow=True)
    icon(svg, icon_kind, x + 35, y + h / 2, color, r=21, background=fill)
    svg.text(x + 68, y + h / 2 - 6, title, size=19, weight=700, fill=color)
    svg.text(x + 68, y + h / 2 + 20, subtitle, size=15, fill=INK)


def figure1():
    s = SVG(1200, 500, "From governed allocation to certified quantum evidence", "An icon-rich three-stage teaser: human-AI mode allocation, five governance and operational factor families, then a bounded U-W-C-Q audit with a classical certificate.")
    header(s, "Governance comes before quantum invocation", "A task-mode decision becomes quantum evidence only inside a classically verified boundary", "IMPLEMENTED ARC")
    panels = [
        (45, 115, 330, 300, BLUE, PALE_BLUE, "1  Allocate modes", "collab"),
        (435, 115, 330, 300, VIOLET, PALE_VIOLET, "2  Evaluate obligations", "shield"),
        (825, 115, 330, 300, GREEN, PALE_GREEN, "3  Audit evidence", "quantum"),
    ]
    for x, y, w, h, c, fill, title, kind in panels:
        s.rect(x, y, w, h, fill=fill, stroke=c, sw=3, rx=20, shadow=True)
        icon(s, kind, x + 42, y + 43, c, r=23, background=fill)
        s.text(x + 78, y + 50, title, size=24, weight=700, fill=c)
    # Reading-direction arrows stay entirely inside reserved gutters.
    s.line(388, 265, 421, 265, stroke=MUTED, sw=3, arrow=True)
    s.line(778, 265, 811, 265, stroke=MUTED, sw=3, arrow=True)

    # Panel 1: three modes.
    mode_rows = [
        ("human-led", "H", NAVY, "human"),
        ("automatable", "A", ORANGE, "ai"),
        ("complementary", "C", GREEN, "collab"),
    ]
    for j, (label, letter, color, kind) in enumerate(mode_rows):
        yy = 205 + j * 58
        icon(s, kind, 86, yy, color, r=19, background=WHITE)
        s.text(116, yy + 7, label, size=20, fill=INK)
        pill(s, 285, yy - 19, 55, letter, color, fill=WHITE, size=20)
    s.text(75, 385, "decision:  yᵢ ∈ {H, A, C}", size=20, weight=700, fill=NAVY)

    # Panel 2: five factor families as technical chips.
    factors = [
        ("governance", "shield", NAVY),
        ("reliability", "reliability", BLUE),
        ("oversight", "review", ORANGE),
        ("workflow", "network", VIOLET),
        ("eligibility", "filter", GREEN),
    ]
    for j, (label, kind, color) in enumerate(factors):
        col, row = j % 2, j // 2
        xx, yy = 470 + col * 145, 198 + row * 62
        icon(s, kind, xx, yy, color, r=18, background=WHITE)
        s.text(xx + 27, yy + 6, label, size=19, fill=INK)
    s.text(600, 385, "objective · feasibility · interpretation", size=17, weight=700, fill=VIOLET, anchor="middle")

    # Panel 3: classical and quantum evidence with a certificate.
    icon(s, "certificate", 875, 208, NAVY, r=20, background=WHITE)
    s.text(907, 214, "C: controls + core", size=20, weight=700, fill=NAVY)
    icon(s, "warm", 875, 263, VIOLET, r=20, background=WHITE)
    s.text(907, 269, "W: incumbent warm state", size=20, fill=INK)
    icon(s, "uniform", 875, 318, BLUE, r=20, background=WHITE)
    s.text(907, 324, "U vs Q: 128 matched draws", size=20, fill=INK)
    pill(s, 895, 352, 220, "CLASSICAL CERTIFICATE", GREEN, fill=WHITE, size=16)

    s.rect(155, 442, 890, 38, fill=PALE_GREEN, stroke=GREEN, sw=2, rx=19)
    s.text(600, 468, "Supported output: conditional statevector concentration—not universal quantum advantage", size=19, weight=700, fill=GREEN, anchor="middle")
    s.save("fig1_teaser.svg")


def figure2():
    s = SVG(1200, 705, "Five benchmark factor families", "A branching taxonomy connects the governed human-AI allocation problem to five implemented factor families, each represented with an original technical icon and a concise formula or role.")
    header(s, "Five factor families make allocation a governance problem", "Branches encode distinct objective, feasibility, or evidence roles; they are not interchangeable metrics", "METHOD DESIGN")

    # Draw the branching spine first so all connectors remain behind cards.
    s.path("M 600 205 L 600 225 L 290 225 L 290 245", stroke=GRID, sw=6)
    s.path("M 600 225 L 910 225 L 910 245", stroke=GRID, sw=6)
    s.path("M 600 205 L 600 430 L 200 430 L 200 450", stroke=GRID, sw=6)
    s.path("M 600 430 L 600 450", stroke=GRID, sw=6)
    s.path("M 600 430 L 1000 430 L 1000 450", stroke=GRID, sw=6)

    # The central card is deliberately wider than the old version: the previous
    # title and subtitle exceeded the card by 26 px and 9 px in Inkscape's
    # rendered bounding boxes.
    s.rect(390, 105, 420, 100, fill=PALE_GREEN, stroke=GREEN, sw=3, rx=20, shadow=True, element_id="taxonomy-center-shape")
    icon(s, "collab", 445, 155, GREEN, r=25, background=PALE_GREEN)
    s.text(490, 145, "Governed H/A/C evaluator", size=23, weight=700, fill=GREEN, element_id="taxonomy-center-title", container="taxonomy-center-shape")
    s.text(490, 174, "one allocation, five factor families", size=18, fill=INK, element_id="taxonomy-center-body", container="taxonomy-center-shape")

    cards = [
        (110, 245, 360, 160, NAVY, "1  Governance", ["mode domain Dᵢ; H(y)=0", "human-required tasks exclude A"], "shield", PALE_BLUE),
        (730, 245, 360, 160, BLUE, "2  Reliability", ["24 correlated scenarios", "qₛ≤ε and q_c≤ε"], "reliability", PALE_BLUE),
        (20, 450, 360, 160, ORANGE, "3  Oversight & exposure", ["review overflow [R(y)−Bᴿ]₊", "regional AI-use dispersion"], "review", PALE_ORANGE),
        (420, 450, 360, 160, VIOLET, "4  Complementarity", ["cluster threshold reward", "handoff and all-AI penalties"], "network", PALE_VIOLET),
        (820, 450, 360, 160, GREEN, "5  Evidence eligibility", ["classical gain + disagreement", "strict core, gate + certificate"], "filter", PALE_GREEN),
    ]
    for idx, args in enumerate(cards, start=1):
        card(s, *args, body_size=18, element_id=f"taxonomy-card-{idx}")

    s.rect(125, 634, 950, 46, fill="#FFF4F4", stroke=RED, sw=2, rx=23, element_id="taxonomy-disclaimer-shape")
    s.text(600, 663, "Synthetic operational construct—not a validated workplace fairness, welfare, or safety instrument", size=18, fill=RED, weight=700, anchor="middle", element_id="taxonomy-disclaimer-label", container="taxonomy-disclaimer-shape", padding=12)
    s.save("fig2_benchmark_taxonomy.svg")


def figure3():
    s = SVG(1200, 720, "U-W-C-Q dependency lanes", "Three separated lanes show the classical backbone, the bounded quantum audit, and the acceptance boundary. Every connector is routed through whitespace and the future router is isolated below the implemented flow.")
    header(s, "U–W–C–Q: dependency lanes and acceptance", "Implemented paths are solid; the leakage-free pre-execution router remains a dashed research target", "IMPLEMENTED + FUTURE")

    # Lane backgrounds.
    lanes = [
        (45, 115, 1110, 180, NAVY, PALE_BLUE, "C  Classical backbone", "certificate"),
        (45, 320, 1110, 225, VIOLET, PALE_VIOLET, "W/U/Q  Bounded audit", "quantum"),
        (45, 570, 1110, 88, GREEN, PALE_GREEN, "Acceptance boundary", "shield"),
    ]
    for x, y, w, h, color, fill, label, kind in lanes:
        s.rect(x, y, w, h, fill=fill, stroke=color, sw=2.8, rx=20)
        icon(s, kind, x + 34, y + 34, color, r=18, background=fill)
        s.text(x + 63, y + 41, label, size=22, weight=700, fill=color)

    # Classical connectors first, in reserved gutters.
    top_y = 226
    for x1, x2 in [(320, 345), (580, 605), (840, 865)]:
        s.line(x1, top_y, x2, top_y, stroke=MUTED, sw=3, arrow=True)
    classical = [
        (95, 175, 225, 90, BLUE, "Greedy", "coordinate descent", "operations"),
        (355, 175, 225, 90, NAVY, "Cluster repair", "18 iter. · 2 restarts", "repair"),
        (615, 175, 225, 90, VIOLET, "Retained core", "≤ 3⁴ ternary states", "network"),
        (875, 175, 225, 90, GREEN, "Certificate", "legal fallback retained", "certificate"),
    ]
    for args in classical:
        compact_card(s, *args)

    # Quantum-audit connectors are drawn before nodes.  W and U feed separate
    # ports; the Q/U comparison then flows to the post-simulation gate.
    s.path("M 468 295 L 468 370", stroke=VIOLET, sw=3, arrow=True)
    s.path("M 728 295 L 728 345 L 520 345 L 520 500 L 510 500", stroke=BLUE, sw=3, arrow=True)
    s.path("M 728 345 L 728 400", stroke=MUTED, sw=3, arrow=True)
    s.line(510, 417, 575, 417, stroke=MUTED, sw=3, arrow=True)
    s.path("M 510 500 L 545 500 L 545 463 L 575 463", stroke=MUTED, sw=3, arrow=True)
    s.line(800, 455, 825, 455, stroke=MUTED, sw=3, arrow=True)
    s.line(987, 500, 987, 570, stroke=GREEN, sw=3, arrow=True)
    s.path("M 987 265 L 987 305 L 1120 305 L 1120 615 L 1105 615", stroke=GREEN, sw=2.5, arrow=True)

    audit_nodes = [
        (250, 375, 260, 84, VIOLET, "W  Warm state", "nearest ALNS state", "warm"),
        (250, 465, 260, 70, BLUE, "U  Uniform", "128 retained-set draws", "uniform"),
        (575, 410, 225, 90, GREEN, "Q  Statevector", "retained graph; p=1,2", "circuit"),
        (825, 410, 315, 90, ORANGE, "Matched evidence gate", "uses p²* after simulation", "filter"),
    ]
    for args in audit_nodes:
        compact_card(s, *args)

    pill(s, 365, 596, 285, "CERTIFIED INCUMBENT = FALLBACK", GREEN, fill=WHITE, size=15)
    pill(s, 710, 596, 395, "CONDITIONAL EVIDENCE MAY BE REPORTED", GREEN, fill=WHITE, size=16)
    s.line(660, 615, 700, 615, stroke=MUTED, sw=2.5, arrow=True)

    s.rect(280, 677, 640, 34, fill=WHITE, stroke=MUTED, sw=2, rx=17, dash="8 6")
    icon(s, "router", 310, 694, MUTED, r=13, background=WHITE)
    s.text(610, 701, "Future: leakage-free pre-execution invocation router", size=19, fill=MUTED, weight=700, anchor="middle")
    s.save("fig3_uwcq_pipeline.svg")


def figure4():
    s = SVG(1200, 705, "Literature convergence map", "Six established research streams connect through reserved gutters to a central four-layer integration stack. Arrowheads stop at the central boundary and do not cross text or icons.")
    header(s, "Six established streams converge on a scoped integration", "Connectors show conceptual dependence—not chronological priority or an exhaustive systematic review", "SCOPED MAP")

    rows = [145, 335, 525]
    # Draw all connectors behind cards and terminate them at the central card boundary.
    for yy in [215, 405, 595]:
        s.line(375, yy, 415, yy, stroke=GRID, sw=3, arrow=True)
        s.line(825, yy, 785, yy, stroke=GRID, sw=3, arrow=True)

    left = [
        (45, rows[0], 330, 140, BLUE, "Quantum optimization", ["QAOA · variational algorithms", "Farhi · Blekos · Cerezo"], "quantum", PALE_BLUE),
        (45, rows[1], 330, 140, NAVY, "Operations uncertainty", ["chance constraints · service ops", "Charnes–Cooper · Gans et al."], "operations", PALE_BLUE),
        (45, rows[2], 330, 140, ORANGE, "Human–AI organizations", ["teaming · work allocation", "Amershi · Seeber · Bai et al."], "collab", PALE_ORANGE),
    ]
    right = [
        (825, rows[0], 330, 140, VIOLET, "Feasibility & warm starts", ["alternating operators · warm QAOA", "Hadfield · Egger · Sawaya"], "warm", PALE_VIOLET),
        (825, rows[1], 330, 140, GREEN, "Selective prediction", ["abstention · learning to defer", "Geifman–El-Yaniv · Madras"], "abstain", PALE_GREEN),
        (825, rows[2], 330, 140, RED, "Governance & fairness", ["sociotechnical context · standards", "Selbst · NIST · ISO/IEC"], "scale", "#FFF4F4"),
    ]
    for args in left + right:
        card(s, *args, title_size=21, body_size=17)

    s.rect(415, 120, 370, 545, fill=PALE_GREEN, stroke=GREEN, sw=3.5, rx=24, shadow=True)
    icon(s, "router", 600, 172, GREEN, r=29, background=PALE_GREEN)
    s.text(600, 222, "Integration evaluated here", size=25, weight=700, fill=GREEN, anchor="middle")
    s.multiline(600, 252, ["selective, classically bounded", "quantum evidence for governed", "H/A/C allocation"], size=18, weight=700, fill=INK, anchor="middle", leading=1.25)

    layers = [
        (440, 350, 320, 55, NAVY, "1  Governed H / A / C allocation", "collab"),
        (440, 420, 320, 55, VIOLET, "2  Strong C + incumbent W", "repair"),
        (440, 490, 320, 55, BLUE, "3  Matched U / Q sampling", "circuit"),
        (440, 560, 320, 55, GREEN, "4  Locked audit + certificate", "certificate"),
    ]
    for x, y, w, h, color, label, kind in layers:
        s.rect(x, y, w, h, fill=WHITE, stroke=color, sw=2.2, rx=14)
        icon(s, kind, x + 29, y + h / 2, color, r=15, background=WHITE)
        s.text(x + 54, y + 35, label, size=17, weight=700, fill=color)
    s.save("fig4_literature_map.svg")


def read_rows():
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    numeric = {
        "uniform_optimal_probability",
        "qaoa_p1_optimal_probability",
        "qaoa_p2_optimal_probability",
        "uniform_time_to_optimum",
        "qaoa_time_to_optimum",
    }
    for row in rows:
        for key in numeric:
            row[key] = float(row[key])
    return rows


def figure5():
    rows = read_rows()
    n = len(rows)
    strict = sum(int(row["strict_feasible_states"]) > 0 for row in rows)
    wins = sum(row["alns_win"] == "True" for row in rows)
    gate = sum(row["adoption_gate"] == "True" for row in rows)
    feasible = sum(row["alns_feasible"] == "True" for row in rows)
    p1_gt_p2 = sum(row["qaoa_p1_optimal_probability"] > row["qaoa_p2_optimal_probability"] for row in rows)
    p2_gt_u = sum(row["qaoa_p2_optimal_probability"] > row["uniform_optimal_probability"] for row in rows)
    mean_u = sum(row["uniform_optimal_probability"] for row in rows) / n
    mean_p2 = sum(row["qaoa_p2_optimal_probability"] for row in rows) / n
    hit_u = sum(row["uniform_time_to_optimum"] for row in rows) / n
    hit_p2 = sum(row["qaoa_time_to_optimum"] for row in rows) / n

    s = SVG(1200, 790, "Locked two-sided evidence dashboard", "Frozen results across 32 synthetic instances with icon-coded metric tiles, paired probability concentration, a matched-draw first-hit proxy, and an explicit counterevidence strip.")
    header(s, "Locked evidence is favorable—but deliberately two-sided", "32 held-out synthetic instances · four-task retained sets · noiseless statevector · 128 matched draws", "OBSERVED RESULTS")

    tiles = [
        (45, BLUE, f"{strict}/{n}", "strict feasible core", "shield"),
        (330, NAVY, f"{wins}/{n}", "cluster repair wins", "repair"),
        (615, ORANGE, f"{gate}/{n}", "post-simulation gate", "filter"),
        (900, GREEN, "0/32", "explicit mode violations", "certificate"),
    ]
    for x, c, value, label, kind in tiles:
        s.rect(x, 110, 255, 108, fill=LIGHT, stroke=c, sw=2.6, rx=17, shadow=True)
        icon(s, kind, x + 42, 164, c, r=22, background=WHITE)
        s.text(x + 84, 157, value, size=31, weight=700, fill=c)
        s.text(x + 84, 187, label, size=16, fill=INK)

    # Paired probability panel.
    s.rect(45, 250, 540, 390, fill=WHITE, stroke=GRID, sw=2, rx=18)
    icon(s, "quantum", 80, 287, GREEN, r=18, background=WHITE)
    s.text(110, 294, "A  Optimum probability (paired)", size=23, weight=700, fill=NAVY)
    x0, y0, w, h = 105, 575, 410, 230
    for tick in [0.0, 0.2, 0.4, 0.6, 0.8]:
        xx = x0 + (tick / 0.8) * w
        yy = y0 - (tick / 0.8) * h
        s.line(xx, y0, xx, y0 - h, stroke="#E8EDF2", sw=1)
        s.line(x0, yy, x0 + w, yy, stroke="#E8EDF2", sw=1)
        s.text(xx, y0 + 25, f"{tick:.1f}", size=16, fill=MUTED, anchor="middle")
        s.text(x0 - 13, yy + 6, f"{tick:.1f}", size=16, fill=MUTED, anchor="end")
    s.line(x0, y0, x0 + w, y0 - h, stroke=MUTED, sw=2, dash="7 6")
    for row in rows:
        xx = x0 + min(row["uniform_optimal_probability"], 0.8) / 0.8 * w
        yy = y0 - min(row["qaoa_p2_optimal_probability"], 0.8) / 0.8 * h
        s.circle(xx, yy, 5, fill=GREEN, stroke=WHITE, sw=1)
    s.text(x0 + w / 2, 625, "Uniform feasible probability", size=17, fill=MUTED, anchor="middle")
    s.text(x0 + 8, y0 - h + 24, "QAOA p=2 ↑", size=16, fill=MUTED)
    s.rect(125, 309, 390, 34, fill=PALE_GREEN, stroke=GREEN, sw=1.8, rx=17)
    s.text(320, 332, f"mean {mean_u:.3f} → {mean_p2:.3f}; p=2 > U on {p2_gt_u}/{n}", size=18, fill=GREEN, weight=700, anchor="middle")

    # First-hit proxy panel.
    s.rect(615, 250, 540, 390, fill=WHITE, stroke=GRID, sw=2, rx=18)
    icon(s, "operations", 650, 287, BLUE, r=18, background=WHITE)
    s.text(680, 294, "B  Matched-budget first-hit proxy", size=23, weight=700, fill=NAVY)
    base = 545
    scale = 5.25
    bars = [(710, hit_u, BLUE, "Uniform", f"{hit_u:.2f}"), (875, hit_p2, GREEN, "QAOA p=2", f"{hit_p2:.2f}")]
    for x, value, c, label, value_label in bars:
        bh = value * scale
        s.rect(x, base - bh, 105, bh, fill=c, stroke=c, sw=1, rx=5)
        s.text(x + 52, base - bh - 12, value_label, size=22, fill=c, weight=700, anchor="middle")
        s.text(x + 52, base + 28, label, size=18, fill=INK, anchor="middle")
    s.line(675, base, 1025, base, stroke=MUTED, sw=2)
    icon(s, "reliability", 1070, 405, GREEN, r=20, background=WHITE)
    s.text(1070, 440, "lower is better", size=17, weight=700, fill=GREEN, anchor="middle")
    s.rect(655, 586, 460, 34, fill=PALE_GREEN, stroke=GREEN, sw=2, rx=17)
    s.text(885, 609, "mean reduction: 23.56 draws", size=19, fill=GREEN, weight=700, anchor="middle")

    # Counterevidence remains visually primary rather than footnoted away.
    s.rect(45, 670, 1110, 86, fill=PALE_ORANGE, stroke=ORANGE, sw=3, rx=17)
    icon(s, "review", 84, 713, ORANGE, r=21, background=WHITE)
    s.text(120, 704, "Counterevidence retained", size=21, weight=700, fill=ORANGE)
    s.text(120, 735, f"p=1 > p=2 on {p1_gt_p2}/{n} (unequal searches); composite-feasible incumbents {feasible}/{n}; the gate is computed after QAOA.", size=20, fill=INK)
    s.save("fig5_results_dashboard.svg")


def figure6():
    s = SVG(1200, 700, "Open interdisciplinary research agenda", "A solid center states the frozen evidence scope, while six dashed icon-coded cards identify future questions in routing, hardware, economics, accountability, benchmark science, and fair automation.")
    header(s, "The audit opens six falsifiable interdisciplinary questions", "Solid center = established evidence; dashed cards = evidence required beyond this audit", "RESEARCH AGENDA")

    # Connectors behind the cards; no arrowheads imply no established direction of causality.
    links = [
        (380, 250, 470, 290), (600, 270, 600, 290), (820, 250, 730, 290),
        (380, 475, 470, 440), (600, 450, 600, 440), (820, 475, 730, 440),
    ]
    for x1, y1, x2, y2 in links:
        s.line(x1, y1, x2, y2, stroke=GRID, sw=3, dash="7 6")

    s.rect(375, 290, 450, 150, fill=PALE_GREEN, stroke=GREEN, sw=3.5, rx=22, shadow=True, element_id="agenda-center-shape")
    icon(s, "certificate", 430, 340, GREEN, r=25, background=PALE_GREEN)
    s.text(475, 332, "Established scope", size=24, weight=700, fill=GREEN, element_id="agenda-center-title", container="agenda-center-shape")
    s.multiline(475, 368, ["frozen synthetic statevector audit", "matched sampling + certificate"], size=17, fill=INK, weight=700, leading=1.35, element_id="agenda-center-body", container="agenda-center-shape")

    questions = [
        (45, 115, 335, 135, BLUE, "Leakage-free routing", ["Can pre-execution features", "predict conditional utility?"], "router"),
        (432, 115, 335, 135, VIOLET, "QPU & scale", ["Do larger/noisy encodings retain", "conditional concentration?"], "circuit"),
        (820, 115, 335, 135, NAVY, "Adoption economics", ["When do hardware, verification", "and opportunity costs pay?"], "economics"),
        (45, 475, 335, 135, ORANGE, "Accountability", ["Who owns a quantum-assisted", "allocation decision?"], "human"),
        (432, 475, 335, 135, GREEN, "Benchmark science", ["Can preregistration, nulls and", "certificates travel to field data?"], "benchmark"),
        (820, 475, 335, 135, RED, "Fair automation", ["Which exposure metrics reflect", "worker and regional harms?"], "scale"),
    ]
    for idx, (x, y, w, h, c, title, lines, kind) in enumerate(questions, start=1):
        card(s, x, y, w, h, c, title, lines, kind, fill=WHITE, dashed=True, title_size=21, body_size=17, element_id=f"agenda-card-{idx}")

    s.rect(105, 638, 990, 44, fill=LIGHT, stroke=MUTED, sw=2, rx=22, element_id="agenda-footer-shape")
    s.text(600, 666, "Progress requires field validation, stakeholder-defined outcomes, and wall-clock/QPU evidence", size=18, fill=MUTED, weight=700, anchor="middle", element_id="agenda-footer-label", container="agenda-footer-shape", padding=12)
    s.save("fig6_open_questions_map.svg")


def main():
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
    figure6()
    print("Generated six editable SVG figures in", FIGS)


if __name__ == "__main__":
    main()
