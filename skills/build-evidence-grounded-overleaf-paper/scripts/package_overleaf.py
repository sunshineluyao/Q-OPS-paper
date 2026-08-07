#!/usr/bin/env python3
"""Create a clean, deterministic Overleaf ZIP from a paper source tree."""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path


EXCLUDED_DIRS = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache", ".idea", ".vscode"}
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db", ".env", "credentials.json", "secrets.json", "missfont.log", "texput.log"}
EXCLUDED_SUFFIXES = (
    ".aux",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".synctex.gz",
    ".toc",
    ".lof",
    ".lot",
    ".pyc",
    ".pyo",
)
FIXED_TIME = (2020, 1, 1, 0, 0, 0)


def is_excluded(path: Path, root: Path, main_stem: str, keep_bbl: bool, include_compiled_pdf: bool) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return True
    if path.name in EXCLUDED_NAMES or any(path.name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return True
    if path.suffix == ".bbl" and not keep_bbl:
        return True
    if relative.parent == Path(".") and path.name == f"{main_stem}.pdf" and not include_compiled_pdf:
        return True
    return False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Overleaf source root")
    parser.add_argument("output", type=Path, help="Output ZIP path")
    parser.add_argument("--main", default="main.tex", help="Main TeX file relative to root")
    parser.add_argument("--keep-bbl", action="store_true", help="Keep generated .bbl files")
    parser.add_argument("--include-compiled-pdf", action="store_true", help="Include the root-level compiled main PDF")
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()
    main_path = root / args.main
    if not root.is_dir() or not main_path.is_file():
        print(f"error: missing source root or main file: {main_path}", file=sys.stderr)
        return 2
    if output == root or root in output.parents:
        print("error: output ZIP must be outside the source tree", file=sys.stderr)
        return 2

    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and not is_excluded(path, root, main_path.stem, args.keep_bbl, args.include_compiled_pdf)
    ]
    if not files:
        print("error: no files selected for packaging", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
            arcname = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(arcname, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    print(f"created={output}")
    print(f"files={len(files)}")
    print(f"sha256={sha256(output)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
