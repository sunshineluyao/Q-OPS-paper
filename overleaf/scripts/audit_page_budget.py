#!/usr/bin/env python3
"""Fail closed unless the anonymous paper uses exactly eight content pages."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "audits"


def page_text(page: int) -> str:
    return subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), str(ROOT / "main.pdf"), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def main() -> int:
    info = subprocess.run(["pdfinfo", str(ROOT / "main.pdf")], check=True, capture_output=True, text=True).stdout
    pages_match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    total_pages = int(pages_match.group(1)) if pages_match else 0
    main_tex = (ROOT / "main.tex").read_text(encoding="utf-8")
    intro = (ROOT / "sections/01_introduction.tex").read_text(encoding="utf-8")
    page8 = page_text(8)
    page9 = page_text(9)
    page9_lines = [line.strip() for line in page9.splitlines() if line.strip()]
    checks = {
        "pdf_has_appendix_pages": total_pages > 9,
        "exactly_six_numbered_sections": len(re.findall(r"\\input\{sections/", main_tex)) == 6,
        "exactly_three_rq_contribution_pairs": len(re.findall(r"\\item\s+\\textbf\{", intro)) == 3 and "exactly three research-question--contribution pairs" in intro,
        "continuous_title": not re.search(r"\\title\{[^}]*\\(?:\\|newline|linebreak)", main_tex, re.S),
        "references_absent_from_page_8": "References" not in page8,
        "references_begin_on_page_9": "References" in page9,
        "main_content_uses_eight_pages": "Trustworthiness, Limitations, and Conclusion" in page8,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "status": status,
        "policy": "Strict common cap: Trustworthy AI for Good permits eight content pages; SaTQuML permits nine. References and appendices are excluded.",
        "content_pages": 8 if checks["references_begin_on_page_9"] else None,
        "references_first_page": 9 if checks["references_begin_on_page_9"] else None,
        "total_pdf_pages": total_pages,
        "checks": checks,
    }
    AUDITS.mkdir(exist_ok=True)
    (AUDITS / "page_budget_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    rows = ["# Page-budget and structure audit", "", f"Status: **{status}**", "", report["policy"], "", f"Content/references/total pages: 8/9/{total_pages}.", "", "| Check | Result |", "|---|---:|"]
    rows.extend(f"| {key.replace('_', ' ')} | {'PASS' if value else 'FAIL'} |" for key, value in checks.items())
    (AUDITS / "page_budget_audit.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
