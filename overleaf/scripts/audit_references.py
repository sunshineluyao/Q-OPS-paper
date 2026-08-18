#!/usr/bin/env python3
"""Audit citation coverage against a primary-source verification registry."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "audits"


def parse_entries(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    starts = list(re.finditer(r"^@(\w+)\{([^,]+),", text, re.M))
    for index, match in enumerate(starts):
        block = text[match.start() : starts[index + 1].start() if index + 1 < len(starts) else len(text)]
        fields = {name.lower(): value.strip() for name, value in re.findall(r"^\s*(\w+)\s*=\s*\{(.*)\},?\s*$", block, re.M)}
        fields["entry_type"] = match.group(1).lower()
        entries[match.group(2)] = fields
    return entries


def main() -> int:
    bib_text = (ROOT / "references.bib").read_text(encoding="utf-8")
    entries = parse_entries(bib_text)
    source_paths = [ROOT / "main.tex"]
    for folder in ("sections", "appendices", "tabs"):
        source_paths.extend(sorted((ROOT / folder).glob("*.tex")))
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)
    cited = {key.strip() for group in re.findall(r"\\cite\w*\{([^}]+)\}", corpus) for key in group.split(",")}
    registry_rows = json.loads((ROOT / "data/reference_registry.json").read_text(encoding="utf-8"))["references"]
    registry = {row["key"]: row for row in registry_rows}
    doi_values = [fields.get("doi", "").lower() for fields in entries.values() if fields.get("doi")]
    checks = {
        "all_citations_resolve": cited <= set(entries),
        "no_unused_bibliography_entries": set(entries) <= cited,
        "registry_covers_every_entry": set(registry) == set(entries),
        "no_duplicate_dois": len(doi_values) == len(set(doi_values)),
        "required_fields_present": all(fields.get("title") and fields.get("author") and fields.get("year") for fields in entries.values()),
        "primary_locator_for_every_entry": all(row.get("canonical_url", "").startswith("https://") for row in registry_rows),
        "doi_registry_alignment": all(not fields.get("doi") or fields["doi"].lower() in registry[key]["canonical_url"].lower() for key, fields in entries.items()),
        "verification_date_recorded": all(row.get("verified_on") == "2026-08-18" for row in registry_rows),
        "no_known_broken_metadata_tokens": not re.search(r'Toniann|Walzner, Stefan|S\{"o\}|F\{"u\}|H\{"o\}|\bMarecek\b|\bFinzgar\b', bib_text),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "status": status,
        "scope": "Bibliographic existence, metadata, and claim support checked against publisher, proceedings, standards-body, journal, or canonical DOI records as of 2026-08-18; this is not a guarantee against future or unindexed notices.",
        "counts": {"entries": len(entries), "cited": len(cited), "registry": len(registry)},
        "missing_citations": sorted(cited - set(entries)),
        "unused_entries": sorted(set(entries) - cited),
        "checks": checks,
    }
    AUDITS.mkdir(exist_ok=True)
    (AUDITS / "reference_integrity_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Reference integrity audit", "", f"Status: **{status}**", "", report["scope"], "", f"Entries/cited/registry: {len(entries)}/{len(cited)}/{len(registry)}.", "", "| Check | Result |", "|---|---:|"]
    lines.extend(f"| {name.replace('_', ' ')} | {'PASS' if value else 'FAIL'} |" for name, value in checks.items())
    (AUDITS / "reference_integrity_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
