# Q-OPS NeurIPS 2026 source package

This package compiles one anonymous, eight-page-compatible NeurIPS 2026
workshop paper and carries the frozen evidence needed to audit every headline
result.

## Compile on Overleaf

Upload the ZIP, select `main.tex` as the main document, and use pdfLaTeX.  The
three publication PDFs are already included, so Inkscape is not required on
Overleaf.

## Rebuild locally

Requirements: Python 3, NumPy, Inkscape, and a TeX distribution with
`latexmk`.

```bash
make
```

The staged build first creates and validates the eight-asset technical clip-art
family, then composes all editable SVG masters and machine-readable table
sources from frozen inputs. `scripts/audit_reproduction.py` compares a fresh runner
with archived evidence on every field emitted by the current runner.

All figures and clip-art assets use original editable vector geometry; no
external logos, stock illustrations, raster masters, or traced bitmaps are
embedded. Publication PDFs are exported from live-text SVG masters. Every
figure text element is classified as container-owned or intentionally free.
Re-run renderer-measured containment checks with:

```bash
make release-audit
```

That target independently checks rendered SVG containment, the unified visual
contract, frozen/rerun numerical equality, cross-document headline values,
bibliographic existence and metadata, anonymity, eight-page body use, and the
static claim boundary. `make package` additionally writes the deterministic
anonymous supplement ZIP and its checksum.

## Evidence snapshot

- Identifying implementation commit: retained only in the non-anonymous external audit
- Frozen instances: 32
- Evidence files: `data/locked_c12_records.csv`,
  `data/locked_c12_summary.json`, and `data/q_ops_global_c1_2_locked.json`
- Fresh rerun rows: `data/locked_rerun_records.csv`
- Exact shared-field reproduction summary:
  `data/shared_field_reproduction.json`
- Sanitized environment and command record:
  `data/rerun_environment_manifest.json`

For double-blind submission, `main.tex` deliberately identifies the public
artifact only as an anonymous supplementary artifact.  Insert the public URL
only if the venue permits a de-anonymized artifact or for the camera-ready
version.

## Claim boundary

The package supports a conditional noiseless statevector concentration signal
across 32 synthetic four-task retained-core comparisons under a matched
128-draw budget. The 28.13% figure is a post-simulation evidence-gate rate, not
prospective adoption. It does not support real-QPU, wall-clock, scaling,
application-level, workplace-safety, or universal-advantage claims.
