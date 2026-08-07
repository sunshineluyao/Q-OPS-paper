---
name: build-evidence-grounded-overleaf-paper
description: Build or revise a submission-ready academic paper from repositories, data, experiment outputs, source documents, and an official venue template. Use when Codex must produce an evidence-grounded modular LaTeX/Overleaf project, verified formulas and citations, editable publication figures, a clean upload ZIP, a compiled PDF, and a reproducibility or submission-audit report; also use when the user asks for a reusable master prompt for that workflow. Do not use for an isolated paragraph polish, a citation-only lookup, or a paper review that does not request artifact creation.
---

# Build an Evidence-Grounded Overleaf Paper

Treat paper production as an evidence, engineering, and release task—not only a writing task. Make the manuscript persuasive by exposing what the evidence supports, including adverse and null findings, while preventing claims from outrunning the implementation.

## Choose the task mode

- **Prompt mode:** When the user asks only for reusable prompts, read `references/prompt-templates.md`, adapt the smallest relevant template, and return it without creating a paper.
- **Production mode:** When the user asks for a final paper or Overleaf package, execute the complete workflow below.
- **Revision mode:** When an Overleaf project already exists, preserve its venue template and file identity, audit it first, then change only what is needed. Use the revision prompt in `references/prompt-templates.md` as the planning frame.

## Apply the operating contract

1. Rank sources of truth in this order:
   - the user's current instructions and explicit claim boundaries;
   - official venue template, call, policies, and checklist;
   - executable code, raw data, frozen configurations, and direct reruns;
   - machine-readable result artifacts;
   - reports, README files, prior drafts, and conversation memory.
2. Treat contradictions as audit findings. Prefer the higher-ranked source and disclose the mismatch.
3. Keep upstream repositories and external resources read-only unless the user explicitly authorizes changes. Run experiments into a new output directory; never overwrite frozen evidence.
4. Verify unstable venue rules, dual-submission policies, standards, and recent literature from official or primary sources. Never invent a citation; leave a visible TODO if verification is impossible.
5. Label every material statement as one of: **verified fact**, **observed result**, **method design**, **interpretation**, **limitation**, or **future work**.
6. Ask only for genuinely blocking choices. Otherwise state conservative assumptions and continue.
7. Treat “first-pass final” as a release condition, not a drafting milestone. Do not hand off a nominally final artifact and wait for the user to discover title, figure, packaging, or PDF defects. Build, audit, repair, and rerun every applicable gate before delivery.

Use relevant installed skills when their trigger applies: use `academic-vector-figures` for exact publication figures, `pdf` for rendered PDF inspection, `documents` for substantive DOCX extraction, and `spreadsheets` for spreadsheet-backed analysis. Do not use generative raster imagery for scientific charts, architectures, or evidence-bearing diagrams.

## 1. Build an authority and artifact map

Record before drafting:

- target venue, track, deadline, page-count rule, bibliography/appendix treatment, anonymity mode, and required checklist;
- official template and compiler expectations;
- source documents, repositories, commit identifiers, data, configurations, archived results, and prior manuscript;
- primary research question, intended audience, requested contributions, and explicit non-claims;
- allowed external actions and resources that must remain unchanged;
- required deliverables and naming convention.

Hash or otherwise identify frozen inputs when practical. Do not let an attractive prior draft override current executable evidence.

## 2. Audit evidence before writing results

Read `references/evidence-and-claims.md` and create a claim ledger. For computational or empirical work:

1. Resolve the exact implementation version or record why it cannot be pinned.
2. Identify the narrow experiment path that supports the paper.
3. Run relevant tests separately from repository-wide tests.
4. Rerun the paper-critical pipeline in a fresh output path when safe and feasible.
5. Compare rerun and archived outputs using stable keys and all shared fields. Distinguish exact shared-field reproduction, tolerance-based agreement, schema mismatch, and byte identity.
6. Record environment, dependencies, hardware, random seeds, runtime, and failures.
7. Preserve counterevidence: failed cases, non-adoption cases, unequal budgets, fallback states, confidence intervals crossing zero, or metrics where a baseline is stronger.
8. Separate a narrow safety or legality check from composite feasibility, deployment safety, fairness validity, or standards compliance.

Do not draft headline results until every headline number has a traceable source. If rerunning would be expensive, destructive, credential-sensitive, or beyond the user's authorization, stop at a read-only audit and report the limitation.

## 3. Design the research story

Lead with the real problem and evaluation gap, then introduce the method. Do not lead with a fashionable algorithm merely because it is technically interesting.

Default to three integrated contributions unless the field strongly requires another structure:

1. a problem, benchmark, dataset, or evaluation contribution;
2. a method, framework, or system contribution;
3. an evidence, empirical, or governance contribution.

Group many design factors into three to six interpretable families in the main text. Put full formula glossaries, variable definitions, implementation mappings, and secondary results in appendices. For each family or mechanism, provide:

- mathematical definition;
- plain-language meaning;
- real-world or scientific role;
- implementation trace;
- verified literature anchor.

Write related work as a relationship argument, not a citation inventory. State which components are established, which combination is unusual, what was searched, and why the novelty claim is qualified. Prefer “to our knowledge,” “among the first,” or “we are not aware of” over absolute-first claims unless a systematic review supports them.

## 4. Create the modular Overleaf source

Start from the official venue files. Do not recreate a style file from memory. For a substantive paper, prefer:

```text
paper/
  main.tex
  <official venue style and checklist files>
  references.bib
  sections/
  appendices/
  figs/
  tabs/
  data/                 # only compact evidence needed for audit/rebuild
  scripts/              # figure or audit regeneration when useful
  README.md
```

Apply these rules:

- Insert sections and appendices with `\input{...}`.
- Keep each table in `tabs/*.tex` and insert it with `\input{...}`.
- Keep all figures in `figs/`; include PDF exports in LaTeX and retain editable masters such as SVG, draw.io, TikZ, or data-generation code.
- Keep bibliography entries only in `references.bib` or the venue-required equivalent.
- Preserve the official checklist and answer it from the actual artifact.
- Centralize macros, colors, and anonymity-sensitive strings in `main.tex` or one small macro file.
- Write `\title{...}` as one continuous semantic string. Never use `\\`, `\newline`, `\linebreak`, `\parbox`, `\shortstack`, spacing tricks, nested tabulars, or equivalent manual title layout. Let the official template wrap the title naturally; apply the same semantic-first rule to headings unless the template explicitly requires otherwise.
- Keep anonymous submission and camera-ready identities separable. Do not print an identifying public repository URL in a double-blind PDF unless the venue explicitly permits it.
- Include only compact, legally shareable evidence. Never package credentials, private data, hidden metadata, `.git`, or unrelated repository content.

## 5. Write with mathematical and evidentiary transparency

Use the following section logic unless the venue dictates otherwise:

1. abstract: problem, gap, method, exact principal result, boundary, impact;
2. introduction: motivation, gap, approach, contributions, claim boundary;
3. related work: component literatures and the paper's intersection;
4. problem/benchmark/data: variables, objectives, constraints, provenance;
5. method/framework: each strategy or component with formulas and role;
6. experiments: protocol, baselines, budgets, metrics, seeds, uncertainty;
7. results/discussion: favorable, adverse, and null evidence with meaning;
8. limitations, ethics, broader impacts, or open questions as venue-appropriate;
9. conclusion: supported result and next falsifiable step.

Never convert a sampling proxy into runtime, a synthetic result into field validity, a zero count on one check into total safety, or a post-hoc evidence partition into a pre-execution policy. State denominators, paired/unpaired design, uncertainty method, and budget comparability.

## 6. Build tables and figures as evidence surfaces

Create a minimum useful visual system, not decoration. Typical paper-level assets are:

- a teaser or graphical research summary;
- a problem/benchmark taxonomy;
- a method or decision pipeline with abstention/fallback paths;
- a literature relationship map;
- result figures generated from verified data;
- an open-questions or deployment roadmap only when it adds scholarly value.

For every figure:

1. maintain an editable master and a publication PDF export;
2. make observed, inferred, hypothetical, and planned elements visually distinguishable;
3. use consistent typography, palette, line weight, notation, and panel labeling;
4. prevent text overlap, clipping, arrows through labels, illegible legends, and false precision;
5. regenerate quantitative charts from frozen data rather than manually entering values;
6. render the figure at its final single- or double-column size and inspect it visually.

Before drawing the first figure, define one visual-system sheet: type scale at final paper size, restrained palette, line weights, corner radii, evidence-status grammar, and a single technical icon family. Prefer original single-stroke vector icons or a consistently licensed outlined family; avoid emoji, mixed clip-art families, and FontAwesome-style generic glyph mixtures unless the user explicitly requests them. Pair unfamiliar icons with text and never use a shield, certificate, robot, quantum, or governance icon to imply unverified capability.

Maintain a figure manifest with: intended message, evidence status, input/version, target width, editable master, export, label, rendered number, rendered page, source wrapper, icon family, connector audit, containment audit, final-size audit, and full-page audit. Resolve this manifest from the compiled paper before release rather than assuming source filenames equal rendered numbers.

Read `references/visual-release-gates.md` before creating or revising a multi-figure visual system, when the user supplies visual references, or when a reviewer identifies arrows, overlap, icons, clipping, or readability defects. Apply its connector-routing, protected-text-zone, icon-system, and four-layer inspection gates. Borrow composition grammar from reference figures without tracing or embedding them.

After compilation, map the user's rendered figure number to its source wrapper and graphic; never assume `fig4_*.svg` is Figure 4 after float placement:

```bash
python3 <this-skill-dir>/scripts/map_rendered_figures.py \
  /absolute/path/to/paper --aux main.aux --json /tmp/figure-map.json
```

For code-generated SVG cards, badges, pills, and swimlanes, annotate every in-shape text element with `data-container="<shape-id>"`, give both elements stable IDs, and declare a `data-padding` clearance. Check the renderer's actual glyph bounds rather than estimated string length:

```bash
python3 <this-skill-dir>/scripts/audit_svg_text_containment.py \
  /absolute/path/to/figure.svg --require-annotations --require-classification \
  --json /tmp/text-containment.json
```

Mark intentional out-of-container labels with `data-containment="free"`. Run the script's `--self-test` once per environment: valid and intentionally free fixtures must pass, while narrowed and unclassified fixtures must fail. Fail if any title, subtitle, formula, note, or multiline block crosses the shape edge, violates declared padding, or is left unclassified. A standalone image that merely looks acceptable at one zoom does not override a containment failure.

Inspect visuals at four layers: editable master/structure, standalone publication export, exact manuscript width, and the full rendered clean-room PDF page under its compiled figure number. Any visual defect is a hard failure, not a releasable caveat.

Use tables for exact mappings, formulas, evidence boundaries, and comparison of claims. Place detailed glossaries in appendices; keep the main tables scannable.

## 7. Verify references

- Search current technical literature using primary sources: official documentation, standards pages, publisher records, or original papers.
- Verify title, authors, year, venue, DOI/URL, and relevance before adding each BibTeX entry.
- Cite the original source for foundational methods and a current review only when it adds synthesis.
- Cite public standards only; never expose internal or unpublished standards material.
- Check every citation key used in TeX against the bibliography and remove hallucinated or unused placeholders before release.
- Ensure the literature map and novelty language match the citations actually present.

## 8. Compile, render, and inspect

Run the bundled static audit during development. Resolve the script path relative to this `SKILL.md`; do not assume the paper already contains the audit utility:

```bash
python3 <this-skill-dir>/scripts/audit_overleaf.py \
  /absolute/path/to/paper --main main.tex --release \
  --json /tmp/overleaf-audit.json
```

This audit rejects manual title layout. If the venue uses a nonstandard title macro, pass it with `--title-commands`; do not disable the rule.

Before release:

1. compile with the venue-supported engine and bibliography workflow until stable;
2. fail on missing files, undefined citations/references, duplicate labels, and LaTeX errors;
3. inspect overfull/underfull boxes and accept only harmless cases explicitly;
4. verify where main content, references, appendices, and checklist begin against the venue's counting rule;
5. render every PDF page and visually inspect text, equations, floats, captions, tables, and anonymity;
6. use the compiled figure map to inspect every figure both standalone and on its rendered page at final size;
7. run relevant reproduction checks and figure regeneration once from frozen inputs;
8. package a clean ZIP with this skill's bundled `scripts/package_overleaf.py` or an equivalent deterministic process;
9. extract the ZIP into a new directory and compile it independently;
10. audit the stable clean-room log and reject unresolved references/citations, fatal errors, missing glyphs, rerun requests, and overfull boxes:

```bash
python3 <this-skill-dir>/scripts/audit_latex_log.py \
  /absolute/path/to/clean-room/main.log --json /tmp/latex-log-audit.json
```

Run `audit_latex_log.py --self-test` once per environment; its clean fixture must pass and its undefined-reference/overfull fixture must fail.

After installing or changing this Skill, run its complete regression suite once:

```bash
python3 <this-skill-dir>/scripts/test_release_gates.py
```

Do not release if any regression test fails. The suite covers starred titles, stable JSON output, Python compatibility, symlink rejection, multi-figure mapping, rerun detection, and curved-container geometry.

11. validate both PDFs with `pdfinfo`, render every page, and compare clean-room page pixels with the intended release; byte equality is not required when metadata differs:

```bash
python3 <this-skill-dir>/scripts/compare_pdf_renders.py \
  /absolute/path/to/intended.pdf /absolute/path/to/clean-room/main.pdf \
  --json /tmp/pdf-render-comparison.json
```

12. record deterministic ZIP checksums, PDF checksums, page count, figure-map coverage, and all gate evidence. If a PDF is truncated, unreadable, missing a page, or visually different, replace it from the verified clean-room build and rerun the entire release sequence.

Read `references/release-gates.md` and pass every applicable gate. Do not declare “final” on compilation alone.

## 9. Produce the handoff

Unless the user requests another set, deliver:

1. a clean Overleaf ZIP;
2. a compiled submission PDF;
3. a reproducibility and submission-audit report PDF or Markdown file.

The report must state:

- artifact/version provenance;
- tests and reruns performed;
- metric traceability and comparison method;
- environment and compute record;
- page-count and anonymity decisions;
- vector figure QA;
- supported and unsupported claim language;
- unresolved caveats and TODOs;
- confirmation of whether any upstream or external resource was modified.

Lead the final response with the deliverables. Summarize the strongest supported claim, the most important limitation, compilation status, and any unresolved blocker. Never hide a caveat in commentary; make the final answer self-contained.

## Resources

- `references/prompt-templates.md`: adaptable master, evidence-audit, architecture, visual, revision, and release prompts. Read when the user requests a prompt or when a complex production task needs decomposition.
- `references/evidence-and-claims.md`: evidence hierarchy, claim ledger, and wording rules. Read before drafting results or novelty claims.
- `references/release-gates.md`: required checks for source, evidence, visuals, bibliography, compilation, packaging, and handoff. Read before calling a paper final.
- `references/visual-release-gates.md`: reference-figure translation, icon-system, connector, protected-text, final-size, and rendered-number QA. Read for figure creation or revision.
- `scripts/audit_overleaf.py`: static audit for modular TeX dependencies, bibliography keys, labels, graphics, editable masters, TODOs, and packaging contaminants.
- `scripts/map_rendered_figures.py`: map compiled figure numbers and pages to labels, source wrappers, and graphics before visual QA.
- `scripts/audit_svg_text_containment.py`: compare Inkscape-rendered text bounds against declared SVG containers and padding.
- `scripts/audit_latex_log.py`: reject unresolved compilation, glyph, rerun, and layout defects from the stable LaTeX log.
- `scripts/compare_pdf_renders.py`: verify page count and page-pixel equivalence between intended and clean-room PDFs.
- `scripts/package_overleaf.py`: create a deterministic clean Overleaf ZIP while excluding build debris and sensitive workspace metadata.
- `scripts/test_release_gates.py`: run deterministic positive and negative regressions for the bundled release utilities.
