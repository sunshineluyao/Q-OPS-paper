#!/usr/bin/env python3
"""Fail when SVG text escapes its declared container or lacks classification.

Annotate a text element with ``data-container="shape-id"`` and optionally
``data-padding="12"``. Mark legitimate out-of-shape labels with
``data-containment="free"`` when using ``--require-classification``. The
referenced shape must have an ``id`` and be an
untransformed rect, circle, or ellipse.  Inkscape supplies the actual rendered
text bounding box, so the check follows the export renderer rather than a
hand-written character-width estimate.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def number(value: str | None, label: str) -> float:
    if value is None:
        raise ValueError(f"missing numeric attribute {label}")
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"unsupported non-numeric {label}={value!r}") from exc


def shape_box(element: ET.Element) -> tuple[float, float, float, float]:
    if element.get("transform"):
        raise ValueError("transformed containers are not supported")
    tag = local_name(element.tag)
    if tag == "rect":
        return (
            number(element.get("x", "0"), "x"),
            number(element.get("y", "0"), "y"),
            number(element.get("width"), "width"),
            number(element.get("height"), "height"),
        )
    if tag == "circle":
        cx = number(element.get("cx"), "cx")
        cy = number(element.get("cy"), "cy")
        radius = number(element.get("r"), "r")
        return cx - radius, cy - radius, 2 * radius, 2 * radius
    if tag == "ellipse":
        cx = number(element.get("cx"), "cx")
        cy = number(element.get("cy"), "cy")
        rx = number(element.get("rx"), "rx")
        ry = number(element.get("ry"), "ry")
        return cx - rx, cy - ry, 2 * rx, 2 * ry
    raise ValueError(f"unsupported container element <{tag}>")


def query_boxes(svg: Path, inkscape: str) -> dict[str, tuple[float, float, float, float]]:
    with tempfile.TemporaryDirectory(prefix="svg-containment-") as tmp:
        env = os.environ.copy()
        for name in ("XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME"):
            target = Path(tmp) / name.lower()
            target.mkdir(parents=True, exist_ok=True)
            env[name] = str(target)
        result = subprocess.run(
            [inkscape, "--query-all", str(svg)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Inkscape query failed")
    boxes: dict[str, tuple[float, float, float, float]] = {}
    for line in result.stdout.splitlines():
        parts = line.strip().split(",")
        if len(parts) != 5:
            continue
        try:
            boxes[parts[0]] = tuple(float(value) for value in parts[1:])  # type: ignore[assignment]
        except ValueError:
            continue
    return boxes


def audit(
    svg: Path,
    inkscape: str,
    tolerance: float,
    require_annotations: bool = False,
    require_classification: bool = False,
) -> list[dict[str, object]]:
    root = ET.parse(svg).getroot()
    by_id = {element.get("id"): element for element in root.iter() if element.get("id")}
    text_elements = [element for element in root.iter() if local_name(element.tag) == "text"]
    annotated = [element for element in text_elements if element.get("data-container")]
    free_text = [element for element in text_elements if element.get("data-containment", "").lower() == "free"]
    boxes = query_boxes(svg, inkscape) if annotated else {}
    records: list[dict[str, object]] = []

    if require_annotations and not annotated:
        records.append(
            {
                "svg": str(svg),
                "text_id": None,
                "container_id": None,
                "status": "FAIL",
                "error": "no data-container annotations found in this SVG",
            }
        )

    if require_classification:
        classified_ids = {id(element) for element in annotated + free_text}
        for text_element in text_elements:
            if id(text_element) in classified_ids:
                continue
            records.append(
                {
                    "svg": str(svg),
                    "text_id": text_element.get("id"),
                    "container_id": None,
                    "status": "FAIL",
                    "error": "text must declare data-container or data-containment='free'",
                }
            )
        for text_element in free_text:
            records.append(
                {
                    "svg": str(svg),
                    "text_id": text_element.get("id"),
                    "container_id": None,
                    "status": "PASS",
                    "classification": "free",
                }
            )

    for text_element in annotated:
        text_id = text_element.get("id")
        container_id = text_element.get("data-container")
        padding = number(text_element.get("data-padding", "12"), "data-padding")
        record: dict[str, object] = {
            "svg": str(svg),
            "text_id": text_id,
            "container_id": container_id,
            "padding": padding,
        }
        try:
            if not text_id:
                raise ValueError("annotated text is missing id")
            if not container_id or container_id not in by_id:
                raise ValueError(f"container id {container_id!r} not found")
            if text_id not in boxes:
                raise ValueError("renderer did not return a text bounding box")
            cx, cy, cw, ch = shape_box(by_id[container_id])
            tx, ty, tw, th = boxes[text_id]
            gaps = {
                "left": tx - cx,
                "right": cx + cw - (tx + tw),
                "top": ty - cy,
                "bottom": cy + ch - (ty + th),
            }
            failures = {side: gap for side, gap in gaps.items() if gap + tolerance < padding}
            record.update(
                {
                    "status": "PASS" if not failures else "FAIL",
                    "container_box": [cx, cy, cw, ch],
                    "text_box": [tx, ty, tw, th],
                    "gaps": gaps,
                    "failures": failures,
                }
            )
        except (ValueError, RuntimeError) as exc:
            record.update({"status": "FAIL", "error": str(exc)})
        records.append(record)
    return records


def self_test(inkscape: str, tolerance: float) -> dict[str, object]:
    """Confirm valid, narrowed, unclassified, and intentional-free behavior."""
    template = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 200 100">
  <rect id="box" x="{x}" y="10" width="{width}" height="80" fill="#eef3f8" stroke="#17324d"/>
  <text id="label" data-container="box" data-padding="8" x="100" y="58"
        text-anchor="middle" font-family="DejaVu Sans" font-size="20">Contained label</text>
</svg>
"""
    with tempfile.TemporaryDirectory(prefix="svg-containment-self-test-") as tmp:
        good = Path(tmp) / "good.svg"
        bad = Path(tmp) / "bad.svg"
        unclassified = Path(tmp) / "unclassified.svg"
        free = Path(tmp) / "free.svg"
        good.write_text(template.format(x=10, width=180), encoding="utf-8")
        bad.write_text(template.format(x=82, width=36), encoding="utf-8")
        unclassified.write_text(
            template.format(x=10, width=180).replace(' data-container="box" data-padding="8"', ""),
            encoding="utf-8",
        )
        free.write_text(
            template.format(x=10, width=180).replace(
                ' data-container="box" data-padding="8"', ' data-containment="free"'
            ),
            encoding="utf-8",
        )
        good_records = audit(
            good, inkscape, tolerance, require_annotations=True, require_classification=True
        )
        bad_records = audit(bad, inkscape, tolerance, require_annotations=True, require_classification=True)
        unclassified_records = audit(
            unclassified, inkscape, tolerance, require_classification=True
        )
        free_records = audit(free, inkscape, tolerance, require_classification=True)
    good_passes = bool(good_records) and all(item.get("status") == "PASS" for item in good_records)
    bad_fails = any(item.get("status") == "FAIL" for item in bad_records)
    unclassified_fails = any(item.get("status") == "FAIL" for item in unclassified_records)
    free_passes = bool(free_records) and all(item.get("status") == "PASS" for item in free_records)
    return {
        "status": "PASS" if good_passes and bad_fails and unclassified_fails and free_passes else "FAIL",
        "positive_fixture_passed": good_passes,
        "negative_fixture_failed": bad_fails,
        "unclassified_fixture_failed": unclassified_fails,
        "intentional_free_fixture_passed": free_passes,
        "positive_records": good_records,
        "negative_records": bad_records,
        "unclassified_records": unclassified_records,
        "intentional_free_records": free_records,
    }


def inputs(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.svg"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", help="SVG file or directory")
    parser.add_argument("--inkscape", default=shutil.which("inkscape") or "inkscape")
    parser.add_argument("--tolerance", type=float, default=0.5)
    parser.add_argument("--require-annotations", action="store_true")
    parser.add_argument(
        "--require-classification",
        action="store_true",
        help="Require each text element to declare data-container or data-containment='free'",
    )
    parser.add_argument("--self-test", action="store_true", help="Run positive and negative renderer fixtures")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    if args.self_test:
        payload = self_test(args.inkscape, args.tolerance)
        rendered = json.dumps(payload, indent=2)
        print(rendered)
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered + "\n", encoding="utf-8")
        return 0 if payload["status"] == "PASS" else 1

    if args.path is None:
        parser.error("path is required unless --self-test is used")

    svg_files = inputs(args.path.resolve())
    if not svg_files:
        print("FAIL: no SVG files found", file=sys.stderr)
        return 2

    all_records: list[dict[str, object]] = []
    for svg in svg_files:
        all_records.extend(
            audit(
                svg,
                args.inkscape,
                args.tolerance,
                require_annotations=args.require_annotations,
                require_classification=args.require_classification,
            )
        )

    for record in all_records:
        gaps = record.get("gaps")
        summary = ""
        if isinstance(gaps, dict):
            summary = " " + " ".join(f"{key}={float(value):.1f}" for key, value in gaps.items())
        print(f"{record['status']} {record['svg']}::{record.get('text_id')} -> {record.get('container_id')}{summary}")

    payload = {
        "files": [str(path) for path in svg_files],
        "records": len(all_records),
        "contained_text": sum(bool(record.get("container_id")) for record in all_records),
        "free_text": sum(record.get("classification") == "free" for record in all_records),
        "passed": sum(record.get("status") == "PASS" for record in all_records),
        "failed": sum(record.get("status") != "PASS" for record in all_records),
        "records": all_records,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return 1 if payload["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
