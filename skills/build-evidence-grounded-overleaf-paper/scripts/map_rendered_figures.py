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
FIGURE_ENV_RE = re.compile(
    r"\\begin\s*\{(?P<kind>figure\*?)\}(?P<body>.*?)\\end\s*\{(?P=kind)\}", re.DOTALL
)


def strip_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        cursor = 0
        while True:
            index = line.find("%", cursor)
            if index < 0:
                lines.append(line)
                break
            backslashes = 0
            pointer = index - 1
            while pointer >= 0 and line[pointer] == "\\":
                backslashes += 1
                pointer -= 1
            if backslashes % 2 == 0:
                lines.append(line[:index])
                break
            cursor = index + 1
    return "\n".join(lines)


def source_index(root: Path) -> dict[str, dict[str, object]]:
    """Associate each figure label with graphics in its enclosing environment."""
    index: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*.tex")):
        try:
            text = strip_comments(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
        relative_path = path.relative_to(root).as_posix()
        enclosed_labels: set[str] = set()
        for environment in FIGURE_ENV_RE.finditer(text):
            body = environment.group("body")
            labels = [label for label in LABEL_RE.findall(body) if label.startswith("fig:")]
            graphics = GRAPHIC_RE.findall(body)
            for label in labels:
                enclosed_labels.add(label)
                index[label] = {
                    "source_tex": relative_path,
                    "graphic": graphics[0] if len(graphics) == 1 else None,
                    "graphics": graphics,
                    "resolution_error": None if graphics else "figure environment has no graphic",
                }
        for label in LABEL_RE.findall(text):
            if label.startswith("fig:") and label not in enclosed_labels:
                index[label] = {
                    "source_tex": relative_path,
                    "graphic": None,
                    "graphics": [],
                    "resolution_error": "figure label is not enclosed by a figure environment",
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
        graphics = source.get("graphics", [])
        if not isinstance(graphics, list):
            graphics = []
        resolved = bool(source.get("source_tex") and graphics)
        rows.append(
            {
                "number": match.group("number"),
                "page": match.group("page"),
                "label": label,
                "source_tex": source.get("source_tex"),
                "graphic": source.get("graphic"),
                "graphics": graphics,
                "status": "resolved" if resolved else "unresolved",
                "resolution_error": source.get("resolution_error")
                or (None if resolved else "label was not found in a source figure environment"),
            }
        )
    unresolved = [row["label"] for row in rows if row["status"] != "resolved"]
    return {
        "root": str(root),
        "aux": aux_name,
        "count": len(rows),
        "resolved_count": len(rows) - len(unresolved),
        "unresolved_count": len(unresolved),
        "unresolved_labels": unresolved,
        "figures": rows,
    }


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

    print("| Figure | Page | Label | Source wrapper | Graphic(s) | Status |")
    print("| --- | --- | --- | --- | --- | --- |")
    for item in result["figures"]:
        graphics = ", ".join(item["graphics"]) if item["graphics"] else "unresolved"
        print(
            f"| {item['number']} | {item['page']} | {item['label']} | "
            f"{item['source_tex'] or 'unresolved'} | {graphics} | {item['status']} |"
        )
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if result["count"] and result["unresolved_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
