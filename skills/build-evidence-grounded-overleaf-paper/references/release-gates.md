# Paper release gates

Pass every applicable gate before calling a paper final. Record `PASS`, `CAVEAT`, `FAIL`, or `N/A` with evidence.

## 1. Authority and venue

- Official venue template is present and is the active style.
- Current page-count, anonymity, supplementary-material, and checklist rules are verified.
- Main-content boundary is checked by rendered page, not guessed from source length.
- Camera-ready identity and double-blind identity are not accidentally mixed.

## 2. Evidence and reproducibility

- Paper-critical code/data/config version is pinned.
- Headline metrics trace to machine-readable evidence.
- Relevant tests and the fresh rerun pass, or failures are disclosed.
- Fresh output uses a new directory and does not overwrite frozen evidence.
- Archived-versus-rerun comparison states keys, shared schema, tolerance, and mismatch count.
- Environment, dependencies, seeds, hardware, runtime, and fallback behavior are recorded.
- Adverse and null findings that limit the claim are retained.
- Repository-wide health is not conflated with the paper-critical path.

## 3. Writing and mathematics

- Title is one continuous semantic string with natural template wrapping; no manual line break, parbox, shortstack, tabular, spacing, or resize command appears inside the active title macro.
- Abstract contains problem, gap, method, quantitative result, boundary, and impact.
- Contributions are distinct, evidenced, and echoed in experiments/results.
- Every objective, constraint, metric, and strategy has a definition and implementation trace.
- Main text groups complexity into a small number of interpretable families.
- Appendices contain detailed formula and variable glossaries.
- Results explain meaning rather than only repeat table values.
- Limitations distinguish current evidence from deployment claims.

## 4. Literature and bibliography

- Every reference is real and bibliographically verified.
- Foundational claims cite primary work; current rules and standards cite official pages.
- No citation key is missing or undefined.
- No novelty claim exceeds the documented search.
- Literature relationship figure agrees with the related-work text and bibliography.

## 5. Figures and tables

- Every evidence-bearing figure has an editable master and publication PDF.
- Quantitative figures regenerate from frozen data.
- One figure manifest records message, evidence source/status, target width, master/export, compiled label/number/page/source, icon family, and each QA result.
- A compiled map resolves every rendered figure number/page to its label, source wrapper, and enclosing graphic or graphic set; any unresolved entry is a hard failure.
- Reference images contribute composition grammar only; no traced or embedded reference raster remains.
- Technical icons use one consistent vector system and do not imply unsupported evidence or certification.
- Connectors are behind nodes, routed through reserved whitespace, and terminate at boundaries/ports; no floating arrowhead remains.
- No clipping, overlap, boundary-touching text, status-badge/title collision, illegible type, connector-through-label defect, or deceptive axis remains.
- Every in-shape SVG text block has a renderer-measured bounding box inside its declared container and clearance padding; circles, ellipses, and rounded rectangles are checked against their true curved boundary rather than an outer box.
- Every SVG text element is explicitly classified as container-bound or intentionally free; the containment check's positive fixture passes and deliberately narrowed negative fixture fails.
- Final-size single/double-column render is readable.
- Every figure passes editable-master/structure, standalone export, final-size, and full-page clean-room PDF inspection under its rendered figure number.
- Captions are self-contained and state evidence scope.
- Observed, inferred, hypothetical, and future elements are visually distinct.
- Tables fit the page and do not duplicate paragraphs unnecessarily.

## 6. LaTeX and PDF

- Clean compilation completes with the venue-supported engine.
- Bibliography and cross-references stabilize after the required passes.
- No missing file, undefined citation/reference, duplicate label, or fatal warning remains.
- Stable compile-log audit reports no fatal error, missing glyph, rerun request, undefined citation/reference, duplicate label, or overfull box; its positive/negative self-test passes, and underfull boxes are reviewed individually.
- Every rendered page is inspected for floats, equations, captions, and anonymity.
- PDF metadata does not reveal identity in double-blind mode.
- Fonts are embedded and figures render correctly.
- `pdfinfo` succeeds on intended and clean-room PDFs; page counts agree, every page rasterizes, and a page-pixel comparison finds no visual mismatch.

## 7. Overleaf package

- ZIP contains source, official style/checklist, bibliography, tables, figures, and required compact evidence/scripts.
- ZIP excludes `.git`, credentials, private data, caches, auxiliary build files, and unrelated repository content.
- Packaging rejects every symlink before reading file contents and verifies selected files remain inside the source root.
- ZIP extracts without path traversal or nested-root confusion.
- Extracted ZIP compiles independently in a fresh directory.
- Clean-room PDF is visually identical to the intended release even when metadata prevents byte identity.
- Final ZIP and PDF checksums are recorded; repeated deterministic packaging yields the same ZIP checksum.

## 8. Audit report and handoff

- Report states provenance, tests, reruns, comparison method, compute, and versions.
- Report separates supported wording from prohibited overclaims.
- Report discloses caveats, failed cases, and unresolved TODOs.
- Report states whether upstream/external resources were modified.
- Final response links all deliverables and summarizes the main claim and limitation.

Any title-layout, visual-containment, connector, clipping, clean-room compilation, page-count, or PDF-render defect is `FAIL`, never a releasable `CAVEAT`. Do not call the artifact final until these failures are repaired and the full gate sequence is rerun.
