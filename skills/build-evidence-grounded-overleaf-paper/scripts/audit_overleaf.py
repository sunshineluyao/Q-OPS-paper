#!/usr/bin/env python3
"""Static audit for a modular Overleaf/LaTeX project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
GRAPHIC_RE = re.compile(r"\\includegraphics(?:\s*\[[^]]*\])?\s*\{([^}]+)\}")
BIB_RE = re.compile(r"\\bibliography\s*\{([^}]+)\}")
ADDBIB_RE = re.compile(r"\\addbibresource(?:\s*\[[^]]*\])?\s*\{([^}]+)\}")
CITE_RE = re.compile(r"\\cite\w*(?:\s*\[[^]]*\]){0,2}\s*\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|pageref|autoref|cref|Cref|eqref)\s*\{([^}]+)\}")
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
TODO_RE = re.compile(r"\b(?:TODO|FIXME|TBD|XXX)\b", re.IGNORECASE)
MANUAL_TITLE_LAYOUT_RE = re.compile(
    r"\\\\|"
    r"\\(?:newline|linebreak|pagebreak|parbox|shortstack|makebox|mbox|raisebox|"
    r"resizebox|scalebox|vspace\*?|hspace\*?|kern|phantom)\b|"
    r"\\begin\s*\{(?:tabular\*?|minipage|array)\}",
    re.IGNORECASE,
)
GRAPHIC_EXTENSIONS = (".pdf", ".svg", ".png", ".jpg", ".jpeg", ".eps")
MASTER_EXTENSIONS = (".svg", ".drawio", ".tex", ".tikz", ".py", ".R", ".ipynb", ".pptx")
BUILD_SUFFIXES = (
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
)
BUILD_NAMES = {"missfont.log", "texput.log"}
SENSITIVE_NAMES = {".git", ".env", "credentials.json", "secrets.json"}


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None


def strip_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        cut = None
        for index, char in enumerate(line):
            if char == "%" and (index == 0 or line[index - 1] != "\\"):
                cut = index
                break
        lines.append(line if cut is None else line[:cut])
    return "\n".join(lines)


def is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def balanced_argument(text: str, start: int, opener: str, closer: str) -> tuple[str, int] | None:
    if start >= len(text) or text[start] != opener:
        return None
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == opener and not is_escaped(text, index):
            depth += 1
        elif char == closer and not is_escaped(text, index):
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    return None


def command_arguments(text: str, commands: list[str]) -> list[tuple[str, str]]:
    """Return balanced mandatory arguments for title-like commands."""
    if not commands:
        return []
    pattern = re.compile(r"\\(?P<command>" + "|".join(re.escape(item) for item in commands) + r")\b")
    found: list[tuple[str, str]] = []
    for match in pattern.finditer(text):
        cursor = match.end()
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor < len(text) and text[cursor] == "[":
            optional = balanced_argument(text, cursor, "[", "]")
            if optional is None:
                continue
            cursor = optional[1]
            while cursor < len(text) and text[cursor].isspace():
                cursor += 1
        mandatory = balanced_argument(text, cursor, "{", "}")
        if mandatory is not None:
            found.append((match.group("command"), mandatory[0]))
    return found


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def resolve_tex(target: str, current_dir: Path, root: Path) -> Path | None:
    raw = Path(target.strip())
    candidates: list[Path] = []
    for base in (current_dir, root):
        candidate = base / raw
        candidates.append(candidate)
        if not candidate.suffix:
            candidates.append(candidate.with_suffix(".tex"))
    return next((path.resolve() for path in candidates if path.is_file()), None)


def resolve_graphic(target: str, current_dir: Path, root: Path) -> Path | None:
    raw = Path(target.strip())
    candidates: list[Path] = []
    for base in (current_dir, root):
        candidate = base / raw
        candidates.append(candidate)
        if not candidate.suffix:
            candidates.extend(candidate.with_suffix(ext) for ext in GRAPHIC_EXTENSIONS)
    return next((path.resolve() for path in candidates if path.is_file()), None)


def resolve_bib(target: str, current_dir: Path, root: Path) -> Path | None:
    raw = Path(target.strip())
    for base in (current_dir, root):
        candidate = base / raw
        if not candidate.suffix:
            candidate = candidate.with_suffix(".bib")
        if candidate.is_file():
            return candidate.resolve()
    return None


def audit(root: Path, main: str, required_dirs: list[str], release: bool, title_commands: list[str]) -> dict:
    findings: list[Finding] = []
    root = root.resolve()
    main_path = (root / main).resolve()

    def add(severity: str, code: str, message: str, path: Path | None = None) -> None:
        findings.append(Finding(severity, code, message, relative(path, root) if path else None))

    if not root.is_dir():
        add("error", "root_missing", "Project root does not exist", root)
        return summarize(root, main, [], [], [], findings)
    if not main_path.is_file():
        add("error", "main_missing", f"Main TeX file does not exist: {main}", main_path)
        return summarize(root, main, [], [], [], findings)

    for directory in required_dirs:
        if directory and not (root / directory).is_dir():
            add("error", "required_dir_missing", f"Required directory is missing: {directory}", root / directory)

    queue = [main_path]
    visited: set[Path] = set()
    tex_text: dict[Path, str] = {}
    graphics: set[Path] = set()
    bib_files: set[Path] = set()

    while queue:
        tex_path = queue.pop()
        if tex_path in visited:
            continue
        visited.add(tex_path)
        try:
            text = strip_comments(tex_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            add("error", "tex_encoding", "TeX file is not valid UTF-8", tex_path)
            continue
        tex_text[tex_path] = text

        for target in INPUT_RE.findall(text):
            resolved = resolve_tex(target, tex_path.parent, root)
            if resolved is None:
                add("error", "input_missing", f"Missing \\input/\\include target: {target}", tex_path)
            elif root not in resolved.parents and resolved != root:
                add("error", "input_outside_root", f"Input resolves outside project: {target}", tex_path)
            else:
                queue.append(resolved)

        for target in GRAPHIC_RE.findall(text):
            resolved = resolve_graphic(target, tex_path.parent, root)
            if resolved is None:
                add("error", "graphic_missing", f"Missing graphic: {target}", tex_path)
            else:
                graphics.add(resolved)

        for group in BIB_RE.findall(text):
            for target in group.split(","):
                resolved = resolve_bib(target, tex_path.parent, root)
                if resolved is None:
                    add("error", "bibliography_missing", f"Missing bibliography: {target.strip()}", tex_path)
                else:
                    bib_files.add(resolved)
        for target in ADDBIB_RE.findall(text):
            resolved = resolve_bib(target, tex_path.parent, root)
            if resolved is None:
                add("error", "bibliography_missing", f"Missing bibliography: {target.strip()}", tex_path)
            else:
                bib_files.add(resolved)

    combined = "\n".join(tex_text.values())
    title_count = 0
    for tex_path, text in tex_text.items():
        for command, title in command_arguments(text, title_commands):
            title_count += 1
            violations = sorted(set(MANUAL_TITLE_LAYOUT_RE.findall(title)))
            if violations:
                rendered = ", ".join(repr(item) for item in violations)
                add(
                    "error" if release else "warning",
                    "manual_title_layout",
                    f"\\{command} must be continuous semantic text with natural template wrapping; found {rendered}",
                    tex_path,
                )
    if title_count > 1:
        add("error", "multiple_titles", f"Found {title_count} active title commands; expected one")
    labels: dict[str, list[Path]] = {}
    for tex_path, text in tex_text.items():
        for label in LABEL_RE.findall(text):
            labels.setdefault(label.strip(), []).append(tex_path)
        if TODO_RE.search(text):
            add("error" if release else "warning", "todo_marker", "Unresolved TODO/FIXME/TBD marker", tex_path)

    for label, locations in labels.items():
        if len(locations) > 1:
            add("error", "duplicate_label", f"Duplicate label '{label}' appears {len(locations)} times", locations[0])

    refs = {item.strip() for group in REF_RE.findall(combined) for item in group.split(",") if item.strip()}
    for ref in sorted(refs - set(labels)):
        add("error", "undefined_reference", f"Reference has no matching label: {ref}")

    cited = {item.strip() for group in CITE_RE.findall(combined) for item in group.split(",") if item.strip() and item.strip() != "*"}
    bib_keys: set[str] = set()
    for bib_path in bib_files:
        try:
            bib_keys.update(BIB_KEY_RE.findall(bib_path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            add("error", "bib_encoding", "Bibliography is not valid UTF-8", bib_path)
    if cited and not bib_files:
        add("error", "bibliography_absent", "Citations exist but no bibliography file was resolved")
    for key in sorted(cited - bib_keys):
        add("error", "citation_missing", f"Citation key is absent from bibliography: {key}")

    for graphic in sorted(graphics):
        if root not in graphic.parents and graphic != root:
            add("error", "graphic_outside_root", "Graphic resolves outside project", graphic)
            continue
        stem = graphic.with_suffix("")
        has_master = any(stem.with_suffix(ext).is_file() for ext in MASTER_EXTENSIONS)
        if graphic.suffix.lower() not in {".svg", ".tex", ".tikz"} and not has_master:
            add("warning", "editable_master_missing", "No same-stem editable figure master found", graphic)

    for path in root.rglob("*"):
        if any(part in SENSITIVE_NAMES for part in path.parts):
            add("error", "sensitive_path", "Sensitive or repository metadata path is inside package", path)
            continue
        if path.is_file() and (path.name in BUILD_NAMES or any(path.name.endswith(suffix) for suffix in BUILD_SUFFIXES)):
            add("error" if release else "warning", "build_artifact", "Build artifact should be excluded from release ZIP", path)

    if not bib_files:
        add("warning", "no_bibliography", "No bibliography file was found")
    if not graphics:
        add("warning", "no_graphics", "No included graphics were found")

    return summarize(root, main, visited, graphics, bib_files, findings)


def summarize(root: Path, main: str, tex_files, graphics, bib_files, findings: list[Finding]) -> dict:
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    return {
        "status": "PASS" if errors == 0 else "FAIL",
        "root": str(root),
        "main": main,
        "counts": {
            "tex_files": len(tex_files),
            "graphics": len(graphics),
            "bibliographies": len(bib_files),
            "errors": errors,
            "warnings": warnings,
        },
        "findings": [asdict(item) for item in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Overleaf project root")
    parser.add_argument("--main", default="main.tex", help="Main TeX file relative to root")
    parser.add_argument("--json", type=Path, help="Optional JSON report path")
    parser.add_argument(
        "--require-dirs",
        default="sections,appendices,figs,tabs",
        help="Comma-separated required directories; pass an empty string for none",
    )
    parser.add_argument("--release", action="store_true", help="Treat TODOs and build artifacts as errors")
    parser.add_argument(
        "--title-commands",
        default="title,icmltitle,papertitle",
        help="Comma-separated title macros whose arguments must not contain manual layout commands",
    )
    args = parser.parse_args()
    required = [item.strip() for item in args.require_dirs.split(",") if item.strip()]
    title_commands = [item.strip().lstrip("\\") for item in args.title_commands.split(",") if item.strip()]
    result = audit(args.root, args.main, required, args.release, title_commands)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
