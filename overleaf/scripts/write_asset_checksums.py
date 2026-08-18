#!/usr/bin/env python3
"""Write a stable checksum ledger for manuscript evidence and visual assets."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "audits"
PATTERNS = (
    "figs/fig[123]_*.svg", "figs/fig[123]_*.pdf", "figs/fig[123]_*.tex",
    "tabs/table1_decision_environment.tex", "tabs/table2_results.tex", "data/table*.csv",
    "assets/clip-art-set/assets/*.svg", "assets/clip-art-set/assets/*.png",
    "assets/clip-art-set/contact-sheet.svg", "assets/clip-art-set/contact-sheet.png",
    "assets/clip-art-set/clip-art-manifest.json", "assets/clip-art-set/*.md",
    "data/locked_c12_records.csv", "data/locked_c12_summary.json", "data/locked_rerun_records.csv",
    "data/locked_rerun_summary.json", "data/shared_field_reproduction.json", "data/rerun_environment_manifest.json",
    "data/reference_registry.json", "scripts/generate_release_assets.py", "scripts/finalize_asset_manifest.py",
)


def main() -> int:
    paths = sorted({path for pattern in PATTERNS for path in ROOT.glob(pattern) if path.is_file()})
    lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}" for path in paths]
    AUDITS.mkdir(exist_ok=True)
    (AUDITS / "asset_checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} checksums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
