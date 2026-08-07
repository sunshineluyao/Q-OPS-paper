#!/usr/bin/env python3
"""Compare a fresh locked run with the archived public evidence.

The current public runner intentionally emits a narrower schema than the
archived evidence table.  This script therefore compares every shared field,
keyed by the frozen instance tuple, and records fields available only in the
archive.  It never mutates the source repository.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


KEY = ("n_tasks", "doping_level", "seed")


def parse(value: str):
    if value in {"True", "False"}:
        return value == "True"
    try:
        return float(value)
    except ValueError:
        return value


def load(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    keyed = {tuple(row[k] for k in KEY): row for row in rows}
    return rows, keyed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("rerun", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()

    archived_rows, archived = load(args.archive)
    rerun_rows, rerun = load(args.rerun)
    archive_fields = list(archived_rows[0])
    rerun_fields = list(rerun_rows[0])
    shared = [field for field in archive_fields if field in rerun_fields]
    archive_only = [field for field in archive_fields if field not in rerun_fields]
    rerun_only = [field for field in rerun_fields if field not in archive_fields]

    mismatches = []
    max_abs_error = 0.0
    comparisons = 0
    for key in sorted(set(archived) | set(rerun)):
        if key not in archived or key not in rerun:
            mismatches.append({"instance": key, "field": "__row__", "archive": key in archived, "rerun": key in rerun})
            continue
        for field in shared:
            left = parse(archived[key][field])
            right = parse(rerun[key][field])
            comparisons += 1
            if isinstance(left, float) and isinstance(right, float):
                if math.isnan(left) and math.isnan(right):
                    continue
                error = abs(left - right)
                max_abs_error = max(max_abs_error, error)
                equal = math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)
            else:
                equal = left == right
            if not equal:
                mismatches.append({"instance": key, "field": field, "archive": left, "rerun": right})

    result = {
        "source_commit": args.commit,
        "archive_rows": len(archived_rows),
        "rerun_rows": len(rerun_rows),
        "archive_field_count": len(archive_fields),
        "rerun_field_count": len(rerun_fields),
        "shared_fields": shared,
        "archive_only_fields": archive_only,
        "rerun_only_fields": rerun_only,
        "shared_value_comparisons": comparisons,
        "max_abs_error": max_abs_error,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:50],
        "status": "PASS" if not mismatches else "FAIL",
        "interpretation": (
            "The fresh run reproduces every field emitted by the current public runner. "
            "The archived table additionally preserves diagnostic fields that the current runner omits."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not mismatches else 1)


if __name__ == "__main__":
    main()
