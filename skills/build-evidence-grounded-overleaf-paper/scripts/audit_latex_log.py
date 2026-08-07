#!/usr/bin/env python3
"""Fail a paper release on unresolved LaTeX, layout, or output-log defects."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    line: int
    message: str


ERROR_PATTERNS = (
    ("fatal_latex", re.compile(r"^!\s+")),
    ("undefined_citation", re.compile(r"(?:Citation .* undefined|There were undefined citations)", re.I)),
    ("undefined_reference", re.compile(r"(?:Reference .* undefined|There were undefined references)", re.I)),
    ("duplicate_label", re.compile(r"(?:multiply defined|multiply-defined labels)", re.I)),
    ("rerun_required", re.compile(r"(?:Label\(s\) may have changed|Rerun to get cross-references right)", re.I)),
    ("missing_character", re.compile(r"^Missing character:", re.I)),
    ("missing_destination", re.compile(r"has been referenced but does not exist", re.I)),
)
OVERFULL_RE = re.compile(r"^Overfull \\[hv]box", re.I)
UNDERFULL_RE = re.compile(r"^Underfull \\[hv]box", re.I)
OUTPUT_RE = re.compile(r"Output written on .*?\((?P<pages>\d+) pages?[,)]", re.I)


def audit(log: Path, allow_overfull: bool, fail_underfull: bool) -> dict[str, object]:
    text = log.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()

    def add(severity: str, code: str, line_number: int, message: str) -> None:
        key = (code, line_number, message)
        if key not in seen:
            findings.append(Finding(severity, code, line_number, message[:500]))
            seen.add(key)

    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        for code, pattern in ERROR_PATTERNS:
            if pattern.search(line):
                add("error", code, line_number, line)
        if OVERFULL_RE.search(line):
            add("warning" if allow_overfull else "error", "overfull_box", line_number, line)
        if UNDERFULL_RE.search(line):
            add("error" if fail_underfull else "warning", "underfull_box", line_number, line)

    outputs = list(OUTPUT_RE.finditer(text))
    if not outputs:
        add("error", "output_missing", 0, "Compilation log does not confirm a written PDF")
        pages = None
    else:
        pages = int(outputs[-1].group("pages"))

    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    return {
        "status": "PASS" if errors == 0 else "FAIL",
        "log": str(log.resolve()),
        "pages": pages,
        "counts": {"errors": errors, "warnings": warnings},
        "findings": [asdict(item) for item in findings],
    }


def self_test() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="latex-log-audit-self-test-") as tmp:
        good = Path(tmp) / "good.log"
        bad = Path(tmp) / "bad.log"
        good.write_text("Output written on main.pdf (2 pages, 100 bytes).\n", encoding="utf-8")
        bad.write_text(
            "LaTeX Warning: There were undefined references.\n"
            "Overfull \\hbox (3.0pt too wide) in paragraph at lines 1--2\n"
            "Output written on main.pdf (2 pages, 100 bytes).\n",
            encoding="utf-8",
        )
        good_result = audit(good, allow_overfull=False, fail_underfull=False)
        bad_result = audit(bad, allow_overfull=False, fail_underfull=False)
    bad_codes = {item["code"] for item in bad_result["findings"]}
    passed = (
        good_result["status"] == "PASS"
        and bad_result["status"] == "FAIL"
        and {"undefined_reference", "overfull_box"}.issubset(bad_codes)
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "positive_fixture_passed": good_result["status"] == "PASS",
        "negative_fixture_failed": bad_result["status"] == "FAIL",
        "negative_codes": sorted(bad_codes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, nargs="?", help="Compiled LaTeX .log file")
    parser.add_argument("--allow-overfull", action="store_true", help="Downgrade overfull boxes to warnings")
    parser.add_argument("--fail-underfull", action="store_true", help="Treat underfull boxes as errors")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        print(rendered)
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered + "\n", encoding="utf-8")
        return 0 if result["status"] == "PASS" else 1
    if args.log is None:
        parser.error("log is required unless --self-test is used")
    if not args.log.is_file():
        print(f"ERROR: log does not exist: {args.log}", file=sys.stderr)
        return 2
    result = audit(args.log, args.allow_overfull, args.fail_underfull)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
