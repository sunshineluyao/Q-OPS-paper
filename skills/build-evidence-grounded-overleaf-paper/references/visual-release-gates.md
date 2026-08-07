# Visual release gates for academic papers

Use these gates when creating or revising any evidence-bearing figure.

## 1. Translate references into visual grammar

- Extract composition principles from example figures: branching, convergence, swimlanes, matrices, icon-coded cards, or evidence layers.
- Do not trace pixels, copy labels, reproduce proprietary logos, or embed the reference raster in the deliverable.
- Preserve the paper's intellectual structure and evidence boundary even when the reference suggests a different style.

## 2. Establish one icon system

- Use original or verified/licensed vector icons with one geometry, bounding box, stroke weight, corner style, and detail level.
- Default to original single-stroke SVG symbols or one consistently licensed outlined technical family (for example, Material Symbols Outlined). Do not mix FontAwesome glyphs, emoji, clip art, logos, and bespoke icons; use another family only when the user or venue explicitly requires it.
- Use icons to accelerate recognition of technical concepts such as people, AI, networks, uncertainty, review, governance, quantum circuits, filters, certificates, data, and experiments.
- Pair every unfamiliar icon with text. Never let an icon imply an unimplemented capability, certified safety, or empirical result.
- Do not mix emoji, photorealistic art, brand marks, filled clip art, and line icons in one figure family.

## 3. Route connectors through protected whitespace

- Draw connectors before nodes so cards mask lines behind them.
- Terminate every arrow at a node boundary or named port; do not leave floating arrowheads.
- Reserve gutters between cards. Keep arrowheads, elbows, and curves out of text and icon clearance zones.
- Use orthogonal or shallow curved paths with few bends. Use wide branch spines or ribbons for many-to-one convergence when separate arrows would cross.
- Give connectors stable IDs and explicit source/target meaning in the generation source. Reserve a connector gutter before placing text; never repair collisions by shrinking labels below the final-size type floor.
- Separate implemented, inferred, and future paths by solid/dashed styling and explain that grammar in the caption.

## 4. Allocate protected text zones

- Give every title, body block, formula, icon, badge, and border a non-overlapping bounding zone.
- Shorten or wrap labels before reducing essential text. Treat 8 pt at final paper size as the default floor; use 7 pt only for secondary notes.
- Keep status badges outside title extents. Keep captions and qualification strips inside their containers.
- Do not place text on top of connectors, plot marks, shaded fills with insufficient contrast, or panel borders.
- Treat containment as geometry, not visual impression. For code-generated SVGs, assign stable IDs to shapes and their text, annotate text with `data-container` and `data-padding`, and compare actual renderer glyph bounds with the container's geometric box.
- Mark legitimate labels outside shapes with `data-containment="free"`; do not leave text ownership implicit.
- Require declared clearance on all four sides. Text that remains technically inside a border but leaves less than the declared padding still fails.

## 5. Inspect at four layers

1. Inspect the editable master structurally for live text, stable IDs, licensed/original icons, connector ordering, embedded raster, and clipping.
2. Inspect each standalone SVG/PDF export at 100% and confirm that the export matches its master.
3. Inspect each figure at its exact `\includegraphics` width. Confirm that icons, formulas, labels, and evidence-status styling remain legible.
4. Compile the clean-room paper, map rendered figure numbers and pages, then inspect those pages at full resolution. A source filename is not a reliable figure number after LaTeX float placement.

Run the structural SVG audit from `academic-vector-figures`, then run:

```bash
python3 <this-skill-dir>/scripts/map_rendered_figures.py \
  /absolute/path/to/paper --aux main.aux --json /tmp/figure-map.json
```

For every generated card/pill/swimlane figure, also run:

```bash
python3 <this-skill-dir>/scripts/audit_svg_text_containment.py \
  /absolute/path/to/figure.svg --require-annotations --require-classification \
  --json /tmp/text-containment.json
```

Before trusting the environment, run:

```bash
python3 <this-skill-dir>/scripts/audit_svg_text_containment.py --self-test
```

The valid and intentionally free fixtures must pass; the narrowed and unclassified fixtures must fail. Record, for every figure: rendered number, page, label, source wrapper, graphic, target width, master audit, export audit, final-size audit, and clean-room full-page audit.

## 6. Quantitative-figure guardrail

- Generate data marks from frozen machine-readable evidence.
- Icons may label panels or metric tiles, but must not obscure marks, uncertainty, axes, scales, or sample definitions.
- Preserve adverse and null evidence with equal visual dignity; do not hide it in a footnote or low-contrast decoration.

Fail the visual release if any connector crosses a label, text is unclassified or leaves its declared shape/padding zone, the negative containment fixture does not fail, an arrowhead floats, a status badge covers a title, an icon is inconsistent, essential text is unreadable at final size, or the inspected source figure does not match the rendered figure number cited by the user or reviewer. Never downgrade these defects to caveats.
