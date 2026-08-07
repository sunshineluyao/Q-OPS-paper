# Q-OPS NeurIPS 2026 source package

This package compiles the anonymous workshop submission and carries the frozen
evidence needed to audit every headline result.

## Compile on Overleaf

Upload the ZIP, select `main.tex` as the main document, and use pdfLaTeX.  The
six publication PDFs are already included, so Inkscape is not required on
Overleaf.

## Rebuild locally

Requirements: Python 3, NumPy, Inkscape, and a TeX distribution with
`latexmk`.

```bash
make
```

`scripts/make_figures.py` regenerates all editable SVG masters from the frozen
CSV.  `scripts/audit_reproduction.py` compares a fresh public-repository run
with the archived evidence on every field emitted by the current runner.

All six figures use original vector line icons generated in
`scripts/make_figures.py`; no external logos, raster illustrations, or traced
bitmaps are embedded.  Publication PDFs are exported from the live-text SVG
masters.  Visual release checks are performed against the rendered PDF figure
number and page, because LaTeX float order need not match source filenames.
Figure 3 and Figure 6 additionally declare each card label's SVG container and
clearance.  Re-run the renderer-measured containment checks with:

```bash
python3 scripts/audit_svg_text_containment.py \
  figs/fig2_benchmark_taxonomy.svg --require-annotations
python3 scripts/audit_svg_text_containment.py \
  figs/fig6_open_questions_map.svg --require-annotations
```

## Evidence snapshot

- Public implementation commit: `ae6a85f52fb5808e631bc0c4cfa43220c10ce9aa`
- Frozen instances: 32
- Evidence files: `data/locked_c12_records.csv`,
  `data/locked_c12_summary.json`, and `data/q_ops_global_c1_2_locked.json`
- Shared-field reproduction audit: `data/reproduction_audit.json`

For double-blind submission, `main.tex` deliberately identifies the public
artifact only as an anonymous supplementary artifact.  Insert the public URL
only if the venue permits a de-anonymized artifact or for the camera-ready
version.

## Claim boundary

The package supports a conditional, noiseless statevector concentration signal
on synthetic four-task retained sets under a matched 128-draw budget.  It does
not support real-QPU, wall-clock, scaling, workplace-safety, or universal
quantum-advantage claims.
