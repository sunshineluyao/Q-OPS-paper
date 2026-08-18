#!/usr/bin/env python3
"""Audit paper-wide SVG typography, palette, and vector-only release rules."""
from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "audits"
FIGURES = sorted((ROOT / "figs").glob("fig[123]_*.svg"))
FONT = "Nimbus Sans,TeX Gyre Heros,Arial,Helvetica,sans-serif"
PALETTE = {
    "#0F766E", "#18324A", "#315EFB", "#536273", "#8B4050", "#A94F21", "#CBD5E1",
    "#E8F6F1", "#EAF0FF", "#F5F7FB", "#FFF3EC", "#FFFFFF",
}


def main() -> int:
    per_figure: dict[str, object] = {}
    global_min = float("inf")
    for path in FIGURES:
        text = path.read_text(encoding="utf-8")
        root = ET.fromstring(text)
        texts = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "text"]
        sizes = [float(node.attrib.get("font-size", "0")) for node in texts]
        colors = set(re.findall(r"#[0-9A-Fa-f]{6}", text))
        pdf = path.with_suffix(".pdf")
        image_list = subprocess.run(["pdfimages", "-list", str(pdf)], check=True, capture_output=True, text=True).stdout if pdf.exists() else ""
        image_rows = [line for line in image_list.splitlines() if re.match(r"\s*\d+\s+\d+", line)]
        result = {
            "width_1200": root.attrib.get("width") == "1200" and root.attrib.get("viewBox", "").split()[:3] == ["0", "0", "1200"],
            "font_family_unified": all(node.attrib.get("font-family") == FONT for node in texts),
            "minimum_font_units": min(sizes) if sizes else 0,
            "minimum_effective_points_at_397_5pt_width": round((min(sizes) if sizes else 0) * 397.5 / 1200, 3),
            "minimum_font_at_least_25_units": bool(sizes) and min(sizes) >= 25,
            "palette_only": colors <= PALETTE,
            "colors": sorted(colors),
            "no_embedded_raster_in_svg": "<image" not in text,
            "publication_pdf_exists": pdf.exists(),
            "no_raster_images_in_publication_pdf": not image_rows,
            "all_text_classified": all("data-container" in node.attrib or node.attrib.get("data-containment") == "free" for node in texts),
        }
        global_min = min(global_min, result["minimum_font_units"])
        per_figure[path.name] = result
    checks = {
        "exactly_three_figure_masters": len(FIGURES) == 3,
        "all_source_checks_pass": all(all(value for key, value in result.items() if key in {"width_1200", "font_family_unified", "minimum_font_at_least_25_units", "palette_only", "no_embedded_raster_in_svg", "publication_pdf_exists", "no_raster_images_in_publication_pdf", "all_text_classified"}) for result in per_figure.values()),
        "clip_art_package_validated": json.loads((AUDITS / "clip_art_validation.json").read_text(encoding="utf-8")).get("status") == "PASS",
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "status": status,
        "contract": {"figure_width_units": 1200, "minimum_font_units": 25, "minimum_effective_points": 8.281, "font_family": FONT, "palette": sorted(PALETTE)},
        "figures": per_figure,
        "checks": checks,
    }
    AUDITS.mkdir(exist_ok=True)
    (AUDITS / "visual_style_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Visual-system audit", "", f"Status: **{status}**", "", "The same live-text vector contract governs every figure; the original eight-asset clip-art family is finalized and decoded before diagram composition.", "", "| Figure | Minimum SVG units | Effective pt | Unified font | Palette | Vector PDF |", "|---|---:|---:|---:|---:|---:|"]
    for name, result in per_figure.items():
        lines.append(f"| {name} | {result['minimum_font_units']} | {result['minimum_effective_points_at_397_5pt_width']} | {'PASS' if result['font_family_unified'] else 'FAIL'} | {'PASS' if result['palette_only'] else 'FAIL'} | {'PASS' if result['no_raster_images_in_publication_pdf'] else 'FAIL'} |")
    (AUDITS / "visual_style_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
