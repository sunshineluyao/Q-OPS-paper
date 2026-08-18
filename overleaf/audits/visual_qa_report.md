# Visual QA and independent review cards

Status: PASS. All retained visuals score at least 90/100 after standalone, insertion-size, and full-page review.

Common contract: Nimbus Sans labels, Times-compatible captions/body, navy ink, blue classical/system structure, teal evidence-positive/verification, orange insufficiency/fallback, neutral gray conceptual boundaries; live SVG text; rounded containers; dedicated connector gutters; color plus shape/state redundancy. Minimum effective figure text is 7.28 pt (22 SVG units at Figure 2's 397/1200 scale); Figures 1 and 3 use at least 7.38 pt for body annotations (26 units at 397/1400 scale).

| Object | Page/source | Score | Review outcome |
|---|---|---:|---|
| Figure 1 architecture | p.2, `figs/fig1_architecture.svg` | 95 | Classical path dominates; optional pilot, independent verification, review, outcome, and fallback are distinct; connectors use gutters; clip art is removable without losing meaning. |
| Figure 2 evidence evolution | p.5, `figs/fig3_evidence_evolution.svg` | 94 | C1.0--C1.2 controls and evidence status are explicit; no invented historical metrics; final annotations remain within bounds. |
| Figure 3 QVR | p.6, `figs/fig2_quantum_value_region.svg` | 96 | All 32 observed points are data-derived; gate state uses fill/outline/cross; conceptual region shading and full-gate caveat are explicit; axes and legend are unclipped. |
| Table 1 environment | p.3, `tabs/table1_decision_environment.tex` | 93 | Compact three-column editorial synthesis, clear evidence boundary, no welfare inference. |
| Table 2 results | p.6, `tabs/table2_results.tex` | 96 | Estimates, denominators/intervals, and scope are separated; adverse and feasibility results retained. |
| Appendix Tables 3--7 | pp.9--13, `tabs/tab_appendix_*.tex` | 91 | Dense but legible at final size; formulas, protocol, partition, and traceability remain editable; no overflow or clipping. |

Automated containment audits pass for every main figure, including negative curved/rounded-container fixtures. Grayscale review preserves hierarchy through borders, fill state, dashes, crosses, and labels rather than hue alone. No raster image is used as a quantitative figure master; PNG clip-art exports are convenience derivatives only.
