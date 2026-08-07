#!/usr/bin/env python3
"""Map rendered LaTeX figure numbers/pages to labels and source graphics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


AUX_FIGURE_RE = re.compile(
    r"\\newlabel\{(?P<label>fig:[^}]+)\}\{\{(?P<number>[^}]*)\}\{(?P<page>[^}]*)\}"
)
LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
GRAPHIC_RE = re.compile(r"\\includegraphics(?:\s*\[[^]]*\])?\s*\{([^}]+)\}")


def source_index(root: Path) -> dict[str, dict[str, str | None]]:
    index: dict[str, dict[str, str | None]] = {}
    for path in sorted(root.rglob("*.tex")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        labels = LABEL_RE.findall(text)
        if not labels:
            continue
        graphics = GRAPHIC_RE.findall(text)
        graphic = graphics[0] if len(graphics) == 1 else None
        for label in labels:
            if label.startswith("fig:"):
                index[label] = {
                    "source_tex": path.relative_to(root).as_posix(),
                    "graphic": graphic,
                }
    return index


def figure_map(root: Path, aux_name: str) -> dict:
    root = root.resolve()
    aux = (root / aux_name).resolve()
    if not aux.is_file():
        raise FileNotFoundError(f"Compiled auxiliary file not found: {aux}")
    aux_text = aux.read_text(encoding="utf-8", errors="replace")
    sources = source_index(root)
    rows = []
    for match in AUX_FIGURE_RE.finditer(aux_text):
        label = match.group("label")
        if label.endswith("@cref"):
            continue
        source = sources.get(label, {})
        rows.append(
            {
                "number": match.group("number"),
                "page": match.group("page"),
                "label": label,
                "source_tex": source.get("source_tex"),
                "graphic": source.get("graphic"),
            }
        )
    return {"root": str(root), "aux": aux_name, "count": len(rows), "figures": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Compiled Overleaf project root")
    parser.add_argument("--aux", default="main.aux", help="Auxiliary file relative to root")
    parser.add_argument("--json", type=Path, help="Optional JSON output path")
    args = parser.parse_args()
    try:
        result = figure_map(args.root, args.aux)
    except (FileNotFoundError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("| Figure | Page | Label | Source wrapper | Graphic |")
    print("| --- | --- | --- | --- | --- |")
    for item in result["figures"]:
        print(
            f"| {item['number']} | {item['page']} | {item['label']} | "
            f"{item['source_tex'] or 'unresolved'} | {item['graphic'] or 'unresolved'} |"
        )
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if result["count"] else 1


if __name__ == "__main__":
    sys.exit(main())
