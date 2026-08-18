#!/usr/bin/env python3
"""Cross-check frozen evidence, rerun records, and every headline claim."""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "audits"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def equal_value(left: str, right: str) -> bool:
    if left == right:
        return True
    try:
        return float(left) == float(right)
    except ValueError:
        return left.lower() == right.lower()


def main() -> int:
    archive = rows(ROOT / "data/locked_c12_records.csv")
    rerun = rows(ROOT / "data/locked_rerun_records.csv")
    summary = json.loads((ROOT / "data/locked_c12_summary.json").read_text(encoding="utf-8"))
    reproduction = json.loads((ROOT / "data/shared_field_reproduction.json").read_text(encoding="utf-8"))
    environment = json.loads((ROOT / "data/rerun_environment_manifest.json").read_text(encoding="utf-8"))
    key = lambda row: (row["n_tasks"], row["doping_level"], row["seed"])
    archive_by_key = {key(row): row for row in archive}
    rerun_by_key = {key(row): row for row in rerun}
    shared = [field for field in rerun[0] if field in archive[0]]
    comparisons = 0
    mismatches: list[dict[str, str]] = []
    for record_key, fresh in rerun_by_key.items():
        old = archive_by_key.get(record_key, {})
        for field in shared:
            comparisons += 1
            if not equal_value(old.get(field, "<missing>"), fresh[field]):
                mismatches.append({"key": "/".join(record_key), "field": field, "archive": old.get(field, "<missing>"), "rerun": fresh[field]})

    n = len(archive)
    gate = sum(row["adoption_gate"].lower() == "true" for row in archive)
    composite = sum(row["alns_feasible"].lower() == "true" for row in archive)
    disallowed = sum(int(row["alns_hard_violations"]) for row in archive)
    strict = sum(float(row["strict_feasible_states"]) > 0 for row in archive)
    adverse_depth = sum(float(row["qaoa_p1_optimal_probability"]) > float(row["qaoa_p2_optimal_probability"]) for row in archive)
    uniform = sum(float(row["uniform_optimal_probability"]) for row in archive) / n
    p2 = sum(float(row["qaoa_p2_optimal_probability"]) for row in archive) / n
    ratio = p2 / uniform

    source_paths = [path for path in (ROOT / "main.tex", ROOT / "README.md", ROOT / "ANONYMOUS_README.md") if path.exists()]
    for dirname in ("sections", "appendices", "tabs", "figs"):
        source_paths.extend(sorted((ROOT / dirname).glob("*.tex")))
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)
    abstract = (ROOT / "main.tex").read_text(encoding="utf-8").split("\\begin{abstract}", 1)[1].split("\\end{abstract}", 1)[0]
    table_csv = (ROOT / "data/table2_results.csv").read_text(encoding="utf-8")
    checks = {
        "frozen_rows_32": n == 32,
        "strict_core_30_of_32": strict == 30,
        "post_simulation_gate_9_of_32": gate == 9,
        "composite_feasible_27_of_32": composite == 27,
        "zero_disallowed_mode_violations": disallowed == 0,
        "adverse_depth_28_of_32": adverse_depth == 28,
        "ratio_of_all_instance_exact_means_6_831386": math.isclose(ratio, 6.8313862792145175, rel_tol=0.0, abs_tol=1e-15),
        "abstract_labels_ratio_exact_and_all_instance": "Across all retained-core comparisons" in abstract and "ratio of exact optimum masses" in abstract and "6.831" in abstract,
        "abstract_separates_matched_draws": "distinct from the matched 128-draw outcomes" in abstract,
        "no_adopted_subset_ratio_claim": not re.search(r"6\.831.{0,100}(?:adopted|gate-positive)|(?:adopted|gate-positive).{0,100}6\.831", corpus, re.I | re.S),
        "gate_always_labeled_post_simulation": "post-simulation evidence gate" in corpus.lower() and "Post-simulation; not prospective" in corpus,
        "table_contains_ratio_and_scope": "Ratio of exact means,6.831$\\times$,All 32 retained-core comparisons; no CI" in table_csv,
        "table_contains_composite_and_violation_rows": "Composite-feasible incumbent,27/32" in table_csv and "Disallowed-mode violations,0/32" in table_csv,
        "rerun_key_set_exact": set(archive_by_key) == set(rerun_by_key),
        "shared_field_count_22": len(shared) == 22,
        "shared_comparisons_704": comparisons == 704,
        "shared_values_exact": not mismatches,
        "published_reproduction_summary_matches": reproduction.get("shared_value_comparisons") == 704 and reproduction.get("mismatch_count") == 0 and reproduction.get("max_absolute_error") == 0,
        "summary_means_match_records": math.isclose(uniform, summary["mean_uniform_optimal_probability"], rel_tol=0.0, abs_tol=1e-15) and math.isclose(p2, summary["mean_qaoa_p2_optimal_probability"], rel_tol=0.0, abs_tol=1e-15),
        "reported_rerun_runtime_matches_manifest": f"{environment['runtime_observation']['wall_seconds']:.3f} seconds wall-clock" in corpus,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "status": status,
        "computed": {
            "instances": n,
            "strict_core_instances": strict,
            "post_simulation_gate_positive": gate,
            "composite_feasible_incumbents": composite,
            "disallowed_mode_violations": disallowed,
            "p1_greater_than_p2_instances": adverse_depth,
            "mean_uniform_exact_optimum_mass": uniform,
            "mean_p2_exact_optimum_mass": p2,
            "ratio_of_means": ratio,
            "shared_fields": len(shared),
            "shared_value_comparisons": comparisons,
            "mismatch_count": len(mismatches),
            "max_abs_error": 0.0 if not mismatches else None,
        },
        "claim_boundary": "Frozen, synthetic, retained-core, noiseless statevector evidence only. The 9/32 gate is retrospective; 6.831x is an all-32 ratio of exact distribution masses, not an adopted-subset or matched-draw estimate.",
        "checks": checks,
        "mismatches": mismatches[:20],
    }
    AUDITS.mkdir(exist_ok=True)
    (AUDITS / "quantitative_consistency_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Quantitative and cross-document consistency audit", "", f"Status: **{status}**", "", report["claim_boundary"], "", "| Computed item | Value |", "|---|---:|"]
    lines.extend(f"| {name.replace('_', ' ')} | {value} |" for name, value in report["computed"].items())
    lines += ["", "| Release check | Result |", "|---|---:|"]
    lines.extend(f"| {name.replace('_', ' ')} | {'PASS' if value else 'FAIL'} |" for name, value in checks.items())
    (AUDITS / "numerical_consistency_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
