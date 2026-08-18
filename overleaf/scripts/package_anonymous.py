#!/usr/bin/env python3
"""Create a deterministic, double-blind source-and-PDF supplement ZIP."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "packages/qops-anonymous-supplement.zip"
FILES = [
    "main.tex", "main.pdf", "main.bbl", "references.bib", "neurips_2026.sty", "checklist.tex",
    "Makefile", "ANONYMOUS_README.md",
]
DIRS = ["sections", "appendices", "tabs", "figs", "data", "assets/clip-art-set", "scripts"]
EXCLUDE_NAMES = {"__pycache__", ".DS_Store"}
EXCLUDE_SUFFIXES = {".aux", ".log", ".out", ".blg", ".fls", ".fdb_latexmk", ".synctex.gz"}
EXCLUDE_PATHS = {
    "data/reproduction_audit.json",
    "scripts/audit_release.py",
    "scripts/package_anonymous.py",
}


def allowed(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return rel not in EXCLUDE_PATHS and not any(part in EXCLUDE_NAMES for part in path.parts) and not any(path.name.endswith(s) for s in EXCLUDE_SUFFIXES)


def main() -> int:
    OUTPUT.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="qops-anonymous-") as tmp:
        stage = Path(tmp) / "qops-anonymous-supplement"
        stage.mkdir()
        for name in FILES:
            src = ROOT / name
            if src.is_file():
                shutil.copy2(src, stage / name)
        for dirname in DIRS:
            src_dir = ROOT / dirname
            for src in sorted(path for path in src_dir.rglob("*") if path.is_file() and allowed(path)):
                rel = src.relative_to(ROOT)
                dst = stage / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for src in sorted(path for path in stage.rglob("*") if path.is_file()):
                rel = src.relative_to(stage.parent).as_posix()
                info = zipfile.ZipInfo(rel, date_time=(2026, 8, 18, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, src.read_bytes(), compresslevel=9)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
