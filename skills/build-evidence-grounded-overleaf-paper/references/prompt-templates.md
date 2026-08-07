# Reusable prompts for evidence-grounded paper production

## Contents

1. Variable sheet
2. Master production prompt
3. Evidence audit prompt
4. Paper architecture prompt
5. Figure and table prompt
6. Revision prompt
7. Final release prompt

These prompts are planning frames. Replace all `{{...}}` variables, delete inapplicable clauses, and preserve explicit non-claims. Do not paste project-specific numbers until they have been verified.

## 1. Variable sheet

| Variable | Meaning |
| --- | --- |
| `{{PROJECT_NAME}}` | Short project/paper identifier |
| `{{TARGET_VENUE}}` | Venue, track, year, and submission type |
| `{{OFFICIAL_TEMPLATE}}` | Local path or official URL for venue source files |
| `{{PAGE_RULE}}` | Main-page limit and whether references/appendices count |
| `{{ANONYMITY_MODE}}` | Double-blind, single-blind, or camera-ready |
| `{{SOURCE_DOCUMENTS}}` | Briefs, prior drafts, requirements, reviewer comments |
| `{{AUTHORITATIVE_REPOS}}` | Repositories/commits; state read-only or write authority |
| `{{DATA_AND_RESULTS}}` | Raw data, configs, frozen outputs, tables, logs |
| `{{RESEARCH_QUESTION}}` | Primary question and intended audience |
| `{{CONTRIBUTIONS}}` | Desired contribution structure, usually three items |
| `{{CLAIM_BOUNDARIES}}` | Statements that must not be made |
| `{{REQUIRED_VISUALS}}` | Teaser, taxonomy, pipeline, results, literature map, etc. |
| `{{REQUIRED_DELIVERABLES}}` | ZIP, PDF, audit report, figure sources, supplementary files |
| `{{OUTPUT_BASENAME}}` | Stable artifact naming stem |
| `{{DO_NOT_MUTATE}}` | Repositories/files/services that must remain unchanged |

## 2. Master production prompt

```markdown
Act as an interdisciplinary senior author, evidence auditor, reproducibility engineer, LaTeX production editor, and publication-quality vector-figure designer.

Goal: transform the supplied materials into a submission-ready paper for {{TARGET_VENUE}}. Use {{OFFICIAL_TEMPLATE}} and comply with {{PAGE_RULE}} under {{ANONYMITY_MODE}}.

Authoritative inputs:
- source documents: {{SOURCE_DOCUMENTS}}
- implementation repositories: {{AUTHORITATIVE_REPOS}}
- data/configurations/results: {{DATA_AND_RESULTS}}
- primary research question: {{RESEARCH_QUESTION}}
- intended contributions: {{CONTRIBUTIONS}}
- mandatory claim boundaries: {{CLAIM_BOUNDARIES}}
- resources that must remain unchanged: {{DO_NOT_MUTATE}}

Operating rules:
1. Treat executable code, frozen configurations, raw data, and direct reruns as stronger evidence than README files, reports, or prior prose.
2. Keep upstream repositories read-only unless explicitly authorized. Run all experiments into fresh output paths.
3. Verify every headline number, formula, reference, venue rule, and priority claim. Never fabricate a result or citation; use a visible TODO when blocked.
4. Retain negative, null, fallback, and adverse-baseline results that constrain the claim.
5. Distinguish verified facts, observed results, method design, interpretation, limitations, and future work.
6. Do not turn a proxy into deployment performance or a narrow constraint check into total safety/compliance.

Evidence phase:
- Pin implementation/data versions and record checksums when practical.
- Identify and run the narrow paper-critical tests.
- Rerun the principal experiment in a fresh directory when safe.
- Compare archived and fresh outputs by stable keys and all shared fields; report exact/tolerance/schema limits honestly.
- Record environment, dependencies, seeds, hardware, runtime, failures, and repository-wide caveats separately.
- Build a claim ledger linking each material statement to its evidence and strongest defensible wording.

Research story:
- Lead with the real scientific or organizational problem and evaluation gap.
- Use three integrated contributions unless the evidence requires another structure: benchmark/data/evaluation; method/framework/system; empirical/evidence/governance.
- Group numerous factors into 3–6 main families. Present representative objectives and constraints in the main text; place full formulas, plain-language definitions, real-world meaning, implementation traces, and references in appendices.
- Write related work as a relationship map. Explain established components, the documented intersection gap, and a qualified novelty statement.

Manuscript structure:
- Abstract: problem, gap, method, exact principal result, boundary, impact.
- Introduction; related work; problem/benchmark/data; method/framework; experiments; results and discussion; limitations/ethics/open questions as appropriate; conclusion.
- Report uncertainty, denominators, budgets, failure coding, and robustness design.

Source architecture:
- Start from the official venue files.
- Use main.tex plus modular sections/, appendices/, figs/, tabs/, references.bib, and only necessary data/ and scripts/.
- Insert all sections, appendices, and tables using \input.
- Keep all figures under figs/ with editable masters and publication PDFs.
- Keep the active paper title as one continuous semantic string. Do not put `\\`, `\newline`, `\linebreak`, `\parbox`, `\shortstack`, tabulars, spacing tricks, resize commands, or equivalent manual layout inside the title; allow the official template to wrap it naturally.
- Preserve the official checklist and handle double-blind repository identity conservatively.

Visuals:
- Produce {{REQUIRED_VISUALS}} only when each adds information.
- Use editable vector masters and PDF exports; generate quantitative figures from verified data.
- Define one visual system before drawing: final-size type scale, restrained palette, line weights, corner radii, evidence-status encoding, and one original/licensed outlined technical icon family.
- Maintain a figure manifest linking each intended message and evidence source to target width, master/export, label, compiled number/page/source wrapper, and four-layer QA.
- Apply publication typography, consistent notation, restrained palette, evidence-status encoding, and final-size visual QA.
- Reject overlap, clipping, arrows through text, unreadable legends, fake dashboards, and decorative raster imagery.

References:
- Put every verified BibTeX record in references.bib.
- Prefer original papers and official public standards/pages.
- Verify title, authors, venue, year, DOI/URL, and relevance.
- Do not claim “first,” “seminal,” “advantage,” “safe,” or “state of the art” beyond the literature search and evidence.

Release:
- Compile to stability, inspect the stable log, enforce the rendered page boundary, and visually review every PDF page.
- Run static dependency/citation/label/figure/title audits; reject manual title layout.
- Run renderer-measured SVG containment with explicit text ownership and a positive/negative self-test.
- Create a clean ZIP; extract and compile it in a fresh directory.
- Validate both PDFs, render every page, and require clean-room page-pixel equivalence with the intended release.
- Produce {{REQUIRED_DELIVERABLES}} using basename {{OUTPUT_BASENAME}}.
- Write an audit report with provenance, tests, rerun comparison, compute, metric traceability, visual QA, anonymity/page decisions, claim boundaries, caveats, and confirmation of external mutations.

Do not call the work final until every applicable release gate passes. Lead the handoff with artifact links, then state the strongest supported result and the most important limitation.
```

## 3. Evidence audit prompt

```markdown
Audit the scientific evidence for {{PROJECT_NAME}} before revising any prose. Keep {{AUTHORITATIVE_REPOS}} read-only.

1. Pin code, data, configuration, and archived-result versions.
2. Identify the exact path that supports each intended headline claim.
3. Run targeted tests and, separately, repository-wide tests.
4. Rerun the principal analysis into a fresh directory if safe.
5. Compare archived and rerun outputs by stable keys and shared fields; distinguish byte identity, exact shared-field equality, numerical tolerance, and schema mismatch.
6. Record environment, dependencies, seeds, hardware, runtime, failures, fallbacks, and missing fields.
7. Produce a claim ledger with: paper location, proposed claim, evidence source/version, verification method, supported wording, prohibited wording, and caveat.
8. Flag any draft claim that confuses probability with runtime, a proxy with deployment impact, one constraint with total feasibility, synthetic evidence with field validity, or post-hoc selection with prospective policy.

Return an evidence report and a machine-readable metric table. Do not draft the final abstract until the audit is complete.
```

## 4. Paper architecture prompt

```markdown
Design the paper architecture for {{TARGET_VENUE}} from the verified claim ledger.

- Reduce the paper to one primary research question and three distinct contributions.
- Group benchmark/data/method complexity into 3–6 interpretable families.
- For every family or strategy, define the mathematical formula, intuitive meaning, scientific/real-world role, implementation trace, and primary reference.
- Keep representative equations and core evidence in the main text; route exhaustive definitions, derivations, formula glossaries, protocol details, extra results, reproducibility, and ethics to separate appendix files.
- Create a section-by-section claim budget: each subsection must name its evidence and purpose.
- Build a related-work matrix showing established components, their relationships, the missing intersection, and the exact qualified novelty statement.
- Specify all main tables and figures with their one-sentence message and source data.
- Allocate the rendered page budget before writing, including floats.

Return the outline, file tree, page budget, table/figure plan, and claim-to-section map before generating LaTeX.
```

## 5. Figure and table prompt

```markdown
Create publication-ready evidence visuals for {{PROJECT_NAME}} using verified data only.

For each proposed asset, state: research message, evidence status, input file/version, generation method, target width, caption claim, and editable master format. Prefer a compact set such as teaser, benchmark taxonomy, method/decision pipeline, literature relationship map, quantitative results, and open-questions map only where useful.

Requirements:
- editable SVG/draw.io/TikZ/data-code master plus PDF export;
- consistent typography, notation, palette, panel labels, and line weights;
- one coherent technical icon system with matched geometry, stroke, optical size, and evidence meaning; unfamiliar icons remain paired with text;
- quantitative values regenerated from frozen data rather than typed manually;
- observed, inferred, hypothetical, and future elements visually distinguished;
- connectors drawn behind nodes, routed through reserved gutters, and terminated at node boundaries or named ports; no floating arrowheads or connector-through-label defects;
- no overlap, clipping, boundary-touching text, status-badge/title collision, unreadable legends, deceptive axes, unsupported icons, or decorative AI-generated imagery;
- for code-generated SVG cards, pills, badges, and swimlanes, stable shape/text IDs plus `data-container`/`data-padding` annotations and renderer-measured containment checks on all four sides;
- every text element explicitly classified with `data-container` or `data-containment="free"`, plus a positive fixture that passes and a narrowed negative fixture that fails;
- visual inspection of the editable master, standalone export, exact single- or double-column size, and clean-room compiled PDF page;
- a compiled mapping from rendered figure number/page to label, source wrapper, and graphic, so reviewer references such as “Figure 4” are resolved from the PDF rather than guessed from filenames;
- when example figures are supplied, reuse their composition grammar only—never trace, copy, or embed the raster reference;
- every table in tabs/*.tex and every figure under figs/.

Return the source files, exports, generation script where applicable, and a per-asset QA record.
```

## 6. Revision prompt

```markdown
Revise the existing Overleaf project for {{TARGET_VENUE}} without rebuilding it blindly.

1. Audit the current source tree, template, continuous-title rule, compilation, citations, page boundary, anonymity, figures, and claim ledger. Compile first and map rendered figure numbers/pages to the actual source files before acting on comments such as “Figure 2 arrows” or “Figure 4 overlap.”
2. Compare reviewer/user requests with verified evidence and mark each as: textual fix, analysis required, new evidence required, unsupported, or venue-policy issue.
3. Preserve user-authored content and unrelated changes. Do not modify {{DO_NOT_MUTATE}}.
4. Implement only evidence-supported revisions; add new analysis only when authorized and reproducible.
5. Update formulas, tables, figures, appendices, bibliography, and checklist consistently.
6. Recompile, render, inspect every revised figure at all four layers, inspect its full rendered clean-room page, then independently compile a clean ZIP and compare page pixels with the intended PDF.
7. Produce a change summary mapping every request to files changed and evidence used, plus remaining caveats.
```

## 7. Final release prompt

```markdown
Perform an independent release audit of {{OUTPUT_BASENAME}}.

Check official template/rules, continuous semantic title with natural wrapping, rendered main-page boundary, anonymity and PDF metadata, modular source dependencies, citations and labels, equations, table and figure placement, editable vector masters, data-driven chart regeneration, targeted reproduction, whole-repository caveats, environment/compute record, unsupported claims, and package cleanliness.

Create the clean Overleaf ZIP, extract it into a new directory, compile from scratch, audit the stable log, validate both PDFs, render every page, and require page-pixel equivalence with the intended submission PDF. Record checksums and deterministic repackaging equality.

Return a gate table with PASS/CAVEAT/FAIL/N/A and direct evidence. A caveat may be released only if it is disclosed and does not invalidate a headline claim. Do not report success if any missing citation, missing input, fatal compile issue, anonymity leak, unsupported headline number, or untraceable figure remains.
```
