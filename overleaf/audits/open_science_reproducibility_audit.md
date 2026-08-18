# Open-science and reproducibility audit

Status: **PASS within the stated evidence boundary**.

- Frozen outputs were not retuned. A fresh 32-row run reproduced all 704 values shared by the current 22-field runner and 30-field archive exactly; maximum absolute error is 0. The row-level rerun, sanitized environment/command manifest, and comparison summary are included.
- The diversity archive uses normalized fractions while the current runner emits counts. Those two archive-only fields are excluded from the 704-field claim rather than silently harmonized.
- Canonical records, summaries, configuration, reference registry, machine-readable table sources, and deterministic figure/table generators are committed. Headline values are generated from frozen data rather than copied into LaTeX.
- Figure 3 plots every frozen observation. Figures 1 and 2 distinguish conceptual/development content from frozen evidence and fabricate no observations.
- The fail-closed build creates, exports, hashes, decodes, and validates the original eight-asset SVG/transparent-PNG clip-art family before composing any diagram. The manifest records palette, geometry, placement, provenance, license, prompts/method, evidence boundary, and checksums.
- Requested prospective router baselines, gate ablations, risk–coverage curves, stronger solver portfolios, QPU results, and application outcomes were not reproducible without changing the frozen study; they are reported as future evaluations.
- Numerical, reference, visual-style, SVG-containment, page-budget, PDF-integrity, anonymity, package, and static release audits are executable with `make release-audit`.
- The targeted frozen experiment and eight positive/negative paper-Skill regressions pass. A broad supporting-repository discovery has an unrelated legacy sparse-tracking failure; Appendix E discloses it and the paper does not claim an entirely green supporting repository.
- Implementation licensing is MIT; the template is NeurIPS-provided; all new visuals are original vector geometry. The anonymous ZIP rejects symlinks/external leakage and omits identifying repository history.
