#!/usr/bin/env python3
"""Compare two PDFs by page count and deterministic rasterized page pixels."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PAGES_RE = re.compile(r"^Pages:\s+(\d+)\s*$", re.MULTILINE)


def page_count(pdf: Path, pdfinfo: str) -> int:
    result = subprocess.run([pdfinfo, str(pdf)], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"pdfinfo failed for {pdf}")
    match = PAGES_RE.search(result.stdout)
    if not match:
        raise RuntimeError(f"could not read page count for {pdf}")
    return int(match.group(1))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def render(pdf: Path, pages: int, dpi: int, pdftoppm: str, output: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for page in range(1, pages + 1):
        prefix = output / f"page-{page:04d}"
        result = subprocess.run(
            [
                pdftoppm,
                "-f",
                str(page),
                "-l",
                str(page),
                "-r",
                str(dpi),
                "-singlefile",
                str(pdf),
                str(prefix),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        rendered = prefix.with_suffix(".ppm")
        if result.returncode != 0 or not rendered.is_file():
            raise RuntimeError(result.stderr.strip() or f"failed to render page {page} of {pdf}")
        records.append({"page": page, "sha256": digest(rendered), "bytes": rendered.stat().st_size})
    return records


def compare(expected: Path, actual: Path, dpi: int, pdfinfo: str, pdftoppm: str) -> dict[str, object]:
    expected_pages = page_count(expected, pdfinfo)
    actual_pages = page_count(actual, pdfinfo)
    if expected_pages != actual_pages:
        return {
            "status": "FAIL",
            "expected": str(expected.resolve()),
            "actual": str(actual.resolve()),
            "dpi": dpi,
            "expected_pages": expected_pages,
            "actual_pages": actual_pages,
            "matching_pages": 0,
            "mismatched_pages": ["page-count mismatch"],
        }
    with tempfile.TemporaryDirectory(prefix="pdf-render-compare-") as tmp:
        first_dir = Path(tmp) / "expected"
        second_dir = Path(tmp) / "actual"
        first_dir.mkdir()
        second_dir.mkdir()
        first = render(expected, expected_pages, dpi, pdftoppm, first_dir)
        second = render(actual, actual_pages, dpi, pdftoppm, second_dir)
    mismatches = [
        item["page"] for item, other in zip(first, second) if item["sha256"] != other["sha256"]
    ]
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "expected": str(expected.resolve()),
        "actual": str(actual.resolve()),
        "dpi": dpi,
        "expected_pages": expected_pages,
        "actual_pages": actual_pages,
        "matching_pages": expected_pages - len(mismatches),
        "mismatched_pages": mismatches,
        "expected_page_digests": first,
        "actual_page_digests": second,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--pdfinfo", default=shutil.which("pdfinfo") or "pdfinfo")
    parser.add_argument("--pdftoppm", default=shutil.which("pdftoppm") or "pdftoppm")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    if not args.expected.is_file() or not args.actual.is_file():
        print("ERROR: both PDF paths must exist", file=sys.stderr)
        return 2
    try:
        result = compare(args.expected, args.actual, args.dpi, args.pdfinfo, args.pdftoppm)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
