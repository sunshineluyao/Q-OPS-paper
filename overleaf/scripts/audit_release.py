#!/usr/bin/env python3
"""Deterministic numerical, structure, and anonymity checks for Q-OPS."""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "audits"


def close(a: float, b: float, tol: float = 5e-7) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main() -> int:
    records = list(csv.DictReader((ROOT / "data/locked_c12_records.csv").open(encoding="utf-8")))
    summary = json.loads((ROOT / "data/locked_c12_summary.json").read_text(encoding="utf-8"))
    source_files = [ROOT / "main.tex", ROOT / "checklist.tex", ROOT / "references.bib"]
    for folder in ("sections", "appendices", "tabs", "figs"):
        source_files.extend(sorted((ROOT / folder).glob("*.tex")))
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in source_files)
    main_tex = (ROOT / "main.tex").read_text(encoding="utf-8")
    intro = (ROOT / "sections/01_introduction.tex").read_text(encoding="utf-8")

    uniform = sum(float(row["uniform_optimal_probability"]) for row in records) / len(records)
    p2 = sum(float(row["qaoa_p2_optimal_probability"]) for row in records) / len(records)
    findings = {
        "record_count_32": len(records) == 32,
        "gate_count_9": sum(row["adoption_gate"].lower() == "true" for row in records) == 9,
        "strict_core_count_30": sum(float(row["strict_feasible_states"]) > 0 for row in records) == 30,
        "composite_feasible_count_27": sum(row["alns_feasible"].lower() == "true" for row in records) == 27,
        "zero_disallowed_mode_violations": sum(int(row["alns_hard_violations"]) for row in records) == 0,
        "mean_uniform_matches": close(uniform, float(summary["mean_uniform_optimal_probability"])),
        "mean_p2_matches": close(p2, float(summary["mean_qaoa_p2_optimal_probability"])),
        "ratio_6_831386": close(p2 / uniform, 6.831386, 5e-7),
        "exactly_six_numbered_section_inputs": len(re.findall(r"\\input\{sections/", main_tex)) == 6,
        "exactly_three_rq_pairs": len(re.findall(r"\\item\s+\\textbf\{", intro)) == 3 and "exactly three research-question--contribution pairs" in intro,
        "continuous_title": not re.search(r"\\title\{[^}]*\\(?:\\|newline|linebreak)", main_tex, re.S),
        "no_adopted_subset_misstatement": not re.search(r"6\.831.{0,80}(adopted|gate-positive)|(?:adopted|gate-positive).{0,80}6\.831", corpus, re.I | re.S),
        "shared_field_not_byte_identity_boundary": "not byte-identical CSV reproduction" in corpus and "does not claim byte identity" in corpus,
    }
    banned = {
        "personal_github_owner": r"sunshineluyao",
        "challenge_identity": r"\b(?:Vanguard|WISER)\b",
        "public_repo_url": r"github\.com/",
        "identifying_commit": r"ae6a85f|c10ce9aa",
        "institutional_identity": r"\bUniversity\s+of\b",
    }
    anonymity = {name: not re.search(pattern, corpus, re.I) for name, pattern in banned.items()}
    status = "PASS" if all(findings.values()) and all(anonymity.values()) else "FAIL"
    report = {
        "status": status,
        "computed": {
            "rows": len(records),
            "gate_positive": sum(row["adoption_gate"].lower() == "true" for row in records),
            "strict_core": sum(float(row["strict_feasible_states"]) > 0 for row in records),
            "composite_feasible": sum(row["alns_feasible"].lower() == "true" for row in records),
            "disallowed_mode_violations": sum(int(row["alns_hard_violations"]) for row in records),
            "mean_uniform_optimum_mass": uniform,
            "mean_p2_optimum_mass": p2,
            "ratio_of_means": p2 / uniform,
        },
        "checks": findings,
        "anonymity": anonymity,
    }
    AUDITS.mkdir(exist_ok=True)
    (AUDITS / "release_consistency.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
