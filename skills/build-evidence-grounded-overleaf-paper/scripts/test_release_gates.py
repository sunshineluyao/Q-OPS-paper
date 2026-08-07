#!/usr/bin/env python3
"""Regression tests for the evidence-grounded paper release utilities."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parent


def load_script(name: str):
    module_name = f"paper_release_gate_{name}"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_DIR / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


SVG = load_script("audit_svg_text_containment")
PDF = load_script("compare_pdf_renders")
OVERLEAF = load_script("audit_overleaf")
PACKAGE = load_script("package_overleaf")
FIGURES = load_script("map_rendered_figures")
LATEX_LOG = load_script("audit_latex_log")


class ReleaseGateRegressionTests(unittest.TestCase):
    def test_svg_json_keeps_record_count_and_records(self) -> None:
        records = [{"status": "PASS", "container_id": "box"}]
        payload = SVG.summarize_records([Path("figure.svg")], records)
        self.assertEqual(payload["record_count"], 1)
        self.assertIs(payload["records"], records)

    def test_pdf_compare_works_with_legacy_zip_signature(self) -> None:
        pages = [
            {"page": 1, "sha256": "a", "bytes": 1},
            {"page": 2, "sha256": "b", "bytes": 1},
        ]

        def legacy_zip(first, second):
            return zip(first, second)

        with (
            mock.patch.object(PDF, "page_count", side_effect=[2, 2]),
            mock.patch.object(PDF, "render", side_effect=[pages, list(pages)]),
            mock.patch.object(PDF, "zip", legacy_zip, create=True),
        ):
            result = PDF.compare(Path("expected.pdf"), Path("actual.pdf"), 180, "pdfinfo", "pdftoppm")
        self.assertEqual(result["status"], "PASS")

    def test_starred_title_manual_break_is_rejected(self) -> None:
        source = r"\title*{A Manual\\Break}"
        self.assertEqual(OVERLEAF.command_arguments(source, ["title"]), [("title", r"A Manual\\Break")])
        with tempfile.TemporaryDirectory(prefix="title-audit-test-") as tmp:
            root = Path(tmp)
            (root / "main.tex").write_text(source + "\n", encoding="utf-8")
            result = OVERLEAF.audit(root, "main.tex", [], True, ["title"])
        codes = {item["code"] for item in result["findings"]}
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("manual_title_layout", codes)

    def test_packager_rejects_external_file_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="package-symlink-test-") as tmp:
            base = Path(tmp)
            root = base / "paper"
            root.mkdir()
            (root / "main.tex").write_text("paper\n", encoding="utf-8")
            private = base / "private.txt"
            private.write_text("do not package\n", encoding="utf-8")
            (root / "leak.txt").symlink_to(private)
            with self.assertRaisesRegex(ValueError, "symlink"):
                PACKAGE.collect_files(root.resolve(), "main", False, False)

    def test_multiple_figure_environments_map_independently(self) -> None:
        with tempfile.TemporaryDirectory(prefix="figure-map-test-") as tmp:
            root = Path(tmp)
            (root / "figures.tex").write_text(
                r"""\begin{figure}
\includegraphics{first.pdf}
\label{fig:first}
\end{figure}
\begin{figure*}
\includegraphics{second.pdf}
\label{fig:second}
\end{figure*}
""",
                encoding="utf-8",
            )
            (root / "main.aux").write_text(
                r"\newlabel{fig:first}{{1}{2}}" "\n" r"\newlabel{fig:second}{{2}{3}}" "\n",
                encoding="utf-8",
            )
            result = FIGURES.figure_map(root, "main.aux")
        self.assertEqual(result["unresolved_count"], 0)
        self.assertEqual([row["graphics"] for row in result["figures"]], [["first.pdf"], ["second.pdf"]])

    def test_unresolved_figure_is_a_failure_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="figure-map-unresolved-test-") as tmp:
            root = Path(tmp)
            (root / "main.tex").write_text("paper\n", encoding="utf-8")
            (root / "main.aux").write_text(r"\newlabel{fig:missing}{{1}{1}}" "\n", encoding="utf-8")
            result = FIGURES.figure_map(root, "main.aux")
        self.assertEqual(result["unresolved_count"], 1)
        self.assertEqual(result["figures"][0]["status"], "unresolved")

    def test_outline_rerun_request_fails_log_audit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="latex-log-rerun-test-") as tmp:
            log = Path(tmp) / "main.log"
            log.write_text(
                "Package rerunfilecheck Warning: File `main.out' has changed.\n"
                "Rerun to get outlines right\n"
                "Output written on main.pdf (2 pages, 100 bytes).\n",
                encoding="utf-8",
            )
            result = LATEX_LOG.audit(log, allow_overfull=False, fail_underfull=False)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("rerun_required", {item["code"] for item in result["findings"]})

    def test_curved_and_rounded_boundaries_reject_corner_text(self) -> None:
        fixtures = [
            (ET.fromstring('<circle cx="50" cy="50" r="50"/>'), (90.0, 5.0, 5.0, 5.0)),
            (ET.fromstring('<ellipse cx="60" cy="40" rx="60" ry="40"/>'), (105.0, 3.0, 5.0, 5.0)),
            (
                ET.fromstring('<rect x="0" y="0" width="100" height="60" rx="20" ry="20"/>'),
                (1.0, 1.0, 5.0, 5.0),
            ),
        ]
        for shape, text_box in fixtures:
            with self.subTest(shape=SVG.local_name(shape.tag)):
                failures, _ = SVG.shape_boundary_failures(shape, text_box, 0.0, 0.0)
                self.assertTrue(failures)
                center_failures, _ = SVG.shape_boundary_failures(shape, (45.0, 25.0, 5.0, 5.0), 0.0, 0.0)
                self.assertFalse(center_failures)


if __name__ == "__main__":
    unittest.main(verbosity=2)
